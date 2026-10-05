# Launch checklist

What must be true before the site takes real customers. Each item is marked:

- **Done** - built and tested in this repository
- **You** - a decision, an account or a document only the owner can supply
- **Open** - still to be built (mostly Phase 5)

Work top to bottom. Do not take live payments until every item in sections 1 to 5 is Done.

## 1. Decisions and accounts (You)

| Item | Why | Status |
|---|---|---|
| Brand name and domain | Check the domain and the trademark (IP India public search) before buying. Then set the name on the `/admin` page. | You |
| Swiss Ephemeris licence | It is free only under the AGPL, which obliges you to publish this product's source code. A closed-source commercial site needs the paid professional licence from Astrodienst (astro.com). **Decide before taking payments.** | You |
| Astrologer review of the rule-book | Every sentence in `backend/app/content/rulebook/` is a first draft. See the list in `README.md`. Run `python -X utf8 -m tests.show_report hi > report_hi.txt` to produce a file to send. | You |
| Lawyer review of the four policy pages | `frontend/lib/legal.ts`. Then set `DRAFT = false` there. | You |
| Astrologer name, years of practice and bio | Enter true details on the `/admin` page. Nothing is shown until then. | You |
| Contact email and WhatsApp number | Enter on the `/admin` page. Needed for the refund and deletion promises in the policies. | You |
| Private GitHub repository | The code exists only on one PC. `git remote add origin <url>` then `git push -u origin main`. Keep it **private**: the project blueprints are in the repository. | You |
| GST registration | As turnover grows; ask an accountant. | You |

## 2. Accuracy

| Item | Status |
|---|---|
| Planet positions checked against NASA data and the sample Patrika | Done (`tests/test_nasa_reference.py`, `tests/test_darak_sample.py`) |
| Yogas, doshas, numerology and names checked against the sample | Done |
| Kundli Milan checked against a hand-worked match | Done (`tests/test_milan.py`) |
| Compare 5 real charts with another trusted program and with the astrologer | You. The blueprint asks for this; it has not been done. |
| Confirm the choices listed under "Choices made in the rules" in `README.md` | You, with the astrologer. Also the Vashya and Gana tables and the band limits in `app/astro/milan.py`. |

## 3. Payments and delivery (Phase 5 - Open)

Nothing in this section is built. The order page runs in "test mode" and makes the PDF without charging.

- Razorpay account in TEST mode, then order creation and checkout
- Webhook that verifies the payment signature before the PDF is made; safe against duplicate webhooks
- Orders stored in a database (Supabase) with status; automatic refund flag if the PDF fails
- PDF stored and delivered by download link and email; WhatsApp later
- Invoice for each order
- Coupon and referral codes; orders and revenue on the admin page
- Run 20 to 30 real reports for friends and family in TEST mode before going live
- Razorpay live mode: complete KYC, add the site's policy page links, switch keys, set `NEXT_PUBLIC_PAYMENTS_ENABLED=true`

Until Phase 5 exists, the WhatsApp number and email typed on the order page are **not stored or sent anywhere**.

## 4. Security

| Item | Status |
|---|---|
| No secrets in the code; `.env` files are ignored by Git | Done |
| Admin page needs a 12+ character password (`ADMIN_TOKEN`); wrong guesses are rate-limited; off when no password is set | Done |
| PDF endpoints limited to 8 requests per address per 10 minutes | Done (`app/limits.py`) |
| All input validated (dates, coordinates, timezone, text lengths); customer text escaped in PDFs | Done |
| Only the website's own address may call the API from a browser (`FRONTEND_ORIGINS`) | Done. **Set it on the live server.** |
| API documentation pages switched off on the live server (`ENV=production`) | Done |
| Security headers on every page (no framing, HSTS, referrer policy) | Done (`frontend/next.config.ts`) |
| HTTPS everywhere | Automatic on Vercel and Render. Check after connecting the domain. |
| Content-Security-Policy header | Open. Not added yet; worth adding once analytics and the payment script are final. |
| The limits are kept in memory per server process | Fine for one server. If you run several, move them to a shared store. |
| Dependency updates | Run `pip list --outdated` and `npm outdated` monthly. |

## 5. Privacy (DPDP Act, 2023)

| Item | Status |
|---|---|
| Collect the minimum: no login, no phone number before the free result | Done |
| Birth details stay in the visitor's browser until a chart is requested | Done |
| Place search runs on our own server; nothing typed goes to an outside service | Done |
| "Remove my details from this device" button on the privacy page | Done |
| Personal result pages kept out of search engines | Done |
| Consent checkbox before an order | Done |
| Privacy policy matches what the product does | Draft. Re-read it after Phase 5 (stored orders) and before switching on analytics. |
| Deletion on request for stored orders | Open (needs Phase 5). Name a person who will handle requests. |
| Analytics | Off by default. If you set `NEXT_PUBLIC_GA_ID`, say so in the privacy policy first. |

## 6. Deployment

Not done yet; these files are ready but **have not been tried on a real host**.

**Backend (Render or Railway)**

1. Push the repository to GitHub (private).
2. On Render: New > Blueprint > choose the repository. It reads `render.yaml` and builds `backend/Dockerfile`.
3. Set `FRONTEND_ORIGINS` (the website's address) and `ADMIN_TOKEN` in the dashboard.
4. Use a plan with at least 1 GB of memory: the PDF generator runs a headless browser.
5. Open `https://<your-api>/health`. It should answer `{"status":"ok"}`.

**Website (Vercel)**

1. New Project > choose the repository > set the root directory to `frontend`.
2. Set `NEXT_PUBLIC_API_URL` (the backend's address) and `NEXT_PUBLIC_SITE_URL` (the site's address).
3. Deploy, then connect the domain.

**After both are up**

- Make one PDF of each variant in each language on the live site.
- Try the admin page; change a price and see it on the site within five minutes.
- Note: prices and brand changed on the admin page are written to a file on the server. On hosts that reset files on each deploy (Render does), they return to the values in Git. Either commit the change to `site.json`, or move settings to the database in Phase 5.

## 7. Search engines

| Item | Status |
|---|---|
| Hindi at `/`, English at `/en`, paired with hreflang | Done |
| Sitemap (about 360 addresses) and robots file | Done (`/sitemap.xml`, `/robots.txt`) |
| Titles, descriptions, one H1 per page, breadcrumbs, FAQ and product data | Done |
| Google Search Console: add the site, submit the sitemap | You, after the domain is live |
| Real search volumes for the keyword map | You (Google Keyword Planner), as the Growth Blueprint asks |
| Reviews | Collect real ones only, after real orders. The site shows none. |

## 8. Backups and monitoring

| Item | Status |
|---|---|
| Code | Git, once a remote exists |
| Orders and PDFs | Open (Phase 5): enable daily database backups in Supabase |
| Uptime check | You: a free monitor (UptimeRobot or similar) on `/health` and the home page |
| Error alerts | Open: add an error tracker (Sentry or similar) to both apps |
| A monthly test order | You, once payments are live |

## 9. Not built, by decision or for want of inputs

- **Phase 5** (payments, orders, delivery): skipped for now at the owner's request.
- **Muhurat pages** (vivah, griha pravesh, namkaran dates): need a muhurat engine.
- **Coupons, referral codes, order and revenue reports**: depend on Phase 5.
- **WhatsApp delivery and reminders**: need a WhatsApp Business API provider.
- **Saved family profiles and login**: not started.
