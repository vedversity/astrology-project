"""Web API. Phase 1 has a single job: POST /calculate returns the chart as JSON.

Run it with:  .venv\\Scripts\\python -m uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

import datetime as dt
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.astro import ENGINE_VERSION, calculate_chart

app = FastAPI(title="Janam Patrika API", version=ENGINE_VERSION)


class BirthInput(BaseModel):
    date: dt.date = Field(examples=["2026-09-27"])
    time: Optional[dt.time] = Field(default=None, examples=["20:00"])
    latitude: float = Field(ge=-90, le=90, examples=[19.0473])
    longitude: float = Field(ge=-180, le=180, examples=[73.0718])
    timezone: str = Field(default="Asia/Kolkata", examples=["Asia/Kolkata"])
    time_known: bool = True


@app.get("/health")
def health():
    return {"status": "ok", "engine_version": ENGINE_VERSION}


@app.post("/calculate")
def calculate(birth: BirthInput):
    if not 1800 <= birth.date.year <= 2200:
        raise HTTPException(status_code=422, detail="Year must be between 1800 and 2200.")
    try:
        ZoneInfo(birth.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=422, detail=f"Unknown timezone: {birth.timezone}")
    return calculate_chart(
        date=birth.date,
        time=birth.time,
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone=birth.timezone,
        time_known=birth.time_known,
    )
