import type { NextConfig } from "next";
import webpack from "webpack";
import path from "path";
import fs from "fs";

// Load env from /environments if not already present
// This allows the website-builder to consume root-level env files
const loadRootEnv = () => {
  try {
    const fileName = process.env.NODE_ENV === 'production' ? 'production.env' : '.env';
    const envPath = path.resolve(__dirname, `../environments/${fileName}`);
    if (!fs.existsSync(envPath)) return;

    const raw = fs.readFileSync(envPath, 'utf-8');
    raw.split('\n').forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;
      const eq = trimmed.indexOf('=');
      if (eq === -1) return;
      const key = trimmed.slice(0, eq).trim();
      const value = trimmed.slice(eq + 1).trim();
      if (!process.env[key]) {
        process.env[key] = value;
      }
    });
  } catch (err) {
    // Non-fatal: fall back to process env
  }
};

loadRootEnv();

const nextConfig: NextConfig = {
  // Optimized for Cloudflare Workers with OpenNext adapter
  // Supports SSR, ISR, and Server Actions on the Edge
  
  // Output configuration - remove static export for dynamic content
  // output: 'export',
  trailingSlash: true,
  
  // Skip API routes during static export
  skipTrailingSlashRedirect: true,
  
  // Image optimization for performance
  images: {
    // Configure for Cloudflare Images or unoptimized for Workers
    unoptimized: true,
    loader: 'custom',
    loaderFile: './lib/image-loader.ts',
    formats: ['image/webp', 'image/avif'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.supabase.co',
        port: '',
        pathname: '/storage/v1/object/public/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'example.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  
  // Compiler optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Global environment variables (Infrastructure only)
  env: {
    // Backend API Configuration - Global Setting
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_VERSION: process.env.NEXT_PUBLIC_API_VERSION || 'v1',
    
    // Feature Flags (Global)
    NEXT_PUBLIC_DEBUG_MODE: process.env.NEXT_PUBLIC_DEBUG_MODE || 'true',
    NEXT_PUBLIC_ANALYTICS_ENABLED: process.env.NEXT_PUBLIC_ANALYTICS_ENABLED || 'false',
    
    // Google Maps API
    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: process.env.GOOGLE_MAPS_API_KEY,
    
    // Business Configuration: DO NOT SET DEFAULTS HERE
    // These should be passed via environment variables or deployment scripts
    NEXT_PUBLIC_BUSINESS_ID: process.env.NEXT_PUBLIC_BUSINESS_ID,
    NEXT_PUBLIC_BUSINESS_NAME: process.env.NEXT_PUBLIC_BUSINESS_NAME,
    NEXT_PUBLIC_BUSINESS_EMAIL: process.env.NEXT_PUBLIC_BUSINESS_EMAIL,
    NEXT_PUBLIC_BUSINESS_PHONE: process.env.NEXT_PUBLIC_BUSINESS_PHONE,
  },
  
  // Enable experimental features for better performance
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
  
  // Webpack optimizations - minimal configuration for SSR compatibility
  webpack: (config, { dev, isServer }) => {
    // Production optimizations (client only)
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
          },
        },
      };
    }

    // SVG handling
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    
    return config;
  },
  
  // Disable TypeScript errors during build (we'll handle them separately)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
