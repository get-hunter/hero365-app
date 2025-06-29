"""
Authentication API Schemas

Request and response schemas for authentication endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer

from ...utils import format_datetime_utc


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    password: str = Field(..., min_length=8, description="User password")
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="User phone number")
    
    def model_validate(cls, values):
        """Validate that either email or phone is provided."""
        if not values.get('email') and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        return values


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    password: str = Field(..., min_length=8, description="User password")
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="User phone number")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    confirm_password: Optional[str] = Field(None, min_length=8, description="Password confirmation")
    
    def model_validate(cls, values):
        """Validate registration data."""
        if not values.get('email') and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if confirm_password and password != confirm_password:
            raise ValueError('Passwords do not match')
        
        return values


class AuthTokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class AuthUserResponse(BaseModel):
    """Schema for authenticated user information."""
    
    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: format_datetime_utc})
    
    id: uuid.UUID
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    supabase_id: Optional[str] = None
    last_login: Optional[datetime] = None
    
    @field_serializer('last_login')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Schema for logout request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    access_token: str = Field(..., description="Access token to invalidate")
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="User phone number")
    
    def model_validate(cls, values):
        """Validate that either email or phone is provided."""
        if not values.get('email') and not values.get('phone'):
            raise ValueError('Either email or phone must be provided')
        return values


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: Optional[str] = Field(None, min_length=8, description="Password confirmation")
    
    def model_validate(cls, values):
        """Validate password reset data."""
        new_password = values.get('new_password')
        confirm_password = values.get('confirm_password')
        if confirm_password and new_password != confirm_password:
            raise ValueError('Passwords do not match')
        return values


class VerifyTokenRequest(BaseModel):
    """Schema for token verification request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    token: str = Field(..., description="Token to verify")
    token_type: str = Field("access", description="Token type: 'access', 'refresh', 'reset'")


class AuthContextResponse(BaseModel):
    """Schema for authentication context response."""
    
    user_id: uuid.UUID
    user_email: Optional[str]
    user_phone: Optional[str]
    is_superuser: bool
    permissions: list[str]
    session_id: Optional[str] = None
    token_claims: Optional[Dict[str, Any]] = None


class SocialAuthRequest(BaseModel):
    """Schema for social authentication request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    provider: str = Field(..., description="OAuth provider: 'google', 'facebook', 'github', etc.")
    provider_id: str = Field(..., description="Provider user ID")
    email: Optional[EmailStr] = Field(None, description="User email from provider")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name from provider")
    avatar_url: Optional[str] = Field(None, description="Avatar URL from provider")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Additional provider data")


class SupabaseAuthResponse(BaseModel):
    """Schema for Supabase authentication response."""
    
    supabase_user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_metadata: Optional[Dict[str, Any]] = None
    app_metadata: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class AuthSessionResponse(BaseModel):
    """Schema for authentication session response."""
    
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    session_id: str
    user_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    @field_serializer('created_at', 'expires_at', 'last_activity')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


# Legacy Auth Models (moved from models.py)
class Token(BaseModel):
    """JWT token response (legacy compatibility)."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload (legacy compatibility)."""
    sub: Optional[str] = None


class NewPassword(BaseModel):
    """New password for reset (legacy compatibility)."""
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Native Mobile OAuth Schemas
class AppleSignInRequest(BaseModel):
    """Schema for Apple Sign-In with ID token from iOS app."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    id_token: str = Field(..., description="ID token from Apple Sign-In")
    user_identifier: str = Field(..., description="User identifier from Apple")
    email: Optional[EmailStr] = Field(None, description="Email from Apple (if provided)")
    full_name: Optional[str] = Field(None, description="Full name from Apple (if provided)")


class GoogleSignInRequest(BaseModel):
    """Schema for Google Sign-In with ID token from iOS app."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    id_token: str = Field(..., description="ID token from Google Sign-In")
    access_token: Optional[str] = Field(None, description="Access token from Google")
    email: Optional[EmailStr] = Field(None, description="Email from Google")
    full_name: Optional[str] = Field(None, description="Full name from Google")
    given_name: Optional[str] = Field(None, description="Given name from Google")
    family_name: Optional[str] = Field(None, description="Family name from Google")
    picture_url: Optional[str] = Field(None, description="Profile picture URL from Google")


class OAuthSignInResponse(BaseModel):
    """Schema for OAuth sign-in response."""
    
    access_token: str = Field(..., description="Supabase access token")
    refresh_token: str = Field(..., description="Supabase refresh token") 
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(default="bearer", description="Token type")
    user: AuthUserResponse = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user") 