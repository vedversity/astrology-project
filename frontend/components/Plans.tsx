import Link from "next/link";

import { content, fill } from "@/lib/content";
import type { Lang, Plan } from "@/lib/site";

type Props = {
  lang: Lang;
  plans: Plan[] | null;
  /** Where each plan's button leads, and what it says. Left out = no buttons. */
  action?: { href: (plan: Plan) => string; label: string };
};

/** The plan cards with prices. Prices come from the backend config, never from this file. */
export default function Plans({ lang, plans, action }: Props) {
  const c = content(lang).plans;
  if (!plans) return <p className="card text-ink-600">{c.unavailable}</p>;

  return (
    <div className="grid gap-4 md:grid-cols-3 md:items-stretch md:pt-3">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className={`card relative flex flex-col ${
            plan.recommended ? "border-2 border-kesar-500 bg-linear-to-b from-kesar-50 to-white shadow-xl md:-translate-y-3" : ""
          }`}
        >
          {plan.recommended && (
            <span className="mb-2 self-start rounded-full bg-linear-to-r from-kesar-600 to-maroon-700 px-3 py-0.5 text-xs font-semibold text-white shadow">
              ★ {c.recommended}
            </span>
          )}
          <h3 className="font-serif text-2xl text-maroon-800">{plan.name[lang]}</h3>
          <p className="text-sm text-ink-600">
            {fill(c.pages, { n: plan.pages })} · {plan.summary[lang]}
          </p>
          <p className="mt-3 flex items-start font-bold text-maroon-800">
            <span className="mt-1 text-xl">₹</span>
            <span className="text-5xl leading-none">{plan.price}</span>
          </p>
          <ul className="mt-4 flex-1 space-y-2 border-t border-kesar-100 pt-4 text-ink-600">
            {plan.features[lang].map((feature) => (
              <li key={feature} className="flex gap-2">
                <span aria-hidden className="mt-1 flex size-5 shrink-0 items-center justify-center rounded-full bg-kesar-100 text-xs text-kesar-700">
                  ✓
                </span>
                {feature}
              </li>
            ))}
          </ul>
          {action && (
            <Link href={action.href(plan)} className={`mt-5 ${plan.recommended ? "btn-primary" : "btn-secondary"}`}>
              {action.label}
            </Link>
          )}
        </div>
      ))}
    </div>
  );
}
