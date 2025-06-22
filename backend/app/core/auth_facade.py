"""
Authentication Facade

Provides a simplified interface for authentication operations while maintaining 
clean architecture principles by delegating to proper use cases and services.
"""

from typing import Optional, Dict, Any, List
import uuid
import jwt
from datetime import datetime, timedelta

from ..infrastructure.config.dependency_injection import get_container
from ..application.exceptions.application_exceptions import UserNotFoundError
from ..core.config import settings


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
        """Verify a JWT token and return user data with business context."""
        auth_service = self.container.get_auth_service()
        result = await auth_service.verify_token(token)
        
        if result.success and result.user:
            # Get user's business memberships
            business_memberships = await self._get_user_business_memberships(result.user.id)
            
            user_data = {
                "sub": result.user.id,  # Standard JWT subject claim
                "id": result.user.id,
                "email": result.user.email,
                "phone": getattr(result.user, 'phone', None),
                "user_metadata": getattr(result.user, 'metadata', {}),
                "app_metadata": {},  # Can be extracted from metadata if needed
                "business_memberships": business_memberships,
                "current_business_id": self._get_current_business_id_from_metadata(
                    getattr(result.user, 'metadata', {}), business_memberships
                )
            }
            return user_data
        return None

    async def create_enhanced_jwt_token(self, user_id: str, current_business_id: Optional[str] = None) -> str:
        """Create an enhanced JWT token with business context."""
        # Get user's business memberships
        business_memberships = await self._get_user_business_memberships(user_id)
        
        # If no current business specified, use the first one or None
        if not current_business_id and business_memberships:
            current_business_id = business_memberships[0]["business_id"]
        
        # Create JWT payload with business context
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "current_business_id": current_business_id,
            "business_memberships": business_memberships,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
        }
        
        # Generate JWT token
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        return token

    async def verify_enhanced_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify enhanced JWT token and return decoded payload."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            
            # Validate business memberships are still active
            user_id = payload.get("sub") or payload.get("user_id")
            current_memberships = await self._get_user_business_memberships(user_id)
            
            # Update token data with current membership status
            payload["business_memberships"] = current_memberships
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    async def switch_business_context(self, user_id: str, new_business_id: str) -> str:
        """Switch user's business context and return new JWT token."""
        # Verify user is member of the target business
        business_memberships = await self._get_user_business_memberships(user_id)
        
        valid_business_ids = [membership["business_id"] for membership in business_memberships]
        
        if new_business_id not in valid_business_ids:
            raise ValueError(f"User is not a member of business {new_business_id}")
        
        # Create new token with updated business context
        return await self.create_enhanced_jwt_token(user_id, new_business_id)

    async def _get_user_business_memberships(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's business memberships with roles and permissions."""
        try:
            membership_repo = self.container.get_business_membership_repository()
            memberships = await membership_repo.get_user_memberships(user_id)
            
            membership_data = []
            for membership in memberships:
                if membership.is_active:
                    membership_data.append({
                        "business_id": str(membership.business_id),
                        "role": membership.role.value,
                        "permissions": membership.permissions,
                        "role_level": membership.get_role_level()
                    })
            
            return membership_data
            
        except Exception:
            return []

    def _get_current_business_id_from_metadata(self, metadata: Dict, memberships: List[Dict]) -> Optional[str]:
        """Extract current business ID from user metadata or default to first membership."""
        # Check if user has a preferred business in metadata
        current_business = metadata.get("current_business_id")
        
        if current_business and memberships:
            # Verify the preferred business is in user's memberships
            valid_business_ids = [m["business_id"] for m in memberships]
            if current_business in valid_business_ids:
                return current_business
        
        # Default to first membership if available
        if memberships:
            return memberships[0]["business_id"]
        
        return None

    # Authentication Operations
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