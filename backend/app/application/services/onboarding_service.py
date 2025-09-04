"""
Onboarding Service

Business logic for the profile-first, activity-driven onboarding flow.
Handles validation, recommendations, and orchestration of onboarding steps.
"""

import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.domain.entities.business import Business, CompanySize, MarketFocus
from app.domain.entities.trade_taxonomy import TradeProfile, TradeActivity, MarketSegment
from app.api.dtos.onboarding_dtos import (
    OnboardingStep, OnboardingProfileResponse, OnboardingActivityResponse,
    ProfileSelectionRequest, ActivitySelectionRequest, BusinessDetailsRequest,
    ServiceTemplateSelectionRequest, CompleteOnboardingRequest,
    OnboardingProgressResponse, OnboardingValidationResponse,
    OnboardingCompletionResponse, OnboardingStatsResponse,
    OnboardingSessionResponse, OnboardingSessionRequest
)
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeProfileRepository, SupabaseTradeActivityRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceTemplateRepository
)
from app.infrastructure.database.repositories.supabase_business_repository import (
    SupabaseBusinessRepository
)

logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Service for managing the onboarding flow.
    
    Provides business logic for:
    - Profile selection and recommendations
    - Activity selection and validation
    - Business creation and setup
    - Service template adoption
    - Progress tracking and validation
    """
    
    def __init__(
        self,
        profile_repository: SupabaseTradeProfileRepository,
        activity_repository: SupabaseTradeActivityRepository,
        service_template_repository: SupabaseServiceTemplateRepository,
        business_repository: SupabaseBusinessRepository
    ):
        self.profile_repository = profile_repository
        self.activity_repository = activity_repository
        self.service_template_repository = service_template_repository
        self.business_repository = business_repository
        
        # Popular profiles based on market data
        self.popular_profiles = {
            'hvac', 'plumbing', 'electrical', 'roofing', 'general-contractor',
            'landscaping-gardening', 'painting-decorating'
        }
        
        # Popular activities by trade
        self.popular_activities = {
            'hvac': ['ac-repair', 'furnace-repair', 'hvac-maintenance'],
            'plumbing': ['drain-cleaning', 'pipe-repair', 'water-heater-service'],
            'electrical': ['electrical-repair', 'panel-upgrade'],
            'roofing': ['roof-repair', 'roof-installation']
        }
        
        logger.info("OnboardingService initialized")
    
    async def start_onboarding_session(
        self, 
        request: OnboardingSessionRequest
    ) -> OnboardingSessionResponse:
        """Start a new onboarding session."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Get initial stats
        profiles_count = await self._get_profiles_count()
        
        return OnboardingSessionResponse(
            session_id=session_id,
            expires_at=expires_at.isoformat(),
            current_step=OnboardingStep.PROFILE_SELECTION,
            available_profiles_count=profiles_count,
            estimated_completion_time="5-10 minutes",
            analytics_enabled=True
        )
    
    async def get_onboarding_profiles(
        self, 
        request: ProfileSelectionRequest
    ) -> Tuple[List[OnboardingProfileResponse], OnboardingStatsResponse]:
        """Get available profiles for onboarding with enhanced data."""
        
        # Build profile list request
        from app.domain.entities.trade_taxonomy import TradeProfileListRequest
        profile_request = TradeProfileListRequest(
            search=request.search,
            segments=request.segments,
            limit=50,
            offset=0
        )
        
        # Get profiles from repository
        profiles, total_count = await self.profile_repository.list_profiles(profile_request)
        
        # Convert to onboarding responses with enhanced data
        onboarding_profiles = []
        popular_profiles = []
        
        for profile in profiles:
            # Get activity count for this profile
            activity_count = await self._get_activity_count_for_profile(profile.slug)
            
            # Check if popular
            is_popular = profile.slug in self.popular_profiles
            
            onboarding_profile = OnboardingProfileResponse(
                slug=profile.slug,
                name=profile.name,
                synonyms=profile.synonyms,
                segments=profile.segments,
                icon=profile.icon,
                description=profile.description,
                activity_count=activity_count,
                is_popular=is_popular,
                estimated_setup_time=self._estimate_setup_time(activity_count)
            )
            
            onboarding_profiles.append(onboarding_profile)
            
            if is_popular and not request.popular_only:
                popular_profiles.append(onboarding_profile)
        
        # Filter for popular only if requested
        if request.popular_only:
            onboarding_profiles = [p for p in onboarding_profiles if p.is_popular]
        
        # Create stats
        stats = OnboardingStatsResponse(
            total_profiles=total_count,
            popular_profiles=popular_profiles[:5],  # Top 5 popular
            total_activities=await self._get_total_activities_count(),
            emergency_activities=await self._get_emergency_activities_count(),
            total_templates=await self._get_total_templates_count(),
            popular_templates=await self._get_popular_templates_count(),
            average_completion_time="7 minutes",
            completion_rate=0.85
        )
        
        return onboarding_profiles, stats
    
    async def get_onboarding_activities(
        self, 
        request: ActivitySelectionRequest
    ) -> Tuple[List[OnboardingActivityResponse], OnboardingProfileResponse]:
        """Get available activities for a trade profile."""
        
        # Get the trade profile
        profile = await self.profile_repository.get_profile_by_slug(request.trade_slug)
        if not profile:
            raise ValueError(f"Trade profile not found: {request.trade_slug}")
        
        # Get activities for this trade
        activities = await self.activity_repository.get_activities_by_trade(request.trade_slug)
        
        # Convert to onboarding responses with enhanced data
        onboarding_activities = []
        popular_activity_slugs = self.popular_activities.get(request.trade_slug, [])
        
        for activity in activities:
            # Get template count for this activity
            template_count = await self._get_template_count_for_activity(activity.slug)
            
            # Check if popular
            is_popular = activity.slug in popular_activity_slugs
            
            # Check if emergency (based on tags or name)
            is_emergency = 'emergency' in activity.tags or 'emergency' in activity.name.lower()
            
            onboarding_activity = OnboardingActivityResponse(
                id=str(activity.id),
                slug=activity.slug,
                name=activity.name,
                description=f"Professional {activity.name.lower()} services",
                synonyms=activity.synonyms,
                tags=activity.tags,
                is_popular=is_popular,
                is_emergency=is_emergency,
                template_count=template_count,
                estimated_revenue=self._estimate_revenue_potential(activity.slug, is_emergency)
            )
            
            onboarding_activities.append(onboarding_activity)
        
        # Filter for emergency or popular if requested
        if request.emergency_only:
            onboarding_activities = [a for a in onboarding_activities if a.is_emergency]
        elif request.popular_only:
            onboarding_activities = [a for a in onboarding_activities if a.is_popular]
        
        # Sort by popularity, then by name
        onboarding_activities.sort(key=lambda x: (not x.is_popular, x.name))
        
        # Convert profile to onboarding response
        activity_count = len(onboarding_activities)
        onboarding_profile = OnboardingProfileResponse(
            slug=profile.slug,
            name=profile.name,
            synonyms=profile.synonyms,
            segments=profile.segments,
            icon=profile.icon,
            description=profile.description,
            activity_count=activity_count,
            is_popular=profile.slug in self.popular_profiles,
            estimated_setup_time=self._estimate_setup_time(activity_count)
        )
        
        return onboarding_activities, onboarding_profile
    
    async def validate_profile_selection(
        self, 
        profile_slug: str
    ) -> OnboardingValidationResponse:
        """Validate a profile selection."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check if profile exists
        profile = await self.profile_repository.get_profile_by_slug(profile_slug)
        if not profile:
            errors.append(f"Profile '{profile_slug}' not found")
            return OnboardingValidationResponse(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
        
        # Check activity availability
        activity_count = await self._get_activity_count_for_profile(profile_slug)
        if activity_count == 0:
            warnings.append(f"No activities available for {profile.name}")
            suggestions.append("Consider selecting a different profile with more service options")
        elif activity_count < 3:
            warnings.append(f"Limited activities available for {profile.name} ({activity_count} available)")
            suggestions.append("You may want to explore additional activities later")
        
        # Check market segment recommendations
        if profile.segments == MarketSegment.COMMERCIAL:
            suggestions.append("Commercial focus requires proper licensing and insurance")
        elif profile.segments == MarketSegment.RESIDENTIAL:
            suggestions.append("Residential services often have faster customer acquisition")
        
        # Check popularity
        if profile_slug in self.popular_profiles:
            suggestions.append("Popular choice! This trade has high demand in most markets")
        else:
            suggestions.append("Specialized trade - consider highlighting your unique expertise")
        
        return OnboardingValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def validate_activity_selections(
        self, 
        trade_slug: str, 
        activity_slugs: List[str]
    ) -> OnboardingValidationResponse:
        """Validate activity selections for a trade."""
        errors = []
        warnings = []
        suggestions = []
        
        if not activity_slugs:
            errors.append("At least one activity must be selected")
            return OnboardingValidationResponse(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=["Select 2-4 activities to start with"]
            )
        
        # Validate each activity belongs to the trade
        valid_activities = await self.activity_repository.get_activities_by_trade(trade_slug)
        valid_slugs = {activity.slug for activity in valid_activities}
        
        for activity_slug in activity_slugs:
            if activity_slug not in valid_slugs:
                errors.append(f"Activity '{activity_slug}' is not valid for trade '{trade_slug}'")
        
        if errors:
            return OnboardingValidationResponse(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
        
        # Provide recommendations based on selection
        if len(activity_slugs) == 1:
            warnings.append("Starting with only one activity may limit your business opportunities")
            suggestions.append("Consider adding 1-2 complementary activities")
        elif len(activity_slugs) > 5:
            warnings.append("Starting with many activities may complicate initial setup")
            suggestions.append("Consider focusing on 3-4 core activities initially")
        
        # Check for emergency services
        emergency_count = 0
        popular_count = 0
        popular_activity_slugs = self.popular_activities.get(trade_slug, [])
        
        for activity_slug in activity_slugs:
            activity = next((a for a in valid_activities if a.slug == activity_slug), None)
            if activity:
                if 'emergency' in activity.tags or 'emergency' in activity.name.lower():
                    emergency_count += 1
                if activity_slug in popular_activity_slugs:
                    popular_count += 1
        
        if emergency_count > 0:
            suggestions.append("Emergency services can increase revenue but require 24/7 availability")
        
        if popular_count == 0:
            suggestions.append("Consider adding at least one popular activity for better market demand")
        elif popular_count == len(activity_slugs):
            suggestions.append("Great selection! All chosen activities are in high demand")
        
        return OnboardingValidationResponse(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def validate_business_details(
        self, 
        details: BusinessDetailsRequest
    ) -> OnboardingValidationResponse:
        """Validate business details."""
        errors = []
        warnings = []
        suggestions = []
        
        # Required field validation
        if not details.name or not details.name.strip():
            errors.append("Business name is required")
        
        # Business name uniqueness (simplified check)
        if details.name and len(details.name.strip()) < 3:
            errors.append("Business name must be at least 3 characters long")
        
        # Contact validation
        if not details.phone_number and not details.business_email:
            warnings.append("No contact information provided")
            suggestions.append("Add phone number or email for customer communication")
        
        # Address validation
        if not details.city or not details.state:
            warnings.append("Location information incomplete")
            suggestions.append("Complete address helps with local SEO and service area setup")
        
        # Business profile validation
        if details.company_size == CompanySize.JUST_ME:
            suggestions.append("Solo business - consider focusing on specialized, high-value services")
        elif details.company_size in [CompanySize.MEDIUM, CompanySize.LARGE]:
            suggestions.append("Larger team - you can handle multiple service areas and complex projects")
        
        # Market focus validation
        if details.market_focus == MarketFocus.COMMERCIAL:
            suggestions.append("Commercial focus - ensure you have proper licensing and insurance")
        elif details.market_focus == MarketFocus.RESIDENTIAL:
            suggestions.append("Residential focus - great for building local reputation and referrals")
        
        return OnboardingValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def complete_onboarding(
        self, 
        request: CompleteOnboardingRequest,
        user_id: str
    ) -> OnboardingCompletionResponse:
        """Complete the entire onboarding process."""
        
        # Validate the complete request
        profile_validation = await self.validate_profile_selection(request.primary_trade_slug)
        if not profile_validation.is_valid:
            raise ValueError(f"Invalid profile selection: {'; '.join(profile_validation.errors)}")
        
        activity_validation = await self.validate_activity_selections(
            request.primary_trade_slug, 
            request.selected_activity_slugs
        )
        if not activity_validation.is_valid:
            raise ValueError(f"Invalid activity selection: {'; '.join(activity_validation.errors)}")
        
        details_validation = await self.validate_business_details(request.business_details)
        if not details_validation.is_valid:
            raise ValueError(f"Invalid business details: {'; '.join(details_validation.errors)}")
        
        # Create the business
        business = Business.create_with_activities(
            name=request.business_details.name,
            primary_trade_slug=request.primary_trade_slug,
            market_focus=request.business_details.market_focus,
            selected_activity_slugs=request.selected_activity_slugs,
            company_size=request.business_details.company_size,
            description=request.business_details.description,
            phone_number=request.business_details.phone_number,
            business_email=request.business_details.business_email,
            website=request.business_details.website,
            address=request.business_details.address,
            city=request.business_details.city,
            state=request.business_details.state,
            postal_code=request.business_details.postal_code,
            business_registration_number=request.business_details.business_registration_number,
            tax_id=request.business_details.tax_id,
            business_license=request.business_details.business_license,
            insurance_number=request.business_details.insurance_number,
            referral_source=request.business_details.referral_source,
            primary_goals=request.business_details.primary_goals,
            onboarding_completed=True,
            onboarding_completed_date=datetime.utcnow()
        )
        
        # Save business to database
        created_business = await self.business_repository.create(business, user_id)
        
        # Auto-adopt service templates
        adopted_templates = []
        created_services_count = 0
        
        if request.template_selections.auto_adopt_popular:
            # Auto-adopt popular templates for selected activities
            for activity_slug in request.selected_activity_slugs:
                try:
                    templates = await self.service_template_repository.get_templates_for_activity(activity_slug)
                    popular_templates = [t for t in templates if t.is_common]
                    
                    for template in popular_templates[:2]:  # Limit to 2 per activity
                        try:
                            await self.service_template_repository.adopt_service_template_by_slug(
                                business_id=created_business.id,
                                template_slug=template.template_slug,
                                activity_slug=activity_slug
                            )
                            adopted_templates.append(template.template_slug)
                            created_services_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to adopt template {template.template_slug}: {e}")
                
                except Exception as e:
                    logger.warning(f"Failed to get templates for activity {activity_slug}: {e}")
        
        # Manually selected templates
        for template_slug in request.template_selections.template_slugs:
            try:
                # Find which activity this template belongs to
                template = await self.service_template_repository.get_template_by_slug(template_slug)
                if template and template.activity_slug in request.selected_activity_slugs:
                    await self.service_template_repository.adopt_service_template_by_slug(
                        business_id=created_business.id,
                        template_slug=template_slug,
                        activity_slug=template.activity_slug
                    )
                    if template_slug not in adopted_templates:
                        adopted_templates.append(template_slug)
                        created_services_count += 1
            except Exception as e:
                logger.warning(f"Failed to adopt selected template {template_slug}: {e}")
        
        # Get enhanced profile and activity data for response
        profile = await self.profile_repository.get_profile_by_slug(request.primary_trade_slug)
        activities = []
        
        for activity_slug in request.selected_activity_slugs:
            activity = await self.activity_repository.get_activity_by_slug(activity_slug)
            if activity:
                template_count = await self._get_template_count_for_activity(activity_slug)
                is_popular = activity_slug in self.popular_activities.get(request.primary_trade_slug, [])
                is_emergency = 'emergency' in activity.tags or 'emergency' in activity.name.lower()
                
                activities.append(OnboardingActivityResponse(
                    id=str(activity.id),
                    slug=activity.slug,
                    name=activity.name,
                    description=f"Professional {activity.name.lower()} services",
                    synonyms=activity.synonyms,
                    tags=activity.tags,
                    is_popular=is_popular,
                    is_emergency=is_emergency,
                    template_count=template_count,
                    estimated_revenue=self._estimate_revenue_potential(activity_slug, is_emergency)
                ))
        
        # Calculate setup completion percentage
        setup_completion = self._calculate_setup_completion(
            created_business, 
            len(adopted_templates),
            len(request.selected_activity_slugs)
        )
        
        return OnboardingCompletionResponse(
            business_id=str(created_business.id),
            business_name=created_business.name,
            primary_trade=OnboardingProfileResponse(
                slug=profile.slug,
                name=profile.name,
                synonyms=profile.synonyms,
                segments=profile.segments,
                icon=profile.icon,
                description=profile.description,
                activity_count=len(request.selected_activity_slugs),
                is_popular=profile.slug in self.popular_profiles,
                estimated_setup_time=self._estimate_setup_time(len(request.selected_activity_slugs))
            ),
            selected_activities=activities,
            adopted_templates=adopted_templates,
            created_services=created_services_count,
            recommended_next_steps=[
                "Set up your service areas and pricing",
                "Upload your business logo and photos",
                "Configure your booking availability",
                "Create your first customer estimate"
            ],
            onboarding_completion_time=f"{request.completion_time_seconds or 420} seconds",
            setup_completion_percentage=setup_completion,
            estimated_revenue_potential=self._estimate_total_revenue_potential(activities)
        )
    
    # Helper methods
    
    async def _get_profiles_count(self) -> int:
        """Get total number of available profiles."""
        try:
            from app.domain.entities.trade_taxonomy import TradeProfileListRequest
            _, count = await self.profile_repository.list_profiles(
                TradeProfileListRequest(limit=1, offset=0)
            )
            return count
        except Exception:
            return 24  # Default count
    
    async def _get_activity_count_for_profile(self, profile_slug: str) -> int:
        """Get number of activities for a profile."""
        try:
            activities = await self.activity_repository.get_activities_by_trade(profile_slug)
            return len(activities)
        except Exception:
            return 0
    
    async def _get_total_activities_count(self) -> int:
        """Get total number of activities."""
        try:
            from app.domain.entities.trade_taxonomy import TradeActivityListRequest
            _, count = await self.activity_repository.list_activities(
                TradeActivityListRequest(limit=1, offset=0)
            )
            return count
        except Exception:
            return 50  # Default count
    
    async def _get_emergency_activities_count(self) -> int:
        """Get number of emergency activities."""
        # This would require a more complex query, for now return estimate
        return 15
    
    async def _get_total_templates_count(self) -> int:
        """Get total number of service templates."""
        # This would require querying the service templates repository
        return 100  # Default estimate
    
    async def _get_popular_templates_count(self) -> int:
        """Get number of popular templates."""
        return 25  # Default estimate
    
    async def _get_template_count_for_activity(self, activity_slug: str) -> int:
        """Get number of templates for an activity."""
        try:
            templates = await self.service_template_repository.get_templates_for_activity(activity_slug)
            return len(templates)
        except Exception:
            return 0
    
    def _estimate_setup_time(self, activity_count: int) -> str:
        """Estimate setup time based on activity count."""
        base_time = 5  # Base 5 minutes
        additional_time = activity_count * 2  # 2 minutes per activity
        total_time = base_time + additional_time
        
        if total_time <= 10:
            return f"{total_time} minutes"
        else:
            return f"{total_time // 60}h {total_time % 60}m"
    
    def _estimate_revenue_potential(self, activity_slug: str, is_emergency: bool) -> str:
        """Estimate revenue potential for an activity."""
        base_revenue = {
            'ac-repair': '$150-800',
            'furnace-repair': '$200-900',
            'hvac-maintenance': '$100-300',
            'drain-cleaning': '$100-400',
            'pipe-repair': '$150-600',
            'water-heater-service': '$200-1200',
            'electrical-repair': '$100-500',
            'panel-upgrade': '$1000-3000',
            'roof-repair': '$300-1500',
            'roof-installation': '$5000-15000'
        }
        
        revenue = base_revenue.get(activity_slug, '$100-500')
        
        if is_emergency:
            return f"{revenue} (1.5x for emergency)"
        
        return revenue
    
    def _estimate_total_revenue_potential(self, activities: List[OnboardingActivityResponse]) -> str:
        """Estimate total revenue potential."""
        if len(activities) <= 2:
            return "$50K-150K annually"
        elif len(activities) <= 4:
            return "$100K-300K annually"
        else:
            return "$200K-500K annually"
    
    def _calculate_setup_completion(
        self, 
        business: Business, 
        template_count: int, 
        activity_count: int
    ) -> float:
        """Calculate setup completion percentage."""
        completion_factors = {
            'business_name': 10 if business.name else 0,
            'contact_info': 10 if (business.phone_number or business.business_email) else 0,
            'address': 10 if (business.city and business.state) else 0,
            'activities': min(30, activity_count * 7.5),  # Up to 30% for activities
            'templates': min(20, template_count * 5),     # Up to 20% for templates
            'profile_complete': 20  # Always 20% for completing onboarding
        }
        
        return sum(completion_factors.values())
