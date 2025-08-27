"""
Customer Membership Domain Entity

Represents customer membership plans and subscriptions in the domain.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


class MembershipPlanType(str, Enum):
    """Types of membership plans available."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    PREMIUM = "premium"


class MembershipStatus(str, Enum):
    """Status of a customer membership."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CustomerMembershipPlan(BaseModel):
    """
    Customer membership plan domain entity.
    
    Represents the available membership plans that customers can subscribe to,
    including pricing, benefits, and business rules.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True
    )
    
    # Required fields
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=100)
    plan_type: MembershipPlanType
    description: str = Field(..., min_length=1, max_length=500)
    tagline: str = Field(..., min_length=1, max_length=100)
    
    # Pricing
    price_monthly: Decimal = Field(..., ge=0)
    price_yearly: Decimal = Field(..., ge=0)
    setup_fee: Decimal = Field(default=Decimal("0"), ge=0)
    discount_percentage: int = Field(..., ge=0, le=100)
    
    # Benefits
    priority_service: bool = Field(default=False)
    extended_warranty: bool = Field(default=False)
    maintenance_included: bool = Field(default=False)
    emergency_response: bool = Field(default=False)
    free_diagnostics: bool = Field(default=False)
    annual_tune_ups: int = Field(default=0, ge=0)
    
    # Display and marketing
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    popular_badge: Optional[str] = Field(None, max_length=50)
    color_scheme: str = Field(default="blue", max_length=20)
    sort_order: int = Field(default=0, ge=0)
    
    # Contract terms
    contract_length_months: int = Field(default=12, ge=1)
    cancellation_policy: str = Field(..., min_length=1, max_length=1000)
    
    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('price_yearly')
    @classmethod
    def validate_yearly_pricing(cls, v, info):
        """Ensure yearly price provides savings over monthly."""
        if 'price_monthly' in info.data:
            monthly_annual = info.data['price_monthly'] * 12
            if v >= monthly_annual:
                raise DomainValidationError("Yearly price must be less than 12x monthly price")
        return v
    
    def calculate_yearly_savings(self) -> Decimal:
        """Calculate annual savings compared to monthly billing."""
        monthly_annual = self.price_monthly * 12
        return monthly_annual - self.price_yearly
    
    def calculate_monthly_savings_percentage(self) -> Decimal:
        """Calculate percentage savings of yearly vs monthly billing."""
        if self.price_monthly == 0:
            return Decimal("0")
        
        monthly_annual = self.price_monthly * 12
        savings = monthly_annual - self.price_yearly
        return (savings / monthly_annual) * Decimal("100")
    
    def is_available_for_signup(self) -> bool:
        """Check if plan is available for new signups."""
        return self.is_active
    
    def get_effective_discount_rate(self) -> Decimal:
        """Get the discount rate as decimal (e.g., 15% = 0.15)."""
        return Decimal(str(self.discount_percentage)) / Decimal("100")


class CustomerMembership(BaseModel):
    """
    Customer membership subscription domain entity.
    
    Represents an active customer subscription to a membership plan.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True
    )
    
    # Required fields
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    customer_id: uuid.UUID
    plan_id: uuid.UUID
    status: MembershipStatus = MembershipStatus.ACTIVE
    
    # Subscription details
    start_date: datetime
    end_date: Optional[datetime] = None
    next_billing_date: datetime
    billing_cycle: str = Field(default="monthly", pattern="^(monthly|yearly)$")
    
    # Pricing locked at subscription time
    locked_monthly_price: Decimal = Field(..., ge=0)
    locked_yearly_price: Decimal = Field(..., ge=0)
    locked_discount_percentage: int = Field(..., ge=0, le=100)
    
    # Payment and billing
    auto_renew: bool = Field(default=True)
    payment_method_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    next_payment_amount: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Usage tracking
    services_used_this_period: int = Field(default=0, ge=0)
    total_savings_to_date: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if membership is currently active."""
        now = datetime.now(timezone.utc)
        return (
            self.status == MembershipStatus.ACTIVE and
            self.start_date <= now and
            (self.end_date is None or self.end_date > now)
        )
    
    def is_due_for_renewal(self) -> bool:
        """Check if membership is due for renewal."""
        if not self.auto_renew or self.status != MembershipStatus.ACTIVE:
            return False
        
        now = datetime.now(timezone.utc)
        return self.next_billing_date <= now
    
    def calculate_current_period_savings(self, regular_service_cost: Decimal) -> Decimal:
        """Calculate savings for current billing period."""
        discount_rate = Decimal(str(self.locked_discount_percentage)) / Decimal("100")
        return regular_service_cost * discount_rate
    
    def get_effective_discount_rate(self) -> Decimal:
        """Get the locked discount rate as decimal."""
        return Decimal(str(self.locked_discount_percentage)) / Decimal("100")
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the membership."""
        if self.status == MembershipStatus.CANCELLED:
            raise BusinessRuleViolationError("Membership is already cancelled")
        
        self.status = MembershipStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
        self.cancellation_reason = reason
        self.auto_renew = False
        self.updated_at = datetime.now(timezone.utc)
    
    def suspend(self) -> None:
        """Suspend the membership."""
        if self.status != MembershipStatus.ACTIVE:
            raise BusinessRuleViolationError("Can only suspend active memberships")
        
        self.status = MembershipStatus.SUSPENDED
        self.updated_at = datetime.now(timezone.utc)
    
    def reactivate(self) -> None:
        """Reactivate a suspended membership."""
        if self.status != MembershipStatus.SUSPENDED:
            raise BusinessRuleViolationError("Can only reactivate suspended memberships")
        
        self.status = MembershipStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
