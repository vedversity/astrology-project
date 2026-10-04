"""Yoga detection. Each rule looks at the chart and returns the facts, never any text.

The wording for every yoga lives in the rule-book (app/content/rulebook/yogas.json)
under the same key, so the astrologer can edit the text without touching this file.
"""

from app.astro import constants as c

from .chartview import EXALTED_IN_SIGN, FIVE, KENDRAS, SEVEN, TRIKONAS

MAHAPURUSHA = {
    "mars": "ruchaka", "mercury": "bhadra", "jupiter": "hamsa",
    "venus": "malavya", "saturn": "shasha",
}
# Signs where Jupiter is exalted, in its own sign, or the guest of a friend (Sun, Moon, Mars)
JUPITER_GOOD_SIGNS = (0, 3, 4, 7, 8, 11)
# Houses that count for Saraswati Yoga: the kendras, the trikonas and the 2nd
SARASWATI_HOUSES = (1, 2, 4, 5, 7, 9, 10)


def _mahapurusha(v):
    """One of the five planets in its own or exaltation sign, in a kendra from the Lagna."""
    found = []
    if not v.has_houses:
        return found
    for planet, key in MAHAPURUSHA.items():
        if v.is_strong(planet) and v.house(planet) in KENDRAS:
            found.append({"key": key, "planets": [planet], "house": v.house(planet),
                          "dignity": v.dignity(planet)})
    return found


def _neecha_bhanga(v):
    """A debilitated planet whose weakness is cancelled. Records which classical reason applies."""
    found = []
    for planet in SEVEN:
        if v.dignity(planet) != "debilitated":
            continue
        sign = v.sign[planet]
        sign_lord = c.SIGN_LORDS[sign]
        exalted_here = EXALTED_IN_SIGN.get(sign)
        exaltation_lord = c.SIGN_LORDS[c.EXALTATION_SIGN[planet]]

        def in_kendra(other):
            # The Moon is always in the 1st from itself, so that case proves nothing
            return v.in_kendra_from_lagna(other) or (other != "moon" and v.in_kendra_from_moon(other))

        reasons = []
        if in_kendra(sign_lord):
            reasons.append("sign_lord_in_kendra")
        if exalted_here and in_kendra(exalted_here):
            reasons.append("exalted_planet_of_sign_in_kendra")
        if in_kendra(exaltation_lord):
            reasons.append("exaltation_lord_in_kendra")
        if any(v.dignity(p) == "exalted" for p in v.companions(planet, SEVEN)):
            reasons.append("joined_by_exalted_planet")
        if sign_lord != planet and v.aspects(sign_lord, planet):
            reasons.append("aspected_by_sign_lord")
        if reasons:
            found.append({"key": "neecha_bhanga", "planets": [planet], "reasons": reasons,
                          "house": v.house(planet)})
    return found


def _conjunctions(v):
    pairs = {"guru_mangal": ("jupiter", "mars"), "budhaditya": ("sun", "mercury"),
             "chandra_mangal": ("moon", "mars")}
    return [{"key": key, "planets": [a, b], "house": v.house(a)}
            for key, (a, b) in pairs.items() if v.together(a, b)]


def _gaja_kesari(v):
    if v.in_kendra_from_moon("jupiter") and not v.together("moon", "jupiter"):
        return [{"key": "gaja_kesari", "planets": ["jupiter", "moon"],
                 "house_from_moon": v.house_from("moon", "jupiter")}]
    return []


def _saraswati(v):
    if not v.has_houses:
        return []
    three = ["jupiter", "venus", "mercury"]
    if all(v.house(p) in SARASWATI_HOUSES for p in three) and v.sign["jupiter"] in JUPITER_GOOD_SIGNS:
        return [{"key": "saraswati", "planets": three, "jupiter_dignity": v.dignity("jupiter")}]
    return []


def _lakshmi(v):
    """Strong 9th lord in a kendra or trikona, backed by a strong Lagna lord or Venus."""
    if not v.has_houses:
        return []
    good_houses = set(KENDRAS + TRIKONAS)

    def well_placed(planet):
        return v.is_strong(planet) and v.house(planet) in good_houses

    ninth_lord = v.lord_of_house(9)
    lagna_lord = v.lord_of_house(1)
    support = [p for p in dict.fromkeys([lagna_lord, "venus"]) if p != ninth_lord and well_placed(p)]
    if well_placed(ninth_lord) and support:
        return [{"key": "lakshmi", "planets": [ninth_lord] + support, "ninth_lord": ninth_lord,
                 "support": support[0]}]
    return []


def _parivartana(v):
    """Two planets sitting in each other's signs."""
    found = []
    for i, a in enumerate(SEVEN):
        for b in SEVEN[i + 1:]:
            if c.SIGN_LORDS[v.sign[a]] == b and c.SIGN_LORDS[v.sign[b]] == a:
                found.append({"key": "parivartana", "planets": [a, b]})
    return found


def _adhi(v):
    """Mercury, Jupiter and Venus in the 6th, 7th or 8th from the Moon (two of them = partial)."""
    present = [p for p in ("mercury", "jupiter", "venus") if v.house_from("moon", p) in (6, 7, 8)]
    if len(present) >= 2:
        return [{"key": "adhi", "planets": present, "partial": len(present) == 2}]
    return []


def _around(v, base, both_key, second_key, twelfth_key):
    """Planets in the 2nd and/or 12th from the Sun or the Moon."""
    second = v.in_house_from(base, 2, FIVE)
    twelfth = v.in_house_from(base, 12, FIVE)
    if second and twelfth:
        return [{"key": both_key, "planets": second + twelfth}]
    if second:
        return [{"key": second_key, "planets": second}]
    if twelfth:
        return [{"key": twelfth_key, "planets": twelfth}]
    return []


def _vargottama(v):
    """Planets in the same sign in the birth chart and the Navamsa."""
    planets = [p for p in (v.chart.get("vargottama") or []) if p != "lagna"]
    return [{"key": "vargottama", "planets": planets}] if planets else []


def find_yogas(v):
    yogas = []
    yogas += _mahapurusha(v)
    yogas += _neecha_bhanga(v)
    yogas += _conjunctions(v)
    yogas += _gaja_kesari(v)
    yogas += _saraswati(v)
    yogas += _lakshmi(v)
    yogas += _parivartana(v)
    yogas += _adhi(v)
    yogas += _around(v, "sun", "ubhayachari", "vesi", "vasi")
    yogas += _around(v, "moon", "durudhara", "sunapha", "anapha")
    yogas += _vargottama(v)
    return yogas
