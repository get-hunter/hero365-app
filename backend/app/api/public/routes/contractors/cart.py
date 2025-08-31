"""
Contractor Shopping Cart API Routes (Clean Architecture)

Public endpoints for managing shopping cart functionality following clean architecture patterns.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from typing import Optional
import logging

from .schemas import CartItemRequest, CartItem, ShoppingCart, CartSummary
from .....application.services.cart_service import CartService
from .....application.dto.cart_dto import AddToCartDTO, UpdateCartItemDTO
from .....application.exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    EntityNotFoundError,
    BusinessRuleError
)
from .....infrastructure.config.dependency_injection import get_business_repository, get_product_repository

logger = logging.getLogger(__name__)

router = APIRouter()


# Singleton cart repository instance
_cart_repository_instance = None

def get_cart_repository():
    """Get singleton cart repository instance."""
    global _cart_repository_instance
    if _cart_repository_instance is None:
        from app.infrastructure.database.repositories.memory_cart_repository import MemoryCartRepository
        _cart_repository_instance = MemoryCartRepository()
    return _cart_repository_instance

def get_cart_service():
    """Get cart service with proper dependency injection."""
    business_repo = get_business_repository()
    cart_repo = get_cart_repository()
    product_repo = get_product_repository()
    return CartService(business_repo, cart_repo, product_repo)


@router.post("/shopping-cart/create-with-id/{cart_id}", response_model=ShoppingCart)
async def create_shopping_cart_with_id(
    cart_id: str = Path(..., description="Specific cart ID to create"),
    business_id: str = Query(..., description="Business ID"),
    session_id: Optional[str] = Query(None, description="Session ID for guest users"),
    customer_id: Optional[str] = Query(None, description="Customer ID for logged-in users"),
    cart_service: CartService = Depends(get_cart_service)
):
    """Create a cart with a specific ID for testing purposes."""
    try:
        from app.domain.entities.cart import ShoppingCart as CartEntity
        import uuid
        
        # Create cart entity with specific ID
        cart_entity = CartEntity(
            id=uuid.UUID(cart_id),
            business_id=uuid.UUID(business_id),
            session_id=session_id,
            customer_id=customer_id,
            items=[]
        )
        
        # Save directly to repository
        cart_repo = get_cart_repository()
        created_cart_entity = await cart_repo.create_cart(cart_entity)
        
        # Convert to DTO and then to API response
        cart_dto = cart_service._convert_cart_entity_to_dto(created_cart_entity)
        
        # Convert to API response format
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_email=None,
            customer_phone=None,
            cart_status="active",
            currency_code="USD",
            items=[],
            membership_type=None,
            membership_verified=False,
            subtotal=0.0,
            total_savings=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            item_count=0,
            last_activity_at=None,
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else "",
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else ""
        )
        
        return shopping_cart
        
    except Exception as e:
        logger.error(f"Error creating cart with ID {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/shopping-cart/create", response_model=ShoppingCart)
async def create_shopping_cart(
    business_id: Optional[str] = Query(None, description="Business ID"),
    session_id: Optional[str] = Query(None, description="Session ID for guest users"),
    customer_id: Optional[str] = Query(None, description="Customer ID for logged-in users"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Create a new shopping cart.
    
    Creates a new cart for either guest users (session-based) or logged-in users.
    At least one of session_id or customer_id must be provided.
    
    Args:
        business_id: The unique identifier of the business
        session_id: Session ID for guest users
        customer_id: Customer ID for logged-in users
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Created shopping cart
        
    Raises:
        HTTPException: If validation fails or creation fails
    """
    
    try:
        # Use default business if none provided (for development/testing)
        if not business_id:
            business_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"  # Default to Austin Elite Home Services
        
        cart_dto = await cart_service.create_cart(
            business_id=business_id,
            session_id=session_id,
            customer_id=customer_id
        )
        
        # Convert DTO to API response model
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_id=cart_dto.customer_id,
            items=[],  # New cart has no items
            subtotal=cart_dto.subtotal,
            tax_amount=cart_dto.tax_amount,
            total=cart_dto.total,
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else None,
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else None,
            expires_at=cart_dto.expires_at
        )
        
        return shopping_cart
        
    except ValidationError as e:
        logger.warning(f"Validation error creating cart: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error creating cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create cart")
    except Exception as e:
        logger.error(f"Unexpected error creating cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/shopping-cart/{cart_id}", response_model=ShoppingCart)
async def get_shopping_cart(
    cart_id: str = Path(..., description="Cart ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get shopping cart by ID.
    
    Args:
        cart_id: The unique identifier of the cart
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Shopping cart details
        
    Raises:
        HTTPException: If cart is not found or retrieval fails
    """
    
    try:
        cart_dto = await cart_service.get_cart(cart_id)
        
        if cart_dto is None:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Convert DTO to API response model
        cart_items = []
        for item_dto in cart_dto.items:
            cart_item = CartItem(
                id=item_dto.id,
                product_id=item_dto.product_id,
                product_name=item_dto.product_name,
                product_sku=item_dto.product_sku,
                unit_price=item_dto.unit_price,
                installation_option_id=item_dto.installation_option_id,
                installation_option_name=getattr(item_dto, "installation_name", None),
                installation_price=item_dto.installation_price,
                quantity=item_dto.quantity,
                item_total=item_dto.unit_price * item_dto.quantity,  # Calculate item total
                discount_amount=0.0,  # TODO: Calculate from discount_percentage
                membership_discount=0.0,  # TODO: Add to DTO
                bundle_savings=0.0  # TODO: Add to DTO
            )
            cart_items.append(cart_item)
        
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_email=None,  # TODO: Add to DTO
            customer_phone=None,  # TODO: Add to DTO
            cart_status="active",
            currency_code="USD",
            items=cart_items,
            membership_type=None,  # TODO: Add to DTO
            membership_verified=False,
            subtotal=cart_dto.subtotal,
            total_savings=0.0,  # TODO: Calculate
            tax_amount=cart_dto.tax_amount,
            total_amount=cart_dto.total,
            item_count=len(cart_items),
            last_activity_at=None,  # TODO: Add to DTO
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else "",
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else ""
        )
        
        return shopping_cart
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (like 404 Cart not found)
        raise
    except ValidationError as e:
        logger.warning(f"Invalid cart ID: {cart_id}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cart")
    except Exception as e:
        logger.error(f"Unexpected error retrieving cart {cart_id}: {str(e)} - Type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/shopping-cart/{cart_id}/items", response_model=ShoppingCart)
async def add_item_to_cart(
    cart_id: str = Path(..., description="Cart ID"),
    item_request: CartItemRequest = Body(..., description="Item to add to cart"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Add an item to the shopping cart.
    
    Args:
        cart_id: The unique identifier of the cart
        item_request: Item details to add to cart
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Updated shopping cart
        
    Raises:
        HTTPException: If cart is not found or operation fails
    """
    
    try:
        # Convert API request to DTO - only use fields that exist on CartItemRequest
        add_item_dto = AddToCartDTO(
            product_id=item_request.product_id,
            quantity=item_request.quantity,
            installation_option_id=item_request.installation_option_id,
            membership_type=item_request.membership_type
        )
        
        cart_dto = await cart_service.add_item_to_cart(cart_id, add_item_dto)
        
        # Convert DTO to API response model (same as get_shopping_cart)
        cart_items = []
        for item_dto in cart_dto.items:
            cart_item = CartItem(
                id=item_dto.id,
                product_id=item_dto.product_id,
                product_name=item_dto.product_name,
                product_sku=item_dto.product_sku,
                unit_price=item_dto.unit_price,
                installation_option_id=item_dto.installation_option_id,
                installation_option_name=getattr(item_dto, "installation_name", None),
                installation_price=item_dto.installation_price,
                quantity=item_dto.quantity,
                item_total=item_dto.unit_price * item_dto.quantity,  # Calculate item total
                discount_amount=0.0,  # TODO: Calculate from discount_percentage
                membership_discount=0.0,  # TODO: Add to DTO
                bundle_savings=0.0  # TODO: Add to DTO
            )
            cart_items.append(cart_item)
        
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_email=None,  # TODO: Add to DTO
            customer_phone=None,  # TODO: Add to DTO
            cart_status="active",
            currency_code="USD",
            items=cart_items,
            membership_type=None,  # TODO: Add to DTO
            membership_verified=False,
            subtotal=cart_dto.subtotal,
            total_savings=0.0,  # TODO: Calculate
            tax_amount=cart_dto.tax_amount,
            total_amount=cart_dto.total,
            item_count=len(cart_items),
            last_activity_at=None,  # TODO: Add to DTO
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else "",
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else ""
        )
        
        return shopping_cart
        
    except EntityNotFoundError as e:
        logger.warning(f"Cart not found: {cart_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error adding item to cart: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except BusinessRuleError as e:
        logger.warning(f"Business rule violation: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error adding item to cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add item to cart")
    except Exception as e:
        logger.error(f"Unexpected error adding item to cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/shopping-cart/{cart_id}/items/{item_id}", response_model=ShoppingCart)
async def update_cart_item(
    cart_id: str = Path(..., description="Cart ID"),
    item_id: str = Path(..., description="Cart item ID"),
    update_request: UpdateCartItemDTO = Body(..., description="Updated item details"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Update the quantity of an item in the cart.
    
    Args:
        cart_id: The unique identifier of the cart
        item_id: The unique identifier of the cart item
        update_request: Updated item details
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Updated shopping cart
        
    Raises:
        HTTPException: If cart or item is not found or operation fails
    """
    
    try:
        cart_dto = await cart_service.update_item_quantity(
            cart_id=cart_id,
            item_id=item_id,
            quantity=update_request.quantity
        )
        
        # Convert DTO to API response model (same as get_shopping_cart)
        cart_items = []
        for item_dto in cart_dto.items:
            cart_item = CartItem(
                id=item_dto.id,
                product_id=item_dto.product_id,
                product_name=item_dto.product_name,
                product_sku=getattr(item_dto, "product_sku", ""),
                unit_price=item_dto.unit_price,
                installation_option_id=item_dto.installation_option_id,
                installation_option_name=getattr(item_dto, "installation_name", None),
                installation_price=item_dto.installation_price,
                quantity=item_dto.quantity,
                item_total=item_dto.unit_price * item_dto.quantity,
                discount_amount=0.0,
                membership_discount=0.0,
                bundle_savings=0.0
            )
            cart_items.append(cart_item)
        
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_id=cart_dto.customer_id,
            items=cart_items,
            subtotal=cart_dto.subtotal,
            tax_amount=cart_dto.tax_amount,
            total=cart_dto.total,
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else None,
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else None,
            expires_at=cart_dto.expires_at
        )
        
        return shopping_cart
        
    except EntityNotFoundError as e:
        logger.warning(f"Cart or item not found: {cart_id}/{item_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error updating cart item: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error updating cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update cart item")
    except Exception as e:
        logger.error(f"Unexpected error updating cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/shopping-cart/{cart_id}/items/{item_id}", response_model=ShoppingCart)
async def remove_item_from_cart(
    cart_id: str = Path(..., description="Cart ID"),
    item_id: str = Path(..., description="Cart item ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Remove an item from the shopping cart.
    
    Args:
        cart_id: The unique identifier of the cart
        item_id: The unique identifier of the cart item
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Updated shopping cart
        
    Raises:
        HTTPException: If cart or item is not found or operation fails
    """
    
    try:
        cart_dto = await cart_service.remove_item_from_cart(cart_id, item_id)
        
        # Convert DTO to API response model (same as get_shopping_cart)
        cart_items = []
        for item_dto in cart_dto.items:
            cart_item = CartItem(
                id=item_dto.id,
                product_id=item_dto.product_id,
                product_name=item_dto.product_name,
                product_sku=getattr(item_dto, "product_sku", ""),
                unit_price=item_dto.unit_price,
                installation_option_id=item_dto.installation_option_id,
                installation_option_name=getattr(item_dto, "installation_name", None),
                installation_price=item_dto.installation_price,
                quantity=item_dto.quantity,
                item_total=item_dto.unit_price * item_dto.quantity,
                discount_amount=0.0,
                membership_discount=0.0,
                bundle_savings=0.0
            )
            cart_items.append(cart_item)
        
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_id=cart_dto.customer_id,
            items=cart_items,
            subtotal=cart_dto.subtotal,
            tax_amount=cart_dto.tax_amount,
            total=cart_dto.total,
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else None,
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else None,
            expires_at=cart_dto.expires_at
        )
        
        return shopping_cart
        
    except EntityNotFoundError as e:
        logger.warning(f"Cart or item not found: {cart_id}/{item_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error removing cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove cart item")
    except Exception as e:
        logger.error(f"Unexpected error removing cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/shopping-cart/{cart_id}/clear", response_model=ShoppingCart)
async def clear_shopping_cart(
    cart_id: str = Path(..., description="Cart ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Clear all items from the shopping cart.
    
    Args:
        cart_id: The unique identifier of the cart
        cart_service: Injected cart service
        
    Returns:
        ShoppingCart: Empty shopping cart
        
    Raises:
        HTTPException: If cart is not found or operation fails
    """
    
    try:
        cart_dto = await cart_service.clear_cart(cart_id)
        
        shopping_cart = ShoppingCart(
            id=cart_dto.id,
            business_id=cart_dto.business_id,
            session_id=cart_dto.session_id,
            customer_id=cart_dto.customer_id,
            items=[],  # Empty cart
            subtotal=cart_dto.subtotal,
            tax_amount=cart_dto.tax_amount,
            total=cart_dto.total,
            created_at=cart_dto.created_at.isoformat() if cart_dto.created_at else None,
            updated_at=cart_dto.updated_at.isoformat() if cart_dto.updated_at else None,
            expires_at=cart_dto.expires_at
        )
        
        return shopping_cart
        
    except EntityNotFoundError as e:
        logger.warning(f"Cart not found: {cart_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error clearing cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cart")
    except Exception as e:
        logger.error(f"Unexpected error clearing cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/shopping-cart/{cart_id}/summary", response_model=CartSummary)
async def get_cart_summary(
    cart_id: str = Path(..., description="Cart ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get shopping cart summary.
    
    Args:
        cart_id: The unique identifier of the cart
        cart_service: Injected cart service
        
    Returns:
        CartSummary: Cart summary information
        
    Raises:
        HTTPException: If cart is not found or retrieval fails
    """
    
    try:
        cart_dto = await cart_service.get_cart(cart_id)
        
        if not cart_dto:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Calculate summary information
        item_count = sum(item.quantity for item in cart_dto.items)
        
        # Calculate total savings from membership discounts
        total_savings = sum(
            (item.unit_price * item.quantity * item.discount_percentage / 100) 
            for item in cart_dto.items 
            if item.discount_percentage > 0
        )
        
        cart_summary = CartSummary(
            item_count=item_count,
            subtotal=cart_dto.subtotal,
            total_savings=total_savings,
            tax_amount=cart_dto.tax_amount,
            total_amount=cart_dto.total,
            savings_percentage=round((total_savings / cart_dto.subtotal * 100) if cart_dto.subtotal > 0 else 0, 1)
        )
        
        return cart_summary
        
    except ValidationError as e:
        logger.warning(f"Invalid cart ID: {cart_id}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving cart summary {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cart summary")
    except Exception as e:
        logger.error(f"Unexpected error retrieving cart summary {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
