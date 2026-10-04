"""Avakahada Chakra: the traditional birth attributes read from the Moon's position."""

from . import constants as c


def _vashya(sign, deg):
    if sign in (0, 1):
        return "chatushpada"
    if sign in (2, 5, 6, 10):
        return "manav"
    if sign in (3, 11):
        return "jalachar"
    if sign == 4:
        return "vanchar"
    if sign == 7:
        return "keet"
    if sign == 8:  # Sagittarius: first half human, second half four-footed
        return "manav" if deg < 15 else "chatushpada"
    # Capricorn: first half four-footed, second half water
    return "chatushpada" if deg < 15 else "jalachar"


def avakahada(moon_lon, moon_house=None):
    """moon_house is the Moon's house from the Lagna; pass None if birth time is unknown."""
    sign = int(moon_lon // 30)
    deg = moon_lon % 30
    nak = int(moon_lon // c.NAK_SPAN)
    pada = int((moon_lon % c.NAK_SPAN) // c.PADA_SPAN) + 1
    element = sign % 4

    out = {
        "rashi": c.named(c.SIGNS[sign], sign),
        "rashi_lord": c.SIGN_LORDS[sign],
        "nakshatra": c.named(c.NAKSHATRAS[nak], nak),
        "pada": pada,
        "nakshatra_lord": c.DASHA_ORDER[nak % 9],
        "naam_akshar": c.named(c.NAAM_AKSHAR[nak][pada - 1]),
        "nakshatra_akshar": [c.named(p) for p in c.NAAM_AKSHAR[nak]],
        "varna": c.named(c.VARNAS[element]),
        "vashya": c.named(c.VASHYAS[_vashya(sign, deg)]),
        "yoni": c.named(c.YONIS[c.NAKSHATRA_YONI[nak]]),
        "gana": c.named(c.GANAS[c.NAKSHATRA_GANA[nak]]),
        "nadi": c.named(c.NADIS[c.NADI_PATTERN[nak % 6]]),
        "tatva": c.named(c.ELEMENTS[element]),
        "paya": None,
    }
    if moon_house is not None:
        out["paya"] = c.named(c.PAYAS[c.PAYA_BY_MOON_HOUSE[moon_house]])
    return out
