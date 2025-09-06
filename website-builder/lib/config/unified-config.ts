/**
 * Unified Configuration System
 * 
 * Consolidates all configuration management into a single, type-safe system
 * Replaces scattered config files with a unified approach
 */

// Environment types
export type Environment = 'development' | 'staging' | 'production';
export type DeploymentTarget = 'localhost' | 'ngrok' | 'cloudflare' | 'production';

// API Configuration
export interface ApiConfig {
  baseUrl: string;
  version: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}

// Business Configuration
export interface BusinessConfig {
  defaultBusinessId: string;
  defaultBusinessName: string;
  defaultBusinessPhone: string;
  defaultBusinessEmail: string;
  requireBusinessId: boolean;
}

// Feature Flags
export interface FeatureFlags {
  analytics: boolean;
  voiceAgent: boolean;
  bookingWidget: boolean;
  errorReporting: boolean;
  performanceMonitoring: boolean;
  debugMode: boolean;
  experimentalFeatures: boolean;
}

// Cache Configuration
export interface CacheConfig {
  defaultTTL: number;
  businessDataTTL: number;
  staticDataTTL: number;
  enableClientCache: boolean;
  enableServerCache: boolean;
}

// Performance Configuration
export interface PerformanceConfig {
  enableCodeSplitting: boolean;
  enableImageOptimization: boolean;
  enablePrefetch: boolean;
  bundleAnalysis: boolean;
  criticalCSS: boolean;
}

// Security Configuration
export interface SecurityConfig {
  enableCSP: boolean;
  enableHSTS: boolean;
  allowedOrigins: string[];
  apiKeyRequired: boolean;
}

// Unified Application Configuration
export interface UnifiedConfig {
  environment: Environment;
  deploymentTarget: DeploymentTarget;
  api: ApiConfig;
  business: BusinessConfig;
  features: FeatureFlags;
  cache: CacheConfig;
  performance: PerformanceConfig;
  security: SecurityConfig;
  buildInfo: {
    version: string;
    buildTime: string;
    gitCommit?: string;
  };
}

/**
 * Environment Detection
 */
function detectEnvironment(): { environment: Environment; deploymentTarget: DeploymentTarget } {
  // Explicit environment variable takes precedence
  if (process.env.NEXT_PUBLIC_ENVIRONMENT) {
    const env = process.env.NEXT_PUBLIC_ENVIRONMENT as Environment;
    return {
      environment: env,
      deploymentTarget: env === 'development' ? 'localhost' : 
                      env === 'staging' ? 'ngrok' : 'production'
    };
  }

  // Server-side detection
  if (typeof window === 'undefined') {
    if (process.env.NODE_ENV === 'production') {
      return { environment: 'production', deploymentTarget: 'production' };
    }
    return { environment: 'development', deploymentTarget: 'localhost' };
  }

  // Client-side detection
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname.includes('127.0.0.1')) {
    return { environment: 'development', deploymentTarget: 'localhost' };
  }
  if (hostname.includes('ngrok') || hostname.includes('staging')) {
    return { environment: 'staging', deploymentTarget: 'ngrok' };
  }
  if (hostname.includes('pages.dev') || hostname.includes('workers.dev')) {
    return { environment: 'staging', deploymentTarget: 'cloudflare' };
  }
  return { environment: 'production', deploymentTarget: 'production' };
}

/**
 * API Configuration Builder
 */
function buildApiConfig(environment: Environment, deploymentTarget: DeploymentTarget): ApiConfig {
  let baseUrl: string;

  // Determine API URL
  if (process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
    baseUrl = process.env.NEXT_PUBLIC_API_URL;
  } else {
    switch (deploymentTarget) {
      case 'localhost':
        baseUrl = 'http://localhost:8000';
        break;
      case 'ngrok':
        baseUrl = process.env.NEXT_PUBLIC_STAGING_API_URL || 'https://5ab8f8ec32f1.ngrok-free.app';
        break;
      case 'cloudflare':
        baseUrl = process.env.NEXT_PUBLIC_STAGING_API_URL || 'https://api-staging.hero365.ai';
        break;
      case 'production':
        baseUrl = 'https://api.hero365.ai';
        break;
      default:
        baseUrl = 'http://localhost:8000';
    }
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-API-Version': 'v1',
  };

  // Add environment-specific headers
  if (environment === 'development') {
    headers['X-Environment'] = 'development';
  }

  // Add ngrok headers if needed
  if (baseUrl.includes('ngrok')) {
    headers['ngrok-skip-browser-warning'] = 'true';
  }

  return {
    baseUrl: baseUrl.includes('/api/v1') ? baseUrl : `${baseUrl}/api/v1`,
    version: 'v1',
    timeout: environment === 'development' ? 30000 : 15000,
    retries: environment === 'development' ? 1 : 3,
    headers
  };
}

/**
 * Business Configuration Builder
 */
function buildBusinessConfig(environment: Environment): BusinessConfig {
  return {
    defaultBusinessId: (() => {
      const id = process.env.NEXT_PUBLIC_BUSINESS_ID || process.env.NEXT_PUBLIC_DEV_BUSINESS_ID || '';
      return id;
    })(),
    defaultBusinessName: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Professional Services',
    defaultBusinessPhone: process.env.NEXT_PUBLIC_BUSINESS_PHONE || '+1-555-123-4567',
    defaultBusinessEmail: process.env.NEXT_PUBLIC_BUSINESS_EMAIL || 'contact@example.com',
    requireBusinessId: environment === 'development'
  };
}

/**
 * Feature Flags Builder
 */
function buildFeatureFlags(environment: Environment): FeatureFlags {
  return {
    analytics: process.env.NEXT_PUBLIC_ANALYTICS_ENABLED !== 'false',
    voiceAgent: process.env.NEXT_PUBLIC_VOICE_AGENT_ENABLED === 'true',
    bookingWidget: process.env.NEXT_PUBLIC_BOOKING_WIDGET_ENABLED !== 'false',
    errorReporting: environment === 'production',
    performanceMonitoring: environment !== 'development',
    debugMode: environment === 'development' || process.env.NEXT_PUBLIC_DEBUG_MODE === 'true',
    experimentalFeatures: environment === 'development'
  };
}

/**
 * Cache Configuration Builder
 */
function buildCacheConfig(environment: Environment): CacheConfig {
  return {
    defaultTTL: environment === 'development' ? 60 : 300, // 1 min dev, 5 min prod
    businessDataTTL: environment === 'development' ? 30 : 300, // 30 sec dev, 5 min prod
    staticDataTTL: environment === 'development' ? 60 : 3600, // 1 min dev, 1 hour prod
    enableClientCache: true,
    enableServerCache: environment !== 'development'
  };
}

/**
 * Performance Configuration Builder
 */
function buildPerformanceConfig(environment: Environment): PerformanceConfig {
  return {
    enableCodeSplitting: environment === 'production',
    enableImageOptimization: environment !== 'development',
    enablePrefetch: environment === 'production',
    bundleAnalysis: environment === 'development',
    criticalCSS: environment === 'production'
  };
}

/**
 * Security Configuration Builder
 */
function buildSecurityConfig(environment: Environment): SecurityConfig {
  return {
    enableCSP: environment === 'production',
    enableHSTS: environment === 'production',
    allowedOrigins: environment === 'development' 
      ? ['http://localhost:3000', 'http://localhost:8000']
      : ['https://*.hero365.ai', 'https://*.tradesites.app'],
    apiKeyRequired: environment === 'production'
  };
}

/**
 * Build Information
 */
function buildBuildInfo(): UnifiedConfig['buildInfo'] {
  return {
    version: process.env.npm_package_version || '1.0.0',
    buildTime: process.env.BUILD_TIME || new Date().toISOString(),
    gitCommit: process.env.VERCEL_GIT_COMMIT_SHA || process.env.CF_PAGES_COMMIT_SHA
  };
}

/**
 * Create Unified Configuration
 */
function createUnifiedConfig(): UnifiedConfig {
  const { environment, deploymentTarget } = detectEnvironment();

  const config: UnifiedConfig = {
    environment,
    deploymentTarget,
    api: buildApiConfig(environment, deploymentTarget),
    business: buildBusinessConfig(environment),
    features: buildFeatureFlags(environment),
    cache: buildCacheConfig(environment),
    performance: buildPerformanceConfig(environment),
    security: buildSecurityConfig(environment),
    buildInfo: buildBuildInfo()
  };

  // Log configuration in development
  if (environment === 'development' && typeof window === 'undefined') {
    console.log('🔧 [UNIFIED-CONFIG] Configuration loaded:', {
      environment,
      deploymentTarget,
      apiBaseUrl: config.api.baseUrl,
      businessId: config.business.defaultBusinessId,
      features: Object.entries(config.features).filter(([, enabled]) => enabled).map(([name]) => name)
    });
  }

  return config;
}

// Global configuration instance
let configInstance: UnifiedConfig | null = null;

/**
 * Get the unified configuration
 */
export function getUnifiedConfig(): UnifiedConfig {
  if (!configInstance) {
    configInstance = createUnifiedConfig();
  }
  return configInstance;
}

/**
 * Reset configuration (useful for testing)
 */
export function resetUnifiedConfig(): void {
  configInstance = null;
}

/**
 * Get specific configuration sections
 */
export const getApiConfig = () => getUnifiedConfig().api;
export const getBusinessConfig = () => getUnifiedConfig().business;
export const getFeatureFlags = () => getUnifiedConfig().features;
export const getCacheConfig = () => getUnifiedConfig().cache;
export const getPerformanceConfig = () => getUnifiedConfig().performance;
export const getSecurityConfig = () => getUnifiedConfig().security;
export const getBuildInfo = () => getUnifiedConfig().buildInfo;

/**
 * Environment helpers
 */
export const isDevelopment = () => getUnifiedConfig().environment === 'development';
export const isStaging = () => getUnifiedConfig().environment === 'staging';
export const isProduction = () => getUnifiedConfig().environment === 'production';

/**
 * Feature flag helpers
 */
export const isFeatureEnabled = (feature: keyof FeatureFlags): boolean => {
  return getFeatureFlags()[feature];
};

/**
 * API helpers
 */
export const buildApiUrl = (endpoint: string): string => {
  const config = getApiConfig();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${config.baseUrl}/${cleanEndpoint}`;
};

export const getApiHeaders = (): Record<string, string> => {
  return { ...getApiConfig().headers };
};

// Default export
export default getUnifiedConfig;
