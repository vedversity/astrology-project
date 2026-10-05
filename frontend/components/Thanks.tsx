"use client";

import Link from "next/link";
import { usePdf } from "@/lib/birth";
import { content } from "@/lib/content";
import { path, type Lang } from "@/lib/site";

/** The download page shown once the PDF is ready. */
export default function Thanks({ lang }: { lang: Lang }) {
  const c = content(lang).thanks;
  // The PDF is held in memory, so it is only known once the page runs in the browser
  const pdf = usePdf();

  if (pdf === undefined) return null;
  if (pdf === null) {
    return (
      <section className="py-10 text-center">
        <p className="text-ink-600">{c.lost}</p>
        <Link href={path(lang, "/preview")} className="btn-primary mx-auto mt-4 max-w-sm">
          {c.again}
        </Link>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-xl py-10 text-center">
      <p className="font-serif text-xl text-kesar-600">{c.blessing}</p>
      <h1 className="mt-2 font-serif text-[28px] leading-tight text-maroon-800">{c.title}</h1>
      <p className="mt-3 text-ink-600">{c.text}</p>
      <a href={pdf.url} download={pdf.filename} className="btn-primary mt-6">
        {c.download}
      </a>
      <Link href={path(lang) + "#kundli"} className="mt-4 inline-block text-kesar-700 underline">
        {c.another}
      </Link>
    </section>
  );
}
