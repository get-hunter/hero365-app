"""Public API routes for website context."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from app.api.dtos.website_context_dtos import (
    WebsiteContextResponse,
    WebsiteContextRequest
)
from app.application.services.website_context_service import WebsiteContextService
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeActivityRepository,
    SupabaseTradeProfileRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import SupabaseServiceTemplateRepository
from app.api.deps import get_supabase_client

router = APIRouter()


def get_website_context_service(supabase_client=Depends(get_supabase_client)) -> WebsiteContextService:
    """Dependency to get WebsiteContextService."""
    business_repo = SupabaseBusinessRepository(supabase_client)
    trade_activity_repo = SupabaseTradeActivityRepository(supabase_client)
    trade_profile_repo = SupabaseTradeProfileRepository(supabase_client)
    service_template_repo = SupabaseServiceTemplateRepository(supabase_client)
    
    return WebsiteContextService(
        supabase_client=supabase_client,
        cache_adapter=None  # TODO: Add Redis cache when available
    )


@router.get("/context/{business_id}", response_model=WebsiteContextResponse)
async def get_website_context(
    business_id: str = Path(..., description="Business ID"),
    include_templates: bool = Query(True, description="Include service templates"),
    include_trades: bool = Query(True, description="Include trade information"),
    activity_limit: Optional[int] = Query(None, description="Limit number of activities", ge=1, le=100),
    template_limit: Optional[int] = Query(None, description="Limit number of templates", ge=1, le=100),
    website_context_service: WebsiteContextService = Depends(get_website_context_service)
):
    """
    Get complete website context for a business.
    
    This endpoint aggregates all data needed for website generation:
    - Business information (name, contact, address, service areas)
    - Selected activities with booking fields
    - Service templates with pricing
    - Trade information
    
    This replaces multiple API calls with a single optimized request.
    """
    try:
        request = WebsiteContextRequest(
            include_templates=include_templates,
            include_trades=include_trades,
            activity_limit=activity_limit,
            template_limit=template_limit
        )
        
        context = await website_context_service.get_comprehensive_context(business_id)
        
        if not context:
            raise HTTPException(
                status_code=404,
                detail=f"Website context not found for business: {business_id}"
            )
        
        # Add caching headers for performance
        response = JSONResponse(
            content=context.model_dump(),
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "ETag": f'"{business_id}-{context.metadata.get("generated_at", "")}"',
                "Vary": "Accept-Encoding"
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving website context: {str(e)}"
        )


@router.get("/context/{business_id}/activities", response_model=dict)
async def get_website_activities_only(
    business_id: str = Path(..., description="Business ID"),
    limit: Optional[int] = Query(None, description="Limit number of activities", ge=1, le=100),
    website_context_service: WebsiteContextService = Depends(get_website_context_service)
):
    """
    Get only activities for a business (lightweight endpoint).
    
    Useful when you only need activity information without full context.
    """
    try:
        request = WebsiteContextRequest(
            include_templates=False,
            include_trades=False,
            activity_limit=limit
        )
        
        context = await website_context_service.get_comprehensive_context(business_id)
        
        if not context:
            raise HTTPException(
                status_code=404,
                detail=f"Business not found: {business_id}"
            )
        
        return {
            "business_id": business_id,
            "activities": context.activities,
            "total_activities": len(context.activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving activities: {str(e)}"
        )


@router.get("/context/{business_id}/summary", response_model=dict)
async def get_website_summary(
    business_id: str = Path(..., description="Business ID"),
    website_context_service: WebsiteContextService = Depends(get_website_context_service)
):
    """
    Get website summary (business info + counts).
    
    Lightweight endpoint for basic website information.
    """
    try:
        request = WebsiteContextRequest(
            include_templates=False,
            include_trades=False,
            activity_limit=0  # Don't fetch full activity data
        )
        
        context = await website_context_service.get_comprehensive_context(business_id)
        
        if not context:
            raise HTTPException(
                status_code=404,
                detail=f"Business not found: {business_id}"
            )
        
        return {
            "business": context.business,
            "metadata": context.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving website summary: {str(e)}"
        )
