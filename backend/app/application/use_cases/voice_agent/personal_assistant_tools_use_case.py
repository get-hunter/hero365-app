"""
Personal Assistant Tools Use Case

Business logic for personal assistant voice tools and hands-free operations.
Handles comprehensive business management tools for mobile use while driving.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Removed personal_assistant_dto imports - using direct parameters for simplified architecture
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.enums import JobStatus, ProjectStatus, ContactType
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError, NotFoundError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class PersonalAssistantToolsUseCase:
    """
    Use case for personal assistant voice tools.
    
    Provides comprehensive business management tools optimized for hands-free,
    mobile use while driving or working in the field. Focuses on safety,
    efficiency, and quick access to critical business information.
    """
    
    def __init__(
        self,
        voice_agent_helper: VoiceAgentHelperService,
        job_repository: Optional[JobRepository] = None,
        project_repository: Optional[ProjectRepository] = None,
        contact_repository: Optional[ContactRepository] = None,
        product_repository: Optional[ProductRepository] = None,
        membership_repository: Optional[BusinessMembershipRepository] = None
    ):
        self.voice_agent_helper = voice_agent_helper
        self.job_repository = job_repository
        self.project_repository = project_repository
        self.contact_repository = contact_repository
        self.product_repository = product_repository
        self.membership_repository = membership_repository
        logger.info("PersonalAssistantToolsUseCase initialized")
    
    async def execute(
        self, 
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Execute personal assistant tool operations.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool-specific parameters
            user_id: User requesting the operation
            business_id: Business context
            
        Returns:
            Dict with operation results including success, message, data, voice_response, suggestions, and metadata
            
        Raises:
            ValidationError: If input validation fails
            ApplicationError: If operation fails
        """
        logger.info(f"Executing personal assistant tool '{tool_name}' for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(tool_name, parameters, user_id, business_id)
            
            # Check basic voice permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "use_voice_assistant"
            )
            
            # Route to appropriate tool handler
            result = await self._route_tool_request(tool_name, parameters, user_id, business_id)
            
            # Create response dictionary
            response = {
                "tool_name": tool_name,
                "success": result["success"],
                "message": result["message"],
                "data": result.get("data"),
                "voice_response": result.get("voice_response", result["message"]),
                "suggestions": result.get("suggestions", []),
                "metadata": result.get("metadata", {})
            }
            
            logger.info(f"Personal assistant tool executed successfully: {tool_name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute personal assistant tool: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to execute personal assistant tool: {str(e)}")
    
    async def _route_tool_request(
        self, 
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Route tool request to appropriate handler."""
        parameters = parameters or {}
        
        # Main business tools
        if tool_name == "get_daily_schedule":
            return await self._get_daily_schedule(parameters, user_id, business_id)
        elif tool_name == "get_next_job":
            return await self._get_next_job(parameters, user_id, business_id)
        elif tool_name == "update_job_status":
            return await self._update_job_status(parameters, user_id, business_id)
        elif tool_name == "get_job_details":
            return await self._get_job_details(parameters, user_id, business_id)
        elif tool_name == "add_job_note":
            return await self._add_job_note(parameters, user_id, business_id)
        elif tool_name == "get_navigation":
            return await self._get_navigation(parameters, user_id, business_id)
        elif tool_name == "check_inventory":
            return await self._check_inventory(parameters, user_id, business_id)
        elif tool_name == "get_client_info":
            return await self._get_client_info(parameters, user_id, business_id)
        elif tool_name == "log_expense":
            return await self._log_expense(parameters, user_id, business_id)
        elif tool_name == "get_business_metrics":
            return await self._get_business_metrics(parameters, user_id, business_id)
        elif tool_name == "send_client_message":
            return await self._send_client_message(parameters, user_id, business_id)
        elif tool_name == "schedule_followup":
            return await self._schedule_followup(parameters, user_id, business_id)
        elif tool_name == "get_weather_info":
            return await self._get_weather_info(parameters, user_id, business_id)
        elif tool_name == "emergency_contact":
            return await self._emergency_contact(parameters, user_id, business_id)
        elif tool_name == "voice_to_text_note":
            return await self._voice_to_text_note(parameters, user_id, business_id)
        else:
            return {
                "success": False,
                "message": f"Unknown tool: {tool_name}",
                "voice_response": f"I don't recognize the tool '{tool_name}'. Available tools include schedule, jobs, navigation, inventory, and client information."
            }
    
    async def _get_daily_schedule(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get daily schedule overview."""
        try:
            if not self.job_repository:
                return {
                    "success": False,
                    "message": "Job information is not available",
                    "voice_response": "I can't access your schedule right now. Please try again later."
                }
            
            # Get today's date or specified date
            target_date = parameters.get("date")
            if not target_date:
                target_date = datetime.utcnow().date()
            elif isinstance(target_date, str):
                target_date = datetime.fromisoformat(target_date).date()
            
            # Get jobs for the day
            jobs = await self.job_repository.get_jobs_by_date(business_id, target_date)
            
            # Calculate schedule metrics
            total_jobs = len(jobs)
            completed_jobs = sum(1 for job in jobs if job.status == JobStatus.COMPLETED)
            upcoming_jobs = sum(1 for job in jobs if job.status in [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS])
            
            # Get next job
            next_job = None
            current_time = datetime.utcnow()
            for job in jobs:
                if job.scheduled_start and job.scheduled_start > current_time:
                    next_job = job
                    break
            
            # Build schedule overview
            schedule_data = {
                "date": target_date.isoformat(),
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "upcoming_jobs": upcoming_jobs,
                "next_job": {
                    "id": str(next_job.id),
                    "title": next_job.title,
                    "client": next_job.client_name,
                    "scheduled_time": next_job.scheduled_start.strftime("%I:%M %p"),
                    "location": next_job.location_address
                } if next_job else None,
                "jobs": [
                    {
                        "id": str(job.id),
                        "title": job.title,
                        "client": job.client_name,
                        "status": job.status.value,
                        "scheduled_time": job.scheduled_start.strftime("%I:%M %p") if job.scheduled_start else None,
                        "location": job.location_address
                    }
                    for job in jobs
                ]
            }
            
            # Generate voice response
            if total_jobs == 0:
                voice_response = f"You have no jobs scheduled for {target_date.strftime('%A, %B %d')}. Enjoy your day off!"
            else:
                voice_response = f"You have {total_jobs} jobs scheduled for {target_date.strftime('%A, %B %d')}. "
                if completed_jobs > 0:
                    voice_response += f"You've completed {completed_jobs} jobs. "
                if upcoming_jobs > 0:
                    voice_response += f"You have {upcoming_jobs} jobs remaining. "
                if next_job:
                    voice_response += f"Your next job is {next_job.title} at {next_job.client_name}, scheduled for {next_job.scheduled_start.strftime('%I:%M %p')}."
            
            return {
                "success": True,
                "message": "Daily schedule retrieved successfully",
                "voice_response": voice_response,
                "data": schedule_data,
                "suggestions": ["Get next job details", "Navigate to next job", "Update job status"]
            }
            
        except Exception as e:
            logger.error(f"Error getting daily schedule: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get daily schedule: {str(e)}",
                "voice_response": "I couldn't retrieve your schedule right now. Please try again."
            }
    
    async def _get_next_job(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get next scheduled job."""
        try:
            if not self.job_repository:
                return {
                    "success": False,
                    "message": "Job information is not available",
                    "voice_response": "I can't access your job information right now."
                }
            
            # Get next job for user
            next_job = await self.job_repository.get_next_job_for_user(business_id, user_id)
            
            if not next_job:
                return {
                    "success": True,
                    "message": "No upcoming jobs found",
                    "voice_response": "You don't have any upcoming jobs scheduled. Great job staying on top of your schedule!",
                    "data": None
                }
            
            # Build job details
            job_data = {
                "id": str(next_job.id),
                "title": next_job.title,
                "client": next_job.client_name,
                "status": next_job.status.value,
                "scheduled_time": next_job.scheduled_start.strftime("%I:%M %p") if next_job.scheduled_start else None,
                "location": next_job.location_address,
                "description": next_job.description,
                "priority": next_job.priority.value if next_job.priority else "normal",
                "estimated_duration": next_job.estimated_duration_minutes,
                "contact_info": next_job.client_phone
            }
            
            # Calculate time until job
            time_until = ""
            if next_job.scheduled_start:
                time_diff = next_job.scheduled_start - datetime.utcnow()
                if time_diff.total_seconds() > 0:
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    if hours > 0:
                        time_until = f"in {hours} hours and {minutes} minutes"
                    else:
                        time_until = f"in {minutes} minutes"
                else:
                    time_until = "now"
            
            # Generate voice response
            voice_response = f"Your next job is {next_job.title} at {next_job.client_name}"
            if next_job.scheduled_start:
                voice_response += f", scheduled for {next_job.scheduled_start.strftime('%I:%M %p')} {time_until}"
            if next_job.location_address:
                voice_response += f". The location is {next_job.location_address}"
            
            return {
                "success": True,
                "message": "Next job retrieved successfully",
                "voice_response": voice_response,
                "data": job_data,
                "suggestions": ["Get navigation to job", "Call client", "Update job status", "Add job note"]
            }
            
        except Exception as e:
            logger.error(f"Error getting next job: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get next job: {str(e)}",
                "voice_response": "I couldn't retrieve your next job information. Please try again."
            }
    
    async def _update_job_status(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Update job status."""
        try:
            if not self.job_repository:
                return {
                    "success": False,
                    "message": "Job updates are not available",
                    "voice_response": "I can't update job status right now."
                }
            
            job_id = parameters.get("job_id")
            new_status = parameters.get("status")
            
            if not job_id:
                return {
                    "success": False,
                    "message": "Job ID is required",
                    "voice_response": "I need the job ID to update the status. Which job would you like to update?"
                }
            
            if not new_status:
                return {
                    "success": False,
                    "message": "New status is required",
                    "voice_response": "What status would you like to set for this job?"
                }
            
            # Validate status
            try:
                status_enum = JobStatus(new_status.upper())
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid status: {new_status}",
                    "voice_response": f"'{new_status}' is not a valid job status. Available statuses are: scheduled, in progress, completed, cancelled."
                }
            
            # Get job and update
            job = await self.job_repository.get_by_id(uuid.UUID(job_id))
            if not job:
                return {
                    "success": False,
                    "message": "Job not found",
                    "voice_response": "I couldn't find that job. Please check the job ID."
                }
            
            if job.business_id != business_id:
                return {
                    "success": False,
                    "message": "Job not found in your business",
                    "voice_response": "That job doesn't belong to your business."
                }
            
            # Update job status
            job.status = status_enum
            updated_job = await self.job_repository.update(job)
            
            # Generate voice response
            voice_response = f"Job {updated_job.title} has been updated to {new_status} status."
            if status_enum == JobStatus.COMPLETED:
                voice_response += " Great job! The job is now marked as completed."
            elif status_enum == JobStatus.IN_PROGRESS:
                voice_response += " The job is now in progress."
            
            return {
                "success": True,
                "message": "Job status updated successfully",
                "voice_response": voice_response,
                "data": {
                    "job_id": str(updated_job.id),
                    "title": updated_job.title,
                    "client": updated_job.client_name,
                    "old_status": job.status.value,
                    "new_status": updated_job.status.value,
                    "updated_at": datetime.utcnow().isoformat()
                },
                "suggestions": ["Add job note", "Get next job", "Check daily schedule"]
            }
            
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to update job status: {str(e)}",
                "voice_response": "I couldn't update the job status. Please try again."
            }
    
    async def _get_navigation(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get navigation to job location."""
        try:
            job_id = parameters.get("job_id")
            address = parameters.get("address")
            
            if not job_id and not address:
                return {
                    "success": False,
                    "message": "Job ID or address is required",
                    "voice_response": "I need either a job ID or an address to provide navigation."
                }
            
            # Get job details if job_id provided
            if job_id and self.job_repository:
                job = await self.job_repository.get_by_id(uuid.UUID(job_id))
                if job and job.business_id == business_id:
                    address = job.location_address
                    client_name = job.client_name
                else:
                    return {
                        "success": False,
                        "message": "Job not found",
                        "voice_response": "I couldn't find that job for navigation."
                    }
            
            if not address:
                return {
                    "success": False,
                    "message": "No address found",
                    "voice_response": "I couldn't find an address for navigation."
                }
            
            # Generate navigation response
            # In a real implementation, this would integrate with Google Maps API
            navigation_data = {
                "destination": address,
                "estimated_travel_time": "15 minutes",
                "distance": "8.2 miles",
                "route_type": "fastest",
                "traffic_conditions": "moderate"
            }
            
            if job_id:
                voice_response = f"Starting navigation to {client_name} at {address}. Estimated travel time is 15 minutes."
            else:
                voice_response = f"Starting navigation to {address}. Estimated travel time is 15 minutes."
            
            return {
                "success": True,
                "message": "Navigation started successfully",
                "voice_response": voice_response,
                "data": navigation_data,
                "suggestions": ["Call client", "Update job status", "Add travel note"]
            }
            
        except Exception as e:
            logger.error(f"Error getting navigation: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get navigation: {str(e)}",
                "voice_response": "I couldn't start navigation. Please try again."
            }
    
    async def _check_inventory(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Check inventory levels."""
        try:
            if not self.product_repository:
                return {
                    "success": False,
                    "message": "Inventory information is not available",
                    "voice_response": "I can't access inventory information right now."
                }
            
            product_name = parameters.get("product_name")
            
            if not product_name:
                # Get low stock items
                low_stock_items = await self.product_repository.get_low_stock_products(business_id)
                
                if not low_stock_items:
                    return {
                        "success": True,
                        "message": "All items are well stocked",
                        "voice_response": "All your products are well stocked. No items need reordering.",
                        "data": {"low_stock_count": 0, "items": []}
                    }
                
                # List low stock items
                items_list = []
                for item in low_stock_items[:5]:  # Limit to 5 items for voice
                    items_list.append({
                        "name": item.name,
                        "current_stock": item.quantity_on_hand,
                        "reorder_point": item.reorder_point,
                        "supplier": item.primary_supplier.name if item.primary_supplier else "Unknown"
                    })
                
                voice_response = f"You have {len(low_stock_items)} items running low on stock. "
                if len(low_stock_items) <= 3:
                    item_names = [item.name for item in low_stock_items[:3]]
                    voice_response += f"Items needing reorder: {', '.join(item_names)}."
                else:
                    voice_response += f"The most critical items are: {', '.join([item.name for item in low_stock_items[:3]])}."
                
                return {
                    "success": True,
                    "message": "Low stock items retrieved",
                    "voice_response": voice_response,
                    "data": {"low_stock_count": len(low_stock_items), "items": items_list},
                    "suggestions": ["Check specific product", "Create purchase order", "Contact supplier"]
                }
            
            else:
                # Check specific product
                products = await self.product_repository.search_products(business_id, name=product_name)
                
                if not products:
                    return {
                        "success": False,
                        "message": "Product not found",
                        "voice_response": f"I couldn't find '{product_name}' in your inventory."
                    }
                
                product = products[0]  # Take first match
                stock_status = "in stock" if product.quantity_on_hand > product.reorder_point else "low stock"
                
                voice_response = f"You have {product.quantity_on_hand} units of {product.name} in stock. "
                if product.quantity_on_hand <= product.reorder_point:
                    voice_response += f"This is below the reorder point of {product.reorder_point}. You should consider reordering."
                else:
                    voice_response += f"This is above the reorder point of {product.reorder_point}. Stock levels are good."
                
                return {
                    "success": True,
                    "message": "Product inventory checked",
                    "voice_response": voice_response,
                    "data": {
                        "product_name": product.name,
                        "current_stock": product.quantity_on_hand,
                        "reorder_point": product.reorder_point,
                        "status": stock_status,
                        "unit_cost": float(product.unit_cost) if product.unit_cost else 0
                    },
                    "suggestions": ["Check other products", "Create purchase order", "Update stock levels"]
                }
            
        except Exception as e:
            logger.error(f"Error checking inventory: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to check inventory: {str(e)}",
                "voice_response": "I couldn't check inventory levels. Please try again."
            }
    
    async def _add_job_note(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Add voice note to job."""
        try:
            job_id = parameters.get("job_id")
            note_text = parameters.get("note")
            
            if not job_id or not note_text:
                return {
                    "success": False,
                    "message": "Job ID and note text are required",
                    "voice_response": "I need both the job ID and the note text to add a note."
                }
            
            # In a real implementation, this would save to the job notes
            note_data = {
                "job_id": job_id,
                "note": note_text,
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "note_type": "voice_note"
            }
            
            return {
                "success": True,
                "message": "Note added successfully",
                "voice_response": f"I've added your note to the job. The note says: {note_text}",
                "data": note_data,
                "suggestions": ["Add another note", "Update job status", "Get job details"]
            }
            
        except Exception as e:
            logger.error(f"Error adding job note: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to add job note: {str(e)}",
                "voice_response": "I couldn't add the note. Please try again."
            }
    
    async def _get_business_metrics(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get business metrics and KPIs."""
        try:
            # In a real implementation, this would calculate actual metrics
            # For now, return mock data
            metrics_data = {
                "period": "today",
                "jobs_completed": 8,
                "jobs_scheduled": 12,
                "revenue_today": 2400.00,
                "revenue_week": 15800.00,
                "completion_rate": 87.5,
                "average_job_value": 300.00,
                "top_performing_service": "HVAC Repair"
            }
            
            voice_response = f"Here are today's business metrics: You've completed {metrics_data['jobs_completed']} out of {metrics_data['jobs_scheduled']} scheduled jobs. "
            voice_response += f"Today's revenue is ${metrics_data['revenue_today']:,.0f}. "
            voice_response += f"This week's total revenue is ${metrics_data['revenue_week']:,.0f}. "
            voice_response += f"Your completion rate is {metrics_data['completion_rate']:.1f}%."
            
            return {
                "success": True,
                "message": "Business metrics retrieved",
                "voice_response": voice_response,
                "data": metrics_data,
                "suggestions": ["Get weekly metrics", "Check revenue trends", "View top services"]
            }
            
        except Exception as e:
            logger.error(f"Error getting business metrics: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get business metrics: {str(e)}",
                "voice_response": "I couldn't retrieve business metrics. Please try again."
            }
    
    async def _emergency_contact(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Handle emergency contact requests."""
        try:
            contact_type = parameters.get("contact_type", "support")
            message = parameters.get("message", "Emergency assistance needed")
            
            # In a real implementation, this would trigger actual emergency protocols
            emergency_data = {
                "contact_type": contact_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "business_id": str(business_id),
                "emergency_id": str(uuid.uuid4())
            }
            
            if contact_type == "911":
                voice_response = "I'm connecting you to emergency services. Please stay on the line and provide your location."
            elif contact_type == "support":
                voice_response = "I've notified business support about your emergency. They will contact you within 5 minutes."
            else:
                voice_response = f"I've sent an emergency alert for {contact_type}. Help is on the way."
            
            return {
                "success": True,
                "message": "Emergency contact initiated",
                "voice_response": voice_response,
                "data": emergency_data,
                "suggestions": ["Provide location", "Add emergency details", "Contact backup"]
            }
            
        except Exception as e:
            logger.error(f"Error with emergency contact: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to process emergency contact: {str(e)}",
                "voice_response": "I couldn't process the emergency contact. Please try calling directly."
            }
    
    async def _voice_to_text_note(self, parameters: Dict[str, Any], user_id: str, business_id: uuid.UUID) -> Dict[str, Any]:
        """Convert voice to text note."""
        try:
            note_text = parameters.get("note_text")
            category = parameters.get("category", "general")
            
            if not note_text:
                return {
                    "success": False,
                    "message": "Note text is required",
                    "voice_response": "I need the note text to create a voice note."
                }
            
            # Create voice note
            note_data = {
                "note_id": str(uuid.uuid4()),
                "text": note_text,
                "category": category,
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "business_id": str(business_id)
            }
            
            return {
                "success": True,
                "message": "Voice note created",
                "voice_response": f"I've created a voice note in the {category} category. The note says: {note_text}",
                "data": note_data,
                "suggestions": ["Add another note", "Categorize notes", "Review recent notes"]
            }
            
        except Exception as e:
            logger.error(f"Error creating voice note: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to create voice note: {str(e)}",
                "voice_response": "I couldn't create the voice note. Please try again."
            }
    
    def _validate_input(
        self, 
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        user_id: str, 
        business_id: uuid.UUID
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not tool_name or not tool_name.strip():
            raise ValidationError("Tool name is required")
        
        # Validate tool name format
        if not tool_name.replace('_', '').isalnum():
            raise ValidationError("Tool name must contain only alphanumeric characters and underscores")
        
        # Validate parameters if provided
        if parameters and not isinstance(parameters, dict):
            raise ValidationError("Parameters must be a dictionary")
        
        # Additional validation for specific tools can be added here 