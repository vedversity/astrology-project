"""Kundli Milan: the eight kootas, checked by hand-worked cases and by rules that must always hold."""

import datetime as dt

from fastapi.testclient import TestClient

from app.astro import calculate_chart
from app.astro import constants as c
from app.astro import milan
from app.main import app
from app.report import build_milan
from tests.darak_sample import BIRTH
from tests.test_content import check_wording
from tests.test_rules import random_births


def fake_chart(nakshatra, pada=1):
    """A chart with the Moon at the start of a nakshatra pada (all that matching reads)."""
    lon = nakshatra * c.NAK_SPAN + (pada - 1) * c.PADA_SPAN + 0.5
    sign = int(lon // 30)
    from app.astro.avakahada import avakahada
    return {"avakahada": avakahada(lon), "planets": {"moon": {"longitude": lon, "sign": {"index": sign}}}}


REVATI, ROHINI, ASHWINI, MAGHA = 26, 3, 0, 9


def points(result):
    return {key: koota["points"] for key, koota in result["kootas"].items()}


def test_hand_worked_match():
    # Groom: Moon in Revati (Pisces). Bride: Moon in Rohini (Taurus).
    result = milan.ashtakoot(fake_chart(REVATI, 2), fake_chart(ROHINI, 2))
    assert points(result) == {
        "varna": 1,       # Brahmin groom, Vaishya bride
        "vashya": 1,      # Jalachar with Chatushpada
        "tara": 1.5,      # Rohini to Revati counts 24 (good); Revati to Rohini counts 5 (not)
        "yoni": 3,        # Elephant with Serpent
        "maitri": 0.5,    # Jupiter sees Venus as an enemy; Venus sees Jupiter as neutral
        "gana": 5,        # Deva groom, Manushya bride
        "bhakoot": 7,     # signs 3 and 11 apart
        "nadi": 0,        # both Antya
    }
    assert result["total"] == 19 and result["band"] == "acceptable"


def test_same_birth_star_is_the_classic_exception():
    same = milan.ashtakoot(fake_chart(REVATI, 1), fake_chart(REVATI, 3))
    assert points(same)["nadi"] == 0 and points(same)["bhakoot"] == 7 and points(same)["yoni"] == 4
    assert same["exceptions"] == ["nadi_same_nakshatra_different_pada"]
    assert same["total"] == 28 and same["band"] == "excellent"


def test_bhakoot_dosha_and_its_cancellation():
    # Aries and Scorpio are 6/8 apart but share a lord (Mars), so the dosha is cancelled
    result = milan.ashtakoot(fake_chart(ASHWINI), fake_chart(16))        # Anuradha, in Scorpio
    assert result["kootas"]["bhakoot"]["points"] == 0
    assert "bhakoot_friendly_lords" in result["exceptions"] and points(result)["maitri"] == 5
    # Aries and Virgo are 6/8 apart with unfriendly lords (Mars, Mercury): no cancellation
    plain = milan.ashtakoot(fake_chart(ASHWINI), fake_chart(12))         # Hasta, in Virgo
    assert plain["kootas"]["bhakoot"]["points"] == 0 and plain["exceptions"] == []


def test_tables_are_sound():
    assert sum(milan.MAX_POINTS.values()) == 36
    for i in range(14):
        assert milan.YONI_POINTS[i][i] == 4
        for j in range(14):
            assert milan.YONI_POINTS[i][j] == milan.YONI_POINTS[j][i]
    enemies = [("ashwa", "mahisha"), ("gaja", "simha"), ("mesha", "vanar"), ("sarpa", "nakul"),
               ("shwan", "mriga"), ("marjar", "mushak"), ("gau", "vyaghra")]
    for a, b in enemies:
        assert milan.YONI_POINTS[milan.YONI_ORDER.index(a)][milan.YONI_ORDER.index(b)] == 0
    for planet, friends in milan.FRIENDS.items():
        assert not set(friends) & set(milan.ENEMIES[planet])
    assert all(row[i] == 2 for i, row in enumerate(milan.VASHYA_POINTS))
    assert all(row[i] == 6 for i, row in enumerate(milan.GANA_POINTS))


def test_every_pair_of_stars_scores_within_range():
    seen = set()
    for g in range(27):
        for b in range(27):
            result = milan.ashtakoot(fake_chart(g, 2), fake_chart(b, 3))
            assert 0 <= result["total"] <= 36
            for key, koota in result["kootas"].items():
                assert 0 <= koota["points"] <= koota["max"], (g, b, key)
            seen.add(result["band"])
    assert seen == {"excellent", "good", "acceptable", "review"}


def test_report_for_two_real_births():
    groom = dict(BIRTH)
    bride = dict(date=dt.date(2027, 3, 14), time=dt.time(9, 15), latitude=26.9124, longitude=75.7873,
                 timezone="Asia/Kolkata")
    result = build_milan(groom, bride)
    check_wording(result)
    assert len(result["kootas"]) == 8 and sum(k["points"] for k in result["kootas"]) == result["total"]
    assert result["people"]["groom"]["nakshatra"]["en"] == "Revati"
    assert str(int(result["total"])) in result["text"]["en"]
    assert result["manglik"]["groom"]["status"] == "cancelled" and result["manglik"]["note"] is None
    # Without the bride's time the Lagna check is not possible, and the report says so
    unknown = build_milan(groom, {**bride, "time": None})
    assert unknown["manglik"]["note"] and unknown["people"]["bride"]["time_known"] is False


def test_wording_on_many_pairs():
    births = list(random_births(40, seed=5))
    for (d1, t1, lat1, lon1), (d2, t2, lat2, lon2) in zip(births[::2], births[1::2]):
        result = build_milan(dict(date=d1, time=t1, latitude=lat1, longitude=lon1),
                             dict(date=d2, time=t2, latitude=lat2, longitude=lon2))
        check_wording(result)
        assert result["manglik"]["text"]["hi"]


def test_api_milan():
    client = TestClient(app)
    person = {"date": "2026-09-27", "time": "20:00", "latitude": 19.0473, "longitude": 73.0718}
    response = client.post("/milan", json={"groom": person, "bride": {**person, "date": "2027-03-14"}})
    assert response.status_code == 200
    assert response.json()["max"] == 36 and len(response.json()["kootas"]) == 8
    assert client.post("/milan", json={"groom": person}).status_code == 422


def test_milan_pdf_page():
    from app.pdf import build_milan_html
    groom = dict(BIRTH)
    bride = dict(date=dt.date(2027, 3, 14), time=dt.time(9, 15), latitude=26.9124, longitude=75.7873,
                 timezone="Asia/Kolkata")
    result = build_milan(groom, bride)
    people = ({"name": "Rohan <b>", "date": groom["date"], "time": groom["time"], "place": "Kharghar"},
              {"name": None, "date": bride["date"], "time": None, "place": None})
    for lang, title in (("hi", "कुल गुण"), ("en", "Total gunas")):
        html = build_milan_html(result, *people, lang=lang)
        assert html.count('<section class="page">') == 1 and title in html
        assert "{{" not in html and "Rohan &lt;b&gt;" in html          # typed text is escaped
        assert f"{result['total']:g} / 36" in html
    assert "27 Sep 2026, 08:00 PM · Kharghar" in build_milan_html(result, *people, lang="en")
    assert "Bride" in build_milan_html(result, *people, lang="en")       # no name given


def test_api_milan_pdf():
    import pytest
    sync_api = pytest.importorskip("playwright.sync_api")
    try:
        with sync_api.sync_playwright() as p:
            p.chromium.launch().close()
    except Exception as error:
        pytest.skip(f"Chromium is not installed: {error}")
    person = {"date": "2026-09-27", "time": "20:00", "latitude": 19.0473, "longitude": 73.0718}
    response = TestClient(app).post("/milan/pdf", json={
        "groom": person, "bride": {**person, "date": "2027-03-14"}, "groom_name": "रोहन", "lang": "hi"})
    assert response.status_code == 200 and response.content.startswith(b"%PDF")
