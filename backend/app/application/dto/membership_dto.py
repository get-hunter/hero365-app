"""
Membership Data Transfer Objects

DTOs for membership-related data transfer between application layers.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MembershipPlanDTO(BaseModel):
    """DTO for membership plan data."""
    
    id: str = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    plan_type: str = Field(..., description="Plan type (residential, commercial, premium)")
    description: str = Field(..., description="Plan description")
    tagline: str = Field(..., description="Plan tagline")
    price_monthly: float = Field(..., description="Monthly price")
    price_yearly: float = Field(..., description="Yearly price")
    yearly_savings: float = Field(..., description="Yearly savings amount")
    setup_fee: float = Field(..., description="Setup fee")
    discount_percentage: int = Field(..., description="Discount percentage")
    priority_service: bool = Field(..., description="Priority service included")
    extended_warranty: bool = Field(..., description="Extended warranty included")
    maintenance_included: bool = Field(..., description="Maintenance included")
    emergency_response: bool = Field(..., description="Emergency response included")
    free_diagnostics: bool = Field(..., description="Free diagnostics included")
    annual_tune_ups: int = Field(..., description="Number of annual tune-ups")
    is_active: bool = Field(..., description="Plan is active")
    is_featured: bool = Field(..., description="Plan is featured")
    popular_badge: Optional[str] = Field(None, description="Popular badge text")
    color_scheme: str = Field(..., description="Plan color scheme")
    sort_order: int = Field(..., description="Sort order")
    contract_length_months: int = Field(..., description="Contract length in months")
    cancellation_policy: str = Field(..., description="Cancellation policy")


class CreateMembershipPlanDTO(BaseModel):
    """DTO for creating a new membership plan."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    plan_type: str = Field(..., description="Plan type (residential, commercial, premium)")
    description: str = Field(..., min_length=1, max_length=500, description="Plan description")
    tagline: str = Field(..., min_length=1, max_length=100, description="Plan tagline")
    price_monthly: float = Field(..., ge=0, description="Monthly price")
    price_yearly: float = Field(..., ge=0, description="Yearly price")
    setup_fee: Optional[float] = Field(None, ge=0, description="Setup fee")
    discount_percentage: int = Field(..., ge=0, le=100, description="Discount percentage")
    priority_service: bool = Field(default=False, description="Priority service included")
    extended_warranty: bool = Field(default=False, description="Extended warranty included")
    maintenance_included: bool = Field(default=False, description="Maintenance included")
    emergency_response: bool = Field(default=False, description="Emergency response included")
    free_diagnostics: bool = Field(default=False, description="Free diagnostics included")
    annual_tune_ups: int = Field(default=0, ge=0, description="Number of annual tune-ups")
    is_featured: bool = Field(default=False, description="Plan is featured")
    color_scheme: Optional[str] = Field(None, max_length=20, description="Plan color scheme")
    sort_order: Optional[int] = Field(None, ge=0, description="Sort order")
    contract_length_months: Optional[int] = Field(None, ge=1, description="Contract length in months")
    cancellation_policy: str = Field(..., min_length=1, max_length=1000, description="Cancellation policy")


class CustomerMembershipDTO(BaseModel):
    """DTO for customer membership subscription data."""
    
    id: str = Field(..., description="Membership ID")
    business_id: str = Field(..., description="Business ID")
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Plan ID")
    status: str = Field(..., description="Membership status")
    start_date: datetime = Field(..., description="Membership start date")
    end_date: Optional[datetime] = Field(None, description="Membership end date")
    next_billing_date: datetime = Field(..., description="Next billing date")
    billing_cycle: str = Field(..., description="Billing cycle (monthly/yearly)")
    locked_monthly_price: float = Field(..., description="Locked monthly price")
    locked_yearly_price: float = Field(..., description="Locked yearly price")
    locked_discount_percentage: int = Field(..., description="Locked discount percentage")
    auto_renew: bool = Field(..., description="Auto-renewal enabled")
    total_savings_to_date: float = Field(..., description="Total savings to date")


class CreateCustomerMembershipDTO(BaseModel):
    """DTO for creating a customer membership subscription."""
    
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Plan ID")
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$", description="Billing cycle")
    payment_method_id: Optional[str] = Field(None, description="Payment method ID")
    auto_renew: bool = Field(default=True, description="Auto-renewal enabled")


class MembershipPricingDTO(BaseModel):
    """DTO for membership pricing calculations."""
    
    base_product_price: float = Field(..., description="Base product price")
    base_installation_price: float = Field(..., description="Base installation price")
    base_total: float = Field(..., description="Base total price")
    membership_plan_id: Optional[str] = Field(None, description="Applied membership plan ID")
    membership_plan_name: Optional[str] = Field(None, description="Applied membership plan name")
    discount_percentage: int = Field(..., description="Applied discount percentage")
    discount_amount: float = Field(..., description="Discount amount")
    final_total: float = Field(..., description="Final total after discount")
    savings: float = Field(..., description="Total savings amount")


class UpdateMembershipPlanDTO(BaseModel):
    """DTO for updating a membership plan."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Plan name")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Plan description")
    tagline: Optional[str] = Field(None, min_length=1, max_length=100, description="Plan tagline")
    price_monthly: Optional[float] = Field(None, ge=0, description="Monthly price")
    price_yearly: Optional[float] = Field(None, ge=0, description="Yearly price")
    setup_fee: Optional[float] = Field(None, ge=0, description="Setup fee")
    discount_percentage: Optional[int] = Field(None, ge=0, le=100, description="Discount percentage")
    priority_service: Optional[bool] = Field(None, description="Priority service included")
    extended_warranty: Optional[bool] = Field(None, description="Extended warranty included")
    maintenance_included: Optional[bool] = Field(None, description="Maintenance included")
    emergency_response: Optional[bool] = Field(None, description="Emergency response included")
    free_diagnostics: Optional[bool] = Field(None, description="Free diagnostics included")
    annual_tune_ups: Optional[int] = Field(None, ge=0, description="Number of annual tune-ups")
    is_active: Optional[bool] = Field(None, description="Plan is active")
    is_featured: Optional[bool] = Field(None, description="Plan is featured")
    popular_badge: Optional[str] = Field(None, max_length=50, description="Popular badge text")
    color_scheme: Optional[str] = Field(None, max_length=20, description="Plan color scheme")
    sort_order: Optional[int] = Field(None, ge=0, description="Sort order")
    contract_length_months: Optional[int] = Field(None, ge=1, description="Contract length in months")
    cancellation_policy: Optional[str] = Field(None, min_length=1, max_length=1000, description="Cancellation policy")
