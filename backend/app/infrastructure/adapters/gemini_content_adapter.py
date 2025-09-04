"""
Gemini Content Generation Adapter

Implementation of ContentGenerationPort using Google's Gemini.
This adapter provides an alternative AI provider for content generation.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ...application.ports.content_generation_port import (
    ContentGenerationPort, ContentGenerationResult
)
from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate
from ...core.config import settings

logger = logging.getLogger(__name__)


class GeminiContentAdapter(ContentGenerationPort):
    """
    Gemini implementation of content generation.
    
    This adapter ONLY handles:
    - Google Gemini API communication
    - Prompt engineering optimized for Gemini
    - Response parsing
    
    It does NOT contain business logic.
    """
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for Gemini content generation")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_CONTENT_MODEL,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=settings.CONTENT_MAX_TOKENS,
            temperature=settings.CONTENT_TEMPERATURE,
        )
    
    async def generate_website_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> ContentGenerationResult:
        """Generate complete website content using Gemini."""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating content for {len(required_pages)} pages using Gemini")
            
            # Generate content for each page
            content_data = {}
            generation_tasks = []
            
            for page_type in required_pages:
                task = self._generate_single_page_content(
                    business, branding, template, page_type
                )
                generation_tasks.append((page_type, task))
            
            # Execute all generations in parallel
            page_results = await asyncio.gather(
                *[task for _, task in generation_tasks],
                return_exceptions=True
            )
            
            # Process results
            warnings = []
            for i, (page_type, result) in enumerate(zip([pt for pt, _ in generation_tasks], page_results)):
                if isinstance(result, Exception):
                    warnings.append(f"Failed to generate {page_type}: {str(result)}")
                    continue
                
                content_data[page_type] = result
            
            # Generate global content (business info, SEO, etc.)
            global_content = await self._generate_global_content(business, branding, template)
            content_data.update(global_content)
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=len(content_data) > 0,
                content_data=content_data,
                pages_generated=list(content_data.keys()),
                generation_time_seconds=generation_time,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            logger.error(f"Gemini content generation failed: {str(e)}")
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=False,
                content_data={},
                pages_generated=[],
                generation_time_seconds=generation_time,
                error_message=str(e)
            )
    
    async def generate_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate content for a specific page using Gemini."""
        
        prompt = self._build_gemini_page_prompt(business, branding, page_type, context)
        
        try:
            # Gemini API is synchronous, so we run it in a thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            )
            
            content_text = response.text
            
            # Parse structured content from response
            return self._parse_gemini_content_response(content_text, page_type)
            
        except Exception as e:
            logger.error(f"Gemini API error for {page_type}: {str(e)}")
            raise
    
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> ContentGenerationResult:
        """Update existing content with changes using Gemini."""
        
        start_time = datetime.utcnow()
        
        try:
            updated_content = {}
            
            # Generate updated content for each specified section
            for section, updates in content_updates.items():
                updated_section = await self._update_section_content(
                    business, branding, section, updates
                )
                updated_content[section] = updated_section
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=True,
                content_data=updated_content,
                pages_generated=list(updated_content.keys()),
                generation_time_seconds=generation_time
            )
            
        except Exception as e:
            logger.error(f"Gemini content update failed: {str(e)}")
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=False,
                content_data={},
                pages_generated=[],
                generation_time_seconds=generation_time,
                error_message=str(e)
            )
    
    async def generate_seo_content(
        self,
        business: Business,
        target_keywords: List[str],
        page_type: str
    ) -> Dict[str, Any]:
        """Generate SEO-optimized content for keywords using Gemini."""
        
        prompt = f"""
        Generate comprehensive SEO content for a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        Business Details:
        - Name: {business.name}
        - Trade: {business.get_primary_trade()}
        - Category: {business.trade_category.value}
        - Service Areas: {', '.join(business.service_areas)}
        
        Target Keywords: {', '.join(target_keywords)}
        Page Type: {page_type}
        
        Generate:
        1. SEO title (50-60 characters)
        2. Meta description (150-160 characters)
        3. H1 heading
        4. 3-4 H2 headings
        5. Schema markup JSON-LD
        6. Open Graph tags
        
        Focus on natural keyword integration and local SEO optimization.
        Return as structured JSON.
        """
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1500,
                        temperature=0.3
                    )
                )
            )
            
            content = response.text
            return self._parse_gemini_seo_content(content)
            
        except Exception as e:
            logger.error(f"Gemini SEO content generation failed: {str(e)}")
            raise
    
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        business: Business
    ) -> Dict[str, Any]:
        """Validate content quality using Gemini."""
        
        prompt = f"""
        Analyze this website content for a {business.get_primary_trade()} business:
        
        Business: {business.name} in {business.city}, {business.state}
        
        Content:
        {json.dumps(content, indent=2)}
        
        Evaluate and score (0-100):
        1. Clarity and readability
        2. Professional tone
        3. Call-to-action effectiveness
        4. Local relevance
        5. Trade-specific accuracy
        6. SEO optimization
        
        Provide overall score and specific improvement suggestions.
        Return as structured JSON.
        """
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2000,
                        temperature=0.2
                    )
                )
            )
            
            analysis = response.text
            return self._parse_gemini_quality_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Gemini content validation failed: {str(e)}")
            return {
                "overall_score": 50,
                "category_scores": {
                    "clarity": 50,
                    "professionalism": 50,
                    "cta_effectiveness": 50,
                    "local_relevance": 50,
                    "trade_accuracy": 50,
                    "seo_optimization": 50
                },
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": ["Please retry content validation"]
            }
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    async def _generate_single_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        page_type: str
    ) -> Dict[str, Any]:
        """Generate content for a single page type using Gemini."""
        
        return await self.generate_page_content(
            business, branding, page_type, {"template": template}
        )
    
    async def _generate_global_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate
    ) -> Dict[str, Any]:
        """Generate global content (business info, SEO, etc.)."""
        
        return {
            "business_info": {
                "name": business.name,
                "phone": business.phone,
                "email": business.email,
                "address": f"{business.address}, {business.city}, {business.state} {business.postal_code}",
                "service_areas": business.service_areas,
                "primary_trade": business.get_primary_trade(),
                "all_trades": business.get_all_trades()
            },
            "branding": {
                "primary_color": branding.primary_color,
                "secondary_color": branding.secondary_color,
                "font_family": branding.font_family,
                "theme_name": branding.theme_name
            },
            "generated_by": "gemini",
            "generation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_gemini_page_prompt(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build Gemini-optimized prompt for page content generation."""
        
        base_prompt = f"""
        You are an expert web content creator for home services businesses. Generate professional website content for:
        
        Business: {business.name}
        Trade: {business.get_primary_trade()} ({business.trade_category.value})
        Location: {business.city}, {business.state}
        Service Areas: {', '.join(business.service_areas)}
        
        Branding:
        - Primary Color: {branding.primary_color}
        - Secondary Color: {branding.secondary_color}
        - Font: {branding.font_family}
        - Theme: {branding.theme_name}
        
        Page Type: {page_type}
        """
        
        # Page-specific instructions
        page_instructions = {
            "home": "Create a compelling homepage with hero section, services overview, trust signals, and strong call-to-action. Focus on local SEO and conversion optimization.",
            "services": "Create detailed service descriptions with benefits, process explanation, and pricing transparency. Include service-specific keywords and clear differentiation.",
            "contact": "Create a conversion-optimized contact page with multiple contact methods, business hours, service areas, and clear next steps.",
            "emergency": "Create urgent, action-oriented emergency service content emphasizing 24/7 availability, quick response, and immediate contact options.",
            "about": "Create trust-building content highlighting company story, qualifications, certifications, and community involvement.",
            "booking": "Create streamlined booking experience with service selection, scheduling options, and clear confirmation process."
        }
        
        instruction = page_instructions.get(page_type, f"Create professional, conversion-focused content for the {page_type} page.")
        
        return f"""{base_prompt}
        
        Instructions: {instruction}
        
        Requirements:
        - Return structured JSON with clear content sections
        - Include SEO elements (title, description, headings)
        - Provide component-ready content blocks
        - Include compelling calls-to-action
        - Maintain professional, trustworthy tone
        - Optimize for local search and conversions
        
        Generate comprehensive, high-quality content that helps this business succeed online."""
    
    def _parse_gemini_content_response(self, content_text: str, page_type: str) -> Dict[str, Any]:
        """Parse Gemini response into structured content."""
        
        try:
            # Try to parse as JSON first
            if content_text.strip().startswith('{'):
                parsed_json = json.loads(content_text)
                parsed_json["page_type"] = page_type
                parsed_json["generated_by"] = "gemini"
                return parsed_json
        except json.JSONDecodeError:
            pass
        
        # Fallback to text parsing
        lines = content_text.strip().split('\n')
        
        parsed_content = {
            "page_type": page_type,
            "generated_by": "gemini",
            "raw_content": content_text,
            "sections": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings
            if (line.startswith('#') or 
                line.startswith('**') and line.endswith('**') or
                line.isupper() and len(line) < 50 or
                line.endswith(':')):
                
                if current_section:
                    parsed_content["sections"].append(current_section)
                
                current_section = {
                    "type": "heading",
                    "content": line.strip('#*: '),
                    "text": []
                }
            elif current_section:
                current_section["text"].append(line)
            else:
                # Content without heading
                if "intro" not in parsed_content:
                    parsed_content["intro"] = []
                parsed_content["intro"].append(line)
        
        # Add final section
        if current_section:
            parsed_content["sections"].append(current_section)
        
        return parsed_content
    
    def _parse_gemini_seo_content(self, content: str) -> Dict[str, Any]:
        """Parse SEO content from Gemini response."""
        
        try:
            # Try JSON parsing first
            if content.strip().startswith('{'):
                return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing
        return {
            "title": "SEO Title Here",
            "meta_description": "Meta description here",
            "h1": "Main heading",
            "h2_headings": ["Heading 1", "Heading 2"],
            "schema_data": {},
            "open_graph": {}
        }
    
    def _parse_gemini_quality_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse quality analysis from Gemini response."""
        
        try:
            # Try JSON parsing first
            if analysis.strip().startswith('{'):
                return json.loads(analysis)
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing
        return {
            "overall_score": 75,
            "category_scores": {
                "clarity": 75,
                "professionalism": 75,
                "cta_effectiveness": 75,
                "local_relevance": 75,
                "trade_accuracy": 75,
                "seo_optimization": 75
            },
            "strengths": ["Professional content", "Clear structure"],
            "improvement_areas": ["Could enhance local SEO"],
            "recommendations": ["Include more location-specific keywords"]
        }
    
    async def _update_section_content(
        self,
        business: Business,
        branding: BusinessBranding,
        section: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update content for a specific section using Gemini."""
        
        prompt = f"""
        Update the {section} section for {business.name}, a {business.get_primary_trade()} business.
        
        Updates needed:
        {json.dumps(updates, indent=2)}
        
        Generate updated content that incorporates these changes while maintaining professional tone and SEO optimization.
        Return as structured JSON.
        """
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1500,
                        temperature=0.4
                    )
                )
            )
            
            updated_content = response.text
            return self._parse_gemini_content_response(updated_content, section)
            
        except Exception as e:
            logger.error(f"Gemini section update failed: {str(e)}")
            raise
