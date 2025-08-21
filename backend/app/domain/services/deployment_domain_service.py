"""
Deployment Domain Service

Contains all deployment-related business logic and rules.
This service is pure domain logic with no external dependencies.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..entities.business import Business, TradeCategory
from ..entities.website import BusinessWebsite, WebsiteStatus

logger = logging.getLogger(__name__)


@dataclass
class DeploymentStrategy:
    """Domain model for deployment strategy decisions."""
    
    hosting_type: str  # STATIC, SERVERLESS, CONTAINER
    cdn_required: bool
    ssl_required: bool
    caching_strategy: str  # AGGRESSIVE, MODERATE, MINIMAL
    compression_enabled: bool
    security_level: str  # BASIC, ENHANCED, ENTERPRISE
    performance_tier: str  # BASIC, OPTIMIZED, PREMIUM
    backup_frequency: str  # NONE, DAILY, WEEKLY
    monitoring_level: str  # BASIC, DETAILED, COMPREHENSIVE


@dataclass
class CacheConfiguration:
    """Domain model for caching configuration."""
    
    html_ttl_seconds: int
    css_ttl_seconds: int
    js_ttl_seconds: int
    image_ttl_seconds: int
    font_ttl_seconds: int
    api_ttl_seconds: int
    enable_browser_caching: bool
    enable_cdn_caching: bool
    cache_invalidation_strategy: str


@dataclass
class SecurityConfiguration:
    """Domain model for security configuration."""
    
    force_https: bool
    enable_hsts: bool
    content_security_policy: str
    x_frame_options: str
    x_content_type_options: str
    referrer_policy: str
    permissions_policy: str
    enable_cors: bool
    cors_origins: List[str]


@dataclass
class PerformanceConfiguration:
    """Domain model for performance optimization."""
    
    enable_compression: bool
    compression_types: List[str]
    enable_minification: bool
    enable_image_optimization: bool
    enable_lazy_loading: bool
    preload_critical_resources: List[str]
    dns_prefetch_domains: List[str]
    resource_hints: Dict[str, List[str]]


@dataclass
class DeploymentValidationResult:
    """Domain model for deployment validation results."""
    
    is_valid: bool
    readiness_score: int  # 1-100
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    estimated_deployment_time: int  # seconds
    resource_requirements: Dict[str, Any]


class DeploymentDomainService:
    """
    Domain service for deployment business logic.
    
    Contains all deployment-related business rules and calculations
    without any external dependencies or infrastructure concerns.
    """
    
    def determine_deployment_strategy(
        self,
        website: BusinessWebsite,
        business: Business,
        target_environment: str = "production"
    ) -> DeploymentStrategy:
        """
        Determine optimal deployment strategy based on business context.
        
        Args:
            website: Website entity
            business: Business context
            target_environment: Target deployment environment
            
        Returns:
            Deployment strategy with optimized settings
        """
        
        # Analyze business requirements
        trade_requirements = self._analyze_trade_requirements(business)
        traffic_expectations = self._estimate_traffic_requirements(business)
        performance_needs = self._assess_performance_needs(business, website)
        
        # Determine hosting type (Hero365 uses static sites)
        hosting_type = "STATIC"
        
        # CDN requirements based on service area coverage
        cdn_required = len(business.service_areas) > 3 or business.trade_category == TradeCategory.COMMERCIAL
        
        # SSL is always required for professional businesses
        ssl_required = True
        
        # Caching strategy based on business type and update frequency
        caching_strategy = self._determine_caching_strategy(business, website)
        
        # Compression for better performance (always enabled for Hero365)
        compression_enabled = True
        
        # Security level based on business type
        security_level = self._determine_security_level(business)
        
        # Performance tier based on business size and expectations
        performance_tier = self._determine_performance_tier(business, traffic_expectations)
        
        # Backup frequency based on business criticality
        backup_frequency = self._determine_backup_frequency(business)
        
        # Monitoring level based on business needs
        monitoring_level = self._determine_monitoring_level(business, target_environment)
        
        return DeploymentStrategy(
            hosting_type=hosting_type,
            cdn_required=cdn_required,
            ssl_required=ssl_required,
            caching_strategy=caching_strategy,
            compression_enabled=compression_enabled,
            security_level=security_level,
            performance_tier=performance_tier,
            backup_frequency=backup_frequency,
            monitoring_level=monitoring_level
        )
    
    def calculate_cache_configuration(
        self,
        strategy: DeploymentStrategy,
        business: Business,
        website: BusinessWebsite
    ) -> CacheConfiguration:
        """
        Calculate optimal cache configuration based on strategy and business needs.
        
        Args:
            strategy: Deployment strategy
            business: Business context
            website: Website entity
            
        Returns:
            Cache configuration with TTL values and settings
        """
        
        # Base TTL values based on caching strategy
        base_ttls = self._get_base_cache_ttls(strategy.caching_strategy)
        
        # Adjust TTLs based on business update frequency
        update_frequency = self._estimate_content_update_frequency(business)
        adjusted_ttls = self._adjust_ttls_for_update_frequency(base_ttls, update_frequency)
        
        # Special considerations for emergency services
        if self._provides_emergency_services(business):
            # Emergency services need shorter cache times for contact info
            adjusted_ttls["html_ttl_seconds"] = min(adjusted_ttls["html_ttl_seconds"], 3600)  # Max 1 hour
        
        return CacheConfiguration(
            html_ttl_seconds=adjusted_ttls["html_ttl_seconds"],
            css_ttl_seconds=adjusted_ttls["css_ttl_seconds"],
            js_ttl_seconds=adjusted_ttls["js_ttl_seconds"],
            image_ttl_seconds=adjusted_ttls["image_ttl_seconds"],
            font_ttl_seconds=adjusted_ttls["font_ttl_seconds"],
            api_ttl_seconds=adjusted_ttls["api_ttl_seconds"],
            enable_browser_caching=True,
            enable_cdn_caching=strategy.cdn_required,
            cache_invalidation_strategy=self._determine_invalidation_strategy(business)
        )
    
    def generate_security_configuration(
        self,
        strategy: DeploymentStrategy,
        business: Business,
        custom_domain: Optional[str] = None
    ) -> SecurityConfiguration:
        """
        Generate security configuration based on strategy and business requirements.
        
        Args:
            strategy: Deployment strategy
            business: Business context
            custom_domain: Optional custom domain
            
        Returns:
            Security configuration with headers and policies
        """
        
        # Base security settings
        force_https = strategy.ssl_required
        enable_hsts = strategy.security_level in ["ENHANCED", "ENTERPRISE"]
        
        # Content Security Policy based on security level
        csp = self._generate_content_security_policy(strategy.security_level, custom_domain)
        
        # Frame options for clickjacking protection
        x_frame_options = "DENY" if strategy.security_level == "ENTERPRISE" else "SAMEORIGIN"
        
        # Content type options
        x_content_type_options = "nosniff"
        
        # Referrer policy based on business type
        referrer_policy = self._determine_referrer_policy(business)
        
        # Permissions policy for modern browsers
        permissions_policy = self._generate_permissions_policy(business)
        
        # CORS settings
        enable_cors = business.trade_category == TradeCategory.COMMERCIAL  # Commercial may need API access
        cors_origins = self._determine_cors_origins(business, custom_domain)
        
        return SecurityConfiguration(
            force_https=force_https,
            enable_hsts=enable_hsts,
            content_security_policy=csp,
            x_frame_options=x_frame_options,
            x_content_type_options=x_content_type_options,
            referrer_policy=referrer_policy,
            permissions_policy=permissions_policy,
            enable_cors=enable_cors,
            cors_origins=cors_origins
        )
    
    def calculate_performance_configuration(
        self,
        strategy: DeploymentStrategy,
        business: Business,
        website: BusinessWebsite
    ) -> PerformanceConfiguration:
        """
        Calculate performance optimization configuration.
        
        Args:
            strategy: Deployment strategy
            business: Business context
            website: Website entity
            
        Returns:
            Performance configuration with optimization settings
        """
        
        # Compression settings
        enable_compression = strategy.compression_enabled
        compression_types = self._get_compression_types(strategy.performance_tier)
        
        # Minification based on performance tier
        enable_minification = strategy.performance_tier in ["OPTIMIZED", "PREMIUM"]
        
        # Image optimization for better Core Web Vitals
        enable_image_optimization = True  # Always enabled for Hero365
        
        # Lazy loading for performance
        enable_lazy_loading = strategy.performance_tier in ["OPTIMIZED", "PREMIUM"]
        
        # Critical resource preloading
        preload_resources = self._determine_critical_resources(business, website)
        
        # DNS prefetch domains
        dns_prefetch_domains = self._get_dns_prefetch_domains(business)
        
        # Resource hints for performance
        resource_hints = self._generate_resource_hints(business, strategy.performance_tier)
        
        return PerformanceConfiguration(
            enable_compression=enable_compression,
            compression_types=compression_types,
            enable_minification=enable_minification,
            enable_image_optimization=enable_image_optimization,
            enable_lazy_loading=enable_lazy_loading,
            preload_critical_resources=preload_resources,
            dns_prefetch_domains=dns_prefetch_domains,
            resource_hints=resource_hints
        )
    
    def validate_deployment_readiness(
        self,
        website: BusinessWebsite,
        business: Business,
        deployment_config: Dict[str, Any]
    ) -> DeploymentValidationResult:
        """
        Validate that a website is ready for deployment.
        
        Args:
            website: Website entity
            business: Business context
            deployment_config: Deployment configuration
            
        Returns:
            Validation result with readiness assessment
        """
        
        issues = []
        warnings = []
        recommendations = []
        readiness_score = 100
        
        # Validate website status
        if website.status != WebsiteStatus.BUILT:
            issues.append("Website must be built before deployment")
            readiness_score -= 50
        
        # Validate required content
        content_validation = self._validate_required_content(website, business)
        if not content_validation["valid"]:
            issues.extend(content_validation["missing_content"])
            readiness_score -= 20
        
        # Validate business information completeness
        business_validation = self._validate_business_information(business)
        if not business_validation["complete"]:
            warnings.extend(business_validation["missing_fields"])
            readiness_score -= 10
        
        # Validate SEO readiness
        seo_validation = self._validate_seo_readiness(website, business)
        if seo_validation["score"] < 70:
            warnings.append(f"SEO score is {seo_validation['score']}/100")
            recommendations.extend(seo_validation["recommendations"])
            readiness_score -= 5
        
        # Validate performance readiness
        performance_validation = self._validate_performance_readiness(website)
        if not performance_validation["optimized"]:
            recommendations.extend(performance_validation["optimizations"])
            readiness_score -= 5
        
        # Estimate deployment time
        estimated_time = self._estimate_deployment_time(website, deployment_config)
        
        # Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(website, business)
        
        return DeploymentValidationResult(
            is_valid=len(issues) == 0,
            readiness_score=max(0, readiness_score),
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            estimated_deployment_time=estimated_time,
            resource_requirements=resource_requirements
        )
    
    def calculate_deployment_cost_estimate(
        self,
        strategy: DeploymentStrategy,
        business: Business,
        website: BusinessWebsite,
        monthly_traffic_estimate: int = 10000
    ) -> Dict[str, Any]:
        """
        Calculate estimated monthly deployment costs.
        
        Args:
            strategy: Deployment strategy
            business: Business context
            website: Website entity
            monthly_traffic_estimate: Expected monthly page views
            
        Returns:
            Cost breakdown and total estimate
        """
        
        costs = {
            "hosting": 0.0,
            "cdn": 0.0,
            "ssl": 0.0,
            "storage": 0.0,
            "bandwidth": 0.0,
            "monitoring": 0.0,
            "backup": 0.0
        }
        
        # Storage costs (S3)
        estimated_size_gb = self._estimate_website_size(website)
        costs["storage"] = estimated_size_gb * 0.023  # $0.023 per GB/month
        
        # Bandwidth costs (CloudFront)
        if strategy.cdn_required:
            estimated_bandwidth_gb = (monthly_traffic_estimate * estimated_size_gb) / 1000
            costs["bandwidth"] = estimated_bandwidth_gb * 0.085  # $0.085 per GB
            costs["cdn"] = 5.0  # Base CDN cost
        
        # SSL certificate (free with AWS Certificate Manager)
        costs["ssl"] = 0.0
        
        # Monitoring costs based on level
        monitoring_costs = {
            "BASIC": 0.0,
            "DETAILED": 5.0,
            "COMPREHENSIVE": 15.0
        }
        costs["monitoring"] = monitoring_costs.get(strategy.monitoring_level, 0.0)
        
        # Backup costs based on frequency
        backup_costs = {
            "NONE": 0.0,
            "WEEKLY": 2.0,
            "DAILY": 5.0
        }
        costs["backup"] = backup_costs.get(strategy.backup_frequency, 0.0)
        
        total_cost = sum(costs.values())
        
        return {
            "breakdown": costs,
            "total_monthly": round(total_cost, 2),
            "currency": "USD",
            "traffic_estimate": monthly_traffic_estimate,
            "cost_per_visitor": round(total_cost / max(monthly_traffic_estimate, 1) * 1000, 4)  # Cost per 1000 visitors
        }
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _analyze_trade_requirements(self, business: Business) -> Dict[str, Any]:
        """Analyze deployment requirements specific to the business trade."""
        
        trade = business.get_primary_trade().lower()
        
        # Trade-specific requirements
        requirements = {
            "high_availability": False,
            "emergency_contact": False,
            "local_seo_critical": True,
            "mobile_first": True,
            "fast_loading": True
        }
        
        # Emergency services need high availability
        emergency_trades = ["plumbing", "hvac", "electrical", "security systems"]
        if trade in emergency_trades:
            requirements["high_availability"] = True
            requirements["emergency_contact"] = True
        
        # Commercial businesses need higher performance
        if business.trade_category == TradeCategory.COMMERCIAL:
            requirements["fast_loading"] = True
            requirements["high_availability"] = True
        
        return requirements
    
    def _estimate_traffic_requirements(self, business: Business) -> Dict[str, int]:
        """Estimate traffic requirements based on business characteristics."""
        
        # Base traffic estimate
        base_monthly_visitors = 1000
        
        # Adjust based on service areas
        area_multiplier = min(len(business.service_areas), 10)  # Cap at 10x
        estimated_monthly = base_monthly_visitors * area_multiplier
        
        # Commercial businesses typically have higher traffic
        if business.trade_category == TradeCategory.COMMERCIAL:
            estimated_monthly *= 2
        
        return {
            "monthly_visitors": estimated_monthly,
            "peak_concurrent": max(10, estimated_monthly // 100),  # 1% of monthly as peak
            "bandwidth_gb": estimated_monthly * 0.005  # 5MB average per visit
        }
    
    def _assess_performance_needs(self, business: Business, website: BusinessWebsite) -> str:
        """Assess performance needs based on business and website characteristics."""
        
        # Emergency services need fastest performance
        if self._provides_emergency_services(business):
            return "CRITICAL"
        
        # Commercial businesses need high performance
        if business.trade_category == TradeCategory.COMMERCIAL:
            return "HIGH"
        
        # Default to standard performance
        return "STANDARD"
    
    def _determine_caching_strategy(self, business: Business, website: BusinessWebsite) -> str:
        """Determine caching strategy based on content update patterns."""
        
        # Emergency services need moderate caching (contact info may change)
        if self._provides_emergency_services(business):
            return "MODERATE"
        
        # Static business websites can use aggressive caching
        return "AGGRESSIVE"
    
    def _determine_security_level(self, business: Business) -> str:
        """Determine security level based on business type and requirements."""
        
        # Commercial businesses need enhanced security
        if business.trade_category == TradeCategory.COMMERCIAL:
            return "ENHANCED"
        
        # Security system businesses need enterprise security
        if "security" in business.get_primary_trade().lower():
            return "ENTERPRISE"
        
        # Default to basic security
        return "BASIC"
    
    def _determine_performance_tier(self, business: Business, traffic_requirements: Dict[str, int]) -> str:
        """Determine performance tier based on business needs and traffic."""
        
        monthly_visitors = traffic_requirements["monthly_visitors"]
        
        # High traffic businesses need premium performance
        if monthly_visitors > 50000:
            return "PREMIUM"
        
        # Medium traffic or commercial businesses need optimized performance
        if monthly_visitors > 10000 or business.trade_category == TradeCategory.COMMERCIAL:
            return "OPTIMIZED"
        
        # Default to basic performance
        return "BASIC"
    
    def _determine_backup_frequency(self, business: Business) -> str:
        """Determine backup frequency based on business criticality."""
        
        # Emergency services need daily backups
        if self._provides_emergency_services(business):
            return "DAILY"
        
        # Commercial businesses need weekly backups
        if business.trade_category == TradeCategory.COMMERCIAL:
            return "WEEKLY"
        
        # Residential services can use weekly backups
        return "WEEKLY"
    
    def _determine_monitoring_level(self, business: Business, environment: str) -> str:
        """Determine monitoring level based on business needs and environment."""
        
        # Production always needs at least detailed monitoring
        if environment == "production":
            # Emergency services need comprehensive monitoring
            if self._provides_emergency_services(business):
                return "COMPREHENSIVE"
            
            # Commercial businesses need detailed monitoring
            if business.trade_category == TradeCategory.COMMERCIAL:
                return "DETAILED"
            
            return "DETAILED"
        
        # Non-production can use basic monitoring
        return "BASIC"
    
    def _provides_emergency_services(self, business: Business) -> bool:
        """Check if business provides emergency services."""
        
        emergency_trades = ["plumbing", "hvac", "electrical", "security systems", "roofing"]
        return business.get_primary_trade().lower() in emergency_trades
    
    def _get_base_cache_ttls(self, strategy: str) -> Dict[str, int]:
        """Get base TTL values for different caching strategies."""
        
        ttl_strategies = {
            "AGGRESSIVE": {
                "html_ttl_seconds": 86400,  # 24 hours
                "css_ttl_seconds": 604800,  # 7 days
                "js_ttl_seconds": 604800,   # 7 days
                "image_ttl_seconds": 2592000,  # 30 days
                "font_ttl_seconds": 2592000,   # 30 days
                "api_ttl_seconds": 300       # 5 minutes
            },
            "MODERATE": {
                "html_ttl_seconds": 3600,   # 1 hour
                "css_ttl_seconds": 86400,   # 24 hours
                "js_ttl_seconds": 86400,    # 24 hours
                "image_ttl_seconds": 604800,  # 7 days
                "font_ttl_seconds": 604800,   # 7 days
                "api_ttl_seconds": 60        # 1 minute
            },
            "MINIMAL": {
                "html_ttl_seconds": 300,    # 5 minutes
                "css_ttl_seconds": 3600,    # 1 hour
                "js_ttl_seconds": 3600,     # 1 hour
                "image_ttl_seconds": 86400,   # 24 hours
                "font_ttl_seconds": 86400,    # 24 hours
                "api_ttl_seconds": 0         # No caching
            }
        }
        
        return ttl_strategies.get(strategy, ttl_strategies["MODERATE"])
    
    def _estimate_content_update_frequency(self, business: Business) -> str:
        """Estimate how frequently business content is updated."""
        
        # Emergency services may update contact info frequently
        if self._provides_emergency_services(business):
            return "WEEKLY"
        
        # Commercial businesses may update services/pricing more often
        if business.trade_category == TradeCategory.COMMERCIAL:
            return "MONTHLY"
        
        # Residential services typically update less frequently
        return "QUARTERLY"
    
    def _adjust_ttls_for_update_frequency(
        self,
        base_ttls: Dict[str, int],
        update_frequency: str
    ) -> Dict[str, int]:
        """Adjust TTL values based on content update frequency."""
        
        # Adjustment factors
        frequency_factors = {
            "DAILY": 0.1,
            "WEEKLY": 0.3,
            "MONTHLY": 0.7,
            "QUARTERLY": 1.0
        }
        
        factor = frequency_factors.get(update_frequency, 1.0)
        
        # Apply factor to HTML TTL (most likely to change)
        adjusted_ttls = base_ttls.copy()
        adjusted_ttls["html_ttl_seconds"] = int(base_ttls["html_ttl_seconds"] * factor)
        
        return adjusted_ttls
    
    def _determine_invalidation_strategy(self, business: Business) -> str:
        """Determine cache invalidation strategy."""
        
        # Emergency services need immediate invalidation capability
        if self._provides_emergency_services(business):
            return "IMMEDIATE"
        
        # Most businesses can use scheduled invalidation
        return "SCHEDULED"
    
    def _generate_content_security_policy(
        self,
        security_level: str,
        custom_domain: Optional[str]
    ) -> str:
        """Generate Content Security Policy header."""
        
        # Base CSP
        csp_parts = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self'"
        ]
        
        # Add custom domain if provided
        if custom_domain:
            csp_parts[0] = f"default-src 'self' https://{custom_domain}"
        
        # Enhanced security removes unsafe-inline
        if security_level in ["ENHANCED", "ENTERPRISE"]:
            csp_parts[1] = "script-src 'self' https://www.googletagmanager.com"
            csp_parts[2] = "style-src 'self' https://fonts.googleapis.com"
        
        return "; ".join(csp_parts)
    
    def _determine_referrer_policy(self, business: Business) -> str:
        """Determine referrer policy based on business type."""
        
        # Commercial businesses may want to track referrers
        if business.trade_category == TradeCategory.COMMERCIAL:
            return "strict-origin-when-cross-origin"
        
        # Default to strict policy
        return "strict-origin"
    
    def _generate_permissions_policy(self, business: Business) -> str:
        """Generate Permissions Policy header."""
        
        # Disable unnecessary features for business websites
        policies = [
            "camera=()",
            "microphone=()",
            "geolocation=(self)",  # May be useful for service area detection
            "payment=()"
        ]
        
        return ", ".join(policies)
    
    def _determine_cors_origins(
        self,
        business: Business,
        custom_domain: Optional[str]
    ) -> List[str]:
        """Determine allowed CORS origins."""
        
        origins = ["https://hero365.ai"]
        
        if custom_domain:
            origins.append(f"https://{custom_domain}")
        
        return origins
    
    def _get_compression_types(self, performance_tier: str) -> List[str]:
        """Get file types to compress based on performance tier."""
        
        basic_types = ["text/html", "text/css", "application/javascript"]
        
        if performance_tier in ["OPTIMIZED", "PREMIUM"]:
            return basic_types + [
                "application/json",
                "application/xml",
                "text/xml",
                "image/svg+xml",
                "text/plain"
            ]
        
        return basic_types
    
    def _determine_critical_resources(
        self,
        business: Business,
        website: BusinessWebsite
    ) -> List[str]:
        """Determine critical resources to preload."""
        
        # Always preload critical CSS and fonts
        critical_resources = [
            "/css/main.css",
            "/fonts/primary-font.woff2"
        ]
        
        # Emergency services should preload contact information
        if self._provides_emergency_services(business):
            critical_resources.append("/js/contact.js")
        
        return critical_resources
    
    def _get_dns_prefetch_domains(self, business: Business) -> List[str]:
        """Get domains to DNS prefetch."""
        
        # Common external domains for business websites
        domains = [
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        ]
        
        # Add Google Analytics if tracking is enabled
        domains.append("www.google-analytics.com")
        
        return domains
    
    def _generate_resource_hints(
        self,
        business: Business,
        performance_tier: str
    ) -> Dict[str, List[str]]:
        """Generate resource hints for performance optimization."""
        
        hints = {
            "dns-prefetch": self._get_dns_prefetch_domains(business),
            "preconnect": ["https://fonts.googleapis.com"],
            "prefetch": []
        }
        
        # Premium tier gets more aggressive prefetching
        if performance_tier == "PREMIUM":
            hints["prefetch"] = ["/images/hero-bg.jpg", "/js/analytics.js"]
        
        return hints
    
    def _validate_required_content(
        self,
        website: BusinessWebsite,
        business: Business
    ) -> Dict[str, Any]:
        """Validate that website has required content for deployment."""
        
        missing_content = []
        
        # Check for essential pages (this would be more sophisticated in real implementation)
        required_pages = ["home", "services", "contact"]
        
        # Emergency services must have emergency contact info
        if self._provides_emergency_services(business):
            required_pages.append("emergency")
        
        # For now, assume content is valid (would check actual content in real implementation)
        return {
            "valid": True,
            "missing_content": missing_content,
            "required_pages": required_pages
        }
    
    def _validate_business_information(self, business: Business) -> Dict[str, Any]:
        """Validate business information completeness."""
        
        missing_fields = []
        
        # Check required fields
        if not business.phone_number:
            missing_fields.append("Business phone number")
        
        if not business.business_email:
            missing_fields.append("Business email address")
        
        if not business.address:
            missing_fields.append("Business address")
        
        if not business.service_areas:
            missing_fields.append("Service areas")
        
        return {
            "complete": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }
    
    def _validate_seo_readiness(
        self,
        website: BusinessWebsite,
        business: Business
    ) -> Dict[str, Any]:
        """Validate SEO readiness for deployment."""
        
        # This would integrate with SEO domain service in real implementation
        seo_score = 85  # Placeholder
        
        recommendations = []
        if seo_score < 80:
            recommendations.append("Optimize page titles and meta descriptions")
        if seo_score < 70:
            recommendations.append("Add more location-specific keywords")
        
        return {
            "score": seo_score,
            "recommendations": recommendations
        }
    
    def _validate_performance_readiness(self, website: BusinessWebsite) -> Dict[str, Any]:
        """Validate performance optimization readiness."""
        
        optimizations = []
        
        # Check for common performance issues (placeholder logic)
        optimizations.append("Enable image compression")
        optimizations.append("Minify CSS and JavaScript")
        
        return {
            "optimized": len(optimizations) == 0,
            "optimizations": optimizations
        }
    
    def _estimate_deployment_time(
        self,
        website: BusinessWebsite,
        deployment_config: Dict[str, Any]
    ) -> int:
        """Estimate deployment time in seconds."""
        
        # Base deployment time
        base_time = 60  # 1 minute
        
        # Add time for CDN setup
        if deployment_config.get("enable_cdn", False):
            base_time += 300  # 5 minutes for CDN propagation
        
        # Add time for SSL setup
        if deployment_config.get("enable_ssl", False):
            base_time += 120  # 2 minutes for SSL
        
        return base_time
    
    def _calculate_resource_requirements(
        self,
        website: BusinessWebsite,
        business: Business
    ) -> Dict[str, Any]:
        """Calculate resource requirements for deployment."""
        
        return {
            "storage_gb": self._estimate_website_size(website),
            "bandwidth_gb_monthly": 10,  # Estimated monthly bandwidth
            "cpu_cores": 0,  # Static sites don't need CPU
            "memory_mb": 0,  # Static sites don't need memory
            "concurrent_connections": 1000  # Estimated concurrent visitors
        }
    
    def _estimate_website_size(self, website: BusinessWebsite) -> float:
        """Estimate website size in GB."""
        
        # Typical Hero365 website size estimate
        base_size_mb = 5  # 5MB for typical business website
        
        # Add size for images (estimated)
        image_size_mb = 10  # 10MB for business images
        
        total_size_mb = base_size_mb + image_size_mb
        return total_size_mb / 1024  # Convert to GB
