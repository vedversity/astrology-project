"""Simple, transparent strength scores for planets and houses.

This is a points system, not classical Shadbala. Each point is listed with its
reason so the astrologer can see why a planet landed where it did and adjust
the numbers below.
"""

from app.astro import constants as c

from .chartview import BENEFICS, DUSTHANAS, KENDRAS, MALEFICS, NODES, SEVEN, TRIKONAS

DIGNITY_POINTS = {"exalted": 3, "moolatrikona": 2, "own": 2, "debilitated": -3}
# Malefics do well in these houses
MALEFIC_GOOD_HOUSES = (3, 6, 11)

PLANET_STRONG_FROM = 2    # this many points or more = strong
HOUSE_STRONG_FROM = 1
WEAK_BELOW = 0            # fewer than this = needs support


def _level(score, strong_from):
    if score >= strong_from:
        return "strong"
    return "weak" if score < WEAK_BELOW else "medium"


def planet_strength(v, neecha_bhanga=()):
    """neecha_bhanga: planets whose debilitation is cancelled (noted, but no points added)."""
    vargottama = v.chart.get("vargottama") or []
    out = {}
    for planet in c.PLANET_KEYS:
        score = 0
        reasons = []

        def add(points, reason):
            nonlocal score
            score += points
            reasons.append(reason)

        dignity = v.dignity(planet)
        if dignity in DIGNITY_POINTS:
            add(DIGNITY_POINTS[dignity], dignity)

        house = v.house(planet)
        if house is not None:
            if planet in MALEFICS and house in MALEFIC_GOOD_HOUSES:
                # Rahu and Ketu have no dignity, so a good house counts double for them
                add(2 if planet in NODES else 1, "upachaya")
            elif house in KENDRAS:
                add(1, "kendra")
            elif house in TRIKONAS:
                add(1, "trikona")
            elif house in DUSTHANAS:
                add(-1, "dusthana")

        if planet in vargottama:
            add(1, "vargottama")
        if planet != "jupiter" and (v.together("jupiter", planet) or v.aspects("jupiter", planet)):
            add(1, "jupiter_support")
        if any(p in ("mars", "saturn", "rahu", "ketu") for p in v.companions(planet)):
            add(-1, "with_malefic")

        if planet in neecha_bhanga:
            reasons.append("neecha_bhanga")

        out[planet] = {"score": score, "level": _level(score, PLANET_STRONG_FROM),
                       "reasons": reasons, "retrograde": v.planets[planet]["retrograde"]}
    return out


def _occupant_points(planet, house, strength):
    level = strength[planet]["level"]
    if level == "strong":
        return 2
    if level == "weak":
        return 0 if "neecha_bhanga" in strength[planet]["reasons"] else -1
    if planet in BENEFICS or house in MALEFIC_GOOD_HOUSES:
        return 1
    return -1


def house_table(v, strength):
    """One row per house: sign, lord, where the lord sits, who is inside, who aspects it."""
    rows = []
    for house in range(1, 13):
        sign = v.sign_of_house(house)
        lord = c.SIGN_LORDS[sign]
        lord_house = v.house(lord)
        occupants = v.in_house(house)
        aspected_by = [p for p in SEVEN if v.aspects_sign(p, sign)]

        score = sum(_occupant_points(p, house, strength) for p in occupants)
        # The lord's own score already includes where it sits, so it counts once: -1, 0 or +1
        score += max(-1, min(1, strength[lord]["score"]))
        if any(p in aspected_by for p in ("jupiter", "venus", "mercury")):
            score += 1

        rows.append({
            "house": house,
            "sign": c.named(c.SIGNS[sign], sign),
            "lord": lord,
            "lord_house": lord_house,
            "lord_dignity": v.dignity(lord),
            "occupants": occupants,
            "aspected_by": aspected_by,
            "score": score,
            "level": _level(score, HOUSE_STRONG_FROM),
        })
    return rows
