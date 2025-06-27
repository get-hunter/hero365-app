"""
Job Data Transfer Objects (DTOs)

DTOs for job management operations in Hero365.
Used for data transfer between application layers.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ...domain.enums import JobType, JobStatus, JobPriority, JobSource
from ...domain.entities.job import JobAddress, JobTimeTracking, JobCostEstimate


@dataclass
class JobAddressDTO:
    """DTO for job address information."""
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    access_notes: Optional[str] = None


@dataclass
class JobTimeTrackingDTO:
    """DTO for job time tracking information."""
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    billable_hours: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_time_minutes: int = 0


@dataclass
class JobCostEstimateDTO:
    """DTO for job cost estimation."""
    labor_cost: Decimal = Decimal("0")
    material_cost: Decimal = Decimal("0")
    equipment_cost: Decimal = Decimal("0")
    overhead_cost: Decimal = Decimal("0")
    markup_percentage: Decimal = Decimal("20")
    tax_percentage: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")


@dataclass
class JobCreateDTO:
    """DTO for creating a new job."""
    contact_id: Optional[uuid.UUID]
    job_number: Optional[str]  # Will be auto-generated if not provided
    title: str
    description: Optional[str]
    job_type: JobType
    priority: JobPriority
    source: JobSource
    job_address: JobAddressDTO
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assigned_to: Optional[List[str]] = None  # User IDs
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    customer_requirements: Optional[str] = None
    time_tracking: Optional[JobTimeTrackingDTO] = None
    cost_estimate: Optional[JobCostEstimateDTO] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class JobUpdateDTO:
    """DTO for updating an existing job."""
    title: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[JobType] = None
    priority: Optional[JobPriority] = None
    source: Optional[JobSource] = None
    job_address: Optional[JobAddressDTO] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assigned_to: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_requirements: Optional[str] = None
    completion_notes: Optional[str] = None
    time_tracking: Optional[JobTimeTrackingDTO] = None
    cost_estimate: Optional[JobCostEstimateDTO] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class JobResponseDTO:
    """DTO for job response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    contact_id: Optional[uuid.UUID]
    contact: Optional['JobContactDTO']  # Add contact data
    job_number: str
    title: str
    description: Optional[str]
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    source: JobSource
    job_address: JobAddressDTO
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    assigned_to: List[str]
    created_by: str
    time_tracking: JobTimeTrackingDTO
    cost_estimate: JobCostEstimateDTO
    tags: List[str]
    notes: Optional[str]
    internal_notes: Optional[str]
    customer_requirements: Optional[str]
    completion_notes: Optional[str]
    custom_fields: Dict[str, Any]
    created_date: datetime
    last_modified: datetime
    completed_date: Optional[datetime]
    
    # Computed fields
    is_overdue: bool
    is_emergency: bool
    duration_days: Optional[int]
    estimated_revenue: Decimal
    profit_margin: Decimal
    status_display: str
    priority_display: str
    type_display: str


@dataclass
class JobListDTO:
    """DTO for job list response with minimal data."""
    id: uuid.UUID
    contact_id: Optional[uuid.UUID]
    contact: Optional['JobContactDTO']  # Add contact data
    job_number: str
    title: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    assigned_to: List[str]
    estimated_revenue: Decimal
    is_overdue: bool
    is_emergency: bool
    created_date: datetime
    last_modified: datetime
    
    # Display fields
    status_display: str
    priority_display: str
    type_display: str


@dataclass
class JobSearchDTO:
    """DTO for job search parameters."""
    search_term: Optional[str] = None
    job_type: Optional[JobType] = None
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    source: Optional[JobSource] = None
    assigned_to: Optional[str] = None  # User ID
    contact_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    scheduled_start_from: Optional[datetime] = None
    scheduled_start_to: Optional[datetime] = None
    scheduled_end_from: Optional[datetime] = None
    scheduled_end_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    is_overdue: Optional[bool] = None
    is_emergency: Optional[bool] = None
    min_revenue: Optional[Decimal] = None
    max_revenue: Optional[Decimal] = None
    skip: int = 0
    limit: int = 100
    sort_by: str = "created_date"
    sort_order: str = "desc"  # asc or desc


@dataclass
class JobStatusUpdateDTO:
    """DTO for updating job status."""
    status: JobStatus
    notes: Optional[str] = None


@dataclass
class JobAssignmentDTO:
    """DTO for job assignment operations."""
    user_ids: List[str]
    replace_existing: bool = False  # If True, replace all assignments; if False, add to existing


@dataclass
class JobBulkUpdateDTO:
    """DTO for bulk job operations."""
    job_ids: List[uuid.UUID]
    status: Optional[JobStatus] = None
    assigned_to: Optional[str] = None  # User ID to assign to
    tags_to_add: Optional[List[str]] = None
    tags_to_remove: Optional[List[str]] = None
    priority: Optional[JobPriority] = None


@dataclass
class JobScheduleUpdateDTO:
    """DTO for updating job schedule."""
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]


@dataclass
class JobTimeTrackingUpdateDTO:
    """DTO for updating job time tracking."""
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    billable_hours: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_time_minutes: Optional[int] = None


@dataclass
class JobCostUpdateDTO:
    """DTO for updating job cost estimate."""
    labor_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None
    equipment_cost: Optional[Decimal] = None
    overhead_cost: Optional[Decimal] = None
    markup_percentage: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None


@dataclass
class JobStatisticsDTO:
    """DTO for job statistics."""
    total_jobs: int
    jobs_by_status: Dict[str, int]
    jobs_by_type: Dict[str, int]
    jobs_by_priority: Dict[str, int]
    overdue_jobs: int
    emergency_jobs: int
    jobs_in_progress: int
    completed_this_month: int
    revenue_this_month: Decimal
    average_job_value: Decimal
    top_job_types: List[Dict[str, Any]]
    completion_rate: float
    on_time_completion_rate: float


@dataclass
class JobRevenueDTO:
    """DTO for job revenue information."""
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    total_jobs: int
    average_job_value: Decimal
    revenue_by_type: Dict[str, Decimal]
    revenue_by_month: List[Dict[str, Any]]
    top_revenue_jobs: List[Dict[str, Any]]


@dataclass
class JobWorkloadDTO:
    """DTO for user workload information."""
    user_id: str
    total_assigned_jobs: int
    jobs_in_progress: int
    overdue_jobs: int
    scheduled_this_week: int
    total_estimated_hours: Decimal
    total_actual_hours: Decimal
    utilization_rate: float
    completion_rate: float


@dataclass
class JobScheduleDTO:
    """DTO for job schedule information."""
    date: datetime
    jobs: List[JobListDTO]
    total_jobs: int
    total_hours: Decimal
    conflicts: List[Dict[str, Any]]  # Overlapping jobs


@dataclass
class JobExportDTO:
    """DTO for job data export."""
    id: str
    job_number: str
    title: str
    description: str
    job_type: str
    status: str
    priority: str
    source: str
    contact_name: str
    contact_email: str
    contact_phone: str
    job_address: str
    scheduled_start: str
    scheduled_end: str
    actual_start: str
    actual_end: str
    assigned_to: str
    estimated_hours: str
    actual_hours: str
    billable_hours: str
    labor_cost: str
    material_cost: str
    equipment_cost: str
    total_cost: str
    profit_margin: str
    tags: str
    notes: str
    completion_notes: str
    created_date: str
    completed_date: str


@dataclass
class JobImportDTO:
    """DTO for job data import."""
    job_number: Optional[str]
    title: str
    description: Optional[str]
    job_type: str
    priority: str
    source: str
    contact_email: Optional[str]  # Will lookup contact by email
    street_address: str
    city: str
    state: str
    postal_code: str
    scheduled_start: Optional[str]
    scheduled_end: Optional[str]
    assigned_to: Optional[str]  # User email or ID
    estimated_hours: Optional[str]
    labor_cost: Optional[str]
    material_cost: Optional[str]
    equipment_cost: Optional[str]
    tags: Optional[str]  # Comma-separated
    notes: Optional[str]
    customer_requirements: Optional[str]


@dataclass
class JobImportResultDTO:
    """DTO for job import results."""
    total_processed: int
    successful_imports: int
    failed_imports: int
    errors: List[Dict[str, Any]]
    imported_job_ids: List[uuid.UUID]
    warnings: List[str]


@dataclass
class JobConversionDTO:
    """DTO for converting job status or type."""
    target_status: Optional[JobStatus] = None
    target_type: Optional[JobType] = None
    notes: Optional[str] = None
    update_cost_estimate: bool = False
    new_cost_estimate: Optional[JobCostEstimateDTO] = None


@dataclass
class JobContactDTO:
    """DTO for contact information in job responses."""
    id: uuid.UUID
    display_name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    primary_contact_method: str = "" 