import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // One "page not found" screen for both the Hindi and the English site
  // cpus: 2 keeps the build within the memory of a small (8 GB) computer
  experimental: { globalNotFound: true, cpus: 2 },
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // The site may not be shown inside another site's frame
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          // Other sites learn only our address, never the page a visitor was on
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(self)" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
        ],
      },
    ];
  },
};

export default nextConfig;
