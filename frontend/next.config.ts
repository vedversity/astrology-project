import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // One "page not found" screen for both the Hindi and the English site
  // cpus: 2 keeps the build within the memory of a small (8 GB) computer
  experimental: { globalNotFound: true, cpus: 2 },
};

export default nextConfig;
