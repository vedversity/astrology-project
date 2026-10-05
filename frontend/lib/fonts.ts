import { Mukta, Tiro_Devanagari_Hindi } from "next/font/google";

// Both fonts are downloaded when the site is built and served from our own
// address, so visitors make no request to Google.

// Body text and buttons: clean Devanagari and Latin in one family
export const mukta = Mukta({
  weight: ["400", "600", "700"],
  subsets: ["devanagari", "latin"],
  variable: "--font-mukta",
  display: "swap",
});

// Headings: a traditional "patrika" feel
export const tiro = Tiro_Devanagari_Hindi({
  weight: "400",
  subsets: ["devanagari", "latin"],
  variable: "--font-tiro",
  display: "swap",
});
