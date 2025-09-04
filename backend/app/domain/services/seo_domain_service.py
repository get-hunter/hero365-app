"""
SEO Domain Service

Contains all SEO-related business logic and rules.
This service is pure domain logic with no external dependencies.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

from ..entities.business import Business, TradeCategory
from ..entities.website import BusinessWebsite, SEOKeywordTracking

logger = logging.getLogger(__name__)


@dataclass
class KeywordAnalysis:
    """Domain model for keyword analysis results."""
    
    keyword: str
    difficulty_score: int  # 1-100
    local_relevance: int  # 1-100
    trade_relevance: int  # 1-100
    commercial_intent: str  # LOW, MEDIUM, HIGH
    search_intent: str  # INFORMATIONAL, NAVIGATIONAL, TRANSACTIONAL, COMMERCIAL
    recommended_priority: str  # HIGH, MEDIUM, LOW


@dataclass
class SEOOptimizationRecommendation:
    """Domain model for SEO optimization recommendations."""
    
    type: str  # CONTENT, TECHNICAL, LOCAL, LINKS
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    implementation_effort: str  # LOW, MEDIUM, HIGH
    expected_impact: str  # LOW, MEDIUM, HIGH
    trade_specific: bool = False


@dataclass
class LocalSEOFactors:
    """Domain model for local SEO factors."""
    
    business_name_in_domain: bool
    location_in_content: bool
    trade_keywords_present: bool
    local_schema_markup: bool
    google_business_profile_linked: bool
    local_citations_count: int
    review_count: int
    average_rating: float


class SEODomainService:
    """
    Domain service for SEO business logic.
    
    Contains all SEO-related business rules and calculations
    without any external dependencies or infrastructure concerns.
    """
    
    def calculate_keyword_difficulty(
        self,
        keyword: str,
        competition_data: Dict[str, Any],
        business: Business
    ) -> int:
        """
        Calculate keyword difficulty score based on business context.
        
        Args:
            keyword: Target keyword
            competition_data: Competition metrics from external sources
            business: Business context for local/trade adjustments
            
        Returns:
            Difficulty score from 1-100 (higher = more difficult)
        """
        
        base_difficulty = competition_data.get('competition_score', 50)
        
        # Adjust for local business factors
        local_adjustment = self._calculate_local_difficulty_adjustment(keyword, business)
        
        # Adjust for trade-specific factors
        trade_adjustment = self._calculate_trade_difficulty_adjustment(keyword, business)
        
        # Adjust for business size/authority
        authority_adjustment = self._calculate_authority_adjustment(business)
        
        # Calculate final difficulty
        final_difficulty = base_difficulty + local_adjustment + trade_adjustment + authority_adjustment
        
        # Ensure score is within bounds
        return max(1, min(100, int(final_difficulty)))
    
    def generate_local_keywords(self, business: Business) -> List[str]:
        """
        Generate local SEO keywords for a business.
        
        Args:
            business: Business entity
            
        Returns:
            List of local keyword variations
        """
        
        keywords = []
        
        # Get base trade keywords
        trade_keywords = self._get_trade_keywords(business)
        
        # Generate location variations
        locations = [
            business.city,
            f"{business.city} {business.state}",
            business.state,
            *business.service_areas
        ]
        
        # Generate keyword combinations
        for trade_keyword in trade_keywords:
            for location in locations:
                # Basic combinations
                keywords.extend([
                    f"{trade_keyword} {location}",
                    f"{trade_keyword} in {location}",
                    f"{trade_keyword} near {location}",
                    f"{location} {trade_keyword}",
                    f"best {trade_keyword} {location}",
                    f"top {trade_keyword} {location}",
                    f"local {trade_keyword} {location}",
                    f"{trade_keyword} services {location}",
                    f"{trade_keyword} company {location}",
                    f"{trade_keyword} contractor {location}"
                ])
                
                # Emergency/urgent variations for applicable trades
                if self._supports_emergency_services(business):
                    keywords.extend([
                        f"emergency {trade_keyword} {location}",
                        f"24/7 {trade_keyword} {location}",
                        f"urgent {trade_keyword} {location}"
                    ])
        
        # Remove duplicates and clean up
        keywords = list(set(keywords))
        keywords = [kw.strip().lower() for kw in keywords if len(kw.strip()) > 0]
        
        # Sort by relevance (shorter, more direct keywords first)
        keywords.sort(key=lambda x: (len(x.split()), len(x)))
        
        return keywords[:50]  # Limit to top 50 keywords for BusinessWebsite validation
    
    def calculate_seo_score(
        self,
        website: BusinessWebsite,
        business: Business,
        content_analysis: Dict[str, Any]
    ) -> int:
        """
        Calculate overall SEO score for a website.
        
        Args:
            website: Website entity
            business: Business entity
            content_analysis: Content analysis data
            
        Returns:
            SEO score from 1-100
        """
        
        scores = {}
        
        # Technical SEO (25%)
        scores['technical'] = self._calculate_technical_seo_score(content_analysis)
        
        # Content SEO (30%)
        scores['content'] = self._calculate_content_seo_score(content_analysis, business)
        
        # Local SEO (25%)
        scores['local'] = self._calculate_local_seo_score(website, business, content_analysis)
        
        # Trade-specific SEO (20%)
        scores['trade'] = self._calculate_trade_seo_score(content_analysis, business)
        
        # Calculate weighted average
        weights = {
            'technical': 0.25,
            'content': 0.30,
            'local': 0.25,
            'trade': 0.20
        }
        
        total_score = sum(scores[category] * weights[category] for category in scores)
        
        return int(total_score)
    
    def optimize_content_for_keywords(
        self,
        content: str,
        target_keywords: List[str],
        business: Business
    ) -> Dict[str, Any]:
        """
        Analyze content and provide keyword optimization recommendations.
        
        Args:
            content: Content to analyze
            target_keywords: Keywords to optimize for
            business: Business context
            
        Returns:
            Optimization recommendations and analysis
        """
        
        analysis = {
            'keyword_density': {},
            'keyword_placement': {},
            'recommendations': [],
            'optimized_content': content
        }
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Calculate keyword density
            keyword_count = content_lower.count(keyword_lower)
            density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            
            analysis['keyword_density'][keyword] = {
                'count': keyword_count,
                'density': density,
                'optimal_range': self._get_optimal_keyword_density(keyword, business)
            }
            
            # Analyze keyword placement
            analysis['keyword_placement'][keyword] = {
                'in_title': keyword_lower in content_lower[:100],
                'in_first_paragraph': keyword_lower in content_lower[:300],
                'in_headings': self._count_keyword_in_headings(content, keyword_lower),
                'in_meta_description': False  # Would need meta description content
            }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_content_recommendations(
            analysis, target_keywords, business
        )
        
        return analysis
    
    def generate_schema_markup(
        self,
        business: Business,
        page_type: str,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate structured data (schema.org) markup for a business page.
        
        Args:
            business: Business entity
            page_type: Type of page (home, services, contact, etc.)
            additional_data: Additional data for specific schema types
            
        Returns:
            Schema.org JSON-LD markup
        """
        
        if page_type == "home":
            return self._generate_local_business_schema(business, additional_data)
        elif page_type == "services":
            return self._generate_service_schema(business, additional_data)
        elif page_type == "contact":
            return self._generate_contact_schema(business)
        elif page_type == "about":
            return self._generate_organization_schema(business)
        else:
            return self._generate_webpage_schema(business, page_type, additional_data)
    
    def analyze_competitor_keywords(
        self,
        competitor_data: List[Dict[str, Any]],
        business: Business
    ) -> Dict[str, Any]:
        """
        Analyze competitor keyword strategies and identify opportunities.
        
        Args:
            competitor_data: Competitor keyword data from external sources
            business: Business context
            
        Returns:
            Competitor analysis and keyword opportunities
        """
        
        analysis = {
            'keyword_gaps': [],
            'competitor_strengths': {},
            'opportunities': [],
            'content_gaps': []
        }
        
        # Identify keywords competitors rank for but business doesn't
        business_keywords = set(self.generate_local_keywords(business))
        
        for competitor in competitor_data:
            competitor_keywords = set(competitor.get('keywords', []))
            
            # Find keyword gaps
            gaps = competitor_keywords - business_keywords
            analysis['keyword_gaps'].extend(list(gaps))
            
            # Analyze competitor strengths
            analysis['competitor_strengths'][competitor['domain']] = {
                'top_keywords': competitor.get('top_keywords', [])[:10],
                'estimated_traffic': competitor.get('traffic', 0),
                'keyword_count': len(competitor_keywords)
            }
        
        # Generate opportunities based on gaps
        analysis['opportunities'] = self._identify_keyword_opportunities(
            analysis['keyword_gaps'], business
        )
        
        return analysis
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _calculate_local_difficulty_adjustment(self, keyword: str, business: Business) -> int:
        """Calculate difficulty adjustment for local factors."""
        
        adjustment = 0
        
        # Local keywords are generally easier for local businesses
        if any(location.lower() in keyword.lower() for location in [business.city, business.state]):
            adjustment -= 15
        
        # Service area keywords
        if any(area.lower() in keyword.lower() for area in business.service_areas):
            adjustment -= 10
        
        return adjustment
    
    def _calculate_trade_difficulty_adjustment(self, keyword: str, business: Business) -> int:
        """Calculate difficulty adjustment for trade-specific factors."""
        
        adjustment = 0
        trade_keywords = self._get_trade_keywords(business)
        
        # Trade-specific keywords may be easier for established businesses
        if any(trade_kw.lower() in keyword.lower() for trade_kw in trade_keywords):
            adjustment -= 5
        
        # Highly competitive trades
        competitive_trades = ['plumbing', 'hvac', 'electrical', 'roofing']
        if business.get_primary_trade().lower() in competitive_trades:
            adjustment += 10
        
        return adjustment
    
    def _calculate_authority_adjustment(self, business: Business) -> int:
        """Calculate difficulty adjustment based on business authority."""
        
        # For new businesses, everything is harder
        # This could be enhanced with actual business age, review count, etc.
        return 5  # Assume new business for now
    
    def _get_trade_keywords(self, business: Business) -> List[str]:
        """Get relevant keywords for a business trade."""
        
        trade_keywords_map = {
            'plumbing': ['plumber', 'plumbing', 'pipe repair', 'drain cleaning', 'water heater'],
            'hvac': ['hvac', 'heating', 'cooling', 'air conditioning', 'furnace repair'],
            'electrical': ['electrician', 'electrical', 'wiring', 'electrical repair'],
            'roofing': ['roofer', 'roofing', 'roof repair', 'roof replacement'],
            'landscaping': ['landscaping', 'lawn care', 'tree service', 'irrigation'],
            'pest control': ['pest control', 'exterminator', 'bug control', 'termite treatment']
        }
        
        primary_trade = business.get_primary_trade().lower()
        return trade_keywords_map.get(primary_trade, [primary_trade])
    
    def _supports_emergency_services(self, business: Business) -> bool:
        """Check if business type typically offers emergency services."""
        
        emergency_trades = ['plumbing', 'hvac', 'electrical', 'roofing', 'security systems']
        return business.get_primary_trade().lower() in emergency_trades
    
    def _calculate_technical_seo_score(self, content_analysis: Dict[str, Any]) -> int:
        """Calculate technical SEO score."""
        
        score = 100
        
        # Page speed (if available)
        if 'page_speed' in content_analysis:
            if content_analysis['page_speed'] < 3:
                score -= 20
            elif content_analysis['page_speed'] < 5:
                score -= 10
        
        # Mobile friendliness
        if not content_analysis.get('mobile_friendly', True):
            score -= 25
        
        # HTTPS
        if not content_analysis.get('https', True):
            score -= 15
        
        # Meta tags
        if not content_analysis.get('has_title_tag', True):
            score -= 20
        if not content_analysis.get('has_meta_description', True):
            score -= 15
        
        return max(0, score)
    
    def _calculate_content_seo_score(
        self,
        content_analysis: Dict[str, Any],
        business: Business
    ) -> int:
        """Calculate content SEO score."""
        
        score = 100
        
        # Content length
        word_count = content_analysis.get('word_count', 0)
        if word_count < 300:
            score -= 30
        elif word_count < 500:
            score -= 15
        
        # Heading structure
        if not content_analysis.get('has_h1', True):
            score -= 20
        if content_analysis.get('h2_count', 0) < 2:
            score -= 10
        
        # Keyword optimization
        keyword_score = content_analysis.get('keyword_optimization_score', 50)
        score = (score + keyword_score) / 2
        
        return max(0, int(score))
    
    def _calculate_local_seo_score(
        self,
        website: BusinessWebsite,
        business: Business,
        content_analysis: Dict[str, Any]
    ) -> int:
        """Calculate local SEO score."""
        
        score = 100
        
        # Business name in content
        if not content_analysis.get('business_name_present', False):
            score -= 20
        
        # Location information
        if not content_analysis.get('location_in_content', False):
            score -= 25
        
        # Local schema markup
        if not content_analysis.get('local_schema_present', False):
            score -= 20
        
        # Contact information
        if not content_analysis.get('phone_number_present', False):
            score -= 15
        if not content_analysis.get('address_present', False):
            score -= 15
        
        return max(0, score)
    
    def _calculate_trade_seo_score(
        self,
        content_analysis: Dict[str, Any],
        business: Business
    ) -> int:
        """Calculate trade-specific SEO score."""
        
        score = 100
        
        # Trade keywords present
        trade_keywords = self._get_trade_keywords(business)
        trade_keyword_count = sum(
            1 for keyword in trade_keywords
            if keyword.lower() in content_analysis.get('content', '').lower()
        )
        
        if trade_keyword_count == 0:
            score -= 40
        elif trade_keyword_count < len(trade_keywords) / 2:
            score -= 20
        
        # Service descriptions
        if not content_analysis.get('services_described', False):
            score -= 30
        
        return max(0, score)
    
    def _get_optimal_keyword_density(self, keyword: str, business: Business) -> Tuple[float, float]:
        """Get optimal keyword density range for a keyword."""
        
        # Primary keywords can have higher density
        trade_keywords = self._get_trade_keywords(business)
        if keyword.lower() in [tk.lower() for tk in trade_keywords]:
            return (1.0, 3.0)  # 1-3% for primary trade keywords
        
        # Location keywords
        locations = [business.city, business.state] + business.service_areas
        if any(loc.lower() in keyword.lower() for loc in locations):
            return (0.5, 2.0)  # 0.5-2% for location keywords
        
        # General keywords
        return (0.5, 1.5)  # 0.5-1.5% for general keywords
    
    def _count_keyword_in_headings(self, content: str, keyword: str) -> int:
        """Count occurrences of keyword in headings."""
        
        # Simple heading detection (would be more sophisticated in real implementation)
        heading_pattern = r'<h[1-6][^>]*>(.*?)</h[1-6]>'
        headings = re.findall(heading_pattern, content, re.IGNORECASE | re.DOTALL)
        
        count = 0
        for heading in headings:
            if keyword.lower() in heading.lower():
                count += 1
        
        return count
    
    def _generate_content_recommendations(
        self,
        analysis: Dict[str, Any],
        target_keywords: List[str],
        business: Business
    ) -> List[SEOOptimizationRecommendation]:
        """Generate content optimization recommendations."""
        
        recommendations = []
        
        for keyword in target_keywords:
            density_data = analysis['keyword_density'][keyword]
            placement_data = analysis['keyword_placement'][keyword]
            
            # Keyword density recommendations
            if density_data['density'] < density_data['optimal_range'][0]:
                recommendations.append(SEOOptimizationRecommendation(
                    type="CONTENT",
                    priority="MEDIUM",
                    title=f"Increase '{keyword}' keyword density",
                    description=f"Current density is {density_data['density']:.1f}%, optimal range is {density_data['optimal_range'][0]}-{density_data['optimal_range'][1]}%",
                    implementation_effort="LOW",
                    expected_impact="MEDIUM",
                    trade_specific=keyword.lower() in [tk.lower() for tk in self._get_trade_keywords(business)]
                ))
            
            # Keyword placement recommendations
            if not placement_data['in_title']:
                recommendations.append(SEOOptimizationRecommendation(
                    type="CONTENT",
                    priority="HIGH",
                    title=f"Include '{keyword}' in page title",
                    description="Including target keywords in the page title is crucial for SEO",
                    implementation_effort="LOW",
                    expected_impact="HIGH",
                    trade_specific=True
                ))
        
        return recommendations
    
    def _generate_local_business_schema(
        self,
        business: Business,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate LocalBusiness schema markup."""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business.name,
            "telephone": business.phone_number,
            "email": business.email,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business.address,
                "addressLocality": business.city,
                "addressRegion": business.state,
                "postalCode": business.postal_code,
                "addressCountry": "US"
            },
            "areaServed": [
                {
                    "@type": "City",
                    "name": area
                } for area in business.service_areas
            ]
        }
        
        # Add trade-specific schema type
        trade_schema_types = {
            'plumbing': 'Plumber',
            'hvac': 'HVACBusiness',
            'electrical': 'Electrician',
            'roofing': 'RoofingContractor',
            'landscaping': 'LandscapingBusiness'
        }
        
        primary_trade = business.get_primary_trade().lower()
        if primary_trade in trade_schema_types:
            schema["@type"] = trade_schema_types[primary_trade]
        
        # Add additional data if provided
        if additional_data:
            if 'hours' in additional_data:
                schema['openingHours'] = additional_data['hours']
            if 'services' in additional_data:
                schema['hasOfferCatalog'] = {
                    "@type": "OfferCatalog",
                    "name": "Services",
                    "itemListElement": [
                        {
                            "@type": "Offer",
                            "itemOffered": {
                                "@type": "Service",
                                "name": service
                            }
                        } for service in additional_data['services']
                    ]
                }
        
        return schema
    
    def _generate_service_schema(
        self,
        business: Business,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate Service schema markup."""
        
        services = additional_data.get('services', []) if additional_data else []
        
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{business.name} Services",
            "itemListElement": [
                {
                    "@type": "Service",
                    "name": service,
                    "provider": {
                        "@type": "LocalBusiness",
                        "name": business.name,
                        "telephone": business.phone
                    },
                    "areaServed": business.service_areas
                } for service in services
            ]
        }
    
    def _generate_contact_schema(self, business: Business) -> Dict[str, Any]:
        """Generate ContactPage schema markup."""
        
        return {
            "@context": "https://schema.org",
            "@type": "ContactPage",
            "mainEntity": {
                "@type": "LocalBusiness",
                "name": business.name,
                "telephone": business.phone_number,
                "email": business.email,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": business.address,
                    "addressLocality": business.city,
                    "addressRegion": business.state,
                    "postalCode": business.postal_code
                }
            }
        }
    
    def _generate_organization_schema(self, business: Business) -> Dict[str, Any]:
        """Generate Organization schema markup."""
        
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": business.name,
            "telephone": business.phone_number,
            "email": business.email,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business.address,
                "addressLocality": business.city,
                "addressRegion": business.state,
                "postalCode": business.postal_code
            },
            "foundingLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": business.city,
                    "addressRegion": business.state
                }
            }
        }
    
    def _generate_webpage_schema(
        self,
        business: Business,
        page_type: str,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate WebPage schema markup."""
        
        return {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": f"{business.name} - {page_type.title()}",
            "description": f"{page_type.title()} page for {business.name}",
            "publisher": {
                "@type": "Organization",
                "name": business.name
            },
            "mainEntity": {
                "@type": "LocalBusiness",
                "name": business.name,
                "telephone": business.phone
            }
        }
    
    def _identify_keyword_opportunities(
        self,
        keyword_gaps: List[str],
        business: Business
    ) -> List[Dict[str, Any]]:
        """Identify keyword opportunities from competitor gaps."""
        
        opportunities = []
        trade_keywords = self._get_trade_keywords(business)
        
        for keyword in keyword_gaps[:20]:  # Limit to top 20 opportunities
            # Calculate opportunity score
            opportunity_score = 50  # Base score
            
            # Higher score for trade-relevant keywords
            if any(trade_kw.lower() in keyword.lower() for trade_kw in trade_keywords):
                opportunity_score += 30
            
            # Higher score for local keywords
            if any(loc.lower() in keyword.lower() for loc in [business.city, business.state]):
                opportunity_score += 20
            
            # Lower score for very competitive keywords
            if len(keyword.split()) == 1:  # Single word keywords are usually more competitive
                opportunity_score -= 20
            
            opportunities.append({
                'keyword': keyword,
                'opportunity_score': min(100, opportunity_score),
                'estimated_difficulty': self.calculate_keyword_difficulty(
                    keyword, {'competition_score': 50}, business
                ),
                'recommended_action': self._get_keyword_action_recommendation(keyword, business)
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return opportunities
    
    def _get_keyword_action_recommendation(self, keyword: str, business: Business) -> str:
        """Get recommended action for a keyword opportunity."""
        
        if any(trade_kw.lower() in keyword.lower() for trade_kw in self._get_trade_keywords(business)):
            return "Create dedicated service page"
        elif any(loc.lower() in keyword.lower() for loc in [business.city, business.state]):
            return "Add location-specific content"
        else:
            return "Create blog content or FAQ section"
