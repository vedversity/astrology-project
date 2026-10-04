# Janam Patrika Online

A mobile-first website where parents enter a newborn's birth details and receive a
Hindi or English Vedic Janam Patrika PDF. The full brief is in
`JanamPatrika_Project_Blueprint.pdf`.

## Where the project stands

| Phase | What | Status |
|---|---|---|
| 1 | Astro engine (calculations) + `/calculate` API | Done and tested |
| 2 | Rule engine, numerology, rule-book text | Not started |
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
cd C:\Users\HP\Desktop\VED\backend
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

## What is in the backend folder

```
backend/
  app/
    main.py            the web API (/calculate, /health)
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
```

## Calculation settings

Sidereal zodiac, Lahiri ayanamsa, whole-sign houses, mean Rahu/Ketu, Vimshottari
dasha with a 365.25-day year. All calculations are done by code with Swiss
Ephemeris; nothing is ever calculated by an AI model.

## Licence warning: Swiss Ephemeris

Swiss Ephemeris is free only under the AGPL licence, which requires publishing
this product's source code. A closed-source commercial site needs the paid
professional licence from Astrodienst (astro.com). **Decide before Phase 5
(real payments).**

## Privacy

The sample report contains a real family's details, so it is excluded from Git
(see `.gitignore`). Tests use only the birth date, time and coordinates.
