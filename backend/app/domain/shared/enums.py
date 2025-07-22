"""
Shared Domain Enums

Enums that are used across multiple domains and entities.
These represent cross-cutting concerns like currency, tax, and pricing.
"""

from enum import Enum


class CurrencyCode(str, Enum):
    """Currency code enumeration (ISO 4217)."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    CNY = "CNY"
    MXN = "MXN"
    BRL = "BRL"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.USD: "US Dollar",
            self.EUR: "Euro",
            self.GBP: "British Pound",
            self.CAD: "Canadian Dollar", 
            self.AUD: "Australian Dollar",
            self.JPY: "Japanese Yen",
            self.CHF: "Swiss Franc",
            self.CNY: "Chinese Yuan",
            self.MXN: "Mexican Peso",
            self.BRL: "Brazilian Real"
        }
        return display_map.get(self, self.value)


class TaxType(str, Enum):
    """Tax type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Tax",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount",
            self.INCLUSIVE: "Tax Inclusive",
            self.EXCLUSIVE: "Tax Exclusive"
        }
        return display_map.get(self, self.value.title())


class DiscountType(str, Enum):
    """Discount type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Discount",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount"
        }
        return display_map.get(self, self.value.title())


class AdvancePaymentType(str, Enum):
    """Advance payment type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Advance Payment",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount"
        }
        return display_map.get(self, self.value.title())


class TemplateType(str, Enum):
    """Template type enumeration."""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    MODERN = "modern"
    CLASSIC = "classic"
    INDUSTRIAL = "industrial"
    SERVICE_FOCUSED = "service_focused"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROFESSIONAL: "Professional",
            self.CREATIVE: "Creative",
            self.MINIMAL: "Minimal",
            self.CORPORATE: "Corporate",
            self.MODERN: "Modern",
            self.CLASSIC: "Classic",
            self.INDUSTRIAL: "Industrial",
            self.SERVICE_FOCUSED: "Service Focused"
        }
        return display_map.get(self, self.value.title())


class PricingModel(str, Enum):
    """Pricing model enumeration."""
    FIXED = "fixed"
    HOURLY = "hourly"
    PER_UNIT = "per_unit"
    TIERED = "tiered"
    CUSTOM = "custom"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.FIXED: "Fixed Price",
            self.HOURLY: "Hourly Rate",
            self.PER_UNIT: "Per Unit",
            self.TIERED: "Tiered Pricing",
            self.CUSTOM: "Custom Pricing"
        }
        return display_map.get(self, self.value.title())


class UnitOfMeasure(str, Enum):
    """Unit of measure enumeration."""
    EACH = "each"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    SQUARE_FOOT = "square_foot"
    LINEAR_FOOT = "linear_foot"
    CUBIC_FOOT = "cubic_foot"
    POUND = "pound"
    KILOGRAM = "kilogram"
    GALLON = "gallon"
    LITER = "liter"
    METER = "meter"
    YARD = "yard"
    PIECE = "piece"
    SET = "set"
    LOT = "lot"
    CASE = "case"
    BOX = "box"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.EACH: "Each",
            self.HOUR: "Hour",
            self.DAY: "Day",
            self.WEEK: "Week",
            self.MONTH: "Month",
            self.SQUARE_FOOT: "Square Foot",
            self.LINEAR_FOOT: "Linear Foot",
            self.CUBIC_FOOT: "Cubic Foot",
            self.POUND: "Pound",
            self.KILOGRAM: "Kilogram",
            self.GALLON: "Gallon",
            self.LITER: "Liter",
            self.METER: "Meter",
            self.YARD: "Yard",
            self.PIECE: "Piece",
            self.SET: "Set",
            self.LOT: "Lot",
            self.CASE: "Case",
            self.BOX: "Box"
        }
        return display_map.get(self, self.value.title())


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    SQUARE = "square"
    VENMO = "venmo"
    ZELLE = "zelle"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.CASH: "Cash",
            self.CHECK: "Check",
            self.CREDIT_CARD: "Credit Card",
            self.DEBIT_CARD: "Debit Card",
            self.ACH: "ACH Transfer",
            self.WIRE_TRANSFER: "Wire Transfer",
            self.PAYPAL: "PayPal",
            self.STRIPE: "Stripe",
            self.SQUARE: "Square",
            self.VENMO: "Venmo",
            self.ZELLE: "Zelle",
            self.BANK_TRANSFER: "Bank Transfer",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title()) 