"""
Contact Domain Entity

Represents a business contact (customer, lead, prospect) with associated business rules and behaviors.
"""

import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError


class ContactType(Enum):
    """Enumeration for contact types."""
    CUSTOMER = "customer"
    LEAD = "lead"
    PROSPECT = "prospect"
    VENDOR = "vendor"
    PARTNER = "partner"
    CONTRACTOR = "contractor"


class ContactStatus(Enum):
    """Enumeration for contact status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class ContactSource(Enum):
    """Enumeration for how the contact was acquired."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    COLD_OUTREACH = "cold_outreach"
    EVENT = "event"
    PARTNER = "partner"
    EXISTING_CUSTOMER = "existing_customer"
    DIRECT = "direct"
    OTHER = "other"


class ContactPriority(Enum):
    """Enumeration for contact priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ContactAddress:
    """Value object for contact address information."""
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Check if address has minimum required information."""
        return bool(self.street_address and self.city)
    
    def get_formatted_address(self) -> str:
        """Get formatted address string."""
        parts = []
        if self.street_address:
            parts.append(self.street_address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


@dataclass
class Contact:
    """
    Contact entity representing a business contact (customer, lead, prospect, etc.).
    
    This entity contains business logic and rules for contact management,
    validation, and lifecycle operations.
    """
    
    # Required fields
    id: uuid.UUID
    business_id: uuid.UUID
    contact_type: ContactType
    status: ContactStatus = ContactStatus.ACTIVE
    
    # Personal Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    
    # Contact Information
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address Information
    address: Optional[ContactAddress] = None
    
    # Business Information
    priority: ContactPriority = ContactPriority.MEDIUM
    source: Optional[ContactSource] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    # Financial Information
    estimated_value: Optional[float] = None
    currency: str = "USD"
    
    # Relationship Information
    assigned_to: Optional[str] = None  # User ID of assigned team member
    created_by: Optional[str] = None   # User ID who created the contact
    
    # Custom Fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values and validate business rules."""
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
        self._validate_contact_rules()
    
    def _validate_contact_rules(self) -> None:
        """Validate core contact business rules."""
        if not self.business_id:
            raise DomainValidationError("Contact must belong to a business")
        
        # At least one name or company name required
        if not self.first_name and not self.last_name and not self.company_name:
            raise DomainValidationError("Contact must have at least first name, last name, or company name")
        
        # At least one contact method required
        if not self.email and not self.phone and not self.mobile_phone:
            raise DomainValidationError("Contact must have at least one contact method (email or phone)")
        
        # Validate email format if provided
        if self.email and not self._is_valid_email(self.email):
            raise DomainValidationError("Invalid email format")
        
        # Validate phone formats if provided
        if self.phone and not self._is_valid_phone(self.phone):
            raise DomainValidationError("Invalid phone format")
        
        if self.mobile_phone and not self._is_valid_phone(self.mobile_phone):
            raise DomainValidationError("Invalid mobile phone format")
        
        # Validate website format if provided
        if self.website and not self._is_valid_website(self.website):
            raise DomainValidationError("Invalid website format")
        
        # Validate estimated value
        if self.estimated_value is not None and self.estimated_value < 0:
            raise DomainValidationError("Estimated value cannot be negative")
        
        # Validate currency format
        if self.currency and len(self.currency) != 3:
            raise DomainValidationError("Currency must be a 3-letter ISO code")
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email.split("@")[-1]
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation."""
        # Remove common phone formatting characters
        cleaned = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return cleaned.isdigit() and len(cleaned) >= 10
    
    def _is_valid_website(self, website: str) -> bool:
        """Basic website validation."""
        return website.startswith(('http://', 'https://')) or '.' in website
    
    @classmethod
    def create_contact(cls, business_id: uuid.UUID, contact_type: ContactType,
                      first_name: Optional[str] = None, last_name: Optional[str] = None,
                      company_name: Optional[str] = None, email: Optional[str] = None,
                      phone: Optional[str] = None, created_by: Optional[str] = None,
                      **kwargs) -> 'Contact':
        """
        Create a new contact with validation.
        
        Args:
            business_id: ID of the business this contact belongs to
            contact_type: Type of contact (customer, lead, prospect, etc.)
            first_name: Contact's first name
            last_name: Contact's last name
            company_name: Company name if business contact
            email: Email address
            phone: Phone number
            created_by: User ID who created the contact
            **kwargs: Additional contact fields
            
        Returns:
            New Contact instance
            
        Raises:
            DomainValidationError: If validation fails
        """
        return cls(
            id=uuid.uuid4(),
            business_id=business_id,
            contact_type=contact_type,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            email=email,
            phone=phone or kwargs.get('mobile_phone'),
            mobile_phone=kwargs.get('mobile_phone'),
            created_by=created_by,
            created_date=datetime.utcnow(),
            **{k: v for k, v in kwargs.items() if k not in ['mobile_phone']}
        )
    
    def get_display_name(self) -> str:
        """Get the display name for the contact."""
        if self.company_name:
            if self.first_name and self.last_name:
                return f"{self.first_name} {self.last_name} ({self.company_name})"
            elif self.first_name or self.last_name:
                name = self.first_name or self.last_name
                return f"{name} ({self.company_name})"
            else:
                return self.company_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "Unknown Contact"
    
    def get_primary_contact_method(self) -> str:
        """Get the primary contact method."""
        if self.email:
            return self.email
        elif self.mobile_phone:
            return self.mobile_phone
        elif self.phone:
            return self.phone
        else:
            return "No contact method"
    
    def get_full_address(self) -> Optional[str]:
        """Get formatted full address."""
        if self.address and self.address.is_complete():
            return self.address.get_formatted_address()
        return None
    
    def is_customer(self) -> bool:
        """Check if contact is a customer."""
        return self.contact_type == ContactType.CUSTOMER
    
    def is_lead(self) -> bool:
        """Check if contact is a lead."""
        return self.contact_type == ContactType.LEAD
    
    def is_prospect(self) -> bool:
        """Check if contact is a prospect."""
        return self.contact_type == ContactType.PROSPECT
    
    def is_active(self) -> bool:
        """Check if contact is active."""
        return self.status == ContactStatus.ACTIVE
    
    def is_high_priority(self) -> bool:
        """Check if contact is high priority."""
        return self.priority in [ContactPriority.HIGH, ContactPriority.URGENT]
    
    def has_complete_address(self) -> bool:
        """Check if contact has a complete address."""
        return self.address is not None and self.address.is_complete()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the contact."""
        if tag and tag not in self.tags:
            self.tags.append(tag.strip().lower())
            self.last_modified = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the contact."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.utcnow()
    
    def has_tag(self, tag: str) -> bool:
        """Check if contact has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def set_custom_field(self, field_name: str, value: Any) -> None:
        """Set a custom field value."""
        self.custom_fields[field_name] = value
        self.last_modified = datetime.utcnow()
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get a custom field value."""
        return self.custom_fields.get(field_name, default)
    
    def update_last_contacted(self) -> None:
        """Update the last contacted timestamp."""
        self.last_contacted = datetime.utcnow()
        self.last_modified = datetime.utcnow()
    
    def convert_to_customer(self) -> None:
        """Convert lead/prospect to customer."""
        if self.contact_type in [ContactType.LEAD, ContactType.PROSPECT]:
            self.contact_type = ContactType.CUSTOMER
            self.last_modified = datetime.utcnow()
        else:
            raise DomainValidationError(f"Cannot convert {self.contact_type.value} to customer")
    
    def convert_to_lead(self) -> None:
        """Convert prospect to lead."""
        if self.contact_type == ContactType.PROSPECT:
            self.contact_type = ContactType.LEAD
            self.last_modified = datetime.utcnow()
        else:
            raise DomainValidationError(f"Cannot convert {self.contact_type.value} to lead")
    
    def assign_to_user(self, user_id: str) -> None:
        """Assign contact to a team member."""
        self.assigned_to = user_id
        self.last_modified = datetime.utcnow()
    
    def unassign(self) -> None:
        """Remove assignment from contact."""
        self.assigned_to = None
        self.last_modified = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive the contact."""
        if self.status == ContactStatus.ACTIVE:
            self.status = ContactStatus.ARCHIVED
            self.last_modified = datetime.utcnow()
        else:
            raise DomainValidationError(f"Cannot archive contact with status: {self.status.value}")
    
    def activate(self) -> None:
        """Activate an inactive or archived contact."""
        if self.status in [ContactStatus.INACTIVE, ContactStatus.ARCHIVED]:
            self.status = ContactStatus.ACTIVE
            self.last_modified = datetime.utcnow()
        else:
            raise DomainValidationError(f"Cannot activate contact with status: {self.status.value}")
    
    def block(self) -> None:
        """Block the contact."""
        self.status = ContactStatus.BLOCKED
        self.last_modified = datetime.utcnow()
    
    def get_type_display(self) -> str:
        """Get human-readable contact type."""
        type_names = {
            ContactType.CUSTOMER: "Customer",
            ContactType.LEAD: "Lead",
            ContactType.PROSPECT: "Prospect",
            ContactType.VENDOR: "Vendor",
            ContactType.PARTNER: "Partner",
            ContactType.CONTRACTOR: "Contractor"
        }
        return type_names.get(self.contact_type, "Unknown")
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        status_names = {
            ContactStatus.ACTIVE: "Active",
            ContactStatus.INACTIVE: "Inactive",
            ContactStatus.ARCHIVED: "Archived",
            ContactStatus.BLOCKED: "Blocked"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_priority_display(self) -> str:
        """Get human-readable priority."""
        priority_names = {
            ContactPriority.LOW: "Low",
            ContactPriority.MEDIUM: "Medium",
            ContactPriority.HIGH: "High",
            ContactPriority.URGENT: "Urgent"
        }
        return priority_names.get(self.priority, "Unknown")
    
    def get_source_display(self) -> str:
        """Get human-readable source."""
        source_names = {
            ContactSource.WEBSITE: "Website",
            ContactSource.REFERRAL: "Referral",
            ContactSource.SOCIAL_MEDIA: "Social Media",
            ContactSource.ADVERTISING: "Advertising",
            ContactSource.COLD_OUTREACH: "Cold Outreach",
            ContactSource.EVENT: "Event",
            ContactSource.PARTNER: "Partner",
            ContactSource.EXISTING_CUSTOMER: "Existing Customer",
            ContactSource.DIRECT: "Direct",
            ContactSource.OTHER: "Other"
        }
        return source_names.get(self.source, "Unknown") if self.source else "Not specified"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "contact_type": self.contact_type.value,
            "status": self.status.value,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "email": self.email,
            "phone": self.phone,
            "mobile_phone": self.mobile_phone,
            "website": self.website,
            "address": {
                "street_address": self.address.street_address,
                "city": self.address.city,
                "state": self.address.state,
                "postal_code": self.address.postal_code,
                "country": self.address.country
            } if self.address else None,
            "priority": self.priority.value,
            "source": self.source.value if self.source else None,
            "tags": self.tags,
            "notes": self.notes,
            "estimated_value": self.estimated_value,
            "currency": self.currency,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "custom_fields": self.custom_fields,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "last_contacted": self.last_contacted.isoformat() if self.last_contacted else None,
            "display_name": self.get_display_name(),
            "primary_contact_method": self.get_primary_contact_method(),
            "type_display": self.get_type_display(),
            "status_display": self.get_status_display(),
            "priority_display": self.get_priority_display(),
            "source_display": self.get_source_display()
        }
    
    def __str__(self) -> str:
        return f"Contact({self.get_display_name()} - {self.get_type_display()})"
    
    def __repr__(self) -> str:
        return (f"Contact(id={self.id}, business_id={self.business_id}, "
                f"name='{self.get_display_name()}', type={self.contact_type}, "
                f"status={self.status})") 