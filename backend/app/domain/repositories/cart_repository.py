"""
Cart Repository Interface

Repository interface for shopping cart persistence and management.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from ..entities.cart import ShoppingCart, CartItem


class CartRepository(ABC):
    """Repository interface for shopping cart operations."""
    
    @abstractmethod
    async def create_cart(self, cart: ShoppingCart) -> ShoppingCart:
        """Create a new shopping cart."""
        pass
    
    @abstractmethod
    async def get_cart_by_id(self, cart_id: uuid.UUID) -> Optional[ShoppingCart]:
        """Get cart by ID."""
        pass
    
    @abstractmethod
    async def update_cart(self, cart: ShoppingCart) -> ShoppingCart:
        """Update an existing cart."""
        pass
    
    @abstractmethod
    async def delete_cart(self, cart_id: uuid.UUID) -> bool:
        """Delete a cart."""
        pass
    
    @abstractmethod
    async def add_item_to_cart(self, cart_id: uuid.UUID, item: CartItem) -> ShoppingCart:
        """Add an item to the cart."""
        pass
    
    @abstractmethod
    async def remove_item_from_cart(self, cart_id: uuid.UUID, item_id: uuid.UUID) -> ShoppingCart:
        """Remove an item from the cart."""
        pass
    
    @abstractmethod
    async def update_item_quantity(self, cart_id: uuid.UUID, item_id: uuid.UUID, quantity: int) -> ShoppingCart:
        """Update item quantity in cart."""
        pass
    
    @abstractmethod
    async def clear_cart(self, cart_id: uuid.UUID) -> ShoppingCart:
        """Clear all items from cart."""
        pass
    
    @abstractmethod
    async def get_carts_by_session(self, session_id: str) -> List[ShoppingCart]:
        """Get carts by session ID."""
        pass
    
    @abstractmethod
    async def get_carts_by_customer(self, customer_id: str) -> List[ShoppingCart]:
        """Get carts by customer ID."""
        pass
