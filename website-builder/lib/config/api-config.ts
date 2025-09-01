/**
 * API Configuration
 * 
 * Centralized configuration for API endpoints that adapts to different environments
 */

export interface ApiConfig {
  baseUrl: string;
  apiVersion: string;
  timeout: number;
  retries: number;
  environment: 'development' | 'staging' | 'production';
}

export interface EnvironmentConfig {
  api: ApiConfig;
  features: {
    analytics: boolean;
    voiceAgent: boolean;
    bookingWidget: boolean;
    errorReporting: boolean;
  };
  business: {
    defaultBusinessId: string;
    defaultBusinessName: string;
    defaultBusinessPhone: string;
    defaultBusinessEmail: string;
  };
}

/**
 * Get the current environment
 * SSR-compatible: ensures consistent environment detection
 */
function getEnvironment(): 'development' | 'staging' | 'production' {
  // HIGHEST PRIORITY: Explicit environment variable (set during deployment)
  if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_ENVIRONMENT) {
    return process.env.NEXT_PUBLIC_ENVIRONMENT as 'development' | 'staging' | 'production';
  }
  
  // SECOND PRIORITY: NODE_ENV for server-side consistency
  if (typeof window === 'undefined') {
    // Server-side: use NODE_ENV
    const nodeEnv = process.env.NODE_ENV;
    if (nodeEnv === 'production') {
      return 'production';
    } else {
      return 'development';
    }
  }
  
  // FALLBACK: Client-side hostname detection (for development only)
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
    return 'development';
  } else if (hostname.includes('staging') || hostname.includes('dev') || hostname.includes('preview')) {
    return 'staging';
  } else {
    return 'production';
  }
}

/**
 * Get API base URL based on environment
 * SSR-compatible: prioritizes explicit env vars to ensure consistency
 */
function getApiBaseUrl(environment: string): string {
  // HIGHEST PRIORITY: Explicit API URL set during build/deployment
  if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // SECOND PRIORITY: Environment-specific API URLs  
  if (typeof process !== 'undefined') {
    if (process.env.NEXT_PUBLIC_STAGING_API_URL && environment === 'staging') {
      return process.env.NEXT_PUBLIC_STAGING_API_URL;
    }
    if (process.env.NEXT_PUBLIC_PRODUCTION_API_URL && environment === 'production') {
      return process.env.NEXT_PUBLIC_PRODUCTION_API_URL;
    }
  }
  
  // FALLBACK: Environment-based defaults (consistent for SSR)
  switch (environment) {
    case 'development':
      return 'http://localhost:8000';
    case 'staging':
      return 'http://localhost:8000';  // Use localhost for staging builds
    case 'production':
      return 'https://api.hero365.ai';
    default:
      return 'http://localhost:8000';
  }
}

/**
 * Create environment-specific configuration
 */
function createEnvironmentConfig(): EnvironmentConfig {
  const environment = getEnvironment();
  const baseUrl = getApiBaseUrl(environment);
  
  return {
    api: {
      baseUrl: baseUrl.includes('/api/v1') ? baseUrl : `${baseUrl}/api/v1`,
      apiVersion: 'v1',
      timeout: environment === 'development' ? 30000 : 15000,
      retries: environment === 'development' ? 1 : 3,
      environment
    },
    features: {
      analytics: process.env.NEXT_PUBLIC_ANALYTICS_ENABLED !== 'false',
      voiceAgent: process.env.NEXT_PUBLIC_VOICE_AGENT_ENABLED === 'true',
      bookingWidget: process.env.NEXT_PUBLIC_BOOKING_WIDGET_ENABLED !== 'false',
      errorReporting: environment === 'production'
    },
    business: {
      // For development: use test business with real data
      // For production: must be set via deployment scripts or environment variables
      defaultBusinessId: process.env.NEXT_PUBLIC_BUSINESS_ID || 
                        process.env.NEXT_PUBLIC_DEV_BUSINESS_ID || 
                        'demo-business-id',
      defaultBusinessName: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Demo Business',
      defaultBusinessPhone: process.env.NEXT_PUBLIC_BUSINESS_PHONE || '+1-555-123-4567',
      defaultBusinessEmail: process.env.NEXT_PUBLIC_BUSINESS_EMAIL || 'contact@example.com'
    }
  };
}

// Global configuration instance
let configInstance: EnvironmentConfig | null = null;

/**
 * Get the current configuration
 */
export function getConfig(): EnvironmentConfig {
  if (!configInstance) {
    configInstance = createEnvironmentConfig();
  }
  return configInstance;
}

/**
 * Reset configuration (useful for testing)
 */
export function resetConfig(): void {
  configInstance = null;
}

/**
 * Get API configuration
 */
export function getApiConfig(): ApiConfig {
  return getConfig().api;
}

/**
 * Get feature flags
 */
export function getFeatures() {
  return getConfig().features;
}

/**
 * Get business configuration
 */
export function getBusinessConfig() {
  // Check for environment variables first (set by deployment script)
  if (typeof process !== 'undefined') {
    const envBusinessId = process.env.NEXT_PUBLIC_BUSINESS_ID;
    const envBusinessName = process.env.NEXT_PUBLIC_BUSINESS_NAME;
    const envBusinessPhone = process.env.NEXT_PUBLIC_BUSINESS_PHONE;
    const envBusinessEmail = process.env.NEXT_PUBLIC_BUSINESS_EMAIL;
    
    if (envBusinessId) {
      return {
        defaultBusinessId: envBusinessId,
        defaultBusinessName: envBusinessName || 'Professional Services',
        defaultBusinessPhone: envBusinessPhone || '+1-555-123-4567',
        defaultBusinessEmail: envBusinessEmail || 'contact@example.com'
      };
    }
  }
  
  // Try to load business-specific configuration file
  if (typeof window !== 'undefined') {
    try {
      // This would be generated by the deployment script
      const businessConfigPath = '/config/business-config.json';
      // Note: In a real implementation, you'd fetch this or have it embedded
      // For now, fall back to default config
    } catch (error) {
      // Fall back to default configuration
    }
  }
  
  return getConfig().business;
}

/**
 * Get the current business ID
 */
export function getCurrentBusinessId(): string {
  const businessConfig = getBusinessConfig();
  return businessConfig.defaultBusinessId;
}

/**
 * Resolve business id from the request host via backend resolver (cached on client).
 * Falls back to env/default config when resolver is unavailable.
 */
let cachedResolvedBusinessId: string | null = null;
export async function resolveBusinessIdFromHost(): Promise<string> {
  if (cachedResolvedBusinessId) return cachedResolvedBusinessId;
  try {
    if (typeof window === 'undefined') {
      // Server-side: return configured id
      return getCurrentBusinessId();
    }
    const host = window.location.host;
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}/api/v1/public/websites/resolve?host=${encodeURIComponent(host)}`;
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    if (res.ok) {
      const data = await res.json();
      const id = data.business_id || data.businessId || data.id;
      if (id) {
        cachedResolvedBusinessId = id as string;
        return cachedResolvedBusinessId;
      }
    }
  } catch (err) {
    // ignore and fallback
  }
  return getCurrentBusinessId();
}

/**
 * Build API URL for a specific endpoint
 */
export function buildApiUrl(endpoint: string): string {
  const config = getApiConfig();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  const fullUrl = `${config.baseUrl}/${cleanEndpoint}`;
  console.log('🔧 [DEBUG] buildApiUrl:', { 
    baseUrl: config.baseUrl, 
    endpoint, 
    cleanEndpoint, 
    fullUrl,
    environment: config.environment 
  });
  return fullUrl;
}

/**
 * Build public API URL (no authentication required)
 */
export function buildPublicApiUrl(endpoint: string): string {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  const fullUrl = buildApiUrl(`public/${cleanEndpoint}`);
  console.log('🔧 [DEBUG] buildPublicApiUrl:', { endpoint, cleanEndpoint, fullUrl });
  return fullUrl;
}

/**
 * Build authenticated API URL (authentication required)
 */
export function buildAuthApiUrl(endpoint: string): string {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return buildApiUrl(cleanEndpoint);
}

/**
 * Check if we're in development mode
 */
export function isDevelopment(): boolean {
  return getConfig().api.environment === 'development';
}

/**
 * Check if we're in production mode
 */
export function isProduction(): boolean {
  return getConfig().api.environment === 'production';
}

/**
 * Get the backend API base URL (without /api/v1 path)
 * This is the global setting for all API calls
 */
export function getBackendUrl(): string {
  const environment = getEnvironment();
  return getApiBaseUrl(environment);
}

/**
 * Get environment-specific headers
 */
export function getDefaultHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add environment-specific headers
  if (isDevelopment()) {
    headers['X-Environment'] = 'development';
  }

  // Add version header
  headers['X-API-Version'] = getApiConfig().apiVersion;

  // Add ngrok header if using ngrok tunnel
  const apiUrl = getApiConfig().baseUrl;
  if (apiUrl.includes('ngrok')) {
    headers['ngrok-skip-browser-warning'] = 'true';
  }

  return headers;
}

/**
 * Configuration for different deployment environments
 */
export const DEPLOYMENT_CONFIGS = {
  development: {
    apiUrl: 'http://localhost:8000',
    websiteUrl: 'http://localhost:3001',
    features: {
      analytics: false,
      errorReporting: false,
      debugMode: true
    }
  },
  staging: {
    apiUrl: 'http://localhost:8000',
    websiteUrl: 'https://staging.hero365.ai',
    features: {
      analytics: true,
      errorReporting: true,
      debugMode: true
    }
  },
  production: {
    apiUrl: 'https://api.hero365.ai',
    websiteUrl: 'https://hero365.ai',
    features: {
      analytics: true,
      errorReporting: true,
      debugMode: false
    }
  }
} as const;

export default getConfig;
