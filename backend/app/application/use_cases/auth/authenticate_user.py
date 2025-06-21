"""
Authenticate User Use Case

Business logic for user authentication with Supabase Auth.
"""

from typing import Optional

from ...dto.auth_dto import LoginDTO, AuthTokenDTO, AuthUserDTO
from ...exceptions.application_exceptions import (
    AuthenticationFailedException, InvalidCredentialsError, AccountInactiveError,
    UserNotFoundError, ValidationError
)


class AuthenticateUserUseCase:
    """
    Use case for authenticating users with Supabase Auth.
    
    This use case handles authentication logic directly with Supabase,
    without needing local user storage.
    """
    
    def __init__(self):
        # No dependencies needed for Supabase-only authentication
        pass
    
    async def execute(self, login_dto: LoginDTO) -> AuthUserDTO:
        """
        Execute the authenticate user use case.
        
        Note: In Supabase-only architecture, authentication is handled
        directly by Supabase Auth. This use case may not be needed in
        most scenarios since authentication happens at the API gateway level.
        
        Args:
            login_dto: Login credentials
            
        Returns:
            AuthUserDTO containing authenticated user data
            
        Raises:
            AuthenticationFailedException: Authentication should be handled by Supabase
        """
        raise AuthenticationFailedException(
            "Authentication is handled directly by Supabase Auth. "
            "Use the Supabase client SDK for authentication."
        )
    
    def create_auth_dto_from_supabase_user(self, supabase_user_data: dict) -> AuthUserDTO:
        """
        Create AuthUserDTO from Supabase user data.
        
        Args:
            supabase_user_data: User data from Supabase Auth
            
        Returns:
            AuthUserDTO containing user data
        """
        from datetime import datetime
        
        return AuthUserDTO(
            id=supabase_user_data.get("id"),
            email=supabase_user_data.get("email"),
            phone=supabase_user_data.get("phone"),
            full_name=supabase_user_data.get("user_metadata", {}).get("full_name"),
            is_active=True,  # Supabase users are active by default
            is_superuser=False,  # Determined by app-level logic
            supabase_id=supabase_user_data.get("id"),
            last_login=datetime.utcnow()
        ) 