"""What the website needs from the API: place search, and the brand, plans and prices."""

from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.pdf import PAGE_COUNT, VARIANTS
from app.places import search

client = TestClient(app)


def test_place_search_finds_the_sample_birthplace():
    found = search("khargh")
    assert found[0]["label"] == "Kharghar, Maharashtra, India"
    # Within a few kilometres of the hospital's coordinates used in the sample chart
    assert abs(found[0]["latitude"] - 19.0473) < 0.05 and abs(found[0]["longitude"] - 73.0718) < 0.05
    assert found[0]["timezone"] == "Asia/Kolkata"


def test_place_search_understands_old_and_hindi_names():
    assert search("bombay")[0]["name"] == "Mumbai"
    assert search("banaras")[0]["name"] == "Varanasi"
    assert search("वाराणसी")[0]["name"] == "Varanasi"
    assert search("  JAIPUR ")[0]["name"] == "Jaipur"


def test_place_search_prefers_india_and_bigger_towns():
    names = [p["name"] for p in search("del")]
    assert names[0] == "Delhi"
    assert search("london")[0]["label"] == "London, England, UK"
    assert search("new york")[0]["timezone"] == "America/New_York"


def test_place_search_limits_and_empty_results():
    assert len(search("a" * 2)) <= 8
    assert search("x") == [] and search("zzzzqq") == []


def test_every_place_has_a_usable_timezone():
    zones = {p["timezone"] for q in ("mum", "lon", "new", "syd", "dub", "tor", "sin") for p in search(q)}
    for zone in zones:
        ZoneInfo(zone)                                       # raises if the name is not valid


def test_api_places():
    response = client.get("/places", params={"q": "vara"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Varanasi"
    assert client.get("/places", params={"q": "v"}).status_code == 422      # too short


def test_site_config_lists_a_price_for_every_pdf_variant():
    site = config.site()
    assert site["brand"]["name"]["hi"] and site["brand"]["name"]["en"]
    plans = {plan["id"]: plan for plan in site["plans"]}
    assert set(plans) == set(VARIANTS)
    for plan_id, plan in plans.items():
        assert isinstance(plan["price"], int) and plan["price"] > 0
        assert plan["pages"] == PAGE_COUNT[plan_id]          # the site must not promise more pages
        for field in ("name", "summary", "features"):
            assert plan[field]["hi"] and plan[field]["en"]
    assert plans["mini"]["price"] < plans["full"]["price"] < plans["premium"]["price"]
    assert config.plan("full")["price"] == plans["full"]["price"] and config.plan("gold") is None


def test_api_site_and_cors_for_the_website():
    response = client.get("/site", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert [plan["id"] for plan in response.json()["plans"]] == ["mini", "full", "premium"]
    # An unknown website is not allowed to call the API from a browser
    other = client.get("/site", headers={"Origin": "https://example.com"})
    assert "access-control-allow-origin" not in other.headers


def test_api_panchang_for_a_day_and_place():
    response = client.get("/panchang", params={"latitude": 19.0473, "longitude": 73.0718, "date": "2026-09-27"})
    assert response.status_code == 200
    body = response.json()
    # Taken at sunrise, as almanacs print it: the same day as the sample birth, earlier nakshatra
    assert body["weekday"]["en"] == "Sunday" and body["tithi"]["en"] == "Pratipada"
    assert body["paksha"]["en"] == "Krishna" and body["nakshatra"]["en"] == "Uttara Bhadrapada"
    assert body["sunrise"].startswith("2026-09-27T06:27") and body["sunset"].startswith("2026-09-27T18:29")
    assert body["rahu_kaal"]["start"].startswith("2026-09-27T16:59")
    assert body["moon_sign"]["en"] == "Pisces" and body["vikram_samvat"] == 2083


def test_api_panchang_defaults_to_today_and_checks_input():
    today = client.get("/panchang", params={"latitude": 28.6139, "longitude": 77.209})
    assert today.status_code == 200 and today.json()["sunrise"] < today.json()["sunset"]
    bad_zone = client.get("/panchang", params={"latitude": 28.6, "longitude": 77.2, "timezone": "Mars/Olympus"})
    assert bad_zone.status_code == 422
    assert client.get("/panchang", params={"latitude": 95, "longitude": 77.2}).status_code == 422
