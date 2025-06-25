"""
Job Domain Entity

Core business entity for job/project management in Hero365.
Handles job lifecycle, status transitions, cost tracking, and team assignments.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


class JobType(Enum):
    """Job type enumeration."""
    SERVICE = "service"
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"
    PROJECT = "project"
    OTHER = "other"


class JobStatus(Enum):
    """Job status enumeration with workflow states."""
    DRAFT = "draft"
    QUOTED = "quoted"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INVOICED = "invoiced"
    PAID = "paid"


class JobPriority(Enum):
    """Job priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class JobSource(Enum):
    """How the job was acquired."""
    WEBSITE = "website"
    GOOGLE_ADS = "google_ads"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    PHONE_CALL = "phone_call"
    WALK_IN = "walk_in"
    EMAIL_MARKETING = "email_marketing"
    TRADE_SHOW = "trade_show"
    DIRECT_MAIL = "direct_mail"
    YELLOW_PAGES = "yellow_pages"
    REPEAT_CUSTOMER = "repeat_customer"
    PARTNER = "partner"
    EXISTING_CUSTOMER = "existing_customer"
    COLD_OUTREACH = "cold_outreach"
    EMERGENCY_CALL = "emergency_call"
    EVENT = "event"
    DIRECT = "direct"
    OTHER = "other"


@dataclass
class JobAddress:
    """Value object for job location address."""
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    access_notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate address data."""
        if not self.street_address or not self.street_address.strip():
            raise DomainValidationError("Street address is required")
        if not self.city or not self.city.strip():
            raise DomainValidationError("City is required")
        if not self.state or not self.state.strip():
            raise DomainValidationError("State is required")
        if not self.postal_code or not self.postal_code.strip():
            raise DomainValidationError("Postal code is required")
    
    def get_full_address(self) -> str:
        """Get formatted full address."""
        return f"{self.street_address}, {self.city}, {self.state} {self.postal_code}"
    
    def get_short_address(self) -> str:
        """Get short address for display."""
        return f"{self.city}, {self.state}"


@dataclass
class JobTimeTracking:
    """Value object for job time tracking."""
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    billable_hours: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_time_minutes: int = 0
    
    def __post_init__(self):
        """Validate time tracking data."""
        if self.estimated_hours is not None and self.estimated_hours < 0:
            raise DomainValidationError("Estimated hours cannot be negative")
        if self.actual_hours is not None and self.actual_hours < 0:
            raise DomainValidationError("Actual hours cannot be negative")
        if self.billable_hours is not None and self.billable_hours < 0:
            raise DomainValidationError("Billable hours cannot be negative")
        if self.break_time_minutes < 0:
            raise DomainValidationError("Break time cannot be negative")
    
    def calculate_duration(self) -> Optional[Decimal]:
        """Calculate duration from start and end times."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            hours = Decimal(duration.total_seconds()) / Decimal(3600)
            break_hours = Decimal(self.break_time_minutes) / Decimal(60)
            return hours - break_hours
        return None
    
    def is_overtime(self, standard_hours: Decimal = Decimal("8")) -> bool:
        """Check if job involves overtime."""
        if self.actual_hours:
            return self.actual_hours > standard_hours
        return False


@dataclass
class JobCostEstimate:
    """Value object for job cost estimation."""
    labor_cost: Decimal = Decimal("0")
    material_cost: Decimal = Decimal("0")
    equipment_cost: Decimal = Decimal("0")
    overhead_cost: Decimal = Decimal("0")
    markup_percentage: Decimal = Decimal("20")  # Default 20% markup
    tax_percentage: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    
    def __post_init__(self):
        """Validate cost data."""
        if self.labor_cost < 0:
            raise DomainValidationError("Labor cost cannot be negative")
        if self.material_cost < 0:
            raise DomainValidationError("Material cost cannot be negative")
        if self.equipment_cost < 0:
            raise DomainValidationError("Equipment cost cannot be negative")
        if self.overhead_cost < 0:
            raise DomainValidationError("Overhead cost cannot be negative")
        if self.markup_percentage < 0:
            raise DomainValidationError("Markup percentage cannot be negative")
        if self.tax_percentage < 0:
            raise DomainValidationError("Tax percentage cannot be negative")
        if self.discount_amount < 0:
            raise DomainValidationError("Discount amount cannot be negative")
    
    def get_subtotal(self) -> Decimal:
        """Calculate subtotal before markup and tax."""
        return self.labor_cost + self.material_cost + self.equipment_cost + self.overhead_cost
    
    def get_markup_amount(self) -> Decimal:
        """Calculate markup amount."""
        return self.get_subtotal() * (self.markup_percentage / Decimal("100"))
    
    def get_total_before_tax(self) -> Decimal:
        """Calculate total before tax."""
        return self.get_subtotal() + self.get_markup_amount() - self.discount_amount
    
    def get_tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.get_total_before_tax() * (self.tax_percentage / Decimal("100"))
    
    def get_total_cost(self) -> Decimal:
        """Calculate final total cost."""
        return self.get_total_before_tax() + self.get_tax_amount()
    
    def get_profit_margin(self) -> Decimal:
        """Calculate profit margin percentage."""
        total = self.get_total_cost()
        if total > 0:
            profit = self.get_markup_amount()
            return (profit / total) * Decimal("100")
        return Decimal("0")


@dataclass
class Job:
    """
    Job domain entity representing a service job or project.
    
    This entity contains all business logic for job management,
    status transitions, cost tracking, and team assignments.
    """
    
    # Required fields (no default values)
    id: uuid.UUID
    business_id: uuid.UUID
    job_number: str
    title: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    source: JobSource
    job_address: JobAddress
    created_by: str
    
    # Optional fields (with default values)
    contact_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    
    # Location and timing
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Assignment and tracking
    assigned_to: List[str] = field(default_factory=list)  # User IDs
    time_tracking: JobTimeTracking = field(default_factory=JobTimeTracking)
    cost_estimate: JobCostEstimate = field(default_factory=JobCostEstimate)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_requirements: Optional[str] = None
    completion_notes: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Audit fields
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate job data after initialization."""
        self._validate_job_rules()
    
    def _validate_job_rules(self) -> None:
        """Validate core job business rules."""
        if not self.business_id:
            raise DomainValidationError("Job must belong to a business")
        
        if not self.job_number or not self.job_number.strip():
            raise DomainValidationError("Job number is required")
        
        if not self.title or not self.title.strip():
            raise DomainValidationError("Job title is required")
        
        if not self.created_by:
            raise DomainValidationError("Job must have a creator")
        
        # Validate scheduling
        if self.scheduled_start and self.scheduled_end:
            if self.scheduled_end <= self.scheduled_start:
                raise DomainValidationError("Scheduled end time must be after start time")
        
        if self.actual_start and self.actual_end:
            if self.actual_end <= self.actual_start:
                raise DomainValidationError("Actual end time must be after start time")
    
    @classmethod
    def create_job(cls, business_id: uuid.UUID, contact_id: Optional[uuid.UUID],
                   job_number: str, title: str, description: Optional[str],
                   job_type: JobType, priority: JobPriority, source: JobSource,
                   job_address: JobAddress, created_by: str,
                   scheduled_start: Optional[datetime] = None,
                   scheduled_end: Optional[datetime] = None,
                   assigned_to: Optional[List[str]] = None,
                   tags: Optional[List[str]] = None,
                   notes: Optional[str] = None,
                   customer_requirements: Optional[str] = None,
                   custom_fields: Optional[Dict[str, Any]] = None) -> 'Job':
        """Create a new job with validation."""
        
        job = cls(
            id=uuid.uuid4(),
            business_id=business_id,
            contact_id=contact_id,
            job_number=job_number,
            title=title,
            description=description,
            job_type=job_type,
            status=JobStatus.DRAFT,
            priority=priority,
            source=source,
            job_address=job_address,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            assigned_to=assigned_to or [],
            created_by=created_by,
            tags=tags or [],
            notes=notes,
            customer_requirements=customer_requirements,
            custom_fields=custom_fields or {}
        )
        
        return job
    
    def update_status(self, new_status: JobStatus, user_id: str, notes: Optional[str] = None) -> None:
        """Update job status with business rule validation."""
        if not self._can_transition_to_status(new_status):
            raise BusinessRuleViolationError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        
        old_status = self.status
        self.status = new_status
        self.last_modified = datetime.utcnow()
        
        # Handle status-specific logic
        if new_status == JobStatus.IN_PROGRESS and not self.actual_start:
            self.actual_start = datetime.utcnow()
        
        if new_status == JobStatus.COMPLETED:
            if not self.actual_end:
                self.actual_end = datetime.utcnow()
            self.completed_date = datetime.utcnow()
            
            # Auto-calculate actual hours if not set
            if not self.time_tracking.actual_hours and self.actual_start and self.actual_end:
                duration = self.time_tracking.calculate_duration()
                if duration:
                    self.time_tracking.actual_hours = duration
        
        # Add status change note
        if notes:
            status_note = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Status changed from {old_status.value} to {new_status.value} by {user_id}: {notes}"
            if self.internal_notes:
                self.internal_notes += f"\n{status_note}"
            else:
                self.internal_notes = status_note
    
    def _can_transition_to_status(self, new_status: JobStatus) -> bool:
        """Check if status transition is allowed."""
        # Define allowed transitions
        allowed_transitions = {
            JobStatus.DRAFT: [JobStatus.QUOTED, JobStatus.SCHEDULED, JobStatus.CANCELLED],
            JobStatus.QUOTED: [JobStatus.SCHEDULED, JobStatus.DRAFT, JobStatus.CANCELLED],
            JobStatus.SCHEDULED: [JobStatus.IN_PROGRESS, JobStatus.ON_HOLD, JobStatus.CANCELLED],
            JobStatus.IN_PROGRESS: [JobStatus.COMPLETED, JobStatus.ON_HOLD, JobStatus.CANCELLED],
            JobStatus.ON_HOLD: [JobStatus.IN_PROGRESS, JobStatus.SCHEDULED, JobStatus.CANCELLED],
            JobStatus.COMPLETED: [JobStatus.INVOICED],
            JobStatus.INVOICED: [JobStatus.PAID],
            JobStatus.CANCELLED: [],  # Terminal state
            JobStatus.PAID: []  # Terminal state
        }
        
        return new_status in allowed_transitions.get(self.status, [])
    
    def assign_team_member(self, user_id: str) -> None:
        """Assign a team member to the job."""
        if user_id not in self.assigned_to:
            self.assigned_to.append(user_id)
            self.last_modified = datetime.utcnow()
    
    def remove_team_member(self, user_id: str) -> None:
        """Remove a team member from the job."""
        if user_id in self.assigned_to:
            self.assigned_to.remove(user_id)
            self.last_modified = datetime.utcnow()
    
    def update_schedule(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> None:
        """Update job schedule with validation."""
        if start_time and end_time and end_time <= start_time:
            raise DomainValidationError("End time must be after start time")
        
        self.scheduled_start = start_time
        self.scheduled_end = end_time
        self.last_modified = datetime.utcnow()
    
    def start_job(self, user_id: str) -> None:
        """Start the job (transition to in progress)."""
        if self.status != JobStatus.SCHEDULED:
            raise BusinessRuleViolationError("Job must be scheduled to start")
        
        self.update_status(JobStatus.IN_PROGRESS, user_id, "Job started")
        self.actual_start = datetime.utcnow()
    
    def complete_job(self, user_id: str, completion_notes: Optional[str] = None) -> None:
        """Complete the job."""
        if self.status != JobStatus.IN_PROGRESS:
            raise BusinessRuleViolationError("Job must be in progress to complete")
        
        self.completion_notes = completion_notes
        self.update_status(JobStatus.COMPLETED, user_id, "Job completed")
    
    def cancel_job(self, user_id: str, reason: str) -> None:
        """Cancel the job with reason."""
        if self.status in [JobStatus.COMPLETED, JobStatus.INVOICED, JobStatus.PAID]:
            raise BusinessRuleViolationError("Cannot cancel completed or invoiced job")
        
        self.update_status(JobStatus.CANCELLED, user_id, f"Job cancelled: {reason}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the job."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the job."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.utcnow()
    
    def update_cost_estimate(self, cost_estimate: JobCostEstimate) -> None:
        """Update job cost estimate."""
        self.cost_estimate = cost_estimate
        self.last_modified = datetime.utcnow()
    
    def update_time_tracking(self, time_tracking: JobTimeTracking) -> None:
        """Update job time tracking."""
        self.time_tracking = time_tracking
        self.last_modified = datetime.utcnow()
    
    def is_overdue(self) -> bool:
        """Check if job is overdue."""
        if self.scheduled_end and self.status in [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS]:
            return datetime.utcnow() > self.scheduled_end
        return False
    
    def is_emergency(self) -> bool:
        """Check if job is emergency priority."""
        return self.priority == JobPriority.EMERGENCY
    
    def get_duration_days(self) -> Optional[int]:
        """Get job duration in days."""
        if self.scheduled_start and self.scheduled_end:
            return (self.scheduled_end.date() - self.scheduled_start.date()).days
        return None
    
    def get_estimated_revenue(self) -> Decimal:
        """Get estimated revenue from cost estimate."""
        return self.cost_estimate.get_total_cost()
    
    def get_profit_margin(self) -> Decimal:
        """Get profit margin percentage."""
        return self.cost_estimate.get_profit_margin()
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        status_display = {
            JobStatus.DRAFT: "Draft",
            JobStatus.QUOTED: "Quoted",
            JobStatus.SCHEDULED: "Scheduled",
            JobStatus.IN_PROGRESS: "In Progress",
            JobStatus.ON_HOLD: "On Hold",
            JobStatus.COMPLETED: "Completed",
            JobStatus.CANCELLED: "Cancelled",
            JobStatus.INVOICED: "Invoiced",
            JobStatus.PAID: "Paid"
        }
        return status_display.get(self.status, self.status.value.title())
    
    def get_priority_display(self) -> str:
        """Get human-readable priority."""
        priority_display = {
            JobPriority.LOW: "Low",
            JobPriority.MEDIUM: "Medium",
            JobPriority.HIGH: "High",
            JobPriority.URGENT: "Urgent",
            JobPriority.EMERGENCY: "Emergency"
        }
        return priority_display.get(self.priority, self.priority.value.title())
    
    def get_type_display(self) -> str:
        """Get human-readable type."""
        type_display = {
            JobType.SERVICE: "Service",
            JobType.INSTALLATION: "Installation",
            JobType.MAINTENANCE: "Maintenance",
            JobType.REPAIR: "Repair",
            JobType.INSPECTION: "Inspection",
            JobType.CONSULTATION: "Consultation",
            JobType.EMERGENCY: "Emergency",
            JobType.PROJECT: "Project",
            JobType.OTHER: "Other"
        }
        return type_display.get(self.job_type, self.job_type.value.title()) 