"""
AI Content Generator Service

Advanced AI-powered content generation for trade-specific websites with SEO optimization,
brand consistency, and conversion-focused copywriting.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal

import openai
from pydantic import BaseModel, Field

from ...domain.entities.business import Business, TradeCategory, CommercialTrade, ResidentialTrade
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import WebsiteTemplate, BusinessWebsite
from ...core.config import settings

logger = logging.getLogger(__name__)


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    
    business: Business
    branding: BusinessBranding
    template: WebsiteTemplate
    website: BusinessWebsite
    page_type: str = Field(..., description="Type of page to generate content for")
    content_type: str = Field(..., description="Specific content type (hero, services, about, etc.)")
    additional_context: Dict[str, Any] = Field(default_factory=dict)


class GeneratedContent(BaseModel):
    """Generated content response."""
    
    content_type: str
    page_type: str
    primary_content: Dict[str, Any]
    seo_metadata: Dict[str, Any]
    conversion_elements: Dict[str, Any]
    trade_specific_elements: Dict[str, Any]
    generation_metadata: Dict[str, Any]


class TradeContentStrategy(BaseModel):
    """Trade-specific content strategy configuration."""
    
    trade_name: str
    category: TradeCategory
    
    # Content focus areas
    pain_points: List[str] = Field(default_factory=list)
    value_propositions: List[str] = Field(default_factory=list)
    service_keywords: List[str] = Field(default_factory=list)
    urgency_triggers: List[str] = Field(default_factory=list)
    trust_signals: List[str] = Field(default_factory=list)
    
    # SEO strategy
    primary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    local_modifiers: List[str] = Field(default_factory=list)
    
    # Content tone and style
    tone: str = Field(default="professional")  # professional, friendly, authoritative, urgent
    technical_level: str = Field(default="accessible")  # technical, accessible, simple
    
    # Conversion strategy
    primary_cta: str = Field(default="Get Free Quote")
    secondary_cta: str = Field(default="Call Now")
    urgency_level: str = Field(default="medium")  # low, medium, high, emergency


class AIContentGeneratorService:
    """
    AI-powered content generation service for trade-specific websites.
    
    Generates SEO-optimized, conversion-focused content that maintains
    brand consistency while addressing trade-specific customer needs.
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.trade_strategies = self._load_trade_strategies()
    
    def _load_trade_strategies(self) -> Dict[str, TradeContentStrategy]:
        """Load trade-specific content strategies."""
        strategies = {}
        
        # Commercial trade strategies
        commercial_trades = {
            "mechanical": TradeContentStrategy(
                trade_name="mechanical",
                category=TradeCategory.COMMERCIAL,
                pain_points=[
                    "Equipment downtime costing thousands per hour",
                    "Inefficient HVAC systems driving up energy costs",
                    "Compliance issues with building codes",
                    "Emergency repairs disrupting business operations"
                ],
                value_propositions=[
                    "24/7 emergency response to minimize downtime",
                    "Preventive maintenance programs to avoid costly repairs",
                    "Energy-efficient solutions that reduce operating costs",
                    "Certified technicians ensuring code compliance"
                ],
                service_keywords=[
                    "commercial HVAC", "mechanical systems", "building automation",
                    "preventive maintenance", "energy efficiency", "emergency repair"
                ],
                urgency_triggers=[
                    "equipment failure", "system breakdown", "emergency repair",
                    "compliance deadline", "energy waste"
                ],
                trust_signals=[
                    "Licensed & Insured", "EPA Certified", "24/7 Emergency Service",
                    "Preventive Maintenance Programs", "Energy Efficiency Guaranteed"
                ],
                primary_keywords=[
                    "commercial mechanical services", "HVAC maintenance", "building systems",
                    "mechanical contractor", "commercial HVAC repair"
                ],
                tone="professional",
                technical_level="accessible",
                primary_cta="Schedule Service",
                secondary_cta="Emergency Repair"
            ),
            
            "plumbing": TradeContentStrategy(
                trade_name="plumbing",
                category=TradeCategory.COMMERCIAL,
                pain_points=[
                    "Water damage from pipe failures",
                    "Health code violations from plumbing issues",
                    "Business disruption from plumbing emergencies",
                    "High water bills from hidden leaks"
                ],
                value_propositions=[
                    "Rapid response to prevent water damage",
                    "Code-compliant installations and repairs",
                    "Leak detection services to reduce water costs",
                    "Preventive maintenance to avoid emergencies"
                ],
                service_keywords=[
                    "commercial plumbing", "pipe repair", "drain cleaning",
                    "water heater service", "backflow prevention", "leak detection"
                ],
                urgency_triggers=[
                    "water leak", "pipe burst", "drain backup", "no hot water",
                    "health inspection", "water damage"
                ],
                trust_signals=[
                    "Licensed Master Plumber", "24/7 Emergency Service",
                    "Water Damage Prevention", "Health Code Compliance"
                ],
                primary_keywords=[
                    "commercial plumbing services", "emergency plumber", "pipe repair",
                    "commercial drain cleaning", "plumbing contractor"
                ],
                tone="professional",
                urgency_level="high",
                primary_cta="Emergency Service",
                secondary_cta="Schedule Inspection"
            ),
            
            "electrical": TradeContentStrategy(
                trade_name="electrical",
                category=TradeCategory.COMMERCIAL,
                pain_points=[
                    "Power outages disrupting business operations",
                    "Electrical safety hazards and fire risks",
                    "Code violations and inspection failures",
                    "Inefficient electrical systems increasing costs"
                ],
                value_propositions=[
                    "Reliable electrical systems to keep business running",
                    "Safety inspections to prevent hazards and liability",
                    "Code-compliant installations and upgrades",
                    "Energy-efficient solutions to reduce operating costs"
                ],
                service_keywords=[
                    "commercial electrical", "electrical contractor", "power systems",
                    "electrical safety", "code compliance", "energy efficiency"
                ],
                urgency_triggers=[
                    "power outage", "electrical fire", "safety hazard", "code violation",
                    "inspection failure", "equipment failure"
                ],
                trust_signals=[
                    "Licensed Electrician", "Safety Certified", "Code Compliant",
                    "24/7 Emergency Service", "Fully Insured"
                ],
                primary_keywords=[
                    "commercial electrical services", "electrical contractor", "power systems",
                    "electrical safety inspection", "commercial electrician"
                ],
                tone="authoritative",
                urgency_level="high",
                primary_cta="Safety Inspection",
                secondary_cta="Emergency Service"
            )
        }
        
        # Residential trade strategies
        residential_trades = {
            "hvac": TradeContentStrategy(
                trade_name="hvac",
                category=TradeCategory.RESIDENTIAL,
                pain_points=[
                    "Uncomfortable home temperatures",
                    "High energy bills from inefficient systems",
                    "Poor air quality affecting family health",
                    "Unreliable heating and cooling systems"
                ],
                value_propositions=[
                    "Year-round comfort for your family",
                    "Energy-efficient systems that save money",
                    "Improved air quality for healthier living",
                    "Reliable service you can count on"
                ],
                service_keywords=[
                    "HVAC repair", "air conditioning", "heating service", "furnace repair",
                    "duct cleaning", "air quality", "energy efficiency"
                ],
                urgency_triggers=[
                    "no heat", "no AC", "system breakdown", "high energy bills",
                    "poor air quality", "strange noises"
                ],
                trust_signals=[
                    "Licensed & Insured", "Same-Day Service", "Free Estimates",
                    "Satisfaction Guaranteed", "Family-Owned Business"
                ],
                primary_keywords=[
                    "HVAC repair", "air conditioning service", "heating contractor",
                    "furnace repair", "HVAC installation"
                ],
                tone="friendly",
                technical_level="simple",
                primary_cta="Schedule Service",
                secondary_cta="Get Free Estimate"
            ),
            
            "plumbing": TradeContentStrategy(
                trade_name="plumbing",
                category=TradeCategory.RESIDENTIAL,
                pain_points=[
                    "Plumbing emergencies disrupting daily life",
                    "Water damage from leaks and pipe failures",
                    "Low water pressure and poor water quality",
                    "Expensive water bills from hidden leaks"
                ],
                value_propositions=[
                    "Fast, reliable plumbing repairs when you need them",
                    "Prevent costly water damage with expert service",
                    "Improve water pressure and quality in your home",
                    "Save money with leak detection and efficient fixtures"
                ],
                service_keywords=[
                    "plumbing repair", "drain cleaning", "water heater", "pipe repair",
                    "leak detection", "bathroom remodel", "kitchen plumbing"
                ],
                urgency_triggers=[
                    "water leak", "clogged drain", "no hot water", "pipe burst",
                    "toilet overflow", "water damage"
                ],
                trust_signals=[
                    "Licensed Plumber", "24/7 Emergency Service", "Upfront Pricing",
                    "Satisfaction Guaranteed", "Clean & Professional"
                ],
                primary_keywords=[
                    "plumbing repair", "emergency plumber", "drain cleaning",
                    "water heater repair", "residential plumber"
                ],
                tone="friendly",
                urgency_level="high",
                primary_cta="Call Now",
                secondary_cta="Schedule Service"
            ),
            
            "electrical": TradeContentStrategy(
                trade_name="electrical",
                category=TradeCategory.RESIDENTIAL,
                pain_points=[
                    "Electrical safety concerns for family",
                    "Outdated wiring and electrical panels",
                    "Insufficient outlets and lighting",
                    "High electricity bills from inefficient systems"
                ],
                value_propositions=[
                    "Safe, reliable electrical systems for your family",
                    "Modern wiring and panels for today's needs",
                    "Convenient outlets and beautiful lighting",
                    "Energy-efficient solutions that save money"
                ],
                service_keywords=[
                    "electrical repair", "panel upgrade", "outlet installation",
                    "lighting installation", "electrical safety", "home rewiring"
                ],
                urgency_triggers=[
                    "power outage", "electrical fire", "sparking outlet", "tripped breaker",
                    "flickering lights", "burning smell"
                ],
                trust_signals=[
                    "Licensed Electrician", "Safety First", "Code Compliant",
                    "Free Safety Inspection", "Fully Insured"
                ],
                primary_keywords=[
                    "electrical repair", "electrician", "panel upgrade",
                    "electrical installation", "home electrical"
                ],
                tone="friendly",
                technical_level="simple",
                primary_cta="Safety Inspection",
                secondary_cta="Get Quote"
            )
        }
        
        strategies.update(commercial_trades)
        strategies.update(residential_trades)
        
        return strategies
    
    async def generate_page_content(
        self,
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """
        Generate comprehensive page content with trade-specific optimization.
        
        This is the main entry point for content generation, orchestrating
        multiple AI calls to create cohesive, SEO-optimized content.
        """
        
        logger.info(f"Generating {request.content_type} content for {request.page_type} page")
        
        # Get trade-specific strategy
        strategy = self._get_trade_strategy(request.business)
        
        # Generate content based on type
        if request.content_type == "hero":
            return await self._generate_hero_content(request, strategy)
        elif request.content_type == "services":
            return await self._generate_services_content(request, strategy)
        elif request.content_type == "about":
            return await self._generate_about_content(request, strategy)
        elif request.content_type == "testimonials":
            return await self._generate_testimonials_content(request, strategy)
        elif request.content_type == "faq":
            return await self._generate_faq_content(request, strategy)
        elif request.content_type == "contact":
            return await self._generate_contact_content(request, strategy)
        elif request.content_type == "emergency":
            return await self._generate_emergency_content(request, strategy)
        elif request.content_type == "full_page":
            return await self._generate_full_page_content(request, strategy)
        else:
            raise ValueError(f"Unsupported content type: {request.content_type}")
    
    def _get_trade_strategy(self, business: Business) -> TradeContentStrategy:
        """Get the appropriate trade strategy for a business."""
        primary_trade = business.get_primary_trade()
        
        if primary_trade and primary_trade in self.trade_strategies:
            return self.trade_strategies[primary_trade]
        
        # Fallback to generic strategy based on category
        if business.trade_category == TradeCategory.COMMERCIAL:
            return self._get_generic_commercial_strategy()
        else:
            return self._get_generic_residential_strategy()
    
    def _get_generic_commercial_strategy(self) -> TradeContentStrategy:
        """Get generic commercial trade strategy."""
        return TradeContentStrategy(
            trade_name="commercial_services",
            category=TradeCategory.COMMERCIAL,
            pain_points=[
                "Business disruption from service issues",
                "Compliance and safety concerns",
                "High operational costs from inefficiencies",
                "Unreliable service providers"
            ],
            value_propositions=[
                "Reliable service to keep your business running",
                "Compliance expertise to avoid violations",
                "Cost-effective solutions that improve efficiency",
                "Professional service you can depend on"
            ],
            tone="professional",
            primary_cta="Schedule Service",
            secondary_cta="Get Quote"
        )
    
    def _get_generic_residential_strategy(self) -> TradeContentStrategy:
        """Get generic residential trade strategy."""
        return TradeContentStrategy(
            trade_name="home_services",
            category=TradeCategory.RESIDENTIAL,
            pain_points=[
                "Home maintenance and repair stress",
                "Finding reliable, trustworthy contractors",
                "Unexpected repair costs and emergencies",
                "Poor quality work from inexperienced providers"
            ],
            value_propositions=[
                "Stress-free home maintenance and repairs",
                "Trusted, experienced professionals",
                "Transparent pricing with no surprises",
                "Quality work backed by guarantees"
            ],
            tone="friendly",
            primary_cta="Get Free Estimate",
            secondary_cta="Call Now"
        )
    
    async def _generate_hero_content(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy
    ) -> GeneratedContent:
        """Generate hero section content."""
        
        prompt = f"""
        Create compelling hero section content for a {strategy.trade_name} website.
        
        Business Context:
        - Business Name: {request.business.name}
        - Trade: {strategy.trade_name}
        - Category: {strategy.category.value}
        - Service Areas: {', '.join(request.business.service_areas)}
        - Primary Trade: {request.business.get_primary_trade()}
        
        Brand Guidelines:
        - Tone: {strategy.tone}
        - Technical Level: {strategy.technical_level}
        - Primary CTA: {strategy.primary_cta}
        - Secondary CTA: {strategy.secondary_cta}
        
        Requirements:
        1. Create a powerful headline that addresses the main pain point
        2. Write a compelling subtitle that highlights the value proposition
        3. Include 3-4 trust signals/credentials
        4. Create primary and secondary call-to-action buttons
        5. Include location-based keywords naturally
        6. Ensure content is conversion-focused and SEO-optimized
        
        Pain Points to Address: {', '.join(strategy.pain_points[:3])}
        Value Propositions: {', '.join(strategy.value_propositions[:3])}
        Trust Signals: {', '.join(strategy.trust_signals[:4])}
        
        Return JSON with:
        {{
            "headline": "Main headline (60 chars max)",
            "subtitle": "Supporting subtitle (120 chars max)",
            "description": "Longer description paragraph (200 words max)",
            "trust_signals": ["signal1", "signal2", "signal3", "signal4"],
            "primary_cta": {{
                "text": "{strategy.primary_cta}",
                "action": "primary_action"
            }},
            "secondary_cta": {{
                "text": "{strategy.secondary_cta}",
                "action": "secondary_action"
            }},
            "background_image_alt": "Alt text for hero background image",
            "keywords_used": ["keyword1", "keyword2", "keyword3"]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert copywriter specializing in {strategy.trade_name} services. "
                              f"Create compelling, conversion-focused content that addresses customer pain points "
                              f"and highlights unique value propositions. Use a {strategy.tone} tone."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content_data = json.loads(response.choices[0].message.content)
        
        # Generate SEO metadata
        seo_metadata = await self._generate_seo_metadata(
            request, strategy, "hero", content_data
        )
        
        return GeneratedContent(
            content_type="hero",
            page_type=request.page_type,
            primary_content=content_data,
            seo_metadata=seo_metadata,
            conversion_elements={
                "primary_cta": content_data["primary_cta"],
                "secondary_cta": content_data["secondary_cta"],
                "trust_signals": content_data["trust_signals"]
            },
            trade_specific_elements={
                "trade": strategy.trade_name,
                "category": strategy.category.value,
                "pain_points_addressed": strategy.pain_points[:3],
                "value_props_highlighted": strategy.value_propositions[:3]
            },
            generation_metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat(),
                "strategy_used": strategy.trade_name,
                "tone": strategy.tone
            }
        )
    
    async def _generate_services_content(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy
    ) -> GeneratedContent:
        """Generate services section content."""
        
        all_trades = request.business.get_all_trades()
        
        prompt = f"""
        Create comprehensive services section content for a {strategy.trade_name} business.
        
        Business Context:
        - Business Name: {request.business.name}
        - All Services: {', '.join(all_trades)}
        - Primary Trade: {request.business.get_primary_trade()}
        - Service Areas: {', '.join(request.business.service_areas)}
        
        Requirements:
        1. Create a compelling section title
        2. Write a brief introduction paragraph
        3. Generate 4-6 main service offerings with descriptions
        4. Include benefits and features for each service
        5. Add relevant keywords naturally
        6. Include pricing indicators where appropriate
        
        Service Keywords: {', '.join(strategy.service_keywords)}
        Value Propositions: {', '.join(strategy.value_propositions)}
        
        Return JSON with:
        {{
            "section_title": "Services section title",
            "introduction": "Brief introduction paragraph",
            "services": [
                {{
                    "name": "Service name",
                    "description": "Service description (100 words)",
                    "benefits": ["benefit1", "benefit2", "benefit3"],
                    "features": ["feature1", "feature2"],
                    "keywords": ["keyword1", "keyword2"],
                    "pricing_indicator": "Starting at $X" or "Free Estimate" or null
                }}
            ],
            "cta_text": "Call-to-action for services section",
            "keywords_used": ["keyword1", "keyword2", "keyword3"]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert in {strategy.trade_name} services. "
                              f"Create detailed, informative content that helps customers "
                              f"understand services and benefits. Use a {strategy.tone} tone."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.6
        )
        
        content_data = json.loads(response.choices[0].message.content)
        
        # Generate SEO metadata
        seo_metadata = await self._generate_seo_metadata(
            request, strategy, "services", content_data
        )
        
        return GeneratedContent(
            content_type="services",
            page_type=request.page_type,
            primary_content=content_data,
            seo_metadata=seo_metadata,
            conversion_elements={
                "cta_text": content_data["cta_text"],
                "pricing_indicators": [s.get("pricing_indicator") for s in content_data["services"] if s.get("pricing_indicator")]
            },
            trade_specific_elements={
                "services_count": len(content_data["services"]),
                "trade_keywords": strategy.service_keywords,
                "all_business_trades": all_trades
            },
            generation_metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat(),
                "strategy_used": strategy.trade_name
            }
        )
    
    async def _generate_emergency_content(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy
    ) -> GeneratedContent:
        """Generate emergency services content."""
        
        prompt = f"""
        Create urgent, compelling emergency services content for {strategy.trade_name}.
        
        Business Context:
        - Business Name: {request.business.name}
        - Trade: {strategy.trade_name}
        - Phone: {request.business.phone_number}
        - Service Areas: {', '.join(request.business.service_areas)}
        
        Requirements:
        1. Create urgent, action-oriented headlines
        2. Emphasize 24/7 availability and fast response
        3. List common emergency situations
        4. Include response time guarantees
        5. Highlight emergency-specific trust signals
        6. Create multiple urgent CTAs
        
        Urgency Triggers: {', '.join(strategy.urgency_triggers)}
        Trust Signals: {', '.join(strategy.trust_signals)}
        
        Return JSON with:
        {{
            "emergency_headline": "Urgent headline for emergencies",
            "response_promise": "Response time guarantee",
            "emergency_situations": [
                {{
                    "situation": "Emergency situation",
                    "description": "Brief description",
                    "urgency_level": "high|medium|critical"
                }}
            ],
            "emergency_ctas": [
                {{
                    "text": "CTA text",
                    "action": "call|form|text",
                    "urgency": "high|critical"
                }}
            ],
            "trust_signals": ["24/7 Available", "Licensed & Insured", "etc"],
            "emergency_number": "{request.business.phone_number or 'BUSINESS_PHONE'}",
            "coverage_areas": {request.business.service_areas}
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert in emergency {strategy.trade_name} services. "
                              f"Create urgent, compelling content that motivates immediate action "
                              f"while building trust and confidence."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content_data = json.loads(response.choices[0].message.content)
        
        return GeneratedContent(
            content_type="emergency",
            page_type=request.page_type,
            primary_content=content_data,
            seo_metadata={
                "title": f"24/7 Emergency {strategy.trade_name.title()} Services - {request.business.name}",
                "description": f"Emergency {strategy.trade_name} services available 24/7. Fast response, licensed professionals. Call now for immediate help.",
                "keywords": [f"emergency {strategy.trade_name}", f"24/7 {strategy.trade_name}", f"{strategy.trade_name} emergency"]
            },
            conversion_elements={
                "emergency_ctas": content_data["emergency_ctas"],
                "response_promise": content_data["response_promise"],
                "phone_number": content_data["emergency_number"]
            },
            trade_specific_elements={
                "urgency_triggers": strategy.urgency_triggers,
                "emergency_situations": content_data["emergency_situations"]
            },
            generation_metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat(),
                "urgency_level": strategy.urgency_level
            }
        )
    
    async def _generate_seo_metadata(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy,
        content_type: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate SEO metadata for content."""
        
        primary_location = request.business.service_areas[0] if request.business.service_areas else "Local Area"
        
        # Generate title
        if content_type == "hero":
            title = f"{request.business.name} - {strategy.trade_name.title()} Services in {primary_location}"
        else:
            title = f"{content_type.title()} - {request.business.name} {strategy.trade_name.title()}"
        
        # Generate description
        description_prompt = f"""
        Create a compelling meta description (150-160 characters) for a {content_type} section 
        of a {strategy.trade_name} website. Include the business name "{request.business.name}" 
        and location "{primary_location}". Focus on the main value proposition and include a call to action.
        
        Content summary: {str(content_data)[:200]}...
        """
        
        desc_response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an SEO expert. Create compelling meta descriptions."},
                {"role": "user", "content": description_prompt}
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        description = desc_response.choices[0].message.content.strip().replace('"', '')
        
        # Generate keywords
        keywords = strategy.primary_keywords[:5] + [
            f"{strategy.trade_name} {primary_location}",
            f"{request.business.name}",
            f"{strategy.trade_name} services"
        ]
        
        return {
            "title": title[:60],  # Limit to 60 characters
            "description": description[:160],  # Limit to 160 characters
            "keywords": keywords,
            "og_title": title,
            "og_description": description,
            "canonical_url": f"/{content_type}" if content_type != "hero" else "/",
            "schema_markup": self._generate_schema_markup(request, strategy, content_type)
        }
    
    def _generate_schema_markup(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy,
        content_type: str
    ) -> Dict[str, Any]:
        """Generate JSON-LD schema markup."""
        
        base_schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": request.business.name,
            "description": f"{strategy.trade_name.title()} services in {', '.join(request.business.service_areas)}",
            "url": request.website.get_website_url() if hasattr(request.website, 'get_website_url') else None,
            "telephone": request.business.phone_number,
            "email": request.business.business_email,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": request.business.business_address
            },
            "areaServed": [
                {"@type": "City", "name": area} for area in request.business.service_areas
            ],
            "serviceType": strategy.trade_name.title(),
            "priceRange": "$$"  # Could be made dynamic based on trade
        }
        
        if content_type == "services":
            base_schema["hasOfferCatalog"] = {
                "@type": "OfferCatalog",
                "name": f"{strategy.trade_name.title()} Services",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": trade.title(),
                            "serviceType": trade
                        }
                    } for trade in request.business.get_all_trades()
                ]
            }
        
        return base_schema
    
    async def _generate_full_page_content(
        self,
        request: ContentGenerationRequest,
        strategy: TradeContentStrategy
    ) -> GeneratedContent:
        """Generate content for a complete page."""
        
        # Generate multiple content sections in parallel
        tasks = [
            self._generate_hero_content(request, strategy),
            self._generate_services_content(request, strategy),
        ]
        
        # Add emergency content for applicable trades
        if strategy.urgency_level in ["high", "emergency"]:
            emergency_request = ContentGenerationRequest(
                business=request.business,
                branding=request.branding,
                template=request.template,
                website=request.website,
                page_type="emergency",
                content_type="emergency"
            )
            tasks.append(self._generate_emergency_content(emergency_request, strategy))
        
        results = await asyncio.gather(*tasks)
        
        # Combine all content
        combined_content = {
            "hero": results[0].primary_content,
            "services": results[1].primary_content,
        }
        
        if len(results) > 2:
            combined_content["emergency"] = results[2].primary_content
        
        # Combine SEO metadata
        combined_seo = results[0].seo_metadata
        combined_seo["keywords"].extend(results[1].seo_metadata["keywords"])
        
        return GeneratedContent(
            content_type="full_page",
            page_type=request.page_type,
            primary_content=combined_content,
            seo_metadata=combined_seo,
            conversion_elements={
                "hero_ctas": results[0].conversion_elements,
                "services_cta": results[1].conversion_elements,
                "emergency_ctas": results[2].conversion_elements if len(results) > 2 else None
            },
            trade_specific_elements={
                "strategy": strategy.dict(),
                "content_sections": list(combined_content.keys())
            },
            generation_metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat(),
                "sections_generated": len(combined_content),
                "total_tokens_estimated": sum(len(str(r.primary_content)) for r in results)
            }
        )
    
    async def optimize_content_for_conversions(
        self,
        content: GeneratedContent,
        business: Business,
        conversion_goals: List[str]
    ) -> GeneratedContent:
        """
        Optimize existing content for better conversions.
        
        Analyzes content and suggests improvements for higher conversion rates.
        """
        
        optimization_prompt = f"""
        Analyze and optimize this website content for better conversions:
        
        Current Content: {json.dumps(content.primary_content, indent=2)}
        
        Business: {business.name}
        Trade: {business.get_primary_trade()}
        Conversion Goals: {', '.join(conversion_goals)}
        
        Provide optimization suggestions for:
        1. Headlines and copy improvements
        2. Call-to-action optimization
        3. Trust signal enhancements
        4. Urgency and scarcity elements
        5. Social proof opportunities
        
        Return JSON with:
        {{
            "optimized_content": {{...}},
            "improvements_made": ["improvement1", "improvement2"],
            "conversion_score": 85,
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a conversion rate optimization expert. "
                              "Analyze content and provide specific improvements to increase conversions."
                },
                {"role": "user", "content": optimization_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        optimization_data = json.loads(response.choices[0].message.content)
        
        # Update content with optimizations
        content.primary_content = optimization_data["optimized_content"]
        content.generation_metadata["optimized_at"] = datetime.utcnow().isoformat()
        content.generation_metadata["conversion_score"] = optimization_data["conversion_score"]
        content.generation_metadata["improvements"] = optimization_data["improvements_made"]
        
        return content
    
    async def generate_local_seo_content(
        self,
        business: Business,
        target_locations: List[str],
        trade: str
    ) -> Dict[str, Any]:
        """Generate location-specific SEO content."""
        
        location_content = {}
        
        for location in target_locations:
            prompt = f"""
            Create location-specific SEO content for {trade} services in {location}.
            
            Business: {business.name}
            Target Location: {location}
            Trade: {trade}
            
            Generate:
            1. Location-specific headline
            2. Local area description
            3. Location-based keywords
            4. Local landmarks/neighborhoods to mention
            5. Location-specific service benefits
            
            Return JSON with location-optimized content.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a local SEO expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            location_content[location] = json.loads(response.choices[0].message.content)
        
        return location_content
