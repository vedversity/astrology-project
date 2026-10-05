"""The one function the rest of the product calls: calculate_chart().

It returns a plain dictionary (JSON-ready) holding every calculated value the
Janam Patrika needs. No interpretation text lives here - only numbers and names.
"""

import datetime as dt
from zoneinfo import ZoneInfo

from . import constants as c
from . import ephemeris as eph
from .avakahada import avakahada
from .dasha import vimshottari
from .panchang import panchang
from .transits import gandmool, sade_sati
from .vargas import VARGAS

# Stored with every chart so an old report can be reproduced exactly
ENGINE_VERSION = "1.0.0"


def format_dms(degrees):
    """9.4712 -> '09° 28′' (rounded to the nearest minute, never rolling into the next sign)."""
    total_minutes = min(round(degrees * 60), 30 * 60 - 1)
    return f"{total_minutes // 60:02d}° {total_minutes % 60:02d}′"


def _dignity(planet, sign, deg):
    if planet in ("rahu", "ketu"):
        return None
    # Moon and Mercury are exalted and moolatrikona inside the same sign
    if planet == "moon" and sign == 1:
        return "exalted" if deg < 3 else "moolatrikona"
    if planet == "mercury" and sign == 5:
        if deg < 15:
            return "exalted"
        return "moolatrikona" if deg < 20 else "own"
    if sign == c.EXALTATION_SIGN[planet]:
        return "exalted"
    if sign == (c.EXALTATION_SIGN[planet] + 6) % 12:
        return "debilitated"
    mt_sign, mt_from, mt_to = c.MOOLATRIKONA[planet]
    if sign == mt_sign and mt_from <= deg < mt_to:
        return "moolatrikona"
    if c.SIGN_LORDS[sign] == planet:
        return "own"
    return "none"


def _position(lon, lagna_sign):
    """Describe one point of the zodiac: sign, degree, nakshatra, pada, house."""
    sign = int(lon // 30)
    deg = lon % 30
    nak = int(lon // c.NAK_SPAN)
    return {
        "longitude": round(lon, 6),
        "sign": c.named(c.SIGNS[sign], sign),
        "degree_in_sign": round(deg, 6),
        "degree_text": format_dms(deg),
        "nakshatra": c.named(c.NAKSHATRAS[nak], nak),
        "pada": int((lon % c.NAK_SPAN) // c.PADA_SPAN) + 1,
        "nakshatra_lord": c.DASHA_ORDER[nak % 9],
        # Whole-sign houses: the Lagna's sign is house 1, the next sign house 2 ...
        "house": None if lagna_sign is None else (sign - lagna_sign) % 12 + 1,
    }


def _chara_karakas(planets):
    """Jaimini karakas: the seven planets ranked by degree within their sign, highest first."""
    seven = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    ranked = sorted(seven, key=lambda p: planets[p]["degree_in_sign"], reverse=True)
    return {key: planet for (key, _label), planet in zip(c.CHARA_KARAKAS, ranked)}


def _vargas(longitudes):
    """Sign of every point in each divisional chart, plus its house in that chart."""
    out = {}
    for name, sign_of in VARGAS.items():
        lagna_sign = sign_of(longitudes["lagna"])
        chart = {}
        for key, lon in longitudes.items():
            sign = sign_of(lon)
            chart[key] = {
                "sign": c.named(c.SIGNS[sign], sign),
                "house": (sign - lagna_sign) % 12 + 1,
            }
        out[name] = chart
    return out


def _moon_certainty(local_dt):
    """When the birth time is unknown: does the Moon change sign/nakshatra/pada that day?"""
    start = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    lon_start = eph.moon_longitude(eph.to_jd(start))
    lon_end = eph.moon_longitude(eph.to_jd(start + dt.timedelta(days=1)))
    return {
        "moon_sign_certain": int(lon_start // 30) == int(lon_end // 30),
        "nakshatra_certain": int(lon_start // c.NAK_SPAN) == int(lon_end // c.NAK_SPAN),
        "pada_certain": int(lon_start // c.PADA_SPAN) == int(lon_end // c.PADA_SPAN),
    }


def sade_sati_on(chart, day):
    """Sade Sati as it stands on a later day (for an adult's report), from a chart's Moon."""
    tz = ZoneInfo(chart["input"]["timezone"])
    jd = eph.to_jd(dt.datetime.combine(day, dt.time(12, 0), tzinfo=tz).astimezone(dt.timezone.utc))

    def fmt(jd_value):
        return eph.from_jd(jd_value).astimezone(tz).isoformat(timespec="seconds")

    return sade_sati(jd, chart["planets"]["moon"]["longitude"], fmt)


def calculate_chart(date, time=None, latitude=0.0, longitude=0.0,
                    timezone="Asia/Kolkata", time_known=True):
    """Calculate the full chart.

    date, time : local birth date and time (datetime.date, datetime.time)
    latitude   : degrees, north positive
    longitude  : degrees, east positive
    timezone   : IANA name such as "Asia/Kolkata"
    time_known : False gives a Moon-based chart (noon is used; no Lagna, houses or vargas)
    """
    if time is None:
        time_known = False
    tz = ZoneInfo(timezone)
    local_dt = dt.datetime.combine(date, time if time_known else dt.time(12, 0), tzinfo=tz)
    utc_dt = local_dt.astimezone(dt.timezone.utc)
    jd = eph.to_jd(utc_dt)

    def fmt(jd_value):
        return eph.from_jd(jd_value).astimezone(tz).isoformat(timespec="seconds")

    # --- Lagna and planets ---
    lagna = None
    lagna_sign = None
    if time_known:
        lagna_lon = eph.ascendant(jd, latitude, longitude)
        lagna_sign = int(lagna_lon // 30)
        lagna = _position(lagna_lon, lagna_sign)

    planets = {}
    longitudes = {}
    for key in c.PLANET_KEYS:
        lon, speed = eph.planet(jd, key)
        longitudes[key] = lon
        info = _position(lon, lagna_sign)
        info["name"] = c.named(c.PLANETS[key])
        # Rahu and Ketu always move backwards, so they are not flagged
        info["retrograde"] = speed < 0 and key not in ("rahu", "ketu")
        info["dignity"] = _dignity(key, info["sign"]["index"], info["degree_in_sign"])
        planets[key] = info

    moon_lon = longitudes["moon"]
    moon_sign = int(moon_lon // 30)
    for key, info in planets.items():
        info["house_from_moon"] = (info["sign"]["index"] - moon_sign) % 12 + 1

    ayanamsa = eph.ayanamsa(jd)
    chart = {
        "meta": {
            "engine_version": ENGINE_VERSION,
            "zodiac": "sidereal",
            "ayanamsa": "Lahiri (Chitrapaksha)",
            "houses": "whole-sign",
            "nodes": "mean Rahu/Ketu",
            "time_known": time_known,
        },
        "input": {
            "local_datetime": local_dt.isoformat(timespec="seconds"),
            "utc_datetime": utc_dt.isoformat(timespec="seconds"),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "julian_day": round(jd, 6),
        },
        "ayanamsa": {"degrees": round(ayanamsa, 6), "text": format_dms(ayanamsa)},
        "lagna": lagna,
        "planets": planets,
        "panchang": panchang(jd, longitudes["sun"], moon_lon, local_dt,
                             latitude, longitude, time_known),
        "avakahada": avakahada(moon_lon, planets["moon"]["house"]),
        "jaimini_karakas": _chara_karakas(planets),
        "dasha": vimshottari(moon_lon, jd, lambda j: fmt(j)[:10]),
        "gandmool": gandmool(jd, moon_lon, fmt),
        "sade_sati": sade_sati(jd, moon_lon, fmt),
        "vargas": None,
        "vargottama": None,
    }

    if time_known:
        chart["vargas"] = _vargas({"lagna": lagna["longitude"], **longitudes})
        # Vargottama = same sign in the birth chart and the Navamsa
        chart["vargottama"] = [
            key for key in chart["vargas"]["D1"]
            if chart["vargas"]["D1"][key]["sign"]["index"] == chart["vargas"]["D9"][key]["sign"]["index"]
        ]
    else:
        chart["time_unknown"] = _moon_certainty(local_dt)

    return chart
