// Talks to the backend API. The address comes from .env.local (see .env.example).

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
// The public address of this website, used for search-engine tags
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
// Phase 5 switches this on. Until then the order page makes the PDF without payment.
export const PAYMENTS_ENABLED = process.env.NEXT_PUBLIC_PAYMENTS_ENABLED === "true";

export type Lang = "hi" | "en";
export type Text = { hi: string; en: string };

export type Plan = {
  id: "mini" | "full" | "premium";
  price: number;
  pages: number;
  recommended?: boolean;
  /** "child" = offered only for a child under 16 (the newborn extras make no sense for an adult) */
  audience?: "child";
  name: Text;
  summary: Text;
  features: { hi: string[]; en: string[] };
};

export type Site = {
  brand: { name: Text; tagline: Text };
  contact: { email: string | null; whatsapp: string | null };
  plans: Plan[];
};

// The city whose Panchang is shown until the visitor chooses their own
export const DEFAULT_CITY = { label: "Delhi, India", latitude: 28.6139, longitude: 77.209, timezone: "Asia/Kolkata" };

/**
 * Brand name, plans and prices, read from the backend (backend/app/config/site.json).
 * Refreshed every five minutes, so a price change shows up without rebuilding the site.
 * Returns null if the backend cannot be reached; pages then hide the price section.
 */
export async function getSite(): Promise<Site | null> {
  try {
    const response = await fetch(`${API_URL}/site`, { next: { revalidate: 300 } });
    if (!response.ok) return null;
    return (await response.json()) as Site;
  } catch {
    return null;
  }
}

/**
 * Read reference data from the backend, kept for the given number of seconds.
 * Returns null if the backend cannot be reached or does not know the item.
 */
export async function api<T>(route: string, keepSeconds: number): Promise<T | null> {
  try {
    const response = await fetch(API_URL + route, { next: { revalidate: keepSeconds } });
    return response.ok ? ((await response.json()) as T) : null;
  } catch {
    return null;
  }
}

/** The plans that suit a person born on the given date (YYYY-MM-DD). */
export function plansFor(plans: Plan[], birthDate: string): Plan[] {
  const born = new Date(birthDate);
  const now = new Date();
  const hadBirthday = now.getMonth() > born.getMonth() || (now.getMonth() === born.getMonth() && now.getDate() >= born.getDate());
  const age = now.getFullYear() - born.getFullYear() - (hadBirthday ? 0 : 1);
  return plans.filter((plan) => plan.audience !== "child" || age < 16);
}

/** Address of a page in the chosen language: Hindi at the root, English under /en. */
export function path(lang: Lang, page: string = "/"): string {
  if (lang === "hi") return page;
  return page === "/" ? "/en" : `/en${page}`;
}
