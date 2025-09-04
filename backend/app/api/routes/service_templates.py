"""
Service Template API Routes

REST API endpoints for managing service templates, categories, and business services.
Supports the new service template system that eliminates manual service creation.
"""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domain.service_templates.models import (
    ServiceCategory,
    ServiceTemplate,
    BusinessService,
    ServiceTemplateListRequest,
    AdoptServiceTemplateRequest,
    CreateCustomServiceRequest,
    BulkAdoptServicesRequest,
    ServiceCategoryWithServices,
    ServiceTemplateWithStats,
    BusinessServiceWithTemplate
)
from pydantic import BaseModel, Field
from app.infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceCategoryRepository,
    SupabaseServiceTemplateRepository,
    SupabaseBusinessServiceRepository,
    SupabaseServiceTemplateAdoptionRepository
)
from app.api.deps import get_current_user, get_business_context
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    DomainValidationError
)
from app.core.db import get_supabase_client

router = APIRouter(prefix="/services", tags=["Services"])

# Dependency to get repositories
def get_category_repo(client=Depends(get_supabase_client)):
    return SupabaseServiceCategoryRepository(client)

def get_template_repo(client=Depends(get_supabase_client)):
    return SupabaseServiceTemplateRepository(client)

def get_business_service_repo(client=Depends(get_supabase_client)):
    return SupabaseBusinessServiceRepository(client)

def get_adoption_repo(client=Depends(get_supabase_client)):
    return SupabaseServiceTemplateAdoptionRepository(client)


# =============================================
# Business Services Endpoints
# =============================================

@router.get("", response_model=List[BusinessService])
async def list_services(
    category_id: UUID = Query(None, description="Filter by category"),
    is_active: bool = Query(True, description="Filter by active status"),
    is_featured: bool = Query(None, description="Filter by featured status"),
    include_template: bool = Query(False, description="Include template information"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """
    List all services for a business.
    
    This replaces the old products endpoint for service listings.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        services = await business_service_repo.list_business_services(
            business_id=business_id,
            category_id=category_id,
            is_active=is_active,
            is_featured=is_featured,
            include_template=include_template
        )
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list business services: {str(e)}"
        )


@router.get("/{service_id}", response_model=BusinessService)
async def get_service(
    service_id: UUID,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """Get detailed information about a specific business service."""
    try:
        business_id = UUID(business_context["business_id"])
        
        service = await business_service_repo.get_business_service_by_id(business_id, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business service not found"
            )
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business service: {str(e)}"
        )


@router.post("/adopt-template", response_model=BusinessService)
async def adopt_template(
    request: AdoptServiceTemplateRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """
    Adopt a service template with optional customizations.
    
    This is the primary way businesses add new services to their catalog.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        business_service = await business_service_repo.adopt_service_template(
            business_id=business_id,
            template_id=request.template_id,
            customizations=request.customizations
        )
        return business_service
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adopt service template: {str(e)}"
        )


# New slug-based adoption models
class AdoptTemplateBySlugRequest(BaseModel):
    """Request to adopt a service template by slug."""
    template_slug: str = Field(..., description="Template slug to adopt")
    activity_slug: str = Field(None, description="Activity slug for validation")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Template customizations")


class BulkAdoptTemplatesRequest(BaseModel):
    """Request to adopt multiple templates for an activity."""
    activity_slug: str = Field(..., description="Activity slug")
    template_slugs: List[str] = Field(..., description="List of template slugs to adopt")
    customizations: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Per-template customizations")


class ActivityTemplatesResponse(BaseModel):
    """Response with templates available for an activity."""
    activity_slug: str
    templates: List[ServiceTemplate]
    total_count: int


@router.post("/adopt-by-slug", response_model=BusinessService)
async def adopt_template_by_slug(
    request: AdoptTemplateBySlugRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Adopt a service template by slug with activity validation.
    
    This is the new activity-driven way to adopt service templates.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        business_service = await template_repo.adopt_service_template_by_slug(
            business_id=business_id,
            template_slug=request.template_slug,
            activity_slug=request.activity_slug,
            customizations=request.customizations
        )
        return business_service
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adopt service template: {str(e)}"
        )


@router.get("/activity/{activity_slug}/templates", response_model=ActivityTemplatesResponse)
async def get_templates_for_activity(
    activity_slug: str,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Get all service templates available for a specific activity.
    
    This endpoint helps businesses discover what services they can offer
    for their selected activities.
    """
    try:
        templates = await template_repo.get_templates_for_activity(activity_slug)
        
        return ActivityTemplatesResponse(
            activity_slug=activity_slug,
            templates=templates,
            total_count=len(templates)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates for activity: {str(e)}"
        )


@router.post("/bulk-adopt-for-activity", response_model=List[BusinessService])
async def bulk_adopt_templates_for_activity(
    request: BulkAdoptTemplatesRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Adopt multiple service templates for an activity in bulk.
    
    This is useful for onboarding when businesses want to quickly
    adopt all recommended services for an activity.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        business_services = await template_repo.bulk_adopt_templates_for_activity(
            business_id=business_id,
            activity_slug=request.activity_slug,
            template_slugs=request.template_slugs,
            customizations=request.customizations
        )
        return business_services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk adopt templates: {str(e)}"
        )


@router.get("/adopted-templates", response_model=List[Dict])
async def get_adopted_templates(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Get all templates adopted by the current business.
    
    Shows the adoption history and current template usage.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        adopted_templates = await template_repo.get_adopted_templates_for_business(business_id)
        return adopted_templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get adopted templates: {str(e)}"
        )


@router.get("/template/{template_slug}", response_model=ServiceTemplate)
async def get_template_by_slug(
    template_slug: str,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Get a service template by slug.
    
    Useful for previewing template details before adoption.
    """
    try:
        template = await template_repo.get_template_by_slug(template_slug)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with slug '{template_slug}' not found"
            )
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.post("/custom", response_model=BusinessService)
async def create_custom_service(
    request: CreateCustomServiceRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """
    Create a completely custom service (not from a template).
    
    Use this when businesses need services not covered by templates.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        service_data = {
            'business_id': business_id,
            'template_id': None,  # Custom service
            'category_id': request.category_id,
            'name': request.name,
            'description': request.description,
            'pricing_model': request.pricing_model,
            'unit_price': request.unit_price,
            'minimum_price': request.minimum_price,
            'unit_of_measure': request.unit_of_measure,
            'estimated_duration_hours': request.estimated_duration_hours,
            'is_emergency': request.is_emergency,
            'requires_booking': request.requires_booking,
            'service_areas': request.service_areas,
            'warranty_terms': request.warranty_terms,
            'terms_and_conditions': request.terms_and_conditions,
            'custom_fields': request.custom_fields,
            'is_active': True,
            'is_featured': False
        }
        
        business_service = await business_service_repo.create_business_service(service_data)
        return business_service
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom service: {str(e)}"
        )


@router.put("/{service_id}", response_model=BusinessService)
async def update_service(
    service_id: UUID,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """Update an existing business service."""
    try:
        business_id = UUID(business_context["business_id"])
        
        # Remove fields that shouldn't be updated directly
        forbidden_fields = ['id', 'business_id', 'template_id', 'created_at']
        for field in forbidden_fields:
            update_data.pop(field, None)
        
        business_service = await business_service_repo.update_business_service(
            business_id=business_id,
            service_id=service_id,
            update_data=update_data
        )
        
        if not business_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business service not found"
            )
        
        return business_service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business service: {str(e)}"
        )


@router.delete("/{service_id}")
async def delete_service(
    service_id: UUID,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """Delete a business service."""
    try:
        business_id = UUID(business_context["business_id"])
        
        deleted = await business_service_repo.delete_business_service(business_id, service_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business service not found"
            )
        
        return {"detail": "Service deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business service: {str(e)}"
        )


# =============================================
# Business Onboarding Endpoints
# =============================================

@router.post("/bulk-adopt", response_model=List[BusinessService])
async def bulk_adopt_services(
    request: BulkAdoptServicesRequest,
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    business_service_repo: SupabaseBusinessServiceRepository = Depends(get_business_service_repo)
):
    """
    Adopt multiple service templates at once.
    
    Useful for business onboarding to quickly set up common services.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        adopted_services = []
        errors = []
        
        for adoption_request in request.template_adoptions:
            try:
                business_service = await business_service_repo.adopt_service_template(
                    business_id=business_id,
                    template_id=adoption_request.template_id,
                    customizations=adoption_request.customizations
                )
                adopted_services.append(business_service)
            except Exception as e:
                errors.append({
                    "template_id": str(adoption_request.template_id),
                    "error": str(e)
                })
        
        # If there were errors but some successes, return partial success
        if errors and adopted_services:
            raise HTTPException(
                status_code=status.HTTP_207_MULTI_STATUS,
                detail={
                    "message": "Some services were adopted successfully, but there were errors",
                    "adopted_services": len(adopted_services),
                    "errors": errors,
                    "services": adopted_services
                }
            )
        elif errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Failed to adopt any services",
                    "errors": errors
                }
            )
        
        return adopted_services
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk adopt services: {str(e)}"
        )


# =============================================
# Website Generation Support Endpoints
# =============================================

@router.get("/categories-with-services", response_model=List[ServiceCategoryWithServices])
async def get_categories_with_services(
    trade_types: List[str] = Query(None, description="Filter by trade types"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    category_repo: SupabaseServiceCategoryRepository = Depends(get_category_repo)
):
    """
    Get service categories with their associated services for a business.
    
    This endpoint is specifically designed for website generation to create
    dynamic navigation and service pages.
    """
    try:
        business_id = UUID(business_context["business_id"])
        
        categories = await category_repo.get_categories_with_services(
            business_id=business_id,
            trade_types=trade_types
        )
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories with services: {str(e)}"
        )
