"""
Business Management Controller

Handles business management API endpoints with proper dependency injection and use case delegation.
"""

import uuid
from typing import List
from fastapi import HTTPException, status

from ..schemas.business_schemas import (
    BusinessCreateRequest, BusinessUpdateRequest, BusinessResponse,
    BusinessSummaryResponse, UserBusinessSummaryResponse,
    BusinessInvitationCreateRequest, BusinessInvitationResponse,
    BusinessInvitationAcceptRequest, BusinessMembershipResponse,
    BusinessMembershipUpdateRequest, BusinessDetailResponse,
    BusinessOnboardingUpdateRequest, BusinessStatsResponse,
    BusinessPermissionCheckRequest, BusinessPermissionCheckResponse,
    BusinessSearchRequest
)
from ...application.use_cases.business.create_business import CreateBusinessUseCase
from ...application.use_cases.business.invite_team_member import InviteTeamMemberUseCase
from ...application.use_cases.business.accept_invitation import AcceptInvitationUseCase
from ...application.use_cases.business.get_user_businesses import GetUserBusinessesUseCase
from ...application.use_cases.business.get_business_detail import GetBusinessDetailUseCase
from ...application.use_cases.business.update_business import UpdateBusinessUseCase
from ...application.use_cases.business.manage_team_member import ManageTeamMemberUseCase
from ...application.use_cases.business.manage_invitations import ManageInvitationsUseCase
from ...application.dto.business_dto import (
    BusinessCreateDTO, BusinessUpdateDTO, BusinessInvitationCreateDTO,
    BusinessInvitationAcceptDTO, BusinessMembershipUpdateDTO,
    BusinessOnboardingUpdateDTO, BusinessSearchDTO
)
from ...domain.entities.business import CompanySize, ReferralSource
from ...domain.entities.business_membership import BusinessRole
from ...application.exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError
)


class BusinessController:
    """
    Business management controller with clean architecture.
    
    This controller delegates business logic to use cases and handles
    HTTP-specific concerns like status codes and error responses.
    """
    
    def __init__(
        self,
        create_business_use_case: CreateBusinessUseCase,
        invite_team_member_use_case: InviteTeamMemberUseCase,
        accept_invitation_use_case: AcceptInvitationUseCase,
        get_user_businesses_use_case: GetUserBusinessesUseCase,
        get_business_detail_use_case: GetBusinessDetailUseCase,
        update_business_use_case: UpdateBusinessUseCase,
        manage_team_member_use_case: ManageTeamMemberUseCase,
        manage_invitations_use_case: ManageInvitationsUseCase
    ):
        self.create_business_use_case = create_business_use_case
        self.invite_team_member_use_case = invite_team_member_use_case
        self.accept_invitation_use_case = accept_invitation_use_case
        self.get_user_businesses_use_case = get_user_businesses_use_case
        self.get_business_detail_use_case = get_business_detail_use_case
        self.update_business_use_case = update_business_use_case
        self.manage_team_member_use_case = manage_team_member_use_case
        self.manage_invitations_use_case = manage_invitations_use_case
    
    async def create_business(self, request: BusinessCreateRequest, current_user_id: str) -> BusinessResponse:
        """Create a new business."""
        try:
            # Convert request to DTO
            dto = BusinessCreateDTO(
                name=request.name,
                industry=request.industry,
                company_size=CompanySize(request.company_size.value),
                owner_id=current_user_id,
                custom_industry=request.custom_industry,
                description=request.description,
                phone_number=request.phone_number,
                business_address=request.business_address,
                website=request.website,
                business_email=request.business_email,
                selected_features=request.selected_features,
                primary_goals=request.primary_goals,
                referral_source=ReferralSource(request.referral_source.value) if request.referral_source else None,
                timezone=request.timezone
            )
            
            # Execute use case
            result = await self.create_business_use_case.execute(dto)
            
            # Convert to response schema
            return self._business_dto_to_response(result)
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_user_businesses(self, current_user_id: str, skip: int = 0, limit: int = 100) -> List[UserBusinessSummaryResponse]:
        """Get all businesses for the current user."""
        try:
            # Execute use case
            results = await self.get_user_businesses_use_case.execute(current_user_id, skip, limit)
            
            # Convert to response schemas
            return [self._user_business_dto_to_response(result) for result in results]
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def invite_team_member(
        self, 
        business_id: uuid.UUID, 
        request: BusinessInvitationCreateRequest, 
        current_user_id: str,
        current_user_name: str
    ) -> BusinessInvitationResponse:
        """Invite a team member to join a business."""
        try:
            # Convert request to DTO
            dto = BusinessInvitationCreateDTO(
                business_id=business_id,
                business_name="",  # Will be filled by use case
                invited_email=request.invited_email,
                invited_phone=request.invited_phone,
                invited_by=current_user_id,
                invited_by_name=current_user_name,
                role=BusinessRole(request.role.value),
                message=request.message,
                permissions=request.permissions,
                department_id=request.department_id,
                expiry_days=request.expiry_days
            )
            
            # Execute use case
            result = await self.invite_team_member_use_case.execute(dto, current_user_id)
            
            # Convert to response schema
            return self._invitation_dto_to_response(result)
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def accept_invitation(self, request: BusinessInvitationAcceptRequest, current_user_id: str) -> BusinessMembershipResponse:
        """Accept a business invitation."""
        try:
            # Convert request to DTO
            dto = BusinessInvitationAcceptDTO(
                invitation_id=request.invitation_id,
                user_id=current_user_id
            )
            
            # Execute use case
            result = await self.accept_invitation_use_case.execute(dto)
            
            # Convert to response schema
            return self._membership_dto_to_response(result)
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    # Helper methods for DTO to response conversion
    def _business_dto_to_response(self, dto) -> BusinessResponse:
        """Convert business DTO to response schema."""
        return BusinessResponse(
            id=dto.id,
            name=dto.name,
            industry=dto.industry,
            company_size=dto.company_size.value,
            owner_id=dto.owner_id,
            custom_industry=dto.custom_industry,
            description=dto.description,
            phone_number=dto.phone_number,
            business_address=dto.business_address,
            website=dto.website,
            logo_url=dto.logo_url,
            business_email=dto.business_email,
            business_registration_number=dto.business_registration_number,
            tax_id=dto.tax_id,
            business_license=dto.business_license,
            insurance_number=dto.insurance_number,
            selected_features=dto.selected_features,
            primary_goals=dto.primary_goals,
            referral_source=dto.referral_source.value if dto.referral_source else None,
            onboarding_completed=dto.onboarding_completed,
            onboarding_completed_date=dto.onboarding_completed_date,
            timezone=dto.timezone,
            currency=dto.currency,
            business_hours=dto.business_hours,
            is_active=dto.is_active,
            max_team_members=dto.max_team_members,
            subscription_tier=dto.subscription_tier,
            enabled_features=dto.enabled_features,
            created_date=dto.created_date,
            last_modified=dto.last_modified
        )
    
    def _user_business_dto_to_response(self, dto) -> UserBusinessSummaryResponse:
        """Convert user business DTO to response schema."""
        return UserBusinessSummaryResponse(
            business=BusinessSummaryResponse(
                id=dto.business.id,
                name=dto.business.name,
                industry=dto.business.industry,
                company_size=dto.business.company_size.value,
                is_active=dto.business.is_active,
                created_date=dto.business.created_date,
                team_member_count=dto.business.team_member_count,
                onboarding_completed=dto.business.onboarding_completed
            ),
            membership=self._membership_dto_to_response(dto.membership),
            is_owner=dto.is_owner,
            pending_invitations_count=dto.pending_invitations_count
        )
    
    def _membership_dto_to_response(self, dto) -> BusinessMembershipResponse:
        """Convert membership DTO to response schema."""
        return BusinessMembershipResponse(
            id=dto.id,
            business_id=dto.business_id,
            user_id=dto.user_id,
            role=dto.role.value,
            permissions=dto.permissions,
            joined_date=dto.joined_date,
            invited_date=dto.invited_date,
            invited_by=dto.invited_by,
            is_active=dto.is_active,
            department_id=dto.department_id,
            job_title=dto.job_title,
            role_display=dto.role_display
        )
    
    def _invitation_dto_to_response(self, dto) -> BusinessInvitationResponse:
        """Convert invitation DTO to response schema."""
        return BusinessInvitationResponse(
            id=dto.id,
            business_id=dto.business_id,
            business_name=dto.business_name,
            invited_email=dto.invited_email,
            invited_phone=dto.invited_phone,
            invited_by=dto.invited_by,
            invited_by_name=dto.invited_by_name,
            role=dto.role.value,
            permissions=dto.permissions,
            invitation_date=dto.invitation_date,
            expiry_date=dto.expiry_date,
            status=dto.status.value,
            message=dto.message,
            accepted_date=dto.accepted_date,
            declined_date=dto.declined_date,
            role_display=dto.role_display,
            status_display=dto.status_display,
            expiry_summary=dto.expiry_summary
        )
    
    async def get_business_detail(self, business_id: uuid.UUID, current_user_id: str) -> BusinessDetailResponse:
        """Get detailed business information."""
        try:
            result = await self.get_business_detail_use_case.execute(business_id, current_user_id)
            
            return BusinessDetailResponse(
                business=self._business_dto_to_response(result.business),
                user_membership=self._membership_dto_to_response(result.user_membership),
                team_members=[self._membership_dto_to_response(member) for member in result.team_members],
                pending_invitations=[self._invitation_dto_to_response(inv) for inv in result.pending_invitations],
                total_members=result.total_members,
                owner_membership=self._membership_dto_to_response(result.owner_membership)
            )
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_business(
        self, 
        business_id: uuid.UUID, 
        request: BusinessUpdateRequest, 
        current_user_id: str
    ) -> BusinessResponse:
        """Update business information."""
        try:
            # Convert request to DTO
            dto = BusinessUpdateDTO(
                name=request.name,
                description=request.description,
                industry=request.industry,
                custom_industry=request.custom_industry,
                phone_number=request.phone_number,
                business_address=request.business_address,
                website=request.website,
                business_email=request.business_email,
                logo_url=request.logo_url,
                business_registration_number=request.business_registration_number,
                tax_id=request.tax_id,
                business_license=request.business_license,
                insurance_number=request.insurance_number,
                timezone=request.timezone,
                currency=request.currency,
                business_hours=request.business_hours,
                max_team_members=request.max_team_members,
                subscription_tier=request.subscription_tier,
                enabled_features=request.enabled_features
            )
            
            result = await self.update_business_use_case.execute(business_id, dto, current_user_id)
            
            return self._business_dto_to_response(result)
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_member_role(
        self,
        business_id: uuid.UUID,
        membership_id: uuid.UUID,
        request: BusinessMembershipUpdateRequest,
        current_user_id: str
    ) -> BusinessMembershipResponse:
        """Update team member role and permissions."""
        try:
            # Convert request to DTO
            dto = BusinessMembershipUpdateDTO(
                role=BusinessRole(request.role.value) if request.role else None,
                permissions=request.permissions,
                department_id=request.department_id,
                job_title=request.job_title
            )
            
            result = await self.manage_team_member_use_case.update_member_role(
                business_id, membership_id, dto, current_user_id
            )
            
            return self._membership_dto_to_response(result)
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def remove_team_member(
        self,
        business_id: uuid.UUID,
        membership_id: uuid.UUID,
        current_user_id: str
    ) -> bool:
        """Remove team member from business."""
        try:
            return await self.manage_team_member_use_case.remove_team_member(
                business_id, membership_id, current_user_id
            )
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_business_invitations(
        self,
        business_id: uuid.UUID,
        current_user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[BusinessInvitationResponse]:
        """Get business invitations."""
        try:
            results = await self.manage_invitations_use_case.get_business_invitations(
                business_id, current_user_id, skip, limit
            )
            
            return [self._invitation_dto_to_response(result) for result in results]
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def cancel_invitation(self, invitation_id: uuid.UUID, current_user_id: str) -> bool:
        """Cancel a pending invitation."""
        try:
            return await self.manage_invitations_use_case.cancel_invitation(
                invitation_id, current_user_id
            )
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def decline_invitation(self, invitation_id: uuid.UUID, current_user_id: str) -> bool:
        """Decline a business invitation."""
        try:
            result = await self.manage_invitations_use_case.decline_invitation(invitation_id, current_user_id)
            return result
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except BusinessLogicError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_user_invitations(self, current_user: dict) -> List[BusinessInvitationResponse]:
        """Get all invitations for the current user."""
        try:
            # Extract email and phone from user data
            user_email = current_user.get("email")
            user_phone = current_user.get("phone")
            
            result = await self.manage_invitations_use_case.get_user_invitations(
                user_email=user_email,
                user_phone=user_phone
            )
            
            return [self._invitation_dto_to_response(invitation) for invitation in result]
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            ) 