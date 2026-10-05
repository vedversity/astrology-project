"""Janam Patrika backend.

Settings that must stay out of Git (passwords, keys) live in backend/.env, one
NAME=value per line. They are read here once, when the app starts.
"""

import os
from pathlib import Path

_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _name, _value = _line.split("=", 1)
            # A value already set on the server wins over the file
            os.environ.setdefault(_name.strip(), _value.strip().strip('"').strip("'"))
