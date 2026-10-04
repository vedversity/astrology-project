"""A small helper wrapped around the chart, so every rule can ask simple questions.

Everything works on whole signs: two planets are "together" when they share a
sign, and a planet "aspects" a sign, never a degree.
"""

from app.astro import constants as c

SEVEN = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
# The five planets that can form yogas around the Sun and the Moon
FIVE = ["mars", "mercury", "jupiter", "venus", "saturn"]
NODES = ["rahu", "ketu"]
BENEFICS = ["moon", "mercury", "jupiter", "venus"]
MALEFICS = ["sun", "mars", "saturn", "rahu", "ketu"]

KENDRAS = (1, 4, 7, 10)
TRIKONAS = (1, 5, 9)
DUSTHANAS = (6, 8, 12)

# Every planet aspects the 7th house from itself; three planets have extra aspects.
# Rahu and Ketu are given no aspects here.
EXTRA_ASPECTS = {"mars": (4, 8), "jupiter": (5, 9), "saturn": (3, 10)}

STRONG_DIGNITIES = ("exalted", "moolatrikona", "own")

# Which planet is exalted in each sign (sign index -> planet)
EXALTED_IN_SIGN = {sign: planet for planet, sign in c.EXALTATION_SIGN.items()}


def count(from_sign, to_sign):
    """House number of to_sign when from_sign is counted as house 1."""
    return (to_sign - from_sign) % 12 + 1


class ChartView:
    def __init__(self, chart):
        self.chart = chart
        self.planets = chart["planets"]
        self.sign = {key: p["sign"]["index"] for key, p in self.planets.items()}
        # None when the birth time is unknown: house-based rules are then skipped
        self.lagna_sign = chart["lagna"]["sign"]["index"] if chart["lagna"] else None
        self.has_houses = self.lagna_sign is not None

    def dignity(self, planet):
        return self.planets[planet]["dignity"]

    def is_strong(self, planet):
        return self.dignity(planet) in STRONG_DIGNITIES

    def house(self, planet):
        """House from the Lagna (None if the birth time is unknown)."""
        return self.planets[planet]["house"]

    def house_from(self, base, planet):
        """House of `planet` counted from the sign of the planet `base`."""
        return count(self.sign[base], self.sign[planet])

    def in_sign(self, sign, among=None):
        return [p for p in (among or c.PLANET_KEYS) if self.sign[p] == sign]

    def in_house(self, house, among=None):
        return self.in_sign((self.lagna_sign + house - 1) % 12, among)

    def in_house_from(self, base, house, among=None):
        return self.in_sign((self.sign[base] + house - 1) % 12, among)

    def together(self, a, b):
        return self.sign[a] == self.sign[b]

    def companions(self, planet, among=None):
        return [p for p in self.in_sign(self.sign[planet], among) if p != planet]

    def aspected_signs(self, planet):
        if planet in NODES:
            return []
        steps = sorted((7,) + EXTRA_ASPECTS.get(planet, ()))
        return [(self.sign[planet] + step - 1) % 12 for step in steps]

    def aspects_sign(self, planet, sign):
        return sign in self.aspected_signs(planet)

    def aspects(self, planet, other):
        return self.aspects_sign(planet, self.sign[other])

    def sign_of_house(self, house):
        return (self.lagna_sign + house - 1) % 12

    def lord_of_house(self, house):
        return c.SIGN_LORDS[self.sign_of_house(house)]

    def in_kendra_from_lagna(self, planet):
        return self.has_houses and self.house(planet) in KENDRAS

    def in_kendra_from_moon(self, planet):
        return self.house_from("moon", planet) in KENDRAS
