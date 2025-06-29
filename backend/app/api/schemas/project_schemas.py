"""
Project API Schemas

Pydantic schemas for project management API endpoints.
Handles request/response validation and serialization.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from ...utils import format_datetime_utc
from ...domain.enums import ProjectType, ProjectStatus, ProjectPriority
from ..converters import EnumConverter, SupabaseConverter

# Use centralized enums directly as API schemas  
ProjectTypeSchema = ProjectType
ProjectStatusSchema = ProjectStatus
ProjectPrioritySchema = ProjectPriority


# Base schemas
class ProjectCreateRequest(BaseModel):
    """Schema for project creation request."""
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    description: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    client_id: uuid.UUID
    project_type: ProjectTypeSchema
    priority: ProjectPrioritySchema
    start_date: datetime
    end_date: Optional[datetime] = None
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    manager_id: Optional[uuid.UUID] = None
    team_members: Optional[List[str]] = Field(default=None, max_length=20)
    tags: Optional[List[str]] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    @field_validator('team_members')
    @classmethod
    def validate_team_members(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set(member.strip() for member in v if member.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Kitchen Renovation Project",
                "description": "Complete kitchen renovation including appliances, cabinets, and flooring",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "project_type": "renovation",
                "priority": "high",
                "start_date": "2024-02-01T09:00:00Z",
                "end_date": "2024-03-15T17:00:00Z",
                "estimated_budget": "25000.00",
                "manager_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_members": ["user1", "user2"],
                "tags": ["kitchen", "renovation", "residential"],
                "notes": "Client wants premium appliances and custom cabinets"
            }
        }
    }


class ProjectUpdateRequest(BaseModel):
    """Schema for project update request."""
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=200)]] = None
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=1000)]] = None
    project_type: Optional[ProjectTypeSchema] = None
    priority: Optional[ProjectPrioritySchema] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    actual_cost: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    manager_id: Optional[uuid.UUID] = None
    team_members: Optional[List[str]] = Field(default=None, max_length=20)
    tags: Optional[List[str]] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    @field_validator('team_members')
    @classmethod
    def validate_team_members(cls, v):
        if v:
            v = list(set(member.strip() for member in v if member.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Kitchen Renovation Project",
                "description": "Updated project description",
                "priority": "critical",
                "estimated_budget": "30000.00",
                "actual_cost": "28500.00",
                "notes": "Updated project notes"
            }
        }
    }


class ProjectStatusUpdateRequest(BaseModel):
    """Schema for project status update request."""
    status: ProjectStatusSchema
    notes: Optional[str] = Field(default=None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "active",
                "notes": "Project has been approved and work is starting"
            }
        }
    }


class ProjectFromTemplateRequest(BaseModel):
    """Schema for creating project from template request."""
    template_id: uuid.UUID
    client_id: uuid.UUID
    start_date: datetime
    custom_name: Optional[str] = Field(default=None, max_length=200)
    custom_description: Optional[str] = Field(default=None, max_length=1000)
    custom_budget: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    manager_id: Optional[uuid.UUID] = None
    team_members: Optional[List[str]] = Field(default=None, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "550e8400-e29b-41d4-a716-446655440010",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "start_date": "2024-02-01T09:00:00Z",
                "custom_name": "Johnson Home HVAC Installation",
                "custom_budget": "15000.00",
                "manager_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }
    }


class ProjectSearchRequest(BaseModel):
    """Schema for project search request."""
    search: Optional[str] = Field(default=None, max_length=100)
    status: Optional[ProjectStatusSchema] = None
    project_type: Optional[ProjectTypeSchema] = None
    priority: Optional[ProjectPrioritySchema] = None
    client_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    is_overdue: Optional[bool] = None
    is_over_budget: Optional[bool] = None
    min_budget: Optional[Decimal] = Field(default=None, ge=0)
    max_budget: Optional[Decimal] = Field(default=None, ge=0)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    sort_by: str = Field(default="created_date", pattern="^(name|start_date|end_date|priority|status|estimated_budget|created_date)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    model_config = {
        "json_schema_extra": {
            "example": {
                "search": "kitchen renovation",
                "status": "active",
                "project_type": "renovation",
                "priority": "high",
                "tags": ["kitchen", "residential"],
                "skip": 0,
                "limit": 50,
                "sort_by": "start_date",
                "sort_order": "asc"
            }
        }
    }


class ProjectResponse(BaseModel):
    """Schema for project response with robust validation."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Project ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    created_by: str = Field(..., description="Creator user ID")
    client_id: uuid.UUID = Field(..., description="Client ID")
    client_name: str = Field(..., description="Client name")
    client_address: str = Field(..., description="Client address")
    project_type: ProjectTypeSchema = Field(..., description="Project type")
    status: ProjectStatusSchema = Field(..., description="Project status")
    priority: ProjectPrioritySchema = Field(..., description="Project priority")
    start_date: datetime = Field(..., description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    estimated_budget: Decimal = Field(..., description="Estimated budget")
    actual_cost: Decimal = Field(..., description="Actual cost")
    manager: Optional[str] = Field(None, description="Manager name")
    manager_id: Optional[uuid.UUID] = Field(None, description="Manager user ID")
    team_members: List[str] = Field(default_factory=list, description="Team member IDs")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    notes: Optional[str] = Field(None, description="Project notes")
    created_date: datetime = Field(..., description="Creation date")
    last_modified: datetime = Field(..., description="Last modification date")
    
    # Computed fields
    is_overdue: bool = Field(..., description="Whether project is overdue")
    is_over_budget: bool = Field(..., description="Whether project is over budget")
    budget_variance: Decimal = Field(..., description="Budget variance (actual - estimated)")
    budget_variance_percentage: Optional[Decimal] = Field(None, description="Budget variance percentage")
    duration_days: Optional[int] = Field(None, description="Duration in days")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    type_display: str = Field(..., description="Human-readable type")

    @field_validator('project_type', mode='before')
    @classmethod
    def validate_project_type(cls, v):
        return EnumConverter.safe_project_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_project_status(v)

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_project_priority(v)

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        return SupabaseConverter.safe_list_field(v)

    @field_validator('team_members', mode='before')
    @classmethod
    def validate_team_members(cls, v):
        return SupabaseConverter.safe_list_field(v)

    @field_validator('created_date', 'last_modified', 'start_date', 'end_date', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_validator('id', 'business_id', 'client_id', 'manager_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_serializer('created_date', 'last_modified', 'start_date', 'end_date')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    client_name: str = Field(..., description="Client name")
    project_type: ProjectTypeSchema = Field(..., description="Project type")
    status: ProjectStatusSchema = Field(..., description="Project status")
    priority: ProjectPrioritySchema = Field(..., description="Project priority")
    start_date: datetime = Field(..., description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    estimated_budget: Decimal = Field(..., description="Estimated budget")
    actual_cost: Decimal = Field(..., description="Actual cost")
    manager: Optional[str] = Field(None, description="Manager name")
    is_overdue: bool = Field(..., description="Whether project is overdue")
    is_over_budget: bool = Field(..., description="Whether project is over budget")
    created_date: datetime = Field(..., description="Creation date")
    last_modified: datetime = Field(..., description="Last modification date")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    type_display: str = Field(..., description="Human-readable type")

    @field_validator('project_type', mode='before')
    @classmethod
    def validate_project_type(cls, v):
        return EnumConverter.safe_project_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_project_status(v)

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_project_priority(v)

    @field_validator('created_date', 'last_modified', 'start_date', 'end_date', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('created_date', 'last_modified', 'start_date', 'end_date')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class ProjectTemplateResponse(BaseModel):
    """Schema for project template response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Template ID")
    business_id: Optional[uuid.UUID] = Field(None, description="Business ID (None for system templates)")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    project_type: ProjectTypeSchema = Field(..., description="Project type")
    priority: ProjectPrioritySchema = Field(..., description="Default priority")
    estimated_budget: Decimal = Field(..., description="Default estimated budget")
    estimated_duration: Optional[int] = Field(None, description="Default duration in days")
    tags: List[str] = Field(default_factory=list, description="Default tags")
    is_system_template: bool = Field(..., description="Whether this is a system template")
    created_date: datetime = Field(..., description="Creation date")
    last_modified: datetime = Field(..., description="Last modification date")

    @field_validator('project_type', mode='before')
    @classmethod
    def validate_project_type(cls, v):
        return EnumConverter.safe_project_type(v)

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_project_priority(v)

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        return SupabaseConverter.safe_list_field(v)

    @field_serializer('created_date', 'last_modified')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class ProjectAssignmentRequest(BaseModel):
    """Schema for project team assignment request."""
    user_ids: List[str] = Field(..., min_length=1, max_length=20)
    replace_existing: bool = Field(default=False)

    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v):
        if v:
            # Remove duplicates and empty strings
            v = list(set(user_id.strip() for user_id in v if user_id.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_ids": ["user1", "user2", "user3"],
                "replace_existing": False
            }
        }
    }


class ProjectJobAssignmentRequest(BaseModel):
    """Schema for assigning jobs to a project."""
    job_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=50, description="List of job IDs to assign to the project")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_ids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            }
        }
    }


class ProjectTemplateCreateRequest(BaseModel):
    """Schema for project template creation request."""
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    description: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    project_type: ProjectTypeSchema
    priority: ProjectPrioritySchema
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    estimated_duration: Optional[int] = Field(default=None, gt=0)
    tags: Optional[List[str]] = Field(default=None, max_length=20)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Standard HVAC Installation",
                "description": "Template for standard residential HVAC installation projects",
                "project_type": "installation",
                "priority": "medium",
                "estimated_budget": "12000.00",
                "estimated_duration": 14,
                "tags": ["hvac", "residential", "installation"]
            }
        }
    }


class ProjectTemplateUpdateRequest(BaseModel):
    """Schema for project template update request."""
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=200)]] = None
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=1000)]] = None
    project_type: Optional[ProjectTypeSchema] = None
    priority: Optional[ProjectPrioritySchema] = None
    estimated_budget: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    estimated_duration: Optional[int] = Field(default=None, gt=0)
    tags: Optional[List[str]] = Field(default=None, max_length=20)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated HVAC Installation Template",
                "description": "Updated template description",
                "estimated_budget": "15000.00",
                "tags": ["hvac", "installation", "updated"]
            }
        }
    }


class ProjectCreateFromTemplateRequest(BaseModel):
    """Schema for creating project from template request."""
    project_number: Optional[str] = Field(default=None, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: ProjectStatusSchema
    priority: Optional[ProjectPrioritySchema] = None
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = Field(default=None, max_length=200)
    client_email: Optional[str] = Field(default=None, max_length=200)
    client_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)
    start_date: datetime
    end_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = Field(default=None, ge=0)
    budget_amount: Optional[Decimal] = Field(default=None, ge=0)
    team_members: Optional[List[str]] = Field(default=None, max_length=20)
    tags: Optional[List[str]] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date') and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            v = list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v

    @field_validator('team_members')
    @classmethod
    def validate_team_members(cls, v):
        if v:
            v = list(set(member.strip() for member in v if member.strip()))
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_number": "PROJ-2024-001",
                "name": "Johnson Home HVAC Installation",
                "description": "HVAC installation for Johnson residence",
                "status": "planning",
                "priority": "medium",
                "contact_id": "550e8400-e29b-41d4-a716-446655440000",
                "client_name": "John Johnson",
                "client_email": "john@johnson.com",
                "start_date": "2024-02-01T09:00:00Z",
                "budget_amount": "15000.00"
            }
        }
    }


class ProjectStatisticsResponse(BaseModel):
    """Schema for project statistics response."""
    total_projects: int = Field(..., ge=0)
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_type: Dict[str, int] = Field(default_factory=dict)
    budget_totals: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_projects": 25,
                "by_status": {
                    "planning": 3,
                    "active": 8,
                    "completed": 15,
                    "on_hold": 2,
                    "cancelled": 1
                },
                "by_priority": {
                    "low": 5,
                    "medium": 12,
                    "high": 6,
                    "critical": 2
                },
                "by_type": {
                    "maintenance": 5,
                    "installation": 12,
                    "renovation": 8
                },
                "budget_totals": {
                    "total_budget": "500000.00",
                    "total_actual": "465000.00",
                    "variance": "35000.00",
                    "project_count": 25
                }
            }
        }
    }


class ProjectBudgetSummaryResponse(BaseModel):
    """Schema for project budget summary response."""
    total_budget: Decimal = Field(..., ge=0, decimal_places=2)
    total_actual: Decimal = Field(..., ge=0, decimal_places=2)
    variance: Decimal = Field(..., decimal_places=2)
    project_count: int = Field(..., ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_budget": "500000.00",
                "total_actual": "465000.00", 
                "variance": "35000.00",
                "project_count": 25
            }
        }
    }


class ProjectProgressReportResponse(BaseModel):
    """Schema for project progress report response."""
    summary: Dict[str, Any] = Field(default_factory=dict)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    overdue_projects: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "summary": {
                    "total_active_projects": 8,
                    "total_overdue_projects": 2,
                    "overdue_percentage": 25.0
                },
                "projects": [
                    {
                        "project_id": "550e8400-e29b-41d4-a716-446655440000",
                        "project_name": "Kitchen Renovation",
                        "project_number": "PROJ-2024-001",
                        "progress": 75.5
                    }
                ],
                "overdue_projects": [
                    {
                        "project_id": "550e8400-e29b-41d4-a716-446655440001",
                        "project_name": "Bathroom Remodel",
                        "project_number": "PROJ-2024-002",
                        "end_date": "2024-01-15",
                        "days_overdue": 5
                    }
                ]
            }
        }
    }


class ProjectAnalyticsResponse(BaseModel):
    """Schema for project analytics response."""
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_projects": 156,
                "active_projects": 23,
                "completed_projects": 120,
                "projects_by_status": {
                    "planning": 8,
                    "active": 23,
                    "on_hold": 5,
                    "completed": 120,
                    "cancelled": 0
                },
                "projects_by_type": {
                    "maintenance": 45,
                    "installation": 32,
                    "renovation": 28
                },
                "budget_analytics": {
                    "total_estimated_budget": 1250000.00,
                    "total_actual_cost": 980000.00,
                    "average_project_budget": 8012.82,
                    "projects_over_budget": 12,
                    "budget_variance_percentage": -21.6
                },
                "timeline_analytics": {
                    "average_project_duration": 14,
                    "overdue_projects": 3,
                    "upcoming_deadlines": 7
                }
            }
        }
    }


class ProjectListPaginatedResponse(BaseModel):
    """Schema for paginated project list response."""
    projects: List[ProjectListResponse]
    pagination: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "example": {
                "projects": [],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 10,
                    "total_items": 95,
                    "items_per_page": 10
                }
            }
        }
    }


class ProjectJobAssignmentResponse(BaseModel):
    """Schema for project-job assignment response."""
    project_id: uuid.UUID
    job_ids: List[uuid.UUID]
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_ids": ["550e8400-e29b-41d4-a716-446655440001"],
                "message": "Job successfully assigned to project"
            }
        }
    }


class ProjectActionResponse(BaseModel):
    """Schema for project action responses."""
    success: bool = True
    message: str
    project_id: Optional[uuid.UUID] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Project created successfully",
                "project_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    }


class ProjectErrorResponse(BaseModel):
    """Schema for project error responses."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "PROJECT_NOT_FOUND",
                "message": "Project not found",
                "details": {"project_id": "550e8400-e29b-41d4-a716-446655440000"}
            }
        }
    } 