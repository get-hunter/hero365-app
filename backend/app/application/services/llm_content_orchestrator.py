"""
LLM Content Orchestrator Service

Orchestrates multiple LLM adapters to generate comprehensive, SEO-optimized content
for contractor websites. This is the central service that coordinates all content
generation activities in the Hero365 website building pipeline.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from ...infrastructure.adapters.content_generation_factory import create_content_adapter, get_provider_info
from ...application.ports.content_generation_port import ContentGenerationPort
from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding

logger = logging.getLogger(__name__)


class LLMContentOrchestrator:
    """
    Orchestrates multiple LLM adapters to generate comprehensive website content.
    
    This service coordinates:
    - Page content generation (titles, descriptions, body copy)
    - SEO metadata generation (meta tags, schema markup)
    - Service descriptions and pricing content
    - Local SEO content (location-specific pages)
    - Blog/educational content
    """
    
    def __init__(
        self,
        business_data: Dict[str, Any],
        seo_scaffolding: Dict[str, Any],
        config: Dict[str, Any]
    ):
        self.business_data = business_data
        self.seo_scaffolding = seo_scaffolding
        self.config = config
        
        # Initialize LLM adapters
        self.adapters = self._initialize_adapters()
        self.primary_adapter = self._get_primary_adapter()
        self.fallback_adapters = self._get_fallback_adapters()
        
        logger.info(f"Initialized LLM orchestrator for {business_data['profile'].get('business_name')}")
        logger.info(f"Primary adapter: {type(self.primary_adapter).__name__ if self.primary_adapter else 'None'}")
        logger.info(f"Fallback adapters: {len(self.fallback_adapters)}")
    
    async def generate_all_content(self) -> Dict[str, Any]:
        """
        Generate all content types for the website.
        
        Returns:
            Dict containing all generated content organized by type
        """
        
        logger.info("Starting comprehensive content generation")
        
        try:
            # Initialize results structure
            results = {
                "pages": [],
                "content_items": [],
                "seo_configs": {},
                "quality_score": 0,
                "generation_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "business_id": self.business_data.get("profile", {}).get("business_id"),
                    "business_name": self.business_data.get("profile", {}).get("business_name"),
                    "total_pages": 0,
                    "total_content_items": 0
                }
            }
            
            # Step 1: Generate core page content
            logger.info("Generating core page content")
            core_pages = await self._generate_core_pages()
            results["pages"].extend(core_pages)
            
            # Step 2: Generate service-location pages from SEO scaffolding
            logger.info("Generating service-location pages")
            service_location_pages = await self._generate_service_location_pages()
            results["pages"].extend(service_location_pages)
            
            # Step 3: Generate service descriptions and content
            logger.info("Generating service content")
            service_content = await self._generate_service_content()
            results["content_items"].extend(service_content)
            
            # Step 4: Generate SEO configurations
            logger.info("Generating SEO configurations")
            seo_configs = await self._generate_seo_configurations()
            results["seo_configs"] = seo_configs
            
            # Step 5: Generate additional content (blog, FAQ, etc.)
            logger.info("Generating additional content")
            additional_content = await self._generate_additional_content()
            results["content_items"].extend(additional_content)
            
            # Calculate quality score and finalize metadata
            results["quality_score"] = self._calculate_quality_score(results)
            results["generation_metadata"]["total_pages"] = len(results["pages"])
            results["generation_metadata"]["total_content_items"] = len(results["content_items"])
            
            logger.info(f"Content generation completed: {len(results['pages'])} pages, {len(results['content_items'])} content items")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            raise
    
    async def _generate_core_pages(self) -> List[Dict[str, Any]]:
        """Generate content for core website pages using LLM adapters."""
        
        if not self.primary_adapter:
            logger.warning("No LLM adapters available, using fallback content")
            return await self._generate_core_pages_fallback()
        
        core_pages = []
        business = self._create_business_entity()
        branding = self._create_branding_entity()
        
        # Define core pages to generate
        page_types = ["home", "about", "services", "contact"]
        
        for page_type in page_types:
            try:
                # Generate content using LLM adapter with fallback
                page_content = await self._generate_content_with_fallback(
                    f"{page_type} page",
                    self._generate_page_content_with_adapter,
                    business,
                    branding,
                    page_type
                )
                
                if page_content:
                    core_pages.append(page_content)
                else:
                    # Fallback to static content for this page
                    fallback_page = await self._generate_fallback_page(page_type, business)
                    if fallback_page:
                        core_pages.append(fallback_page)
                        
            except Exception as e:
                logger.error(f"Error generating {page_type} page: {str(e)}")
                # Continue with other pages
                continue
        
        logger.info(f"Generated {len(core_pages)} core pages with LLM adapters")
        return core_pages
    
    async def _generate_core_pages_fallback(self) -> List[Dict[str, Any]]:
        """Fallback method for generating core pages without LLM adapters."""
        
        core_pages = []
        business_name = self.business_data.get("profile", {}).get("business_name", "Professional Services")
        primary_trade = self._get_primary_trade()
        service_areas = self.business_data.get("profile", {}).get("service_areas", [])
        
        # Home page
        home_page = {
            "slug": "home",
            "path": "/",
            "title": f"{business_name} - Professional {primary_trade} Services",
            "meta_description": f"Professional {primary_trade.lower()} services by {business_name}. Serving {', '.join(service_areas[:3])}. Licensed, insured, and trusted by homeowners.",
            "content": {
                "hero": {
                    "headline": f"Professional {primary_trade} Services You Can Trust",
                    "subheadline": f"Expert {primary_trade.lower()} solutions for your home and business",
                    "cta_text": "Get Free Estimate",
                    "background_focus": "service_quality"
                },
                "services_preview": {
                    "title": f"Our {primary_trade} Services",
                    "description": f"Comprehensive {primary_trade.lower()} services for residential and commercial properties"
                },
                "about_preview": {
                    "title": f"Why Choose {business_name}?",
                    "points": [
                        "Licensed and insured professionals",
                        "24/7 emergency service available",
                        "Satisfaction guaranteed",
                        "Local expertise and fast response"
                    ]
                }
            },
            "seo": {
                "canonical": "/",
                "og_type": "website",
                "schema_type": "LocalBusiness"
            }
        }
        core_pages.append(home_page)
        
        # About page
        about_page = {
            "slug": "about",
            "path": "/about",
            "title": f"About {business_name} - Your Trusted {primary_trade} Experts",
            "meta_description": f"Learn about {business_name}, your trusted {primary_trade.lower()} professionals. Years of experience serving {', '.join(service_areas[:2])} with quality workmanship.",
            "content": {
                "hero": {
                    "headline": f"About {business_name}",
                    "subheadline": f"Your trusted {primary_trade.lower()} professionals"
                },
                "story": {
                    "title": "Our Story",
                    "content": f"At {business_name}, we've been providing exceptional {primary_trade.lower()} services to homeowners and businesses. Our commitment to quality workmanship and customer satisfaction has made us a trusted name in the industry."
                },
                "values": {
                    "title": "Our Values",
                    "items": [
                        {"name": "Quality", "description": "We never compromise on the quality of our work"},
                        {"name": "Reliability", "description": "You can count on us to be there when you need us"},
                        {"name": "Integrity", "description": "Honest pricing and transparent communication"},
                        {"name": "Expertise", "description": "Continuous training and industry certifications"}
                    ]
                }
            },
            "seo": {
                "canonical": "/about",
                "og_type": "article"
            }
        }
        core_pages.append(about_page)
        
        # Services overview page
        services_page = {
            "slug": "services",
            "path": "/services",
            "title": f"{primary_trade} Services - {business_name}",
            "meta_description": f"Complete {primary_trade.lower()} services including installation, repair, and maintenance. Professional service in {', '.join(service_areas[:3])}.",
            "content": {
                "hero": {
                    "headline": f"Professional {primary_trade} Services",
                    "subheadline": "Complete solutions for all your needs"
                },
                "services_grid": {
                    "title": "Our Services",
                    "description": f"We offer a full range of {primary_trade.lower()} services for residential and commercial properties"
                }
            },
            "seo": {
                "canonical": "/services",
                "og_type": "article"
            }
        }
        core_pages.append(services_page)
        
        # Contact page
        contact_page = {
            "slug": "contact",
            "path": "/contact",
            "title": f"Contact {business_name} - Get Your Free Estimate",
            "meta_description": f"Contact {business_name} for professional {primary_trade.lower()} services. Free estimates, 24/7 emergency service. Call now!",
            "content": {
                "hero": {
                    "headline": "Get Your Free Estimate Today",
                    "subheadline": "Ready to help with all your needs"
                },
                "contact_info": {
                    "title": "Contact Information",
                    "phone": self.business_data.get("profile", {}).get("phone"),
                    "email": self.business_data.get("profile", {}).get("email"),
                    "address": self.business_data.get("profile", {}).get("address"),
                    "service_areas": service_areas
                },
                "emergency_notice": {
                    "title": "24/7 Emergency Service",
                    "description": "Need immediate assistance? We're available 24/7 for emergency situations."
                }
            },
            "seo": {
                "canonical": "/contact",
                "og_type": "article"
            }
        }
        core_pages.append(contact_page)
        
        logger.info(f"Generated {len(core_pages)} core pages")
        return core_pages
    
    async def _generate_service_location_pages(self) -> List[Dict[str, Any]]:
        """Generate service-location specific pages from SEO scaffolding."""
        
        service_location_pages = []
        scaffolding_pages = self.seo_scaffolding.get("service_location_pages", [])
        
        for page_data in scaffolding_pages[:20]:  # Limit to top 20 for initial generation
            try:
                service_name = page_data.get("service_display_name", "Service")
                location_name = page_data.get("location_name", "Local Area")
                business_name = self.business_data.get("profile", {}).get("business_name", "Professional Services")
                
                page = {
                    "slug": page_data.get("page_slug", f"service-location-{len(service_location_pages)}"),
                    "path": f"/{page_data.get('page_slug', f'service-location-{len(service_location_pages)}')}",
                    "title": f"{service_name} in {location_name} - {business_name}",
                    "meta_description": f"Professional {service_name.lower()} services in {location_name}. Licensed, insured, and trusted by local residents. Free estimates available.",
                    "content": {
                        "hero": {
                            "headline": f"{service_name} in {location_name}",
                            "subheadline": f"Professional {service_name.lower()} services for {location_name} residents",
                            "cta_text": "Get Free Estimate",
                            "location_focus": location_name
                        },
                        "service_details": {
                            "title": f"Professional {service_name} Services",
                            "description": f"We provide comprehensive {service_name.lower()} services to homeowners and businesses in {location_name}.",
                            "benefits": [
                                "Licensed and insured professionals",
                                "Local expertise and fast response",
                                "Competitive pricing",
                                "Satisfaction guaranteed"
                            ]
                        },
                        "local_info": {
                            "title": f"Serving {location_name}",
                            "description": f"As local {service_name.lower()} experts, we understand the unique needs of {location_name} properties."
                        }
                    },
                    "seo": {
                        "canonical": f"/{page_data.get('page_slug')}",
                        "og_type": "article",
                        "local_business_schema": True,
                        "service_area": location_name,
                        "primary_service": service_name
                    },
                    "priority_score": page_data.get("priority_score", 50)
                }
                
                service_location_pages.append(page)
                
            except Exception as e:
                logger.warning(f"Error generating service-location page: {str(e)}")
                continue
        
        logger.info(f"Generated {len(service_location_pages)} service-location pages")
        return service_location_pages
    
    async def _generate_service_content(self) -> List[Dict[str, Any]]:
        """Generate detailed service descriptions and content."""
        
        service_content = []
        services = self.business_data.get("services", [])
        
        for service in services[:10]:  # Limit to top 10 services
            try:
                content_item = {
                    "type": "service_description",
                    "service_id": service.get("id"),
                    "service_name": service.get("name", "Professional Service"),
                    "content": {
                        "short_description": f"Professional {service.get('name', 'service').lower()} services with guaranteed quality and competitive pricing.",
                        "detailed_description": f"Our experienced team provides comprehensive {service.get('name', 'service').lower()} solutions for residential and commercial properties. We use industry-leading techniques and high-quality materials to ensure lasting results.",
                        "key_benefits": [
                            "Expert installation and service",
                            "Quality materials and workmanship",
                            "Competitive pricing",
                            "Satisfaction guaranteed"
                        ],
                        "process_steps": [
                            "Initial consultation and assessment",
                            "Detailed estimate and planning",
                            "Professional installation/service",
                            "Quality inspection and cleanup"
                        ]
                    },
                    "seo": {
                        "keywords": [
                            service.get("name", "service").lower(),
                            f"{service.get('name', 'service').lower()} service",
                            f"professional {service.get('name', 'service').lower()}"
                        ]
                    }
                }
                
                service_content.append(content_item)
                
            except Exception as e:
                logger.warning(f"Error generating service content: {str(e)}")
                continue
        
        logger.info(f"Generated {len(service_content)} service content items")
        return service_content
    
    async def _generate_seo_configurations(self) -> Dict[str, Any]:
        """Generate SEO configurations for the website."""
        
        business_name = self.business_data.get("profile", {}).get("business_name", "Professional Services")
        primary_trade = self._get_primary_trade()
        service_areas = self.business_data.get("profile", {}).get("service_areas", [])
        
        seo_config = {
            "global": {
                "site_name": business_name,
                "default_title_suffix": f" - {business_name}",
                "default_description": f"Professional {primary_trade.lower()} services by {business_name}. Serving {', '.join(service_areas[:3])}.",
                "keywords": [
                    primary_trade.lower(),
                    f"{primary_trade.lower()} service",
                    f"professional {primary_trade.lower()}",
                    business_name.lower()
                ],
                "og_image": "/images/og-default.jpg",
                "twitter_card": "summary_large_image"
            },
            "local_seo": {
                "business_name": business_name,
                "service_areas": service_areas,
                "primary_service": primary_trade,
                "schema_markup": {
                    "@context": "https://schema.org",
                    "@type": "LocalBusiness",
                    "name": business_name,
                    "description": f"Professional {primary_trade.lower()} services",
                    "serviceArea": service_areas
                }
            },
            "structured_data": {
                "organization": {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": business_name,
                    "description": f"Professional {primary_trade.lower()} services"
                }
            }
        }
        
        logger.info("Generated SEO configurations")
        return seo_config
    
    async def _generate_additional_content(self) -> List[Dict[str, Any]]:
        """Generate additional content like FAQ, blog posts, etc."""
        
        additional_content = []
        primary_trade = self._get_primary_trade()
        
        # FAQ content
        faq_content = {
            "type": "faq",
            "title": "Frequently Asked Questions",
            "items": [
                {
                    "question": f"How much does {primary_trade.lower()} service cost?",
                    "answer": f"The cost of {primary_trade.lower()} service varies depending on the scope of work. We provide free estimates to give you accurate pricing for your specific needs."
                },
                {
                    "question": "Are you licensed and insured?",
                    "answer": "Yes, we are fully licensed and insured for your protection and peace of mind."
                },
                {
                    "question": "Do you offer emergency services?",
                    "answer": "Yes, we provide 24/7 emergency services for urgent situations."
                },
                {
                    "question": "What areas do you serve?",
                    "answer": f"We serve {', '.join(self.business_data.get('profile', {}).get('service_areas', ['the local area']))} and surrounding communities."
                }
            ]
        }
        additional_content.append(faq_content)
        
        logger.info(f"Generated {len(additional_content)} additional content items")
        return additional_content
    
    def _get_primary_trade(self) -> str:
        """Get the primary trade/service type for the business."""
        
        # Try to get from business data
        profile = self.business_data.get("profile", {})
        
        if profile.get("trade_type"):
            return profile["trade_type"].upper()
        
        # Fallback to first service if available
        services = self.business_data.get("services", [])
        if services:
            return services[0].get("category", "Professional Services")
        
        return "Professional Services"
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> int:
        """Calculate a quality score for the generated content."""
        
        score = 70  # Base score
        
        # Add points for content completeness
        if len(results["pages"]) >= 4:
            score += 10
        
        if len(results["content_items"]) >= 5:
            score += 10
        
        if results["seo_configs"]:
            score += 10
        
        # Cap at 100
        return min(score, 100)
    
    def _initialize_adapters(self) -> Dict[str, ContentGenerationPort]:
        """Initialize available LLM adapters based on configuration."""
        
        adapters = {}
        provider_info = get_provider_info()
        
        # Get preferred providers from config
        preferred_providers = self.config.get("preferred_providers", ["openai", "gemini", "claude"])
        
        # Initialize adapters in order of preference
        for provider in preferred_providers:
            if provider in provider_info and provider_info[provider]["configured"]:
                try:
                    adapter = create_content_adapter(provider)
                    adapters[provider] = adapter
                    logger.info(f"Initialized {provider} adapter successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize {provider} adapter: {str(e)}")
        
        # Fallback: try to initialize any configured adapter
        if not adapters:
            for provider, info in provider_info.items():
                if info["configured"]:
                    try:
                        adapter = create_content_adapter(provider)
                        adapters[provider] = adapter
                        logger.info(f"Initialized fallback {provider} adapter")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to initialize fallback {provider} adapter: {str(e)}")
        
        if not adapters:
            logger.error("No LLM adapters could be initialized. Check API key configuration.")
        
        return adapters
    
    def _get_primary_adapter(self) -> Optional[ContentGenerationPort]:
        """Get the primary adapter for content generation."""
        
        if not self.adapters:
            return None
        
        # Use configured primary provider if available
        primary_provider = self.config.get("primary_provider")
        if primary_provider and primary_provider in self.adapters:
            return self.adapters[primary_provider]
        
        # Use first available adapter
        return next(iter(self.adapters.values()))
    
    def _get_fallback_adapters(self) -> List[ContentGenerationPort]:
        """Get fallback adapters for redundancy."""
        
        fallbacks = []
        primary_provider = None
        
        if self.primary_adapter:
            # Find the primary provider name
            for provider, adapter in self.adapters.items():
                if adapter == self.primary_adapter:
                    primary_provider = provider
                    break
        
        # Add all other adapters as fallbacks
        for provider, adapter in self.adapters.items():
            if provider != primary_provider:
                fallbacks.append(adapter)
        
        return fallbacks
    
    async def _generate_content_with_fallback(
        self, 
        content_type: str, 
        generation_func, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Generate content with automatic fallback to other adapters if primary fails.
        
        Args:
            content_type: Type of content being generated (for logging)
            generation_func: Function to call on the adapter
            *args, **kwargs: Arguments to pass to the generation function
            
        Returns:
            Generated content or None if all adapters fail
        """
        
        # Try primary adapter first
        if self.primary_adapter:
            try:
                logger.info(f"Generating {content_type} with primary adapter")
                result = await generation_func(self.primary_adapter, *args, **kwargs)
                return result
            except Exception as e:
                logger.warning(f"Primary adapter failed for {content_type}: {str(e)}")
        
        # Try fallback adapters
        for i, adapter in enumerate(self.fallback_adapters):
            try:
                logger.info(f"Trying fallback adapter {i+1} for {content_type}")
                result = await generation_func(adapter, *args, **kwargs)
                return result
            except Exception as e:
                logger.warning(f"Fallback adapter {i+1} failed for {content_type}: {str(e)}")
        
        logger.error(f"All adapters failed for {content_type}")
        return None
    
    def _create_business_entity(self) -> Business:
        """Create a Business entity from business_data for adapter compatibility."""
        
        profile = self.business_data.get("profile", {})
        
        # This is a simplified conversion - in a real implementation,
        # you'd want to properly map all fields
        business = Business(
            id=profile.get("business_id"),
            name=profile.get("business_name", "Professional Services"),
            industry=profile.get("industry", "Professional Services"),
            description=profile.get("description", ""),
            phone_number=profile.get("phone", ""),
            business_email=profile.get("email", ""),
            business_address=profile.get("address", ""),
            website=profile.get("website", ""),
            service_areas=profile.get("service_areas", []),
            primary_trade=profile.get("trade_type", "professional_services"),
            market_focus="both"  # Default value
        )
        
        return business
    
    def _create_branding_entity(self) -> BusinessBranding:
        """Create a BusinessBranding entity with default values."""
        
        profile = self.business_data.get("profile", {})
        
        branding = BusinessBranding(
            business_id=profile.get("business_id"),
            primary_color="#1E3A8A",  # Professional blue
            secondary_color="#3B82F6",  # Lighter blue
            accent_color="#EF4444",  # Red for CTAs
            font_family="Inter, sans-serif",
            theme_name="Professional"
        )
        
        return branding
    
    async def _generate_page_content_with_adapter(
        self, 
        adapter: ContentGenerationPort, 
        business: Business, 
        branding: BusinessBranding, 
        page_type: str
    ) -> Dict[str, Any]:
        """Generate page content using a specific LLM adapter."""
        
        # Create context for the page generation
        context = {
            "seo_scaffolding": self.seo_scaffolding,
            "business_data": self.business_data,
            "page_requirements": self._get_page_requirements(page_type)
        }
        
        # Generate content using the adapter
        page_content = await adapter.generate_page_content(
            business=business,
            branding=branding,
            page_type=page_type,
            context=context
        )
        
        # Enhance with our specific formatting
        enhanced_content = self._enhance_page_content(page_content, page_type, business)
        
        return enhanced_content
    
    async def _generate_fallback_page(self, page_type: str, business: Business) -> Dict[str, Any]:
        """Generate a fallback page when LLM adapters fail."""
        
        business_name = business.name
        primary_trade = self._get_primary_trade()
        service_areas = business.service_areas or []
        
        if page_type == "home":
            return {
                "slug": "home",
                "path": "/",
                "title": f"{business_name} - Professional {primary_trade} Services",
                "meta_description": f"Professional {primary_trade.lower()} services by {business_name}. Serving {', '.join(service_areas[:3])}. Licensed, insured, and trusted by homeowners.",
                "content": {
                    "hero": {
                        "headline": f"Professional {primary_trade} Services You Can Trust",
                        "subheadline": f"Expert {primary_trade.lower()} solutions for your home and business",
                        "cta_text": "Get Free Estimate"
                    }
                },
                "seo": {"canonical": "/", "og_type": "website"},
                "generation_method": "fallback"
            }
        elif page_type == "about":
            return {
                "slug": "about",
                "path": "/about",
                "title": f"About {business_name} - Your Trusted {primary_trade} Experts",
                "meta_description": f"Learn about {business_name}, your trusted {primary_trade.lower()} professionals.",
                "content": {
                    "hero": {
                        "headline": f"About {business_name}",
                        "subheadline": f"Your trusted {primary_trade.lower()} professionals"
                    }
                },
                "seo": {"canonical": "/about", "og_type": "article"},
                "generation_method": "fallback"
            }
        elif page_type == "services":
            return {
                "slug": "services",
                "path": "/services",
                "title": f"{primary_trade} Services - {business_name}",
                "meta_description": f"Complete {primary_trade.lower()} services including installation, repair, and maintenance.",
                "content": {
                    "hero": {
                        "headline": f"Professional {primary_trade} Services",
                        "subheadline": "Complete solutions for all your needs"
                    }
                },
                "seo": {"canonical": "/services", "og_type": "article"},
                "generation_method": "fallback"
            }
        elif page_type == "contact":
            return {
                "slug": "contact",
                "path": "/contact",
                "title": f"Contact {business_name} - Get Your Free Estimate",
                "meta_description": f"Contact {business_name} for professional {primary_trade.lower()} services. Free estimates available.",
                "content": {
                    "hero": {
                        "headline": "Get Your Free Estimate Today",
                        "subheadline": "Ready to help with all your needs"
                    }
                },
                "seo": {"canonical": "/contact", "og_type": "article"},
                "generation_method": "fallback"
            }
        
        return None
    
    def _get_page_requirements(self, page_type: str) -> Dict[str, Any]:
        """Get specific requirements for each page type."""
        
        requirements = {
            "home": {
                "sections": ["hero", "services_preview", "about_preview", "testimonials", "cta"],
                "seo_priority": "high",
                "target_keywords": [self._get_primary_trade().lower(), "professional services"],
                "conversion_focus": True
            },
            "about": {
                "sections": ["hero", "story", "values", "team", "certifications"],
                "seo_priority": "medium",
                "target_keywords": ["about", "company", "professional"],
                "conversion_focus": False
            },
            "services": {
                "sections": ["hero", "services_grid", "process", "pricing_info"],
                "seo_priority": "high",
                "target_keywords": [self._get_primary_trade().lower(), "services"],
                "conversion_focus": True
            },
            "contact": {
                "sections": ["hero", "contact_form", "contact_info", "service_areas"],
                "seo_priority": "medium",
                "target_keywords": ["contact", "free estimate"],
                "conversion_focus": True
            }
        }
        
        return requirements.get(page_type, {})
    
    def _enhance_page_content(self, page_content: Dict[str, Any], page_type: str, business: Business) -> Dict[str, Any]:
        """Enhance LLM-generated content with our specific formatting and metadata."""
        
        # Ensure required fields exist
        enhanced = {
            "slug": page_content.get("slug", page_type),
            "path": page_content.get("path", f"/{page_type}" if page_type != "home" else "/"),
            "title": page_content.get("title", f"{business.name} - {page_type.title()}"),
            "meta_description": page_content.get("meta_description", ""),
            "content": page_content.get("content", {}),
            "seo": page_content.get("seo", {}),
            "generation_method": "llm_adapter",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Add default SEO if missing
        if not enhanced["seo"]:
            enhanced["seo"] = {
                "canonical": enhanced["path"],
                "og_type": "website" if page_type == "home" else "article"
            }
        
        return enhanced
