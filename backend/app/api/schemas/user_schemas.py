"""
User API Schemas

Request and response schemas for user endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="User phone number")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="User password")
    is_superuser: bool = Field(False, description="Whether user is a superuser")
    
    def model_validate(cls, values):
        """Validate that either email or phone is provided."""
        if not values.get('email') and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        return values


class UserUpdateRequest(BaseModel):
    """Schema for updating user information."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="User phone number")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    is_superuser: Optional[bool] = Field(None, description="Whether user is a superuser")


class UserResponse(BaseModel):
    """Schema for user response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    supabase_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    onboarding_completed: Optional[bool] = None
    onboarding_completed_at: Optional[datetime] = None
    completed_steps: Optional[List[str]] = None


class UserSummaryResponse(BaseModel):
    """Schema for user summary response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class UserSearchRequest(BaseModel):
    """Schema for user search request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    email: Optional[str] = Field(None, max_length=255, description="Email filter")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="Phone filter")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name filter")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_superuser: Optional[bool] = Field(None, description="Filter by superuser status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    skip: int = Field(0, ge=0, description="Number of users to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of users to return")


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Password confirmation")
    
    def model_validate(cls, values):
        """Validate password change data."""
        new_password = values.get('new_password')
        confirm_password = values.get('confirm_password')
        if new_password != confirm_password:
            raise ValueError('New passwords do not match')
        
        current_password = values.get('current_password')
        if current_password == new_password:
            raise ValueError('New password must be different from current password')
        
        return values


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""
    
    total_users: int
    active_users: int
    inactive_users: int
    superusers: int
    recent_users_count: int  # Users created in last 7 days
    email_users: int
    phone_users: int


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    item_count: int = 0
    

class BulkUserOperationRequest(BaseModel):
    """Schema for bulk operations on users."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    user_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=100, description="List of user IDs")
    operation: str = Field(..., description="Operation to perform: 'activate', 'deactivate', 'delete'")
    operation_data: Optional[dict] = Field(None, description="Additional data for the operation")


class BulkUserOperationResponse(BaseModel):
    """Schema for bulk operation response."""
    
    success: bool
    message: str
    processed_count: int
    failed_count: int
    failed_users: Optional[List[uuid.UUID]] = None


class OnboardingCompletedRequest(BaseModel):
    """Schema for marking onboarding as completed."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    completed_steps: Optional[List[str]] = Field(None, description="List of completed onboarding steps")
    completion_date: Optional[datetime] = Field(None, description="Date when onboarding was completed")


class OnboardingCompletedResponse(BaseModel):
    """Schema for onboarding completion response."""
    
    success: bool
    message: str
    onboarding_completed: bool
    completed_at: Optional[datetime] = None 