"""Web API.

POST /calculate  the raw chart (Phase 1)
POST /preview    the free preview: Rashi, Nakshatra, Pada, name letters
POST /report     everything a Janam Patrika needs: chart, yogas, doshas,
                 numerology, names and the wording in Hindi and English
POST /pdf        the finished Janam Patrika as a PDF file
POST /milan      Kundli Milan: 36-guna matching for two births
POST /milan/pdf  the Kundli Milan result as a one-page PDF
GET  /panchang   the day's Panchang and Choghadiya for a place
GET  /rashifal   the day's Rashifal for the twelve Rashis
GET  /places     birth-place search (name -> latitude, longitude, timezone)
GET  /cities     the cities that have their own Panchang page
GET  /guide/...  reference pages: nakshatras with names, planets in houses
GET  /site       brand name, plans and prices (from app/config/site.json)
GET/PUT /admin/site  the owner's settings page (needs the ADMIN_TOKEN password)

Run it with:  .venv\\Scripts\\python -m uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

import datetime as dt
import hmac
import os
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config, guide, places
from app.astro import ENGINE_VERSION, calculate_chart
from app.limits import admin_limit, pdf_limit
from app.pdf import PdfError, generate_milan_pdf, generate_pdf
from app.report import build_milan, build_panchang, build_preview, build_rashifal, build_report

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


class BirthInput(BaseModel):
    date: dt.date = Field(examples=["2026-09-27"])
    time: Optional[dt.time] = Field(default=None, examples=["20:00"])
    latitude: float = Field(ge=-90, le=90, examples=[19.0473])
    longitude: float = Field(ge=-180, le=180, examples=[73.0718])
    timezone: str = Field(default="Asia/Kolkata", examples=["Asia/Kolkata"])
    time_known: bool = True


class ReportInput(BirthInput):
    gender: Literal["male", "female"] = Field(examples=["male"])
    # Used only for name numerology and the wording; nothing is stored
    surname: Optional[str] = Field(default=None, max_length=60, examples=["Sharma"])
    kuldevi: Optional[str] = Field(default=None, max_length=60)


class PdfInput(ReportInput):
    variant: Literal["mini", "full", "premium"] = "full"
    lang: Literal["hi", "en"] = "hi"
    # Printed on the cover exactly as typed; nothing is stored
    child_name: Optional[str] = Field(default=None, max_length=80)
    father_name: Optional[str] = Field(default=None, max_length=80)
    mother_name: Optional[str] = Field(default=None, max_length=80)
    gotra: Optional[str] = Field(default=None, max_length=60)
    place: Optional[str] = Field(default=None, max_length=160, examples=["Kharghar, Navi Mumbai"])


class MilanInput(BaseModel):
    groom: BirthInput
    bride: BirthInput


class MilanPdfInput(MilanInput):
    lang: Literal["hi", "en"] = "hi"
    groom_name: Optional[str] = Field(default=None, max_length=80)
    bride_name: Optional[str] = Field(default=None, max_length=80)
    groom_place: Optional[str] = Field(default=None, max_length=160)
    bride_place: Optional[str] = Field(default=None, max_length=160)


def _checked(birth):
    """Reject impossible input, then return the birth details as plain arguments."""
    if not 1800 <= birth.date.year <= 2200:
        raise HTTPException(status_code=422, detail="Year must be between 1800 and 2200.")
    try:
        ZoneInfo(birth.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=422, detail=f"Unknown timezone: {birth.timezone}")
    return {
        "date": birth.date, "time": birth.time, "latitude": birth.latitude,
        "longitude": birth.longitude, "timezone": birth.timezone, "time_known": birth.time_known,
    }


@app.get("/health")
def health():
    return {"status": "ok", "engine_version": ENGINE_VERSION}


@app.get("/site")
def site():
    return config.site()


def _admin(request: Request, x_admin_token: str = Header(default="")):
    """Guard for the owner's pages. The password is the ADMIN_TOKEN line in backend/.env."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    if len(expected) < 12:
        raise HTTPException(status_code=503, detail="The admin page is switched off. Set ADMIN_TOKEN (12+ characters) to use it.")
    if not hmac.compare_digest(x_admin_token.encode(), expected.encode()):
        admin_limit(request)
        raise HTTPException(status_code=401, detail="Wrong admin password.")


@app.get("/admin/site", dependencies=[Depends(_admin)])
def admin_site():
    return config.site()


@app.put("/admin/site", dependencies=[Depends(_admin)])
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


@app.post("/calculate")
def calculate(birth: BirthInput):
    return calculate_chart(**_checked(birth))


@app.post("/preview")
def preview(birth: BirthInput):
    return build_preview(**_checked(birth))


@app.post("/milan")
def milan(pair: MilanInput):
    return build_milan(_checked(pair.groom), _checked(pair.bride))


@app.post("/milan/pdf", dependencies=[Depends(pdf_limit)])
def milan_pdf(pair: MilanPdfInput):
    result = build_milan(_checked(pair.groom), _checked(pair.bride))

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


@app.post("/report")
def report(birth: ReportInput):
    return build_report(**_checked(birth), gender=birth.gender,
                        surname=birth.surname, kuldevi=birth.kuldevi)


@app.post("/pdf", dependencies=[Depends(pdf_limit)])
def pdf(birth: PdfInput):
    report = build_report(**_checked(birth), gender=birth.gender,
                          surname=birth.surname, kuldevi=birth.kuldevi)
    person = birth.model_dump(include={"child_name", "gender", "father_name", "mother_name",
                                       "gotra", "kuldevi", "place", "surname"})
    try:
        content = generate_pdf(report, person, birth.variant, birth.lang)
    except PdfError as error:
        raise HTTPException(status_code=500, detail=f"The PDF could not be produced: {error}")
    return Response(content=content, media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="janam-patrika.pdf"'})
