import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker containerization
  output: "standalone",
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
  // Proxy ChatKit API requests to backend
  async rewrites() {
    return [
      {
        source: "/api/chatkit",
        destination: process.env.NEXT_PUBLIC_BACKEND_URL
          ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/chatkit`
          : "http://127.0.0.1:8000/chatkit",
      },
    ];
  },
};

export default nextConfig;
