// Daily pages: Choghadiya and Rashifal.

import Link from "next/link";
import { notFound } from "next/navigation";

import { CityLinks } from "@/components/guides";
import { guideMetadata } from "@/components/guides";
import Panchang, { type PanchangData } from "@/components/Panchang";
import { Breadcrumbs, Cta, FaqList, Heading, Intro } from "@/components/ui";
import { content, fill } from "@/lib/content";
import { guides } from "@/lib/guides";
import { api, DEFAULT_CITY, path, type Lang, type Text } from "@/lib/site";

type Rashi = {
  slug: string; name: Text; lord: Text; house: number;
  mood: Text; text: Text; good_for: Text; go_easy: Text; basis: Text;
};
type Rashifal = { date: string; moon_sign: Text; moon_nakshatra: Text; method: Text; rashis: Rashi[] };

const TEN_MINUTES = 600;

/** "2026-09-27" -> "27 Sep 2026" / "27 सितम्बर 2026" */
function longDate(iso: string, lang: Lang) {
  return new Date(iso + "T00:00:00").toLocaleDateString(lang === "hi" ? "hi-IN" : "en-IN", {
    day: "numeric", month: "long", year: "numeric",
  });
}

function nextDay(iso: string) {
  const day = new Date(iso + "T00:00:00Z");
  day.setUTCDate(day.getUTCDate() + 1);
  return day.toISOString().slice(0, 10);
}

// ---------- Choghadiya ----------

export function choghadiyaMetadata(lang: Lang) {
  const g = guides(lang).choghadiya;
  return guideMetadata(lang, "/choghadiya", g.title, g.description);
}

export async function ChoghadiyaPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const query = new URLSearchParams({
    latitude: String(DEFAULT_CITY.latitude), longitude: String(DEFAULT_CITY.longitude), timezone: DEFAULT_CITY.timezone,
  });
  const initial = await api<PanchangData>(`/panchang?${query}`, TEN_MINUTES);
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.choghadiya.crumb }]} />
      <Intro h1={g.choghadiya.h1} h2={g.choghadiya.h2} answer={g.choghadiya.answer} />
      <section className="pb-8">
        <Panchang lang={lang} initial={initial} only="choghadiya" />
      </section>
      <section className="grid gap-3 pb-8 md:grid-cols-3">
        {g.choghadiya.sections.map((section) => (
          <div key={section.h} className="card">
            <h2 className="font-semibold">{section.h}</h2>
            <p className="mt-1 text-sm text-ink-600">{section.p}</p>
          </div>
        ))}
      </section>
      <FaqList title={content(lang).faqTitle} items={g.choghadiya.faqs} />
      <section className="pb-8">
        <Link href={path(lang, "/panchang")} className="font-semibold text-kesar-700 underline">
          {content(lang).panchang.stripMore}
        </Link>
      </section>
      <CityLinks lang={lang} />
      <Cta lang={lang} />
    </>
  );
}

// ---------- Rashifal ----------

export function rashifalIndexMetadata(lang: Lang) {
  const g = guides(lang).rashifal;
  return guideMetadata(lang, "/rashifal", g.indexTitle, g.indexDescription);
}

export async function RashifalIndexPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const today = await api<Rashifal>("/rashifal", TEN_MINUTES);
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.rashifal.crumb }]} />
      <Intro
        h1={g.rashifal.indexH1}
        h2={g.rashifal.h2}
        answer={today ? fill(g.rashifal.indexAnswer, { date: longDate(today.date, lang), moon: today.moon_sign[lang], nakshatra: today.moon_nakshatra[lang] }) : g.rashifal.unavailable}
      />
      {today && (
        <section className="grid gap-3 pb-8 md:grid-cols-2">
          {today.rashis.map((rashi) => (
            <Link key={rashi.slug} href={path(lang, `/rashifal/${rashi.slug}`)} className="card hover:border-kesar-500">
              <h2 className="font-serif text-xl text-maroon-800">{rashi.name[lang]}</h2>
              <p className="font-semibold">{rashi.mood[lang]}</p>
              <p className="mt-1 text-sm text-ink-600">{rashi.text[lang]}</p>
              <span className="mt-2 inline-block text-sm font-semibold text-kesar-700">{g.dosh.read}</span>
            </Link>
          ))}
        </section>
      )}
      {today && <p className="pb-8 text-sm text-ink-600">{today.method[lang]}</p>}
      <section className="pb-8">
        <Link href={path(lang, "/rashi-nakshatra")} className="font-semibold text-kesar-700 underline">
          {g.rashifal.unknown}
        </Link>
      </section>
      <FaqList title={content(lang).faqTitle} items={g.rashifal.faqs} />
      <Cta lang={lang} />
    </>
  );
}

async function findRashi(slug: string) {
  const today = await api<Rashifal>("/rashifal", TEN_MINUTES);
  const rashi = today?.rashis.find((item) => item.slug === slug);
  return today && rashi ? { today, rashi } : null;
}

export async function rashifalMetadata(lang: Lang, slug: string) {
  const found = await findRashi(slug);
  if (!found) return {};
  const g = guides(lang).rashifal;
  const values = { rashi: found.rashi.name[lang] };
  return guideMetadata(lang, `/rashifal/${slug}`, fill(g.title, values), fill(g.description, values));
}

function Forecast({ lang, heading, rashi }: { lang: Lang; heading: string; rashi: Rashi }) {
  const g = guides(lang).rashifal;
  return (
    <section className="pb-6">
      <Heading>{heading}</Heading>
      <div className="card">
        <p className="font-serif text-xl text-maroon-800">{rashi.mood[lang]}</p>
        <p className="mt-2">{rashi.text[lang]}</p>
        <dl className="mt-3 grid gap-2 md:grid-cols-2">
          <div className="rounded-lg bg-kesar-50 p-3">
            <dt className="text-sm font-semibold text-green-800">{g.goodFor}</dt>
            <dd>{rashi.good_for[lang]}</dd>
          </div>
          <div className="rounded-lg bg-kesar-50 p-3">
            <dt className="text-sm font-semibold text-kesar-700">{g.goEasy}</dt>
            <dd>{rashi.go_easy[lang]}</dd>
          </div>
        </dl>
        <p className="mt-3 text-sm text-ink-600">{rashi.basis[lang]}</p>
      </div>
    </section>
  );
}

export async function RashifalPage({ lang, slug }: { lang: Lang; slug: string }) {
  const found = await findRashi(slug);
  if (!found) notFound();
  const { today, rashi } = found;
  const g = guides(lang);
  const tomorrow = (await api<Rashifal>(`/rashifal?date=${nextDay(today.date)}`, TEN_MINUTES))?.rashis.find(
    (item) => item.slug === slug,
  );
  const name = rashi.name[lang];

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.rashifal.crumb, page: "/rashifal" }, { label: name }]} />
      <Intro
        h1={fill(g.rashifal.h1, { rashi: name })}
        h2={fill(g.rashifal.h2Rashi, { rashi: rashi.name[lang === "hi" ? "en" : "hi"] })}
        answer={fill(g.rashifal.answer, { rashi: name, date: longDate(today.date, lang), lord: rashi.lord[lang] })}
      />
      <Forecast lang={lang} heading={fill(g.rashifal.today, { date: longDate(today.date, lang) })} rashi={rashi} />
      {tomorrow && <Forecast lang={lang} heading={fill(g.rashifal.tomorrow, { date: longDate(nextDay(today.date), lang) })} rashi={tomorrow} />}
      <p className="pb-8 text-sm text-ink-600">{today.method[lang]}</p>

      <section className="pb-8">
        <Heading>{g.rashifal.others}</Heading>
        <div className="flex flex-wrap gap-2">
          {today.rashis
            .filter((other) => other.slug !== slug)
            .map((other) => (
              <Link key={other.slug} href={path(lang, `/rashifal/${other.slug}`)} className="rounded-full border border-kesar-100 bg-white px-4 py-2">
                {other.name[lang]}
              </Link>
            ))}
        </div>
      </section>
      <Cta lang={lang} title={g.rashifal.ctaTitle} text={g.rashifal.ctaText} />
    </>
  );
}
