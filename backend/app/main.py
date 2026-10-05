"""Web API.

POST /calculate  the raw chart (Phase 1)
POST /preview    the free preview: Rashi, Nakshatra, Pada, name letters
POST /report     everything a Janam Patrika needs (development only; off once payments are on)
POST /pdf        the finished Janam Patrika as a PDF file (development only, likewise)
POST /orders ... placing an order, payment, download and receipt: see app/orders.py
POST /milan      Kundli Milan: 36-guna matching for two births
POST /milan/pdf  the Kundli Milan result as a one-page PDF
GET  /panchang   the day's Panchang and Choghadiya for a place
GET  /rashifal   the day's Rashifal for the twelve Rashis
GET  /muhurat    the ceremonies and years on offer
GET  /muhurat/{type}/{year}  shubh dates for vivah, griha-pravesh, namkaran or mundan
GET  /places     birth-place search (name -> latitude, longitude, timezone)
GET  /cities     the cities that have their own Panchang page
GET  /guide/...  reference pages: nakshatras with names, planets in houses
GET  /site       brand name, plans and prices (from app/config/site.json)
GET/PUT /admin/site  the owner's settings page (needs the ADMIN_TOKEN password)

Run it with:  .venv\\Scripts\\python -m uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

import datetime as dt
import os
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config, guide, payments, places
from app.api_common import BirthInput, PdfInput, ReportInput, admin_only, checked, free_only
from app.astro import ENGINE_VERSION, calculate_chart
from app.limits import pdf_limit
from app.orders import router as orders_router
from app.pdf import PdfError, generate_milan_pdf, generate_pdf
from app.astro.muhurat import TYPES as MUHURAT_TYPES
from app.report import build_milan, build_muhurat, build_muhurat_index, build_panchang, build_preview, build_rashifal, build_report

# On the live server (ENV=production) the interactive API pages are switched off
_live = os.environ.get("ENV") == "production"
app = FastAPI(title="Janam Patrika API", version=ENGINE_VERSION,
              docs_url=None if _live else "/docs", redoc_url=None, openapi_url=None if _live else "/openapi.json")

# The website runs on a different address from this API, so it must be named here.
# Set FRONTEND_ORIGINS in .env for the live site (comma-separated).
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "X-Admin-Token"],
)


class MilanInput(BaseModel):
    groom: BirthInput
    bride: BirthInput


class MilanPdfInput(MilanInput):
    lang: Literal["hi", "en"] = "hi"
    groom_name: Optional[str] = Field(default=None, max_length=80)
    bride_name: Optional[str] = Field(default=None, max_length=80)
    groom_place: Optional[str] = Field(default=None, max_length=160)
    bride_place: Optional[str] = Field(default=None, max_length=160)


@app.get("/health")
def health():
    return {"status": "ok", "engine_version": ENGINE_VERSION}


@app.get("/site")
def site():
    # "payments" tells the website how the order page should behave:
    # razorpay = take payment, test = make the PDF without charging, off = not accepting orders
    return {**config.site(), "payments": payments.mode()}


app.include_router(orders_router)


@app.get("/admin/site", dependencies=[Depends(admin_only)])
def admin_site():
    return config.site()


@app.put("/admin/site", dependencies=[Depends(admin_only)])
def admin_save(update: config.SiteUpdate):
    try:
        return config.save_site(update)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))


@app.get("/places")
def place_search(q: str = Query(min_length=2, max_length=60)):
    return places.search(q)


@app.get("/cities")
def city_list():
    return places.cities()


@app.get("/guide/nakshatras")
def guide_nakshatras():
    return guide.nakshatras()


@app.get("/guide/nakshatras/{slug}")
def guide_nakshatra(slug: str):
    found = guide.nakshatra(slug)
    if not found:
        raise HTTPException(status_code=404, detail="Unknown nakshatra.")
    return found


@app.get("/guide/planets")
def guide_planets():
    return guide.planets()


@app.get("/panchang")
def panchang(latitude: float = Query(ge=-66, le=66), longitude: float = Query(ge=-180, le=180),
             timezone: str = "Asia/Kolkata", date: Optional[dt.date] = None):
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=422, detail=f"Unknown timezone: {timezone}")
    day = date or dt.datetime.now(zone).date()
    if not 1800 <= day.year <= 2200:
        raise HTTPException(status_code=422, detail="Year must be between 1800 and 2200.")
    return build_panchang(day, latitude, longitude, timezone)


@app.get("/rashifal")
def rashifal(date: Optional[dt.date] = None):
    day = date or dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
    if not 1800 <= day.year <= 2200:
        raise HTTPException(status_code=422, detail="Year must be between 1800 and 2200.")
    return build_rashifal(day)


def _muhurat_years():
    # Only this year and the next two: enough for planning, and it keeps the work bounded
    this_year = dt.datetime.now(ZoneInfo("Asia/Kolkata")).year
    return range(this_year, this_year + 3)


@app.get("/muhurat")
def muhurat_index():
    return build_muhurat_index(_muhurat_years())


@app.get("/muhurat/{kind}/{year}")
def muhurat(kind: str, year: int):
    if kind not in MUHURAT_TYPES or year not in _muhurat_years():
        raise HTTPException(status_code=404, detail="No muhurat list for this.")
    return build_muhurat(kind, year)


@app.post("/calculate")
def calculate(birth: BirthInput):
    return calculate_chart(**checked(birth))


@app.post("/preview")
def preview(birth: BirthInput):
    return build_preview(**checked(birth))


@app.post("/milan")
def milan(pair: MilanInput):
    return build_milan(checked(pair.groom), checked(pair.bride))


@app.post("/milan/pdf", dependencies=[Depends(pdf_limit)])
def milan_pdf(pair: MilanPdfInput):
    result = build_milan(checked(pair.groom), checked(pair.bride))

    def person(birth, name, place):
        return {"name": name, "place": place, "date": birth.date,
                "time": birth.time if birth.time_known else None}

    try:
        content = generate_milan_pdf(result, person(pair.groom, pair.groom_name, pair.groom_place),
                                     person(pair.bride, pair.bride_name, pair.bride_place), pair.lang)
    except PdfError as error:
        raise HTTPException(status_code=500, detail=f"The PDF could not be produced: {error}")
    return Response(content=content, media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="kundli-milan.pdf"'})


@app.post("/report", dependencies=[Depends(free_only)])
def report(birth: ReportInput):
    return build_report(**checked(birth), gender=birth.gender,
                        surname=birth.surname, kuldevi=birth.kuldevi)


@app.post("/pdf", dependencies=[Depends(pdf_limit), Depends(free_only)])
def pdf(birth: PdfInput):
    report = build_report(**checked(birth), gender=birth.gender,
                          surname=birth.surname, kuldevi=birth.kuldevi)
    person = birth.model_dump(include={"child_name", "gender", "father_name", "mother_name",
                                       "gotra", "kuldevi", "place", "surname"})
    try:
        content = generate_pdf(report, person, birth.variant, birth.lang)
    except PdfError as error:
        raise HTTPException(status_code=500, detail=f"The PDF could not be produced: {error}")
    return Response(content=content, media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="janam-patrika.pdf"'})
