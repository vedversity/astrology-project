// The free reference pages: Rashi-Nakshatra, names by nakshatra, planets in
// houses, dosha guides and the Panchang of each city. Their data comes from the
// backend, so they always agree with the reports.

import Link from "next/link";
import { notFound } from "next/navigation";

import KundliForm from "@/components/KundliForm";
import Milan from "@/components/Milan";
import Panchang, { type PanchangData } from "@/components/Panchang";
import { Breadcrumbs, Cta, FaqList, Heading, Intro, LinkGrid } from "@/components/ui";
import { content, fill } from "@/lib/content";
import { DOSHA_SLUGS, guides, type DoshaSlug } from "@/lib/guides";
import { api, getSite, path, SITE_URL, type Lang, type Text } from "@/lib/site";

// ---------- shapes of the data the backend sends ----------

type Letter = Text & { pada: number };
type NakshatraBrief = { slug: string; name: Text; lord: Text; rashis: Text[]; letters: Letter[]; gandmool: boolean };
type NameRow = { en: string; hi: string; gender: "boy" | "girl" | "unisex"; meaning: Text; number: number; pada: number | null };
type NakshatraFull = NakshatraBrief & {
  deity: Text; symbol: Text; tree: Text; nature: Text; gana: Text; yoni: Text; nadi: Text;
  names: NameRow[]; previous: string; next: string;
};
type Planet = {
  slug: string; name: Text; day: Text; deity: Text; mantra: string; career: Text; period: Text; remedy: Text;
  houses: { house: number; name: Text; text: Text }[];
};
export type City = { slug: string; name: string; hi: string; state: string; latitude: number; longitude: number; timezone: string };

const DAY = 86400;
const HOUR = 3600;

/** Search-engine tags for a reference page. */
export async function guideMetadata(lang: Lang, page: string, title: string, description: string) {
  const brand = (await getSite())?.brand.name[lang];
  return {
    title: brand ? `${title} | ${brand}` : title,
    description,
    alternates: {
      canonical: SITE_URL + path(lang, page),
      languages: {
        "hi-IN": SITE_URL + path("hi", page),
        "en-IN": SITE_URL + path("en", page),
        "x-default": SITE_URL + path("hi", page),
      },
    },
  };
}

const lettersOf = (n: NakshatraBrief, lang: Lang) =>
  n.letters.map((letter) => (lang === "hi" ? letter.hi : `${letter.en} (${letter.hi})`)).join(", ");

// ---------- Rashi and Nakshatra ----------

export function rashiMetadata(lang: Lang) {
  const g = guides(lang).rashi;
  return guideMetadata(lang, "/rashi-nakshatra", g.title, g.description);
}

export function RashiPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.tools.items[0].title }]} />
      <div className="md:grid md:grid-cols-2 md:items-start md:gap-10">
        <Intro h1={g.rashi.h1} h2={g.rashi.h2} answer={g.rashi.answer} />
        <div className="pb-8 md:pt-4">
          <KundliForm lang={lang} />
        </div>
      </div>
      <section className="grid gap-3 pb-8 md:grid-cols-3">
        {g.rashi.sections.map((section) => (
          <div key={section.h} className="card">
            <h2 className="font-semibold">{section.h}</h2>
            {section.p.map((paragraph) => (
              <p key={paragraph} className="mt-1 text-sm text-ink-600">
                {paragraph}
              </p>
            ))}
          </div>
        ))}
      </section>
      <FaqList title={content(lang).faqTitle} items={g.rashi.faqs} />
    </>
  );
}

// ---------- names by nakshatra ----------

export function naamIndexMetadata(lang: Lang) {
  const g = guides(lang).naam;
  return guideMetadata(lang, "/naam", g.indexTitle, g.indexDescription);
}

export async function NaamIndexPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const list = (await api<NakshatraBrief[]>("/guide/nakshatras", DAY)) ?? [];
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.naam }]} />
      <Intro h1={g.naam.indexH1} answer={g.naam.indexAnswer} />
      <section className="pb-8">
        <LinkGrid
          items={list.map((n) => ({
            href: path(lang, `/naam/${n.slug}`),
            title: n.name[lang],
            text: n.letters.map((letter) => `${letter.hi} ${letter.en}`).join(" · "),
          }))}
        />
        <Link href={path(lang, "/rashi-nakshatra")} className="mt-4 inline-block font-semibold text-kesar-700 underline">
          {g.naam.unknown}
        </Link>
      </section>
      <Cta lang={lang} />
    </>
  );
}

export async function naamMetadata(lang: Lang, slug: string) {
  const n = await api<NakshatraFull>(`/guide/nakshatras/${slug}`, DAY);
  if (!n) return {};
  const g = guides(lang).naam;
  // Search results show plain letters; the page itself shows both scripts
  const values = { name: n.name[lang], letters: n.letters.map((letter) => letter[lang]).join(", ") };
  return guideMetadata(lang, `/naam/${slug}`, fill(g.title, values), fill(g.description, values));
}

function NameTable({ lang, title, rows }: { lang: Lang; title: string; rows: NameRow[] }) {
  const g = guides(lang).naam;
  if (rows.length === 0) return null;
  return (
    <section className="pb-8">
      <Heading>{title}</Heading>
      <div className="overflow-x-auto rounded-2xl border border-kesar-100 bg-white">
        <table className="w-full text-left">
          <thead className="bg-kesar-50 text-sm text-maroon-800">
            <tr>
              <th className="px-4 py-2">{g.columns.name}</th>
              <th className="px-4 py-2">{g.columns.meaning}</th>
              <th className="hidden px-4 py-2 md:table-cell">{g.columns.letter}</th>
              <th className="px-4 py-2 text-center">{g.columns.number}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.en} className="border-t border-kesar-100">
                <td className="px-4 py-2 font-semibold">
                  {row.hi} <span className="block text-sm font-normal text-ink-600 md:inline">{row.en}</span>
                </td>
                <td className="px-4 py-2 text-ink-600">{row.meaning[lang]}</td>
                <td className="hidden px-4 py-2 text-sm whitespace-nowrap text-ink-600 md:table-cell">
                  {row.pada ? fill(g.pada, { n: row.pada }) : g.sameSound}
                </td>
                <td className="px-4 py-2 text-center">{row.number}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export async function NaamPage({ lang, slug }: { lang: Lang; slug: string }) {
  const n = await api<NakshatraFull>(`/guide/nakshatras/${slug}`, DAY);
  if (!n) notFound();
  const g = guides(lang);
  const name = n.name[lang];
  const values = { name, letters: lettersOf(n, lang) };
  const facts: [string, string][] = [
    [g.naam.facts.lord, n.lord[lang]],
    [g.naam.facts.rashi, n.rashis.map((rashi) => rashi[lang]).join(", ")],
    [g.naam.facts.deity, n.deity[lang]],
    [g.naam.facts.symbol, n.symbol[lang]],
    [g.naam.facts.gana, n.gana[lang]],
    [g.naam.facts.yoni, n.yoni[lang]],
    [g.naam.facts.nadi, n.nadi[lang]],
    [g.naam.facts.tree, n.tree[lang]],
  ];

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.naam, page: "/naam" }, { label: name }]} />
      <Intro h1={fill(g.naam.h1, values)} h2={fill(g.naam.h2, { name: n.name[lang === "hi" ? "en" : "hi"] })} answer={fill(g.naam.answer, values)} />

      <section className="pb-8">
        <Heading>{g.naam.lettersTitle}</Heading>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {n.letters.map((letter) => (
            <div key={letter.pada} className="card text-center">
              <p className="text-sm text-ink-600">{fill(g.naam.pada, { n: letter.pada })}</p>
              <p className="font-serif text-3xl text-maroon-800">{letter.hi}</p>
              <p className="text-ink-600">{letter.en}</p>
            </div>
          ))}
        </div>
      </section>

      <NameTable lang={lang} title={g.naam.boys} rows={n.names.filter((row) => row.gender !== "girl")} />
      <NameTable lang={lang} title={g.naam.girls} rows={n.names.filter((row) => row.gender !== "boy")} />
      <p className="pb-8 text-sm text-ink-600">
        {g.naam.note} {g.naam.premium}
      </p>

      <section className="pb-8">
        <Heading>{fill(g.naam.aboutTitle, { name })}</Heading>
        <div className="card">
          <p>{n.nature[lang]}</p>
          <dl className="mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm md:grid-cols-[auto_1fr_auto_1fr]">
            {facts.map(([label, value]) => (
              <div key={label} className="col-span-2 grid grid-cols-subgrid">
                <dt className="font-semibold text-maroon-700">{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          {n.gandmool && (
            <p className="mt-3 rounded-lg bg-kesar-50 p-3 text-sm">
              {fill(g.naam.gandmool, { name })}{" "}
              <Link href={path(lang, "/dosh/gandmool")} className="text-kesar-700 underline">
                {g.dosh.read}
              </Link>
            </p>
          )}
        </div>
      </section>

      <nav className="flex justify-between gap-3 pb-8 text-sm">
        <Link href={path(lang, `/naam/${n.previous}`)} className="text-kesar-700 underline">
          ← {g.naam.previous}
        </Link>
        <Link href={path(lang, `/naam/${n.next}`)} className="text-kesar-700 underline">
          {g.naam.next} →
        </Link>
      </nav>
      <Cta lang={lang} />
    </>
  );
}

// ---------- planets in houses ----------

export function grahIndexMetadata(lang: Lang) {
  const g = guides(lang).grah;
  return guideMetadata(lang, "/grah", g.indexTitle, g.indexDescription);
}

export async function GrahIndexPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const planets = (await api<Planet[]>("/guide/planets", DAY)) ?? [];
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.grah }]} />
      <Intro h1={g.grah.indexH1} answer={g.grah.indexAnswer} />
      <section className="pb-8">
        <LinkGrid
          items={planets.map((planet) => ({
            href: path(lang, `/grah/${planet.slug}`),
            title: planet.name[lang],
            text: planet.day[lang],
          }))}
        />
      </section>
      <Cta lang={lang} />
    </>
  );
}

export async function grahMetadata(lang: Lang, slug: string) {
  const planet = ((await api<Planet[]>("/guide/planets", DAY)) ?? []).find((p) => p.slug === slug);
  if (!planet) return {};
  const g = guides(lang).grah;
  const values = { name: planet.name[lang] };
  return guideMetadata(lang, `/grah/${slug}`, fill(g.title, values), fill(g.description, values));
}

export async function GrahPage({ lang, slug }: { lang: Lang; slug: string }) {
  const planets = (await api<Planet[]>("/guide/planets", DAY)) ?? [];
  const planet = planets.find((p) => p.slug === slug);
  if (!planet) notFound();
  const g = guides(lang);
  const name = planet.name[lang];
  const ordinals = lang === "hi"
    ? ["प्रथम", "द्वितीय", "तृतीय", "चतुर्थ", "पंचम", "षष्ठ", "सप्तम", "अष्टम", "नवम", "दशम", "एकादश", "द्वादश"]
    : ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.grah, page: "/grah" }, { label: name }]} />
      <Intro h1={fill(g.grah.h1, { name })} h2={fill(g.grah.h2, { name: planet.name[lang === "hi" ? "en" : "hi"] })} answer={fill(g.grah.answer, { name })} />

      <section className="pb-8">
        <dl className="card grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
          <dt className="font-semibold text-maroon-700">{g.grah.facts.day}</dt>
          <dd>{planet.day[lang]}</dd>
          <dt className="font-semibold text-maroon-700">{g.grah.facts.deity}</dt>
          <dd>{planet.deity[lang]}</dd>
          <dt className="font-semibold text-maroon-700">{g.grah.facts.mantra}</dt>
          <dd lang="hi">{planet.mantra}</dd>
          <dt className="font-semibold text-maroon-700">{g.grah.facts.career}</dt>
          <dd>{planet.career[lang]}</dd>
        </dl>
      </section>

      <section className="pb-8">
        <Heading>{g.grah.housesTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-2">
          {planet.houses.map((house) => (
            <div key={house.house} className="card">
              <h3 className="font-semibold text-maroon-800">
                {fill(g.grah.house, { n: ordinals[house.house - 1] })} · {house.name[lang]}
              </h3>
              <p className="mt-1 text-ink-600">{house.text[lang].replace(/^[^:]+:\s*/, "")}</p>
            </div>
          ))}
        </div>
        <p className="mt-3 text-sm text-ink-600">{g.grah.note}</p>
      </section>

      <section className="grid gap-3 pb-8 md:grid-cols-2">
        <div className="card">
          <h2 className="font-semibold">{fill(g.grah.periodTitle, { name })}</h2>
          <p className="mt-1 text-ink-600">{planet.period[lang]}</p>
        </div>
        <div className="card">
          <h2 className="font-semibold">{g.grah.remedyTitle}</h2>
          <p className="mt-1 text-ink-600">{planet.remedy[lang]}</p>
        </div>
      </section>

      <section className="pb-8">
        <Heading>{g.grah.others}</Heading>
        <div className="flex flex-wrap gap-2">
          {planets
            .filter((other) => other.slug !== slug)
            .map((other) => (
              <Link key={other.slug} href={path(lang, `/grah/${other.slug}`)} className="rounded-full border border-kesar-100 bg-white px-4 py-2">
                {other.name[lang]}
              </Link>
            ))}
        </div>
      </section>
      <Cta lang={lang} />
    </>
  );
}

// ---------- dosha guides ----------

export function doshIndexMetadata(lang: Lang) {
  const g = guides(lang).dosh;
  return guideMetadata(lang, "/dosh", g.indexTitle, g.indexDescription);
}

export function DoshIndexPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.dosh }]} />
      <Intro h1={g.dosh.indexH1} answer={g.dosh.indexAnswer} />
      <section className="grid gap-3 pb-8 md:grid-cols-2">
        {DOSHA_SLUGS.map((slug) => (
          <Link key={slug} href={path(lang, `/dosh/${slug}`)} className="card hover:border-kesar-500">
            <h2 className="font-serif text-xl text-maroon-800">{g.doshas[slug].name}</h2>
            <p className="mt-1 text-ink-600">{g.doshas[slug].answer}</p>
            <span className="mt-2 inline-block font-semibold text-kesar-700">{g.dosh.read}</span>
          </Link>
        ))}
      </section>
      <Cta lang={lang} title={g.dosh.checkTitle} text={g.dosh.checkText} />
    </>
  );
}

export const isDosha = (slug: string): slug is DoshaSlug => (DOSHA_SLUGS as readonly string[]).includes(slug);

export function doshMetadata(lang: Lang, slug: string) {
  if (!isDosha(slug)) return {};
  const page = guides(lang).doshas[slug];
  return guideMetadata(lang, `/dosh/${slug}`, page.title, page.description);
}

export function DoshPage({ lang, slug }: { lang: Lang; slug: string }) {
  if (!isDosha(slug)) notFound();
  const g = guides(lang);
  const page = g.doshas[slug];
  return (
    <article>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.dosh, page: "/dosh" }, { label: page.name }]} />
      <Intro h1={page.title} answer={page.answer} />
      {page.sections.map((section) => (
        <section key={section.h} className="max-w-3xl pb-6">
          <h2 className="font-serif text-xl text-maroon-800">{section.h}</h2>
          {section.p.length === 1 ? (
            <p className="mt-2">{section.p[0]}</p>
          ) : (
            <ul className="mt-2 list-disc space-y-1 pl-5">
              {section.p.map((paragraph) => (
                <li key={paragraph}>{paragraph}</li>
              ))}
            </ul>
          )}
        </section>
      ))}
      <FaqList title={content(lang).faqTitle} items={page.faqs} />
      <section className="pb-8">
        <Heading>{g.dosh.others}</Heading>
        <div className="flex flex-wrap gap-2">
          {DOSHA_SLUGS.filter((other) => other !== slug).map((other) => (
            <Link key={other} href={path(lang, `/dosh/${other}`)} className="rounded-full border border-kesar-100 bg-white px-4 py-2">
              {g.doshas[other].name}
            </Link>
          ))}
        </div>
      </section>
      <Cta lang={lang} title={g.dosh.checkTitle} text={g.dosh.checkText} />
    </article>
  );
}

// ---------- Panchang of a city ----------

const cityName = (city: City, lang: Lang) => (lang === "hi" ? city.hi : city.name);

export async function cityMetadata(lang: Lang, slug: string) {
  const city = ((await api<City[]>("/cities", DAY)) ?? []).find((c) => c.slug === slug);
  if (!city) return {};
  const g = guides(lang).city;
  const values = { city: cityName(city, lang) };
  return guideMetadata(lang, `/panchang/${slug}`, fill(g.title, values), fill(g.description, values));
}

/** Links to the city pages, shown on the main Panchang page and on each city page. */
export async function CityLinks({ lang, except }: { lang: Lang; except?: string }) {
  const cities = (await api<City[]>("/cities", DAY)) ?? [];
  if (cities.length === 0) return null;
  const g = guides(lang).city;
  return (
    <section className="pb-8">
      <Heading>{except ? g.citiesTitle : g.allCities}</Heading>
      <div className="flex flex-wrap gap-2 text-sm">
        {cities
          .filter((city) => city.slug !== except)
          .map((city) => (
            <Link key={city.slug} href={path(lang, `/panchang/${city.slug}`)} className="rounded-full border border-kesar-100 bg-white px-3 py-1.5">
              {cityName(city, lang)}
            </Link>
          ))}
      </div>
    </section>
  );
}

export async function CityPanchangPage({ lang, slug }: { lang: Lang; slug: string }) {
  const city = ((await api<City[]>("/cities", DAY)) ?? []).find((c) => c.slug === slug);
  if (!city) notFound();
  const g = guides(lang);
  const c = content(lang);
  const place = { label: `${city.name}, ${city.state}, India`, latitude: city.latitude, longitude: city.longitude, timezone: city.timezone };
  const query = new URLSearchParams({ latitude: String(city.latitude), longitude: String(city.longitude), timezone: city.timezone });
  const initial = await api<PanchangData>(`/panchang?${query}`, HOUR / 6);
  const values = { city: cityName(city, lang), cityEn: city.name, cityHi: city.hi, state: city.state };

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.crumbs.panchang, page: "/panchang" }, { label: values.city }]} />
      <Intro h1={fill(g.city.h1, values)} h2={fill(g.city.h2, values)} answer={fill(g.city.answer, values)} />
      <section className="pb-8">
        <Panchang lang={lang} initial={initial} fixed={place} />
      </section>
      <section className="grid gap-3 pb-8 md:grid-cols-3">
        {c.panchang.what.map((item) => (
          <div key={item.title} className="card">
            <h2 className="font-semibold">{item.title}</h2>
            <p className="mt-1 text-sm text-ink-600">{item.text}</p>
          </div>
        ))}
      </section>
      <CityLinks lang={lang} except={slug} />
      <Cta lang={lang} />
    </>
  );
}

// ---------- Kundli Milan ----------

export function milanMetadata(lang: Lang) {
  const g = guides(lang).milan;
  return guideMetadata(lang, "/kundli-milan", g.title, g.description);
}

export function MilanPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const m = g.milan;
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: m.crumb }]} />
      <Intro h1={m.h1} h2={m.h2} answer={m.answer} />
      <section className="pb-8">
        <Milan lang={lang} />
      </section>

      <section className="pb-8">
        <Heading>{m.kootasTitle}</Heading>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {m.kootas.map((koota) => (
            <div key={koota.name} className="card">
              <h3 className="font-semibold">{koota.name}</h3>
              <p className="mt-1 text-sm text-ink-600">{koota.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-3 pb-8 md:grid-cols-3">
        {m.sections.map((section) => (
          <div key={section.h} className="card">
            <h2 className="font-semibold">{section.h}</h2>
            {section.p.map((paragraph) => (
              <p key={paragraph} className="mt-1 text-sm text-ink-600">
                {paragraph}
              </p>
            ))}
            {section === m.sections[1] && (
              <Link href={path(lang, "/dosh/manglik")} className="mt-2 inline-block text-sm font-semibold text-kesar-700 underline">
                {g.dosh.read}
              </Link>
            )}
          </div>
        ))}
      </section>
      <FaqList title={content(lang).faqTitle} items={m.faqs} />
      <Cta lang={lang} />
    </>
  );
}
