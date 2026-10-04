"""Checks that must hold for ANY chart, independent of the sample PDF."""

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.astro import calculate_chart
from app.astro import vargas
from app.astro.constants import DASHA_YEARS, NAAM_AKSHAR, NAKSHATRA_GANA, NAKSHATRA_YONI
from app.main import app
from tests.darak_sample import BIRTH

# A spread of dates, places and timezones (date, time, lat, lon, timezone)
BIRTHS = [
    (dt.date(2026, 9, 27), dt.time(20, 0), 19.0473, 73.0718, "Asia/Kolkata"),
    (dt.date(1990, 1, 15), dt.time(4, 30), 28.6139, 77.2090, "Asia/Kolkata"),
    (dt.date(2000, 6, 21), dt.time(12, 0), 51.5074, -0.1278, "Europe/London"),
    (dt.date(1975, 12, 5), dt.time(23, 45), 40.7128, -74.0060, "America/New_York"),
    (dt.date(2024, 2, 29), dt.time(0, 5), -33.8688, 151.2093, "Australia/Sydney"),
]


@pytest.fixture(params=BIRTHS, ids=[str(b[0]) for b in BIRTHS])
def chart(request):
    date, time, lat, lon, tz = request.param
    return calculate_chart(date, time, lat, lon, tz)


def test_ketu_is_opposite_rahu(chart):
    rahu = chart["planets"]["rahu"]["longitude"]
    ketu = chart["planets"]["ketu"]["longitude"]
    assert abs((ketu - rahu) % 360 - 180) < 1e-6


def test_lagna_is_first_house(chart):
    assert chart["lagna"]["house"] == 1
    assert chart["vargas"]["D1"]["lagna"]["sign"]["index"] == chart["lagna"]["sign"]["index"]


def test_houses_and_padas_in_range(chart):
    for planet in chart["planets"].values():
        assert 1 <= planet["house"] <= 12
        assert 1 <= planet["pada"] <= 4
        assert 0 <= planet["degree_in_sign"] < 30


def test_sun_and_moon_never_retrograde(chart):
    assert chart["planets"]["sun"]["retrograde"] is False
    assert chart["planets"]["moon"]["retrograde"] is False


def test_dasha_starts_with_moon_nakshatra_lord(chart):
    assert chart["dasha"]["mahadashas"][0]["lord"] == chart["planets"]["moon"]["nakshatra_lord"]


def test_dasha_covers_all_nine_lords(chart):
    lords = [m["lord"] for m in chart["dasha"]["mahadashas"]]
    assert sorted(lords) == sorted(DASHA_YEARS)
    for mahadasha in chart["dasha"]["mahadashas"]:
        assert mahadasha["antardashas"][0]["lord"] == mahadasha["lord"]
        assert mahadasha["antardashas"][0]["start"] == mahadasha["start"]
        assert mahadasha["antardashas"][-1]["end"] == mahadasha["end"]


def test_dasha_balance_is_within_first_period(chart):
    balance = chart["dasha"]["balance_at_birth"]
    assert 0 < balance["total_years"] <= DASHA_YEARS[balance["lord"]]


def test_tithi_contains_birth_moment(chart):
    tithi = chart["panchang"]["tithi"]
    birth = chart["input"]["local_datetime"]
    assert dt.datetime.fromisoformat(tithi["start"]) <= dt.datetime.fromisoformat(birth)
    assert dt.datetime.fromisoformat(birth) <= dt.datetime.fromisoformat(tithi["end"])


def test_sunrise_is_before_sunset(chart):
    p = chart["panchang"]
    assert dt.datetime.fromisoformat(p["sunrise"]) < dt.datetime.fromisoformat(p["sunset"])


def test_lookup_tables_are_complete():
    assert len(NAAM_AKSHAR) == 27 and all(len(row) == 4 for row in NAAM_AKSHAR)
    assert len(NAKSHATRA_YONI) == 27
    assert len(NAKSHATRA_GANA) == 27
    assert sum(DASHA_YEARS.values()) == 120


def test_varga_formulas_on_known_points():
    # 0 degrees Aries sits in Aries in every divisional chart except the Hora (Leo)
    for name, sign_of in vargas.VARGAS.items():
        assert sign_of(0.0) == (4 if name == "D2" else 0)
    # The last navamsa of Pisces is Pisces; the first navamsa of Taurus is Capricorn
    assert vargas.d9_navamsa(359.9) == 11
    assert vargas.d9_navamsa(30.1) == 9


def test_unknown_time_gives_moon_based_chart():
    chart = calculate_chart(BIRTH["date"], None, BIRTH["latitude"], BIRTH["longitude"],
                            BIRTH["timezone"])
    assert chart["meta"]["time_known"] is False
    assert chart["lagna"] is None
    assert chart["vargas"] is None
    assert chart["planets"]["moon"]["house"] is None
    assert chart["avakahada"]["paya"] is None
    assert chart["planets"]["moon"]["sign"]["en"] == "Pisces"
    assert "moon_sign_certain" in chart["time_unknown"]


def test_api_calculate():
    client = TestClient(app)
    response = client.post("/calculate", json={
        "date": "2026-09-27", "time": "20:00",
        "latitude": 19.0473, "longitude": 73.0718, "timezone": "Asia/Kolkata",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["lagna"]["sign"]["en"] == "Aries"
    assert body["planets"]["moon"]["nakshatra"]["en"] == "Revati"


def test_api_rejects_bad_timezone():
    client = TestClient(app)
    response = client.post("/calculate", json={
        "date": "2026-09-27", "time": "20:00",
        "latitude": 19.0473, "longitude": 73.0718, "timezone": "Mars/Olympus",
    })
    assert response.status_code == 422
