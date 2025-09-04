"""API routes for activity content packs and business activity data."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.api.dtos.activity_content_dtos import (
    ActivityContentPackResponse,
    ActivityContentPackListResponse,
    BusinessActivityDataResponse,
    ActivityPageDataResponse
)
from app.application.services.activity_content_service import ActivityContentService
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeActivityRepository,
    SupabaseTradeProfileRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import SupabaseServiceTemplateRepository
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository
from app.api.deps import get_supabase_client

router = APIRouter(prefix="/activity-content", tags=["Activity Content"])


def get_activity_content_service(supabase_client=Depends(get_supabase_client)) -> ActivityContentService:
    """Dependency to get ActivityContentService."""
    trade_activity_repo = SupabaseTradeActivityRepository(supabase_client)
    trade_profile_repo = SupabaseTradeProfileRepository(supabase_client)
    service_template_repo = SupabaseServiceTemplateRepository(supabase_client)
    business_repo = SupabaseBusinessRepository(supabase_client)
    
    return ActivityContentService(
        trade_activity_repository=trade_activity_repo,
        trade_profile_repository=trade_profile_repo,
        service_template_repository=service_template_repo,
        business_repository=business_repo
    )


@router.get("/content-packs", response_model=ActivityContentPackListResponse)
async def list_activity_content_packs(
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Get list of all available activity content packs."""
    activity_slugs = activity_content_service.get_available_activity_slugs()
    
    return ActivityContentPackListResponse(
        activity_slugs=activity_slugs,
        total_count=len(activity_slugs)
    )


@router.get("/content-packs/{activity_slug}", response_model=ActivityContentPackResponse)
async def get_activity_content_pack(
    activity_slug: str = Path(..., description="Activity slug"),
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Get content pack for a specific activity."""
    content_pack = activity_content_service.get_content_pack(activity_slug)
    
    if not content_pack:
        raise HTTPException(
            status_code=404,
            detail=f"Content pack not found for activity: {activity_slug}"
        )
    
    return content_pack


@router.get("/business/{business_id}/activities/{activity_slug}", response_model=BusinessActivityDataResponse)
async def get_business_activity_data(
    business_id: str = Path(..., description="Business ID"),
    activity_slug: str = Path(..., description="Activity slug"),
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Get business-specific activity data including service templates and booking fields."""
    activity_data = await activity_content_service.get_business_activity_data(business_id, activity_slug)
    
    if not activity_data:
        raise HTTPException(
            status_code=404,
            detail=f"Activity data not found for business {business_id} and activity {activity_slug}"
        )
    
    return activity_data


@router.get("/business/{business_id}/activities/{activity_slug}/page-data", response_model=ActivityPageDataResponse)
async def get_activity_page_data(
    business_id: str = Path(..., description="Business ID"),
    activity_slug: str = Path(..., description="Activity slug"),
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Get complete activity page data including content pack, business data, and activity information."""
    page_data = await activity_content_service.get_activity_page_data(business_id, activity_slug)
    
    if not page_data:
        raise HTTPException(
            status_code=404,
            detail=f"Page data not found for business {business_id} and activity {activity_slug}"
        )
    
    return page_data


# Public endpoints for website builder (no authentication required)
@router.get("/public/content-packs/{activity_slug}", response_model=ActivityContentPackResponse, tags=["Public"])
async def get_public_activity_content_pack(
    activity_slug: str = Path(..., description="Activity slug"),
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Public endpoint to get content pack for a specific activity (for website builder)."""
    content_pack = activity_content_service.get_content_pack(activity_slug)
    
    if not content_pack:
        raise HTTPException(
            status_code=404,
            detail=f"Content pack not found for activity: {activity_slug}"
        )
    
    return content_pack


@router.get("/public/business/{business_id}/activities/{activity_slug}/page-data", response_model=ActivityPageDataResponse, tags=["Public"])
async def get_public_activity_page_data(
    business_id: str = Path(..., description="Business ID"),
    activity_slug: str = Path(..., description="Activity slug"),
    activity_content_service: ActivityContentService = Depends(get_activity_content_service)
):
    """Public endpoint to get complete activity page data (for website builder)."""
    page_data = await activity_content_service.get_activity_page_data(business_id, activity_slug)
    
    if not page_data:
        raise HTTPException(
            status_code=404,
            detail=f"Page data not found for business {business_id} and activity {activity_slug}"
        )
    
    return page_data
