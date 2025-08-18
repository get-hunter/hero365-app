"""
Job Domain Entity

Core business entity for job/project management in Hero365.
Handles job lifecycle, status transitions, cost tracking, and team assignments.
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Annotated
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator
from .job_enums.enums import JobType, JobStatus, JobPriority, JobSource
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError

# Import unified Address value object
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_job_type(v) -> 'JobType':
    """Convert string to JobType enum."""
    if isinstance(v, str):
        return JobType(v)
    return v

def validate_job_status(v) -> 'JobStatus':
    """Convert string to JobStatus enum."""
    if isinstance(v, str):
        return JobStatus(v)
    return v

def validate_job_priority(v) -> 'JobPriority':
    """Convert string to JobPriority enum."""
    if isinstance(v, str):
        return JobPriority(v)
    return v

def validate_job_source(v) -> 'JobSource':
    """Convert string to JobSource enum."""
    if isinstance(v, str):
        return JobSource(v)
    return v


class JobTimeTracking(BaseModel):
    """Value object for job time tracking."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0)
    actual_hours: Optional[Decimal] = Field(default=None, ge=0)
    billable_hours: Optional[Decimal] = Field(default=None, ge=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_time_minutes: int = Field(default=0, ge=0)
    
    @model_validator(mode='after')
    def validate_time_consistency(self):
        """Validate time consistency."""
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError("End time must be after start time")
        return self
    
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


class JobCostEstimate(BaseModel):
    """Value object for job cost estimation."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    labor_cost: Decimal = Field(default=Decimal("0"), ge=0)
    material_cost: Decimal = Field(default=Decimal("0"), ge=0)
    equipment_cost: Decimal = Field(default=Decimal("0"), ge=0)
    overhead_cost: Decimal = Field(default=Decimal("0"), ge=0)
    markup_percentage: Decimal = Field(default=Decimal("20"), ge=0)  # Default 20% markup
    tax_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    
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


class Job(BaseModel):
    """
    Job domain entity representing a service job or project.
    
    This entity contains all business logic for job management,
    status transitions, cost tracking, and team assignments.
    """
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    # Required fields (no default values)
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4
    job_number: str = Field(min_length=1)
    title: str = Field(min_length=1)
    job_type: Annotated[JobType, BeforeValidator(validate_job_type)]
    status: Annotated[JobStatus, BeforeValidator(validate_job_status)]
    priority: Annotated[JobPriority, BeforeValidator(validate_job_priority)]
    source: Annotated[JobSource, BeforeValidator(validate_job_source)]
    job_address: Address
    created_by: str = Field(min_length=1)
    
    # Optional fields (with default values)
    contact_id: Optional[UUID4] = None
    project_id: Optional[UUID4] = None  # Reference to project if job is part of a project
    description: Optional[str] = None
    
    # Location and timing
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Assignment and tracking
    assigned_to: List[str] = Field(default_factory=list)  # User IDs
    time_tracking: JobTimeTracking = Field(default_factory=JobTimeTracking)
    cost_estimate: JobCostEstimate = Field(default_factory=JobCostEstimate)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_requirements: Optional[str] = None
    completion_notes: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit fields
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_date: Optional[datetime] = None
    
    @field_validator('job_number')
    @classmethod
    def validate_job_number_format(cls, v):
        """Validate job number format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Job number cannot be empty")
        return v.strip()
    
    @model_validator(mode='after')
    def validate_job_rules(self):
        """Validate business rules after initialization."""
        self._validate_job_rules()
        return self
    
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
                   job_address: Address, created_by: str,
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
    
    def update_status(self, new_status: JobStatus, user_id: str, notes: Optional[str] = None) -> 'Job':
        """Update job status with business rule validation. Returns new Job instance."""
        if not self._can_transition_to_status(new_status):
            raise BusinessRuleViolationError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        
        old_status = self.status
        now = datetime.now(timezone.utc)
        
        update_data = {
            'status': new_status,
            'last_modified': now
        }
        
        # Handle status-specific logic
        if new_status == JobStatus.IN_PROGRESS and not self.actual_start:
            update_data['actual_start'] = now
        
        if new_status == JobStatus.COMPLETED:
            if not self.actual_end:
                update_data['actual_end'] = now
            update_data['completed_date'] = now
            
            # Auto-calculate actual hours if not set
            if not self.time_tracking.actual_hours and self.actual_start and self.actual_end:
                duration = self.time_tracking.calculate_duration()
                if duration:
                    update_data['time_tracking'] = self.time_tracking.model_copy(update={'actual_hours': duration})
        
        # Add status change note
        if notes:
            old_status_value = old_status.value if hasattr(old_status, 'value') else old_status
            new_status_value = new_status.value if hasattr(new_status, 'value') else new_status
            status_note = f"[{now.strftime('%Y-%m-%d %H:%M')}] Status changed from {old_status_value} to {new_status_value} by {user_id}: {notes}"
            if self.internal_notes:
                update_data['internal_notes'] = f"{self.internal_notes}\n{status_note}"
            else:
                update_data['internal_notes'] = status_note
        
        return self.model_copy(update=update_data)
    
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
    
    def assign_team_member(self, user_id: str) -> 'Job':
        """Assign a team member to the job. Returns new Job instance."""
        if user_id not in self.assigned_to:
            new_assigned = self.assigned_to + [user_id]
            return self.model_copy(update={
                'assigned_to': new_assigned,
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def remove_team_member(self, user_id: str) -> 'Job':
        """Remove a team member from the job. Returns new Job instance."""
        if user_id in self.assigned_to:
            new_assigned = [uid for uid in self.assigned_to if uid != user_id]
            return self.model_copy(update={
                'assigned_to': new_assigned,
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def update_schedule(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> 'Job':
        """Update job schedule with validation. Returns new Job instance."""
        if start_time and end_time and end_time <= start_time:
            raise DomainValidationError("End time must be after start time")
        
        return self.model_copy(update={
            'scheduled_start': start_time,
            'scheduled_end': end_time,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def start_job(self, user_id: str) -> 'Job':
        """Start the job (transition to in progress). Returns new Job instance."""
        if self.status != JobStatus.SCHEDULED:
            raise BusinessRuleViolationError("Job must be scheduled to start")
        
        now = datetime.now(timezone.utc)
        updated_job = self.update_status(JobStatus.IN_PROGRESS, user_id, "Job started")
        return updated_job.model_copy(update={'actual_start': now})
    
    def complete_job(self, user_id: str, completion_notes: Optional[str] = None) -> 'Job':
        """Complete the job. Returns new Job instance."""
        if self.status != JobStatus.IN_PROGRESS:
            raise BusinessRuleViolationError("Job must be in progress to complete")
        
        update_data = {}
        if completion_notes:
            update_data['completion_notes'] = completion_notes
        
        updated_job = self.model_copy(update=update_data) if update_data else self
        return updated_job.update_status(JobStatus.COMPLETED, user_id, "Job completed")
    
    def cancel_job(self, user_id: str, reason: str) -> 'Job':
        """Cancel the job with reason. Returns new Job instance."""
        if self.status in [JobStatus.COMPLETED, JobStatus.INVOICED, JobStatus.PAID]:
            raise BusinessRuleViolationError("Cannot cancel completed or invoiced job")
        
        return self.update_status(JobStatus.CANCELLED, user_id, f"Job cancelled: {reason}")
    
    def add_tag(self, tag: str) -> 'Job':
        """Add a tag to the job. Returns new Job instance."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            new_tags = self.tags + [tag]
            return self.model_copy(update={
                'tags': new_tags,
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def remove_tag(self, tag: str) -> 'Job':
        """Remove a tag from the job. Returns new Job instance."""
        tag = tag.strip().lower()
        if tag in self.tags:
            new_tags = [t for t in self.tags if t != tag]
            return self.model_copy(update={
                'tags': new_tags,
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def update_cost_estimate(self, cost_estimate: JobCostEstimate) -> 'Job':
        """Update job cost estimate. Returns new Job instance."""
        return self.model_copy(update={
            'cost_estimate': cost_estimate,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def update_time_tracking(self, time_tracking: JobTimeTracking) -> 'Job':
        """Update job time tracking. Returns new Job instance."""
        return self.model_copy(update={
            'time_tracking': time_tracking,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def is_overdue(self) -> bool:
        """Check if job is overdue."""
        if self.scheduled_end and self.status in [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS]:
            return datetime.now(timezone.utc) > self.scheduled_end
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
        if hasattr(self.status, 'get_display'):
            return self.status.get_display()
        # Handle status as string
        return str(self.status).replace('_', ' ').title()
    
    def get_priority_display(self) -> str:
        """Get human-readable priority."""
        if hasattr(self.priority, 'get_display'):
            return self.priority.get_display()
        # Handle priority as string
        return str(self.priority).replace('_', ' ').title()
    
    def get_type_display(self) -> str:
        """Get human-readable type."""
        if hasattr(self.job_type, 'get_display'):
            return self.job_type.get_display()
        # Handle job_type as string
        return str(self.job_type).replace('_', ' ').title() 