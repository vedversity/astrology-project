"""Life areas (education, career, wealth ...): how well the chart supports each one.

Each area looks at a few houses, a few natural significator planets and the
yogas that help it. The result picks which of the three rule-book paragraphs
(strong / medium / weak) is printed. Needs a known birth time.
"""

from .chartview import KENDRAS, TRIKONAS

# area: (houses, significator planets, yogas that support it)
AREAS = {
    "education": ((4, 5), ("mercury", "jupiter"), ("saraswati", "budhaditya", "bhadra", "hamsa")),
    "career": ((10,), ("sun", "saturn"),
               ("ruchaka", "bhadra", "hamsa", "malavya", "shasha", "lakshmi", "neecha_bhanga")),
    "wealth": ((2, 11), ("jupiter", "venus"), ("lakshmi", "sunapha", "durudhara", "adhi", "chandra_mangal")),
    "health": ((1, 6), ("sun",), ()),
    "family": ((2, 4, 9), ("moon",), ("hamsa", "gaja_kesari")),
    "marriage": ((7,), ("venus",), ("malavya",)),
}
LEVEL_POINTS = {"strong": 1, "medium": 0, "weak": -1}
AREA_STRONG_FROM = 2


def _foreign(v):
    """Count the classical signs of a link with foreign lands."""
    signs = 0
    if v.in_house(12):
        signs += 1
    if v.house("rahu") in (1, 7, 9, 12):
        signs += 1
    if v.house(v.lord_of_house(1)) == 12:
        signs += 1
    if v.house(v.lord_of_house(10)) in (9, 12):
        signs += 1
    if v.house(v.lord_of_house(12)) in KENDRAS + TRIKONAS:
        signs += 1
    return {"score": signs, "level": "strong" if signs >= 2 else "medium" if signs == 1 else "weak",
            "yogas": []}


def life_areas(v, strength, houses, yogas):
    present = [y["key"] for y in yogas]
    out = {}
    for area, (area_houses, planets, area_yogas) in AREAS.items():
        helping = [key for key in area_yogas if key in present]
        score = sum(LEVEL_POINTS[houses[h - 1]["level"]] for h in area_houses)
        score += sum(LEVEL_POINTS[strength[p]["level"]] for p in planets)
        if area == "health":
            # The Lagna lord carries the body's vitality
            score += LEVEL_POINTS[strength[v.lord_of_house(1)]["level"]]
        if helping:
            score += 1
        level = "strong" if score >= AREA_STRONG_FROM else "weak" if score < 0 else "medium"
        out[area] = {"score": score, "level": level, "yogas": helping}
    out["foreign"] = _foreign(v)
    # Planets that colour the career: the 10th lord and anyone sitting in the 10th
    out["career"]["planets"] = list(dict.fromkeys([v.lord_of_house(10)] + v.in_house(10)))
    return out
