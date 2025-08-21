# Business Logic Migration Analysis

## Overview
The `external_services` folder contains significant business logic mixed with infrastructure concerns, violating Clean Architecture principles. This document analyzes the current state and provides a migration plan.

## Current Issues

### 1. **Domain Registration Service** (`domain_registration_service.py`)
**Business Logic Found:**
- SEO scoring algorithms (`_calculate_trade_seo_score`, `_calculate_brandability_score`)
- Domain suggestion generation (`_generate_domain_suggestions`)
- Trade-specific TLD recommendations (`_get_tlds_for_trade`)
- Pricing strategy logic
- Domain validation rules

**Infrastructure Concerns:**
- Cloudflare API communication
- HTTP requests and responses
- API authentication

### 2. **SEO Optimization Service** (`seo_optimization_service.py`)
**Business Logic Found:**
- Keyword research algorithms
- Competition analysis logic
- Local SEO scoring
- Content optimization recommendations
- Rank tracking interpretation
- Competitor analysis algorithms
- Schema markup generation rules

**Infrastructure Concerns:**
- SERP API integration
- Web scraping
- External SEO tool APIs (SEMrush, Ahrefs)

### 3. **AWS Deployment Service** (`aws_deployment_service.py`)
**Business Logic Found:**
- Deployment strategy selection
- Performance optimization rules
- Cache configuration logic
- Security header policies
- Error page routing rules
- SSL certificate management policies

**Infrastructure Concerns:**
- AWS S3 operations
- CloudFront configuration
- Route53 DNS management
- Certificate Manager integration

### 4. **Google Business Profile Service** (`google_business_profile_service.py`)
**Business Logic Found:**
- Profile matching algorithms
- Review sentiment analysis
- Posting strategy logic
- Insights interpretation
- Business verification workflows
- Local SEO optimization rules

**Infrastructure Concerns:**
- Google API authentication
- API request/response handling
- OAuth flow management

### 5. **Hero365 Subdomain Service** (`hero365_subdomain_service.py`)
**Business Logic Found:**
- Subdomain generation rules
- Deployment verification logic
- Cache invalidation strategies
- Health check algorithms

**Infrastructure Concerns:**
- AWS service integration
- DNS configuration
- File upload operations

## Migration Strategy

### Phase 1: Create Domain Services and Ports

#### 1.1 SEO Domain Service
```python
# backend/app/domain/services/seo_domain_service.py
class SEODomainService:
    def calculate_keyword_difficulty(self, keyword: str, competition_data: Dict) -> int
    def generate_local_keywords(self, business: Business) -> List[str]
    def calculate_seo_score(self, factors: SEOFactors) -> int
    def optimize_content_for_keywords(self, content: str, keywords: List[str]) -> str
    def generate_schema_markup(self, business: Business, page_type: str) -> Dict
```

#### 1.2 Domain Registration Domain Service
```python
# backend/app/domain/services/domain_registration_domain_service.py
class DomainRegistrationDomainService:
    def calculate_seo_score(self, domain: str, business: Business) -> int
    def generate_domain_suggestions(self, business: Business) -> List[str]
    def calculate_brandability_score(self, domain: str) -> int
    def get_recommended_tlds(self, trade: str) -> List[str]
    def validate_domain_for_business(self, domain: str, business: Business) -> ValidationResult
```

#### 1.3 Deployment Domain Service
```python
# backend/app/domain/services/deployment_domain_service.py
class DeploymentDomainService:
    def determine_deployment_strategy(self, website: BusinessWebsite) -> DeploymentStrategy
    def calculate_cache_settings(self, content_type: str) -> CacheConfig
    def generate_security_headers(self, website: BusinessWebsite) -> Dict[str, str]
    def validate_deployment_readiness(self, website: BusinessWebsite) -> ValidationResult
```

### Phase 2: Create Infrastructure Ports

#### 2.1 SEO Infrastructure Port
```python
# backend/app/application/ports/seo_research_port.py
class SEOResearchPort(ABC):
    @abstractmethod
    async def research_keywords(self, seed_keywords: List[str], location: str) -> List[KeywordData]
    
    @abstractmethod
    async def track_rankings(self, keywords: List[str], domain: str) -> List[RankingData]
    
    @abstractmethod
    async def analyze_competitors(self, domain: str, keywords: List[str]) -> List[CompetitorData]
```

#### 2.2 Domain Registration Port
```python
# backend/app/application/ports/domain_registry_port.py
class DomainRegistryPort(ABC):
    @abstractmethod
    async def check_availability(self, domain: str) -> bool
    
    @abstractmethod
    async def get_pricing(self, domain: str) -> DomainPricing
    
    @abstractmethod
    async def register_domain(self, domain: str, contact_info: ContactInfo) -> RegistrationResult
```

#### 2.3 Deployment Infrastructure Port
```python
# backend/app/application/ports/hosting_port.py
class HostingPort(ABC):
    @abstractmethod
    async def deploy_static_site(self, files: Dict[str, bytes], config: DeploymentConfig) -> DeploymentResult
    
    @abstractmethod
    async def configure_cdn(self, domain: str, config: CDNConfig) -> CDNResult
    
    @abstractmethod
    async def setup_ssl(self, domain: str) -> SSLResult
```

### Phase 3: Create Infrastructure Adapters

#### 3.1 Cloudflare Domain Adapter
```python
# backend/app/infrastructure/adapters/cloudflare_domain_adapter.py
class CloudflareDomainAdapter(DomainRegistryPort):
    # Pure infrastructure - only API calls, no business logic
```

#### 3.2 AWS Hosting Adapter
```python
# backend/app/infrastructure/adapters/aws_hosting_adapter.py
class AWSHostingAdapter(HostingPort):
    # Pure infrastructure - only AWS operations, no business logic
```

#### 3.3 SEO Tools Adapter
```python
# backend/app/infrastructure/adapters/seo_tools_adapter.py
class SEOToolsAdapter(SEOResearchPort):
    # Pure infrastructure - only external API calls, no business logic
```

## Migration Plan

### Step 1: Extract Domain Services (Week 1)
1. Create `SEODomainService` with business logic from `SEOOptimizationService`
2. Create `DomainRegistrationDomainService` with logic from `DomainRegistrationService`
3. Create `DeploymentDomainService` with logic from `AWSDeploymentService`
4. Create `GoogleBusinessProfileDomainService` with logic from `GoogleBusinessProfileService`

### Step 2: Create Infrastructure Ports (Week 1)
1. Define abstract interfaces for external service operations
2. Ensure ports only define infrastructure operations, no business logic
3. Create comprehensive type definitions for data exchange

### Step 3: Create Infrastructure Adapters (Week 2)
1. Extract pure infrastructure code into adapters
2. Implement ports with external service integrations
3. Remove all business logic from adapters

### Step 4: Update Application Services (Week 2)
1. Update orchestration services to use domain services and ports
2. Inject adapters through dependency injection
3. Ensure clean separation of concerns

### Step 5: Testing and Validation (Week 3)
1. Create comprehensive tests for domain services
2. Create integration tests for adapters
3. Validate that all functionality is preserved
4. Performance testing to ensure no degradation

## Benefits After Migration

1. **Clean Architecture Compliance**: Clear separation of concerns
2. **Testability**: Domain logic can be unit tested without external dependencies
3. **Flexibility**: Easy to swap infrastructure providers
4. **Maintainability**: Business logic is centralized and easier to modify
5. **Reusability**: Domain services can be used across different application contexts

## Files to be Created

### Domain Services
- `backend/app/domain/services/seo_domain_service.py`
- `backend/app/domain/services/domain_registration_domain_service.py`
- `backend/app/domain/services/deployment_domain_service.py`
- `backend/app/domain/services/google_business_profile_domain_service.py`

### Application Ports
- `backend/app/application/ports/seo_research_port.py`
- `backend/app/application/ports/domain_registry_port.py`
- `backend/app/application/ports/hosting_port.py`
- `backend/app/application/ports/google_business_port.py`

### Infrastructure Adapters
- `backend/app/infrastructure/adapters/cloudflare_domain_adapter.py`
- `backend/app/infrastructure/adapters/aws_hosting_adapter.py`
- `backend/app/infrastructure/adapters/seo_tools_adapter.py`
- `backend/app/infrastructure/adapters/google_business_adapter.py`

### Files to be Refactored/Removed
- `backend/app/infrastructure/external_services/domain_registration_service.py` → Remove
- `backend/app/infrastructure/external_services/seo_optimization_service.py` → Remove
- `backend/app/infrastructure/external_services/aws_deployment_service.py` → Remove
- `backend/app/infrastructure/external_services/google_business_profile_service.py` → Remove
- `backend/app/infrastructure/external_services/hero365_subdomain_service.py` → Refactor

## Implementation Priority

1. **High Priority**: SEO and Domain Registration (core website builder functionality)
2. **Medium Priority**: Deployment services (affects user experience)
3. **Low Priority**: Google Business Profile (enhancement feature)

This migration will significantly improve the codebase architecture and make it more maintainable and testable.
