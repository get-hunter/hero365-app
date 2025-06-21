from supabase import create_client, Client
from gotrue import SyncGoTrueClient
from gotrue.types import AuthResponse, User as SupabaseUser
from typing import Optional
import jwt
from fastapi import HTTPException, status

from app.core.config import settings


class SupabaseService:
    def __init__(self):
        """Initialize Supabase client with required configuration."""
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.admin_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.enabled = True
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a Supabase JWT token and return user data."""
        try:
            # Use Supabase client to verify token
            response = self.client.auth.get_user(token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "phone": response.user.phone,
                    "user_metadata": response.user.user_metadata,
                    "app_metadata": response.user.app_metadata,
                }
            return None
        except Exception as e:
            return None
    
    def create_user(self, email: str, password: str, user_metadata: dict = None) -> AuthResponse:
        """Create a new user with email and password using Supabase Auth."""
        try:
            response = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": user_metadata or {},
                "email_confirm": True  # Auto-confirm email for admin created users
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user: {str(e)}"
            )
    
    def create_user_with_phone(self, phone: str, password: str, user_metadata: dict = None) -> AuthResponse:
        """Create a new user with phone number and password using Supabase Auth."""
        try:
            response = self.admin_client.auth.admin.create_user({
                "phone": phone,
                "password": password,
                "user_metadata": user_metadata or {},
                "phone_confirm": True  # Auto-confirm phone for admin created users
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user with phone: {str(e)}"
            )
    
    def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number for passwordless authentication."""
        try:
            response = self.client.auth.sign_in_with_otp({
                "phone": phone
            })
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send OTP: {str(e)}"
            )
    
    def verify_otp(self, phone: str, token: str) -> AuthResponse:
        """Verify OTP for phone number authentication."""
        try:
            response = self.client.auth.verify_otp({
                "phone": phone,
                "token": token,
                "type": "sms"
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to verify OTP: {str(e)}"
            )
    
    def update_user_metadata(self, user_id: str, user_metadata: dict) -> dict:
        """Update user metadata."""
        try:
            response = self.admin_client.auth.admin.update_user_by_id(
                user_id, 
                {"user_metadata": user_metadata}
            )
            return response.user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update user: {str(e)}"
            )
    
    def mark_onboarding_completed(self, user_id: str, completed_steps: list = None, completion_date: str = None) -> dict:
        """Mark user onboarding as completed."""
        try:
            # Get current user metadata
            user_response = self.admin_client.auth.admin.get_user_by_id(user_id)
            current_metadata = user_response.user.user_metadata or {}
            
            # Update onboarding metadata
            onboarding_data = {
                "onboarding_completed": True,
                "completed_at": completion_date,
                "completed_steps": completed_steps or []
            }
            
            # Merge with existing metadata
            updated_metadata = {**current_metadata, **onboarding_data}
            
            # Update user metadata
            response = self.admin_client.auth.admin.update_user_by_id(
                user_id, 
                {"user_metadata": updated_metadata}
            )
            return response.user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to mark onboarding completed: {str(e)}"
            )
    
    def get_onboarding_data(self, user_metadata: dict) -> dict:
        """Extract onboarding data from user metadata."""
        if not user_metadata:
            return {
                "onboarding_completed": False,
                "onboarding_completed_at": None,
                "completed_steps": []
            }
        
        from datetime import datetime
        completed_at_str = user_metadata.get("completed_at")
        completed_at = None
        if completed_at_str:
            try:
                completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return {
            "onboarding_completed": user_metadata.get("onboarding_completed", False),
            "onboarding_completed_at": completed_at,
            "completed_steps": user_metadata.get("completed_steps", [])
        }
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            self.admin_client.auth.admin.delete_user(user_id)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete user: {str(e)}"
            )
    
    def list_users(self, page: int = 1, per_page: int = 50) -> dict:
        """List all users."""
        try:
            response = self.admin_client.auth.admin.list_users(
                page=page,
                per_page=per_page
            )
            return {
                "users": response.users,
                "aud": response.aud,
                "next_page": response.next_page,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to list users: {str(e)}"
            )
    
    def sign_in_with_oauth(self, provider: str, id_token: str, access_token: str = None) -> AuthResponse:
        """Sign in with OAuth provider using ID token."""
        try:
            # Use the correct Supabase method for ID token authentication
            response = self.client.auth.sign_in_with_id_token({
                "provider": provider,
                "token": id_token,
                "access_token": access_token
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to sign in with {provider}: {str(e)}"
            )
    
    def create_user_with_oauth(self, provider: str, provider_id: str, email: str, user_metadata: dict = None) -> AuthResponse:
        """Create a user from OAuth provider data."""
        try:
            # Create user with admin client
            response = self.admin_client.auth.admin.create_user({
                "email": email,
                "user_metadata": user_metadata or {},
                "app_metadata": {
                    "provider": provider,
                    "provider_id": provider_id
                },
                "email_confirm": True  # OAuth users are pre-verified
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create OAuth user: {str(e)}"
            )


# Global instance
supabase_service = SupabaseService() 