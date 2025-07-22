"""
User Context Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class UserContext(BaseModel):
    """User-specific context for the voice agent"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    role: str = Field(..., description="User's role in the business")
    permissions: List[str] = Field(default_factory=list, description="User's permissions")
    last_active: datetime = Field(default_factory=datetime.now, description="Last active timestamp")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    recent_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent user actions")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "name": "John Smith",
                "email": "john@smithplumbing.com",
                "role": "owner",
                "permissions": ["create_jobs", "view_estimates", "manage_contacts"],
                "preferences": {
                    "timezone": "America/New_York",
                    "notifications": True,
                    "language": "en"
                },
                "recent_actions": [
                    {
                        "action": "created_job",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "details": {"job_id": "job_456"}
                    }
                ]
            }
        } 