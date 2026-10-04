"""Numerology: Mulank, Bhagyank, Kua, Lo Shu grid, personal years, Chaldean name numbers.

Pure arithmetic on the birth date and on names. No text lives here; the meaning
of each number is in app/content/rulebook/numerology.json.
"""


from app.content import load

CHALDEAN = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

# The Lo Shu square as it is drawn, top row first
LO_SHU_LAYOUT = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
PLANES = {
    "mental": (4, 9, 2), "emotional": (3, 5, 7), "practical": (8, 1, 6),
    "thought": (4, 3, 8), "will": (9, 5, 1), "action": (2, 7, 6),
}
PLANE_STATUS = {3: "complete", 2: "good", 1: "develop", 0: "missing"}

# Kua: element, group, then the four good directions (success, health, relationships, growth)
KUA = {
    1: ("water", "east", ["SE", "E", "S", "N"]),
    2: ("earth", "west", ["NE", "W", "NW", "SW"]),
    3: ("wood", "east", ["S", "N", "SE", "E"]),
    4: ("wood", "east", ["N", "S", "E", "SE"]),
    6: ("metal", "west", ["W", "NE", "SW", "NW"]),
    7: ("metal", "west", ["NW", "SW", "NE", "W"]),
    8: ("earth", "west", ["SW", "NW", "W", "NE"]),
    9: ("fire", "east", ["E", "SE", "N", "S"]),
}
KUA_DIRECTION_USES = ["success", "health", "relationships", "growth"]


def reduce_number(n):
    """28 -> 10 -> 1. Keeps adding the digits until one digit is left."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def digit_sum(*numbers):
    return sum(int(d) for n in numbers for d in str(n))


def mulank(date):
    """Psychic number: the day of the month, reduced."""
    return reduce_number(date.day)


def bhagyank(date):
    """Destiny number: every digit of the full date, reduced."""
    return reduce_number(digit_sum(date.day, date.month, date.year))


def kua(date, gender):
    """Kua number. gender is "male" or "female".

    The Kua year starts around 4 February, so a January birth belongs to the year before.
    Kua 5 does not exist: it becomes 2 for boys and 8 for girls.
    """
    year = date.year - 1 if (date.month, date.day) < (2, 4) else date.year
    base = reduce_number(digit_sum(year))
    if gender == "male":
        number = reduce_number(11 - base)
        return 2 if number == 5 else number
    number = reduce_number(4 + base)
    return 8 if number == 5 else number


def lo_shu(date, mulank_no, bhagyank_no, kua_no):
    """Count how often each digit 1-9 appears: birth date digits plus the three key numbers."""
    digits = [int(d) for d in f"{date.day}{date.month}{date.year}" if d != "0"]
    extra = [bhagyank_no, kua_no]
    # The Mulank is not added again when the day itself is that single digit (or 10, 20, 30)
    if date.day > 9 and date.day % 10 != 0:
        extra.insert(0, mulank_no)
    counts = {n: (digits + extra).count(n) for n in range(1, 10)}
    planes = {}
    for name, numbers in PLANES.items():
        present = [n for n in numbers if counts[n]]
        planes[name] = {"numbers": list(numbers), "present": present,
                        "status": PLANE_STATUS[len(present)]}
    return {
        "date_digits": digits,
        "counts": counts,
        "grid": [[{"number": n, "count": counts[n]} for n in row] for row in LO_SHU_LAYOUT],
        "present": [n for n in range(1, 10) if counts[n]],
        "missing": [n for n in range(1, 10) if not counts[n]],
        "planes": planes,
    }


def personal_year(date, year):
    return reduce_number(digit_sum(date.day, date.month, year))


def name_number(name):
    """Chaldean number of a name. Returns (compound, single), e.g. Deepansh -> (36, 9)."""
    total = sum(CHALDEAN.get(ch, 0) for ch in name.upper())
    return total, reduce_number(total)


def relationship(number):
    """Friendly, neutral and avoid numbers for a Mulank (from the rule-book table)."""
    return load("numerology")["relationships"][str(number)]


def lucky_dates(numbers):
    """Days of the month that reduce to one of the given numbers."""
    return [day for day in range(1, 32) if reduce_number(day) in numbers]


def _working(digits, result):
    """Show the sum the way it is written by hand: "2+7+0+9+2+0+2+6 = 28 → 1"."""
    if len(digits) == 1:
        return digits
    total = digit_sum(digits)
    return f"{'+'.join(digits)} = {total}" + ("" if total == result else f" → {result}")


def numerology(date, gender, years_ahead=9):
    m, b, k = mulank(date), bhagyank(date), kua(date, gender)
    rel = relationship(m)
    element, group, directions = KUA[k]
    # Lucky numbers: the two key numbers first, then the other friends
    key_numbers = [m] if b in rel["avoid"] else [m, b]
    lucky = list(dict.fromkeys(key_numbers + rel["friendly"]))
    return {
        "mulank": {"number": m, "working": _working(str(date.day), m)},
        "bhagyank": {"number": b,
                     "working": _working(f"{date.day:02d}{date.month:02d}{date.year}", b)},
        "kua": {"number": k, "element": element, "group": group,
                "directions": dict(zip(KUA_DIRECTION_USES, directions))},
        "relationship": rel,
        "lucky_numbers": lucky,
        "lucky_dates": {
            "best": lucky_dates({m, b} - set(rel["avoid"])),
            "good": lucky_dates(set(rel["friendly"]) - {m, b}),
            "avoid": lucky_dates(set(rel["avoid"])),
        },
        "lo_shu": lo_shu(date, m, b, k),
        "personal_years": [
            {"year": year, "number": personal_year(date, year),
             "favourable": personal_year(date, year) in lucky}
            for year in range(date.year + 1, date.year + 1 + years_ahead)
        ],
    }
