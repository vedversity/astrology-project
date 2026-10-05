"""The rule-book and the report wording.

These tests make sure every fact the engines can produce has wording in both
languages, so a report can never come out with a blank or a stray {placeholder}.
"""

import json
import re

import pytest
from fastapi.testclient import TestClient

from app.astro import constants as c
from app.content import RULEBOOK_DIR, load
from app.main import app
from app.report import build_preview, build_report
from tests.darak_sample import BIRTH
from tests.test_rules import random_births

DEVANAGARI = re.compile("[ऀ-ॿ]")
REPORT = build_report(**BIRTH, gender="male", surname="Darak", kuldevi="Ashapura Mata")
CONTENT = REPORT["content"]

YOGA_KEYS = ["ruchaka", "bhadra", "hamsa", "malavya", "shasha", "neecha_bhanga", "guru_mangal",
             "budhaditya", "chandra_mangal", "gaja_kesari", "saraswati", "lakshmi", "parivartana",
             "adhi", "vesi", "vasi", "ubhayachari", "sunapha", "anapha", "durudhara", "vargottama"]
DOSHA_STATUSES = {
    "gandmool": ["not_present", "mild", "present"],
    "manglik": ["not_present", "partial", "present", "cancelled"],
    "kaal_sarp": ["not_present", "present"],
    "vish": ["not_present", "mild", "present"],
    "kemadruma": ["not_present", "cancelled", "present"],
    "grahan": ["not_present", "present"],
    "guru_chandal": ["not_present", "present"],
    "angarak": ["not_present", "present"],
    "pitru": ["not_present", "minor", "present"],
    "sade_sati": ["not_present", "running"],
}


def walk_texts(node, path=""):
    """Yield every {"en": ..., "hi": ...} pair found anywhere inside a structure."""
    if isinstance(node, dict):
        if "en" in node and "hi" in node and isinstance(node["en"], str):
            yield path, node
        for key, value in node.items():
            yield from walk_texts(value, f"{path}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk_texts(value, f"{path}[{i}]")


def check_wording(content):
    for path, text in walk_texts(content):
        for lang in ("en", "hi"):
            assert text[lang].strip() or path.endswith(("reasons", "where")), f"blank text at {path}"
            assert "{" not in text[lang] and "}" not in text[lang], f"unfilled placeholder at {path}"


# ---------- the rule-book files ----------

@pytest.mark.parametrize("path", sorted(RULEBOOK_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_rulebook_file_has_both_languages(path):
    book = json.loads(path.read_text(encoding="utf-8"))
    pairs = list(walk_texts(book))
    assert pairs, "no texts found"
    for where, text in pairs:
        assert text["en"].strip() and text["hi"].strip(), f"blank text at {where}"
        if re.search("[A-Za-z]{3}", re.sub(r"{\w+}", "", text["en"])):
            assert DEVANAGARI.search(text["hi"]), f"Hindi text is not in Devanagari at {where}"
        # The same placeholders must appear in both languages
        assert sorted(set(re.findall(r"{(\w+)}", text["en"]))) == sorted(set(re.findall(r"{(\w+)}", text["hi"]))), where


def test_every_yoga_and_dosha_has_wording():
    yogas = load("yogas")
    for key in YOGA_KEYS:
        assert {"name", "formation", "result"} <= set(yogas[key]), key
    doshas = load("doshas")
    labels = load("labels")["dosha_status"]
    for key, statuses in DOSHA_STATUSES.items():
        for status in statuses:
            assert status in doshas[key]["details"], f"{key}: {status}"
            assert status in labels


def test_tables_are_complete():
    assert len(load("signs")["signs"]) == 12
    assert len(load("nakshatras")["nakshatras"]) == 27
    houses = load("houses")
    assert len(houses["houses"]) == 12
    assert set(houses["planets"]) == set(c.PLANET_KEYS)
    assert all(len(texts) == 12 for texts in houses["planets"].values())
    assert set(load("planets")) - {"_note"} == set(c.PLANET_KEYS)
    assert set(load("numerology")["numbers"]) == {str(n) for n in range(1, 10)}


def test_tone_is_never_fearful():
    banned = ["death", "die ", "fatal", "accident", "disease", "divorce", "curse", "danger",
              "मृत्यु", "मौत", "दुर्घटना", "तलाक", "शाप", "श्राप", "खतरा", "भयंकर"]
    for path in RULEBOOK_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8").lower()
        for word in banned:
            assert word not in text, f"{path.name} contains '{word}'"


# ---------- the sample report ----------

def test_sample_report_wording():
    check_wording(CONTENT)
    json.dumps(REPORT)                                         # must be JSON-ready for the API
    assert [y["name"]["en"] for y in CONTENT["yogas"]][:2] == ["Hamsa Mahapurusha Yoga", "Malavya Mahapurusha Yoga"]
    assert CONTENT["yogas"][6]["name"] == {"en": "Moon-Jupiter Parivartana Yoga", "hi": "चन्द्र-गुरु परिवर्तन योग"}
    assert CONTENT["yogas"][7]["name"]["en"] == "Adhi Yoga (partial)"
    assert len(CONTENT["houses"]) == 12 and len(CONTENT["doshas"]) == 10
    assert len(CONTENT["names"]["suggestions"]) == 10


def test_sample_report_matches_the_pdf():
    doshas = {d["key"]: d for d in CONTENT["doshas"]}
    assert doshas["gandmool"]["status_label"]["en"] == "Present (mild)"
    assert "24 Oct 2026" in doshas["gandmool"]["details"]["en"]
    assert "Jupiter sits with Mars" in doshas["manglik"]["details"]["en"]
    assert "Pratipada Shraddha" in doshas["pitru"]["details"]["en"]

    lucky = CONTENT["lucky"]
    assert lucky["days"]["en"] == "Tuesday, Sunday, Thursday"       # page 9 of the sample
    assert lucky["numbers"] == [9, 1, 3]
    assert "ॐ बुं बुधाय नमः" in lucky["mantras"]                    # the running dasha

    remedies = [r["for"]["en"] for r in CONTENT["remedies"]]
    assert remedies == ["Gandmool", "Vish Yoga", "Shani Sade Sati", "Moon", "Mars (Lagna lord)",
                        "Mercury Mahadasha", "Kuldevi & ancestors", "Gemstones (later)"]
    assert "Red Coral" in CONTENT["remedies"][-1]["text"]["en"]
    assert "Yellow Sapphire" in CONTENT["remedies"][-1]["text"]["en"]

    sanskar = {s["name"]["en"]: s for s in CONTENT["sanskar"]}
    assert "After the Gandmool Shanti" in sanskar["Namkaran"]["when"]["en"]
    assert "2027 / 2029" in sanskar["Mundan"]["when"]["en"]
    assert "Even months" in sanskar["Annaprashan"]["note"]["en"]

    numerology = CONTENT["numerology"]
    assert numerology["surname"]["en"] == "The surname Darak = 10 → 1."
    assert [m["number"] for m in numerology["lo_shu_missing"]] == [3, 4, 5, 8]
    assert CONTENT["nakshatra"]["tree"]["en"] == "Mahua"
    assert "Hamsa" in CONTENT["summary"]["astrologer_note"]["en"]
    assert {"Education", "Marriage"} <= {a["en"] for a in CONTENT["summary"]["strongest_areas"]}


def test_dasha_wording_covers_a_lifetime():
    periods = CONTENT["dasha"]
    assert periods[0]["lord"]["en"] == "Mercury" and periods[0]["age_from"] == 0
    assert [p["lord"]["en"] for p in periods[:4]] == ["Mercury", "Ketu", "Venus", "Sun"]
    assert periods[-1]["age_from"] <= 85 < periods[-1]["age_to"]


def test_girl_report_differs_where_it_should():
    girl = build_report(**BIRTH, gender="female")
    check_wording(girl["content"])
    assert girl["numerology"]["kua"]["number"] == 8
    assert "Odd months" in girl["content"]["sanskar"][1]["note"]["en"]
    assert all(n["en"] not in ("Deepansh", "Devesh") for n in girl["content"]["names"]["suggestions"])
    assert "family deity" in girl["content"]["remedies"][-2]["text"]["en"]     # no Kuldevi given


def test_unknown_time_report():
    report = build_report(BIRTH["date"], None, BIRTH["latitude"], BIRTH["longitude"],
                          BIRTH["timezone"], gender="male")
    content = report["content"]
    check_wording(content)
    assert content["houses"] is None and content["aspects"] is None and content["vargas"] is None
    assert [p["key"] for p in content["predictions"]] == ["personality"]
    assert content["prediction_note"] and content["general"]["time_unknown"]
    assert len(content["general"]["calculation_notes"]) == 2
    assert content["remedies"][-4]["for"]["en"] == "Jupiter (Rashi lord)"


def test_wording_is_complete_on_many_charts():
    seen_yogas, seen_statuses = set(), set()
    for i, (date, time, lat, lon) in enumerate(random_births(120)):
        report = build_report(date, time if i % 6 else None, lat, lon, "Asia/Kolkata",
                              gender="male" if i % 2 else "female", surname="Sharma" if i % 3 else None,
                              today=date)                    # prepared at birth: the child's report
        check_wording(report["content"])
        seen_yogas |= {y["key"] for y in report["content"]["yogas"]}
        seen_statuses |= {(d["key"], d["status"]) for d in report["content"]["doshas"]}
        assert len(report["content"]["names"]["suggestions"]) == 10
    # The spread of charts should exercise nearly all of the rule-book
    assert len(seen_yogas) >= 18
    assert len(seen_statuses) >= 22


# ---------- API ----------

BODY = {"date": "2026-09-27", "time": "20:00", "latitude": 19.0473, "longitude": 73.0718,
        "timezone": "Asia/Kolkata"}


def test_api_preview():
    response = TestClient(app).post("/preview", json=BODY)
    assert response.status_code == 200
    body = response.json()
    assert body["rashi"]["en"] == "Pisces" and body["nakshatra"]["en"] == "Revati" and body["pada"] == 2
    assert body["name_letters"]["primary"]["hi"] == "दो"
    assert "content" not in body and "planets" not in body          # the preview gives away nothing more
    assert body == json.loads(json.dumps(build_preview(**BIRTH)))


def test_api_report():
    response = TestClient(app).post("/report", json={**BODY, "gender": "male", "surname": "Darak"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"audience", "prepared_on", "chart", "analysis", "numerology", "content"}
    assert body["content"]["names"]["suggestions"][0]["en"] == "Deepansh"


def test_api_report_needs_gender():
    assert TestClient(app).post("/report", json=BODY).status_code == 422
    assert TestClient(app).post("/report", json={**BODY, "gender": "other"}).status_code == 422


# ---------- a report for an adult ----------

ADULT_BIRTH = dict(date=__import__("datetime").date(1990, 1, 15), time=__import__("datetime").time(4, 30),
                   latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata")
TODAY = __import__("datetime").date(2026, 10, 5)
# ("infancy" alone is allowed: an adult's Gandmool note says the Shanti is done in infancy)
CHILD_WORDING = re.compile(r"\bthe child\b|\bbaby\b|care in infancy|\btoys?\b|a parent (?:offers|lights)|बच्च|शिशु", re.I)


def test_reader_is_chosen_by_age():
    from app.content import audience_for
    import datetime as dt
    assert audience_for(dt.date(2026, 9, 27), TODAY) == "child"
    assert audience_for(dt.date(2010, 10, 6), TODAY) == "child"      # 15, a day short of 16
    assert audience_for(dt.date(2010, 10, 5), TODAY) == "adult"      # 16 today
    assert build_report(**BIRTH, gender="male", today=TODAY)["audience"] == "child"


def test_adult_report_is_written_for_an_adult():
    report = build_report(**ADULT_BIRTH, gender="male", surname="Sharma", today=TODAY)
    content = report["content"]
    assert report["audience"] == "adult"
    check_wording(content)
    found = CHILD_WORDING.findall(json.dumps(content, ensure_ascii=False))
    assert not found, found
    # No childhood ceremonies and no baby names; the name letters are still shown
    assert content["sanskar"] is None and content["names"]["suggestions"] == []
    assert content["names"]["primary"]["en"]
    # The dasha running today, and remedies and mantras for it rather than for the birth dasha
    now = content["dasha_now"]
    assert now["mahadasha"]["en"] == "Mars" and now["mahadasha_ends"]["en"] == "Aug 2027"
    assert "Mars" in " ".join(r["for"]["en"] for r in content["remedies"])
    assert "the native" in content["predictions"][0]["text"]["en"]
    assert content["remedies"][-1]["for"]["en"] == "Gemstones"


def test_adult_sade_sati_is_checked_for_today():
    # Moon in Pisces, born 1970: Saturn was nowhere near at birth, but is in Pisces in October 2026
    import datetime as dt
    birth = dict(date=dt.date(1970, 3, 9), time=dt.time(10, 0), latitude=19.07, longitude=72.88, timezone="Asia/Kolkata")
    report = build_report(**birth, gender="female", today=TODAY)
    assert report["chart"]["planets"]["moon"]["sign"]["en"] == "Pisces"
    dosha = next(d for d in report["content"]["doshas"] if d["key"] == "sade_sati")
    assert dosha["status"] == "running" and dosha["status_label"]["en"] == "Running now"
    assert "now transiting" in dosha["details"]["en"]
    assert report["chart"]["sade_sati"]["as_of"] == "2026-10-05"


def test_child_wording_is_unchanged_by_the_adult_versions():
    child = build_report(**BIRTH, gender="male", today=TODAY)["content"]
    assert "the child" in child["predictions"][0]["text"]["en"]
    assert child["dasha_now"] is None and len(child["sanskar"]) == 4
    assert "adult" not in json.dumps(child)


def test_adult_wording_is_complete_on_many_charts():
    for i, (date, time, lat, lon) in enumerate(random_births(60, seed=3)):
        if date.year > 2005:
            continue
        report = build_report(date, time if i % 5 else None, lat, lon, "Asia/Kolkata",
                              gender="male" if i % 2 else "female", today=TODAY)
        assert report["audience"] == "adult"
        check_wording(report["content"])
        found = CHILD_WORDING.findall(json.dumps(report["content"], ensure_ascii=False))
        assert not found, (date, found)
