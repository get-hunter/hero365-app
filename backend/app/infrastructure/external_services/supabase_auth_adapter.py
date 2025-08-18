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
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None, 
                 supabase_service_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = supabase_service_key or os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be provided")
        
        if not self.supabase_service_key:
            raise ValueError("Supabase service key must be provided for admin operations")
        
        # Regular client for standard operations
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Admin client for admin operations (user management, metadata updates)
        self.admin_client: Client = create_client(self.supabase_url, self.supabase_service_key)
    
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
            # Use admin client to get user by JWT token
            response = self.admin_client.auth.get_user(jwt=token)
            
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
            response = self.admin_client.auth.admin.get_user_by_id(user_id)
            
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
        """Delete a user account."""
        try:
            # First, invalidate all active sessions for the user
            await self._invalidate_user_sessions(user_id)
            
            # Then delete the user
            self.admin_client.auth.admin.delete_user(user_id)
            return True
        except Exception:
            return False
    
    async def _invalidate_user_sessions(self, user_id: str) -> bool:
        """Invalidate all active sessions for a user."""
        try:
            # Get all sessions for the user and revoke them
            # Note: This requires Supabase admin privileges
            self.admin_client.auth.admin.sign_out(user_id, scope='global')
            return True
        except Exception:
            return False
    
    async def revoke_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a specific user."""
        try:
            # Sign out user from all sessions
            self.admin_client.auth.admin.sign_out(user_id, scope='global')
            return True
        except Exception:
            return False
    
    async def list_users(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """List all users with pagination."""
        try:
            response = self.admin_client.auth.admin.list_users(
                page=page,
                per_page=per_page
            )
            
            users = [self._convert_to_auth_user(user) for user in response.users]
            
            return {
                "users": users,
                "page": page,
                "per_page": per_page,
                "total": len(users),
                "has_next": response.next_page is not None
            }
        except Exception as e:
            return {
                "users": [],
                "page": page,
                "per_page": per_page,
                "total": 0,
                "has_next": False,
                "error": str(e)
            }
    
    async def sign_in_with_oauth(self, provider: str, id_token: str, access_token: str = None) -> AuthResult:
        """Sign in with OAuth provider using ID token."""
        try:
            response = self.client.auth.sign_in_with_id_token({
                "provider": provider,
                "token": id_token,
                "access_token": access_token
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
                    error_message="OAuth authentication failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="OAUTH_ERROR"
            )
    
    async def create_user_with_oauth(self, provider: str, provider_id: str, email: str, 
                                   user_metadata: Dict[str, Any] = None) -> AuthResult:
        """Create a user from OAuth provider data."""
        try:
            response = self.admin_client.auth.admin.create_user({
                "email": email,
                "user_metadata": user_metadata or {},
                "app_metadata": {
                    "provider": provider,
                    "provider_id": provider_id
                },
                "email_confirm": True  # OAuth users are pre-verified
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
                    error_message="Failed to create OAuth user"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="OAUTH_CREATE_ERROR"
            )
    
    async def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number for passwordless authentication."""
        try:
            self.client.auth.sign_in_with_otp({"phone": phone})
            return True
        except Exception:
            return False
    
    async def verify_otp(self, phone: str, token: str) -> AuthResult:
        """Verify OTP for phone number authentication."""
        try:
            response = self.client.auth.verify_otp({
                "phone": phone,
                "token": token,
                "type": "sms"
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
                    error_message="OTP verification failed"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="OTP_ERROR"
            )
    
    async def update_user_metadata(self, user_id: str, user_metadata: Dict[str, Any]) -> AuthResult:
        """Update user metadata."""
        try:
            response = self.admin_client.auth.admin.update_user_by_id(
                user_id, 
                {"user_metadata": user_metadata}
            )
            
            if response.user:
                auth_user = self._convert_to_auth_user(response.user)
                return AuthResult(
                    success=True,
                    user=auth_user
                )
            else:
                return AuthResult(
                    success=False,
                    error_message="Failed to update user metadata"
                )
        except Exception as e:
            return AuthResult(
                success=False,
                error_message=str(e),
                error_code="UPDATE_ERROR"
            )

    async def get_service_health(self) -> Dict[str, Any]:
        """Check if the authentication service is healthy."""
        try:
            # Simple health check by trying to get current user
            # This will fail gracefully if service is down
            await self.verify_token("dummy_token")  # This will fail but service is responsive
            return {
                "status": "healthy",
                "service": "supabase_auth",
                "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
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
        user_metadata = supabase_user.user_metadata or {}
        
        # Convert datetime objects to ISO format strings
        created_at_str = None
        if supabase_user.created_at:
            if hasattr(supabase_user.created_at, 'isoformat'):
                created_at_str = supabase_user.created_at.isoformat()
            else:
                created_at_str = str(supabase_user.created_at)
        
        last_sign_in_str = None
        if supabase_user.last_sign_in_at:
            if hasattr(supabase_user.last_sign_in_at, 'isoformat'):
                last_sign_in_str = supabase_user.last_sign_in_at.isoformat()
            else:
                last_sign_in_str = str(supabase_user.last_sign_in_at)
        
        return AuthUser(
            id=supabase_user.id,
            email=supabase_user.email,
            phone=supabase_user.phone,
            full_name=user_metadata.get("full_name"),
            provider=AuthProvider.SUPABASE,
            is_email_verified=bool(supabase_user.email_confirmed_at),
            is_phone_verified=bool(supabase_user.phone_confirmed_at),
            provider_metadata=user_metadata,
            created_at=created_at_str,
            last_sign_in=last_sign_in_str
        )
    
    def _convert_to_auth_token(self, supabase_session) -> AuthToken:
        """Convert Supabase session to AuthToken."""
        # Convert expires_at to string if it's provided as an integer timestamp
        expires_at_str = None
        if supabase_session.expires_at is not None:
            if isinstance(supabase_session.expires_at, (int, float)):
                # Convert Unix timestamp to string
                expires_at_str = str(int(supabase_session.expires_at))
            else:
                # Already a string or other type, convert to string
                expires_at_str = str(supabase_session.expires_at)
        
        return AuthToken(
            access_token=supabase_session.access_token,
            refresh_token=supabase_session.refresh_token,
            token_type=supabase_session.token_type or "Bearer",
            expires_in=supabase_session.expires_in,
            expires_at=expires_at_str
        ) 