"""One test per value printed in the sample PDF (see darak_sample.py).

Values listed in KNOWN_SAMPLE_DIFFERENCES are expected to differ, with the reason
recorded there. Any NEW difference fails the test run.
"""

import pytest

from app.astro import calculate_chart
from tests.darak_sample import BIRTH, KNOWN_SAMPLE_DIFFERENCES, compare

ROWS = compare(calculate_chart(**BIRTH))


@pytest.mark.parametrize("row", ROWS, ids=[r["item"] for r in ROWS])
def test_matches_sample(row):
    if row["item"] in KNOWN_SAMPLE_DIFFERENCES:
        # If this ever starts matching, the list above is out of date
        assert not row["match"], f"{row['item']} now matches; remove it from KNOWN_SAMPLE_DIFFERENCES"
        pytest.xfail(KNOWN_SAMPLE_DIFFERENCES[row["item"]])
    assert row["match"], f"sample says {row['sample']}, engine says {row['engine']}"
