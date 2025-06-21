"""
Register User Use Case

Business logic for user registration with Supabase Auth.
"""

import uuid
from typing import Optional

from ...dto.auth_dto import RegisterDTO, AuthUserDTO
from ...exceptions.application_exceptions import (
    UserAlreadyExistsError, ValidationError
)


class RegisterUserUseCase:
    """
    Use case for user registration with Supabase Auth.
    
    This use case handles registration logic directly with Supabase,
    without needing local user storage.
    """
    
    def __init__(self):
        # No dependencies needed for Supabase-only registration
        pass
    
    async def execute(self, register_dto: RegisterDTO) -> AuthUserDTO:
        """
        Execute the register user use case.
        
        Note: In Supabase-only architecture, registration is handled
        directly by Supabase Auth. This use case may not be needed in
        most scenarios since registration happens at the client level.
        
        Args:
            register_dto: Registration data
            
        Returns:
            AuthUserDTO containing the registered user data
            
        Raises:
            ValidationError: Registration should be handled by Supabase
        """
        raise ValidationError(
            "registration",
            "Registration is handled directly by Supabase Auth. "
            "Use the Supabase client SDK for registration."
        )
    
    def create_auth_dto_from_supabase_user(self, supabase_user_data: dict) -> AuthUserDTO:
        """
        Create AuthUserDTO from Supabase user data after registration.
        
        Args:
            supabase_user_data: User data from Supabase Auth
            
        Returns:
            AuthUserDTO containing the registered user data
        """
        from datetime import datetime
        
        return AuthUserDTO(
            id=supabase_user_data.get("id"),
            email=supabase_user_data.get("email"),
            phone=supabase_user_data.get("phone"),
            full_name=supabase_user_data.get("user_metadata", {}).get("full_name"),
            is_active=True,  # Supabase users are active by default
            is_superuser=False,  # New registrations are never superusers
            supabase_id=supabase_user_data.get("id"),
            last_login=datetime.utcnow()
        ) 