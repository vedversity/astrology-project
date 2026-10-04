"""Date calculations that look beyond the birth moment: Gandmool return and Sade Sati."""

from . import constants as c
from . import ephemeris as eph


def gandmool(jd, moon_lon, fmt):
    """Is the birth nakshatra Gandmool, and when does the Moon next return to it (about day 27)?"""
    nak = int(moon_lon // c.NAK_SPAN)
    if nak not in c.GANDMOOL_NAKSHATRAS:
        return {"is_gandmool": False}
    # The Moon comes back after about 27.3 days; start looking a week early
    enters = eph.find_crossing(eph.moon_longitude, jd + 20, nak * c.NAK_SPAN, 13.18)
    leaves = eph.find_crossing(eph.moon_longitude, enters + 0.5, ((nak + 1) * c.NAK_SPAN) % 360, 13.18)
    return {
        "is_gandmool": True,
        "moon_returns": {"start": fmt(enters), "end": fmt(leaves)},
    }


def _saturn_offset(jd, moon_sign):
    """Saturn's sign counted from the Moon sign (0 = same sign, 11 = the sign before)."""
    return (int(eph.planet(jd, "saturn")[0] // 30) - moon_sign) % 12


def sade_sati(jd, moon_lon, fmt):
    """Sade Sati = Saturn passing through the sign before, of, and after the natal Moon."""
    moon_sign = int(moon_lon // 30)
    phases = {11: "rising", 0: "peak", 1: "setting"}
    offset = _saturn_offset(jd, moon_sign)
    if offset not in phases:
        return {"active_at_birth": False}

    # Walk forward day by day. Saturn can step out and come back while retrograde,
    # so we only stop once it has stayed out for more than a year.
    last_inside = jd
    first_exit = None
    t = jd
    while t - jd < 3700:
        t += 1
        if _saturn_offset(t, moon_sign) in phases:
            last_inside = t
        else:
            if first_exit is None:
                first_exit = t
            if t - last_inside > 400:
                break
    return {
        "active_at_birth": True,
        "phase": phases[offset],
        # First time Saturn steps out; it may return for a few months while retrograde
        "first_exit": fmt(first_exit)[:10] if first_exit else None,
        # Last day Saturn is inside for good
        "ends": fmt(last_inside)[:10],
    }
