"""
Authentication Service Port

Interface for external authentication service operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
from pydantic import BaseModel, Field


class AuthProvider(Enum):
    """Authentication provider types."""
    SUPABASE = "supabase"
    FIREBASE = "firebase"
    AUTH0 = "auth0"
    LOCAL = "local"


class AuthUser(BaseModel):
    """External authentication user data."""
    id: str  # Provider-specific user ID
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    provider: AuthProvider = AuthProvider.SUPABASE
    is_email_verified: bool = False
    is_phone_verified: bool = False
    provider_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    last_sign_in: Optional[str] = None


class AuthToken(BaseModel):
    """Authentication token information."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[str] = None
    scope: Optional[str] = None


class AuthResult(BaseModel):
    """Authentication operation result."""
    success: bool
    user: Optional[AuthUser] = None
    token: Optional[AuthToken] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    requires_verification: bool = False


class AuthServicePort(ABC):
    """
    Authentication service port interface.
    
    This interface defines the contract for external authentication
    services like Supabase, Firebase, Auth0, etc.
    """
    
    @abstractmethod
    async def authenticate_with_email(self, email: str, password: str) -> AuthResult:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            AuthResult with authentication status and user data
        """
        pass
    
    @abstractmethod
    async def authenticate_with_phone(self, phone: str, password: str) -> AuthResult:
        """
        Authenticate user with phone and password.
        
        Args:
            phone: User phone number
            password: User password
            
        Returns:
            AuthResult with authentication status and user data
        """
        pass
    
    @abstractmethod
    async def register_user(self, email: Optional[str] = None, phone: Optional[str] = None,
                           password: Optional[str] = None, full_name: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> AuthResult:
        """
        Register a new user with the authentication service.
        
        Args:
            email: User email address
            phone: User phone number
            password: User password
            full_name: User full name
            metadata: Additional user metadata
            
        Returns:
            AuthResult with registration status and user data
        """
        pass
    
    @abstractmethod
    async def verify_token(self, token: str) -> AuthResult:
        """
        Verify an authentication token.
        
        Args:
            token: Authentication token to verify
            
        Returns:
            AuthResult with verification status and user data
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """
        Refresh an authentication token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            AuthResult with new token information
        """
        pass
    
    @abstractmethod
    async def logout_user(self, access_token: str) -> bool:
        """
        Logout user and invalidate tokens.
        
        Args:
            access_token: User's access token
            
        Returns:
            True if logout was successful
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        """
        Get user information by provider ID.
        
        Args:
            user_id: Provider-specific user ID
            
        Returns:
            AuthUser if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> AuthResult:
        """
        Update user information in the authentication service.
        
        Args:
            user_id: Provider-specific user ID
            updates: Dictionary of fields to update
            
        Returns:
            AuthResult with update status and user data
        """
        pass
    
    @abstractmethod
    async def change_password(self, user_id: str, current_password: str,
                             new_password: str) -> AuthResult:
        """
        Change user password.
        
        Args:
            user_id: Provider-specific user ID
            current_password: Current password
            new_password: New password
            
        Returns:
            AuthResult with operation status
        """
        pass
    
    @abstractmethod
    async def reset_password(self, email: str) -> bool:
        """
        Initiate password reset for user.
        
        Args:
            email: User email address
            
        Returns:
            True if reset was initiated
        """
        pass
    
    @abstractmethod
    async def confirm_password_reset(self, token: str, new_password: str) -> AuthResult:
        """
        Confirm password reset with token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            AuthResult with operation status
        """
        pass
    
    @abstractmethod
    async def send_email_verification(self, user_id: str) -> bool:
        """
        Send email verification to user.
        
        Args:
            user_id: Provider-specific user ID
            
        Returns:
            True if verification email was sent
        """
        pass
    
    @abstractmethod
    async def verify_email(self, token: str) -> AuthResult:
        """
        Verify user email with token.
        
        Args:
            token: Email verification token
            
        Returns:
            AuthResult with verification status
        """
        pass
    
    @abstractmethod
    async def send_phone_verification(self, user_id: str) -> bool:
        """
        Send phone verification to user.
        
        Args:
            user_id: Provider-specific user ID
            
        Returns:
            True if verification SMS was sent
        """
        pass
    
    @abstractmethod
    async def verify_phone(self, user_id: str, code: str) -> AuthResult:
        """
        Verify user phone with code.
        
        Args:
            user_id: Provider-specific user ID
            code: Verification code
            
        Returns:
            AuthResult with verification status
        """
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user from authentication service.
        
        Args:
            user_id: Provider-specific user ID
            
        Returns:
            True if user was deleted
        """
        pass
    
    @abstractmethod
    async def list_users(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        List users in the authentication service.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with users list and pagination info
        """
        pass
    
    @abstractmethod
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get authentication service health status.
        
        Returns:
            Dictionary with service health information
        """
        pass
    
    @abstractmethod
    async def revoke_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a specific user."""
        pass 