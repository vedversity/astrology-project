"""Build the place list used by the birth-place search box.

The data comes from GeoNames (https://www.geonames.org, licence CC BY 4.0).
Download and unzip these three files into one folder, then run:

    .venv\Scripts\python scripts\build_places.py <folder>

    https://download.geonames.org/export/dump/cities5000.zip      (towns of India)
    https://download.geonames.org/export/dump/cities15000.zip     (cities of the world)
    https://download.geonames.org/export/dump/admin1CodesASCII.txt (state names)

It writes app/places/data/places.json: every Indian town above 5,000 people and
every city elsewhere above 50,000, with latitude, longitude and timezone.
"""

import json
import re
import sys
from pathlib import Path

WORLD_MIN_POPULATION = 50000
ALIAS_MIN_POPULATION = 100000
DEVANAGARI = re.compile(r"^[ऀ-ॿ ]+$")
PLAIN = re.compile(r"^[A-Za-z][A-Za-z .'-]{3,}$")
OUT = Path(__file__).resolve().parent.parent / "app" / "places" / "data" / "places.json"


def rows(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n").split("\t")


def main(folder):
    folder = Path(folder)
    states = {r[0]: r[1] for r in rows(folder / "admin1CodesASCII.txt")}
    places = {}
    for filename, keep in (("cities5000.txt", lambda r: r[8] == "IN"),
                           ("cities15000.txt", lambda r: r[8] != "IN" and int(r[14]) >= WORLD_MIN_POPULATION)):
        for r in rows(folder / filename):
            if not keep(r):
                continue
            alternates = r[3].split(",") if r[3] else []
            # Extra spellings people may type: Hindi names, and for big Indian cities the
            # older English ones such as Bombay or Banaras. Used for searching only.
            aliases = {a for a in alternates if DEVANAGARI.match(a)}
            if r[8] == "IN" and int(r[14]) >= ALIAS_MIN_POPULATION:
                aliases |= {a for a in alternates if PLAIN.match(a) and a.lower() != r[2].lower()}
            places[r[0]] = [r[2], states.get(f"{r[8]}.{r[10]}", ""), r[8], round(float(r[4]), 4),
                            round(float(r[5]), 4), r[17], int(r[14]), sorted(aliases)]
    ordered = sorted(places.values(), key=lambda p: -p[6])
    OUT.write_text(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    india = sum(1 for p in ordered if p[2] == "IN")
    print(f"wrote {OUT}: {len(ordered)} places ({india} in India), {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1])
