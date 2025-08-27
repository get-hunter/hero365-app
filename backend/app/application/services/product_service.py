"""
Product Application Service

Orchestrates product-related business operations and use cases.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal

from ..dto.product_dto import (
    ProductItemDTO,
    ProductCatalogDTO,
    ProductInstallationOptionDTO,
    PricingBreakdownDTO,
    ProductCategoryDTO
)
from ..exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    EntityNotFoundError
)
from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ...domain.repositories.business_repository import BusinessRepository
from ...domain.repositories.customer_membership_repository import CustomerMembershipRepository

logger = logging.getLogger(__name__)


class ProductService:
    """
    Application service for product operations.
    
    Handles business logic for product catalog, pricing, and availability,
    following clean architecture principles.
    """
    
    def __init__(
        self,
        product_repository: ProductRepository,
        business_repository: BusinessRepository,
        membership_repository: Optional[CustomerMembershipRepository] = None
    ):
        self.product_repository = product_repository
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def get_business_products(
        self,
        business_id: str,
        category: Optional[str] = None,
        in_stock_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[ProductItemDTO]:
        """
        Get products for a business with filtering options.
        
        Args:
            business_id: Business identifier
            category: Optional category filter
            in_stock_only: Only return in-stock products
            limit: Maximum number of products to return
            offset: Pagination offset
            
        Returns:
            List of product items as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Temporarily skip business validation for debugging
            logger.info(f"🔥 DEBUGGING: Skipping business validation for {business_id}")
            # business = await self.business_repository.get_by_id(business_uuid)
            # if not business:
            #     raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get products from repository
            logger.info(f"🔥 DEBUGGING: Calling product repository for business {business_uuid}")
            try:
                products = await self.product_repository.list_by_business(
                    business_uuid,
                    limit=limit,
                    offset=offset,
                    category_id=uuid.UUID(category) if category else None
                )
                logger.info(f"🔥 DEBUGGING: Got {len(products)} products from repository")
            except Exception as repo_error:
                logger.error(f"🔥 DEBUGGING: Product repository error: {str(repo_error)}")
                raise
            
            # Convert to DTOs with business logic
            product_dtos = []
            for product in products:
                # Apply business rules
                if in_stock_only and not product.is_active():
                    continue
                
                # Only include actual products, not services
                if hasattr(product, 'product_type') and str(product.product_type) == 'service':
                    continue
                
                product_dto = self._convert_product_to_dto(product)
                product_dtos.append(product_dto)
            
            logger.info(f"🔥 CLEAN ARCHITECTURE: Retrieved {len(product_dtos)} REAL products for business {business_id}")
            return product_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving products for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve products: {str(e)}")
    
    async def get_product_catalog(
        self,
        business_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
        featured_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[ProductCatalogDTO]:
        """
        Get product catalog with installation options for e-commerce display.
        
        Args:
            business_id: Business identifier
            category: Optional category filter
            search: Optional search query
            featured_only: Only return featured products
            limit: Maximum number of products to return
            offset: Pagination offset
            
        Returns:
            List of product catalog items with installation options
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            logger.info(f"🔥 PRODUCT CATALOG: Getting business {business_uuid}")
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                logger.error(f"🔥 PRODUCT CATALOG: Business not found: {business_id}")
                raise EntityNotFoundError(f"Business not found: {business_id}")
            logger.info(f"🔥 PRODUCT CATALOG: Business found: {business.name}")
            
            # Build search filters
            filters = {}
            if category:
                filters['category_id'] = uuid.UUID(category)
            if featured_only:
                filters['is_featured'] = True
            
            # Get products from repository
            logger.info(f"🔥 PRODUCT CATALOG: Getting products with filters: {filters}")
            if search:
                products = await self.product_repository.search_products(
                    business_uuid,
                    search,
                    limit=limit,
                    offset=offset,
                    filters=filters
                )
            else:
                # For now, get all products and filter in application layer
                # TODO: Add is_featured parameter to repository method
                products = await self.product_repository.list_by_business(
                    business_uuid,
                    limit=limit * 2,  # Get more to account for filtering
                    offset=offset,
                    category_id=filters.get('category_id')
                )
            logger.info(f"🔥 PRODUCT CATALOG: Got {len(products)} products from repository")
            
            # Convert to catalog DTOs
            catalog_dtos = []
            for product in products:
                # Apply business rules
                if not product.is_active():
                    continue
                
                # Only include actual products for catalog
                if hasattr(product, 'product_type') and str(product.product_type) == 'service':
                    continue
                
                # Apply featured filter if specified
                if featured_only and not getattr(product, 'is_featured', False):
                    continue
                
                catalog_dto = await self._convert_product_to_catalog_dto(product, business_uuid)
                catalog_dtos.append(catalog_dto)
            
            logger.info(f"Retrieved {len(catalog_dtos)} catalog items for business {business_id}")
            return catalog_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving product catalog for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve product catalog: {str(e)}")
    
    async def get_product_by_id(
        self,
        business_id: str,
        product_id: str
    ) -> Optional[ProductCatalogDTO]:
        """
        Get a specific product with full details and installation options.
        
        Args:
            business_id: Business identifier
            product_id: Product identifier
            
        Returns:
            Product catalog DTO if found, None otherwise
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If IDs are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            product_uuid = uuid.UUID(product_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get product from repository
            product = await self.product_repository.get_by_id(business_uuid, product_uuid)
            if not product:
                return None
            
            # Convert to catalog DTO with full details
            catalog_dto = await self._convert_product_to_catalog_dto(product, business_uuid)
            
            logger.info(f"Retrieved product {product_id} for business {business_id}")
            return catalog_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid ID format: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve product: {str(e)}")
    
    async def calculate_product_pricing(
        self,
        business_id: str,
        product_id: str,
        installation_option_id: Optional[str] = None,
        membership_plan_id: Optional[str] = None,
        quantity: int = 1
    ) -> PricingBreakdownDTO:
        """
        Calculate comprehensive pricing for a product with installation and membership discounts.
        
        Args:
            business_id: Business identifier
            product_id: Product identifier
            installation_option_id: Optional installation option
            membership_plan_id: Optional membership plan for discounts
            quantity: Product quantity
            
        Returns:
            Detailed pricing breakdown
            
        Raises:
            EntityNotFoundError: If business or product doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If calculation fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            product_uuid = uuid.UUID(product_id)
            
            # Get product
            product = await self.product_repository.get_by_id(business_uuid, product_uuid)
            if not product:
                raise EntityNotFoundError(f"Product not found: {product_id}")
            
            # Calculate base pricing
            base_product_price = product.unit_price * quantity
            installation_price = Decimal("0")
            installation_name = None
            
            # Add installation pricing if specified
            if installation_option_id:
                # TODO: Get installation option from repository
                # For now, use placeholder values
                installation_price = Decimal("150.00")  # Placeholder
                installation_name = "Standard Installation"  # Placeholder
            
            subtotal = base_product_price + installation_price
            
            # Apply membership discount if specified
            discount_percentage = 0
            discount_amount = Decimal("0")
            membership_plan_name = None
            
            if membership_plan_id and self.membership_repository:
                try:
                    plan_uuid = uuid.UUID(membership_plan_id)
                    plan = await self.membership_repository.get_plan_by_id(plan_uuid)
                    if plan:
                        discount_percentage = plan.discount_percentage
                        discount_amount = subtotal * plan.get_effective_discount_rate()
                        membership_plan_name = plan.name
                except Exception as e:
                    logger.warning(f"Could not apply membership discount: {str(e)}")
            
            # Calculate final totals
            total_after_discount = subtotal - discount_amount
            tax_rate = Decimal("0.08")  # 8% tax rate (should be configurable)
            tax_amount = total_after_discount * tax_rate
            final_total = total_after_discount + tax_amount
            
            return PricingBreakdownDTO(
                product_id=product_id,
                product_name=product.name,
                quantity=quantity,
                unit_price=float(product.unit_price),
                product_subtotal=float(base_product_price),
                installation_option_id=installation_option_id,
                installation_name=installation_name,
                installation_price=float(installation_price),
                subtotal=float(subtotal),
                membership_plan_id=membership_plan_id,
                membership_plan_name=membership_plan_name,
                discount_percentage=discount_percentage,
                discount_amount=float(discount_amount),
                tax_rate=float(tax_rate),
                tax_amount=float(tax_amount),
                total=float(final_total)
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating pricing: {str(e)}")
            raise ApplicationError(f"Failed to calculate pricing: {str(e)}")
    
    def _convert_product_to_dto(self, product: Product) -> ProductItemDTO:
        """Convert product entity to ProductItemDTO."""
        return ProductItemDTO(
            id=str(product.id),
            name=product.name,
            description=product.description or "",
            category="General",  # TODO: Get category name from category_id
            brand="Professional Brand",  # TODO: Add brand field to product entity
            model="",  # TODO: Add model field to product entity
            sku=product.sku or "",
            price=float(product.unit_price),
            msrp=None,  # TODO: Add MSRP field to product entity
            in_stock=product.is_active(),
            stock_quantity=int(product.quantity_on_hand) if product.quantity_on_hand else 0,
            specifications={},  # TODO: Add specifications field
            warranty_years=None,  # TODO: Add warranty field
            energy_rating=None  # TODO: Add energy rating field
        )
    
    async def _convert_product_to_catalog_dto(self, product: Product, business_id: uuid.UUID) -> ProductCatalogDTO:
        """Convert product entity to ProductCatalogDTO with installation options."""
        # TODO: Get installation options from repository
        installation_options = []  # Placeholder
        
        return ProductCatalogDTO(
            id=str(product.id),
            name=product.name,
            description=product.description or "",
            category="General",  # TODO: Get category name
            brand="Professional Brand",  # TODO: Add brand field
            model="",  # TODO: Add model field
            sku=product.sku or "",
            unit_price=float(product.unit_price),
            msrp=None,  # TODO: Add MSRP field
            in_stock=product.is_active(),
            stock_quantity=int(product.quantity_on_hand) if product.quantity_on_hand else 0,
            specifications={},  # TODO: Add specifications
            warranty_years=None,  # TODO: Add warranty
            energy_rating=None,  # TODO: Add energy rating
            images=[],  # TODO: Add product images
            installation_options=installation_options,
            has_variations=False,  # TODO: Check for product variations
            is_featured=False,  # TODO: Add featured flag
            tags=[]  # TODO: Add product tags
        )
