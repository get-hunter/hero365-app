"""
OAuth Controller

Handles Apple and Google Sign-In using Supabase's server-side OAuth methods.
This maintains the iOS App → Backend → Supabase Auth flow.
"""

import jwt
from typing import Dict, Any
from fastapi import HTTPException, status

from app.core.auth_facade import auth_facade
from app.infrastructure.config.dependency_injection import get_container
from app.api.schemas.auth_schemas import (
    AppleSignInRequest,
    GoogleSignInRequest, 
    OAuthSignInResponse,
    AuthUserResponse
)


class OAuthController:
    """Controller for handling OAuth authentication flows."""
    
    def __init__(self):
        self.auth_facade = auth_facade
        self.container = get_container()
    
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
            auth_response = await self.auth_facade.sign_in_with_oauth(
                provider="apple",
                id_token=request.id_token
            )
            
            user_data = auth_response.get("user")
            session_data = auth_response.get("session")
            
            if not user_data or not session_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Apple Sign-In failed: Invalid ID token"
                )
            
            print(f"✅ Apple Sign-In successful for Supabase user: {user_data.id}")
            
            # Update user metadata with provided full_name if available
            if request.full_name:
                await self._update_user_metadata_if_needed(user_data.id, {
                    "full_name": request.full_name
                })
                print(f"📝 Updated user metadata with full_name: {request.full_name}")
            
            # Check if this is a new user
            is_new_user = self._is_new_user(user_data)
            
            # Get fresh user data to include any metadata updates
            auth_service = self.container.get_auth_service()
            updated_user_result = await auth_service.get_user_by_id(user_data.id)
            
            # Get onboarding data using the correct metadata field
            user_metadata = (updated_user_result.provider_metadata if updated_user_result 
                           else user_data.provider_metadata) or {}
            onboarding_data = self.auth_facade.get_onboarding_data(user_metadata)
            
            # Build user response
            user_response = AuthUserResponse(
                id=user_data.id,
                email=user_data.email,
                phone=user_data.phone,
                full_name=self._get_full_name_from_metadata(user_metadata, request.full_name),
                is_active=True,
                is_superuser=False,
                supabase_id=user_data.id,
                onboarding_completed=onboarding_data["onboarding_completed"],
                onboarding_completed_at=onboarding_data["onboarding_completed_at"],
                completed_steps=onboarding_data["completed_steps"]
            )
            
            return OAuthSignInResponse(
                access_token=session_data.access_token,
                refresh_token=session_data.refresh_token,
                expires_in=getattr(session_data, 'expires_in', 3600),
                token_type="bearer",
                user=user_response,
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
            auth_response = await self.auth_facade.sign_in_with_oauth(
                provider="google",
                id_token=request.id_token,
                access_token=request.access_token
            )
            
            user_data = auth_response.get("user")
            session_data = auth_response.get("session")
            
            if not user_data or not session_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Sign-In failed: Invalid ID token"
                )
            
            print(f"✅ Google Sign-In successful for Supabase user: {user_data.id}")
            
            # Update user metadata with provided full_name if available
            if request.full_name:
                await self._update_user_metadata_if_needed(user_data.id, {
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
                await self._update_user_metadata_if_needed(user_data.id, google_metadata)
                print(f"📝 Updated user metadata with Google data: {google_metadata}")
            
            # Check if this is a new user
            is_new_user = self._is_new_user(user_data)
            
            # Get fresh user data to include any metadata updates
            auth_service = self.container.get_auth_service()
            updated_user_result = await auth_service.get_user_by_id(user_data.id)
            
            # Get onboarding data using the correct metadata field
            user_metadata = (updated_user_result.provider_metadata if updated_user_result 
                           else user_data.provider_metadata) or {}
            onboarding_data = self.auth_facade.get_onboarding_data(user_metadata)
            
            # Build user response
            user_response = AuthUserResponse(
                id=user_data.id,
                email=user_data.email,
                phone=user_data.phone,
                full_name=self._get_full_name_from_metadata(user_metadata, request.full_name),
                is_active=True,
                is_superuser=False,
                supabase_id=user_data.id,
                onboarding_completed=onboarding_data["onboarding_completed"],
                onboarding_completed_at=onboarding_data["onboarding_completed_at"],
                completed_steps=onboarding_data["completed_steps"]
            )
            
            return OAuthSignInResponse(
                access_token=session_data.access_token,
                refresh_token=session_data.refresh_token,
                expires_in=getattr(session_data, 'expires_in', 3600),
                token_type="bearer",
                user=user_response,
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
            created_at_str = getattr(user, 'created_at', None)
            if not created_at_str:
                return False
            
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            return datetime.now().astimezone() - created_at < timedelta(minutes=1)
        except:
            return False
    
    async def _update_user_metadata_if_needed(self, user_id: str, metadata_updates: dict) -> None:
        """Update user metadata if the provided data is not empty."""
        if not metadata_updates:
            return
        
        try:
            await self.auth_facade.update_user_metadata(user_id, metadata_updates)
        except Exception as e:
            print(f"⚠️ Warning: Failed to update user metadata: {str(e)}")
            # Don't fail the whole flow if metadata update fails
    
    def _get_full_name_from_metadata(self, user_metadata: dict, fallback_name: str = None) -> str:
        """Extract full name from user metadata with fallback."""
        if not user_metadata:
            return fallback_name
        
        return user_metadata.get("full_name", fallback_name) 