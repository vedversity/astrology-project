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
    <div className="grid gap-3 md:grid-cols-3">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className={`flex flex-col rounded-2xl bg-white p-5 ${
            plan.recommended ? "border-2 border-kesar-500" : "border border-kesar-100"
          }`}
        >
          {plan.recommended && (
            <span className="mb-2 self-start rounded-full bg-kesar-600 px-3 py-0.5 text-xs font-semibold text-white">
              {c.recommended}
            </span>
          )}
          <h3 className="font-serif text-xl text-maroon-800">{plan.name[lang]}</h3>
          <p className="text-sm text-ink-600">
            {fill(c.pages, { n: plan.pages })} · {plan.summary[lang]}
          </p>
          <p className="mt-2 text-3xl font-bold">₹{plan.price}</p>
          <ul className="mt-3 flex-1 space-y-1 text-ink-600">
            {plan.features[lang].map((feature) => (
              <li key={feature} className="flex gap-2">
                <span aria-hidden className="text-kesar-600">
                  ✓
                </span>
                {feature}
              </li>
            ))}
          </ul>
          {action && (
            <Link href={action.href(plan)} className={`mt-4 ${plan.recommended ? "btn-primary" : "btn-secondary"}`}>
              {action.label}
            </Link>
          )}
        </div>
      ))}
    </div>
  );
}
