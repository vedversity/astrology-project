"""Web API.

POST /calculate  the raw chart (Phase 1)
POST /preview    the free preview: Rashi, Nakshatra, Pada, name letters
POST /report     everything a Janam Patrika needs: chart, yogas, doshas,
                 numerology, names and the wording in Hindi and English

Run it with:  .venv\\Scripts\\python -m uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

import datetime as dt
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.astro import ENGINE_VERSION, calculate_chart
from app.report import build_preview, build_report

app = FastAPI(title="Janam Patrika API", version=ENGINE_VERSION)


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
