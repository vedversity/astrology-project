# Janam Patrika Online

A mobile-first website where parents enter a newborn's birth details and receive a
Hindi or English Vedic Janam Patrika PDF. The full brief is in
`JanamPatrika_Project_Blueprint.pdf`.

## Where the project stands

| Phase | What | Status |
|---|---|---|
| 1 | Astro engine (calculations) + `/calculate` API | Done and tested |
| 2 | Rule engine, numerology, rule-book text, names | Built and tested; rule-book awaits astrologer review |
| 3 | PDF generator | Not started |
| 4 | Website | Not started |
| 5 | Payments and delivery | Not started |
| 6 | Admin and growth | Not started |
| 7 | Launch checklist | Not started |

## One-time setup (Windows)

Install Python, Node.js and Git. In PowerShell, one line at a time:

```powershell
winget install -e --id Python.Python.3.11
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Git.Git
```

Use Python 3.11, not 3.12 or newer: Swiss Ephemeris ships a ready-made Windows
build only up to 3.11.

Close PowerShell, open it again, then set up the backend:

```powershell
cd "D:\Ved Development\Astro\backend"
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

## Phase 1: how to run and test

All commands are run from the `backend` folder.

**Run the automatic tests**

```powershell
.venv\Scripts\python -m pytest
```

**See the engine compared with the sample PDF, line by line**

```powershell
.venv\Scripts\python -m tests.compare_sample
```

**Start the API and try it in a browser**

```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs, click `POST /calculate`, click "Try it out",
and press "Execute". Press Ctrl+C in PowerShell to stop it.

## Phase 2: how to run and test

All commands are run from the `backend` folder.

**Run the automatic tests** (Phase 1 and Phase 2 together)

```powershell
.venv\Scripts\python -m pytest
```

**Read the sample report's wording, in English or Hindi**

```powershell
.venv\Scripts\python -X utf8 -m tests.show_report
.venv\Scripts\python -X utf8 -m tests.show_report hi
```

Add `> report_hi.txt` to the end of the line to save it as a file you can send
to the astrologer.

**Try it in a browser**

Start the API as in Phase 1 and open http://127.0.0.1:8000/docs. There are two
new buttons:

- `POST /preview` - the free preview (Rashi, Nakshatra, Pada, name letters)
- `POST /report` - everything a Janam Patrika needs, with all wording in Hindi
  and English. It needs one extra field, `"gender": "male"` or `"female"`.

### Editing the rule-book (no coding needed)

Every sentence a report can print lives in `backend/app/content/rulebook/`, one
file per topic. Each text is written twice, once as `"en"` and once as `"hi"`.

- Change the words freely. Do not change the keys (the names on the left) or
  anything inside curly brackets such as `{planet}`: those are filled in by the
  code.
- After editing, run the tests. They check that every text exists in both
  languages, that the curly-bracket names match, and that no fearful words
  (death, accident, curse and so on) have slipped in.

**The rule-book is a first draft written from the sample PDF and standard
references. The astrologer must review every file before launch.** These need
their judgement most:

| File | What to check |
|---|---|
| `numerology.json` | The friendly / neutral / avoid table for each number, lucky days and colours |
| `doshas.json` | Wording and remedies; which Gandmool padas count as mild |
| `yogas.json` | Results of each yoga |
| `houses.json` | The 108 planet-in-house sentences |
| `planets.json` | Remedies, gemstones, mantras, career fields |
| `predictions.json` | The strong / medium / needs-support paragraph for each life area |

### Adding names

Open `backend/app/names/data/names.json` and add a line: English spelling, Hindi
spelling, `boy` / `girl` / `unisex`, and the meaning in both languages. The
starting letter is read from the Hindi spelling. There are about 250 names now;
every nakshatra pada gets at least 10 suggestions for boys and for girls.

### Choices made in the rules (ask the astrologer to confirm)

- **Manglik** is checked from the Lagna, the Moon and Venus, in houses 1, 4, 7,
  8 and 12 (North Indian convention; the 2nd house is not counted). It is
  treated as cancelled when Jupiter joins or aspects Mars, or Mars is in its
  own or exaltation sign.
- **Planet and house strength** is a simple points system (listed in
  `rules/strength.py`), not classical Shadbala. It reproduces the sample's
  strong / medium / needs-support groups.
- **Kua number** uses 4 February as the start of the year, so a January birth
  is counted in the previous year.
- **Lo Shu grid** adds the Mulank, Bhagyank and Kua to the birth-date digits,
  as the sample does.

## What is in the backend folder

```
backend/
  app/
    main.py            the web API (/calculate, /preview, /report, /health)
    report.py          build_report() - runs the whole pipeline in one call
    rules/
      chartview.py     small helper: who sits where, who aspects whom
      yogas.py         detects 21 yogas (Hamsa, Malavya, Saraswati, Neecha-Bhanga ...)
      doshas.py        checks 10 doshas (Gandmool, Manglik, Kaal Sarp, Sade Sati ...)
      strength.py      planet strength and the 12-house table
      areas.py         education, career, wealth, health, family, marriage, foreign
    numerology/
      core.py          Mulank, Bhagyank, Kua, Lo Shu grid, personal years, name numbers
    names/
      __init__.py      name letters and name suggestions
      data/names.json  the names database
    content/
      interpret.py     drops the facts into the rule-book wording
      rulebook/        the editable Hindi + English text (JSON files)
    astro/
      engine.py        calculate_chart() - the one function everything else calls
      ephemeris.py     the only file that talks to Swiss Ephemeris
      panchang.py      tithi, nakshatra, yoga, karana, sunrise, month, year
      vargas.py        divisional charts D-1, 2, 3, 7, 9, 10, 12
      dasha.py         Vimshottari mahadasha and antardasha
      avakahada.py     varna, vashya, yoni, gana, nadi, paya, name letter
      transits.py      Gandmool return date, Sade Sati
      constants.py     lookup tables, every name in English and Hindi
  tests/
    darak_sample.py        the values printed in the sample PDF
    test_darak_sample.py   one test per sample value
    test_nasa_reference.py planet positions checked against NASA's own data
    test_engine_rules.py   checks that must hold for any chart
    compare_sample.py      prints the side-by-side comparison
    test_rules.py          yogas, doshas and strengths against the sample
    test_numerology.py     numerology against the sample
    test_names.py          name letters and suggested names against the sample
    test_content.py        rule-book completeness and the /preview, /report API
    show_report.py         prints the sample report's wording
```

## Calculation settings

Sidereal zodiac, Lahiri ayanamsa, whole-sign houses, mean Rahu/Ketu, Vimshottari
dasha with a 365.25-day year. All calculations are done by code with Swiss
Ephemeris; nothing is ever calculated by an AI model. Yogas, doshas and
numerology are found by fixed rules in code, and every sentence in a report
comes from the rule-book files, never from an AI model at run time.

## Licence warning: Swiss Ephemeris

Swiss Ephemeris is free only under the AGPL licence, which requires publishing
this product's source code. A closed-source commercial site needs the paid
professional licence from Astrodienst (astro.com). **Decide before Phase 5
(real payments).**

## Privacy

The sample report contains a real family's details, so it is excluded from Git
(see `.gitignore`). Tests use only the birth date, time and coordinates.
