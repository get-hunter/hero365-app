"""
Subdomain Domain Service

Contains pure business logic for subdomain operations.
No external dependencies - only domain rules and calculations.
"""

import uuid
from typing import Dict, Any
from datetime import datetime

from ..entities.website import BusinessWebsite


class SubdomainDomainService:
    """
    Domain service containing pure business logic for subdomain operations.
    
    This service handles:
    - Subdomain naming rules
    - Validation logic
    - Analytics calculations
    """
    
    def generate_subdomain_name(self, website: BusinessWebsite) -> str:
        """
        Generate a unique subdomain name for the website.
        
        Business rules:
        - Use primary trade as base name
        - Add random suffix for uniqueness
        - Ensure valid DNS format (lowercase, alphanumeric + hyphens)
        - No leading/trailing hyphens
        """
        
        # Business rule: Use primary trade or fallback to "website"
        base_name = website.primary_trade or "website"
        
        # Business rule: Add 8-character random suffix for uniqueness
        random_suffix = uuid.uuid4().hex[:8]
        
        subdomain = f"{base_name}-{random_suffix}"
        
        # Business rule: Ensure subdomain is valid DNS format
        subdomain = subdomain.lower().replace('_', '-')
        subdomain = ''.join(c for c in subdomain if c.isalnum() or c == '-')
        
        # Business rule: No leading/trailing hyphens
        subdomain = subdomain.strip('-')
        
        return subdomain
    
    def validate_subdomain_name(self, subdomain: str) -> Dict[str, Any]:
        """
        Validate subdomain name against business rules.
        
        Business rules:
        - Length: 3-63 characters
        - Format: lowercase alphanumeric + hyphens only
        - No leading/trailing hyphens
        - No consecutive hyphens
        """
        
        errors = []
        
        # Length validation
        if len(subdomain) < 3:
            errors.append("Subdomain must be at least 3 characters long")
        elif len(subdomain) > 63:
            errors.append("Subdomain cannot exceed 63 characters")
        
        # Format validation
        if not subdomain.islower():
            errors.append("Subdomain must be lowercase")
        
        if not all(c.isalnum() or c == '-' for c in subdomain):
            errors.append("Subdomain can only contain letters, numbers, and hyphens")
        
        # Hyphen rules
        if subdomain.startswith('-') or subdomain.endswith('-'):
            errors.append("Subdomain cannot start or end with a hyphen")
        
        if '--' in subdomain:
            errors.append("Subdomain cannot contain consecutive hyphens")
        
        # Reserved names
        reserved_names = ['www', 'api', 'admin', 'mail', 'ftp', 'blog', 'shop']
        if subdomain in reserved_names:
            errors.append(f"'{subdomain}' is a reserved subdomain name")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "subdomain": subdomain
        }
    
    def calculate_deployment_priority(
        self, 
        website: BusinessWebsite, 
        deployment_context: Dict[str, Any]
    ) -> int:
        """
        Calculate deployment priority based on business rules.
        
        Business rules:
        - Premium businesses get higher priority
        - Larger websites get higher priority
        - Time-sensitive deployments get boost
        """
        
        priority = 50  # Base priority
        
        # Business tier priority
        business_tier = deployment_context.get("business_tier", "basic")
        if business_tier == "premium":
            priority += 30
        elif business_tier == "pro":
            priority += 20
        elif business_tier == "standard":
            priority += 10
        
        # Website size priority
        file_count = deployment_context.get("file_count", 0)
        if file_count > 100:
            priority += 15
        elif file_count > 50:
            priority += 10
        elif file_count > 20:
            priority += 5
        
        # Urgency boost
        if deployment_context.get("urgent", False):
            priority += 25
        
        # Time-based priority (business hours get slight boost)
        current_hour = datetime.utcnow().hour
        if 9 <= current_hour <= 17:  # Business hours UTC
            priority += 5
        
        return min(priority, 100)  # Cap at 100
    
    def generate_analytics_summary(self, raw_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate business-friendly analytics summary.
        
        Business rules:
        - Calculate key performance indicators
        - Provide actionable insights
        - Format for business users
        """
        
        page_views = raw_analytics.get("page_views", 0)
        unique_visitors = raw_analytics.get("unique_visitors", 0)
        bounce_rate = raw_analytics.get("bounce_rate", 0)
        
        # Calculate engagement score (business rule)
        engagement_score = 0
        if unique_visitors > 0:
            pages_per_session = page_views / unique_visitors
            engagement_score = min((pages_per_session * (100 - bounce_rate)) / 100, 100)
        
        # Determine performance rating (business rule)
        if engagement_score >= 80:
            performance_rating = "Excellent"
        elif engagement_score >= 60:
            performance_rating = "Good"
        elif engagement_score >= 40:
            performance_rating = "Fair"
        else:
            performance_rating = "Needs Improvement"
        
        # Generate insights (business rules)
        insights = []
        
        if bounce_rate > 70:
            insights.append("High bounce rate - consider improving page load speed or content relevance")
        
        if page_views > 0 and unique_visitors > 0:
            conversion_potential = (unique_visitors / page_views) * 100
            if conversion_potential < 20:
                insights.append("Low visitor engagement - consider adding call-to-action buttons")
        
        traffic_sources = raw_analytics.get("traffic_sources", {})
        search_traffic = traffic_sources.get("search", 0)
        total_traffic = sum(traffic_sources.values()) if traffic_sources else 1
        
        if search_traffic / total_traffic < 0.3:
            insights.append("Low search traffic - consider SEO optimization")
        
        return {
            "engagement_score": round(engagement_score, 1),
            "performance_rating": performance_rating,
            "insights": insights,
            "summary": {
                "total_visitors": unique_visitors,
                "total_views": page_views,
                "engagement_level": performance_rating.lower(),
                "primary_recommendation": insights[0] if insights else "Keep up the good work!"
            }
        }
    
    def determine_cache_strategy(self, deployment_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine optimal caching strategy based on business rules.
        
        Business rules:
        - Static content: long cache times
        - Dynamic content: short cache times
        - Business tier affects cache duration
        """
        
        file_types = deployment_context.get("file_types", [])
        business_tier = deployment_context.get("business_tier", "basic")
        
        # Base cache times (business rules)
        cache_config = {
            "html": 3600,      # 1 hour
            "css": 86400,      # 24 hours
            "js": 86400,       # 24 hours
            "images": 604800,  # 7 days
            "fonts": 2592000,  # 30 days
            "default": 3600    # 1 hour
        }
        
        # Premium businesses get longer cache times (business rule)
        if business_tier in ["premium", "pro"]:
            cache_config = {k: v * 2 for k, v in cache_config.items()}
        
        # Determine primary strategy
        if any(ft in ["html", "php", "asp"] for ft in file_types):
            strategy = "mixed"  # Mix of static and dynamic
        else:
            strategy = "static"  # Mostly static content
        
        return {
            "strategy": strategy,
            "cache_times": cache_config,
            "cdn_enabled": business_tier in ["premium", "pro"],
            "compression_enabled": True
        }
