"""
Business Context Models for Hero365 LiveKit Agents
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BusinessContext(BaseModel):
    """Complete business context for the voice agent"""
    business_id: str = Field(..., description="Unique business identifier")
    business_name: str = Field(..., description="Business name")
    business_type: str = Field(..., description="Type of business")
    owner_name: str = Field(..., description="Business owner name")
    phone: Optional[str] = Field(None, description="Business phone number")
    email: Optional[str] = Field(None, description="Business email address")
    address: Optional[str] = Field(None, description="Business address")
    current_time: datetime = Field(default_factory=datetime.now, description="Current timestamp")
    timezone: str = Field(default="UTC", description="Business timezone")
    
    # Context counts and metrics
    recent_contacts_count: int = Field(default=0, description="Number of recent contacts")
    recent_jobs_count: int = Field(default=0, description="Number of recent jobs")
    recent_estimates_count: int = Field(default=0, description="Number of recent estimates")
    active_jobs: int = Field(default=0, description="Number of active jobs")
    pending_estimates: int = Field(default=0, description="Number of pending estimates")
    last_refresh: Optional[datetime] = Field(default_factory=datetime.now, description="Last context refresh time")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        schema_extra = {
            "example": {
                "business_id": "bus_123",
                "business_name": "Smith Plumbing",
                "business_type": "Plumbing",
                "owner_name": "John Smith",
                "phone": "555-1234",
                "email": "john@smithplumbing.com",
                "address": "123 Main St, Anytown, USA",
                "timezone": "America/New_York",
                "active_jobs": 5,
                "pending_estimates": 3
            }
        }


class BusinessSummary(BaseModel):
    """Business summary for quick context"""
    total_contacts: int = Field(..., ge=0, description="Total number of contacts")
    active_jobs: int = Field(..., ge=0, description="Number of active jobs")
    pending_estimates: int = Field(..., ge=0, description="Number of pending estimates")
    overdue_invoices: int = Field(..., ge=0, description="Number of overdue invoices")
    revenue_this_month: float = Field(..., ge=0, description="Revenue for current month")
    jobs_this_week: int = Field(..., ge=0, description="Number of jobs this week")
    upcoming_appointments: int = Field(..., ge=0, description="Number of upcoming appointments")
    
    class Config:
        schema_extra = {
            "example": {
                "total_contacts": 150,
                "active_jobs": 8,
                "pending_estimates": 5,
                "overdue_invoices": 2,
                "revenue_this_month": 25000.50,
                "jobs_this_week": 12,
                "upcoming_appointments": 6
            }
        } 