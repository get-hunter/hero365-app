"""
Onboarding Progress Service

Manages onboarding session state, progress tracking, and step validation.
Provides persistent state management for multi-step onboarding flows.
"""

import uuid
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

from app.api.dtos.onboarding_dtos import (
    OnboardingStep, OnboardingProgressResponse, OnboardingProfileResponse,
    OnboardingActivityResponse, BusinessDetailsRequest, OnboardingValidationResponse
)

logger = logging.getLogger(__name__)


class OnboardingProgressService:
    """
    Service for managing onboarding progress and session state.
    
    Provides functionality for:
    - Session state persistence
    - Progress calculation
    - Step validation
    - Recommendations and guidance
    """
    
    def __init__(self):
        # In-memory storage for demo - in production, use Redis or database
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_expiry: Dict[str, datetime] = {}
        
        # Step weights for progress calculation
        self._step_weights = {
            OnboardingStep.PROFILE_SELECTION: 25,
            OnboardingStep.ACTIVITY_SELECTION: 25,
            OnboardingStep.BUSINESS_DETAILS: 30,
            OnboardingStep.SERVICE_TEMPLATES: 10,
            OnboardingStep.COMPLETION: 10
        }
        
        logger.info("OnboardingProgressService initialized")
    
    def create_session(
        self, 
        user_id: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new onboarding session."""
        session_id = str(uuid.uuid4())
        expiry = datetime.utcnow() + timedelta(hours=24)
        
        initial_data = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'current_step': OnboardingStep.PROFILE_SELECTION.value,
            'completed_steps': [],
            'selected_profile': None,
            'selected_activities': [],
            'business_details': None,
            'template_selections': None,
            'validation_errors': [],
            'last_activity': datetime.utcnow().isoformat(),
            **(session_data or {})
        }
        
        self._sessions[session_id] = initial_data
        self._session_expiry[session_id] = expiry
        
        logger.info(f"Created onboarding session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        if session_id not in self._sessions:
            return None
        
        # Check expiry
        if session_id in self._session_expiry:
            if datetime.utcnow() > self._session_expiry[session_id]:
                self._cleanup_session(session_id)
                return None
        
        return self._sessions[session_id]
    
    def update_session(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update session data."""
        if session_id not in self._sessions:
            return False
        
        self._sessions[session_id].update(updates)
        self._sessions[session_id]['last_activity'] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated session {session_id}: {list(updates.keys())}")
        return True
    
    def get_progress(self, session_id: str) -> Optional[OnboardingProgressResponse]:
        """Get current onboarding progress for a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        current_step = OnboardingStep(session['current_step'])
        completed_steps = [OnboardingStep(step) for step in session['completed_steps']]
        
        # Calculate progress percentage
        progress_percentage = self._calculate_progress_percentage(current_step, completed_steps)
        
        # Determine if can proceed to next step
        can_proceed, validation_errors = self._validate_current_step(session)
        
        # Get recommendations
        recommended_action = self._get_recommended_action(current_step, session)
        estimated_time = self._estimate_remaining_time(current_step, completed_steps)
        
        return OnboardingProgressResponse(
            session_id=session_id,
            current_step=current_step,
            completed_steps=completed_steps,
            progress_percentage=progress_percentage,
            selected_profile=session.get('selected_profile'),
            selected_activities=session.get('selected_activities', []),
            business_details=session.get('business_details'),
            can_proceed=can_proceed,
            validation_errors=validation_errors,
            recommended_next_action=recommended_action,
            estimated_time_remaining=estimated_time
        )
    
    def advance_step(
        self, 
        session_id: str, 
        next_step: OnboardingStep,
        step_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Advance to the next onboarding step."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        current_step = OnboardingStep(session['current_step'])
        
        # Validate current step before advancing
        can_proceed, _ = self._validate_current_step(session)
        if not can_proceed:
            logger.warning(f"Cannot advance from {current_step} - validation failed")
            return False
        
        # Mark current step as completed
        completed_steps = session['completed_steps']
        if current_step.value not in completed_steps:
            completed_steps.append(current_step.value)
        
        # Update session
        updates = {
            'current_step': next_step.value,
            'completed_steps': completed_steps
        }
        
        if step_data:
            updates.update(step_data)
        
        return self.update_session(session_id, updates)
    
    def set_profile_selection(
        self, 
        session_id: str, 
        profile: OnboardingProfileResponse
    ) -> bool:
        """Set selected profile and advance to activity selection."""
        updates = {
            'selected_profile': profile.dict(),
            'current_step': OnboardingStep.ACTIVITY_SELECTION.value
        }
        
        # Mark profile selection as completed
        session = self.get_session(session_id)
        if session:
            completed_steps = session['completed_steps']
            if OnboardingStep.PROFILE_SELECTION.value not in completed_steps:
                completed_steps.append(OnboardingStep.PROFILE_SELECTION.value)
                updates['completed_steps'] = completed_steps
        
        return self.update_session(session_id, updates)
    
    def set_activity_selections(
        self, 
        session_id: str, 
        activities: List[OnboardingActivityResponse]
    ) -> bool:
        """Set selected activities and advance to business details."""
        updates = {
            'selected_activities': [activity.dict() for activity in activities],
            'current_step': OnboardingStep.BUSINESS_DETAILS.value
        }
        
        # Mark activity selection as completed
        session = self.get_session(session_id)
        if session:
            completed_steps = session['completed_steps']
            if OnboardingStep.ACTIVITY_SELECTION.value not in completed_steps:
                completed_steps.append(OnboardingStep.ACTIVITY_SELECTION.value)
                updates['completed_steps'] = completed_steps
        
        return self.update_session(session_id, updates)
    
    def set_business_details(
        self, 
        session_id: str, 
        details: BusinessDetailsRequest
    ) -> bool:
        """Set business details and advance to service templates."""
        updates = {
            'business_details': details.dict(),
            'current_step': OnboardingStep.SERVICE_TEMPLATES.value
        }
        
        # Mark business details as completed
        session = self.get_session(session_id)
        if session:
            completed_steps = session['completed_steps']
            if OnboardingStep.BUSINESS_DETAILS.value not in completed_steps:
                completed_steps.append(OnboardingStep.BUSINESS_DETAILS.value)
                updates['completed_steps'] = completed_steps
        
        return self.update_session(session_id, updates)
    
    def set_template_selections(
        self, 
        session_id: str, 
        template_data: Dict[str, Any]
    ) -> bool:
        """Set template selections and advance to completion."""
        updates = {
            'template_selections': template_data,
            'current_step': OnboardingStep.COMPLETION.value
        }
        
        # Mark service templates as completed
        session = self.get_session(session_id)
        if session:
            completed_steps = session['completed_steps']
            if OnboardingStep.SERVICE_TEMPLATES.value not in completed_steps:
                completed_steps.append(OnboardingStep.SERVICE_TEMPLATES.value)
                updates['completed_steps'] = completed_steps
        
        return self.update_session(session_id, updates)
    
    def complete_onboarding(self, session_id: str, business_id: str) -> bool:
        """Mark onboarding as completed."""
        updates = {
            'current_step': OnboardingStep.COMPLETION.value,
            'business_id': business_id,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Mark completion step as completed
        session = self.get_session(session_id)
        if session:
            completed_steps = session['completed_steps']
            if OnboardingStep.COMPLETION.value not in completed_steps:
                completed_steps.append(OnboardingStep.COMPLETION.value)
                updates['completed_steps'] = completed_steps
        
        return self.update_session(session_id, updates)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, expiry in self._session_expiry.items():
            if now > expiry:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self._cleanup_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    # Private helper methods
    
    def _cleanup_session(self, session_id: str) -> None:
        """Remove session data."""
        self._sessions.pop(session_id, None)
        self._session_expiry.pop(session_id, None)
    
    def _calculate_progress_percentage(
        self, 
        current_step: OnboardingStep, 
        completed_steps: List[OnboardingStep]
    ) -> float:
        """Calculate progress percentage based on completed steps."""
        total_weight = sum(self._step_weights.values())
        completed_weight = sum(
            self._step_weights[step] for step in completed_steps 
            if step in self._step_weights
        )
        
        # Add partial weight for current step
        current_weight = self._step_weights.get(current_step, 0)
        if current_step not in completed_steps:
            completed_weight += current_weight * 0.1  # 10% for starting the step
        
        return min(100.0, (completed_weight / total_weight) * 100)
    
    def _validate_current_step(
        self, 
        session: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """Validate if current step can proceed to next."""
        current_step = OnboardingStep(session['current_step'])
        errors = []
        
        if current_step == OnboardingStep.PROFILE_SELECTION:
            if not session.get('selected_profile'):
                errors.append("Please select a trade profile")
        
        elif current_step == OnboardingStep.ACTIVITY_SELECTION:
            activities = session.get('selected_activities', [])
            if not activities:
                errors.append("Please select at least one activity")
            elif len(activities) > 6:
                errors.append("Too many activities selected (maximum 6)")
        
        elif current_step == OnboardingStep.BUSINESS_DETAILS:
            details = session.get('business_details')
            if not details:
                errors.append("Please provide business details")
            elif not details.get('name'):
                errors.append("Business name is required")
        
        elif current_step == OnboardingStep.SERVICE_TEMPLATES:
            # Templates are optional, always valid
            pass
        
        elif current_step == OnboardingStep.COMPLETION:
            # All previous steps should be completed
            required_data = ['selected_profile', 'selected_activities', 'business_details']
            for field in required_data:
                if not session.get(field):
                    errors.append(f"Missing required data: {field}")
        
        return len(errors) == 0, errors
    
    def _get_recommended_action(
        self, 
        current_step: OnboardingStep, 
        session: Dict[str, Any]
    ) -> Optional[str]:
        """Get recommended next action for user."""
        if current_step == OnboardingStep.PROFILE_SELECTION:
            return "Choose your primary trade from the popular options"
        
        elif current_step == OnboardingStep.ACTIVITY_SELECTION:
            profile = session.get('selected_profile')
            if profile:
                return f"Select 2-4 activities you want to offer in {profile['name']}"
            return "Select activities for your chosen trade"
        
        elif current_step == OnboardingStep.BUSINESS_DETAILS:
            return "Provide your business information and contact details"
        
        elif current_step == OnboardingStep.SERVICE_TEMPLATES:
            return "Review and select service templates (or skip to auto-adopt popular ones)"
        
        elif current_step == OnboardingStep.COMPLETION:
            return "Complete your business setup"
        
        return None
    
    def _estimate_remaining_time(
        self, 
        current_step: OnboardingStep, 
        completed_steps: List[OnboardingStep]
    ) -> str:
        """Estimate remaining time to complete onboarding."""
        step_times = {
            OnboardingStep.PROFILE_SELECTION: 1,  # minutes
            OnboardingStep.ACTIVITY_SELECTION: 2,
            OnboardingStep.BUSINESS_DETAILS: 3,
            OnboardingStep.SERVICE_TEMPLATES: 1,
            OnboardingStep.COMPLETION: 1
        }
        
        remaining_steps = []
        all_steps = list(OnboardingStep)
        
        # Find current step index
        try:
            current_index = all_steps.index(current_step)
            remaining_steps = all_steps[current_index:]
        except ValueError:
            remaining_steps = all_steps
        
        # Remove already completed steps
        remaining_steps = [
            step for step in remaining_steps 
            if step not in completed_steps
        ]
        
        total_minutes = sum(step_times.get(step, 1) for step in remaining_steps)
        
        if total_minutes <= 1:
            return "Less than 1 minute"
        elif total_minutes <= 5:
            return f"{total_minutes} minutes"
        else:
            return f"{total_minutes // 60}h {total_minutes % 60}m"
