"""
Manage User Onboarding Use Case

Business logic for handling user onboarding process.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from ...dto.user_dto import UserDTO, UpdateUserDTO
from ...exceptions.application_exceptions import UserNotFoundError
from ....domain.repositories.user_repository import UserRepository
from ...ports.auth_service import AuthServicePort


class ManageOnboardingUseCase:
    """
    Use case for managing user onboarding process.
    
    Handles onboarding completion, tracking steps, and extracting onboarding data.
    """
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthServicePort):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    async def mark_onboarding_completed(
        self, 
        user_id: uuid.UUID, 
        completed_steps: Optional[List[str]] = None,
        completion_date: Optional[datetime] = None
    ) -> UserDTO:
        """
        Mark user onboarding as completed.
        
        Args:
            user_id: ID of the user
            completed_steps: List of completed onboarding steps  
            completion_date: When onboarding was completed
            
        Returns:
            Updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        # Get current user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Prepare onboarding metadata
        completion_date = completion_date or datetime.utcnow()
        onboarding_data = {
            "onboarding_completed": True,
            "completed_at": completion_date.isoformat(),
            "completed_steps": completed_steps or []
        }
        
        # Update user metadata in auth service
        current_metadata = user.metadata or {}
        updated_metadata = {**current_metadata, **onboarding_data}
        
        auth_result = await self.auth_service.update_user_metadata(
            str(user_id), 
            updated_metadata
        )
        
        if not auth_result.success:
            raise Exception(f"Failed to update user metadata: {auth_result.error_message}")
        
        # Update user in repository
        update_dto = UpdateUserDTO(
            metadata=updated_metadata
        )
        
        updated_user = await self.user_repository.update(user_id, update_dto)
        return UserDTO.from_entity(updated_user)
    
    def get_onboarding_data(self, user_metadata: Optional[Dict]) -> Dict:
        """
        Extract onboarding data from user metadata.
        
        Args:
            user_metadata: User's metadata dictionary
            
        Returns:
            Dictionary containing onboarding status and data
        """
        if not user_metadata:
            return {
                "onboarding_completed": False,
                "onboarding_completed_at": None,
                "completed_steps": []
            }
        
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
    
    async def get_user_onboarding_status(self, user_id: uuid.UUID) -> Dict:
        """
        Get onboarding status for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing onboarding status and data
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        return self.get_onboarding_data(user.metadata)
    
    async def update_onboarding_step(
        self, 
        user_id: uuid.UUID, 
        step_name: str, 
        step_data: Optional[Dict] = None
    ) -> UserDTO:
        """
        Update a specific onboarding step for a user.
        
        Args:
            user_id: ID of the user
            step_name: Name of the onboarding step
            step_data: Additional data for the step
            
        Returns:
            Updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        current_metadata = user.metadata or {}
        completed_steps = current_metadata.get("completed_steps", [])
        
        # Add step if not already completed
        if step_name not in completed_steps:
            completed_steps.append(step_name)
        
        # Update step data if provided
        step_metadata = current_metadata.get("step_data", {})
        if step_data:
            step_metadata[step_name] = step_data
        
        # Update metadata
        updated_metadata = {
            **current_metadata,
            "completed_steps": completed_steps,
            "step_data": step_metadata
        }
        
        # Update in auth service
        auth_result = await self.auth_service.update_user_metadata(
            str(user_id), 
            updated_metadata
        )
        
        if not auth_result.success:
            raise Exception(f"Failed to update user metadata: {auth_result.error_message}")
        
        # Update user in repository
        update_dto = UpdateUserDTO(
            metadata=updated_metadata
        )
        
        updated_user = await self.user_repository.update(user_id, update_dto)
        return UserDTO.from_entity(updated_user) 