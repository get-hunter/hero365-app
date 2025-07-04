"""
Schedule Outbound Call Use Case

Business logic for scheduling and managing outbound voice calls.
Handles call scheduling, campaign management, and client outreach.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ...dto.outbound_call_dto import OutboundCallResponseDTO
from app.domain.repositories.outbound_call_repository import OutboundCallRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.entities.outbound_call import OutboundCall, CallRecipient, CallScript
from app.domain.enums import CallStatus, CallPurpose, CallOutcome
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class ScheduleOutboundCallUseCase:
    """
    Use case for scheduling outbound calls.
    
    Handles outbound call scheduling for:
    - Lead generation and follow-up
    - Client appointment reminders
    - Service maintenance notifications
    - Payment reminders
    - Customer satisfaction surveys
    - Emergency notifications
    """
    
    def __init__(
        self,
        voice_agent_helper: VoiceAgentHelperService,
        outbound_call_repository: Optional[OutboundCallRepository] = None,
        contact_repository: Optional[ContactRepository] = None
    ):
        self.voice_agent_helper = voice_agent_helper
        self.outbound_call_repository = outbound_call_repository
        self.contact_repository = contact_repository
        logger.info("ScheduleOutboundCallUseCase initialized")
    
    async def execute(
        self, 
        recipient_phone: str,
        user_id: str, 
        business_id: uuid.UUID,
        recipient_name: Optional[str] = None,
        call_purpose: Optional[CallPurpose] = None,
        scheduled_time: Optional[datetime] = None,
        script_content: Optional[str] = None,
        campaign_id: Optional[uuid.UUID] = None,
        priority: Optional[int] = None,
        estimated_duration: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute outbound call scheduling.
        
        Args:
            recipient_phone: Phone number to call
            user_id: User scheduling the call
            business_id: Business context
            recipient_name: Optional recipient name
            call_purpose: Purpose of the call
            scheduled_time: When to schedule the call
            script_content: Optional script content
            campaign_id: Optional campaign ID
            priority: Call priority (1-10)
            estimated_duration: Estimated call duration in minutes
            max_attempts: Maximum retry attempts
            
        Returns:
            Dictionary with call details and scheduling information
            
        Raises:
            ValidationError: If input validation fails
            BusinessRuleViolationError: If scheduling rules are violated
            ApplicationError: If scheduling fails
        """
        logger.info(f"Scheduling outbound call for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(
                recipient_phone, user_id, business_id, recipient_name, call_purpose,
                scheduled_time, script_content, campaign_id, priority, estimated_duration, max_attempts
            )
            
            # Check outbound call permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "schedule_outbound_calls"
            )
            
            # Validate call recipient
            recipient_info = await self._validate_and_get_recipient(
                recipient_phone, 
                recipient_name,
                business_id
            )
            
            # Check do-not-call restrictions
            await self._check_do_not_call_restrictions(
                recipient_phone,
                business_id
            )
            
            # Create outbound call
            outbound_call = await self._create_outbound_call(
                recipient_info,
                user_id, 
                business_id,
                call_purpose,
                scheduled_time,
                script_content,
                campaign_id,
                priority,
                estimated_duration,
                max_attempts
            )
            
            # Schedule the call
            scheduling_result = await self._schedule_call(
                outbound_call, 
                call_purpose,
                scheduled_time,
                campaign_id
            )
            
            # Create response data
            response_data = {
                "call_id": str(outbound_call.id),
                "recipient_phone": outbound_call.recipient.phone_number,
                "recipient_name": outbound_call.recipient.name,
                "call_purpose": outbound_call.purpose.value,
                "scheduled_time": outbound_call.scheduled_time.isoformat() if outbound_call.scheduled_time else None,
                "status": outbound_call.status.value,
                "campaign_id": str(outbound_call.campaign_id) if outbound_call.campaign_id else None,
                "script_content": outbound_call.script.content if outbound_call.script else None,
                "estimated_duration": outbound_call.estimated_duration_minutes,
                "success": scheduling_result["success"],
                "message": scheduling_result["message"],
                "voice_response": scheduling_result["voice_response"],
                "metadata": {
                    "call_window": scheduling_result.get("call_window"),
                    "retry_attempts": 0,
                    "max_attempts": outbound_call.max_attempts,
                    "priority": outbound_call.priority.value if outbound_call.priority else "normal"
                }
            }
            
            logger.info(f"Outbound call scheduled successfully: {outbound_call.id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Failed to schedule outbound call: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to schedule outbound call: {str(e)}")
    
    async def _validate_and_get_recipient(
        self, 
        phone_number: str, 
        recipient_name: Optional[str],
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Validate and get recipient information."""
        try:
            # Check if contact exists in database
            contact = None
            if self.contact_repository:
                contact = await self.contact_repository.get_by_phone(business_id, phone_number)
            
            # Use existing contact info if available
            if contact:
                return {
                    "phone_number": phone_number,
                    "name": contact.name,
                    "contact_id": contact.id,
                    "preferred_time": contact.preferred_contact_time,
                    "timezone": contact.timezone,
                    "language": contact.preferred_language,
                    "is_existing_contact": True
                }
            else:
                # Create new recipient info
                return {
                    "phone_number": phone_number,
                    "name": recipient_name or "Unknown",
                    "contact_id": None,
                    "preferred_time": None,
                    "timezone": "UTC",
                    "language": "en-US",
                    "is_existing_contact": False
                }
                
        except Exception as e:
            logger.error(f"Error validating recipient: {str(e)}")
            raise ValidationError(f"Invalid recipient information: {str(e)}")
    
    async def _check_do_not_call_restrictions(
        self, 
        phone_number: str,
        business_id: uuid.UUID
    ) -> None:
        """Check do-not-call list restrictions."""
        try:
            if self.outbound_call_repository:
                is_restricted = await self.outbound_call_repository.is_on_do_not_call_list(
                    business_id, phone_number
                )
                
                if is_restricted:
                    raise BusinessRuleViolationError(
                        f"Phone number {phone_number} is on the do-not-call list"
                    )
                    
        except BusinessRuleViolationError:
            raise
        except Exception as e:
            logger.warning(f"Could not check do-not-call restrictions: {str(e)}")
            # Continue with call scheduling if check fails
    
    async def _create_outbound_call(
        self, 
        recipient_info: Dict[str, Any],
        user_id: str, 
        business_id: uuid.UUID,
        call_purpose: Optional[CallPurpose] = None,
        scheduled_time: Optional[datetime] = None,
        script_content: Optional[str] = None,
        campaign_id: Optional[uuid.UUID] = None,
        priority: Optional[int] = None,
        estimated_duration: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> OutboundCall:
        """Create outbound call entity."""
        try:
            # Create call recipient
            recipient = CallRecipient(
                name=recipient_info["name"],
                phone_number=recipient_info["phone_number"],
                contact_id=recipient_info["contact_id"],
                preferred_time=recipient_info["preferred_time"],
                timezone=recipient_info["timezone"] or "UTC",
                language=recipient_info["language"] or "en-US"
            )
            
            # Create call script
            script = None
            if script_content or call_purpose:
                script = CallScript(
                    content=script_content or self._get_default_script(call_purpose),
                    script_type=call_purpose.value if call_purpose else "general",
                    language=recipient_info["language"] or "en-US",
                    estimated_duration_minutes=estimated_duration or 5
                )
            
            # Create outbound call
            outbound_call = OutboundCall.schedule_call(
                business_id=business_id,
                recipient=recipient,
                purpose=call_purpose or CallPurpose.GENERAL_FOLLOWUP,
                scheduled_time=scheduled_time or datetime.utcnow() + timedelta(minutes=5),
                script=script,
                campaign_id=campaign_id,
                created_by=user_id,
                priority=priority,
                max_attempts=max_attempts or 3
            )
            
            # Save to repository
            if self.outbound_call_repository:
                created_call = await self.outbound_call_repository.create(outbound_call)
                return created_call
            else:
                return outbound_call
                
        except Exception as e:
            logger.error(f"Error creating outbound call: {str(e)}")
            raise ApplicationError(f"Failed to create outbound call: {str(e)}")
    
    async def _schedule_call(
        self, 
        outbound_call: OutboundCall, 
        call_purpose: Optional[CallPurpose] = None,
        scheduled_time: Optional[datetime] = None,
        campaign_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Schedule the outbound call."""
        try:
            # Calculate call window
            call_scheduled_time = outbound_call.scheduled_time
            call_window = {
                "start": call_scheduled_time.isoformat(),
                "end": (call_scheduled_time + timedelta(minutes=30)).isoformat()
            }
            
            # Determine time until call
            time_until = ""
            time_diff = call_scheduled_time - datetime.utcnow()
            if time_diff.total_seconds() > 0:
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                if hours > 0:
                    time_until = f"in {hours} hours and {minutes} minutes"
                else:
                    time_until = f"in {minutes} minutes"
            else:
                time_until = "immediately"
            
            # Generate voice response
            voice_response = f"Outbound call scheduled successfully for {outbound_call.recipient.name} at {outbound_call.recipient.phone_number}. "
            voice_response += f"Call purpose: {outbound_call.purpose.value.replace('_', ' ')}. "
            voice_response += f"Scheduled {time_until} at {call_scheduled_time.strftime('%I:%M %p')}."
            
            if outbound_call.campaign_id:
                voice_response += f" This call is part of campaign {outbound_call.campaign_id}."
            
            return {
                "success": True,
                "message": "Outbound call scheduled successfully",
                "voice_response": voice_response,
                "call_window": call_window,
                "time_until_call": time_until
            }
            
        except Exception as e:
            logger.error(f"Error scheduling call: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to schedule call: {str(e)}",
                "voice_response": "I couldn't schedule the outbound call. Please try again."
            }
    
    def _get_default_script(self, call_purpose: CallPurpose) -> str:
        """Get default script content based on call purpose."""
        scripts = {
            CallPurpose.APPOINTMENT_REMINDER: "Hello {name}, this is a friendly reminder about your appointment with {business_name} scheduled for {appointment_time}. Please call us if you need to reschedule.",
            
            CallPurpose.PAYMENT_REMINDER: "Hello {name}, this is {business_name}. We wanted to remind you about your outstanding balance of {amount}. Please contact us to arrange payment or discuss payment options.",
            
            CallPurpose.SERVICE_FOLLOWUP: "Hello {name}, this is {business_name}. We recently completed work at your property and wanted to follow up to ensure you're satisfied with our service. Do you have any questions or concerns?",
            
            CallPurpose.MAINTENANCE_REMINDER: "Hello {name}, this is {business_name}. It's time for your scheduled maintenance service. Please call us to schedule an appointment at your convenience.",
            
            CallPurpose.LEAD_QUALIFICATION: "Hello {name}, this is {business_name}. Thank you for your interest in our services. I'd like to discuss your project requirements and see how we can help you.",
            
            CallPurpose.CUSTOMER_SURVEY: "Hello {name}, this is {business_name}. We'd appreciate a few minutes of your time to get feedback about our recent service. Your input helps us improve our services.",
            
            CallPurpose.EMERGENCY_NOTIFICATION: "Hello {name}, this is {business_name} with an important notification regarding your service. Please call us back as soon as possible.",
            
            CallPurpose.GENERAL_FOLLOWUP: "Hello {name}, this is {business_name}. We wanted to follow up on our recent interaction and see if you have any questions or if there's anything else we can help you with."
        }
        
        return scripts.get(call_purpose, "Hello {name}, this is {business_name}. Thank you for your time.")
    
    def _validate_input(
        self, 
        recipient_phone: str,
        user_id: str, 
        business_id: uuid.UUID,
        recipient_name: Optional[str] = None,
        call_purpose: Optional[CallPurpose] = None,
        scheduled_time: Optional[datetime] = None,
        script_content: Optional[str] = None,
        campaign_id: Optional[uuid.UUID] = None,
        priority: Optional[int] = None,
        estimated_duration: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not recipient_phone or not recipient_phone.strip():
            raise ValidationError("Recipient phone number is required")
        
        # Validate phone number format (basic validation)
        phone = recipient_phone.strip()
        if len(phone) < 10:
            raise ValidationError("Phone number must be at least 10 digits")
        
        # Validate scheduled time
        if scheduled_time and scheduled_time < datetime.utcnow():
            raise ValidationError("Scheduled time cannot be in the past")
        
        # Validate estimated duration
        if estimated_duration and (estimated_duration < 1 or estimated_duration > 60):
            raise ValidationError("Estimated duration must be between 1 and 60 minutes")
        
        # Validate max attempts
        if max_attempts and (max_attempts < 1 or max_attempts > 10):
            raise ValidationError("Max attempts must be between 1 and 10")
        
        # Validate script content length
        if script_content and len(script_content) > 2000:
            raise ValidationError("Script content must be 2000 characters or less") 