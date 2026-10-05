"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { apiBody, keepPdf, useBirth, type Birth } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { API_URL, path, PAYMENTS_ENABLED, type Lang, type Plan } from "@/lib/site";

/** Collects the names to print and the contact details, then gets the PDF. */
export default function Order({ lang }: { lang: Lang }) {
  const birth = useBirth();
  if (birth === undefined) return null;
  if (birth === null) {
    return (
      <section className="py-10 text-center">
        <p className="text-ink-600">{content(lang).preview.noData}</p>
        <Link href={path(lang) + "#kundli"} className="btn-primary mx-auto mt-4 max-w-sm">
          {content(lang).preview.goHome}
        </Link>
      </section>
    );
  }
  return <Fields lang={lang} birth={birth} />;
}

function Fields({ lang, birth }: { lang: Lang; birth: Birth }) {
  const c = content(lang).order;
  const router = useRouter();
  const planId = useSearchParams().get("plan") ?? "full";

  const [plan, setPlan] = useState<Plan | null>(null);
  const [reportLang, setReportLang] = useState<Lang>(lang);
  const [names, setNames] = useState({
    child_name: birth.name,
    surname: "",
    father_name: "",
    mother_name: "",
    gotra: "",
    kuldevi: "",
  });
  const [whatsapp, setWhatsapp] = useState("");
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/site`)
      .then((response) => response.json())
      .then((site) => setPlan(site.plans.find((p: Plan) => p.id === planId) ?? site.plans[0]))
      .catch(() => setPlan(null));
  }, [planId]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!/^[6-9]\d{9}$/.test(whatsapp.replace(/[\s-]/g, "").replace(/^(\+?91|0)/, ""))) return setError(c.errors.whatsapp);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return setError(c.errors.email);
    if (!consent) return setError(c.errors.consent);
    setError("");
    setWorking(true);
    try {
      // Phase 5 puts the payment here. Until then this makes the PDF directly.
      const response = await fetch(`${API_URL}/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...apiBody(birth),
          gender: birth.gender,
          place: birth.place.label,
          variant: plan?.id ?? planId,
          lang: reportLang,
          ...Object.fromEntries(Object.entries(names).map(([key, value]) => [key, value.trim() || null])),
        }),
      });
      if (!response.ok) throw new Error(String(response.status));
      keepPdf(await response.blob(), "janam-patrika.pdf");
      router.push(path(lang, "/thank-you"));
    } catch {
      setError(c.failed);
      setWorking(false);
    }
  }

  const nameFields: { key: keyof typeof names; label: string }[] = [
    { key: "child_name", label: c.childName },
    { key: "surname", label: c.surname },
    { key: "father_name", label: c.father },
    { key: "mother_name", label: c.mother },
    { key: "gotra", label: c.gotra },
    { key: "kuldevi", label: c.kuldevi },
  ];

  return (
    <form onSubmit={submit} noValidate className="mx-auto max-w-xl py-6">
      <h1 className="font-serif text-[28px] leading-tight text-maroon-800">{c.title}</h1>

      {plan && (
        <div className="card mt-4 flex items-center justify-between">
          <div>
            <p className="text-sm text-ink-600">{c.plan}</p>
            <p className="font-semibold">
              {plan.name[lang]} · ₹{plan.price}
            </p>
          </div>
          <Link href={path(lang, "/preview")} className="text-sm text-kesar-700 underline">
            {c.changePlan}
          </Link>
        </div>
      )}

      <fieldset className="card mt-3">
        <legend className="sr-only">{c.language}</legend>
        <p className="label">{c.language}</p>
        <div className="mt-1 grid grid-cols-2 gap-2">
          {(["hi", "en"] as Lang[]).map((option) => (
            <label
              key={option}
              className={`flex h-12 cursor-pointer items-center justify-center rounded-xl border ${
                reportLang === option ? "border-kesar-600 bg-kesar-50 font-semibold" : "border-gray-300"
              }`}
            >
              <input
                type="radio"
                name="report-lang"
                className="sr-only"
                checked={reportLang === option}
                onChange={() => setReportLang(option)}
              />
              {option === "hi" ? c.langHi : c.langEn}
            </label>
          ))}
        </div>
      </fieldset>

      <div className="card mt-3">
        <h2 className="font-semibold">{c.coverTitle}</h2>
        <p className="text-sm text-ink-600">{c.coverHint}</p>
        {nameFields.map((field) => (
          <div key={field.key} className="mt-3">
            <label className="label" htmlFor={field.key}>
              {field.label}
            </label>
            <input
              id={field.key}
              className="field"
              maxLength={60}
              autoComplete="off"
              value={names[field.key]}
              onChange={(event) => setNames({ ...names, [field.key]: event.target.value })}
            />
          </div>
        ))}
      </div>

      <div className="card mt-3">
        <h2 className="font-semibold">{c.contactTitle}</h2>
        <label className="label mt-3" htmlFor="whatsapp">
          {c.whatsapp}
        </label>
        <input
          id="whatsapp"
          type="tel"
          inputMode="numeric"
          autoComplete="tel"
          className="field"
          value={whatsapp}
          onChange={(event) => setWhatsapp(event.target.value)}
        />
        <label className="label mt-3" htmlFor="email">
          {c.email}
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          className="field"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label className="mt-4 flex gap-3 text-sm">
          <input
            type="checkbox"
            className="mt-1 size-5 shrink-0 accent-kesar-600"
            checked={consent}
            onChange={(event) => setConsent(event.target.checked)}
          />
          {c.consent}
        </label>
      </div>

      {!PAYMENTS_ENABLED && <p className="mt-3 rounded-lg bg-haldi-300/40 p-3 text-sm">{c.testMode}</p>}
      {error && (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      )}
      <button type="submit" disabled={working} className="btn-primary mt-4">
        {working ? c.working : PAYMENTS_ENABLED && plan ? fill(c.pay, { price: plan.price }) : c.testButton}
      </button>
    </form>
  );
}
