"""
Authenticate User Use Case

Business logic for user authentication.
"""

from typing import Optional

from ...dto.auth_dto import LoginDTO, AuthTokenDTO, AuthUserDTO
from ...exceptions.application_exceptions import (
    AuthenticationFailedException, InvalidCredentialsError, AccountInactiveError,
    UserNotFoundError, ValidationError
)
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.value_objects.password import Password
from ....domain.exceptions.domain_exceptions import DomainValidationError


class AuthenticateUserUseCase:
    """
    Use case for authenticating users.
    
    This use case handles the business logic for user authentication,
    including credential validation and account status checking.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, login_dto: LoginDTO) -> AuthUserDTO:
        """
        Execute the authenticate user use case.
        
        Args:
            login_dto: Login credentials
            
        Returns:
            AuthUserDTO containing authenticated user data
            
        Raises:
            ValidationError: If input validation fails
            UserNotFoundError: If user doesn't exist
            InvalidCredentialsError: If credentials are invalid
            AccountInactiveError: If account is inactive
            AuthenticationFailedException: If authentication fails
        """
        # Validate input
        self._validate_input(login_dto)
        
        # Find user by email or phone
        user = await self._find_user(login_dto)
        if not user:
            raise UserNotFoundError("Invalid credentials")
        
        # Check account status
        if not user.can_access_system():
            raise AccountInactiveError()
        
        # For Supabase users, we don't verify password here
        # That would be handled by Supabase authentication
        if user.supabase_id:
            # Supabase user - authentication is handled externally
            pass
        else:
            # Local user - verify password if available
            # Note: In the current domain model, User entity doesn't store hashed_password
            # This would need to be handled differently, perhaps through a separate service
            raise AuthenticationFailedException("Local authentication not supported in this implementation")
        
        # Return authenticated user data
        return self._entity_to_auth_dto(user)
    
    async def authenticate_supabase_user(self, supabase_id: str) -> AuthUserDTO:
        """
        Authenticate a user using Supabase ID.
        
        Args:
            supabase_id: Supabase user ID
            
        Returns:
            AuthUserDTO containing authenticated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            AccountInactiveError: If account is inactive
        """
        # Find user by Supabase ID
        user = await self.user_repository.get_by_supabase_id(supabase_id)
        if not user:
            raise UserNotFoundError(f"supabase_id:{supabase_id}")
        
        # Check account status
        if not user.can_access_system():
            raise AccountInactiveError()
        
        return self._entity_to_auth_dto(user)
    
    def _validate_input(self, dto: LoginDTO) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: LoginDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Must have either email or phone
        if not dto.email and not dto.phone:
            raise ValidationError(
                "credentials", 
                "Either email or phone number is required"
            )
        
        # Must have password
        if not dto.password:
            raise ValidationError("password", "Password is required")
        
        # Validate email format if provided
        if dto.email:
            try:
                Email.create(dto.email)
            except DomainValidationError as e:
                raise ValidationError("email", str(e))
        
        # Validate phone format if provided
        if dto.phone:
            try:
                Phone.create(dto.phone)
            except DomainValidationError as e:
                raise ValidationError("phone", str(e))
    
    async def _find_user(self, dto: LoginDTO):
        """
        Find user by email or phone.
        
        Args:
            dto: LoginDTO with credentials
            
        Returns:
            User entity if found, None otherwise
        """
        if dto.email:
            try:
                email = Email.create(dto.email)
                return await self.user_repository.get_by_email(email)
            except DomainValidationError:
                pass
        
        if dto.phone:
            try:
                phone = Phone.create(dto.phone)
                return await self.user_repository.get_by_phone(phone)
            except DomainValidationError:
                pass
        
        return None
    
    def _entity_to_auth_dto(self, user) -> AuthUserDTO:
        """
        Convert User entity to AuthUserDTO.
        
        Args:
            user: User entity
            
        Returns:
            AuthUserDTO
        """
        from datetime import datetime
        
        return AuthUserDTO(
            id=user.id,
            email=str(user.email) if user.email else None,
            phone=str(user.phone) if user.phone else None,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            supabase_id=user.supabase_id,
            last_login=datetime.utcnow()  # Would be updated in a real implementation
        ) 