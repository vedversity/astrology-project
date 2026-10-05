"""Turn the facts (chart, rule engine, numerology, names) into the report's wording.

Nothing is calculated here and no sentence is invented here: every text comes
from the rule-book JSON files, with the facts dropped into the {placeholders}.
Every text is returned in both languages as {"en": "...", "hi": "..."}.
"""

import datetime as dt
from contextvars import ContextVar

from app.astro import constants as c
from app.numerology import name_number
from app.rules.chartview import KENDRAS, SEVEN, STRONG_DIGNITIES, TRIKONAS

from . import load as _load

# Who the report being written speaks to; set by interpret()
_audience = ContextVar("audience", default="child")


def load(name):
    return _load(name, _audience.get())

LANGS = ("en", "hi")
# Dosha statuses that deserve a remedy row and a mention among the points to look after
ACTIVE = ("present", "mild", "partial", "running")


# ---------- small helpers ----------

def both(value):
    """Use the same value in both languages."""
    return {"en": str(value), "hi": str(value)}


def fill(template, /, **facts):
    """Drop facts into a rule-book text. Facts may be plain values or {"en", "hi"} pairs."""
    out = {}
    for lang in LANGS:
        values = {k: v[lang] if isinstance(v, dict) else v for k, v in facts.items()}
        out[lang] = template[lang].format(**values)
    return out


def join(items, sep=", ", last=None):
    """Join a list of {"en", "hi"} pairs into one pair: "A, B and C"."""
    last = last or load("labels")["and"]
    out = {}
    for lang in LANGS:
        words = [item[lang] for item in items]
        out[lang] = words[0] if len(words) == 1 else sep.join(words[:-1]) + last[lang] + words[-1] if words else ""
    return out


def sentences(items):
    return {lang: " ".join(item[lang] for item in items if item[lang]) for lang in LANGS}


def planet(key):
    return c.named(c.PLANETS[key])


def planets(keys):
    return join([planet(k) for k in keys])


def ordinal(n):
    labels = load("labels")["ordinals"]
    return {lang: labels[lang][n - 1] for lang in LANGS}


def fmt_date(iso, day=True):
    """'2026-10-24T20:32...' -> {"en": "24 Oct 2026", "hi": "24 अक्टूबर 2026"}."""
    d = dt.date.fromisoformat(iso[:10])
    months = load("labels")["months"]
    return {lang: f"{d.day} {months[lang][d.month - 1]} {d.year}" if day
            else f"{months[lang][d.month - 1]} {d.year}" for lang in LANGS}


def add_months(date, months):
    month = date.month - 1 + months
    year, month = date.year + month // 12, month % 12 + 1
    return dt.date(year, month, min(date.day, 28))


# ---------- yogas and doshas ----------

def yoga_texts(analysis):
    book = load("yogas")
    labels = load("labels")
    out = []
    for yoga in analysis["yogas"]:
        entry = book[yoga["key"]]
        names = [planet(p) for p in yoga["planets"]]
        house = ordinal(yoga["house"]) if yoga.get("house") else None
        facts = {
            "planet": names[0],
            "planets": join(names),
            "a": names[0], "b": names[-1],
            "house": house or both(""),
            "where": fill(book["_where"], house=house) if house else both(""),
            "dignity": labels["dignity"].get(yoga.get("dignity"), both("")),
            "reasons": join([book["_neecha_bhanga_reasons"][r] for r in yoga.get("reasons", [])],
                            sep="; ", last=both("; ")),
            "ninth_lord": planet(yoga["ninth_lord"]) if "ninth_lord" in yoga else both(""),
            "support": planet(yoga["support"]) if "support" in yoga else both(""),
        }
        name = entry["partial_name"] if yoga.get("partial") else entry["name"]
        out.append({
            "key": yoga["key"],
            "name": fill(name, **facts),
            "formation": fill(entry["formation"], **facts),
            "result": entry["result"],
        })
    return out


def dosha_texts(analysis):
    book = load("doshas")
    labels = load("labels")
    out = []
    for dosha in analysis["doshas"]:
        entry = book[dosha["key"]]
        status = dosha["status"]
        facts = {}
        if "nakshatra" in dosha:
            facts.update(nakshatra=dosha["nakshatra"], pada=dosha["pada"],
                         return_date=fmt_date(dosha["moon_returns"]["start"]))
        if dosha.get("from"):
            facts["from"] = join([entry["from"][base] for base in dosha["from"]])
        if dosha.get("cancelled_by"):
            facts["reasons"] = join([entry["cancelled_by"][r] for r in dosha["cancelled_by"]])
        if dosha.get("joined"):
            facts["pairs"] = join([fill(both("{a}-{b}"), a=planet(j["planet"]), b=planet(j["node"]))
                                   for j in dosha["joined"]])
        if status == "running":
            facts.update(moon_sign=dosha["moon_sign"], ends=fmt_date(dosha["ends"], day=False),
                         phase=labels["sade_sati_phase"][dosha["phase"]])

        details = [fill(entry["details"][status], **facts)]
        if dosha.get("born_in_pitru_paksha"):
            details.append(fill(entry["pitru_paksha_birth"], tithi=dosha["tithi"]))
        row = {
            "key": dosha["key"],
            "name": entry["name"],
            "status": status,
            "status_label": labels["dosha_status"][status],
            "details": sentences(details),
            "remedy": None,
        }
        if status in ACTIVE and "remedy" in entry:
            row["remedy"] = fill(entry["remedy"], **facts)
        out.append(row)
    return out


# ---------- chart pages ----------

def aspect_texts(analysis):
    book = load("general")["aspects"]
    out = []
    for key in SEVEN:
        info = analysis["aspects"][key]
        if not info["planets"]:
            continue
        onto = fill(book["onto"], planets=planets(info["planets"]))
        out.append(fill(book["line"], planet=planet(key), house=ordinal(info["from_house"]),
                        houses=join([ordinal(h) for h in info["houses"]]), planets=onto))
    return out


def house_texts(analysis):
    book = load("houses")
    labels = load("labels")
    out = []
    for row in analysis["houses"]:
        house = row["house"]
        info = book["houses"][house - 1]
        lines = [book["planets"][p][house - 1] for p in row["occupants"]]
        if not lines:
            lines.append(fill(book["empty"], lord=planet(row["lord"]), lord_house=ordinal(row["lord_house"]),
                              topic=info["topic"], lord_topic=book["houses"][row["lord_house"] - 1]["topic"]))
        if row["lord_dignity"] in STRONG_DIGNITIES:
            lines.append(fill(book["lord_strong"], dignity=labels["dignity"][row["lord_dignity"]]))
        elif not row["occupants"]:
            if row["lord_house"] == house:
                quality = "own"
            elif row["lord_house"] in KENDRAS + TRIKONAS:
                quality = "good"
            else:
                quality = "effort" if row["lord_house"] in (6, 8, 12) else "steady"
            lines.append(book["lord_quality"][quality])

        soft = [p for p in ("venus", "mercury", "moon") if p in row["aspected_by"]]
        if "jupiter" in row["aspected_by"]:
            lines.append(book["aspect"]["jupiter"])
        elif soft:
            lines.append(fill(book["aspect"]["benefic"], planets=planets(soft)))
        elif "saturn" in row["aspected_by"]:
            lines.append(book["aspect"]["saturn"])
        elif "mars" in row["aspected_by"]:
            lines.append(book["aspect"]["mars"])

        out.append({
            "house": house,
            "name": info["name"],
            "sign": {"en": row["sign"]["en"], "hi": row["sign"]["hi"]},
            "lord": planet(row["lord"]),
            "lord_house": row["lord_house"],
            "occupants": [planet(p) for p in row["occupants"]],
            "level": row["level"],
            "text": sentences(lines),
        })
    return out


def strength_texts(analysis):
    labels = load("labels")
    groups = {level: {"label": labels["strength_level"][level], "planets": []}
              for level in ("strong", "medium", "weak")}
    for key, info in analysis["strength"].items():
        reasons = [labels["strength_reason"][r] for r in info["reasons"]]
        if info["retrograde"]:
            reasons.append(labels["strength_reason"]["retrograde"])
        groups[info["level"]]["planets"].append({
            "planet": planet(key),
            "reasons": join(reasons, last=both(", ")) if reasons else both(""),
        })
    return groups


def varga_texts(chart, analysis):
    book = load("general")["vargas"]
    labels = load("labels")
    lines = []
    for item in analysis["varga_highlights"]:
        lines.append(fill(book["highlight"], varga=book["purpose"][item["varga"]],
                          planet=planet(item["planet"]), dignity=labels["dignity"][item["dignity"]],
                          topic=book["topic"][item["varga"]]))
    vargottama = [p for p in chart["vargottama"] if p != "lagna"]
    if vargottama:
        lines.append(fill(book["vargottama"], planets=planets(vargottama)))
    return lines or [book["none"]]


# ---------- dasha ----------

def _stage(age):
    for limit, name in ((5, "infancy"), (12, "childhood"), (20, "teen"), (40, "youth"), (60, "midlife")):
        if age < limit:
            return name
    return "later"


def dasha_texts(chart, analysis, max_age=85):
    book = load("predictions")["dasha"]
    planet_book = load("planets")
    birth = dt.date.fromisoformat(chart["input"]["local_datetime"][:10])
    out = []
    for period in chart["dasha"]["mahadashas"]:
        start = max(dt.date.fromisoformat(period["start"]), birth)
        end = dt.date.fromisoformat(period["end"])
        age_from = (start - birth).days / 365.25
        age_to = (end - birth).days / 365.25
        if age_from > max_age:
            break
        lord = period["lord"]
        lines = [planet_book[lord]["dasha"], book["stage"][_stage((age_from + age_to) / 2)]]
        level = analysis["strength"][lord]["level"]
        if level in book["strength"]:
            lines.append(fill(book["strength"][level], lord=planet(lord)))
        out.append({
            "lord": planet(lord),
            "from": fmt_date(start.isoformat(), day=False),
            "to": fmt_date(end.isoformat(), day=False),
            "age_from": round(age_from, 1),
            "age_to": round(age_to, 1),
            "text": sentences(lines),
        })
    return out


# ---------- life predictions ----------

def prediction_texts(chart, analysis, yogas, doshas):
    book = load("predictions")
    signs = load("signs")
    planet_book = load("planets")
    moon = chart["planets"]["moon"]
    yoga_names = {y["key"]: y["name"] for y in yogas}
    dosha_by_key = {d["key"]: d for d in analysis["doshas"]}

    personality = []
    if chart["lagna"]:
        personality.append(signs["signs"][chart["lagna"]["sign"]["index"]]["lagna"])
    personality.append(signs["signs"][moon["sign"]["index"]]["moon"])
    personality.append(load("nakshatras")["nakshatras"][moon["nakshatra"]["index"]]["nature"])
    personality.append(signs["gana"][chart["avakahada"]["gana"]["en"]])
    out = [{"key": "personality", "title": book["areas"]["personality"]["title"],
            "level": None, "text": sentences(personality)}]

    if not analysis["areas"]:
        return out, book["time_unknown"]

    for area, info in analysis["areas"].items():
        entry = book["areas"][area]
        lines = [entry["levels"][info["level"]]]
        if info["yogas"]:
            lines.append(fill(book["supported_by"], yogas=join([yoga_names[k] for k in info["yogas"]])))
        if area == "career":
            fields = join([planet_book[p]["career"] for p in info["planets"]], sep="; ", last=both("; "))
            lines.append(fill(book["career_fields"], fields=fields))
        if area == "health":
            lines.append(fill(book["health_watch"],
                              areas=signs["signs"][chart["lagna"]["sign"]["index"]]["health"]))
            sade_sati = dosha_by_key["sade_sati"]
            if sade_sati["status"] == "running":
                lines.append(fill(book["sade_sati_care"], ends=fmt_date(sade_sati["ends"], day=False)))
        if area == "marriage" and dosha_by_key["manglik"]["status"] in book["marriage_manglik"]:
            lines.append(book["marriage_manglik"][dosha_by_key["manglik"]["status"]])
        out.append({"key": area, "title": entry["title"], "level": info["level"], "text": sentences(lines)})
    return out, None


# ---------- remedies, lucky factors, sanskar calendar ----------

def _guiding_planets(chart, analysis):
    """Lagna lord with the 5th and 9th lords (the friendly trio); Rashi lord if time is unknown."""
    if analysis["houses"]:
        lords = [analysis["houses"][h - 1]["lord"] for h in (1, 5, 9)]
        return list(dict.fromkeys(lords))
    return [chart["avakahada"]["rashi_lord"]]


def dasha_on(chart, day):
    """The mahadasha and antardasha running on a given day."""
    day = day.isoformat()
    for index, period in enumerate(chart["dasha"]["mahadashas"]):
        if period["start"] <= day < period["end"]:
            sub = next(ad for ad in period["antardashas"] if ad["start"] <= day < ad["end"])
            return {"index": index, "mahadasha": period["lord"], "antardasha": sub["lord"],
                    "mahadasha_ends": period["end"], "antardasha_ends": sub["end"]}
    return None


def remedy_texts(chart, analysis, doshas, kuldevi=None, running_lord=None):
    book = load("general")["remedies"]
    planet_book = load("planets")
    rows = [{"for": d["name"], "text": d["remedy"]} for d in doshas if d["remedy"]]
    used = set()

    def add(key, title):
        if key not in used:
            used.add(key)
            rows.append({"for": fill(book[title], planet=planet(key)), "text": planet_book[key]["remedy"]})

    main = _guiding_planets(chart, analysis)[0]
    for key, info in analysis["strength"].items():
        if info["level"] == "weak" and key != main:
            add(key, "for_planet")
    add(main, "for_lagna_lord" if analysis["houses"] else "for_rashi_lord")
    add(running_lord or chart["dasha"]["current_at_birth"]["mahadasha"], "for_dasha")

    rows.append({"for": book["kuldevi_title"],
                 "text": fill(book["kuldevi"], kuldevi=kuldevi) if kuldevi else book["kuldevi_unknown"]})
    # Stones of the Lagna lord and the 9th lord (or the Rashi lord when the time is unknown)
    guides = _guiding_planets(chart, analysis)
    stones = [fill(book["gemstone_for"], stone=planet_book[p]["gemstone"], planet=planet(p))
              for p in dict.fromkeys([guides[0], guides[-1]])]
    rows.append({"for": book["gemstone_title"], "text": fill(book["gemstone"], stones=join(stones))})
    return rows


def lucky_factors(chart, analysis, running_lord=None):
    planet_book = load("planets")
    guides = _guiding_planets(chart, analysis)
    dasha_lord = running_lord or chart["dasha"]["current_at_birth"]["mahadasha"]

    def collect(field):
        return join([planet_book[p][field] for p in guides], last=both(", "))

    colours = {lang: ", ".join(dict.fromkeys(col for p in guides for col in planet_book[p]["colours"][lang]))
               for lang in LANGS}
    return {
        "planets": [planet(p) for p in guides],
        "days": collect("day"),
        "numbers": [planet_book[p]["number"] for p in guides],
        "colours": colours,
        "metal": planet_book[guides[0]]["metal"],
        "direction": collect("direction"),
        "deity": collect("deity"),
        "mantras": list(dict.fromkeys(planet_book[p]["mantra"] for p in [dasha_lord] + guides)),
    }


def sanskar_calendar(chart, analysis, gender, kuldevi=None):
    book = load("general")["sanskar"]
    labels = load("labels")
    birth = dt.date.fromisoformat(chart["input"]["local_datetime"][:10])
    doshas = {d["key"]: d for d in analysis["doshas"]}

    def iso(days):
        return (birth + dt.timedelta(days=days)).isoformat()

    namkaran = book["namkaran"]
    gandmool = doshas["gandmool"]
    if gandmool["status"] != "not_present":
        when = fill(namkaran["gandmool"], return_date=fmt_date(gandmool["moon_returns"]["end"]))
    else:
        when = fill(namkaran["normal"], day11=fmt_date(iso(10)), day12=fmt_date(iso(11)))
    note = namkaran["pitru_note"] if doshas["pitru"]["born_in_pitru_paksha"] else namkaran["note"]
    rows = [{"name": namkaran["name"], "when": when, "note": note}]

    # Boys: 6th or 8th month. Girls: 5th or 7th month.
    first, second = (6, 8) if gender == "male" else (5, 7)
    anna = book["annaprashan"]
    rows.append({
        "name": anna["name"],
        "when": fill(anna["when"], first=ordinal(first), second=ordinal(second),
                     **{"from": fmt_date(add_months(birth, first - 1).isoformat(), day=False),
                        "to": fmt_date(add_months(birth, second).isoformat(), day=False)}),
        "note": anna["note_male" if gender == "male" else "note_female"],
    })

    mundan = book["mundan"]
    rows.append({
        "name": mundan["name"],
        "when": fill(mundan["when"], year1=birth.year + 1, year3=birth.year + 3),
        "note": fill(mundan["note"], kuldevi=kuldevi) if kuldevi else mundan["note_unknown"],
    })

    vidya = book["vidyarambh"]
    has_saraswati = any(y["key"] == "saraswati" for y in analysis["yogas"])
    rows.append({
        "name": vidya["name"],
        "when": fill(vidya["when"], year3=birth.year + 3, year5=birth.year + 5),
        "note": vidya["note_saraswati" if has_saraswati else "note"],
    })
    return rows


# ---------- numerology and names ----------

def numerology_texts(numbers, surname=None):
    book = load("numerology")
    planet_book = book["numbers"]
    m, b = numbers["mulank"]["number"], numbers["bhagyank"]["number"]
    rel = numbers["relationship"]
    fit = "friendly" if b in rel["friendly"] else "avoid" if b in rel["avoid"] else "neutral"

    def ruler(n):
        return planet(planet_book[str(n)]["planet"])

    kua = numbers["kua"]
    kua_book = book["kua"]
    directions = {use: kua_book["directions"][code] for use, code in kua["directions"].items()}

    lo_shu = numbers["lo_shu"]
    present = []
    for n in lo_shu["present"]:
        count = lo_shu["counts"][n]
        present.append({"number": n, "count": count, "planet": ruler(n),
                        "text": planet_book[str(n)]["repeated" if count > 1 else "present"]})
    lucky = numbers["lucky_numbers"]
    good_years = [str(y["year"]) for y in numbers["personal_years"] if y["favourable"]]
    out = {
        "mulank": {"number": m, "planet": ruler(m), "text": planet_book[str(m)]["mulank"]},
        "bhagyank": {"number": b, "planet": ruler(b), "text": planet_book[str(b)]["bhagyank"]},
        "combination": fill(book["combination"][fit], mulank=m, bhagyank=b,
                            mulank_planet=ruler(m), bhagyank_planet=ruler(b)),
        "kua": {
            "number": kua["number"],
            "element": kua_book["elements"][kua["element"]],
            "group": kua_book["groups"][kua["group"]],
            "directions": [{"use": kua_book["uses"][use], "direction": d} for use, d in directions.items()],
            "advice": fill(kua_book["advice"], **directions),
        },
        "lucky_days": join([planet_book[str(n)]["day"] for n in lucky], last=both(", ")),
        "lucky_colours": {lang: ", ".join(dict.fromkeys(
            col for n in (m, b) for col in planet_book[str(n)]["colours"][lang])) for lang in LANGS},
        "colours_to_minimise": {lang: ", ".join(planet_book[str(m)]["colours_avoid"][lang]) for lang in LANGS},
        "lo_shu_present": present,
        "lo_shu_planes": [
            {"name": book["planes"][name], "numbers": plane["numbers"], "present": plane["present"],
             "status": book["plane_status"][plane["status"]],
             "text": book["plane_complete"][name] if plane["status"] == "complete" else None}
            for name, plane in lo_shu["planes"].items()
        ],
        "lo_shu_missing": [
            {"number": n, "planet": ruler(n), **planet_book[str(n)]["missing"]} for n in lo_shu["missing"]
        ],
        "personal_years": fill(book["personal_years"], years=", ".join(good_years)) if good_years else None,
        "surname": None,
    }
    if surname:
        compound, single = name_number(surname)
        out["surname"] = fill(book["surname"], surname=surname, compound=compound, single=single)
    return out


def name_texts(letters, suggestions, numbers):
    labels = load("labels")
    rel = numbers["relationship"]
    return {
        "primary": letters["primary"],
        "nakshatra": letters["nakshatra"],
        "rashi": letters["rashi"],
        "suggestions": [
            {"en": n["en"], "hi": n["hi"], "meaning": n["meaning"],
             "match": labels["name_match"][n["match"]],
             "fit": labels["number_fit"][n["numerology"]["fit"]],
             "numerology": n["numerology"]}
            for n in suggestions
        ],
        "note": fill(load("numerology")["name_note"],
                     friendly=", ".join(map(str, rel["friendly"])),
                     avoid=" / ".join(map(str, rel["avoid"]))),
    }


# ---------- summary ----------

def summary_texts(yogas, doshas, predictions):
    book = load("general")["summary"]
    great = {"ruchaka", "bhadra", "hamsa", "malavya", "shasha"}
    count = len(yogas)
    if count >= 5 or sum(y["key"] in great for y in yogas) >= 2:
        kind = "blessed"
    else:
        kind = "good" if count >= 2 else "steady"
    top = join([y["name"] for y in yogas[:3]]) if yogas else both("")
    active = [d["name"] for d in doshas if d["status"] in ACTIVE]
    lines = [fill(book["note"][kind], count=count, top=top),
             fill(book["challenges"], list=join(active)) if active else book["no_challenges"]]
    return {
        "astrologer_note": sentences(lines),
        "yogas": [y["name"] for y in yogas],
        "doshas": [{"name": d["name"], "status": d["status_label"]} for d in doshas
                   if d["status"] != "not_present"],
        "strongest_areas": [p["title"] for p in predictions if p["level"] == "strong"],
        "closing": book["closing"],
    }


def general_texts(chart, kuldevi=None):
    book = load("general")
    local = dt.datetime.fromisoformat(chart["input"]["local_datetime"])
    out = {
        "invocation": book["invocation"],
        "cover_shloka": book["cover_shloka"],
        "cover_blessing": book["cover_blessing"],
        "closing_blessing": book["closing_blessing"],
        "kuldevi_line": fill(book["kuldevi_line"], kuldevi=kuldevi) if kuldevi else None,
        "disclaimer": book["disclaimer"],
        "milan_note": book["milan_note"],
        "calculation_notes": [fill(note, time=local.strftime("%I:%M %p").lstrip("0"))
                              for note in book["calculation_notes"]],
        "time_unknown": None,
    }
    if not chart["meta"]["time_known"]:
        # Without a birth time the last note (about the exact minute) does not apply
        out["calculation_notes"] = out["calculation_notes"][:2]
        notes = [book["time_unknown_note"]]
        certain = chart["time_unknown"]
        changed = [book["moon_change"][key] for key, flag in
                   (("moon_sign", "moon_sign_certain"), ("nakshatra", "nakshatra_certain"),
                    ("pada", "pada_certain")) if not certain[flag]]
        if changed:
            notes.append(fill(book["time_unknown_uncertain"], what=join(changed)))
        out["time_unknown"] = sentences(notes)
    return out


def nakshatra_details(chart):
    """Deity, symbol and tree of the birth nakshatra (for the Avakahada table)."""
    entry = load("nakshatras")["nakshatras"][chart["planets"]["moon"]["nakshatra"]["index"]]
    return {key: entry[key] for key in ("deity", "symbol", "tree")}


def interpret(chart, analysis, numbers, letters, suggestions, gender, kuldevi=None, surname=None,
              audience="child", today=None):
    """Build every piece of wording the report needs.

    audience: "child" (written for the parents) or "adult" (written for the person).
    today: the day the report is prepared; an adult's report shows the dasha running on it.
    """
    _audience.set(audience)
    now = dasha_on(chart, today) if audience == "adult" and today else None
    running_lord = now["mahadasha"] if now else None
    yogas = yoga_texts(analysis)
    doshas = dosha_texts(analysis)
    predictions, prediction_note = prediction_texts(chart, analysis, yogas, doshas)
    has_houses = analysis["houses"] is not None
    return {
        "general": general_texts(chart, kuldevi),
        "nakshatra": nakshatra_details(chart),
        "aspects": aspect_texts(analysis) if has_houses else None,
        "vargas": varga_texts(chart, analysis) if has_houses else None,
        "houses": house_texts(analysis) if has_houses else None,
        "strength": strength_texts(analysis),
        "yogas": yogas,
        "doshas": doshas,
        "dasha": dasha_texts(chart, analysis),
        "predictions": predictions,
        "prediction_note": prediction_note,
        "audience": audience,
        # An adult's report shows what is running today, not only at birth
        "dasha_now": now and {
            "index": now["index"],
            "mahadasha": planet(now["mahadasha"]), "antardasha": planet(now["antardasha"]),
            "mahadasha_ends": fmt_date(now["mahadasha_ends"], day=False),
            "antardasha_ends": fmt_date(now["antardasha_ends"], day=False),
        },
        "remedies": remedy_texts(chart, analysis, doshas, kuldevi, running_lord),
        # The childhood ceremonies are only for a child's report
        "sanskar": sanskar_calendar(chart, analysis, gender, kuldevi) if audience == "child" else None,
        "lucky": lucky_factors(chart, analysis, running_lord),
        "numerology": numerology_texts(numbers, surname),
        "names": name_texts(letters, suggestions, numbers),
        "summary": summary_texts(yogas, doshas, predictions),
    }
