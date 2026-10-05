"""Everything a Janam Patrika needs, in one dictionary.

build_report() runs the whole pipeline: astro engine -> rule engine ->
numerology -> names -> wording from the rule-book. The PDF generator (Phase 3)
and the website only read this result; they never calculate anything.
"""

import datetime as dt

from app.astro import calculate_chart
from app.content.interpret import interpret
from app.names import name_letters, suggest_names
from app.numerology import numerology
from app.rules import analyze


def build_preview(date, time=None, latitude=0.0, longitude=0.0, timezone="Asia/Kolkata",
                  time_known=True):
    """The free preview: Rashi, Nakshatra, Pada and name letters only."""
    chart = calculate_chart(date, time, latitude, longitude, timezone, time_known)
    a = chart["avakahada"]
    return {
        "rashi": a["rashi"],
        "nakshatra": a["nakshatra"],
        "pada": a["pada"],
        "name_letters": name_letters(chart),
        "time_known": chart["meta"]["time_known"],
        # Present only when the birth time is unknown: is the Moon's position certain that day?
        "certainty": chart.get("time_unknown"),
    }


def build_panchang(date, latitude, longitude, timezone="Asia/Kolkata"):
    """The day's Panchang for a place, taken at sunrise as printed almanacs do."""
    noon = calculate_chart(date, dt.time(12, 0), latitude, longitude, timezone)
    sunrise = dt.datetime.fromisoformat(noon["panchang"]["sunrise"])
    # One minute after sunrise, so the weekday and tithi are those of the new day
    moment = (sunrise + dt.timedelta(minutes=1)).time().replace(microsecond=0)
    chart = calculate_chart(date, moment, latitude, longitude, timezone)
    p = chart["panchang"]
    keep = ("tithi", "paksha", "nakshatra", "yoga", "karana", "maas", "ritu", "ayana", "weekday",
            "vikram_samvat", "shaka_samvat", "samvatsara", "sunrise", "sunset", "rahu_kaal")
    return {
        "date": date.isoformat(),
        **{key: p[key] for key in keep},
        "moon_sign": chart["planets"]["moon"]["sign"],
        "sun_sign": chart["planets"]["sun"]["sign"],
    }


def build_report(date, time=None, latitude=0.0, longitude=0.0, timezone="Asia/Kolkata",
                 time_known=True, gender="male", surname=None, kuldevi=None, names_limit=10):
    """gender: "male" or "female". surname and kuldevi are optional."""
    chart = calculate_chart(date, time, latitude, longitude, timezone, time_known)
    analysis = analyze(chart)
    numbers = numerology(date, gender)
    letters = name_letters(chart)
    suggestions = suggest_names(chart, gender, numbers, surname, names_limit)
    return {
        "chart": chart,
        "analysis": analysis,
        "numerology": numbers,
        "content": interpret(chart, analysis, numbers, letters, suggestions, gender, kuldevi, surname),
    }
