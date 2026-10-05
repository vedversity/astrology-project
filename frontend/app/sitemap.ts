import type { MetadataRoute } from "next";

import { DOSHA_SLUGS } from "@/lib/guides";
import { api, path, SITE_URL } from "@/lib/site";

const RASHIS = ["mesh", "vrishabh", "mithun", "kark", "singh", "kanya", "tula", "vrishchik", "dhanu", "makar", "kumbh", "meen"];
const PAGES = [
  "/", "/janam-patrika", "/kundli-milan", "/rashifal", "/choghadiya", "/rashi-nakshatra", "/panchang", "/muhurat", "/naam", "/grah", "/dosh", "/about",
  "/privacy", "/terms", "/refund", "/disclaimer",
];

// Each public page, with its Hindi and English addresses paired for search engines
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [nakshatras, planets, cities, muhurat] = await Promise.all([
    api<{ slug: string }[]>("/guide/nakshatras", 86400),
    api<{ slug: string }[]>("/guide/planets", 86400),
    api<{ slug: string }[]>("/cities", 86400),
    api<{ years: number[]; types: { type: string }[] }>("/muhurat", 86400),
  ]);
  const pages = [
    ...PAGES,
    ...(nakshatras ?? []).map((item) => `/naam/${item.slug}`),
    ...(planets ?? []).map((item) => `/grah/${item.slug}`),
    ...DOSHA_SLUGS.map((slug) => `/dosh/${slug}`),
    ...RASHIS.map((slug) => `/rashifal/${slug}`),
    ...(cities ?? []).map((item) => `/panchang/${item.slug}`),
    ...(muhurat?.types ?? []).flatMap((item) => muhurat!.years.map((year) => `/muhurat/${item.type}/${year}`)),
  ];
  return pages.flatMap((page) =>
    (["hi", "en"] as const).map((lang) => ({
      url: SITE_URL + path(lang, page),
      alternates: {
        languages: { "hi-IN": SITE_URL + path("hi", page), "en-IN": SITE_URL + path("en", page) },
      },
    })),
  );
}
