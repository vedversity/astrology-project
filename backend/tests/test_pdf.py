"""PDF generator: the charts, the filled template and the finished PDF."""

import re

import pytest
from fastapi.testclient import TestClient

from app.astro import calculate_chart
from app.main import app
from app.pdf import PAGE_COUNT, build_html, charts, generate_pdf
from app.report import build_report
from tests.darak_sample import BIRTH

CHART = calculate_chart(**BIRTH)
REPORT = build_report(**BIRTH, gender="male", surname="Darak", kuldevi="Ashapura Mata")
PERSON = {"child_name": "Baby Boy Darak", "gender": "male", "father_name": "Shri Example Darak",
          "mother_name": "Smt. Example Darak", "gotra": "Bharadwaj", "kuldevi": "Ashapura Mata",
          "place": "Kharghar, Navi Mumbai, Maharashtra", "surname": "Darak"}
UNKNOWN_TIME = build_report(BIRTH["date"], None, BIRTH["latitude"], BIRTH["longitude"],
                            BIRTH["timezone"], gender="female")


def pages(html):
    return html.count('<section class="page">')


def pdf_pages(pdf):
    return len(re.findall(rb"/Type\s*/Page\b", pdf))


def house_of(svg, label):
    """Which house a label was drawn in, read back from its position in the chart."""
    x, y = re.search(rf'<text x="([\d.]+)" y="([\d.]+)" class="k-planet"[^>]*>{re.escape(label)}<', svg).groups()
    x, y = float(x) / charts.SIZE, float(y) / charts.SIZE
    distances = [(abs(x - px) + abs(y - py), house + 1) for house, (px, py) in enumerate(charts.PLANET_SPOT)]
    return min(distances)[1]


# ---------- charts ----------

def test_lagna_chart_matches_the_sample():
    svg = charts.lagna_chart(CHART)
    # Page 3 of the sample: Lagna in the 1st, Mars and Jupiter in the 4th, Moon and Saturn in the 12th
    expected = {"ल Asc": 1, "सू Su": 6, "चं Mo": 12, "मं Ma": 4, "बु Me": 7, "गु Ju": 4,
                "शु Ve": 7, "श Sa(R)": 12, "रा Ra": 11, "के Ke": 5}
    for label, house in expected.items():
        assert house_of(svg, label) == house, label
    # Aries rises, so the houses are numbered 1 to 12 in order
    assert re.findall(r'class="k-num"[^>]*>(\d+)<', svg) == [str(n) for n in range(1, 13)]


def test_moon_chart_puts_the_moon_first():
    svg = charts.moon_chart(CHART)
    assert house_of(svg, "चं Mo") == 1
    assert house_of(svg, "ल Asc") == 2                       # Aries is the 2nd from Pisces
    assert re.findall(r'class="k-num"[^>]*>(\d+)<', svg)[0] == "12"


def test_divisional_charts_match_the_sample():
    d9 = charts.lagna_chart(CHART, "D9")                     # Gemini rises in the Navamsa
    assert re.findall(r'class="k-num"[^>]*>(\d+)<', d9)[0] == "3"
    assert house_of(d9, "सू Su") == 11 and house_of(d9, "बु Me") == 5
    d10 = charts.lagna_chart(CHART, "D10")                   # Cancer rises in the Dashamsa
    assert re.findall(r'class="k-num"[^>]*>(\d+)<', d10)[0] == "4"
    assert house_of(d10, "मं Ma") == 10


def test_crowded_house_still_draws_every_planet():
    points = {key: (0, False) for key in ["lagna", "sun", "moon", "mars", "mercury", "jupiter", "venus"]}
    points.update(saturn=(1, True), rahu=(1, False), ketu=(1, False))
    svg = charts.kundali_svg(points, 0)
    assert svg.count('class="k-planet"') == 10
    sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', svg)]
    assert min(sizes) < 12.5                                 # the crowded houses use smaller text


# ---------- the filled template ----------

@pytest.mark.parametrize("variant", ["mini", "full", "premium"])
@pytest.mark.parametrize("lang", ["hi", "en"])
def test_page_count(variant, lang):
    html = build_html(REPORT, PERSON, variant, lang)
    assert pages(html) == PAGE_COUNT[variant]
    assert "{{" not in html and "{%" not in html
    assert "Baby Boy Darak" in html and "Page 1" in html


def test_variants_differ_as_priced():
    mini, full, premium = (build_html(REPORT, PERSON, v, "en") for v in ("mini", "full", "premium"))
    # Only Premium has the suggested names and the Sanskar calendar
    assert "Suggested Names" in premium and "Deepansh" in premium and "Sanskar Calendar" in premium
    for html in (mini, full):
        assert "Suggested Names" not in html and "Deepansh" not in html
        assert "Suggested Sanskar Calendar" not in html
    # Full has the analysis pages; Mini does not
    assert "House-by-House Analysis" in full and "Vimshottari Dasha" in full and "Lo Shu Grid" in full
    assert "House-by-House Analysis" not in mini and "Lo Shu Grid" not in mini
    # Everyone gets the charts, the name letters and the disclaimer
    for html in (mini, full, premium):
        assert html.count('class="kundali"') >= 2
        assert "Nakshatra Letters" in html and "guidance and cultural purposes" in html


def test_language_switches_the_body_text():
    hi, en = build_html(REPORT, PERSON, "full", "hi"), build_html(REPORT, PERSON, "full", "en")
    assert "रेवती गण्डमूल नक्षत्र है" in hi and "Revati is a Gandmool nakshatra" not in hi
    assert "Revati is a Gandmool nakshatra" in en
    assert "27 सितम्बर 2026" in hi and "27 Sep 2026" in en
    for html in (hi, en):                                    # headings are always in both languages
        assert "योग एवं दोष विचार" in html and "Yogas &amp; Doshas" in html


def test_sample_values_are_printed():
    html = build_html(REPORT, PERSON, "premium", "en")
    for text in ["19° 02′ 50″ N", "73° 04′ 18″ E", "08:00 PM (14:30 UTC)", "Parabhava", "Dhruva",
                 "Kaulava", "Loha (Iron)", "Hamsa Mahapurusha Yoga", "Mercury–Sun", "36 → 9",
                 "46 → 1 ★★", "2+7+0+9+2+0+2+6 = 28 → 1", "Ashapura Mata"]:
        assert text in html, text


def test_unknown_birth_time_leaves_out_the_lagna_pages():
    person = {"gender": "female", "surname": "Sharma"}
    html = build_html(UNKNOWN_TIME, person, "premium", "en")
    assert pages(html) == 11                                 # no divisional charts, no house table
    assert html.count('class="kundali"') == 1                # the Moon chart only
    assert "Baby Girl Sharma" in html
    assert "House-by-House Analysis" not in html and "Navamsa (D-9)" not in html
    assert "exact birth time was not known" in html
    assert pages(build_html(UNKNOWN_TIME, person, "mini", "hi")) == 4


def test_customer_text_is_escaped():
    person = {**PERSON, "child_name": "<script>alert(1)</script>"}
    html = build_html(REPORT, person, "mini", "en")
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_bad_variant_or_language_is_rejected():
    with pytest.raises(ValueError):
        build_html(REPORT, PERSON, "gold", "en")
    with pytest.raises(ValueError):
        build_html(REPORT, PERSON, "full", "fr")


# ---------- the finished PDF (needs Chromium: python -m playwright install chromium) ----------

@pytest.fixture(scope="module")
def chromium():
    sync_api = pytest.importorskip("playwright.sync_api")
    try:
        with sync_api.sync_playwright() as p:
            p.chromium.launch().close()
    except Exception as error:                               # browser not downloaded yet
        pytest.skip(f"Chromium is not installed: {error}")


@pytest.mark.parametrize("variant,lang", [("premium", "hi"), ("full", "en"), ("mini", "hi")])
def test_pdf_is_produced(chromium, variant, lang):
    pdf = generate_pdf(REPORT, PERSON, variant, lang)
    assert pdf.startswith(b"%PDF")
    assert pdf_pages(pdf) == PAGE_COUNT[variant]             # nothing spilled onto an extra page
    fonts = set(re.findall(rb"/BaseFont\s*/[A-Z]+\+([A-Za-z0-9]+)", pdf))
    assert b"NotoSansDevanagari" in fonts                    # the Hindi font is embedded
    # Only the bundled fonts are used, so the PDF looks the same on any server
    assert all(name.startswith(b"Noto") for name in fonts), fonts


def test_pdf_for_unknown_time(chromium):
    pdf = generate_pdf(UNKNOWN_TIME, {"gender": "female"}, "full", "hi")
    assert pdf_pages(pdf) == 11


def test_api_pdf(chromium):
    body = {"date": "2026-09-27", "time": "20:00", "latitude": 19.0473, "longitude": 73.0718,
            "timezone": "Asia/Kolkata", "gender": "male", "surname": "Darak",
            "child_name": "Baby Boy Darak", "variant": "mini", "lang": "en"}
    response = TestClient(app).post("/pdf", json=body)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF") and pdf_pages(response.content) == 4
    assert TestClient(app).post("/pdf", json={**body, "variant": "gold"}).status_code == 422
