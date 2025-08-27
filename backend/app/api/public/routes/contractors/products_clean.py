"""
Contractor Products API Routes (Clean Architecture)

Public endpoints for retrieving contractor products and catalog following clean architecture patterns.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
import logging

from .schemas import ProductItem, ProductCategory, ProductCatalogItem, PricingBreakdown
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
            # TODO: Convert installation options from DTOs
            installation_options = []  # Placeholder
            
            catalog_item = ProductCatalogItem(
                id=catalog_dto.id,
                name=catalog_dto.name,
                description=catalog_dto.description,
                category=catalog_dto.category,
                brand=catalog_dto.brand,
                model=catalog_dto.model,
                sku=catalog_dto.sku,
                unit_price=catalog_dto.unit_price,
                msrp=catalog_dto.msrp,
                in_stock=catalog_dto.in_stock,
                stock_quantity=catalog_dto.stock_quantity,
                specifications=catalog_dto.specifications,
                warranty_years=catalog_dto.warranty_years,
                energy_rating=catalog_dto.energy_rating,
                images=catalog_dto.images,
                installation_options=installation_options,
                has_variations=catalog_dto.has_variations,
                is_featured=catalog_dto.is_featured,
                tags=catalog_dto.tags,
                # Additional fields for catalog display
                long_description="",  # TODO: Add to DTO
                product_highlights=[],  # TODO: Add to DTO
                technical_specs={},  # TODO: Add to DTO
                meta_title="",  # TODO: Add to DTO
                meta_description="",  # TODO: Add to DTO
                slug="",  # TODO: Add to DTO
                featured_image_url="",  # TODO: Add to DTO
                gallery_images=[],  # TODO: Add to DTO
                requires_professional_install=False,  # TODO: Add to DTO
                install_complexity="medium",  # TODO: Add to DTO
                installation_time_estimate=2.0  # TODO: Add to DTO
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
        
        # TODO: Convert installation options from DTOs
        installation_options = []  # Placeholder
        
        catalog_item = ProductCatalogItem(
            id=catalog_dto.id,
            name=catalog_dto.name,
            description=catalog_dto.description,
            category=catalog_dto.category,
            brand=catalog_dto.brand,
            model=catalog_dto.model,
            sku=catalog_dto.sku,
            unit_price=catalog_dto.unit_price,
            msrp=catalog_dto.msrp,
            in_stock=catalog_dto.in_stock,
            stock_quantity=catalog_dto.stock_quantity,
            specifications=catalog_dto.specifications,
            warranty_years=catalog_dto.warranty_years,
            energy_rating=catalog_dto.energy_rating,
            images=catalog_dto.images,
            installation_options=installation_options,
            has_variations=catalog_dto.has_variations,
            is_featured=catalog_dto.is_featured,
            tags=catalog_dto.tags,
            # Additional fields for catalog display
            long_description="",  # TODO: Add to DTO
            product_highlights=[],  # TODO: Add to DTO
            technical_specs={},  # TODO: Add to DTO
            meta_title="",  # TODO: Add to DTO
            meta_description="",  # TODO: Add to DTO
            slug="",  # TODO: Add to DTO
            featured_image_url="",  # TODO: Add to DTO
            gallery_images=[],  # TODO: Add to DTO
            requires_professional_install=False,  # TODO: Add to DTO
            install_complexity="medium",  # TODO: Add to DTO
            installation_time_estimate=2.0  # TODO: Add to DTO
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
        
        pricing_breakdown = PricingBreakdown(
            product_id=pricing_dto.product_id,
            product_name=pricing_dto.product_name,
            quantity=pricing_dto.quantity,
            unit_price=pricing_dto.unit_price,
            product_subtotal=pricing_dto.product_subtotal,
            installation_option_id=pricing_dto.installation_option_id,
            installation_name=pricing_dto.installation_name,
            installation_price=pricing_dto.installation_price,
            subtotal=pricing_dto.subtotal,
            membership_plan_id=pricing_dto.membership_plan_id,
            membership_plan_name=pricing_dto.membership_plan_name,
            discount_percentage=pricing_dto.discount_percentage,
            discount_amount=pricing_dto.discount_amount,
            tax_rate=pricing_dto.tax_rate,
            tax_amount=pricing_dto.tax_amount,
            total=pricing_dto.total
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
