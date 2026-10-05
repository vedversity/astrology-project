"""Birth-place search: type a few letters, get towns with latitude, longitude and timezone.

The list is bundled with the app (built by scripts/build_places.py from GeoNames,
licence CC BY 4.0), so no outside service is called and no API key is needed.
A customer's typing never leaves our own server.
"""

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data" / "places.json"
COUNTRY_NAMES = {"IN": "India", "US": "USA", "GB": "UK", "CA": "Canada", "AU": "Australia",
                 "AE": "UAE", "SG": "Singapore", "NP": "Nepal", "NZ": "New Zealand"}


@lru_cache(maxsize=None)
def _places():
    """Each place: name, state, country, latitude, longitude, timezone, population, search keys."""
    with open(DATA, encoding="utf-8") as f:
        rows = json.load(f)
    return [(name, state, country, lat, lon, tz, population,
             [name.lower()] + [a.lower() for a in aliases])
            for name, state, country, lat, lon, tz, population, aliases in rows]


def search(query, limit=8):
    """Places whose name starts with the typed text, Indian and larger towns first."""
    q = " ".join(query.lower().split())
    if len(q) < 2:
        return []
    found = []
    for name, state, country, lat, lon, tz, population, keys in _places():
        if keys[0].startswith(q):
            rank = 0
        elif any(key.startswith(q) for key in keys[1:]):
            rank = 1
        elif f" {q}" in keys[0]:
            rank = 2                      # matches a later word, e.g. "mumbai" in "Navi Mumbai"
        else:
            continue
        found.append((rank, country != "IN", -population, name, state, country, lat, lon, tz))
    found.sort()
    return [
        {"name": name,
         "label": ", ".join(part for part in (name, state, COUNTRY_NAMES.get(country, country)) if part),
         "latitude": lat, "longitude": lon, "timezone": tz}
        for _rank, _abroad, _pop, name, state, country, lat, lon, tz in found[:limit]
    ]


__all__ = ["search"]
