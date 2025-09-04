"""
Trade Taxonomy API Routes

Provides endpoints for trade profiles and activities management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.domain.entities.trade_taxonomy import (
    TradeProfile,
    TradeActivity,
    MarketSegment,
    TradeProfileListRequest,
    TradeActivityListRequest,
    TradeProfileWithActivities,
    ActivityWithTemplates
)
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeProfileRepository,
    SupabaseTradeActivityRepository
)
from app.api.deps import get_supabase_client

router = APIRouter()


# Response Models
class TradeProfileResponse(BaseModel):
    """Response model for trade profile."""
    slug: str
    name: str
    synonyms: List[str]
    segments: MarketSegment
    icon: Optional[str] = None
    description: Optional[str] = None


class TradeActivityResponse(BaseModel):
    """Response model for trade activity."""
    id: str
    trade_slug: str
    slug: str
    name: str
    synonyms: List[str]
    tags: List[str]
    default_booking_fields: List[dict]
    required_booking_fields: List[dict]


class TradeProfileWithActivitiesResponse(BaseModel):
    """Response model for trade profile with activities."""
    profile: TradeProfileResponse
    activities: List[TradeActivityResponse]


class ActivityWithTemplatesResponse(BaseModel):
    """Response model for activity with service templates."""
    activity: TradeActivityResponse
    templates: List[dict]  # Simplified for now


# Trade Profiles Endpoints
@router.get("/profiles", response_model=List[TradeProfileResponse])
async def list_trade_profiles(
    segments: Optional[List[MarketSegment]] = Query(None, description="Filter by market segments"),
    search: Optional[str] = Query(None, description="Search in name and synonyms"),
    limit: Optional[int] = Query(50, le=100, description="Maximum number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    order_by: Optional[str] = Query("name", description="Field to order by"),
    order_desc: bool = Query(False, description="Order in descending order"),
    supabase_client = Depends(get_supabase_client)
):
    """
    Get all trade profiles with optional filtering and pagination.
    
    This endpoint provides the canonical list of trade profiles that businesses
    can select from during onboarding.
    """
    try:
        repo = SupabaseTradeProfileRepository(supabase_client)
        request = TradeProfileListRequest(
            segments=segments,
            search=search,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
        
        profiles = await repo.get_all_profiles(request)
        
        return [
            TradeProfileResponse(
                slug=profile.slug,
                name=profile.name,
                synonyms=profile.synonyms,
                segments=profile.segments,
                icon=profile.icon,
                description=profile.description
            )
            for profile in profiles
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trade profiles: {str(e)}")


@router.get("/profiles/{slug}", response_model=TradeProfileResponse)
async def get_trade_profile(
    slug: str,
    supabase_client = Depends(get_supabase_client)
):
    """Get a specific trade profile by slug."""
    try:
        repo = SupabaseTradeProfileRepository(supabase_client)
        profile = await repo.get_profile_by_slug(slug)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Trade profile not found")
        
        return TradeProfileResponse(
            slug=profile.slug,
            name=profile.name,
            synonyms=profile.synonyms,
            segments=profile.segments,
            icon=profile.icon,
            description=profile.description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trade profile: {str(e)}")


@router.get("/profiles-with-activities", response_model=List[TradeProfileWithActivitiesResponse])
async def list_profiles_with_activities(
    segments: Optional[List[MarketSegment]] = Query(None, description="Filter by market segments"),
    search: Optional[str] = Query(None, description="Search in name and synonyms"),
    limit: Optional[int] = Query(20, le=50, description="Maximum number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    supabase_client = Depends(get_supabase_client)
):
    """
    Get trade profiles with their associated activities.
    
    This endpoint is useful for onboarding flows where users need to see
    both the trade profile and available activities in one request.
    """
    try:
        repo = SupabaseTradeProfileRepository(supabase_client)
        request = TradeProfileListRequest(
            segments=segments,
            search=search,
            limit=limit,
            offset=offset
        )
        
        profiles_with_activities = await repo.get_profiles_with_activities(request)
        
        return [
            TradeProfileWithActivitiesResponse(
                profile=TradeProfileResponse(
                    slug=item.profile.slug,
                    name=item.profile.name,
                    synonyms=item.profile.synonyms,
                    segments=item.profile.segments,
                    icon=item.profile.icon,
                    description=item.profile.description
                ),
                activities=[
                    TradeActivityResponse(
                        id=str(activity.id),
                        trade_slug=activity.trade_slug,
                        slug=activity.slug,
                        name=activity.name,
                        synonyms=activity.synonyms,
                        tags=activity.tags,
                        default_booking_fields=[field.dict() for field in activity.default_booking_fields],
                        required_booking_fields=[field.dict() for field in activity.required_booking_fields]
                    )
                    for activity in item.activities
                ]
            )
            for item in profiles_with_activities
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profiles with activities: {str(e)}")


# Trade Activities Endpoints
@router.get("/profiles/{trade_slug}/activities", response_model=List[TradeActivityResponse])
async def list_trade_activities(
    trade_slug: str,
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search in name and synonyms"),
    limit: Optional[int] = Query(50, le=100, description="Maximum number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    order_by: Optional[str] = Query("name", description="Field to order by"),
    order_desc: bool = Query(False, description="Order in descending order"),
    supabase_client = Depends(get_supabase_client)
):
    """
    Get activities for a specific trade profile.
    
    This endpoint provides the activities that businesses can select
    for a given trade profile during onboarding.
    """
    try:
        repo = SupabaseTradeActivityRepository(supabase_client)
        request = TradeActivityListRequest(
            tags=tags,
            search=search,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
        
        activities = await repo.get_activities_by_trade(trade_slug, request)
        
        return [
            TradeActivityResponse(
                id=str(activity.id),
                trade_slug=activity.trade_slug,
                slug=activity.slug,
                name=activity.name,
                synonyms=activity.synonyms,
                tags=activity.tags,
                default_booking_fields=[field.dict() for field in activity.default_booking_fields],
                required_booking_fields=[field.dict() for field in activity.required_booking_fields]
            )
            for activity in activities
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trade activities: {str(e)}")


@router.get("/activities/{slug}", response_model=TradeActivityResponse)
async def get_trade_activity(
    slug: str,
    supabase_client = Depends(get_supabase_client)
):
    """Get a specific trade activity by slug."""
    try:
        repo = SupabaseTradeActivityRepository(supabase_client)
        activity = await repo.get_activity_by_slug(slug)
        
        if not activity:
            raise HTTPException(status_code=404, detail="Trade activity not found")
        
        return TradeActivityResponse(
            id=str(activity.id),
            trade_slug=activity.trade_slug,
            slug=activity.slug,
            name=activity.name,
            synonyms=activity.synonyms,
            tags=activity.tags,
            default_booking_fields=[field.dict() for field in activity.default_booking_fields],
            required_booking_fields=[field.dict() for field in activity.required_booking_fields]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trade activity: {str(e)}")


@router.get("/profiles/{trade_slug}/activities-with-templates", response_model=List[ActivityWithTemplatesResponse])
async def list_activities_with_templates(
    trade_slug: str,
    supabase_client = Depends(get_supabase_client)
):
    """
    Get activities with their associated service templates.
    
    This endpoint is useful for understanding what service templates
    are available for each activity in a trade.
    """
    try:
        repo = SupabaseTradeActivityRepository(supabase_client)
        activities_with_templates = await repo.get_activities_with_templates(trade_slug)
        
        return [
            ActivityWithTemplatesResponse(
                activity=TradeActivityResponse(
                    id=str(item.activity.id),
                    trade_slug=item.activity.trade_slug,
                    slug=item.activity.slug,
                    name=item.activity.name,
                    synonyms=item.activity.synonyms,
                    tags=item.activity.tags,
                    default_booking_fields=[field.dict() for field in item.activity.default_booking_fields],
                    required_booking_fields=[field.dict() for field in item.activity.required_booking_fields]
                ),
                templates=item.templates
            )
            for item in activities_with_templates
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activities with templates: {str(e)}")
