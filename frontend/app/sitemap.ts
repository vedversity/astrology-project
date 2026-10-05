import type { MetadataRoute } from "next";

import { path, SITE_URL } from "@/lib/site";

const PAGES = ["/", "/janam-patrika", "/panchang", "/about", "/privacy", "/terms", "/refund", "/disclaimer"];

// Each public page, with its Hindi and English addresses paired for search engines
export default function sitemap(): MetadataRoute.Sitemap {
  return PAGES.flatMap((page) =>
    (["hi", "en"] as const).map((lang) => ({
      url: SITE_URL + path(lang, page),
      alternates: {
        languages: { "hi-IN": SITE_URL + path("hi", page), "en-IN": SITE_URL + path("en", page) },
      },
    })),
  );
}
