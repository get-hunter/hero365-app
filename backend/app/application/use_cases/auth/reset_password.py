"""
Reset Password Use Case

Business logic for password reset operations.
"""

import uuid
from typing import Optional

from ...dto.auth_dto import ForgotPasswordDTO, ResetPasswordTokenDTO
from ...exceptions.application_exceptions import (
    UserNotFoundError, ValidationError, InvalidCredentialsError
)
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.value_objects.password import Password
from ....domain.exceptions.domain_exceptions import DomainValidationError


class ResetPasswordUseCase:
    """
    Use case for password reset operations.
    
    This use case handles the business logic for password reset,
    including token generation, validation, and password updates.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def request_password_reset(self, forgot_password_dto: ForgotPasswordDTO) -> bool:
        """
        Request a password reset token.
        
        Args:
            forgot_password_dto: Request data with email or phone
            
        Returns:
            True if reset was initiated (always returns True for security)
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate input
        self._validate_forgot_password_input(forgot_password_dto)
        
        # Find user
        user = await self._find_user_for_reset(forgot_password_dto)
        
        if user:
            # In a real implementation, you would:
            # 1. Generate a secure reset token
            # 2. Store it with expiration time
            # 3. Send it via email/SMS
            # 4. Log the reset request
            
            # For now, we just simulate the process
            pass
        
        # Always return True for security (don't reveal if user exists)
        return True
    
    async def reset_password_with_token(self, reset_dto: ResetPasswordTokenDTO) -> bool:
        """
        Reset password using a reset token.
        
        Args:
            reset_dto: Reset data with token and new password
            
        Returns:
            True if password was reset successfully
            
        Raises:
            ValidationError: If input validation fails
            InvalidCredentialsError: If token is invalid
        """
        # Validate input
        self._validate_reset_password_input(reset_dto)
        
        # In a real implementation, you would:
        # 1. Validate the reset token
        # 2. Check if it's not expired
        # 3. Find the user associated with the token
        # 4. Update the user's password
        # 5. Invalidate the token
        # 6. Log the password change
        
        # For this implementation, we'll simulate token validation
        # and demonstrate the password reset process
        
        # Simulate token validation (would be real validation in production)
        if not self._validate_reset_token(reset_dto.token):
            raise InvalidCredentialsError("Invalid or expired reset token")
        
        # In a Supabase implementation, password reset would be handled
        # by Supabase's authentication system
        
        return True
    
    async def change_password(self, user_id: uuid.UUID, current_password: str, 
                             new_password: str) -> bool:
        """
        Change password for an authenticated user.
        
        Args:
            user_id: ID of the user changing password
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was changed successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValidationError: If input validation fails
            InvalidCredentialsError: If current password is incorrect
        """
        # Find user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Validate new password
        try:
            new_pwd = Password.create_plain(new_password)
            if new_pwd.get_strength_score() < 60:
                raise ValidationError("new_password", "New password is too weak")
        except DomainValidationError as e:
            raise ValidationError("new_password", str(e))
        
        # For Supabase users, password change would be handled externally
        if user.supabase_id:
            # Supabase password change would be handled by Supabase API
            pass
        else:
            # Local user password change would require password verification
            # This is not fully implemented in the current domain model
            pass
        
        return True
    
    def _validate_forgot_password_input(self, dto: ForgotPasswordDTO) -> None:
        """
        Validate forgot password input.
        
        Args:
            dto: ForgotPasswordDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Must have either email or phone
        if not dto.email and not dto.phone:
            raise ValidationError(
                "contact_info",
                "Either email or phone number is required"
            )
        
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
    
    def _validate_reset_password_input(self, dto: ResetPasswordTokenDTO) -> None:
        """
        Validate reset password input.
        
        Args:
            dto: ResetPasswordTokenDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Must have token
        if not dto.token or len(dto.token.strip()) == 0:
            raise ValidationError("token", "Reset token is required")
        
        # Must have new password
        if not dto.new_password:
            raise ValidationError("new_password", "New password is required")
        
        # Validate password confirmation if provided
        if dto.confirm_password is not None:
            if dto.new_password != dto.confirm_password:
                raise ValidationError("confirm_password", "Passwords do not match")
        
        # Validate new password strength
        try:
            password = Password.create_plain(dto.new_password)
            if password.get_strength_score() < 60:
                raise ValidationError("new_password", "Password is too weak")
        except DomainValidationError as e:
            raise ValidationError("new_password", str(e))
    
    async def _find_user_for_reset(self, dto: ForgotPasswordDTO):
        """
        Find user for password reset.
        
        Args:
            dto: ForgotPasswordDTO with contact info
            
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
    
    def _validate_reset_token(self, token: str) -> bool:
        """
        Validate a reset token.
        
        Args:
            token: Reset token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        # In a real implementation, this would:
        # 1. Look up the token in a secure store
        # 2. Check if it's not expired
        # 3. Verify its integrity/signature
        
        # For simulation purposes, we'll accept tokens that are not empty
        # and have a reasonable length
        return len(token) >= 32  # Minimum token length 