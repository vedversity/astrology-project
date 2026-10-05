# Website (Next.js)

How to run and what to edit is explained in the main `README.md` one folder up,
under "Phase 4: the website".

```
frontend/
  app/
    (hi)/            Hindi pages, served at /
    (en)/en/         English pages, served at /en
    globals.css      colours, fonts and shared button/field styles
    robots.ts        tells search engines which pages to skip
    sitemap.ts       lists the public pages with their hi/en pairs
  components/
    Shell.tsx        header and footer
    pages.tsx        Home, Janam Patrika and About pages
    KundliForm.tsx   the two-step birth form
    PlaceInput.tsx   birth-place search box
    Preview.tsx      the free result
    Order.tsx        names to print, contact details, consent
    Thanks.tsx       the download page
    Plans.tsx        plan cards with prices
  lib/
    content.ts       every word on the site, Hindi and English
    site.ts          reads brand, plans and prices from the backend
    birth.ts         keeps the form's details in the visitor's browser
    fonts.ts         Mukta (body) and Tiro Devanagari Hindi (headings)
  public/sample/     sample-page pictures (made by backend/scripts/make_site_samples.py)
```

Checks before committing: `npm run lint` and `npm run build`.
