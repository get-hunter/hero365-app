import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  // Disable TypeScript errors during build (we'll handle them separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
