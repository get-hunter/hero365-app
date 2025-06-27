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

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from ...utils import format_datetime_utc
# Import centralized enums
from ...domain.enums import (
    JobType, JobStatus, JobPriority, JobSource
)
from ..converters import EnumConverter, SupabaseConverter

# Use centralized enums directly as API schemas  
JobTypeSchema = JobType
JobStatusSchema = JobStatus
JobPrioritySchema = JobPriority
JobSourceSchema = JobSource


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


class JobContactSchema(BaseModel):
    """Lightweight contact schema for job responses."""
    id: uuid.UUID
    display_name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    primary_contact_method: str
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "display_name": "John Doe (Acme Corp)",
                "company_name": "Acme Corp",
                "email": "john@acme.com",
                "phone": "+1-555-0123",
                "mobile_phone": "+1-555-0124",
                "primary_contact_method": "john@acme.com"
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
    job_type: JobTypeSchema
    priority: JobPrioritySchema = JobPrioritySchema.MEDIUM
    source: JobSourceSchema = JobSourceSchema.OTHER
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
    job_type: Optional[JobTypeSchema] = None
    priority: Optional[JobPrioritySchema] = None
    source: Optional[JobSourceSchema] = None
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
    status: JobStatusSchema
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
    status: Optional[JobStatusSchema] = None
    assigned_to: Optional[str] = None
    tags_to_add: Optional[List[str]] = Field(default=None, max_length=10)
    tags_to_remove: Optional[List[str]] = Field(default=None, max_length=10)
    priority: Optional[JobPrioritySchema] = None

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
    job_type: Optional[JobTypeSchema] = None
    status: Optional[JobStatusSchema] = None
    priority: Optional[JobPrioritySchema] = None
    source: Optional[JobSourceSchema] = None
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
    """Schema for job response with robust validation."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Job ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    contact_id: Optional[uuid.UUID] = Field(None, description="Contact ID")
    contact: Optional[JobContactSchema] = Field(None, description="Contact details")
    job_number: str = Field(..., description="Job number")
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    job_type: JobTypeSchema = Field(..., description="Job type")
    status: JobStatusSchema = Field(..., description="Job status")
    priority: JobPrioritySchema = Field(..., description="Job priority")
    source: JobSourceSchema = Field(..., description="Job source")
    job_address: JobAddressSchema = Field(..., description="Job address")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end time")
    actual_start: Optional[datetime] = Field(None, description="Actual start time")
    actual_end: Optional[datetime] = Field(None, description="Actual end time")
    assigned_to: List[str] = Field(default_factory=list, description="Assigned user IDs")
    created_by: str = Field(..., description="Creator user ID")
    time_tracking: JobTimeTrackingSchema = Field(..., description="Time tracking details")
    cost_estimate: JobCostEstimateSchema = Field(..., description="Cost estimate details")
    tags: List[str] = Field(default_factory=list, description="Job tags")
    notes: Optional[str] = Field(None, description="Job notes")
    internal_notes: Optional[str] = Field(None, description="Internal notes")
    customer_requirements: Optional[str] = Field(None, description="Customer requirements")
    completion_notes: Optional[str] = Field(None, description="Completion notes")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    last_modified: Optional[datetime] = Field(None, description="Last modification date")
    completed_date: Optional[datetime] = Field(None, description="Completion date")
    
    # Computed fields
    is_overdue: bool = Field(..., description="Whether job is overdue")
    is_emergency: bool = Field(..., description="Whether job is emergency")
    duration_days: Optional[int] = Field(None, description="Duration in days")
    estimated_revenue: Decimal = Field(..., description="Estimated revenue")
    profit_margin: Decimal = Field(..., description="Profit margin")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    type_display: str = Field(..., description="Human-readable type")

    @field_validator('job_type', mode='before')
    @classmethod
    def validate_job_type(cls, v):
        return EnumConverter.safe_job_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_job_status(v)

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_job_priority(v)

    @field_validator('source', mode='before')
    @classmethod
    def validate_source(cls, v):
        return EnumConverter.safe_job_source(v)

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        return SupabaseConverter.parse_list_field(v, default=[])

    @field_validator('assigned_to', mode='before')
    @classmethod
    def validate_assigned_to(cls, v):
        return SupabaseConverter.parse_list_field(v, default=[])

    @field_validator('custom_fields', mode='before')
    @classmethod
    def validate_custom_fields(cls, v):
        return SupabaseConverter.parse_dict_field(v, default={})

    @field_validator('created_date', 'last_modified', 'completed_date', 'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.parse_datetime(v)

    @field_validator('id', 'business_id', 'contact_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.parse_uuid(v)

    @classmethod
    def from_supabase_dict(cls, data: Dict[str, Any]) -> "JobResponse":
        """Create JobResponse from Supabase dictionary with proper validation."""
        # Compute display fields
        data['type_display'] = cls._compute_type_display(data)
        data['status_display'] = cls._compute_status_display(data)
        data['priority_display'] = cls._compute_priority_display(data)
        
        return cls.model_validate(data)

    @staticmethod
    def _compute_type_display(data: Dict[str, Any]) -> str:
        """Compute human-readable type display."""
        job_type = EnumConverter.safe_job_type(data.get('job_type'))
        return job_type.get_display()

    @staticmethod
    def _compute_status_display(data: Dict[str, Any]) -> str:
        """Compute human-readable status display."""
        status = EnumConverter.safe_job_status(data.get('status'))
        return status.get_display()

    @staticmethod
    def _compute_priority_display(data: Dict[str, Any]) -> str:
        """Compute human-readable priority display."""
        priority = EnumConverter.safe_job_priority(data.get('priority'))
        return priority.get_display()

    @field_serializer('created_date', 'last_modified', 'completed_date', 'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class JobListResponse(BaseModel):
    """Schema for job list response with robust validation."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Job ID")
    contact_id: Optional[uuid.UUID] = Field(None, description="Contact ID")
    contact: Optional[JobContactSchema] = Field(None, description="Contact details")
    job_number: str = Field(..., description="Job number")
    title: str = Field(..., description="Job title")
    job_type: JobTypeSchema = Field(..., description="Job type")
    status: JobStatusSchema = Field(..., description="Job status")
    priority: JobPrioritySchema = Field(..., description="Job priority")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end time")
    assigned_to: List[str] = Field(default_factory=list, description="Assigned user IDs")
    estimated_revenue: Decimal = Field(..., description="Estimated revenue")
    is_overdue: bool = Field(..., description="Whether job is overdue")
    is_emergency: bool = Field(..., description="Whether job is emergency")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    last_modified: Optional[datetime] = Field(None, description="Last modification date")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    type_display: str = Field(..., description="Human-readable type")

    @field_validator('job_type', mode='before')
    @classmethod
    def validate_job_type(cls, v):
        return EnumConverter.safe_job_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_job_status(v)

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_job_priority(v)

    @field_validator('assigned_to', mode='before')
    @classmethod
    def validate_assigned_to(cls, v):
        return SupabaseConverter.parse_list_field(v, default=[])

    @field_validator('created_date', 'last_modified', 'scheduled_start', 'scheduled_end', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.parse_datetime(v)

    @field_validator('id', 'contact_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.parse_uuid(v)

    @field_serializer('created_date', 'last_modified', 'scheduled_start', 'scheduled_end')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


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