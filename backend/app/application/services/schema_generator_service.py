"""
Schema Generator Service for JSON-LD Structured Data

Generates structured data markup for better SEO and rich search results.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from app.domain.entities.service_page_content import SchemaBlock, SchemaType

logger = logging.getLogger(__name__)


class SchemaGeneratorService:
    """Service for generating JSON-LD structured data schemas."""
    
    def __init__(self):
        pass
    
    def generate_service_schema(self, context: Dict[str, Any]) -> SchemaBlock:
        """Generate Service schema for a service page."""
        business_name = context.get('business_name', 'Business')
        service_name = context.get('service_name', 'Service')
        city = context.get('city', 'City')
        state = context.get('state', 'State')
        phone = context.get('phone', '')
        email = context.get('email', '')
        
        # Extract business info from RAG context if available
        rag_context = context.get('rag_context', {})
        business_info = rag_context.get('business_info', {})
        target_service = rag_context.get('target_service', {})
        
        # Use enhanced business info
        if business_info:
            business_name = business_info.get('display_name') or business_info.get('name', business_name)
            city = business_info.get('city', city)
            state = business_info.get('state', state)
            phone = business_info.get('phone', phone)
            email = business_info.get('email', email)
        
        # Service pricing info
        base_price = target_service.get('base_price')
        price_range_min = target_service.get('price_range_min')
        price_range_max = target_service.get('price_range_max')
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service_name,
            "description": f"Professional {service_name.lower()} services in {city}, {state}",
            "provider": {
                "@type": "LocalBusiness",
                "name": business_name,
                "telephone": phone,
                "email": email,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": city,
                    "addressRegion": state,
                    "addressCountry": "US"
                }
            },
            "areaServed": {
                "@type": "City",
                "name": city,
                "containedInPlace": {
                    "@type": "State",
                    "name": state
                }
            },
            "serviceType": service_name,
            "category": target_service.get('category', 'Home Services')
        }
        
        # Add pricing if available
        if base_price or (price_range_min and price_range_max):
            offers = {
                "@type": "Offer",
                "priceCurrency": "USD"
            }
            
            if base_price:
                offers["price"] = str(base_price)
            elif price_range_min and price_range_max:
                offers["priceRange"] = f"${price_range_min}-${price_range_max}"
            
            schema_data["offers"] = offers
        
        return SchemaBlock(
            type=SchemaType.SERVICE,
            data=schema_data
        )
    
    def generate_local_business_schema(self, context: Dict[str, Any]) -> SchemaBlock:
        """Generate LocalBusiness schema."""
        business_name = context.get('business_name', 'Business')
        city = context.get('city', 'City')
        state = context.get('state', 'State')
        phone = context.get('phone', '')
        email = context.get('email', '')
        
        # Extract enhanced business info
        rag_context = context.get('rag_context', {})
        business_info = rag_context.get('business_info', {})
        
        if business_info:
            business_name = business_info.get('display_name') or business_info.get('name', business_name)
            city = business_info.get('city', city)
            state = business_info.get('state', state)
            phone = business_info.get('phone', phone)
            email = business_info.get('email', email)
            zip_code = business_info.get('zip_code')
            years_in_business = business_info.get('years_in_business')
            license_number = business_info.get('license_number')
            primary_trade = business_info.get('primary_trade')
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name,
            "telephone": phone,
            "email": email,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressRegion": state,
                "addressCountry": "US"
            },
            "areaServed": {
                "@type": "City",
                "name": city
            }
        }
        
        # Add postal code if available
        if business_info.get('zip_code'):
            schema_data["address"]["postalCode"] = business_info['zip_code']
        
        # Add business category
        if business_info.get('primary_trade'):
            trade_categories = {
                'HVAC': 'HVACBusiness',
                'Plumbing': 'PlumbingBusiness', 
                'Electrical': 'ElectricalBusiness',
                'Roofing': 'RoofingContractor'
            }
            business_type = trade_categories.get(business_info['primary_trade'], 'LocalBusiness')
            schema_data["@type"] = business_type
        
        # Add founding date if years in business is available
        if business_info.get('years_in_business'):
            current_year = datetime.now().year
            founding_year = current_year - business_info['years_in_business']
            schema_data["foundingDate"] = str(founding_year)
        
        return SchemaBlock(
            type=SchemaType.LOCAL_BUSINESS,
            data=schema_data
        )
    
    def generate_faq_schema(self, faq_content: Dict[str, Any]) -> Optional[SchemaBlock]:
        """Generate FAQPage schema from FAQ content."""
        faqs = faq_content.get('faqs', [])
        
        if not faqs:
            return None
        
        main_entities = []
        for faq in faqs:
            if isinstance(faq, dict) and 'question' in faq and 'answer' in faq:
                main_entities.append({
                    "@type": "Question",
                    "name": faq['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq['answer']
                    }
                })
        
        if not main_entities:
            return None
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entities
        }
        
        return SchemaBlock(
            type=SchemaType.FAQ_PAGE,
            data=schema_data
        )
    
    def generate_how_to_schema(self, process_steps_content: Dict[str, Any], context: Dict[str, Any]) -> Optional[SchemaBlock]:
        """Generate HowTo schema from process steps."""
        steps = process_steps_content.get('steps', [])
        
        if not steps:
            return None
        
        service_name = context.get('service_name', 'Service')
        
        supply_list = []
        step_list = []
        
        for i, step in enumerate(steps):
            if isinstance(step, dict) and 'name' in step and 'text' in step:
                step_list.append({
                    "@type": "HowToStep",
                    "position": i + 1,
                    "name": step['name'],
                    "text": step['text']
                })
        
        if not step_list:
            return None
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"How to Get {service_name}",
            "description": f"Step-by-step process for {service_name.lower()}",
            "step": step_list,
            "totalTime": "PT1H",  # Default 1 hour
            "estimatedCost": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "value": "varies"
            }
        }
        
        return SchemaBlock(
            type=SchemaType.HOW_TO,
            data=schema_data
        )
    
    def generate_breadcrumb_schema(self, service_slug: str, context: Dict[str, Any]) -> SchemaBlock:
        """Generate BreadcrumbList schema."""
        business_name = context.get('business_name', 'Business')
        service_name = context.get('service_name', 'Service')
        city = context.get('city', 'City')
        
        # Build breadcrumb items
        items = [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "/"
            },
            {
                "@type": "ListItem", 
                "position": 2,
                "name": "Services",
                "item": "/services"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": service_name,
                "item": f"/services/{service_slug}"
            }
        ]
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        
        return SchemaBlock(
            type=SchemaType.BREADCRUMB_LIST,
            data=schema_data
        )
    
    def generate_aggregate_rating_schema(self, testimonials: List[Dict[str, Any]], context: Dict[str, Any]) -> Optional[SchemaBlock]:
        """Generate AggregateRating schema from testimonials."""
        if not testimonials:
            return None
        
        # Calculate rating statistics
        ratings = [t.get('rating', 0) for t in testimonials if t.get('rating')]
        
        if not ratings:
            return None
        
        avg_rating = sum(ratings) / len(ratings)
        review_count = len(ratings)
        
        business_name = context.get('business_name', 'Business')
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "AggregateRating",
            "ratingValue": round(avg_rating, 1),
            "reviewCount": review_count,
            "bestRating": 5,
            "worstRating": 1,
            "itemReviewed": {
                "@type": "LocalBusiness",
                "name": business_name
            }
        }
        
        return SchemaBlock(
            type=SchemaType.AGGREGATE_RATING,
            data=schema_data
        )
    
    def generate_all_schemas(self, page_context: Dict[str, Any], content_blocks: List[Any]) -> List[SchemaBlock]:
        """Generate all applicable schemas for a service page."""
        schemas = []
        
        # Always generate core schemas
        schemas.append(self.generate_service_schema(page_context))
        schemas.append(self.generate_local_business_schema(page_context))
        
        service_slug = page_context.get('service_slug', 'service')
        schemas.append(self.generate_breadcrumb_schema(service_slug, page_context))
        
        # Generate content-specific schemas
        for block in content_blocks:
            if hasattr(block, 'type') and hasattr(block, 'content'):
                if block.type == 'faq':
                    faq_schema = self.generate_faq_schema(block.content)
                    if faq_schema:
                        schemas.append(faq_schema)
                
                elif block.type == 'process_steps':
                    howto_schema = self.generate_how_to_schema(block.content, page_context)
                    if howto_schema:
                        schemas.append(howto_schema)
        
        # Generate rating schema if testimonials available
        rag_context = page_context.get('rag_context', {})
        testimonials = rag_context.get('testimonials', [])
        if testimonials:
            rating_schema = self.generate_aggregate_rating_schema(testimonials, page_context)
            if rating_schema:
                schemas.append(rating_schema)
        
        return [s for s in schemas if s is not None]
