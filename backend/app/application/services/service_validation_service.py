"""
Service Validation Service

Validates that businesses have actual services configured before generating 
website content. Ensures dynamic websites are only generated for businesses 
with proper service catalogs.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from ...infrastructure.database.repositories.supabase_service_template_repository import (
    SupabaseServiceCategoryRepository,
    SupabaseBusinessServiceRepository
)
from ...domain.entities.business import Business
from ...core.db import get_supabase_client

logger = logging.getLogger(__name__)


class ServiceValidationResult:
    """Result of service validation for a business."""
    
    def __init__(
        self, 
        business_id: UUID, 
        is_valid: bool, 
        total_services: int,
        total_categories: int,
        issues: List[str] = None
    ):
        self.business_id = business_id
        self.is_valid = is_valid
        self.total_services = total_services
        self.total_categories = total_categories
        self.issues = issues or []
        
    def has_sufficient_services(self, min_services: int = 1) -> bool:
        """Check if business has minimum required services."""
        return self.total_services >= min_services
        
    def has_multiple_categories(self) -> bool:
        """Check if business has services across multiple categories."""
        return self.total_categories >= 2
        
    def get_recommendation(self) -> str:
        """Get recommendation based on validation result."""
        if not self.is_valid:
            return "Business needs to configure services before website generation"
        elif self.total_services < 3:
            return "Consider adding more services for better website content"
        elif self.total_categories < 2:
            return "Consider adding services in additional categories for richer navigation"
        else:
            return "Business is ready for comprehensive website generation"


class ServiceValidationService:
    """
    Service that validates business service configurations and provides
    recommendations for website generation readiness.
    """
    
    def __init__(self):
        self.supabase_client = get_supabase_client()
        self.category_repo = SupabaseServiceCategoryRepository(self.supabase_client)
        self.business_service_repo = SupabaseBusinessServiceRepository(self.supabase_client)
        
    async def validate_business_services(
        self, 
        business: Business,
        min_services_required: int = 1
    ) -> ServiceValidationResult:
        """
        Validate that a business has sufficient services configured
        for website generation.
        """
        
        logger.info(f"Validating services for business: {business.name}")
        
        try:
            issues = []
            
            # Get all service categories with services for this business
            categories_with_services = await self.category_repo.get_categories_with_services(
                business_id=business.id,
                trade_types=None
            )
            
            # Count total services across all categories
            total_services = 0
            active_categories = 0
            
            for category in categories_with_services:
                if hasattr(category, 'services') and category.services:
                    category_service_count = len(category.services)
                    total_services += category_service_count
                    active_categories += 1
                    logger.info(f"Category {category.name}: {category_service_count} services")
            
            # Validation checks
            is_valid = True
            
            if total_services == 0:
                is_valid = False
                issues.append("No services configured for this business")
            elif total_services < min_services_required:
                is_valid = False
                issues.append(f"Business has {total_services} services but requires at least {min_services_required}")
                
            if active_categories == 0:
                is_valid = False
                issues.append("No service categories with services found")
                
            # Additional checks for website quality
            if active_categories == 1 and total_services < 3:
                issues.append("Single category with few services may result in limited website content")
                
            if total_services > 0:
                # Check service completeness
                incomplete_services = await self._check_service_completeness(business.id)
                if incomplete_services:
                    issues.extend(incomplete_services)
                    
            result = ServiceValidationResult(
                business_id=business.id,
                is_valid=is_valid,
                total_services=total_services,
                total_categories=active_categories,
                issues=issues
            )
            
            logger.info(f"Validation result for {business.name}: Valid={is_valid}, Services={total_services}, Categories={active_categories}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating services for business {business.name}: {str(e)}")
            return ServiceValidationResult(
                business_id=business.id,
                is_valid=False,
                total_services=0,
                total_categories=0,
                issues=[f"Validation error: {str(e)}"]
            )
    
    async def _check_service_completeness(self, business_id: UUID) -> List[str]:
        """Check for incomplete service configurations."""
        
        issues = []
        
        try:
            # Get all business services
            business_services = await self.business_service_repo.list_business_services(
                business_id=business_id,
                is_active=True
            )
            
            services_without_price = 0
            services_without_description = 0
            
            for service in business_services:
                if not service.unit_price or service.unit_price <= 0:
                    services_without_price += 1
                    
                if not service.description or len(service.description.strip()) < 10:
                    services_without_description += 1
            
            if services_without_price > 0:
                issues.append(f"{services_without_price} services missing pricing information")
                
            if services_without_description > 0:
                issues.append(f"{services_without_description} services missing proper descriptions")
                
        except Exception as e:
            logger.error(f"Error checking service completeness: {str(e)}")
            issues.append("Unable to validate service completeness")
            
        return issues
    
    async def get_website_generation_readiness(
        self, 
        business: Business
    ) -> Dict[str, Any]:
        """
        Get comprehensive readiness assessment for website generation.
        """
        
        validation_result = await self.validate_business_services(business)
        
        # Determine readiness level
        readiness_level = "not_ready"
        if validation_result.is_valid:
            if validation_result.total_services >= 5 and validation_result.total_categories >= 2:
                readiness_level = "excellent"
            elif validation_result.total_services >= 3:
                readiness_level = "good"
            else:
                readiness_level = "basic"
        
        # Generate recommendations
        recommendations = []
        if not validation_result.is_valid:
            recommendations.append("Add at least one service to enable website generation")
            
        if validation_result.total_categories < 2:
            recommendations.append("Add services in multiple categories for better navigation")
            
        if validation_result.total_services < 5:
            recommendations.append("Add more services to showcase your full capabilities")
            
        # Website features available based on readiness
        available_features = []
        if validation_result.is_valid:
            available_features.extend([
                "Basic website generation",
                "Contact forms",
                "Business information pages"
            ])
            
        if validation_result.total_categories >= 2:
            available_features.extend([
                "Multi-category navigation",
                "Category-specific pages",
                "Service comparison"
            ])
            
        if validation_result.total_services >= 5:
            available_features.extend([
                "Comprehensive service showcase",
                "Featured service highlighting",
                "Professional credibility display"
            ])
        
        return {
            "business_id": str(business.id),
            "business_name": business.name,
            "readiness_level": readiness_level,
            "is_ready_for_generation": validation_result.is_valid,
            "total_services": validation_result.total_services,
            "total_categories": validation_result.total_categories,
            "issues": validation_result.issues,
            "recommendations": recommendations,
            "available_features": available_features,
            "overall_recommendation": validation_result.get_recommendation()
        }
    
    async def get_businesses_ready_for_websites(
        self, 
        business_ids: List[UUID]
    ) -> List[Dict[str, Any]]:
        """
        Get list of businesses that are ready for website generation.
        """
        
        ready_businesses = []
        
        for business_id in business_ids:
            try:
                # This would require getting the business entity
                # For now, just validate the services
                validation_result = ServiceValidationResult(
                    business_id=business_id,
                    is_valid=False,
                    total_services=0,
                    total_categories=0
                )
                
                if validation_result.is_valid:
                    ready_businesses.append({
                        "business_id": str(business_id),
                        "total_services": validation_result.total_services,
                        "total_categories": validation_result.total_categories
                    })
                    
            except Exception as e:
                logger.error(f"Error checking business {business_id}: {str(e)}")
                continue
                
        return ready_businesses
