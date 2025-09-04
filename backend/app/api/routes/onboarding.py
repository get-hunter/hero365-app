"""
Onboarding API Routes

Profile-first, activity-driven onboarding endpoints for mobile app.
Enhanced with comprehensive onboarding flow management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from app.api.deps import get_supabase_client, get_current_user
from app.api.dtos.onboarding_dtos import (
    OnboardingSessionRequest, OnboardingSessionResponse,
    ProfileSelectionRequest, ActivitySelectionRequest, BusinessDetailsRequest,
    ServiceTemplateSelectionRequest, CompleteOnboardingRequest,
    OnboardingProfileListResponse, OnboardingActivityListResponse,
    OnboardingValidationResponse, OnboardingCompletionResponse,
    OnboardingProgressResponse
)
from app.application.use_cases.onboarding.onboarding_use_case import OnboardingUseCase
from app.application.services.onboarding_service import OnboardingService
from app.application.services.onboarding_progress_service import OnboardingProgressService
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeProfileRepository, SupabaseTradeActivityRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceTemplateRepository
)
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository

router = APIRouter()


def get_onboarding_use_case(supabase_client = Depends(get_supabase_client)) -> OnboardingUseCase:
    """Dependency to get configured OnboardingUseCase."""
    profile_repository = SupabaseTradeProfileRepository(supabase_client)
    activity_repository = SupabaseTradeActivityRepository(supabase_client)
    service_template_repository = SupabaseServiceTemplateRepository(supabase_client)
    business_repository = SupabaseBusinessRepository(supabase_client)
    
    onboarding_service = OnboardingService(
        profile_repository=profile_repository,
        activity_repository=activity_repository,
        service_template_repository=service_template_repository,
        business_repository=business_repository
    )
    
    return OnboardingUseCase(onboarding_service)


def get_progress_service() -> OnboardingProgressService:
    """Dependency to get OnboardingProgressService."""
    return OnboardingProgressService()


# Session Management

@router.post("/session/start", response_model=OnboardingSessionResponse)
async def start_onboarding_session(
    request: OnboardingSessionRequest = Body(...),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case),
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Start a new onboarding session."""
    
    try:
        response = await onboarding_use_case.start_onboarding_session(request)
        
        # Create progress tracking session
        progress_service.create_session(
            user_id=None,  # Will be set when user authenticates
            session_data={
                'session_id': response.session_id,
                'referral_source': request.referral_source.value if request.referral_source else None,
                'utm_parameters': request.utm_parameters
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start onboarding session: {str(e)}")


@router.get("/session/{session_id}/progress", response_model=OnboardingProgressResponse)
async def get_onboarding_progress(
    session_id: str,
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Get current onboarding progress for a session."""
    
    try:
        progress = progress_service.get_progress(session_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.post("/session/{session_id}/profile", response_model=OnboardingProgressResponse)
async def set_session_profile(
    session_id: str,
    profile: dict = Body(...),
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Set selected profile for the session."""
    
    try:
        from app.api.dtos.onboarding_dtos import OnboardingProfileResponse
        profile_obj = OnboardingProfileResponse(**profile)
        
        success = progress_service.set_profile_selection(session_id, profile_obj)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        progress = progress_service.get_progress(session_id)
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set profile: {str(e)}")


@router.post("/session/{session_id}/activities", response_model=OnboardingProgressResponse)
async def set_session_activities(
    session_id: str,
    activities: List[dict] = Body(...),
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Set selected activities for the session."""
    
    try:
        from app.api.dtos.onboarding_dtos import OnboardingActivityResponse
        activity_objs = [OnboardingActivityResponse(**activity) for activity in activities]
        
        success = progress_service.set_activity_selections(session_id, activity_objs)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        progress = progress_service.get_progress(session_id)
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set activities: {str(e)}")


@router.post("/session/{session_id}/business-details", response_model=OnboardingProgressResponse)
async def set_session_business_details(
    session_id: str,
    details: BusinessDetailsRequest = Body(...),
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Set business details for the session."""
    
    try:
        success = progress_service.set_business_details(session_id, details)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        progress = progress_service.get_progress(session_id)
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set business details: {str(e)}")


# Profile Selection

@router.get("/profiles", response_model=OnboardingProfileListResponse)
async def get_onboarding_profiles(
    search: Optional[str] = Query(None, description="Search in name and synonyms"),
    segments: Optional[List[str]] = Query(None, description="Filter by market segments"),
    popular_only: bool = Query(False, description="Show only popular profiles"),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Get trade profiles for onboarding with enhanced data."""
    
    try:
        # Convert segments to MarketSegment enums if provided
        segment_enums = None
        if segments:
            from app.domain.entities.trade_taxonomy import MarketSegment
            segment_enums = []
            for segment in segments:
                try:
                    segment_enums.append(MarketSegment(segment))
                except ValueError:
                    pass  # Skip invalid segments
        
        request = ProfileSelectionRequest(
            search=search,
            segments=segment_enums,
            popular_only=popular_only
        )
        
        return await onboarding_use_case.get_onboarding_profiles(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch onboarding profiles: {str(e)}")


@router.get("/profiles/popular", response_model=OnboardingProfileListResponse)
async def get_popular_profiles(
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Get only popular profiles for quick selection."""
    
    try:
        return await onboarding_use_case.get_popular_profiles()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular profiles: {str(e)}")


@router.get("/profiles/search", response_model=OnboardingProfileListResponse)
async def search_profiles(
    q: str = Query(..., description="Search term"),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Search profiles by name or synonyms."""
    
    try:
        return await onboarding_use_case.search_profiles(q)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search profiles: {str(e)}")


# Activity Selection

@router.get("/profiles/{trade_slug}/activities", response_model=OnboardingActivityListResponse)
async def get_onboarding_activities_for_trade(
    trade_slug: str,
    search: Optional[str] = Query(None, description="Search in name and synonyms"),
    emergency_only: bool = Query(False, description="Only emergency activities"),
    popular_only: bool = Query(False, description="Only popular activities"),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Get activities for a specific trade profile during onboarding."""
    
    try:
        request = ActivitySelectionRequest(
            trade_slug=trade_slug,
            search=search,
            emergency_only=emergency_only,
            popular_only=popular_only
        )
        
        return await onboarding_use_case.get_onboarding_activities(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activities for trade {trade_slug}: {str(e)}")


@router.get("/profiles/{trade_slug}/activities/popular", response_model=OnboardingActivityListResponse)
async def get_popular_activities_for_trade(
    trade_slug: str,
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Get only popular activities for a trade."""
    
    try:
        return await onboarding_use_case.get_popular_activities_for_trade(trade_slug)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular activities for {trade_slug}: {str(e)}")


@router.get("/profiles/{trade_slug}/activities/emergency", response_model=OnboardingActivityListResponse)
async def get_emergency_activities_for_trade(
    trade_slug: str,
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Get only emergency activities for a trade."""
    
    try:
        return await onboarding_use_case.get_emergency_activities_for_trade(trade_slug)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emergency activities for {trade_slug}: {str(e)}")


@router.get("/profiles/{trade_slug}/activities/search", response_model=OnboardingActivityListResponse)
async def search_activities_for_trade(
    trade_slug: str,
    q: str = Query(..., description="Search term"),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Search activities within a trade."""
    
    try:
        return await onboarding_use_case.search_activities(trade_slug, q)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search activities for {trade_slug}: {str(e)}")


# Validation

@router.post("/validate/profile", response_model=OnboardingValidationResponse)
async def validate_profile_selection(
    profile_slug: str = Body(..., embed=True),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Validate a profile selection during onboarding."""
    
    try:
        return await onboarding_use_case.validate_profile_selection(profile_slug)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate profile: {str(e)}")


@router.post("/validate/activities", response_model=OnboardingValidationResponse)
async def validate_activity_selections(
    trade_slug: str = Body(...),
    activity_slugs: List[str] = Body(...),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Validate activity selections for a trade during onboarding."""
    
    try:
        return await onboarding_use_case.validate_activity_selections(trade_slug, activity_slugs)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate activities: {str(e)}")


@router.post("/validate/business-details", response_model=OnboardingValidationResponse)
async def validate_business_details(
    details: BusinessDetailsRequest = Body(...),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Validate business details during onboarding."""
    
    try:
        return await onboarding_use_case.validate_business_details(details)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate business details: {str(e)}")


@router.post("/validate/complete", response_model=OnboardingValidationResponse)
async def validate_complete_onboarding(
    request: CompleteOnboardingRequest = Body(...),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Validate the complete onboarding request before processing."""
    
    try:
        return await onboarding_use_case.validate_complete_onboarding_request(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate complete onboarding: {str(e)}")


# Completion

@router.post("/complete", response_model=OnboardingCompletionResponse)
async def complete_onboarding(
    request: CompleteOnboardingRequest = Body(...),
    current_user = Depends(get_current_user),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case),
    progress_service: OnboardingProgressService = Depends(get_progress_service)
):
    """Complete the entire onboarding process."""
    
    try:
        response = await onboarding_use_case.complete_onboarding(request, str(current_user.id))
        
        # Update progress tracking if session ID provided
        if request.onboarding_session_id:
            progress_service.complete_onboarding(
                request.onboarding_session_id, 
                response.business_id
            )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete onboarding: {str(e)}")


# Legacy endpoints for backward compatibility

@router.post("/create-business", response_model=OnboardingCompletionResponse)
async def create_business_onboarding_legacy(
    request: CompleteOnboardingRequest = Body(...),
    current_user = Depends(get_current_user),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Legacy endpoint - use /complete instead."""
    
    try:
        return await onboarding_use_case.complete_onboarding(request, str(current_user.id))
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create business: {str(e)}")


# Simplified legacy endpoints for backward compatibility with existing mobile app

@router.post("/validate-profile", response_model=dict)
async def validate_profile_legacy(
    profile_slug: str = Body(..., embed=True),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Legacy profile validation endpoint."""
    
    try:
        validation = await onboarding_use_case.validate_profile_selection(profile_slug)
        return {
            "valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate profile: {str(e)}")


@router.post("/validate-activities", response_model=dict)
async def validate_activities_legacy(
    trade_slug: str = Body(...),
    activity_slugs: List[str] = Body(..., alias="selected_activity_slugs"),
    onboarding_use_case: OnboardingUseCase = Depends(get_onboarding_use_case)
):
    """Legacy activity validation endpoint."""
    
    try:
        validation = await onboarding_use_case.validate_activity_selections(trade_slug, activity_slugs)
        return {
            "valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "count": len(activity_slugs) if validation.is_valid else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate activities: {str(e)}")