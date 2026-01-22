import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable Turbopack for Next.js 16+
  turbopack: {},
  // Enable webpack polling for WSL/Windows file system (dev only)
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
};

export default nextConfig;
