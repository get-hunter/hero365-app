"""
Mobile Website Deployment API Routes

Provides mobile-optimized endpoints for deploying websites from collected business data.
Handles subdomain reservation, background deployment, and status tracking.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from uuid import UUID, uuid4
import logging
import re

from ..deps import get_current_user, get_business_context
from ...core.config import settings
from ...application.services.website_orchestration_service import WebsiteOrchestrationService
from ...application.services.service_validation_service import ServiceValidationService
from ...infrastructure.config.dependency_injection import get_business_repository
from ...workers.website_tasks import publish_website_task
from ...domain.entities.website_deployment import WebsiteDeployment, BusinessWebsite, DeploymentStatus
from ...infrastructure.database.repositories.supabase_website_deployment_repository import (
    SupabaseWebsiteDeploymentRepository,
    SupabaseBusinessWebsiteRepository
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile/website", tags=["Mobile Website Deployment"])


# =====================================
# REQUEST/RESPONSE MODELS
# =====================================

class BusinessHoursField(BaseModel):
    """Business hours for a specific day."""
    day_of_week: int = Field(..., ge=1, le=7, description="1=Monday, 7=Sunday")
    is_open: bool = Field(True, description="Whether business is open this day")
    open_time: Optional[time] = Field(None, description="Opening time")
    close_time: Optional[time] = Field(None, description="Closing time")
    lunch_start: Optional[time] = Field(None, description="Lunch break start")
    lunch_end: Optional[time] = Field(None, description="Lunch break end")
    is_emergency_only: bool = Field(False, description="Emergency service only")

    @validator('close_time')
    def validate_times(cls, v, values):
        if v and values.get('open_time') and v <= values['open_time']:
            raise ValueError('Close time must be after open time')
        return v


class ServiceAreaField(BaseModel):
    """Service area coverage."""
    postal_code: str = Field(..., min_length=3, max_length=20, description="Postal/ZIP code")
    country_code: str = Field("US", min_length=2, max_length=2, description="Country code")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    region: Optional[str] = Field(None, max_length=100, description="State/Province")
    emergency_services_available: bool = Field(True, description="Emergency services available")
    regular_services_available: bool = Field(True, description="Regular services available")


class BusinessServiceField(BaseModel):
    """Business service offering."""
    name: str = Field(..., min_length=1, max_length=200, description="Service name")
    description: Optional[str] = Field(None, max_length=1000, description="Service description")
    pricing_model: str = Field("fixed", description="Pricing model")
    unit_price: Optional[float] = Field(None, ge=0, description="Service price")
    estimated_duration_hours: Optional[float] = Field(None, ge=0, description="Estimated duration")
    is_emergency: bool = Field(False, description="Emergency service flag")
    is_featured: bool = Field(False, description="Featured service flag")

    @validator('pricing_model')
    def validate_pricing_model(cls, v):
        allowed = ['fixed', 'hourly', 'per_unit', 'tiered', 'custom']
        if v not in allowed:
            raise ValueError(f'Pricing model must be one of: {allowed}')
        return v


class BusinessProductField(BaseModel):
    """Business product offering."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    sku: Optional[str] = Field(None, max_length=100, description="Product SKU")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    unit_price: Optional[float] = Field(None, ge=0, description="Product price")
    is_featured: bool = Field(False, description="Featured product flag")


class BusinessLocationField(BaseModel):
    """Business location."""
    name: Optional[str] = Field(None, max_length=200, description="Location name")
    address: Optional[str] = Field(None, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=50, description="State/Province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    is_primary: bool = Field(False, description="Primary location flag")


class BrandingField(BaseModel):
    """Business branding preferences."""
    primary_color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Primary brand color")
    secondary_color: str = Field("#10B981", pattern=r"^#[0-9A-Fa-f]{6}$", description="Secondary brand color")
    logo_url: Optional[str] = Field(None, description="Logo URL")


class MobileWebsiteDeployRequest(BaseModel):
    """Mobile website deployment request."""
    
    # Core website settings
    subdomain: str = Field(..., min_length=1, max_length=58, description="Requested subdomain")
    
    # Business data
    service_areas: List[ServiceAreaField] = Field(..., min_items=1, description="Service coverage areas")
    services: List[BusinessServiceField] = Field(..., min_items=1, description="Business services")
    products: Optional[List[BusinessProductField]] = Field([], description="Business products")
    locations: Optional[List[BusinessLocationField]] = Field([], description="Business locations")
    hours: List[BusinessHoursField] = Field(..., min_items=5, max_items=7, description="Business hours")
    
    # Optional customization
    branding: Optional[BrandingField] = Field(None, description="Branding preferences")
    
    # Idempotency
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for duplicate prevention")

    @validator('subdomain')
    def validate_subdomain(cls, v):
        # Lowercase, alphanumeric + hyphen, no leading/trailing hyphen
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,56}[a-z0-9])?$', v.lower()):
            raise ValueError('Subdomain must be lowercase alphanumeric with hyphens, 1-58 chars, no leading/trailing hyphens')
        
        # Reserved names
        reserved = ['www', 'api', 'admin', 'app', 'mail', 'ftp', 'blog', 'shop', 'store', 'support', 'help']
        if v.lower() in reserved:
            raise ValueError(f'Subdomain "{v}" is reserved')
        
        return v.lower()

    @validator('hours')
    def validate_hours_coverage(cls, v):
        days = [h.day_of_week for h in v]
        # Ensure at least Monday-Friday coverage
        weekdays = [1, 2, 3, 4, 5]
        missing_weekdays = [d for d in weekdays if d not in days]
        if missing_weekdays:
            raise ValueError(f'Missing business hours for weekdays: {missing_weekdays}')
        return v


class MobileWebsiteDeployResponse(BaseModel):
    """Mobile website deployment response."""
    
    deployment_id: str = Field(..., description="Unique deployment ID")
    status: str = Field(..., description="Deployment status")
    status_url: str = Field(..., description="URL to check deployment status")
    estimated_completion_minutes: int = Field(3, description="Estimated completion time")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeploymentStatusResponse(BaseModel):
    """Deployment status response."""
    
    deployment_id: str = Field(..., description="Deployment ID")
    status: str = Field(..., description="Current status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current deployment step")
    website_url: Optional[str] = Field(None, description="Live website URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    build_logs: Optional[List[str]] = Field(None, description="Build log entries")
    created_at: datetime = Field(..., description="Deployment start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


class DeploymentListResponse(BaseModel):
    """List of deployments response."""
    
    deployments: List[DeploymentStatusResponse] = Field(..., description="Recent deployments")
    total_count: int = Field(..., description="Total deployment count")


# =====================================
# SUBDOMAIN VALIDATION SERVICE
# =====================================

class SubdomainService:
    """Service for subdomain validation and reservation."""
    
    def __init__(self):
        self.website_repo = SupabaseBusinessWebsiteRepository()
    
    async def validate_subdomain_availability(self, subdomain: str, business_id: UUID) -> Dict[str, Any]:
        """Validate subdomain is available for the business."""
        try:
            is_available = await self.website_repo.is_subdomain_available(subdomain, business_id)
            
            conflicts = []
            if not is_available:
                existing = await self.website_repo.get_by_subdomain(subdomain)
                if existing:
                    conflicts.append({
                        "business_id": str(existing.business_id),
                        "subdomain": existing.subdomain
                    })
            
            return {
                "available": is_available,
                "subdomain": subdomain,
                "conflicts": conflicts
            }
        except Exception as e:
            logger.error(f"Failed to validate subdomain availability: {str(e)}")
            return {
                "available": False,
                "subdomain": subdomain,
                "conflicts": [],
                "error": str(e)
            }
    
    async def reserve_subdomain(self, subdomain: str, business_id: UUID) -> Dict[str, Any]:
        """Reserve subdomain for the business."""
        try:
            # Create or update business website with subdomain
            website = BusinessWebsite(
                business_id=business_id,
                subdomain=subdomain,
                status="building"
            )
            
            result = await self.website_repo.upsert_by_business_id(website)
            
            return {
                "reserved": True,
                "subdomain": subdomain,
                "business_id": str(business_id),
                "website_id": str(result.id)
            }
        except Exception as e:
            logger.error(f"Failed to reserve subdomain: {str(e)}")
            return {
                "reserved": False,
                "subdomain": subdomain,
                "business_id": str(business_id),
                "error": str(e)
            }


# =====================================
# API ENDPOINTS
# =====================================

@router.post("/deploy", response_model=MobileWebsiteDeployResponse)
async def deploy_website_mobile(
    request: MobileWebsiteDeployRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_repository = Depends(get_business_repository),
    raw_request: Request = None
):
    """
    Deploy website from mobile app with collected business data.
    
    This endpoint:
    1. Validates business readiness and subdomain availability
    2. Reserves the subdomain
    3. Persists business data to appropriate tables
    4. Enqueues background deployment job
    5. Returns deployment tracking information
    """
    
    try:
        # Dev-bypass: short-circuit deployment flow for local testing
        if settings.ENVIRONMENT == "local" and raw_request and raw_request.headers.get("X-Dev-Bypass", "").lower() in ("1", "true", "yes"):
            fake_id = f"dev-{request.subdomain}"
            return MobileWebsiteDeployResponse(
                deployment_id=fake_id,
                status="completed",
                status_url=f"/api/v1/mobile/website/deployments/{fake_id}",
                estimated_completion_minutes=0,
                created_at=datetime.utcnow()
            )
        business_id = UUID(business_context["business_id"])
        deployment_repo = SupabaseWebsiteDeploymentRepository()
        
        # Get business information
        business = await business_repository.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        # Check for existing active deployment
        active_deployment = await deployment_repo.get_active_deployment(business_id)
        if active_deployment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Active deployment already in progress: {active_deployment.id}"
            )
        
        # Handle idempotency
        if request.idempotency_key:
            existing_deployment = await deployment_repo.get_by_idempotency_key(
                business_id, request.idempotency_key
            )
            if existing_deployment:
                # Return existing deployment
                return MobileWebsiteDeployResponse(
                    deployment_id=str(existing_deployment.id),
                    status=existing_deployment.status.value,
                    status_url=f"/api/mobile/website/deployments/{existing_deployment.id}",
                    estimated_completion_minutes=3,
                    created_at=existing_deployment.created_at
                )
        
        # Validate subdomain availability
        subdomain_service = SubdomainService()
        subdomain_check = await subdomain_service.validate_subdomain_availability(
            request.subdomain, business_id
        )
        
        if not subdomain_check["available"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subdomain '{request.subdomain}' is not available"
            )
        
        # Validate business readiness
        validation_service = ServiceValidationService()
        # TODO: Implement mobile-specific readiness check
        
        # Reserve subdomain
        reservation_result = await subdomain_service.reserve_subdomain(request.subdomain, business_id)
        if not reservation_result["reserved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to reserve subdomain: {reservation_result.get('error', 'Unknown error')}"
            )
        
        # Create deployment record
        deployment = WebsiteDeployment(
            business_id=business_id,
            website_id=UUID(reservation_result["website_id"]),
            project_name=f"hero365-{request.subdomain}",
            subdomain=request.subdomain,
            status=DeploymentStatus.PENDING,
            metadata={
                "idempotency_key": request.idempotency_key,
                "mobile_request": True,
                "request_data": request.dict()
            } if request.idempotency_key else {
                "mobile_request": True,
                "request_data": request.dict()
            }
        )
        
        created_deployment = await deployment_repo.create(deployment)
        
        # Enqueue background deployment job
        background_tasks.add_task(
            publish_website_task.delay,
            deployment_id=str(created_deployment.id),
            business_id=str(business_id),
            request_data=request.dict()
        )
        
        # Return deployment tracking info
        return MobileWebsiteDeployResponse(
            deployment_id=str(created_deployment.id),
            status=created_deployment.status.value,
            status_url=f"/api/mobile/website/deployments/{created_deployment.id}",
            estimated_completion_minutes=3,
            created_at=created_deployment.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start mobile website deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start website deployment: {str(e)}"
        )


@router.get("/deployments/{deployment_id}", response_model=DeploymentStatusResponse)
async def get_deployment_status_mobile(
    deployment_id: str,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    raw_request: Request = None
):
    """
    Get deployment status for mobile app polling.
    
    Returns current status, progress, and website URL when completed.
    """
    
    try:
        # Dev-bypass: synthesize a completed deployment with computed URL
        if settings.ENVIRONMENT == "local" and raw_request and raw_request.headers.get("X-Dev-Bypass", "").lower() in ("1", "true", "yes"):
            if deployment_id.startswith("dev-"):
                sub = deployment_id[4:]
                return DeploymentStatusResponse(
                    deployment_id=deployment_id,
                    status="completed",
                    progress=100,
                    current_step="Deployment completed",
                    website_url=f"https://hero365-{sub}.pages.dev",
                    error_message=None,
                    build_logs=None,
                    created_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
        business_id = UUID(business_context["business_id"])
        deployment_repo = SupabaseWebsiteDeploymentRepository()
        
        # Get deployment by ID
        deployment = await deployment_repo.get_by_id(UUID(deployment_id))
        
        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found"
            )
        
        # Verify deployment belongs to the current business
        if deployment.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this deployment"
            )
        
        return DeploymentStatusResponse(
            deployment_id=str(deployment.id),
            status=deployment.status.value,
            progress=deployment.progress,
            current_step=deployment.current_step,
            website_url=deployment.deploy_url,
            error_message=deployment.error_message,
            build_logs=deployment.build_logs[-10:] if deployment.build_logs else None,  # Last 10 logs
            created_at=deployment.created_at,
            completed_at=deployment.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get deployment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment status: {str(e)}"
        )


@router.get("/deployments", response_model=DeploymentListResponse)
async def list_deployments_mobile(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    limit: int = 10,
    skip: int = 0
):
    """
    List recent deployments for the current business.
    """
    
    try:
        business_id = UUID(business_context["business_id"])
        deployment_repo = SupabaseWebsiteDeploymentRepository()
        
        # Get deployments for the business
        deployments = await deployment_repo.get_by_business_id(business_id, skip, limit)
        total_count = await deployment_repo.count_by_business(business_id)
        
        # Convert to response format
        deployment_responses = []
        for deployment in deployments:
            deployment_responses.append(DeploymentStatusResponse(
                deployment_id=str(deployment.id),
                status=deployment.status.value,
                progress=deployment.progress,
                current_step=deployment.current_step,
                website_url=deployment.deploy_url,
                error_message=deployment.error_message,
                build_logs=deployment.build_logs[-5:] if deployment.build_logs else None,  # Last 5 logs
                created_at=deployment.created_at,
                completed_at=deployment.completed_at
            ))
        
        return DeploymentListResponse(
            deployments=deployment_responses,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Failed to list deployments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {str(e)}"
        )


@router.post("/deployments/{deployment_id}/cancel")
async def cancel_deployment_mobile(
    deployment_id: str,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context)
):
    """
    Cancel a pending or in-progress deployment.
    """
    
    try:
        business_id = UUID(business_context["business_id"])
        deployment_repo = SupabaseWebsiteDeploymentRepository()
        
        # Get deployment to verify ownership
        deployment = await deployment_repo.get_by_id(UUID(deployment_id))
        
        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found"
            )
        
        # Verify deployment belongs to the current business
        if deployment.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this deployment"
            )
        
        # Check if deployment can be cancelled
        if deployment.is_terminal_status():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel deployment in {deployment.status.value} status"
            )
        
        # Cancel the deployment
        success = await deployment_repo.cancel_deployment(UUID(deployment_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel deployment"
            )
        
        # TODO: Cancel background job if possible (Celery task cancellation)
        
        return {"message": "Deployment cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel deployment: {str(e)}"
        )
