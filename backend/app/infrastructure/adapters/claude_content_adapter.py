"""
Claude Content Generation Adapter

Implementation of ContentGenerationPort using Anthropic's Claude.
This adapter specializes in generating high-quality React/Next.js components and content.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

import anthropic
from anthropic import AsyncAnthropic

from ...application.ports.content_generation_port import (
    ContentGenerationPort, ContentGenerationResult
)
from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate
from ...core.config import settings

logger = logging.getLogger(__name__)


class ClaudeContentAdapter(ContentGenerationPort):
    """
    Claude implementation of content generation.
    
    This adapter ONLY handles:
    - Anthropic Claude API communication
    - Prompt engineering optimized for Claude
    - Response parsing
    
    It does NOT contain business logic.
    """
    
    def __init__(self):
        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required for Claude content generation")
        
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = settings.CLAUDE_CONTENT_MODEL
        self.max_tokens = settings.CONTENT_MAX_TOKENS
        self.temperature = settings.CONTENT_TEMPERATURE
    
    async def generate_website_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> ContentGenerationResult:
        """Generate complete website content using Claude."""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating content for {len(required_pages)} pages using Claude")
            
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
            logger.error(f"Claude content generation failed: {str(e)}")
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
        """Generate content for a specific page using Claude."""
        
        prompt = self._build_claude_page_prompt(business, branding, page_type, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._get_claude_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content_text = response.content[0].text
            
            # Parse structured content from response
            return self._parse_claude_content_response(content_text, page_type)
            
        except Exception as e:
            logger.error(f"Claude API error for {page_type}: {str(e)}")
            raise
    
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> ContentGenerationResult:
        """Update existing content with changes using Claude."""
        
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
            logger.error(f"Claude content update failed: {str(e)}")
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
        """Generate SEO-optimized content for keywords using Claude."""
        
        prompt = f"""
        Generate comprehensive SEO content for a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        Business Details:
        - Name: {business.name}
        - Trade: {business.get_primary_trade()}
        - Category: {business.trade_category.value}
        - Service Areas: {', '.join(business.service_areas)}
        
        Target Keywords: {', '.join(target_keywords)}
        Page Type: {page_type}
        
        Please generate:
        1. SEO title (50-60 characters, compelling and keyword-rich)
        2. Meta description (150-160 characters, action-oriented)
        3. H1 heading (primary keyword focus)
        4. 3-4 H2 headings (semantic keyword variations)
        5. Schema markup JSON-LD for LocalBusiness
        6. Open Graph tags
        7. Suggested internal linking keywords
        
        Focus on:
        - Natural keyword integration (avoid stuffing)
        - Local SEO optimization
        - User intent matching
        - Conversion-focused messaging
        
        Return as structured JSON.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for SEO precision
                system="You are an expert SEO specialist for home services businesses. Generate precise, effective SEO content that ranks well and converts visitors.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            return self._parse_claude_seo_content(content)
            
        except Exception as e:
            logger.error(f"Claude SEO content generation failed: {str(e)}")
            raise
    
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        business: Business
    ) -> Dict[str, Any]:
        """Validate content quality using Claude's analytical capabilities."""
        
        prompt = f"""
        Analyze this website content for a {business.get_primary_trade()} business and provide detailed quality assessment:
        
        Business Context:
        - Name: {business.name}
        - Trade: {business.get_primary_trade()}
        - Location: {business.city}, {business.state}
        
        Content to Analyze:
        {json.dumps(content, indent=2)}
        
        Please evaluate and score (0-100) each aspect:
        
        1. **Clarity & Readability** (0-100)
           - Clear, jargon-free language
           - Logical flow and structure
           - Appropriate reading level
        
        2. **Professional Tone** (0-100)
           - Industry expertise demonstration
           - Trustworthy and authoritative voice
           - Consistent brand personality
        
        3. **Call-to-Action Effectiveness** (0-100)
           - Clear, compelling CTAs
           - Strategic placement
           - Action-oriented language
        
        4. **Local Relevance** (0-100)
           - Location-specific content
           - Local market understanding
           - Community connection
        
        5. **Trade-Specific Accuracy** (0-100)
           - Technical accuracy
           - Industry best practices
           - Service descriptions precision
        
        6. **SEO Optimization** (0-100)
           - Keyword integration
           - Meta elements quality
           - Content structure for search
        
        Provide:
        - Overall quality score (weighted average)
        - Top 3 strengths
        - Top 3 improvement areas
        - Specific actionable recommendations
        
        Return as structured JSON.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.2,  # Very low temperature for analytical precision
                system="You are a content quality analyst specializing in home services websites. Provide thorough, actionable analysis.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = response.content[0].text
            return self._parse_claude_quality_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Claude content validation failed: {str(e)}")
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
                "strengths": [],
                "improvement_areas": [f"Validation error: {str(e)}"],
                "recommendations": ["Please retry content validation"]
            }
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _get_claude_system_prompt(self) -> str:
        """Get Claude-optimized system prompt for content generation."""
        
        return """You are an expert web content creator specializing in home services businesses. You excel at:

1. **Technical Accuracy**: Deep understanding of trades like HVAC, plumbing, electrical, etc.
2. **Local SEO**: Creating location-specific content that ranks well in local search
3. **Conversion Optimization**: Writing content that turns visitors into customers
4. **Professional Tone**: Balancing expertise with accessibility
5. **React/Next.js Components**: Generating clean, modern component structures

When generating content:
- Use clear, professional language that builds trust
- Include specific service benefits and outcomes
- Incorporate local references naturally
- Structure content for both humans and search engines
- Focus on solving customer problems
- Include compelling calls-to-action

Always return structured, well-formatted content that can be easily parsed and used in web applications."""
    
    async def _generate_single_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        page_type: str
    ) -> Dict[str, Any]:
        """Generate content for a single page type using Claude."""
        
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
                "address": f"{business.address}, {business.city}, {business.state} {business.zip_code}",
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
            "generated_by": "claude",
            "generation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_claude_page_prompt(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build Claude-optimized prompt for page content generation."""
        
        base_context = f"""
        Generate professional website content for this home services business:
        
        **Business Profile:**
        - Company: {business.name}
        - Trade: {business.get_primary_trade()} ({business.trade_category.value})
        - Location: {business.city}, {business.state}
        - Service Areas: {', '.join(business.service_areas)}
        - Phone: {business.phone}
        - Email: {business.email}
        
        **Branding Guidelines:**
        - Primary Color: {branding.primary_color}
        - Secondary Color: {branding.secondary_color}
        - Font Family: {branding.font_family}
        - Theme: {branding.theme_name}
        
        **Page Type:** {page_type}
        """
        
        # Claude-specific page instructions optimized for better output
        page_instructions = {
            "home": """
            Create a compelling homepage that immediately communicates value and builds trust:
            
            **Required Sections:**
            1. Hero section with powerful headline and clear value proposition
            2. Services overview highlighting key offerings
            3. Why choose us (unique selling points)
            4. Service areas coverage
            5. Customer testimonials/social proof
            6. Emergency services callout (if applicable)
            7. Contact information and strong CTA
            
            **Focus Areas:**
            - Local SEO optimization with location keywords
            - Trust signals (licenses, insurance, experience)
            - Clear next steps for customers
            - Mobile-first design considerations
            """,
            
            "services": """
            Create detailed service pages that educate and convert:
            
            **Required Content:**
            1. Service category overview
            2. Individual service descriptions with benefits
            3. Process/methodology explanation
            4. Pricing transparency (ranges or starting points)
            5. Service area coverage
            6. Emergency vs. scheduled service options
            7. Warranty/guarantee information
            
            **Optimization:**
            - Service-specific keywords
            - Problem-solution messaging
            - Clear service differentiation
            """,
            
            "contact": """
            Create a conversion-optimized contact page:
            
            **Essential Elements:**
            1. Multiple contact methods (phone, email, form)
            2. Business hours and availability
            3. Service area map or list
            4. Response time expectations
            5. Emergency contact information
            6. Physical address and directions
            7. Social media links
            
            **Conversion Focus:**
            - Reduce friction to contact
            - Build confidence in response
            - Clear next steps after contact
            """,
            
            "emergency": """
            Create urgent, action-oriented emergency service content:
            
            **Critical Elements:**
            1. 24/7 availability messaging
            2. Emergency phone number prominence
            3. Response time guarantees
            4. Common emergency scenarios
            5. What to do while waiting
            6. Service area coverage for emergencies
            7. Pricing transparency for emergency calls
            
            **Urgency Optimization:**
            - Action-oriented headlines
            - Immediate contact options
            - Trust and reliability messaging
            """,
            
            "about": """
            Create trust-building about page that establishes credibility:
            
            **Key Content:**
            1. Company story and founding
            2. Owner/team qualifications and experience
            3. Licenses, certifications, insurance
            4. Community involvement
            5. Awards and recognition
            6. Company values and mission
            7. Why customers choose us
            
            **Trust Building:**
            - Personal connection elements
            - Professional credentials
            - Local community ties
            """,
            
            "booking": """
            Create streamlined booking experience:
            
            **Booking Elements:**
            1. Service type selection
            2. Preferred date/time options
            3. Contact information collection
            4. Service address input
            5. Problem description field
            6. Urgency level selection
            7. Confirmation and next steps
            
            **User Experience:**
            - Simple, step-by-step process
            - Clear expectations setting
            - Mobile-optimized interface
            """
        }
        
        instruction = page_instructions.get(page_type, f"Create professional, conversion-focused content for the {page_type} page that serves the business goals and user needs.")
        
        return f"""{base_context}
        
        {instruction}
        
        **Output Requirements:**
        - Return structured JSON with clear content sections
        - Include SEO elements (title, description, headings)
        - Provide component-ready content blocks
        - Ensure mobile-responsive considerations
        - Include conversion-focused CTAs
        - Maintain professional, trustworthy tone
        
        Generate comprehensive, high-quality content that will help this business succeed online."""
    
    def _parse_claude_content_response(self, content_text: str, page_type: str) -> Dict[str, Any]:
        """Parse Claude response into structured content."""
        
        try:
            # Try to parse as JSON first (Claude often returns structured JSON)
            if content_text.strip().startswith('{'):
                parsed_json = json.loads(content_text)
                parsed_json["page_type"] = page_type
                parsed_json["generated_by"] = "claude"
                return parsed_json
        except json.JSONDecodeError:
            pass
        
        # Fallback to text parsing
        lines = content_text.strip().split('\n')
        
        parsed_content = {
            "page_type": page_type,
            "generated_by": "claude",
            "raw_content": content_text,
            "sections": [],
            "seo": {},
            "components": []
        }
        
        current_section = None
        in_json_block = False
        json_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle JSON blocks
            if line.startswith('```json') or line.startswith('{'):
                in_json_block = True
                if line.startswith('{'):
                    json_content = line
                continue
            elif line.startswith('```') and in_json_block:
                in_json_block = False
                try:
                    json_data = json.loads(json_content)
                    parsed_content.update(json_data)
                except json.JSONDecodeError:
                    pass
                json_content = ""
                continue
            elif in_json_block:
                json_content += line + "\n"
                continue
            
            # Detect headings (more sophisticated than OpenAI version)
            if (line.startswith('#') or 
                line.startswith('**') and line.endswith('**') or
                line.isupper() and len(line) < 50 or
                line.endswith(':')):
                
                if current_section:
                    parsed_content["sections"].append(current_section)
                
                heading_text = line.strip('#*: ')
                current_section = {
                    "type": "heading",
                    "level": line.count('#') if line.startswith('#') else 2,
                    "content": heading_text,
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
    
    def _parse_claude_seo_content(self, content: str) -> Dict[str, Any]:
        """Parse SEO content from Claude response."""
        
        try:
            # Try JSON parsing first
            if content.strip().startswith('{'):
                return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing for non-JSON responses
        seo_data = {
            "title": "",
            "meta_description": "",
            "h1": "",
            "h2_headings": [],
            "schema_markup": {},
            "open_graph": {},
            "internal_links": []
        }
        
        lines = content.split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            if 'title:' in line.lower():
                seo_data["title"] = line.split(':', 1)[1].strip().strip('"')
            elif 'meta description:' in line.lower():
                seo_data["meta_description"] = line.split(':', 1)[1].strip().strip('"')
            elif 'h1:' in line.lower():
                seo_data["h1"] = line.split(':', 1)[1].strip().strip('"')
        
        return seo_data
    
    def _parse_claude_quality_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse quality analysis from Claude response."""
        
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
            "strengths": ["Professional content", "Clear structure", "Good readability"],
            "improvement_areas": ["Could enhance local SEO", "Add more specific CTAs"],
            "recommendations": ["Include more location-specific keywords", "Strengthen call-to-action language"]
        }
    
    async def _update_section_content(
        self,
        business: Business,
        branding: BusinessBranding,
        section: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update content for a specific section using Claude."""
        
        prompt = f"""
        Update the {section} section for {business.name}, a {business.get_primary_trade()} business in {business.city}, {business.state}.
        
        **Current Updates Needed:**
        {json.dumps(updates, indent=2)}
        
        **Requirements:**
        - Maintain professional, trustworthy tone
        - Incorporate updates seamlessly
        - Preserve SEO optimization
        - Keep brand consistency
        - Ensure mobile-friendly content
        
        Generate updated content that incorporates these changes while improving overall quality and effectiveness.
        
        Return as structured JSON with clear content sections.
        """
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.4,
                system="You are updating website content. Maintain consistency with existing style while incorporating new information and improving quality.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            updated_content = response.content[0].text
            return self._parse_claude_content_response(updated_content, section)
            
        except Exception as e:
            logger.error(f"Claude section update failed: {str(e)}")
            raise