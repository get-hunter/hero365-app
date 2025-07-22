"""
Shared Domain Module

Contains shared enums and domain definitions used across multiple domains.
"""

from .enums import (
    CurrencyCode, TaxType, DiscountType, AdvancePaymentType, TemplateType,
    PricingModel, UnitOfMeasure, PaymentMethod
)

__all__ = [
    "CurrencyCode",
    "TaxType",
    "DiscountType",
    "AdvancePaymentType",
    "TemplateType",
    "PricingModel",
    "UnitOfMeasure",
    "PaymentMethod",
] 