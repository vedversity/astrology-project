import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

const PRIVATE = ["/preview", "/order", "/thank-you"];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", ...PRIVATE, ...PRIVATE.map((page) => "/en" + page)] },
    sitemap: SITE_URL + "/sitemap.xml",
  };
}
