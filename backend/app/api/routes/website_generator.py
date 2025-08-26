"""
Website Generator API

Endpoints for generating and deploying business-specific websites with proper configuration.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel, Field, validator

from ...domain.entities.business import Business
from ...domain.entities.website import BusinessWebsite, WebsiteStatus, WebsiteTemplate
from ...application.services.website_orchestration_service import WebsiteOrchestrationService
from ...infrastructure.auth.dependencies import get_current_user, get_business_context
from ...infrastructure.auth.permissions import require_edit_projects_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/website-generator", tags=["Website Generator"])


class BusinessWebsiteRequest(BaseModel):
    """Request to generate a website for a specific business."""
    
    business_id: str = Field(..., description="Business UUID to generate website for")
    template_name: str = Field(default="professional", description="Template to use")
    
    # Deployment Configuration
    environment: str = Field(default="development", description="Target environment")
    project_name: Optional[str] = Field(None, description="Custom Cloudflare project name")
    custom_domain: Optional[str] = Field(None, description="Custom domain for the website")
    
    # Business Overrides (optional)
    business_name_override: Optional[str] = Field(None, description="Override business name")
    business_phone_override: Optional[str] = Field(None, description="Override business phone")
    business_email_override: Optional[str] = Field(None, description="Override business email")
    
    # Build Options
    build_immediately: bool = Field(default=True, description="Start build immediately")
    deploy_immediately: bool = Field(default=False, description="Deploy after build")
    
    # Feature Flags
    enable_booking_widget: bool = Field(default=True, description="Enable booking widget")
    enable_analytics: bool = Field(default=True, description="Enable analytics")
    enable_voice_agent: bool = Field(default=False, description="Enable voice agent")
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @validator('business_id')
    def validate_business_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('business_id must be a valid UUID')
        return v


class WebsiteGenerationResponse(BaseModel):
    """Response from website generation request."""
    
    success: bool
    job_id: str
    business_id: str
    template_name: str
    environment: str
    
    # URLs
    preview_url: Optional[str] = None
    deployment_url: Optional[str] = None
    
    # Status
    build_status: str
    deployment_status: Optional[str] = None
    
    # Configuration
    business_config: Dict[str, Any]
    deployment_config: Dict[str, Any]
    
    # Timestamps
    created_at: datetime
    estimated_completion: Optional[datetime] = None


class WebsiteGenerationStatus(BaseModel):
    """Status of a website generation job."""
    
    job_id: str
    business_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    current_step: str
    
    # Results
    preview_url: Optional[str] = None
    deployment_url: Optional[str] = None
    build_logs: Optional[List[str]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Error information
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=WebsiteGenerationResponse)
async def generate_business_website(
    request: BusinessWebsiteRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context)
):
    """
    Generate a website for a specific business with custom configuration.
    
    This endpoint creates a complete website build job that:
    1. Fetches business data from the database
    2. Generates business-specific configuration
    3. Builds the Next.js website with proper environment variables
    4. Optionally deploys to Cloudflare Pages
    """
    
    job_id = str(uuid.uuid4())
    
    logger.info(f"Starting website generation job {job_id} for business {request.business_id}")
    
    try:
        # Validate business access
        user_business_id = business_context.get("business_id")
        if user_business_id != request.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to generate websites for this business"
            )
        
        # TODO: Fetch business data from repository
        # business = await business_repository.get_by_id(uuid.UUID(request.business_id))
        # if not business:
        #     raise HTTPException(404, f"Business {request.business_id} not found")
        
        # Mock business data for now
        mock_business_data = {
            "business_id": request.business_id,
            "business_name": request.business_name_override or "Professional Services",
            "phone": request.business_phone_override or "+1-555-123-4567",
            "email": request.business_email_override or "contact@example.com",
            "trade_type": "HVAC",
            "description": "Professional service provider committed to excellence.",
            "service_areas": ["Local Area"],
            "emergency_service": True,
            "years_in_business": 10,
            "license_number": "Licensed & Insured",
            "insurance_verified": True,
            "average_rating": 4.8,
            "total_reviews": 150
        }
        
        # Generate business configuration
        business_config = {
            "businessId": request.business_id,
            "environment": request.environment,
            "businessData": mock_business_data,
            "features": {
                "bookingWidget": request.enable_booking_widget,
                "analytics": request.enable_analytics,
                "voiceAgent": request.enable_voice_agent,
                "errorReporting": request.environment != "development"
            },
            "generatedAt": datetime.utcnow().isoformat()
        }
        
        # Generate deployment configuration
        deployment_config = {
            "environment": request.environment,
            "projectName": request.project_name,
            "customDomain": request.custom_domain,
            "templateName": request.template_name,
            "buildImmediately": request.build_immediately,
            "deployImmediately": request.deploy_immediately
        }
        
        # Create initial job record
        # TODO: Save to database
        job_data = {
            "job_id": job_id,
            "business_id": request.business_id,
            "template_name": request.template_name,
            "environment": request.environment,
            "status": "pending",
            "progress": 0,
            "current_step": "initializing",
            "business_config": business_config,
            "deployment_config": deployment_config,
            "created_at": datetime.utcnow(),
            "created_by": current_user.get("user_id")
        }
        
        # Queue background job if requested
        if request.build_immediately:
            background_tasks.add_task(
                _generate_website_background,
                job_id,
                request,
                business_config,
                deployment_config
            )
        
        return WebsiteGenerationResponse(
            success=True,
            job_id=job_id,
            business_id=request.business_id,
            template_name=request.template_name,
            environment=request.environment,
            build_status="pending" if request.build_immediately else "not_started",
            deployment_status="pending" if request.deploy_immediately else None,
            business_config=business_config,
            deployment_config=deployment_config,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start website generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start website generation: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=WebsiteGenerationStatus)
async def get_generation_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a website generation job."""
    
    try:
        # TODO: Fetch job status from database
        # job = await job_repository.get_by_id(job_id)
        # if not job:
        #     raise HTTPException(404, f"Job {job_id} not found")
        
        # Mock job status for now
        mock_status = WebsiteGenerationStatus(
            job_id=job_id,
            business_id="123e4567-e89b-12d3-a456-426614174000",
            status="completed",
            progress=100,
            current_step="deployment_complete",
            preview_url=f"https://preview-{job_id[:8]}.pages.dev",
            deployment_url=f"https://{job_id[:8]}.hero365.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        return mock_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.post("/deploy-script", response_model=Dict[str, Any])
async def generate_deployment_script(
    request: BusinessWebsiteRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context)
):
    """
    Generate a deployment script for local/CI usage.
    
    Returns the exact command line that can be used to deploy this website
    configuration using the enhanced deployment script.
    """
    
    try:
        # Validate business access
        user_business_id = business_context.get("business_id")
        if user_business_id != request.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to generate deployment scripts for this business"
            )
        
        # Generate deployment command
        cmd_parts = [
            "node scripts/deploy-with-business.js",
            f"--businessId={request.business_id}",
            f"--env={request.environment}"
        ]
        
        if request.project_name:
            cmd_parts.append(f"--project={request.project_name}")
        
        if request.custom_domain:
            cmd_parts.append(f"--domain={request.custom_domain}")
        
        if request.business_name_override:
            cmd_parts.append(f"--businessName='{request.business_name_override}'")
        
        if request.business_phone_override:
            cmd_parts.append(f"--businessPhone='{request.business_phone_override}'")
        
        if request.business_email_override:
            cmd_parts.append(f"--businessEmail='{request.business_email_override}'")
        
        if not request.deploy_immediately:
            cmd_parts.append("--build-only")
        
        deployment_command = " ".join(cmd_parts)
        
        # Generate environment variables
        env_vars = {
            "NEXT_PUBLIC_BUSINESS_ID": request.business_id,
            "NEXT_PUBLIC_ENVIRONMENT": request.environment,
            "NEXT_PUBLIC_BOOKING_WIDGET_ENABLED": str(request.enable_booking_widget).lower(),
            "NEXT_PUBLIC_ANALYTICS_ENABLED": str(request.enable_analytics).lower(),
            "NEXT_PUBLIC_VOICE_AGENT_ENABLED": str(request.enable_voice_agent).lower()
        }
        
        if request.business_name_override:
            env_vars["NEXT_PUBLIC_BUSINESS_NAME"] = request.business_name_override
        if request.business_phone_override:
            env_vars["NEXT_PUBLIC_BUSINESS_PHONE"] = request.business_phone_override
        if request.business_email_override:
            env_vars["NEXT_PUBLIC_BUSINESS_EMAIL"] = request.business_email_override
        
        return {
            "success": True,
            "deployment_command": deployment_command,
            "environment_variables": env_vars,
            "instructions": [
                "1. Navigate to the website-builder directory",
                "2. Ensure you have the required dependencies installed (npm install)",
                "3. Make sure wrangler is configured for Cloudflare Pages",
                "4. Run the deployment command below",
                "5. The script will automatically configure the business ID and deploy"
            ],
            "example_usage": f"cd website-builder && {deployment_command}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate deployment script: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate deployment script: {str(e)}"
        )


async def _generate_website_background(
    job_id: str,
    request: BusinessWebsiteRequest,
    business_config: Dict[str, Any],
    deployment_config: Dict[str, Any]
):
    """
    Background task to generate and optionally deploy a website.
    
    This would typically:
    1. Update job status to "building"
    2. Generate business-specific configuration files
    3. Run the Next.js build process
    4. If deploy_immediately is True, deploy to Cloudflare Pages
    5. Update job status to "completed" or "failed"
    """
    
    logger.info(f"Starting background website generation for job {job_id}")
    
    try:
        # TODO: Implement actual website generation logic
        # This would call the deployment script or use the website builder service
        
        # For now, just log the process
        logger.info(f"Job {job_id}: Generating configuration...")
        logger.info(f"Job {job_id}: Building website...")
        
        if request.deploy_immediately:
            logger.info(f"Job {job_id}: Deploying to {request.environment}...")
        
        logger.info(f"Job {job_id}: Website generation completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id}: Website generation failed: {str(e)}")
        # TODO: Update job status to "failed"


# Additional utility endpoints

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_available_templates():
    """List all available website templates."""
    
    return [
        {
            "name": "professional",
            "display_name": "Professional Services",
            "description": "Clean, professional template for service businesses",
            "features": ["Booking Widget", "Service Showcase", "Customer Reviews", "Contact Forms"],
            "suitable_for": ["HVAC", "Plumbing", "Electrical", "General Services"]
        },
        {
            "name": "elite",
            "display_name": "Elite Professional",
            "description": "Premium template with advanced features",
            "features": ["Advanced Booking", "Analytics", "A/B Testing", "Voice Agent"],
            "suitable_for": ["High-end Services", "Enterprise", "Premium Brands"]
        }
    ]


@router.get("/environments", response_model=List[Dict[str, Any]])
async def list_deployment_environments():
    """List available deployment environments and their configurations."""
    
    return [
        {
            "name": "development",
            "display_name": "Development",
            "description": "Local development and testing",
            "api_url": "http://localhost:8000",
            "features": {
                "analytics": False,
                "error_reporting": False,
                "debug_mode": True
            }
        },
        {
            "name": "staging",
            "display_name": "Staging",
            "description": "Pre-production testing environment",
            "api_url": "https://api-staging.hero365.ai",
            "features": {
                "analytics": True,
                "error_reporting": True,
                "debug_mode": True
            }
        },
        {
            "name": "production",
            "display_name": "Production",
            "description": "Live production environment",
            "api_url": "https://api.hero365.ai",
            "features": {
                "analytics": True,
                "error_reporting": True,
                "debug_mode": False
            }
        }
    ]
