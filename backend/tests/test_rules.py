"""Rule engine: yogas, doshas and strengths, checked against the sample PDF and on many charts."""

import datetime as dt
import random

import pytest

from app.astro import calculate_chart
from app.rules import analyze
from tests.darak_sample import BIRTH

CHART = calculate_chart(**BIRTH)
ANALYSIS = analyze(CHART)

# Page 6 of the sample PDF
SAMPLE_YOGAS = {"hamsa", "malavya", "neecha_bhanga", "guru_mangal", "saraswati", "lakshmi",
                "parivartana", "adhi", "vesi", "vargottama"}
SAMPLE_DOSHAS = {
    "gandmool": "mild", "manglik": "cancelled", "kaal_sarp": "not_present", "vish": "mild",
    "kemadruma": "cancelled", "grahan": "not_present", "guru_chandal": "not_present",
    "angarak": "not_present", "pitru": "minor", "sade_sati": "running",
}
# Page 5 of the sample PDF (planetary strength summary)
SAMPLE_STRENGTH = {
    "jupiter": "strong", "venus": "strong", "mercury": "strong", "rahu": "strong",
    "sun": "medium", "saturn": "medium", "moon": "weak", "mars": "weak",
}


def _yoga(key):
    return next(y for y in ANALYSIS["yogas"] if y["key"] == key)


def _dosha(key):
    return next(d for d in ANALYSIS["doshas"] if d["key"] == key)


def test_sample_yogas_match_exactly():
    assert {y["key"] for y in ANALYSIS["yogas"]} == SAMPLE_YOGAS


@pytest.mark.parametrize("key,status", SAMPLE_DOSHAS.items())
def test_sample_dosha_status(key, status):
    assert _dosha(key)["status"] == status


@pytest.mark.parametrize("planet,level", SAMPLE_STRENGTH.items())
def test_sample_planet_strength(planet, level):
    assert ANALYSIS["strength"][planet]["level"] == level


def test_sample_yoga_details():
    assert _yoga("hamsa")["house"] == 4
    assert _yoga("malavya")["house"] == 7
    assert _yoga("neecha_bhanga")["planets"] == ["mars"]
    assert "joined_by_exalted_planet" in _yoga("neecha_bhanga")["reasons"]
    assert _yoga("parivartana")["planets"] == ["moon", "jupiter"]
    assert _yoga("adhi")["partial"] is True
    assert _yoga("vargottama")["planets"] == ["mercury"]


def test_sample_dosha_details():
    manglik = _dosha("manglik")
    assert manglik["from"] == ["lagna"]                      # Anshik: from the Lagna only
    assert manglik["cancelled_by"] == ["jupiter_conjunct"]
    assert _dosha("gandmool")["moon_returns"]["start"][:10] == "2026-10-24"
    assert _dosha("pitru")["born_in_pitru_paksha"] is True
    assert _dosha("sade_sati")["phase"] == "peak"


def test_sample_aspects():
    # Page 3 of the sample: "Jupiter (4th) aspects 8th, 10th and 12th (Moon & Saturn)"
    jupiter = ANALYSIS["aspects"]["jupiter"]
    assert jupiter["houses"] == [8, 10, 12]
    assert set(jupiter["planets"]) == {"moon", "saturn"}
    assert ANALYSIS["aspects"]["saturn"]["houses"] == [2, 6, 9]
    assert ANALYSIS["aspects"]["mars"]["houses"] == [7, 10, 11]


def test_sample_strongest_life_areas():
    # Page 13: education, home, marriage, fortune and foreign success are the strong areas
    areas = ANALYSIS["areas"]
    for area in ("education", "family", "marriage", "wealth", "foreign"):
        assert areas[area]["level"] == "strong", area


def test_sample_house_table():
    houses = ANALYSIS["houses"]
    assert [h["lord"] for h in houses][:4] == ["mars", "venus", "mercury", "moon"]
    assert houses[3]["occupants"] == ["mars", "jupiter"]
    assert houses[6]["occupants"] == ["mercury", "venus"]
    assert houses[9]["lord_house"] == 12                     # 10th lord Saturn in the 12th


def test_sample_varga_highlights():
    found = {(h["varga"], h["planet"], h["dignity"]) for h in ANALYSIS["varga_highlights"]}
    assert {("D9", "sun", "exalted"), ("D10", "sun", "own"), ("D10", "mars", "own"),
            ("D7", "saturn", "own"), ("D12", "venus", "exalted")} <= found


def test_unknown_time_skips_house_rules():
    chart = calculate_chart(BIRTH["date"], None, BIRTH["latitude"], BIRTH["longitude"], BIRTH["timezone"])
    analysis = analyze(chart)
    assert analysis["houses"] is None and analysis["areas"] is None
    keys = {y["key"] for y in analysis["yogas"]}
    assert "hamsa" not in keys and "saraswati" not in keys   # these need houses
    assert "parivartana" in keys and "vesi" in keys          # these do not
    assert len(analysis["doshas"]) == 10


def random_births(count, seed=7):
    """A repeatable spread of Indian births between 1950 and 2048."""
    rng = random.Random(seed)
    for _ in range(count):
        date = dt.date(1950, 1, 1) + dt.timedelta(days=rng.randint(0, 36000))
        yield date, dt.time(rng.randint(0, 23), rng.randint(0, 59)), rng.uniform(8, 35), rng.uniform(68, 95)


def test_rules_hold_on_many_charts():
    statuses = {"not_present", "present", "mild", "partial", "cancelled", "minor", "running"}
    for date, time, lat, lon in random_births(150):
        chart = calculate_chart(date, time, lat, lon, "Asia/Kolkata")
        analysis = analyze(chart)
        keys = set(y["key"] for y in analysis["yogas"])
        for dosha in analysis["doshas"]:
            assert dosha["status"] in statuses
        # A yoga with planets on both sides replaces the one-sided yogas
        assert not ("ubhayachari" in keys and keys & {"vesi", "vasi"})
        assert not ("durudhara" in keys and keys & {"sunapha", "anapha"})
        # Kemadruma can only form when nothing sits beside the Moon
        if keys & {"sunapha", "anapha", "durudhara"}:
            assert next(d for d in analysis["doshas"] if d["key"] == "kemadruma")["status"] == "not_present"
        for planet in chart["planets"]:
            assert analysis["strength"][planet]["level"] in ("strong", "medium", "weak")
        assert len(analysis["houses"]) == 12
        assert sorted(p for h in analysis["houses"] for p in h["occupants"]) == sorted(chart["planets"])
