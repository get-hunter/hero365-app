"""
Register User Use Case

Business logic for user registration.
"""

import uuid
from typing import Optional

from ...dto.auth_dto import RegisterDTO, AuthUserDTO
from ...dto.user_dto import CreateUserDTO
from ...exceptions.application_exceptions import (
    UserAlreadyExistsError, ValidationError
)
from ..user.create_user import CreateUserUseCase
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.value_objects.password import Password
from ....domain.exceptions.domain_exceptions import DomainValidationError


class RegisterUserUseCase:
    """
    Use case for user registration.
    
    This use case handles the business logic for user registration,
    including validation, password confirmation, and account creation.
    """
    
    def __init__(self, create_user_use_case: CreateUserUseCase):
        self.create_user_use_case = create_user_use_case
    
    async def execute(self, register_dto: RegisterDTO) -> AuthUserDTO:
        """
        Execute the register user use case.
        
        Args:
            register_dto: Registration data
            
        Returns:
            AuthUserDTO containing the registered user data
            
        Raises:
            ValidationError: If input validation fails
            UserAlreadyExistsError: If user already exists
        """
        # Validate input
        self._validate_input(register_dto)
        
        # Create user DTO
        create_user_dto = self._to_create_user_dto(register_dto)
        
        # Create user using the create user use case
        user_dto = await self.create_user_use_case.execute(create_user_dto)
        
        # Convert to auth user DTO
        return self._to_auth_user_dto(user_dto)
    
    async def register_supabase_user(self, supabase_id: str, email: Optional[str] = None,
                                   phone: Optional[str] = None, full_name: Optional[str] = None) -> AuthUserDTO:
        """
        Register a user from Supabase authentication.
        
        Args:
            supabase_id: Supabase user ID
            email: User email
            phone: User phone
            full_name: User full name
            
        Returns:
            AuthUserDTO containing the registered user data
            
        Raises:
            ValidationError: If input validation fails
            UserAlreadyExistsError: If user already exists
        """
        # Validate that we have at least email or phone
        if not email and not phone:
            raise ValidationError(
                "contact_info",
                "Either email or phone number is required"
            )
        
        # Create user DTO for Supabase user
        create_user_dto = CreateUserDTO(
            email=email,
            phone=phone,
            full_name=full_name,
            is_superuser=False,
            supabase_id=supabase_id
        )
        
        # Create user
        user_dto = await self.create_user_use_case.execute(create_user_dto)
        
        # Convert to auth user DTO
        return self._to_auth_user_dto(user_dto)
    
    def _validate_input(self, dto: RegisterDTO) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: RegisterDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Must have either email or phone
        if not dto.email and not dto.phone:
            raise ValidationError(
                "contact_info", 
                "Either email or phone number is required"
            )
        
        # Must have password
        if not dto.password:
            raise ValidationError("password", "Password is required")
        
        # Validate password confirmation if provided
        if dto.confirm_password is not None:
            if dto.password != dto.confirm_password:
                raise ValidationError("confirm_password", "Passwords do not match")
        
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
        
        # Validate password strength
        try:
            password = Password.create_plain(dto.password)
            if password.get_strength_score() < 60:
                raise ValidationError("password", "Password is too weak")
        except DomainValidationError as e:
            raise ValidationError("password", str(e))
        
        # Validate full name if provided
        if dto.full_name is not None:
            if len(dto.full_name.strip()) == 0:
                raise ValidationError("full_name", "Full name cannot be empty")
            if len(dto.full_name) > 255:
                raise ValidationError("full_name", "Full name too long (max 255 characters)")
    
    def _to_create_user_dto(self, register_dto: RegisterDTO) -> CreateUserDTO:
        """
        Convert RegisterDTO to CreateUserDTO.
        
        Args:
            register_dto: Registration data
            
        Returns:
            CreateUserDTO
        """
        return CreateUserDTO(
            email=register_dto.email,
            phone=register_dto.phone,
            full_name=register_dto.full_name,
            password=register_dto.password,
            is_superuser=False  # New registrations are never superusers
        )
    
    def _to_auth_user_dto(self, user_dto) -> AuthUserDTO:
        """
        Convert UserDTO to AuthUserDTO.
        
        Args:
            user_dto: User data
            
        Returns:
            AuthUserDTO
        """
        from datetime import datetime
        
        return AuthUserDTO(
            id=user_dto.id,
            email=user_dto.email,
            phone=user_dto.phone,
            full_name=user_dto.full_name,
            is_active=user_dto.is_active,
            is_superuser=user_dto.is_superuser,
            supabase_id=user_dto.supabase_id,
            last_login=datetime.utcnow()
        ) 