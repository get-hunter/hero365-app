"""
Cart Application Service

Orchestrates shopping cart-related business operations and use cases.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone

from ..dto.cart_dto import (
    CartDTO,
    CartItemDTO,
    CartSummaryDTO,
    AddToCartDTO
)
from ..exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    BusinessRuleError
)
from ...domain.exceptions.domain_exceptions import EntityNotFoundError
from ...domain.repositories.business_repository import BusinessRepository
from ...domain.repositories.cart_repository import CartRepository
from ...domain.repositories.product_repository import ProductRepository
from ...domain.entities.cart import ShoppingCart as CartEntity, CartItem as CartItemEntity
from .installation_templates import get_template_by_id

logger = logging.getLogger(__name__)


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except Exception:
        return False


class CartService:
    """
    Application service for shopping cart operations.
    
    Handles business logic for cart management, item operations, and pricing calculations,
    following clean architecture principles.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        cart_repository: CartRepository,
        product_repository: Optional[ProductRepository] = None
    ):
        self.business_repository = business_repository
        self.cart_repository = cart_repository
        self.product_repository = product_repository
    
    async def create_cart(
        self,
        business_id: str,
        session_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> CartDTO:
        """
        Create a new shopping cart.
        
        Args:
            business_id: Business identifier
            session_id: Session ID for guest users
            customer_id: Customer ID for logged-in users
            
        Returns:
            Created cart as DTO
            
        Raises:
            ValidationError: If neither session_id nor customer_id provided
            EntityNotFoundError: If business doesn't exist
            ApplicationError: If creation fails
        """
        try:
            if not session_id and not customer_id:
                raise ValidationError("Either session_id or customer_id must be provided")
            
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Create cart entity
            cart_id = uuid.uuid4()
            cart_entity = CartEntity(
                id=cart_id,
                business_id=business_uuid,
                session_id=session_id,
                customer_id=customer_id,
                items=[],
                expires_at=None  # TODO: Set expiration based on business rules
            )
            
            # Save to repository
            created_cart_entity = await self.cart_repository.create_cart(cart_entity)
            
            # Convert to DTO
            cart_dto = self._convert_cart_entity_to_dto(created_cart_entity)
            
            logger.info(f"Created cart {cart_id} for business {business_id}")
            return cart_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error creating cart for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to create cart: {str(e)}")
    
    async def get_cart(
        self,
        cart_id: str
    ) -> Optional[CartDTO]:
        """
        Get a shopping cart by ID.
        
        Args:
            cart_id: Cart identifier
            
        Returns:
            Cart DTO if found, None otherwise
            
        Raises:
            ValidationError: If cart ID is invalid
            ApplicationError: If retrieval fails
        """
        try:
            cart_uuid = uuid.UUID(cart_id)
            
            # Get cart from repository
            cart_entity = await self.cart_repository.get_cart_by_id(cart_uuid)
            if not cart_entity:
                return None
            
            # Convert entity to DTO
            cart_dto = self._convert_cart_entity_to_dto(cart_entity)
            return cart_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid cart ID format: {cart_id}")
        except Exception as e:
            logger.error(f"Error retrieving cart {cart_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve cart: {str(e)}")
    
    async def add_item_to_cart(
        self,
        cart_id: str,
        add_item_dto: AddToCartDTO
    ) -> CartDTO:
        """
        Add an item to the shopping cart.
        
        Args:
            cart_id: Cart identifier
            add_item_dto: Item to add to cart
            
        Returns:
            Updated cart DTO
            
        Raises:
            EntityNotFoundError: If cart doesn't exist
            ValidationError: If item data is invalid
            BusinessRuleError: If business rules are violated
            ApplicationError: If operation fails
        """
        try:
            cart_uuid = uuid.UUID(cart_id)
            
            # Get existing cart from repository
            cart_entity = await self.cart_repository.get_cart_by_id(cart_uuid)
            if not cart_entity:
                raise EntityNotFoundError(f"Cart not found: {cart_id}")
            
            # Validate item data
            if add_item_dto.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0")
            
            # Fetch product details if not provided in DTO
            product_name = add_item_dto.product_name
            product_sku = ""
            unit_price = add_item_dto.unit_price or 0.0
            
            if self.product_repository and (not product_name or not unit_price):
                try:
                    # Product repository needs both business_id and product_id
                    product_entity = await self.product_repository.get_by_id(
                        cart_entity.business_id, 
                        uuid.UUID(add_item_dto.product_id)
                    )
                    if product_entity:
                        product_name = product_name or product_entity.name
                        product_sku = product_entity.sku or ""
                        unit_price = unit_price or float(product_entity.unit_price)
                except Exception as e:
                    logger.warning(f"Failed to fetch product details for {add_item_dto.product_id}: {str(e)}")
            
            # Determine installation pricing and name from template if provided
            installation_price = Decimal('0')
            installation_name = None
            if add_item_dto.installation_option_id:
                try:
                    template = get_template_by_id(add_item_dto.installation_option_id)
                    if template:
                        # template.base_price might be Decimal or numeric
                        installation_price = Decimal(str(template.base_price))
                        installation_name = template.name
                    else:
                        installation_price = Decimal('150.00')
                        installation_name = 'Standard Installation'
                except Exception:
                    installation_price = Decimal('150.00')
                    installation_name = 'Standard Installation'

            # Create cart item entity with real product and installation data
            cart_item_entity = CartItemEntity(
                id=uuid.uuid4(),
                cart_id=cart_uuid,
                product_id=uuid.UUID(add_item_dto.product_id),
                product_name=product_name or "Product",
                product_sku=product_sku,
                quantity=add_item_dto.quantity,
                unit_price=Decimal(str(unit_price)),
                # Only set installation_option_id if it's a valid UUID; otherwise leave None (template IDs are strings)
                installation_option_id=(
                    uuid.UUID(add_item_dto.installation_option_id)
                    if add_item_dto.installation_option_id and _is_valid_uuid(add_item_dto.installation_option_id)
                    else None
                ),
                installation_option_name=installation_name,
                installation_price=installation_price,
                membership_plan_id=uuid.UUID(add_item_dto.membership_plan_id) if add_item_dto.membership_plan_id else None,
                discount_percentage=add_item_dto.discount_percentage or 0
            )
            
            # Add item to cart (this handles duplicate checking)
            updated_cart_entity = await self.cart_repository.add_item_to_cart(cart_uuid, cart_item_entity)
            
            # Convert back to DTO
            cart_dto = self._convert_cart_entity_to_dto(updated_cart_entity)
            
            logger.info(f"Added item to cart {cart_id}")
            return cart_dto
            
        except (EntityNotFoundError, ValidationError, BusinessRuleError):
            raise
        except Exception as e:
            logger.error(f"Error adding item to cart {cart_id}: {str(e)}")
            raise ApplicationError(f"Failed to add item to cart: {str(e)}")
    
    async def remove_item_from_cart(
        self,
        cart_id: str,
        item_id: str
    ) -> CartDTO:
        """
        Remove an item from the shopping cart.
        
        Args:
            cart_id: Cart identifier
            item_id: Item identifier to remove
            
        Returns:
            Updated cart DTO
            
        Raises:
            EntityNotFoundError: If cart or item doesn't exist
            ApplicationError: If operation fails
        """
        try:
            # Use repository to remove item
            updated_cart_entity = await self.cart_repository.remove_item_from_cart(
                uuid.UUID(cart_id), 
                uuid.UUID(item_id)
            )
            
            # Convert entity to DTO
            updated_cart_dto = self._convert_cart_entity_to_dto(updated_cart_entity)
            logger.info(f"Removed item {item_id} from cart {cart_id}")
            return updated_cart_dto
            
        except (EntityNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error removing item from cart {cart_id}: {str(e)}")
            raise ApplicationError(f"Failed to remove item from cart: {str(e)}")
    
    async def update_item_quantity(
        self,
        cart_id: str,
        item_id: str,
        quantity: int
    ) -> CartDTO:
        """
        Update the quantity of an item in the cart.
        
        Args:
            cart_id: Cart identifier
            item_id: Item identifier
            quantity: New quantity
            
        Returns:
            Updated cart DTO
            
        Raises:
            EntityNotFoundError: If cart or item doesn't exist
            ValidationError: If quantity is invalid
            ApplicationError: If operation fails
        """
        try:
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than 0")
            
            # Use repository to update item quantity
            updated_cart_entity = await self.cart_repository.update_item_quantity(
                uuid.UUID(cart_id), 
                uuid.UUID(item_id), 
                quantity
            )
            
            # Convert entity to DTO
            updated_cart_dto = self._convert_cart_entity_to_dto(updated_cart_entity)
            logger.info(f"Updated item {item_id} quantity to {quantity} in cart {cart_id}")
            return updated_cart_dto
            
        except (EntityNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating item quantity in cart {cart_id}: {str(e)}")
            raise ApplicationError(f"Failed to update item quantity: {str(e)}")
    
    async def clear_cart(
        self,
        cart_id: str
    ) -> CartDTO:
        """
        Clear all items from the shopping cart.
        
        Args:
            cart_id: Cart identifier
            
        Returns:
            Updated empty cart DTO
            
        Raises:
            EntityNotFoundError: If cart doesn't exist
            ApplicationError: If operation fails
        """
        try:
            # Get existing cart
            cart = await self.get_cart(cart_id)
            if not cart:
                raise EntityNotFoundError(f"Cart not found: {cart_id}")
            
            # Clear all items
            cart.items = []
            cart.subtotal = 0.0
            cart.tax_amount = 0.0
            cart.total = 0.0
            cart.updated_at = datetime.now(timezone.utc)
            
            # TODO: Save to repository
            logger.info(f"Cleared cart {cart_id}")
            return cart
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error clearing cart {cart_id}: {str(e)}")
            raise ApplicationError(f"Failed to clear cart: {str(e)}")
    
    def _recalculate_cart_totals(self, cart: CartDTO) -> CartDTO:
        """
        Recalculate cart totals based on items.
        
        Args:
            cart: Cart DTO to recalculate
            
        Returns:
            Cart DTO with updated totals
        """
        subtotal = Decimal("0")
        
        for item in cart.items:
            # Calculate item total
            item_product_total = Decimal(str(item.unit_price)) * item.quantity
            item_installation_total = Decimal(str(item.installation_price)) * item.quantity
            item_subtotal = item_product_total + item_installation_total
            
            # Apply discount if applicable
            if item.discount_percentage > 0:
                discount_amount = item_subtotal * (Decimal(str(item.discount_percentage)) / Decimal("100"))
                item_subtotal -= discount_amount
            
            subtotal += item_subtotal
        
        # Calculate tax (8% for now - should be configurable)
        tax_rate = Decimal("0.08")
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        cart.subtotal = float(subtotal)
        cart.tax_amount = float(tax_amount)
        cart.total = float(total)
        
        return cart
    
    def _convert_cart_entity_to_dto(self, cart_entity: CartEntity) -> CartDTO:
        """Convert cart entity to DTO."""
        item_dtos = []
        for item_entity in cart_entity.items:
            item_dto = CartItemDTO(
                id=str(item_entity.id),
                cart_id=str(item_entity.cart_id),
                product_id=str(item_entity.product_id),
                product_name=item_entity.product_name,
                product_sku=item_entity.product_sku,
                quantity=item_entity.quantity,
                unit_price=float(item_entity.unit_price),
                installation_option_id=str(item_entity.installation_option_id) if item_entity.installation_option_id else None,
                installation_name=item_entity.installation_option_name,
                installation_price=float(item_entity.installation_price),
                membership_plan_id=str(item_entity.membership_plan_id) if item_entity.membership_plan_id else None,
                discount_percentage=item_entity.discount_percentage,
                created_at=item_entity.created_at,
                updated_at=item_entity.updated_at
            )
            item_dtos.append(item_dto)
        
        return CartDTO(
            id=str(cart_entity.id),
            business_id=str(cart_entity.business_id),
            session_id=cart_entity.session_id,
            customer_id=cart_entity.customer_id,
            items=item_dtos,
            subtotal=float(cart_entity.calculate_subtotal()),
            tax_amount=float(cart_entity.calculate_tax_amount()),
            total=float(cart_entity.calculate_total()),
            created_at=cart_entity.created_at,
            updated_at=cart_entity.updated_at,
            expires_at=cart_entity.expires_at
        )
