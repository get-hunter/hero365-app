"""
Project Data Transfer Objects

Pydantic DTOs for project-related data transfer operations.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field
from ...domain.enums import ProjectType, ProjectStatus, ProjectPriority
from .contact_dto import ContactAddressDTO


class ProjectCreateDTO(BaseModel):
    """DTO for creating a new project."""
    business_id: uuid.UUID
    project_number: Optional[str] = Field(default=None, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    project_type: ProjectType
    status: ProjectStatus
    priority: ProjectPriority
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = Field(default=None, max_length=200)
    client_email: Optional[str] = Field(default=None, max_length=200)
    client_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[ContactAddressDTO] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0)
    actual_hours: Optional[Decimal] = Field(default=None, ge=0)
    budget_amount: Optional[Decimal] = Field(default=None, ge=0)
    actual_cost: Optional[Decimal] = Field(default=None, ge=0)
    manager_id: Optional[uuid.UUID] = None
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ProjectUpdateDTO(BaseModel):
    """DTO for updating project information."""
    project_id: uuid.UUID
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = Field(default=None, max_length=200)
    client_email: Optional[str] = Field(default=None, max_length=200)
    client_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[ContactAddressDTO] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0)
    actual_hours: Optional[Decimal] = Field(default=None, ge=0)
    budget_amount: Optional[Decimal] = Field(default=None, ge=0)
    actual_cost: Optional[Decimal] = Field(default=None, ge=0)
    manager_id: Optional[uuid.UUID] = None
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ProjectStatusUpdateDTO(BaseModel):
    """DTO for updating project status."""
    project_id: uuid.UUID
    status: ProjectStatus
    notes: Optional[str] = Field(default=None, max_length=500)


class ProjectResponseDTO(BaseModel):
    """DTO for project response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    project_number: Optional[str]
    name: str
    description: str
    created_by: str
    client_id: uuid.UUID
    client_name: str
    client_address: Optional[ContactAddressDTO]
    project_type: ProjectType
    status: ProjectStatus
    priority: ProjectPriority
    start_date: datetime
    end_date: Optional[datetime]
    estimated_budget: Decimal
    actual_cost: Decimal
    manager: Optional[str]
    manager_id: Optional[uuid.UUID]
    team_members: List[str]
    tags: List[str]
    notes: Optional[str]
    created_date: datetime
    last_modified: datetime
    
    # Computed fields
    is_overdue: bool
    is_over_budget: bool
    budget_variance: Decimal
    budget_variance_percentage: Optional[Decimal]
    duration_days: Optional[int]
    status_display: str
    priority_display: str
    type_display: str


class ProjectListDTO(BaseModel):
    """DTO for project list items."""
    id: uuid.UUID
    name: str
    client_id: uuid.UUID
    client_name: str
    project_type: ProjectType
    status: ProjectStatus
    priority: ProjectPriority
    start_date: datetime
    end_date: Optional[datetime]
    estimated_budget: Decimal
    actual_cost: Decimal
    manager: Optional[str]
    is_overdue: bool
    is_over_budget: bool
    created_date: datetime
    last_modified: datetime
    status_display: str
    priority_display: str
    type_display: str


class ProjectSearchDTO(BaseModel):
    """DTO for project search parameters."""
    search: Optional[str] = Field(default=None, max_length=100)
    status: Optional[ProjectStatus] = None
    project_type: Optional[ProjectType] = None
    priority: Optional[ProjectPriority] = None
    client_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    is_overdue: Optional[bool] = None
    is_over_budget: Optional[bool] = None
    min_budget: Optional[Decimal] = Field(default=None, ge=0)
    max_budget: Optional[Decimal] = Field(default=None, ge=0)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    sort_by: str = Field(default="created_date")
    sort_order: str = Field(default="desc")


class ProjectTemplateCreateDTO(BaseModel):
    """DTO for creating a new project template."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    project_type: ProjectType
    priority: ProjectPriority
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0)
    estimated_duration: Optional[int] = Field(default=None, gt=0)
    tags: Optional[List[str]] = None


class ProjectTemplateUpdateDTO(BaseModel):
    """DTO for updating project template."""
    template_id: uuid.UUID
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    project_type: Optional[ProjectType] = None
    priority: Optional[ProjectPriority] = None
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0)
    estimated_duration: Optional[int] = Field(default=None, gt=0)
    tags: Optional[List[str]] = None


class ProjectTemplateResponseDTO(BaseModel):
    """DTO for project template response data."""
    id: uuid.UUID
    business_id: Optional[uuid.UUID]
    name: str
    description: str
    project_type: ProjectType
    priority: ProjectPriority
    estimated_budget: Decimal
    estimated_duration: Optional[int]
    tags: List[str]
    is_system_template: bool
    created_date: datetime
    last_modified: datetime


class ProjectCreateFromTemplateDTO(BaseModel):
    """DTO for creating project from template."""
    project_number: Optional[str] = Field(default=None, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: ProjectStatus
    priority: Optional[ProjectPriority] = None
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = Field(default=None, max_length=200)
    client_email: Optional[str] = Field(default=None, max_length=200)
    client_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[ContactAddressDTO] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0)
    budget_amount: Optional[Decimal] = Field(default=None, ge=0)
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ProjectBudgetSummaryDTO(BaseModel):
    """DTO for project budget summary data."""
    total_budget: Decimal = Field(..., ge=0)
    total_actual: Decimal = Field(..., ge=0)
    variance: Decimal
    project_count: int = Field(..., ge=0)


class ProjectStatisticsDTO(BaseModel):
    """DTO for project statistics data."""
    total_projects: int = Field(..., ge=0)
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    by_type: Dict[str, int]
    budget_totals: ProjectBudgetSummaryDTO


class ProjectAnalyticsDTO(BaseModel):
    """DTO for project analytics data."""
    business_id: uuid.UUID
    total_projects: int
    active_projects: int
    completed_projects: int
    projects_by_status: Dict[str, int]
    projects_by_type: Dict[str, int]
    projects_by_priority: Dict[str, int]
    budget_analytics: Dict[str, Any]
    timeline_analytics: Dict[str, Any]
    overdue_projects: int
    projects_over_budget: int


class ProjectAssignmentDTO(BaseModel):
    """DTO for project team assignment operations."""
    user_ids: List[str] = Field(..., min_length=1)
    replace_existing: bool = Field(default=False)


class ProjectJobAssignmentDTO(BaseModel):
    """DTO for project-job assignment operations."""
    project_id: uuid.UUID
    job_ids: List[uuid.UUID]


class ProjectBulkUpdateDTO(BaseModel):
    """DTO for bulk project updates."""
    project_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=50)
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    manager_id: Optional[uuid.UUID] = None
    tags_to_add: Optional[List[str]] = None
    tags_to_remove: Optional[List[str]] = None


class ProjectTimelineDTO(BaseModel):
    """DTO for project timeline data."""
    project_id: uuid.UUID
    milestones: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    progress_percentage: float = Field(..., ge=0, le=100)


class ProjectFinancialSummaryDTO(BaseModel):
    """DTO for project financial summary."""
    project_id: uuid.UUID
    estimated_budget: Decimal
    actual_cost: Decimal
    budget_variance: Decimal
    budget_variance_percentage: Optional[Decimal]
    cost_breakdown: Dict[str, Decimal]
    payment_schedule: Optional[List[Dict[str, Any]]] = None


class ProjectTeamAssignmentDTO(BaseModel):
    """DTO for project team assignment operations."""
    project_id: uuid.UUID
    team_member_ids: List[str]
    manager_id: Optional[uuid.UUID] = None
    replace_existing: bool = False


class ProjectReportDTO(BaseModel):
    """DTO for project reports."""
    report_type: str
    date_range: Dict[str, datetime]
    filters: Dict[str, Any]
    projects: List[ProjectListDTO]
    summary: Dict[str, Any]


class ProjectNotificationDTO(BaseModel):
    """DTO for project-related notifications."""
    project_id: uuid.UUID
    notification_type: str
    recipient_ids: List[str]
    message: str
    priority: str = Field(default="medium")
    scheduled_date: Optional[datetime] = None


class ProjectValidationDTO(BaseModel):
    """DTO for project validation results."""
    project_id: uuid.UUID
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class ProjectExportDTO(BaseModel):
    """DTO for project data export."""
    project_ids: List[uuid.UUID]
    export_format: str = Field(default="csv")
    include_jobs: bool = False
    include_financials: bool = False
    include_timeline: bool = False
    date_range: Optional[Dict[str, datetime]] = None 