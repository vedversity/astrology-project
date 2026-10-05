"""Muhurat dates: the rules must hold on every date offered, and the set-aside periods must be right."""

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.astro import muhurat
from app.main import app
from app.report import build_muhurat
from tests.test_content import check_wording

YEAR = 2027


@pytest.mark.parametrize("kind", muhurat.TYPES)
def test_every_date_passes_its_own_rules(kind):
    rule = muhurat.RULES[kind]
    dates = muhurat.shubh_dates(kind, YEAR)
    assert dates, kind
    for day in dates:
        assert day["nakshatra"] in rule["nakshatras"] and day["tithi"] in rule["tithis"]
        assert day["weekday"] in rule["weekdays"] and not day["amavasya"]
        assert not (day["marks"] & rule["avoid"])
        assert day["date"].year == YEAR


def test_weddings_keep_clear_of_the_set_aside_periods():
    dates = [d["date"] for d in muhurat.shubh_dates("vivah", YEAR)]
    assert 25 <= len(dates) <= 90
    assert not [d for d in dates if d.weekday() in (muhurat.TUE, muhurat.SAT)]
    # Chaturmas 2027 runs from mid-July (Devshayani Ekadashi) to early November (Devuthani Ekadashi)
    assert not [d for d in dates if dt.date(YEAR, 7, 16) <= d <= dt.date(YEAR, 11, 8)]
    # Kharmas: the Sun in Sagittarius (mid-December to mid-January) and Pisces (mid-March to mid-April)
    assert not [d for d in dates if d >= dt.date(YEAR, 12, 17) or d <= dt.date(YEAR, 1, 13)]
    assert not [d for d in dates if dt.date(YEAR, 3, 16) <= d <= dt.date(YEAR, 4, 13)]


def test_set_aside_periods_for_2027():
    periods = {(reason, start.month): (start, end) for reason, start, end in muhurat.set_aside_periods("vivah", YEAR)}
    start, end = periods[("chaturmas", 7)]
    assert dt.date(YEAR, 7, 12) <= start <= dt.date(YEAR, 7, 16) and dt.date(YEAR, 11, 7) <= end <= dt.date(YEAR, 11, 11)
    start, end = periods[("holashtak", 3)]
    assert (end - start).days in (6, 7, 8) and end == dt.date(YEAR, 3, 22)        # Holi 2027: 22 March
    assert ("kharmas", 3) in periods and ("kharmas", 12) in periods
    assert muhurat.set_aside_periods("namkaran", YEAR) == []                      # a naming does not wait for a season


def test_namkaran_is_available_all_year():
    months = {d["date"].month for d in muhurat.shubh_dates("namkaran", YEAR)}
    assert months == set(range(1, 13))


def test_muhurat_report():
    report = build_muhurat("vivah", YEAR)
    check_wording(report)
    assert report["name"] == {"en": "Vivah Muhurat", "hi": "विवाह मुहूर्त"}
    assert len(report["months"]) == 12 and sum(len(m["dates"]) for m in report["months"]) == report["count"]
    first = report["months"][0]["dates"][0]
    assert first["date"].startswith("2027-01") and first["nakshatra"]["hi"] and first["weekday"]["en"]
    assert report["months"][7]["dates"] == []                                    # August: inside Chaturmas
    assert [p["reason"]["en"] for p in report["set_aside"]].count("Chaturmas") == 1


def test_api_muhurat():
    client = TestClient(app)
    year = dt.date.today().year
    assert client.get(f"/muhurat/vivah/{year + 1}").status_code == 200
    assert client.get(f"/muhurat/mundan/{year}").json()["type"] == "mundan"
    assert client.get(f"/muhurat/vivah/{year + 5}").status_code == 404
    assert client.get(f"/muhurat/picnic/{year}").status_code == 404
    index = client.get("/muhurat").json()
    assert index["years"] == [year, year + 1, year + 2] and [t["type"] for t in index["types"]] == muhurat.TYPES
    vivah = index["types"][0]
    assert vivah["counts"][str(year + 1)] == client.get(f"/muhurat/vivah/{year + 1}").json()["count"]
