"""
Emergency Scheduling Use Case

Business logic for emergency scheduling and urgent job management.
Handles urgent job creation, team notifications, and emergency response protocols.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

# Removed emergency_scheduling_dto imports - using direct parameters for simplified architecture
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.job import Job
from app.domain.enums import JobStatus, JobPriority, JobType
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class EmergencySchedulingUseCase:
    """
    Use case for emergency scheduling and urgent job management.
    
    Handles critical scenarios that require immediate attention:
    - Equipment failures requiring urgent repair
    - Safety incidents needing immediate response
    - Client emergencies with priority scheduling
    - Weather-related emergency adjustments
    - Supply shortages requiring urgent procurement
    """
    
    def __init__(
        self,
        voice_agent_helper: VoiceAgentHelperService,
        job_repository: Optional[JobRepository] = None,
        contact_repository: Optional[ContactRepository] = None,
        membership_repository: Optional[BusinessMembershipRepository] = None
    ):
        self.voice_agent_helper = voice_agent_helper
        self.job_repository = job_repository
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
        logger.info("EmergencySchedulingUseCase initialized")
    
    async def execute(
        self, 
        emergency_type: str,
        description: str,
        user_id: str, 
        business_id: uuid.UUID,
        client_name: Optional[str] = None,
        location: Optional[str] = None,
        equipment_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute emergency scheduling operations.
        
        Args:
            emergency_type: Type of emergency (equipment_failure, safety_incident, etc.)
            description: Description of the emergency
            user_id: User requesting emergency scheduling
            business_id: Business context
            client_name: Optional client name
            location: Optional location
            equipment_type: Optional equipment type for equipment failures
            severity: Optional severity level (low, medium, high, critical)
            
        Returns:
            Dict with emergency job details and notifications
            
        Raises:
            ValidationError: If input validation fails
            BusinessRuleViolationError: If emergency rules are violated
            ApplicationError: If scheduling fails
        """
        logger.info(f"Processing emergency scheduling request for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(emergency_type, description, user_id, business_id)
            
            # Check emergency permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "emergency_scheduling"
            )
            
            # Validate emergency session
            is_valid_emergency = await self.voice_agent_helper.validate_emergency_session(
                business_id, user_id, emergency_type
            )
            
            if not is_valid_emergency:
                raise BusinessRuleViolationError("Emergency scheduling validation failed")
            
            # Process emergency based on type
            result = await self._process_emergency_request(
                emergency_type, description, user_id, business_id, 
                client_name, location, equipment_type, severity
            )
            
            # Create emergency response
            response = {
                "emergency_id": result["emergency_id"],
                "emergency_type": emergency_type,
                "priority": result["priority"],
                "status": result["status"],
                "message": result["message"],
                "voice_response": result["voice_response"],
                "emergency_job": result.get("emergency_job"),
                "notifications_sent": result.get("notifications", []),
                "estimated_response_time": result.get("response_time"),
                "emergency_contacts": result.get("emergency_contacts", []),
                "follow_up_actions": result.get("follow_up_actions", []),
                "metadata": result.get("metadata", {})
            }
            
            logger.info(f"Emergency scheduling processed successfully: {result['emergency_id']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process emergency scheduling: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to process emergency scheduling: {str(e)}")
    
    async def _process_emergency_request(
        self, 
        emergency_type: str,
        description: str,
        user_id: str, 
        business_id: uuid.UUID,
        client_name: Optional[str] = None,
        location: Optional[str] = None,
        equipment_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process emergency request based on type."""
        params = {
            "emergency_type": emergency_type,
            "description": description,
            "client_name": client_name,
            "location": location,
            "equipment_type": equipment_type,
            "severity": severity
        }
        
        if emergency_type == "equipment_failure":
            return await self._handle_equipment_failure(params, user_id, business_id)
        elif emergency_type == "safety_incident":
            return await self._handle_safety_incident(params, user_id, business_id)
        elif emergency_type == "client_emergency":
            return await self._handle_client_emergency(params, user_id, business_id)
        elif emergency_type == "weather_emergency":
            return await self._handle_weather_emergency(params, user_id, business_id)
        elif emergency_type == "supply_shortage":
            return await self._handle_supply_shortage(params, user_id, business_id)
        elif emergency_type == "urgent_job":
            return await self._handle_urgent_job(params, user_id, business_id)
        else:
            return await self._handle_generic_emergency(params, user_id, business_id)
    
    async def _handle_equipment_failure(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle equipment failure emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Create emergency job
            emergency_job = None
            if self.job_repository:
                emergency_job = await self._create_emergency_job(
                    title=f"EMERGENCY: Equipment Failure - {params.get('equipment_type', 'Unknown Equipment')}",
                    description=f"Equipment failure reported: {params.get('description', '')}",
                    client_name=params.get('client_name'),
                    location=params.get('location'),
                    priority=JobPriority.EMERGENCY,
                    business_id=business_id,
                    user_id=user_id,
                    emergency_type=params.get('emergency_type')
                )
            
            # Determine response time based on severity
            response_time = self._calculate_response_time(params.get('severity', 'high'))
            
            # Prepare notifications
            notifications = await self._prepare_emergency_notifications(
                emergency_type="equipment_failure",
                emergency_id=emergency_id,
                business_id=business_id,
                details=params.get('description', ''),
                severity=params.get('severity')
            )
            
            # Generate follow-up actions
            follow_up_actions = [
                "Dispatch emergency repair technician",
                "Notify client of equipment failure",
                "Prepare backup equipment if available",
                "Schedule follow-up inspection"
            ]
            
            if params.get('equipment_type'):
                follow_up_actions.append(f"Check warranty status for {params.get('equipment_type')}")
            
            voice_response = f"Emergency equipment failure reported. I've created an emergency job and notified the team. "
            voice_response += f"A technician will respond within {response_time}. "
            if params.get('client_name'):
                voice_response += f"The client {params.get('client_name')} will be contacted immediately."
            
            return {
                "emergency_id": emergency_id,
                "priority": "emergency",
                "status": "dispatched",
                "message": "Equipment failure emergency processed",
                "voice_response": voice_response,
                "emergency_job": emergency_job,
                "notifications": notifications,
                "response_time": response_time,
                "follow_up_actions": follow_up_actions,
                "metadata": {
                    "equipment_type": request.equipment_type,
                    "failure_type": request.description,
                    "severity": request.severity or "high"
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling equipment failure emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "emergency",
                "status": "failed",
                "message": f"Failed to process equipment failure emergency: {str(e)}",
                "voice_response": "I couldn't process the equipment failure emergency. Please contact support directly."
            }
    
    async def _handle_safety_incident(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle safety incident emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Safety incidents require immediate response
            response_time = "15 minutes"
            
            # Create emergency job
            emergency_job = None
            if self.job_repository:
                emergency_job = await self._create_emergency_job(
                    title=f"SAFETY INCIDENT: {request.incident_type or 'Safety Emergency'}",
                    description=f"Safety incident reported: {request.description}",
                    client_name=request.client_name,
                    location=request.location,
                    priority=JobPriority.EMERGENCY,
                    business_id=business_id,
                    user_id=user_id,
                    emergency_type=request.emergency_type
                )
            
            # Prepare emergency notifications
            notifications = await self._prepare_emergency_notifications(
                emergency_type="safety_incident",
                emergency_id=emergency_id,
                business_id=business_id,
                details=request.description,
                severity="critical"
            )
            
            # Add safety-specific contacts
            emergency_contacts = [
                {"type": "safety_officer", "contact": "Safety Department"},
                {"type": "management", "contact": "Emergency Management"},
                {"type": "insurance", "contact": "Insurance Provider"}
            ]
            
            # Generate follow-up actions
            follow_up_actions = [
                "Secure the incident area",
                "Document the safety incident",
                "Notify insurance company",
                "Conduct safety investigation",
                "Review safety protocols"
            ]
            
            voice_response = f"Safety incident reported and emergency response initiated. "
            voice_response += f"Safety personnel will arrive within {response_time}. "
            voice_response += "Please ensure the area is secure and all personnel are safe."
            
            return {
                "emergency_id": emergency_id,
                "priority": "critical",
                "status": "responding",
                "message": "Safety incident emergency processed",
                "voice_response": voice_response,
                "emergency_job": emergency_job,
                "notifications": notifications,
                "response_time": response_time,
                "emergency_contacts": emergency_contacts,
                "follow_up_actions": follow_up_actions,
                "metadata": {
                    "incident_type": request.incident_type,
                    "safety_level": "critical",
                    "requires_documentation": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling safety incident emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "critical",
                "status": "failed",
                "message": f"Failed to process safety incident emergency: {str(e)}",
                "voice_response": "I couldn't process the safety incident emergency. Please contact emergency services directly."
            }
    
    async def _handle_client_emergency(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle client emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Client emergencies prioritize customer service
            response_time = self._calculate_response_time(request.severity or "high")
            
            # Create emergency job
            emergency_job = None
            if self.job_repository:
                emergency_job = await self._create_emergency_job(
                    title=f"CLIENT EMERGENCY: {request.client_name or 'Urgent Client Request'}",
                    description=f"Client emergency: {request.description}",
                    client_name=request.client_name,
                    location=request.location,
                    priority=JobPriority.URGENT,
                    business_id=business_id,
                    user_id=user_id,
                    emergency_type=request.emergency_type
                )
            
            # Prepare notifications
            notifications = await self._prepare_emergency_notifications(
                emergency_type="client_emergency",
                emergency_id=emergency_id,
                business_id=business_id,
                details=request.description,
                severity=request.severity or "high"
            )
            
            # Generate follow-up actions
            follow_up_actions = [
                "Contact client immediately",
                "Dispatch available technician",
                "Provide client updates every 30 minutes",
                "Escalate to management if needed"
            ]
            
            voice_response = f"Client emergency reported for {request.client_name or 'client'}. "
            voice_response += f"Emergency response team will arrive within {response_time}. "
            voice_response += "The client will be contacted immediately with updates."
            
            return {
                "emergency_id": emergency_id,
                "priority": "urgent",
                "status": "dispatched",
                "message": "Client emergency processed",
                "voice_response": voice_response,
                "emergency_job": emergency_job,
                "notifications": notifications,
                "response_time": response_time,
                "follow_up_actions": follow_up_actions,
                "metadata": {
                    "client_name": request.client_name,
                    "requires_client_updates": True,
                    "escalation_level": request.severity or "high"
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling client emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "urgent",
                "status": "failed",
                "message": f"Failed to process client emergency: {str(e)}",
                "voice_response": "I couldn't process the client emergency. Please contact the client directly."
            }
    
    async def _handle_weather_emergency(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle weather-related emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Weather emergencies may affect multiple jobs
            response_time = "30 minutes"
            
            # Prepare notifications
            notifications = await self._prepare_emergency_notifications(
                emergency_type="weather_emergency",
                emergency_id=emergency_id,
                business_id=business_id,
                details=request.description,
                severity=request.severity or "moderate"
            )
            
            # Generate follow-up actions
            follow_up_actions = [
                "Review all outdoor jobs for the day",
                "Notify affected clients",
                "Reschedule weather-dependent jobs",
                "Secure equipment and materials",
                "Monitor weather conditions"
            ]
            
            voice_response = f"Weather emergency reported: {request.description}. "
            voice_response += "I'm reviewing all affected jobs and will notify clients of any schedule changes. "
            voice_response += "The team will assess weather conditions and adjust schedules accordingly."
            
            return {
                "emergency_id": emergency_id,
                "priority": "moderate",
                "status": "assessing",
                "message": "Weather emergency processed",
                "voice_response": voice_response,
                "notifications": notifications,
                "response_time": response_time,
                "follow_up_actions": follow_up_actions,
                "metadata": {
                    "weather_type": request.description,
                    "affects_multiple_jobs": True,
                    "requires_rescheduling": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling weather emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "moderate",
                "status": "failed",
                "message": f"Failed to process weather emergency: {str(e)}",
                "voice_response": "I couldn't process the weather emergency. Please manually review affected jobs."
            }
    
    async def _handle_supply_shortage(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle supply shortage emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Supply shortages need urgent procurement
            response_time = "1 hour"
            
            # Generate follow-up actions
            follow_up_actions = [
                "Contact primary supplier immediately",
                "Check alternative suppliers",
                "Assess impact on scheduled jobs",
                "Notify affected clients if needed",
                "Consider emergency procurement"
            ]
            
            voice_response = f"Supply shortage emergency reported for {request.supply_item or 'critical supplies'}. "
            voice_response += "I'm contacting suppliers and assessing the impact on scheduled jobs. "
            voice_response += "You'll receive updates on procurement status within the hour."
            
            return {
                "emergency_id": emergency_id,
                "priority": "high",
                "status": "procuring",
                "message": "Supply shortage emergency processed",
                "voice_response": voice_response,
                "response_time": response_time,
                "follow_up_actions": follow_up_actions,
                "metadata": {
                    "supply_item": request.supply_item,
                    "quantity_needed": request.quantity,
                    "urgency_level": "high"
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling supply shortage emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "high",
                "status": "failed",
                "message": f"Failed to process supply shortage emergency: {str(e)}",
                "voice_response": "I couldn't process the supply shortage emergency. Please contact suppliers directly."
            }
    
    async def _handle_urgent_job(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle urgent job scheduling."""
        try:
            emergency_id = str(uuid.uuid4())
            
            # Create urgent job
            emergency_job = None
            if self.job_repository:
                emergency_job = await self._create_emergency_job(
                    title=f"URGENT: {request.job_title or 'Urgent Job Request'}",
                    description=request.description,
                    client_name=request.client_name,
                    location=request.location,
                    priority=JobPriority.URGENT,
                    business_id=business_id,
                    user_id=user_id,
                    emergency_type=request.emergency_type
                )
            
            response_time = self._calculate_response_time(request.severity or "high")
            
            voice_response = f"Urgent job scheduled: {request.job_title or 'Urgent Job'}. "
            voice_response += f"Response time is {response_time}. "
            if request.client_name:
                voice_response += f"The client {request.client_name} will be contacted with arrival time."
            
            return {
                "emergency_id": emergency_id,
                "priority": "urgent",
                "status": "scheduled",
                "message": "Urgent job scheduled successfully",
                "voice_response": voice_response,
                "emergency_job": emergency_job,
                "response_time": response_time,
                "metadata": {
                    "job_title": request.job_title,
                    "scheduled_immediately": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling urgent job: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "urgent",
                "status": "failed",
                "message": f"Failed to schedule urgent job: {str(e)}",
                "voice_response": "I couldn't schedule the urgent job. Please handle manually."
            }
    
    async def _handle_generic_emergency(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Handle generic emergency."""
        try:
            emergency_id = str(uuid.uuid4())
            
            response_time = self._calculate_response_time(params.get('severity', 'moderate'))
            
            voice_response = f"Emergency situation reported: {params.get('description', '')}. "
            voice_response += f"Emergency response initiated with {response_time} response time. "
            voice_response += "The team has been notified and will respond accordingly."
            
            return {
                "emergency_id": emergency_id,
                "priority": "moderate",
                "status": "responding",
                "message": "Emergency processed",
                "voice_response": voice_response,
                "response_time": response_time,
                "metadata": {
                    "emergency_type": params.get('emergency_type'),
                    "description": params.get('description')
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling generic emergency: {str(e)}")
            return {
                "emergency_id": str(uuid.uuid4()),
                "priority": "moderate",
                "status": "failed",
                "message": f"Failed to process emergency: {str(e)}",
                "voice_response": "I couldn't process the emergency. Please contact support."
            }
    
    async def _create_emergency_job(
        self,
        title: str,
        description: str,
        client_name: Optional[str],
        location: Optional[str],
        priority: JobPriority,
        business_id: uuid.UUID,
        user_id: str,
        emergency_type: str
    ) -> Optional[Dict[str, Any]]:
        """Create emergency job."""
        try:
            if not self.job_repository:
                return None
            
            # Create job entity
            job = Job(
                id=uuid.uuid4(),
                business_id=business_id,
                title=title,
                description=description,
                client_name=client_name or "Emergency Client",
                location_address=location,
                priority=priority,
                status=JobStatus.SCHEDULED,
                job_type=JobType.EMERGENCY,
                scheduled_start=datetime.utcnow() + timedelta(minutes=30),  # Schedule ASAP
                estimated_duration_minutes=120,  # Default 2 hours
                created_by=user_id,
                created_date=datetime.utcnow()
            )
            
            # Save job
            created_job = await self.job_repository.create(job)
            
            # Convert to dict
            return {
                "id": str(created_job.id),
                "title": created_job.title,
                "description": created_job.description,
                "client_name": created_job.client_name,
                "location": created_job.location_address,
                "priority": created_job.priority.value,
                "status": created_job.status.value,
                "scheduled_start": created_job.scheduled_start.isoformat() if created_job.scheduled_start else None,
                "emergency_type": emergency_type,
                "created_by": user_id,
                "created_date": created_job.created_date.isoformat() if created_job.created_date else None
            }
            
        except Exception as e:
            logger.error(f"Error creating emergency job: {str(e)}")
            return None
    
    async def _prepare_emergency_notifications(
        self,
        emergency_type: str,
        emergency_id: str,
        business_id: uuid.UUID,
        details: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """Prepare emergency notifications."""
        notifications = []
        
        try:
            # Get team members for notifications
            if self.membership_repository:
                team_members = await self.membership_repository.get_business_members(business_id)
                
                for member in team_members[:5]:  # Limit to 5 notifications
                    notification = {
                        "id": str(uuid.uuid4()),
                        "recipient_id": member.user_id,
                        "recipient_type": "team_member",
                        "emergency_type": emergency_type,
                        "emergency_id": emergency_id,
                        "message": f"Emergency {emergency_type}: {details}",
                        "severity": severity,
                        "notification_method": "sms",
                        "sent_at": datetime.utcnow().isoformat()
                    }
                    notifications.append(notification)
            
            # Add standard emergency notifications
            notifications.append({
                "id": str(uuid.uuid4()),
                "recipient_id": "dispatch",
                "recipient_type": "system",
                "emergency_type": emergency_type,
                "emergency_id": emergency_id,
                "message": f"Emergency dispatch required: {details}",
                "severity": severity,
                "notification_method": "system",
                "sent_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error preparing emergency notifications: {str(e)}")
        
        return notifications
    
    def _calculate_response_time(self, severity: str) -> str:
        """Calculate response time based on severity."""
        severity_times = {
            "critical": "15 minutes",
            "high": "30 minutes",
            "moderate": "1 hour",
            "low": "2 hours"
        }
        
        return severity_times.get(severity.lower(), "30 minutes")
    
    def _validate_input(
        self, 
        emergency_type: str,
        description: str,
        user_id: str, 
        business_id: uuid.UUID
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not emergency_type:
            raise ValidationError("Emergency type is required")
        
        if not description:
            raise ValidationError("Emergency description is required")
        
        # Validate emergency type
        valid_types = [
            "equipment_failure", "safety_incident", "client_emergency",
            "weather_emergency", "supply_shortage", "urgent_job"
        ]
        
        if emergency_type not in valid_types:
            raise ValidationError(f"Invalid emergency type: {emergency_type}")
        
        # Validate description length
        if len(description) > 500:
            raise ValidationError("Description must be 500 characters or less") 