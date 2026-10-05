"""Pieces shared by the API files: the shapes of the requests, and two guards."""

import datetime as dt
import hmac
import os
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Header, HTTPException, Request
from pydantic import BaseModel, Field

from app import payments
from app.limits import admin_limit


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


def checked(birth):
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


def admin_only(request: Request, x_admin_token: str = Header(default="")):
    """Guard for the owner's pages. The password is the ADMIN_TOKEN line in backend/.env."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    if len(expected) < 12:
        raise HTTPException(status_code=503, detail="The admin page is switched off. Set ADMIN_TOKEN (12+ characters) to use it.")
    if not hmac.compare_digest(x_admin_token.encode(), expected.encode()):
        admin_limit(request)
        raise HTTPException(status_code=401, detail="Wrong admin password.")



def free_only():
    """Guard for the endpoints that hand out a full report without an order.

    They exist for development. Once payments are switched on (or on the live
    server), a report can only be obtained through a paid order.
    """
    if payments.mode() != "test":
        raise HTTPException(status_code=403, detail="Reports are delivered through an order.")
