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


def test_cities_with_their_own_panchang_page():
    cities = client.get("/cities").json()
    assert len(cities) >= 100
    assert len({c["slug"] for c in cities}) == len(cities)
    by_slug = {c["slug"]: c for c in cities}
    assert by_slug["varanasi"]["hi"] == "वाराणसी" and by_slug["navi-mumbai"]["name"] == "Navi Mumbai"
    for name in ("delhi", "bengaluru", "prayagraj", "mysuru", "gurugram", "lucknow"):
        assert name in by_slug, name
    assert all(c["timezone"] == "Asia/Kolkata" and 6 < c["latitude"] < 36 for c in cities)


def test_guide_nakshatras():
    listing = client.get("/guide/nakshatras").json()
    assert len(listing) == 27 and listing[0]["slug"] == "ashwini" and listing[26]["slug"] == "revati"
    revati = client.get("/guide/nakshatras/revati").json()
    assert [l["en"] for l in revati["letters"]] == ["De", "Do", "Cha", "Chi"]
    assert revati["lord"]["en"] == "Mercury" and revati["rashis"][0]["en"] == "Pisces" and revati["gandmool"]
    assert revati["tree"]["en"] == "Mahua" and revati["previous"] == "uttara-bhadrapada" and revati["next"] == "ashwini"
    names = {n["en"]: n for n in revati["names"]}
    assert names["Devesh"]["pada"] == 1 and names["Chinmay"]["pada"] == 4 and names["Devesh"]["number"] == 1
    assert names["Deepansh"]["pada"] is None                 # same sound, different vowel
    assert "Aarav" not in names
    # Krittika spans two rashis
    assert [r["en"] for r in client.get("/guide/nakshatras/krittika").json()["rashis"]] == ["Aries", "Taurus"]
    assert client.get("/guide/nakshatras/nowhere").status_code == 404
    for item in listing:                                     # every nakshatra page has names to show
        page = client.get(f"/guide/nakshatras/{item['slug']}").json()
        assert len(page["names"]) >= 5, item["slug"]


def test_guide_planets():
    planets = client.get("/guide/planets").json()
    assert [p["slug"] for p in planets] == ["surya", "chandra", "mangal", "budh", "guru", "shukra",
                                           "shani", "rahu", "ketu"]
    for planet in planets:
        assert len(planet["houses"]) == 12
        assert all(h["text"]["hi"] and h["text"]["en"] for h in planet["houses"])
    assert planets[4]["name"]["hi"] == "गुरु" and "4th" in planets[4]["houses"][3]["text"]["en"]
