/**
 * Runtime Configuration Service
 * 
 * Handles environment detection and API URL resolution for:
 * - localhost:8000 (development)
 * - ngrok tunnel (staging)
 * - production API (future)
 */

interface RuntimeConfig {
  apiUrl: string;
  environment: 'development' | 'staging' | 'production';
  businessId?: string;
}

interface EnvironmentDetection {
  isLocalhost: boolean;
  isNgrokTunnel: boolean;
  isProduction: boolean;
  hostname: string;
}

/**
 * Detect the current environment based on various signals
 */
function detectEnvironment(): EnvironmentDetection {
  // Server-side detection
  if (typeof window === 'undefined') {
    // Check if we have Cloudflare Worker environment variables
    const hasWorkerEnv = process.env.NEXT_PUBLIC_ENVIRONMENT === 'staging' ||
                        process.env.NEXT_PUBLIC_ENVIRONMENT === 'production';
    
    if (hasWorkerEnv) {
      // We're in a Cloudflare Worker
      const envType = process.env.NEXT_PUBLIC_ENVIRONMENT;
      
      return {
        isLocalhost: false,
        isNgrokTunnel: envType === 'staging',
        isProduction: envType === 'production',
        hostname: 'cloudflare-worker'
      };
    }
    
    // Local development server
    return {
      isLocalhost: true,
      isNgrokTunnel: false,
      isProduction: false,
      hostname: 'localhost'
    };
  }
  
  // Client-side detection
  const hostname = window.location.hostname;
  
  return {
    isLocalhost: hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.'),
    isNgrokTunnel: hostname.includes('tradesites.app') && !hostname.includes('hero365.ai'),
    isProduction: hostname.includes('hero365.ai') || (hostname.includes('tradesites.app') && process.env.NODE_ENV === 'production'),
    hostname
  };
}

/**
 * Get API URL based on environment detection
 */
function getApiUrl(detection: EnvironmentDetection): string {
  if (detection.isLocalhost) {
    return 'http://localhost:8000';
  }
  
  if (detection.isNgrokTunnel) {
    // For staging/ngrok environment, try to get from environment variables
    // This will work in Cloudflare Workers
    if (typeof process !== 'undefined') {
      const stagingUrl = process.env.NEXT_PUBLIC_API_URL || 
                        process.env.API_URL ||
                        'https://5ab8f8ec32f1.ngrok-free.app';
      
      // Validate it's not localhost (which would be from build-time inlining)
      if (!stagingUrl.includes('localhost')) {
        return stagingUrl;
      }
    }
    
    // Fallback to the known ngrok URL
    return 'https://5ab8f8ec32f1.ngrok-free.app';
  }
  
  if (detection.isProduction) {
    return 'https://api.hero365.ai';
  }
  
  // Default fallback
  return 'http://localhost:8000';
}

/**
 * Get business ID for the current environment
 */
function getBusinessId(detection: EnvironmentDetection): string | undefined {
  if (detection.isLocalhost) {
    // Always require explicit business ID for localhost
    const businessId = process.env.NEXT_PUBLIC_BUSINESS_ID;
    if (!businessId) {
      throw new Error('NEXT_PUBLIC_BUSINESS_ID is required for localhost development');
    }
    return businessId;
  }
  
  if (detection.isNgrokTunnel) {
    // For staging, allow explicit business ID override
    return process.env.NEXT_PUBLIC_BUSINESS_ID || '550e8400-e29b-41d4-a716-446655440010';
  }
  
  // Production: business ID resolved from hostname
  return undefined;
}

/**
 * Get runtime configuration for the current environment
 */
export async function getRuntimeConfig(): Promise<RuntimeConfig> {
  const detection = detectEnvironment();
  
  const config: RuntimeConfig = {
    apiUrl: getApiUrl(detection),
    environment: detection.isLocalhost ? 'development' : 
                detection.isNgrokTunnel ? 'staging' : 'production',
    businessId: getBusinessId(detection)
  };
  
  // Log configuration for debugging (server-side only)
  if (typeof window === 'undefined') {
    console.log('🔧 [RUNTIME-CONFIG]', {
      detection,
      config,
      processEnv: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT,
        NEXT_PUBLIC_BUSINESS_ID: process.env.NEXT_PUBLIC_BUSINESS_ID
      }
    });
  }
  
  return config;
}

/**
 * Get API URL for the current environment (convenience function)
 */
export async function getRuntimeApiUrl(): Promise<string> {
  const config = await getRuntimeConfig();
  return config.apiUrl;
}

/**
 * Check if we're in development mode
 */
export async function isDevelopment(): Promise<boolean> {
  const config = await getRuntimeConfig();
  return config.environment === 'development';
}

/**
 * Check if we're in staging mode (ngrok)
 */
export async function isStaging(): Promise<boolean> {
  const config = await getRuntimeConfig();
  return config.environment === 'staging';
}
