// The three public pages. Each is written once and shown in Hindi (at /) or
// English (at /en) depending on the "lang" it is given.

import Image from "next/image";
import Link from "next/link";

import ForgetButton from "@/components/ForgetButton";
import KundliForm from "@/components/KundliForm";
import { CityLinks } from "@/components/guides";
import Panchang, { PanchangStrip, type PanchangData } from "@/components/Panchang";
import { Breadcrumbs, Schema, ToolIcon, Wheel } from "@/components/ui";
import { guides } from "@/lib/guides";
import Plans from "@/components/Plans";
import { content, fill, type Content } from "@/lib/content";
import { DRAFT, LAST_UPDATED, legal, type LegalKey } from "@/lib/legal";
import { API_URL, DEFAULT_CITY, getSite, path, SITE_URL, type Lang } from "@/lib/site";

const SAMPLE_PAGES = [1, 2, 3, 4];

function Heading({ children }: { children: React.ReactNode }) {
  return <h2 className="section-title">{children}</h2>;
}

/** Questions and answers, also given to search engines as FAQ data. */
function Faq({ c }: { c: Content }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: c.faqs.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: { "@type": "Answer", text: item.a },
    })),
  };
  return (
    <section className="pb-10">
      <Heading>{c.faqTitle}</Heading>
      {c.faqs.map((item) => (
        <details key={item.q} className="faq">
          <summary>{item.q}</summary>
          <p className="mt-2 text-ink-600">{item.a}</p>
        </details>
      ))}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
    </section>
  );
}

/** Search-engine tags shared by the public pages: title, description and the hi/en pair. */
export async function pageMetadata(
  lang: Lang,
  page: string,
  key: "home" | "patrika" | "about" | "panchang" | LegalKey,
) {
  const all = content(lang);
  const c = key === "home" || key === "patrika" || key === "about" || key === "panchang" ? all[key] : legal(lang)[key];
  const site = await getSite();
  const lowest = site ? Math.min(...site.plans.map((plan) => plan.price)) : "";
  const brand = site?.brand.name[lang];
  return {
    title: fill(c.title, { price: lowest }) + (brand ? ` | ${brand}` : ""),
    description: fill(c.description, { price: lowest }),
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

export async function HomePage({ lang }: { lang: Lang }) {
  const c = content(lang);
  const g = guides(lang);
  const site = await getSite();

  return (
    <>
      <section className="bleed night rounded-b-[2rem] pt-8 pb-10 md:rounded-b-[3rem] md:pt-14 md:pb-16">
        <Wheel className="absolute -top-24 -right-28 size-[26rem] text-haldi-300/20 md:top-[-6rem] md:right-[38%] md:size-[34rem]" />
        <div className="relative md:grid md:grid-cols-[1.1fr_1fr] md:items-center md:gap-12">
          <div>
            {site?.brand.tagline[lang] && (
              <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-haldi-300/40 bg-white/10 px-3 py-1 text-sm text-haldi-300">
                <span aria-hidden>✦</span>
                {site.brand.tagline[lang]}
              </p>
            )}
            <h1 className="font-serif text-[32px] leading-tight md:text-5xl md:leading-[1.15]">{c.home.h1}</h1>
            <p className="mt-4 text-[17px] text-white/85 md:text-lg">{c.home.intro}</p>
            <ul className="mt-5 flex flex-wrap gap-2 text-sm">
              {c.home.chips.map((chip) => (
                <li key={chip} className="rounded-full border border-white/20 bg-white/10 px-3 py-1 backdrop-blur">
                  <span aria-hidden className="text-haldi-300">✓</span> {chip}
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-7 text-ink-900 md:mt-0 [&>form]:shadow-2xl [&>form]:ring-1 [&>form]:ring-haldi-300/40">
            <KundliForm lang={lang} />
          </div>
        </div>
      </section>

      <section className="pt-10 pb-10">
        <Heading>{g.tools.title}</Heading>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {g.tools.items.map((item) => (
            <Link key={item.href} href={path(lang, item.href)} className="card flex flex-col gap-3 last:col-span-2 last:flex-row last:items-center md:flex-row md:items-center md:last:col-span-1">
              <ToolIcon page={item.href} />
              <span>
                <span className="block font-semibold text-maroon-800">{item.title}</span>
                <span className="mt-0.5 block text-sm text-ink-600">{item.text}</span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="pb-10">
        <Heading>{c.home.freeTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.home.free.map((item, index) => (
            <div key={item.title} className="card flex gap-4">
              <span className="badge font-serif text-xl">{index + 1}</span>
              <div>
                <h3 className="font-semibold text-maroon-800">{item.title}</h3>
                <p className="mt-1 text-sm text-ink-600">{item.text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="pb-10">
        <Heading>{c.home.plansTitle}</Heading>
        <p className="mb-4 text-ink-600">{c.home.plansIntro}</p>
        <Plans lang={lang} plans={site?.plans ?? null} />
        <Link
          href={path(lang, "/janam-patrika") + "#sample"}
          className="mt-4 inline-block font-semibold text-kesar-700 underline decoration-kesar-500/50 underline-offset-4"
        >
          {c.home.sampleLink} →
        </Link>
      </section>

      <section className="pb-10">
        <div className="night rounded-3xl p-6 shadow-xl md:p-10">
          <Wheel className="absolute -right-20 -bottom-24 size-72 text-haldi-300/20" />
          <h2 className="relative font-serif text-2xl md:text-3xl">{c.home.whyTitle}</h2>
          <ul className="relative mt-5 grid gap-x-8 gap-y-3 md:grid-cols-2">
            {c.home.why.map((line) => (
              <li key={line} className="flex gap-3 text-white/90">
                <span aria-hidden className="mt-0.5 text-haldi-300">
                  ✦
                </span>
                {line}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="pb-10">
        <PanchangStrip lang={lang} />
      </section>

      <section className="pb-10">
        <Heading>{c.home.trustTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.home.trust.map((item) => (
            <div key={item.title} className="card border-t-4 border-t-haldi-400">
              <h3 className="font-semibold text-maroon-800">{item.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      {site?.astrologer && (
        <section className="pb-8">
          <Heading>{c.about.astrologerTitle}</Heading>
          <div className="card">
            <h3 className="font-serif text-xl text-maroon-800">{site.astrologer.name[lang]}</h3>
            <p className="text-sm font-semibold text-kesar-700">{fill(c.about.astrologerYears, { n: site.astrologer.experience_years })}</p>
            <p className="mt-2 text-ink-600">{site.astrologer.bio[lang]}</p>
          </div>
        </section>
      )}

      <Faq c={c} />

      {/* Room for, and then the bar itself: always within thumb reach on a phone */}
      <div className="h-16 md:hidden" />
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-kesar-100 bg-white/95 p-3 shadow-[0_-8px_24px_-12px_rgb(122_31_43/0.3)] backdrop-blur md:hidden">
        <div className="flex gap-2">
          <a href="#kundli" className="btn-primary">
            {c.home.stickyCta}
          </a>
          {site?.contact?.whatsapp && (
            <a
              href={`https://wa.me/${site.contact.whatsapp}`}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={c.about.whatsapp}
              className="flex h-12 shrink-0 items-center rounded-xl border border-kesar-600 px-4 font-semibold text-kesar-700"
            >
              WhatsApp
            </a>
          )}
        </div>
      </div>
    </>
  );
}

export async function PatrikaPage({ lang }: { lang: Lang }) {
  const c = content(lang);
  const g = guides(lang);
  const site = await getSite();

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: c.nav.patrika }]} />
      {site && (
        <Schema
          data={{
            "@context": "https://schema.org",
            "@type": "Product",
            name: c.patrika.h1,
            description: c.patrika.description,
            image: SITE_URL + `/sample/${lang}-1.jpg`,
            brand: { "@type": "Brand", name: site.brand.name[lang] },
            offers: site.plans.map((plan) => ({
              "@type": "Offer",
              name: plan.name[lang],
              price: plan.price,
              priceCurrency: "INR",
              availability: "https://schema.org/InStock",
              url: SITE_URL + path(lang, "/janam-patrika"),
            })),
          }}
        />
      )}
      <section className="pt-4 pb-8">
        <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{c.patrika.h1}</h1>
        <p className="mt-3 max-w-3xl text-ink-600">{c.patrika.intro}</p>
      </section>

      <section className="pb-8">
        <Heading>{c.patrika.insideTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.patrika.inside.map((item) => (
            <div key={item.title} className="card">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="sample" className="scroll-mt-20 pb-8">
        <Heading>{c.patrika.sampleTitle}</Heading>
        <div className="flex snap-x gap-3 overflow-x-auto pb-2">
          {SAMPLE_PAGES.map((number) => (
            <a
              key={number}
              href={`/sample/${lang}-${number}.jpg`}
              target="_blank"
              rel="noopener"
              className="shrink-0 snap-start"
            >
              <Image
                src={`/sample/${lang}-${number}.jpg`}
                alt={`${c.patrika.sampleTitle} ${number}`}
                width={596}
                height={842}
                className="h-auto w-64 rounded-lg border border-kesar-100 shadow-sm md:w-72"
              />
            </a>
          ))}
        </div>
        <p className="mt-2 text-sm text-ink-600">{c.patrika.sampleNote}</p>
      </section>

      <section className="pb-8">
        <Heading>{g.positioning.title}</Heading>
        <div className="overflow-hidden rounded-2xl border border-kesar-100 bg-white">
          <div className="grid grid-cols-2 bg-kesar-50 text-sm font-semibold text-maroon-800">
            <p className="px-4 py-2">{g.positioning.themLabel}</p>
            <p className="px-4 py-2">{g.positioning.usLabel}</p>
          </div>
          {g.positioning.rows.map((row) => (
            <div key={row.us} className="grid grid-cols-2 border-t border-kesar-100">
              <p className="px-4 py-3 text-ink-600">{row.them}</p>
              <p className="px-4 py-3 font-semibold">{row.us}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="pb-8">
        <Heading>{c.patrika.plansTitle}</Heading>
        <Plans lang={lang} plans={site?.plans ?? null} />
        <Link href={path(lang) + "#kundli"} className="btn-primary mt-4 md:mx-auto md:max-w-sm">
          {c.patrika.start}
        </Link>
      </section>

      <Faq c={c} />
    </>
  );
}

export async function AboutPage({ lang }: { lang: Lang }) {
  const c = content(lang);
  const site = await getSite();

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: c.nav.about }]} />
      <section className="pt-4 pb-8">
        <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{c.about.h1}</h1>
        <p className="mt-3 max-w-3xl text-ink-600">{c.about.intro}</p>
      </section>

      <section className="pb-8">
        <Heading>{c.about.methodTitle}</Heading>
        <ul className="card space-y-2">
          {c.about.method.map((line) => (
            <li key={line} className="flex gap-2">
              <span aria-hidden className="text-kesar-600">
                ✓
              </span>
              {line}
            </li>
          ))}
        </ul>
      </section>

      {site?.astrologer && (
        <section className="pb-8">
          <Heading>{c.about.astrologerTitle}</Heading>
          <div className="card">
            <h3 className="font-serif text-xl text-maroon-800">{site.astrologer.name[lang]}</h3>
            <p className="text-sm font-semibold text-kesar-700">{fill(c.about.astrologerYears, { n: site.astrologer.experience_years })}</p>
            <p className="mt-2 text-ink-600">{site.astrologer.bio[lang]}</p>
          </div>
        </section>
      )}

      <section className="pb-8">
        <Heading>{c.about.promisesTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.about.promises.map((item) => (
            <div key={item.title} className="card">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="pb-10">
        <Link href={path(lang) + "#kundli"} className="btn-primary md:mx-auto md:max-w-sm">
          {c.about.cta}
        </Link>
      </section>
    </>
  );
}

export async function PanchangPage({ lang }: { lang: Lang }) {
  const c = content(lang);
  // The Panchang for Delhi is prepared on the server so the page is useful at once and to
  // search engines; the visitor's own city is then loaded in the browser.
  let initial: PanchangData | null = null;
  try {
    const query = new URLSearchParams({
      latitude: String(DEFAULT_CITY.latitude),
      longitude: String(DEFAULT_CITY.longitude),
      timezone: DEFAULT_CITY.timezone,
    });
    const response = await fetch(`${API_URL}/panchang?${query}`, { next: { revalidate: 600 } });
    if (response.ok) initial = await response.json();
  } catch {
    initial = null;
  }

  return (
    <>
      <Breadcrumbs lang={lang} trail={[{ label: c.nav.panchang }]} />
      <section className="pt-4 pb-6">
        <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{c.panchang.h1}</h1>
        <p className="mt-3 max-w-3xl text-ink-600">{c.panchang.intro}</p>
      </section>

      <section className="pb-8">
        <Panchang lang={lang} initial={initial} />
      </section>

      <section className="pb-8">
        <div className="grid gap-3 md:grid-cols-3">
          {c.panchang.what.map((item) => (
            <div key={item.title} className="card">
              <h2 className="font-semibold">{item.title}</h2>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <CityLinks lang={lang} />

      <section className="pb-10">
        <Link href={path(lang) + "#kundli"} className="btn-primary md:mx-auto md:max-w-md">
          {c.panchang.cta}
        </Link>
      </section>
    </>
  );
}

/** Privacy, Terms, Refund and Disclaimer pages (wording in lib/legal.ts). */
export async function LegalPage({ lang, doc }: { lang: Lang; doc: LegalKey }) {
  const all = legal(lang);
  const page = all[doc];
  const site = await getSite();
  const email = site?.contact?.email;

  return (
    <article className="mx-auto max-w-3xl py-6">
      <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{page.title}</h1>
      <p className="mt-1 text-sm text-ink-600">
        {all.updated}: {LAST_UPDATED}
      </p>
      {DRAFT && <p className="mt-3 rounded-lg bg-haldi-300/40 p-3 text-sm">{all.draft}</p>}

      {page.sections.map((section) => (
        <section key={section.h} className="mt-6">
          <h2 className="font-serif text-xl text-maroon-800">{section.h}</h2>
          {section.p.map((paragraph) => (
            <p key={paragraph} className="mt-2 text-ink-900">
              {paragraph}
            </p>
          ))}
        </section>
      ))}

      {email && (
        <p className="mt-6">
          {content(lang).footer.contact}:{" "}
          <a href={`mailto:${email}`} className="text-kesar-700 underline">
            {email}
          </a>
        </p>
      )}
      {doc === "privacy" && <ForgetButton lang={lang} />}
    </article>
  );
}
