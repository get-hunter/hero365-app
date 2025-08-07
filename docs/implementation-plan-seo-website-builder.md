# SEO Website Builder Implementation Plan

## Executive Summary
Build an AI-powered website generation and SEO optimization platform that automatically creates, deploys, and maintains high-performing websites for Hero365 professionals, integrated with Google Business Profile management, local SEO tools, and one-click domain registration for maximum SEO impact.

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

### 1.1 Database Schema Design
```sql
-- Website configuration and templates
CREATE TABLE website_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_type VARCHAR(50) NOT NULL, -- 'plumbing', 'electrical', etc.
    trade_category VARCHAR(20) NOT NULL, -- 'commercial' or 'residential'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    preview_url VARCHAR(500),
    structure JSONB NOT NULL, -- Page hierarchy and components
    default_content JSONB, -- AI prompts and seed content
    seo_config JSONB, -- Meta tags, schema templates
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE business_websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    template_id UUID REFERENCES website_templates(id),
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(100), -- for hero365.ai subdomains
    status VARCHAR(50) DEFAULT 'draft', -- draft, building, deployed, error
    
    -- Customization
    theme_config JSONB, -- colors, fonts, logo
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
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID

class WebsiteTemplate(BaseModel):
    id: UUID
    trade_type: str  # 'plumbing', 'electrical', etc.
    trade_category: str  # 'commercial' or 'residential'
    name: str
    description: Optional[str]
    preview_url: Optional[HttpUrl]
    structure: Dict  # Page hierarchy
    default_content: Dict
    seo_config: Dict

class BusinessWebsite(BaseModel):
    id: UUID
    business_id: UUID
    template_id: Optional[UUID]
    domain: Optional[str]
    subdomain: Optional[str]
    status: str  # draft, building, deployed
    theme_config: Dict
    content_overrides: Dict
    pages: List[Dict]
    deployment_info: Optional[Dict]
    seo_settings: Dict
    last_build_at: Optional[datetime]
    last_deploy_at: Optional[datetime]
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
```typescript
// website-builder/templates/plumbing-commercial.ts
export const plumbingCommercialTemplate = {
  trade: 'plumbing',
  category: 'commercial',
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
```

### 2.2 AI Content Generator Service
```python
# backend/app/application/services/content_generator_service.py
from typing import Dict, List
import openai

class ContentGeneratorService:
    def __init__(self, openai_client):
        self.client = openai_client
    
    async def generate_page_content(
        self,
        template: WebsiteTemplate,
        business: Business,
        page_type: str
    ) -> Dict:
        """Generate SEO-optimized content for a page"""
        
        prompt = self._build_content_prompt(template, business, page_type)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an SEO expert..."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def optimize_meta_tags(
        self,
        page_content: str,
        target_keywords: List[str],
        location: str
    ) -> Dict:
        """Generate optimized meta tags"""
        # Implementation
        pass
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
        business_name: str,
        location: str,
        trade_type: str
    ) -> List[Dict]:
        """Generate and check domain suggestions"""
        
        # Generate smart suggestions
        suggestions = self._generate_domain_suggestions(
            business_name,
            location,
            trade_type
        )
        
        # Check availability across all TLDs
        results = []
        for suggestion in suggestions:
            for tld in ['.com', '.net', '.org', '.co', '.biz', '.pro', '.services']:
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
                        'score': self._calculate_seo_score(domain, trade_type)
                    })
        
        # Sort by SEO score and price
        results.sort(key=lambda x: (-x['score'], x['price']))
        
        return results[:20]  # Return top 20 suggestions
    
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
    
    def _calculate_seo_score(self, domain: str, trade_type: str) -> int:
        """Calculate SEO value of domain"""
        
        score = 100
        
        # Prefer .com
        if domain.endswith('.com'):
            score += 20
        
        # Shorter is better
        if len(domain) < 15:
            score += 15
        elif len(domain) > 25:
            score -= 10
        
        # Contains trade keyword
        if trade_type.lower() in domain.lower():
            score += 25
        
        # No hyphens is better
        if '-' not in domain:
            score += 10
        
        # Easy to spell/remember
        if domain.replace('.', '').isalpha():
            score += 10
        
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
    """Search for available domains with SEO scoring"""
    
    business = await get_business(business_id)
    
    # Generate and check domain suggestions
    suggestions = await domain_service.search_domains(
        business_name=business.name,
        location=business.city,
        trade_type=request.trade_type
    )
    
    return {
        "suggestions": suggestions,
        "recommended": suggestions[0] if suggestions else None
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
    builder_service: WebsiteBuilderService = Depends()
):
    """Create a new website for business"""
    
    # Select template
    template = await get_template(request.trade_type)
    
    # Generate content
    content = await generate_content(business_id, template)
    
    # Create website record
    website = await create_website_record(
        business_id,
        template.id,
        content
    )
    
    # Trigger build job
    await queue_build_job(website.id)
    
    return WebsiteResponse(
        id=website.id,
        status="building",
        preview_url=f"/preview/{website.id}"
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

- **Week 1-2**: Database schema, domain entities, repositories (including domain registration tables)
- **Week 2-3**: Template system, AI content generation, domain registration service
- **Week 3-4**: Website builder engine, deployment service with auto-DNS configuration
- **Week 4-5**: Google Business Profile integration
- **Week 5-6**: SEO optimization engine with domain scoring
- **Week 6-7**: API endpoints, mobile integration with domain picker UI
- **Week 7-8**: Background jobs, testing
- **Week 8-9**: Performance optimization, security
- **Week 9-10**: Production deployment, monitoring

## Next Steps

1. Review and approve implementation plan
2. Set up development environment
3. Create Jira epics and stories
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews
