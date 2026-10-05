// Shubh Muhurat pages: the list of ceremonies, and the dates of one ceremony in one year.

import Link from "next/link";
import { notFound } from "next/navigation";

import { guideMetadata } from "@/components/guides";
import { Breadcrumbs, Cta, FaqList, Heading, Intro } from "@/components/ui";
import { content, fill } from "@/lib/content";
import { guides } from "@/lib/guides";
import { api, path, type Lang, type Text } from "@/lib/site";

type Index = { years: number[]; types: { type: string; name: Text; what: Text; counts: Record<string, number> }[] };
type ShubhDate = { date: string; weekday: Text; tithi: Text; paksha: Text; nakshatra: Text };
type Muhurat = {
  type: string; year: number; name: Text; what: Text; rule: Text; count: number;
  months: { month: number; dates: ShubhDate[] }[];
  set_aside: { reason: Text; why: Text; from: string; to: string }[];
  caution: Text;
};

const HOUR = 3600;
const locale = (lang: Lang) => (lang === "hi" ? "hi-IN" : "en-IN");

/** "2027-02-12" -> "12 February" / "12 फ़रवरी" */
function dayMonth(iso: string, lang: Lang) {
  return new Date(iso + "T00:00:00").toLocaleDateString(locale(lang), { day: "numeric", month: "long" });
}

function monthName(year: number, month: number, lang: Lang) {
  return new Date(year, month - 1, 1).toLocaleDateString(locale(lang), { month: "long", year: "numeric" });
}

/** Today's date in India, as YYYY-MM-DD */
function todayInIndia() {
  return new Date(Date.now() + 5.5 * HOUR * 1000).toISOString().slice(0, 10);
}

// ---------- the list of ceremonies ----------

export async function muhuratIndexMetadata(lang: Lang) {
  const g = guides(lang).muhurat;
  const year = (await api<Index>("/muhurat", HOUR))?.years[0] ?? new Date().getFullYear();
  return guideMetadata(lang, "/muhurat", fill(g.indexTitle, { year }), fill(g.indexDescription, { year }));
}

export async function MuhuratIndexPage({ lang }: { lang: Lang }) {
  const g = guides(lang);
  const index = await api<Index>("/muhurat", HOUR);
  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: g.muhurat.crumb }]} />
      <Intro
        h1={fill(g.muhurat.indexH1, { year: index?.years[0] ?? "" }).trim()}
        h2={g.muhurat.h2}
        answer={index ? g.muhurat.indexAnswer : g.muhurat.unavailable}
      />
      {index && (
        <section className="grid gap-3 pb-8 md:grid-cols-2">
          {index.types.map((item) => (
            <div key={item.type} className="card">
              <h2 className="font-serif text-xl text-maroon-800">{item.name[lang]}</h2>
              <ul className="mt-2 flex flex-wrap gap-2">
                {index.years.map((year) => (
                  <li key={year}>
                    <Link
                      href={path(lang, `/muhurat/${item.type}/${year}`)}
                      className="flex min-h-10 items-center rounded-full border border-kesar-100 bg-kesar-50 px-4 font-semibold text-kesar-700"
                    >
                      {fill(g.muhurat.count, { year, count: item.counts[String(year)] })}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}
      <section className="grid gap-3 pb-8 md:grid-cols-3">
        {g.muhurat.sections.map((section) => (
          <div key={section.h} className="card">
            <h2 className="font-semibold">{section.h}</h2>
            <p className="mt-1 text-sm text-ink-600">{section.p}</p>
          </div>
        ))}
      </section>
      <FaqList title={content(lang).faqTitle} items={g.muhurat.faqs} />
      <section className="pb-8">
        <Link href={path(lang, "/panchang")} className="font-semibold text-kesar-700 underline">
          {content(lang).panchang.stripMore}
        </Link>
      </section>
      <Cta lang={lang} />
    </>
  );
}

// ---------- one ceremony, one year ----------

async function find(type: string, year: string) {
  if (!/^\d{4}$/.test(year)) return null;
  return api<Muhurat>(`/muhurat/${type}/${year}`, HOUR);
}

export async function muhuratMetadata(lang: Lang, type: string, year: string) {
  const found = await find(type, year);
  if (!found) return {};
  const g = guides(lang).muhurat;
  const values = { name: found.name[lang], what: found.what[lang], year: found.year };
  return guideMetadata(lang, `/muhurat/${type}/${year}`, fill(g.title, values), fill(g.description, values));
}

export async function MuhuratPage({ lang, type, year }: { lang: Lang; type: string; year: string }) {
  const found = await find(type, year);
  if (!found) notFound();
  const g = guides(lang);
  const index = await api<Index>("/muhurat", HOUR);
  const values = { name: found.name[lang], what: found.what[lang], year: found.year, count: found.count };
  const today = todayInIndia();

  return (
    <>
      <Breadcrumbs
        lang={lang}
        trail={[{ label: g.muhurat.crumb, page: "/muhurat" }, { label: fill(g.muhurat.h1, values) }]}
      />
      <Intro h1={fill(g.muhurat.h1, values)} h2={found.name[lang === "hi" ? "en" : "hi"] + " " + found.year} answer={fill(g.muhurat.answer, values)} />

      <section className="grid gap-3 pb-8 md:grid-cols-2">
        {found.months.map((month) => (
          <div key={month.month} className="card">
            <h2 className="font-serif text-xl text-maroon-800">{monthName(found.year, month.month, lang)}</h2>
            {month.dates.length === 0 ? (
              <p className="mt-2 text-sm text-ink-600">{g.muhurat.none}</p>
            ) : (
              <ul className="mt-2 divide-y divide-kesar-100">
                {month.dates.map((day) => (
                  <li key={day.date} className={`py-2 ${day.date < today ? "opacity-60" : ""}`}>
                    <p className="font-semibold">
                      <time dateTime={day.date}>{dayMonth(day.date, lang)}</time> · {day.weekday[lang]}
                      {day.date < today && <span className="ml-2 text-xs font-normal text-ink-600">({g.muhurat.passed})</span>}
                    </p>
                    <p className="text-sm text-ink-600">
                      {day.paksha[lang]} {day.tithi[lang]} · {day.nakshatra[lang]}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </section>

      <p className="mb-8 rounded-xl bg-haldi-300/40 p-4 text-sm">{found.caution[lang]}</p>

      {found.set_aside.length > 0 && (
        <section className="pb-8">
          <Heading>{fill(g.muhurat.setAsideTitle, values)}</Heading>
          <ul className="grid gap-3 md:grid-cols-2">
            {found.set_aside.map((period) => (
              <li key={period.reason.en + period.from} className="card">
                <p className="font-semibold">{period.reason[lang]}</p>
                <p>
                  {dayMonth(period.from, lang)} {g.muhurat.until} {dayMonth(period.to, lang)}
                </p>
                <p className="mt-1 text-sm text-ink-600">{period.why[lang]}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="pb-8">
        <Heading>{g.muhurat.ruleTitle}</Heading>
        <p className="max-w-3xl">{found.rule[lang]}</p>
      </section>

      {index && (
        <section className="pb-8">
          <Heading>{g.muhurat.otherYears}</Heading>
          <div className="flex flex-wrap gap-2">
            {index.years
              .filter((other) => other !== found.year)
              .map((other) => (
                <Link key={other} href={path(lang, `/muhurat/${type}/${other}`)} className="rounded-full border border-kesar-100 bg-white px-4 py-2">
                  {found.name[lang]} {other}
                </Link>
              ))}
          </div>
          <div className="mt-6">
            <Heading>{g.muhurat.otherTypes}</Heading>
          </div>
          <div className="flex flex-wrap gap-2">
            {index.types
              .filter((other) => other.type !== type)
              .map((other) => (
                <Link key={other.type} href={path(lang, `/muhurat/${other.type}/${found.year}`)} className="rounded-full border border-kesar-100 bg-white px-4 py-2">
                  {other.name[lang]} {found.year}
                </Link>
              ))}
          </div>
        </section>
      )}
      <FaqList title={content(lang).faqTitle} items={g.muhurat.faqs} />
      <Cta lang={lang} />
    </>
  );
}
