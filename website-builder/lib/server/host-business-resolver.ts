/**
 * Host-Based Business Resolution
 * 
 * Resolves business ID from request host for multi-tenant routing
 * No rebuilds required - single Worker serves all businesses
 */

import { headers } from 'next/headers';
import { getBackendUrl } from '../shared/config/api-config';
import { getRuntimeConfig } from './runtime-config';

interface BusinessResolution {
  businessId: string;
  subdomain: string;
  hostname: string;
  isCustomDomain: boolean;
}

// In-memory cache for host → businessId to avoid resolving on every request
// Note: Cloudflare may spin up multiple isolates; this optimizes within an isolate.
const hostResolutionCache = new Map<string, { businessId: string; expiresAt: number }>();
const HOST_RESOLUTION_TTL_MS = 5 * 60 * 1000; // 5 minutes

/**
 * Extract business info from request host
 */
function parseHostname(hostname: string): { subdomain: string; isCustomDomain: boolean } {
  // tradesites.app subdomain pattern: elite-hvac-austin.tradesites.app
  if (hostname.endsWith('.tradesites.app')) {
    const subdomain = hostname.replace('.tradesites.app', '');
    return { subdomain, isCustomDomain: false };
  }
  
  // Custom domain pattern: elitehvacaustin.com
  return { subdomain: hostname, isCustomDomain: true };
}

/**
 * Resolve business ID from hostname via backend API
 */
async function resolveBusinessFromBackend(hostname: string): Promise<string | null> {
  const config = await getRuntimeConfig();
  const backendUrl = config.apiUrl;
  const url = `${backendUrl}/api/v1/public/websites/resolve?host=${encodeURIComponent(hostname)}`;
  console.log(`🔍 [HOST-RESOLVER] Resolving business for: ${hostname} → ${url}`);
  
  // Simple retry logic for transient network issues (2 attempts)
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Hero365-Website/1.0',
          'ngrok-skip-browser-warning': 'true'
        },
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const text = await response.text().catch(() => '');
        console.warn(`⚠️ [HOST-RESOLVER] Attempt ${attempt} failed: ${response.status} ${text?.slice(0, 200)}`);
        continue;
      }
      
      const data = await response.json();
      const businessId = data.business_id || data.businessId || data.id;
      if (businessId) {
        console.log(`✅ [HOST-RESOLVER] Resolved: ${hostname} → ${businessId}`);
        return businessId;
      }
      console.warn(`⚠️ [HOST-RESOLVER] Attempt ${attempt} missing business ID in response`);
    } catch (error) {
      console.error(`❌ [HOST-RESOLVER] Attempt ${attempt} error for ${hostname}:`, error);
    }
  }
  
  return null;
}

/**
 * Get business ID from current request host (server-side only)
 */
export async function getBusinessIdFromHost(): Promise<BusinessResolution> {
  const headersList = await headers();
  const hostname = headersList.get('host') || 'localhost:3000';
  const hostKey = hostname.toLowerCase();
  const config = await getRuntimeConfig();
  
  // Development: always use explicit business ID
  if (config.environment === 'development') {
    if (!config.businessId) {
      throw new Error('NEXT_PUBLIC_BUSINESS_ID required for development');
    }
    
    return {
      businessId: config.businessId,
      subdomain: 'localhost',
      hostname,
      isCustomDomain: false
    };
  }
  
  // Parse hostname
  const { subdomain, isCustomDomain } = parseHostname(hostname);
  
  // Staging: allow explicit business ID override for testing
  if (config.environment === 'staging' && config.businessId) {
    return {
      businessId: config.businessId,
      subdomain,
      hostname,
      isCustomDomain
    };
  }

  // Cache check first
  const cached = hostResolutionCache.get(hostKey);
  if (cached && cached.expiresAt > Date.now()) {
    return {
      businessId: cached.businessId,
      subdomain,
      hostname,
      isCustomDomain
    };
  }
  
  // Try backend resolution first
  const resolvedBusinessId = await resolveBusinessFromBackend(hostname);
  
  if (resolvedBusinessId) {
    // Cache the successful resolution
    hostResolutionCache.set(hostKey, {
      businessId: resolvedBusinessId,
      expiresAt: Date.now() + HOST_RESOLUTION_TTL_MS
    });
    return {
      businessId: resolvedBusinessId,
      subdomain,
      hostname,
      isCustomDomain
    };
  }
  
  // No resolution possible (strict, no-fallback)
  throw new Error(`Unable to resolve business for hostname: ${hostname}`);
}

/**
 * Get business context from resolved host
 */
export async function getBusinessContextFromHost() {
  const resolution = await getBusinessIdFromHost();
  const backendUrl = getBackendUrl();
  
  try {
    // Fetch business context from backend
    const contextUrl = `${backendUrl}/api/v1/public/contractors/${resolution.businessId}/context`;
    
    console.log(`📊 [HOST-RESOLVER] Fetching context for: ${resolution.businessId}`);
    
    const response = await fetch(contextUrl, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Hero365-Website/1.0'
      },
      // Cache for 5 minutes
      next: { revalidate: 300 }
    });
    
    if (!response.ok) {
      throw new Error(`Business context fetch failed: ${response.status}`);
    }
    
    const businessContext = await response.json();
    
    return {
      ...businessContext,
      resolution
    };
    
  } catch (error) {
    console.error(`❌ [HOST-RESOLVER] Context fetch error for ${resolution.businessId}:`, error);
    throw error;
  }
}

/**
 * Validate that business exists and is active
 */
export async function validateBusinessHost(): Promise<boolean> {
  try {
    const resolution = await getBusinessIdFromHost();
    const backendUrl = getBackendUrl();
    
    // Quick validation endpoint
    const validateUrl = `${backendUrl}/api/v1/public/contractors/${resolution.businessId}/validate`;
    
    const response = await fetch(validateUrl, {
      method: 'HEAD',
      signal: AbortSignal.timeout(2000)
    });
    
    return response.ok;
    
  } catch (error) {
    console.error('❌ [HOST-RESOLVER] Business validation failed:', error);
    return false;
  }
}
