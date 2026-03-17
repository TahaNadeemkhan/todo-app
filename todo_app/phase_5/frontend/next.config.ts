import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
  // Proxy API requests to backend
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    console.log(`[Next Config] Rewriting /api to ${backendUrl}`);
    return [
      {
        source: "/api/chatkit",
        destination: `${backendUrl}/chatkit`,
      },
      {
        source: "/api/voice/transcribe",
        destination: `${backendUrl}/voice/transcribe`,
      },
      // Proxy everything EXCEPT /api/auth
      {
        source: "/api/:path*((?!auth).*)",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
