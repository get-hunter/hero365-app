/** @type {import('next').NextConfig} */
const nextConfig = {
  // Global environment variables
  env: {
    // Backend API Configuration - Global Setting
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_VERSION: process.env.NEXT_PUBLIC_API_VERSION || 'v1',
    
    // Business Configuration
    NEXT_PUBLIC_BUSINESS_ID: process.env.NEXT_PUBLIC_BUSINESS_ID || 'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    NEXT_PUBLIC_BUSINESS_NAME: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Austin Elite HVAC',
    NEXT_PUBLIC_BUSINESS_EMAIL: process.env.NEXT_PUBLIC_BUSINESS_EMAIL || 'info@austinelitehvac.com',
    NEXT_PUBLIC_BUSINESS_PHONE: process.env.NEXT_PUBLIC_BUSINESS_PHONE || '(512) 555-COOL',
    
    // Feature Flags
    NEXT_PUBLIC_DEBUG_MODE: process.env.NEXT_PUBLIC_DEBUG_MODE || 'true',
  },
  
  // Optional: Add webpack config for better performance
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    if (dev) {
      // Development optimizations
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config;
  },

  // Enable experimental features
  experimental: {
    // Improve performance
    optimizeCss: true,
  },

  // Image configuration for external domains
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.supabase.co',
        port: '',
        pathname: '/storage/v1/object/public/**',
      },
    ],
  },
};

module.exports = nextConfig;
