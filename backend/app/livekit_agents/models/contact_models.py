"""
Contact Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class ContextPriority(str, Enum):
    """Priority levels for context items"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecentContact(BaseModel):
    """Recent contact information"""
    id: str = Field(..., description="Unique contact identifier")
    name: str = Field(..., description="Contact's full name")
    phone: Optional[str] = Field(None, description="Contact's phone number")
    email: Optional[EmailStr] = Field(None, description="Contact's email address")
    contact_type: str = Field(..., description="Type of contact (lead, customer, vendor)")
    last_interaction: datetime = Field(..., description="Last interaction timestamp")
    recent_jobs: List[str] = Field(default_factory=list, description="List of recent job IDs")
    recent_estimates: List[str] = Field(default_factory=list, description="List of recent estimate IDs")
    priority: ContextPriority = Field(default=ContextPriority.MEDIUM, description="Contact priority level")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "contact_123",
                "name": "Jane Doe",
                "phone": "555-0123",
                "email": "jane@example.com",
                "contact_type": "customer",
                "last_interaction": "2024-01-15T14:30:00Z",
                "recent_jobs": ["job_456", "job_789"],
                "recent_estimates": ["est_123"],
                "priority": "high"
            }
        } 