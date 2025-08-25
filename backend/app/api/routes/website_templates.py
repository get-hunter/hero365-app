"""
Website Templates API Routes

API endpoints for dynamic website generation and deployment.
Handles template composition, static site generation, and Cloudflare Pages deployment.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse

from ...domain.entities.website_template import (
    DynamicWebsiteRequest, WebsiteGenerationResponse, WebsiteDeploymentResponse,
    TemplateProps, WebsiteDeployment, BuildStatus, DeploymentType
)
from ...application.services.template_composition_service import TemplateCompositionService
from ...application.services.static_site_builder_service import StaticSiteBuilderService
from ...application.services.cloudflare_pages_deployment_service import CloudflarePagesDeploymentService
from ...application.exceptions.application_exceptions import (
    BusinessNotFoundError, DataCompositionError, BuildError, DeploymentError
)
from supabase import Client
from ...core.config import settings
from ..deps import get_supabase_client

router = APIRouter(prefix="/website-templates", tags=["Website Templates"])

# Global services (will be dependency injected in production)


def get_template_composition_service(
    supabase: Client = Depends(get_supabase_client)
) -> TemplateCompositionService:
    """Get template composition service."""
    return TemplateCompositionService(supabase)


def get_static_site_builder_service() -> StaticSiteBuilderService:
    """Get static site builder service."""
    return StaticSiteBuilderService()


def get_cloudflare_deployment_service() -> CloudflarePagesDeploymentService:
    """Get Cloudflare Pages deployment service."""
    return CloudflarePagesDeploymentService(
        api_token=getattr(settings, 'CLOUDFLARE_API_TOKEN', None),
        account_id=getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', None)
    )


@router.post("/preview", response_model=TemplateProps)
async def preview_website_template(
    request: DynamicWebsiteRequest,
    composition_service: TemplateCompositionService = Depends(get_template_composition_service)
):
    """
    Preview website template data without generating or deploying.
    
    Returns composed template properties that would be used for generation.
    """
    try:
        template_props = await composition_service.compose_template_props(
            business_id=request.business_id,
            template_name=request.template_name,
            include_promos=request.include_promos,
            include_testimonials=request.include_testimonials,
            include_ratings=request.include_ratings,
            include_awards=request.include_awards,
            include_partnerships=request.include_partnerships
        )
        
        # Apply any overrides
        if request.meta_title_override:
            template_props.meta_title = request.meta_title_override
        if request.meta_description_override:
            template_props.meta_description = request.meta_description_override
        
        return template_props
        
    except BusinessNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business {request.business_id} not found"
        )
    except DataCompositionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to compose template data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/generate", response_model=WebsiteGenerationResponse)
async def generate_website(
    request: DynamicWebsiteRequest,
    background_tasks: BackgroundTasks,
    composition_service: TemplateCompositionService = Depends(get_template_composition_service),
    builder_service: StaticSiteBuilderService = Depends(get_static_site_builder_service),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Generate website artifacts and build static site.
    
    Creates a build job and returns job ID for status tracking.
    The actual build happens in the background.
    """
    try:
        # Generate job ID
        job_id = uuid.uuid4()
        
        # Compose template data
        template_props = await composition_service.compose_template_props(
            business_id=request.business_id,
            template_name=request.template_name,
            include_promos=request.include_promos,
            include_testimonials=request.include_testimonials,
            include_ratings=request.include_ratings,
            include_awards=request.include_awards,
            include_partnerships=request.include_partnerships
        )
        
        # Apply any overrides
        if request.meta_title_override:
            template_props.meta_title = request.meta_title_override
        if request.meta_description_override:
            template_props.meta_description = request.meta_description_override
        
        # Create initial deployment record
        deployment = WebsiteDeployment(
            id=job_id,
            business_id=request.business_id,
            template_name=request.template_name,
            deployment_type=request.deployment_type,
            project_name="",  # Will be set during build
            deploy_url="",  # Will be set during build
            custom_domain=request.custom_domain,
            build_status=BuildStatus.PENDING,
            deployed_by="api",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save deployment record to database
        await _save_deployment_record(supabase, deployment)
        
        # Start background build task
        background_tasks.add_task(
            _build_website_task,
            job_id=job_id,
            template_props=template_props,
            builder_service=builder_service,
            supabase=supabase
        )
        
        return WebsiteGenerationResponse(
            job_id=job_id,
            business_id=request.business_id,
            template_props=template_props,
            deployment=deployment
        )
        
    except BusinessNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business {request.business_id} not found"
        )
    except DataCompositionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to compose template data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/deploy", response_model=WebsiteDeploymentResponse)
async def deploy_website(
    request: DynamicWebsiteRequest,
    background_tasks: BackgroundTasks,
    composition_service: TemplateCompositionService = Depends(get_template_composition_service),
    builder_service: StaticSiteBuilderService = Depends(get_static_site_builder_service),
    deployment_service: CloudflarePagesDeploymentService = Depends(get_cloudflare_deployment_service),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Generate and deploy website to Cloudflare Pages.
    
    This is a full end-to-end operation that composes data, builds the site,
    and deploys to Cloudflare Pages.
    """
    try:
        # Generate deployment ID
        deployment_id = uuid.uuid4()
        
        # Compose template data
        template_props = await composition_service.compose_template_props(
            business_id=request.business_id,
            template_name=request.template_name,
            include_promos=request.include_promos,
            include_testimonials=request.include_testimonials,
            include_ratings=request.include_ratings,
            include_awards=request.include_awards,
            include_partnerships=request.include_partnerships
        )
        
        # Apply any overrides
        if request.meta_title_override:
            template_props.meta_title = request.meta_title_override
        if request.meta_description_override:
            template_props.meta_description = request.meta_description_override
        
        # Create initial deployment record
        deployment = WebsiteDeployment(
            id=deployment_id,
            business_id=request.business_id,
            template_name=request.template_name,
            deployment_type=request.deployment_type,
            project_name="",  # Will be set during deployment
            deploy_url="",  # Will be set during deployment
            custom_domain=request.custom_domain,
            build_status=BuildStatus.BUILDING,
            deployed_by="api",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save deployment record to database
        await _save_deployment_record(supabase, deployment)
        
        # Start background deployment task
        background_tasks.add_task(
            _deploy_website_task,
            deployment_id=deployment_id,
            template_props=template_props,
            builder_service=builder_service,
            deployment_service=deployment_service,
            supabase=supabase
        )
        
        return WebsiteDeploymentResponse(
            deployment_id=deployment_id,
            deploy_url="",  # Will be updated when deployment completes
            build_status=BuildStatus.BUILDING
        )
        
    except BusinessNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business {request.business_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=WebsiteDeploymentResponse)
async def get_deployment_status(
    job_id: uuid.UUID,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get deployment status and details.
    
    Returns current status, deployment URL, and performance metrics if available.
    """
    try:
        # Get deployment record from database
        response = supabase.table("website_deployments").select("*").eq(
            "id", str(job_id)
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment {job_id} not found"
            )
        
        deployment_data = response.data[0]
        
        # Extract Lighthouse scores if available
        lighthouse_scores = None
        if deployment_data.get("lighthouse_json"):
            lighthouse_scores = {
                "performance": deployment_data.get("performance_score"),
                "accessibility": deployment_data.get("accessibility_score"),
                "seo": deployment_data.get("seo_score"),
                "best_practices": deployment_data.get("best_practices_score")
            }
        
        return WebsiteDeploymentResponse(
            deployment_id=job_id,
            deploy_url=deployment_data.get("deploy_url", ""),
            build_status=deployment_data.get("build_status", BuildStatus.PENDING),
            lighthouse_scores=lighthouse_scores
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(
    deployment_id: uuid.UUID,
    deployment_service: CloudflarePagesDeploymentService = Depends(get_cloudflare_deployment_service),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a website deployment.
    
    Removes the Cloudflare Pages project and marks the deployment as cancelled.
    """
    try:
        # Get deployment record
        response = supabase.table("website_deployments").select("*").eq(
            "id", str(deployment_id)
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment {deployment_id} not found"
            )
        
        deployment_data = response.data[0]
        project_name = deployment_data.get("project_name")
        
        # Delete Cloudflare Pages project if it exists
        if project_name:
            try:
                await deployment_service.delete_project(project_name)
            except DeploymentError:
                # Project might not exist or already be deleted
                pass
        
        # Update deployment status
        supabase.table("website_deployments").update({
            "build_status": BuildStatus.CANCELLED.value,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(deployment_id)).execute()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Deployment deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Background task functions

async def _build_website_task(
    job_id: uuid.UUID,
    template_props: TemplateProps,
    builder_service: StaticSiteBuilderService,
    supabase: Client
):
    """Background task to build website."""
    try:
        # Update status to building
        await _update_deployment_status(supabase, job_id, BuildStatus.BUILDING)
        
        # Build the website
        build_result = await builder_service.build_static_site(
            template_props=template_props,
            build_id=str(job_id),
            template_name=template_props.template_name
        )
        
        # Update deployment record with build results
        update_data = {
            "build_status": build_result["status"].value,
            "build_log": build_result.get("build_log"),
            "build_duration_seconds": build_result.get("build_time"),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if build_result.get("error"):
            update_data["error_message"] = build_result["error"]
        
        supabase.table("website_deployments").update(update_data).eq(
            "id", str(job_id)
        ).execute()
        
    except Exception as e:
        # Update with error status
        await _update_deployment_status(
            supabase, job_id, BuildStatus.FAILED, error_message=str(e)
        )


async def _deploy_website_task(
    deployment_id: uuid.UUID,
    template_props: TemplateProps,
    builder_service: StaticSiteBuilderService,
    deployment_service: CloudflarePagesDeploymentService,
    supabase: Client
):
    """Background task to build and deploy website."""
    try:
        # Build the website
        build_result = await builder_service.build_static_site(
            template_props=template_props,
            build_id=str(deployment_id),
            template_name=template_props.template_name
        )
        
        if build_result["status"] != BuildStatus.SUCCESS:
            raise BuildError(f"Build failed: {build_result.get('error', 'Unknown error')}")
        
        # Deploy to Cloudflare Pages
        from pathlib import Path
        build_dir = Path(build_result["build_dir"])
        
        deployment = await deployment_service.deploy_to_pages(
            build_dir=build_dir,
            business_name=template_props.business.name,
            deployment_type=DeploymentType.PRODUCTION  # Get from request in real implementation
        )
        
        # Update deployment record with results
        update_data = {
            "project_name": deployment.project_name,
            "deploy_url": deployment.deploy_url,
            "build_id": deployment.build_id,
            "build_status": deployment.build_status.value,
            "build_log": deployment.build_log,
            "build_duration_seconds": build_result.get("build_time"),
            "is_current": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if deployment.error_message:
            update_data["error_message"] = deployment.error_message
        
        supabase.table("website_deployments").update(update_data).eq(
            "id", str(deployment_id)
        ).execute()
        
        # Mark other deployments for this business as not current
        supabase.table("website_deployments").update({
            "is_current": False
        }).eq("business_id", str(template_props.business.id)).neq(
            "id", str(deployment_id)
        ).execute()
        
        # Clean up build directory
        builder_service.cleanup_build(str(deployment_id))
        
    except Exception as e:
        # Update with error status
        await _update_deployment_status(
            supabase, deployment_id, BuildStatus.FAILED, error_message=str(e)
        )


async def _save_deployment_record(supabase: Client, deployment: WebsiteDeployment):
    """Save deployment record to database."""
    deployment_data = {
        "id": str(deployment.id),
        "business_id": str(deployment.business_id),
        "template_name": deployment.template_name,
        "template_version": deployment.template_version,
        "deployment_type": deployment.deployment_type.value,
        "project_name": deployment.project_name,
        "deploy_url": deployment.deploy_url,
        "custom_domain": deployment.custom_domain,
        "build_id": deployment.build_id,
        "build_status": deployment.build_status.value,
        "build_log": deployment.build_log,
        "build_duration_seconds": deployment.build_duration_seconds,
        "is_current": deployment.is_current,
        "error_message": deployment.error_message,
        "metadata": deployment.metadata,
        "deployed_by": deployment.deployed_by,
        "created_at": deployment.created_at.isoformat(),
        "updated_at": deployment.updated_at.isoformat()
    }
    
    supabase.table("website_deployments").insert(deployment_data).execute()


async def _update_deployment_status(
    supabase: Client,
    deployment_id: uuid.UUID,
    status: BuildStatus,
    error_message: Optional[str] = None
):
    """Update deployment status in database."""
    update_data = {
        "build_status": status.value,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if error_message:
        update_data["error_message"] = error_message
    
    supabase.table("website_deployments").update(update_data).eq(
        "id", str(deployment_id)
    ).execute()
