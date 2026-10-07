// Small pieces shared by the reference pages.

import Link from "next/link";

import { guides } from "@/lib/guides";
import { path, SITE_URL, type Lang } from "@/lib/site";

/** Data for search engines, written into the page as JSON-LD. */
export function Schema({ data }: { data: object }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}

/** Decoration only: a zodiac wheel of twelve divisions, drawn in gold lines. */
export function Wheel({ className = "" }: { className?: string }) {
  const spokes = Array.from({ length: 12 }, (_, index) => index * 30);
  return (
    <svg aria-hidden viewBox="0 0 200 200" fill="none" stroke="currentColor" className={`wheel pointer-events-none ${className}`}>
      <circle cx="100" cy="100" r="98" strokeWidth="1" />
      <circle cx="100" cy="100" r="76" strokeWidth="1" />
      <circle cx="100" cy="100" r="42" strokeWidth="0.75" />
      {spokes.map((angle) => (
        <g key={angle} transform={`rotate(${angle} 100 100)`}>
          <line x1="100" y1="2" x2="100" y2="24" strokeWidth="1" />
          <circle cx="100" cy="13" r="2.5" fill="currentColor" stroke="none" transform="rotate(15 100 100)" />
          <line x1="100" y1="24" x2="100" y2="58" strokeWidth="0.5" />
        </g>
      ))}
      <path d="M100 66l8 26 26 8-26 8-8 26-8-26-26-8 26-8z" strokeWidth="1" />
    </svg>
  );
}

const ICONS: Record<string, React.ReactNode> = {
  "/kundli-milan": <><circle cx="9" cy="12" r="5.5" /><circle cx="15" cy="12" r="5.5" /></>,
  "/rashi-nakshatra": <path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.3l6.1-.7z" />,
  "/rashifal": <path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z" />,
  "/panchang": <><rect x="3.5" y="5" width="17" height="15.5" rx="2.5" /><path d="M3.5 10h17M8 3v4M16 3v4" /></>,
  "/choghadiya": <><circle cx="12" cy="12" r="8.5" /><path d="M12 7v5l3.5 2" /></>,
  "/naam": <><path d="M4 5h9l7 7-8 8-8-8z" /><circle cx="8.5" cy="9.5" r="1.2" /></>,
  "/dosh": <><path d="M12 3l7 3v6c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6z" /><path d="M9 12l2 2 4-4" /></>,
  "/grah": <><circle cx="12" cy="12" r="5" /><ellipse cx="12" cy="12" rx="10" ry="3.2" transform="rotate(-20 12 12)" /></>,
  "/muhurat": <path d="M12 3l2 6.5 6.5 2-6.5 2-2 6.5-2-6.5-6.5-2 6.5-2z" />,
};

/** The line icon of a tool, by its address ("/panchang"). */
export function ToolIcon({ page }: { page: string }) {
  return (
    <span className="badge">
      <svg aria-hidden viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        {ICONS[page]}
      </svg>
    </span>
  );
}

/** "Home › Names by Nakshatra › Revati", also given to search engines. */
export function Breadcrumbs({ lang, trail }: { lang: Lang; trail: { label: string; page?: string }[] }) {
  const all = [{ label: guides(lang).crumbs.home, page: "/" }, ...trail];
  return (
    <nav aria-label="Breadcrumb" className="pt-4 text-sm text-ink-600">
      <ol className="flex flex-wrap items-center gap-x-2">
        {all.map((crumb, index) => (
          <li key={crumb.label} className="flex items-center gap-x-2">
            {index > 0 && <span aria-hidden className="text-kesar-500">›</span>}
            {crumb.page && index < all.length - 1 ? (
              <Link href={path(lang, crumb.page)} className="underline decoration-kesar-500/50 underline-offset-4 hover:text-kesar-700">
                {crumb.label}
              </Link>
            ) : (
              <span aria-current="page">{crumb.label}</span>
            )}
          </li>
        ))}
      </ol>
      <Schema
        data={{
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: all.map((crumb, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: crumb.label,
            ...(crumb.page ? { item: SITE_URL + path(lang, crumb.page) } : {}),
          })),
        }}
      />
    </nav>
  );
}

/** Page heading: the main keyword as H1, the other language's keyword just below, then the short answer. */
export function Intro({ h1, h2, answer }: { h1: string; h2?: string; answer: string }) {
  return (
    <section className="pt-5 pb-7">
      <h1 className="font-serif text-[30px] leading-tight text-maroon-800 md:text-[42px]">{h1}</h1>
      {h2 && <h2 className="mt-1 text-kesar-700">{h2}</h2>}
      <div aria-hidden className="mt-3 h-[3px] w-20 rounded-full bg-linear-to-r from-kesar-500 to-haldi-400" />
      <p className="mt-4 max-w-3xl text-[17px]">{answer}</p>
    </section>
  );
}

export function Heading({ children }: { children: React.ReactNode }) {
  return <h2 className="section-title">{children}</h2>;
}

/** Questions and answers, also given to search engines as FAQ data. */
export function FaqList({ title, items }: { title: string; items: { q: string; a: string }[] }) {
  return (
    <section className="pb-10">
      <Heading>{title}</Heading>
      {items.map((item) => (
        <details key={item.q} className="faq">
          <summary>{item.q}</summary>
          <p className="mt-2 text-ink-600">{item.a}</p>
        </details>
      ))}
      <Schema
        data={{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: items.map((item) => ({
            "@type": "Question",
            name: item.q,
            acceptedAnswer: { "@type": "Answer", text: item.a },
          })),
        }}
      />
    </section>
  );
}

/** The link from every free page to the form: the step that leads to the paid Patrika. */
export function Cta({ lang, title, text }: { lang: Lang; title?: string; text?: string }) {
  const c = guides(lang).cta;
  return (
    <section className="pb-12">
      <div className="night rounded-3xl p-6 shadow-xl md:flex md:items-center md:justify-between md:gap-6 md:p-8">
        <Wheel className="absolute -top-16 -right-16 size-56 text-haldi-300/25" />
        <div className="relative">
          <h2 className="font-serif text-2xl">{title ?? c.title}</h2>
          <p className="mt-1 text-white/85">{text ?? c.text}</p>
        </div>
        <Link
          href={path(lang) + "#kundli"}
          className="relative mt-5 flex h-12 shrink-0 items-center justify-center rounded-xl bg-linear-to-b from-haldi-300 to-haldi-400 px-7 font-semibold text-maroon-900 shadow-lg transition hover:brightness-105 active:scale-[0.98] md:mt-0"
        >
          {c.button}
        </Link>
      </div>
    </section>
  );
}

/** A grid of link cards. */
export function LinkGrid({ items }: { items: { href: string; title: string; text?: string }[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
      {items.map((item) => (
        <Link key={item.href} href={item.href} className="card">
          <h3 className="font-semibold text-maroon-800">{item.title}</h3>
          {item.text && <p className="mt-1 text-sm text-ink-600">{item.text}</p>}
        </Link>
      ))}
    </div>
  );
}
