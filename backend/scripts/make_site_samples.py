"""Make the sample-page pictures shown on the website's Janam Patrika page.

Run from the backend folder whenever the PDF design changes:
    .venv\Scripts\python -m scripts.make_site_samples

It prints the sample chart with made-up names and saves four pages, in Hindi
and in English, into frontend/public/sample.
"""

import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.pdf import build_html
from app.report import build_report
from tests.darak_sample import BIRTH

TARGET = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "sample"
# Cover, charts, yogas and doshas, numerology
PAGES = [1, 3, 6, 12]
PERSON = {
    "hi": {"child_name": "चि. आरव शर्मा", "gender": "male", "father_name": "श्री राजेश शर्मा",
           "mother_name": "श्रीमती सुनीता शर्मा", "gotra": "भारद्वाज", "place": "वाराणसी, उत्तर प्रदेश",
           "surname": "Sharma"},
    "en": {"child_name": "Aarav Sharma", "gender": "male", "father_name": "Shri Rajesh Sharma",
           "mother_name": "Smt. Sunita Sharma", "gotra": "Bharadwaj", "place": "Varanasi, Uttar Pradesh",
           "surname": "Sharma"},
}


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    report = build_report(**BIRTH, gender="male", surname="Sharma")
    with sync_playwright() as p, tempfile.TemporaryDirectory() as folder:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 1130})
        for lang, person in PERSON.items():
            page_file = Path(folder) / f"{lang}.html"
            page_file.write_text(build_html(report, person, "full", lang), encoding="utf-8")
            page.goto(page_file.as_uri())
            page.wait_for_function("document.body.dataset.ready === '1'")
            sheets = page.locator("section.page")
            for index, number in enumerate(PAGES, start=1):
                target = TARGET / f"{lang}-{index}.jpg"
                sheets.nth(number - 1).screenshot(path=str(target), type="jpeg", quality=72)
                print(f"wrote {target}  ({target.stat().st_size // 1024} KB)")
        browser.close()


if __name__ == "__main__":
    main()
