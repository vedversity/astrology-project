"""Name letters and name suggestions, checked against page 10 of the sample PDF."""

from collections import Counter

from app.astro import calculate_chart
from app.astro import constants as c
from app.names import first_sound, load_names, name_letters, rashi_letters, suggest_names
from app.numerology import numerology
from tests.darak_sample import BIRTH

CHART = calculate_chart(**BIRTH)
NUMBERS = numerology(BIRTH["date"], "male")


def test_sample_name_letters():
    letters = name_letters(CHART)
    assert letters["primary"]["en"] == "Do"
    assert [x["en"] for x in letters["nakshatra"]] == ["De", "Do", "Cha", "Chi"]
    assert [x["en"] for x in letters["rashi"]] == ["Di", "Du", "Tha", "Jha", "Yna", "De", "Do", "Cha", "Chi"]


def test_sample_suggested_names():
    found = suggest_names(CHART, "male", NUMBERS, surname="Darak", limit=10)
    names = [n["en"] for n in found]
    # Nine of the sample's ten names; the two the sample marks with two stars come first
    assert names[:2] == ["Deepansh", "Dakssh"]
    assert {"Devesh", "Devraj", "Devansh", "Devam", "Chinmay", "Chitransh", "Charvik"} <= set(names)
    best = found[0]["numerology"]
    assert (best["compound"], best["number"]) == (36, 9)
    assert (best["full_name"]["compound"], best["full_name"]["number"]) == (46, 1)
    assert best["stars"] == 2
    assert all(n["numerology"]["fit"] != "avoid" for n in found)


def test_first_sound():
    assert first_sound("दीपांश") == ("द", "i")
    assert first_sound("दक्ष") == ("द", "a")
    assert first_sound("आरव") == ("", "a")
    assert first_sound("प्रणव") == ("प", "a")        # joined consonant: the vowel after it
    assert first_sound("श्रुति") == ("श", "u")
    assert first_sound("डो") == ("द", "o")           # retroflex and dental count as one sound


def test_every_rashi_has_nine_letters():
    seen = [pair for sign in range(12) for pair in rashi_letters(sign)]
    assert len(seen) == 108
    assert seen == [pair for row in c.NAAM_AKSHAR for pair in row]


def test_names_database():
    names = load_names()
    assert len(names) >= 200
    assert len({n["en"] for n in names}) == len(names), "duplicate English spelling"
    genders = Counter(n["gender"] for n in names)
    assert genders["boy"] >= 90 and genders["girl"] >= 90
    for n in names:
        assert n["gender"] in ("boy", "girl", "unisex")
        assert n["en"].isalpha() and n["hi"] and n["meaning"]["en"] and n["meaning"]["hi"]
        assert "ऀ" <= n["hi"][0] <= "ॿ", f"{n['en']}: Hindi spelling must be in Devanagari"


def test_every_pada_gets_ten_names_for_boys_and_girls():
    for nak in range(27):
        for pada in range(4):
            lon = nak * c.NAK_SPAN + pada * c.PADA_SPAN + 0.5
            chart = {"avakahada": {"nakshatra": {"index": nak}, "pada": pada + 1,
                                   "naam_akshar": c.named(c.NAAM_AKSHAR[nak][pada]),
                                   "rashi": {"index": int(lon // 30)}}}
            for gender in ("male", "female"):
                found = suggest_names(chart, gender, NUMBERS, limit=10)
                assert len(found) == 10, f"{c.NAKSHATRAS[nak][0]} pada {pada + 1} {gender}: {len(found)}"
                wrong = "girl" if gender == "male" else "boy"
                assert all(n["gender"] != wrong for n in found)
