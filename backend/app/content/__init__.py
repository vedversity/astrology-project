"""Content layer: the editable rule-book (JSON files) and the code that reads it.

Every piece of wording in a report comes from app/content/rulebook/*.json.
Each text is stored as {"en": "...", "hi": "..."}.

Reports are written for one of two readers:
  "child" - the parents of a baby or child (the wording as it is stored)
  "adult" - the person themselves
A text that must read differently for an adult carries its own version:
  {"en": "...", "hi": "...", "adult": {"en": "...", "hi": "..."}}
Where there is none, the stored text is used and "the child" becomes "the native".
"""

import json
import re
from functools import lru_cache
from pathlib import Path

RULEBOOK_DIR = Path(__file__).parent / "rulebook"
AUDIENCES = ("child", "adult")
# Below this age the report is written for the parents
ADULT_FROM_AGE = 16

_CHILD_WORDS = [(re.compile(r"\bThe child\b"), "The native"), (re.compile(r"\bthe child\b"), "the native")]


def audience_for(birth_date, today):
    """Who the report speaks to, from the person's age on the day it is prepared."""
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return "adult" if age >= ADULT_FROM_AGE else "child"


def _for_adult(node):
    if isinstance(node, list):
        return [_for_adult(item) for item in node]
    if not isinstance(node, dict):
        return node
    if isinstance(node.get("en"), str) and "hi" in node:
        out = {key: _for_adult(value) for key, value in node.items() if key != "adult"}
        if "adult" in node:
            out.update(node["adult"])
        else:
            for pattern, word in _CHILD_WORDS:
                out["en"] = pattern.sub(word, out["en"])
        return out
    return {key: _for_adult(value) for key, value in node.items()}


def _for_child(node):
    if isinstance(node, list):
        return [_for_child(item) for item in node]
    if isinstance(node, dict):
        return {key: _for_child(value) for key, value in node.items() if key != "adult"}
    return node


@lru_cache(maxsize=None)
def load(name, audience="child"):
    """Read one rule-book file, for example load("yogas") or load("yogas", "adult")."""
    with open(RULEBOOK_DIR / f"{name}.json", encoding="utf-8") as f:
        book = json.load(f)
    return _for_adult(book) if audience == "adult" else _for_child(book)
