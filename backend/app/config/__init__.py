"""Owner-editable settings: brand name, contact details, astrologer and plans (site.json).

The file can be edited by hand or through the admin page of the website, which
calls save_site(). Only the fields an owner should change can be changed there;
plans cannot be added or removed, because each one matches a PDF variant.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

SITE_FILE = Path(__file__).parent / "site.json"


class Text(BaseModel):
    hi: str = Field(min_length=1, max_length=400)
    en: str = Field(min_length=1, max_length=400)


class Brand(BaseModel):
    name: Text
    tagline: Text


class Contact(BaseModel):
    email: Optional[str] = Field(default=None, max_length=120, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    # Digits only with country code, e.g. 919876543210 (used for a wa.me link)
    whatsapp: Optional[str] = Field(default=None, pattern=r"^\d{10,15}$")


class Astrologer(BaseModel):
    name: Text
    experience_years: int = Field(ge=1, le=90)
    bio: Text


class SiteUpdate(BaseModel):
    brand: Brand
    contact: Contact
    astrologer: Optional[Astrologer] = None
    # plan id -> price in rupees
    prices: dict[str, int]


def _read():
    with open(SITE_FILE, encoding="utf-8") as f:
        return json.load(f)


def site():
    """Read fresh each time, so a change needs no restart."""
    data = _read()
    data.pop("_note", None)
    data.setdefault("contact", {"email": None, "whatsapp": None})
    data.setdefault("astrologer", None)
    return data


def plan(plan_id):
    return next((p for p in site()["plans"] if p["id"] == plan_id), None)


def save_site(update: SiteUpdate):
    """Apply an owner's changes. Raises ValueError if a price is missing or not sensible."""
    data = _read()
    ids = [p["id"] for p in data["plans"]]
    if set(update.prices) != set(ids):
        raise ValueError(f"Give a price for each plan: {', '.join(ids)}")
    for value in update.prices.values():
        if not 1 <= value <= 100000:
            raise ValueError("Each price must be between 1 and 100000 rupees.")
    data["brand"] = update.brand.model_dump()
    data["contact"] = update.contact.model_dump()
    data["astrologer"] = update.astrologer.model_dump() if update.astrologer else None
    for item in data["plans"]:
        item["price"] = update.prices[item["id"]]

    # Write to a temporary file first, so a crash can never leave half a file behind
    handle, temp = tempfile.mkstemp(dir=SITE_FILE.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temp, SITE_FILE)
    return site()
