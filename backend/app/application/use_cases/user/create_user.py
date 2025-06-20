"""
Create User Use Case

Business logic for creating new users.
"""

import uuid
from typing import Optional

from ...dto.user_dto import CreateUserDTO, UserDTO
from ...exceptions.application_exceptions import UserAlreadyExistsError, ValidationError
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.exceptions.domain_exceptions import DomainValidationError


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    This use case handles the business logic for user creation,
    including validation, uniqueness checks, and domain entity creation.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, create_user_dto: CreateUserDTO) -> UserDTO:
        """
        Execute the create user use case.
        
        Args:
            create_user_dto: Data for creating the user
            
        Returns:
            UserDTO containing the created user data
            
        Raises:
            ValidationError: If input validation fails
            UserAlreadyExistsError: If user already exists
            DomainValidationError: If domain rules are violated
        """
        # Validate input
        await self._validate_input(create_user_dto)
        
        # Check for existing users
        await self._check_uniqueness(create_user_dto)
        
        # Create domain objects
        email = self._create_email(create_user_dto.email)
        phone = self._create_phone(create_user_dto.phone)
        
        # Create user entity
        user = User(
            id=uuid.uuid4(),
            email=email,
            phone=phone,
            full_name=create_user_dto.full_name,
            is_active=True,
            is_superuser=create_user_dto.is_superuser,
            supabase_id=create_user_dto.supabase_id
        )
        
        # Save to repository
        created_user = await self.user_repository.create(user)
        
        # Convert to DTO
        return self._entity_to_dto(created_user)
    
    async def _validate_input(self, dto: CreateUserDTO) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: CreateUserDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Must have at least email or phone
        if not dto.email and not dto.phone:
            raise ValidationError(
                "contact_info", 
                "Either email or phone number is required"
            )
        
        # Validate full name if provided
        if dto.full_name is not None and len(dto.full_name.strip()) == 0:
            raise ValidationError("full_name", "Full name cannot be empty")
        
        # Validate password if provided (for non-Supabase users)
        if dto.password is not None:
            if len(dto.password) < 8:
                raise ValidationError("password", "Password must be at least 8 characters long")
            if len(dto.password) > 40:
                raise ValidationError("password", "Password must be at most 40 characters long")
    
    async def _check_uniqueness(self, dto: CreateUserDTO) -> None:
        """
        Check if user already exists.
        
        Args:
            dto: CreateUserDTO to check
            
        Raises:
            UserAlreadyExistsError: If user already exists
        """
        if dto.email:
            try:
                email = Email.create(dto.email)
                existing_user = await self.user_repository.get_by_email(email)
                if existing_user:
                    raise UserAlreadyExistsError(f"email:{dto.email}")
            except DomainValidationError as e:
                raise ValidationError("email", str(e))
        
        if dto.phone:
            try:
                phone = Phone.create(dto.phone)
                existing_user = await self.user_repository.get_by_phone(phone)
                if existing_user:
                    raise UserAlreadyExistsError(f"phone:{dto.phone}")
            except DomainValidationError as e:
                raise ValidationError("phone", str(e))
        
        if dto.supabase_id:
            existing_user = await self.user_repository.get_by_supabase_id(dto.supabase_id)
            if existing_user:
                raise UserAlreadyExistsError(f"supabase_id:{dto.supabase_id}")
    
    def _create_email(self, email_str: Optional[str]) -> Optional[Email]:
        """
        Create Email value object.
        
        Args:
            email_str: Email string
            
        Returns:
            Email value object or None
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email_str:
            return None
        
        try:
            return Email.create(email_str)
        except DomainValidationError as e:
            raise ValidationError("email", str(e))
    
    def _create_phone(self, phone_str: Optional[str]) -> Optional[Phone]:
        """
        Create Phone value object.
        
        Args:
            phone_str: Phone string
            
        Returns:
            Phone value object or None
            
        Raises:
            ValidationError: If phone format is invalid
        """
        if not phone_str:
            return None
        
        try:
            return Phone.create(phone_str)
        except DomainValidationError as e:
            raise ValidationError("phone", str(e))
    
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
    
    async def execute_oauth_registration(self, create_user_dto: CreateUserDTO) -> UserDTO:
        """
        Execute OAuth user registration without requiring current_user_id.
        
        This method is specifically for OAuth flows where users are created
        automatically during the authentication process.
        
        Args:
            create_user_dto: Data for creating the OAuth user
            
        Returns:
            UserDTO containing the created user data
            
        Raises:
            ValidationError: If input validation fails
            UserAlreadyExistsError: If user already exists
            DomainValidationError: If domain rules are violated
        """
        # Validate OAuth-specific input
        await self._validate_oauth_input(create_user_dto)
        
        # Check for existing users (with OAuth-specific logic)
        await self._check_oauth_uniqueness(create_user_dto)
        
        # Create domain objects
        email = self._create_email(create_user_dto.email)
        phone = self._create_phone(create_user_dto.phone)
        
        # Create user entity with OAuth defaults
        user = User(
            id=uuid.uuid4(),
            email=email,
            phone=phone,
            full_name=create_user_dto.full_name,
            is_active=create_user_dto.is_active,
            is_superuser=False,  # OAuth users are not superusers by default
            supabase_id=create_user_dto.supabase_id
        )
        
        # Save to repository
        created_user = await self.user_repository.create(user)
        
        # Convert to DTO
        return self._entity_to_dto(created_user)
    
    async def _validate_oauth_input(self, dto: CreateUserDTO) -> None:
        """
        Validate OAuth-specific input.
        
        Args:
            dto: CreateUserDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # For OAuth, email is typically required
        if not dto.email:
            raise ValidationError(
                "email",
                "Email is required for OAuth registration"
            )
        
        # Validate full name if provided
        if dto.full_name is not None and len(dto.full_name.strip()) == 0:
            raise ValidationError("full_name", "Full name cannot be empty")
    
    async def _check_oauth_uniqueness(self, dto: CreateUserDTO) -> None:
        """
        Check OAuth user uniqueness with lenient rules.
        
        For OAuth, we may want to link existing users instead of throwing errors.
        
        Args:
            dto: CreateUserDTO to check
            
        Raises:
            UserAlreadyExistsError: If user already exists and cannot be linked
        """
        if dto.email:
            try:
                email = Email.create(dto.email)
                existing_user = await self.user_repository.get_by_email(email)
                if existing_user:
                    # For OAuth, we might want to link accounts instead of failing
                    # For now, we'll still throw an error but with a more helpful message
                    raise UserAlreadyExistsError(
                        f"User with email {dto.email} already exists. "
                        f"Consider linking OAuth account to existing user."
                    )
            except DomainValidationError as e:
                raise ValidationError("email", str(e)) 