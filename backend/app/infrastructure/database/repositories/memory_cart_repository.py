"""
In-Memory Cart Repository Implementation

Simple in-memory implementation of the cart repository for development/testing.
In production, this should be replaced with a proper database implementation.
"""

import uuid
from typing import Optional, List, Dict
from datetime import datetime, timezone

from ....domain.repositories.cart_repository import CartRepository
from ....domain.entities.cart import ShoppingCart, CartItem
from ....domain.exceptions.domain_exceptions import EntityNotFoundError


class MemoryCartRepository(CartRepository):
    """In-memory implementation of cart repository."""
    
    def __init__(self):
        self._carts: Dict[uuid.UUID, ShoppingCart] = {}
    
    async def create_cart(self, cart: ShoppingCart) -> ShoppingCart:
        """Create a new shopping cart."""
        self._carts[cart.id] = cart
        return cart
    
    async def get_cart_by_id(self, cart_id: uuid.UUID) -> Optional[ShoppingCart]:
        """Get cart by ID."""
        return self._carts.get(cart_id)
    
    async def update_cart(self, cart: ShoppingCart) -> ShoppingCart:
        """Update an existing cart."""
        if cart.id not in self._carts:
            raise EntityNotFoundError("Cart", str(cart.id))
        
        cart.updated_at = datetime.now(timezone.utc)
        self._carts[cart.id] = cart
        return cart
    
    async def delete_cart(self, cart_id: uuid.UUID) -> bool:
        """Delete a cart."""
        if cart_id in self._carts:
            del self._carts[cart_id]
            return True
        return False
    
    async def add_item_to_cart(self, cart_id: uuid.UUID, item: CartItem) -> ShoppingCart:
        """Add an item to the cart."""
        cart = self._carts.get(cart_id)
        if not cart:
            raise EntityNotFoundError("Cart", str(cart_id))
        
        cart.add_item(item)
        return cart
    
    async def remove_item_from_cart(self, cart_id: uuid.UUID, item_id: uuid.UUID) -> ShoppingCart:
        """Remove an item from the cart."""
        cart = self._carts.get(cart_id)
        if not cart:
            raise EntityNotFoundError("Cart", str(cart_id))
        
        if not cart.remove_item(item_id):
            raise EntityNotFoundError("CartItem", str(item_id))
        
        return cart
    
    async def update_item_quantity(self, cart_id: uuid.UUID, item_id: uuid.UUID, quantity: int) -> ShoppingCart:
        """Update item quantity in cart."""
        cart = self._carts.get(cart_id)
        if not cart:
            raise EntityNotFoundError("Cart", str(cart_id))
        
        if not cart.update_item_quantity(item_id, quantity):
            raise EntityNotFoundError("CartItem", str(item_id))
        
        return cart
    
    async def clear_cart(self, cart_id: uuid.UUID) -> ShoppingCart:
        """Clear all items from cart."""
        cart = self._carts.get(cart_id)
        if not cart:
            raise EntityNotFoundError("Cart", str(cart_id))
        
        cart.clear_items()
        return cart
    
    async def get_carts_by_session(self, session_id: str) -> List[ShoppingCart]:
        """Get carts by session ID."""
        return [cart for cart in self._carts.values() if cart.session_id == session_id]
    
    async def get_carts_by_customer(self, customer_id: str) -> List[ShoppingCart]:
        """Get carts by customer ID."""
        return [cart for cart in self._carts.values() if cart.customer_id == customer_id]
