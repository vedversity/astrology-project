"""Dosha check. Every dosha is always reported, with a status, so the report can
show the full table (including the reassuring "not present" rows).

Statuses: not_present, present, mild, partial, cancelled, minor, running.
The wording for each status lives in app/content/rulebook/doshas.json.
"""

from .chartview import FIVE, KENDRAS, SEVEN

# North Indian convention. Some traditions also count the 2nd house.
MANGLIK_HOUSES = (1, 4, 7, 8, 12)

# The pada that touches a water-fire sign junction (gandanta) is the strong one
GANDMOOL_STRONG_PADA = {0: 1, 9: 1, 18: 1, 8: 4, 17: 4, 26: 4}


def _gandmool(v):
    info = v.chart["gandmool"]
    if not info["is_gandmool"]:
        return {"key": "gandmool", "status": "not_present"}
    moon = v.planets["moon"]
    nak = moon["nakshatra"]["index"]
    strong = GANDMOOL_STRONG_PADA[nak] == moon["pada"]
    return {"key": "gandmool", "status": "present" if strong else "mild",
            "nakshatra": moon["nakshatra"], "pada": moon["pada"],
            "moon_returns": info["moon_returns"]}


def _manglik(v):
    seen_from = {}
    if v.has_houses:
        seen_from["lagna"] = v.house("mars")
    seen_from["moon"] = v.house_from("moon", "mars")
    seen_from["venus"] = v.house_from("venus", "mars")
    hits = [base for base, house in seen_from.items() if house in MANGLIK_HOUSES]
    out = {"key": "manglik", "status": "not_present", "houses": seen_from, "from": hits}
    if not hits:
        return out

    cancelled_by = []
    if v.together("mars", "jupiter"):
        cancelled_by.append("jupiter_conjunct")
    elif v.aspects("jupiter", "mars"):
        cancelled_by.append("jupiter_aspect")
    if v.dignity("mars") in ("own", "moolatrikona", "exalted"):
        cancelled_by.append("mars_strong")
    out["level"] = "full" if len(hits) == len(seen_from) else "partial"
    out["cancelled_by"] = cancelled_by
    out["status"] = "cancelled" if cancelled_by else ("present" if out["level"] == "full" else "partial")
    return out


def _kaal_sarp(v):
    """All seven planets on one side of the Rahu-Ketu line."""
    rahu = v.planets["rahu"]["longitude"]
    sides = {(v.planets[p]["longitude"] - rahu) % 360 < 180 for p in SEVEN}
    return {"key": "kaal_sarp", "status": "present" if len(sides) == 1 else "not_present"}


def _vish(v):
    if not v.together("moon", "saturn"):
        return {"key": "vish", "status": "not_present"}
    eased = v.aspects("jupiter", "moon") or v.together("jupiter", "moon")
    return {"key": "vish", "status": "mild" if eased else "present", "house": v.house("moon"),
            "eased_by_jupiter": eased}


def _kemadruma(v):
    """Nobody beside the Moon: no planet in the 2nd or 12th from it."""
    if v.in_house_from("moon", 2, FIVE) or v.in_house_from("moon", 12, FIVE):
        return {"key": "kemadruma", "status": "not_present"}
    cancelled_by = []
    if v.companions("moon", FIVE):
        cancelled_by.append("planet_with_moon")
    if v.aspects("jupiter", "moon"):
        cancelled_by.append("jupiter_aspect")
    if any(v.house_from("moon", p) in KENDRAS for p in FIVE if not v.together("moon", p)):
        cancelled_by.append("planet_in_kendra_from_moon")
    if v.has_houses and any(v.house(p) in KENDRAS for p in FIVE):
        cancelled_by.append("planet_in_kendra_from_lagna")
    return {"key": "kemadruma", "status": "cancelled" if cancelled_by else "present",
            "cancelled_by": cancelled_by}


def _with_nodes(v, key, planets):
    """Rahu or Ketu sharing a sign with one of the given planets."""
    joined = [{"planet": p, "node": node} for p in planets for node in ("rahu", "ketu")
              if v.together(p, node)]
    return {"key": key, "status": "present" if joined else "not_present", "joined": joined}


def _pitru(v):
    panchang = v.chart["panchang"]
    out = {
        "key": "pitru", "status": "not_present",
        # The dark half of Bhadrapada (amanta) is Pitru Paksha
        "born_in_pitru_paksha": panchang["maas"]["amanta"]["en"] == "Bhadrapada"
                                and panchang["paksha"]["en"] == "Krishna",
        "tithi": {"en": panchang["tithi"]["en"], "hi": panchang["tithi"]["hi"]},
    }
    if v.together("sun", "rahu") or v.together("sun", "ketu") or (v.has_houses and v.house("rahu") == 9):
        out["status"] = "present"
    elif v.together("sun", "saturn") or v.aspects("saturn", "sun"):
        out["status"] = "minor"
    return out


def _sade_sati(v):
    info = v.chart["sade_sati"]
    if not info["active_at_birth"]:
        return {"key": "sade_sati", "status": "not_present"}
    return {"key": "sade_sati", "status": "running", "phase": info["phase"],
            "ends": info["ends"], "moon_sign": v.planets["moon"]["sign"]}


def find_doshas(v):
    return [
        _gandmool(v),
        _manglik(v),
        _kaal_sarp(v),
        _vish(v),
        _kemadruma(v),
        _with_nodes(v, "grahan", ["sun", "moon"]),
        _with_nodes(v, "guru_chandal", ["jupiter"]),
        _with_nodes(v, "angarak", ["mars"]),
        _pitru(v),
        _sade_sati(v),
    ]
