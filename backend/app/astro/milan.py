"""Kundli Milan: Ashtakoot (eight-fold) Guna matching, 36 points in all.

Everything is read from the two Moons: sign, nakshatra and what follows from
them. The tables below are the standard North Indian ones; where almanacs
differ (Vashya and Gana), the choice made is noted for the astrologer to confirm.
"""

from . import constants as c

# ---- 1. Varna (1 point): rank of the Moon sign's element; higher is "senior"
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# ---- 2. Vashya (2 points): rows = groom, columns = bride
VASHYA_ORDER = ["chatushpada", "manav", "jalachar", "vanchar", "keet"]
VASHYA_POINTS = [
    [2, 1, 1, 0.5, 1],
    [1, 2, 0.5, 0, 1],
    [1, 0.5, 2, 1, 1],
    [0, 0, 0, 2, 0],
    [1, 1, 1, 0, 2],
]

# ---- 4. Yoni (4 points): the animal of each nakshatra; the table is the same both ways
YONI_ORDER = ["ashwa", "gaja", "mesha", "sarpa", "shwan", "marjar", "mushak", "gau",
              "mahisha", "vyaghra", "mriga", "vanar", "nakul", "simha"]
YONI_POINTS = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]

# ---- 5. Graha Maitri (5 points): natural friendship between the lords of the two Moon signs
FRIENDS = {
    "sun": ("moon", "mars", "jupiter"), "moon": ("sun", "mercury"), "mars": ("sun", "moon", "jupiter"),
    "mercury": ("sun", "venus"), "jupiter": ("sun", "moon", "mars"), "venus": ("mercury", "saturn"),
    "saturn": ("mercury", "venus"),
}
ENEMIES = {
    "sun": ("venus", "saturn"), "moon": (), "mars": ("mercury",), "mercury": ("moon",),
    "jupiter": ("mercury", "venus"), "venus": ("sun", "moon"), "saturn": ("sun", "moon", "mars"),
}
# (how A sees B, how B sees A) -> points
MAITRI_POINTS = {
    ("friend", "friend"): 5, ("friend", "neutral"): 4, ("neutral", "neutral"): 3,
    ("enemy", "friend"): 1, ("enemy", "neutral"): 0.5, ("enemy", "enemy"): 0,
}

# ---- 6. Gana (6 points): rows = groom, columns = bride; order Deva, Manushya, Rakshasa
GANA_POINTS = [
    [6, 5, 1],
    [6, 6, 0],
    [0, 0, 6],
]

# ---- 7. Bhakoot (7 points): these sign distances give no points
BHAKOOT_BAD = {(2, 12), (5, 9), (6, 8)}

MAX_POINTS = {"varna": 1, "vashya": 2, "tara": 3, "yoni": 4, "maitri": 5, "gana": 6, "bhakoot": 7, "nadi": 8}


def _moon(chart):
    """The pieces of a chart that matching uses."""
    a = chart["avakahada"]
    moon = chart["planets"]["moon"]
    return {
        "sign": a["rashi"]["index"], "nakshatra": a["nakshatra"]["index"], "pada": a["pada"],
        "lord": a["rashi_lord"], "varna": a["varna"]["en"],
        "vashya": next(key for key, pair in c.VASHYAS.items() if pair[0] == a["vashya"]["en"]),
        "yoni": c.NAKSHATRA_YONI[a["nakshatra"]["index"]],
        "gana": c.NAKSHATRA_GANA[a["nakshatra"]["index"]],
        "nadi": c.NADI_PATTERN[a["nakshatra"]["index"] % 6],
        "longitude": moon["longitude"],
    }


def _relation(planet, other):
    if other in FRIENDS[planet]:
        return "friend"
    return "enemy" if other in ENEMIES[planet] else "neutral"


def _tara(from_nakshatra, to_nakshatra):
    """Counting from one birth star to the other: remainders 3, 5 and 7 (of 9) are unfavourable."""
    count = (to_nakshatra - from_nakshatra) % 27 + 1
    return 0 if count % 9 in (3, 5, 7) else 1.5


def ashtakoot(groom_chart, bride_chart):
    """Score the eight kootas. Returns the points, and the facts each one was based on."""
    g, b = _moon(groom_chart), _moon(bride_chart)
    kootas = {}

    kootas["varna"] = {"points": 1 if VARNA_RANK[g["varna"]] >= VARNA_RANK[b["varna"]] else 0}
    kootas["vashya"] = {
        "points": VASHYA_POINTS[VASHYA_ORDER.index(g["vashya"])][VASHYA_ORDER.index(b["vashya"])]}
    kootas["tara"] = {
        "points": _tara(b["nakshatra"], g["nakshatra"]) + _tara(g["nakshatra"], b["nakshatra"])}
    kootas["yoni"] = {"points": YONI_POINTS[YONI_ORDER.index(g["yoni"])][YONI_ORDER.index(b["yoni"])]}

    if g["lord"] == b["lord"]:
        maitri = 5
    else:
        pair = tuple(sorted((_relation(g["lord"], b["lord"]), _relation(b["lord"], g["lord"]))))
        maitri = MAITRI_POINTS[pair]
    kootas["maitri"] = {"points": maitri}

    kootas["gana"] = {"points": GANA_POINTS[g["gana"]][b["gana"]]}

    distance = (b["sign"] - g["sign"]) % 12 + 1
    back = (g["sign"] - b["sign"]) % 12 + 1
    bhakoot_bad = tuple(sorted((distance, back))) in BHAKOOT_BAD
    kootas["bhakoot"] = {"points": 0 if bhakoot_bad else 7, "distance": [distance, back]}

    same_nadi = g["nadi"] == b["nadi"]
    kootas["nadi"] = {"points": 0 if same_nadi else 8}

    # Classical exceptions (parihar). They are reported, not added to the score.
    exceptions = []
    if bhakoot_bad and (g["lord"] == b["lord"] or maitri >= 4):
        exceptions.append("bhakoot_friendly_lords")
    if same_nadi:
        if g["nakshatra"] == b["nakshatra"] and g["pada"] != b["pada"]:
            exceptions.append("nadi_same_nakshatra_different_pada")
        elif g["sign"] == b["sign"] and g["nakshatra"] != b["nakshatra"]:
            exceptions.append("nadi_same_rashi_different_nakshatra")
        elif g["nakshatra"] == b["nakshatra"] and g["sign"] != b["sign"]:
            exceptions.append("nadi_same_nakshatra_different_rashi")

    for key, koota in kootas.items():
        koota["max"] = MAX_POINTS[key]
    total = sum(k["points"] for k in kootas.values())
    return {
        "kootas": kootas,
        "total": total,
        "max": 36,
        "band": "excellent" if total >= 28 else "good" if total >= 21 else "acceptable" if total >= 18 else "review",
        "exceptions": exceptions,
        "facts": {
            who: {
                "varna": chart["avakahada"]["varna"], "vashya": chart["avakahada"]["vashya"],
                "yoni": chart["avakahada"]["yoni"], "gana": chart["avakahada"]["gana"],
                "nadi": chart["avakahada"]["nadi"], "rashi": chart["avakahada"]["rashi"],
                "rashi_lord": c.named(c.PLANETS[chart["avakahada"]["rashi_lord"]]),
                "nakshatra": chart["avakahada"]["nakshatra"], "pada": chart["avakahada"]["pada"],
            }
            for who, chart in (("groom", groom_chart), ("bride", bride_chart))
        },
    }
