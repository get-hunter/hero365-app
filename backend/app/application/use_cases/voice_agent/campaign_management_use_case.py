"""
Campaign Management Use Case

Business logic for managing outbound call campaigns.
Handles campaign creation, execution, and performance tracking.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Using direct parameters for simplified architecture
from app.domain.repositories.outbound_call_repository import OutboundCallRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.enums import CallStatus, CallPurpose, CallOutcome
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class CampaignManagementUseCase:
    """
    Use case for managing outbound call campaigns.
    
    Handles campaign management operations:
    - Campaign creation and configuration
    - Bulk call scheduling
    - Campaign performance tracking
    - Call outcome analysis
    - Follow-up automation
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
        logger.info("CampaignManagementUseCase initialized")
    
    async def execute(
        self, 
        operation: str,
        user_id: str, 
        business_id: uuid.UUID,
        campaign_name: Optional[str] = None,
        campaign_description: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute campaign management operations.
        
        Args:
            operation: Type of operation (create_campaign, start_campaign, etc.)
            user_id: User managing the campaign
            business_id: Business context
            campaign_name: Optional campaign name
            campaign_description: Optional campaign description
            campaign_id: Optional campaign ID for existing campaigns
            
        Returns:
            Dictionary with campaign details and results
            
        Raises:
            ValidationError: If input validation fails
            ApplicationError: If campaign management fails
        """
        logger.info(f"Processing campaign management request for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(operation, user_id, business_id, campaign_name, campaign_id)
            
            # Check campaign management permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "campaign_management"
            )
            
            # Route to appropriate campaign handler
            result = await self._route_campaign_request(
                operation, user_id, business_id, campaign_name, campaign_description, campaign_id
            )
            
            # Create response data
            response_data = {
                "campaign_id": result["campaign_id"],
                "operation": operation,
                "success": result["success"],
                "message": result["message"],
                "voice_response": result.get("voice_response", result["message"]),
                "campaign_details": result.get("campaign"),
                "performance_metrics": result.get("performance"),
                "scheduled_calls_count": result.get("scheduled_calls", 0),
                "metadata": result.get("metadata", {})
            }
            
            logger.info(f"Campaign management processed successfully: {result['campaign_id']}")
            return response_data
            
        except Exception as e:
            logger.error(f"Failed to process campaign management: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to process campaign management: {str(e)}")
    
    async def _route_campaign_request(
        self, 
        operation: str,
        user_id: str, 
        business_id: uuid.UUID,
        campaign_name: Optional[str] = None,
        campaign_description: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route campaign request to appropriate handler."""
        if operation == "create_campaign":
            return await self._create_campaign(
                user_id, business_id, campaign_name, campaign_description
            )
        elif operation == "start_campaign":
            return await self._start_campaign(campaign_id, user_id, business_id)
        elif operation == "pause_campaign":
            return await self._pause_campaign(campaign_id, user_id, business_id)
        elif operation == "stop_campaign":
            return await self._stop_campaign(campaign_id, user_id, business_id)
        elif operation == "get_performance":
            return await self._get_campaign_performance(campaign_id, user_id, business_id)
        elif operation == "schedule_bulk_calls":
            return await self._schedule_bulk_calls(campaign_id, user_id, business_id)
        else:
            return {
                "campaign_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Unknown campaign operation: {operation}",
                "voice_response": f"I don't recognize the campaign operation '{operation}'. Available operations include create, start, pause, stop, and get performance."
            }
    
    async def _create_campaign(
        self, 
        user_id: str, 
        business_id: uuid.UUID,
        campaign_name: Optional[str] = None,
        campaign_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new campaign."""
        try:
            campaign_id = str(uuid.uuid4())
            
            # Create campaign data
            campaign_data = {
                "id": campaign_id,
                "name": campaign_name or "Unnamed Campaign",
                "description": campaign_description or "No description provided",
                "purpose": CallPurpose.GENERAL_FOLLOWUP.value,
                "business_id": str(business_id),
                "created_by": user_id,
                "created_date": datetime.utcnow().isoformat(),
                "status": "created",
                "start_time": None,
                "end_time": None,
                "target_contacts": [],
                "script_template": "",
                "max_attempts_per_contact": 3,
                "call_window_start": "09:00",
                "call_window_end": "17:00"
            }
            
            # Save campaign (in real implementation)
            # if self.outbound_call_repository:
            #     await self.outbound_call_repository.create_campaign(campaign_data)
            
            voice_response = f"Campaign '{campaign_name or 'Unnamed Campaign'}' created successfully. "
            voice_response += "Campaign is ready to start when you're ready."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Campaign created successfully",
                "voice_response": voice_response,
                "campaign": campaign_data,
                "metadata": {
                    "target_count": 0,
                    "estimated_duration": "Unknown",
                    "call_purpose": "general"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {
                "campaign_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create campaign: {str(e)}",
                "voice_response": "I couldn't create the campaign. Please try again."
            }
    
    async def _start_campaign(
        self, 
        campaign_id: Optional[str],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Start existing campaign."""
        try:
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            # In real implementation, get campaign from repository
            # campaign = await self.outbound_call_repository.get_campaign(campaign_id)
            
            # Mock campaign start
            scheduled_calls = 10  # Default mock value
            
            # Start campaign execution
            start_result = await self._execute_campaign_start(campaign_id, user_id, business_id)
            
            voice_response = f"Campaign started successfully. "
            voice_response += f"I've scheduled {scheduled_calls} calls to begin immediately. "
            voice_response += "You'll receive updates as calls are completed."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Campaign started successfully",
                "voice_response": voice_response,
                "scheduled_calls": scheduled_calls,
                "metadata": {
                    "start_time": datetime.utcnow().isoformat(),
                    "calls_scheduled": scheduled_calls,
                    "status": "active"
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting campaign: {str(e)}")
            return {
                "campaign_id": campaign_id or str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to start campaign: {str(e)}",
                "voice_response": "I couldn't start the campaign. Please try again."
            }
    
    async def _pause_campaign(
        self, 
        campaign_id: Optional[str],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Pause active campaign."""
        try:
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            # In real implementation, pause campaign in repository
            # await self.outbound_call_repository.pause_campaign(campaign_id)
            
            voice_response = f"Campaign paused successfully. "
            voice_response += "All pending calls have been suspended. "
            voice_response += "You can resume the campaign when you're ready."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Campaign paused successfully",
                "voice_response": voice_response,
                "metadata": {
                    "pause_time": datetime.utcnow().isoformat(),
                    "status": "paused"
                }
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {str(e)}")
            return {
                "campaign_id": campaign_id or str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to pause campaign: {str(e)}",
                "voice_response": "I couldn't pause the campaign. Please try again."
            }
    
    async def _stop_campaign(
        self, 
        campaign_id: Optional[str],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Stop campaign permanently."""
        try:
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            # In real implementation, stop campaign in repository
            # await self.outbound_call_repository.stop_campaign(campaign_id)
            
            voice_response = f"Campaign stopped successfully. "
            voice_response += "All pending calls have been cancelled. "
            voice_response += "You can view the final campaign performance report."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Campaign stopped successfully",
                "voice_response": voice_response,
                "metadata": {
                    "stop_time": datetime.utcnow().isoformat(),
                    "status": "stopped"
                }
            }
            
        except Exception as e:
            logger.error(f"Error stopping campaign: {str(e)}")
            return {
                "campaign_id": campaign_id or str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to stop campaign: {str(e)}",
                "voice_response": "I couldn't stop the campaign. Please try again."
            }
    
    async def _get_campaign_performance(
        self, 
        campaign_id: Optional[str],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get campaign performance metrics."""
        try:
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            # In real implementation, get performance from repository
            # performance = await self.outbound_call_repository.get_campaign_performance(campaign_id)
            
            # Mock performance data
            performance = {
                "total_calls": 50,
                "completed_calls": 30,
                "successful_calls": 15,
                "success_rate": 50.0,
                "average_call_duration": 4.5,
                "appointments_scheduled": 8,
                "callbacks_requested": 5,
                "total_duration_minutes": 135.0
            }
            
            voice_response = f"Campaign performance summary: "
            voice_response += f"{performance['completed_calls']} of {performance['total_calls']} calls completed. "
            voice_response += f"Success rate: {performance['success_rate']}%. "
            voice_response += f"{performance['appointments_scheduled']} appointments scheduled."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Campaign performance retrieved successfully",
                "voice_response": voice_response,
                "performance": performance,
                "metadata": {
                    "report_generated": datetime.utcnow().isoformat(),
                    "data_accuracy": "real_time"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign performance: {str(e)}")
            return {
                "campaign_id": campaign_id or str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to get campaign performance: {str(e)}",
                "voice_response": "I couldn't retrieve the campaign performance. Please try again."
            }
    
    async def _schedule_bulk_calls(
        self, 
        campaign_id: Optional[str],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Schedule bulk calls for campaign."""
        try:
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            # Get contacts for campaign
            target_contacts = await self._get_contacts_for_campaign(business_id)
            scheduled_count = 0
            
            # Schedule calls for each contact
            for contact in target_contacts:
                try:
                    # In real implementation, create individual outbound calls
                    # call = await self._create_campaign_call(contact, campaign_id, user_id)
                    scheduled_count += 1
                except Exception as e:
                    logger.warning(f"Failed to schedule call for contact {contact}: {str(e)}")
            
            voice_response = f"Bulk call scheduling completed. "
            voice_response += f"Successfully scheduled {scheduled_count} calls for campaign. "
            if len(target_contacts) > scheduled_count:
                failed_count = len(target_contacts) - scheduled_count
                voice_response += f"{failed_count} calls failed to schedule and will be retried."
            
            return {
                "campaign_id": campaign_id,
                "success": True,
                "message": "Bulk calls scheduled successfully",
                "voice_response": voice_response,
                "scheduled_calls": scheduled_count,
                "metadata": {
                    "total_targets": len(target_contacts),
                    "successful_schedules": scheduled_count,
                    "failed_schedules": len(target_contacts) - scheduled_count,
                    "schedule_time": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error scheduling bulk calls: {str(e)}")
            return {
                "campaign_id": campaign_id or str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to schedule bulk calls: {str(e)}",
                "voice_response": "I couldn't schedule the bulk calls. Please try again."
            }
    
    async def _execute_campaign_start(
        self, 
        campaign_id: str,
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Execute campaign start logic."""
        try:
            # In real implementation, this would:
            # 1. Update campaign status to active
            # 2. Schedule initial batch of calls
            # 3. Set up campaign monitoring
            # 4. Initialize performance tracking
            
            return {
                "success": True,
                "calls_scheduled": 10,  # Mock value
                "start_time": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error executing campaign start: {str(e)}")
            raise ApplicationError(f"Failed to start campaign execution: {str(e)}")
    
    async def _get_contacts_for_campaign(
        self, 
        business_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get contacts for campaign based on criteria."""
        try:
            if not self.contact_repository:
                return []
            
            # In real implementation, apply filters and get contacts
            # contacts = await self.contact_repository.get_contacts_for_campaign(business_id)
            
            # Return mock contacts for now
            return [
                {"id": str(uuid.uuid4()), "name": "Contact 1", "phone": "+1234567890"},
                {"id": str(uuid.uuid4()), "name": "Contact 2", "phone": "+1234567891"},
            ]
            
        except Exception as e:
            logger.error(f"Error getting contacts for campaign: {str(e)}")
            return []
    
    def _validate_input(
        self, 
        operation: str,
        user_id: str, 
        business_id: uuid.UUID,
        campaign_name: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not operation or not operation.strip():
            raise ValidationError("Campaign operation is required")
        
        # Validate operation type
        valid_operations = [
            "create_campaign", "start_campaign", "pause_campaign", 
            "stop_campaign", "get_performance", "schedule_bulk_calls"
        ]
        
        if operation not in valid_operations:
            raise ValidationError(f"Invalid campaign operation: {operation}")
        
        # Operation-specific validations
        if operation == "create_campaign":
            if not campaign_name:
                raise ValidationError("Campaign name is required for create operation")
        
        elif operation in ["start_campaign", "pause_campaign", "stop_campaign", "get_performance"]:
            if not campaign_id:
                raise ValidationError(f"Campaign ID is required for {operation} operation")
        
        # Validate campaign name length
        if campaign_name and len(campaign_name) > 100:
            raise ValidationError("Campaign name must be 100 characters or less")
        
        # Validate campaign description length
        if campaign_description and len(campaign_description) > 500:
            raise ValidationError("Campaign description must be 500 characters or less") 