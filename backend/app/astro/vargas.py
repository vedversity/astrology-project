"""Divisional charts (vargas), Parashari method.

Each function takes a sidereal longitude (0-360) and returns the sign index
(0 = Aries ... 11 = Pisces) that point falls in for that divisional chart.
"""


def _split(lon):
    sign = int(lon // 30) % 12
    return sign, lon % 30


def _is_odd(sign):
    # Aries, Gemini, Leo ... are the "odd" signs (1st, 3rd, 5th ...)
    return sign % 2 == 0


def d1(lon):
    return _split(lon)[0]


def d2_hora(lon):
    """Odd signs: first half Sun's hora (Leo), second half Moon's (Cancer). Even signs: reversed."""
    sign, deg = _split(lon)
    first_half = deg < 15
    if _is_odd(sign):
        return 4 if first_half else 3
    return 3 if first_half else 4


def d3_drekkana(lon):
    """Three parts of 10 degrees: same sign, 5th from it, 9th from it."""
    sign, deg = _split(lon)
    return (sign + 4 * int(deg // 10)) % 12


def d7_saptamsa(lon):
    """Seven parts. Odd signs count from the sign itself, even signs from the 7th."""
    sign, deg = _split(lon)
    part = min(int(deg / (30 / 7)), 6)
    start = sign if _is_odd(sign) else sign + 6
    return (start + part) % 12


def d9_navamsa(lon):
    """Nine parts of 3 deg 20 min, running continuously from Aries."""
    return int(lon * 9 // 30) % 12


def d10_dashamsa(lon):
    """Ten parts of 3 degrees. Odd signs count from the sign itself, even signs from the 9th."""
    sign, deg = _split(lon)
    part = int(deg // 3)
    start = sign if _is_odd(sign) else sign + 8
    return (start + part) % 12


def d12_dwadasamsa(lon):
    """Twelve parts of 2 deg 30 min, counted from the sign itself."""
    sign, deg = _split(lon)
    return (sign + int(deg // 2.5)) % 12


VARGAS = {
    "D1": d1,
    "D2": d2_hora,
    "D3": d3_drekkana,
    "D7": d7_saptamsa,
    "D9": d9_navamsa,
    "D10": d10_dashamsa,
    "D12": d12_dwadasamsa,
}
