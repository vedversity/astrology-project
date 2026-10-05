"""Web API.

POST /calculate  the raw chart (Phase 1)
POST /preview    the free preview: Rashi, Nakshatra, Pada, name letters
POST /report     everything a Janam Patrika needs: chart, yogas, doshas,
                 numerology, names and the wording in Hindi and English
POST /pdf        the finished Janam Patrika as a PDF file
GET  /panchang   the day's Panchang for a place (tithi, nakshatra, Rahu Kaal ...)
GET  /places     birth-place search (name -> latitude, longitude, timezone)
GET  /site       brand name, plans and prices (from app/config/site.json)

Run it with:  .venv\\Scripts\\python -m uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

import datetime as dt
import os
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import config, places
from app.astro import ENGINE_VERSION, calculate_chart
from app.pdf import PdfError, generate_pdf
from app.report import build_panchang, build_preview, build_report

app = FastAPI(title="Janam Patrika API", version=ENGINE_VERSION)

# The website runs on a different address from this API, so it must be named here.
# Set FRONTEND_ORIGINS in .env for the live site (comma-separated).
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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


@app.get("/places")
def place_search(q: str = Query(min_length=2, max_length=60)):
    return places.search(q)


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


@app.post("/calculate")
def calculate(birth: BirthInput):
    return calculate_chart(**_checked(birth))


@app.post("/preview")
def preview(birth: BirthInput):
    return build_preview(**_checked(birth))


@app.post("/report")
def report(birth: ReportInput):
    return build_report(**_checked(birth), gender=birth.gender,
                        surname=birth.surname, kuldevi=birth.kuldevi)


@app.post("/pdf")
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
