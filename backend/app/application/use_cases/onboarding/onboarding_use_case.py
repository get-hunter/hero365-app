"""
Onboarding Use Case

Orchestrates the complete onboarding flow using clean architecture principles.
Coordinates between the onboarding service and various repositories.
"""

from typing import List, Tuple
import logging

from app.application.services.onboarding_service import OnboardingService
from app.api.dtos.onboarding_dtos import (
    ProfileSelectionRequest, ActivitySelectionRequest, BusinessDetailsRequest,
    ServiceTemplateSelectionRequest, CompleteOnboardingRequest,
    OnboardingProfileResponse, OnboardingActivityResponse,
    OnboardingValidationResponse, OnboardingCompletionResponse,
    OnboardingStatsResponse, OnboardingSessionRequest, OnboardingSessionResponse,
    OnboardingProfileListResponse, OnboardingActivityListResponse
)

logger = logging.getLogger(__name__)


class OnboardingUseCase:
    """
    Use case for managing the complete onboarding flow.
    
    Provides high-level orchestration for:
    - Session management
    - Profile selection
    - Activity selection  
    - Business creation
    - Template adoption
    - Validation and completion
    """
    
    def __init__(self, onboarding_service: OnboardingService):
        self.onboarding_service = onboarding_service
        logger.info("OnboardingUseCase initialized")
    
    async def start_onboarding_session(
        self, 
        request: OnboardingSessionRequest
    ) -> OnboardingSessionResponse:
        """Start a new onboarding session."""
        logger.info("Starting new onboarding session")
        
        try:
            response = await self.onboarding_service.start_onboarding_session(request)
            logger.info(f"Onboarding session started: {response.session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to start onboarding session: {e}")
            raise
    
    async def get_onboarding_profiles(
        self, 
        request: ProfileSelectionRequest
    ) -> OnboardingProfileListResponse:
        """Get available profiles for onboarding."""
        logger.info(f"Getting onboarding profiles: search='{request.search}', segments={request.segments}")
        
        try:
            profiles, stats = await self.onboarding_service.get_onboarding_profiles(request)
            
            # Count popular profiles
            popular_count = sum(1 for p in profiles if p.is_popular)
            
            response = OnboardingProfileListResponse(
                profiles=profiles,
                total_count=len(profiles),
                popular_count=popular_count,
                stats=stats
            )
            
            logger.info(f"Retrieved {len(profiles)} profiles ({popular_count} popular)")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get onboarding profiles: {e}")
            raise
    
    async def get_onboarding_activities(
        self, 
        request: ActivitySelectionRequest
    ) -> OnboardingActivityListResponse:
        """Get available activities for a trade profile."""
        logger.info(f"Getting activities for trade: {request.trade_slug}")
        
        try:
            activities, profile = await self.onboarding_service.get_onboarding_activities(request)
            
            # Count emergency activities
            emergency_count = sum(1 for a in activities if a.is_emergency)
            
            response = OnboardingActivityListResponse(
                activities=activities,
                total_count=len(activities),
                emergency_count=emergency_count,
                trade_profile=profile
            )
            
            logger.info(f"Retrieved {len(activities)} activities for {request.trade_slug} ({emergency_count} emergency)")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get activities for trade {request.trade_slug}: {e}")
            raise
    
    async def validate_profile_selection(
        self, 
        profile_slug: str
    ) -> OnboardingValidationResponse:
        """Validate a profile selection."""
        logger.info(f"Validating profile selection: {profile_slug}")
        
        try:
            response = await self.onboarding_service.validate_profile_selection(profile_slug)
            
            logger.info(f"Profile validation result: valid={response.is_valid}, "
                       f"errors={len(response.errors)}, warnings={len(response.warnings)}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to validate profile {profile_slug}: {e}")
            raise
    
    async def validate_activity_selections(
        self, 
        trade_slug: str, 
        activity_slugs: List[str]
    ) -> OnboardingValidationResponse:
        """Validate activity selections."""
        logger.info(f"Validating activity selections for {trade_slug}: {activity_slugs}")
        
        try:
            response = await self.onboarding_service.validate_activity_selections(
                trade_slug, activity_slugs
            )
            
            logger.info(f"Activity validation result: valid={response.is_valid}, "
                       f"errors={len(response.errors)}, warnings={len(response.warnings)}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to validate activities for {trade_slug}: {e}")
            raise
    
    async def validate_business_details(
        self, 
        details: BusinessDetailsRequest
    ) -> OnboardingValidationResponse:
        """Validate business details."""
        logger.info(f"Validating business details for: {details.name}")
        
        try:
            response = await self.onboarding_service.validate_business_details(details)
            
            logger.info(f"Business details validation result: valid={response.is_valid}, "
                       f"errors={len(response.errors)}, warnings={len(response.warnings)}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to validate business details: {e}")
            raise
    
    async def complete_onboarding(
        self, 
        request: CompleteOnboardingRequest,
        user_id: str
    ) -> OnboardingCompletionResponse:
        """Complete the entire onboarding process."""
        logger.info(f"Completing onboarding for user {user_id}: "
                   f"trade={request.primary_trade_slug}, "
                   f"activities={len(request.selected_activity_slugs)}, "
                   f"business={request.business_details.name}")
        
        try:
            response = await self.onboarding_service.complete_onboarding(request, user_id)
            
            logger.info(f"Onboarding completed successfully: "
                       f"business_id={response.business_id}, "
                       f"services_created={response.created_services}, "
                       f"templates_adopted={len(response.adopted_templates)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to complete onboarding for user {user_id}: {e}")
            raise
    
    # Convenience methods for step-by-step onboarding
    
    async def get_popular_profiles(self) -> OnboardingProfileListResponse:
        """Get only popular profiles for quick selection."""
        request = ProfileSelectionRequest(popular_only=True)
        return await self.get_onboarding_profiles(request)
    
    async def get_popular_activities_for_trade(
        self, 
        trade_slug: str
    ) -> OnboardingActivityListResponse:
        """Get only popular activities for a trade."""
        request = ActivitySelectionRequest(trade_slug=trade_slug, popular_only=True)
        return await self.get_onboarding_activities(request)
    
    async def get_emergency_activities_for_trade(
        self, 
        trade_slug: str
    ) -> OnboardingActivityListResponse:
        """Get only emergency activities for a trade."""
        request = ActivitySelectionRequest(trade_slug=trade_slug, emergency_only=True)
        return await self.get_onboarding_activities(request)
    
    async def search_profiles(self, search_term: str) -> OnboardingProfileListResponse:
        """Search profiles by name or synonyms."""
        request = ProfileSelectionRequest(search=search_term)
        return await self.get_onboarding_profiles(request)
    
    async def search_activities(
        self, 
        trade_slug: str, 
        search_term: str
    ) -> OnboardingActivityListResponse:
        """Search activities within a trade."""
        request = ActivitySelectionRequest(trade_slug=trade_slug, search=search_term)
        return await self.get_onboarding_activities(request)
    
    # Batch validation methods
    
    async def validate_complete_onboarding_request(
        self, 
        request: CompleteOnboardingRequest
    ) -> OnboardingValidationResponse:
        """Validate the complete onboarding request before processing."""
        logger.info("Validating complete onboarding request")
        
        all_errors = []
        all_warnings = []
        all_suggestions = []
        
        try:
            # Validate profile
            profile_validation = await self.validate_profile_selection(request.primary_trade_slug)
            all_errors.extend(profile_validation.errors)
            all_warnings.extend(profile_validation.warnings)
            all_suggestions.extend(profile_validation.suggestions)
            
            # Validate activities
            activity_validation = await self.validate_activity_selections(
                request.primary_trade_slug, 
                request.selected_activity_slugs
            )
            all_errors.extend(activity_validation.errors)
            all_warnings.extend(activity_validation.warnings)
            all_suggestions.extend(activity_validation.suggestions)
            
            # Validate business details
            details_validation = await self.validate_business_details(request.business_details)
            all_errors.extend(details_validation.errors)
            all_warnings.extend(details_validation.warnings)
            all_suggestions.extend(details_validation.suggestions)
            
            is_valid = len(all_errors) == 0
            
            logger.info(f"Complete validation result: valid={is_valid}, "
                       f"total_errors={len(all_errors)}, total_warnings={len(all_warnings)}")
            
            return OnboardingValidationResponse(
                is_valid=is_valid,
                errors=all_errors,
                warnings=all_warnings,
                suggestions=all_suggestions
            )
            
        except Exception as e:
            logger.error(f"Failed to validate complete onboarding request: {e}")
            raise
