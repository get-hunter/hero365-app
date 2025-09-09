"""Service for managing activity content packs."""

from typing import Dict, List, Optional
from app.api.dtos.activity_content_dtos import (
    ActivityContentPackResponse,
    ActivityContentPackHero,
    ActivityContentPackBenefits,
    ActivityContentPackProcess,
    ActivityContentPackFAQ,
    ActivityContentPackSEO,
    ActivityContentPackSchema,
    ActivityContentPackPricing,
    BusinessActivityDataResponse,
    BusinessActivityServiceTemplate,
    BusinessActivityBookingField,
    ActivityPageDataResponse
)
from app.infrastructure.database.repositories.supabase_trade_taxonomy_repository import (
    SupabaseTradeActivityRepository,
    SupabaseTradeProfileRepository
)
from app.infrastructure.database.repositories.supabase_service_template_repository import SupabaseServiceTemplateRepository
from app.infrastructure.database.repositories.supabase_business_repository import SupabaseBusinessRepository


class ActivityContentService:
    """Service for managing activity content packs and business activity data."""

    def __init__(
        self,
        trade_activity_repository: SupabaseTradeActivityRepository,
        trade_profile_repository: SupabaseTradeProfileRepository,
        service_template_repository: SupabaseServiceTemplateRepository,
        business_repository: SupabaseBusinessRepository,
        supabase_client
    ):
        self.trade_activity_repository = trade_activity_repository
        self.trade_profile_repository = trade_profile_repository
        self.service_template_repository = service_template_repository
        self.business_repository = business_repository
        self.supabase = supabase_client
        
        # Static content packs - in production, these could come from a CMS or database
        self._content_packs = self._initialize_content_packs()

    def _initialize_content_packs(self) -> Dict[str, ActivityContentPackResponse]:
        """Initialize static content packs for activities."""
        return {
            'ac-installation': ActivityContentPackResponse(
                activity_slug='ac-installation',
                hero=ActivityContentPackHero(
                    title='Professional AC Installation Services',
                    subtitle='Stay cool with expert air conditioning installation from certified HVAC technicians',
                    cta_label='Get Free Quote',
                    icon='snowflake'
                ),
                benefits=ActivityContentPackBenefits(
                    heading='Why Choose Our AC Installation?',
                    bullets=[
                        'Licensed and insured HVAC technicians',
                        'Energy-efficient system recommendations',
                        'Proper sizing and load calculations',
                        'Warranty on parts and labor',
                        'Same-day service available',
                        'Financing options available'
                    ]
                ),
                process=ActivityContentPackProcess(
                    heading='Our Installation Process',
                    steps=[
                        'Free in-home consultation and estimate',
                        'System sizing and equipment selection',
                        'Professional installation by certified techs',
                        'System testing and commissioning',
                        'Customer walkthrough and maintenance tips'
                    ]
                ),
                faqs=[
                    ActivityContentPackFAQ(
                        q='How long does AC installation take?',
                        a='Most installations take 4-8 hours depending on system complexity and any required electrical or ductwork modifications.'
                    ),
                    ActivityContentPackFAQ(
                        q='Do you provide warranties?',
                        a='Yes, we provide manufacturer warranties on equipment plus our own labor warranty for complete peace of mind.'
                    ),
                    ActivityContentPackFAQ(
                        q='What size AC unit do I need?',
                        a='We perform detailed load calculations considering your home size, insulation, windows, and local climate to recommend the perfect size.'
                    )
                ],
                seo=ActivityContentPackSEO(
                    title_template='{businessName} - Professional AC Installation in {city}',
                    description_template='Expert air conditioning installation services in {city}. Licensed HVAC technicians, energy-efficient systems, warranties included. Call {phone} for free quote.',
                    keywords=['ac installation', 'air conditioning installation', 'hvac installation', 'central air installation', 'cooling system installation']
                ),
                schema=ActivityContentPackSchema(
                    service_type='Air Conditioning Installation',
                    description='Professional installation of residential and commercial air conditioning systems',
                    category='HVAC Services'
                ),
                pricing=ActivityContentPackPricing(
                    starting_price=3500.0,
                    price_range='$3,500 - $8,000',
                    unit='complete system'
                )
            ),
            'ac-repair': ActivityContentPackResponse(
                activity_slug='ac-repair',
                hero=ActivityContentPackHero(
                    title='Fast AC Repair Services',
                    subtitle='Emergency air conditioning repair available 24/7 to keep you comfortable',
                    cta_label='Call Now',
                    icon='wrench'
                ),
                benefits=ActivityContentPackBenefits(
                    heading='Expert AC Repair Services',
                    bullets=[
                        '24/7 emergency service available',
                        'Diagnostic fee waived with repair',
                        'All major brands serviced',
                        'Upfront pricing with no surprises',
                        'Same-day repairs when possible',
                        '100% satisfaction guarantee'
                    ]
                ),
                process=ActivityContentPackProcess(
                    heading='Our Repair Process',
                    steps=[
                        'Emergency dispatch or scheduled appointment',
                        'Comprehensive system diagnosis',
                        'Transparent pricing before work begins',
                        'Professional repair with quality parts',
                        'System testing and performance verification'
                    ]
                ),
                faqs=[
                    ActivityContentPackFAQ(
                        q='Do you offer emergency AC repair?',
                        a='Yes, we provide 24/7 emergency AC repair services because we know cooling failures don\'t wait for business hours.'
                    ),
                    ActivityContentPackFAQ(
                        q='How much does AC repair cost?',
                        a='Repair costs vary by issue complexity. We provide upfront pricing after diagnosis, with no hidden fees.'
                    ),
                    ActivityContentPackFAQ(
                        q='Should I repair or replace my AC?',
                        a='We\'ll help you decide based on your system\'s age, repair costs, and efficiency. Generally, if repairs cost more than 50% of replacement, we recommend upgrading.'
                    )
                ],
                seo=ActivityContentPackSEO(
                    title_template='{businessName} - 24/7 AC Repair Services in {city}',
                    description_template='Emergency air conditioning repair in {city}. Fast, reliable HVAC repair services. Licensed technicians, upfront pricing. Call {phone} now.',
                    keywords=['ac repair', 'air conditioning repair', 'hvac repair', 'emergency ac repair', 'cooling system repair']
                ),
                schema=ActivityContentPackSchema(
                    service_type='Air Conditioning Repair',
                    description='24/7 emergency and scheduled air conditioning repair services',
                    category='HVAC Services'
                ),
                pricing=ActivityContentPackPricing(
                    starting_price=150.0,
                    price_range='$150 - $800',
                    unit='per repair'
                )
            ),
            'drain-cleaning': ActivityContentPackResponse(
                activity_slug='drain-cleaning',
                hero=ActivityContentPackHero(
                    title='Professional Drain Cleaning Services',
                    subtitle='Fast, effective drain cleaning to restore proper flow and prevent backups',
                    cta_label='Clear My Drains',
                    icon='droplet'
                ),
                benefits=ActivityContentPackBenefits(
                    heading='Expert Drain Cleaning',
                    bullets=[
                        'Advanced drain cleaning equipment',
                        'Video camera inspections available',
                        'Eco-friendly cleaning methods',
                        'Same-day service available',
                        'Preventive maintenance plans',
                        '100% satisfaction guarantee'
                    ]
                ),
                process=ActivityContentPackProcess(
                    heading='Our Drain Cleaning Process',
                    steps=[
                        'Initial assessment and diagnosis',
                        'Video inspection if needed',
                        'Professional drain cleaning service',
                        'Flow testing and verification',
                        'Preventive maintenance recommendations'
                    ]
                ),
                faqs=[
                    ActivityContentPackFAQ(
                        q='How do you clean drains?',
                        a='We use professional-grade equipment including drain snakes, hydro-jetting, and video inspection to thoroughly clean and clear your drains.'
                    ),
                    ActivityContentPackFAQ(
                        q='How often should drains be cleaned?',
                        a='For prevention, we recommend annual drain cleaning. High-use drains may need more frequent service.'
                    ),
                    ActivityContentPackFAQ(
                        q='Do you offer emergency drain cleaning?',
                        a='Yes, we provide emergency drain cleaning services for severe backups and urgent situations.'
                    )
                ],
                seo=ActivityContentPackSEO(
                    title_template='{businessName} - Professional Drain Cleaning in {city}',
                    description_template='Expert drain cleaning services in {city}. Clear clogs, prevent backups. Same-day service available. Licensed plumbers. Call {phone}.',
                    keywords=['drain cleaning', 'clogged drain', 'drain snake', 'hydro jetting', 'sewer cleaning']
                ),
                schema=ActivityContentPackSchema(
                    service_type='Drain Cleaning',
                    description='Professional drain cleaning and clog removal services',
                    category='Plumbing Services'
                ),
                pricing=ActivityContentPackPricing(
                    starting_price=150.0,
                    price_range='$150 - $400',
                    unit='per drain'
                )
            )
        }

    def get_content_pack(self, activity_slug: str) -> Optional[ActivityContentPackResponse]:
        """Get content pack for a specific activity."""
        return self._content_packs.get(activity_slug)

    def get_available_activity_slugs(self) -> List[str]:
        """Get list of all available activity slugs with content packs."""
        return list(self._content_packs.keys())

    async def get_business_activity_data(self, business_id: str, activity_slug: str) -> Optional[BusinessActivityDataResponse]:
        """Get business-specific activity data including service templates and booking fields."""
        try:
            # Get the activity from taxonomy
            activity = await self.trade_activity_repository.get_by_slug(activity_slug)
            if not activity:
                return None

            # Get the trade profile
            trade_profile = await self.trade_profile_repository.get_by_slug(activity.trade_slug)
            if not trade_profile:
                return None

            # Check if business has selected this activity
            activity_check = self.supabase.table("business_activity_selections")\
                .select("id")\
                .eq("business_id", business_id)\
                .eq("activity_slug", activity_slug)\
                .eq("is_active", True)\
                .execute()
            
            if not activity_check.data:
                return None

            # Get service templates for this activity (if any)
            service_templates = []
            # Note: This would be enhanced to get actual adopted service templates
            # For now, we'll return empty list

            # Convert booking fields
            booking_fields = []
            for field in activity.required_booking_fields + activity.default_booking_fields:
                booking_fields.append(BusinessActivityBookingField(
                    key=field.key,
                    type=field.type,
                    label=field.label,
                    options=field.options,
                    required=field in activity.required_booking_fields
                ))

            return BusinessActivityDataResponse(
                activity_slug=activity.slug,
                activity_name=activity.name,
                trade_slug=activity.trade_slug,
                trade_name=trade_profile.name,
                service_templates=service_templates,
                booking_fields=booking_fields
            )

        except Exception as e:
            # Log error in production
            return None

    async def get_activity_page_data(self, business_id: str, activity_slug: str) -> Optional[ActivityPageDataResponse]:
        """Get complete activity page data including content pack and business data."""
        try:
            # Get business activity data
            activity_data = await self.get_business_activity_data(business_id, activity_slug)
            if not activity_data:
                return None

            # Get content pack
            content_pack = self.get_content_pack(activity_slug)
            if not content_pack:
                return None

            # Get business information
            business = await self.business_repository.get_by_id(business_id)
            if not business:
                return None

            business_data = {
                'name': business.name,
                'phone': business.phone or '',
                'email': business.email or '',
                'address': business.address or '',
                'city': business.city or '',
                'state': business.state or '',
                'postal_code': business.postal_code or '',
                'service_areas': business.service_areas or []
            }

            return ActivityPageDataResponse(
                activity=activity_data,
                content=content_pack,
                business=business_data
            )

        except Exception as e:
            # Log error in production
            return None
