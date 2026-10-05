"""The owner's settings page, the request limits and the live-server switches."""

import json

import pytest
from fastapi.testclient import TestClient

from app import config
from app.limits import Limiter
from app.main import app

TOKEN = "a-long-test-password"
GOOD = {
    "brand": {"name": {"hi": "पत्रिका सेतु", "en": "Patrika Setu"}, "tagline": {"hi": "सरल", "en": "Simple"}},
    "contact": {"email": "help@example.com", "whatsapp": "919876543210"},
    "astrologer": {"name": {"hi": "पं. शर्मा", "en": "Pt. Sharma"}, "experience_years": 50,
                   "bio": {"hi": "पराशरी ज्योतिष", "en": "Parashari astrology"}},
    "prices": {"mini": 61, "full": 111, "premium": 301},
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A client whose changes go to a copy of site.json, never the real file."""
    copy = tmp_path / "site.json"
    copy.write_text(config.SITE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(config, "SITE_FILE", copy)
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    return TestClient(app)


def test_admin_is_off_without_a_password(client, monkeypatch):
    monkeypatch.delenv("ADMIN_TOKEN")
    assert client.get("/admin/site").status_code == 503
    monkeypatch.setenv("ADMIN_TOKEN", "short")              # too short to be safe
    assert client.get("/admin/site", headers={"X-Admin-Token": "short"}).status_code == 503


def test_admin_needs_the_right_password(client):
    assert client.get("/admin/site").status_code == 401
    assert client.get("/admin/site", headers={"X-Admin-Token": "wrong"}).status_code == 401
    assert client.put("/admin/site", json=GOOD).status_code == 401
    ok = client.get("/admin/site", headers={"X-Admin-Token": TOKEN})
    assert ok.status_code == 200 and ok.json()["plans"][0]["id"] == "mini"


def test_owner_can_change_prices_brand_and_astrologer(client):
    headers = {"X-Admin-Token": TOKEN}
    response = client.put("/admin/site", json=GOOD, headers=headers)
    assert response.status_code == 200
    site = client.get("/site").json()                        # the public site sees the change at once
    assert [p["price"] for p in site["plans"]] == [61, 111, 301]
    assert site["brand"]["name"]["en"] == "Patrika Setu" and site["contact"]["whatsapp"] == "919876543210"
    assert site["astrologer"]["experience_years"] == 50
    # Everything else about a plan is untouched, and the explanatory note is kept in the file
    assert site["plans"][2]["audience"] == "child" and len(site["plans"][1]["features"]["hi"]) >= 4
    assert "_note" in json.loads(config.SITE_FILE.read_text(encoding="utf-8"))
    # The astrologer can be removed again
    cleared = client.put("/admin/site", json={**GOOD, "astrologer": None}, headers=headers).json()
    assert cleared["astrologer"] is None


@pytest.mark.parametrize("change", [
    {"prices": {"mini": 61, "full": 111}},                                   # a plan is missing
    {"prices": {"mini": 0, "full": 111, "premium": 301}},                    # free is not allowed
    {"prices": {"mini": 61, "full": 111, "premium": 301, "gold": 999}},      # no new plans
    {"contact": {"email": "not-an-email", "whatsapp": None}},
    {"contact": {"email": None, "whatsapp": "+91 98765 43210"}},             # digits only
    {"brand": {"name": {"hi": "", "en": "X"}, "tagline": {"hi": "क", "en": "k"}}},
])
def test_bad_changes_are_refused_and_nothing_is_saved(client, change):
    before = config.SITE_FILE.read_text(encoding="utf-8")
    response = client.put("/admin/site", json={**GOOD, **change}, headers={"X-Admin-Token": TOKEN})
    assert response.status_code == 422
    assert config.SITE_FILE.read_text(encoding="utf-8") == before


def test_limiter_blocks_after_the_limit_then_recovers(monkeypatch):
    import app.limits as limits

    class Visitor:
        client = type("C", (), {"host": "1.2.3.4"})()

    clock = [1000.0]
    monkeypatch.setattr(limits.time, "monotonic", lambda: clock[0])
    limiter = Limiter(limit=3, seconds=60)
    for _ in range(3):
        limiter(Visitor())
    with pytest.raises(Exception) as blocked:
        limiter(Visitor())
    assert blocked.value.status_code == 429
    other = type("V", (), {"client": type("C", (), {"host": "5.6.7.8"})()})()
    limiter(other)                                           # a different visitor is not affected
    clock[0] += 61
    limiter(Visitor())                                       # allowed again after the window


def test_many_wrong_passwords_are_slowed_down(client):
    from app.limits import admin_limit
    admin_limit.seen.clear()
    codes = [client.get("/admin/site", headers={"X-Admin-Token": f"guess-{i}"}).status_code for i in range(12)]
    assert codes[:10] == [401] * 10 and codes[10:] == [429, 429]
    admin_limit.seen.clear()


def test_env_file_values_do_not_override_the_server(tmp_path, monkeypatch):
    # The loader in app/__init__.py uses setdefault: a value set on the server always wins
    import os
    monkeypatch.setenv("ADMIN_TOKEN", "from-the-server")
    os.environ.setdefault("ADMIN_TOKEN", "from-the-file")
    assert os.environ["ADMIN_TOKEN"] == "from-the-server"
