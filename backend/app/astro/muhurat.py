"""Shubh dates for four ceremonies through a year: Vivah, Griha Pravesh, Namkaran, Mundan.

A date is offered when its Panchang at sunrise passes the widely published
rules below (nakshatra, tithi, weekday) and it does not fall in a period that
tradition sets aside (Chaturmas, Kharmas, Adhik Maas, Holashtak, or while
Jupiter or Venus is combust).

What this does NOT do: choose the time of day. The Lagna and the exact muhurat
window must still be fixed by the family's pandit. The pages say so.

DRAFT for the astrologer: regional traditions differ. Every rule is a plain
table below so it can be corrected without touching the code.
"""

import datetime as dt
from functools import lru_cache
from zoneinfo import ZoneInfo

from . import constants as c
from . import ephemeris as eph
from .panchang import _lunar_month

# Nakshatra indexes (Ashwini = 0)
ASHWINI, ROHINI, MRIGASHIRA, PUNARVASU, PUSHYA, MAGHA, U_PHALGUNI, HASTA, CHITRA, SWATI = 0, 3, 4, 6, 7, 9, 11, 12, 13, 14
ANURADHA, JYESHTHA, MULA, U_ASHADHA, SHRAVANA, DHANISHTA, SHATABHISHA, U_BHADRAPADA, REVATI = 16, 17, 18, 20, 21, 22, 23, 25, 26
# Python weekdays: Monday = 0 ... Sunday = 6
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
GENTLE_DAYS = {MON, WED, THU, FRI}
RIKTA = {4, 9, 14}                       # the "empty" tithis, avoided for beginnings

# Lunar months (amanta), Chaitra = 0
VAISHAKHA, JYESHTHA_MONTH, ASHADHA, KARTIK, MAGHA_MONTH, PHALGUNA = 1, 2, 3, 7, 10, 11

RULES = {
    "vivah": {
        "nakshatras": {ROHINI, MRIGASHIRA, MAGHA, U_PHALGUNI, HASTA, SWATI, ANURADHA, MULA, U_ASHADHA,
                       U_BHADRAPADA, REVATI},
        "tithis": set(range(1, 16)) - RIKTA,      # 15 = Purnima; Amavasya is excluded separately
        "weekdays": GENTLE_DAYS | {SUN},
        "avoid": {"chaturmas", "kharmas", "adhik", "holashtak", "guru_asta", "shukra_asta"},
    },
    "griha-pravesh": {
        "nakshatras": {ROHINI, MRIGASHIRA, U_PHALGUNI, CHITRA, ANURADHA, U_ASHADHA, U_BHADRAPADA, REVATI},
        "tithis": {2, 3, 5, 7, 10, 11, 12, 13},
        "weekdays": GENTLE_DAYS,
        "avoid": {"chaturmas", "kharmas", "adhik", "holashtak", "guru_asta", "shukra_asta"},
    },
    "namkaran": {
        "nakshatras": {ASHWINI, ROHINI, MRIGASHIRA, PUNARVASU, PUSHYA, U_PHALGUNI, HASTA, CHITRA, SWATI, ANURADHA,
                       U_ASHADHA, SHRAVANA, DHANISHTA, SHATABHISHA, U_BHADRAPADA, REVATI},
        "tithis": set(range(1, 16)) - RIKTA,
        "weekdays": GENTLE_DAYS,
        "avoid": set(),                           # a naming cannot wait for a season
    },
    "mundan": {
        "nakshatras": {ASHWINI, MRIGASHIRA, PUNARVASU, PUSHYA, HASTA, CHITRA, SWATI, JYESHTHA, SHRAVANA,
                       DHANISHTA, SHATABHISHA, REVATI},
        "tithis": {2, 3, 5, 7, 10, 11, 13},
        "weekdays": GENTLE_DAYS,
        "avoid": {"chaturmas", "kharmas", "adhik", "guru_asta", "shukra_asta"},
    },
}
TYPES = list(RULES)

# How close to the Sun (in degrees) a planet is counted as combust (asta)
GURU_ASTA_WITHIN = 11
SHUKRA_ASTA_WITHIN = 9

# Dates are worked out for Delhi; elsewhere in India a date can shift by a day at the edges
PLACE = (28.6139, 77.2090, "Asia/Kolkata")


def _apart(a, b):
    return abs((a - b + 180) % 360 - 180)


@lru_cache(maxsize=8)
def year_days(year):
    """The Panchang at sunrise for every day of a year, with the set-aside periods marked."""
    latitude, longitude, timezone = PLACE
    tz = ZoneInfo(timezone)
    days = []
    in_chaturmas = False
    # Start in mid-December so the Chaturmas switch is in the right state by 1 January
    day = dt.date(year - 1, 12, 15)
    while day <= dt.date(year, 12, 31):
        midnight = eph.to_jd(dt.datetime.combine(day, dt.time(0, 0), tzinfo=tz).astimezone(dt.timezone.utc))
        sunrise = eph.next_sunrise(midnight, latitude, longitude)
        sun = eph.sun_longitude(sunrise)
        moon = eph.moon_longitude(sunrise)
        angle = (moon - sun) % 360
        index = int(angle // 12)                         # 0-29
        paksha = 0 if index < 15 else 1                  # 0 = Shukla, 1 = Krishna
        tithi = index % 15 + 1                           # 1-15
        month = _lunar_month(sunrise, paksha)
        amanta = month["amanta"]["index"]
        adhik = month["is_adhika"]

        # Chaturmas: from Ashadha Shukla Ekadashi to Kartik Shukla Ekadashi
        if not adhik and paksha == 0 and tithi >= 11:
            if amanta == ASHADHA:
                in_chaturmas = True
            elif amanta == KARTIK:
                in_chaturmas = False
        marks = set()
        if in_chaturmas:
            marks.add("chaturmas")
        if int(sun // 30) in (8, 11):                    # Sun in Sagittarius or Pisces
            marks.add("kharmas")
        if adhik:
            marks.add("adhik")
        if amanta == PHALGUNA and paksha == 0 and tithi >= 8:
            marks.add("holashtak")
        if _apart(eph.planet(sunrise, "jupiter")[0], sun) < GURU_ASTA_WITHIN:
            marks.add("guru_asta")
        if _apart(eph.planet(sunrise, "venus")[0], sun) < SHUKRA_ASTA_WITHIN:
            marks.add("shukra_asta")

        if day.year == year:
            days.append({
                "date": day, "weekday": day.weekday(), "tithi": tithi, "paksha": paksha,
                "amavasya": paksha == 1 and tithi == 15,
                "nakshatra": int(moon // c.NAK_SPAN), "amanta": amanta, "marks": marks,
            })
        day += dt.timedelta(days=1)
    return days


def shubh_dates(kind, year):
    """The dates of a year that pass the rules for one ceremony."""
    rule = RULES[kind]
    return [day for day in year_days(year)
            if day["nakshatra"] in rule["nakshatras"]
            and day["tithi"] in rule["tithis"] and not day["amavasya"]
            and day["weekday"] in rule["weekdays"]
            and not (day["marks"] & rule["avoid"])]


def set_aside_periods(kind, year):
    """The stretches of the year left out for a ceremony, as (reason, first day, last day)."""
    periods = []
    for reason in sorted(RULES[kind]["avoid"]):
        start = previous = None
        for day in year_days(year):
            if reason in day["marks"]:
                start = start or day["date"]
                previous = day["date"]
            elif start:
                periods.append((reason, start, previous))
                start = None
        if start:
            periods.append((reason, start, previous))
    return sorted(periods, key=lambda p: p[1])
