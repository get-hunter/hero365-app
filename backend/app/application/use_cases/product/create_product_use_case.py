"""
Create Product Use Case

Handles the creation of new products with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.product_category_repository import ProductCategoryRepository
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.product_dto import CreateProductDTO, ProductDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class CreateProductUseCase:
    """Use case for creating new products."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: Optional[ProductCategoryRepository] = None,
        supplier_repository: Optional[SupplierRepository] = None
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.supplier_repository = supplier_repository
    
    async def execute(self, request: CreateProductDTO, user_id: str, business_id: uuid.UUID) -> ProductDTO:
        """Execute the create product use case."""
        try:
            logger.info(f"Creating product for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate and get related entities
            category = await self._validate_and_get_category(request.category_id, business_id)
            supplier = await self._validate_and_get_supplier(request.primary_supplier_id, business_id)
            
            # Check for duplicate SKU
            if await self.product_repository.exists_by_sku(business_id, request.sku):
                raise AppValidationError(f"Product with SKU '{request.sku}' already exists")
            
            # Create the product entity
            product = Product(
                id=uuid.uuid4(),
                business_id=business_id,
                sku=request.sku,
                name=request.name,
                description=request.description,
                product_type=request.product_type,
                status=request.status,
                category_id=request.category_id,
                pricing_model=request.pricing_model,
                unit_price=request.unit_price,
                unit_cost=request.cost_price,
                average_cost=request.cost_price,
                markup_percentage=request.markup_percentage,
                unit_of_measure=request.unit_of_measure,
                weight=request.weight,
                weight_unit=request.weight_unit,
                dimensions=request.dimensions,
                track_inventory=request.track_inventory,
                quantity_on_hand=request.initial_quantity,
                reorder_point=request.reorder_point,
                reorder_quantity=request.reorder_quantity,
                minimum_quantity=request.minimum_quantity,
                maximum_quantity=request.maximum_quantity,
                costing_method=request.costing_method,
                tax_rate=request.tax_rate or Decimal('0'),
                tax_code=request.tax_code,
                is_taxable=request.is_taxable,
                primary_supplier_id=request.primary_supplier_id,
                barcode=request.barcode,
                manufacturer=request.manufacturer,
                manufacturer_sku=request.manufacturer_sku,
                brand=request.brand,
                image_urls=request.image_urls or [],
                created_by=user_id,
                created_date=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
            
            # Apply category defaults if category is specified
            if category:
                self._apply_category_defaults(product, category)
            
            # Validate business rules
            self._validate_business_rules(product)
            
            # Save the product
            created_product = await self.product_repository.create(product)
            
            logger.info(f"Successfully created product {created_product.id} with SKU {created_product.sku}")
            
            return ProductDTO.from_entity(created_product)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error creating product: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation creating product: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found creating product: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating product: {e}")
            raise ApplicationError(f"Failed to create product: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to create products in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can create products
        pass
    
    async def _validate_and_get_category(self, category_id: Optional[uuid.UUID], business_id: uuid.UUID):
        """Validate and retrieve the product category."""
        if not category_id or not self.category_repository:
            return None
        
        category = await self.category_repository.get_by_id(business_id, category_id)
        if not category:
            raise EntityNotFoundError(f"Product category with ID {category_id} not found")
        
        if not category.is_active:
            raise BusinessRuleViolationError("Product category is not active")
        
        return category
    
    async def _validate_and_get_supplier(self, supplier_id: Optional[uuid.UUID], business_id: uuid.UUID):
        """Validate and retrieve the supplier."""
        if not supplier_id or not self.supplier_repository:
            return None
        
        supplier = await self.supplier_repository.get_by_id(business_id, supplier_id)
        if not supplier:
            raise EntityNotFoundError(f"Supplier with ID {supplier_id} not found")
        
        if not supplier.is_active:
            raise BusinessRuleViolationError("Supplier is not active")
        
        return supplier
    
    def _apply_category_defaults(self, product: Product, category) -> None:
        """Apply category defaults to the product."""
        if hasattr(category, 'defaults') and category.defaults:
            defaults = category.defaults
            
            # Apply tax defaults if not explicitly set
            if product.tax_rate == Decimal('0') and defaults.default_tax_rate:
                product.tax_rate = defaults.default_tax_rate
            
            # Apply markup defaults if not explicitly set
            if not product.markup_percentage and defaults.default_markup_percentage:
                product.markup_percentage = defaults.default_markup_percentage
                # Recalculate unit price based on markup
                if product.unit_cost > 0:
                    markup_factor = Decimal('1') + (defaults.default_markup_percentage / Decimal('100'))
                    product.unit_price = product.unit_cost * markup_factor
            
            # Apply unit of measure default if not explicitly set
            if product.unit_of_measure.value == "each" and defaults.default_unit_of_measure:
                from app.domain.enums import UnitOfMeasure
                try:
                    product.unit_of_measure = UnitOfMeasure(defaults.default_unit_of_measure)
                except ValueError:
                    # If invalid unit of measure in defaults, keep the existing one
                    pass
            
            # Apply inventory tracking default
            if defaults.track_inventory_default is not None:
                product.track_inventory = defaults.track_inventory_default
    
    def _validate_business_rules(self, product: Product) -> None:
        """Validate business rules for the product."""
        # Validate pricing rules
        if product.unit_price < 0:
            raise BusinessRuleViolationError("Unit price cannot be negative")
        
        if product.unit_cost < 0:
            raise BusinessRuleViolationError("Unit cost cannot be negative")
        
        # Validate markup percentage if set
        if product.markup_percentage is not None and product.markup_percentage < 0:
            raise BusinessRuleViolationError("Markup percentage cannot be negative")
        
        # Validate inventory quantities
        if product.quantity_on_hand < 0:
            raise BusinessRuleViolationError("Initial quantity cannot be negative")
        
        if product.reorder_point is not None and product.reorder_point < 0:
            raise BusinessRuleViolationError("Reorder point cannot be negative")
        
        if product.reorder_quantity is not None and product.reorder_quantity <= 0:
            raise BusinessRuleViolationError("Reorder quantity must be positive")
        
        # Validate minimum/maximum quantities
        if (product.minimum_quantity is not None and 
            product.maximum_quantity is not None and 
            product.minimum_quantity > product.maximum_quantity):
            raise BusinessRuleViolationError("Minimum quantity cannot be greater than maximum quantity")
        
        # Validate reorder rules
        if (product.reorder_point is not None and 
            product.minimum_quantity is not None and 
            product.reorder_point < product.minimum_quantity):
            raise BusinessRuleViolationError("Reorder point should be at least the minimum quantity")
        
        # Validate weight
        if product.weight is not None and product.weight < 0:
            raise BusinessRuleViolationError("Weight cannot be negative")
        
        # Validate tax rate
        if product.tax_rate < 0 or product.tax_rate > 100:
            raise BusinessRuleViolationError("Tax rate must be between 0 and 100 percent")
        
        # Validate inventory tracking consistency
        if not product.track_inventory and (
            product.reorder_point is not None or 
            product.reorder_quantity is not None or
            product.minimum_quantity is not None or
            product.maximum_quantity is not None
        ):
            raise BusinessRuleViolationError(
                "Cannot set inventory thresholds when inventory tracking is disabled"
            ) 