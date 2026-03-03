import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for the multi-stage Docker build (copies only minimal files)
  output: "standalone",

  // Expose backend URL to the browser bundle
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
