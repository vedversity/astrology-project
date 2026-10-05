"""Choghadiya and the daily Rashifal."""

import datetime as dt

from fastapi.testclient import TestClient

from app.astro import daily
from app.main import app
from app.report import build_panchang, build_rashifal
from tests.test_content import check_wording

client = TestClient(app)
SUNDAY = dt.date(2026, 9, 27)
KHARGHAR = (19.0473, 73.0718)


def keys(slots):
    return [slot["key"] for slot in slots]


def test_choghadiya_order_for_each_weekday():
    # The published order: Sunday begins with Udveg by day and Shubh by night
    sunday = daily.choghadiya(SUNDAY, *KHARGHAR)
    assert keys(sunday["day"]) == ["udveg", "char", "labh", "amrit", "kaal", "shubh", "rog", "udveg"]
    assert keys(sunday["night"]) == ["shubh", "amrit", "char", "rog", "kaal", "labh", "udveg", "shubh"]
    monday = daily.choghadiya(SUNDAY + dt.timedelta(days=1), *KHARGHAR)
    assert keys(monday["day"]) == ["amrit", "kaal", "shubh", "rog", "udveg", "char", "labh", "amrit"]
    assert keys(monday["night"]) == ["char", "rog", "kaal", "labh", "udveg", "shubh", "amrit", "char"]
    # Every day and every night begins and ends with the same slot
    for offset in range(7):
        slots = daily.choghadiya(SUNDAY + dt.timedelta(days=offset), *KHARGHAR)
        for part in slots.values():
            assert len(part) == 8 and part[0]["key"] == part[7]["key"]


def test_choghadiya_fills_the_day_and_the_night():
    slots = daily.choghadiya(SUNDAY, *KHARGHAR)
    assert slots["day"][0]["start"].startswith("2026-09-27T06:27")       # sunrise
    assert slots["day"][7]["end"] == slots["night"][0]["start"]          # sunset joins the two
    assert slots["night"][0]["start"].startswith("2026-09-27T18:29")
    assert slots["night"][7]["end"].startswith("2026-09-28T06:27")       # next sunrise
    for part in slots.values():
        for earlier, later in zip(part, part[1:]):
            assert earlier["end"] == later["start"]
    start = dt.datetime.fromisoformat(slots["day"][0]["start"])
    end = dt.datetime.fromisoformat(slots["day"][0]["end"])
    assert abs((end - start).total_seconds() / 60 - 90.3) < 1            # an eighth of a 12-hour day
    assert daily.QUALITY["amrit"] == "good" and daily.QUALITY["kaal"] == "avoid"


def test_panchang_includes_choghadiya_with_names():
    body = build_panchang(SUNDAY, *KHARGHAR)
    first = body["choghadiya"]["day"][0]
    assert first["name"] == {"en": "Udveg", "hi": "उद्वेग"} and first["quality_label"]["en"] == "Avoid new starts"
    check_wording(body["choghadiya"])


def test_rashifal_follows_the_moon():
    # On the sample day the Moon is in Pisces (Uttara Bhadrapada at 6 a.m.)
    result = build_rashifal(SUNDAY)
    assert result["moon_sign"]["en"] == "Pisces" and result["moon_nakshatra"]["en"] == "Uttara Bhadrapada"
    by_slug = {r["slug"]: r for r in result["rashis"]}
    assert len(by_slug) == 12
    assert by_slug["meen"]["house"] == 1 and by_slug["mesh"]["house"] == 12
    assert by_slug["kark"]["house"] == 9 and by_slug["singh"]["house"] == 8     # Chandrashtama for Leo
    assert sorted(r["house"] for r in result["rashis"]) == list(range(1, 13))
    assert "Pisces" in by_slug["mesh"]["basis"]["en"] and "12th" in by_slug["mesh"]["basis"]["en"]
    assert result["moon_leaves_sign"] > "2026-09-27"
    check_wording(result)


def test_rashifal_changes_when_the_moon_changes_sign():
    today = build_rashifal(SUNDAY)
    later = build_rashifal(SUNDAY + dt.timedelta(days=3))
    assert today["moon_sign"]["en"] != later["moon_sign"]["en"]
    assert [r["house"] for r in today["rashis"]] != [r["house"] for r in later["rashis"]]


def test_api_rashifal():
    response = client.get("/rashifal", params={"date": "2026-09-27"})
    assert response.status_code == 200 and len(response.json()["rashis"]) == 12
    assert client.get("/rashifal").status_code == 200
    assert client.get("/rashifal", params={"date": "1500-01-01"}).status_code == 422
