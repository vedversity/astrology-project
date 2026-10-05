// Visitor counting (Google Analytics 4). It is OFF unless NEXT_PUBLIC_GA_ID is
// set in .env.local, so nothing is sent anywhere until the owner switches it on.
//
// Only page views and these few named steps are recorded. Birth details, names
// and phone numbers are never sent.

export const GA_ID = process.env.NEXT_PUBLIC_GA_ID ?? "";

type Step = "preview_shown" | "plan_chosen" | "pdf_made" | "milan_done" | "share_card";

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}

/** Record one step of the journey, e.g. track("plan_chosen", { plan: "full" }). */
export function track(step: Step, details: Record<string, string | number> = {}) {
  if (typeof window !== "undefined" && GA_ID && window.gtag) {
    window.gtag("event", step, details);
  }
}
