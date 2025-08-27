"""
Contractor Products API Routes

Public endpoints for retrieving contractor products and catalog.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
import logging
import uuid

from .....infrastructure.config.dependency_injection import get_product_repository as get_product_repo_func
from .....domain.repositories.product_repository import ProductRepository
from .schemas import ProductItem, ProductCategory, ProductCatalogItem, PricingBreakdown

logger = logging.getLogger(__name__)

router = APIRouter()


def get_product_repository() -> ProductRepository:
    """Get product repository instance."""
    return get_product_repo_func()


@router.get("/products/{business_id}", response_model=List[ProductItem])
async def get_contractor_products(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    in_stock_only: bool = Query(True, description="Show only in-stock products"),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """
    Get contractor products sold by a business.
    
    Returns list of products with pricing and availability information.
    """
    
    try:
        # Try to fetch products from database
        products = await product_repo.list_by_business(uuid.UUID(business_id))
        
        if products:
            # Convert product entities to response models
            product_items = []
            for product in products:
                # Only include actual products, not services
                if hasattr(product, 'product_type') and str(product.product_type) == 'service':
                    continue
                    
                if in_stock_only and not product.is_active():
                    continue
                
                if category and product.category_id != category:
                    continue
                
                product_data = {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description or "",
                    "category": "General",  # TODO: Get category name from category_id
                    "brand": "Professional Brand",  # TODO: Add brand field to product entity
                    "model": "",  # TODO: Add model field to product entity
                    "sku": product.sku or "",
                    "price": float(product.unit_price),
                    "msrp": None,  # TODO: Add MSRP field to product entity
                    "in_stock": product.is_active(),
                    "stock_quantity": int(product.quantity_on_hand) if product.quantity_on_hand else 0,
                    "specifications": {},  # TODO: Add specifications field
                    "warranty_years": None,  # TODO: Add warranty field
                    "energy_rating": None  # TODO: Add energy rating field
                }
                
                product_items.append(ProductItem(**product_data))
            
            return product_items
        
        # No products found in database
        return []
        
    except Exception as e:
        logger.error(f"Error fetching products for {business_id}: {str(e)}")
        return []


@router.get("/product-catalog/{business_id}", response_model=List[ProductCatalogItem])
async def get_product_catalog(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search products by name or description"),
    featured_only: bool = Query(False, description="Show only featured products"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get product catalog with installation options for e-commerce display.
    
    Returns products that are available for website display with their installation options
    and pricing information for different membership tiers.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Build query for products
        query = supabase.table("products").select(
            """
            id, name, sku, description, long_description, unit_price,
            category_id, warranty_years, energy_efficiency_rating,
            requires_professional_install, install_complexity, installation_time_estimate,
            featured_image_url, gallery_images, product_highlights, technical_specs,
            meta_title, meta_description, slug, is_active, is_featured, current_stock
            """
        ).eq("business_id", business_id).eq("show_on_website", True).eq("is_active", True)
        
        # Apply filters
        if featured_only:
            query = query.eq("is_featured", True)
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        # Apply pagination  
        query = query.range(offset, offset + limit - 1).order("name")
        
        products_result = query.execute()
        
        if not products_result.data:
            return []
        
        # Get categories for these products
        category_ids = [p["category_id"] for p in products_result.data if p.get("category_id")]
        categories_by_id = {}
        
        if category_ids:
            categories_query = supabase.table("product_categories").select("id, name").in_("id", category_ids)
            categories_result = categories_query.execute()
            categories_by_id = {cat["id"]: cat["name"] for cat in categories_result.data or []}
        
        # Apply category filter if specified
        if category:
            filtered_products = []
            for product in products_result.data:
                category_name = categories_by_id.get(product.get("category_id"))
                if category_name == category:
                    filtered_products.append(product)
            products_result.data = filtered_products
        
        if not products_result.data:
            return []
        
        # Get installation options for these products
        product_ids = [p["id"] for p in products_result.data]
        
        install_options_query = supabase.table("product_installation_options").select(
            """
            id, product_id, option_name, description, base_install_price,
            residential_install_price, commercial_install_price, premium_install_price,
            estimated_duration_hours, complexity_multiplier, is_default,
            requirements, included_in_install
            """
        ).in_("product_id", product_ids).eq("is_active", True).order("product_id")
        
        install_options_result = install_options_query.execute()
        
        # Group installation options by product_id
        install_options_by_product = {}
        for option in install_options_result.data or []:
            product_id = option["product_id"]
            if product_id not in install_options_by_product:
                install_options_by_product[product_id] = []
            install_options_by_product[product_id].append(option)
        
        # Convert to response models
        catalog_items = []
        for product in products_result.data:
            # Get category name
            category_name = categories_by_id.get(product.get("category_id"))
            
            # Get installation options for this product
            product_install_options = install_options_by_product.get(product["id"], [])
            
            # Convert installation options
            from .schemas import ProductInstallationOption
            installation_options = []
            for option in product_install_options:
                installation_option = ProductInstallationOption(
                    id=str(option["id"]),
                    option_name=option["option_name"],
                    description=option.get("description"),
                    base_install_price=float(option["base_install_price"]),
                    residential_install_price=float(option["residential_install_price"]) if option.get("residential_install_price") else None,
                    commercial_install_price=float(option["commercial_install_price"]) if option.get("commercial_install_price") else None,
                    premium_install_price=float(option["premium_install_price"]) if option.get("premium_install_price") else None,
                    estimated_duration_hours=float(option["estimated_duration_hours"]) if option.get("estimated_duration_hours") else None,
                    complexity_multiplier=float(option.get("complexity_multiplier", 1.0)),
                    is_default=option.get("is_default", False),
                    requirements=option.get("requirements", {}),
                    included_in_install=option.get("included_in_install", [])
                )
                installation_options.append(installation_option)
            
            # Create catalog item
            catalog_item = ProductCatalogItem(
                id=str(product["id"]),
                name=product["name"],
                sku=product["sku"],
                description=product.get("description"),
                long_description=product.get("long_description"),
                unit_price=float(product["unit_price"]),
                category_name=category_name,
                warranty_years=product.get("warranty_years"),
                energy_efficiency_rating=product.get("energy_efficiency_rating"),
                requires_professional_install=product.get("requires_professional_install", False),
                install_complexity=product.get("install_complexity", "standard"),
                installation_time_estimate=product.get("installation_time_estimate"),
                featured_image_url=product.get("featured_image_url"),
                gallery_images=product.get("gallery_images", []),
                product_highlights=product.get("product_highlights", []),
                technical_specs=product.get("technical_specs", {}),
                meta_title=product.get("meta_title"),
                meta_description=product.get("meta_description"),
                slug=product.get("slug"),
                is_active=product.get("is_active", True),
                is_featured=product.get("is_featured", False),
                current_stock=float(product["current_stock"]) if product.get("current_stock") else None,
                installation_options=installation_options
            )
            
            catalog_items.append(catalog_item)
        
        return catalog_items
        
    except Exception as e:
        logger.error(f"Error fetching product catalog for {business_id}: {str(e)}")
        return []


@router.get("/debug-products/{business_id}")
async def debug_products(business_id: str = Path(..., description="Business ID")):
    """Debug endpoint to check raw product data"""
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Simple query to get all products for this business
        query = supabase.table("products").select("*").eq("business_id", business_id)
        result = query.execute()
        
        # Also check total products in database (all businesses)
        all_products_query = supabase.table("products").select("business_id, name, sku").limit(10)
        all_products_result = all_products_query.execute()
        
        debug_info = {
            "total_products_for_business": len(result.data) if result.data else 0,
            "products_with_website_flag": len([p for p in result.data if p.get("show_on_website")]) if result.data else 0,
            "products_active": len([p for p in result.data if p.get("is_active")]) if result.data else 0,
            "sample_product": result.data[0] if result.data else None,
            "total_products_in_database": len(all_products_result.data) if all_products_result.data else 0,
            "all_products_sample": all_products_result.data[:3] if all_products_result.data else []
        }
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/product-categories/{business_id}", response_model=List[ProductCategory])
async def get_product_categories(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get product categories for a business.
    
    Returns list of product categories with product counts for navigation.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get categories with product counts
        query = supabase.table("product_categories").select(
            "id, name, description, sort_order, active_product_count"
        ).eq("business_id", business_id).eq("is_active", True).order("sort_order").order("name")
        
        result = query.execute()
        
        if not result.data:
            return []
        
        categories = []
        for category in result.data:
            categories.append(ProductCategory(
                id=str(category["id"]),
                name=category["name"],
                description=category.get("description"),
                product_count=category.get("active_product_count", 0),
                sort_order=category.get("sort_order", 0)
            ))
        
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching product categories for {business_id}: {str(e)}")
        return []


@router.get("/product/{business_id}/{product_id}", response_model=ProductCatalogItem)
async def get_product_details(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID")
):
    """
    Get detailed product information with installation options.
    
    Returns complete product details for product detail page display.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get product details
        product_query = supabase.table("products").select(
            """
            id, name, sku, description, long_description, unit_price,
            category_id, warranty_years, energy_efficiency_rating,
            requires_professional_install, install_complexity, installation_time_estimate,
            featured_image_url, gallery_images, product_highlights, technical_specs,
            installation_requirements, meta_title, meta_description, slug,
            is_active, is_featured, current_stock,
            product_categories(id, name)
            """
        ).eq("business_id", business_id).eq("id", product_id).eq("show_on_website", True).eq("is_active", True)
        
        product_result = product_query.execute()
        
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = product_result.data[0]
        
        # Get installation options
        install_options_query = supabase.table("product_installation_options").select(
            """
            id, option_name, description, base_install_price,
            residential_install_price, commercial_install_price, premium_install_price,
            estimated_duration_hours, complexity_multiplier, is_default,
            requirements, included_in_install
            """
        ).eq("product_id", product_id).eq("is_active", True).order("sort_order").order("option_name")
        
        install_options_result = install_options_query.execute()
        
        # Convert installation options
        from .schemas import ProductInstallationOption
        installation_options = []
        for option in install_options_result.data or []:
            installation_option = ProductInstallationOption(
                id=str(option["id"]),
                option_name=option["option_name"],
                description=option.get("description"),
                base_install_price=float(option["base_install_price"]),
                residential_install_price=float(option["residential_install_price"]) if option.get("residential_install_price") else None,
                commercial_install_price=float(option["commercial_install_price"]) if option.get("commercial_install_price") else None,
                premium_install_price=float(option["premium_install_price"]) if option.get("premium_install_price") else None,
                estimated_duration_hours=float(option["estimated_duration_hours"]) if option.get("estimated_duration_hours") else None,
                complexity_multiplier=float(option.get("complexity_multiplier", 1.0)),
                is_default=option.get("is_default", False),
                requirements=option.get("requirements", {}),
                included_in_install=option.get("included_in_install", [])
            )
            installation_options.append(installation_option)
        
        # Get category info
        category_info = product.get("product_categories", {})
        category_name = category_info.get("name") if category_info else None
        
        # Create detailed product response
        product_detail = ProductCatalogItem(
            id=str(product["id"]),
            name=product["name"],
            sku=product["sku"],
            description=product.get("description"),
            long_description=product.get("long_description"),
            unit_price=float(product["unit_price"]),
            category_name=category_name,
            warranty_years=product.get("warranty_years"),
            energy_efficiency_rating=product.get("energy_efficiency_rating"),
            requires_professional_install=product.get("requires_professional_install", False),
            install_complexity=product.get("install_complexity", "standard"),
            installation_time_estimate=product.get("installation_time_estimate"),
            featured_image_url=product.get("featured_image_url"),
            gallery_images=product.get("gallery_images", []),
            product_highlights=product.get("product_highlights", []),
            technical_specs=product.get("technical_specs", {}),
            meta_title=product.get("meta_title"),
            meta_description=product.get("meta_description"),
            slug=product.get("slug"),
            is_active=product.get("is_active", True),
            is_featured=product.get("is_featured", False),
            current_stock=float(product["current_stock"]) if product.get("current_stock") else None,
            installation_options=installation_options
        )
        
        return product_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details for {business_id}/{product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch product details")


@router.post("/product-pricing/{business_id}/{product_id}", response_model=PricingBreakdown)
async def calculate_product_pricing(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID"),
    installation_option_id: Optional[str] = Query(None, description="Installation option ID"),
    quantity: int = Query(1, ge=1, le=100, description="Quantity"),
    membership_type: Optional[str] = Query(None, description="Membership type (residential, commercial, premium)")
):
    """
    Calculate detailed pricing for product + installation combination.
    
    Returns comprehensive pricing breakdown including membership discounts,
    bundle savings, tax calculations, and formatted display pricing.
    """
    
    try:
        from .....core.db import get_supabase_client
        from .....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption, MembershipType
        )
        from decimal import Decimal
        
        supabase = get_supabase_client()
        
        # Get product information
        product_query = supabase.table("products").select(
            """
            id, name, sku, unit_price, cost_price, requires_professional_install,
            install_complexity, warranty_years, is_taxable, tax_rate
            """
        ).eq("business_id", business_id).eq("id", product_id).eq("show_on_website", True).eq("is_active", True)
        
        product_result = product_query.execute()
        
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product_result.data[0]
        
        # Create ProductInfo object
        product_info = ProductInfo(
            id=str(product_data["id"]),
            name=product_data["name"],
            sku=product_data["sku"],
            unit_price=Decimal(str(product_data["unit_price"])),
            cost_price=Decimal(str(product_data["cost_price"])) if product_data.get("cost_price") else None,
            requires_professional_install=product_data.get("requires_professional_install", False),
            install_complexity=product_data.get("install_complexity", "standard"),
            warranty_years=product_data.get("warranty_years", 1),
            is_taxable=product_data.get("is_taxable", True),
            tax_rate=Decimal(str(product_data["tax_rate"])) if product_data.get("tax_rate") else None
        )
        
        # Default installation option if none specified
        install_option = None
        
        if installation_option_id:
            # Get specific installation option
            install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("id", installation_option_id).eq("product_id", product_id).eq("is_active", True)
            
            install_result = install_query.execute()
            
            if install_result.data:
                install_data = install_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    description=install_data.get("description", ""),
                    base_install_price=Decimal(str(install_data["base_install_price"])),
                    complexity_multiplier=Decimal(str(install_data.get("complexity_multiplier", 1.0))),
                    estimated_duration_hours=Decimal(str(install_data.get("estimated_duration_hours", 2.0))),
                    residential_install_price=Decimal(str(install_data["residential_install_price"])) if install_data.get("residential_install_price") else None,
                    commercial_install_price=Decimal(str(install_data["commercial_install_price"])) if install_data.get("commercial_install_price") else None,
                    premium_install_price=Decimal(str(install_data["premium_install_price"])) if install_data.get("premium_install_price") else None,
                    requirements=install_data.get("requirements", {}),
                    included_in_install=install_data.get("included_in_install", [])
                )
        
        # If no installation option but product requires installation, get default
        if not install_option and product_info.requires_professional_install:
            default_install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("product_id", product_id).eq("is_default", True).eq("is_active", True)
            
            default_result = default_install_query.execute()
            
            if default_result.data:
                install_data = default_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    description=install_data.get("description", ""),
                    base_install_price=Decimal(str(install_data["base_install_price"])),
                    complexity_multiplier=Decimal(str(install_data.get("complexity_multiplier", 1.0))),
                    estimated_duration_hours=Decimal(str(install_data.get("estimated_duration_hours", 2.0))),
                    residential_install_price=Decimal(str(install_data["residential_install_price"])) if install_data.get("residential_install_price") else None,
                    commercial_install_price=Decimal(str(install_data["commercial_install_price"])) if install_data.get("commercial_install_price") else None,
                    premium_install_price=Decimal(str(install_data["premium_install_price"])) if install_data.get("premium_install_price") else None,
                    requirements=install_data.get("requirements", {}),
                    included_in_install=install_data.get("included_in_install", [])
                )
        
        # Create default installation option if none found
        if not install_option:
            install_option = InstallationOption(
                id="default",
                option_name="No Installation",
                description="Product only, no installation included",
                base_install_price=Decimal('0')
            )
        
        # Parse membership type
        membership = None
        if membership_type:
            try:
                membership = MembershipType(membership_type)
            except ValueError:
                pass  # Invalid membership type, proceed without membership
        
        # Calculate pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, quantity, membership
        )
        
        # Convert to response model
        pricing_breakdown = PricingBreakdown(
            product_unit_price=float(calculation.product_unit_price),
            installation_base_price=float(calculation.installation_base_price),
            quantity=calculation.quantity,
            product_subtotal=float(calculation.product_subtotal),
            installation_subtotal=float(calculation.installation_subtotal),
            subtotal_before_discounts=float(calculation.subtotal_before_discounts),
            membership_type=calculation.membership_type.value if calculation.membership_type else None,
            product_discount_amount=float(calculation.product_discount_amount),
            installation_discount_amount=float(calculation.installation_discount_amount),
            total_discount_amount=float(calculation.total_discount_amount),
            bundle_savings=float(calculation.bundle_savings),
            subtotal_after_discounts=float(calculation.subtotal_after_discounts),
            tax_rate=float(calculation.tax_rate),
            tax_amount=float(calculation.tax_amount),
            total_amount=float(calculation.total_amount),
            total_savings=float(calculation.total_savings),
            savings_percentage=float(calculation.savings_percentage),
            formatted_display_price=calculation.formatted_display_price,
            price_display_type=calculation.price_display_type.value
        )
        
        return pricing_breakdown
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating pricing for {business_id}/{product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate pricing")
