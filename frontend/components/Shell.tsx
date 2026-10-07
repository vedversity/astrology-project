import Link from "next/link";

import { content } from "@/lib/content";
import { Schema, Wheel } from "@/components/ui";
import { guides } from "@/lib/guides";
import { getSite, path, SITE_URL, type Lang } from "@/lib/site";

/** The site's mark: a small rising sun in a saffron circle. */
function Mark() {
  return (
    <span className="flex size-9 items-center justify-center rounded-full bg-linear-to-br from-kesar-500 to-maroon-700 text-haldi-300 shadow">
      <svg aria-hidden viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
        <circle cx="12" cy="12" r="3.5" fill="currentColor" stroke="none" />
        <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />
      </svg>
    </span>
  );
}

/** Header and footer wrapped around every page. */
export default async function Shell({ lang, children }: { lang: Lang; children: React.ReactNode }) {
  const c = content(lang);
  const site = await getSite();
  const brand = site?.brand.name[lang] ?? (lang === "hi" ? "जन्म पत्रिका" : "Janam Patrika");
  const other: Lang = lang === "hi" ? "en" : "hi";
  const links = [
    { href: path(lang, "/janam-patrika"), label: c.nav.patrika },
    { href: path(lang, "/kundli-milan"), label: guides(lang).milan.crumb },
    { href: path(lang, "/rashifal"), label: guides(lang).rashifal.crumb },
    { href: path(lang, "/panchang"), label: c.nav.panchang },
    { href: path(lang, "/about"), label: c.nav.about },
  ];
  const tools = guides(lang)
    .tools.items.filter((item) => !["/panchang", "/kundli-milan", "/rashifal"].includes(item.href))
    .map((item) => ({ href: path(lang, item.href), label: item.title }));
  const policies = [
    { href: path(lang, "/privacy"), label: c.footer.privacy },
    { href: path(lang, "/terms"), label: c.footer.terms },
    { href: path(lang, "/refund"), label: c.footer.refund },
    { href: path(lang, "/disclaimer"), label: c.footer.disclaimer },
  ];

  return (
    <>
      <header className="sticky top-0 z-20 border-b border-kesar-100 bg-white/90 shadow-sm backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
          <Link href={path(lang)} className="flex items-center gap-2 font-serif text-xl text-maroon-700">
            <Mark />
            {brand}
          </Link>
          <nav className="flex items-center gap-4 text-ink-600 md:gap-5">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="hidden transition-colors hover:text-kesar-600 md:block">
                {link.label}
              </Link>
            ))}
            {/* A plain link: the two languages are separate sites with their own <html lang> */}
            <a
              href={path(other)}
              lang={other}
              className="rounded-full border border-kesar-600 px-3 py-1 text-sm font-semibold text-kesar-700 transition-colors hover:bg-kesar-50"
            >
              {c.nav.otherLang}
            </a>
          </nav>
        </div>
        {/* On a phone the links sit in their own row, always visible: no hidden menu to find */}
        <nav className="flex gap-5 overflow-x-auto border-t border-kesar-100 px-4 text-sm text-ink-600 md:hidden">
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

      <footer className="night">
        <Wheel className="absolute -bottom-28 -left-24 size-80 text-haldi-300/15" />
        <div className="relative mx-auto max-w-5xl px-4 py-10 text-sm text-white/80">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-[1.3fr_1fr_1fr_1fr]">
            <div className="col-span-2 md:col-span-1">
              <Link href={path(lang)} className="flex items-center gap-2 font-serif text-2xl text-white">
                <Mark />
                {brand}
              </Link>
              {site?.brand.tagline[lang] && <p className="mt-3 max-w-xs text-haldi-300">{site.brand.tagline[lang]}</p>}
              {site?.contact?.whatsapp && (
                <p className="mt-3">
                  <a href={`https://wa.me/${site.contact.whatsapp}`} target="_blank" rel="noopener noreferrer" className="underline">
                    {c.about.whatsapp}
                  </a>
                </p>
              )}
              {site?.contact?.email && (
                <p className="mt-3">
                  {c.footer.contact}:{" "}
                  <a href={`mailto:${site.contact.email}`} className="underline">
                    {site.contact.email}
                  </a>
                </p>
              )}
            </div>
            {[links, tools, policies].map((group) => (
              <nav key={group[0].href} className="flex flex-col">
                {group.map((link) => (
                  <Link key={link.href} href={link.href} className="flex min-h-9 items-center transition-colors hover:text-haldi-300">
                    {link.label}
                  </Link>
                ))}
              </nav>
            ))}
          </div>
          <p className="mt-8 border-t border-white/15 pt-5">{c.disclaimer}</p>
          <p className="mt-2 text-xs text-white/60">
            © {new Date().getFullYear()} {brand} · {c.footer.dataCredit}
          </p>
        </div>
      </footer>
    </>
  );
}
