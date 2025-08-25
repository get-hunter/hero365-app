"""
Template Composition Service

Service for composing template data from various business sources
into a unified TemplateProps object for website generation.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...domain.entities.business import Business
from ...domain.entities.website_template import (
    TemplateProps, BusinessProps, ServiceCategoryProps,
    PromoOffer, RatingSnapshot, AwardCertification, 
    OEMPartnership, Testimonial, BusinessLocation,
    PromoPlacement, ModerationStatus
)
from supabase import Client
from ..exceptions.application_exceptions import BusinessNotFoundError, DataCompositionError


class TemplateCompositionService:
    """Service for composing template data from business sources."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def compose_template_props(
        self, 
        business_id: uuid.UUID,
        template_name: str = "professional",
        include_promos: bool = True,
        include_testimonials: bool = True,
        include_ratings: bool = True,
        include_awards: bool = True,
        include_partnerships: bool = True
    ) -> TemplateProps:
        """
        Compose complete template properties for a business.
        
        Args:
            business_id: Business UUID
            template_name: Template name to use
            include_*: Flags to control which content sections to include
            
        Returns:
            TemplateProps: Complete template data
            
        Raises:
            BusinessNotFoundError: If business doesn't exist
            DataCompositionError: If data composition fails
        """
        try:
            # Get business data
            business = await self._get_business_data(business_id)
            business_props = self._convert_business_to_props(business)
            
            # Get service categories
            service_categories = await self._get_service_categories(business_id)
            
            # Get content sections based on flags
            promos = await self._get_promos(business_id) if include_promos else []
            ratings = await self._get_ratings(business_id) if include_ratings else []
            awards = await self._get_awards(business_id) if include_awards else []
            partnerships = await self._get_partnerships(business_id) if include_partnerships else []
            testimonials = await self._get_testimonials(business_id) if include_testimonials else []
            locations = await self._get_locations(business_id)
            
            # Generate SEO metadata
            meta_title, meta_description = self._generate_seo_metadata(business, service_categories)
            
            return TemplateProps(
                business=business_props,
                service_categories=service_categories,
                promos=promos,
                ratings=ratings,
                awards=awards,
                partnerships=partnerships,
                testimonials=testimonials,
                locations=locations,
                template_name=template_name,
                template_version="1.0",
                generated_at=datetime.utcnow(),
                meta_title=meta_title,
                meta_description=meta_description
            )
            
        except Exception as e:
            raise DataCompositionError(f"Failed to compose template data: {str(e)}")
    
    async def _get_business_data(self, business_id: uuid.UUID) -> Business:
        """Get business data from database."""
        try:
            response = self.supabase.table("businesses").select("*").eq("id", str(business_id)).execute()
            
            if not response.data:
                raise BusinessNotFoundError(f"Business {business_id} not found")
            
            business_data = response.data[0]
            
            # Convert database record to Business entity
            return Business(
                id=uuid.UUID(business_data["id"]),
                name=business_data["name"],
                industry=business_data["industry"] or "General Contractor",
                company_size=business_data.get("company_size", "small"),
                description=business_data.get("description"),
                phone_number=business_data.get("phone_number"),
                business_email=business_data.get("business_email"),
                website=business_data.get("website"),
                logo_url=business_data.get("logo_url"),
                address=business_data.get("address"),
                city=business_data.get("city"),
                state=business_data.get("state"),
                zip_code=business_data.get("zip_code"),
                commercial_trades=business_data.get("commercial_trades", []),
                residential_trades=business_data.get("residential_trades", []),
                service_areas=business_data.get("service_areas", []),
                business_hours=business_data.get("business_hours"),
                is_active=business_data.get("is_active", True)
            )
            
        except Exception as e:
            raise DataCompositionError(f"Failed to fetch business data: {str(e)}")
    
    def _convert_business_to_props(self, business: Business) -> BusinessProps:
        """Convert Business entity to BusinessProps for template."""
        return BusinessProps(
            id=business.id,
            name=business.name,
            description=business.description,
            phone_number=business.phone_number,
            business_email=business.business_email,
            website=business.website,
            logo_url=business.logo_url,
            address=business.address,
            city=business.city,
            state=business.state,
            zip_code=business.zip_code,
            trades=business.get_all_trades(),
            service_areas=business.service_areas,
            business_hours=business.business_hours,
            primary_trade=business.get_primary_trade(),
            seo_keywords=business.get_seo_keywords()
        )
    
    async def _get_service_categories(self, business_id: uuid.UUID) -> List[ServiceCategoryProps]:
        """Get service categories for the business."""
        try:
            # Get service categories with service counts
            response = self.supabase.rpc(
                "get_business_service_categories_with_counts",
                {"p_business_id": str(business_id)}
            ).execute()
            
            categories = []
            for row in response.data or []:
                categories.append(ServiceCategoryProps(
                    id=uuid.UUID(row["id"]),
                    name=row["name"],
                    description=row.get("description"),
                    icon_name=row.get("icon_name"),
                    slug=row.get("slug", row["name"].lower().replace(" ", "-")),
                    services_count=row.get("services_count", 0),
                    is_featured=row.get("is_featured", False),
                    sort_order=row.get("sort_order", 0)
                ))
            
            return sorted(categories, key=lambda x: (x.is_featured, x.sort_order), reverse=True)
            
        except Exception as e:
            # Fallback to empty list if service categories don't exist yet
            return []
    
    async def _get_promos(self, business_id: uuid.UUID) -> List[PromoOffer]:
        """Get active promotional offers."""
        try:
            response = self.supabase.rpc(
                "get_active_promos",
                {"p_business_id": str(business_id)}
            ).execute()
            
            promos = []
            for row in response.data or []:
                promos.append(PromoOffer(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    title=row["title"],
                    subtitle=row.get("subtitle"),
                    description=row.get("description"),
                    offer_type=row["offer_type"],
                    price_label=row.get("price_label"),
                    badge_text=row.get("badge_text"),
                    cta_text=row.get("cta_text", "Learn More"),
                    cta_link=row.get("cta_link"),
                    placement=row["placement"],
                    priority=row.get("priority", 0),
                    target_services=row.get("target_services", []),
                    target_trades=row.get("target_trades", []),
                    service_areas=row.get("service_areas", []),
                    start_date=row.get("start_date"),
                    end_date=row.get("end_date"),
                    is_active=row.get("is_active", True),
                    is_featured=row.get("is_featured", False),
                    view_count=row.get("view_count", 0),
                    click_count=row.get("click_count", 0),
                    conversion_count=row.get("conversion_count", 0)
                ))
            
            return promos
            
        except Exception:
            return []
    
    async def _get_ratings(self, business_id: uuid.UUID) -> List[RatingSnapshot]:
        """Get ratings snapshots."""
        try:
            response = self.supabase.rpc(
                "get_featured_ratings",
                {"p_business_id": str(business_id)}
            ).execute()
            
            ratings = []
            for row in response.data or []:
                ratings.append(RatingSnapshot(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    platform=row["platform"],
                    rating=row["rating"],
                    review_count=row["review_count"],
                    total_reviews=row.get("total_reviews"),
                    display_name=row.get("display_name"),
                    logo_url=row.get("logo_url"),
                    profile_url=row.get("profile_url"),
                    is_featured=row.get("is_featured", False),
                    sort_order=row.get("sort_order", 0),
                    last_synced_at=row.get("last_synced_at"),
                    sync_frequency_hours=row.get("sync_frequency_hours", 24),
                    is_active=row.get("is_active", True)
                ))
            
            return ratings
            
        except Exception:
            return []
    
    async def _get_awards(self, business_id: uuid.UUID) -> List[AwardCertification]:
        """Get awards and certifications."""
        try:
            response = self.supabase.table("awards_certifications").select("*").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).eq("display_on_website", True).order(
                "is_featured", desc=True
            ).order("sort_order").execute()
            
            awards = []
            for row in response.data or []:
                awards.append(AwardCertification(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    name=row["name"],
                    issuing_organization=row.get("issuing_organization"),
                    description=row.get("description"),
                    certificate_type=row.get("certificate_type"),
                    logo_url=row.get("logo_url"),
                    certificate_url=row.get("certificate_url"),
                    verification_url=row.get("verification_url"),
                    issued_date=row.get("issued_date"),
                    expiry_date=row.get("expiry_date"),
                    is_current=row.get("is_current", True),
                    is_featured=row.get("is_featured", False),
                    sort_order=row.get("sort_order", 0),
                    display_on_website=row.get("display_on_website", True),
                    trade_relevance=row.get("trade_relevance", []),
                    service_categories=row.get("service_categories", []),
                    is_active=row.get("is_active", True)
                ))
            
            return awards
            
        except Exception:
            return []
    
    async def _get_partnerships(self, business_id: uuid.UUID) -> List[OEMPartnership]:
        """Get OEM partnerships."""
        try:
            response = self.supabase.table("oem_partnerships").select("*").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).eq("display_on_website", True).order(
                "is_featured", desc=True
            ).order("sort_order").execute()
            
            partnerships = []
            for row in response.data or []:
                partnerships.append(OEMPartnership(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    partner_name=row["partner_name"],
                    partner_type=row["partner_type"],
                    partnership_level=row.get("partnership_level"),
                    description=row.get("description"),
                    partnership_benefits=row.get("partnership_benefits", []),
                    logo_url=row["logo_url"],
                    partner_url=row.get("partner_url"),
                    verification_url=row.get("verification_url"),
                    trade_relevance=row["trade_relevance"],
                    service_categories=row.get("service_categories", []),
                    product_lines=row.get("product_lines", []),
                    is_featured=row.get("is_featured", False),
                    sort_order=row.get("sort_order", 0),
                    display_on_website=row.get("display_on_website", True),
                    start_date=row.get("start_date"),
                    end_date=row.get("end_date"),
                    is_active=row.get("is_active", True),
                    is_current=row.get("is_current", True)
                ))
            
            return partnerships
            
        except Exception:
            return []
    
    async def _get_testimonials(self, business_id: uuid.UUID) -> List[Testimonial]:
        """Get approved testimonials."""
        try:
            response = self.supabase.table("testimonials").select("*").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).eq("display_on_website", True).eq(
                "moderation_status", ModerationStatus.APPROVED.value
            ).order("is_featured", desc=True).order("rating", desc=True).execute()
            
            testimonials = []
            for row in response.data or []:
                testimonials.append(Testimonial(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    source_type=row["source_type"],
                    source_id=row.get("source_id"),
                    source_url=row.get("source_url"),
                    quote=row["quote"],
                    full_review=row.get("full_review"),
                    rating=row.get("rating"),
                    customer_name=row.get("customer_name"),
                    customer_initial=row.get("customer_initial"),
                    customer_location=row.get("customer_location"),
                    customer_avatar_url=row.get("customer_avatar_url"),
                    service_performed=row.get("service_performed"),
                    service_date=row.get("service_date"),
                    project_value=row.get("project_value"),
                    trade_category=row.get("trade_category"),
                    is_featured=row.get("is_featured", False),
                    is_verified=row.get("is_verified", False),
                    display_on_website=row.get("display_on_website", True),
                    sort_order=row.get("sort_order", 0),
                    moderation_status=row.get("moderation_status", ModerationStatus.PENDING.value),
                    moderated_by=row.get("moderated_by"),
                    moderated_at=row.get("moderated_at"),
                    is_active=row.get("is_active", True)
                ))
            
            return testimonials
            
        except Exception:
            return []
    
    async def _get_locations(self, business_id: uuid.UUID) -> List[BusinessLocation]:
        """Get business locations."""
        try:
            response = self.supabase.table("business_locations").select("*").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).eq("display_on_website", True).order(
                "is_primary", desc=True
            ).execute()
            
            locations = []
            for row in response.data or []:
                locations.append(BusinessLocation(
                    id=uuid.UUID(row["id"]),
                    business_id=business_id,
                    name=row.get("name"),
                    address=row.get("address"),
                    city=row["city"],
                    state=row["state"],
                    zip_code=row.get("zip_code"),
                    county=row.get("county"),
                    latitude=row.get("latitude"),
                    longitude=row.get("longitude"),
                    service_radius_miles=row.get("service_radius_miles"),
                    location_type=row["location_type"],
                    is_primary=row.get("is_primary", False),
                    is_active=row.get("is_active", True),
                    services_offered=row.get("services_offered", []),
                    trades_covered=row.get("trades_covered", []),
                    operating_hours=row.get("operating_hours"),
                    display_on_website=row.get("display_on_website", True),
                    seo_description=row.get("seo_description"),
                    page_slug=row.get("page_slug")
                ))
            
            return locations
            
        except Exception:
            return []
    
    def _generate_seo_metadata(
        self, 
        business: Business, 
        service_categories: List[ServiceCategoryProps]
    ) -> tuple[str, str]:
        """Generate SEO metadata for the business."""
        # Generate meta title
        primary_trade = business.get_primary_trade()
        if primary_trade:
            trade_display = primary_trade.replace("_", " ").title()
            if business.city and business.state:
                meta_title = f"{trade_display} Services in {business.city}, {business.state} | {business.name}"
            else:
                meta_title = f"Professional {trade_display} Services | {business.name}"
        else:
            meta_title = f"Professional Services | {business.name}"
        
        # Generate meta description
        services_text = ""
        if service_categories:
            top_services = [cat.name for cat in service_categories[:3]]
            services_text = f"Specializing in {', '.join(top_services)}. "
        
        location_text = ""
        if business.service_areas:
            location_text = f"Serving {', '.join(business.service_areas[:3])}. "
        elif business.city and business.state:
            location_text = f"Serving {business.city}, {business.state} and surrounding areas. "
        
        contact_text = ""
        if business.phone_number:
            contact_text = f"Call {business.phone_number} for a free estimate."
        
        meta_description = f"{services_text}{location_text}{contact_text}".strip()
        
        # Ensure meta description is within limits
        if len(meta_description) > 155:
            meta_description = meta_description[:152] + "..."
        
        return meta_title, meta_description
