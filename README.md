# Janam Patrika Online

A mobile-first website where parents enter a newborn's birth details and receive a
Hindi or English Vedic Janam Patrika PDF. The full brief is in
`JanamPatrika_Project_Blueprint.pdf`.

## Where the project stands

| Phase | What | Status |
|---|---|---|
| 1 | Astro engine (calculations) + `/calculate` API | Done and tested |
| 2 | Rule engine, numerology, rule-book text, names | Built and tested; rule-book awaits astrologer review |
| 3 | PDF generator (Mini, Full, Premium; Hindi and English) | Built and tested |
| 4 | Website (Hindi at `/`, English at `/en`) | Built and tested; payment not connected yet |
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
.venv\Scripts\python -m playwright install chromium
```

The last line downloads the Chromium browser (about 150 MB, once). The PDF
generator uses it, without ever opening a window, to print the report.

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

### One report for a child, another for an adult

The report is written for whoever it is about, decided by age on the day it is
prepared (under 16 = child, set by `ADULT_FROM_AGE` in `app/content/__init__.py`).

| | Child (written for the parents) | Adult (written for the person) |
|---|---|---|
| Wording | "the child", remedies done by the parents | "the native", remedies done by oneself |
| Dasha | from birth | also shows the dasha running today, and its antardashas |
| Sade Sati | checked at birth | checked for today |
| Sanskar calendar, suggested names | in Premium | left out; the site offers only Mini and Full |

In the rule-book, a text that must read differently for an adult has an
`"adult"` version right beside it, with its own `"en"` and `"hi"`. Edit either
one. Where there is no adult version, the same text is used for both.

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

## Phase 3: how to run and test

All commands are run from the `backend` folder.

**Make the sample PDFs and compare with the original**

```powershell
.venv\Scripts\python -m tests.make_sample_pdf
```

This writes six PDFs into `backend\output` (Mini, Full and Premium, each in
Hindi and English) and a page called `compare.html`. Open `compare.html` in
Chrome or Edge to see the original sample on the left and the new Premium PDF
on the right.

The script prints example names. To print the real family's names, create
`backend\output\person.json` like this (the `output` folder never goes to Git):

```json
{"child_name": "Baby Boy ...", "father_name": "Shri ...", "mother_name": "Smt. ...",
 "gotra": "...", "kuldevi": "...", "surname": "..."}
```

**Get a PDF from the API**

Start the API, open http://127.0.0.1:8000/docs and use `POST /pdf`. Besides the
birth details it takes `variant` (`mini`, `full` or `premium`), `lang` (`hi` or
`en`) and the names to print on the cover. Click "Download file" in the
response to open the PDF.

### The three variants

| Variant | Pages | Contents |
|---|---|---|
| Mini | 4 | Cover, birth details and Panchang, charts and planet positions, name letters with an at-a-glance summary |
| Full | 13 | Everything in the sample, except the suggested names and the Sanskar calendar |
| Premium | 13 | Full, plus 10 suggested names with numerology and the Sanskar calendar |

If the birth time is not known, the Lagna, divisional-chart and house pages are
left out (Full and Premium become 11 pages) and a note explains why.

### How the PDF is made

`app/pdf/templates/patrika.html` is the page layout and `style.css` is its
look (colours, fonts, borders). The words come from the Phase 2 rule-book, so
editing the rule-book changes the PDF. Headings are always printed in Hindi and
English; the body text follows the chosen language. If a page has more text
than fits, its text is shrunk slightly so that nothing is ever cut off.

Fonts are the Noto families (free, SIL Open Font Licence), bundled in
`app/pdf/fonts`, so the PDF looks the same on any computer or server.

## Phase 4: the website

The website lives in the `frontend` folder. It needs the backend API running at
the same time, so use two PowerShell windows.

**One-time setup**

```powershell
cd "D:\Ved Development\Astro\frontend"
npm install
```

**Window 1: start the API** (from the `backend` folder)

```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload
```

**Window 2: start the website** (from the `frontend` folder)

```powershell
npm run dev
```

On a computer with little free memory, `npm run dev` can stop with an "out of
memory" message. Use the lighter way instead: `npm run build` once, then
`npm run start` (repeat the build after changing any website file).

Open http://localhost:3000 for Hindi and http://localhost:3000/en for English.
To see it as a phone would, press F12 in Chrome and click the phone icon.

**What to try**

1. Fill the two-step form and pick a town from the list.
2. The free preview shows Rashi, Nakshatra, Pada and name letters.
3. Choose a plan, fill in the names to print, tick the consent box.
4. Press the test button. The PDF is prepared and offered for download.

Payment is not connected yet (that is Phase 5), so the order page shows a
"test mode" notice and prepares the PDF without charging. The WhatsApp number
and email typed there are not stored or sent anywhere yet.

### Pages

| Address | Page |
|---|---|
| `/` and `/en` | Home: the form, what is free, the plans, FAQ |
| `/janam-patrika` | What the Patrika contains, sample pages, the plans |
| `/panchang` | Today's Panchang for any city (tithi, nakshatra, sunrise, Rahu Kaal); also shown as a strip on the home page |
| `/panchang/varanasi` (115 cities) | Today's Panchang for that city, by its own sunrise. Cities and their Hindi names are in `backend/app/places/data/cities_hi.json` |
| `/rashi-nakshatra` | Find your Rashi and Nakshatra: the form, with an explanation |
| `/naam`, `/naam/revati` (27) | Baby names by nakshatra: the four letters and names from the names database |
| `/grah`, `/grah/guru` (9) | What each planet means in the 12 houses, from the rule-book |
| `/dosh`, `/dosh/manglik` (4) | Fear-free dosha guides with cancellation rules (wording in `frontend/lib/guides.ts`) |
| `/about` | Calculation method and the three promises |
| `/privacy`, `/terms`, `/refund`, `/disclaimer` | Policy pages. Drafts: have a lawyer check them, then set `DRAFT = false` in `frontend/lib/legal.ts` |
| `/preview`, `/order`, `/thank-you` | A visitor's own result, order and download (hidden from search engines) |

### Changing things without coding

| To change | Edit |
|---|---|
| Prices, plan names, plan bullet points, brand name | `backend/app/config/site.json` (shows on the site within five minutes) |
| Any wording on the website | `frontend/lib/content.ts` |
| Colours | the top of `frontend/app/globals.css` |
| Sample pages on the site | run `.venv\Scripts\python -m scripts.make_site_samples` in `backend` |

The brand name is a placeholder ("Janam Patrika") until the real name is chosen.

### Place search

The birth-place box searches a list bundled with the backend: about 6,500
Indian towns and 11,000 cities abroad, each with latitude, longitude and
timezone. Nothing a visitor types is sent to Google or any outside service, and
no API key is needed. The list comes from GeoNames (licence CC BY 4.0, credited
in the site footer). `backend/scripts/build_places.py` rebuilds it. A village
not in the list is handled by picking the nearest town.

### What is deliberately not on the site yet

The Growth Blueprint also describes Kundli Milan, Panchang, Rashifal and
Muhurat pages. Those need calculation engines that do not exist yet, so the
site does not link to them. Nothing is claimed that the product cannot do: no
reviews, no astrologer details, no "50+ pages".

## What is in the backend folder

```
backend/
  app/
    main.py            the web API (/calculate, /preview, /report, /pdf, /places, /site, /health)
    config/site.json   brand name, plans and prices (owner-editable)
    places/            birth-place search and its bundled town list
    report.py          build_report() - runs the whole pipeline in one call
    pdf/
      __init__.py      generate_pdf() - fills the template and prints it to PDF
      charts.py        draws the North Indian kundali charts as SVG
      templates/       patrika.html (layout) and style.css (look)
      fonts/           Noto fonts for Hindi and English
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
    test_pdf.py            charts, page counts, variants, languages and the finished PDF
    make_sample_pdf.py     writes the sample PDFs and compare.html
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
