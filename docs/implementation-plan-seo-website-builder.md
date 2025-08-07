# SEO Website Builder Implementation Plan

## Executive Summary
Build an AI-powered website generation and SEO optimization platform that automatically creates, deploys, and maintains high-performing websites for Hero365 professionals, integrated with Google Business Profile management, local SEO tools, and one-click domain registration for maximum SEO impact. The system leverages the trade-based business classification (Commercial and Residential trades) to generate industry-specific, highly optimized websites.

## Architecture Overview

### Core Components
1. **Website Generator Service** - AI-powered static site generation using Next.js
2. **Domain Registration Service** - Multi-provider integration for one-click domain purchase with SEO scoring
3. **SEO Optimization Engine** - Content generation, keyword research, schema markup
4. **Google Business Profile Manager** - Two-way sync, insights, review management  
5. **Deployment Infrastructure** - AWS S3 + CloudFront for hosting
6. **Analytics & Monitoring** - Performance tracking, rank monitoring, Core Web Vitals

### Technology Stack
- **Frontend Generation**: Next.js 14+ (static export)
- **AI Services**: OpenAI GPT-4 for content, embeddings for semantic search
- **CDN/Hosting**: Cloudflare Pages (integrated with domain) or AWS S3 + CloudFront
- **Database**: Supabase (PostgreSQL) for templates, settings, analytics
- **Background Jobs**: Celery/Redis for async processing
- **APIs**: Google Business Profile API, Google Search Console API
- **Domain Registration & CDN**: Cloudflare (single provider for domains, DNS, CDN, and DDoS protection)

## Phase 1: Foundation (Week 1-2)

### 1.0 Unified Business Branding System
```python
# backend/app/domain/entities/business_branding.py
"""
Centralized branding configuration shared across all business components:
- Websites (SEO sites, landing pages)
- Documents (Estimates, Invoices, Contracts)
- Emails (Transactional, Marketing)
- Mobile App (Custom theming)

Benefits:
1. Single source of truth for brand identity
2. Consistent customer experience across all touchpoints
3. Easy brand updates propagate to all components
4. Trade-specific theme suggestions
5. Export to design tools (Figma, Sketch)
"""

# Key Features:
- ColorScheme: Unified colors with trade-specific suggestions
- Typography: Consistent fonts and sizes across all materials
- BrandAssets: Centralized logo, watermark, signature management
- Trade Themes: Automatic color suggestions based on trade type
- CSS Generation: Auto-generate CSS variables for web components
- Component Configs: Specific settings for each component type
```

### 1.1 Database Schema Design
```sql
-- Website configuration and templates
CREATE TABLE website_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_type VARCHAR(50) NOT NULL, -- Specific trade from CommercialTrade or ResidentialTrade enums
    trade_category VARCHAR(20) NOT NULL, -- 'COMMERCIAL', 'RESIDENTIAL', or 'BOTH'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    preview_url VARCHAR(500),
    structure JSONB NOT NULL, -- Page hierarchy and components
    default_content JSONB, -- AI prompts and seed content
    seo_config JSONB, -- Meta tags, schema templates
    is_multi_trade BOOLEAN DEFAULT FALSE, -- Support for multi-trade businesses
    supported_trades TEXT[], -- Array of supported trade combinations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE business_websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    branding_id UUID REFERENCES business_branding(id), -- Link to centralized branding
    template_id UUID REFERENCES website_templates(id),
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(100), -- for hero365.ai subdomains
    status VARCHAR(50) DEFAULT 'draft', -- draft, building, deployed, error
    
    -- Customization (overrides from central branding if needed)
    theme_overrides JSONB, -- Component-specific overrides
    content_overrides JSONB, -- User edits to AI content
    pages JSONB, -- Generated page structure
    
    -- Deployment info
    s3_bucket VARCHAR(255),
    cloudfront_distribution_id VARCHAR(255),
    certificate_arn VARCHAR(255),
    last_build_at TIMESTAMP WITH TIME ZONE,
    last_deploy_at TIMESTAMP WITH TIME ZONE,
    
    -- SEO Settings
    seo_keywords JSONB,
    target_locations JSONB,
    google_site_verification VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE domain_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    website_id UUID REFERENCES business_websites(id) ON DELETE SET NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL DEFAULT 'cloudflare',
    status VARCHAR(50) DEFAULT 'active', -- active, expired, transferred, cancelled
    
    -- Registration details
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    auto_renew BOOLEAN DEFAULT true,
    privacy_protection BOOLEAN DEFAULT true,
    
    -- Provider details
    provider_order_id VARCHAR(255),
    nameservers JSONB,
    dns_configured BOOLEAN DEFAULT false,
    
    -- Pricing
    purchase_price DECIMAL(10,2),
    renewal_price DECIMAL(10,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE website_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES business_websites(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    avg_session_duration INTEGER, -- seconds
    bounce_rate DECIMAL(5,2),
    core_web_vitals JSONB, -- LCP, FID, CLS scores
    search_impressions INTEGER DEFAULT 0,
    search_clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(website_id, date)
);
```

### 1.2 Domain Entities
```python
# backend/app/domain/entities/website.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.domain.entities.business import TradeCategory, CommercialTrade, ResidentialTrade

class WebsiteStatus(Enum):
    DRAFT = "draft"
    BUILDING = "building"
    BUILT = "built"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ERROR = "error"

class WebsiteTemplate(BaseModel):
    id: UUID
    trade_type: str  # Specific trade value from CommercialTrade or ResidentialTrade
    trade_category: TradeCategory
    name: str
    description: Optional[str] = None
    preview_url: Optional[HttpUrl] = None
    structure: Dict = Field(default_factory=dict)  # Page hierarchy
    default_content: Dict = Field(default_factory=dict)
    seo_config: Dict = Field(default_factory=dict)
    is_multi_trade: bool = False
    supported_trades: List[str] = Field(default_factory=list)
    
    def supports_business(self, business: 'Business') -> bool:
        """Check if template supports a business's trades"""
        business_trades = business.get_all_trades()
        if self.is_multi_trade:
            return any(trade in self.supported_trades for trade in business_trades)
        return self.trade_type in business_trades

class BusinessWebsite(BaseModel):
    id: UUID
    business_id: UUID
    template_id: Optional[UUID] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    status: WebsiteStatus = WebsiteStatus.DRAFT
    
    # Customization
    theme_config: Dict = Field(default_factory=dict)
    content_overrides: Dict = Field(default_factory=dict)
    pages: List[Dict] = Field(default_factory=list)
    
    # Trade-specific content
    primary_trade: Optional[str] = None  # Primary trade for SEO focus
    secondary_trades: List[str] = Field(default_factory=list)  # Additional trades to mention
    service_areas: List[str] = Field(default_factory=list)  # Geographic service areas
    
    # Deployment
    deployment_info: Optional[Dict] = None
    seo_settings: Dict = Field(default_factory=dict)
    last_build_at: Optional[datetime] = None
    last_deploy_at: Optional[datetime] = None
    
    def get_seo_focus_keywords(self) -> List[str]:
        """Generate primary SEO keywords based on trades"""
        keywords = []
        if self.primary_trade:
            keywords.extend([
                f"{self.primary_trade} services",
                f"{self.primary_trade} contractor",
                f"professional {self.primary_trade}"
            ])
        for area in self.service_areas[:3]:  # Top 3 service areas
            if self.primary_trade:
                keywords.append(f"{self.primary_trade} {area}")
        return keywords
```

### 1.3 Repository Layer
```python
# backend/app/domain/repositories/website_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

class WebsiteRepository(ABC):
    @abstractmethod
    async def create_website(self, website: BusinessWebsite) -> BusinessWebsite:
        pass
    
    @abstractmethod
    async def get_website_by_business(self, business_id: UUID) -> Optional[BusinessWebsite]:
        pass
    
    @abstractmethod
    async def update_website(self, website_id: UUID, updates: Dict) -> BusinessWebsite:
        pass
    
    @abstractmethod
    async def get_templates_by_trade(self, trade_type: str) -> List[WebsiteTemplate]:
        pass
```

## Phase 2: Template System (Week 2-3)

### 2.1 Create Industry Templates

#### Commercial Trade Templates
```typescript
// website-builder/templates/commercial/plumbing.ts
export const plumbingCommercialTemplate = {
  trade: CommercialTrade.PLUMBING,
  category: TradeCategory.COMMERCIAL,
  name: 'Commercial Plumbing Professional',
  pages: [
    {
      path: '/',
      name: 'Home',
      sections: [
        { type: 'hero', config: { headline: 'Commercial Plumbing Experts' } },
        { type: 'services', config: { featured: true } },
        { type: 'certifications' },
        { type: 'testimonials', config: { count: 3 } },
        { type: 'cta', config: { action: 'Get Quote' } }
      ]
    },
    {
      path: '/services',
      name: 'Services',
      sections: [
        { type: 'service-grid' },
        { type: 'process' },
        { type: 'faq' }
      ]
    }
  ],
  seo: {
    keywords: ['commercial plumbing', 'pipe repair', 'water heater installation'],
    schema: ['LocalBusiness', 'PlumbingService']
  }
};

// Templates for all 10 Commercial Trades:
// - Mechanical, Refrigeration, Plumbing, Electrical
// - Security Systems, Landscaping, Roofing
// - Kitchen Equipment, Water Treatment, Pool & Spa
```

#### Residential Trade Templates
```typescript
// website-builder/templates/residential/hvac.ts
export const hvacResidentialTemplate = {
  trade: ResidentialTrade.HVAC,
  category: TradeCategory.RESIDENTIAL,
  name: 'Residential HVAC Services',
  pages: [
    {
      path: '/',
      name: 'Home',
      sections: [
        { type: 'hero', config: { headline: 'Your Comfort is Our Priority' } },
        { type: 'services', config: { residential: true } },
        { type: 'emergency-service' },
        { type: 'reviews' },
        { type: 'service-areas' }
      ]
    }
  ],
  seo: {
    keywords: ['hvac repair', 'air conditioning', 'heating services'],
    schema: ['LocalBusiness', 'HVACBusiness']
  }
};

// Templates for all 10 Residential Trades:
// - HVAC, Plumbing, Electrical, Chimney
// - Roofing, Garage Door, Septic
// - Pest Control, Irrigation, Painting
```

#### Multi-Trade Templates
```typescript
// website-builder/templates/multi-trade.ts
export const multiTradeTemplate = {
  trade_category: TradeCategory.BOTH,
  is_multi_trade: true,
  name: 'Multi-Service Professional',
  supports_dynamic_trades: true,
  pages: [
    {
      path: '/',
      name: 'Home',
      sections: [
        { type: 'hero', config: { dynamic: true } },
        { type: 'trade-selector' },  // Dynamic based on business trades
        { type: 'service-grid', config: { multi_trade: true } },
        { type: 'why-choose-us' },
        { type: 'coverage-map' }
      ]
    }
  ]
};
```

### 2.2 AI Content Generator Service with Unified Branding
```python
# backend/app/application/services/content_generator_service.py
from typing import Dict, List
import openai
import json

from app.domain.entities.business import Business, TradeCategory
from app.domain.entities.business_branding import BusinessBranding

class ContentGeneratorService:
    def __init__(self, openai_client):
        self.client = openai_client
    
    async def generate_page_content(
        self,
        template: WebsiteTemplate,
        business: Business,
        branding: BusinessBranding,
        page_type: str
    ) -> Dict:
        """Generate SEO-optimized content for a page with brand consistency"""
        
        # Get business trade information
        primary_trade = business.get_primary_trade()
        all_trades = business.get_all_trades()
        is_multi_trade = business.is_multi_trade_business()
        
        # Apply trade-specific branding if not already applied
        if not branding.trade_customizations:
            branding = branding.apply_trade_theme(
                primary_trade, 
                business.trade_category.value if business.trade_category else "both"
            )
        
        # Build trade-specific prompt
        prompt = self._build_trade_content_prompt(
            template, 
            business, 
            page_type,
            primary_trade,
            all_trades,
            is_multi_trade
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are an SEO expert specializing in {primary_trade} services. "
                              f"Create compelling, keyword-rich content for local service businesses."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _build_trade_content_prompt(
        self,
        template: WebsiteTemplate,
        business: Business,
        page_type: str,
        primary_trade: str,
        all_trades: List[str],
        is_multi_trade: bool
    ) -> str:
        """Build content prompt based on trade specifics"""
        
        base_prompt = f"""
        Generate SEO-optimized content for a {page_type} page.
        
        Business Information:
        - Name: {business.name}
        - Primary Trade: {primary_trade}
        - All Services: {', '.join(all_trades)}
        - Multi-Trade Business: {is_multi_trade}
        - Trade Category: {business.trade_category.value if business.trade_category else 'Both'}
        - Location: {business.business_address}
        - Service Areas: {', '.join(business.service_areas)}
        
        SEO Requirements:
        - Include location-based keywords
        - Mention all relevant trades naturally
        - Focus on {primary_trade} as the main service
        - Include calls-to-action
        - Use schema markup suggestions
        """
        
        if business.trade_category == TradeCategory.COMMERCIAL:
            base_prompt += """
        - Emphasize commercial expertise, certifications, and scale
        - Mention business hours, emergency services, and contracts
        - Include industry-specific terminology
        """
        elif business.trade_category == TradeCategory.RESIDENTIAL:
            base_prompt += """
        - Focus on homeowner benefits, trust, and reliability
        - Emphasize family-friendly service and local presence
        - Include residential-specific services and warranties
        """
        
        return base_prompt
    
    async def optimize_meta_tags(
        self,
        page_content: str,
        business: Business,
        location: str
    ) -> Dict:
        """Generate optimized meta tags based on business trades"""
        
        primary_trade = business.get_primary_trade()
        seo_keywords = business.get_seo_keywords()
        
        return {
            "title": f"{business.name} - {primary_trade.title()} Services in {location}",
            "description": f"Professional {primary_trade} services in {location}. "
                          f"{business.name} offers {', '.join(business.get_all_trades())}. "
                          f"Call now for expert service.",
            "keywords": seo_keywords[:10],  # Top 10 keywords
            "og:title": f"{business.name} - Expert {primary_trade.title()} Services",
            "og:description": f"Trusted {primary_trade} professionals serving {location}",
            "schema": self._generate_schema_markup(business, primary_trade, location)
        }
    
    def _generate_schema_markup(
        self, 
        business: Business, 
        primary_trade: str,
        location: str
    ) -> Dict:
        """Generate JSON-LD schema for local business"""
        
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business.name,
            "description": f"{primary_trade.title()} services in {location}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business.business_address,
                "addressLocality": location
            },
            "telephone": business.phone_number,
            "email": business.business_email,
            "url": business.website,
            "areaServed": business.service_areas,
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": f"{primary_trade.title()} Services",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": trade.title()
                        }
                    } for trade in business.get_all_trades()
                ]
            }
        }
```

## Phase 3: Website Builder Engine (Week 3-4)

### 3.0 Domain Registration Service
```python
# backend/app/infrastructure/external_services/domain_registration_service.py
import aiohttp
from typing import Dict, List, Optional
from decimal import Decimal

class DomainRegistrationService:
    """
    Domain registration using Cloudflare Registrar
    - At-cost pricing (no markup)
    - Free WHOIS privacy
    - Automatic SSL
    - Built-in CDN and DDoS protection
    - Simple API
    """
    
    def __init__(self):
        self.cloudflare = CloudflareAPI(
            api_token=settings.CLOUDFLARE_API_TOKEN,
            account_id=settings.CLOUDFLARE_ACCOUNT_ID
        )
        self.base_url = "https://api.cloudflare.com/client/v4"
    
    async def search_domains(
        self,
        business: Business,
        location: str
    ) -> List[Dict]:
        """Generate and check domain suggestions based on business trades"""
        
        # Get business trade information
        primary_trade = business.get_primary_trade()
        all_trades = business.get_all_trades()
        
        # Generate smart suggestions using business and trade info
        suggestions = self._generate_domain_suggestions(
            business_name=business.name,
            location=location,
            primary_trade=primary_trade,
            all_trades=all_trades,
            is_multi_trade=business.is_multi_trade_business()
        )
        
        # Check availability across all TLDs
        results = []
        for suggestion in suggestions:
            # Prioritize TLDs based on trade category
            tlds = self._get_tlds_for_trade(business.trade_category)
            
            for tld in tlds:
                domain = f"{suggestion}{tld}"
                
                # Check availability and pricing with Cloudflare
                availability = await self._check_availability(domain)
                if availability['available']:
                    price = await self._get_price(domain)
                    results.append({
                        'domain': domain,
                        'available': True,
                        'price': price['amount'],  # At-cost pricing
                        'premium': price.get('premium', False),
                        'score': self._calculate_trade_seo_score(
                            domain, 
                            primary_trade,
                            all_trades,
                            business.trade_category
                        ),
                        'recommended_for': primary_trade
                    })
        
        # Sort by SEO score and price
        results.sort(key=lambda x: (-x['score'], x['price']))
        
        return results[:20]  # Return top 20 suggestions
    
    def _get_tlds_for_trade(self, trade_category: TradeCategory) -> List[str]:
        """Get recommended TLDs based on trade category"""
        base_tlds = ['.com', '.net', '.org']
        
        if trade_category == TradeCategory.COMMERCIAL:
            return base_tlds + ['.pro', '.biz', '.services', '.contractors']
        elif trade_category == TradeCategory.RESIDENTIAL:
            return base_tlds + ['.services', '.repair', '.home', '.house']
        else:  # BOTH
            return base_tlds + ['.services', '.pro', '.contractors', '.solutions']
    
    async def register_domain(
        self,
        domain: str,
        business_id: str,
        contact_info: Dict,
        auto_renew: bool = True
    ) -> Dict:
        """Register domain with Cloudflare"""
        
        # Register with Cloudflare (at-cost pricing)
        result = await self.cloudflare.register(
            domain,
            contact_info,
            auto_renew=auto_renew
        )
        
        # Store domain registration info
        await self._store_domain_registration(
            business_id,
            domain,
            'cloudflare',
            result
        )
        
        # Auto-configure DNS for Hero365 hosting
        await self._configure_dns(domain)
        
        return {
            'domain': domain,
            'status': 'registered',
            'provider': 'cloudflare',
            'nameservers': result['nameservers'],
            'expires_at': result['expires_at'],
            'auto_renew': auto_renew
        }
    
    async def _configure_dns(self, domain: str):
        """Auto-configure DNS with Cloudflare for Hero365 hosting"""
        
        # Create DNS records
        dns_records = [
            {'type': 'A', 'name': '@', 'value': settings.HERO365_IP, 'proxied': True},
            {'type': 'A', 'name': 'www', 'value': settings.HERO365_IP, 'proxied': True},
            {'type': 'TXT', 'name': '@', 'value': f"hero365-verification={domain}", 'proxied': False}
        ]
        
        # Add DNS records with Cloudflare CDN enabled
        for record in dns_records:
            await self.cloudflare.add_dns_record(domain, record)
    
    def _calculate_trade_seo_score(
        self, 
        domain: str, 
        primary_trade: str,
        all_trades: List[str],
        trade_category: TradeCategory
    ) -> int:
        """Calculate SEO value of domain based on trades"""
        
        score = 100
        
        # Prefer .com
        if domain.endswith('.com'):
            score += 20
        elif domain.endswith('.services') or domain.endswith('.pro'):
            score += 15  # Good for service businesses
        
        # Shorter is better
        domain_length = len(domain.split('.')[0])  # Without TLD
        if domain_length < 15:
            score += 15
        elif domain_length > 25:
            score -= 10
        
        # Contains primary trade keyword (highest value)
        if primary_trade.lower() in domain.lower():
            score += 30
        # Contains any trade keyword
        elif any(trade.lower() in domain.lower() for trade in all_trades):
            score += 20
        
        # Trade category specific scoring
        if trade_category == TradeCategory.COMMERCIAL:
            if any(word in domain.lower() for word in ['commercial', 'pro', 'business']):
                score += 10
        elif trade_category == TradeCategory.RESIDENTIAL:
            if any(word in domain.lower() for word in ['home', 'house', 'residential']):
                score += 10
        
        # No hyphens is better
        if '-' not in domain:
            score += 10
        elif domain.count('-') == 1:
            score += 5  # One hyphen is acceptable
        
        # Easy to spell/remember
        if domain.replace('.', '').replace('-', '').isalpha():
            score += 10
        
        # Exact match bonus
        if domain.split('.')[0].lower() == primary_trade.lower():
            score += 25
        
        return min(score, 100)
```

### 3.1 Static Site Generator
```python
# backend/app/application/services/website_builder_service.py
import subprocess
from pathlib import Path
import json

class WebsiteBuilderService:
    def __init__(self, template_path: str, output_path: str):
        self.template_path = Path(template_path)
        self.output_path = Path(output_path)
    
    async def build_website(
        self,
        website: BusinessWebsite,
        content: Dict
    ) -> str:
        """Build static website using Next.js"""
        
        # 1. Prepare build directory
        build_dir = self.output_path / str(website.id)
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Generate pages from template
        await self._generate_pages(website, content, build_dir)
        
        # 3. Copy Next.js template
        await self._copy_template(website.template_id, build_dir)
        
        # 4. Inject content and configuration
        await self._inject_content(content, build_dir)
        
        # 5. Run Next.js build
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise BuildError(f"Build failed: {result.stderr}")
        
        # 6. Export static files
        subprocess.run(
            ["npm", "run", "export"],
            cwd=build_dir,
            check=True
        )
        
        return str(build_dir / "out")
    
    async def validate_build(self, build_path: str) -> Dict:
        """Run Lighthouse and SEO checks"""
        # Implementation
        pass
```

### 3.2 Deployment Service
```python
# backend/app/infrastructure/external_services/aws_deployment_service.py
import boto3
from typing import Dict

class AWSDeploymentService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.cloudfront = boto3.client('cloudfront')
        self.acm = boto3.client('acm')
        self.route53 = boto3.client('route53')
    
    async def deploy_website(
        self,
        website_id: str,
        build_path: str,
        domain: str
    ) -> Dict:
        """Deploy website to S3 + CloudFront"""
        
        # 1. Create/update S3 bucket
        bucket_name = f"hero365-site-{website_id}"
        await self._ensure_s3_bucket(bucket_name)
        
        # 2. Upload build files
        await self._upload_to_s3(build_path, bucket_name)
        
        # 3. Request SSL certificate
        cert_arn = await self._ensure_ssl_certificate(domain)
        
        # 4. Create/update CloudFront distribution
        distribution = await self._ensure_cloudfront_distribution(
            bucket_name,
            domain,
            cert_arn
        )
        
        # 5. Configure DNS
        await self._configure_dns(domain, distribution['DomainName'])
        
        return {
            'bucket': bucket_name,
            'distribution_id': distribution['Id'],
            'domain': domain,
            'url': f"https://{domain}"
        }
    
    async def _ensure_ssl_certificate(self, domain: str) -> str:
        """Request and validate ACM certificate"""
        # Implementation
        pass
```

## Phase 4: Google Business Profile Integration (Week 4-5)

### 4.1 Google API Service
```python
# backend/app/infrastructure/external_services/google_business_service.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleBusinessService:
    def __init__(self, credentials: Credentials):
        self.service = build('mybusinessbusinessinformation', 'v1', 
                           credentials=credentials)
        self.gmb_service = build('mybusinessaccountmanagement', 'v1',
                               credentials=credentials)
    
    async def sync_business_info(
        self,
        account_id: str,
        business_data: Dict
    ) -> Dict:
        """Sync business info to Google Business Profile"""
        
        location = {
            'title': business_data['name'],
            'address': business_data['address'],
            'primaryPhone': business_data['phone'],
            'websiteUri': business_data['website'],
            'regularHours': business_data['hours'],
            'categories': business_data['categories']
        }
        
        response = self.service.locations().patch(
            name=f"accounts/{account_id}/locations/{location_id}",
            body=location
        ).execute()
        
        return response
    
    async def fetch_insights(
        self,
        account_id: str,
        location_id: str
    ) -> Dict:
        """Fetch performance insights"""
        # Implementation
        pass
    
    async def manage_reviews(
        self,
        account_id: str,
        location_id: str
    ) -> List[Dict]:
        """Fetch and respond to reviews"""
        # Implementation
        pass
```

### 4.2 Review Automation
```python
# backend/app/application/use_cases/seo/review_automation_use_case.py
class ReviewAutomationUseCase:
    def __init__(
        self,
        google_service: GoogleBusinessService,
        sms_service: SMSServicePort,
        ai_service: ContentGeneratorService
    ):
        self.google = google_service
        self.sms = sms_service
        self.ai = ai_service
    
    async def request_review_after_job(
        self,
        job: Job,
        contact: Contact
    ) -> None:
        """Send personalized review request"""
        
        # Generate personalized message
        message = await self.ai.generate_review_request(
            business_name=job.business.name,
            service=job.service_type,
            customer_name=contact.name
        )
        
        # Add review link
        review_link = f"https://g.page/r/{job.business.google_place_id}/review"
        message += f"\n\nLeave a review: {review_link}"
        
        # Send SMS
        await self.sms.send(contact.phone, message)
    
    async def respond_to_review(
        self,
        review: Dict,
        business: Business
    ) -> str:
        """Generate and post AI response"""
        
        # Generate response
        response = await self.ai.generate_review_response(
            review_text=review['text'],
            rating=review['rating'],
            business_context=business
        )
        
        # Post response
        await self.google.post_review_response(
            review['id'],
            response
        )
        
        return response
```

## Phase 5: SEO Optimization Engine (Week 5-6)

### 5.1 Keyword Research Service
```python
# backend/app/application/services/keyword_research_service.py
import aiohttp
from typing import List, Dict

class KeywordResearchService:
    def __init__(self, serpapi_key: str):
        self.api_key = serpapi_key
    
    async def analyze_competitors(
        self,
        business_type: str,
        location: str
    ) -> Dict:
        """Analyze competitor keywords and rankings"""
        
        # Search for top competitors
        competitors = await self._find_local_competitors(
            business_type,
            location
        )
        
        # Analyze their content
        keywords = []
        for competitor in competitors:
            site_keywords = await self._extract_keywords(
                competitor['url']
            )
            keywords.extend(site_keywords)
        
        # Get search volumes
        keyword_data = await self._get_search_volumes(
            keywords,
            location
        )
        
        return {
            'competitors': competitors,
            'keywords': keyword_data,
            'recommendations': self._generate_recommendations(keyword_data)
        }
    
    async def track_rankings(
        self,
        domain: str,
        keywords: List[str],
        location: Dict
    ) -> List[Dict]:
        """Track keyword rankings in search results"""
        # Implementation
        pass
```

### 5.2 Local Rank Tracker
```python
# backend/app/application/services/rank_tracking_service.py
class RankTrackingService:
    def __init__(self, google_service, storage_service):
        self.google = google_service
        self.storage = storage_service
    
    async def check_local_rankings(
        self,
        business: Business,
        keywords: List[str]
    ) -> Dict:
        """Check rankings in local pack and organic results"""
        
        results = {}
        
        for keyword in keywords:
            # Check multiple locations
            locations = self._get_grid_points(
                business.latitude,
                business.longitude,
                radius_miles=5
            )
            
            rankings = []
            for lat, lng in locations:
                rank = await self._check_rank_at_location(
                    keyword,
                    business.name,
                    lat,
                    lng
                )
                rankings.append({
                    'location': (lat, lng),
                    'rank': rank
                })
            
            results[keyword] = {
                'average_rank': sum(r['rank'] for r in rankings) / len(rankings),
                'rankings': rankings
            }
        
        # Store results
        await self.storage.save_ranking_snapshot(
            business.id,
            results
        )
        
        return results
```

## Phase 6: API Endpoints (Week 6)

### 6.1 Website Management API
```python
# backend/app/api/routes/websites.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/websites", tags=["websites"])

@router.post("/domains/search")
async def search_domains(
    request: DomainSearchRequest,
    business_id: UUID = Depends(get_current_business),
    domain_service: DomainRegistrationService = Depends()
):
    """Search for available domains with trade-based SEO scoring"""
    
    business = await get_business(business_id)
    
    # Use business trades for domain generation
    if not business.get_all_trades():
        raise HTTPException(
            status_code=400,
            detail="Business must have at least one trade specified for domain suggestions"
        )
    
    # Generate and check domain suggestions based on trades
    suggestions = await domain_service.search_domains(
        business=business,
        location=request.location or business.city
    )
    
    # Group suggestions by trade relevance
    primary_trade = business.get_primary_trade()
    primary_suggestions = [s for s in suggestions if s['recommended_for'] == primary_trade]
    other_suggestions = [s for s in suggestions if s['recommended_for'] != primary_trade]
    
    return {
        "primary_suggestions": primary_suggestions[:10],
        "other_suggestions": other_suggestions[:10],
        "recommended": primary_suggestions[0] if primary_suggestions else suggestions[0] if suggestions else None,
        "business_trades": business.get_all_trades()
    }

@router.post("/domains/register")
async def register_domain(
    request: DomainRegistrationRequest,
    business_id: UUID = Depends(get_current_business),
    domain_service: DomainRegistrationService = Depends()
):
    """One-click domain registration"""
    
    business = await get_business(business_id)
    
    # Prepare contact info from business data
    contact_info = {
        "name": business.owner_name,
        "email": business.email,
        "phone": business.phone,
        "address": business.address,
        "city": business.city,
        "state": business.state,
        "postal_code": business.postal_code,
        "country": business.country
    }
    
    # Register domain
    result = await domain_service.register_domain(
        domain=request.domain,
        business_id=business_id,
        contact_info=contact_info,
        auto_renew=request.auto_renew
    )
    
    # Update website record with domain
    await update_website_domain(business_id, request.domain)
    
    return DomainRegistrationResponse(
        domain=result['domain'],
        status=result['status'],
        provider=result['provider'],
        expires_at=result['expires_at'],
        dns_configured=True
    )

@router.post("/")
async def create_website(
    request: CreateWebsiteRequest,
    business_id: UUID = Depends(get_current_business),
    builder_service: WebsiteBuilderService = Depends(),
    content_service: ContentGeneratorService = Depends()
):
    """Create a new website based on business trades"""
    
    business = await get_business(business_id)
    
    # Validate business has trades
    if not business.get_all_trades():
        raise HTTPException(
            status_code=400,
            detail="Business must have at least one trade specified"
        )
    
    # Auto-select template based on business trades
    primary_trade = business.get_primary_trade()
    template = await get_template_for_trade(
        primary_trade,
        business.trade_category,
        is_multi_trade=business.is_multi_trade_business()
    )
    
    if not template:
        # Fallback to multi-trade template
        template = await get_multi_trade_template()
    
    # Generate trade-specific content
    content = await content_service.generate_page_content(
        template=template,
        business=business,
        page_type="full_site"
    )
    
    # Create website record with trade information
    website = await create_website_record(
        business_id=business_id,
        template_id=template.id,
        content=content,
        primary_trade=primary_trade,
        secondary_trades=business.get_all_trades()[1:] if len(business.get_all_trades()) > 1 else [],
        service_areas=business.service_areas
    )
    
    # Trigger build job
    await queue_build_job(website.id)
    
    return WebsiteResponse(
        id=website.id,
        status="building",
        preview_url=f"/preview/{website.id}",
        template_name=template.name,
        primary_trade=primary_trade,
        seo_keywords=business.get_seo_keywords()[:5]  # Top 5 keywords
    )

@router.post("/{website_id}/publish")
async def publish_website(
    website_id: UUID,
    domain: str,
    deployment_service: AWSDeploymentService = Depends()
):
    """Deploy website to production"""
    
    website = await get_website(website_id)
    
    if website.status != "built":
        raise HTTPException(400, "Website must be built first")
    
    # Deploy to AWS
    deployment = await deployment_service.deploy_website(
        website_id,
        website.build_path,
        domain
    )
    
    # Update website record
    await update_website(
        website_id,
        status="deployed",
        domain=domain,
        deployment_info=deployment
    )
    
    return {
        "status": "deployed",
        "url": deployment['url']
    }

@router.get("/{website_id}/analytics")
async def get_website_analytics(
    website_id: UUID,
    date_from: date,
    date_to: date
):
    """Get website performance metrics"""
    # Implementation
    pass
```

### 6.2 Google Business Profile API
```python
# backend/app/api/routes/google_profile.py
@router.post("/google/connect")
async def connect_google_account(
    auth_code: str,
    business_id: UUID = Depends(get_current_business)
):
    """Connect Google Business Profile"""
    
    # Exchange auth code for tokens
    credentials = await exchange_auth_code(auth_code)
    
    # Store encrypted tokens
    await store_google_credentials(business_id, credentials)
    
    # Fetch and sync initial data
    profile = await sync_google_profile(business_id)
    
    return profile

@router.get("/google/insights")
async def get_google_insights(
    business_id: UUID = Depends(get_current_business),
    date_range: str = "LAST_30_DAYS"
):
    """Get Google Business Profile insights"""
    # Implementation
    pass

@router.post("/google/reviews/{review_id}/reply")
async def reply_to_review(
    review_id: str,
    reply: ReviewReplyRequest,
    ai_generated: bool = True
):
    """Reply to a Google review"""
    # Implementation
    pass
```

## Phase 7: Mobile App Integration (Week 7)

### 7.1 Swift API Client Updates
```swift
// iOS/Hero365/Services/WebsiteService.swift
class WebsiteService {
    func searchDomains(
        businessName: String,
        location: String,
        tradeType: String
    ) async throws -> DomainSuggestions {
        // API call to search domains
    }
    
    func registerDomain(
        domain: String,
        autoRenew: Bool = true
    ) async throws -> DomainRegistration {
        // One-click domain registration
    }
    
    func createWebsite(
        tradeType: String,
        template: WebsiteTemplate
    ) async throws -> Website {
        // API call implementation
    }
    
    func customizeWebsite(
        websiteId: UUID,
        theme: ThemeConfig,
        content: ContentOverrides
    ) async throws -> Website {
        // API call implementation
    }
    
    func publishWebsite(
        websiteId: UUID,
        domain: String
    ) async throws -> DeploymentInfo {
        // API call implementation
    }
}
```

### 7.2 Website Builder UI
```swift
// iOS/Hero365/Views/WebsiteBuilder/WebsiteBuilderView.swift
struct WebsiteBuilderView: View {
    @StateObject var viewModel: WebsiteBuilderViewModel
    @State private var showDomainPicker = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Template selection
                TemplatePickerView(
                    templates: viewModel.templates,
                    selected: $viewModel.selectedTemplate
                )
                
                // Domain selection with one-click purchase
                DomainSelectionCard(
                    domain: viewModel.selectedDomain,
                    onTap: { showDomainPicker = true }
                )
                
                // Live preview
                WebsitePreviewView(
                    website: viewModel.website
                )
                
                // Customization controls
                CustomizationPanel(
                    theme: $viewModel.theme,
                    content: $viewModel.content
                )
                
                // Publish button
                Button("Publish Website") {
                    viewModel.publishWebsite()
                }
                .buttonStyle(PrimaryButtonStyle())
                .disabled(viewModel.selectedDomain == nil)
            }
        }
        .sheet(isPresented: $showDomainPicker) {
            DomainPickerView(viewModel: viewModel)
        }
    }
}

// iOS/Hero365/Views/WebsiteBuilder/DomainPickerView.swift
struct DomainPickerView: View {
    @ObservedObject var viewModel: WebsiteBuilderViewModel
    @State private var searchText = ""
    @State private var isSearching = false
    @State private var domainSuggestions: [DomainSuggestion] = []
    
    var body: some View {
        NavigationView {
            VStack {
                // Search bar
                HStack {
                    TextField("Search for your perfect domain", text: $searchText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onSubmit {
                            searchDomains()
                        }
                    
                    Button("Search") {
                        searchDomains()
                    }
                }
                .padding()
                
                if isSearching {
                    ProgressView("Finding available domains...")
                        .padding()
                } else {
                    // Domain suggestions with SEO scores
                    List(domainSuggestions) { suggestion in
                        DomainSuggestionRow(
                            suggestion: suggestion,
                            onRegister: {
                                registerDomain(suggestion)
                            }
                        )
                    }
                }
                
                // Free subdomain option
                VStack(alignment: .leading) {
                    Text("Or use a free Hero365 subdomain:")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    HStack {
                        Text("\(viewModel.businessName.lowercased()).hero365.ai")
                            .font(.system(.body, design: .monospaced))
                        
                        Spacer()
                        
                        Button("Use Free") {
                            viewModel.selectedDomain = "\(viewModel.businessName.lowercased()).hero365.ai"
                            dismiss()
                        }
                        .buttonStyle(SecondaryButtonStyle())
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                }
                .padding()
            }
            .navigationTitle("Choose Your Domain")
            .navigationBarItems(trailing: Button("Cancel") { dismiss() })
        }
    }
    
    func searchDomains() {
        isSearching = true
        Task {
            do {
                let suggestions = try await viewModel.searchDomains(searchText)
                domainSuggestions = suggestions
                isSearching = false
            } catch {
                // Handle error
                isSearching = false
            }
        }
    }
    
    func registerDomain(_ suggestion: DomainSuggestion) {
        Task {
            do {
                let registration = try await viewModel.registerDomain(suggestion.domain)
                viewModel.selectedDomain = suggestion.domain
                dismiss()
            } catch {
                // Handle error
            }
        }
    }
}

struct DomainSuggestionRow: View {
    let suggestion: DomainSuggestion
    let onRegister: () -> Void
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(suggestion.domain)
                    .font(.system(.body, design: .monospaced))
                
                HStack {
                    // SEO score indicator
                    Label("\(suggestion.seoScore)/100", systemImage: "chart.line.uptrend.xyaxis")
                        .font(.caption)
                        .foregroundColor(seoScoreColor)
                    
                    if suggestion.premium {
                        Label("Premium", systemImage: "star.fill")
                            .font(.caption)
                            .foregroundColor(.orange)
                    }
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing) {
                Text("$\(suggestion.price, specifier: "%.2f")/year")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                
                Button("Register") {
                    onRegister()
                }
                .buttonStyle(SmallPrimaryButtonStyle())
            }
        }
        .padding(.vertical, 4)
    }
    
    var seoScoreColor: Color {
        if suggestion.seoScore >= 80 {
            return .green
        } else if suggestion.seoScore >= 60 {
            return .orange
        } else {
            return .red
        }
    }
}
```

## Phase 8: Background Jobs (Week 7-8)

### 8.1 Celery Tasks
```python
# backend/app/workers/website_tasks.py
from celery import Celery

app = Celery('hero365', broker=settings.REDIS_URL)

@app.task
def build_website_task(website_id: str):
    """Build static website"""
    
    # Get website data
    website = get_website(website_id)
    
    # Generate content
    content = generate_all_content(website)
    
    # Build site
    build_path = build_static_site(website, content)
    
    # Run tests
    test_results = run_lighthouse_tests(build_path)
    
    if test_results['score'] < 90:
        optimize_build(build_path)
    
    # Update status
    update_website_status(website_id, 'built')
    
    return build_path

@app.task
def sync_google_profile_task(business_id: str):
    """Sync with Google Business Profile"""
    # Implementation
    pass

@app.task
def track_rankings_task():
    """Daily ranking check for all websites"""
    # Implementation
    pass
```

## Phase 9: Testing & Optimization (Week 8-9)

### 9.1 Integration Tests
```python
# backend/app/tests/test_website_builder.py
import pytest
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_website_creation_flow():
    """Test complete website creation flow"""
    
    # Create business
    business = await create_test_business()
    
    # Select template
    template = await get_template('plumbing', 'commercial')
    
    # Create website
    website = await create_website(
        business_id=business.id,
        template_id=template.id
    )
    
    assert website.status == 'draft'
    
    # Generate content
    content = await generate_content(website)
    assert 'pages' in content
    
    # Build website
    build_path = await build_website(website, content)
    assert Path(build_path).exists()
    
    # Validate SEO
    seo_score = await validate_seo(build_path)
    assert seo_score >= 90

@pytest.mark.asyncio
async def test_google_sync():
    """Test Google Business Profile sync"""
    # Implementation
    pass
```

### 9.2 Performance Tests
```python
# backend/app/tests/test_performance.py
@pytest.mark.benchmark
async def test_build_performance():
    """Ensure builds complete within SLA"""
    
    start = time.time()
    
    website = await create_test_website()
    await build_website_task(website.id)
    
    duration = time.time() - start
    
    assert duration < 60  # Should complete in under 1 minute

@pytest.mark.benchmark  
async def test_concurrent_builds():
    """Test multiple concurrent builds"""
    # Implementation
    pass
```

## Phase 9.5: Trade-Specific Template Generation (Week 9)

### 9.5.1 Template Factory Service
```python
# backend/app/application/services/template_factory_service.py
from typing import Dict, Optional
from app.domain.entities.business import Business, TradeCategory, CommercialTrade, ResidentialTrade

class TemplateFactoryService:
    """Factory for creating trade-specific website templates"""
    
    def __init__(self):
        self.commercial_templates = self._load_commercial_templates()
        self.residential_templates = self._load_residential_templates()
    
    def _load_commercial_templates(self) -> Dict:
        """Load all commercial trade templates"""
        return {
            CommercialTrade.MECHANICAL: "mechanical_commercial.json",
            CommercialTrade.REFRIGERATION: "refrigeration_commercial.json",
            CommercialTrade.PLUMBING: "plumbing_commercial.json",
            CommercialTrade.ELECTRICAL: "electrical_commercial.json",
            CommercialTrade.SECURITY_SYSTEMS: "security_commercial.json",
            CommercialTrade.LANDSCAPING: "landscaping_commercial.json",
            CommercialTrade.ROOFING: "roofing_commercial.json",
            CommercialTrade.KITCHEN_EQUIPMENT: "kitchen_equipment_commercial.json",
            CommercialTrade.WATER_TREATMENT: "water_treatment_commercial.json",
            CommercialTrade.POOL_SPA: "pool_spa_commercial.json"
        }
    
    def _load_residential_templates(self) -> Dict:
        """Load all residential trade templates"""
        return {
            ResidentialTrade.HVAC: "hvac_residential.json",
            ResidentialTrade.PLUMBING: "plumbing_residential.json",
            ResidentialTrade.ELECTRICAL: "electrical_residential.json",
            ResidentialTrade.CHIMNEY: "chimney_residential.json",
            ResidentialTrade.ROOFING: "roofing_residential.json",
            ResidentialTrade.GARAGE_DOOR: "garage_door_residential.json",
            ResidentialTrade.SEPTIC: "septic_residential.json",
            ResidentialTrade.PEST_CONTROL: "pest_control_residential.json",
            ResidentialTrade.IRRIGATION: "irrigation_residential.json",
            ResidentialTrade.PAINTING: "painting_residential.json"
        }
    
    async def get_template_for_business(
        self, 
        business: Business
    ) -> Optional[WebsiteTemplate]:
        """Get the best template for a business based on trades"""
        
        primary_trade = business.get_primary_trade()
        
        if business.is_multi_trade_business():
            # Use multi-trade template
            return await self._get_multi_trade_template(business)
        
        # Single trade - get specific template
        if business.trade_category == TradeCategory.COMMERCIAL:
            for trade in business.commercial_trades:
                if trade.value == primary_trade:
                    return await self._load_template(
                        self.commercial_templates.get(trade)
                    )
        
        elif business.trade_category == TradeCategory.RESIDENTIAL:
            for trade in business.residential_trades:
                if trade.value == primary_trade:
                    return await self._load_template(
                        self.residential_templates.get(trade)
                    )
        
        # Both categories - check both
        else:
            # Check commercial first
            for trade in business.commercial_trades:
                if trade.value == primary_trade:
                    return await self._load_template(
                        self.commercial_templates.get(trade)
                    )
            # Then residential
            for trade in business.residential_trades:
                if trade.value == primary_trade:
                    return await self._load_template(
                        self.residential_templates.get(trade)
                    )
        
        return None
    
    async def _get_multi_trade_template(
        self,
        business: Business
    ) -> WebsiteTemplate:
        """Create dynamic multi-trade template"""
        
        all_trades = business.get_all_trades()
        primary_trade = business.get_primary_trade()
        
        template = WebsiteTemplate(
            id=uuid.uuid4(),
            trade_type=primary_trade,
            trade_category=business.trade_category or TradeCategory.BOTH,
            name=f"Multi-Service {business.trade_category.value if business.trade_category else 'Professional'}",
            is_multi_trade=True,
            supported_trades=all_trades,
            structure={
                "pages": [
                    {
                        "path": "/",
                        "sections": [
                            {"type": "hero", "focus": primary_trade},
                            {"type": "multi-service-grid", "trades": all_trades},
                            {"type": "why-choose-us"},
                            {"type": "service-areas", "areas": business.service_areas}
                        ]
                    },
                    # Dynamic service pages for each trade
                    *[
                        {
                            "path": f"/services/{trade.lower().replace(' ', '-')}",
                            "trade": trade,
                            "sections": [
                                {"type": "service-hero", "trade": trade},
                                {"type": "service-details"},
                                {"type": "pricing"},
                                {"type": "cta"}
                            ]
                        } for trade in all_trades
                    ]
                ]
            },
            seo_config={
                "primary_keywords": business.get_seo_keywords(),
                "schema_types": ["LocalBusiness", "ProfessionalService"] + 
                               [f"{trade.title()}Service" for trade in all_trades[:3]]
            }
        )
        
        return template
```

### 9.5.2 Template Seed Data
```sql
-- Seed commercial trade templates
INSERT INTO website_templates (trade_type, trade_category, name, structure, seo_config)
VALUES 
    ('mechanical', 'COMMERCIAL', 'Commercial Mechanical Services', '{}', '{}'),
    ('refrigeration', 'COMMERCIAL', 'Commercial Refrigeration Experts', '{}', '{}'),
    ('plumbing', 'COMMERCIAL', 'Commercial Plumbing Solutions', '{}', '{}'),
    ('electrical', 'COMMERCIAL', 'Commercial Electrical Contractors', '{}', '{}'),
    ('security_systems', 'COMMERCIAL', 'Business Security Systems', '{}', '{}'),
    ('landscaping', 'COMMERCIAL', 'Commercial Landscaping Services', '{}', '{}'),
    ('roofing', 'COMMERCIAL', 'Commercial Roofing Specialists', '{}', '{}'),
    ('kitchen_equipment', 'COMMERCIAL', 'Commercial Kitchen Equipment', '{}', '{}'),
    ('water_treatment', 'COMMERCIAL', 'Industrial Water Treatment', '{}', '{}'),
    ('pool_spa', 'COMMERCIAL', 'Commercial Pool & Spa Services', '{}', '{}');

-- Seed residential trade templates  
INSERT INTO website_templates (trade_type, trade_category, name, structure, seo_config)
VALUES
    ('hvac', 'RESIDENTIAL', 'Home HVAC Services', '{}', '{}'),
    ('plumbing', 'RESIDENTIAL', 'Residential Plumbing Experts', '{}', '{}'),
    ('electrical', 'RESIDENTIAL', 'Home Electrical Services', '{}', '{}'),
    ('chimney', 'RESIDENTIAL', 'Chimney Cleaning & Repair', '{}', '{}'),
    ('roofing', 'RESIDENTIAL', 'Residential Roofing Services', '{}', '{}'),
    ('garage_door', 'RESIDENTIAL', 'Garage Door Repair & Installation', '{}', '{}'),
    ('septic', 'RESIDENTIAL', 'Septic System Services', '{}', '{}'),
    ('pest_control', 'RESIDENTIAL', 'Pest Control Solutions', '{}', '{}'),
    ('irrigation', 'RESIDENTIAL', 'Lawn Irrigation Systems', '{}', '{}'),
    ('painting', 'RESIDENTIAL', 'Professional Painting Services', '{}', '{}');

-- Multi-trade template
INSERT INTO website_templates (trade_type, trade_category, name, is_multi_trade, structure, seo_config)
VALUES
    ('multi', 'BOTH', 'Multi-Service Professional', true, '{}', '{}');
```

## Phase 10: Production Deployment (Week 9-10)

### 10.1 Infrastructure Setup
```bash
# aws/deploy-website-builder.sh
#!/bin/bash

# Create S3 buckets for website hosting
aws s3api create-bucket \
  --bucket hero365-websites \
  --region us-east-1

# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# Setup Route53 hosted zone
aws route53 create-hosted-zone \
  --name hero365sites.com \
  --caller-reference $(date +%s)

# Deploy Lambda functions for SSL automation
aws lambda create-function \
  --function-name ssl-certificate-manager \
  --runtime python3.9 \
  --handler ssl_manager.handler \
  --role arn:aws:iam::account:role/lambda-role
```

### 10.2 Environment Configuration
```env
# environments/.env
# Website Builder Configuration
WEBSITE_BUILDER_ENABLED=true
WEBSITE_TEMPLATE_PATH=/app/website-templates
WEBSITE_BUILD_PATH=/tmp/website-builds
WEBSITE_DEPLOY_BUCKET=hero365-websites

# Cloudflare Domain Registration & CDN
CLOUDFLARE_API_TOKEN=xxx
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_ZONE_ID=xxx

# Google APIs
GOOGLE_BUSINESS_CLIENT_ID=xxx
GOOGLE_BUSINESS_CLIENT_SECRET=xxx
GOOGLE_SEARCH_CONSOLE_API_KEY=xxx

# AWS Configuration
AWS_REGION=us-east-1
AWS_CLOUDFRONT_DISTRIBUTION=xxx
AWS_CERTIFICATE_MANAGER_ARN=xxx
HERO365_IP=xxx.xxx.xxx.xxx

# SEO Services
SERPAPI_KEY=xxx
AHREFS_API_KEY=xxx
SEMRUSH_API_KEY=xxx

# Content Generation
OPENAI_MODEL_CONTENT=gpt-4
CONTENT_GENERATION_TEMPERATURE=0.7
```

### 10.3 Monitoring & Alerts
```python
# backend/app/monitoring/website_monitoring.py
from datadog import initialize, statsd

class WebsiteMonitoring:
    def __init__(self):
        initialize(api_key=settings.DATADOG_API_KEY)
    
    def track_build(self, website_id: str, duration: float, success: bool):
        """Track website build metrics"""
        statsd.histogram('website.build.duration', duration)
        statsd.increment('website.build.total')
        
        if success:
            statsd.increment('website.build.success')
        else:
            statsd.increment('website.build.failure')
    
    def track_deployment(self, website_id: str, domain: str):
        """Track deployment metrics"""
        statsd.increment('website.deployment.total')
        statsd.gauge('website.deployment.active', 1, tags=[f"domain:{domain}"])
    
    def track_seo_score(self, website_id: str, scores: Dict):
        """Track SEO performance"""
        for metric, value in scores.items():
            statsd.gauge(f'website.seo.{metric}', value, tags=[f"website:{website_id}"])
```

## Migration Script
```python
# backend/app/scripts/generate_client.sh
#!/bin/bash

# Generate OpenAPI spec
python -m app.main generate-openapi > openapi.json

# Generate TypeScript client
npx openapi-typescript openapi.json -o frontend/src/api/types.ts

# Generate Swift client  
openapi-generator generate \
  -i openapi.json \
  -g swift5 \
  -o ios/Hero365/API

echo "API clients generated successfully"
```

## Success Metrics

### Technical KPIs
- Website build time < 60 seconds
- Lighthouse score > 90
- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- 99.9% uptime for deployed sites
- < 5 minute deployment time
- Domain registration completion < 2 minutes
- DNS propagation < 30 minutes

### Business KPIs
- 80% of professionals activate website feature
- 60% purchase custom domain (vs free subdomain)
- 50% improvement in Google rankings within 3 months
- 30% increase in lead generation
- 25% reduction in customer acquisition cost
- Average domain SEO score > 75/100

## Risk Mitigation

### Technical Risks
1. **Build failures**: Implement retry logic, fallback templates
2. **SSL certificate issues**: Automate renewal, monitor expiration
3. **Google API limits**: Implement rate limiting, caching
4. **Content quality**: Human review queue for AI content

### Business Risks
1. **Domain disputes**: Clear terms of service, verification process
2. **Content liability**: Disclaimer, moderation system
3. **SEO penalties**: Follow Google guidelines, avoid over-optimization
4. **Competitive response**: Continuous innovation, feature differentiation

## Timeline Summary

- **Week 1-2**: Database schema, domain entities with Pydantic v2, repositories (including domain registration tables)
- **Week 2-3**: Trade-specific template system (20 templates for Commercial/Residential trades), AI content generation, domain registration service with Cloudflare
- **Week 3-4**: Website builder engine with trade-aware content, deployment service with auto-DNS configuration
- **Week 4-5**: Google Business Profile integration with trade-specific optimization
- **Week 5-6**: SEO optimization engine with trade-based domain scoring
- **Week 6-7**: API endpoints with trade validation, mobile integration with domain picker UI
- **Week 7-8**: Background jobs, testing for all trade combinations
- **Week 8-9**: Performance optimization, multi-trade template generation
- **Week 9**: Trade-specific template factory and seed data creation
- **Week 9-10**: Production deployment, monitoring, trade-based analytics

## Key Updates from Latest Business Entity Changes

1. **Unified Business Branding System** ✨ **NEW**:
   - Centralized `BusinessBranding` entity manages brand identity across ALL components
   - Single source of truth for colors, fonts, logos shared by websites, estimates, invoices, emails
   - Trade-specific theme suggestions (e.g., industrial colors for commercial, friendly for residential)
   - Auto-generates CSS variables for web components
   - Export to design tools (Figma, Sketch) for consistent design workflows
   - Eliminates duplication between EstimateTemplate, InvoiceTemplate, and WebsiteTemplate branding

2. **Trade-Based Architecture**: 
   - Removed `BusinessType` enum in favor of explicit trade classifications
   - Business entity now uses `CommercialTrade` (10 trades) and `ResidentialTrade` (10 trades) enums
   - Support for multi-trade businesses with primary and secondary trade identification

3. **Pydantic v2 Migration**:
   - Business entity migrated from dataclass to Pydantic BaseModel
   - Enhanced validation with field and model validators
   - Immutable operations pattern for better data integrity

4. **Template System Enhancement**:
   - 20 pre-built templates (10 commercial, 10 residential)
   - Dynamic multi-trade template generation
   - Trade-specific SEO optimization and content generation
   - Templates now reference centralized `BusinessBranding` instead of duplicating brand settings

5. **Domain Registration Improvements**:
   - Trade-aware domain suggestions and SEO scoring
   - TLD recommendations based on trade category
   - Primary trade focus for domain naming

6. **Database Schema Updates**:
   - Added `business_branding` table for centralized brand management
   - Added trade_category, commercial_trades, residential_trades columns to businesses
   - Service areas support for geographic targeting
   - Constraint ensuring at least one trade is specified
   - Foreign key references from templates to business_branding

## Next Steps

1. Review and approve updated implementation plan
2. Complete Business entity migration across all repositories and use cases
3. Set up development environment with trade templates
4. Create Jira epics for each trade template
5. Begin Phase 1 implementation with trade-aware architecture
6. Schedule weekly progress reviews with trade-specific milestones
