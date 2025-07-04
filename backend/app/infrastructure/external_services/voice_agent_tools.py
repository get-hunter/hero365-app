"""
Voice Agent Tools System

Advanced voice agent tools that integrate with existing use cases for sophisticated business operations.
Provides scheduling, calendar management, quote generation, and other business functionalities.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List, Protocol
from datetime import datetime, timedelta, date
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ...application.use_cases.scheduling.intelligent_scheduling_use_case import IntelligentSchedulingUseCase
from ...application.use_cases.scheduling.calendar_management_use_case import CalendarManagementUseCase
from ...application.use_cases.estimate.create_estimate_use_case import CreateEstimateUseCase
from ...application.use_cases.estimate.get_estimate_use_case import GetEstimateUseCase
from ...application.use_cases.estimate.update_estimate_use_case import UpdateEstimateUseCase
from ...application.use_cases.estimate.convert_estimate_to_invoice_use_case import ConvertEstimateToInvoiceUseCase
from ...application.use_cases.job.create_job_use_case import CreateJobUseCase
from ...application.use_cases.job.update_job_use_case import UpdateJobUseCase
from ...application.use_cases.job.job_scheduling_use_case import JobSchedulingUseCase
from ...application.use_cases.contact.get_contact_use_case import GetContactUseCase
from ...application.use_cases.contact.search_contacts_use_case import SearchContactsUseCase

from ...application.dto.scheduling_dto import (
    AvailableTimeSlotRequestDTO, TimeSlotBookingRequestDTO, AvailabilityCheckRequestDTO
)
from ...application.dto.estimate_dto import CreateEstimateDTO, UpdateEstimateDTO
from ...application.dto.job_dto import JobCreateDTO, JobUpdateDTO, JobAddressDTO
from ...application.dto.contact_dto import ContactSearchDTO

from ...domain.enums import JobType, JobPriority, EstimateStatus, JobStatus, JobSource
from ...domain.value_objects.address import Address

logger = logging.getLogger(__name__)


# =============================================================================
# BASE VOICE AGENT TOOL SYSTEM
# =============================================================================

@dataclass
class VoiceAgentContext:
    """Enhanced context for voice agent operations with business access."""
    session_id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    agent_type: str
    participant_identity: Optional[str] = None
    dial_info: Optional[Dict[str, Any]] = None
    current_customer_id: Optional[str] = None
    current_job_id: Optional[str] = None
    current_project_id: Optional[str] = None


class VoiceAgentToolProtocol(Protocol):
    """Protocol for voice agent tools."""
    
    @property
    def name(self) -> str:
        """Tool name."""
        ...
    
    @property
    def description(self) -> str:
        """Tool description."""
        ...
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        ...


class BaseVoiceAgentTool(ABC):
    """Base class for voice agent tools with use case integration."""
    
    def __init__(self, use_case_container: Any):
        """Initialize with use case container for dependency injection."""
        self.use_case_container = use_case_container
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @abstractmethod
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the tool with business logic."""
        pass
    
    def _build_success_response(self, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a success response."""
        return {
            "success": True,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_error_response(self, message: str, error: str = None) -> Dict[str, Any]:
        """Build an error response."""
        return {
            "success": False,
            "message": message,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }


# =============================================================================
# SCHEDULING TOOLS
# =============================================================================

class AdvancedAvailabilityLookupTool(BaseVoiceAgentTool):
    """Advanced availability lookup using intelligent scheduling."""
    
    @property
    def name(self) -> str:
        return "advanced_availability_lookup"
    
    @property
    def description(self) -> str:
        return "Look up detailed availability for scheduling with skill matching and optimization"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute advanced availability lookup."""
        try:
            # Extract parameters
            date_range = kwargs.get("date_range", {})
            service_type = kwargs.get("service_type", "general")
            required_skills = kwargs.get("required_skills", [])
            customer_address = kwargs.get("customer_address", {})
            duration_hours = kwargs.get("duration_hours", 2)
            preferred_time = kwargs.get("preferred_time", "morning")
            
            # Get intelligent scheduling use case
            scheduling_use_case = self.use_case_container.get_intelligent_scheduling_use_case()
            
            # Build request
            request = AvailableTimeSlotRequestDTO(
                business_id=str(context.business_id),
                preferred_date_range={
                    "start_date": date_range.get("start_date", datetime.now().date()),
                    "end_date": date_range.get("end_date", (datetime.now() + timedelta(days=7)).date())
                },
                service_type=service_type,
                required_skills=required_skills,
                estimated_duration_hours=duration_hours,
                customer_address=customer_address,
                customer_preferences={
                    "preferred_time_of_day": preferred_time,
                    "max_travel_time_minutes": 30
                }
            )
            
            # Get available time slots
            response = await scheduling_use_case.get_available_time_slots(
                context.business_id, request, context.user_id
            )
            
            if response.total_slots_found == 0:
                return self._build_success_response(
                    "No available time slots found for the requested criteria. Let me suggest some alternatives.",
                    {
                        "available_slots": [],
                        "recommendations": response.recommendations,
                        "alternative_suggestions": response.alternative_suggestions
                    }
                )
            
            # Format slots for voice response
            formatted_slots = []
            for slot in response.available_slots[:5]:  # Top 5 slots
                formatted_slots.append({
                    "slot_id": slot.slot_id,
                    "date": slot.start_datetime.strftime("%A, %B %d"),
                    "time": slot.start_datetime.strftime("%I:%M %p"),
                    "technician": slot.assigned_technician.get("name", "Available technician"),
                    "estimated_duration": f"{slot.duration_minutes // 60} hours",
                    "travel_time": f"{slot.estimated_travel_time_minutes} minutes",
                    "confidence_score": slot.quality_score
                })
            
            # Build natural language response
            if len(formatted_slots) == 1:
                message = f"I found one available slot: {formatted_slots[0]['date']} at {formatted_slots[0]['time']} with {formatted_slots[0]['technician']}."
            else:
                message = f"I found {len(formatted_slots)} available slots. The best options are:"
                for i, slot in enumerate(formatted_slots[:3]):
                    message += f"\n{i+1}. {slot['date']} at {slot['time']} with {slot['technician']}"
            
            return self._build_success_response(message, {
                "available_slots": formatted_slots,
                "total_found": response.total_slots_found,
                "recommendations": response.recommendations
            })
            
        except Exception as e:
            self._logger.error(f"Error in advanced availability lookup: {str(e)}")
            return self._build_error_response(
                "I'm having trouble checking our schedule right now. Let me try a different approach.",
                str(e)
            )


class IntelligentAppointmentBookingTool(BaseVoiceAgentTool):
    """Intelligent appointment booking with job creation."""
    
    @property
    def name(self) -> str:
        return "intelligent_appointment_booking"
    
    @property
    def description(self) -> str:
        return "Book appointments intelligently with automatic job creation and optimization"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute intelligent appointment booking."""
        try:
            # Extract parameters
            slot_id = kwargs.get("slot_id")
            customer_info = kwargs.get("customer_info", {})
            service_details = kwargs.get("service_details", {})
            contact_info = kwargs.get("contact_info", {})
            
            if not slot_id:
                return self._build_error_response("Slot ID is required for booking")
            
            # Get use cases
            scheduling_use_case = self.use_case_container.get_intelligent_scheduling_use_case()
            
            # Build booking request
            booking_request = TimeSlotBookingRequestDTO(
                slot_id=slot_id,
                customer_info=customer_info,
                service_details=service_details,
                customer_contact=contact_info
            )
            
            # Book the slot
            booking_response = await scheduling_use_case.book_time_slot(
                context.business_id, booking_request, context.user_id
            )
            
            if booking_response.status == "confirmed":
                # Store job ID in context for future reference
                context.current_job_id = booking_response.job_id
                
                message = f"Perfect! I've booked your appointment for {booking_response.scheduled_slot['date']} at {booking_response.scheduled_slot['time']}. "
                message += f"Your confirmation number is {booking_response.confirmation_details['confirmation_number']}. "
                message += f"{booking_response.assigned_technician['name']} will be your technician."
                
                return self._build_success_response(message, {
                    "booking_confirmed": True,
                    "job_id": booking_response.job_id,
                    "confirmation_number": booking_response.confirmation_details["confirmation_number"],
                    "scheduled_slot": booking_response.scheduled_slot,
                    "technician": booking_response.assigned_technician,
                    "next_steps": booking_response.next_steps
                })
            else:
                return self._build_error_response(
                    "I wasn't able to confirm that booking. The slot may have been taken. Let me check for other available times."
                )
                
        except Exception as e:
            self._logger.error(f"Error in intelligent appointment booking: {str(e)}")
            return self._build_error_response(
                "I'm having trouble booking that appointment right now. Let me try again.",
                str(e)
            )


class CalendarAvailabilityCheckTool(BaseVoiceAgentTool):
    """Check team calendar availability comprehensively."""
    
    @property
    def name(self) -> str:
        return "calendar_availability_check"
    
    @property
    def description(self) -> str:
        return "Check detailed calendar availability for team members including working hours and time off"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute calendar availability check."""
        try:
            # Extract parameters
            user_ids = kwargs.get("user_ids", [])
            start_datetime = kwargs.get("start_datetime")
            end_datetime = kwargs.get("end_datetime")
            include_details = kwargs.get("include_details", True)
            
            if not start_datetime or not end_datetime:
                return self._build_error_response("Start and end datetime are required")
            
            # Get calendar management use case
            calendar_use_case = self.use_case_container.get_calendar_management_use_case()
            
            # Build availability request
            availability_request = AvailabilityCheckRequestDTO(
                user_ids=user_ids,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                include_working_hours=True,
                include_time_off=True,
                include_calendar_events=True
            )
            
            # Check availability
            availability_response = await calendar_use_case.check_user_availability(
                context.business_id, availability_request, context.user_id
            )
            
            # Format response for voice
            available_users = []
            unavailable_users = []
            
            for user_avail in availability_response.user_availability:
                if user_avail.is_available:
                    available_users.append({
                        "user_id": user_avail.user_id,
                        "name": user_avail.user_name,
                        "available_hours": user_avail.available_hours,
                        "conflicts": user_avail.conflicts
                    })
                else:
                    unavailable_users.append({
                        "user_id": user_avail.user_id,
                        "name": user_avail.user_name,
                        "reason": user_avail.unavailable_reason
                    })
            
            # Build natural language response
            if len(available_users) == 0:
                message = "Unfortunately, no team members are available during that time. "
                if unavailable_users:
                    message += f"The following team members are unavailable: {', '.join([u['name'] for u in unavailable_users])}"
            else:
                message = f"I found {len(available_users)} team member(s) available. "
                for user in available_users[:3]:  # Top 3
                    message += f"{user['name']} is available for {user['available_hours']} hours. "
            
            return self._build_success_response(message, {
                "available_users": available_users,
                "unavailable_users": unavailable_users,
                "summary": availability_response.summary
            })
            
        except Exception as e:
            self._logger.error(f"Error in calendar availability check: {str(e)}")
            return self._build_error_response(
                "I'm having trouble checking the calendar right now.",
                str(e)
            )


class AppointmentReschedulingTool(BaseVoiceAgentTool):
    """Reschedule appointments with intelligent optimization."""
    
    @property
    def name(self) -> str:
        return "appointment_rescheduling"
    
    @property
    def description(self) -> str:
        return "Reschedule existing appointments with intelligent slot optimization"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute appointment rescheduling."""
        try:
            # Extract parameters
            job_id = kwargs.get("job_id") or context.current_job_id
            new_date_range = kwargs.get("new_date_range", {})
            reason = kwargs.get("reason", "Customer requested")
            
            if not job_id:
                return self._build_error_response("Job ID is required for rescheduling")
            
            # Get use cases
            job_use_case = self.use_case_container.get_update_job_use_case()
            scheduling_use_case = self.use_case_container.get_intelligent_scheduling_use_case()
            
            # First, get current job details
            current_job = await job_use_case.get_job(context.business_id, job_id, context.user_id)
            
            if not current_job:
                return self._build_error_response("Job not found for rescheduling")
            
            # Find new available slots
            request = AvailableTimeSlotRequestDTO(
                business_id=str(context.business_id),
                preferred_date_range=new_date_range,
                service_type=current_job.job_type.value,
                estimated_duration_hours=float(current_job.time_tracking.estimated_hours or 2),
                customer_address=current_job.job_address.__dict__ if current_job.job_address else {},
                customer_preferences={"preferred_time_of_day": "any"}
            )
            
            slots_response = await scheduling_use_case.get_available_time_slots(
                context.business_id, request, context.user_id
            )
            
            if slots_response.total_slots_found == 0:
                return self._build_success_response(
                    "I couldn't find any available slots for rescheduling. Let me suggest some alternatives.",
                    {
                        "rescheduled": False,
                        "alternatives": slots_response.alternative_suggestions,
                        "recommendations": slots_response.recommendations
                    }
                )
            
            # Present best options to user
            best_slots = slots_response.available_slots[:3]
            message = f"I found {len(best_slots)} good options for rescheduling. "
            message += "Would you like me to book one of these times? "
            
            slot_options = []
            for i, slot in enumerate(best_slots):
                slot_info = f"{i+1}. {slot.start_datetime.strftime('%A, %B %d at %I:%M %p')} with {slot.assigned_technician.get('name', 'Available technician')}"
                slot_options.append(slot_info)
                message += f"\n{slot_info}"
            
            return self._build_success_response(message, {
                "rescheduling_options": [
                    {
                        "slot_id": slot.slot_id,
                        "date": slot.start_datetime.strftime("%A, %B %d"),
                        "time": slot.start_datetime.strftime("%I:%M %p"),
                        "technician": slot.assigned_technician.get("name", "Available technician")
                    }
                    for slot in best_slots
                ],
                "original_job_id": job_id,
                "reason": reason
            })
            
        except Exception as e:
            self._logger.error(f"Error in appointment rescheduling: {str(e)}")
            return self._build_error_response(
                "I'm having trouble rescheduling that appointment right now.",
                str(e)
            )


# =============================================================================
# ESTIMATE AND QUOTE TOOLS
# =============================================================================

class IntelligentQuoteGenerationTool(BaseVoiceAgentTool):
    """Generate intelligent quotes based on service requirements."""
    
    @property
    def name(self) -> str:
        return "intelligent_quote_generation"
    
    @property
    def description(self) -> str:
        return "Generate detailed quotes/estimates based on service requirements and customer needs"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute intelligent quote generation."""
        try:
            # Extract parameters
            customer_info = kwargs.get("customer_info", {})
            service_details = kwargs.get("service_details", {})
            address_info = kwargs.get("address_info", {})
            urgency = kwargs.get("urgency", "normal")
            
            # Get use cases
            estimate_use_case = self.use_case_container.get_create_estimate_use_case()
            contact_search_use_case = self.use_case_container.get_search_contacts_use_case()
            
            # Try to find existing customer
            customer_id = None
            if customer_info.get("phone") or customer_info.get("email"):
                search_request = ContactSearchDTO(
                    business_id=uuid.UUID(str(context.business_id)),
                    search_term=customer_info.get("phone", "") or customer_info.get("email", "")
                )
                
                search_results = await contact_search_use_case.execute(search_request, context.user_id)
                if search_results.contacts:
                    customer_id = search_results.contacts[0].id
                    context.current_customer_id = customer_id
            
            # Build estimate request
            if not customer_id:
                return self._build_error_response(
                    "I need customer information to generate a quote. Could you provide the customer's name or contact details?"
                )
            
            estimate_request = CreateEstimateDTO(
                contact_id=uuid.UUID(customer_id),
                title=service_details.get("title", "Service Estimate"),
                description=service_details.get("description", ""),
                line_items=[
                    {
                        "description": item.get("description", ""),
                        "quantity": item.get("quantity", 1),
                        "unit_price": item.get("unit_price", 0),
                        "total": item.get("total", 0)
                    }
                    for item in service_details.get("line_items", [])
                ],
                internal_notes=f"Generated via voice agent. Urgency: {urgency}",
                valid_until_date=(datetime.now() + timedelta(days=30)).date()
            )
            
            # Create estimate
            estimate_response = await estimate_use_case.execute(
                context.business_id, estimate_request, context.user_id
            )
            
            if estimate_response.success:
                # Format response for voice
                total_amount = estimate_response.estimate.total_amount
                estimate_number = estimate_response.estimate.estimate_number
                
                message = f"I've generated estimate #{estimate_number} for ${total_amount:.2f}. "
                message += f"This estimate includes {len(estimate_response.estimate.line_items)} items "
                message += f"and is valid until {estimate_response.estimate.valid_until.strftime('%B %d, %Y')}. "
                message += "Would you like me to email this estimate to the customer?"
                
                return self._build_success_response(message, {
                    "estimate_created": True,
                    "estimate_id": estimate_response.estimate.id,
                    "estimate_number": estimate_number,
                    "total_amount": float(total_amount),
                    "line_items": len(estimate_response.estimate.line_items),
                    "valid_until": estimate_response.estimate.valid_until.isoformat(),
                    "customer_id": customer_id
                })
            else:
                return self._build_error_response(
                    "I wasn't able to generate the estimate. Let me try again with different parameters."
                )
                
        except Exception as e:
            self._logger.error(f"Error in intelligent quote generation: {str(e)}")
            return self._build_error_response(
                "I'm having trouble generating that quote right now.",
                str(e)
            )


class EstimateToInvoiceConversionTool(BaseVoiceAgentTool):
    """Convert approved estimates to invoices."""
    
    @property
    def name(self) -> str:
        return "estimate_to_invoice_conversion"
    
    @property
    def description(self) -> str:
        return "Convert approved estimates to invoices when work is completed"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute estimate to invoice conversion."""
        try:
            # Extract parameters
            estimate_id = kwargs.get("estimate_id")
            work_completed = kwargs.get("work_completed", True)
            additional_items = kwargs.get("additional_items", [])
            
            if not estimate_id:
                return self._build_error_response("Estimate ID is required for conversion")
            
            # Get use case
            conversion_use_case = self.use_case_container.get_convert_estimate_to_invoice_use_case()
            
            # Convert estimate to invoice
            conversion_response = await conversion_use_case.execute(
                estimate_id, additional_items, context.user_id
            )
            
            if conversion_response.success:
                invoice = conversion_response.invoice
                message = f"Great! I've converted estimate #{conversion_response.original_estimate_number} "
                message += f"to invoice #{invoice.invoice_number}. "
                message += f"The total amount is ${invoice.total_amount:.2f}. "
                message += "The invoice has been sent to the customer."
                
                return self._build_success_response(message, {
                    "invoice_created": True,
                    "invoice_id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "total_amount": float(invoice.total_amount),
                    "original_estimate_id": estimate_id,
                    "status": invoice.status.value
                })
            else:
                return self._build_error_response(
                    "I wasn't able to convert the estimate to an invoice. Please check the estimate status."
                )
                
        except Exception as e:
            self._logger.error(f"Error in estimate to invoice conversion: {str(e)}")
            return self._build_error_response(
                "I'm having trouble converting that estimate to an invoice right now.",
                str(e)
            )


# =============================================================================
# CUSTOMER MANAGEMENT TOOLS
# =============================================================================

class CustomerLookupTool(BaseVoiceAgentTool):
    """Look up customer information and history."""
    
    @property
    def name(self) -> str:
        return "customer_lookup"
    
    @property
    def description(self) -> str:
        return "Look up customer information, history, and previous interactions"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute customer lookup."""
        try:
            # Extract parameters
            search_term = kwargs.get("search_term", "")
            phone_number = kwargs.get("phone_number", "")
            email = kwargs.get("email", "")
            
            if not any([search_term, phone_number, email]):
                return self._build_error_response("Search term, phone number, or email is required")
            
            # Get use case
            search_use_case = self.use_case_container.get_search_contacts_use_case()
            
            # Build search request
            query = search_term or phone_number or email
            search_request = ContactSearchDTO(
                business_id=uuid.UUID(str(context.business_id)),
                search_term=query
            )
            
            # Search for customer
            search_results = await search_use_case.execute(search_request, context.user_id)
            
            if not search_results.contacts:
                message = f"I couldn't find any customers matching '{query}'. "
                message += "Would you like me to create a new customer record?"
                
                return self._build_success_response(message, {
                    "customer_found": False,
                    "search_term": query,
                    "suggestion": "create_new_customer"
                })
            
            # Found customer(s)
            customer = search_results.contacts[0]  # Take first result
            context.current_customer_id = customer.id
            
            message = f"I found {customer.first_name} {customer.last_name}. "
            if customer.phone:
                message += f"Phone: {customer.phone}. "
            if customer.email:
                message += f"Email: {customer.email}. "
            
            # Get customer history summary
            message += f"This customer has been with us since {customer.created_at.strftime('%B %Y')}."
            
            return self._build_success_response(message, {
                "customer_found": True,
                "customer_id": customer.id,
                "customer_name": f"{customer.first_name} {customer.last_name}",
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address.__dict__ if customer.address else None,
                "customer_since": customer.created_at.isoformat()
            })
            
        except Exception as e:
            self._logger.error(f"Error in customer lookup: {str(e)}")
            return self._build_error_response(
                "I'm having trouble looking up that customer right now.",
                str(e)
            )


# =============================================================================
# EMERGENCY AND PRIORITY TOOLS
# =============================================================================

class EmergencySchedulingTool(BaseVoiceAgentTool):
    """Handle emergency scheduling with priority override."""
    
    @property
    def name(self) -> str:
        return "emergency_scheduling"
    
    @property
    def description(self) -> str:
        return "Schedule emergency jobs with priority override and immediate dispatch"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute emergency scheduling."""
        try:
            # Extract parameters
            emergency_type = kwargs.get("emergency_type", "general")
            customer_info = kwargs.get("customer_info", {})
            address_info = kwargs.get("address_info", {})
            description = kwargs.get("description", "Emergency service request")
            
            # Get use cases
            job_use_case = self.use_case_container.get_create_job_use_case()
            scheduling_use_case = self.use_case_container.get_intelligent_scheduling_use_case()
            
            # Create emergency job
            job_request = JobCreateDTO(
                business_id=uuid.UUID(str(context.business_id)),
                title=f"EMERGENCY: {emergency_type}",
                description=description,
                job_type=JobType.EMERGENCY,
                priority=JobPriority.URGENT,
                contact_id=uuid.UUID(context.current_customer_id) if context.current_customer_id else None,
                job_address=JobAddressDTO(**address_info) if address_info else None,
                scheduled_start=datetime.now() + timedelta(hours=1),  # ASAP
                source=JobSource.VOICE,
                notes=f"Emergency contact: {customer_info.get('phone', '')}",
                customer_requirements=f"Emergency call. Requires immediate dispatch."
            )
            
            job_response = await job_use_case.execute(job_request, context.user_id)
            
            if job_response.success:
                # Find immediate availability
                availability_request = AvailableTimeSlotRequestDTO(
                    business_id=str(context.business_id),
                    preferred_date_range={
                        "start_date": datetime.now().date(),
                        "end_date": datetime.now().date()
                    },
                    service_type=emergency_type,
                    estimated_duration_hours=1,
                    customer_address=address_info,
                    emergency_override=True
                )
                
                slots_response = await scheduling_use_case.get_available_time_slots(
                    context.business_id, availability_request, context.user_id
                )
                
                if slots_response.available_slots:
                    next_slot = slots_response.available_slots[0]
                    message = f"Emergency job created and assigned! "
                    message += f"A technician will be dispatched within {next_slot.estimated_travel_time_minutes} minutes. "
                    message += f"Your emergency job number is {job_response.job.id}. "
                    message += f"Please keep this number for reference."
                    
                    return self._build_success_response(message, {
                        "emergency_scheduled": True,
                        "job_id": job_response.job.id,
                        "dispatch_time": next_slot.start_datetime.isoformat(),
                        "technician": next_slot.assigned_technician.get("name", "Emergency technician"),
                        "eta_minutes": next_slot.estimated_travel_time_minutes
                    })
                else:
                    message = f"Emergency job created (#{job_response.job.id}). "
                    message += "I'm dispatching the next available technician. "
                    message += "You'll receive a call within 15 minutes with the ETA."
                    
                    return self._build_success_response(message, {
                        "emergency_scheduled": True,
                        "job_id": job_response.job.id,
                        "status": "dispatching",
                        "callback_within_minutes": 15
                    })
            
            return self._build_error_response(
                "I'm having trouble creating the emergency job. Let me transfer you to our emergency line."
            )
            
        except Exception as e:
            self._logger.error(f"Error in emergency scheduling: {str(e)}")
            return self._build_error_response(
                "This is an emergency situation. Let me transfer you to our emergency line immediately.",
                str(e)
            )


# =============================================================================
# TOOL FACTORY AND REGISTRY
# =============================================================================

class VoiceAgentToolFactory:
    """Factory for creating voice agent tools with proper dependency injection."""
    
    def __init__(self, use_case_container: Any):
        self.use_case_container = use_case_container
    
    def create_scheduling_tools(self) -> List[BaseVoiceAgentTool]:
        """Create scheduling-related tools."""
        return [
            AdvancedAvailabilityLookupTool(self.use_case_container),
            IntelligentAppointmentBookingTool(self.use_case_container),
            CalendarAvailabilityCheckTool(self.use_case_container),
            AppointmentReschedulingTool(self.use_case_container),
            EmergencySchedulingTool(self.use_case_container)
        ]
    
    def create_estimate_tools(self) -> List[BaseVoiceAgentTool]:
        """Create estimate and quote tools."""
        return [
            IntelligentQuoteGenerationTool(self.use_case_container),
            EstimateToInvoiceConversionTool(self.use_case_container)
        ]
    
    def create_customer_tools(self) -> List[BaseVoiceAgentTool]:
        """Create customer management tools."""
        return [
            CustomerLookupTool(self.use_case_container)
        ]
    
    def create_all_tools(self) -> List[BaseVoiceAgentTool]:
        """Create all available tools."""
        tools = []
        tools.extend(self.create_scheduling_tools())
        tools.extend(self.create_estimate_tools())
        tools.extend(self.create_customer_tools())
        return tools


def create_voice_agent_tools(use_case_container: Any) -> List[BaseVoiceAgentTool]:
    """Create all voice agent tools with dependency injection."""
    factory = VoiceAgentToolFactory(use_case_container)
    return factory.create_all_tools() 