"""
Job Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status options"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class JobPriority(str, Enum):
    """Job priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecentJob(BaseModel):
    """Recent job information"""
    id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title/summary")
    contact_id: str = Field(..., description="Associated contact ID")
    contact_name: str = Field(..., description="Contact's name")
    status: JobStatus = Field(..., description="Current job status")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date and time")
    estimated_duration: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")
    priority: JobPriority = Field(default=JobPriority.MEDIUM, description="Job priority level")
    description: Optional[str] = Field(None, description="Detailed job description")
    location: Optional[str] = Field(None, description="Job location/address")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "job_123",
                "title": "Kitchen Sink Repair",
                "contact_id": "contact_456",
                "contact_name": "Jane Doe",
                "status": "scheduled",
                "scheduled_date": "2024-01-20T10:00:00Z",
                "estimated_duration": 120,
                "priority": "high",
                "description": "Replace kitchen sink faucet and check for leaks",
                "location": "123 Main St, Anytown, USA"
            }
        } 