"""Independent ground truth: planet positions from NASA JPL Horizons.

These numbers were downloaded from NASA's Horizons service on 4 Oct 2026 for
27 Sep 2026 14:30 UTC (geocentric apparent ecliptic longitude, tropical).
NASA knows nothing about astrology, so this checks the astronomy on its own.

Engine sidereal longitude + Lahiri ayanamsa should equal NASA's tropical longitude.
A steady gap of about 8 arc-seconds is expected: NASA includes the Earth's small
wobble (nutation) and the ayanamsa figure does not. 60 arc-seconds = 1 arc-minute.
"""

import pytest

from app.astro import calculate_chart
from tests.darak_sample import BIRTH

NASA_TROPICAL_LONGITUDE = {
    "sun": 184.5054071,
    "moon": 15.9781916,
    "mercury": 206.0661370,
    "venus": 217.8829978,
    "mars": 119.6978301,
    "jupiter": 138.9753257,
    "saturn": 11.8433272,
}
TOLERANCE_ARCSEC = 15

CHART = calculate_chart(**BIRTH)


@pytest.mark.parametrize("planet", NASA_TROPICAL_LONGITUDE)
def test_planet_matches_nasa(planet):
    engine = (CHART["planets"][planet]["longitude"] + CHART["ayanamsa"]["degrees"]) % 360
    nasa = NASA_TROPICAL_LONGITUDE[planet]
    diff_arcsec = abs((engine - nasa + 180) % 360 - 180) * 3600
    assert diff_arcsec < TOLERANCE_ARCSEC, f"{planet}: {diff_arcsec:.1f} arc-seconds from NASA"
