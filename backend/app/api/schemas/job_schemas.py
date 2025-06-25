"""
Job API Schemas

Pydantic schemas for job management API endpoints.
Handles request/response validation and serialization.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from ...domain.entities.job import JobType, JobStatus, JobPriority, JobSource


# Enums for API documentation
class JobTypeEnum(str, Enum):
    """Job type enumeration for API."""
    SERVICE = "service"
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"
    PROJECT = "project"
    OTHER = "other"


class JobStatusEnum(str, Enum):
    """Job status enumeration for API."""
    DRAFT = "draft"
    QUOTED = "quoted"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INVOICED = "invoiced"
    PAID = "paid"


class JobPriorityEnum(str, Enum):
    """Job priority enumeration for API."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class JobSourceEnum(str, Enum):
    """Job source enumeration for API."""
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


# Base schemas
class JobAddressSchema(BaseModel):
    """Schema for job address."""
    street_address: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    city: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    state: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    postal_code: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    country: str = Field(default="US", max_length=2)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    access_notes: Optional[str] = Field(default=None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "street_address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "12345",
                "country": "US",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "access_notes": "Gate code: 1234"
            }
        }
    }


class JobTimeTrackingSchema(BaseModel):
    """Schema for job time tracking."""
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    actual_hours: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    billable_hours: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_time_minutes: int = Field(default=0, ge=0)

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        if v and info.data.get('start_time') and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "estimated_hours": "2.5",
                "actual_hours": "2.75",
                "billable_hours": "2.5",
                "start_time": "2024-01-15T09:00:00Z",
                "end_time": "2024-01-15T11:45:00Z",
                "break_time_minutes": 15
            }
        }
    }


class JobCostEstimateSchema(BaseModel):
    """Schema for job cost estimation."""
    labor_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    material_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    equipment_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    overhead_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    markup_percentage: Decimal = Field(default=Decimal("20"), ge=0, decimal_places=2)
    tax_percentage: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)

    model_config = {
        "json_schema_extra": {
            "example": {
                "labor_cost": "150.00",
                "material_cost": "75.00",
                "equipment_cost": "25.00",
                "overhead_cost": "30.00",
                "markup_percentage": "20.00",
                "tax_percentage": "8.25",
                "discount_amount": "10.00"
            }
        }
    }


# Request schemas
class JobCreateRequest(BaseModel):
    """Schema for job creation request."""
    contact_id: Optional[uuid.UUID] = None
    job_number: Optional[str] = Field(default=None, max_length=50)
    title: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    description: Optional[str] = Field(default=None, max_length=2000)
    job_type: JobTypeEnum
    priority: JobPriorityEnum = JobPriorityEnum.MEDIUM
    source: JobSourceEnum = JobSourceEnum.OTHER
    job_address: JobAddressSchema
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assigned_to: Optional[List[str]] = Field(default=None, max_length=10)
    tags: Optional[List[str]] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=2000)
    customer_requirements: Optional[str] = Field(default=None, max_length=2000)
    time_tracking: Optional[JobTimeTrackingSchema] = None
    cost_estimate: Optional[JobCostEstimateSchema] = None
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator('scheduled_end')
    @classmethod
    def validate_scheduled_end(cls, v, info):
        if v and info.data.get('scheduled_start') and v <= info.data['scheduled_start']:
            raise ValueError('Scheduled end time must be after start time')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "contact_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "HVAC Maintenance Service",
                "description": "Annual HVAC system maintenance and inspection",
                "job_type": "maintenance",
                "priority": "medium",
                "source": "website",
                "job_address": {
                    "street_address": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "postal_code": "12345"
                },
                "scheduled_start": "2024-01-15T09:00:00Z",
                "scheduled_end": "2024-01-15T12:00:00Z",
                "tags": ["hvac", "maintenance", "routine"],
                "notes": "Customer prefers morning appointments"
            }
        }
    }


class JobUpdateRequest(BaseModel):
    """Schema for job update request."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    job_type: Optional[JobTypeEnum] = None
    priority: Optional[JobPriorityEnum] = None
    source: Optional[JobSourceEnum] = None
    job_address: Optional[JobAddressSchema] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    assigned_to: Optional[List[str]] = Field(default=None, max_length=10)
    tags: Optional[List[str]] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=2000)
    internal_notes: Optional[str] = Field(default=None, max_length=2000)
    customer_requirements: Optional[str] = Field(default=None, max_length=2000)
    completion_notes: Optional[str] = Field(default=None, max_length=2000)
    time_tracking: Optional[JobTimeTrackingSchema] = None
    cost_estimate: Optional[JobCostEstimateSchema] = None
    custom_fields: Optional[Dict[str, Any]] = None

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v


class JobStatusUpdateRequest(BaseModel):
    """Schema for job status update request."""
    status: JobStatusEnum
    notes: Optional[str] = Field(default=None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in_progress",
                "notes": "Started work on site"
            }
        }
    }


class JobAssignmentRequest(BaseModel):
    """Schema for job assignment request."""
    user_ids: List[str] = Field(min_length=1, max_length=10)
    replace_existing: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_ids": ["user123", "user456"],
                "replace_existing": True
            }
        }
    }


class JobBulkUpdateRequest(BaseModel):
    """Schema for bulk job update request."""
    job_ids: List[uuid.UUID] = Field(min_length=1, max_length=50)
    status: Optional[JobStatusEnum] = None
    assigned_to: Optional[str] = None
    tags_to_add: Optional[List[str]] = Field(default=None, max_length=10)
    tags_to_remove: Optional[List[str]] = Field(default=None, max_length=10)
    priority: Optional[JobPriorityEnum] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "status": "scheduled",
                "assigned_to": "user123",
                "tags_to_add": ["urgent"]
            }
        }
    }


class JobSearchRequest(BaseModel):
    """Schema for job search request."""
    search_term: Optional[str] = Field(default=None, max_length=100)
    job_type: Optional[JobTypeEnum] = None
    status: Optional[JobStatusEnum] = None
    priority: Optional[JobPriorityEnum] = None
    source: Optional[JobSourceEnum] = None
    assigned_to: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    scheduled_start_from: Optional[datetime] = None
    scheduled_start_to: Optional[datetime] = None
    scheduled_end_from: Optional[datetime] = None
    scheduled_end_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    is_overdue: Optional[bool] = None
    is_emergency: Optional[bool] = None
    min_revenue: Optional[Decimal] = Field(default=None, ge=0)
    max_revenue: Optional[Decimal] = Field(default=None, ge=0)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    sort_by: str = Field(default="created_date", pattern="^(created_date|last_modified|scheduled_start|title|status|priority)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Response schemas
class JobResponse(BaseModel):
    """Schema for job response."""
    id: uuid.UUID
    business_id: uuid.UUID
    contact_id: Optional[uuid.UUID]
    job_number: str
    title: str
    description: Optional[str]
    job_type: JobTypeEnum
    status: JobStatusEnum
    priority: JobPriorityEnum
    source: JobSourceEnum
    job_address: JobAddressSchema
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    assigned_to: List[str]
    created_by: str
    time_tracking: JobTimeTrackingSchema
    cost_estimate: JobCostEstimateSchema
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

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "business_id": "550e8400-e29b-41d4-a716-446655440001",
                "contact_id": "550e8400-e29b-41d4-a716-446655440002",
                "job_number": "JOB-000001",
                "title": "HVAC Maintenance Service",
                "description": "Annual HVAC system maintenance",
                "job_type": "maintenance",
                "status": "scheduled",
                "priority": "medium",
                "source": "website",
                "is_overdue": False,
                "is_emergency": False,
                "estimated_revenue": "280.00"
            }
        }
    }


class JobListResponse(BaseModel):
    """Schema for job list response."""
    id: uuid.UUID
    job_number: str
    title: str
    job_type: JobTypeEnum
    status: JobStatusEnum
    priority: JobPriorityEnum
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    assigned_to: List[str]
    estimated_revenue: Decimal
    is_overdue: bool
    is_emergency: bool
    created_date: datetime
    last_modified: datetime
    status_display: str
    priority_display: str
    type_display: str

    model_config = {"from_attributes": True}


class JobStatisticsResponse(BaseModel):
    """Schema for job statistics response."""
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_jobs": 150,
                "jobs_by_status": {
                    "draft": 5,
                    "scheduled": 25,
                    "in_progress": 10,
                    "completed": 100,
                    "cancelled": 10
                },
                "overdue_jobs": 3,
                "emergency_jobs": 2,
                "revenue_this_month": "25000.00",
                "completion_rate": 85.5
            }
        }
    }


class JobWorkloadResponse(BaseModel):
    """Schema for job workload response."""
    user_id: str
    total_assigned_jobs: int
    jobs_in_progress: int
    overdue_jobs: int
    scheduled_this_week: int
    total_estimated_hours: Decimal
    total_actual_hours: Decimal
    utilization_rate: float
    completion_rate: float

    model_config = {"from_attributes": True}


class JobScheduleResponse(BaseModel):
    """Schema for job schedule response."""
    date: datetime
    jobs: List[JobListResponse]
    total_jobs: int
    total_hours: Decimal
    conflicts: List[Dict[str, Any]]

    model_config = {"from_attributes": True}


# Pagination response
class JobListPaginatedResponse(BaseModel):
    """Schema for paginated job list response."""
    jobs: List[JobListResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "jobs": [],
                "total": 150,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }
    }


# Error response schemas
class JobErrorResponse(BaseModel):
    """Schema for job error responses."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Job title is required",
                "details": {"field": "title"}
            }
        }
    }


class JobValidationErrorResponse(BaseModel):
    """Schema for job validation error responses."""
    error: str = "ValidationError"
    message: str
    validation_errors: List[Dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "validation_errors": [
                    {
                        "field": "title",
                        "message": "Title is required"
                    }
                ]
            }
        }
    }


# Success response schemas
class JobActionResponse(BaseModel):
    """Schema for job action responses."""
    success: bool = True
    message: str
    job_id: Optional[uuid.UUID] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Job created successfully",
                "job_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    }


class JobBulkActionResponse(BaseModel):
    """Schema for bulk job action responses."""
    success: bool = True
    message: str
    updated_count: int
    failed_count: int = 0
    errors: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Bulk update completed",
                "updated_count": 5,
                "failed_count": 0
            }
        }
    } 