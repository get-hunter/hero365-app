"""
Manage Onboarding Use Case

Business logic for user onboarding operations.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from ...dto.auth_dto import AuthUserDTO
from ...exceptions.application_exceptions import UserNotFoundError, ValidationError


class ManageOnboardingUseCase:
    """
    Use case for managing user onboarding operations.
    
    This use case handles:
    - Extracting onboarding data from user metadata
    - Marking onboarding as completed
    - Updating onboarding steps
    - Validating onboarding status
    """
    
    def __init__(self):
        # No dependencies needed for Supabase-only onboarding management
        pass
    
    def get_onboarding_data(self, user_metadata: Dict) -> Dict:
        """
        Extract onboarding data from user metadata.
        
        Args:
            user_metadata: User metadata dictionary from Supabase
            
        Returns:
            Dict containing onboarding status and completion data
        """
        if not user_metadata:
            user_metadata = {}
        
        # Extract onboarding data with defaults
        onboarding_completed = user_metadata.get("onboarding_completed", False)
        completed_at = user_metadata.get("completed_at")
        completed_steps = user_metadata.get("completed_steps", [])
        
        # Parse completion date if it exists
        onboarding_completed_at = None
        if completed_at:
            try:
                if isinstance(completed_at, str):
                    # Try to parse ISO format
                    onboarding_completed_at = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                elif isinstance(completed_at, datetime):
                    onboarding_completed_at = completed_at
            except (ValueError, AttributeError):
                # If parsing fails, leave as None
                pass
        
        return {
            "onboarding_completed": onboarding_completed,
            "onboarding_completed_at": onboarding_completed_at,
            "completed_steps": completed_steps if isinstance(completed_steps, list) else []
        }
    
    async def mark_onboarding_completed(
        self,
        user_id: uuid.UUID,
        completed_steps: Optional[List[str]] = None,
        completion_date: Optional[datetime] = None
    ) -> AuthUserDTO:
        """
        Mark user onboarding as completed.
        
        Args:
            user_id: ID of the user
            completed_steps: List of completed onboarding steps
            completion_date: Custom completion date (defaults to current timestamp)
            
        Returns:
            AuthUserDTO with updated onboarding data
            
        Raises:
            UserNotFoundError: If user not found
            ValidationError: If input data is invalid
        """
        if not user_id:
            raise ValidationError("User ID is required")
        
        # Set completion date to now if not provided
        if not completion_date:
            completion_date = datetime.utcnow()
        
        # Validate completed steps
        if completed_steps is None:
            completed_steps = []
        elif not isinstance(completed_steps, list):
            raise ValidationError("Completed steps must be a list")
        
        # Note: In a full implementation, this would update the user metadata
        # through the auth service. For now, we'll create a DTO representation
        # that the facade can use to update the actual user.
        
        return AuthUserDTO(
            id=str(user_id),
            email=None,  # Will be filled by the facade
            phone=None,  # Will be filled by the facade
            metadata={
                "onboarding_completed": True,
                "completed_at": completion_date.isoformat(),
                "completed_steps": completed_steps
            }
        )
    
    def update_onboarding_step(
        self,
        user_metadata: Dict,
        step_name: str,
        completed: bool = True
    ) -> Dict:
        """
        Update a specific onboarding step.
        
        Args:
            user_metadata: Current user metadata
            step_name: Name of the onboarding step
            completed: Whether the step is completed
            
        Returns:
            Updated metadata dictionary
        """
        if not user_metadata:
            user_metadata = {}
        
        if not step_name:
            raise ValidationError("Step name is required")
        
        # Get current completed steps
        completed_steps = user_metadata.get("completed_steps", [])
        if not isinstance(completed_steps, list):
            completed_steps = []
        
        # Update step status
        if completed and step_name not in completed_steps:
            completed_steps.append(step_name)
        elif not completed and step_name in completed_steps:
            completed_steps.remove(step_name)
        
        # Update metadata
        updated_metadata = user_metadata.copy()
        updated_metadata["completed_steps"] = completed_steps
        
        return updated_metadata
    
    def is_onboarding_complete(
        self,
        user_metadata: Dict,
        required_steps: Optional[List[str]] = None
    ) -> bool:
        """
        Check if onboarding is complete based on required steps.
        
        Args:
            user_metadata: User metadata dictionary
            required_steps: List of required steps (optional)
            
        Returns:
            True if onboarding is complete
        """
        onboarding_data = self.get_onboarding_data(user_metadata)
        
        # If onboarding is explicitly marked as completed
        if onboarding_data["onboarding_completed"]:
            return True
        
        # If required steps are specified, check if all are completed
        if required_steps:
            completed_steps = set(onboarding_data["completed_steps"])
            required_steps_set = set(required_steps)
            return required_steps_set.issubset(completed_steps)
        
        return False
    
    def get_pending_steps(
        self,
        user_metadata: Dict,
        all_steps: List[str]
    ) -> List[str]:
        """
        Get list of pending onboarding steps.
        
        Args:
            user_metadata: User metadata dictionary
            all_steps: List of all possible onboarding steps
            
        Returns:
            List of pending step names
        """
        onboarding_data = self.get_onboarding_data(user_metadata)
        completed_steps = set(onboarding_data["completed_steps"])
        all_steps_set = set(all_steps)
        
        return list(all_steps_set - completed_steps) 