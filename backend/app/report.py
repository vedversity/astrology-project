"""Everything a Janam Patrika needs, in one dictionary.

build_report() runs the whole pipeline: astro engine -> rule engine ->
numerology -> names -> wording from the rule-book. The PDF generator (Phase 3)
and the website only read this result; they never calculate anything.
"""

import datetime as dt

from app.astro import calculate_chart, sade_sati_on
from app.astro import constants as astro_constants
from app.astro.daily import RASHI_SLUGS, choghadiya, moon_transit
from app.astro import muhurat as muhurat_engine
from app.astro.milan import ashtakoot
from app.content import audience_for, load
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
    names = load("daily")
    slots = choghadiya(date, latitude, longitude, timezone)
    for part in slots.values():
        for slot in part:
            slot["name"] = names["choghadiya"][slot["key"]]["name"]
            slot["use"] = names["choghadiya"][slot["key"]]["use"]
            slot["quality_label"] = names["quality"][slot["quality"]]
    return {
        "date": date.isoformat(),
        **{key: p[key] for key in keep},
        "moon_sign": chart["planets"]["moon"]["sign"],
        "sun_sign": chart["planets"]["sun"]["sign"],
        "choghadiya": slots,
    }


def build_rashifal(date, timezone="Asia/Kolkata"):
    """The day's Rashifal for all twelve Rashis, read from the Moon's transit."""
    book = load("daily")["rashifal"]
    ordinals = load("labels")["ordinals"]
    transit = moon_transit(date, timezone)
    rashis = []
    for index, house in enumerate(transit["houses"]):
        entry = book["houses"][house - 1]
        name = astro_constants.named(astro_constants.SIGNS[index])
        rashis.append({
            "slug": RASHI_SLUGS[index],
            "name": name,
            "lord": astro_constants.named(astro_constants.PLANETS[astro_constants.SIGN_LORDS[index]]),
            "house": house,
            "mood": entry["mood"], "text": entry["text"],
            "good_for": entry["good_for"], "go_easy": entry["go_easy"],
            "basis": {lang: book["basis"][lang].format(
                moon_sign=transit["moon_sign"][lang], nakshatra=transit["moon_nakshatra"][lang],
                house=ordinals[lang][house - 1], rashi=name[lang]) for lang in ("en", "hi")},
        })
    return {
        "date": transit["date"],
        "moon_sign": transit["moon_sign"], "moon_nakshatra": transit["moon_nakshatra"],
        "moon_leaves_sign": transit["moon_leaves_sign"],
        "method": book["method"],
        "rashis": rashis,
    }


def build_muhurat_index(years):
    """The ceremonies on offer, with how many shubh dates each has in each year."""
    book = load("muhurat")
    return {
        "years": list(years),
        "types": [{"type": kind, "name": book["types"][kind]["name"], "what": book["types"][kind]["what"],
                   "counts": {str(year): len(muhurat_engine.shubh_dates(kind, year)) for year in years}}
                  for kind in muhurat_engine.TYPES],
    }


def build_muhurat(kind, year):
    """Shubh dates for one ceremony in one year, by month, with the periods left out and why."""
    book = load("muhurat")
    names = astro_constants

    def tithi_name(day):
        if day["tithi"] == 15:
            return names.named(names.PURNIMA)
        return names.named(names.TITHIS[day["tithi"] - 1])

    dates = [{
        "date": day["date"].isoformat(),
        "weekday": {"en": names.WEEKDAYS[day["weekday"]][0], "hi": names.WEEKDAYS[day["weekday"]][1]},
        "tithi": tithi_name(day),
        "paksha": names.named(names.PAKSHAS[day["paksha"]]),
        "nakshatra": names.named(names.NAKSHATRAS[day["nakshatra"]]),
    } for day in muhurat_engine.shubh_dates(kind, year)]
    months = [{"month": month, "dates": [d for d in dates if int(d["date"][5:7]) == month]} for month in range(1, 13)]
    return {
        "type": kind, "year": year,
        "name": book["types"][kind]["name"], "what": book["types"][kind]["what"],
        "rule": book["types"][kind]["rule"],
        "count": len(dates),
        "months": months,
        "set_aside": [{"reason": book["reasons"][reason]["name"], "why": book["reasons"][reason]["why"],
                       "from": start.isoformat(), "to": end.isoformat()}
                      for reason, start, end in muhurat_engine.set_aside_periods(kind, year)],
        "caution": book["caution"],
    }


# Which fact of each person a koota is read from (shown beside its score)
MILAN_FACT = {"varna": "varna", "vashya": "vashya", "tara": "nakshatra", "yoni": "yoni",
              "maitri": "rashi_lord", "gana": "gana", "bhakoot": "rashi", "nadi": "nadi"}


def build_milan(groom, bride):
    """Ashtakoot Guna matching for two births, with a Manglik comparison.

    groom, bride: the same details as build_preview takes (date, time, latitude ...).
    """
    book = load("milan")
    charts = {"groom": calculate_chart(**groom), "bride": calculate_chart(**bride)}
    result = ashtakoot(charts["groom"], charts["bride"])

    def pair(value):
        return {"en": value["en"], "hi": value["hi"]}

    kootas = []
    for key, koota in result["kootas"].items():
        fact = MILAN_FACT[key]
        kootas.append({
            "key": key, "name": book["kootas"][key]["name"], "about": book["kootas"][key]["about"],
            "points": koota["points"], "max": koota["max"],
            "groom": pair(result["facts"]["groom"][fact]), "bride": pair(result["facts"]["bride"][fact]),
        })

    manglik = {}
    for who, chart in charts.items():
        status = next(d for d in analyze(chart)["doshas"] if d["key"] == "manglik")["status"]
        manglik[who] = {"status": status, "label": book["manglik"]["status"][status]}
    has = [m["status"] in ("partial", "present") for m in manglik.values()]
    verdict = "both_manglik" if all(has) else "one_manglik" if any(has) else "both_clear"
    times_known = all(chart["meta"]["time_known"] for chart in charts.values())

    people = {
        who: {"rashi": pair(result["facts"][who]["rashi"]), "nakshatra": pair(result["facts"][who]["nakshatra"]),
              "pada": result["facts"][who]["pada"], "time_known": charts[who]["meta"]["time_known"]}
        for who in charts
    }
    total = result["total"]
    shown = int(total) if total == int(total) else total
    return {
        "total": total, "max": 36, "band": result["band"],
        "label": book["bands"][result["band"]]["label"],
        "text": {lang: book["bands"][result["band"]]["text"][lang].format(total=shown) for lang in ("en", "hi")},
        "kootas": kootas,
        "exceptions": [book["exceptions"][key] for key in result["exceptions"]],
        "manglik": {**manglik, "text": book["manglik"][verdict],
                    "note": None if times_known else book["manglik"]["unknown"]},
        "people": people,
        "note": book["note"],
    }


def build_report(date, time=None, latitude=0.0, longitude=0.0, timezone="Asia/Kolkata",
                 time_known=True, gender="male", surname=None, kuldevi=None, names_limit=10,
                 today=None):
    """gender: "male" or "female". surname and kuldevi are optional.

    today: the day the report is prepared (defaults to the real date). From the age on
    that day the report is written either for a child's parents or for an adult.
    """
    today = today or dt.date.today()
    audience = audience_for(date, today)
    chart = calculate_chart(date, time, latitude, longitude, timezone, time_known)
    if audience == "adult":
        # What matters to an adult is whether Sade Sati is running now, not at birth
        chart["sade_sati"] = {**sade_sati_on(chart, today), "as_of": today.isoformat()}
    analysis = analyze(chart)
    numbers = numerology(date, gender)
    letters = name_letters(chart)
    # Name suggestions are for naming a baby; an adult already has a name
    suggestions = suggest_names(chart, gender, numbers, surname, names_limit) if audience == "child" else []
    return {
        "audience": audience,
        "prepared_on": today.isoformat(),
        "chart": chart,
        "analysis": analysis,
        "numerology": numbers,
        "content": interpret(chart, analysis, numbers, letters, suggestions, gender, kuldevi, surname,
                             audience, today),
    }
