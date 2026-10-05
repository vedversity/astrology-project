"use client";

import { useState } from "react";

import { API_URL, type Site } from "@/lib/site";

// The owner's settings page. It is in English only and is not linked from the
// site; the address is /admin. The password is the ADMIN_TOKEN line in
// backend/.env, and is kept only until the browser tab is closed.

type Astrologer = { name: { hi: string; en: string }; experience_years: number; bio: { hi: string; en: string } };
type AdminSite = Site & { astrologer: Astrologer | null };
type Form = {
  brandHi: string; brandEn: string; taglineHi: string; taglineEn: string;
  email: string; whatsapp: string;
  astroNameHi: string; astroNameEn: string; astroYears: string; astroBioHi: string; astroBioEn: string;
  prices: Record<string, string>;
};

function toForm(site: AdminSite): Form {
  return {
    brandHi: site.brand.name.hi, brandEn: site.brand.name.en,
    taglineHi: site.brand.tagline.hi, taglineEn: site.brand.tagline.en,
    email: site.contact.email ?? "", whatsapp: site.contact.whatsapp ?? "",
    astroNameHi: site.astrologer?.name.hi ?? "", astroNameEn: site.astrologer?.name.en ?? "",
    astroYears: site.astrologer ? String(site.astrologer.experience_years) : "",
    astroBioHi: site.astrologer?.bio.hi ?? "", astroBioEn: site.astrologer?.bio.en ?? "",
    prices: Object.fromEntries(site.plans.map((plan) => [plan.id, String(plan.price)])),
  };
}

export default function Admin() {
  const [token, setToken] = useState("");
  const [site, setSite] = useState<AdminSite | null>(null);
  const [form, setForm] = useState<Form | null>(null);
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  async function call(method: "GET" | "PUT", body?: unknown) {
    const response = await fetch(`${API_URL}/admin/site`, {
      method,
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : "Please check the values and try again.";
      throw new Error(detail);
    }
    return data as AdminSite;
  }

  async function signIn(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage(null);
    try {
      const loaded = await call("GET");
      setSite(loaded);
      setForm(toForm(loaded));
    } catch (error) {
      setMessage({ ok: false, text: (error as Error).message });
    } finally {
      setBusy(false);
    }
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    if (!form) return;
    setBusy(true);
    setMessage(null);
    const hasAstrologer = form.astroNameHi || form.astroNameEn || form.astroBioHi || form.astroBioEn || form.astroYears;
    try {
      const saved = await call("PUT", {
        brand: { name: { hi: form.brandHi, en: form.brandEn }, tagline: { hi: form.taglineHi, en: form.taglineEn } },
        contact: { email: form.email.trim() || null, whatsapp: form.whatsapp.trim() || null },
        astrologer: hasAstrologer
          ? {
              name: { hi: form.astroNameHi, en: form.astroNameEn },
              experience_years: Number(form.astroYears),
              bio: { hi: form.astroBioHi, en: form.astroBioEn },
            }
          : null,
        prices: Object.fromEntries(Object.entries(form.prices).map(([id, value]) => [id, Number(value)])),
      });
      setSite(saved);
      setForm(toForm(saved));
      setMessage({ ok: true, text: "Saved. The website shows the change within five minutes." });
    } catch (error) {
      setMessage({ ok: false, text: (error as Error).message });
    } finally {
      setBusy(false);
    }
  }

  const field = (label: string, key: keyof Omit<Form, "prices">, hint?: string, type = "text") => (
    <div className="mt-3">
      <label className="label" htmlFor={key}>
        {label}
      </label>
      <input
        id={key}
        type={type}
        className="field"
        value={form?.[key] ?? ""}
        onChange={(event) => form && setForm({ ...form, [key]: event.target.value })}
      />
      {hint && <p className="mt-1 text-xs text-ink-600">{hint}</p>}
    </div>
  );

  if (!site || !form) {
    return (
      <form onSubmit={signIn} className="card mx-auto mt-10 max-w-sm">
        <h1 className="font-serif text-2xl text-maroon-800">Site settings</h1>
        <label className="label mt-4" htmlFor="token">
          Admin password
        </label>
        <input id="token" type="password" className="field" value={token} autoComplete="current-password" onChange={(event) => setToken(event.target.value)} />
        <p className="mt-1 text-xs text-ink-600">The ADMIN_TOKEN line in backend/.env.</p>
        {message && (
          <p role="alert" className="mt-3 text-sm font-semibold text-red-700">
            {message.text}
          </p>
        )}
        <button type="submit" disabled={busy || !token} className="btn-primary mt-4">
          {busy ? "Checking…" : "Open settings"}
        </button>
      </form>
    );
  }

  return (
    <form onSubmit={save} className="mx-auto max-w-2xl py-6">
      <h1 className="font-serif text-[28px] text-maroon-800">Site settings</h1>

      <section className="card mt-4">
        <h2 className="font-semibold">Prices (rupees)</h2>
        <div className="grid gap-3 md:grid-cols-3">
          {site.plans.map((plan) => (
            <div key={plan.id} className="mt-3">
              <label className="label" htmlFor={`price-${plan.id}`}>
                {plan.name.en}
              </label>
              <input
                id={`price-${plan.id}`}
                type="number"
                min={1}
                className="field"
                value={form.prices[plan.id] ?? ""}
                onChange={(event) => setForm({ ...form, prices: { ...form.prices, [plan.id]: event.target.value } })}
              />
            </div>
          ))}
        </div>
      </section>

      <section className="card mt-3">
        <h2 className="font-semibold">Brand</h2>
        {field("Name (Hindi)", "brandHi")}
        {field("Name (English)", "brandEn")}
        {field("Tagline (Hindi)", "taglineHi")}
        {field("Tagline (English)", "taglineEn")}
      </section>

      <section className="card mt-3">
        <h2 className="font-semibold">Contact</h2>
        {field("Email", "email", "Shown in the footer and on the policy pages. Leave empty to hide.", "email")}
        {field("WhatsApp number", "whatsapp", "Digits only with country code, e.g. 919876543210. Adds a WhatsApp button. Leave empty to hide.")}
      </section>

      <section className="card mt-3">
        <h2 className="font-semibold">Astrologer</h2>
        <p className="text-sm text-ink-600">
          Shown on the About page and the home page. Enter true details only. Leave everything empty to hide the section.
        </p>
        {field("Name (Hindi)", "astroNameHi")}
        {field("Name (English)", "astroNameEn")}
        {field("Years of practice", "astroYears", undefined, "number")}
        {field("About (Hindi)", "astroBioHi", "One or two sentences: tradition, guru, speciality.")}
        {field("About (English)", "astroBioEn")}
      </section>

      {message && (
        <p role={message.ok ? "status" : "alert"} className={`mt-3 text-sm font-semibold ${message.ok ? "text-green-800" : "text-red-700"}`}>
          {message.text}
        </p>
      )}
      <button type="submit" disabled={busy} className="btn-primary mt-4">
        {busy ? "Saving…" : "Save changes"}
      </button>
    </form>
  );
}
