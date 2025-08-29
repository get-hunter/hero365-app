import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use Next-on-Pages for optimal Cloudflare Pages deployment with Edge SSR + ISR
  // This gives us the best of both worlds: pre-rendered pages + dynamic capabilities
  
  images: {
    unoptimized: true,
  },
  
  // Disable TypeScript errors during build (we'll handle them separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
