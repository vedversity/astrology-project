"""PDF generator: report data -> HTML (Jinja2 template) -> PDF (headless Chromium).

    from app.pdf import generate_pdf
    pdf_bytes = generate_pdf(report, person, variant="full", lang="hi")

report  : the result of app.report.build_report()
person  : names and places typed by the customer (see PERSON_FIELDS)
variant : "mini" (4 pages), "full" (13 pages) or "premium" (13 pages with
          suggested names and the Sanskar calendar)
lang    : "hi" or "en" for the body text; headings are always in both
"""

import datetime as dt
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.astro import constants as c
from app.content import load

from . import charts

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"
FONTS = HERE / "fonts"

VARIANTS = ("mini", "full", "premium")
LANGS = ("hi", "en")
PERSON_FIELDS = ("child_name", "gender", "father_name", "mother_name", "gotra", "kuldevi",
                 "place", "surname")
VARGA_ORDER = ["D1", "D2", "D3", "D7", "D9", "D10", "D12"]
PAGE_COUNT = {"mini": 4, "full": 13, "premium": 13}

# Shrinks the text of any page whose content is too tall, so nothing is ever cut off
FIT_JS = """
document.fonts.ready.then(() => {
  let overflow = 0;
  for (const box of document.querySelectorAll('.fit')) {
    const base = parseFloat(getComputedStyle(box).fontSize);
    let scale = 1;
    while (box.scrollHeight > box.clientHeight + 1 && scale > 0.6) {
      scale -= 0.02;
      box.style.fontSize = (base * scale) + 'px';
    }
    if (box.scrollHeight > box.clientHeight + 1) overflow += 1;
  }
  document.body.dataset.overflow = overflow;
  document.body.dataset.ready = '1';
});
"""

_env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]),
                   trim_blocks=True, lstrip_blocks=True)


class PdfError(Exception):
    """The PDF could not be produced (used later to flag an automatic refund)."""


def _display_name(person, lang, audience):
    if person.get("child_name"):
        return person["child_name"]
    label = load("labels", audience)["child"][person["gender"]][lang]
    return f"{label} {person['surname']}" if person.get("surname") else label


def build_html(report, person, variant="full", lang="hi", prepared_on=None):
    """Fill the template. Returned as a string so it can be checked without a browser."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    if lang not in LANGS:
        raise ValueError(f"lang must be one of {LANGS}")

    chart = report["chart"]
    content = report["content"]
    audience = report.get("audience", "child")
    # Premium adds what a newborn needs (names, Sanskar calendar); for an adult it is the Full report
    if audience == "adult" and variant == "premium":
        variant = "full"
    labels = load("labels", audience)
    months = labels["months"][lang]
    local = dt.datetime.fromisoformat(chart["input"]["local_datetime"])
    utc = dt.datetime.fromisoformat(chart["input"]["utc_datetime"])
    prepared = prepared_on or dt.date.today()

    def t(pair):
        return pair[lang] if pair else ""

    def L(hindi, english):
        return hindi if lang == "hi" else english

    def P(key):
        return c.PLANETS[key][0 if lang == "en" else 1]

    def clock(iso):
        return dt.datetime.fromisoformat(iso).strftime("%I:%M %p")

    def short_date(d):
        return f"{d.day} {months[d.month - 1]}"

    def day_clock(iso):
        """A time, with the date added when it falls on a different day from the birth."""
        moment = dt.datetime.fromisoformat(iso)
        text = moment.strftime("%I:%M %p")
        return text if moment.date() == local.date() else f"{text}, {short_date(moment)}"

    def long_date(iso):
        d = dt.date.fromisoformat(iso[:10])
        return f"{d.day} {months[d.month - 1]} {d.year}"

    def dms(value, positive, negative):
        total = round(abs(value) * 3600)
        return f"{total // 3600}° {total % 3600 // 60:02d}′ {total % 60:02d}″ {positive if value >= 0 else negative}"

    def age(years):
        return f"{years:g}"

    def dignity_text(key):
        """Dignity plus the flags worth showing beside it."""
        planet = chart["planets"][key]
        parts = []
        if planet["dignity"] not in (None, "none"):
            parts.append(t(labels["dignity"][planet["dignity"]]))
        reasons = report["analysis"]["strength"][key]["reasons"]
        for flag in ("neecha_bhanga", "vargottama"):
            if flag in reasons:
                parts.append(t(labels["strength_reason"][flag]))
        if planet["retrograde"]:
            parts.append(t(labels["strength_reason"]["retrograde"]))
        text = " · ".join(parts)
        return text[:1].upper() + text[1:] if text else "—"

    # Antardashas of two mahadashas: from the birth for a child, from the running one for an adult
    first = content["dasha_now"]["index"] if content.get("dasha_now") else 0
    antardashas = []
    for period in chart["dasha"]["mahadashas"][first:first + 2]:
        rows = []
        for ad in period["antardashas"]:
            if ad["end"] <= local.date().isoformat():
                continue
            starts_before_birth = ad["start"] < local.date().isoformat()
            start, end = dt.date.fromisoformat(ad["start"]), dt.date.fromisoformat(ad["end"])
            rows.append({
                "lord": c.named(c.PLANETS[ad["lord"]]),
                "from": {"en": "Birth", "hi": "जन्म"} if starts_before_birth
                        else {k: f"{labels['months'][k][start.month - 1]} {start.year}" for k in LANGS},
                "to": {k: f"{labels['months'][k][end.month - 1]} {end.year}" for k in LANGS},
            })
        antardashas.append({"lord": c.named(c.PLANETS[period["lord"]]), "periods": rows})

    svg = {"moon": charts.moon_chart(chart)}
    if chart["lagna"]:
        svg.update(lagna=charts.lagna_chart(chart), d9=charts.lagna_chart(chart, "D9"),
                   d10=charts.lagna_chart(chart, "D10"))

    offset = local.utcoffset()
    minutes = int(offset.total_seconds() // 60)
    person = {field: (person.get(field) or "").strip() or None for field in PERSON_FIELDS}
    person["display_name"] = _display_name(person, lang, audience)

    css = (TEMPLATES / "style.css").read_text(encoding="utf-8").replace("FONTS", FONTS.as_uri())
    return _env.get_template("patrika.html").render(
        css=css, fit_js=FIT_JS, lang=lang, variant=variant, person=person,
        chart=chart, content=content, numbers=report["numerology"],
        num=content["numerology"], names=content["names"],
        av=chart["avakahada"], pan=chart["panchang"], dasha=chart["dasha"], labels=labels,
        weekday=chart["panchang"]["weekday"],
        lagna_lord=c.SIGN_LORDS[chart["lagna"]["sign"]["index"]] if chart["lagna"] else None,
        utc_clock=utc.strftime("%H:%M"),
        utc_offset=f"{'+' if minutes >= 0 else '-'}{abs(minutes) // 60:02d}:{abs(minutes) % 60:02d}",
        varga_order=VARGA_ORDER, varga_keys=["lagna"] + c.PLANET_KEYS, svg=svg,
        antardashas=antardashas, audience=audience,
        content_remedies_intro=t(load("general", audience)["remedies"]["intro"]),
        prepared_on=f"{prepared.day} {months[prepared.month - 1]} {prepared.year}",
        t=t, L=L, P=P, clock=clock, day_clock=day_clock, long_date=long_date, dms=dms, age=age,
        dignity_text=dignity_text,
    )


def html_to_pdf(html):
    """Print the HTML to an A4 PDF with headless Chromium. Returns the PDF as bytes."""
    from playwright.sync_api import sync_playwright

    # The page is loaded from a file so that it is allowed to read the font files
    with tempfile.TemporaryDirectory() as folder:
        page_file = Path(folder) / "patrika.html"
        page_file.write_text(html, encoding="utf-8")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(page_file.as_uri())
                page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
                overflow = int(page.evaluate("document.body.dataset.overflow"))
                if overflow:
                    raise PdfError(f"{overflow} page(s) have more content than fits")
                return page.pdf(format="A4", print_background=True, prefer_css_page_size=True)
            finally:
                browser.close()


def build_milan_html(milan, groom, bride, lang="hi", prepared_on=None):
    """Fill the one-page Kundli Milan report.

    milan: the result of app.report.build_milan(). groom, bride: {"name", "date", "time", "place"}
    as typed by the customer (date and time are printed, not recalculated).
    """
    if lang not in LANGS:
        raise ValueError(f"lang must be one of {LANGS}")
    labels = load("labels")
    months = labels["months"][lang]
    prepared = prepared_on or dt.date.today()

    def t(pair):
        return pair[lang] if pair else ""

    def born(person):
        d = person["date"]
        text = f"{d.day} {months[d.month - 1]} {d.year}"
        if person.get("time"):
            text += ", " + person["time"].strftime("%I:%M %p")
        return text + (f" · {person['place']}" if person.get("place") else "")

    def num(value):
        return f"{value:g}"

    fallback = {"groom": {"hi": "वर", "en": "Groom"}, "bride": {"hi": "वधू", "en": "Bride"}}
    css = (TEMPLATES / "style.css").read_text(encoding="utf-8").replace("FONTS", FONTS.as_uri())
    return _env.get_template("milan.html").render(
        css=css, fit_js=FIT_JS, lang=lang, m=milan, t=t, num=num, total=num(milan["total"]),
        L=lambda hindi, english: hindi if lang == "hi" else english,
        groom_name=(groom.get("name") or "").strip() or fallback["groom"][lang],
        bride_name=(bride.get("name") or "").strip() or fallback["bride"][lang],
        births={"groom": born(groom), "bride": born(bride)},
        invocation=load("general")["invocation"], disclaimer=load("general", "adult")["disclaimer"],
        prepared_on=f"{prepared.day} {months[prepared.month - 1]} {prepared.year}",
    )


def generate_milan_pdf(milan, groom, bride, lang="hi", prepared_on=None):
    return html_to_pdf(build_milan_html(milan, groom, bride, lang, prepared_on))


def generate_pdf(report, person, variant="full", lang="hi", prepared_on=None):
    return html_to_pdf(build_html(report, person, variant, lang, prepared_on))


__all__ = ["PAGE_COUNT", "PdfError", "VARIANTS", "build_html", "build_milan_html", "generate_milan_pdf",
           "generate_pdf", "html_to_pdf"]
