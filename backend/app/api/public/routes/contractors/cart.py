"""
Contractor Shopping Cart API Routes

Public endpoints for managing shopping cart functionality.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body
from typing import Optional
import logging
import os
import uuid
from datetime import datetime

from .schemas import (
    CartItemRequest, CartItem, ShoppingCart, CartSummary
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/shopping-cart/create", response_model=ShoppingCart)
async def create_shopping_cart(
    session_id: Optional[str] = Query(None, description="Session ID for guest users"),
    customer_id: Optional[str] = Query(None, description="Customer ID for logged-in users")
):
    """
    Create a new shopping cart.
    
    Creates a new cart for either guest users (session-based) or logged-in users.
    At least one of session_id or customer_id must be provided.
    """
    
    if not session_id and not customer_id:
        raise HTTPException(status_code=400, detail="Either session_id or customer_id must be provided")
    
    try:
        from .....core.db import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Get business ID from environment variable
        business_id = os.getenv("BUSINESS_ID", "a1b2c3d4-e5f6-7890-1234-567890abcdef")
        
        # Create new cart
        cart_data = {
            "id": str(uuid.uuid4()),
            "business_id": business_id,
            "session_id": session_id,
            "customer_email": customer_id,  # Using customer_id as email for now
            "cart_status": "active",
            "currency_code": "USD",
            "subtotal": 0.0,
            "total_savings": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "membership_type": "none",
            "membership_verified": False,
            "last_activity_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("shopping_carts").insert(cart_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create cart")
        
        cart = result.data[0]
        
        return ShoppingCart(
            id=cart["id"],
            business_id=cart.get("business_id"),
            session_id=cart.get("session_id"),
            customer_email=cart.get("customer_email"),
            customer_phone=cart.get("customer_phone"),
            cart_status=cart["cart_status"],
            currency_code=cart.get("currency_code", "USD"),
            items=[],
            membership_type=cart.get("membership_type"),
            membership_verified=cart.get("membership_verified", False),
            subtotal=float(cart["subtotal"]),
            total_savings=float(cart["total_savings"]),
            tax_amount=float(cart["tax_amount"]),
            total_amount=float(cart["total_amount"]),
            item_count=0,  # No items yet
            last_activity_at=cart.get("last_activity_at"),
            created_at=cart["created_at"],
            updated_at=cart["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error creating shopping cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create shopping cart")


@router.get("/shopping-cart/{cart_identifier}", response_model=ShoppingCart)
async def get_shopping_cart(
    cart_identifier: str = Path(..., description="Cart ID or Session ID"),
    business_id: Optional[str] = Query(None, description="Business ID for pricing context (optional - will use cart's business_id)")
):
    """
    Get shopping cart with all items and pricing calculations.
    
    Retrieves cart by cart ID or session ID with real-time pricing updates.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Try to find cart by ID first, then by session_id
        cart_query = supabase.table("shopping_carts").select("*")
        
        if len(cart_identifier) > 20:  # Likely a UUID cart ID
            cart_query = cart_query.eq("id", cart_identifier)
        else:  # Likely a session ID
            cart_query = cart_query.eq("session_id", cart_identifier)
        
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        cart_data = cart_result.data[0]
        cart_id = cart_data["id"]
        
        # Use cart's business_id if not provided in query
        if not business_id:
            business_id = cart_data.get("business_id")
            if not business_id:
                raise HTTPException(status_code=400, detail="Business ID not found in cart or query parameters")
        
        # Get cart items with product details
        items_query = supabase.table("cart_items").select(
            """
            id, product_id, installation_option_id, quantity,
            unit_price, install_price, subtotal_price, product_discount, 
            install_discount, total_discount, final_price, product_name,
            products(name, sku, unit_price),
            product_installation_options(option_name, base_install_price)
            """
        ).eq("cart_id", cart_id).order("created_at")
        
        items_result = items_query.execute()
        
        # Process cart items
        cart_items = []
        total_subtotal = 0.0
        total_discount = 0.0
        
        for item_data in items_result.data or []:
            product = item_data.get("products", {})
            install_option = item_data.get("product_installation_options", {})
            
            # Use stored values from cart_items table
            item_total = float(item_data["final_price"])
            discount_amount = float(item_data["total_discount"])
            
            cart_item = CartItem(
                id=str(item_data["id"]),
                product_id=item_data["product_id"],
                product_name=item_data.get("product_name") or (product.get("name", "Unknown Product") if product else "Unknown Product"),
                product_sku=product.get("sku", "") if product else "",
                unit_price=float(item_data["unit_price"]),
                installation_option_id=item_data.get("installation_option_id"),
                installation_option_name=install_option.get("option_name") if install_option else None,
                installation_price=float(item_data["install_price"]),
                quantity=item_data["quantity"],
                item_total=item_total,
                discount_amount=discount_amount,
                membership_discount=float(item_data.get("product_discount", 0)) + float(item_data.get("install_discount", 0)),
                bundle_savings=0.0  # Not stored in cart_items currently
            )
            
            cart_items.append(cart_item)
            total_subtotal += item_total + discount_amount  # Subtotal before discounts
            total_discount += discount_amount
        
        # Calculate tax and totals
        tax_rate = 0.0825
        tax_amount = (total_subtotal - total_discount) * tax_rate
        total_amount = (total_subtotal - total_discount) + tax_amount
        
        return ShoppingCart(
            id=cart_data["id"],
            business_id=cart_data.get("business_id"),
            session_id=cart_data.get("session_id"),
            customer_email=cart_data.get("customer_email"),
            customer_phone=cart_data.get("customer_phone"),
            cart_status=cart_data.get("cart_status", "active"),
            currency_code=cart_data.get("currency_code", "USD"),
            items=cart_items,
            membership_type=cart_data.get("membership_type", "none"),
            membership_verified=cart_data.get("membership_verified", False),
            subtotal=total_subtotal,
            total_savings=total_discount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            item_count=len(cart_items),
            last_activity_at=cart_data.get("updated_at"),
            created_at=cart_data.get("created_at"),
            updated_at=cart_data.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching shopping cart {cart_identifier}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch shopping cart")


@router.post("/shopping-cart/{cart_id}/items", response_model=CartItem)
async def add_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item: CartItemRequest = Body(...),
    business_id: str = Query(..., description="Business ID for pricing context")
):
    """
    Add item to shopping cart with real-time pricing calculation.
    
    Adds a product with optional installation to the cart and calculates
    pricing with membership discounts and bundle savings.
    """
    
    try:
        from .....core.db import get_supabase_client
        from .....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption, MembershipType
        )
        from decimal import Decimal
        
        supabase = get_supabase_client()
        
        # Verify cart exists
        cart_result = supabase.table("shopping_carts").select("id, membership_type").eq("id", cart_id).execute()
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        cart_data = cart_result.data[0]
        
        # Get product information
        product_query = supabase.table("products").select(
            """
            id, name, sku, unit_price, cost_price, requires_professional_install,
            install_complexity, warranty_years, is_taxable
            """
        ).eq("business_id", business_id).eq("id", item.product_id).eq("show_on_website", True).eq("is_active", True)
        
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
            is_taxable=product_data.get("is_taxable", True)
        )
        
        # Get installation option if specified
        install_option = None
        if item.installation_option_id:
            install_query = supabase.table("product_installation_options").select(
                """
                id, option_name, description, base_install_price, complexity_multiplier,
                residential_install_price, commercial_install_price, premium_install_price,
                estimated_duration_hours, requirements, included_in_install
                """
            ).eq("id", item.installation_option_id).eq("product_id", item.product_id).eq("is_active", True)
            
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
        
        # Parse membership type (prioritize item level, then cart level)
        membership = None
        membership_type = item.membership_type or cart_data.get("membership_type")
        if membership_type:
            try:
                membership = MembershipType(membership_type)
            except ValueError:
                pass  # Invalid membership type, proceed without membership
        
        # Calculate pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, item.quantity, membership
        )
        
        # Check for existing item with same product and installation option
        existing_item_query = supabase.table("cart_items").select("id, quantity").eq("cart_id", cart_id).eq("product_id", item.product_id)
        
        if item.installation_option_id:
            existing_item_query = existing_item_query.eq("installation_option_id", item.installation_option_id)
        else:
            existing_item_query = existing_item_query.is_("installation_option_id", "null")
        
        existing_item_result = existing_item_query.execute()
        
        if existing_item_result.data:
            # Update existing item quantity
            existing_item = existing_item_result.data[0]
            new_quantity = existing_item["quantity"] + item.quantity
            
            # Recalculate pricing for new quantity
            new_calculation = pricing_engine.calculate_combined_pricing(
                product_info, install_option, new_quantity, membership
            )
            
            updated_item = supabase.table("cart_items").update({
                "quantity": new_quantity,
                "unit_price": float(calculation.product_unit_price),
                "install_price": float(calculation.installation_base_price),
                "final_price": float(new_calculation.subtotal_after_discounts),
                "total_discount": float(new_calculation.total_discount_amount),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", existing_item["id"]).execute()
            
            if not updated_item.data:
                raise HTTPException(status_code=500, detail="Failed to update cart item")
            
            cart_item_data = updated_item.data[0]
            final_quantity = new_quantity
        else:
            # Create new cart item
            cart_item_data = {
                "id": str(uuid.uuid4()),
                "cart_id": cart_id,
                "product_id": item.product_id,
                "product_name": product_info.name,
                "product_sku": product_info.sku,
                "installation_option_id": item.installation_option_id,
                "installation_name": install_option.option_name if install_option else None,
                "quantity": item.quantity,
                "unit_price": float(calculation.product_unit_price),
                "install_price": float(calculation.installation_base_price),
                "subtotal_price": float(calculation.subtotal_before_discounts),
                "membership_type": calculation.membership_type.value if calculation.membership_type else None,
                "product_discount": float(calculation.product_discount_amount),
                "install_discount": float(calculation.installation_discount_amount),
                "total_discount": float(calculation.total_discount_amount),
                "final_price": float(calculation.subtotal_after_discounts),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("cart_items").insert(cart_item_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to add item to cart")
            
            cart_item_data = result.data[0]
            final_quantity = item.quantity
        
        # Update cart membership type if provided
        if item.membership_type and item.membership_type != cart_data.get("membership_type"):
            supabase.table("shopping_carts").update({
                "membership_type": item.membership_type,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", cart_id).execute()
        
        # Return cart item response
        return CartItem(
            id=str(cart_item_data["id"]),
            product_id=cart_item_data["product_id"],
            product_name=product_info.name,
            product_sku=product_info.sku,
            unit_price=float(cart_item_data["unit_price"]),
            installation_option_id=cart_item_data.get("installation_option_id"),
            installation_option_name=install_option.option_name if install_option else None,
            installation_price=float(cart_item_data["install_price"]),
            quantity=final_quantity,
            item_total=float(cart_item_data["final_price"]),
            discount_amount=float(cart_item_data["total_discount"]),
            membership_discount=float(calculation.product_discount_amount + calculation.installation_discount_amount),
            bundle_savings=float(calculation.bundle_savings)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add item to cart")


@router.put("/shopping-cart/{cart_id}/items/{item_id}", response_model=CartItem)
async def update_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item_id: str = Path(..., description="Cart item ID"),
    quantity: int = Query(..., ge=0, le=100, description="New quantity (0 to remove)"),
    business_id: str = Query(..., description="Business ID for pricing context")
):
    """
    Update cart item quantity with real-time pricing recalculation.
    
    Updates quantity and recalculates pricing. Set quantity to 0 to remove item.
    """
    
    try:
        from .....core.db import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Verify cart and item exist
        cart_item_query = supabase.table("cart_items").select(
            "id, cart_id, product_id, installation_option_id"
        ).eq("id", item_id).eq("cart_id", cart_id)
        
        cart_item_result = cart_item_query.execute()
        if not cart_item_result.data:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        cart_item_data = cart_item_result.data[0]
        
        if quantity == 0:
            # Remove item from cart
            supabase.table("cart_items").delete().eq("id", item_id).execute()
            raise HTTPException(status_code=204, detail="Item removed from cart")
        
        # Get product and installation info for pricing recalculation
        product_query = supabase.table("products").select(
            "id, name, sku, unit_price, cost_price, requires_professional_install, install_complexity"
        ).eq("business_id", business_id).eq("id", cart_item_data["product_id"]).eq("is_active", True)
        
        product_result = product_query.execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product_result.data[0]
        
        # Recalculate pricing with new quantity
        from .....application.services.product_install_pricing_service import (
            ProductInstallPricingEngine, ProductInfo, InstallationOption
        )
        from decimal import Decimal
        
        product_info = ProductInfo(
            id=str(product_data["id"]),
            name=product_data["name"],
            sku=product_data["sku"],
            unit_price=Decimal(str(product_data["unit_price"])),
            requires_professional_install=bool(cart_item_data.get("installation_option_id"))
        )
        
        install_option = None
        if cart_item_data.get("installation_option_id"):
            install_query = supabase.table("product_installation_options").select(
                "id, option_name, base_install_price"
            ).eq("id", cart_item_data["installation_option_id"]).eq("is_active", True)
            
            install_result = install_query.execute()
            if install_result.data:
                install_data = install_result.data[0]
                install_option = InstallationOption(
                    id=str(install_data["id"]),
                    option_name=install_data["option_name"],
                    base_install_price=Decimal(str(install_data["base_install_price"]))
                )
        
        # Calculate new pricing
        pricing_engine = ProductInstallPricingEngine()
        calculation = pricing_engine.calculate_combined_pricing(
            product_info, install_option, quantity, None  # TODO: Get membership from cart
        )
        
        # Update cart item
        updated_item = supabase.table("cart_items").update({
            "quantity": quantity,
            "final_price": float(calculation.subtotal_after_discounts),
            "total_discount": float(calculation.total_discount_amount),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", item_id).execute()
        
        if not updated_item.data:
            raise HTTPException(status_code=500, detail="Failed to update cart item")
        
        updated_data = updated_item.data[0]
        
        return CartItem(
            id=str(updated_data["id"]),
            product_id=updated_data["product_id"],
            product_name=product_info.name,
            product_sku=product_info.sku,
            unit_price=float(calculation.product_unit_price),
            installation_option_id=updated_data.get("installation_option_id"),
            installation_option_name=install_option.option_name if install_option else None,
            installation_price=float(calculation.installation_base_price),
            quantity=quantity,
            item_total=float(updated_data["final_price"]),
            discount_amount=float(updated_data["total_discount"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update cart item")


@router.delete("/shopping-cart/{cart_id}/items/{item_id}")
async def remove_cart_item(
    cart_id: str = Path(..., description="Shopping cart ID"),
    item_id: str = Path(..., description="Cart item ID")
):
    """
    Remove specific item from shopping cart.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Verify item exists and belongs to cart
        item_query = supabase.table("cart_items").select("id").eq("id", item_id).eq("cart_id", cart_id)
        item_result = item_query.execute()
        
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Delete item
        supabase.table("cart_items").delete().eq("id", item_id).execute()
        
        return {"message": "Item removed from cart successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing cart item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove cart item")


@router.delete("/shopping-cart/{cart_id}")
async def clear_shopping_cart(
    cart_id: str = Path(..., description="Shopping cart ID")
):
    """
    Clear all items from shopping cart or delete the cart entirely.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Verify cart exists
        cart_query = supabase.table("shopping_carts").select("id").eq("id", cart_id)
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        
        # Delete all cart items
        supabase.table("cart_items").delete().eq("cart_id", cart_id).execute()
        
        # Update cart totals to zero
        supabase.table("shopping_carts").update({
            "subtotal": 0.0,
            "total_savings": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", cart_id).execute()
        
        return {"message": "Shopping cart cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cart {cart_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear shopping cart")


@router.get("/shopping-cart/{cart_identifier}/summary", response_model=CartSummary)
async def get_cart_summary(
    cart_identifier: str = Path(..., description="Cart ID or Session ID")
):
    """
    Get cart summary with totals for header/navigation display.
    
    Returns lightweight cart summary for UI elements that need
    quick access to cart totals and item counts.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Find cart
        cart_query = supabase.table("shopping_carts").select(
            "id, subtotal, total_savings, tax_amount, total_amount"
        )
        
        if len(cart_identifier) > 20:  # UUID cart ID
            cart_query = cart_query.eq("id", cart_identifier)
        else:  # Session ID
            cart_query = cart_query.eq("session_id", cart_identifier)
        
        cart_result = cart_query.execute()
        
        if not cart_result.data:
            # Return empty cart summary
            return CartSummary(
                item_count=0,
                subtotal=0.0,
                total_savings=0.0,
                tax_amount=0.0,
                total_amount=0.0,
                savings_percentage=0.0
            )
        
        cart = cart_result.data[0]
        subtotal = float(cart["subtotal"])
        total_savings = float(cart["total_savings"])
        
        # Calculate item count from cart_items table
        items_count_result = supabase.table("cart_items").select("id", count="exact").eq("cart_id", cart["id"]).execute()
        item_count = items_count_result.count or 0
        
        savings_percentage = (total_savings / subtotal * 100) if subtotal > 0 else 0.0
        
        return CartSummary(
            item_count=item_count,
            subtotal=subtotal,
            total_savings=total_savings,
            tax_amount=float(cart["tax_amount"]),
            total_amount=float(cart["total_amount"]),
            savings_percentage=savings_percentage
        )
        
    except Exception as e:
        logger.error(f"Error fetching cart summary for {cart_identifier}: {str(e)}")
        # Return empty cart on error
        return CartSummary(
            item_count=0,
            subtotal=0.0,
            total_savings=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            savings_percentage=0.0
        )
