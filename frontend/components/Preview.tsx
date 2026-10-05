"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import Plans from "@/components/Plans";
import ShareCard from "@/components/ShareCard";
import { apiBody, useBirth } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { API_URL, path, plansFor, type Lang, type Plan, type Text } from "@/lib/site";
import { track } from "@/lib/track";

type Letter = Text & { pada?: number };
type PreviewData = {
  rashi: Text;
  nakshatra: Text;
  pada: number;
  time_known: boolean;
  name_letters: { primary: Text; nakshatra: Letter[]; rashi: Letter[] };
  certainty: { moon_sign_certain: boolean; nakshatra_certain: boolean; pada_certain: boolean } | null;
};

/** The free result: Rashi, Nakshatra, Pada and name letters, then the plans. */
export default function Preview({ lang }: { lang: Lang }) {
  const c = content(lang).preview;
  const birth = useBirth();
  const [data, setData] = useState<PreviewData | null>(null);
  const [plans, setPlans] = useState<Plan[] | null>(null);
  const [brand, setBrand] = useState("");
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0); // goes up by one for each "try again"

  useEffect(() => {
    if (!birth) return;
    let current = true;
    Promise.all([
      fetch(`${API_URL}/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(apiBody(birth)),
      }),
      fetch(`${API_URL}/site`),
    ])
      .then(async ([preview, site]) => {
        if (!preview.ok) throw new Error(String(preview.status));
        const result = await preview.json();
        const siteData = site.ok ? await site.json() : null;
        if (!current) return;
        setData(result);
        setPlans(siteData?.plans ?? null);
        setBrand(siteData?.brand.name[lang] ?? "");
        track("preview_shown");
      })
      .catch(() => current && setFailed(true));
    return () => {
      current = false;
    };
  }, [birth, attempt, lang]);

  if (birth === null) {
    return (
      <section className="py-10 text-center">
        <p className="text-ink-600">{c.noData}</p>
        <Link href={path(lang) + "#kundli"} className="btn-primary mx-auto mt-4 max-w-sm">
          {c.goHome}
        </Link>
      </section>
    );
  }
  if (failed) {
    return (
      <section className="py-10 text-center">
        <p role="alert" className="text-ink-600">
          {c.error}
        </p>
        <button
          onClick={() => {
            setFailed(false);
            setAttempt(attempt + 1);
          }}
          className="btn-primary mx-auto mt-4 max-w-sm"
        >
          {c.retry}
        </button>
      </section>
    );
  }
  if (!data || !birth) {
    return <p className="py-16 text-center text-ink-600">{c.loading}</p>;
  }

  const letters = data.name_letters;
  const changed = data.certainty
    ? [
        !data.certainty.moon_sign_certain && c.uncertainParts.rashi,
        !data.certainty.nakshatra_certain && c.uncertainParts.nakshatra,
        !data.certainty.pada_certain && c.uncertainParts.pada,
      ].filter(Boolean)
    : [];
  const shareText = fill(c.shareText, {
    name: birth.name || (lang === "hi" ? "शिशु" : "Baby"),
    rashi: data.rashi[lang],
    nakshatra: data.nakshatra[lang],
    pada: data.pada,
    letter: `${letters.primary.hi} (${letters.primary.en})`,
  });

  return (
    <>
      <section className="pt-6 pb-8">
        <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{c.title}</h1>
        {birth.name && <p className="mt-1 text-ink-600">{fill(c.for, { name: birth.name })}</p>}

        <div className="mt-4 rounded-2xl border-2 border-kesar-500 bg-white p-5">
          <dl className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div>
              <dt className="text-sm text-ink-600">{c.rashi}</dt>
              <dd className="font-serif text-2xl text-maroon-800">{data.rashi[lang]}</dd>
            </div>
            <div>
              <dt className="text-sm text-ink-600">{c.nakshatra}</dt>
              <dd className="font-serif text-2xl text-maroon-800">{data.nakshatra[lang]}</dd>
            </div>
            <div>
              <dt className="text-sm text-ink-600">{c.pada}</dt>
              <dd className="font-serif text-2xl text-maroon-800">{data.pada}</dd>
            </div>
            <div>
              <dt className="text-sm text-ink-600">{c.letter}</dt>
              <dd className="font-serif text-2xl text-maroon-800">
                {letters.primary.hi} <span className="text-lg text-ink-600">({letters.primary.en})</span>
              </dd>
            </div>
          </dl>

          <h2 className="mt-5 text-sm font-semibold">{c.nakshatraLetters}</h2>
          <ul className="mt-1 flex flex-wrap gap-2">
            {letters.nakshatra.map((letter) => (
              <li
                key={letter.pada}
                className={`rounded-lg border px-3 py-1 font-semibold ${
                  letter.pada === data.pada ? "border-kesar-600 bg-kesar-600 text-white" : "border-kesar-100"
                }`}
              >
                {letter.hi} {letter.en}
                {letter.pada === data.pada && <span className="ml-1 text-xs font-normal">({c.birthPada})</span>}
              </li>
            ))}
          </ul>

          <h2 className="mt-4 text-sm font-semibold">{c.rashiLetters}</h2>
          <ul className="mt-1 flex flex-wrap gap-2">
            {letters.rashi.map((letter) => (
              <li key={letter.hi} className="rounded-lg border border-kesar-100 px-3 py-1">
                {letter.hi} {letter.en}
              </li>
            ))}
          </ul>

          {!data.time_known && (
            <p className="mt-4 rounded-lg bg-kesar-50 p-3 text-sm text-ink-600">
              {changed.length > 0
                ? fill(c.uncertain, { what: changed.join(lang === "hi" ? " और " : " and ") })
                : c.timeNote}
            </p>
          )}

          <div className="mt-5 grid gap-2 md:grid-cols-2">
            <ShareCard
              brand={brand}
              heading={fill(c.cardHeading, { name: birth.name || (lang === "hi" ? "शिशु" : "Baby") })}
              rows={[
                { label: c.rashi, value: data.rashi[lang] },
                { label: c.nakshatra, value: `${data.nakshatra[lang]} · ${c.pada} ${data.pada}` },
                { label: c.letter, value: `${letters.primary.hi} (${letters.primary.en})` },
              ]}
              blessing={c.cardBlessing}
              buttonLabel={c.card}
              shareText={shareText}
            />
            <a
              href={`https://wa.me/?text=${encodeURIComponent(shareText)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              {c.share}
            </a>
          </div>
          <Link href={path(lang) + "#kundli"} className="mt-2 flex h-10 items-center justify-center text-ink-600 underline">
            {c.edit}
          </Link>
        </div>
      </section>

      <section className="pb-10">
        <h2 className="mb-3 font-serif text-2xl text-maroon-800">{c.nextTitle}</h2>
        <Plans
          lang={lang}
          plans={plans && plansFor(plans, birth.date)}
          action={{ href: (plan) => `${path(lang, "/order")}?plan=${plan.id}`, label: c.choose }}
        />
      </section>
    </>
  );
}
