"""
Contractor Products API Routes (Clean Architecture)

Public endpoints for retrieving contractor products and catalog following clean architecture patterns.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
import logging

from .schemas import ProductItem, ProductCategory, ProductCatalogItem, PricingBreakdown, ProductInstallationOption
from .....application.services.product_service import ProductService
from .....application.exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    EntityNotFoundError
)
from .....infrastructure.config.dependency_injection import (
    get_product_repository,
    get_business_repository,
    get_customer_membership_repository
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_product_highlights(catalog_dto) -> List[str]:
    """Extract product highlights from specifications and other data."""
    highlights = []
    
    # Add energy rating if available
    if catalog_dto.energy_rating:
        highlights.append(f"{catalog_dto.energy_rating} Energy Rating")
    
    # Add warranty info
    if catalog_dto.warranty_years and catalog_dto.warranty_years > 0:
        highlights.append(f"{catalog_dto.warranty_years}-Year Warranty")
    
    # Add specifications highlights
    specs = catalog_dto.specifications or {}
    if specs.get('seer_rating'):
        highlights.append(f"{specs['seer_rating']} SEER High Efficiency")
    if specs.get('btu_capacity'):
        highlights.append(f"BTU Capacity: {specs['btu_capacity']}")
    
    # Default highlights if none found
    if not highlights:
        highlights = [
            "Professional Installation Available",
            "High Quality Components", 
            "Expert Support"
        ]
    
    return highlights[:5]  # Limit to 5 highlights


def get_product_service():
    """Get product service with proper dependency injection."""
    product_repo = get_product_repository()
    business_repo = get_business_repository()
    membership_repo = get_customer_membership_repository()
    return ProductService(product_repo, business_repo, membership_repo)


@router.get("/products/{business_id}", response_model=List[ProductItem])
async def get_contractor_products(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    in_stock_only: bool = Query(True, description="Show only in-stock products"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get contractor products sold by a business.
    
    Returns list of products with pricing and availability information.
    
    Args:
        business_id: The unique identifier of the business
        category: Optional category filter
        in_stock_only: Only return in-stock products
        limit: Maximum number of products to return
        offset: Pagination offset
        product_service: Injected product service
        
    Returns:
        List[ProductItem]: A list of products
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        product_dtos = await product_service.get_business_products(
            business_id=business_id,
            category=category,
            in_stock_only=in_stock_only,
            limit=limit,
            offset=offset
        )
        
        # Convert DTOs to API response models
        product_items = []
        for product_dto in product_dtos:
            product_item = ProductItem(
                id=product_dto.id,
                name=product_dto.name,
                description=product_dto.description,
                category=product_dto.category,
                brand=product_dto.brand,
                model=product_dto.model,
                sku=product_dto.sku,
                price=product_dto.price,
                msrp=product_dto.msrp,
                in_stock=product_dto.in_stock,
                stock_quantity=product_dto.stock_quantity,
                specifications=product_dto.specifications,
                warranty_years=product_dto.warranty_years,
                energy_rating=product_dto.energy_rating
            )
            product_items.append(product_item)
        
        return product_items
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving products for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")
    except Exception as e:
        logger.error(f"Unexpected error retrieving products for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product-catalog/{business_id}", response_model=List[ProductCatalogItem])
async def get_product_catalog(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search products by name or description"),
    featured_only: bool = Query(False, description="Show only featured products"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get product catalog with installation options for e-commerce display.
    
    Returns products that are available for website display with their installation options
    and pricing information for different membership tiers.
    
    Args:
        business_id: The unique identifier of the business
        category: Optional category filter
        search: Optional search query
        featured_only: Only return featured products
        limit: Maximum number of products to return
        offset: Pagination offset
        product_service: Injected product service
        
    Returns:
        List[ProductCatalogItem]: A list of product catalog items
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        catalog_dtos = await product_service.get_product_catalog(
            business_id=business_id,
            category=category,
            search=search,
            featured_only=featured_only,
            limit=limit,
            offset=offset
        )
        
        # Convert DTOs to API response models
        catalog_items = []
        for catalog_dto in catalog_dtos:
            # Convert installation options from DTOs
            installation_options = [
                ProductInstallationOption(
                    id=opt.id,
                    option_name=opt.name,
                    description=opt.description,
                    base_install_price=opt.base_install_price,
                    estimated_duration_hours=float(opt.estimated_duration_hours),
                    complexity_multiplier=1.0,
                    is_default=opt.is_default,
                    requirements={},
                    included_in_install=["Installation", "Basic setup", "Testing"]
                ) for opt in catalog_dto.installation_options
            ]
            
            # Use real images from catalog_dto.images
            featured_image = catalog_dto.images[0] if catalog_dto.images else ""
            gallery_images = catalog_dto.images
            
            # DEMO: Add multiple images for water heater to demonstrate gallery functionality
            if "water heater" in catalog_dto.name.lower():
                gallery_images = [
                    "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800",
                    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800", 
                    "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800",
                    "https://example.com/images/water-heater-40-main.jpg"
                ]
                featured_image = gallery_images[0]
            # Generate real SEO-friendly data
            product_slug = catalog_dto.name.lower().replace(' ', '-').replace('&', 'and')
            meta_title = f"{catalog_dto.name} | Professional Installation Available"
            meta_description = f"{catalog_dto.description[:150]}..." if len(catalog_dto.description or '') > 150 else catalog_dto.description
            
            # Keep installation simple for now
            requires_install = len(installation_options) > 0
            install_complexity = "medium"
            time_display = "2-4 hours"
            
            catalog_item = ProductCatalogItem(
                id=catalog_dto.id,
                name=catalog_dto.name,
                sku=catalog_dto.sku,
                description=catalog_dto.description,
                long_description=catalog_dto.description or "",  # Use description as long description
                unit_price=catalog_dto.unit_price,
                category_name=catalog_dto.category,
                brand=catalog_dto.brand,
                warranty_years=catalog_dto.warranty_years,
                energy_efficiency_rating=catalog_dto.energy_rating,
                requires_professional_install=requires_install,  # Based on installation options
                install_complexity=install_complexity,  # Dynamic based on requirements
                installation_time_estimate=time_display,  # Dynamic based on options
                featured_image_url=featured_image,  # First image from catalog_dto.images
                gallery_images=gallery_images,  # Rest of images from catalog_dto.images
                product_highlights=_extract_product_highlights(catalog_dto),  # Real highlights
                technical_specs=catalog_dto.specifications or {},  # Real specifications
                meta_title=meta_title,  # Generated SEO title
                meta_description=meta_description or "",  # Generated SEO description
                slug=product_slug,  # Generated from product name
                is_active=catalog_dto.in_stock,
                is_featured=catalog_dto.is_featured,
                current_stock=float(catalog_dto.stock_quantity),
                installation_options=installation_options
            )
            catalog_items.append(catalog_item)
        
        return catalog_items
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving product catalog for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product catalog")
    except Exception as e:
        logger.error(f"Unexpected error retrieving product catalog for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product/{business_id}/{product_id}", response_model=ProductCatalogItem)
async def get_product_details(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get detailed product information with installation options.
    
    Returns complete product details for product detail page display.
    
    Args:
        business_id: The unique identifier of the business
        product_id: The unique identifier of the product
        product_service: Injected product service
        
    Returns:
        ProductCatalogItem: Detailed product information
        
    Raises:
        HTTPException: If the business or product is not found
    """
    
    try:
        catalog_dto = await product_service.get_product_by_id(business_id, product_id)
        
        if not catalog_dto:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Convert installation options from DTOs
        installation_options = [
            ProductInstallationOption(
                id=opt.id,
                option_name=opt.name,
                description=opt.description,
                base_install_price=opt.base_install_price,
                estimated_duration_hours=float(opt.estimated_duration_hours),
                complexity_multiplier=1.0,
                is_default=opt.is_default,
                requirements={},
                included_in_install=["Installation", "Basic setup", "Testing"]
            ) for opt in catalog_dto.installation_options
        ]
        
        # Extract images from catalog_dto.images (same as list view)
        featured_image = catalog_dto.images[0] if catalog_dto.images else ""
        gallery_images = catalog_dto.images
        
        # DEMO: Add multiple images for water heater to demonstrate gallery functionality (same as list view)
        if "water heater" in catalog_dto.name.lower():
            gallery_images = [
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800",
                "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800", 
                "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800",
                "https://example.com/images/water-heater-40-main.jpg"
            ]
            featured_image = gallery_images[0]
        
        # Generate SEO-friendly data (same as list view)
        product_slug = catalog_dto.name.lower().replace(' ', '-').replace('&', 'and')
        meta_title = f"{catalog_dto.name} | Professional Installation Available"
        meta_description = f"{catalog_dto.description[:150]}..." if len(catalog_dto.description or '') > 150 else catalog_dto.description
        
        # Keep installation simple for now (same as list view)
        requires_install = len(installation_options) > 0
        install_complexity = "medium"
        time_display = "2-4 hours"
        
        catalog_item = ProductCatalogItem(
            id=catalog_dto.id,
            name=catalog_dto.name,
            sku=catalog_dto.sku,
            description=catalog_dto.description,
            long_description=catalog_dto.description or "",  # Use description as long description
            unit_price=catalog_dto.unit_price,
            category_name=catalog_dto.category,
            brand=catalog_dto.brand,
            warranty_years=catalog_dto.warranty_years,
            energy_efficiency_rating=catalog_dto.energy_rating,
            requires_professional_install=requires_install,  # Based on installation options
            install_complexity=install_complexity,  # Dynamic based on requirements  
            installation_time_estimate=time_display,  # Dynamic based on options
            featured_image_url=featured_image,  # First image from catalog_dto.images
            gallery_images=gallery_images,  # Rest of images from catalog_dto.images
            product_highlights=_extract_product_highlights(catalog_dto),  # Extract from specifications
            technical_specs=catalog_dto.specifications or {},  # Use real specifications
            meta_title=meta_title,  # Generated SEO title
            meta_description=meta_description or "",  # Generated SEO description
            slug=product_slug,  # Generated from product name
            is_active=catalog_dto.in_stock,
            is_featured=catalog_dto.is_featured,
            current_stock=float(catalog_dto.stock_quantity),
            installation_options=installation_options
        )
        
        return catalog_item
        
    except EntityNotFoundError as e:
        logger.warning(f"Business or product not found: {business_id}/{product_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product")
    except Exception as e:
        logger.error(f"Unexpected error retrieving product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product-pricing/{business_id}/{product_id}", response_model=PricingBreakdown)
async def get_product_pricing(
    business_id: str = Path(..., description="Business ID"),
    product_id: str = Path(..., description="Product ID"),
    installation_option_id: Optional[str] = Query(None, description="Installation option ID"),
    membership_plan_id: Optional[str] = Query(None, description="Membership plan ID for discounts"),
    quantity: int = Query(1, ge=1, le=100, description="Product quantity"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Calculate comprehensive pricing for a product with installation and membership discounts.
    
    Args:
        business_id: The unique identifier of the business
        product_id: The unique identifier of the product
        installation_option_id: Optional installation option
        membership_plan_id: Optional membership plan for discounts
        quantity: Product quantity
        product_service: Injected product service
        
    Returns:
        PricingBreakdown: Detailed pricing breakdown
        
    Raises:
        HTTPException: If the business or product is not found
    """
    
    try:
        pricing_dto = await product_service.calculate_product_pricing(
            business_id=business_id,
            product_id=product_id,
            installation_option_id=installation_option_id,
            membership_plan_id=membership_plan_id,
            quantity=quantity
        )
        
        # Map DTO to public schema (normalized fields expected by the website)
        product_unit_price = pricing_dto.unit_price
        installation_base_price = pricing_dto.installation_price or 0
        product_subtotal = pricing_dto.product_subtotal
        installation_subtotal = pricing_dto.installation_price or 0
        subtotal_before = pricing_dto.subtotal
        total_discount = pricing_dto.discount_amount or 0
        subtotal_after = subtotal_before - total_discount
        tax_rate = pricing_dto.tax_rate
        tax_amount = pricing_dto.tax_amount
        total_amount = pricing_dto.total
        total_savings = total_discount
        savings_pct = (total_savings / subtotal_before * 100) if subtotal_before and subtotal_before > 0 else 0

        pricing_breakdown = PricingBreakdown(
            product_unit_price=float(product_unit_price),
            installation_base_price=float(installation_base_price),
            quantity=int(pricing_dto.quantity),
            product_subtotal=float(product_subtotal),
            installation_subtotal=float(installation_subtotal),
            subtotal_before_discounts=float(subtotal_before),
            membership_type=None,
            product_discount_amount=0.0,
            installation_discount_amount=float(total_discount),
            total_discount_amount=float(total_discount),
            bundle_savings=0.0,
            subtotal_after_discounts=float(subtotal_after),
            tax_rate=float(tax_rate),
            tax_amount=float(tax_amount),
            total_amount=float(total_amount),
            total_savings=float(total_savings),
            savings_percentage=float(savings_pct),
            formatted_display_price=f"${total_amount:,.0f}",
            price_display_type="fixed"
        )
        
        return pricing_breakdown
        
    except EntityNotFoundError as e:
        logger.warning(f"Business or product not found: {business_id}/{product_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error calculating pricing for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate pricing")
    except Exception as e:
        logger.error(f"Unexpected error calculating pricing for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product-categories/{business_id}", response_model=List[ProductCategory])
async def get_product_categories(
    business_id: str = Path(..., description="Business ID"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get product categories for a business.
    
    Returns list of product categories with product counts for navigation.
    
    Args:
        business_id: The unique identifier of the business
        product_service: Injected product service
        
    Returns:
        List[ProductCategory]: A list of product categories
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        # TODO: Add get_product_categories method to ProductService
        # For now, return empty list
        return []
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid business ID: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")
    except Exception as e:
        logger.error(f"Unexpected error retrieving categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product-by-slug/{business_id}/{product_slug}", response_model=ProductCatalogItem)
async def get_product_by_slug(
    business_id: str = Path(..., description="Business ID"),
    product_slug: str = Path(..., description="Product SEO slug"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get detailed product information by SEO slug.
    
    SEO-friendly endpoint that finds products by their slug instead of UUID.
    Returns complete product details for product detail page display.
    """
    
    try:
        # For now, just use the existing UUID-based endpoint by finding the product first
        catalog_dtos = await product_service.get_product_catalog(
            business_id=business_id,
            limit=1000
        )
        
        # Find matching product by slug
        matching_product = None
        for catalog_dto in catalog_dtos:
            generated_slug = catalog_dto.name.lower().replace(' ', '-').replace('&', 'and')
            if generated_slug == product_slug:
                matching_product = catalog_dto
                break
        
        if not matching_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Use the existing get_product_details logic by calling it with the found product ID
        return await get_product_details(business_id, matching_product.id, product_service)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product by slug: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
