import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable webpack polling for WSL/Windows file system
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300,
      };
    }
    return config;
  },
};

export default nextConfig;
