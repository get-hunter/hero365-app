"""
Authentication Facade

Provides a simplified interface for authentication operations while maintaining 
clean architecture principles by delegating to proper use cases and services.
"""

from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from ..infrastructure.config.dependency_injection import get_container
from ..application.exceptions.application_exceptions import UserNotFoundError


class AuthFacade:
    """
    Facade for authentication and user management operations.
    
    This provides a simplified interface while maintaining proper separation of concerns
    by delegating to use cases and services from the clean architecture.
    """
    
    def __init__(self):
        self.container = get_container()
    
    # Authentication Operations
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a JWT token and return user data."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.verify_token(token)
        
        if result.success and result.user:
            return {
                "id": result.user.id,
                "email": result.user.email,
                "phone": result.user.phone,
                "user_metadata": result.user.metadata,
                "app_metadata": {},  # Can be extracted from metadata if needed
            }
        return None
    
    async def create_user(self, email: str, password: str, user_metadata: Dict = None) -> Dict:
        """Create a new user with email and password."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.register_user(
            email=email,
            password=password,
            metadata=user_metadata
        )
        
        if not result.success:
            raise Exception(f"Failed to create user: {result.error_message}")
        
        return {"user": result.user, "session": result.token}
    
    async def create_user_with_phone(self, phone: str, password: str, user_metadata: Dict = None) -> Dict:
        """Create a new user with phone number and password."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.register_user(
            phone=phone,
            password=password,
            metadata=user_metadata
        )
        
        if not result.success:
            raise Exception(f"Failed to create user with phone: {result.error_message}")
        
        return {"user": result.user, "session": result.token}
    
    # OTP Operations
    async def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number for passwordless authentication."""
        auth_service = self.container.get_auth_service()
        return await auth_service.send_otp(phone)
    
    async def verify_otp(self, phone: str, token: str) -> Dict:
        """Verify OTP for phone number authentication."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.verify_otp(phone, token)
        
        if not result.success:
            raise Exception(f"Failed to verify OTP: {result.error_message}")
        
        return {"user": result.user, "session": result.token}
    
    # User Metadata Operations
    async def update_user_metadata(self, user_id: str, user_metadata: Dict) -> Dict:
        """Update user metadata."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.update_user_metadata(user_id, user_metadata)
        
        if not result.success:
            raise Exception(f"Failed to update user: {result.error_message}")
        
        return result.user
    
    # Onboarding Operations
    async def mark_onboarding_completed(self, user_id: str, completed_steps: List = None, 
                                      completion_date: str = None) -> Dict:
        """Mark user onboarding as completed."""
        onboarding_use_case = self.container.get_manage_onboarding_use_case()
        
        completion_datetime = None
        if completion_date:
            try:
                completion_datetime = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                completion_datetime = datetime.utcnow()
        
        try:
            user_dto = await onboarding_use_case.mark_onboarding_completed(
                uuid.UUID(user_id),
                completed_steps,
                completion_datetime
            )
            return {"user": user_dto.to_dict()}
        except UserNotFoundError as e:
            raise Exception(f"Failed to mark onboarding completed: {str(e)}")
    
    def get_onboarding_data(self, user_metadata: Dict) -> Dict:
        """Extract onboarding data from user metadata."""
        onboarding_use_case = self.container.get_manage_onboarding_use_case()
        return onboarding_use_case.get_onboarding_data(user_metadata)
    
    # User Management Operations
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        auth_service = self.container.get_auth_service()
        return await auth_service.delete_user(user_id)
    
    async def list_users(self, page: int = 1, per_page: int = 50) -> Dict:
        """List all users."""
        auth_service = self.container.get_auth_service()
        return await auth_service.list_users(page, per_page)
    
    # OAuth Operations
    async def sign_in_with_oauth(self, provider: str, id_token: str, access_token: str = None) -> Dict:
        """Sign in with OAuth provider using ID token."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.sign_in_with_oauth(provider, id_token, access_token)
        
        if not result.success:
            raise Exception(f"Failed to sign in with {provider}: {result.error_message}")
        
        return {"user": result.user, "session": result.token}
    
    async def create_user_with_oauth(self, provider: str, provider_id: str, email: str, 
                                   user_metadata: Dict = None) -> Dict:
        """Create a user from OAuth provider data."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.create_user_with_oauth(
            provider, provider_id, email, user_metadata
        )
        
        if not result.success:
            raise Exception(f"Failed to create OAuth user: {result.error_message}")
        
        return {"user": result.user}


# Global instance for backwards compatibility
auth_facade = AuthFacade() 