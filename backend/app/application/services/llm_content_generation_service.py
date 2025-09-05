"""
LLM Content Generation Service

Provides AI-powered content generation for trade-aware websites:
- Dynamic hero content based on business context
- Personalized service descriptions
- Weather-aware seasonal messaging
- Local market adaptation
- Trade-specific terminology optimization
- Customer journey personalization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import openai
from redis.asyncio import Redis as AsyncRedis
import httpx

logger = logging.getLogger(__name__)


class ContentType(Enum):
    HERO_CONTENT = "hero_content"
    SERVICE_DESCRIPTION = "service_description"
    TESTIMONIAL_HIGHLIGHT = "testimonial_highlight"
    SEASONAL_MESSAGE = "seasonal_message"
    EMERGENCY_ALERT = "emergency_alert"
    TRUST_INDICATOR = "trust_indicator"
    CTA_OPTIMIZATION = "cta_optimization"


@dataclass
class ContentGenerationRequest:
    content_type: ContentType
    business_context: Dict[str, Any]
    trade_config: Dict[str, Any]
    target_audience: str
    seasonal_context: Optional[Dict[str, Any]] = None
    weather_context: Optional[Dict[str, Any]] = None
    local_market_data: Optional[Dict[str, Any]] = None
    personalization_data: Optional[Dict[str, Any]] = None


@dataclass
class GeneratedContent:
    content_type: ContentType
    primary_text: str
    secondary_text: Optional[str] = None
    cta_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    generation_timestamp: datetime = None


class LLMContentGenerationService:
    def __init__(
        self,
        openai_api_key: str,
        redis_client: Optional[AsyncRedis] = None,
        weather_api_key: Optional[str] = None
    ):
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.redis_client = redis_client or AsyncRedis(host='localhost', port=6379, db=0)
        self.weather_api_key = weather_api_key
        
        # Content generation templates
        self.content_templates = self._load_content_templates()
        
        # Cache settings
        self.cache_ttl = {
            ContentType.HERO_CONTENT: 3600,  # 1 hour
            ContentType.SERVICE_DESCRIPTION: 7200,  # 2 hours
            ContentType.SEASONAL_MESSAGE: 86400,  # 24 hours
            ContentType.EMERGENCY_ALERT: 300,  # 5 minutes
            ContentType.TRUST_INDICATOR: 3600,  # 1 hour
        }

    async def generate_content(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate AI-powered content based on business context and requirements."""
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_content = await self._get_cached_content(cache_key)
        
        if cached_content:
            logger.info(f"Returning cached content for {request.content_type}")
            return cached_content
        
        # Enrich request with additional context
        enriched_request = await self._enrich_request_context(request)
        
        # Generate content using appropriate strategy
        generated_content = await self._generate_content_by_type(enriched_request)
        
        # Cache the result
        await self._cache_content(cache_key, generated_content, request.content_type)
        
        logger.info(f"Generated new content for {request.content_type}")
        return generated_content

    async def enhance_artifact_content(
        self,
        artifact: Dict[str, Any],
        business_context: Dict[str, Any],
        location_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhance a base artifact with LLM-generated copy.

        This method is used by the content orchestrator for the ENHANCED tier.
        It updates hero headline/subheadline/CTA and may adjust meta fields.
        On any error or if LLM is unavailable, returns a minimally improved artifact.
        """
        try:
            # Build minimal trade config from the artifact
            activity_name = artifact.get('activity_name') or artifact.get('activity_slug', '').replace('-', ' ').title()
            trade_config = { 'display_name': activity_name }

            # Ensure business context shape contains expected keys
            business_ctx = dict(business_context or {})
            if location_context:
                # Provide a simple location object for prompts
                business_ctx.setdefault('city', location_context.get('city'))
                business_ctx.setdefault('state', location_context.get('state'))

            # Generate improved hero copy
            hero_content = await self.generate_hero_content(business_ctx, trade_config)

            # Apply enhancements
            enhanced = dict(artifact)
            enhanced.setdefault('hero', {})
            enhanced['hero'].update({
                'headline': hero_content.primary_text or enhanced['hero'].get('headline') or activity_name,
                'subheadline': hero_content.secondary_text or enhanced['hero'].get('subheadline') or '',
                'cta_text': hero_content.cta_text or enhanced['hero'].get('cta_text') or 'Get Free Estimate',
            })

            # If business phone is present, set CTA URL
            phone = (business_ctx.get('phone') or '').strip()
            if phone:
                enhanced['hero']['cta_url'] = f"tel:{phone}"

            # Optionally adjust meta title/description
            city = business_ctx.get('city') or (location_context or {}).get('city')
            state = business_ctx.get('state') or (location_context or {}).get('state')
            if city and state:
                enhanced['meta_title'] = enhanced.get('meta_title') or f"{activity_name} in {city}, {state} | Professional Service"
                if not enhanced.get('meta_description'):
                    enhanced['meta_description'] = f"Professional {activity_name.lower()} in {city}, {state}. Call today for prompt, reliable service."

            return enhanced
        except Exception as e:
            logger.warning(f"enhance_artifact_content failed; returning base artifact. Error: {e}")
            return artifact

    async def generate_hero_content(
        self,
        business_context: Dict[str, Any],
        trade_config: Dict[str, Any],
        weather_context: Optional[Dict[str, Any]] = None
    ) -> GeneratedContent:
        """Generate dynamic hero section content."""
        
        request = ContentGenerationRequest(
            content_type=ContentType.HERO_CONTENT,
            business_context=business_context,
            trade_config=trade_config,
            target_audience="homeowners",
            weather_context=weather_context
        )
        
        return await self.generate_content(request)

    async def generate_seasonal_messaging(
        self,
        business_context: Dict[str, Any],
        trade_config: Dict[str, Any],
        season: str,
        weather_data: Optional[Dict[str, Any]] = None
    ) -> List[GeneratedContent]:
        """Generate seasonal messaging for different content types."""
        
        seasonal_content = []
        
        # Generate different types of seasonal content
        content_types = [
            ContentType.HERO_CONTENT,
            ContentType.SERVICE_DESCRIPTION,
            ContentType.SEASONAL_MESSAGE
        ]
        
        for content_type in content_types:
            request = ContentGenerationRequest(
                content_type=content_type,
                business_context=business_context,
                trade_config=trade_config,
                target_audience="homeowners",
                seasonal_context={"season": season, "weather": weather_data}
            )
            
            content = await self.generate_content(request)
            seasonal_content.append(content)
        
        return seasonal_content

    async def _enrich_request_context(
        self, 
        request: ContentGenerationRequest
    ) -> ContentGenerationRequest:
        """Enrich the request with additional contextual data."""
        
        # Get weather data if location is available
        if not request.weather_context and request.business_context.get('location'):
            weather_data = await self._get_weather_data(
                request.business_context['location']
            )
            request.weather_context = weather_data
        
        # Get local market data
        if not request.local_market_data:
            market_data = await self._get_local_market_data(
                request.business_context.get('location', {})
            )
            request.local_market_data = market_data
        
        # Add seasonal context
        if not request.seasonal_context:
            request.seasonal_context = self._get_seasonal_context()
        
        return request

    async def _generate_content_by_type(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate content based on the specific content type."""
        
        if request.content_type == ContentType.HERO_CONTENT:
            return await self._generate_hero_content(request)
        elif request.content_type == ContentType.SERVICE_DESCRIPTION:
            return await self._generate_service_description(request)
        elif request.content_type == ContentType.SEASONAL_MESSAGE:
            return await self._generate_seasonal_message(request)
        elif request.content_type == ContentType.EMERGENCY_ALERT:
            return await self._generate_emergency_alert(request)
        elif request.content_type == ContentType.TRUST_INDICATOR:
            return await self._generate_trust_indicator(request)
        else:
            raise ValueError(f"Unsupported content type: {request.content_type}")

    async def _generate_hero_content(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate hero section content using LLM."""
        
        # Build context-aware prompt
        prompt = self._build_hero_prompt(request)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert copywriter specializing in home services marketing. Create compelling, trustworthy, and locally-relevant hero content that converts visitors into customers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content_data = self._parse_hero_response(response.choices[0].message.content)
            
            return GeneratedContent(
                content_type=ContentType.HERO_CONTENT,
                primary_text=content_data.get('headline', ''),
                secondary_text=content_data.get('subheadline', ''),
                cta_text=content_data.get('cta', ''),
                metadata=content_data.get('metadata', {}),
                confidence_score=0.85,
                generation_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating hero content: {e}")
            return self._get_fallback_hero_content(request)

    async def _generate_service_description(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate service description content."""
        
        prompt = self._build_service_description_prompt(request)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical writer specializing in home services. Create clear, informative, and persuasive service descriptions that educate customers and build trust."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            
            return GeneratedContent(
                content_type=ContentType.SERVICE_DESCRIPTION,
                primary_text=content,
                confidence_score=0.80,
                generation_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating service description: {e}")
            return self._get_fallback_service_description(request)

    async def _generate_seasonal_message(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """Generate seasonal messaging content."""
        
        prompt = self._build_seasonal_prompt(request)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marketing specialist creating seasonal messaging for home services. Focus on timely, relevant, and actionable content that addresses seasonal needs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            return GeneratedContent(
                content_type=ContentType.SEASONAL_MESSAGE,
                primary_text=content,
                confidence_score=0.75,
                generation_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating seasonal message: {e}")
            return self._get_fallback_seasonal_message(request)

    def _build_hero_prompt(self, request: ContentGenerationRequest) -> str:
        """Build a comprehensive prompt for hero content generation."""
        
        business = request.business_context
        trade = request.trade_config
        weather = request.weather_context or {}
        seasonal = request.seasonal_context or {}
        
        prompt = f"""
Create compelling hero section content for a {trade.get('display_name', 'home services')} business.

BUSINESS CONTEXT:
- Company: {business.get('name', 'Professional Services')}
- Location: {business.get('city', 'Local Area')}, {business.get('state', '')}
- Experience: {business.get('years_in_business', 10)} years in business
- Team Size: {business.get('team_size', 5)} professionals
- Specialties: {', '.join(business.get('specialties', []))}
- Service Areas: {', '.join(business.get('service_areas', []))}

TRADE SPECIFICS:
- Trade: {trade.get('display_name', 'Home Services')}
- Emergency Services: {trade.get('emergency_services', False)}
- Service Model: {trade.get('service_model', {})}
- Key Benefits: {', '.join(trade.get('key_benefits', []))}

CONTEXTUAL FACTORS:
- Current Season: {seasonal.get('season', 'year-round')}
- Weather: {weather.get('condition', 'normal')} conditions
- Temperature: {weather.get('temperature', 'comfortable')}
- Local Market: {request.local_market_data or 'competitive'}

REQUIREMENTS:
1. Create a powerful headline (8-12 words) that includes location and trade
2. Write a compelling subheadline (15-25 words) highlighting key benefits
3. Suggest a strong call-to-action button text
4. Include trust indicators relevant to the trade
5. Consider seasonal/weather factors if relevant
6. Use local terminology and references
7. Emphasize emergency availability if applicable

Format the response as JSON:
{{
    "headline": "Main headline text",
    "subheadline": "Supporting subheadline text",
    "cta": "Call-to-action button text",
    "trust_indicators": ["indicator1", "indicator2", "indicator3"],
    "emergency_message": "Emergency service message (if applicable)",
    "metadata": {{
        "tone": "professional/friendly/urgent",
        "focus": "primary benefit emphasized",
        "local_elements": ["local references used"]
    }}
}}
"""
        
        return prompt

    def _build_service_description_prompt(self, request: ContentGenerationRequest) -> str:
        """Build prompt for service description generation."""
        
        business = request.business_context
        trade = request.trade_config
        
        prompt = f"""
Write a comprehensive service description for {trade.get('display_name', 'home services')}.

BUSINESS CONTEXT:
- Company: {business.get('name')}
- Experience: {business.get('years_in_business', 10)} years
- Certifications: {', '.join(business.get('certifications', []))}
- Service Philosophy: {business.get('service_philosophy', 'Quality and reliability')}

TRADE REQUIREMENTS:
- Service Type: {trade.get('display_name')}
- Key Services: {', '.join(trade.get('service_categories', []))}
- Typical Projects: {', '.join(trade.get('typical_projects', []))}
- Quality Standards: {trade.get('quality_standards', 'Industry best practices')}

Create a 150-200 word service description that:
1. Explains what the service includes
2. Highlights unique qualifications and approach
3. Mentions key benefits for customers
4. Includes relevant technical expertise
5. Builds trust and credibility
6. Uses industry-appropriate terminology
7. Ends with a soft call-to-action

Write in a professional but approachable tone.
"""
        
        return prompt

    def _build_seasonal_prompt(self, request: ContentGenerationRequest) -> str:
        """Build prompt for seasonal messaging."""
        
        seasonal = request.seasonal_context or {}
        weather = request.weather_context or {}
        trade = request.trade_config
        
        prompt = f"""
Create seasonal messaging for {trade.get('display_name', 'home services')} during {seasonal.get('season', 'current season')}.

SEASONAL CONTEXT:
- Season: {seasonal.get('season')}
- Weather Conditions: {weather.get('condition', 'typical')}
- Temperature: {weather.get('temperature', 'seasonal average')}
- Seasonal Challenges: {seasonal.get('challenges', [])}

TRADE-SPECIFIC CONSIDERATIONS:
- Service Type: {trade.get('display_name')}
- Seasonal Demand: {trade.get('seasonal_patterns', {}).get(seasonal.get('season', 'spring'), 'steady')}
- Weather Impact: {trade.get('weather_considerations', [])}

Create a 50-75 word seasonal message that:
1. Acknowledges the current season/weather
2. Highlights relevant service needs
3. Creates urgency if appropriate
4. Offers seasonal benefits or promotions
5. Includes a clear next step

Focus on being helpful and timely rather than pushy.
"""
        
        return prompt

    def _parse_hero_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response for hero content."""
        
        try:
            # Try to parse as JSON first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to text parsing
            lines = response_text.strip().split('\n')
            
            return {
                'headline': lines[0] if lines else 'Professional Home Services',
                'subheadline': lines[1] if len(lines) > 1 else 'Quality work you can trust',
                'cta': 'Get Free Estimate',
                'trust_indicators': ['Licensed', 'Insured', 'Local'],
                'metadata': {'tone': 'professional', 'focus': 'quality'}
            }

    async def _get_weather_data(self, location: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch current weather data for the location."""
        
        if not self.weather_api_key or not location.get('city'):
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://api.openweathermap.org/data/2.5/weather",
                    params={
                        'q': f"{location.get('city')},{location.get('state')}",
                        'appid': self.weather_api_key,
                        'units': 'imperial'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'condition': data['weather'][0]['main'].lower(),
                        'description': data['weather'][0]['description'],
                        'temperature': round(data['main']['temp']),
                        'feels_like': round(data['main']['feels_like']),
                        'humidity': data['main']['humidity']
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch weather data: {e}")
        
        return None

    async def _get_local_market_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get local market context data."""
        
        # This would integrate with market data APIs in production
        # For now, return mock data based on location
        
        return {
            'market_type': 'suburban',
            'competition_level': 'moderate',
            'average_income': 'middle',
            'housing_age': 'mixed',
            'growth_rate': 'steady'
        }

    def _get_seasonal_context(self) -> Dict[str, Any]:
        """Get current seasonal context."""
        
        now = datetime.now()
        month = now.month
        
        if month in [12, 1, 2]:
            season = 'winter'
            challenges = ['heating issues', 'frozen pipes', 'ice damage']
        elif month in [3, 4, 5]:
            season = 'spring'
            challenges = ['maintenance prep', 'system tune-ups', 'storm damage']
        elif month in [6, 7, 8]:
            season = 'summer'
            challenges = ['cooling needs', 'high usage', 'vacation prep']
        else:
            season = 'fall'
            challenges = ['winterization', 'maintenance', 'preparation']
        
        return {
            'season': season,
            'month': now.strftime('%B'),
            'challenges': challenges
        }

    def _get_fallback_hero_content(self, request: ContentGenerationRequest) -> GeneratedContent:
        """Provide fallback hero content if LLM generation fails."""
        
        business = request.business_context
        trade = request.trade_config
        
        return GeneratedContent(
            content_type=ContentType.HERO_CONTENT,
            primary_text=f"Professional {trade.get('display_name', 'Home Services')} in {business.get('city', 'Your Area')}",
            secondary_text=f"Trusted by homeowners for {business.get('years_in_business', 10)}+ years. Licensed, insured, and ready to help.",
            cta_text="Get Free Estimate",
            confidence_score=0.60,
            generation_timestamp=datetime.now()
        )

    def _get_fallback_service_description(self, request: ContentGenerationRequest) -> GeneratedContent:
        """Provide fallback service description."""
        
        trade = request.trade_config
        
        return GeneratedContent(
            content_type=ContentType.SERVICE_DESCRIPTION,
            primary_text=f"Our experienced team provides comprehensive {trade.get('display_name', 'home services')} with a focus on quality, reliability, and customer satisfaction. We use industry-best practices and premium materials to ensure lasting results.",
            confidence_score=0.50,
            generation_timestamp=datetime.now()
        )

    def _get_fallback_seasonal_message(self, request: ContentGenerationRequest) -> GeneratedContent:
        """Provide fallback seasonal message."""
        
        seasonal = request.seasonal_context or {}
        
        return GeneratedContent(
            content_type=ContentType.SEASONAL_MESSAGE,
            primary_text=f"This {seasonal.get('season', 'season')}, ensure your home is ready with professional maintenance and repairs. Contact us for seasonal service recommendations.",
            confidence_score=0.40,
            generation_timestamp=datetime.now()
        )

    def _get_cache_key(self, request: ContentGenerationRequest) -> str:
        """Generate cache key for the request."""
        
        key_parts = [
            request.content_type.value,
            request.business_context.get('id', 'default'),
            request.trade_config.get('slug', 'general'),
            request.target_audience
        ]
        
        # Add seasonal context to key for time-sensitive content
        if request.seasonal_context:
            key_parts.append(request.seasonal_context.get('season', 'none'))
        
        return f"llm_content:{':'.join(key_parts)}"

    async def _get_cached_content(self, cache_key: str) -> Optional[GeneratedContent]:
        """Retrieve cached content if available."""
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return GeneratedContent(**data)
        except Exception as e:
            logger.warning(f"Failed to retrieve cached content: {e}")
        
        return None

    async def _cache_content(
        self, 
        cache_key: str, 
        content: GeneratedContent, 
        content_type: ContentType
    ) -> None:
        """Cache generated content."""
        
        try:
            ttl = self.cache_ttl.get(content_type, 3600)
            content_data = {
                'content_type': content.content_type.value,
                'primary_text': content.primary_text,
                'secondary_text': content.secondary_text,
                'cta_text': content.cta_text,
                'metadata': content.metadata,
                'confidence_score': content.confidence_score,
                'generation_timestamp': content.generation_timestamp.isoformat() if content.generation_timestamp else None
            }
            
            await self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(content_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache content: {e}")

    def _load_content_templates(self) -> Dict[str, Any]:
        """Load content generation templates."""
        
        return {
            'hero_templates': {
                'hvac': {
                    'headlines': [
                        'Expert HVAC Services in {city}',
                        'Reliable Heating & Cooling Solutions',
                        '24/7 Emergency HVAC Repair'
                    ],
                    'benefits': [
                        'Licensed & Insured Technicians',
                        'Same-Day Service Available',
                        'Energy Efficiency Experts'
                    ]
                },
                'plumbing': {
                    'headlines': [
                        'Professional Plumbing Services',
                        'Emergency Plumber Available 24/7',
                        'Trusted Local Plumbing Experts'
                    ],
                    'benefits': [
                        'No Hidden Fees',
                        'Upfront Pricing',
                        'Satisfaction Guaranteed'
                    ]
                }
            }
        }


# Usage example and factory function
async def create_llm_content_service(
    openai_api_key: str,
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    weather_api_key: Optional[str] = None
) -> LLMContentGenerationService:
    """Factory function to create LLM content generation service."""
    
    redis_client = AsyncRedis(host=redis_host, port=redis_port, db=0)
    
    return LLMContentGenerationService(
        openai_api_key=openai_api_key,
        redis_client=redis_client,
        weather_api_key=weather_api_key
    )
