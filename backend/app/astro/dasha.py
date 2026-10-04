"""Vimshottari dasha (120-year cycle) from the Moon's position at birth."""

from .constants import DASHA_ORDER, DASHA_YEAR_DAYS, DASHA_YEARS, NAK_SPAN


def vimshottari(moon_lon, jd_birth, to_local_date):
    """Return mahadashas with their antardashas.

    to_local_date: function that turns a Julian Day into a local "YYYY-MM-DD" string.
    """
    nak_index = int(moon_lon // NAK_SPAN)
    # How far the Moon has already travelled through its nakshatra (0 to 1)
    elapsed = (moon_lon % NAK_SPAN) / NAK_SPAN
    first = nak_index % 9
    first_lord = DASHA_ORDER[first]

    balance_years = (1 - elapsed) * DASHA_YEARS[first_lord]
    # The first mahadasha notionally began before birth
    start = jd_birth - elapsed * DASHA_YEARS[first_lord] * DASHA_YEAR_DAYS

    mahadashas = []
    current = {}
    for i in range(9):
        md_lord = DASHA_ORDER[(first + i) % 9]
        md_days = DASHA_YEARS[md_lord] * DASHA_YEAR_DAYS
        antardashas = []
        ad_start = start
        for j in range(9):
            ad_lord = DASHA_ORDER[(first + i + j) % 9]
            ad_days = md_days * DASHA_YEARS[ad_lord] / 120
            antardashas.append({
                "lord": ad_lord,
                "start": to_local_date(ad_start),
                "end": to_local_date(ad_start + ad_days),
            })
            if ad_start <= jd_birth < ad_start + ad_days:
                current = {"mahadasha": md_lord, "antardasha": ad_lord}
            ad_start += ad_days
        mahadashas.append({
            "lord": md_lord,
            "years": DASHA_YEARS[md_lord],
            "start": to_local_date(start),
            "end": to_local_date(start + md_days),
            "antardashas": antardashas,
        })
        start += md_days

    years = int(balance_years)
    months_float = (balance_years - years) * 12
    months = int(months_float)
    days = int((months_float - months) * 30)

    return {
        "system": "Vimshottari (365.25-day year)",
        "balance_at_birth": {
            "lord": first_lord,
            "total_years": round(balance_years, 4),
            "years": years, "months": months, "days": days,
        },
        "current_at_birth": current,
        "mahadashas": mahadashas,
    }
