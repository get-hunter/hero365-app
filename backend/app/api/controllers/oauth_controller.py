"""
OAuth Controller

Handles Apple and Google Sign-In using Supabase's server-side OAuth methods.
This maintains the iOS App → Backend → Supabase Auth flow.
"""

import jwt
from typing import Dict, Any
from fastapi import HTTPException, status

from app.core.supabase import supabase_service
from app.api.schemas.auth_schemas import (
    AppleSignInRequest,
    GoogleSignInRequest, 
    OAuthSignInResponse,
    AuthUserResponse
)


class OAuthController:
    """Controller for handling OAuth authentication flows."""
    
    def __init__(self):
        self.supabase = supabase_service
    
    async def apple_sign_in(self, request: AppleSignInRequest) -> OAuthSignInResponse:
        """
        Handle Apple Sign-In using ID token from iOS app.
        
        Flow: iOS App sends ID token → Backend validates with Supabase → Returns session
        """
        try:
            print(f"🍎 Apple Sign-In attempt for user: {request.user_identifier}")
            print(f"📧 Email: {request.email}")
            print(f"👤 Full name: {request.full_name}")
            print(f"🔑 ID token length: {len(request.id_token)} chars")
            
            # Use Supabase's OAuth method with Apple ID token
            auth_response = self.supabase.sign_in_with_oauth(
                provider="apple",
                id_token=request.id_token
            )
            
            if not auth_response.user or not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Apple Sign-In failed: Invalid ID token"
                )
            
            print(f"✅ Apple Sign-In successful for Supabase user: {auth_response.user.id}")
            
            # Update user metadata with provided full_name if available
            if request.full_name:
                await self._update_user_metadata_if_needed(auth_response.user.id, {
                    "full_name": request.full_name
                })
                print(f"📝 Updated user metadata with full_name: {request.full_name}")
            
            # Check if this is a new user
            is_new_user = self._is_new_user(auth_response.user)
            
            # Get fresh user data to include any metadata updates
            updated_user_response = self.supabase.admin_client.auth.admin.get_user_by_id(auth_response.user.id)
            updated_user = updated_user_response.user
            
            # Get onboarding data
            onboarding_data = self.supabase.get_onboarding_data(updated_user.user_metadata or {})
            
            # Build user response
            user_data = AuthUserResponse(
                id=updated_user.id,
                email=updated_user.email,
                phone=updated_user.phone,
                full_name=self._get_full_name(updated_user, request.full_name),
                is_active=True,
                is_superuser=False,
                supabase_id=updated_user.id,
                onboarding_completed=onboarding_data["onboarding_completed"],
                onboarding_completed_at=onboarding_data["onboarding_completed_at"],
                completed_steps=onboarding_data["completed_steps"]
            )
            
            return OAuthSignInResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                expires_in=auth_response.session.expires_in or 3600,
                token_type="bearer",
                user=user_data,
                is_new_user=is_new_user
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Apple Sign-In error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Apple Sign-In failed: {str(e)}"
            )
    
    async def google_sign_in(self, request: GoogleSignInRequest) -> OAuthSignInResponse:
        """
        Handle Google Sign-In using ID token from iOS app.
        
        Flow: iOS App sends ID token → Backend validates with Supabase → Returns session
        """
        try:
            print(f"🔍 Google Sign-In attempt")
            print(f"📧 Email: {request.email}")
            print(f"👤 Full name: {request.full_name}")
            print(f"🔑 ID token length: {len(request.id_token)} chars")
            
            # Use Supabase's OAuth method with Google ID token
            auth_response = self.supabase.sign_in_with_oauth(
                provider="google",
                id_token=request.id_token,
                access_token=request.access_token
            )
            
            if not auth_response.user or not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Sign-In failed: Invalid ID token"
                )
            
            print(f"✅ Google Sign-In successful for Supabase user: {auth_response.user.id}")
            
            # Update user metadata with provided full_name if available
            if request.full_name:
                await self._update_user_metadata_if_needed(auth_response.user.id, {
                    "full_name": request.full_name
                })
                print(f"📝 Updated user metadata with full_name: {request.full_name}")
            
            # Update user metadata with additional Google data if available
            google_metadata = {}
            if request.given_name:
                google_metadata["given_name"] = request.given_name
            if request.family_name:
                google_metadata["family_name"] = request.family_name
            if request.picture_url:
                google_metadata["picture_url"] = request.picture_url
            
            if google_metadata:
                await self._update_user_metadata_if_needed(auth_response.user.id, google_metadata)
                print(f"📝 Updated user metadata with Google data: {google_metadata}")
            
            # Check if this is a new user
            is_new_user = self._is_new_user(auth_response.user)
            
            # Get fresh user data to include any metadata updates
            updated_user_response = self.supabase.admin_client.auth.admin.get_user_by_id(auth_response.user.id)
            updated_user = updated_user_response.user
            
            # Get onboarding data
            onboarding_data = self.supabase.get_onboarding_data(updated_user.user_metadata or {})
            
            # Build user response
            user_data = AuthUserResponse(
                id=updated_user.id,
                email=updated_user.email,
                phone=updated_user.phone,
                full_name=self._get_full_name(updated_user, request.full_name),
                is_active=True,
                is_superuser=False,
                supabase_id=updated_user.id,
                onboarding_completed=onboarding_data["onboarding_completed"],
                onboarding_completed_at=onboarding_data["onboarding_completed_at"],
                completed_steps=onboarding_data["completed_steps"]
            )
            
            return OAuthSignInResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                expires_in=auth_response.session.expires_in or 3600,
                token_type="bearer",
                user=user_data,
                is_new_user=is_new_user
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Google Sign-In error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google Sign-In failed: {str(e)}"
            )
    
    def _is_new_user(self, user) -> bool:
        """Check if this is a newly created user based on creation time."""
        try:
            # Simple heuristic: if user was created in the last minute, consider it new
            from datetime import datetime, timedelta
            created_at = datetime.fromisoformat(user.created_at.replace('Z', '+00:00'))
            return datetime.now().astimezone() - created_at < timedelta(minutes=1)
        except:
            return False
    
    def _get_full_name(self, user, provided_name: str = None) -> str:
        """Get full name from user metadata or provided name."""
        if provided_name:
            return provided_name
        
        user_metadata = getattr(user, 'user_metadata', {}) or {}
        return (
            user_metadata.get('full_name') or
            user_metadata.get('name') or
            f"{user_metadata.get('given_name', '')} {user_metadata.get('family_name', '')}".strip() or
            None
        )
    
    async def _update_user_metadata_if_needed(self, user_id: str, metadata_updates: dict) -> None:
        """Update user metadata with provided information if not already present."""
        try:
            # Get current user metadata
            user_response = self.supabase.admin_client.auth.admin.get_user_by_id(user_id)
            current_metadata = user_response.user.user_metadata or {}
            
            # Only update fields that are not already set or are empty
            updates_needed = {}
            for key, value in metadata_updates.items():
                if value and (not current_metadata.get(key) or current_metadata.get(key).strip() == ""):
                    updates_needed[key] = value
            
            # Update only if there are changes needed
            if updates_needed:
                updated_metadata = {**current_metadata, **updates_needed}
                self.supabase.admin_client.auth.admin.update_user_by_id(
                    user_id,
                    {"user_metadata": updated_metadata}
                )
                print(f"🔄 Updated user metadata: {updates_needed}")
            else:
                print(f"ℹ️ User metadata already contains required fields, no update needed")
                
        except Exception as e:
            print(f"⚠️ Failed to update user metadata: {str(e)}")
            # Don't raise exception - this is not critical for auth flow 