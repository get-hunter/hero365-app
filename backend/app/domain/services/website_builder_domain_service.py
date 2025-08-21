"""
Website Builder Domain Service

Pure business logic for website building without external dependencies.
Contains core business rules and domain logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..entities.business import Business
from ..entities.business_branding import BusinessBranding  
from ..entities.website import BusinessWebsite, WebsiteTemplate, WebsiteStatus


class WebsiteBuilderDomainService:
    """
    Domain service containing pure business logic for website building.
    
    This service contains NO external dependencies - only business rules.
    """
    
    def validate_website_creation(
        self,
        business: Business,
        template: WebsiteTemplate,
        subdomain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate if a website can be created for this business."""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Business validation
        if not business.get_all_trades():
            validation_result["valid"] = False
            validation_result["errors"].append("Business must have at least one trade specified")
        
        # Template compatibility
        if template.trade_category != business.trade_category:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Template category {template.trade_category} doesn't match business category {business.trade_category}")
        
        if template.trade_type not in business.get_all_trades():
            validation_result["warnings"].append(f"Template trade {template.trade_type} not in business trades")
        
        # Subdomain validation
        if subdomain:
            if not self._is_valid_subdomain(subdomain):
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid subdomain format")
        
        return validation_result
    
    def calculate_build_priority(
        self,
        business: Business,
        website: BusinessWebsite,
        is_emergency: bool = False
    ) -> int:
        """Calculate build priority (1-10, higher = more urgent)."""
        
        priority = 5  # Base priority
        
        # Emergency builds get highest priority
        if is_emergency:
            priority = 10
        
        # New businesses get higher priority
        if not hasattr(business, 'existing_websites_count') or business.existing_websites_count == 0:
            priority += 2
        
        # Commercial businesses get slightly higher priority
        if business.trade_category.value == "commercial":
            priority += 1
        
        # Certain trades get priority (emergency services)
        emergency_trades = ["plumbing", "hvac", "electrical"]
        if business.get_primary_trade() in emergency_trades:
            priority += 1
        
        return min(10, priority)
    
    def determine_required_pages(
        self,
        business: Business,
        template: WebsiteTemplate
    ) -> List[str]:
        """Determine which pages are required for this business."""
        
        required_pages = ["home", "services", "contact"]
        
        # Add trade-specific pages
        primary_trade = business.get_primary_trade()
        
        if primary_trade in ["plumbing", "hvac", "electrical"]:
            required_pages.append("emergency")
        
        if business.trade_category.value == "commercial":
            required_pages.extend(["quote", "projects"])
        else:
            required_pages.append("booking")
        
        # Add pages based on business size
        if business.company_size in ["MEDIUM", "LARGE"]:
            required_pages.extend(["about", "testimonials"])
        
        return required_pages
    
    def calculate_seo_keywords(
        self,
        business: Business,
        template: WebsiteTemplate
    ) -> List[str]:
        """Calculate SEO keywords based on business and template."""
        
        keywords = []
        
        # Base trade keywords
        primary_trade = business.get_primary_trade()
        keywords.extend([
            primary_trade,
            f"{primary_trade} services",
            f"{primary_trade} contractor"
        ])
        
        # Location-based keywords
        for area in business.service_areas[:5]:  # Limit to top 5
            keywords.extend([
                f"{primary_trade} {area}",
                f"{area} {primary_trade}",
                f"{primary_trade} near {area}"
            ])
        
        # Emergency keywords for applicable trades
        emergency_trades = ["plumbing", "hvac", "electrical"]
        if primary_trade in emergency_trades:
            keywords.extend([
                f"emergency {primary_trade}",
                f"24/7 {primary_trade}",
                f"{primary_trade} emergency service"
            ])
        
        # Commercial vs residential keywords
        if business.trade_category.value == "commercial":
            keywords.extend([
                f"commercial {primary_trade}",
                f"business {primary_trade}",
                f"industrial {primary_trade}"
            ])
        else:
            keywords.extend([
                f"residential {primary_trade}",
                f"home {primary_trade}",
                f"{primary_trade} repair"
            ])
        
        return list(set(keywords))  # Remove duplicates
    
    def validate_content_requirements(
        self,
        business: Business,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that content meets business requirements."""
        
        validation = {
            "valid": True,
            "missing_content": [],
            "quality_issues": []
        }
        
        # Required content fields
        required_fields = [
            "business_name",
            "primary_service",
            "contact_phone",
            "service_areas"
        ]
        
        for field in required_fields:
            if field not in content_data or not content_data[field]:
                validation["valid"] = False
                validation["missing_content"].append(field)
        
        # Content quality checks
        if "business_description" in content_data:
            desc = content_data["business_description"]
            if len(desc) < 50:
                validation["quality_issues"].append("Business description too short (minimum 50 characters)")
            if len(desc) > 500:
                validation["quality_issues"].append("Business description too long (maximum 500 characters)")
        
        # Trade-specific content validation
        primary_trade = business.get_primary_trade()
        
        if primary_trade in ["plumbing", "hvac", "electrical"]:
            if "emergency_contact" not in content_data:
                validation["quality_issues"].append("Emergency trades should have emergency contact info")
        
        return validation
    
    def _is_valid_subdomain(self, subdomain: str) -> bool:
        """Validate subdomain format."""
        
        if not subdomain:
            return False
        
        # Basic validation rules
        if len(subdomain) < 3 or len(subdomain) > 50:
            return False
        
        # Must start and end with alphanumeric
        if not subdomain[0].isalnum() or not subdomain[-1].isalnum():
            return False
        
        # Only alphanumeric and hyphens
        if not all(c.isalnum() or c == '-' for c in subdomain):
            return False
        
        # No consecutive hyphens
        if '--' in subdomain:
            return False
        
        return True
