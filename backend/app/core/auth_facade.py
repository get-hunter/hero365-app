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
            
            # Get current business context with automatic default selection
            current_business_id = self._get_current_business_id_from_metadata(
                getattr(result.user, 'metadata', {}), business_memberships
            )
            
            # If user has businesses but no current business context, set the first one as default
            if not current_business_id and business_memberships:
                current_business_id = business_memberships[0]["business_id"]
                # Update user metadata to remember this choice for future requests
                try:
                    await self.update_user_metadata(result.user.id, {
                        "current_business_id": current_business_id
                    })
                except Exception:
                    # If updating metadata fails, continue anyway
                    pass
            
            user_data = {
                "sub": result.user.id,  # Standard JWT subject claim
                "id": result.user.id,
                "email": result.user.email,
                "phone": getattr(result.user, 'phone', None),
                "user_metadata": getattr(result.user, 'metadata', {}),
                "app_metadata": {},  # Can be extracted from metadata if needed
                "business_memberships": business_memberships,
                "current_business_id": current_business_id
            }
            return user_data
        return None

    async def create_enhanced_jwt_token(self, user_id: str, current_business_id: Optional[str] = None) -> str:
        """Create an enhanced JWT token with business context."""
        # Get user's business memberships
        business_memberships = await self._get_user_business_memberships(user_id)
        
        # Normalize business IDs to lowercase for consistency
        normalized_memberships = []
        for membership in business_memberships:
            normalized_membership = membership.copy()
            normalized_membership["business_id"] = membership["business_id"].lower()
            normalized_memberships.append(normalized_membership)
        
        # If no current business specified, use the first one or None
        if not current_business_id and normalized_memberships:
            current_business_id = normalized_memberships[0]["business_id"]
        elif current_business_id:
            # Normalize current business ID to lowercase
            current_business_id = current_business_id.lower()
        
        # Create JWT payload with business context
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "current_business_id": current_business_id,
            "business_memberships": normalized_memberships,
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
        
        # Normalize UUIDs to lowercase for case-insensitive comparison
        new_business_id_normalized = new_business_id.lower()
        valid_business_ids_normalized = [bid.lower() for bid in valid_business_ids]
        
        if new_business_id_normalized not in valid_business_ids_normalized:
            raise ValueError(f"User is not a member of business {new_business_id}")
        
        # Create new token with updated business context (use original case from database)
        # Find the original business ID from the valid list
        matching_business_id = None
        for original_id in valid_business_ids:
            if original_id.lower() == new_business_id_normalized:
                matching_business_id = original_id
                break
        
        return await self.create_enhanced_jwt_token(user_id, matching_business_id or new_business_id)

    async def _get_user_business_memberships(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's business memberships with roles and permissions."""
        try:
            membership_repo = self.container.get_business_membership_repository()
            memberships = await membership_repo.get_user_memberships(user_id)
            
            membership_data = []
            for membership in memberships:
                if membership.is_active:
                    # Handle role as either enum or string
                    role_value = membership.role.value if hasattr(membership.role, 'value') else membership.role
                    
                    membership_data.append({
                        "business_id": str(membership.business_id),
                        "role": role_value,
                        "permissions": membership.permissions,
                        "role_level": membership.get_role_level() if hasattr(membership, 'get_role_level') else 0
                    })
            
            return membership_data
            
        except Exception as e:
            # Log the actual error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting user business memberships for {user_id}: {str(e)}")
            return []

    def _get_current_business_id_from_metadata(self, metadata: Dict, memberships: List[Dict]) -> Optional[str]:
        """Extract current business ID from user metadata or default to first membership."""
        # Check if user has a preferred business in metadata
        current_business = metadata.get("current_business_id")
        
        if current_business and memberships:
            # Verify the preferred business is in user's memberships with case-insensitive comparison
            valid_business_ids = [m["business_id"] for m in memberships]
            current_business_normalized = current_business.lower()
            valid_business_ids_normalized = [bid.lower() for bid in valid_business_ids]
            
            if current_business_normalized in valid_business_ids_normalized:
                # Find the original business ID with correct case
                for original_id in valid_business_ids:
                    if original_id.lower() == current_business_normalized:
                        return original_id
        
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
    
    async def revoke_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a specific user (force sign out)."""
        auth_service = self.container.get_auth_service()
        return await auth_service.revoke_user_tokens(user_id)
    
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