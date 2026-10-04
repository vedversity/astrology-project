"""Numerology, checked against pages 10-12 of the sample PDF."""

import datetime as dt

import pytest

from app.numerology import bhagyank, kua, mulank, name_number, numerology, reduce_number
from app.numerology.core import relationship
from tests.darak_sample import BIRTH

NUMBERS = numerology(BIRTH["date"], "male")


def test_sample_key_numbers():
    assert NUMBERS["mulank"]["number"] == 9
    assert NUMBERS["bhagyank"]["number"] == 1
    assert NUMBERS["bhagyank"]["working"] == "2+7+0+9+2+0+2+6 = 28 → 1"
    assert NUMBERS["kua"]["number"] == 1
    assert NUMBERS["kua"]["element"] == "water" and NUMBERS["kua"]["group"] == "east"
    assert NUMBERS["kua"]["directions"] == {"success": "SE", "health": "E", "relationships": "S", "growth": "N"}


def test_sample_number_relationships():
    assert NUMBERS["relationship"] == {"friendly": [1, 2, 3, 9], "neutral": [5, 6, 7], "avoid": [4, 8]}
    assert NUMBERS["lucky_dates"]["best"] == [1, 9, 10, 18, 19, 27, 28]
    assert NUMBERS["lucky_dates"]["avoid"] == [4, 8, 13, 17, 22, 26, 31]


def test_sample_lo_shu_grid():
    grid = NUMBERS["lo_shu"]
    assert grid["date_digits"] == [2, 7, 9, 2, 2, 6]
    assert grid["counts"] == {1: 2, 2: 3, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1, 8: 0, 9: 2}
    assert grid["missing"] == [3, 4, 5, 8]
    assert grid["planes"]["action"]["status"] == "complete"
    assert grid["planes"]["thought"]["status"] == "missing"
    assert [cell["number"] for row in grid["grid"] for cell in row] == [4, 9, 2, 3, 5, 7, 8, 1, 6]


def test_sample_personal_years():
    years = {y["year"]: y["number"] for y in NUMBERS["personal_years"]}
    assert years == {2027: 2, 2028: 3, 2029: 4, 2030: 5, 2031: 6, 2032: 7, 2033: 8, 2034: 9, 2035: 1}


@pytest.mark.parametrize("name,compound,single", [
    ("Deepansh", 36, 9), ("Dakssh", 18, 9), ("Daksh", 15, 6), ("Devesh", 28, 1), ("Devraj", 19, 1),
    ("Devansh", 29, 2), ("Devam", 20, 2), ("Dushyant", 29, 2), ("Chinmay", 20, 2),
    ("Chitransh", 29, 2), ("Charvik", 20, 2), ("Darak", 10, 1), ("DeepanshDarak", 46, 1),
])
def test_sample_chaldean_name_numbers(name, compound, single):
    assert name_number(name) == (compound, single)


@pytest.mark.parametrize("date,gender,expected", [
    (dt.date(2026, 9, 27), "male", 1),
    (dt.date(2026, 9, 27), "female", 8),     # 4 + 1 = 5, and 5 becomes 8 for girls
    (dt.date(1984, 3, 3), "male", 7),
    (dt.date(1984, 3, 3), "female", 8),
    (dt.date(1990, 1, 15), "male", 2),       # before 4 February: counted in 1989
    (dt.date(2000, 6, 21), "male", 9),
    (dt.date(2000, 6, 21), "female", 6),
])
def test_kua_number(date, gender, expected):
    assert kua(date, gender) == expected


def test_basic_numbers():
    assert reduce_number(28) == 1 and reduce_number(9) == 9 and reduce_number(999) == 9
    assert mulank(dt.date(2024, 2, 29)) == 2
    assert bhagyank(dt.date(2000, 1, 1)) == 4


def test_single_digit_day_is_not_counted_twice_in_lo_shu():
    # 5 March 2021: date digits 5,3,2,2,1. The Mulank 5 is the day itself, so it is not added again.
    grid = numerology(dt.date(2021, 3, 5), "female")["lo_shu"]
    assert grid["date_digits"].count(5) == 1
    extra_fives = [numerology(dt.date(2021, 3, 5), "female")[k]["number"] for k in ("bhagyank", "kua")].count(5)
    assert grid["counts"][5] == 1 + extra_fives


def test_relationship_table_is_complete():
    for number in range(1, 10):
        rel = relationship(number)
        assert sorted(rel["friendly"] + rel["neutral"] + rel["avoid"]) == list(range(1, 10))
        assert number in rel["friendly"]
