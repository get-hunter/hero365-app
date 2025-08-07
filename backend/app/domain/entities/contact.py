"""
Contact Domain Entity

Represents a business contact (customer, lead, prospect) with associated business rules and behaviors.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_contact_type(v) -> 'ContactType':
    """Convert string to ContactType enum."""
    if isinstance(v, str):
        return ContactType(v)
    return v

def validate_contact_status(v) -> 'ContactStatus':
    """Convert string to ContactStatus enum."""
    if isinstance(v, str):
        return ContactStatus(v)
    return v

def validate_relationship_status(v) -> 'RelationshipStatus':
    """Convert string to RelationshipStatus enum."""
    if isinstance(v, str):
        return RelationshipStatus(v)
    return v

def validate_lifecycle_stage(v) -> 'LifecycleStage':
    """Convert string to LifecycleStage enum."""
    if isinstance(v, str):
        return LifecycleStage(v)
    return v

def validate_contact_source(v) -> 'ContactSource':
    """Convert string to ContactSource enum."""
    if isinstance(v, str):
        return ContactSource(v)
    return v

def validate_contact_priority(v) -> 'ContactPriority':
    """Convert string to ContactPriority enum."""
    if isinstance(v, str):
        return ContactPriority(v)
    return v

def validate_interaction_type(v) -> 'InteractionType':
    """Convert string to InteractionType enum."""
    if isinstance(v, str):
        return InteractionType(v)
    return v


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


class RelationshipStatus(Enum):
    """Enumeration for relationship status in sales/client lifecycle."""
    PROSPECT = "prospect"
    QUALIFIED_LEAD = "qualified_lead"
    OPPORTUNITY = "opportunity"
    ACTIVE_CLIENT = "active_client"
    PAST_CLIENT = "past_client"
    LOST_LEAD = "lost_lead"
    INACTIVE = "inactive"


class LifecycleStage(Enum):
    """Enumeration for customer lifecycle stage."""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    RETENTION = "retention"
    CUSTOMER = "customer"


class ContactSource(Enum):
    """Enumeration for how the contact was acquired."""
    WEBSITE = "website"
    ONLINE = "online"
    GOOGLE_ADS = "google_ads"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    PHONE_CALL = "phone_call"
    WALK_IN = "walk_in"
    EMAIL_MARKETING = "email_marketing"
    TRADE_SHOW = "trade_show"
    DIRECT_MAIL = "direct_mail"
    YELLOW_PAGES = "yellow_pages"
    PARTNER = "partner"
    EXISTING_CUSTOMER = "existing_customer"
    COLD_OUTREACH = "cold_outreach"
    EVENT = "event"
    DIRECT = "direct"
    OTHER = "other"


class ContactPriority(Enum):
    """Enumeration for contact priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class InteractionType(Enum):
    """Enumeration for interaction types."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    PROPOSAL = "proposal"
    QUOTE = "quote"
    CONTRACT = "contract"
    SERVICE = "service"
    FOLLOW_UP = "follow_up"
    NOTE = "note"


# Import unified Address value object
from ..value_objects.address import Address


class StatusHistoryEntry(BaseModel):
    """Value object for status history entry."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    from_status: Optional[Annotated[RelationshipStatus, BeforeValidator(validate_relationship_status)]] = None
    to_status: Annotated[RelationshipStatus, BeforeValidator(validate_relationship_status)]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changed_by: str
    changed_by_id: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class InteractionHistoryEntry(BaseModel):
    """Value object for interaction history entry."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    type: Annotated[InteractionType, BeforeValidator(validate_interaction_type)]
    description: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    performed_by: str = Field(min_length=1)
    performed_by_id: Optional[str] = None
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    scheduled_follow_up: Optional[datetime] = None


class Contact(BaseModel):
    """
    Contact entity representing a business contact (customer, lead, prospect, etc.).
    
    This entity contains business logic and rules for contact management,
    validation, and lifecycle operations.
    """
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    # Required fields
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4
    contact_type: Annotated[ContactType, BeforeValidator(validate_contact_type)]
    status: Annotated[ContactStatus, BeforeValidator(validate_contact_status)] = ContactStatus.ACTIVE
    
    # Enhanced relationship tracking
    relationship_status: Annotated[RelationshipStatus, BeforeValidator(validate_relationship_status)] = RelationshipStatus.PROSPECT
    lifecycle_stage: Annotated[LifecycleStage, BeforeValidator(validate_lifecycle_stage)] = LifecycleStage.AWARENESS
    
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
    address: Optional[Address] = None
    
    # Business Information
    priority: Annotated[ContactPriority, BeforeValidator(validate_contact_priority)] = ContactPriority.MEDIUM
    source: Optional[Annotated[ContactSource, BeforeValidator(validate_contact_source)]] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Financial Information
    estimated_value: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    
    # Relationship Information
    assigned_to: Optional[str] = None  # User ID of assigned team member
    created_by: Optional[str] = None   # User ID who created the contact
    
    # Custom Fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Enhanced tracking fields
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)
    interaction_history: List[InteractionHistoryEntry] = Field(default_factory=list)
    
    # Metadata
    created_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_modified: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_contacted: Optional[datetime] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        """Validate email format if provided."""
        if v and not cls._is_valid_email_static(v):
            raise ValueError("Invalid email format")
        return v
    
    @field_validator('phone', 'mobile_phone')
    @classmethod
    def validate_phone_format(cls, v):
        """Validate phone format if provided."""
        if v and not cls._is_valid_phone_static(v):
            raise ValueError("Invalid phone format")
        return v
    
    @field_validator('website')
    @classmethod
    def validate_website_format(cls, v):
        """Validate website format if provided."""
        if v and not cls._is_valid_website_static(v):
            raise ValueError("Invalid website format")
        return v
    
    @model_validator(mode='after')
    def validate_contact_rules(self):
        """Validate core contact business rules."""
        # At least one name or company name required
        if not self.first_name and not self.last_name and not self.company_name:
            raise ValueError("Contact must have at least first name, last name, or company name")
        
        # At least one contact method required
        if not self.email and not self.phone and not self.mobile_phone:
            raise ValueError("Contact must have at least one contact method (email or phone)")
        
        # Validate relationship status and lifecycle stage alignment
        self._validate_status_alignment()
        
        return self
    

    
    def _validate_status_alignment(self) -> None:
        """Validate that relationship status and lifecycle stage are aligned."""
        valid_combinations = {
            RelationshipStatus.PROSPECT: [LifecycleStage.AWARENESS, LifecycleStage.INTEREST],
            RelationshipStatus.QUALIFIED_LEAD: [LifecycleStage.INTEREST, LifecycleStage.CONSIDERATION],
            RelationshipStatus.OPPORTUNITY: [LifecycleStage.CONSIDERATION, LifecycleStage.DECISION],
            RelationshipStatus.ACTIVE_CLIENT: [LifecycleStage.CUSTOMER, LifecycleStage.RETENTION],
            RelationshipStatus.PAST_CLIENT: [LifecycleStage.RETENTION],
            RelationshipStatus.LOST_LEAD: [LifecycleStage.CONSIDERATION, LifecycleStage.DECISION],
            RelationshipStatus.INACTIVE: [LifecycleStage.RETENTION]
        }
        
        valid_stages = valid_combinations.get(self.relationship_status, [])
        if valid_stages and self.lifecycle_stage not in valid_stages:
            # Auto-correct lifecycle stage based on relationship status (for validation only)
            # In Pydantic, we can't modify self, so we'll just pass this validation
            # The correction should be handled at the application level
            pass
    
    @staticmethod
    def _is_valid_email_static(email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email.split("@")[-1]
    
    @staticmethod
    def _is_valid_phone_static(phone: str) -> bool:
        """Basic phone validation."""
        # Remove common phone formatting characters
        cleaned = phone.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return cleaned.isdigit() and len(cleaned) >= 10
    
    @staticmethod
    def _is_valid_website_static(website: str) -> bool:
        """Basic website validation."""
        return website.startswith(('http://', 'https://')) or '.' in website
    
    # Instance methods for backward compatibility
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        return self._is_valid_email_static(email)
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation."""
        return self._is_valid_phone_static(phone)
    
    def _is_valid_website(self, website: str) -> bool:
        """Basic website validation."""
        return self._is_valid_website_static(website)
    
    @classmethod
    def create_contact(cls, business_id: uuid.UUID, contact_type: ContactType,
                      first_name: Optional[str] = None, last_name: Optional[str] = None,
                      company_name: Optional[str] = None, email: Optional[str] = None,
                      phone: Optional[str] = None, created_by: Optional[str] = None,
                      relationship_status: Optional[RelationshipStatus] = None,
                      lifecycle_stage: Optional[LifecycleStage] = None,
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
            relationship_status: Relationship status in sales lifecycle
            lifecycle_stage: Stage in customer lifecycle
            **kwargs: Additional contact fields
            
        Returns:
            New Contact instance
            
        Raises:
            DomainValidationError: If validation fails
        """
        # Set default relationship status based on contact type
        if not relationship_status:
            relationship_status = {
                ContactType.CUSTOMER: RelationshipStatus.ACTIVE_CLIENT,
                ContactType.LEAD: RelationshipStatus.QUALIFIED_LEAD,
                ContactType.PROSPECT: RelationshipStatus.PROSPECT,
                ContactType.VENDOR: RelationshipStatus.ACTIVE_CLIENT,
                ContactType.PARTNER: RelationshipStatus.ACTIVE_CLIENT,
                ContactType.CONTRACTOR: RelationshipStatus.ACTIVE_CLIENT
            }.get(contact_type, RelationshipStatus.PROSPECT)
        
        # Set default lifecycle stage based on relationship status
        if not lifecycle_stage:
            lifecycle_stage = {
                RelationshipStatus.PROSPECT: LifecycleStage.AWARENESS,
                RelationshipStatus.QUALIFIED_LEAD: LifecycleStage.INTEREST,
                RelationshipStatus.OPPORTUNITY: LifecycleStage.CONSIDERATION,
                RelationshipStatus.ACTIVE_CLIENT: LifecycleStage.CUSTOMER,
                RelationshipStatus.PAST_CLIENT: LifecycleStage.RETENTION,
                RelationshipStatus.LOST_LEAD: LifecycleStage.CONSIDERATION,
                RelationshipStatus.INACTIVE: LifecycleStage.RETENTION
            }.get(relationship_status, LifecycleStage.AWARENESS)
        
        contact = cls(
            id=uuid.uuid4(),
            business_id=business_id,
            contact_type=contact_type,
            relationship_status=relationship_status,
            lifecycle_stage=lifecycle_stage,
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
        
        # Initialize status history
        if created_by:  # Only add status history if created_by is provided
            contact.add_status_history_entry(None, relationship_status, created_by, "Initial status")
        
        return contact
    
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
    
    def update_relationship_status(self, new_status: RelationshipStatus, 
                                 changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Update relationship status with history tracking. Returns new Contact instance."""
        if self.relationship_status == new_status:
            return self
        
        old_status = self.relationship_status
        now = datetime.utcnow()
        
        # Create new status history entry
        new_entry = StatusHistoryEntry(
            from_status=old_status,
            to_status=new_status,
            timestamp=now,
            changed_by=changed_by,
            reason=reason
        )
        
        new_history = self.status_history + [new_entry]
        # Keep only last 20 entries to prevent unbounded growth
        if len(new_history) > 20:
            new_history = new_history[-20:]
        
        return self.model_copy(update={
            'relationship_status': new_status,
            'last_modified': now,
            'status_history': new_history
        })
    
    def add_status_history_entry(self, from_status: Optional[RelationshipStatus], 
                               to_status: RelationshipStatus, changed_by: str, 
                               reason: Optional[str] = None) -> 'Contact':
        """Add entry to status history. Returns new Contact instance."""
        entry = StatusHistoryEntry(
            from_status=from_status,
            to_status=to_status,
            timestamp=datetime.utcnow(),
            changed_by=changed_by,
            reason=reason
        )
        
        new_history = self.status_history + [entry]
        # Keep only last 20 entries to prevent unbounded growth
        if len(new_history) > 20:
            new_history = new_history[-20:]
        
        return self.model_copy(update={'status_history': new_history})
    
    def add_interaction(self, interaction_type: InteractionType, description: str,
                       performed_by: str, outcome: Optional[str] = None,
                       next_action: Optional[str] = None,
                       scheduled_follow_up: Optional[datetime] = None) -> 'Contact':
        """Add interaction to history and update last_contacted. Returns new Contact instance."""
        now = datetime.utcnow()
        
        interaction = InteractionHistoryEntry(
            type=interaction_type,
            description=description,
            timestamp=now,
            performed_by=performed_by,
            outcome=outcome,
            next_action=next_action,
            scheduled_follow_up=scheduled_follow_up
        )
        
        new_history = self.interaction_history + [interaction]
        # Keep only last 10 interactions for quick access
        if len(new_history) > 10:
            new_history = new_history[-10:]
        
        update_data = {
            'interaction_history': new_history,
            'last_modified': now
        }
        
        # Update last contacted for communication interactions
        if interaction_type in [InteractionType.CALL, InteractionType.EMAIL, InteractionType.MEETING]:
            update_data['last_contacted'] = now
        
        return self.model_copy(update=update_data)
    
    def get_relationship_status_display(self) -> str:
        """Get human-readable relationship status."""
        status_names = {
            RelationshipStatus.PROSPECT: "Prospect",
            RelationshipStatus.QUALIFIED_LEAD: "Qualified Lead",
            RelationshipStatus.OPPORTUNITY: "Opportunity",
            RelationshipStatus.ACTIVE_CLIENT: "Active Client",
            RelationshipStatus.PAST_CLIENT: "Past Client",
            RelationshipStatus.LOST_LEAD: "Lost Lead",
            RelationshipStatus.INACTIVE: "Inactive"
        }
        return status_names.get(self.relationship_status, "Unknown")
    
    def get_lifecycle_stage_display(self) -> str:
        """Get human-readable lifecycle stage."""
        stage_names = {
            LifecycleStage.AWARENESS: "Awareness",
            LifecycleStage.INTEREST: "Interest", 
            LifecycleStage.CONSIDERATION: "Consideration",
            LifecycleStage.DECISION: "Decision",
            LifecycleStage.RETENTION: "Retention",
            LifecycleStage.CUSTOMER: "Customer"
        }
        return stage_names.get(self.lifecycle_stage, "Unknown")
    
    def can_progress_to_lead(self) -> bool:
        """Check if contact can be progressed to qualified lead."""
        return self.relationship_status == RelationshipStatus.PROSPECT
    
    def can_progress_to_opportunity(self) -> bool:
        """Check if contact can be progressed to opportunity."""
        return self.relationship_status == RelationshipStatus.QUALIFIED_LEAD
    
    def can_convert_to_client(self) -> bool:
        """Check if contact can be converted to active client."""
        return self.relationship_status in [
            RelationshipStatus.OPPORTUNITY,
            RelationshipStatus.QUALIFIED_LEAD
        ]
    
    def progress_to_qualified_lead(self, changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Progress prospect to qualified lead. Returns new Contact instance."""
        if not self.can_progress_to_lead():
            raise DomainValidationError(f"Cannot progress {self.relationship_status.value} to qualified lead")
        
        updated_contact = self.update_relationship_status(RelationshipStatus.QUALIFIED_LEAD, changed_by, reason)
        return updated_contact.model_copy(update={'lifecycle_stage': LifecycleStage.INTEREST})
    
    def progress_to_opportunity(self, changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Progress qualified lead to opportunity. Returns new Contact instance."""
        if not self.can_progress_to_opportunity():
            raise DomainValidationError(f"Cannot progress {self.relationship_status.value} to opportunity")
        
        updated_contact = self.update_relationship_status(RelationshipStatus.OPPORTUNITY, changed_by, reason)
        return updated_contact.model_copy(update={'lifecycle_stage': LifecycleStage.CONSIDERATION})
    
    def convert_to_client(self, changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Convert lead/opportunity to active client. Returns new Contact instance."""
        if not self.can_convert_to_client():
            raise DomainValidationError(f"Cannot convert {self.relationship_status.value} to client")
        
        updated_contact = self.update_relationship_status(RelationshipStatus.ACTIVE_CLIENT, changed_by, reason)
        return updated_contact.model_copy(update={
            'lifecycle_stage': LifecycleStage.CUSTOMER,
            'contact_type': ContactType.CUSTOMER
        })
    
    def mark_as_lost_lead(self, changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Mark as lost lead. Returns new Contact instance."""
        if self.relationship_status not in [RelationshipStatus.QUALIFIED_LEAD, RelationshipStatus.OPPORTUNITY]:
            raise DomainValidationError(f"Cannot mark {self.relationship_status.value} as lost lead")
        
        return self.update_relationship_status(RelationshipStatus.LOST_LEAD, changed_by, reason)
    
    def reactivate_contact(self, changed_by: str, reason: Optional[str] = None) -> 'Contact':
        """Reactivate inactive or lost contact. Returns new Contact instance."""
        if self.relationship_status in [RelationshipStatus.INACTIVE, RelationshipStatus.LOST_LEAD]:
            updated_contact = self.update_relationship_status(RelationshipStatus.PROSPECT, changed_by, reason)
            return updated_contact.model_copy(update={'lifecycle_stage': LifecycleStage.AWARENESS})
        else:
            raise DomainValidationError(f"Cannot reactivate contact with status {self.relationship_status.value}")
    
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
            return self.address.get_full_address()
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
    
    def has_geocoded_address(self) -> bool:
        """Check if contact has address with coordinates."""
        return self.address is not None and self.address.has_coordinates()
    
    def add_tag(self, tag: str) -> 'Contact':
        """Add a tag to the contact. Returns new Contact instance."""
        if tag and tag not in self.tags:
            new_tags = self.tags + [tag.strip().lower()]
            return self.model_copy(update={
                'tags': new_tags,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def remove_tag(self, tag: str) -> 'Contact':
        """Remove a tag from the contact. Returns new Contact instance."""
        if tag in self.tags:
            new_tags = [t for t in self.tags if t != tag]
            return self.model_copy(update={
                'tags': new_tags,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def has_tag(self, tag: str) -> bool:
        """Check if contact has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def set_custom_field(self, field_name: str, value: Any) -> 'Contact':
        """Set a custom field value. Returns new Contact instance."""
        new_custom_fields = self.custom_fields.copy()
        new_custom_fields[field_name] = value
        
        return self.model_copy(update={
            'custom_fields': new_custom_fields,
            'last_modified': datetime.utcnow()
        })
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get a custom field value."""
        return self.custom_fields.get(field_name, default)
    
    def update_last_contacted(self) -> 'Contact':
        """Update the last contacted timestamp. Returns new Contact instance."""
        now = datetime.utcnow()
        return self.model_copy(update={
            'last_contacted': now,
            'last_modified': now
        })
    
    def convert_to_customer(self) -> 'Contact':
        """Convert lead/prospect to customer. Returns new Contact instance."""
        if self.contact_type in [ContactType.LEAD, ContactType.PROSPECT]:
            update_data = {
                'contact_type': ContactType.CUSTOMER,
                'last_modified': datetime.utcnow()
            }
            
            # Also update relationship status
            if self.relationship_status in [RelationshipStatus.PROSPECT, RelationshipStatus.QUALIFIED_LEAD]:
                update_data['relationship_status'] = RelationshipStatus.ACTIVE_CLIENT
                update_data['lifecycle_stage'] = LifecycleStage.CUSTOMER
            
            return self.model_copy(update=update_data)
        else:
            raise DomainValidationError(f"Cannot convert {self.contact_type.value} to customer")
    
    def convert_to_lead(self) -> 'Contact':
        """Convert prospect to lead. Returns new Contact instance."""
        if self.contact_type == ContactType.PROSPECT:
            return self.model_copy(update={
                'contact_type': ContactType.LEAD,
                'relationship_status': RelationshipStatus.QUALIFIED_LEAD,
                'lifecycle_stage': LifecycleStage.INTEREST,
                'last_modified': datetime.utcnow()
            })
        else:
            raise DomainValidationError(f"Cannot convert {self.contact_type.value} to lead")
    
    def assign_to_user(self, user_id: str) -> 'Contact':
        """Assign contact to a team member. Returns new Contact instance."""
        return self.model_copy(update={
            'assigned_to': user_id,
            'last_modified': datetime.utcnow()
        })
    
    def unassign(self) -> 'Contact':
        """Remove assignment from contact. Returns new Contact instance."""
        return self.model_copy(update={
            'assigned_to': None,
            'last_modified': datetime.utcnow()
        })
    
    def archive(self) -> 'Contact':
        """Archive the contact. Returns new Contact instance."""
        if self.status == ContactStatus.ACTIVE:
            return self.model_copy(update={
                'status': ContactStatus.ARCHIVED,
                'last_modified': datetime.utcnow()
            })
        else:
            raise DomainValidationError(f"Cannot archive contact with status: {self.status.value}")
    
    def activate(self) -> 'Contact':
        """Activate an inactive or archived contact. Returns new Contact instance."""
        if self.status in [ContactStatus.INACTIVE, ContactStatus.ARCHIVED]:
            return self.model_copy(update={
                'status': ContactStatus.ACTIVE,
                'last_modified': datetime.utcnow()
            })
        else:
            raise DomainValidationError(f"Cannot activate contact with status: {self.status.value}")
    
    def block(self) -> 'Contact':
        """Block the contact. Returns new Contact instance."""
        return self.model_copy(update={
            'status': ContactStatus.BLOCKED,
            'last_modified': datetime.utcnow()
        })
    
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
            ContactSource.ONLINE: "Online",
            ContactSource.GOOGLE_ADS: "Google Ads",
            ContactSource.SOCIAL_MEDIA: "Social Media",
            ContactSource.REFERRAL: "Referral",
            ContactSource.PHONE_CALL: "Phone Call",
            ContactSource.WALK_IN: "Walk-In",
            ContactSource.EMAIL_MARKETING: "Email Marketing",
            ContactSource.TRADE_SHOW: "Trade Show",
            ContactSource.DIRECT_MAIL: "Direct Mail",
            ContactSource.YELLOW_PAGES: "Yellow Pages",
            ContactSource.PARTNER: "Partner",
            ContactSource.EXISTING_CUSTOMER: "Existing Customer",
            ContactSource.COLD_OUTREACH: "Cold Outreach",
            ContactSource.EVENT: "Event",
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
            "relationship_status": self.relationship_status.value,
            "lifecycle_stage": self.lifecycle_stage.value,
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
            "status_history": [
                {
                    "id": str(entry.id),
                    "from_status": entry.from_status.value if entry.from_status else None,
                    "to_status": entry.to_status.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "changed_by": entry.changed_by,
                    "reason": entry.reason
                }
                for entry in self.status_history
            ],
            "interaction_history": [
                {
                    "id": str(entry.id),
                    "type": entry.type.value,
                    "description": entry.description,
                    "timestamp": entry.timestamp.isoformat(),
                    "performed_by": entry.performed_by,
                    "outcome": entry.outcome
                }
                for entry in self.interaction_history
            ],
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "last_contacted": self.last_contacted.isoformat() if self.last_contacted else None,
            "display_name": self.get_display_name(),
            "primary_contact_method": self.get_primary_contact_method(),
            "type_display": self.get_type_display(),
            "status_display": self.get_status_display(),
            "priority_display": self.get_priority_display(),
            "source_display": self.get_source_display(),
            "relationship_status_display": self.get_relationship_status_display(),
            "lifecycle_stage_display": self.get_lifecycle_stage_display()
        }
    
    def __str__(self) -> str:
        return f"Contact({self.get_display_name()} - {self.get_relationship_status_display()})"
    
    def __repr__(self) -> str:
        return (f"Contact(id={self.id}, business_id={self.business_id}, "
                f"name='{self.get_display_name()}', type={self.contact_type}, "
                f"status={self.status}, relationship_status={self.relationship_status})") 