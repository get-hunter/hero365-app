from supabase import create_client, Client
from gotrue import SyncGoTrueClient
from gotrue.types import AuthResponse, User as SupabaseUser
from typing import Optional
import jwt
from fastapi import HTTPException, status

from app.core.config import settings


class SupabaseService:
    def __init__(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.admin_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            self.enabled = True
        else:
            self.client = None
            self.admin_client = None
            self.enabled = False
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a Supabase JWT token and return user data."""
        if not self.enabled or not self.client:
            return None
        
        try:
            # Use Supabase client to verify token
            response = self.client.auth.get_user(token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "app_metadata": response.user.app_metadata,
                }
            return None
        except Exception as e:
            return None
    
    def create_user(self, email: str, password: str, user_metadata: dict = None) -> AuthResponse:
        """Create a new user with Supabase Auth."""
        if not self.enabled or not self.admin_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication is not configured"
            )
        
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
    
    def update_user_metadata(self, user_id: str, user_metadata: dict) -> dict:
        """Update user metadata."""
        if not self.enabled or not self.admin_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication is not configured"
            )
        
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
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if not self.enabled or not self.admin_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication is not configured"
            )
        
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
        if not self.enabled or not self.admin_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication is not configured"
            )
        
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


# Global instance
supabase_service = SupabaseService() 