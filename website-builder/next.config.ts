import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Only use static export for production builds
  ...(process.env.NODE_ENV === 'production' && process.env.NEXT_BUILD_MODE === 'export' ? {
    output: 'export',
    distDir: 'out',
    trailingSlash: true,
  } : {}),
  
  images: {
    unoptimized: true,
  },
  
  // Disable TypeScript errors during build (we'll handle them separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
