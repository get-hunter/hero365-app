"""
User Data Transfer Objects

DTOs for transferring user data between application layers.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateUserDTO:
    """DTO for creating a new user."""
    
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None  # For non-Supabase users
    is_superuser: bool = False
    supabase_id: Optional[str] = None


@dataclass
class UpdateUserDTO:
    """DTO for updating user information."""
    
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


@dataclass
class UserDTO:
    """DTO for user data transfer."""
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    supabase_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserProfileDTO:
    """DTO for user profile information (public data)."""
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool


@dataclass
class UserListDTO:
    """DTO for paginated user list."""
    
    users: list[UserDTO]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


@dataclass
class UserSearchDTO:
    """DTO for user search parameters."""
    
    query: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    skip: int = 0
    limit: int = 100


@dataclass
class ChangePasswordDTO:
    """DTO for password change operations."""
    
    user_id: uuid.UUID
    current_password: str
    new_password: str


@dataclass
class ResetPasswordDTO:
    """DTO for password reset operations."""
    
    token: str
    new_password: str
    user_id: Optional[uuid.UUID] = None 