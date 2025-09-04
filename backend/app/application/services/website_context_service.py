"""Service for aggregating website context data."""

from typing import List, Optional, Dict, Any
import logging
from app.api.dtos.website_context_dtos import (
    WebsiteContextResponse,
    WebsiteBusinessInfo,
    WebsiteActivityInfo,
    WebsiteServiceTemplate,
    WebsiteTradeInfo,
    WebsiteBookingField,
    WebsiteContextRequest
)
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeActivityRepository,
    SupabaseTradeProfileRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import SupabaseServiceTemplateRepository
from app.domain.entities.trade_taxonomy import BookingField

logger = logging.getLogger(__name__)


class WebsiteContextService:
    """Service for aggregating all website context data in a single call."""

    def __init__(
        self,
        business_repository: SupabaseBusinessRepository,
        trade_activity_repository: SupabaseTradeActivityRepository,
        trade_profile_repository: SupabaseTradeProfileRepository,
        service_template_repository: SupabaseServiceTemplateRepository
    ):
        self.business_repository = business_repository
        self.trade_activity_repository = trade_activity_repository
        self.trade_profile_repository = trade_profile_repository
        self.service_template_repository = service_template_repository

    async def get_website_context(
        self, 
        business_id: str, 
        request: Optional[WebsiteContextRequest] = None
    ) -> Optional[WebsiteContextResponse]:
        """
        Get complete website context for a business.
        
        This aggregates all data needed for website generation:
        - Business information
        - Selected activities with booking fields
        - Service templates
        - Trade information
        """
        try:
            if request is None:
                request = WebsiteContextRequest()

            # Step 1: Get business information
            business = await self.business_repository.get_by_id(business_id)
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return None

            # Step 2: Transform business data
            website_business = self._transform_business_info(business)

            # Step 3: Get activities for selected activity slugs
            activities = []
            if business.selected_activity_slugs:
                activity_slugs = business.selected_activity_slugs
                if request.activity_limit:
                    activity_slugs = activity_slugs[:request.activity_limit]
                
                activities = await self._get_activities_info(activity_slugs)

            # Step 4: Get service templates (if requested)
            service_templates = []
            if request.include_templates:
                service_templates = await self._get_service_templates_info(
                    business_id, 
                    business.selected_activity_slugs,
                    request.template_limit
                )

            # Step 5: Get trade information (if requested)
            trades = []
            if request.include_trades:
                trades = await self._get_trades_info(business, activities)

            # Step 6: Build metadata
            metadata = {
                "generated_at": business.updated_at.isoformat() if business.updated_at else None,
                "total_activities": len(activities),
                "total_templates": len(service_templates),
                "total_trades": len(trades),
                "primary_trade": business.primary_trade_slug
            }

            return WebsiteContextResponse(
                business=website_business,
                activities=activities,
                service_templates=service_templates,
                trades=trades,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error getting website context for business {business_id}: {str(e)}")
            return None

    def _transform_business_info(self, business) -> WebsiteBusinessInfo:
        """Transform business entity to website business info."""
        return WebsiteBusinessInfo(
            id=business.id,
            name=business.name,
            description=business.description,
            phone=business.phone,
            email=business.email,
            address=business.address,
            city=business.city,
            state=business.state,
            postal_code=business.postal_code,
            website=business.website,
            primary_trade_slug=business.primary_trade_slug,
            service_areas=business.service_areas or []
        )

    async def _get_activities_info(self, activity_slugs: List[str]) -> List[WebsiteActivityInfo]:
        """Get activity information for given slugs."""
        activities = []
        
        for slug in activity_slugs:
            try:
                activity = await self.trade_activity_repository.get_by_slug(slug)
                if activity:
                    # Get trade info for this activity
                    trade = await self.trade_profile_repository.get_by_slug(activity.trade_slug)
                    trade_name = trade.name if trade else activity.trade_slug

                    # Transform booking fields
                    default_fields = [
                        self._transform_booking_field(field, required=False)
                        for field in activity.default_booking_fields
                    ]
                    required_fields = [
                        self._transform_booking_field(field, required=True)
                        for field in activity.required_booking_fields
                    ]

                    website_activity = WebsiteActivityInfo(
                        slug=activity.slug,
                        name=activity.name,
                        trade_slug=activity.trade_slug,
                        trade_name=trade_name,
                        synonyms=activity.synonyms,
                        tags=activity.tags,
                        default_booking_fields=default_fields,
                        required_booking_fields=required_fields
                    )
                    activities.append(website_activity)
                else:
                    logger.warning(f"Activity not found: {slug}")
            except Exception as e:
                logger.error(f"Error getting activity {slug}: {str(e)}")
                continue

        return activities

    async def _get_service_templates_info(
        self, 
        business_id: str, 
        activity_slugs: List[str],
        limit: Optional[int] = None
    ) -> List[WebsiteServiceTemplate]:
        """Get service templates information."""
        templates = []
        
        try:
            # Get business services (adopted templates)
            business_services = await self.service_template_repository.get_business_services(business_id)
            
            # Transform to website service templates
            for service in business_services:
                if limit and len(templates) >= limit:
                    break
                    
                template = WebsiteServiceTemplate(
                    template_slug=service.get('template_slug', service.get('name', '')),
                    name=service.get('name', ''),
                    description=service.get('description'),
                    pricing_model=service.get('pricing_model', 'quote'),
                    pricing_config=service.get('pricing_config', {}),
                    unit_of_measure=service.get('unit_of_measure'),
                    is_emergency=service.get('is_emergency', False),
                    activity_slug=service.get('activity_slug')
                )
                templates.append(template)

        except Exception as e:
            logger.error(f"Error getting service templates for business {business_id}: {str(e)}")

        return templates

    async def _get_trades_info(self, business, activities: List[WebsiteActivityInfo]) -> List[WebsiteTradeInfo]:
        """Get trade information for business and activities."""
        trades = []
        trade_slugs = set()

        # Add primary trade
        if business.primary_trade_slug:
            trade_slugs.add(business.primary_trade_slug)

        # Add trades from activities
        for activity in activities:
            trade_slugs.add(activity.trade_slug)

        # Fetch trade information
        for trade_slug in trade_slugs:
            try:
                trade = await self.trade_profile_repository.get_by_slug(trade_slug)
                if trade:
                    website_trade = WebsiteTradeInfo(
                        slug=trade.slug,
                        name=trade.name,
                        description=trade.description,
                        segments=trade.segments.value if hasattr(trade.segments, 'value') else str(trade.segments),
                        icon=trade.icon
                    )
                    trades.append(website_trade)
            except Exception as e:
                logger.error(f"Error getting trade {trade_slug}: {str(e)}")
                continue

        return trades

    def _transform_booking_field(self, field: BookingField, required: bool = False) -> WebsiteBookingField:
        """Transform domain booking field to website booking field."""
        return WebsiteBookingField(
            key=field.key,
            type=field.type,
            label=field.label,
            options=field.options,
            required=required,
            placeholder=getattr(field, 'placeholder', None),
            help_text=getattr(field, 'help_text', None)
        )
