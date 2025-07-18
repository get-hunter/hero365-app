"""
Estimate Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class EstimateStatus(str, Enum):
    """Estimate status options"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RecentEstimate(BaseModel):
    """Recent estimate information"""
    id: str = Field(..., description="Unique estimate identifier")
    title: str = Field(..., description="Estimate title/summary")
    contact_id: str = Field(..., description="Associated contact ID")
    contact_name: str = Field(..., description="Contact's name")
    status: EstimateStatus = Field(..., description="Current estimate status")
    total_amount: Optional[float] = Field(None, ge=0, description="Total estimate amount")
    created_date: datetime = Field(..., description="Estimate creation date")
    valid_until: Optional[datetime] = Field(None, description="Estimate expiration date")
    line_items_count: int = Field(default=0, ge=0, description="Number of line items")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "est_123",
                "title": "Kitchen Renovation Estimate",
                "contact_id": "contact_456",
                "contact_name": "Jane Doe",
                "status": "sent",
                "total_amount": 2500.00,
                "created_date": "2024-01-15T09:00:00Z",
                "valid_until": "2024-02-15T09:00:00Z",
                "line_items_count": 8
            }
        } 