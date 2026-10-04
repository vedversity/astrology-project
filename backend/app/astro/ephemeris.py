"""Thin wrapper around Swiss Ephemeris (pyswisseph).

This is the ONLY file that talks to Swiss Ephemeris. Settings used everywhere:
sidereal zodiac, Lahiri ayanamsa, mean Rahu/Ketu.

We use the built-in "Moshier" mode, which needs no extra data files and is
accurate to about one arc-second for our date range - far finer than the
arc-minute precision a Janam Patrika prints.
"""

import datetime as dt

import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

_BODY_IDS = {
    "sun": swe.SUN, "moon": swe.MOON, "mars": swe.MARS, "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER, "venus": swe.VENUS, "saturn": swe.SATURN,
    "rahu": swe.MEAN_NODE,
}


def to_jd(utc_dt):
    """Julian Day (UT) for a timezone-aware datetime."""
    utc_dt = utc_dt.astimezone(dt.timezone.utc)
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


def from_jd(jd):
    """UTC datetime for a Julian Day (UT)."""
    year, month, day, hour = swe.revjul(jd)
    base = dt.datetime(year, month, day, tzinfo=dt.timezone.utc)
    return base + dt.timedelta(seconds=round(hour * 3600))


def planet(jd, key):
    """Sidereal longitude (0-360) and daily speed of a planet. Ketu is opposite Rahu."""
    if key == "ketu":
        lon, speed = planet(jd, "rahu")
        return (lon + 180) % 360, speed
    values, _ = swe.calc_ut(jd, _BODY_IDS[key], _FLAGS)
    return values[0] % 360, values[3]


def sun_longitude(jd):
    return planet(jd, "sun")[0]


def moon_longitude(jd):
    return planet(jd, "moon")[0]


def moon_sun_angle(jd):
    """Moon minus Sun (0-360). Every 12 degrees is one tithi."""
    return (moon_longitude(jd) - sun_longitude(jd)) % 360


def sun_moon_sum(jd):
    """Sun plus Moon (0-360). Every 13 deg 20 min is one yoga."""
    return (moon_longitude(jd) + sun_longitude(jd)) % 360


def ayanamsa(jd):
    """Lahiri ayanamsa in degrees."""
    return swe.get_ayanamsa_ut(jd)


def ascendant(jd, latitude, longitude):
    """Sidereal longitude of the Lagna (rising degree)."""
    _cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    return ascmc[0] % 360


def _rise_or_set(jd_start, latitude, longitude, which):
    result, times = swe.rise_trans(
        jd_start, swe.SUN, which, (longitude, latitude, 0.0), 1013.25, 15.0, swe.FLG_MOSEPH
    )
    # result is non-zero where the Sun does not rise/set that day (polar regions)
    return times[0] if result == 0 else None


def next_sunrise(jd_start, latitude, longitude):
    return _rise_or_set(jd_start, latitude, longitude, swe.CALC_RISE)


def next_sunset(jd_start, latitude, longitude):
    return _rise_or_set(jd_start, latitude, longitude, swe.CALC_SET)


def find_crossing(angle_at, jd, target, rate, forward=True):
    """Find when a steadily growing angle reaches `target` degrees.

    angle_at: function jd -> angle in degrees (0-360)
    rate:     rough speed of that angle in degrees per day
    forward:  True = next time after jd, False = most recent time before jd
    """
    current = angle_at(jd)
    if forward:
        t = jd + ((target - current) % 360) / rate
    else:
        t = jd - ((current - target) % 360) / rate
    # Refine: each pass corrects the remaining small error
    for _ in range(30):
        error = (target - angle_at(t) + 180) % 360 - 180
        if abs(error) < 1e-7:
            break
        t += error / rate
    return t
