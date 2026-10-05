import "./globals.css";

import Link from "next/link";

import { content } from "@/lib/content";
import { mukta, tiro } from "@/lib/fonts";

export const metadata = { title: "404", robots: { index: false } };

// Shown for any address that does not exist. It cannot know which language the
// visitor wanted, so it says it in both.
export default function GlobalNotFound() {
  const hi = content("hi").notFound;
  const en = content("en").notFound;
  return (
    <html lang="hi" className={`${mukta.variable} ${tiro.variable} h-full`}>
      <body className="flex min-h-full flex-col items-center justify-center px-4 text-center font-sans text-[17px]">
        <p className="font-serif text-6xl text-kesar-600">404</p>
        <h1 className="mt-2 font-serif text-2xl text-maroon-800">{hi.title}</h1>
        <p className="text-ink-600">{hi.text}</p>
        <Link href="/" className="btn-primary mt-4 max-w-xs">
          {hi.home}
        </Link>
        <div lang="en" className="mt-8">
          <h2 className="font-serif text-xl text-maroon-800">{en.title}</h2>
          <p className="text-ink-600">{en.text}</p>
          <Link href="/en" className="mt-2 inline-block text-kesar-700 underline">
            {en.home}
          </Link>
        </div>
      </body>
    </html>
  );
}
