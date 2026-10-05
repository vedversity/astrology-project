"""Daily tools: Choghadiya (the day's eight day and eight night slots) and the
Moon's transit for each Rashi (the basis of the daily Rashifal)."""

import datetime as dt
from zoneinfo import ZoneInfo

from . import constants as c
from . import ephemeris as eph

# The order in which the slots follow one another by day and by night
DAY_CYCLE = ["udveg", "char", "labh", "amrit", "kaal", "shubh", "rog"]
NIGHT_CYCLE = ["shubh", "amrit", "char", "rog", "kaal", "labh", "udveg"]
# First slot after sunrise and after sunset, index = Python weekday (Monday = 0)
DAY_FIRST = ["amrit", "rog", "labh", "shubh", "char", "kaal", "udveg"]
NIGHT_FIRST = ["char", "kaal", "udveg", "amrit", "rog", "labh", "shubh"]

QUALITY = {"amrit": "good", "shubh": "good", "labh": "good", "char": "neutral",
           "udveg": "avoid", "rog": "avoid", "kaal": "avoid"}

RASHI_SLUGS = ["mesh", "vrishabh", "mithun", "kark", "singh", "kanya",
               "tula", "vrishchik", "dhanu", "makar", "kumbh", "meen"]


def _slots(cycle, first, start, end, fmt):
    length = (end - start) / 8
    at = cycle.index(first)
    return [{"key": cycle[(at + i) % 7], "quality": QUALITY[cycle[(at + i) % 7]],
             "start": fmt(start + i * length), "end": fmt(start + (i + 1) * length)}
            for i in range(8)]


def choghadiya(date, latitude, longitude, timezone="Asia/Kolkata"):
    """The sixteen Choghadiya slots of a date: eight from sunrise, eight from sunset."""
    tz = ZoneInfo(timezone)
    midnight = eph.to_jd(dt.datetime.combine(date, dt.time(0, 0), tzinfo=tz).astimezone(dt.timezone.utc))
    sunrise = eph.next_sunrise(midnight, latitude, longitude)
    sunset = eph.next_sunset(sunrise, latitude, longitude)
    following = eph.next_sunrise(sunset, latitude, longitude)

    def fmt(jd):
        return eph.from_jd(jd).astimezone(tz).isoformat(timespec="seconds")

    weekday = date.weekday()
    return {
        "day": _slots(DAY_CYCLE, DAY_FIRST[weekday], sunrise, sunset, fmt),
        "night": _slots(NIGHT_CYCLE, NIGHT_FIRST[weekday], sunset, following, fmt),
    }


def moon_transit(date, timezone="Asia/Kolkata"):
    """Where the Moon is on a date (taken at 6 a.m.), and its house from each of the 12 Rashis."""
    tz = ZoneInfo(timezone)
    jd = eph.to_jd(dt.datetime.combine(date, dt.time(6, 0), tzinfo=tz).astimezone(dt.timezone.utc))
    lon = eph.moon_longitude(jd)
    sign = int(lon // 30)
    nakshatra = int(lon // c.NAK_SPAN)
    leaves = eph.find_crossing(eph.moon_longitude, jd, ((sign + 1) * 30) % 360, 13.18)
    return {
        "date": date.isoformat(),
        "moon_sign": c.named(c.SIGNS[sign], sign),
        "moon_nakshatra": c.named(c.NAKSHATRAS[nakshatra], nakshatra),
        "moon_leaves_sign": eph.from_jd(leaves).astimezone(tz).isoformat(timespec="seconds"),
        # House of the transiting Moon counted from each Rashi, Aries first
        "houses": [(sign - rashi) % 12 + 1 for rashi in range(12)],
    }
