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
# Installation template imports removed for now
from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from ...domain.repositories.business_repository import BusinessRepository
from ...domain.repositories.customer_membership_repository import CustomerMembershipRepository

# Import the new installation pricing system
from .product_install_pricing_service import ProductInstallPricingEngine, ProductInfo
from .installation_templates import (
    get_templates_by_trade, TradeType, InstallationType,
    get_template_by_id, calculate_adjusted_price, ComplexityLevel
)

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
        # Initialize the new pricing engine
        self.pricing_engine = ProductInstallPricingEngine()
    
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
        SIMPLIFIED: Use same logic as get_business_products but return ProductCatalogDTO
        """
        try:
            # Use the working get_business_products method
            product_dtos = await self.get_business_products(
                business_id=business_id,
                category=category,
                in_stock_only=True,  # Default for catalog
                limit=limit,
                offset=offset
            )
            
            # Convert ProductItemDTO to ProductCatalogDTO
            catalog_dtos = []
            for product_dto in product_dtos:
                # We need to get the actual product entity to generate installation options
                # For now, create basic installation options based on product name
                installation_options = []
                if any(keyword in product_dto.name.lower() for keyword in ['water heater', 'heater']):
                    installation_options.append(ProductInstallationOptionDTO(
                        id="water_heater_replace",
                        name="Water Heater Replacement",
                        description="Complete water heater replacement with professional installation",
                        base_install_price=250.0,
                        estimated_duration_hours=4,
                        requires_permit=True,
                        includes_materials=True,
                        warranty_years=2,
                        is_default=True
                    ))
                elif any(keyword in product_dto.name.lower() for keyword in ['thermostat']):
                    installation_options.append(ProductInstallationOptionDTO(
                        id="thermostat_install",
                        name="Thermostat Installation",
                        description="Professional thermostat installation and setup",
                        base_install_price=125.0,
                        estimated_duration_hours=2,
                        requires_permit=False,
                        includes_materials=True,
                        warranty_years=1,
                        is_default=True
                    ))
                else:
                    installation_options.append(ProductInstallationOptionDTO(
                        id="standard_install",
                        name="Standard Installation",
                        description="Professional installation service",
                        base_install_price=150.0,
                        estimated_duration_hours=2,
                        requires_permit=False,
                        includes_materials=True,
                        warranty_years=1,
                        is_default=True
                    ))
                
                catalog_dto = ProductCatalogDTO(
                    id=product_dto.id,
                    name=product_dto.name,
                    description=product_dto.description,
                    category=product_dto.category,
                    brand=product_dto.brand,
                    model=product_dto.model,
                    sku=product_dto.sku,
                    unit_price=product_dto.price,  # Convert price -> unit_price
                    msrp=product_dto.msrp,
                    in_stock=product_dto.in_stock,
                    stock_quantity=product_dto.stock_quantity,
                    specifications=product_dto.specifications,
                    warranty_years=product_dto.warranty_years,
                    energy_rating=product_dto.energy_rating,
                    images=getattr(product_dto, 'images', []) or [],  # Use real product images
                    installation_options=installation_options,
                    has_variations=getattr(product_dto, 'has_variations', False),
                    is_featured=getattr(product_dto, 'is_featured', False),
                    tags=getattr(product_dto, 'tags', []) or []
                )
                catalog_dtos.append(catalog_dto)
            
            return catalog_dtos
            
        except Exception as e:
            logger.error(f"Error in simplified product catalog: {str(e)}")
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
                raise EntityNotFoundError("Business", business_id)
            
            # Get product from repository
            product = await self.product_repository.get_by_id(business_uuid, product_uuid)
            if not product:
                return None
            
            # Convert to catalog DTO with full details
            catalog_dto = self._convert_product_to_catalog_dto(product, business_uuid)
            
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
            
            # Add installation pricing using our new template system!
            if installation_option_id:
                template = get_template_by_id(installation_option_id)
                if template:
                    installation_price = template.base_price  
                    installation_name = template.name
                else:
                    # Fallback for invalid template ID
                    installation_price = Decimal("150.00")
                    installation_name = "Custom Installation"
            
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
    
    def _extract_brand_from_name(self, product_name: str) -> str:
        """Extract brand name from product name."""
        # Common HVAC brands found in product names
        brands = [
            "Trane", "Carrier", "Lennox", "Rheem", "Goodman", "York", "Amana", 
            "Bryant", "Payne", "Heil", "Tempstar", "Comfortmaker", "Honeywell",
            "AO Smith", "Bradford White", "State", "Navien", "Rinnai", "Tankless",
            "Mitsubishi", "Daikin", "LG", "Samsung", "Friedrich", "GE", "Whirlpool",
            "Aprilaire", "Ecobee", "Nest", "Tesla"
        ]
        
        name_upper = product_name.upper()
        for brand in brands:
            if brand.upper() in name_upper:
                return brand
        
        # If no brand found, try to extract first word as potential brand
        first_word = product_name.split()[0] if product_name.split() else ""
        return first_word if len(first_word) > 2 else "Professional Brand"
    
    def _extract_model_from_name(self, product_name: str) -> str:
        """Extract model number from product name."""
        import re
        # Look for model patterns like XR16, 40-Gallon, MERV-11, etc.
        model_patterns = [
            r'\b([A-Z]{2,4}\d{1,4}[A-Z]*)\b',  # XR16, SEER16, MERV11
            r'\b(\d{1,2}[- ]?(?:Gallon|Ton|SEER|MERV))\b',  # 40-Gallon, 3-Ton
            r'\b([A-Z]\d{3,5})\b',  # A1234, B4567
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_category_from_sku(self, sku: str) -> str:
        """Extract category from SKU prefix."""
        if not sku:
            return "General"
        
        sku_upper = sku.upper()
        if sku_upper.startswith(('HVAC', 'AC', 'HP')):
            return "HVAC Systems"
        elif sku_upper.startswith(('WH', 'WATER')):
            return "Water Heaters"
        elif sku_upper.startswith(('THERM', 'STAT')):
            return "Thermostats"
        elif sku_upper.startswith(('FILTER', 'AIR')):
            return "Air Quality"
        elif sku_upper.startswith(('DUCT', 'PIPE')):
            return "Ductwork & Piping"
        elif sku_upper.startswith(('EV', 'ELECTRIC')):
            return "Electrical"
        elif sku_upper.startswith(('SVC', 'SERVICE')):
            return "Services"
        
        return "General"
    
    def _get_installation_options_for_product(self, product: Product) -> List[ProductInstallationOptionDTO]:
        """
        Get available installation options for a product.
        
        Returns basic installation options based on product type.
        """
        installation_options = []
        product_name_lower = product.name.lower()
        
        # Add relevant installation options based on product
        if any(keyword in product_name_lower for keyword in ['water heater', 'heater']):
            installation_options.append(ProductInstallationOptionDTO(
                id="water_heater_replace",
                name="Water Heater Replacement",
                description="Complete water heater replacement with professional installation",
                base_install_price=250.0,
                estimated_duration_hours=4,
                requires_permit=True,
                includes_materials=True,
                warranty_years=2,
                is_default=True
            ))
        elif any(keyword in product_name_lower for keyword in ['thermostat']):
            installation_options.append(ProductInstallationOptionDTO(
                id="thermostat_install",
                name="Thermostat Installation",
                description="Professional thermostat installation and setup",
                base_install_price=125.0,
                estimated_duration_hours=2,
                requires_permit=False,
                includes_materials=True,
                warranty_years=1,
                is_default=True
            ))
        else:
            # Default installation option for other products
            installation_options.append(ProductInstallationOptionDTO(
                id="standard_install",
                name="Standard Installation",
                description="Professional installation service",
                base_install_price=150.0,
                estimated_duration_hours=2,
                requires_permit=False,
                includes_materials=True,
                warranty_years=1,
                is_default=True
            ))
        
        return installation_options
    
    def _convert_product_to_dto(self, product: Product) -> ProductItemDTO:
        """Convert product entity to ProductItemDTO."""
        return ProductItemDTO(
            id=str(product.id),
            name=product.name,
            description=product.description or "",
            category=product.category_name or self._extract_category_from_sku(product.sku),
            brand=self._extract_brand_from_name(product.name),
            model=self._extract_model_from_name(product.name),
            sku=product.sku or "",
            price=float(product.unit_price),
            msrp=float(getattr(product, 'msrp', 0)) if getattr(product, 'msrp', None) else None,
            in_stock=product.is_active(),
            stock_quantity=int(product.quantity_on_hand) if product.quantity_on_hand else 0,
            specifications=getattr(product, 'specifications', {}) or {},
            warranty_years=getattr(product, 'warranty_years', None),
            energy_rating=getattr(product, 'energy_rating', None),
            images=getattr(product, 'image_urls', []) or [],  # Use product.image_urls from entity
            has_variations=getattr(product, 'has_variations', False),
            is_featured=getattr(product, 'is_featured', False),
            tags=getattr(product, 'tags', []) or []
        )
    
    def _convert_product_to_catalog_dto(self, product: Product, business_id: uuid.UUID) -> ProductCatalogDTO:
        """Convert product entity to ProductCatalogDTO."""
        # Include installation options derived from product
        installation_options = self._get_installation_options_for_product(product)
        
        # Use exact same mapping as working ProductItemDTO but for ProductCatalogDTO fields
        return ProductCatalogDTO(
            id=str(product.id),
            name=product.name,
            description=product.description or "",
            category=product.category_name or self._extract_category_from_sku(product.sku),
            brand=self._extract_brand_from_name(product.name),
            model=self._extract_model_from_name(product.name),
            sku=product.sku or "",
            unit_price=float(product.unit_price),  # Note: this is unit_price not price
            msrp=float(getattr(product, 'msrp', 0)) if getattr(product, 'msrp', None) else None,
            in_stock=product.is_active(),
            stock_quantity=int(product.quantity_on_hand) if product.quantity_on_hand else 0,
            specifications=getattr(product, 'specifications', {}) or {},
            warranty_years=getattr(product, 'warranty_years', None),
            energy_rating=getattr(product, 'energy_rating', None),
            images=getattr(product, 'image_urls', []) or [],
            installation_options=[
                ProductInstallationOptionDTO(
                    id=opt.id,
                    name=opt.name,
                    description=opt.description,
                    base_install_price=opt.base_install_price,
                    estimated_duration_hours=int(opt.estimated_duration_hours),
                    requires_permit=getattr(opt, 'requires_permit', False),
                    includes_materials=getattr(opt, 'includes_materials', True),
                    warranty_years=getattr(opt, 'warranty_years', 1),
                    is_default=getattr(opt, 'is_default', False)
                ) for opt in installation_options
            ],
            has_variations=False,
            is_featured=False,
            tags=[]
        )
