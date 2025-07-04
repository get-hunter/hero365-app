"""
Voice Field Notes Use Case

Business logic for voice-to-text field notes and documentation.
Handles field notes, photo tagging, job documentation, and voice memos.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Removed voice_field_notes_dto imports - using direct parameters for simplified architecture
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.entities.job import Job
from app.domain.entities.project import Project
from ...exceptions.application_exceptions import (
    ValidationError, BusinessRuleViolationError, ApplicationError, NotFoundError
)
from .voice_agent_helper_service import VoiceAgentHelperService

logger = logging.getLogger(__name__)


class VoiceFieldNotesUseCase:
    """
    Use case for voice field notes and documentation.
    
    Provides comprehensive field documentation capabilities:
    - Voice-to-text field notes
    - Photo tagging with voice descriptions
    - Job progress documentation
    - Equipment inspection notes
    - Client interaction summaries
    - Work completion reports
    """
    
    def __init__(
        self,
        voice_agent_helper: VoiceAgentHelperService,
        job_repository: Optional[JobRepository] = None,
        project_repository: Optional[ProjectRepository] = None
    ):
        self.voice_agent_helper = voice_agent_helper
        self.job_repository = job_repository
        self.project_repository = project_repository
        logger.info("VoiceFieldNotesUseCase initialized")
    
    async def execute(
        self, 
        note_type: str,
        note_content: str,
        user_id: str, 
        business_id: uuid.UUID,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute voice field notes operations.
        
        Args:
            note_type: Type of note (job_note, progress_update, photo_tag, etc.)
            note_content: Content of the note
            user_id: User creating the notes
            business_id: Business context
            job_id: Optional job ID for job-related notes
            project_id: Optional project ID for project-related notes
            location: Optional location information
            tags: Optional tags for categorization
            priority: Optional priority level
            category: Optional category
            
        Returns:
            Dict with created notes and documentation
            
        Raises:
            ValidationError: If input validation fails
            ApplicationError: If note creation fails
        """
        logger.info(f"Processing voice field notes request for user {user_id}")
        
        try:
            # Validate input data
            self._validate_input(note_type, note_content, user_id, business_id)
            
            # Check voice permissions
            await self.voice_agent_helper.check_voice_permission(
                business_id, user_id, "use_voice_assistant"
            )
            
            # Route to appropriate note handler
            result = await self._route_notes_request(
                note_type, note_content, user_id, business_id, 
                job_id, project_id, location, tags, priority, category
            )
            
            # Create response dictionary
            response = {
                "note_id": result["note_id"],
                "note_type": note_type,
                "success": result["success"],
                "message": result["message"],
                "voice_response": result.get("voice_response", result["message"]),
                "field_note": result.get("field_note"),
                "photo_tags": result.get("photo_tags", []),
                "job_documentation": result.get("job_documentation"),
                "created_date": datetime.utcnow().isoformat(),
                "metadata": result.get("metadata", {})
            }
            
            logger.info(f"Voice field notes processed successfully: {result['note_id']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process voice field notes: {str(e)}")
            
            if isinstance(e, (ValidationError, BusinessRuleViolationError)):
                raise
            
            raise ApplicationError(f"Failed to process voice field notes: {str(e)}")
    
    async def _route_notes_request(
        self, 
        note_type: str,
        note_content: str,
        user_id: str, 
        business_id: uuid.UUID,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route notes request to appropriate handler."""
        params = {
            "note_type": note_type,
            "note_content": note_content,
            "job_id": job_id,
            "project_id": project_id,
            "location": location,
            "tags": tags,
            "priority": priority,
            "category": category
        }
        
        if note_type == "job_note":
            return await self._create_job_note(params, user_id, business_id)
        elif note_type == "progress_update":
            return await self._create_progress_update(params, user_id, business_id)
        elif note_type == "photo_tag":
            return await self._create_photo_tag(params, user_id, business_id)
        elif note_type == "inspection_note":
            return await self._create_inspection_note(params, user_id, business_id)
        elif note_type == "client_interaction":
            return await self._create_client_interaction_note(params, user_id, business_id)
        elif note_type == "completion_report":
            return await self._create_completion_report(params, user_id, business_id)
        elif note_type == "safety_observation":
            return await self._create_safety_observation(params, user_id, business_id)
        elif note_type == "material_usage":
            return await self._create_material_usage_note(params, user_id, business_id)
        elif note_type == "general_memo":
            return await self._create_general_memo(params, user_id, business_id)
        else:
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Unknown note type: {note_type}",
                "voice_response": f"I don't recognize the note type '{note_type}'. Available types include job notes, progress updates, photo tags, and inspection notes."
            }
    
    async def _create_job_note(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create job-specific note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Validate job exists if job_id provided
            job = None
            if params.get("job_id") and self.job_repository:
                job = await self.job_repository.get_by_id(params.get("job_id"))
                if not job or job.business_id != business_id:
                    return {
                        "note_id": note_id,
                        "success": False,
                        "message": "Job not found",
                        "voice_response": "I couldn't find that job to add the note."
                    }
            
            # Create field note
            field_note = {
                "id": note_id,
                "note_type": "job_note",
                "content": params.get("note_content", ""),
                "job_id": params.get("job_id"),
                "project_id": params.get("project_id"),
                "location": params.get("location"),
                "timestamp": datetime.utcnow().isoformat(),
                "created_by": user_id,
                "tags": params.get("tags", []),
                "priority": params.get("priority", "normal"),
                "category": params.get("category", "general")
            }
            
            # In a real implementation, save to database
            # await self.job_repository.add_note(job.id, field_note)
            
            voice_response = f"Job note added successfully. "
            if job:
                voice_response += f"The note has been attached to {job.title}. "
            
            note_content = params.get("note_content", "")
            voice_response += f"Note content: {note_content[:100]}{'...' if len(note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Job note created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "job_title": job.title if job else None,
                    "note_length": len(note_content),
                    "has_location": bool(params.get("location"))
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating job note: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create job note: {str(e)}",
                "voice_response": "I couldn't create the job note. Please try again."
            }
    
    async def _create_progress_update(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create progress update note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Extract progress information
            progress_percentage = request.progress_percentage or 0
            estimated_completion = request.estimated_completion
            
            # Create progress update
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="progress_update",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["progress"],
                priority=request.priority or "normal",
                category="progress_tracking"
            )
            
            # Calculate time estimates
            time_info = ""
            if estimated_completion:
                time_diff = estimated_completion - datetime.utcnow()
                if time_diff.total_seconds() > 0:
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    if hours > 0:
                        time_info = f"Estimated completion in {hours} hours and {minutes} minutes. "
                    else:
                        time_info = f"Estimated completion in {minutes} minutes. "
            
            voice_response = f"Progress update recorded. "
            if progress_percentage > 0:
                voice_response += f"Job is {progress_percentage}% complete. "
            voice_response += time_info
            voice_response += f"Update details: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Progress update created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "progress_percentage": progress_percentage,
                    "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
                    "time_remaining": time_info.strip()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating progress update: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create progress update: {str(e)}",
                "voice_response": "I couldn't create the progress update. Please try again."
            }
    
    async def _create_photo_tag(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create photo tag with voice description."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create photo tag
            photo_tag = VoicePhotoTagDTO(
                id=uuid.UUID(note_id),
                photo_url=request.photo_url,
                description=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or [],
                photo_type=request.photo_type or "general"
            )
            
            # Generate voice response
            voice_response = f"Photo tagged successfully with description: {request.note_content}. "
            if request.photo_type:
                voice_response += f"Photo type: {request.photo_type}. "
            if request.location:
                voice_response += f"Location: {request.location}."
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Photo tag created successfully",
                "voice_response": voice_response,
                "photo_tags": [photo_tag],
                "metadata": {
                    "photo_url": request.photo_url,
                    "photo_type": request.photo_type,
                    "description_length": len(request.note_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating photo tag: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create photo tag: {str(e)}",
                "voice_response": "I couldn't create the photo tag. Please try again."
            }
    
    async def _create_inspection_note(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create equipment inspection note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create inspection note
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="inspection_note",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["inspection"],
                priority=request.priority or "normal",
                category="inspection"
            )
            
            # Check for issues or concerns in the note
            concerns = []
            issue_keywords = ["problem", "issue", "broken", "damaged", "leak", "error", "fault", "concern"]
            note_lower = request.note_content.lower()
            
            for keyword in issue_keywords:
                if keyword in note_lower:
                    concerns.append(keyword)
            
            voice_response = f"Inspection note recorded. "
            if concerns:
                voice_response += f"I noticed some potential concerns in your inspection: {', '.join(concerns[:3])}. "
                voice_response += "You may want to flag this for follow-up. "
            else:
                voice_response += "No immediate concerns detected in the inspection. "
            
            voice_response += f"Inspection details: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Inspection note created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "equipment_type": request.equipment_type,
                    "inspection_type": request.inspection_type or "general",
                    "concerns_detected": concerns,
                    "requires_followup": len(concerns) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating inspection note: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create inspection note: {str(e)}",
                "voice_response": "I couldn't create the inspection note. Please try again."
            }
    
    async def _create_client_interaction_note(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create client interaction summary note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create client interaction note
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="client_interaction",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["client"],
                priority=request.priority or "normal",
                category="client_communication"
            )
            
            # Analyze interaction sentiment (basic keyword analysis)
            positive_keywords = ["satisfied", "happy", "pleased", "good", "excellent", "thank"]
            negative_keywords = ["unhappy", "dissatisfied", "problem", "complaint", "issue", "concern"]
            
            note_lower = request.note_content.lower()
            sentiment = "neutral"
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in note_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in note_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            
            voice_response = f"Client interaction note recorded. "
            if sentiment == "positive":
                voice_response += "The interaction appears to be positive. "
            elif sentiment == "negative":
                voice_response += "I detected some concerns in the interaction. You may want to follow up. "
            
            voice_response += f"Interaction summary: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Client interaction note created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "client_name": request.client_name,
                    "interaction_type": request.interaction_type or "general",
                    "sentiment": sentiment,
                    "requires_followup": sentiment == "negative"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating client interaction note: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create client interaction note: {str(e)}",
                "voice_response": "I couldn't create the client interaction note. Please try again."
            }
    
    async def _create_completion_report(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create job completion report."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create completion report
            job_documentation = JobDocumentationDTO(
                id=uuid.UUID(note_id),
                job_id=request.job_id,
                document_type="completion_report",
                title=f"Completion Report - {request.job_title or 'Job'}",
                content=request.note_content,
                created_by=user_id,
                created_date=datetime.utcnow(),
                work_performed=request.work_performed or [],
                materials_used=request.materials_used or [],
                time_spent=request.time_spent,
                client_signature_required=request.client_signature_required or False,
                photos_attached=bool(request.photo_urls),
                completion_percentage=100
            )
            
            voice_response = f"Job completion report created successfully. "
            if request.time_spent:
                voice_response += f"Total time spent: {request.time_spent} minutes. "
            if request.materials_used:
                voice_response += f"Materials used: {len(request.materials_used)} items. "
            if request.client_signature_required:
                voice_response += "Client signature is required for this completion report. "
            
            voice_response += f"Report summary: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Completion report created successfully",
                "voice_response": voice_response,
                "job_documentation": job_documentation,
                "metadata": {
                    "completion_percentage": 100,
                    "time_spent": request.time_spent,
                    "materials_count": len(request.materials_used or []),
                    "requires_signature": request.client_signature_required
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating completion report: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create completion report: {str(e)}",
                "voice_response": "I couldn't create the completion report. Please try again."
            }
    
    async def _create_safety_observation(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create safety observation note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create safety observation
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="safety_observation",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["safety"],
                priority=request.priority or "high",  # Safety is typically high priority
                category="safety"
            )
            
            # Check for safety concerns
            safety_keywords = ["hazard", "danger", "unsafe", "risk", "accident", "injury", "violation"]
            note_lower = request.note_content.lower()
            
            safety_concerns = [keyword for keyword in safety_keywords if keyword in note_lower]
            
            voice_response = f"Safety observation recorded. "
            if safety_concerns:
                voice_response += f"I detected potential safety concerns: {', '.join(safety_concerns[:3])}. "
                voice_response += "This has been flagged for immediate attention. "
            else:
                voice_response += "No immediate safety concerns detected. "
            
            voice_response += f"Safety observation: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Safety observation created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "safety_level": "high" if safety_concerns else "normal",
                    "concerns_detected": safety_concerns,
                    "requires_immediate_attention": len(safety_concerns) > 0,
                    "flagged_for_review": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating safety observation: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create safety observation: {str(e)}",
                "voice_response": "I couldn't create the safety observation. Please try again."
            }
    
    async def _create_material_usage_note(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create material usage tracking note."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create material usage note
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="material_usage",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["materials"],
                priority=request.priority or "normal",
                category="inventory"
            )
            
            # Extract material information
            materials_used = request.materials_used or []
            total_cost = sum(float(item.get("cost", 0)) for item in materials_used)
            
            voice_response = f"Material usage note recorded. "
            if materials_used:
                voice_response += f"Tracked {len(materials_used)} material items. "
                if total_cost > 0:
                    voice_response += f"Total material cost: ${total_cost:.2f}. "
            
            voice_response += f"Usage details: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "Material usage note created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "materials_count": len(materials_used),
                    "total_cost": total_cost,
                    "materials_used": materials_used,
                    "affects_inventory": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating material usage note: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create material usage note: {str(e)}",
                "voice_response": "I couldn't create the material usage note. Please try again."
            }
    
    async def _create_general_memo(
        self, 
        params: Dict[str, Any], 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create general voice memo."""
        try:
            note_id = str(uuid.uuid4())
            
            # Create general memo
            field_note = FieldNoteDTO(
                id=uuid.UUID(note_id),
                note_type="general_memo",
                content=request.note_content,
                job_id=request.job_id,
                project_id=request.project_id,
                location=request.location,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                tags=request.tags or ["memo"],
                priority=request.priority or "normal",
                category=request.category or "general"
            )
            
            voice_response = f"General memo created successfully. "
            voice_response += f"Memo content: {request.note_content[:100]}{'...' if len(request.note_content) > 100 else ''}"
            
            return {
                "note_id": note_id,
                "success": True,
                "message": "General memo created successfully",
                "voice_response": voice_response,
                "field_note": field_note,
                "metadata": {
                    "memo_length": len(request.note_content),
                    "has_tags": len(request.tags or []) > 0,
                    "category": request.category or "general"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating general memo: {str(e)}")
            return {
                "note_id": str(uuid.uuid4()),
                "success": False,
                "message": f"Failed to create general memo: {str(e)}",
                "voice_response": "I couldn't create the memo. Please try again."
            }
    
    def _validate_input(
        self, 
        note_type: str,
        note_content: str,
        user_id: str, 
        business_id: uuid.UUID
    ) -> None:
        """Validate input parameters."""
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
        
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not note_type or not note_type.strip():
            raise ValidationError("Note type is required")
        
        if not note_content or not note_content.strip():
            raise ValidationError("Note content is required")
        
        # Validate note type
        valid_note_types = [
            "job_note", "progress_update", "photo_tag", "inspection_note",
            "client_interaction", "completion_report", "safety_observation",
            "material_usage", "general_memo"
        ]
        
        if note_type not in valid_note_types:
            raise ValidationError(f"Invalid note type: {note_type}")
        
        # Validate content length
        if len(note_content) > 5000:
            raise ValidationError("Note content must be 5000 characters or less")