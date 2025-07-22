"""
Change Estimate Status Use Case

Handles changing estimate status with comprehensive business rules validation.
"""

import uuid
import logging
from typing import Optional

from app.domain.entities.estimate import Estimate
from app.domain.entities.estimate_enums.enums import EstimateStatus
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError, DomainValidationError
from app.application.dto.estimate_dto import EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError, NotFoundError
)

logger = logging.getLogger(__name__)


class ChangeEstimateStatusUseCase:
    """Use case for changing estimate status with business validation."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID,
        new_status: EstimateStatus,
        business_id: uuid.UUID,
        user_id: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> EstimateDTO:
        """
        Execute the change estimate status use case.
        
        Args:
            estimate_id: ID of the estimate to update
            new_status: New status to set
            business_id: Business ID for permission validation
            user_id: ID of the user making the change
            reason: Optional reason for the status change
            notes: Optional additional notes
            
        Returns:
            EstimateDTO of the updated estimate
            
        Raises:
            NotFoundError: If estimate doesn't exist
            ValidationError: If status change is invalid
            ApplicationError: If update fails
        """
        try:
            # Ensure new_status is an EstimateStatus enum
            if isinstance(new_status, str):
                parsed_status = EstimateStatus.parse_from_string(new_status)
                if not parsed_status:
                    raise AppValidationError(f"Invalid status '{new_status}'. Valid options are: draft, sent, viewed, approved, rejected, cancelled, converted, expired")
                new_status = parsed_status
            elif not isinstance(new_status, EstimateStatus):
                raise AppValidationError(f"new_status must be EstimateStatus enum or string, got {type(new_status)}")
            
            logger.info(f"Changing estimate {estimate_id} status to {new_status.value}")
            
            # Retrieve and validate the estimate
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Validate the status transition
            self._validate_status_transition(estimate, new_status)
            
            # Apply the status change with appropriate method
            await self._apply_status_change(estimate, new_status, user_id, reason, notes)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            # Convert to DTO and return
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully changed estimate {estimate.estimate_number} status to {new_status.value}")
            
            return result_dto
            
        except (NotFoundError, BusinessRuleViolationError, DomainValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error changing estimate status: {e}")
            raise ApplicationError(f"Failed to change estimate status: {str(e)}")
    
    async def send_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        client_email: Optional[str] = None
    ) -> EstimateDTO:
        """
        Send estimate to client (changes status to SENT).
        
        Args:
            estimate_id: ID of the estimate to send
            business_id: Business ID for validation
            user_id: User sending the estimate
            client_email: Optional client email override
            
        Returns:
            EstimateDTO of the sent estimate
        """
        try:
            logger.info(f"Sending estimate {estimate_id} to client")
            
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Update client email if provided
            if client_email:
                estimate.client_email = client_email
            
            # Send the estimate (this validates requirements and changes status)
            estimate.send_estimate(user_id)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            # TODO: Trigger email sending notification
            await self._trigger_email_notification(updated_estimate)
            
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully sent estimate {estimate.estimate_number}")
            
            return result_dto
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Cannot send estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error sending estimate: {e}")
            raise ApplicationError(f"Failed to send estimate: {str(e)}")
    
    async def approve_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        approval_notes: Optional[str] = None
    ) -> EstimateDTO:
        """
        Approve estimate (changes status to APPROVED).
        
        Args:
            estimate_id: ID of the estimate to approve
            business_id: Business ID for validation
            user_id: User approving the estimate
            approval_notes: Optional approval notes
            
        Returns:
            EstimateDTO of the approved estimate
        """
        try:
            logger.info(f"Approving estimate {estimate_id}")
            
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Approve the estimate
            estimate.approve_estimate(user_id, approval_notes)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully approved estimate {estimate.estimate_number}")
            
            return result_dto
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Cannot approve estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error approving estimate: {e}")
            raise ApplicationError(f"Failed to approve estimate: {str(e)}")
    
    async def reject_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        rejection_reason: Optional[str] = None
    ) -> EstimateDTO:
        """
        Reject estimate (changes status to REJECTED).
        
        Args:
            estimate_id: ID of the estimate to reject
            business_id: Business ID for validation
            user_id: User rejecting the estimate
            rejection_reason: Optional rejection reason
            
        Returns:
            EstimateDTO of the rejected estimate
        """
        try:
            logger.info(f"Rejecting estimate {estimate_id}")
            
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Reject the estimate
            estimate.reject_estimate(user_id, rejection_reason)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully rejected estimate {estimate.estimate_number}")
            
            return result_dto
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Cannot reject estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error rejecting estimate: {e}")
            raise ApplicationError(f"Failed to reject estimate: {str(e)}")
    
    async def cancel_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        cancellation_reason: Optional[str] = None
    ) -> EstimateDTO:
        """
        Cancel estimate (changes status to CANCELLED).
        
        Args:
            estimate_id: ID of the estimate to cancel
            business_id: Business ID for validation
            user_id: User cancelling the estimate
            cancellation_reason: Optional cancellation reason
            
        Returns:
            EstimateDTO of the cancelled estimate
        """
        try:
            logger.info(f"Cancelling estimate {estimate_id}")
            
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Cancel the estimate
            estimate.cancel_estimate(user_id, cancellation_reason)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully cancelled estimate {estimate.estimate_number}")
            
            return result_dto
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Cannot cancel estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error cancelling estimate: {e}")
            raise ApplicationError(f"Failed to cancel estimate: {str(e)}")
    
    async def mark_as_converted(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        invoice_id: Optional[uuid.UUID] = None
    ) -> EstimateDTO:
        """
        Mark estimate as converted to invoice.
        
        Args:
            estimate_id: ID of the estimate to mark as converted
            business_id: Business ID for validation
            user_id: User performing the conversion
            invoice_id: Optional ID of the created invoice
            
        Returns:
            EstimateDTO of the converted estimate
        """
        try:
            logger.info(f"Marking estimate {estimate_id} as converted")
            
            estimate = await self._get_and_validate_estimate(estimate_id, business_id, user_id)
            
            # Mark as converted
            estimate.mark_as_converted(user_id, invoice_id)
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            result_dto = EstimateDTO.from_entity(updated_estimate)
            
            logger.info(f"Successfully marked estimate {estimate.estimate_number} as converted")
            
            return result_dto
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Cannot mark estimate as converted: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error marking estimate as converted: {e}")
            raise ApplicationError(f"Failed to mark estimate as converted: {str(e)}")
    
    async def _get_and_validate_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str
    ) -> Estimate:
        """Get estimate and validate permissions."""
        estimate = await self.estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise NotFoundError(f"Estimate with ID {estimate_id} not found")
        
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError(
                f"Estimate does not belong to business {business_id}"
            )
        
        # TODO: Add more granular permission checking
        logger.debug(f"Estimate {estimate_id} validated for user {user_id}")
        
        return estimate
    
    def _validate_status_transition(
        self,
        estimate: Estimate,
        new_status: EstimateStatus
    ) -> None:
        """Validate that the status transition is allowed."""
        current_status = estimate.status
        
        # Define allowed transitions
        allowed_transitions = {
            EstimateStatus.DRAFT: [EstimateStatus.SENT, EstimateStatus.CANCELLED],
            EstimateStatus.SENT: [EstimateStatus.VIEWED, EstimateStatus.APPROVED, EstimateStatus.REJECTED, EstimateStatus.CANCELLED, EstimateStatus.EXPIRED],
            EstimateStatus.VIEWED: [EstimateStatus.APPROVED, EstimateStatus.REJECTED, EstimateStatus.CANCELLED, EstimateStatus.EXPIRED],
            EstimateStatus.APPROVED: [EstimateStatus.CONVERTED, EstimateStatus.CANCELLED],
            EstimateStatus.REJECTED: [],
            EstimateStatus.CANCELLED: [],
            EstimateStatus.CONVERTED: [],
            EstimateStatus.EXPIRED: [EstimateStatus.SENT, EstimateStatus.CANCELLED]
        }
        
        if current_status not in allowed_transitions:
            raise BusinessRuleViolationError(f"Invalid current status: {current_status.value}")
        
        if new_status not in allowed_transitions[current_status]:
            raise BusinessRuleViolationError(
                f"Cannot change status from {current_status.value} to {new_status.value}"
            )
    
    async def _apply_status_change(
        self,
        estimate: Estimate,
        new_status: EstimateStatus,
        user_id: str,
        reason: Optional[str],
        notes: Optional[str]
    ) -> None:
        """Apply the status change using appropriate domain method."""
        if new_status == EstimateStatus.SENT:
            estimate.send_estimate(user_id)
        elif new_status == EstimateStatus.VIEWED:
            estimate.mark_as_viewed(user_id)
        elif new_status == EstimateStatus.APPROVED:
            estimate.approve_estimate(user_id, notes)
        elif new_status == EstimateStatus.REJECTED:
            estimate.reject_estimate(user_id, reason)
        elif new_status == EstimateStatus.CANCELLED:
            estimate.cancel_estimate(user_id, reason)
        elif new_status == EstimateStatus.CONVERTED:
            estimate.mark_as_converted(user_id)
        elif new_status == EstimateStatus.EXPIRED:
            estimate.mark_as_expired(user_id)
        else:
            # Fallback to generic status update
            estimate.update_status(new_status, user_id, reason)
    
    async def _trigger_email_notification(self, estimate: Estimate) -> None:
        """Trigger email notification for sent estimate."""
        try:
            logger.info(f"Triggering email notification for estimate {estimate.estimate_number}")
            
            # TODO: Implement email notification logic
            # This would typically:
            # 1. Generate email content from estimate
            # 2. Send email to client
            # 3. Track email delivery
            
            # For now, just add email tracking entry
            if estimate.client_email:
                estimate.add_email_tracking(
                    recipient_email=estimate.client_email,
                    subject=f"Estimate {estimate.estimate_number} - {estimate.title}"
                )
            
        except Exception as e:
            # Don't fail the status change if email fails
            logger.warning(f"Failed to trigger email notification: {e}") 