"""Name letters (by nakshatra pada and rashi) and name suggestions.

The names database is app/names/data/names.json. To add a name, add one line
there: English spelling, Hindi spelling, gender (boy / girl / unisex), meaning.
The starting letter is read from the Hindi spelling automatically.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.astro import constants as c
from app.numerology import name_number

NAMES_FILE = Path(__file__).parent / "data" / "names.json"

VOWELS = {"अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u",
          "ए": "e", "ऐ": "e", "ओ": "o", "औ": "o"}
MATRAS = {"ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u",
          "े": "e", "ै": "e", "ो": "o", "ौ": "o", "ॉ": "o"}
VIRAMA = "्"
NUKTA = "़"
# Sounds that families treat as the same letter when choosing a name
SAME_SOUND = {"ट": "त", "ठ": "थ", "ड": "द", "ढ": "ध", "ण": "न", "ष": "श"}

# How closely a name's first letter fits the chart (lower is better)
MATCH_LABELS = {1: "birth_pada", 2: "nakshatra", 3: "rashi", 4: "same_consonant"}


def first_sound(hindi):
    """Split the start of a Hindi word into (consonant, vowel sound): दीपांश -> ("द", "i")."""
    first = hindi[0]
    if first in VOWELS:
        return "", VOWELS[first]
    rest = hindi[1:].lstrip(NUKTA)
    # Skip a joined consonant (प्र, श्र ...) so the vowel after it is read
    while rest[:1] == VIRAMA:
        rest = rest[2:].lstrip(NUKTA)
    return SAME_SOUND.get(first, first), MATRAS.get(rest[:1], "a")


def rashi_letters(sign):
    """The nine name syllables of a rashi (each sign holds nine nakshatra padas)."""
    return [c.NAAM_AKSHAR[p // 4][p % 4] for p in range(sign * 9, sign * 9 + 9)]


def name_letters(chart):
    """Name syllables for a chart: the birth pada first, then the nakshatra, then the rashi."""
    a = chart["avakahada"]
    nak = a["nakshatra"]["index"]
    return {
        "primary": a["naam_akshar"],
        "birth_pada": a["pada"],
        "nakshatra": [dict(c.named(pair), pada=i + 1) for i, pair in enumerate(c.NAAM_AKSHAR[nak])],
        "rashi": [c.named(pair) for pair in rashi_letters(a["rashi"]["index"])],
    }


@lru_cache(maxsize=None)
def load_names():
    with open(NAMES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _match_level(name_hi, letters):
    sound = first_sound(name_hi)
    if sound == first_sound(letters["primary"]["hi"]):
        return 1
    if sound in [first_sound(x["hi"]) for x in letters["nakshatra"]]:
        return 2
    if sound in [first_sound(x["hi"]) for x in letters["rashi"]]:
        return 3
    consonants = {first_sound(x["hi"])[0] for x in letters["nakshatra"] + letters["rashi"]}
    return 4 if sound[0] in consonants else None


def rate_name(name, numbers, surname=None):
    """Chaldean numbers of a name and how well they suit the child's Mulank and Bhagyank."""
    rel = numbers["relationship"]
    mulank, bhagyank = numbers["mulank"]["number"], numbers["bhagyank"]["number"]
    compound, single = name_number(name)
    out = {"compound": compound, "number": single, "full_name": None}
    full_single = None
    if surname:
        full_compound, full_single = name_number(name + surname)
        out["full_name"] = {"surname": surname, "compound": full_compound, "number": full_single}
    out["fit"] = "friendly" if single in rel["friendly"] else "avoid" if single in rel["avoid"] else "neutral"
    # A full name that totals an unfriendly number is a poor match, however good the first name
    out["full_name_avoid"] = full_single in rel["avoid"]
    # Two stars: first name matches the Mulank and the full name matches the Bhagyank
    if single == mulank and full_single == bhagyank:
        out["stars"] = 2
    elif single in (mulank, bhagyank):
        out["stars"] = 1
    else:
        out["stars"] = 0
    return out


def suggest_names(chart, gender, numbers, surname=None, limit=10):
    """Names whose first letter suits the chart, best numerology first.

    gender: "male" or "female". numbers: the result of numerology().
    """
    wanted = ("boy", "unisex") if gender == "male" else ("girl", "unisex")
    letters = name_letters(chart)
    found = []
    for entry in load_names():
        if entry["gender"] not in wanted:
            continue
        level = _match_level(entry["hi"], letters)
        if level is None:
            continue
        rating = rate_name(entry["en"], numbers, surname)
        points = (4 - level) + {"friendly": 2, "neutral": 1, "avoid": 0}[rating["fit"]] + 2 * rating["stars"]
        if rating["full_name_avoid"]:
            points -= 2
        found.append({**entry, "match": MATCH_LABELS[level], "numerology": rating, "points": points})

    # Names with an unfriendly number are only used if there is nothing better
    # On equal points, a friendly name number wins
    found.sort(key=lambda n: (n["numerology"]["fit"] == "avoid", -n["points"],
                              n["numerology"]["fit"] != "friendly", n["en"]))
    return found[:limit]


__all__ = ["first_sound", "name_letters", "rashi_letters", "rate_name", "suggest_names"]
