"""
Product + Installation Pricing Engine

This service handles complex pricing calculations for products with installation services,
including membership discounts, bundle pricing, and various pricing models.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MembershipType(str, Enum):
    """Customer membership types"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial" 
    PREMIUM = "premium"


class PriceDisplayType(str, Enum):
    """Price display types"""
    FIXED = "fixed"
    FROM = "from"
    QUOTE_REQUIRED = "quote_required"
    FREE = "free"


@dataclass
class ProductInfo:
    """Product information for pricing calculations"""
    id: str
    name: str
    sku: str
    unit_price: Decimal
    cost_price: Optional[Decimal] = None
    requires_professional_install: bool = False
    install_complexity: str = "standard"
    warranty_years: int = 1
    is_taxable: bool = True
    tax_rate: Optional[Decimal] = None


@dataclass
class InstallationOption:
    """Installation option information"""
    id: str
    option_name: str
    description: str
    base_install_price: Decimal
    complexity_multiplier: Decimal = Decimal('1.0')
    estimated_duration_hours: Decimal = Decimal('2.0')
    
    # Membership-specific pricing (optional)
    residential_install_price: Optional[Decimal] = None
    commercial_install_price: Optional[Decimal] = None
    premium_install_price: Optional[Decimal] = None
    
    # Requirements and details
    requirements: Dict[str, Any] = None
    included_in_install: List[str] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}
        if self.included_in_install is None:
            self.included_in_install = []


@dataclass 
class PricingCalculation:
    """Complete pricing breakdown for product + installation"""
    # Base pricing
    product_unit_price: Decimal
    installation_base_price: Decimal
    quantity: int
    
    # Subtotals before discounts
    product_subtotal: Decimal
    installation_subtotal: Decimal
    subtotal_before_discounts: Decimal
    
    # Membership discounts
    membership_type: Optional[MembershipType]
    product_discount_amount: Decimal = Decimal('0')
    installation_discount_amount: Decimal = Decimal('0')
    total_discount_amount: Decimal = Decimal('0')
    
    # Final pricing
    product_final_price: Decimal = Decimal('0')
    installation_final_price: Decimal = Decimal('0')
    subtotal_after_discounts: Decimal = Decimal('0')
    
    # Tax calculations
    tax_rate: Decimal = Decimal('0')
    tax_amount: Decimal = Decimal('0')
    
    # Final total
    total_amount: Decimal = Decimal('0')
    
    # Savings information
    total_savings: Decimal = Decimal('0')
    savings_percentage: Decimal = Decimal('0')
    
    # Price display information
    price_display_type: PriceDisplayType = PriceDisplayType.FIXED
    formatted_display_price: str = ""
    
    # Bundle information
    is_bundle: bool = True  # Always true for product + installation
    bundle_savings: Decimal = Decimal('0')
    
    def __post_init__(self):
        """Calculate derived fields"""
        self.total_discount_amount = self.product_discount_amount + self.installation_discount_amount
        self.product_final_price = self.product_subtotal - self.product_discount_amount
        self.installation_final_price = self.installation_subtotal - self.installation_discount_amount
        self.subtotal_after_discounts = self.product_final_price + self.installation_final_price
        self.total_amount = self.subtotal_after_discounts + self.tax_amount
        self.total_savings = self.total_discount_amount
        
        if self.subtotal_before_discounts > 0:
            self.savings_percentage = (self.total_savings / self.subtotal_before_discounts * 100).quantize(
                Decimal('0.1'), rounding=ROUND_HALF_UP
            )


class ProductInstallPricingEngine:
    """
    Advanced pricing engine for product + installation combinations
    
    This engine handles:
    - Product pricing with volume discounts
    - Installation pricing with complexity multipliers
    - Membership-based discounts
    - Bundle savings
    - Tax calculations
    - Price display formatting
    """
    
    def __init__(self):
        self.default_tax_rate = Decimal('0.0825')  # 8.25% default tax rate
        
    def calculate_combined_pricing(
        self,
        product: ProductInfo,
        installation_option: Optional[InstallationOption],
        quantity: int = 1,
        membership_type: Optional[MembershipType] = None,
        tax_rate: Optional[Decimal] = None,
        apply_bundle_discount: bool = True
    ) -> PricingCalculation:
        """
        Calculate complete pricing for product + installation combination
        
        Args:
            product: Product information
            installation_option: Installation option details
            quantity: Number of units
            membership_type: Customer membership level
            tax_rate: Override tax rate
            apply_bundle_discount: Apply bundle savings for buying together
            
        Returns:
            Complete pricing breakdown
        """
        
        logger.debug(f"Calculating pricing for {product.name} + {installation_option.option_name if installation_option else 'No Installation'}")
        
        # Calculate base pricing
        product_subtotal = product.unit_price * quantity
        installation_subtotal = self._calculate_installation_pricing(
            installation_option, quantity
        )
        subtotal_before_discounts = product_subtotal + installation_subtotal
        
        # Calculate membership discounts
        product_discount, installation_discount = self._calculate_membership_discounts(
            product, installation_option, product_subtotal, installation_subtotal, membership_type
        )
        
        # Apply bundle discount if applicable
        bundle_discount = Decimal('0')
        if apply_bundle_discount:
            bundle_discount = self._calculate_bundle_discount(
                product_subtotal, installation_subtotal
            )
            # Apply bundle discount proportionally
            bundle_product_discount = bundle_discount * (product_subtotal / subtotal_before_discounts)
            bundle_install_discount = bundle_discount * (installation_subtotal / subtotal_before_discounts)
            product_discount += bundle_product_discount
            installation_discount += bundle_install_discount
        
        # Calculate tax
        effective_tax_rate = tax_rate or product.tax_rate or self.default_tax_rate
        subtotal_after_discounts = (product_subtotal - product_discount) + (installation_subtotal - installation_discount)
        tax_amount = self._calculate_tax(subtotal_after_discounts, effective_tax_rate, product.is_taxable)
        
        # Determine price display type
        price_display_type = self._determine_price_display_type(product, installation_option)
        
        # Create pricing calculation
        calculation = PricingCalculation(
            product_unit_price=product.unit_price,
            installation_base_price=installation_option.base_install_price if installation_option else Decimal('0'),
            quantity=quantity,
            product_subtotal=product_subtotal,
            installation_subtotal=installation_subtotal,
            subtotal_before_discounts=subtotal_before_discounts,
            membership_type=membership_type,
            product_discount_amount=product_discount,
            installation_discount_amount=installation_discount,
            tax_rate=effective_tax_rate,
            tax_amount=tax_amount,
            price_display_type=price_display_type,
            bundle_savings=bundle_discount
        )
        
        # Format display price
        calculation.formatted_display_price = self._format_display_price(
            calculation, price_display_type
        )
        
        logger.debug(f"Pricing calculated: ${calculation.total_amount} (saved ${calculation.total_savings})")
        
        return calculation
    
    def _calculate_installation_pricing(
        self,
        installation_option: Optional[InstallationOption],
        quantity: int
    ) -> Decimal:
        """Calculate installation pricing with complexity multipliers"""
        
        # If no installation option, return 0
        if not installation_option:
            return Decimal('0')
            
        base_price = installation_option.base_install_price
        complexity_multiplier = installation_option.complexity_multiplier or Decimal('1.0')
        
        # Installation pricing often has economies of scale
        # Multiple units might not require full installation price each
        if quantity == 1:
            return base_price * complexity_multiplier
        elif quantity <= 3:
            # Slight discount for multiple units
            return (base_price * complexity_multiplier * quantity * Decimal('0.9'))
        else:
            # Larger discount for volume installations
            return (base_price * complexity_multiplier * quantity * Decimal('0.8'))
    
    def _calculate_membership_discounts(
        self,
        product: ProductInfo,
        installation_option: InstallationOption,
        product_subtotal: Decimal,
        installation_subtotal: Decimal,
        membership_type: Optional[MembershipType]
    ) -> tuple[Decimal, Decimal]:
        """Calculate membership-based discounts for product and installation"""
        
        if not membership_type:
            return Decimal('0'), Decimal('0')
        
        # Get membership discount percentages
        product_discount_rate = self._get_membership_discount_rate(membership_type, 'product')
        installation_discount_rate = self._get_membership_discount_rate(membership_type, 'installation')
        
        # Check for specific membership pricing on installation
        installation_discount = self._get_specific_membership_installation_price(
            installation_option, installation_subtotal, membership_type
        )
        
        # If no specific pricing, use percentage discount
        if installation_discount == Decimal('0'):
            installation_discount = installation_subtotal * installation_discount_rate
        
        # Product discount (always percentage-based)
        product_discount = product_subtotal * product_discount_rate
        
        return product_discount, installation_discount
    
    def _get_specific_membership_installation_price(
        self,
        installation_option: InstallationOption,
        calculated_price: Decimal,
        membership_type: MembershipType
    ) -> Decimal:
        """Get specific membership pricing if available"""
        
        specific_price = None
        
        if membership_type == MembershipType.RESIDENTIAL:
            specific_price = installation_option.residential_install_price
        elif membership_type == MembershipType.COMMERCIAL:
            specific_price = installation_option.commercial_install_price
        elif membership_type == MembershipType.PREMIUM:
            specific_price = installation_option.premium_install_price
        
        if specific_price and specific_price < calculated_price:
            return calculated_price - specific_price
            
        return Decimal('0')
    
    def _get_membership_discount_rate(self, membership_type: MembershipType, item_type: str) -> Decimal:
        """Get discount rate for membership type"""
        
        # Standard membership discount rates
        discount_rates = {
            MembershipType.RESIDENTIAL: {
                'product': Decimal('0.10'),      # 10% off products
                'installation': Decimal('0.15')  # 15% off installation
            },
            MembershipType.COMMERCIAL: {
                'product': Decimal('0.15'),      # 15% off products
                'installation': Decimal('0.20')  # 20% off installation
            },
            MembershipType.PREMIUM: {
                'product': Decimal('0.20'),      # 20% off products
                'installation': Decimal('0.25')  # 25% off installation
            }
        }
        
        return discount_rates.get(membership_type, {}).get(item_type, Decimal('0'))
    
    def _calculate_bundle_discount(self, product_subtotal: Decimal, installation_subtotal: Decimal) -> Decimal:
        """Calculate additional discount for buying product + installation together"""
        
        # Bundle discount: 5% additional discount when buying product + installation
        bundle_discount_rate = Decimal('0.05')  # 5%
        total = product_subtotal + installation_subtotal
        
        # Only apply bundle discount for orders over $500
        if total >= 500:
            return total * bundle_discount_rate
            
        return Decimal('0')
    
    def _calculate_tax(self, subtotal: Decimal, tax_rate: Decimal, is_taxable: bool) -> Decimal:
        """Calculate tax amount"""
        
        if not is_taxable or not tax_rate:
            return Decimal('0')
            
        return (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _determine_price_display_type(
        self, 
        product: ProductInfo, 
        installation_option: InstallationOption
    ) -> PriceDisplayType:
        """Determine how to display the price"""
        
        # Complex installations often require quotes
        if product.install_complexity == 'expert':
            return PriceDisplayType.QUOTE_REQUIRED
        
        # If installation has complex requirements, show "from" pricing
        if (installation_option and installation_option.requirements and 
            any(key in installation_option.requirements for key in ['permit', 'electrical_upgrade', 'special_access'])):
            return PriceDisplayType.FROM
        
        # Free services
        if product.unit_price == 0 and (not installation_option or installation_option.base_install_price == 0):
            return PriceDisplayType.FREE
        
        # Default to fixed pricing
        return PriceDisplayType.FIXED
    
    def _format_display_price(self, calculation: PricingCalculation, display_type: PriceDisplayType) -> str:
        """Format price for display"""
        
        total = calculation.total_amount
        
        if display_type == PriceDisplayType.FREE:
            return "FREE"
        elif display_type == PriceDisplayType.QUOTE_REQUIRED:
            return "Quote Required"
        elif display_type == PriceDisplayType.FROM:
            return f"from ${total:,.0f}"
        else:
            return f"${total:,.0f}"
    
    def calculate_volume_pricing(
        self,
        product: ProductInfo,
        installation_option: InstallationOption,
        quantities: List[int],
        membership_type: Optional[MembershipType] = None
    ) -> List[PricingCalculation]:
        """Calculate pricing for multiple quantity tiers"""
        
        return [
            self.calculate_combined_pricing(
                product, installation_option, qty, membership_type
            ) for qty in quantities
        ]
    
    def get_membership_savings(
        self,
        product: ProductInfo,
        installation_option: InstallationOption,
        quantity: int = 1,
        membership_type: MembershipType = MembershipType.RESIDENTIAL
    ) -> Dict[str, Decimal]:
        """Calculate potential membership savings"""
        
        # Calculate pricing without membership
        non_member_pricing = self.calculate_combined_pricing(
            product, installation_option, quantity, None
        )
        
        # Calculate pricing with membership
        member_pricing = self.calculate_combined_pricing(
            product, installation_option, quantity, membership_type
        )
        
        total_savings = non_member_pricing.total_amount - member_pricing.total_amount
        percentage_savings = (total_savings / non_member_pricing.total_amount * 100) if non_member_pricing.total_amount > 0 else Decimal('0')
        
        return {
            'non_member_total': non_member_pricing.total_amount,
            'member_total': member_pricing.total_amount,
            'total_savings': total_savings,
            'percentage_savings': percentage_savings.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP),
            'membership_type': membership_type
        }


# Convenience functions for common use cases
def calculate_product_install_price(
    product_price: Decimal,
    install_price: Decimal,
    membership_type: Optional[str] = None,
    quantity: int = 1
) -> Dict[str, Any]:
    """Simple function for basic product + install pricing"""
    
    engine = ProductInstallPricingEngine()
    
    # Create basic product and installation objects
    product = ProductInfo(
        id="temp",
        name="Product",
        sku="TEMP",
        unit_price=product_price
    )
    
    installation = InstallationOption(
        id="temp",
        option_name="Installation",
        description="Standard installation",
        base_install_price=install_price
    )
    
    membership = MembershipType(membership_type) if membership_type else None
    
    calculation = engine.calculate_combined_pricing(
        product, installation, quantity, membership
    )
    
    return {
        'subtotal': float(calculation.subtotal_before_discounts),
        'total_discount': float(calculation.total_discount_amount),
        'final_price': float(calculation.total_amount),
        'savings': float(calculation.total_savings),
        'formatted_price': calculation.formatted_display_price
    }
