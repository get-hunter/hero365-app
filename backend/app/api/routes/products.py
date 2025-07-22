"""
Product API Routes

REST API endpoints for product and inventory management operations.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import (
    require_view_projects_dep, require_edit_projects_dep, require_delete_projects_dep
)
from ..schemas.product_schemas import (
    CreateProductSchema, UpdateProductSchema, ProductSearchSchema,
    ProductResponseSchema, ProductListResponseSchema, ProductSummarySchema,
    StockAdjustmentSchema, StockMovementResponseSchema,
    ReorderSuggestionsResponseSchema, ProductActionResponse, StockActionResponse
)
from ..schemas.activity_schemas import MessageResponse
from ...application.use_cases.product.create_product_use_case import CreateProductUseCase
from ...application.use_cases.product.manage_inventory_use_case import ManageInventoryUseCase
from ...application.use_cases.product.inventory_reorder_management_use_case import InventoryReorderManagementUseCase
from ...application.dto.product_dto import (
    CreateProductDTO, ProductDTO, ProductSearchCriteria, StockAdjustmentDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_product_repository, get_create_product_use_case, get_manage_inventory_use_case,
    get_inventory_reorder_management_use_case
)
from ...domain.entities.product_enums.enums import ProductStatus, ProductType

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED, operation_id="create_product_no_slash")
async def create_product(
    request: CreateProductSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new product.
    
    Creates a new product in the inventory system with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Starting product creation for business {business_id}")
    logger.info(f"🔧 ProductAPI: Request data: SKU={request.sku}, Name={request.name}")
    
    try:
        # Create DTO
        create_dto = CreateProductDTO(
            sku=request.sku,
            name=request.name,
            description=request.description,
            product_type=request.product_type,
            status=request.status,
            category_id=request.category_id,
            pricing_model=request.pricing_model,
            unit_price=request.unit_price,
            cost_price=request.cost_price,
            markup_percentage=request.markup_percentage,
            currency=request.currency,
            track_inventory=request.track_inventory,
            unit_of_measure=request.unit_of_measure,
            initial_quantity=request.initial_quantity,
            reorder_point=request.reorder_point,
            reorder_quantity=request.reorder_quantity,
            minimum_quantity=request.minimum_quantity,
            maximum_quantity=request.maximum_quantity,
            costing_method=request.costing_method,
            weight=request.weight,
            weight_unit=request.weight_unit,
            dimensions=request.dimensions,
            tax_rate=request.tax_rate,
            tax_code=request.tax_code,
            is_taxable=request.is_taxable,
            primary_supplier_id=request.primary_supplier_id,
            barcode=request.barcode,
            manufacturer=request.manufacturer,
            manufacturer_sku=request.manufacturer_sku,
            brand=request.brand,
            image_urls=request.image_urls
        )
        
        logger.info(f"🔧 ProductAPI: DTO created successfully, calling use case")
        
        product_dto = await use_case.execute(create_dto, current_user["sub"], business_id)
        logger.info(f"🔧 ProductAPI: Use case completed successfully")
        
        return _product_dto_to_response(product_dto)
        
    except ValidationError as e:
        logger.error(f"❌ ProductAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionDeniedError as e:
        logger.error(f"❌ ProductAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ ProductAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error creating product: {str(e)}")
        logger.error(f"❌ ProductAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ ProductAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product(
    product_id: uuid.UUID = Path(..., description="Product ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    product_repository = Depends(get_product_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get a product by ID.
    
    Retrieves detailed information about a specific product.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Getting product {product_id} for business {business_id}")
    
    try:
        product = await product_repository.get_by_id(business_id, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        product_dto = ProductDTO.from_entity(product)
        return _product_dto_to_response(product_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error getting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{product_id}", response_model=ProductResponseSchema)
async def update_product(
    product_id: uuid.UUID = Path(..., description="Product ID"),
    request: UpdateProductSchema = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    product_repository = Depends(get_product_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update a product.
    
    Updates an existing product with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Updating product {product_id} for business {business_id}")
    
    try:
        # Get existing product
        product = await product_repository.get_by_id(business_id, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # Update product fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        product.last_modified = datetime.utcnow()
        
        # Save updated product
        updated_product = await product_repository.update(product)
        product_dto = ProductDTO.from_entity(updated_product)
        
        return _product_dto_to_response(product_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: uuid.UUID = Path(..., description="Product ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    product_repository = Depends(get_product_repository),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    Delete a product.
    
    Soft deletes a product from the inventory system.
    Requires 'delete_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Deleting product {product_id} for business {business_id}")
    
    try:
        # Check if product exists
        product = await product_repository.get_by_id(business_id, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # Soft delete the product
        await product_repository.delete(business_id, product_id)
        
        return MessageResponse(message="Product deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=ProductListResponseSchema)
@router.get("", response_model=ProductListResponseSchema, operation_id="list_products_no_slash")
async def list_products(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by product status"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category ID"),
    supplier_id: Optional[uuid.UUID] = Query(None, description="Filter by supplier ID"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    current_user: dict = Depends(get_current_user),
    product_repository = Depends(get_product_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List products.
    
    Retrieves a paginated list of products with optional filtering.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Listing products for business {business_id}")
    
    try:
        # Build search criteria
        criteria = ProductSearchCriteria(
            business_id=business_id,
            status=status,
            category_id=category_id,
            supplier_id=supplier_id,
            low_stock_only=low_stock_only,
            skip=skip,
            limit=limit
        )
        
        # Get products
        products, total_count = await product_repository.search(criteria)
        
        # Convert to DTOs
        product_dtos = [ProductDTO.from_entity(p) for p in products]
        product_responses = [_product_dto_to_response(dto) for dto in product_dtos]
        
        # Calculate pagination
        page = (skip // limit) + 1
        per_page = limit
        has_next = (skip + limit) < total_count
        has_prev = skip > 0
        
        return ProductListResponseSchema(
            products=product_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error listing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search", response_model=ProductListResponseSchema)
async def search_products(
    request: ProductSearchSchema,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    product_repository = Depends(get_product_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search products.
    
    Advanced search for products with comprehensive filtering options.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Searching products for business {business_id}")
    
    try:
        # Convert to search criteria
        criteria = ProductSearchCriteria(
            business_id=business_id,
            search_term=request.search_term,
            category_id=request.category_id,
            status=request.status,
            product_type=request.product_type,
            supplier_id=request.supplier_id,
            low_stock_only=request.low_stock_only,
            out_of_stock_only=request.out_of_stock_only,
            needs_reorder_only=request.needs_reorder_only,
            min_price=request.min_price,
            max_price=request.max_price,
            min_quantity=request.min_quantity,
            max_quantity=request.max_quantity,
            barcode=request.barcode,
            manufacturer=request.manufacturer,
            brand=request.brand,
            created_from=request.created_from,
            created_to=request.created_to,
            created_by=request.created_by,
            skip=request.skip,
            limit=request.limit,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        
        # Search products
        products, total_count = await product_repository.search(criteria)
        
        # Convert to DTOs
        product_dtos = [ProductDTO.from_entity(p) for p in products]
        product_responses = [_product_dto_to_response(dto) for dto in product_dtos]
        
        # Calculate pagination
        page = (request.skip // request.limit) + 1
        per_page = request.limit
        has_next = (request.skip + request.limit) < total_count
        has_prev = request.skip > 0
        
        return ProductListResponseSchema(
            products=product_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error searching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Stock Management Endpoints

@router.post("/{product_id}/adjust-stock", response_model=StockActionResponse)
async def adjust_stock(
    product_id: uuid.UUID = Path(..., description="Product ID"),
    request: StockAdjustmentSchema = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageInventoryUseCase = Depends(get_manage_inventory_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Adjust product stock.
    
    Performs a stock adjustment (increase or decrease) for a product.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Adjusting stock for product {product_id}")
    
    try:
        # Ensure product_id matches request
        request.product_id = product_id
        
        # Convert to DTO
        adjustment_dto = StockAdjustmentDTO(
            product_id=request.product_id,
            quantity_change=request.quantity_change,
            adjustment_reason=request.adjustment_reason,
            reference_number=request.reference_number,
            notes=request.notes
        )
        
        # Execute adjustment
        result = await use_case.adjust_stock(adjustment_dto, current_user["sub"], business_id)
        
        return StockActionResponse(
            success=result["success"],
            message="Stock adjusted successfully",
            movement_id=result.get("movement_id"),
            quantity_before=result.get("quantity_before"),
            quantity_after=result.get("quantity_after"),
            quantity_change=result.get("quantity_change")
        )
        
    except ValidationError as e:
        logger.error(f"❌ ProductAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ ProductAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error adjusting stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{product_id}/reserve", response_model=StockActionResponse)
async def reserve_stock(
    product_id: uuid.UUID = Path(..., description="Product ID"),
    quantity: float = Body(..., description="Quantity to reserve"),
    reference_id: uuid.UUID = Body(..., description="Reference ID (order, estimate, etc.)"),
    reference_type: str = Body(..., description="Reference type"),
    notes: Optional[str] = Body(None, description="Optional notes"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageInventoryUseCase = Depends(get_manage_inventory_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Reserve product stock.
    
    Reserves stock for orders, estimates, or other references.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Reserving {quantity} units of product {product_id}")
    
    try:
        from decimal import Decimal
        
        # Execute reservation
        result = await use_case.reserve_stock(
            product_id=product_id,
            quantity=Decimal(str(quantity)),
            reference_id=reference_id,
            reference_type=reference_type,
            user_id=current_user["sub"],
            business_id=business_id,
            notes=notes
        )
        
        return StockActionResponse(
            success=result["success"],
            message="Stock reserved successfully",
            quantity_change=result.get("quantity_reserved")
        )
        
    except ValidationError as e:
        logger.error(f"❌ ProductAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ ProductAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error reserving stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Inventory Management Endpoints

@router.get("/reorder/suggestions", response_model=ReorderSuggestionsResponseSchema)
async def get_reorder_suggestions(
    business_context: dict = Depends(get_business_context),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category"),
    supplier_id: Optional[uuid.UUID] = Query(None, description="Filter by supplier"),
    current_user: dict = Depends(get_current_user),
    use_case: InventoryReorderManagementUseCase = Depends(get_inventory_reorder_management_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get reorder suggestions.
    
    Returns automated reorder suggestions for products that need restocking.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ProductAPI: Getting reorder suggestions for business {business_id}")
    
    try:
        suggestions = await use_case.get_reorder_suggestions(
            business_id=business_id,
            user_id=current_user["sub"],
            category_id=category_id,
            supplier_id=supplier_id
        )
        
        return ReorderSuggestionsResponseSchema(**suggestions)
        
    except Exception as e:
        logger.error(f"❌ ProductAPI: Error getting reorder suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )




# Helper functions

def _product_dto_to_response(product_dto: ProductDTO) -> ProductResponseSchema:
    """Convert ProductDTO to ProductResponseSchema."""
    return ProductResponseSchema(
        id=product_dto.id,
        business_id=product_dto.business_id,
        sku=product_dto.sku,
        name=product_dto.name,
        description=product_dto.description,
        product_type=product_dto.product_type,
        product_type_display=product_dto.product_type.replace("_", " ").title() if product_dto.product_type else "",
        status=product_dto.status,
        status_display=product_dto.status.replace("_", " ").title() if product_dto.status else "",
        category_id=product_dto.category_id,
        category_name=product_dto.category_name,
        pricing_model=product_dto.pricing_model,
        unit_price=product_dto.unit_price,
        currency=product_dto.currency,
        unit_cost=product_dto.unit_cost,
        average_cost=product_dto.average_cost,
        markup_percentage=product_dto.markup_percentage,
        margin_percentage=product_dto.margin_percentage,
        track_inventory=product_dto.track_inventory,
        quantity_on_hand=product_dto.quantity_on_hand,
        quantity_reserved=product_dto.quantity_reserved,
        quantity_available=product_dto.quantity_available,
        quantity_on_order=product_dto.quantity_on_order,
        reorder_point=product_dto.reorder_point,
        reorder_quantity=product_dto.reorder_quantity,
        minimum_quantity=product_dto.minimum_quantity,
        maximum_quantity=product_dto.maximum_quantity,
        needs_reorder=product_dto.needs_reorder,
        is_low_stock=product_dto.is_low_stock,
        is_out_of_stock=product_dto.is_out_of_stock,
        unit_of_measure=product_dto.unit_of_measure,
        weight=product_dto.weight,
        weight_unit=product_dto.weight_unit,
        dimensions=product_dto.dimensions,
        tax_rate=product_dto.tax_rate,
        tax_code=product_dto.tax_code,
        is_taxable=product_dto.is_taxable,
        primary_supplier_id=product_dto.primary_supplier_id,
        suppliers=[],  # TODO: Convert supplier DTOs
        locations=[],  # TODO: Convert location DTOs
        pricing_tiers=[],  # TODO: Convert pricing tier DTOs
        barcode=product_dto.barcode,
        manufacturer=product_dto.manufacturer,
        manufacturer_sku=product_dto.manufacturer_sku,
        brand=product_dto.brand,
        image_urls=product_dto.image_urls or [],
        times_sold=product_dto.times_sold,
        last_sale_date=product_dto.last_sale_date,
        last_purchase_date=product_dto.last_purchase_date,
        inventory_value=product_dto.inventory_value,
        created_by=product_dto.created_by,
        created_date=product_dto.created_date,
        last_modified=product_dto.last_modified
    ) 