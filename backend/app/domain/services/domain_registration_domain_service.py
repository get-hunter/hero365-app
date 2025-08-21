"""
Domain Registration Domain Service

Contains all domain registration business logic and rules.
This service is pure domain logic with no external dependencies.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from dataclasses import dataclass

from ..entities.business import Business, TradeCategory
from ..entities.website import SEOFactors

logger = logging.getLogger(__name__)


@dataclass
class DomainSuggestion:
    """Domain model for domain suggestions."""
    
    domain: str
    tld: str
    seo_score: int  # 1-100
    brandability_score: int  # 1-100
    memorability_score: int  # 1-100
    trade_relevance: int  # 1-100
    local_relevance: int  # 1-100
    recommended_priority: str  # HIGH, MEDIUM, LOW
    reasoning: List[str]  # Reasons for the score/recommendation


@dataclass
class DomainValidationResult:
    """Domain model for domain validation results."""
    
    is_valid: bool
    domain: str
    issues: List[str]
    warnings: List[str]
    seo_impact: str  # POSITIVE, NEUTRAL, NEGATIVE
    recommendations: List[str]


@dataclass
class SEODomainFactors:
    """Domain model for SEO factors in domain evaluation."""
    
    length_score: int  # 1-100
    keyword_presence: int  # 1-100
    brandability: int  # 1-100
    memorability: int  # 1-100
    tld_authority: int  # 1-100
    local_relevance: int  # 1-100
    trade_relevance: int  # 1-100


class DomainRegistrationDomainService:
    """
    Domain service for domain registration business logic.
    
    Contains all domain-related business rules and calculations
    without any external dependencies or infrastructure concerns.
    """
    
    def calculate_seo_score(self, domain: str, business: Business) -> int:
        """
        Calculate SEO score for a domain based on business context.
        
        Args:
            domain: Domain name to evaluate
            business: Business context
            
        Returns:
            SEO score from 1-100
        """
        
        factors = self._analyze_seo_factors(domain, business)
        
        # Weight different factors
        weights = {
            'length_score': 0.15,
            'keyword_presence': 0.25,
            'brandability': 0.20,
            'memorability': 0.15,
            'tld_authority': 0.10,
            'local_relevance': 0.10,
            'trade_relevance': 0.05
        }
        
        total_score = sum(
            getattr(factors, factor) * weight
            for factor, weight in weights.items()
        )
        
        return int(total_score)
    
    def generate_domain_suggestions(
        self,
        business: Business,
        max_suggestions: int = 20
    ) -> List[DomainSuggestion]:
        """
        Generate domain name suggestions for a business.
        
        Args:
            business: Business entity
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of domain suggestions sorted by relevance
        """
        
        suggestions = []
        
        # Get base components for domain generation
        business_name_parts = self._extract_business_name_parts(business.name)
        trade_keywords = self._get_trade_keywords(business)
        location_keywords = self._get_location_keywords(business)
        
        # Generate different types of domain suggestions
        suggestions.extend(self._generate_exact_match_domains(business_name_parts))
        suggestions.extend(self._generate_trade_domains(business_name_parts, trade_keywords))
        suggestions.extend(self._generate_location_domains(business_name_parts, location_keywords))
        suggestions.extend(self._generate_branded_domains(business_name_parts))
        suggestions.extend(self._generate_creative_domains(business_name_parts, trade_keywords))
        
        # Score and rank suggestions
        scored_suggestions = []
        for suggestion in suggestions:
            seo_score = self.calculate_seo_score(suggestion, business)
            brandability_score = self._calculate_brandability_score(suggestion)
            memorability_score = self._calculate_memorability_score(suggestion)
            trade_relevance = self._calculate_trade_relevance(suggestion, business)
            local_relevance = self._calculate_local_relevance(suggestion, business)
            
            # Determine priority
            priority = self._determine_domain_priority(
                seo_score, brandability_score, memorability_score, trade_relevance
            )
            
            # Generate reasoning
            reasoning = self._generate_domain_reasoning(
                suggestion, seo_score, brandability_score, trade_relevance, business
            )
            
            scored_suggestions.append(DomainSuggestion(
                domain=suggestion,
                tld=self._extract_tld(suggestion),
                seo_score=seo_score,
                brandability_score=brandability_score,
                memorability_score=memorability_score,
                trade_relevance=trade_relevance,
                local_relevance=local_relevance,
                recommended_priority=priority,
                reasoning=reasoning
            ))
        
        # Sort by overall quality (weighted combination of scores)
        scored_suggestions.sort(
            key=lambda x: (
                x.seo_score * 0.4 +
                x.brandability_score * 0.3 +
                x.trade_relevance * 0.2 +
                x.memorability_score * 0.1
            ),
            reverse=True
        )
        
        return scored_suggestions[:max_suggestions]
    
    def get_recommended_tlds(self, business: Business) -> List[Tuple[str, int, str]]:
        """
        Get recommended TLDs for a business with priority scores.
        
        Args:
            business: Business entity
            
        Returns:
            List of tuples: (tld, priority_score, reasoning)
        """
        
        recommendations = []
        
        # Universal recommendations
        recommendations.append(('.com', 100, 'Most trusted and memorable TLD'))
        recommendations.append(('.net', 75, 'Good alternative to .com'))
        
        # Trade-specific TLDs
        trade_tlds = self._get_trade_specific_tlds(business)
        for tld, score, reason in trade_tlds:
            recommendations.append((tld, score, reason))
        
        # Location-specific TLDs (if applicable)
        if business.state.lower() in ['california', 'texas', 'florida', 'new york']:
            recommendations.append(('.us', 60, 'Good for US-based local businesses'))
        
        # Business type TLDs
        if business.trade_category == TradeCategory.COMMERCIAL:
            recommendations.append(('.biz', 50, 'Suitable for commercial businesses'))
        
        # Sort by priority score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def validate_domain_for_business(
        self,
        domain: str,
        business: Business
    ) -> DomainValidationResult:
        """
        Validate a domain name for a specific business.
        
        Args:
            domain: Domain name to validate
            business: Business context
            
        Returns:
            Validation result with issues and recommendations
        """
        
        issues = []
        warnings = []
        recommendations = []
        
        # Basic format validation
        if not self._is_valid_domain_format(domain):
            issues.append("Invalid domain format")
        
        # Length validation
        domain_name = domain.split('.')[0]
        if len(domain_name) < 3:
            issues.append("Domain name too short (minimum 3 characters)")
        elif len(domain_name) > 63:
            issues.append("Domain name too long (maximum 63 characters)")
        elif len(domain_name) > 25:
            warnings.append("Long domain names are harder to remember and type")
        
        # Character validation
        if not re.match(r'^[a-zA-Z0-9-]+$', domain_name):
            issues.append("Domain contains invalid characters")
        
        if domain_name.startswith('-') or domain_name.endswith('-'):
            issues.append("Domain cannot start or end with hyphen")
        
        if '--' in domain_name:
            warnings.append("Multiple consecutive hyphens can be confusing")
        
        # Business relevance validation
        business_name_clean = re.sub(r'[^a-zA-Z0-9]', '', business.name.lower())
        domain_clean = re.sub(r'[^a-zA-Z0-9]', '', domain_name.lower())
        
        if business_name_clean not in domain_clean and domain_clean not in business_name_clean:
            trade_keywords = [kw.lower() for kw in self._get_trade_keywords(business)]
            if not any(keyword in domain_clean for keyword in trade_keywords):
                warnings.append("Domain doesn't clearly relate to business name or services")
        
        # SEO considerations
        seo_score = self.calculate_seo_score(domain, business)
        if seo_score < 40:
            warnings.append("Domain has low SEO potential")
            recommendations.append("Consider including business name or trade keywords")
        
        # TLD validation
        tld = self._extract_tld(domain)
        recommended_tlds = [rec[0] for rec in self.get_recommended_tlds(business)]
        if tld not in recommended_tlds[:5]:  # Top 5 recommended
            warnings.append(f"TLD '{tld}' is not among top recommendations for your business")
        
        # Determine SEO impact
        if seo_score >= 70:
            seo_impact = "POSITIVE"
        elif seo_score >= 40:
            seo_impact = "NEUTRAL"
        else:
            seo_impact = "NEGATIVE"
        
        # Generate recommendations
        if not recommendations:
            if seo_score >= 70:
                recommendations.append("Good domain choice for SEO")
            else:
                recommendations.append("Consider domains with business name or trade keywords")
        
        return DomainValidationResult(
            is_valid=len(issues) == 0,
            domain=domain,
            issues=issues,
            warnings=warnings,
            seo_impact=seo_impact,
            recommendations=recommendations
        )
    
    def calculate_brandability_score(self, domain: str) -> int:
        """
        Calculate how brandable a domain name is.
        
        Args:
            domain: Domain name to evaluate
            
        Returns:
            Brandability score from 1-100
        """
        
        return self._calculate_brandability_score(domain)
    
    def suggest_domain_improvements(
        self,
        domain: str,
        business: Business
    ) -> List[str]:
        """
        Suggest improvements for a domain name.
        
        Args:
            domain: Current domain name
            business: Business context
            
        Returns:
            List of improved domain suggestions
        """
        
        improvements = []
        domain_name = domain.split('.')[0]
        tld = self._extract_tld(domain)
        
        # Suggest shorter versions
        if len(domain_name) > 15:
            shorter_versions = self._generate_shorter_versions(domain_name, business)
            improvements.extend([f"{short}.{tld}" for short in shorter_versions])
        
        # Suggest versions without hyphens
        if '-' in domain_name:
            no_hyphen = domain_name.replace('-', '')
            if len(no_hyphen) <= 20:
                improvements.append(f"{no_hyphen}.{tld}")
        
        # Suggest with trade keywords
        trade_keywords = self._get_trade_keywords(business)
        for keyword in trade_keywords[:2]:  # Top 2 trade keywords
            if keyword.lower() not in domain_name.lower():
                improvements.append(f"{domain_name}{keyword}.{tld}")
                improvements.append(f"{keyword}{domain_name}.{tld}")
        
        # Suggest better TLDs
        if tld not in ['.com', '.net']:
            improvements.append(f"{domain_name}.com")
            improvements.append(f"{domain_name}.net")
        
        # Remove duplicates and return top suggestions
        improvements = list(set(improvements))
        return improvements[:10]
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _analyze_seo_factors(self, domain: str, business: Business) -> SEODomainFactors:
        """Analyze SEO factors for a domain."""
        
        domain_name = domain.split('.')[0]
        tld = self._extract_tld(domain)
        
        return SEODomainFactors(
            length_score=self._calculate_length_score(domain_name),
            keyword_presence=self._calculate_keyword_presence_score(domain_name, business),
            brandability=self._calculate_brandability_score(domain),
            memorability=self._calculate_memorability_score(domain),
            tld_authority=self._calculate_tld_authority_score(tld),
            local_relevance=self._calculate_local_relevance(domain, business),
            trade_relevance=self._calculate_trade_relevance(domain, business)
        )
    
    def _extract_business_name_parts(self, business_name: str) -> List[str]:
        """Extract meaningful parts from business name."""
        
        # Remove common business suffixes
        suffixes = ['llc', 'inc', 'corp', 'company', 'co', 'ltd', 'services', 'service']
        name_clean = business_name.lower()
        
        for suffix in suffixes:
            name_clean = re.sub(rf'\b{suffix}\b', '', name_clean)
        
        # Split into words and filter
        words = re.findall(r'\b[a-zA-Z]+\b', name_clean)
        
        # Filter out common words
        common_words = ['the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with']
        meaningful_words = [word for word in words if word not in common_words and len(word) > 2]
        
        return meaningful_words
    
    def _get_trade_keywords(self, business: Business) -> List[str]:
        """Get relevant trade keywords for domain generation."""
        
        trade_keywords_map = {
            'plumbing': ['plumbing', 'plumber', 'pipes', 'drain', 'water'],
            'hvac': ['hvac', 'heating', 'cooling', 'air', 'climate'],
            'electrical': ['electric', 'electrical', 'electrician', 'power', 'wiring'],
            'roofing': ['roofing', 'roofer', 'roof', 'shingles', 'gutters'],
            'landscaping': ['landscape', 'landscaping', 'lawn', 'garden', 'yard'],
            'pest control': ['pest', 'exterminator', 'bug', 'termite', 'control'],
            'security systems': ['security', 'alarm', 'surveillance', 'protection'],
            'pool & spa': ['pool', 'spa', 'swimming', 'hot tub', 'water'],
            'garage door': ['garage', 'door', 'opener', 'repair'],
            'septic': ['septic', 'sewer', 'waste', 'pumping']
        }
        
        primary_trade = business.get_primary_trade().lower()
        return trade_keywords_map.get(primary_trade, [primary_trade.replace(' ', '')])
    
    def _get_location_keywords(self, business: Business) -> List[str]:
        """Get location-based keywords for domain generation."""
        
        keywords = []
        
        # City name variations
        city_clean = re.sub(r'[^a-zA-Z]', '', business.city.lower())
        keywords.append(city_clean)
        
        # State abbreviation
        keywords.append(business.state.lower())
        
        # Service areas
        for area in business.service_areas[:3]:  # Limit to top 3
            area_clean = re.sub(r'[^a-zA-Z]', '', area.lower())
            if len(area_clean) <= 10:  # Only short area names
                keywords.append(area_clean)
        
        return keywords
    
    def _generate_exact_match_domains(self, business_parts: List[str]) -> List[str]:
        """Generate exact match domains from business name."""
        
        domains = []
        
        if business_parts:
            # Single word
            if len(business_parts) == 1:
                domains.append(f"{business_parts[0]}.com")
                domains.append(f"{business_parts[0]}.net")
            
            # Multiple words
            elif len(business_parts) > 1:
                # Concatenated
                concatenated = ''.join(business_parts)
                if len(concatenated) <= 20:
                    domains.append(f"{concatenated}.com")
                    domains.append(f"{concatenated}.net")
                
                # Hyphenated
                hyphenated = '-'.join(business_parts)
                if len(hyphenated) <= 25:
                    domains.append(f"{hyphenated}.com")
                    domains.append(f"{hyphenated}.net")
        
        return domains
    
    def _generate_trade_domains(
        self,
        business_parts: List[str],
        trade_keywords: List[str]
    ) -> List[str]:
        """Generate trade-specific domain combinations."""
        
        domains = []
        
        for business_part in business_parts[:2]:  # Limit to first 2 parts
            for trade_keyword in trade_keywords[:3]:  # Limit to first 3 keywords
                # Business + Trade
                combo1 = f"{business_part}{trade_keyword}"
                if len(combo1) <= 20:
                    domains.extend([f"{combo1}.com", f"{combo1}.services"])
                
                # Trade + Business
                combo2 = f"{trade_keyword}{business_part}"
                if len(combo2) <= 20:
                    domains.extend([f"{combo2}.com", f"{combo2}.services"])
        
        return domains
    
    def _generate_location_domains(
        self,
        business_parts: List[str],
        location_keywords: List[str]
    ) -> List[str]:
        """Generate location-specific domain combinations."""
        
        domains = []
        
        for business_part in business_parts[:2]:
            for location in location_keywords[:2]:
                # Business + Location
                combo1 = f"{business_part}{location}"
                if len(combo1) <= 20:
                    domains.extend([f"{combo1}.com", f"{combo1}.net"])
                
                # Location + Business
                combo2 = f"{location}{business_part}"
                if len(combo2) <= 20:
                    domains.extend([f"{combo2}.com", f"{combo2}.net"])
        
        return domains
    
    def _generate_branded_domains(self, business_parts: List[str]) -> List[str]:
        """Generate brandable domain variations."""
        
        domains = []
        
        if business_parts:
            main_part = business_parts[0]
            
            # Add common prefixes/suffixes
            prefixes = ['get', 'my', 'the', 'pro']
            suffixes = ['pro', 'hub', 'zone', 'plus', 'now']
            
            for prefix in prefixes:
                combo = f"{prefix}{main_part}"
                if len(combo) <= 15:
                    domains.append(f"{combo}.com")
            
            for suffix in suffixes:
                combo = f"{main_part}{suffix}"
                if len(combo) <= 15:
                    domains.append(f"{combo}.com")
        
        return domains
    
    def _generate_creative_domains(
        self,
        business_parts: List[str],
        trade_keywords: List[str]
    ) -> List[str]:
        """Generate creative domain combinations."""
        
        domains = []
        
        # Creative combinations with action words
        action_words = ['fix', 'repair', 'install', 'service', 'care']
        
        for action in action_words:
            for trade in trade_keywords[:2]:
                combo = f"{action}{trade}"
                if len(combo) <= 15:
                    domains.append(f"{combo}.com")
        
        return domains
    
    def _calculate_length_score(self, domain_name: str) -> int:
        """Calculate score based on domain length."""
        
        length = len(domain_name)
        
        if length <= 8:
            return 100
        elif length <= 12:
            return 90
        elif length <= 16:
            return 70
        elif length <= 20:
            return 50
        else:
            return 20
    
    def _calculate_keyword_presence_score(self, domain_name: str, business: Business) -> int:
        """Calculate score based on keyword presence."""
        
        score = 0
        domain_lower = domain_name.lower()
        
        # Business name keywords
        business_parts = self._extract_business_name_parts(business.name)
        for part in business_parts:
            if part.lower() in domain_lower:
                score += 30
        
        # Trade keywords
        trade_keywords = self._get_trade_keywords(business)
        for keyword in trade_keywords:
            if keyword.lower() in domain_lower:
                score += 25
        
        # Location keywords
        location_keywords = self._get_location_keywords(business)
        for keyword in location_keywords:
            if keyword.lower() in domain_lower:
                score += 15
        
        return min(100, score)
    
    def _calculate_brandability_score(self, domain: str) -> int:
        """Calculate brandability score for a domain."""
        
        domain_name = domain.split('.')[0]
        score = 100
        
        # Penalize hyphens
        hyphen_count = domain_name.count('-')
        score -= hyphen_count * 15
        
        # Penalize numbers
        number_count = sum(1 for char in domain_name if char.isdigit())
        score -= number_count * 10
        
        # Reward pronounceability (simple heuristic)
        vowels = 'aeiou'
        vowel_count = sum(1 for char in domain_name.lower() if char in vowels)
        consonant_count = len([char for char in domain_name.lower() if char.isalpha() and char not in vowels])
        
        if vowel_count > 0:
            vowel_ratio = vowel_count / (vowel_count + consonant_count)
            if 0.2 <= vowel_ratio <= 0.6:  # Good vowel-consonant balance
                score += 10
            else:
                score -= 10
        
        # Penalize very long domains
        if len(domain_name) > 15:
            score -= (len(domain_name) - 15) * 3
        
        return max(0, score)
    
    def _calculate_memorability_score(self, domain: str) -> int:
        """Calculate memorability score for a domain."""
        
        domain_name = domain.split('.')[0]
        score = 100
        
        # Shorter is more memorable
        if len(domain_name) > 12:
            score -= (len(domain_name) - 12) * 5
        
        # Simple patterns are more memorable
        if re.match(r'^[a-z]+$', domain_name.lower()):  # All letters
            score += 10
        
        # Penalize complex patterns
        if re.search(r'[0-9]', domain_name):
            score -= 15
        if '-' in domain_name:
            score -= 10
        
        # Reward common word patterns
        if any(word in domain_name.lower() for word in ['pro', 'fix', 'care', 'service']):
            score += 5
        
        return max(0, score)
    
    def _calculate_tld_authority_score(self, tld: str) -> int:
        """Calculate authority score for TLD."""
        
        tld_scores = {
            '.com': 100,
            '.net': 85,
            '.org': 80,
            '.services': 70,
            '.biz': 60,
            '.info': 50,
            '.us': 65,
            '.co': 75
        }
        
        return tld_scores.get(tld, 40)
    
    def _calculate_local_relevance(self, domain: str, business: Business) -> int:
        """Calculate local relevance score."""
        
        domain_lower = domain.lower()
        score = 0
        
        # City name
        if business.city.lower() in domain_lower:
            score += 40
        
        # State name or abbreviation
        if business.state.lower() in domain_lower:
            score += 30
        
        # Service areas
        for area in business.service_areas:
            if area.lower() in domain_lower:
                score += 20
                break
        
        return min(100, score)
    
    def _calculate_trade_relevance(self, domain: str, business: Business) -> int:
        """Calculate trade relevance score."""
        
        domain_lower = domain.lower()
        score = 0
        
        trade_keywords = self._get_trade_keywords(business)
        for keyword in trade_keywords:
            if keyword.lower() in domain_lower:
                score += 30
        
        return min(100, score)
    
    def _extract_tld(self, domain: str) -> str:
        """Extract TLD from domain."""
        
        parts = domain.split('.')
        if len(parts) > 1:
            return '.' + parts[-1]
        return '.com'  # Default
    
    def _get_trade_specific_tlds(self, business: Business) -> List[Tuple[str, int, str]]:
        """Get trade-specific TLD recommendations."""
        
        recommendations = []
        
        # Service-related TLDs
        recommendations.append(('.services', 80, 'Perfect for service-based businesses'))
        
        # Trade-specific TLDs
        primary_trade = business.get_primary_trade().lower()
        
        if 'plumbing' in primary_trade:
            recommendations.append(('.repair', 70, 'Great for repair services'))
        elif 'hvac' in primary_trade or 'heating' in primary_trade:
            recommendations.append(('.heating', 75, 'Specific to heating services'))
        elif 'electrical' in primary_trade:
            recommendations.append(('.electric', 75, 'Specific to electrical services'))
        elif 'landscaping' in primary_trade:
            recommendations.append(('.garden', 65, 'Good for landscaping businesses'))
        
        # Professional TLDs
        recommendations.append(('.pro', 70, 'Indicates professional services'))
        
        return recommendations
    
    def _is_valid_domain_format(self, domain: str) -> bool:
        """Check if domain has valid format."""
        
        # Basic domain regex
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        return bool(re.match(pattern, domain))
    
    def _determine_domain_priority(
        self,
        seo_score: int,
        brandability_score: int,
        memorability_score: int,
        trade_relevance: int
    ) -> str:
        """Determine priority level for domain suggestion."""
        
        avg_score = (seo_score + brandability_score + memorability_score + trade_relevance) / 4
        
        if avg_score >= 80:
            return "HIGH"
        elif avg_score >= 60:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_domain_reasoning(
        self,
        domain: str,
        seo_score: int,
        brandability_score: int,
        trade_relevance: int,
        business: Business
    ) -> List[str]:
        """Generate reasoning for domain recommendation."""
        
        reasoning = []
        
        if seo_score >= 80:
            reasoning.append("Excellent SEO potential")
        elif seo_score >= 60:
            reasoning.append("Good SEO potential")
        else:
            reasoning.append("Limited SEO potential")
        
        if brandability_score >= 80:
            reasoning.append("Highly brandable")
        elif brandability_score >= 60:
            reasoning.append("Moderately brandable")
        
        if trade_relevance >= 70:
            reasoning.append("Clearly relates to your services")
        
        domain_name = domain.split('.')[0]
        if len(domain_name) <= 10:
            reasoning.append("Short and memorable")
        elif len(domain_name) <= 15:
            reasoning.append("Reasonable length")
        
        tld = self._extract_tld(domain)
        if tld == '.com':
            reasoning.append("Premium .com extension")
        elif tld in ['.net', '.services']:
            reasoning.append("Professional extension")
        
        return reasoning
    
    def _generate_shorter_versions(self, domain_name: str, business: Business) -> List[str]:
        """Generate shorter versions of a domain name."""
        
        shorter_versions = []
        
        # Try acronyms
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', domain_name)
        if len(words) > 1:
            acronym = ''.join(word[0].lower() for word in words)
            if len(acronym) >= 3:
                shorter_versions.append(acronym)
        
        # Try removing common words
        common_removals = ['service', 'services', 'company', 'co', 'inc', 'llc']
        for removal in common_removals:
            if removal in domain_name.lower():
                shorter = domain_name.lower().replace(removal, '')
                if len(shorter) >= 4:
                    shorter_versions.append(shorter)
        
        # Try abbreviations of trade keywords
        trade_keywords = self._get_trade_keywords(business)
        for keyword in trade_keywords:
            if keyword in domain_name.lower():
                # Simple abbreviation (first 3-4 letters)
                abbrev = keyword[:4] if len(keyword) > 4 else keyword
                shorter = domain_name.lower().replace(keyword, abbrev)
                if len(shorter) <= 15:
                    shorter_versions.append(shorter)
        
        return list(set(shorter_versions))[:5]  # Return top 5 unique versions
