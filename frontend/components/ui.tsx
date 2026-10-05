// Small pieces shared by the reference pages.

import Link from "next/link";

import { guides } from "@/lib/guides";
import { path, SITE_URL, type Lang } from "@/lib/site";

/** Data for search engines, written into the page as JSON-LD. */
export function Schema({ data }: { data: object }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}

/** "Home › Names by Nakshatra › Revati", also given to search engines. */
export function Breadcrumbs({ lang, trail }: { lang: Lang; trail: { label: string; page?: string }[] }) {
  const all = [{ label: guides(lang).crumbs.home, page: "/" }, ...trail];
  return (
    <nav aria-label="Breadcrumb" className="pt-4 text-sm text-ink-600">
      <ol className="flex flex-wrap items-center gap-x-2">
        {all.map((crumb, index) => (
          <li key={crumb.label} className="flex items-center gap-x-2">
            {index > 0 && <span aria-hidden>›</span>}
            {crumb.page && index < all.length - 1 ? (
              <Link href={path(lang, crumb.page)} className="underline">
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
    <section className="pt-4 pb-6">
      <h1 className="font-serif text-[28px] leading-tight text-maroon-800 md:text-4xl">{h1}</h1>
      {h2 && <h2 className="mt-1 text-ink-600">{h2}</h2>}
      <p className="mt-3 max-w-3xl">{answer}</p>
    </section>
  );
}

export function Heading({ children }: { children: React.ReactNode }) {
  return <h2 className="mb-3 font-serif text-2xl text-maroon-800">{children}</h2>;
}

/** Questions and answers, also given to search engines as FAQ data. */
export function FaqList({ title, items }: { title: string; items: { q: string; a: string }[] }) {
  return (
    <section className="pb-8">
      <Heading>{title}</Heading>
      {items.map((item) => (
        <details key={item.q} className="mb-2 rounded-xl border border-kesar-100 bg-white p-4">
          <summary className="cursor-pointer font-semibold">{item.q}</summary>
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
    <section className="pb-10">
      <div className="rounded-2xl bg-maroon-700 p-5 text-white md:flex md:items-center md:justify-between md:gap-6">
        <div>
          <h2 className="font-serif text-xl">{title ?? c.title}</h2>
          <p className="mt-1 opacity-90">{text ?? c.text}</p>
        </div>
        <Link
          href={path(lang) + "#kundli"}
          className="mt-4 flex h-12 shrink-0 items-center justify-center rounded-xl bg-white px-6 font-semibold text-maroon-800 md:mt-0"
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
        <Link key={item.href} href={item.href} className="card hover:border-kesar-500">
          <h3 className="font-semibold">{item.title}</h3>
          {item.text && <p className="mt-1 text-sm text-ink-600">{item.text}</p>}
        </Link>
      ))}
    </div>
  );
}
