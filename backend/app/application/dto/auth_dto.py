"""
Authentication Data Transfer Objects

DTOs for transferring authentication and authorization data.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LoginDTO(BaseModel):
    """DTO for user login."""
    
    password: str = Field(min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None


class RegisterDTO(BaseModel):
    """DTO for user registration."""
    
    password: str = Field(min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    confirm_password: Optional[str] = None


class AuthTokenDTO(BaseModel):
    """DTO for authentication tokens."""
    
    access_token: str = Field(min_length=1)
    token_type: str = Field(default="bearer", min_length=1)
    expires_in: Optional[int] = Field(default=None, gt=0)
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class AuthUserDTO(BaseModel):
    """DTO for authenticated user information."""
    
    id: str = Field(min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    supabase_id: Optional[str] = None
    last_login: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "supabase_id": self.supabase_id,
            "last_login": self.last_login,
            "metadata": self.metadata or {}
        }


class RefreshTokenDTO(BaseModel):
    """DTO for token refresh operations."""
    
    refresh_token: str = Field(min_length=1)


class LogoutDTO(BaseModel):
    """DTO for user logout."""
    
    access_token: str = Field(min_length=1)
    refresh_token: Optional[str] = None


class ForgotPasswordDTO(BaseModel):
    """DTO for forgot password requests."""
    
    email: Optional[str] = None
    phone: Optional[str] = None


class ResetPasswordTokenDTO(BaseModel):
    """DTO for password reset token operations."""
    
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=1)
    confirm_password: Optional[str] = None


class VerifyTokenDTO(BaseModel):
    """DTO for token verification."""
    
    token: str = Field(min_length=1)
    token_type: str = Field(default="access", min_length=1)  # 'access', 'refresh', 'reset'


class AuthContextDTO(BaseModel):
    """DTO for authentication context in requests."""
    
    user_id: uuid.UUID
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    is_superuser: bool
    permissions: list[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    token_claims: Optional[Dict[str, Any]] = None


class SocialAuthDTO(BaseModel):
    """DTO for social authentication (OAuth)."""
    
    provider: str = Field(min_length=1)  # 'google', 'facebook', 'github', etc.
    provider_id: str = Field(min_length=1)
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None


class SupabaseAuthDTO(BaseModel):
    """DTO for Supabase authentication data."""
    
    supabase_user_id: str = Field(min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    user_metadata: Optional[Dict[str, Any]] = None
    app_metadata: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class AuthSessionDTO(BaseModel):
    """DTO for authentication session information."""
    
    session_id: str = Field(min_length=1)
    user_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True 