"""
Authentication Data Transfer Objects

DTOs for transferring authentication and authorization data.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class LoginDTO:
    """DTO for user login."""
    
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class RegisterDTO:
    """DTO for user registration."""
    
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    confirm_password: Optional[str] = None


@dataclass
class AuthTokenDTO:
    """DTO for authentication tokens."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


@dataclass
class AuthUserDTO:
    """DTO for authenticated user information."""
    
    id: str
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
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


@dataclass
class RefreshTokenDTO:
    """DTO for token refresh operations."""
    
    refresh_token: str


@dataclass
class LogoutDTO:
    """DTO for user logout."""
    
    access_token: str
    refresh_token: Optional[str] = None


@dataclass
class ForgotPasswordDTO:
    """DTO for forgot password requests."""
    
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class ResetPasswordTokenDTO:
    """DTO for password reset token operations."""
    
    token: str
    new_password: str
    confirm_password: Optional[str] = None


@dataclass
class VerifyTokenDTO:
    """DTO for token verification."""
    
    token: str
    token_type: str = "access"  # 'access', 'refresh', 'reset'


@dataclass
class AuthContextDTO:
    """DTO for authentication context in requests."""
    
    user_id: uuid.UUID
    user_email: Optional[str]
    user_phone: Optional[str]
    is_superuser: bool
    permissions: list[str]
    session_id: Optional[str] = None
    token_claims: Optional[Dict[str, Any]] = None


@dataclass
class SocialAuthDTO:
    """DTO for social authentication (OAuth)."""
    
    provider: str  # 'google', 'facebook', 'github', etc.
    provider_id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None


@dataclass
class SupabaseAuthDTO:
    """DTO for Supabase authentication data."""
    
    supabase_user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_metadata: Optional[Dict[str, Any]] = None
    app_metadata: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


@dataclass
class AuthSessionDTO:
    """DTO for authentication session information."""
    
    session_id: str
    user_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True 