"""Make the sample Janam Patrika PDFs and a page that shows one beside the original.

Run from the backend folder:
    .venv\\Scripts\\python -m tests.make_sample_pdf

It writes six PDFs (Mini, Full and Premium, each in Hindi and English) into
backend\\output, plus compare.html. Open compare.html in Chrome or Edge to see
the original sample on the left and the new Premium PDF on the right.

The names below are examples. Put the real family's names in a file called
backend\\output\\person.json (same keys) to print them instead; the output
folder is never committed to Git.
"""

import json
from pathlib import Path

from app.pdf import VARIANTS, generate_pdf
from app.report import build_report
from tests.darak_sample import BIRTH

OUTPUT = Path(__file__).resolve().parent.parent / "output"
PROJECT = OUTPUT.parent.parent
PERSON = {"child_name": "Baby Boy", "gender": "male", "father_name": "Father's name",
          "mother_name": "Mother's name", "gotra": None, "kuldevi": None,
          "place": "Kharghar, Navi Mumbai, Maharashtra", "surname": None}

COMPARE = """<!doctype html>
<meta charset="utf-8">
<title>Sample vs generated</title>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #333; color: #fff; }}
  header {{ display: flex; }} header div {{ flex: 1; padding: 8px 12px; }}
  main {{ display: flex; height: calc(100vh - 36px); }} embed {{ flex: 1; border: 0; }}
</style>
<header><div>Original sample</div><div>Generated: {generated}</div></header>
<main><embed src="{sample}" type="application/pdf"><embed src="{generated}" type="application/pdf"></main>
"""


def main():
    OUTPUT.mkdir(exist_ok=True)
    person = dict(PERSON)
    person_file = OUTPUT / "person.json"
    if person_file.exists():
        person.update(json.loads(person_file.read_text(encoding="utf-8")))

    report = build_report(**BIRTH, gender=person["gender"], surname=person["surname"],
                          kuldevi=person["kuldevi"])
    for variant in VARIANTS:
        for lang in ("hi", "en"):
            target = OUTPUT / f"sample_{variant}_{lang}.pdf"
            target.write_bytes(generate_pdf(report, person, variant, lang))
            print(f"wrote {target}  ({target.stat().st_size // 1024} KB)")

    samples = sorted(PROJECT.glob("Janam*Patrika*Darak*.pdf"))
    if samples:
        page = COMPARE.format(sample=samples[0].as_uri(), generated="sample_premium_en.pdf")
        (OUTPUT / "compare.html").write_text(page, encoding="utf-8")
        print(f"wrote {OUTPUT / 'compare.html'}  (open it in Chrome or Edge)")
    else:
        print("The original sample PDF was not found in the project folder, so compare.html was skipped.")


if __name__ == "__main__":
    main()
