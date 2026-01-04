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
  // Proxy ChatKit API requests to backend
  async rewrites() {
    const backendUrl = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
    return [
      {
        source: "/api/chatkit",
        destination: `${backendUrl}/chatkit`,
      },
      {
        source: "/api/voice/transcribe",
        destination: `${backendUrl}/voice/transcribe`,
      },
    ];
  },
};

export default nextConfig;
