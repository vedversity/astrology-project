"""Everything a Janam Patrika needs, in one dictionary.

build_report() runs the whole pipeline: astro engine -> rule engine ->
numerology -> names -> wording from the rule-book. The PDF generator (Phase 3)
and the website only read this result; they never calculate anything.
"""

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
