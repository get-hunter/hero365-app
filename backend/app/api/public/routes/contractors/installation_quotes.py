"""
Installation Quote Endpoints

Fast pricing quotes optimized for home service contractors.
Supports both fixed-price templates (80% of jobs) and hourly rates (20% of jobs).
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from decimal import Decimal
import logging

from app.application.services.product_install_pricing_service import (
    ProductInstallPricingEngine, ProductInfo, MembershipType
)
from app.application.services.installation_templates import ComplexityLevel
from app.application.services.product_service import ProductService
from app.infrastructure.config.dependency_injection import (
    get_product_repository,
    get_business_repository,
    get_customer_membership_repository
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class QuickQuoteRequest(BaseModel):
    """Request for a quick installation quote"""
    business_id: str = Field(..., description="Business ID")
    product_id: str = Field(..., description="Product ID")
    installation_type: str = Field(default="standard", description="Type of installation")
    complexity: str = Field(default="standard", description="Job complexity: simple, standard, complex, custom")
    timing: str = Field(default="business_hours", description="Service timing: business_hours, evening, weekend, emergency")
    location: str = Field(default="local", description="Service location: local, regional, distant")
    membership_type: Optional[str] = Field(None, description="Customer membership: residential, commercial, premium")
    quantity: int = Field(default=1, description="Number of units")

class QuickQuoteResponse(BaseModel):
    """Response with installation quote"""
    success: bool
    quote: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    recommendations: Optional[Dict[str, Any]] = None


def get_product_service():
    """Get product service with proper dependency injection."""
    product_repo = get_product_repository()
    business_repo = get_business_repository()
    membership_repo = get_customer_membership_repository()
    return ProductService(product_repo, business_repo, membership_repo)


def get_pricing_engine() -> ProductInstallPricingEngine:
    """Get the pricing engine instance"""
    return ProductInstallPricingEngine()


@router.post("/quick-quote", response_model=QuickQuoteResponse)
async def get_quick_installation_quote(
    request: QuickQuoteRequest,
    pricing_engine: ProductInstallPricingEngine = Depends(get_pricing_engine),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get a quick installation quote for phone calls
    
    Perfect for contractors who need to give instant pricing to customers:
    - Water heater replacement: $250 + product cost
    - Thermostat installation: $125 + product cost  
    - AC repair: $150 + parts
    
    Includes smart adjustments for complexity, timing, and location.
    """
    try:
        # Get product information
        product_entity = await product_service.get_product_by_id(
            request.business_id, request.product_id
        )
        if not product_entity:
            return QuickQuoteResponse(
                success=False,
                error=f"Product not found: {request.product_id}"
            )
        
        # Convert to ProductInfo for pricing engine (fix Decimal/float mismatch)
        product_info = ProductInfo(
            id=str(product_entity.id),
            name=product_entity.name,
            sku=product_entity.sku or "",
            unit_price=Decimal(str(product_entity.unit_price)),  # Ensure Decimal type
            cost_price=Decimal(str(getattr(product_entity, 'cost_price', 0))) if getattr(product_entity, 'cost_price', None) else None,
            requires_professional_install=True,  # Assume professional installation
            install_complexity=request.complexity
        )
        
        # Parse enum values
        complexity_level = ComplexityLevel(request.complexity)
        membership_type = MembershipType(request.membership_type) if request.membership_type else None
        
        # Get quick quote
        quote_result = pricing_engine.get_quick_installation_quote(
            product=product_info,
            installation_type=request.installation_type,
            complexity=complexity_level,
            timing=request.timing,
            location=request.location,
            membership_type=membership_type
        )
        
        if "error" in quote_result:
            return QuickQuoteResponse(
                success=False,
                error=quote_result["error"],
                recommendations={"available_templates": quote_result.get("available_templates", [])}
            )
        
        return QuickQuoteResponse(
            success=True,
            quote=quote_result
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating quick quote: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate quote")


@router.get("/templates/{business_id}")
async def get_available_templates(
    business_id: str = Path(..., description="Business ID"),
    trade_type: Optional[str] = Query(None, description="Filter by trade type: hvac, plumbing, electrical"),
    product_service: ProductService = Depends(get_product_service),
    pricing_engine: ProductInstallPricingEngine = Depends(get_pricing_engine)
):
    """
    Get available installation templates for a business
    
    Shows all the fixed-price installation options available:
    - Water heater replacement: $250
    - Thermostat installation: $125
    - Standard AC repair: $150
    - Plus hourly rates for diagnostic and custom work
    """
    try:
        # Get all templates
        templates = pricing_engine.templates
        
        # Filter by trade type if specified
        if trade_type:
            from app.application.services.installation_templates import TradeType
            trade_filter = TradeType(trade_type)
            templates = {
                template_id: template 
                for template_id, template in templates.items()
                if template.trade_type == trade_filter
            }
        
        # Format response
        template_list = []
        for template_id, template in templates.items():
            template_list.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "trade_type": template.trade_type.value,
                "installation_type": template.installation_type.value,
                "base_price": float(template.base_price),
                "estimated_hours": float(template.estimated_hours),
                "hourly_equivalent": float(template.hourly_equivalent),
                "includes": template.includes,
                "materials_included": template.materials_included,
                "warranty_years": template.warranty_years,
                "requires_permit": template.requires_permit
            })
        
        return {
            "business_id": business_id,
            "total_templates": len(template_list),
            "templates": template_list,
            "usage_guide": {
                "fixed_price": "80% of jobs - instant phone quotes",
                "hourly": "20% of jobs - complex/diagnostic work",
                "membership_discounts": "10-20% off labor costs"
            }
        }
        
    except ValueError as e:
        logger.warning(f"Invalid trade type: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid trade type: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")


@router.get("/pricing-demo/{business_id}/{product_id}")
async def pricing_demo(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID"),
    product_service: ProductService = Depends(get_product_service),
    pricing_engine: ProductInstallPricingEngine = Depends(get_pricing_engine)
):
    """
    Demo endpoint showing pricing for different scenarios
    
    Perfect for testing the new pricing system with real examples:
    - Standard pricing vs. complex job pricing
    - Business hours vs. emergency pricing
    - Member vs. non-member pricing
    """
    try:
        # Get product
        product_entity = await product_service.get_product_by_id(business_id, product_id)
        if not product_entity:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_info = ProductInfo(
            id=str(product_entity.id),
            name=product_entity.name,
            sku=product_entity.sku or "",
            unit_price=product_entity.unit_price,
            requires_professional_install=True
        )
        
        # Generate quotes for different scenarios
        scenarios = []
        
        # Scenario 1: Standard installation, business hours, no membership
        standard_quote = pricing_engine.get_quick_installation_quote(
            product=product_info,
            complexity=ComplexityLevel.STANDARD,
            timing="business_hours",
            location="local"
        )
        scenarios.append({
            "scenario": "Standard Installation",
            "description": "Normal business hours, standard complexity, no membership",
            "quote": standard_quote
        })
        
        # Scenario 2: Emergency installation, weekend
        emergency_quote = pricing_engine.get_quick_installation_quote(
            product=product_info,
            complexity=ComplexityLevel.STANDARD,
            timing="emergency",
            location="local"
        )
        scenarios.append({
            "scenario": "Emergency Service",
            "description": "Emergency call, weekend, standard complexity",
            "quote": emergency_quote
        })
        
        # Scenario 3: Complex installation with residential membership
        complex_member_quote = pricing_engine.get_quick_installation_quote(
            product=product_info,
            complexity=ComplexityLevel.COMPLEX,
            timing="business_hours",
            location="local",
            membership_type=MembershipType.RESIDENTIAL
        )
        scenarios.append({
            "scenario": "Complex Job with Membership",
            "description": "Complex installation, residential member savings",
            "quote": complex_member_quote
        })
        
        return {
            "product_name": product_entity.name,
            "product_price": float(product_entity.unit_price),
            "scenarios": scenarios,
            "pricing_summary": {
                "model": "Hybrid: 80% fixed price + 20% hourly",
                "target_users": "Home service contractors needing fast quotes",
                "key_benefit": "Instant phone quotes that close more deals"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating pricing demo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")
