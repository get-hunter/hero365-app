"""
Service Discovery API Routes

Public endpoints for discovering service templates and categories.
These don't require business context and are used for onboarding and discovery.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.service_templates.models import (
    ServiceCategory,
    ServiceTemplate
)
from app.infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceCategoryRepository,
    SupabaseServiceTemplateRepository
)
from app.api.deps import get_current_user
from app.core.db import get_supabase_client

router = APIRouter(prefix="/service-templates", tags=["Service Discovery"])

# Dependency to get repositories
def get_category_repo(client=Depends(get_supabase_client)):
    return SupabaseServiceCategoryRepository(client)

def get_template_repo(client=Depends(get_supabase_client)):
    return SupabaseServiceTemplateRepository(client)


# =============================================
# Service Category Discovery
# =============================================

@router.get("/categories", response_model=List[ServiceCategory])
async def list_categories(
    trade_type: str = None,
    category_repo: SupabaseServiceCategoryRepository = Depends(get_category_repo)
):
    """
    Get all available service categories.
    
    Used for business onboarding and service discovery.
    """
    try:
        categories = await category_repo.list_categories(
            trade_types=[trade_type] if trade_type else None,
            is_active=True
        )
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}"
        )


@router.get("/categories/{category_id}", response_model=ServiceCategory)
async def get_category(
    category_id: UUID,
    category_repo: SupabaseServiceCategoryRepository = Depends(get_category_repo)
):
    """Get details of a specific service category."""
    try:
        category = await category_repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service category not found"
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category: {str(e)}"
        )


# =============================================
# Service Template Discovery
# =============================================

@router.get("/templates", response_model=List[ServiceTemplate])
async def list_templates(
    category_id: UUID = None,
    trade_type: str = None,
    is_common: bool = None,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Get available service templates for discovery and adoption.
    
    Used by businesses to browse and adopt standard services.
    """
    try:
        templates = await template_repo.list_templates(
            category_id=category_id,
            trade_types=[trade_type] if trade_type else None,
            is_common=is_common,
            is_active=True
        )
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=ServiceTemplate)
async def get_template(
    template_id: UUID,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """Get detailed information about a specific service template."""
    try:
        template = await template_repo.get_template_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service template not found"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.get("/templates/common/{trade_type}", response_model=List[ServiceTemplate])
async def get_common_templates_for_trade(
    trade_type: str,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """
    Get the most commonly adopted service templates for a specific trade.
    
    Perfect for business onboarding to quickly set up standard services.
    """
    try:
        templates = await template_repo.get_common_templates_for_trade(trade_type)
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get common templates: {str(e)}"
        )


@router.get("/categories/{category_id}/templates", response_model=List[ServiceTemplate]) 
async def get_templates_by_category(
    category_id: UUID,
    trade_type: str = None,
    template_repo: SupabaseServiceTemplateRepository = Depends(get_template_repo)
):
    """Get all service templates in a specific category."""
    try:
        templates = await template_repo.list_templates(
            category_id=category_id,
            trade_types=[trade_type] if trade_type else None,
            is_active=True
        )
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates by category: {str(e)}"
        )
