"""
Supplier Domain Entity

Represents a supplier for inventory management with comprehensive business rules,
contact information, and supplier performance tracking.
"""

import uuid
import logging
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator, computed_field

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..enums import SupplierStatus, CurrencyCode
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


class SupplierContact(BaseModel):
    """Contact information for a supplier."""
    name: str = Field(..., min_length=1, max_length=200, description="Contact person name")
    title: Optional[str] = Field(None, max_length=100, description="Contact person title")
    email: Optional[str] = Field(None, max_length=255, description="Contact email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    mobile: Optional[str] = Field(None, max_length=50, description="Contact mobile number")
    is_primary: bool = Field(default=False, description="Whether this is the primary contact")
    department: Optional[str] = Field(None, max_length=100, description="Department or division")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about contact")
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid email format')
        return v


class PaymentTerms(BaseModel):
    """Payment terms for supplier transactions."""
    net_days: int = Field(default=30, ge=0, le=365, description="Net payment days")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Early payment discount percentage")
    discount_days: Optional[int] = Field(None, ge=0, description="Days to qualify for early payment discount")
    payment_method: Optional[str] = Field(None, max_length=50, description="Preferred payment method")
    currency: CurrencyCode = Field(default=CurrencyCode.USD, description="Payment currency")
    credit_limit: Optional[Decimal] = Field(None, ge=0, description="Credit limit with supplier")
    
    class Config:
        use_enum_values = True
    
    def get_discount_date(self, invoice_date: date) -> Optional[date]:
        """Calculate discount due date."""
        if self.discount_days is not None:
            from datetime import timedelta
            return invoice_date + timedelta(days=self.discount_days)
        return None
    
    def get_net_due_date(self, invoice_date: date) -> date:
        """Calculate net due date."""
        from datetime import timedelta
        return invoice_date + timedelta(days=self.net_days)


class SupplierPerformance(BaseModel):
    """Supplier performance metrics."""
    total_orders: int = Field(default=0, ge=0, description="Total number of orders")
    total_value: Decimal = Field(default=Decimal('0'), ge=0, description="Total order value")
    on_time_deliveries: int = Field(default=0, ge=0, description="Number of on-time deliveries")
    late_deliveries: int = Field(default=0, ge=0, description="Number of late deliveries")
    quality_issues: int = Field(default=0, ge=0, description="Number of quality issues")
    returns: int = Field(default=0, ge=0, description="Number of returns")
    average_lead_time_days: Optional[Decimal] = Field(None, ge=0, description="Average lead time in days")
    last_order_date: Optional[datetime] = Field(None, description="Date of last order")
    
    @computed_field
    @property
    def on_time_percentage(self) -> Decimal:
        """Calculate on-time delivery percentage."""
        total_deliveries = self.on_time_deliveries + self.late_deliveries
        if total_deliveries == 0:
            return Decimal('100')  # Default to 100% for new suppliers
        return (Decimal(str(self.on_time_deliveries)) / Decimal(str(total_deliveries))) * Decimal('100')
    
    @computed_field
    @property
    def quality_score(self) -> Decimal:
        """Calculate quality score (100% - quality issues rate)."""
        if self.total_orders == 0:
            return Decimal('100')  # Default to 100% for new suppliers
        quality_rate = (Decimal(str(self.quality_issues)) / Decimal(str(self.total_orders))) * Decimal('100')
        return Decimal('100') - quality_rate
    
    @computed_field
    @property
    def return_rate(self) -> Decimal:
        """Calculate return rate percentage."""
        if self.total_orders == 0:
            return Decimal('0')
        return (Decimal(str(self.returns)) / Decimal(str(self.total_orders))) * Decimal('100')
    
    @computed_field
    @property
    def overall_score(self) -> Decimal:
        """Calculate overall supplier performance score."""
        # Weighted average: 40% on-time, 40% quality, 20% return rate
        on_time_weight = Decimal('0.4')
        quality_weight = Decimal('0.4')
        return_weight = Decimal('0.2')
        
        return_score = Decimal('100') - self.return_rate
        
        overall = (
            (self.on_time_percentage * on_time_weight) +
            (self.quality_score * quality_weight) +
            (return_score * return_weight)
        )
        
        return overall.quantize(Decimal('0.1'))


class Supplier(BaseModel):
    """
    Supplier domain entity.
    
    Represents a supplier with comprehensive contact information,
    payment terms, and performance tracking.
    """
    
    # Basic supplier information
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Supplier unique identifier")
    business_id: uuid.UUID = Field(..., description="Business identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Supplier company name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name for supplier")
    supplier_code: Optional[str] = Field(None, max_length=50, description="Internal supplier code")
    
    # Status and classification
    status: SupplierStatus = Field(default=SupplierStatus.ACTIVE, description="Supplier status")
    category: Optional[str] = Field(None, max_length=100, description="Supplier category")
    is_preferred: bool = Field(default=False, description="Whether this is a preferred supplier")
    
    # Contact information
    contacts: List[SupplierContact] = Field(default_factory=list, description="Supplier contacts")
    primary_email: Optional[str] = Field(None, max_length=255, description="Primary email address")
    primary_phone: Optional[str] = Field(None, max_length=50, description="Primary phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    
    # Address information
    billing_address: Optional[Address] = Field(None, description="Billing address")
    shipping_address: Optional[Address] = Field(None, description="Shipping address")
    
    # Business details
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax identification number")
    business_registration: Optional[str] = Field(None, max_length=100, description="Business registration number")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    
    # Payment and terms
    payment_terms: PaymentTerms = Field(default_factory=PaymentTerms, description="Payment terms")
    
    # Performance metrics
    performance: SupplierPerformance = Field(default_factory=SupplierPerformance, description="Performance metrics")
    
    # Operational details
    lead_time_days: Optional[int] = Field(None, ge=0, description="Standard lead time in days")
    minimum_order_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount")
    shipping_terms: Optional[str] = Field(None, max_length=100, description="Shipping terms (FOB, CIF, etc.)")
    
    # Notes and attachments
    notes: Optional[str] = Field(None, max_length=2000, description="General notes about supplier")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes (not shared)")
    tags: List[str] = Field(default_factory=list, description="Supplier tags for organization")
    
    # Metadata
    created_by: str = Field(..., description="User who created the supplier")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation date")
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification date")
    last_contact_date: Optional[datetime] = Field(None, description="Last contact date")
    
    # Business rules validation
    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Supplier name cannot be empty')
        return v.strip()
    
    @validator('supplier_code')
    def validate_supplier_code(cls, v):
        if v is not None:
            v = v.strip().upper()
            if not v:
                return None
            # Supplier code should be alphanumeric with hyphens and underscores
            import re
            if not re.match(r'^[A-Za-z0-9_-]+$', v):
                raise ValueError('Supplier code can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('primary_email')
    def validate_primary_email(cls, v):
        if v is not None:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @validator('website')
    def validate_website(cls, v):
        if v is not None:
            v = v.strip()
            if v and not v.startswith(('http://', 'https://')):
                v = f'https://{v}'
        return v
    
    @validator('contacts')
    def validate_contacts(cls, v):
        if not v:
            return v
        
        # Ensure only one primary contact
        primary_contacts = [contact for contact in v if contact.is_primary]
        if len(primary_contacts) > 1:
            raise ValueError('Only one contact can be marked as primary')
        
        return v
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            uuid.UUID: str,
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    
    # Computed fields
    @computed_field
    @property
    def display_name_or_name(self) -> str:
        """Get display name or fall back to name."""
        return self.display_name or self.name
    
    @computed_field
    @property
    def primary_contact(self) -> Optional[SupplierContact]:
        """Get the primary contact."""
        for contact in self.contacts:
            if contact.is_primary:
                return contact
        return self.contacts[0] if self.contacts else None
    
    @computed_field
    @property
    def has_billing_address(self) -> bool:
        """Check if supplier has billing address."""
        return self.billing_address is not None
    
    @computed_field
    @property
    def has_shipping_address(self) -> bool:
        """Check if supplier has shipping address."""
        return self.shipping_address is not None
    
    @computed_field
    @property
    def effective_shipping_address(self) -> Optional[Address]:
        """Get shipping address or fall back to billing address."""
        return self.shipping_address or self.billing_address
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if supplier is active."""
        return self.status == SupplierStatus.ACTIVE
    
    @computed_field
    @property
    def contact_count(self) -> int:
        """Get number of contacts."""
        return len(self.contacts)
    
    # Business logic methods
    def activate(self):
        """Activate the supplier."""
        if self.status != SupplierStatus.ACTIVE:
            self.status = SupplierStatus.ACTIVE
            self.last_modified = datetime.now(timezone.utc)
            logger.info(f"Supplier {self.name} activated")
    
    def deactivate(self):
        """Deactivate the supplier."""
        if self.status == SupplierStatus.ACTIVE:
            self.status = SupplierStatus.INACTIVE
            self.last_modified = datetime.now(timezone.utc)
            logger.info(f"Supplier {self.name} deactivated")
    
    def suspend(self, reason: Optional[str] = None):
        """Suspend the supplier."""
        if self.status != SupplierStatus.SUSPENDED:
            self.status = SupplierStatus.SUSPENDED
            self.last_modified = datetime.now(timezone.utc)
            if reason:
                self.internal_notes = f"{self.internal_notes or ''}\nSuspended: {reason}".strip()
            logger.warning(f"Supplier {self.name} suspended. Reason: {reason or 'Not specified'}")
    
    def add_contact(self, contact: SupplierContact):
        """Add a contact to the supplier."""
        # If this is the first contact or marked as primary, make it primary
        if not self.contacts or contact.is_primary:
            # Clear existing primary contacts
            for existing_contact in self.contacts:
                existing_contact.is_primary = False
            contact.is_primary = True
        
        self.contacts.append(contact)
        self.last_modified = datetime.now(timezone.utc)
    
    def remove_contact(self, contact_name: str) -> bool:
        """Remove a contact by name."""
        for i, contact in enumerate(self.contacts):
            if contact.name == contact_name:
                removed_contact = self.contacts.pop(i)
                
                # If we removed the primary contact, make the first remaining contact primary
                if removed_contact.is_primary and self.contacts:
                    self.contacts[0].is_primary = True
                
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def set_primary_contact(self, contact_name: str) -> bool:
        """Set a contact as primary by name."""
        for contact in self.contacts:
            if contact.name == contact_name:
                # Clear existing primary
                for c in self.contacts:
                    c.is_primary = False
                contact.is_primary = True
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def update_performance_metrics(self, **metrics):
        """Update performance metrics."""
        for key, value in metrics.items():
            if hasattr(self.performance, key):
                setattr(self.performance, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def record_order(self, order_value: Decimal, order_date: Optional[datetime] = None):
        """Record a new order for performance tracking."""
        self.performance.total_orders += 1
        self.performance.total_value += order_value
        self.performance.last_order_date = order_date or datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
    
    def record_delivery(self, on_time: bool, actual_lead_time_days: Optional[int] = None):
        """Record delivery performance."""
        if on_time:
            self.performance.on_time_deliveries += 1
        else:
            self.performance.late_deliveries += 1
        
        # Update average lead time
        if actual_lead_time_days is not None:
            total_deliveries = self.performance.on_time_deliveries + self.performance.late_deliveries
            if self.performance.average_lead_time_days is None:
                self.performance.average_lead_time_days = Decimal(str(actual_lead_time_days))
            else:
                # Calculate running average
                current_total = self.performance.average_lead_time_days * Decimal(str(total_deliveries - 1))
                new_total = current_total + Decimal(str(actual_lead_time_days))
                self.performance.average_lead_time_days = new_total / Decimal(str(total_deliveries))
        
        self.last_modified = datetime.now(timezone.utc)
    
    def record_quality_issue(self):
        """Record a quality issue."""
        self.performance.quality_issues += 1
        self.last_modified = datetime.now(timezone.utc)
    
    def record_return(self):
        """Record a return."""
        self.performance.returns += 1
        self.last_modified = datetime.now(timezone.utc)
    
    def update_last_contact(self):
        """Update last contact date to now."""
        self.last_contact_date = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str):
        """Add a tag to the supplier."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the supplier."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.now(timezone.utc)
            return True
        return False
    
    def get_performance_grade(self) -> str:
        """Get performance grade based on overall score."""
        score = self.performance.overall_score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def can_place_order(self, order_value: Decimal) -> bool:
        """Check if an order can be placed with this supplier."""
        if not self.is_active:
            return False
        
        if self.status == SupplierStatus.SUSPENDED:
            return False
        
        if self.minimum_order_amount and order_value < self.minimum_order_amount:
            return False
        
        return True
    
    def get_estimated_delivery_date(self, order_date: Optional[datetime] = None) -> Optional[datetime]:
        """Get estimated delivery date based on lead time."""
        if not self.lead_time_days:
            return None
        
        base_date = order_date or datetime.now(timezone.utc)
        from datetime import timedelta
        return base_date + timedelta(days=self.lead_time_days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert supplier to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "name": self.name,
            "display_name": self.display_name,
            "display_name_or_name": self.display_name_or_name,
            "supplier_code": self.supplier_code,
            "status": self.status.value,
            "status_display": self.status.get_display(),
            "category": self.category,
            "is_preferred": self.is_preferred,
            "is_active": self.is_active,
            "primary_email": self.primary_email,
            "primary_phone": self.primary_phone,
            "website": self.website,
            "contacts": [
                {
                    "name": contact.name,
                    "title": contact.title,
                    "email": contact.email,
                    "phone": contact.phone,
                    "mobile": contact.mobile,
                    "is_primary": contact.is_primary,
                    "department": contact.department,
                    "notes": contact.notes
                }
                for contact in self.contacts
            ],
            "primary_contact": {
                "name": self.primary_contact.name,
                "title": self.primary_contact.title,
                "email": self.primary_contact.email,
                "phone": self.primary_contact.phone,
                "mobile": self.primary_contact.mobile,
                "department": self.primary_contact.department
            } if self.primary_contact else None,
            "contact_count": self.contact_count,
            "billing_address": self.billing_address.to_dict() if self.billing_address else None,
            "shipping_address": self.shipping_address.to_dict() if self.shipping_address else None,
            "has_billing_address": self.has_billing_address,
            "has_shipping_address": self.has_shipping_address,
            "tax_id": self.tax_id,
            "business_registration": self.business_registration,
            "industry": self.industry,
            "payment_terms": {
                "net_days": self.payment_terms.net_days,
                "discount_percentage": float(self.payment_terms.discount_percentage) if self.payment_terms.discount_percentage else None,
                "discount_days": self.payment_terms.discount_days,
                "payment_method": self.payment_terms.payment_method,
                "currency": self.payment_terms.currency.value,
                "credit_limit": float(self.payment_terms.credit_limit) if self.payment_terms.credit_limit else None
            },
            "performance": {
                "total_orders": self.performance.total_orders,
                "total_value": float(self.performance.total_value),
                "on_time_deliveries": self.performance.on_time_deliveries,
                "late_deliveries": self.performance.late_deliveries,
                "quality_issues": self.performance.quality_issues,
                "returns": self.performance.returns,
                "average_lead_time_days": float(self.performance.average_lead_time_days) if self.performance.average_lead_time_days else None,
                "last_order_date": self.performance.last_order_date.isoformat() if self.performance.last_order_date else None,
                "on_time_percentage": float(self.performance.on_time_percentage),
                "quality_score": float(self.performance.quality_score),
                "return_rate": float(self.performance.return_rate),
                "overall_score": float(self.performance.overall_score),
                "performance_grade": self.get_performance_grade()
            },
            "lead_time_days": self.lead_time_days,
            "minimum_order_amount": float(self.minimum_order_amount) if self.minimum_order_amount else None,
            "shipping_terms": self.shipping_terms,
            "notes": self.notes,
            "internal_notes": self.internal_notes,
            "tags": self.tags,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "last_contact_date": self.last_contact_date.isoformat() if self.last_contact_date else None
        }
    
    def __str__(self) -> str:
        return f"Supplier({self.display_name_or_name})"
    
    def __repr__(self) -> str:
        return f"Supplier(id={self.id}, name='{self.name}', status='{self.status}')" 