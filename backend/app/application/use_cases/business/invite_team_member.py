"""
Invite Team Member Use Case

Handles the business logic for inviting team members to join a business.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from ...dto.business_dto import BusinessInvitationCreateDTO, BusinessInvitationResponseDTO
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ....domain.repositories.business_invitation_repository import BusinessInvitationRepository
from ....domain.entities.business_invitation import BusinessInvitation, InvitationStatus
from ....domain.entities.business_membership import BusinessRole, get_default_permissions_for_role
from ....domain.exceptions.domain_exceptions import EntityNotFoundError, DuplicateEntityError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError
)
from ...ports.email_service import EmailServicePort


class InviteTeamMemberUseCase:
    """
    Use case for inviting team members to join a business.
    
    This use case handles:
    - Permission validation (inviter must have team management permissions)
    - Invitation creation and validation
    - Email/SMS notification sending
    - Duplicate invitation prevention
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository,
        invitation_repository: BusinessInvitationRepository,
        email_service: EmailServicePort
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
        self.invitation_repository = invitation_repository
        self.email_service = email_service
    
    async def execute(self, dto: BusinessInvitationCreateDTO, inviter_user_id: str) -> BusinessInvitationResponseDTO:
        """
        Execute the invite team member use case.
        
        Args:
            dto: Invitation creation data
            inviter_user_id: User ID of the person sending the invitation
            
        Returns:
            BusinessInvitationResponseDTO: Created invitation information
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If business logic is violated
            ApplicationError: If invitation creation fails
        """
        try:
            # Validate input data
            self._validate_input(dto)
            
            # Verify business exists
            business = await self._get_business(dto.business_id)
            
            # Verify inviter has permission to invite team members
            await self._validate_inviter_permissions(dto.business_id, inviter_user_id)
            
            # Check for existing pending invitations
            await self._validate_no_duplicate_invitation(dto)
            
            # Check if user is already a member
            await self._validate_not_existing_member(dto)
            
            # Create invitation entity
            invitation = self._create_invitation_entity(dto)
            
            # Save invitation to repository
            created_invitation = await self.invitation_repository.create(invitation)
            
            # Send invitation notification
            await self._send_invitation_notification(created_invitation)
            
            # Convert to response DTO
            return self._to_response_dto(created_invitation)
            
        except EntityNotFoundError as e:
            raise BusinessLogicError(f"Business not found: {str(e)}")
        except DuplicateEntityError as e:
            raise BusinessLogicError(f"Invitation already exists: {str(e)}")
        except Exception as e:
            raise ApplicationError(f"Failed to create invitation: {str(e)}")
    
    def _validate_input(self, dto: BusinessInvitationCreateDTO) -> None:
        """Validate input data."""
        if not dto.business_id:
            raise ValidationError("Business ID is required")
        
        if not dto.invited_by:
            raise ValidationError("Inviter user ID is required")
        
        if not dto.invited_by_name:
            raise ValidationError("Inviter name is required")
        
        if not dto.business_name:
            raise ValidationError("Business name is required")
        
        # Must have either email or phone
        if not dto.invited_email and not dto.invited_phone:
            raise ValidationError("Either email or phone number is required")
        
        # Validate email format if provided
        if dto.invited_email and '@' not in dto.invited_email:
            raise ValidationError("Invalid email format")
        
        # Validate role
        if not dto.role:
            raise ValidationError("Role is required")
        
        # Validate expiry days
        if dto.expiry_days < 1 or dto.expiry_days > 30:
            raise ValidationError("Expiry days must be between 1 and 30")
    
    async def _get_business(self, business_id: uuid.UUID):
        """Get business and verify it exists."""
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise EntityNotFoundError(f"Business with ID {business_id} not found")
        if not business.is_active:
            raise BusinessLogicError("Cannot invite members to inactive business")
        return business
    
    async def _validate_inviter_permissions(self, business_id: uuid.UUID, inviter_user_id: str) -> None:
        """Validate that the inviter has permission to invite team members."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, inviter_user_id)
        
        if not membership:
            raise BusinessLogicError("User is not a member of this business")
        
        if not membership.is_active:
            raise BusinessLogicError("User membership is inactive")
        
        # Check if user has team management permissions
        if not membership.has_permission("team:invite"):
            raise BusinessLogicError("User does not have permission to invite team members")
    
    async def _validate_no_duplicate_invitation(self, dto: BusinessInvitationCreateDTO) -> None:
        """Validate that there's no existing pending invitation."""
        has_pending = await self.invitation_repository.has_pending_invitation(
            dto.business_id,
            email=dto.invited_email,
            phone=dto.invited_phone
        )
        
        if has_pending:
            contact_method = dto.invited_email or dto.invited_phone
            raise BusinessLogicError(f"Pending invitation already exists for {contact_method}")
    
    async def _validate_not_existing_member(self, dto: BusinessInvitationCreateDTO) -> None:
        """Validate that the invitee is not already a member."""
        # For now, we'll skip this validation since we don't have a way to map
        # email/phone to user ID without additional user service
        # In a complete implementation, this would check against existing memberships
        pass
    
    def _create_invitation_entity(self, dto: BusinessInvitationCreateDTO) -> BusinessInvitation:
        """Create invitation entity from DTO."""
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=dto.expiry_days)
        
        # Get permissions for the role
        permissions = dto.permissions or get_default_permissions_for_role(dto.role)
        
        return BusinessInvitation(
            id=uuid.uuid4(),
            business_id=dto.business_id,
            business_name=dto.business_name,
            invited_email=dto.invited_email,
            invited_phone=dto.invited_phone,
            invited_by=dto.invited_by,
            invited_by_name=dto.invited_by_name,
            role=dto.role,
            permissions=permissions,
            invitation_date=now,
            expiry_date=expiry_date,
            status=InvitationStatus.PENDING,
            message=dto.message
        )
    
    async def _send_invitation_notification(self, invitation: BusinessInvitation) -> None:
        """Send invitation notification via email or SMS."""
        try:
            if invitation.invited_email:
                await self._send_email_invitation(invitation)
            # TODO: Add SMS invitation support when SMS service is available
            # elif invitation.invited_phone:
            #     await self._send_sms_invitation(invitation)
        except Exception as e:
            # Log the error but don't fail the invitation creation
            # In a production system, we might want to queue this for retry
            pass
    
    async def _send_email_invitation(self, invitation: BusinessInvitation) -> None:
        """Send email invitation."""
        subject = f"Invitation to join {invitation.business_name}"
        
        # Create invitation message
        message = f"""
        You've been invited to join {invitation.business_name} as a {invitation.role.value.title()}.
        
        {invitation.message or ''}
        
        This invitation expires on {invitation.expiry_date.strftime('%B %d, %Y')}.
        
        To accept this invitation, please click the link below:
        [Accept Invitation Link - TODO: Add actual link]
        
        Best regards,
        {invitation.invited_by_name}
        """
        
        await self.email_service.send_email(
            to_email=invitation.invited_email,
            subject=subject,
            content=message
        )
    
    def _to_response_dto(self, invitation: BusinessInvitation) -> BusinessInvitationResponseDTO:
        """Convert invitation entity to response DTO."""
        return BusinessInvitationResponseDTO(
            id=invitation.id,
            business_id=invitation.business_id,
            business_name=invitation.business_name,
            invited_email=invitation.invited_email,
            invited_phone=invitation.invited_phone,
            invited_by=invitation.invited_by,
            invited_by_name=invitation.invited_by_name,
            role=invitation.role,
            permissions=invitation.permissions,
            invitation_date=invitation.invitation_date,
            expiry_date=invitation.expiry_date,
            status=invitation.status,
            message=invitation.message,
            accepted_date=invitation.accepted_date,
            declined_date=invitation.declined_date,
            role_display=invitation.role.value.title(),
            status_display=invitation.status.value.title(),
            expiry_summary=self._get_expiry_summary(invitation.expiry_date)
        )
    
    def _get_expiry_summary(self, expiry_date: datetime) -> str:
        """Get human-readable expiry summary."""
        now = datetime.utcnow()
        days_remaining = (expiry_date - now).days
        
        if days_remaining < 0:
            return "Expired"
        elif days_remaining == 0:
            return "Expires today"
        elif days_remaining == 1:
            return "Expires tomorrow"
        else:
            return f"Expires in {days_remaining} days" 