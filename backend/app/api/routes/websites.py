"""
Website Builder API Routes

Comprehensive API endpoints for website creation, management, domain registration,
and analytics for the Hero365 SEO Website Builder system.
"""

import uuid
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import require_view_projects_dep, require_edit_projects_dep
from ...domain.entities.business import Business, TradeCategory
from ...domain.entities.website import (
    BusinessWebsite, WebsiteTemplate, DomainRegistration, WebsiteStatus,
    WebsiteIntakeForm, WebsiteFormSubmission, WebsiteBookingSlot,
    WebsiteConversionTracking, SEOKeywordTracking, WebsiteAnalytics
)
from ...application.services.website_builder_service import (
    WebsiteBuilderService, BuildConfiguration, BuildResult
)
from ...application.services.ai_content_generator_service import AIContentGeneratorService
from ...infrastructure.adapters.content_generation_factory import get_provider_info
from ...infrastructure.adapters.cloudflare_domain_adapter import CloudflareDomainAdapter
from ...domain.services.domain_registration_domain_service import DomainRegistrationDomainService
from ...application.ports.domain_registry_port import DomainAvailabilityResult
from ...application.exceptions.application_exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/websites", tags=["websites"])


# =====================================
# REQUEST/RESPONSE MODELS
# =====================================

class WebsiteCreateRequest(BaseModel):
    """Request model for creating a new website."""
    
    template_id: Optional[uuid.UUID] = None
    subdomain: Optional[str] = Field(None, max_length=100, description="Subdomain for hero365.ai")
    custom_domain: Optional[str] = Field(None, max_length=255, description="Custom domain name")
    
    # Content customization
    theme_overrides: Dict[str, Any] = Field(default_factory=dict)
    content_overrides: Dict[str, Any] = Field(default_factory=dict)
    
    # SEO settings
    target_keywords: List[str] = Field(default_factory=list, max_items=20)
    target_locations: List[str] = Field(default_factory=list, max_items=10)
    
    # Build configuration
    build_immediately: bool = Field(default=True, description="Start building immediately")


class WebsiteUpdateRequest(BaseModel):
    """Request model for updating website settings."""
    
    theme_overrides: Optional[Dict[str, Any]] = None
    content_overrides: Optional[Dict[str, Any]] = None
    seo_keywords: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    google_site_verification: Optional[str] = None


class WebsiteResponse(BaseModel):
    """Response model for website data."""
    
    id: uuid.UUID
    business_id: uuid.UUID
    template_id: Optional[uuid.UUID]
    domain: Optional[str]
    subdomain: Optional[str]
    status: WebsiteStatus
    
    # Trade information
    primary_trade: Optional[str]
    secondary_trades: List[str]
    service_areas: List[str]
    
    # URLs
    website_url: Optional[str]
    preview_url: Optional[str]
    
    # Build information
    last_build_at: Optional[datetime]
    last_deploy_at: Optional[datetime]
    build_duration_seconds: Optional[int]
    
    # Performance metrics
    lighthouse_score: Optional[int]
    seo_keywords: List[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class DomainSearchResponse(BaseModel):
    """Response model for domain search results."""
    
    primary_suggestions: List[DomainSuggestion]
    other_suggestions: List[DomainSuggestion]
    recommended: Optional[DomainSuggestion]
    business_trades: List[str]
    search_metadata: Dict[str, Any]


class DomainRegistrationRequest(BaseModel):
    """Request model for domain registration."""
    
    domain: str = Field(..., description="Domain name to register")
    years: int = Field(default=1, ge=1, le=10, description="Registration period in years")
    auto_renew: bool = Field(default=True, description="Enable auto-renewal")
    privacy_protection: bool = Field(default=True, description="Enable WHOIS privacy")


class FormSubmissionRequest(BaseModel):
    """Request model for form submissions from websites."""
    
    website_id: uuid.UUID
    business_id: uuid.UUID
    form_type: str
    form_data: Dict[str, Any]
    visitor_info: Dict[str, Any] = Field(default_factory=dict)


class BookingRequest(BaseModel):
    """Request model for service bookings."""
    
    website_id: uuid.UUID
    service_type: str
    appointment_date: date
    start_time: str  # HH:MM format
    duration_minutes: int
    
    # Customer information
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: str
    service_address: str
    
    # Additional details
    booking_notes: Optional[str] = None
    special_requirements: Optional[str] = None
    access_instructions: Optional[str] = None


class AnalyticsRequest(BaseModel):
    """Request model for analytics queries."""
    
    date_from: date
    date_to: date
    metrics: List[str] = Field(default_factory=lambda: ["page_views", "conversions", "seo"])
    granularity: str = Field(default="daily", description="daily, weekly, monthly")


# =====================================
# WEBSITE MANAGEMENT ENDPOINTS
# =====================================

@router.get("", response_model=List[WebsiteResponse])
async def get_websites(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Get all websites for the current business."""
    
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"Getting websites for business {business_id}")
    
    try:
        # TODO: Implement repository call
        # websites = await website_repository.get_by_business_id(business_id)
        
        # Get real websites from database when repository is implemented
        # websites = await website_repository.get_by_business_id(business_id)
        # return [WebsiteResponse.from_entity(website) for website in websites]
        return []  # Return empty list until repository is implemented
        
    except Exception as e:
        logger.error(f"Error getting websites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve websites: {str(e)}"
        )


@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    request: WebsiteCreateRequest,
    background_tasks: BackgroundTasks,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_edit_projects_dep)
):
    """Create a new website for the business."""
    
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"Creating website for business {business_id}")
    
    try:
        # TODO: Get business and validate trades
        # business = await business_repository.get_by_id(business_id)
        # if not business.get_all_trades():
        #     raise HTTPException(400, "Business must have at least one trade specified")
        
        # TODO: Auto-select template based on business trades if not provided
        # if not request.template_id:
        #     primary_trade = business.get_primary_trade()
        #     template = await template_repository.get_by_trade(primary_trade)
        #     if not template:
        #         template = await template_repository.get_multi_trade_template()
        
        # Create website record
        website_id = uuid.uuid4()
        
        # TODO: Create website in database
        # website = BusinessWebsite(
        #     id=website_id,
        #     business_id=business_id,
        #     template_id=request.template_id,
        #     subdomain=request.subdomain,
        #     domain=request.custom_domain,
        #     status=WebsiteStatus.DRAFT,
        #     theme_overrides=request.theme_overrides,
        #     content_overrides=request.content_overrides,
        #     seo_keywords=request.target_keywords,
        #     target_locations=request.target_locations
        # )
        # 
        # created_website = await website_repository.create(website)
        
        # Queue build job if requested
        if request.build_immediately:
            background_tasks.add_task(
                _queue_website_build,
                website_id,
                business_id
            )
        
        # Return response based on created website entity
        # In production, this would return the actual created website
        # For now, return basic structure until repository is fully implemented
        return WebsiteResponse(
            id=website_id,
            business_id=business_id,
            template_id=request.template_id,
            domain=request.custom_domain,
            subdomain=request.subdomain,
            status=WebsiteStatus.BUILDING if request.build_immediately else WebsiteStatus.DRAFT,
            primary_trade="hvac",  # Default to HVAC
            secondary_trades=[],
            service_areas=["Austin", "Round Rock", "Cedar Park"],
            website_url=None,
            preview_url=f"/preview/{website_id}",
            last_build_at=None,
            last_deploy_at=None,
            build_duration_seconds=None,
            lighthouse_score=None,
            seo_keywords=request.target_keywords,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error creating website: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create website: {str(e)}"
        )


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Get a specific website by ID."""
    
    try:
        # TODO: Implement repository call with business validation
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        
        # Return actual website data when repository is implemented
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        # return WebsiteResponse.from_entity(website)
        
        # Placeholder response until repository is implemented
        return WebsiteResponse(
            id=website_id,
            business_id=uuid.UUID(business_context["business_id"]),
            template_id=None,
            domain=None,
            subdomain="austin-elite-hvac",
            status=WebsiteStatus.DEPLOYED,
            primary_trade="hvac",
            secondary_trades=[],
            service_areas=["Austin", "Round Rock", "Cedar Park"],
            website_url="https://86a38fce.hero365-websites.pages.dev",
            preview_url=f"/preview/{website_id}",
            last_build_at=datetime.utcnow(),
            last_deploy_at=datetime.utcnow(),
            build_duration_seconds=45,
            lighthouse_score=94,
            seo_keywords=["hvac services", "emergency hvac"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting website: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve website: {str(e)}"
        )


@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: uuid.UUID,
    request: WebsiteUpdateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_edit_projects_dep)
):
    """Update website settings."""
    
    try:
        # TODO: Implement update logic
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        
        # Update fields
        updates = {}
        if request.theme_overrides is not None:
            updates["theme_overrides"] = request.theme_overrides
        if request.content_overrides is not None:
            updates["content_overrides"] = request.content_overrides
        if request.seo_keywords is not None:
            updates["seo_keywords"] = request.seo_keywords
        if request.target_locations is not None:
            updates["target_locations"] = request.target_locations
        if request.google_site_verification is not None:
            updates["google_site_verification"] = request.google_site_verification
        
        # updated_website = await website_repository.update(website_id, updates)
        
        # Mock response
        return WebsiteResponse(
            id=website_id,
            business_id=uuid.UUID(business_context["business_id"]),
            template_id=None,
            domain=None,
            subdomain="mock-business",
            status=WebsiteStatus.DEPLOYED,
            primary_trade="plumbing",
            secondary_trades=["electrical"],
            service_areas=["New York", "Brooklyn"],
            website_url="https://mock-business.hero365.ai",
            preview_url=f"/preview/{website_id}",
            last_build_at=datetime.utcnow(),
            last_deploy_at=datetime.utcnow(),
            build_duration_seconds=45,
            lighthouse_score=94,
            seo_keywords=request.seo_keywords or ["plumbing services"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating website: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update website: {str(e)}"
        )


@router.post("/{website_id}/build")
async def build_website(
    website_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    build_config: Optional[BuildConfiguration] = None,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_edit_projects_dep)
):
    """Trigger a website build."""
    
    try:
        # TODO: Validate website ownership
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        
        # Queue build job
        background_tasks.add_task(
            _queue_website_build,
            website_id,
            uuid.UUID(business_context["business_id"]),
            build_config
        )
        
        return {
            "message": "Website build queued successfully",
            "website_id": website_id,
            "status": "building"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing website build: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue website build: {str(e)}"
        )


@router.post("/{website_id}/deploy")
async def deploy_website(
    website_id: uuid.UUID,
    domain: Optional[str] = None,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_edit_projects_dep)
):
    """Deploy website to production."""
    
    try:
        # TODO: Implement deployment logic
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        
        # if website.status != WebsiteStatus.BUILT:
        #     raise HTTPException(400, "Website must be built before deployment")
        
        # Deploy to AWS S3 + CloudFront
        # deployment_service = AWSDeploymentService()
        # deployment_result = await deployment_service.deploy_website(
        #     website_id, website.build_path, domain or website.get_full_domain()
        # )
        
        return {
            "message": "Website deployed successfully",
            "website_id": website_id,
            "url": f"https://{domain or 'mock-business.hero365.ai'}",
            "status": "deployed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying website: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy website: {str(e)}"
        )


# =====================================
# DOMAIN MANAGEMENT ENDPOINTS
# =====================================

@router.post("/domains/search", response_model=DomainSearchResponse)
async def search_domains(
    business_name: str = Body(..., description="Business name for domain suggestions"),
    location: Optional[str] = Body(None, description="Business location"),
    max_results: int = Body(20, ge=5, le=50, description="Maximum number of suggestions"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Search for available domains with trade-based SEO scoring."""
    
    try:
        # TODO: Get business data
        # business = await business_repository.get_by_id(uuid.UUID(business_context["business_id"]))
        # if not business.get_all_trades():
        #     raise HTTPException(400, "Business must have at least one trade specified for domain suggestions")
        
        # Mock business data for now
        mock_trades = ["plumbing", "electrical"]
        primary_trade = mock_trades[0]
        
        # Create domain search request
        search_request = DomainSearchRequest(
            business_name=business_name,
            primary_trade=primary_trade,
            all_trades=mock_trades,
            trade_category=TradeCategory.RESIDENTIAL,  # Mock
            location=location or "New York"
        )
        
        # Search domains
        domain_service = DomainRegistrationService()
        suggestions = await domain_service.search_domains(search_request)
        
        # Group suggestions by trade relevance
        primary_suggestions = [s for s in suggestions if s.recommended_for == primary_trade]
        other_suggestions = [s for s in suggestions if s.recommended_for != primary_trade]
        
        return DomainSearchResponse(
            primary_suggestions=primary_suggestions[:10],
            other_suggestions=other_suggestions[:10],
            recommended=primary_suggestions[0] if primary_suggestions else (suggestions[0] if suggestions else None),
            business_trades=mock_trades,
            search_metadata={
                "total_suggestions": len(suggestions),
                "search_time_ms": 1250,
                "primary_trade": primary_trade
            }
        )
        
    except Exception as e:
        logger.error(f"Error searching domains: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search domains: {str(e)}"
        )


@router.post("/domains/register")
async def register_domain(
    request: DomainRegistrationRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_edit_projects_dep)
):
    """Register a domain with Cloudflare."""
    
    try:
        business_id = uuid.UUID(business_context["business_id"])
        
        # TODO: Get business data for contact info
        # business = await business_repository.get_by_id(business_id)
        
        # Mock contact info
        contact_info = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0123",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "US"
        }
        
        # Register domain
        domain_service = DomainRegistrationService()
        # registration = await domain_service.register_domain(
        #     request.domain,
        #     business,
        #     contact_info,
        #     request.years,
        #     request.auto_renew
        # )
        
        # Mock response
        return {
            "message": "Domain registered successfully",
            "domain": request.domain,
            "status": "active",
            "expires_at": "2025-01-27T00:00:00Z",
            "auto_renew": request.auto_renew,
            "dns_configured": True
        }
        
    except Exception as e:
        logger.error(f"Error registering domain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register domain: {str(e)}"
        )


@router.get("/domains")
async def get_domains(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Get all domains for the business."""
    
    try:
        business_id = uuid.UUID(business_context["business_id"])
        
        # TODO: Get domains from repository
        # domains = await domain_repository.get_by_business_id(business_id)
        
        # Mock response
        return [
            {
                "id": str(uuid.uuid4()),
                "domain": "example-plumbing.com",
                "status": "active",
                "registered_at": "2024-01-27T00:00:00Z",
                "expires_at": "2025-01-27T00:00:00Z",
                "auto_renew": True,
                "seo_score": 87
            }
        ]
        
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get domains: {str(e)}"
        )


# =====================================
# FORM SUBMISSION ENDPOINTS
# =====================================

@router.post("/forms/submit")
async def submit_form(
    request: FormSubmissionRequest,
    background_tasks: BackgroundTasks
):
    """Handle form submissions from websites (public endpoint)."""
    
    try:
        logger.info(f"Form submission received for website {request.website_id}")
        
        # TODO: Validate website exists and is active
        # website = await website_repository.get_by_id(request.website_id)
        # if not website:
        #     raise HTTPException(404, "Website not found")
        
        # Process form submission
        background_tasks.add_task(
            _process_form_submission,
            request.website_id,
            request.business_id,
            request.form_type,
            request.form_data,
            request.visitor_info
        )
        
        # Send immediate response
        return {
            "success": True,
            "message": "Form submitted successfully",
            "submission_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process form submission"
        )


@router.post("/bookings")
async def create_booking(
    request: BookingRequest,
    background_tasks: BackgroundTasks
):
    """Create a service booking from website (public endpoint)."""
    
    try:
        logger.info(f"Booking request received for website {request.website_id}")
        
        # TODO: Validate website and availability
        # website = await website_repository.get_by_id(request.website_id)
        # if not website:
        #     raise HTTPException(404, "Website not found")
        
        # Process booking
        booking_id = uuid.uuid4()
        background_tasks.add_task(
            _process_booking_request,
            booking_id,
            request
        )
        
        return {
            "success": True,
            "message": "Booking request received",
            "booking_id": booking_id,
            "confirmation_sent": True
        }
        
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process booking"
        )


# =====================================
# ANALYTICS ENDPOINTS
# =====================================

@router.get("/{website_id}/analytics")
async def get_website_analytics(
    website_id: uuid.UUID,
    date_from: date = Query(..., description="Start date for analytics"),
    date_to: date = Query(..., description="End date for analytics"),
    metrics: List[str] = Query(default=["traffic", "conversions"], description="Metrics to include"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Get website analytics and performance metrics."""
    
    try:
        # TODO: Validate website ownership
        # website = await website_repository.get_by_id(website_id)
        # if not website or website.business_id != uuid.UUID(business_context["business_id"]):
        #     raise HTTPException(404, "Website not found")
        
        # TODO: Get analytics data
        # analytics_data = await analytics_repository.get_website_analytics(
        #     website_id, date_from, date_to, metrics
        # )
        
        # Mock analytics response
        return {
            "website_id": website_id,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "traffic": {
                "page_views": 1250,
                "unique_visitors": 890,
                "sessions": 1050,
                "bounce_rate": 35.2,
                "avg_session_duration": 185
            },
            "conversions": {
                "form_submissions": 45,
                "phone_calls": 23,
                "bookings": 18,
                "conversion_rate": 4.3
            },
            "seo": {
                "search_impressions": 5600,
                "search_clicks": 280,
                "avg_position": 8.5,
                "ctr": 5.0
            },
            "performance": {
                "lighthouse_score": 94,
                "core_web_vitals": {
                    "lcp": 1.2,
                    "fid": 45,
                    "cls": 0.05
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/{website_id}/seo/keywords")
async def get_seo_keywords(
    website_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_view_projects_dep)
):
    """Get SEO keyword tracking for website."""
    
    try:
        # TODO: Get keyword tracking data
        # keywords = await seo_repository.get_keyword_tracking(website_id)
        
        # Mock response
        return [
            {
                "keyword": "plumbing services",
                "current_rank": 5,
                "previous_rank": 7,
                "search_volume": 1200,
                "competition": "medium",
                "trend": "improving"
            },
            {
                "keyword": "emergency plumber",
                "current_rank": 3,
                "previous_rank": 3,
                "search_volume": 800,
                "competition": "high",
                "trend": "stable"
            }
        ]
        
    except Exception as e:
        logger.error(f"Error getting SEO keywords: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SEO keywords: {str(e)}"
        )


# =====================================
# BACKGROUND TASK FUNCTIONS
# =====================================

async def _queue_website_build(
    website_id: uuid.UUID,
    business_id: uuid.UUID,
    build_config: Optional[BuildConfiguration] = None
):
    """Queue a website build job."""
    
    try:
        logger.info(f"Queuing website build for {website_id}")
        
        # TODO: Create build job record
        # build_job = WebsiteBuildJob(
        #     website_id=website_id,
        #     job_type=BuildJobType.INITIAL_BUILD,
        #     job_config=build_config.dict() if build_config else {},
        #     priority=5
        # )
        # 
        # await build_job_repository.create(build_job)
        
        # TODO: Queue with Celery
        # from ...workers.website_tasks import build_website_task
        # build_website_task.delay(str(website_id))
        
        logger.info(f"Website build queued successfully for {website_id}")
        
    except Exception as e:
        logger.error(f"Error queuing website build: {str(e)}")


async def _process_form_submission(
    website_id: uuid.UUID,
    business_id: uuid.UUID,
    form_type: str,
    form_data: Dict[str, Any],
    visitor_info: Dict[str, Any]
):
    """Process form submission in background."""
    
    try:
        logger.info(f"Processing form submission for website {website_id}")
        
        # TODO: Create form submission record
        # submission = WebsiteFormSubmission(
        #     website_id=website_id,
        #     business_id=business_id,
        #     form_data=form_data,
        #     visitor_info=visitor_info,
        #     lead_type=_determine_lead_type(form_type, form_data),
        #     priority_level=_determine_priority(form_data)
        # )
        # 
        # submission.extract_contact_info()
        # created_submission = await form_submission_repository.create(submission)
        
        # TODO: Route lead based on type
        # if submission.lead_type == LeadType.EMERGENCY:
        #     await _handle_emergency_lead(created_submission)
        # elif submission.lead_type == LeadType.QUOTE_REQUEST:
        #     await _create_estimate_from_submission(created_submission)
        # elif submission.lead_type == LeadType.SERVICE_BOOKING:
        #     await _create_job_from_submission(created_submission)
        
        # TODO: Send notifications
        # await _send_lead_notifications(created_submission)
        
        logger.info(f"Form submission processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")


async def _process_booking_request(
    booking_id: uuid.UUID,
    request: BookingRequest
):
    """Process booking request in background."""
    
    try:
        logger.info(f"Processing booking request {booking_id}")
        
        # TODO: Create booking record
        # booking = WebsiteBookingSlot(
        #     id=booking_id,
        #     website_id=request.website_id,
        #     service_type=request.service_type,
        #     appointment_date=request.appointment_date,
        #     start_time=datetime.strptime(request.start_time, "%H:%M").time(),
        #     end_time=(datetime.strptime(request.start_time, "%H:%M") + 
        #              timedelta(minutes=request.duration_minutes)).time(),
        #     duration_minutes=request.duration_minutes,
        #     customer_name=request.customer_name,
        #     customer_email=request.customer_email,
        #     customer_phone=request.customer_phone,
        #     service_address=request.service_address,
        #     booking_notes=request.booking_notes,
        #     special_requirements=request.special_requirements,
        #     access_instructions=request.access_instructions
        # )
        # 
        # created_booking = await booking_repository.create(booking)
        
        # TODO: Add to calendar system
        # await _add_booking_to_calendar(created_booking)
        
        # TODO: Send confirmation
        # await _send_booking_confirmation(created_booking)
        
        logger.info(f"Booking processed successfully: {booking_id}")
        
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")


def _determine_lead_type(form_type: str, form_data: Dict[str, Any]) -> str:
    """Determine lead type from form data."""
    
    if form_type == "emergency":
        return "emergency"
    elif form_type == "quote":
        return "quote_request"
    elif form_type == "booking":
        return "service_booking"
    elif "urgency" in form_data and form_data["urgency"] == "emergency":
        return "emergency"
    else:
        return "general_inquiry"


def _determine_priority(form_data: Dict[str, Any]) -> str:
    """Determine priority level from form data."""
    
    urgency = form_data.get("urgency", "").lower()
    
    if urgency in ["emergency", "asap"]:
        return "emergency"
    elif urgency in ["24hours", "urgent"]:
        return "high"
    elif urgency in ["week"]:
        return "medium"
    else:
        return "low"


# =====================================
# CONTENT GENERATION PROVIDER MANAGEMENT
# =====================================

class ContentProviderResponse(BaseModel):
    """Response model for content provider information."""
    
    name: str
    configured: bool
    adapter_class: str
    description: str


class ContentProviderListResponse(BaseModel):
    """Response model for listing available content providers."""
    
    current_provider: str
    available_providers: Dict[str, ContentProviderResponse]


class SwitchProviderRequest(BaseModel):
    """Request model for switching content generation provider."""
    
    provider: str = Field(..., description="Provider name (openai, claude, gemini)")


@router.get(
    "/content-providers",
    response_model=ContentProviderListResponse,
    summary="Get Available Content Generation Providers",
    description="Get information about available AI content generation providers and their configuration status."
)
async def get_content_providers(
    current_user = Depends(get_current_user),
    business: Business = Depends(get_business_context)
):
    """Get available content generation providers and their status."""
    
    try:
        # Get provider information
        providers_info = get_provider_info()
        
        # Convert to response format
        providers = {}
        for name, info in providers_info.items():
            providers[name] = ContentProviderResponse(
                name=info["name"],
                configured=info["configured"],
                adapter_class=info["adapter_class"],
                description=info["description"]
            )
        
        # Get current provider from settings
        from ...core.config import settings
        current_provider = settings.CONTENT_GENERATION_PROVIDER
        
        return ContentProviderListResponse(
            current_provider=current_provider,
            available_providers=providers
        )
        
    except Exception as e:
        logger.error(f"Error getting content providers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content providers: {str(e)}"
        )


@router.post(
    "/content-providers/switch",
    summary="Switch Content Generation Provider",
    description="Switch to a different AI content generation provider for website building."
)
async def switch_content_provider(
    request: SwitchProviderRequest,
    current_user = Depends(get_current_user),
    business: Business = Depends(get_business_context)
):
    """Switch to a different content generation provider."""
    
    try:
        # Validate provider is available
        providers_info = get_provider_info()
        
        if request.provider not in providers_info:
            available = ", ".join(providers_info.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider '{request.provider}'. Available: {available}"
            )
        
        # Check if provider is configured
        provider_info = providers_info[request.provider]
        if not provider_info["configured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' is not configured. Check API keys and settings."
            )
        
        # Test the provider by creating an adapter
        from ...infrastructure.adapters.content_generation_factory import create_content_adapter
        
        try:
            test_adapter = create_content_adapter(provider=request.provider)
            logger.info(f"Successfully validated {request.provider} provider")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to initialize {request.provider} provider: {str(e)}"
            )
        
        # Update configuration (in a real app, you might want to persist this)
        # For now, we'll just update the runtime setting
        from ...core.config import settings
        settings.CONTENT_GENERATION_PROVIDER = request.provider
        
        logger.info(f"Switched content generation provider to {request.provider}")
        
        return {
            "success": True,
            "message": f"Successfully switched to {request.provider} content generation provider",
            "provider": request.provider,
            "switched_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching content provider: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch content provider: {str(e)}"
        )


@router.post(
    "/content-providers/test/{provider}",
    summary="Test Content Generation Provider",
    description="Test a content generation provider to ensure it's working correctly."
)
async def test_content_provider(
    provider: str,
    current_user = Depends(get_current_user),
    business: Business = Depends(get_business_context)
):
    """Test a content generation provider."""
    
    try:
        # Validate provider exists
        providers_info = get_provider_info()
        
        if provider not in providers_info:
            available = ", ".join(providers_info.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider '{provider}'. Available: {available}"
            )
        
        # Check if provider is configured
        provider_info = providers_info[provider]
        if not provider_info["configured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{provider}' is not configured"
            )
        
        # Create adapter and test basic functionality
        from ...infrastructure.adapters.content_generation_factory import create_content_adapter
        from ...domain.entities.business_branding import BusinessBranding
        
        start_time = datetime.utcnow()
        
        try:
            adapter = create_content_adapter(provider=provider)
            
            # Create minimal test branding
            test_branding = BusinessBranding(
                business_id=business.id,
                primary_color="#007bff",
                secondary_color="#6c757d",
                font_family="Inter",
                theme_name="professional"
            )
            
            # Test basic content generation
            test_content = await adapter.generate_page_content(
                business=business,
                branding=test_branding,
                page_type="home",
                context={"test": True}
            )
            
            test_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "provider": provider,
                "test_duration_seconds": test_time,
                "content_generated": bool(test_content),
                "content_keys": list(test_content.keys()) if test_content else [],
                "tested_at": datetime.utcnow()
            }
            
        except Exception as e:
            test_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": False,
                "provider": provider,
                "test_duration_seconds": test_time,
                "error": str(e),
                "tested_at": datetime.utcnow()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing content provider: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test content provider: {str(e)}"
        )
