import Link from "next/link";

import { content } from "@/lib/content";
import { Schema } from "@/components/ui";
import { guides } from "@/lib/guides";
import { getSite, path, SITE_URL, type Lang } from "@/lib/site";

/** Header and footer wrapped around every page. */
export default async function Shell({ lang, children }: { lang: Lang; children: React.ReactNode }) {
  const c = content(lang);
  const site = await getSite();
  const brand = site?.brand.name[lang] ?? (lang === "hi" ? "जन्म पत्रिका" : "Janam Patrika");
  const other: Lang = lang === "hi" ? "en" : "hi";
  const links = [
    { href: path(lang, "/janam-patrika"), label: c.nav.patrika },
    { href: path(lang, "/panchang"), label: c.nav.panchang },
    { href: path(lang, "/about"), label: c.nav.about },
  ];
  const tools = guides(lang)
    .tools.items.filter((item) => !["/panchang", "/janam-patrika"].includes(item.href))
    .map((item) => ({ href: path(lang, item.href), label: item.title }));
  const policies = [
    { href: path(lang, "/privacy"), label: c.footer.privacy },
    { href: path(lang, "/terms"), label: c.footer.terms },
    { href: path(lang, "/refund"), label: c.footer.refund },
    { href: path(lang, "/disclaimer"), label: c.footer.disclaimer },
  ];

  return (
    <>
      <header className="sticky top-0 z-20 border-b border-kesar-100 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
          <Link href={path(lang)} className="font-serif text-xl text-maroon-700">
            {brand}
          </Link>
          <nav className="flex items-center gap-4 text-ink-600 md:gap-6">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="hidden hover:text-kesar-600 sm:block">
                {link.label}
              </Link>
            ))}
            {/* A plain link: the two languages are separate sites with their own <html lang> */}
            <a
              href={path(other)}
              lang={other}
              className="rounded-full border border-kesar-600 px-3 py-1 text-sm text-kesar-700"
            >
              {c.nav.otherLang}
            </a>
          </nav>
        </div>
        {/* On a phone the links sit in their own row, always visible: no hidden menu to find */}
        <nav className="flex gap-5 overflow-x-auto border-t border-kesar-100 px-4 text-sm text-ink-600 sm:hidden">
          {links.map((link) => (
            <Link key={link.href} href={link.href} className="flex h-10 shrink-0 items-center">
              {link.label}
            </Link>
          ))}
        </nav>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-4">{children}</main>
      <Schema
        data={{
          "@context": "https://schema.org",
          "@graph": [
            { "@type": "Organization", "@id": SITE_URL + "/#org", name: brand, url: SITE_URL },
            { "@type": "WebSite", url: SITE_URL + path(lang), name: brand, inLanguage: lang === "hi" ? "hi-IN" : "en-IN", publisher: { "@id": SITE_URL + "/#org" } },
          ],
        }}
      />

      <footer className="border-t border-kesar-100 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-6 text-sm text-ink-600">
          <nav className="flex flex-wrap gap-x-5 gap-y-1">
            {[...links, ...tools, ...policies].map((link) => (
              <Link key={link.href} href={link.href} className="flex min-h-8 items-center hover:text-kesar-600">
                {link.label}
              </Link>
            ))}
          </nav>
          {site?.contact?.email && (
            <p className="mt-3">
              {c.footer.contact}:{" "}
              <a href={`mailto:${site.contact.email}`} className="underline">
                {site.contact.email}
              </a>
            </p>
          )}
          <p className="mt-3">{c.disclaimer}</p>
          <p className="mt-2 text-xs">
            © {new Date().getFullYear()} {brand} · {c.footer.dataCredit}
          </p>
        </div>
      </footer>
    </>
  );
}
