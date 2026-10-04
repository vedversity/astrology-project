"""Panchang at birth: tithi, nakshatra, yoga, karana, weekday, sunrise, month, year."""

import datetime as dt

from . import constants as c
from . import ephemeris as eph

# Rough daily speeds, used only as a starting guess when searching for end times
_TITHI_RATE = 12.19   # Moon minus Sun
_MOON_RATE = 13.18
_YOGA_RATE = 14.16    # Moon plus Sun


def _tithi(jd, fmt):
    angle = eph.moon_sun_angle(jd)
    index = int(angle // 12)                 # 0-29
    paksha = 0 if index < 15 else 1          # bright half, then dark half
    day = index % 15                         # 0-14 within the half
    if day == 14:
        name = c.PURNIMA if paksha == 0 else c.AMAVASYA
    else:
        name = c.TITHIS[day]
    start = eph.find_crossing(eph.moon_sun_angle, jd, index * 12, _TITHI_RATE, forward=False)
    end = eph.find_crossing(eph.moon_sun_angle, jd, ((index + 1) * 12) % 360, _TITHI_RATE)
    tithi = {**c.named(name), "number": day + 1, "start": fmt(start), "end": fmt(end)}
    return tithi, paksha, angle


def _karana(angle):
    index = int(angle // 6)                  # 0-59, two per tithi
    if index == 0:
        return c.KARANA_KIMSTUGHNA
    if index >= 57:
        return c.KARANAS_FIXED_END[index - 57]
    return c.KARANAS_MOVABLE[(index - 1) % 7]


def _nakshatra(jd, moon_lon, fmt):
    index = int(moon_lon // c.NAK_SPAN)
    pada = int((moon_lon % c.NAK_SPAN) // c.PADA_SPAN) + 1
    start = eph.find_crossing(eph.moon_longitude, jd, index * c.NAK_SPAN, _MOON_RATE, forward=False)
    end = eph.find_crossing(eph.moon_longitude, jd, ((index + 1) * c.NAK_SPAN) % 360, _MOON_RATE)
    return {**c.named(c.NAKSHATRAS[index], index), "pada": pada, "start": fmt(start), "end": fmt(end)}


def _yoga(jd, fmt):
    index = int(eph.sun_moon_sum(jd) // c.NAK_SPAN)
    end = eph.find_crossing(eph.sun_moon_sum, jd, ((index + 1) * c.NAK_SPAN) % 360, _YOGA_RATE)
    return {**c.named(c.YOGAS[index], index), "end": fmt(end)}


def _lunar_month(jd, paksha):
    """Month name comes from the Sun's sign at the new moon that started the month."""
    prev_new_moon = eph.find_crossing(eph.moon_sun_angle, jd, 0, _TITHI_RATE, forward=False)
    next_new_moon = eph.find_crossing(eph.moon_sun_angle, jd, 0, _TITHI_RATE)
    sign_at_start = int(eph.sun_longitude(prev_new_moon) // 30)
    sign_at_end = int(eph.sun_longitude(next_new_moon) // 30)
    amanta = (sign_at_start + 1) % 12
    # In the dark half, the North Indian (Purnimanta) calendar is already in the next month
    purnimanta = amanta if paksha == 0 else (amanta + 1) % 12
    return {
        "amanta": c.named(c.LUNAR_MONTHS[amanta], amanta),
        "purnimanta": c.named(c.LUNAR_MONTHS[purnimanta], purnimanta),
        # Sun stays in one sign for the whole lunar month = extra (adhika) month
        "is_adhika": sign_at_start == sign_at_end,
    }


def _years(local_date, amanta_index):
    """Vikram and Shaka years. The year changes at Chaitra Shukla Pratipada (March/April)."""
    if local_date.month >= 5:
        new_year_passed = True
    elif local_date.month <= 2:
        new_year_passed = False
    else:
        new_year_passed = amanta_index in (0, 1)
    shaka = local_date.year - (78 if new_year_passed else 79)
    samvatsara = (shaka + 11) % 60
    return {
        "vikram_samvat": shaka + 135,
        "shaka_samvat": shaka,
        "samvatsara": c.named(c.SAMVATSARAS[samvatsara], samvatsara),
    }


def _sun_times(jd, local_dt, latitude, longitude, time_known):
    """Sunrise before the birth, the sunset after it, and the following sunrise."""
    midnight = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    jd_midnight = eph.to_jd(midnight)
    sunrise = eph.next_sunrise(jd_midnight, latitude, longitude)
    if sunrise is None:
        return None
    if time_known and jd < sunrise:
        # Born before dawn: the Vedic day still belongs to the previous sunrise
        sunrise = eph.next_sunrise(jd_midnight - 1, latitude, longitude)
        if sunrise is None:
            return None
    sunset = eph.next_sunset(sunrise, latitude, longitude)
    if sunset is None:
        return None
    following = eph.next_sunrise(sunset, latitude, longitude)
    if following is None:
        return None
    return sunrise, sunset, following


def panchang(jd, sun_lon, moon_lon, local_dt, latitude, longitude, time_known=True):
    tz = local_dt.tzinfo

    def fmt(jd_value):
        return eph.from_jd(jd_value).astimezone(tz).isoformat(timespec="seconds")

    tithi, paksha, angle = _tithi(jd, fmt)
    month = _lunar_month(jd, paksha)
    sun_nak = int(sun_lon // c.NAK_SPAN)
    tropical_sun = (sun_lon + eph.ayanamsa(jd)) % 360

    out = {
        "tithi": tithi,
        "paksha": c.named(c.PAKSHAS[paksha], paksha),
        "nakshatra": _nakshatra(jd, moon_lon, fmt),
        "yoga": _yoga(jd, fmt),
        "karana": c.named(_karana(angle)),
        "surya_nakshatra": c.named(c.NAKSHATRAS[sun_nak], sun_nak),
        "maas": month,
        "ritu": c.named(c.RITUS[((int(sun_lon // 30) + 1) % 12) // 2]),
        # Sun moves north from the winter solstice (270) to the summer solstice (90)
        "ayana": c.named(c.AYANAS[0 if (tropical_sun >= 270 or tropical_sun < 90) else 1]),
        **_years(local_dt.date(), month["amanta"]["index"]),
    }

    civil_weekday = local_dt.weekday()
    out["weekday"] = c.named(c.WEEKDAYS[civil_weekday][:2], civil_weekday)

    times = _sun_times(jd, local_dt, latitude, longitude, time_known)
    if times is None:
        return out
    sunrise, sunset, following = times
    out["sunrise"] = fmt(sunrise)
    out["sunset"] = fmt(sunset)

    # The Vedic day runs sunrise to sunrise
    vedic_weekday = eph.from_jd(sunrise).astimezone(tz).weekday()
    out["vedic_weekday"] = c.named(c.WEEKDAYS[vedic_weekday][:2], vedic_weekday)

    day_length = sunset - sunrise
    part = c.RAHU_KAAL_PART[vedic_weekday]
    out["rahu_kaal"] = {
        "start": fmt(sunrise + (part - 1) * day_length / 8),
        "end": fmt(sunrise + part * day_length / 8),
    }

    if not time_known:
        return out

    is_day = sunrise <= jd < sunset
    out["is_day_birth"] = is_day

    # Ishta Kaal: time since sunrise, in ghati and pal (1 day = 60 ghati, 1 ghati = 60 pal)
    total_pal = round((jd - sunrise) * 24 * 2.5 * 60)
    out["ishta_kaal"] = {"ghati": total_pal // 60, "pal": total_pal % 60}

    # Hora: daytime and night are each split into 12 planetary hours
    if is_day:
        hora_number = int((jd - sunrise) / (day_length / 12))
    else:
        hora_number = 12 + int((jd - sunset) / ((following - sunset) / 12))
    day_lord = c.WEEKDAYS[vedic_weekday][2]
    out["hora_lord"] = c.HORA_SEQUENCE[(c.HORA_SEQUENCE.index(day_lord) + hora_number) % 7]

    return out
