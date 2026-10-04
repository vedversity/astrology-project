"""Values printed in the sample Janam Patrika (Baby Boy Darak), compared with the engine.

Only the birth date, time and coordinates are used - no names or personal details.
The sample is a ROUGH reference, not ground truth. Where the engine disagrees,
Swiss Ephemeris is trusted and the difference is reported to the founder.
"""

import datetime as dt

BIRTH = {
    "date": dt.date(2026, 9, 27),
    "time": dt.time(20, 0),
    "latitude": 19.0473,
    "longitude": 73.0718,
    "timezone": "Asia/Kolkata",
}

# Places where the sample PDF is wrong or uses a different convention. The engine's
# planet positions were verified against NASA (see test_nasa_reference.py).
KNOWN_SAMPLE_DIFFERENCES = {
    "mars: degree": "Sample degree is inaccurate; the engine matches NASA.",
    "jupiter: degree": "Sample degree is inaccurate; the engine matches NASA.",
    "venus: degree": "Sample degree is inaccurate; the engine matches NASA.",
    "saturn: degree": "Sample degree is inaccurate; the engine matches NASA.",
    "D12 saturn": "Follows from the sample's wrong Saturn degree (17d14m instead of 17d37m).",
    "panchang: ishta kaal": "Follows from sunrise: engine 06:27, sample 'about 06:29'.",
    "dasha: balance years+months": "Follows from the sample's Moon being 4 arc-min too far.",
    "dasha: balance days": "Follows from the sample's Moon being 4 arc-min too far.",
    "dasha: mercury ends (month)": "Follows from the sample's Moon being 4 arc-min too far.",
    "dasha: mercury-sun ends (month)": "Follows from the sample's Moon being 4 arc-min too far.",
    "sade sati: ends (month)": "Sample gives Saturn's first exit (Aug 2029); Saturn returns "
                               "in Oct 2029 and leaves for good in Apr 2030.",
}

DEGREE_TOLERANCE_ARCMIN = 5
TIME_TOLERANCE_MIN = 5

# point: (sign, (deg, min), nakshatra, pada, house)
POSITIONS = {
    "lagna": ("Aries", (9, 28), "Ashwini", 3, 1),
    "sun": ("Virgo", (10, 16), "Hasta", 1, 6),
    "moon": ("Pisces", (21, 49), "Revati", 2, 12),
    "mars": ("Cancer", (5, 11), "Pushya", 1, 4),
    "mercury": ("Libra", (1, 45), "Chitra", 3, 7),
    "jupiter": ("Cancer", (24, 28), "Ashlesha", 3, 4),
    "venus": ("Libra", (14, 17), "Swati", 3, 7),
    "saturn": ("Pisces", (17, 14), "Revati", 1, 12),
    "rahu": ("Aquarius", (3, 40), "Dhanishta", 4, 11),
    "ketu": ("Leo", (3, 40), "Magha", 2, 5),
}

DIGNITIES = {"mars": "debilitated", "jupiter": "exalted", "venus": "moolatrikona"}

VARGA_ORDER = ["D1", "D2", "D3", "D7", "D9", "D10", "D12"]
VARGAS = {
    "lagna": ["Aries", "Leo", "Aries", "Gemini", "Gemini", "Cancer", "Cancer"],
    "sun": ["Virgo", "Cancer", "Capricorn", "Taurus", "Aries", "Leo", "Capricorn"],
    "moon": ["Pisces", "Leo", "Scorpio", "Aquarius", "Capricorn", "Gemini", "Scorpio"],
    "mars": ["Cancer", "Cancer", "Cancer", "Aquarius", "Leo", "Aries", "Virgo"],
    "mercury": ["Libra", "Leo", "Libra", "Libra", "Libra", "Libra", "Libra"],
    "jupiter": ["Cancer", "Leo", "Pisces", "Gemini", "Aquarius", "Scorpio", "Aries"],
    "venus": ["Libra", "Leo", "Aquarius", "Capricorn", "Aquarius", "Aquarius", "Pisces"],
    "saturn": ["Pisces", "Leo", "Cancer", "Capricorn", "Sagittarius", "Aries", "Virgo"],
    "rahu": ["Aquarius", "Leo", "Aquarius", "Aquarius", "Scorpio", "Pisces", "Pisces"],
    "ketu": ["Leo", "Leo", "Leo", "Leo", "Taurus", "Virgo", "Virgo"],
}

KARAKAS = {
    "atmakaraka": "jupiter", "amatyakaraka": "moon", "bhratrikaraka": "saturn",
    "matrikaraka": "venus", "putrakaraka": "sun", "gnatikaraka": "mars",
    "darakaraka": "mercury",
}


def _exact(rows, item, sample, engine):
    rows.append({"item": item, "sample": str(sample), "engine": str(engine),
                 "match": sample == engine})


def _degrees(rows, item, sample_dm, engine_degrees):
    sample_degrees = sample_dm[0] + sample_dm[1] / 60
    diff_arcmin = abs(sample_degrees - engine_degrees) * 60
    whole = int(engine_degrees)
    engine_text = f"{whole}d {(engine_degrees - whole) * 60:04.1f}m"
    rows.append({"item": item, "sample": f"{sample_dm[0]}d {sample_dm[1]:02d}m",
                 "engine": f"{engine_text} (off by {diff_arcmin:.1f} arc-min)",
                 "match": diff_arcmin <= DEGREE_TOLERANCE_ARCMIN})


def _clock(rows, item, sample_iso, engine_iso):
    """Compare two local date-times, written like 2026-09-27T20:58."""
    sample_time = dt.datetime.fromisoformat(sample_iso)
    engine_time = dt.datetime.fromisoformat(engine_iso).replace(tzinfo=None)
    diff_min = abs((engine_time - sample_time).total_seconds()) / 60
    rows.append({"item": item, "sample": sample_iso.replace("T", " "),
                 "engine": f"{engine_time:%Y-%m-%d %H:%M} (off by {diff_min:.0f} min)",
                 "match": diff_min <= TIME_TOLERANCE_MIN})


def compare(chart):
    """Return one row per value: what the sample says, what the engine says, do they agree."""
    rows = []

    for key, (sign, dm, nak, pada, house) in POSITIONS.items():
        point = chart["lagna"] if key == "lagna" else chart["planets"][key]
        _exact(rows, f"{key}: sign", sign, point["sign"]["en"])
        _degrees(rows, f"{key}: degree", dm, point["degree_in_sign"])
        _exact(rows, f"{key}: nakshatra", nak, point["nakshatra"]["en"])
        _exact(rows, f"{key}: pada", pada, point["pada"])
        _exact(rows, f"{key}: house", house, point["house"])

    _exact(rows, "saturn: retrograde", True, chart["planets"]["saturn"]["retrograde"])
    for key, dignity in DIGNITIES.items():
        _exact(rows, f"{key}: dignity", dignity, chart["planets"][key]["dignity"])
    _exact(rows, "vargottama: mercury", True, "mercury" in chart["vargottama"])
    _degrees(rows, "ayanamsa (Lahiri)", (24, 13), chart["ayanamsa"]["degrees"])

    for key, signs in VARGAS.items():
        for varga, sign in zip(VARGA_ORDER, signs):
            _exact(rows, f"{varga} {key}", sign, chart["vargas"][varga][key]["sign"]["en"])

    for karaka, planet in KARAKAS.items():
        _exact(rows, f"karaka: {karaka}", planet, chart["jaimini_karakas"][karaka])

    p = chart["panchang"]
    _exact(rows, "panchang: weekday", "Sunday", p["vedic_weekday"]["en"])
    _exact(rows, "panchang: paksha", "Krishna", p["paksha"]["en"])
    _exact(rows, "panchang: tithi", "Pratipada", p["tithi"]["en"])
    _clock(rows, "panchang: tithi ends", "2026-09-27T20:58", p["tithi"]["end"])
    _exact(rows, "panchang: nakshatra", "Revati", p["nakshatra"]["en"])
    _clock(rows, "panchang: nakshatra starts", "2026-09-27T11:05", p["nakshatra"]["start"])
    _clock(rows, "panchang: nakshatra ends", "2026-09-28T10:12", p["nakshatra"]["end"])
    _exact(rows, "panchang: yoga", "Dhruva", p["yoga"]["en"])
    _exact(rows, "panchang: karana", "Kaulava", p["karana"]["en"])
    _exact(rows, "panchang: surya nakshatra", "Hasta", p["surya_nakshatra"]["en"])
    _exact(rows, "panchang: amanta month", "Bhadrapada", p["maas"]["amanta"]["en"])
    _exact(rows, "panchang: purnimanta month", "Ashwin", p["maas"]["purnimanta"]["en"])
    _exact(rows, "panchang: ritu", "Sharad", p["ritu"]["en"])
    _exact(rows, "panchang: ayana", "Dakshinayana", p["ayana"]["en"])
    _exact(rows, "panchang: vikram samvat", 2083, p["vikram_samvat"])
    _exact(rows, "panchang: shaka samvat", 1948, p["shaka_samvat"])
    _exact(rows, "panchang: samvatsara", "Parabhava", p["samvatsara"]["en"])
    _clock(rows, "panchang: sunrise", "2026-09-27T06:29", p["sunrise"])
    _clock(rows, "panchang: sunset", "2026-09-27T18:32", p["sunset"])
    _exact(rows, "panchang: born in daytime", False, p["is_day_birth"])
    _exact(rows, "panchang: ishta kaal", "33 ghati 47 pal",
           f"{p['ishta_kaal']['ghati']} ghati {p['ishta_kaal']['pal']} pal")
    _exact(rows, "panchang: hora lord", "mars", p["hora_lord"])
    _clock(rows, "panchang: rahu kaal starts", "2026-09-27T17:02", p["rahu_kaal"]["start"])
    _clock(rows, "panchang: rahu kaal ends", "2026-09-27T18:32", p["rahu_kaal"]["end"])

    a = chart["avakahada"]
    _exact(rows, "avakahada: varna", "Brahmin", a["varna"]["en"])
    _exact(rows, "avakahada: vashya", "Jalachar", a["vashya"]["en"])
    _exact(rows, "avakahada: yoni", "Gaja (Elephant)", a["yoni"]["en"])
    _exact(rows, "avakahada: gana", "Deva", a["gana"]["en"])
    _exact(rows, "avakahada: nadi", "Antya", a["nadi"]["en"])
    _exact(rows, "avakahada: tatva", "Water", a["tatva"]["en"])
    _exact(rows, "avakahada: paya", "Loha (Iron)", a["paya"]["en"])
    _exact(rows, "avakahada: naam akshar", "Do", a["naam_akshar"]["en"])

    d = chart["dasha"]
    balance = d["balance_at_birth"]
    _exact(rows, "dasha: mahadasha at birth", "mercury", d["current_at_birth"]["mahadasha"])
    _exact(rows, "dasha: antardasha at birth", "sun", d["current_at_birth"]["antardasha"])
    _exact(rows, "dasha: balance years+months", "10y 5m", f"{balance['years']}y {balance['months']}m")
    _exact(rows, "dasha: balance days", 9, balance["days"])
    _exact(rows, "dasha: mercury ends (month)", "2037-03", d["mahadashas"][0]["end"][:7])
    _exact(rows, "dasha: mercury-sun ends (month)", "2027-04",
           d["mahadashas"][0]["antardashas"][3]["end"][:7])

    _exact(rows, "gandmool: present", True, chart["gandmool"]["is_gandmool"])
    _exact(rows, "gandmool: moon returns (date)", "2026-10-24",
           chart["gandmool"].get("moon_returns", {}).get("start", "")[:10])
    _exact(rows, "sade sati: running at birth", True, chart["sade_sati"]["active_at_birth"])
    _exact(rows, "sade sati: phase", "peak", chart["sade_sati"].get("phase"))
    _exact(rows, "sade sati: first exit (month)", "2029-08",
           (chart["sade_sati"].get("first_exit") or "")[:7])
    _exact(rows, "sade sati: ends (month)", "2029-08", chart["sade_sati"].get("ends", "")[:7])

    return rows
