"""Content layer: the editable rule-book (JSON files) and the code that reads it.

Every piece of wording in a report comes from app/content/rulebook/*.json.
Each text is stored as {"en": "...", "hi": "..."}.
"""

import json
from functools import lru_cache
from pathlib import Path

RULEBOOK_DIR = Path(__file__).parent / "rulebook"


@lru_cache(maxsize=None)
def load(name):
    """Read one rule-book file, for example load("yogas")."""
    with open(RULEBOOK_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)
