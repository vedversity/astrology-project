"""Rule engine: reads a calculated chart and reports yogas, doshas and strengths.

It produces facts only (keys, planets, houses, statuses). The words that
explain them come from the rule-book in app/content.
"""

from app.astro import constants as c

from .areas import life_areas
from .chartview import ChartView
from .doshas import find_doshas
from .strength import house_table, planet_strength
from .yogas import find_yogas

RULES_VERSION = "1.0.0"

# Divisional charts whose strong placements are worth a sentence in the report
VARGA_TOPICS = ("D7", "D9", "D10", "D12")


def _aspects(v):
    """For each planet: the houses it aspects and the planets sitting there."""
    out = {}
    for planet in c.PLANET_KEYS:
        signs = v.aspected_signs(planet)
        out[planet] = {
            "from_house": v.house(planet),
            "houses": [(s - v.lagna_sign) % 12 + 1 for s in signs] if v.has_houses else None,
            "signs": signs,
            "planets": [p for s in signs for p in v.in_sign(s)],
        }
    return out


def _varga_highlights(chart):
    """Planets that are exalted or in their own sign in a divisional chart."""
    out = []
    for varga in VARGA_TOPICS:
        for planet, exalted_sign in c.EXALTATION_SIGN.items():
            placed = chart["vargas"][varga][planet]
            sign = placed["sign"]["index"]
            if sign == exalted_sign:
                dignity = "exalted"
            elif c.SIGN_LORDS[sign] == planet:
                dignity = "own"
            else:
                continue
            out.append({"varga": varga, "planet": planet, "dignity": dignity,
                        "sign": placed["sign"], "house": placed["house"]})
    return out


def analyze(chart):
    """Return everything the rule engine can say about a chart."""
    v = ChartView(chart)
    yogas = find_yogas(v)
    cancelled = [p for y in yogas if y["key"] == "neecha_bhanga" for p in y["planets"]]
    strength = planet_strength(v, cancelled)
    houses = house_table(v, strength) if v.has_houses else None
    return {
        "rules_version": RULES_VERSION,
        "aspects": _aspects(v),
        "strength": strength,
        "houses": houses,
        "yogas": yogas,
        "doshas": find_doshas(v),
        "varga_highlights": _varga_highlights(chart) if v.has_houses else None,
        "areas": life_areas(v, strength, houses, yogas) if v.has_houses else None,
    }


__all__ = ["RULES_VERSION", "analyze"]
