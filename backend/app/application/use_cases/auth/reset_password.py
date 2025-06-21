"""
Reset Password Use Case

Business logic for password reset operations with Supabase Auth.
"""

import uuid
from typing import Optional

from ...dto.auth_dto import ForgotPasswordDTO, ResetPasswordTokenDTO
from ...exceptions.application_exceptions import (
    UserNotFoundError, ValidationError, InvalidCredentialsError
)


class ResetPasswordUseCase:
    """
    Use case for password reset operations with Supabase Auth.
    
    This use case handles password reset logic directly with Supabase,
    without needing local user storage.
    """
    
    def __init__(self):
        # No dependencies needed for Supabase-only password reset
        pass
    
    async def request_password_reset(self, forgot_password_dto: ForgotPasswordDTO) -> bool:
        """
        Request a password reset token.
        
        Note: In Supabase-only architecture, password reset is handled
        directly by Supabase Auth. This use case may not be needed in
        most scenarios since password reset happens at the client level.
        
        Args:
            forgot_password_dto: Request data with email or phone
            
        Returns:
            True if reset was initiated (always returns True for security)
            
        Raises:
            ValidationError: Password reset should be handled by Supabase
        """
        raise ValidationError(
            "password_reset",
            "Password reset is handled directly by Supabase Auth. "
            "Use the Supabase client SDK for password reset."
        )
    
    async def reset_password_with_token(self, reset_dto: ResetPasswordTokenDTO) -> bool:
        """
        Reset password using a reset token.
        
        Note: In Supabase-only architecture, password reset is handled
        directly by Supabase Auth.
        
        Args:
            reset_dto: Reset data with token and new password
            
        Returns:
            True if password was reset successfully
            
        Raises:
            ValidationError: Password reset should be handled by Supabase
        """
        raise ValidationError(
            "password_reset",
            "Password reset is handled directly by Supabase Auth. "
            "Use the Supabase client SDK for password reset."
        )
    
    async def change_password(self, user_id: uuid.UUID, current_password: str, 
                             new_password: str) -> bool:
        """
        Change password for an authenticated user.
        
        Note: In Supabase-only architecture, password change is handled
        directly by Supabase Auth.
        
        Args:
            user_id: ID of the user changing password
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValidationError: Password change should be handled by Supabase
        """
        raise ValidationError(
            "password_change",
            "Password change is handled directly by Supabase Auth. "
            "Use the Supabase client SDK for password change."
        ) 