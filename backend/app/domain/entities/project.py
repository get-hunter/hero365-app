"""
Project Domain Entity

Represents a project in the domain with associated business rules and behaviors.
Projects are higher-level constructs that can contain multiple jobs and track
overall progress, budget, and timeline management.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .project_enums.enums import ProjectType, ProjectStatus, ProjectPriority
from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..value_objects.address import Address


class Project(BaseModel):
    """
    Project domain entity representing a construction/service project.
    
    This entity contains business logic for project management,
    status transitions, budget tracking, and team assignments.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True
    )
    
    # Required fields
    id: uuid.UUID
    business_id: uuid.UUID
    project_number: Optional[str] = Field(None, max_length=50, description="Unique project number within business")
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    created_by: str = Field(..., description="User ID who created this project")
    client_id: uuid.UUID
    client_name: str = Field(..., min_length=1, max_length=200)
    address: Optional[Address] = Field(None, description="Project address using unified address system")
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.PLANNING
    priority: ProjectPriority
    start_date: datetime
    
    # Optional fields
    end_date: Optional[datetime] = None
    estimated_budget: Decimal = Field(default=Decimal("0"), ge=0)
    actual_cost: Decimal = Field(default=Decimal("0"), ge=0)
    manager: Optional[str] = Field(None, max_length=200, description="Manager name")
    manager_id: Optional[uuid.UUID] = Field(None, description="Manager user ID")
    team_members: List[str] = Field(default_factory=list, description="Array of team member names/IDs")
    tags: List[str] = Field(default_factory=list, description="Array of tag strings")
    notes: Optional[str] = Field(None, max_length=2000)
    
    # Audit fields
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def model_post_init(self, __context) -> None:
        """Validate project data after initialization."""
        self._validate_project_rules()
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate end date is after start date."""
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @field_validator('name', 'description', 'client_name')
    @classmethod
    def validate_required_strings(cls, v):
        """Validate required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty strings, convert to lowercase
            v = list(set(tag.strip().lower() for tag in v if tag and tag.strip()))
        return v
    
    def _validate_project_rules(self) -> None:
        """Validate core project business rules."""
        # Additional business rules beyond field validation
        pass
    
    @classmethod
    def create_project(cls, business_id: uuid.UUID, name: str, description: str,
                      created_by: str, client_id: uuid.UUID, client_name: str,
                      address: Optional[Address], project_type: ProjectType,
                      priority: ProjectPriority, start_date: datetime,
                      project_number: Optional[str] = None,
                      end_date: Optional[datetime] = None,
                      estimated_budget: Optional[Decimal] = None,
                      manager_id: Optional[uuid.UUID] = None,
                      team_members: Optional[List[str]] = None,
                      tags: Optional[List[str]] = None,
                      notes: Optional[str] = None) -> 'Project':
        """Create a new project with validation."""
        
        project = cls(
            id=uuid.uuid4(),
            business_id=business_id,
            project_number=project_number,
            name=name,
            description=description,
            created_by=created_by,
            client_id=client_id,
            client_name=client_name,
            address=address,
            project_type=project_type,
            status=ProjectStatus.PLANNING,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            estimated_budget=estimated_budget or Decimal("0"),
            manager_id=manager_id,
            team_members=team_members or [],
            tags=tags or [],
            notes=notes
        )
        
        return project
    
    def update_status(self, new_status: ProjectStatus) -> None:
        """Update project status with validation."""
        if not self._can_transition_to_status(new_status):
            raise BusinessRuleViolationError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        
        self.status = new_status
        self.last_modified = datetime.now(timezone.utc)
    
    def _can_transition_to_status(self, new_status: ProjectStatus) -> bool:
        """Check if status transition is allowed."""
        allowed_transitions = {
            ProjectStatus.PLANNING: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.ACTIVE: [ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
            ProjectStatus.ON_HOLD: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.COMPLETED: [],  # Terminal state
            ProjectStatus.CANCELLED: []  # Terminal state
        }
        
        # Handle both string and enum values for current status
        current_status = ProjectStatus(self.status) if isinstance(self.status, str) else self.status
        return new_status in allowed_transitions.get(current_status, [])
    
    def assign_team_member(self, user_id: str) -> None:
        """Assign a team member to the project."""
        if user_id not in self.team_members:
            self.team_members.append(user_id)
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_team_member(self, user_id: str) -> None:
        """Remove a team member from the project."""
        if user_id in self.team_members:
            self.team_members.remove(user_id)
            self.last_modified = datetime.now(timezone.utc)
    
    def update_budget(self, estimated_budget: Decimal) -> None:
        """Update project budget with validation."""
        if estimated_budget < 0:
            raise DomainValidationError("Budget cannot be negative")
        
        self.estimated_budget = estimated_budget
        self.last_modified = datetime.now(timezone.utc)
    
    def update_actual_cost(self, actual_cost: Decimal) -> None:
        """Update actual cost with validation."""
        if actual_cost < 0:
            raise DomainValidationError("Actual cost cannot be negative")
        
        self.actual_cost = actual_cost
        self.last_modified = datetime.now(timezone.utc)
    
    def update_schedule(self, start_date: datetime, end_date: Optional[datetime] = None) -> None:
        """Update project schedule with validation."""
        if end_date and end_date <= start_date:
            raise DomainValidationError("End date must be after start date")
        
        self.start_date = start_date
        self.end_date = end_date
        self.last_modified = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag and tag.strip() and tag not in self.tags:
            self.tags.append(tag.strip())
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def update_notes(self, notes: Optional[str]) -> None:
        """Update project notes."""
        self.notes = notes
        self.last_modified = datetime.now(timezone.utc)
    
    def get_budget_variance(self) -> Decimal:
        """Calculate budget variance (actual - estimated)."""
        return self.actual_cost - self.estimated_budget
    
    def get_budget_variance_percentage(self) -> Optional[Decimal]:
        """Calculate budget variance as percentage."""
        if self.estimated_budget == 0:
            return None
        return (self.get_budget_variance() / self.estimated_budget) * Decimal("100")
    
    def is_over_budget(self) -> bool:
        """Check if project is over budget."""
        return self.actual_cost > self.estimated_budget
    
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if self.end_date:
            # Handle both string and enum values for status
            status_value = self.status if isinstance(self.status, str) else self.status.value
            if status_value not in [ProjectStatus.COMPLETED.value, ProjectStatus.CANCELLED.value]:
                return datetime.now(timezone.utc) > self.end_date
        return False
    
    def get_duration_days(self) -> Optional[int]:
        """Get project duration in days."""
        if self.end_date:
            return (self.end_date.date() - self.start_date.date()).days
        return None
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        if isinstance(self.status, str):
            return ProjectStatus(self.status).get_display()
        return self.status.get_display()
    
    def get_priority_display(self) -> str:
        """Get human-readable priority."""
        if isinstance(self.priority, str):
            return ProjectPriority(self.priority).get_display()
        return self.priority.get_display()
    
    def get_type_display(self) -> str:
        """Get human-readable type."""
        if isinstance(self.project_type, str):
            return ProjectType(self.project_type).get_display()
        return self.project_type.get_display()
    
    def can_be_deleted(self) -> bool:
        """Check if project can be deleted."""
        # Projects can only be deleted if they are in planning or cancelled status
        status_value = self.status if isinstance(self.status, str) else self.status.value
        return status_value in [ProjectStatus.PLANNING.value, ProjectStatus.CANCELLED.value]
    
    def is_active(self) -> bool:
        """Check if project is currently active."""
        status_value = self.status if isinstance(self.status, str) else self.status.value
        return status_value == ProjectStatus.ACTIVE.value
    
    def is_completed(self) -> bool:
        """Check if project is completed."""
        status_value = self.status if isinstance(self.status, str) else self.status.value
        return status_value == ProjectStatus.COMPLETED.value


class ProjectTemplate(BaseModel):
    """
    Project Template entity for creating standardized project configurations.
    
    Templates allow businesses to quickly create projects with predefined
    settings, budgets, and configurations.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True
    )
    
    # Required fields
    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    project_type: ProjectType
    priority: ProjectPriority
    
    # Optional business/system template
    business_id: Optional[uuid.UUID] = Field(None, description="None for system templates")
    is_system_template: bool = False
    
    # Template configuration
    estimated_budget: Decimal = Field(default=Decimal("0"), ge=0)
    estimated_duration: Optional[int] = Field(None, gt=0, description="Duration in days")
    tags: List[str] = Field(default_factory=list)
    
    # Audit fields
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('name', 'description')
    @classmethod
    def validate_required_strings(cls, v):
        """Validate required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty strings, convert to lowercase
            v = list(set(tag.strip().lower() for tag in v if tag and tag.strip()))
        return v
    
    def model_post_init(self, __context) -> None:
        """Validate template data after initialization."""
        self._validate_template_rules()
    
    def _validate_template_rules(self) -> None:
        """Validate template business rules."""
        # Additional business rules beyond field validation
        pass
    
    @classmethod
    def create_template(cls, name: str, description: str, project_type: ProjectType,
                       priority: ProjectPriority, business_id: Optional[uuid.UUID] = None,
                       estimated_budget: Optional[Decimal] = None,
                       estimated_duration: Optional[int] = None,
                       tags: Optional[List[str]] = None) -> 'ProjectTemplate':
        """Create a new project template with validation."""
        
        template = cls(
            id=uuid.uuid4(),
            business_id=business_id,
            name=name,
            description=description,
            project_type=project_type,
            priority=priority,
            estimated_budget=estimated_budget or Decimal("0"),
            estimated_duration=estimated_duration,
            tags=tags or [],
            is_system_template=business_id is None
        )
        
        return template
    
    def update_template(self, **kwargs) -> None:
        """Update template with validation."""
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def is_accessible_by_business(self, business_id: uuid.UUID) -> bool:
        """Check if template is accessible by a specific business."""
        # System templates are accessible by all businesses
        if self.is_system_template:
            return True
        # Business templates are only accessible by the owning business
        return self.business_id == business_id 