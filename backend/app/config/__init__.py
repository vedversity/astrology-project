"""Owner-editable settings: the brand name, the plans and their prices (site.json)."""

import json
from pathlib import Path

SITE_FILE = Path(__file__).parent / "site.json"


def site():
    """Read fresh each time, so a price change needs no restart."""
    with open(SITE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_note", None)
    return data


def plan(plan_id):
    return next((p for p in site()["plans"] if p["id"] == plan_id), None)
