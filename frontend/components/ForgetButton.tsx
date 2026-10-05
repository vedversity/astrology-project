"use client";

import { useState } from "react";

import { forgetEverything } from "@/lib/birth";
import { content } from "@/lib/content";
import type { Lang } from "@/lib/site";

/** "Delete my data" for what this site keeps in the visitor's own browser. */
export default function ForgetButton({ lang }: { lang: Lang }) {
  const c = content(lang).forget;
  const [done, setDone] = useState(false);

  return (
    <section className="card mt-6">
      <h2 className="font-semibold">{c.title}</h2>
      <p className="mt-1 text-sm text-ink-600">{c.text}</p>
      {done ? (
        <p role="status" className="mt-3 font-semibold text-green-800">
          {c.done}
        </p>
      ) : (
        <button
          type="button"
          className="btn-secondary mt-3 md:max-w-xs"
          onClick={() => {
            forgetEverything();
            setDone(true);
          }}
        >
          {c.button}
        </button>
      )}
    </section>
  );
}
