// The three public pages. Each is written once and shown in Hindi (at /) or
// English (at /en) depending on the "lang" it is given.

import Image from "next/image";
import Link from "next/link";

import ForgetButton from "@/components/ForgetButton";
import KundliForm from "@/components/KundliForm";
import { CityLinks } from "@/components/guides";
import Panchang, { PanchangStrip, type PanchangData } from "@/components/Panchang";
import { Breadcrumbs, LinkGrid, Schema } from "@/components/ui";
import { guides } from "@/lib/guides";
import Plans from "@/components/Plans";
import { content, fill, type Content } from "@/lib/content";
import { DRAFT, LAST_UPDATED, legal, type LegalKey } from "@/lib/legal";
import { API_URL, DEFAULT_CITY, getSite, path, SITE_URL, type Lang } from "@/lib/site";

const SAMPLE_PAGES = [1, 2, 3, 4];

function Heading({ children }: { children: React.ReactNode }) {
  return <h2 className="mb-3 font-serif text-2xl text-maroon-800">{children}</h2>;
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
        <details key={item.q} className="mb-2 rounded-xl border border-kesar-100 bg-white p-4">
          <summary className="cursor-pointer font-semibold">{item.q}</summary>
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
      <section className="pt-6 pb-8 md:grid md:grid-cols-2 md:items-center md:gap-10">
        <div>
          <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{c.home.h1}</h1>
          <p className="mt-3 text-ink-600">{c.home.intro}</p>
          <ul className="mt-4 flex flex-wrap gap-2 text-sm">
            {c.home.chips.map((chip) => (
              <li key={chip} className="rounded-full border border-kesar-100 bg-white px-3 py-1">
                ✓ {chip}
              </li>
            ))}
          </ul>
        </div>
        <div className="mt-6 md:mt-0">
          <KundliForm lang={lang} />
        </div>
      </section>

      <section className="pb-8">
        <Heading>{g.tools.title}</Heading>
        <LinkGrid items={g.tools.items.map((item) => ({ ...item, href: path(lang, item.href) }))} />
      </section>

      <section className="pb-8">
        <Heading>{c.home.freeTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.home.free.map((item) => (
            <div key={item.title} className="card">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="pb-8">
        <Heading>{c.home.plansTitle}</Heading>
        <p className="mb-3 text-ink-600">{c.home.plansIntro}</p>
        <Plans lang={lang} plans={site?.plans ?? null} />
        <Link
          href={path(lang, "/janam-patrika") + "#sample"}
          className="mt-3 inline-block font-semibold text-kesar-700 underline"
        >
          {c.home.sampleLink} →
        </Link>
      </section>

      <section className="pb-8">
        <Heading>{c.home.whyTitle}</Heading>
        <ul className="card space-y-2">
          {c.home.why.map((line) => (
            <li key={line} className="flex gap-2">
              <span aria-hidden className="text-kesar-600">
                ✦
              </span>
              {line}
            </li>
          ))}
        </ul>
      </section>

      <section className="pb-8">
        <PanchangStrip lang={lang} />
      </section>

      <section className="pb-8">
        <Heading>{c.home.trustTitle}</Heading>
        <div className="grid gap-3 md:grid-cols-3">
          {c.home.trust.map((item) => (
            <div key={item.title} className="card">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <Faq c={c} />

      {/* Room for, and then the bar itself: always within thumb reach on a phone */}
      <div className="h-16 md:hidden" />
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-kesar-100 bg-white p-3 md:hidden">
        <a href="#kundli" className="btn-primary">
          {c.home.stickyCta}
        </a>
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
