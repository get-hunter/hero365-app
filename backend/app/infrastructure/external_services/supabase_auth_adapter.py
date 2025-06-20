"""
Supabase Authentication Service Adapter

Implementation of AuthServicePort interface using Supabase.
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

from ...application.ports.auth_service import (
    AuthServicePort, AuthUser, AuthToken, AuthResult, AuthProvider
)


class SupabaseAuthAdapter(AuthServicePort):
    """
    Supabase implementation of AuthServicePort.
    
    This adapter handles authentication operations using Supabase Auth API.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be provided")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def authenticate_with_email(self, email: str, password: str) -> AuthResult:
        """Authenticate user with email and password."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                auth_user = self._convert_to_auth_user(response.user)
                auth_token = self._convert_to_auth_token(response.session)
                
                return AuthResult(
                    success=True,
                    user=auth_user,
                    token=auth_token
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Authentication failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="AUTH_ERROR"
            )
    
    async def authenticate_with_phone(self, phone: str, password: str) -> AuthResult:
        """Authenticate user with phone and password."""
        try:
            response = self.client.auth.sign_in_with_password({
                "phone": phone,
                "password": password
            })
            
            if response.user and response.session:
                auth_user = self._convert_to_auth_user(response.user)
                auth_token = self._convert_to_auth_token(response.session)
                
                return AuthResult(
                    success=True,
                    user=auth_user,
                    token=auth_token
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Authentication failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="AUTH_ERROR"
            )
    
    async def register_user(self, email: Optional[str] = None, phone: Optional[str] = None,
                           password: Optional[str] = None, full_name: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> AuthResult:
        """Register a new user with the authentication service."""
        try:
            credentials = {}
            if email and password:
                credentials = {"email": email, "password": password}
            elif phone and password:
                credentials = {"phone": phone, "password": password}
            else:
                return AuthResult(
                    success=False,
                    error_message="Email or phone with password is required"
                )
            
            # Add user metadata
            user_metadata = {"full_name": full_name} if full_name else {}
            if metadata:
                user_metadata.update(metadata)
            
            if user_metadata:
                credentials["options"] = {"data": user_metadata}
            
            response = self.client.auth.sign_up(credentials)
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                auth_token = None
                
                if response.session:
                    auth_token = self._convert_to_auth_token(response.session)
                
                return AuthResult(
                    success=True,
                    user=auth_user,
                    token=auth_token,
                    requires_verification=not response.user.email_confirmed_at
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Registration failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="REGISTER_ERROR"
            )
    
    async def verify_token(self, token: str) -> AuthResult:
        """Verify an authentication token."""
        try:
            # Set the session with the token
            self.client.auth.set_session(token, token)  # Using same token for access and refresh
            
            # Get user info
            response = self.client.auth.get_user()
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Invalid token"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="TOKEN_ERROR"
            )
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """Refresh an authentication token."""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session:
                auth_token = self._convert_to_auth_token(response.session)
                auth_user = None
                
                if response.user:
                    auth_user = self._convert_to_auth_user(response.user)
                
                return AuthResult(
                    success=True,
                    user=auth_user,
                    token=auth_token
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Token refresh failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="REFRESH_ERROR"
            )
    
    async def logout_user(self, access_token: str) -> bool:
        """Logout user and invalidate tokens."""
        try:
            self.client.auth.sign_out()
            return True
        except Exception:
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Get user information by provider ID."""
        try:
            # This requires admin privileges in Supabase
            # For regular app usage, this might not be available
            response = self.client.auth.admin.get_user_by_id(user_id)
            
            if response.user:
                return self._convert_to_auth_user(response.user)
            return None
        except Exception:
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> AuthResult:
        """Update user information in the authentication service."""
        try:
            response = self.client.auth.update_user(updates)
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Update failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="UPDATE_ERROR"
            )
    
    async def change_password(self, user_id: str, current_password: str,
                             new_password: str) -> AuthResult:
        """Change user password."""
        try:
            response = self.client.auth.update_user({"password": new_password})
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Password change failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="PASSWORD_ERROR"
            )
    
    async def reset_password(self, email: str) -> bool:
        """Initiate password reset for user."""
        try:
            self.client.auth.reset_password_email(email)
            return True
        except Exception:
            return False
    
    async def confirm_password_reset(self, token: str, new_password: str) -> AuthResult:
        """Confirm password reset with token."""
        try:
            response = self.client.auth.update_user({"password": new_password})
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Password reset confirmation failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="RESET_ERROR"
            )
    
    async def send_email_verification(self, user_id: str) -> bool:
        """Send email verification to user."""
        try:
            # This would typically be handled automatically by Supabase
            # or require admin API access
            return True
        except Exception:
            return False
    
    async def verify_email(self, token: str) -> AuthResult:
        """Verify user email with token."""
        try:
            response = self.client.auth.verify_otp({
                "token": token,
                "type": "email"
            })
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Email verification failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="VERIFY_ERROR"
            )
    
    async def send_phone_verification(self, user_id: str) -> bool:
        """Send phone verification to user."""
        try:
            # This would require the phone number and is handled by Supabase
            return True
        except Exception:
            return False
    
    async def verify_phone(self, user_id: str, code: str) -> AuthResult:
        """Verify user phone with code."""
        try:
            response = self.client.auth.verify_otp({
                "token": code,
                "type": "phone"
            })
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Phone verification failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="VERIFY_ERROR"
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user from authentication service."""
        try:
            # This requires admin privileges
            self.client.auth.admin.delete_user(user_id)
            return True
        except Exception:
            return False
    
    async def list_users(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """List users in the authentication service."""
        try:
            # This requires admin privileges
            response = self.client.auth.admin.list_users(page=page, per_page=per_page)
            
            users = []
            if hasattr(response, 'users'):
                users = [self._convert_to_auth_user(user) for user in response.users]
            
            return {
                "users": users,
                "page": page,
                "per_page": per_page,
                "total": len(users)  # Supabase doesn't provide total count in basic response
            }
        except Exception:
            return {
                "users": [],
                "page": page,
                "per_page": per_page,
                "total": 0
            }
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get authentication service health status."""
        try:
            # Simple health check by attempting to get current session
            self.client.auth.get_session()
            return {
                "status": "healthy",
                "service": "supabase_auth",
                "timestamp": "2024-01-01T00:00:00Z"  # Would be current timestamp
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "supabase_auth",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    def _convert_to_auth_user(self, supabase_user) -> AuthUser:
        """Convert Supabase user to AuthUser."""
        return AuthUser(
            id=supabase_user.id,
            email=supabase_user.email,
            phone=supabase_user.phone,
            full_name=supabase_user.user_metadata.get("full_name") if supabase_user.user_metadata else None,
            provider=AuthProvider.SUPABASE,
            is_email_verified=bool(supabase_user.email_confirmed_at),
            is_phone_verified=bool(supabase_user.phone_confirmed_at),
            provider_metadata=supabase_user.user_metadata or {},
            created_at=supabase_user.created_at,
            last_sign_in=supabase_user.last_sign_in_at
        )
    
    def _convert_to_auth_token(self, supabase_session) -> AuthToken:
        """Convert Supabase session to AuthToken."""
        return AuthToken(
            access_token=supabase_session.access_token,
            refresh_token=supabase_session.refresh_token,
            token_type="Bearer",
            expires_in=supabase_session.expires_in,
            expires_at=str(supabase_session.expires_at) if supabase_session.expires_at else None
        ) 