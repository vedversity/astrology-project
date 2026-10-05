"""Reference pages for the website: nakshatras with their names, and planets in houses.

Everything here is read from files that already exist (the rule-book, the names
database, the engine's tables), so these pages always agree with the reports.
"""

from app.astro import constants as c
from app.content import load
from app.names import first_sound, load_names
from app.numerology import name_number

# Web addresses use the familiar Hindi names of the planets
PLANET_SLUGS = {"sun": "surya", "moon": "chandra", "mars": "mangal", "mercury": "budh",
                "jupiter": "guru", "venus": "shukra", "saturn": "shani", "rahu": "rahu", "ketu": "ketu"}


def slug(name):
    """'Purva Phalguni' -> 'purva-phalguni'."""
    return name.lower().replace(" ", "-")


def _nakshatra_basics(index):
    name = c.NAKSHATRAS[index]
    first_pada = index * 4
    last_pada = first_pada + 3
    signs = sorted({first_pada // 9, last_pada // 9})
    return {
        "slug": slug(name[0]),
        "index": index,
        "name": c.named(name),
        "lord": c.named(c.PLANETS[c.DASHA_ORDER[index % 9]]),
        "rashis": [c.named(c.SIGNS[s]) for s in signs],
        "letters": [dict(c.named(pair), pada=i + 1) for i, pair in enumerate(c.NAAM_AKSHAR[index])],
        "gandmool": index in c.GANDMOOL_NAKSHATRAS,
    }


def nakshatras():
    """All 27 nakshatras, for the index page."""
    return [_nakshatra_basics(i) for i in range(27)]


def nakshatra(nakshatra_slug):
    """One nakshatra: its description, its name letters and the names that start with them."""
    index = next((i for i in range(27) if slug(c.NAKSHATRAS[i][0]) == nakshatra_slug), None)
    if index is None:
        return None
    out = _nakshatra_basics(index)
    book = load("nakshatras")["nakshatras"][index]
    out.update(deity=book["deity"], symbol=book["symbol"], tree=book["tree"], nature=book["nature"],
               gana=c.named(c.GANAS[c.NAKSHATRA_GANA[index]]),
               yoni=c.named(c.YONIS[c.NAKSHATRA_YONI[index]]),
               nadi=c.named(c.NADIS[c.NADI_PATTERN[index % 6]]))

    sounds = {first_sound(letter["hi"]): letter for letter in out["letters"]}
    consonants = {sound[0] for sound in sounds}
    names = []
    for entry in load_names():
        sound = first_sound(entry["hi"])
        letter = sounds.get(sound)
        if not letter and sound[0] not in consonants:
            continue
        compound, single = name_number(entry["en"])
        names.append({
            "en": entry["en"], "hi": entry["hi"], "gender": entry["gender"], "meaning": entry["meaning"],
            "number": single,
            # The pada whose letter the name starts with; None = same sound, different vowel
            "pada": letter["pada"] if letter else None,
        })
    names.sort(key=lambda n: (n["pada"] is None, n["pada"] or 0, n["en"]))
    out["names"] = names
    out["previous"] = slug(c.NAKSHATRAS[(index - 1) % 27][0])
    out["next"] = slug(c.NAKSHATRAS[(index + 1) % 27][0])
    return out


def planets():
    """Each planet with its nature and what it means in each of the 12 houses."""
    houses = load("houses")
    book = load("planets")
    out = []
    for key in c.PLANET_KEYS:
        info = book[key]
        out.append({
            "slug": PLANET_SLUGS[key],
            "key": key,
            "name": c.named(c.PLANETS[key]),
            "day": info["day"], "deity": info["deity"], "mantra": info["mantra"],
            "career": info["career"], "period": info["dasha"], "remedy": info["remedy"],
            "houses": [{"house": i + 1, "name": houses["houses"][i]["name"], "text": text}
                       for i, text in enumerate(houses["planets"][key])],
        })
    return out
