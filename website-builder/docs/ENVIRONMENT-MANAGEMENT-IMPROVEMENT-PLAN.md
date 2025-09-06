# 🔧 Environment Management Improvement Plan

## Current State Analysis

### 🔴 Problems Identified

1. **Hardcoded API URLs**: The home page (`app/page.tsx`) has a hardcoded ngrok URL to bypass environment variable issues
2. **Build-time Variable Inlining**: Next.js bakes in `NEXT_PUBLIC_*` variables at build time, causing localhost to be used in production
3. **Complex Environment Detection**: Multiple fallback mechanisms that aren't working correctly
4. **Manual Deployment Process**: Despite having automation scripts, cache and version management is problematic
5. **Inconsistent Multi-tenant Routing**: Business resolution works but environment-specific API URLs don't
6. **No Production Backend**: Currently using ngrok tunnels for staging, no production API deployed

### 🟡 Current Architecture

```
Local Development:
  Backend: localhost:8000
  Frontend: localhost:3000
  Business ID: Hardcoded in env vars

Staging (ngrok):
  Backend: https://xxxxx.ngrok-free.app (changes frequently)
  Frontend: *.tradesites.app (Cloudflare Workers)
  Business ID: Resolved from hostname

Production (planned):
  Backend: https://api.hero365.ai
  Frontend: *.tradesites.app or custom domains
  Business ID: Resolved from hostname
```

## 📋 Improvement Plan

### Phase 1: Environment Configuration Cleanup (Immediate)

#### 1.1 Create Runtime Configuration Service
```typescript
// website-builder/lib/server/runtime-config.ts

interface RuntimeConfig {
  apiUrl: string;
  environment: 'development' | 'staging' | 'production';
  businessId?: string;
}

export async function getRuntimeConfig(): Promise<RuntimeConfig> {
  // Server-side only - read from Cloudflare Worker bindings
  if (typeof process !== 'undefined' && process.env.CF_PAGES) {
    // Cloudflare Workers environment
    const env = (globalThis as any).__env__;
    return {
      apiUrl: env.API_URL || 'https://api.hero365.ai',
      environment: env.ENVIRONMENT || 'production',
      businessId: env.BUSINESS_ID
    };
  }
  
  // Local development
  return {
    apiUrl: process.env.API_URL || 'http://localhost:8000',
    environment: 'development',
    businessId: process.env.NEXT_PUBLIC_BUSINESS_ID
  };
}
```

#### 1.2 Update wrangler.toml with Clear Environment Separation
```toml
# website-builder/wrangler.toml

[env.development]
name = "hero365-website-dev"
vars = { API_URL = "http://localhost:8000", ENVIRONMENT = "development" }

[env.staging]
name = "hero365-website-staging"
vars = { API_URL = "https://staging-api.hero365.ai", ENVIRONMENT = "staging" }
# Note: Will use ngrok URL until staging API is deployed

[env.production]
name = "hero365-website-production"
vars = { API_URL = "https://api.hero365.ai", ENVIRONMENT = "production" }

[[env.staging.routes]]
pattern = "*.staging.tradesites.app/*"
zone_id = "c28e66bcb1f56af2ac253ae47bf341f4"

[[env.production.routes]]
pattern = "*.tradesites.app/*"
zone_id = "c28e66bcb1f56af2ac253ae47bf341f4"
```

#### 1.3 Remove All Hardcoded URLs
```typescript
// website-builder/app/page.tsx
async function loadBusinessData(businessId: string) {
  const config = await getRuntimeConfig();
  const backendUrl = config.apiUrl;
  // ... rest of the code
}
```

### Phase 2: Backend API Deployment (Week 1)

#### 2.1 Deploy Staging API
```yaml
# backend/docker-compose.staging.yml
services:
  backend:
    image: hero365-backend:staging
    environment:
      - DATABASE_URL=${SUPABASE_URL}
      - ENVIRONMENT=staging
    deploy:
      replicas: 2
    labels:
      - "traefik.http.routers.api-staging.rule=Host(`staging-api.hero365.ai`)"
```

#### 2.2 Deploy Production API
```yaml
# backend/docker-compose.production.yml
services:
  backend:
    image: hero365-backend:production
    environment:
      - DATABASE_URL=${SUPABASE_URL}
      - ENVIRONMENT=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    labels:
      - "traefik.http.routers.api.rule=Host(`api.hero365.ai`)"
```

### Phase 3: Automated Environment Management (Week 2)

#### 3.1 Environment-Aware Deployment Script
```bash
#!/bin/bash
# scripts/deploy-environment.sh

ENVIRONMENT=${1:-staging}
BACKEND_URL=${2:-auto}

# Auto-detect backend URL based on environment
if [ "$BACKEND_URL" = "auto" ]; then
  case $ENVIRONMENT in
    development)
      BACKEND_URL="http://localhost:8000"
      ;;
    staging)
      # Check if staging API is live
      if curl -f https://staging-api.hero365.ai/health; then
        BACKEND_URL="https://staging-api.hero365.ai"
      else
        # Fallback to ngrok
        BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
      fi
      ;;
    production)
      BACKEND_URL="https://api.hero365.ai"
      ;;
  esac
fi

echo "Deploying to $ENVIRONMENT with backend: $BACKEND_URL"

# Update wrangler.toml dynamically
sed -i "s|API_URL = \".*\"|API_URL = \"$BACKEND_URL\"|g" wrangler.toml

# Build and deploy
npm run build
npx opennextjs-cloudflare build
npx wrangler deploy --env $ENVIRONMENT

# Purge cache
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

#### 3.2 GitHub Actions CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy Website

on:
  push:
    branches: [main, staging, develop]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Determine Environment
        id: env
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/main" ]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/staging" ]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
          fi
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          
      - name: Install Dependencies
        run: |
          cd website-builder
          npm ci
          
      - name: Deploy to Cloudflare
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          ENVIRONMENT: ${{ steps.env.outputs.environment }}
        run: |
          cd website-builder
          ./scripts/deploy-environment.sh $ENVIRONMENT
```

### Phase 4: Multi-Tenant Improvements (Week 3)

#### 4.1 Enhanced Business Resolution
```typescript
// website-builder/lib/server/business-resolver-v2.ts

export class BusinessResolver {
  private static cache = new Map<string, CachedResolution>();
  
  static async resolve(hostname: string): Promise<BusinessResolution> {
    // Check cache first
    const cached = this.cache.get(hostname);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.data;
    }
    
    // Determine resolution strategy based on environment
    const config = await getRuntimeConfig();
    let resolution: BusinessResolution;
    
    switch (config.environment) {
      case 'development':
        resolution = await this.resolveForDevelopment();
        break;
      case 'staging':
        resolution = await this.resolveForStaging(hostname);
        break;
      case 'production':
        resolution = await this.resolveForProduction(hostname);
        break;
    }
    
    // Cache the resolution
    this.cache.set(hostname, {
      data: resolution,
      expiresAt: Date.now() + 5 * 60 * 1000 // 5 minutes
    });
    
    return resolution;
  }
  
  private static async resolveForProduction(hostname: string): Promise<BusinessResolution> {
    // Check if custom domain
    if (!hostname.includes('tradesites.app')) {
      // Query backend for custom domain mapping
      const response = await fetch(`${config.apiUrl}/api/v1/domains/resolve`, {
        method: 'POST',
        body: JSON.stringify({ hostname })
      });
      return response.json();
    }
    
    // Extract subdomain for *.tradesites.app
    const subdomain = hostname.split('.')[0];
    
    // Query backend for business by subdomain
    const response = await fetch(
      `${config.apiUrl}/api/v1/businesses/by-subdomain/${subdomain}`
    );
    
    return response.json();
  }
}
```

#### 4.2 Database Schema for Domain Management
```sql
-- Supabase migration
CREATE TABLE domain_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id UUID NOT NULL REFERENCES businesses(id),
  domain TEXT NOT NULL UNIQUE,
  subdomain TEXT NOT NULL,
  is_custom BOOLEAN DEFAULT false,
  ssl_status TEXT DEFAULT 'pending',
  cloudflare_zone_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_domain_mappings_domain ON domain_mappings(domain);
CREATE INDEX idx_domain_mappings_subdomain ON domain_mappings(subdomain);
```

### Phase 5: Monitoring & Observability (Week 4)

#### 5.1 Environment Health Dashboard
```typescript
// website-builder/app/api/health/detailed/route.ts

export async function GET() {
  const config = await getRuntimeConfig();
  
  const checks = await Promise.allSettled([
    checkBackendHealth(config.apiUrl),
    checkDatabaseConnection(),
    checkCloudflareWorkerStatus(),
    checkBusinessResolution()
  ]);
  
  return Response.json({
    environment: config.environment,
    timestamp: new Date().toISOString(),
    checks: {
      backend: checks[0].status === 'fulfilled' ? checks[0].value : { status: 'error', error: checks[0].reason },
      database: checks[1].status === 'fulfilled' ? checks[1].value : { status: 'error', error: checks[1].reason },
      worker: checks[2].status === 'fulfilled' ? checks[2].value : { status: 'error', error: checks[2].reason },
      resolution: checks[3].status === 'fulfilled' ? checks[3].value : { status: 'error', error: checks[3].reason }
    }
  });
}
```

#### 5.2 Deployment Verification
```typescript
// scripts/verify-deployment.ts

async function verifyDeployment(environment: string) {
  const urls = {
    development: 'http://localhost:3000',
    staging: 'https://elite-hvac-austin.staging.tradesites.app',
    production: 'https://elite-hvac-austin.tradesites.app'
  };
  
  const url = urls[environment];
  
  console.log(`Verifying deployment for ${environment}...`);
  
  // Check health endpoint
  const healthResponse = await fetch(`${url}/api/health/detailed`);
  const health = await healthResponse.json();
  
  if (health.checks.backend.status !== 'healthy') {
    throw new Error(`Backend unhealthy: ${JSON.stringify(health.checks.backend)}`);
  }
  
  // Check page rendering
  const pageResponse = await fetch(url);
  const html = await pageResponse.text();
  
  if (html.includes('Error:') || html.includes('localhost:8000')) {
    throw new Error('Page contains error or localhost references');
  }
  
  console.log(`✅ Deployment verified for ${environment}`);
}
```

## 🚀 Implementation Timeline

### Week 1: Environment Cleanup
- [ ] Implement runtime configuration service
- [ ] Remove all hardcoded URLs
- [ ] Update wrangler.toml with proper environment separation
- [ ] Deploy staging API on AWS/GCP

### Week 2: Backend Deployment
- [ ] Deploy production API
- [ ] Set up load balancing and auto-scaling
- [ ] Configure SSL certificates
- [ ] Implement health checks

### Week 3: Automation
- [ ] Create environment-aware deployment scripts
- [ ] Set up GitHub Actions CI/CD
- [ ] Implement automatic cache purging
- [ ] Add deployment verification

### Week 4: Multi-tenant & Monitoring
- [ ] Enhance business resolution logic
- [ ] Implement domain mapping database
- [ ] Create health dashboard
- [ ] Set up monitoring alerts

## 📊 Success Metrics

1. **Zero Hardcoded URLs**: All environment-specific configuration via runtime
2. **Deployment Success Rate**: >99% successful deployments
3. **Environment Isolation**: No cross-environment data leakage
4. **Cache Hit Rate**: <5 minute cache TTL for dynamic content
5. **API Response Time**: <200ms p95 latency
6. **Business Resolution**: <50ms resolution time with caching

## 🔄 Migration Strategy

1. **Phase 1**: Deploy new runtime config alongside existing code
2. **Phase 2**: Gradually migrate routes to use new config
3. **Phase 3**: Remove old hardcoded values
4. **Phase 4**: Monitor and optimize

## 🛡️ Risk Mitigation

1. **Rollback Plan**: Keep old deployment scripts as `legacy-deploy.sh`
2. **Feature Flags**: Use environment variables to toggle new features
3. **Gradual Rollout**: Test with single business first, then expand
4. **Monitoring**: Alert on any localhost references in production

## 📝 Documentation Updates

1. Update deployment guide with new environment management
2. Create troubleshooting guide for common issues
3. Document environment variable requirements
4. Add architecture diagrams for multi-tenant routing

This plan will transform the current fragmented environment management into a robust, automated system that handles local development, staging, and production seamlessly!
