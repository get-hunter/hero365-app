"""
Update User Use Case

Business logic for updating user information.
"""

import uuid
from typing import Optional

from ...dto.user_dto import UpdateUserDTO, UserDTO
from ...exceptions.application_exceptions import (
    UserNotFoundError, UserAlreadyExistsError, ValidationError, PermissionDeniedError
)
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.exceptions.domain_exceptions import DomainValidationError


class UpdateUserUseCase:
    """
    Use case for updating user information.
    
    This use case handles the business logic for user updates,
    including validation, uniqueness checks, and permission verification.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: uuid.UUID, update_dto: UpdateUserDTO,
                     requesting_user_id: Optional[uuid.UUID] = None,
                     is_superuser: bool = False) -> UserDTO:
        """
        Execute the update user use case.
        
        Args:
            user_id: ID of the user to update
            update_dto: Data for updating the user
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            UserDTO containing the updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValidationError: If input validation fails
            UserAlreadyExistsError: If email/phone already exists
            PermissionDeniedError: If user lacks permission
        """
        # Get existing user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Check permissions
        if not self._can_update_user(user, requesting_user_id, is_superuser):
            raise PermissionDeniedError("update_user", str(user_id))
        
        # Validate input
        await self._validate_input(update_dto, user_id)
        
        # Check for conflicts with other users
        await self._check_uniqueness(update_dto, user_id)
        
        # Update user entity
        await self._update_user_entity(user, update_dto)
        
        # Save changes
        updated_user = await self.user_repository.update(user)
        
        # Convert to DTO
        return self._entity_to_dto(updated_user)
    
    async def _validate_input(self, dto: UpdateUserDTO, user_id: uuid.UUID) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: UpdateUserDTO to validate
            user_id: ID of user being updated
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate email format if provided
        if dto.email is not None:
            try:
                Email.create(dto.email)
            except DomainValidationError as e:
                raise ValidationError("email", str(e))
        
        # Validate phone format if provided
        if dto.phone is not None:
            try:
                Phone.create(dto.phone)
            except DomainValidationError as e:
                raise ValidationError("phone", str(e))
        
        # Validate full name if provided
        if dto.full_name is not None and len(dto.full_name.strip()) == 0:
            raise ValidationError("full_name", "Full name cannot be empty")
    
    async def _check_uniqueness(self, dto: UpdateUserDTO, user_id: uuid.UUID) -> None:
        """
        Check if email/phone conflicts with other users.
        
        Args:
            dto: UpdateUserDTO to check
            user_id: ID of user being updated (to exclude from check)
            
        Raises:
            UserAlreadyExistsError: If email/phone already exists
        """
        if dto.email is not None:
            email = Email.create(dto.email)
            if await self.user_repository.email_exists(email, exclude_user_id=user_id):
                raise UserAlreadyExistsError(f"email:{dto.email}")
        
        if dto.phone is not None:
            phone = Phone.create(dto.phone)
            if await self.user_repository.phone_exists(phone, exclude_user_id=user_id):
                raise UserAlreadyExistsError(f"phone:{dto.phone}")
    
    async def _update_user_entity(self, user: User, dto: UpdateUserDTO) -> None:
        """
        Update the user entity with new data.
        
        Args:
            user: User entity to update
            dto: Update data
        """
        # Prepare update data
        email = Email.create(dto.email) if dto.email is not None else None
        phone = Phone.create(dto.phone) if dto.phone is not None else None
        
        # Update profile information
        if dto.email is not None or dto.phone is not None or dto.full_name is not None:
            user.update_profile(
                full_name=dto.full_name,
                email=email,
                phone=phone
            )
        
        # Update status if provided (only superusers can change this)
        if dto.is_active is not None:
            if dto.is_active:
                user.activate()
            else:
                user.deactivate()
        
        # Update superuser status if provided (only superusers can change this)
        if dto.is_superuser is not None:
            if dto.is_superuser:
                user.grant_superuser_privileges()
            else:
                user.revoke_superuser_privileges()
    
    def _can_update_user(self, user: User, requesting_user_id: Optional[uuid.UUID],
                        is_superuser: bool) -> bool:
        """
        Check if the requesting user can update the target user.
        
        Args:
            user: User to update
            requesting_user_id: ID of requesting user
            is_superuser: Whether requesting user is superuser
            
        Returns:
            True if user can be updated, False otherwise
        """
        # Superusers can update any user
        if is_superuser:
            return True
        
        # Users can update their own profile (with limitations)
        if requesting_user_id and user.id == requesting_user_id:
            return True
        
        return False
    
    def _entity_to_dto(self, user: User) -> UserDTO:
        """
        Convert User entity to UserDTO.
        
        Args:
            user: User entity
            
        Returns:
            UserDTO
        """
        return UserDTO(
            id=user.id,
            email=str(user.email) if user.email else None,
            phone=str(user.phone) if user.phone else None,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            supabase_id=user.supabase_id
        ) 