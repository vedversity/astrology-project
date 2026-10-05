"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { apiBody, useBirth, type Birth } from "@/lib/birth";
import { content, fill } from "@/lib/content";
import { API_URL, path, plansFor, type Lang, type Plan, type Site } from "@/lib/site";
import { track } from "@/lib/track";

type Checkout = { key: string; order_id: string; amount: number; currency: string };
type RazorpayReply = { razorpay_payment_id: string; razorpay_signature: string };
declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

/** Loads Razorpay's payment window the first time it is needed. */
function loadRazorpay(): Promise<boolean> {
  if (window.Razorpay) return Promise.resolve(true);
  return new Promise((resolve) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

/** Collects the names to print and the contact details, takes payment, and hands over to the order page. */
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
  const [mode, setMode] = useState<Site["payments"]>("test");
  const [brand, setBrand] = useState("");
  const [couponText, setCouponText] = useState("");
  const [coupon, setCoupon] = useState<{ code: string; discount: number; amount: number } | null>(null);
  const [couponError, setCouponError] = useState(false);
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
      .then((site: Site) => {
        setMode(site.payments);
        setBrand(site.brand.name[lang]);
        // A plan that does not suit this birth date falls back to the Full Patrika
        const offered = plansFor(site.plans as Plan[], birth.date);
        setPlan(offered.find((p) => p.id === planId) ?? offered.find((p) => p.id === "full") ?? offered[0]);
      })
      .catch(() => setPlan(null));
  }, [planId, birth.date, lang]);

  const phone = whatsapp.replace(/[\s-]/g, "").replace(/^(\+?91|0)/, "");
  const orderPage = (id: string) => `${path(lang, "/thank-you")}?order=${id}`;

  async function applyCoupon() {
    setCoupon(null);
    setCouponError(false);
    if (!couponText.trim() || !plan) return;
    try {
      const response = await fetch(`${API_URL}/coupons/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: couponText.trim(), plan: plan.id }),
      });
      if (!response.ok) return setCouponError(true);
      setCoupon(await response.json());
    } catch {
      setCouponError(true);
    }
  }

  /** Opens Razorpay's window; after a payment, has our server check it before moving on. */
  async function pay(orderId: string, checkout: Checkout) {
    if (!(await loadRazorpay()) || !window.Razorpay) throw new Error("checkout");
    new window.Razorpay({
      key: checkout.key,
      order_id: checkout.order_id,
      amount: checkout.amount,
      currency: checkout.currency,
      name: brand,
      description: plan?.name[lang],
      prefill: { contact: phone, email: email || undefined },
      theme: { color: "#7a1f2b" },
      handler: async (reply: RazorpayReply) => {
        try {
          const response = await fetch(`${API_URL}/orders/${orderId}/verify`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reply),
          });
          if (!response.ok) throw new Error(String(response.status));
          track("pdf_made", { plan: plan?.id ?? planId, lang: reportLang });
          router.push(orderPage(orderId));
        } catch {
          setError(c.paymentFailed);
          setWorking(false);
        }
      },
      modal: { ondismiss: () => setWorking(false) },
    }).open();
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!/^[6-9]\d{9}$/.test(phone)) return setError(c.errors.whatsapp);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return setError(c.errors.email);
    if (!consent) return setError(c.errors.consent);
    setError("");
    setWorking(true);
    try {
      const response = await fetch(`${API_URL}/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...apiBody(birth),
          gender: birth.gender,
          place: birth.place.label,
          variant: plan?.id ?? planId,
          lang: reportLang,
          ...Object.fromEntries(Object.entries(names).map(([key, value]) => [key, value.trim() || null])),
          whatsapp: phone,
          email: email.trim() || null,
          coupon: coupon?.code ?? null,
          consent: true,
        }),
      });
      if (!response.ok) throw new Error(String(response.status));
      const placed: { order: { id: string }; checkout: Checkout | null } = await response.json();
      if (placed.checkout) {
        await pay(placed.order.id, placed.checkout);
      } else {
        // Nothing to pay: test mode, or a coupon that covers the whole price
        track("pdf_made", { plan: plan?.id ?? planId, lang: reportLang });
        router.push(orderPage(placed.order.id));
      }
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

      <div className="card mt-3">
        <label className="label" htmlFor="coupon">
          {c.coupon}
        </label>
        <div className="flex gap-2">
          <input
            id="coupon"
            className="field uppercase"
            maxLength={20}
            autoComplete="off"
            value={couponText}
            onChange={(event) => {
              setCouponText(event.target.value);
              setCoupon(null);
              setCouponError(false);
            }}
          />
          <button type="button" onClick={applyCoupon} className="mt-1 h-12 shrink-0 rounded-xl border border-kesar-600 px-4 font-semibold text-kesar-700">
            {c.apply}
          </button>
        </div>
        {coupon && <p role="status" className="mt-2 text-sm font-semibold text-green-800">{fill(c.couponOk, { discount: coupon.discount, amount: coupon.amount })}</p>}
        {couponError && <p role="alert" className="mt-2 text-sm font-semibold text-red-700">{c.couponBad}</p>}
      </div>

      {mode === "test" && <p className="mt-3 rounded-lg bg-haldi-300/40 p-3 text-sm">{c.testMode}</p>}
      {mode === "off" && <p role="alert" className="mt-3 rounded-lg bg-haldi-300/40 p-3 text-sm">{c.closed}</p>}
      {error && (
        <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
          {error}
        </p>
      )}
      <button type="submit" disabled={working || mode === "off"} className="btn-primary mt-4">
        {working ? c.working : mode === "razorpay" && plan ? fill(c.pay, { price: coupon?.amount ?? plan.price }) : c.testButton}
      </button>
      {mode === "razorpay" && <p className="mt-2 text-center text-xs text-ink-600">{c.secure}</p>}
    </form>
  );
}
