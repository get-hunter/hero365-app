# Multi-Voice Agent System Implementation Plan
## Hero365 AI-Native ERP Voice Agent Architecture

### Executive Summary

This document outlines the implementation plan for Hero365's multi-voice agent system, featuring:
1. **Personal Voice Agents** - For users during driving/working using LiveKit Agents framework
2. **Outbound Calling Agents** - For sales, support, and client communication using LiveKit SIP integration

Both systems will leverage Hero365's existing clean architecture use cases for jobs, projects, invoices, estimates, contacts, and more.

---

## System Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   Hero365 Voice Agent System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Personal Agents   │    │    Outbound Calling Agents      │ │
│  │                     │    │                                 │ │
│  │ • Job Management    │    │ • Sales Calls                  │ │
│  │ • Project Updates   │    │ • Customer Support             │ │
│  │ • Invoice Actions   │    │ • Job Rescheduling             │ │
│  │ • Estimate Creation │    │ • Lead Follow-up               │ │
│  │ • Contact Queries   │    │ • Service Reminders            │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                  Shared Voice Agent Infrastructure              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Agent Tools       │    │    LiveKit Integration         │ │
│  │                     │    │                                 │ │
│  │ • Job Tools         │    │ • Agents Framework             │ │
│  │ • Project Tools     │    │ • SIP Integration              │ │
│  │ • Invoice Tools     │    │ • WebRTC Transport             │ │
│  │ • Estimate Tools    │    │ • Telephony Stack              │ │
│  │ • Contact Tools     │    │ • Audio Processing             │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     Existing Hero365 Backend                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Use Cases         │    │    Domain Layer                 │ │
│  │                     │    │                                 │ │
│  │ • Job Management    │    │ • Job Entity                   │ │
│  │ • Project Tracking  │    │ • Project Entity               │ │
│  │ • Invoice Processing│    │ • Invoice Entity               │ │
│  │ • Estimate Creation │    │ • Estimate Entity              │ │
│  │ • Contact Management│    │ • Contact Entity               │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Setup (Week 1-2)

### 1.1 Infrastructure Setup

**Goal**: Establish basic LiveKit infrastructure and voice agent framework

**Tasks**:
- Install LiveKit agents dependencies
- Configure project structure for voice agents
- Set up basic dependency injection integration
- Create voice agent base classes

**Dependencies to Add**:
```bash
# LiveKit Core
uv add "livekit-agents[deepgram,openai,cartesia,silero,turn-detector]~=1.0"
uv add "livekit-plugins-noise-cancellation~=0.2"

# SIP Integration for outbound calling
uv add "livekit-sip~=1.0"

# Additional utilities
uv add "python-dotenv"
uv add "asyncio-mqtt"  # For event handling
```

**Directory Structure**:
```
backend/app/
├── voice_agents/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── agent_context.py
│   │   └── voice_config.py
│   ├── personal/
│   │   ├── __init__.py
│   │   ├── personal_agent.py
│   │   └── mobile_integration.py
│   ├── outbound/
│   │   ├── __init__.py
│   │   ├── sales_agent.py
│   │   ├── support_agent.py
│   │   └── outbound_caller.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── job_tools.py
│   │   ├── project_tools.py
│   │   ├── invoice_tools.py
│   │   ├── estimate_tools.py
│   │   └── contact_tools.py
│   └── utils/
│       ├── __init__.py
│       ├── audio_processing.py
│       └── conversation_context.py
```

### 1.2 Base Voice Agent Implementation

**Base Agent Class**:
```python
# backend/app/voice_agents/core/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, cartesia, deepgram, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

class BaseVoiceAgent(Agent, ABC):
    """Base class for all Hero365 voice agents"""
    
    def __init__(self, 
                 instructions: str,
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any]):
        super().__init__(instructions=instructions)
        self.business_context = business_context
        self.user_context = user_context
        self.session: Optional[AgentSession] = None
        
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Return list of tools available to this agent"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    def create_session(self) -> AgentSession:
        """Create and configure agent session"""
        return AgentSession(
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
```

### 1.3 Tool Integration with Existing Use Cases

**Job Management Tools**:
```python
# backend/app/voice_agents/tools/job_tools.py
from livekit.agents import function_tool
from app.application.use_cases.job import *
from app.infrastructure.config.dependency_injection import get_container

@function_tool
async def create_job(
    title: str,
    description: str,
    client_contact_id: str,
    scheduled_date: str,
    estimated_duration: int
) -> dict:
    """Create a new job for the business"""
    container = get_container()
    create_job_use_case = container.get(CreateJobUseCase)
    
    # Get business context from agent
    business_id = get_current_business_id()
    user_id = get_current_user_id()
    
    job_dto = CreateJobDTO(
        title=title,
        description=description,
        client_contact_id=client_contact_id,
        scheduled_date=scheduled_date,
        estimated_duration=estimated_duration
    )
    
    result = await create_job_use_case.execute(job_dto, business_id, user_id)
    return {
        "success": True,
        "job_id": result.id,
        "message": f"Job '{title}' created successfully and scheduled for {scheduled_date}"
    }

@function_tool
async def get_upcoming_jobs(days_ahead: int = 7) -> dict:
    """Get upcoming jobs for the next specified days"""
    container = get_container()
    job_search_use_case = container.get(JobSearchUseCase)
    
    business_id = get_current_business_id()
    user_id = get_current_user_id()
    
    jobs = await job_search_use_case.get_upcoming_jobs(business_id, user_id, days_ahead)
    
    return {
        "success": True,
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "client": job.client_name,
                "scheduled_date": job.scheduled_date,
                "status": job.status
            } for job in jobs
        ]
    }

@function_tool
async def update_job_status(job_id: str, new_status: str, notes: str = None) -> dict:
    """Update job status with optional notes"""
    container = get_container()
    update_job_use_case = container.get(UpdateJobUseCase)
    
    business_id = get_current_business_id()
    user_id = get_current_user_id()
    
    update_dto = UpdateJobDTO(
        status=new_status,
        notes=notes
    )
    
    result = await update_job_use_case.execute(job_id, update_dto, business_id, user_id)
    return {
        "success": True,
        "message": f"Job status updated to {new_status}"
    }
```

---

## Phase 2: Personal Agent Enhancement (Week 3-4)

### 2.1 Personal Voice Agent Implementation

**Personal Agent for Mobile Users**:
```python
# backend/app/voice_agents/personal/personal_agent.py
from ..core.base_agent import BaseVoiceAgent
from ..tools import job_tools, project_tools, invoice_tools, estimate_tools, contact_tools
from livekit.agents import function_tool

class PersonalVoiceAgent(BaseVoiceAgent):
    """Personal voice agent for mobile users during driving/working"""
    
    def __init__(self, business_context: dict, user_context: dict):
        super().__init__(
            instructions=self.get_system_prompt(),
            business_context=business_context,
            user_context=user_context
        )
    
    def get_tools(self):
        return [
            # Job management
            job_tools.create_job,
            job_tools.get_upcoming_jobs,
            job_tools.update_job_status,
            job_tools.reschedule_job,
            
            # Project management
            project_tools.get_project_status,
            project_tools.update_project_progress,
            project_tools.create_project_milestone,
            
            # Invoice management
            invoice_tools.create_invoice,
            invoice_tools.get_invoice_status,
            invoice_tools.send_invoice_reminder,
            
            # Estimate management
            estimate_tools.create_estimate,
            estimate_tools.convert_estimate_to_invoice,
            estimate_tools.get_pending_estimates,
            
            # Contact management
            contact_tools.get_contact_info,
            contact_tools.add_contact_interaction,
            contact_tools.schedule_follow_up,
            
            # Navigation and productivity
            self.get_driving_directions,
            self.set_reminder,
            self.get_weather_for_job_location,
        ]
    
    def get_system_prompt(self):
        return f"""You are Hero365's personal AI assistant for home service professionals.
        
        CONTEXT:
        - User: {self.user_context.get('name', 'User')}
        - Business: {self.business_context.get('name', 'Business')}
        - Current location: {self.user_context.get('location', 'Unknown')}
        - Business type: {self.business_context.get('type', 'Home services')}
        
        CAPABILITIES:
        You can help with:
        - Job management (create, update, reschedule jobs)
        - Project tracking and updates
        - Invoice creation and management
        - Estimate preparation and conversion
        - Contact management and follow-ups
        - Navigation and scheduling assistance
        - Weather and location-based insights
        
        COMMUNICATION STYLE:
        - Be concise and professional
        - Use hands-free friendly responses
        - Provide clear confirmations for actions
        - Ask clarifying questions when needed
        - Prioritize safety during driving
        
        SAFETY PROTOCOLS:
        - Keep responses brief when user is driving
        - Suggest pull-over for complex tasks
        - Use audio-only confirmations
        - Avoid visual-dependent instructions
        """
    
    @function_tool
    async def get_driving_directions(self, destination: str) -> dict:
        """Get driving directions to a job location or address"""
        # Integration with mapping service
        return {
            "success": True,
            "directions": "Turn left on Main Street, then right on Oak Avenue...",
            "estimated_time": "15 minutes",
            "traffic_conditions": "Light traffic"
        }
    
    @function_tool
    async def set_reminder(self, message: str, time: str) -> dict:
        """Set a voice reminder for the user"""
        return {
            "success": True,
            "message": f"Reminder set: {message} at {time}"
        }
    
    @function_tool
    async def get_weather_for_job_location(self, job_id: str) -> dict:
        """Get weather conditions for a job location"""
        # Integration with weather service
        return {
            "success": True,
            "weather": "Partly cloudy, 72°F",
            "conditions": "Good for outdoor work"
        }
```

### 2.2 Mobile App Integration

**API Endpoints for Mobile Integration**:
```python
# backend/app/api/routes/voice_agents.py
from fastapi import APIRouter, Depends, HTTPException
from livekit import api
from ..middleware.auth_handler import get_current_user
from ..middleware.business_context_middleware import get_current_business
from ...voice_agents.personal.personal_agent import PersonalVoiceAgent

router = APIRouter(prefix="/voice-agents", tags=["voice-agents"])

@router.post("/personal/start-session")
async def start_personal_voice_session(
    request: StartVoiceSessionRequest,
    current_user = Depends(get_current_user),
    current_business = Depends(get_current_business)
):
    """Start a personal voice agent session for mobile user"""
    
    # Create LiveKit room for voice session
    room_service = api.RoomService()
    room_name = f"personal-{current_user.id}-{current_business.id}"
    
    room = await room_service.create_room(
        api.CreateRoomRequest(
            name=room_name,
            empty_timeout=30,
            max_participants=2
        )
    )
    
    # Generate access token for mobile app
    token = api.AccessToken(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET
    )
    token.add_grant(api.VideoGrant(room_join=True, room=room_name))
    token.identity = f"user-{current_user.id}"
    
    # Start personal agent
    agent = PersonalVoiceAgent(
        business_context={
            "id": current_business.id,
            "name": current_business.name,
            "type": current_business.company_size
        },
        user_context={
            "id": current_user.id,
            "name": current_user.email,
            "location": request.location,
            "preferences": request.preferences
        }
    )
    
    return {
        "room_name": room_name,
        "access_token": token.to_jwt(),
        "agent_id": agent.id
    }

@router.post("/personal/send-command")
async def send_voice_command(
    request: VoiceCommandRequest,
    current_user = Depends(get_current_user)
):
    """Send a text command to the personal voice agent"""
    
    # Process command through agent
    # This allows for text-based interaction when voice isn't available
    
    return {
        "success": True,
        "response": "Command processed successfully"
    }
```

---

## Phase 3: Outbound Calling System (Week 5-6)

### 3.1 Outbound Calling Infrastructure

**SIP Integration Setup**:
```python
# backend/app/voice_agents/outbound/outbound_caller.py
from livekit import api
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, cartesia, deepgram
from typing import Dict, Any, Optional

class OutboundCallerAgent(Agent):
    """Base class for outbound calling agents"""
    
    def __init__(self, 
                 call_purpose: str,
                 target_contact: Dict[str, Any],
                 business_context: Dict[str, Any]):
        super().__init__(instructions=self.get_system_prompt())
        self.call_purpose = call_purpose
        self.target_contact = target_contact
        self.business_context = business_context
        self.call_session: Optional[AgentSession] = None
    
    async def initiate_call(self, phone_number: str) -> Dict[str, Any]:
        """Initiate outbound call via LiveKit SIP"""
        
        # Create SIP participant for outbound call
        sip_service = api.SIPService()
        
        create_request = api.CreateSIPParticipantRequest(
            sip_trunk_id=settings.LIVEKIT_SIP_TRUNK_ID,
            sip_call_to=phone_number,
            room_name=f"outbound-{self.call_purpose}-{self.target_contact['id']}",
            participant_identity=f"agent-{self.call_purpose}",
            participant_name=f"Hero365 {self.call_purpose.title()} Agent",
            dtmf="",  # Optional DTMF tones
            play_ringtone=True
        )
        
        participant = await sip_service.create_sip_participant(create_request)
        
        # Initialize agent session
        self.call_session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(model="sonic-2", voice="business-professional"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
        
        return {
            "call_id": participant.participant.sid,
            "status": "initiated",
            "room_name": create_request.room_name
        }
    
    def get_system_prompt(self) -> str:
        return f"""You are a professional AI assistant representing {self.business_context['name']}.
        
        CALL PURPOSE: {self.call_purpose}
        CONTACT: {self.target_contact['name']} - {self.target_contact.get('company', 'Individual')}
        
        GUIDELINES:
        - Be professional and courteous
        - Identify yourself as an AI assistant
        - Respect the person's time
        - Follow compliance and legal requirements
        - Provide clear next steps
        - Handle objections professionally
        - Record call outcomes and follow-up needs
        """
```

### 3.2 Sales Agent Implementation

**Sales-Focused Outbound Agent**:
```python
# backend/app/voice_agents/outbound/sales_agent.py
from .outbound_caller import OutboundCallerAgent
from ..tools import contact_tools, estimate_tools, product_tools
from livekit.agents import function_tool

class SalesAgent(OutboundCallerAgent):
    """Sales-focused outbound calling agent"""
    
    def __init__(self, target_contact: dict, business_context: dict):
        super().__init__(
            call_purpose="sales",
            target_contact=target_contact,
            business_context=business_context
        )
    
    def get_tools(self):
        return [
            # Contact management
            contact_tools.update_contact_interaction,
            contact_tools.update_contact_status,
            contact_tools.schedule_follow_up,
            
            # Product/service tools
            product_tools.get_product_catalog,
            product_tools.check_product_availability,
            product_tools.get_pricing_info,
            
            # Estimate tools
            estimate_tools.create_estimate,
            estimate_tools.send_estimate,
            
            # Sales-specific tools
            self.qualify_lead,
            self.schedule_consultation,
            self.handle_objection,
            self.close_sale
        ]
    
    def get_system_prompt(self):
        return f"""You are Hero365's professional sales AI assistant calling {self.target_contact['name']}.
        
        BUSINESS: {self.business_context['name']} - {self.business_context['type']}
        
        CALL OBJECTIVES:
        - Introduce our home services business
        - Understand customer needs
        - Qualify the lead
        - Schedule consultation or provide estimate
        - Build rapport and trust
        
        SALES PROCESS:
        1. Professional introduction
        2. Permission to continue call
        3. Needs assessment
        4. Service presentation
        5. Handle objections
        6. Close or schedule follow-up
        
        COMPLIANCE:
        - Follow all telemarketing regulations
        - Respect Do Not Call preferences
        - Provide opt-out options
        - Maintain professional standards
        """
    
    @function_tool
    async def qualify_lead(self, 
                          needs: str, 
                          timeline: str, 
                          budget_range: str,
                          decision_maker: bool) -> dict:
        """Qualify lead based on needs, timeline, budget, and authority"""
        
        # Update contact with qualification info
        container = get_container()
        contact_interaction_use_case = container.get(ContactInteractionUseCase)
        
        qualification_data = {
            "needs": needs,
            "timeline": timeline,
            "budget_range": budget_range,
            "decision_maker": decision_maker,
            "qualification_score": self._calculate_qualification_score(needs, timeline, budget_range, decision_maker)
        }
        
        # Record interaction
        await contact_interaction_use_case.record_interaction(
            contact_id=self.target_contact['id'],
            interaction_type="qualification_call",
            details=qualification_data,
            business_id=self.business_context['id']
        )
        
        return {
            "success": True,
            "qualification_score": qualification_data["qualification_score"],
            "next_action": "schedule_consultation" if qualification_data["qualification_score"] >= 7 else "follow_up"
        }
    
    @function_tool
    async def schedule_consultation(self, preferred_date: str, preferred_time: str) -> dict:
        """Schedule in-person consultation"""
        
        # Create job/appointment for consultation
        container = get_container()
        create_job_use_case = container.get(CreateJobUseCase)
        
        job_dto = CreateJobDTO(
            title=f"Consultation - {self.target_contact['name']}",
            description=f"Sales consultation call scheduled from outbound sales agent",
            client_contact_id=self.target_contact['id'],
            scheduled_date=preferred_date,
            scheduled_time=preferred_time,
            job_type="consultation",
            estimated_duration=60
        )
        
        result = await create_job_use_case.execute(job_dto, self.business_context['id'], "sales-agent")
        
        return {
            "success": True,
            "consultation_id": result.id,
            "scheduled_date": preferred_date,
            "scheduled_time": preferred_time,
            "message": "Consultation scheduled successfully"
        }
    
    def _calculate_qualification_score(self, needs: str, timeline: str, budget_range: str, decision_maker: bool) -> int:
        """Calculate lead qualification score (1-10)"""
        score = 0
        
        # Needs assessment (0-3 points)
        if "urgent" in needs.lower() or "immediate" in needs.lower():
            score += 3
        elif "soon" in needs.lower() or "planning" in needs.lower():
            score += 2
        elif "future" in needs.lower() or "considering" in needs.lower():
            score += 1
        
        # Timeline (0-3 points)
        if "week" in timeline.lower() or "month" in timeline.lower():
            score += 3
        elif "quarter" in timeline.lower() or "season" in timeline.lower():
            score += 2
        elif "year" in timeline.lower():
            score += 1
        
        # Budget (0-2 points)
        if "budget" in budget_range.lower() and "approved" in budget_range.lower():
            score += 2
        elif "budget" in budget_range.lower():
            score += 1
        
        # Decision maker (0-2 points)
        if decision_maker:
            score += 2
        
        return min(score, 10)
```

### 3.3 Support Agent Implementation

**Customer Support Outbound Agent**:
```python
# backend/app/voice_agents/outbound/support_agent.py
from .outbound_caller import OutboundCallerAgent
from ..tools import job_tools, contact_tools
from livekit.agents import function_tool

class SupportAgent(OutboundCallerAgent):
    """Customer support outbound calling agent"""
    
    def __init__(self, target_contact: dict, business_context: dict, support_reason: str):
        super().__init__(
            call_purpose="support",
            target_contact=target_contact,
            business_context=business_context
        )
        self.support_reason = support_reason
    
    def get_tools(self):
        return [
            # Job management
            job_tools.reschedule_job,
            job_tools.get_job_details,
            job_tools.update_job_status,
            job_tools.create_follow_up_job,
            
            # Contact management
            contact_tools.update_contact_interaction,
            contact_tools.add_contact_note,
            
            # Support-specific tools
            self.reschedule_appointment,
            self.collect_feedback,
            self.resolve_issue,
            self.schedule_maintenance_reminder
        ]
    
    def get_system_prompt(self):
        return f"""You are Hero365's customer support AI assistant calling {self.target_contact['name']}.
        
        BUSINESS: {self.business_context['name']}
        SUPPORT REASON: {self.support_reason}
        
        CALL OBJECTIVES:
        - Provide excellent customer service
        - Resolve customer issues efficiently
        - Maintain customer satisfaction
        - Collect feedback and improve services
        - Schedule follow-up services as needed
        
        SUPPORT PRINCIPLES:
        - Listen actively to customer concerns
        - Provide clear explanations
        - Offer practical solutions
        - Follow up on commitments
        - Maintain professional empathy
        - Document all interactions
        """
    
    @function_tool
    async def reschedule_appointment(self, job_id: str, new_date: str, new_time: str, reason: str) -> dict:
        """Reschedule customer appointment"""
        
        container = get_container()
        job_scheduling_use_case = container.get(JobSchedulingUseCase)
        
        result = await job_scheduling_use_case.reschedule_job(
            job_id=job_id,
            new_date=new_date,
            new_time=new_time,
            reason=reason,
            business_id=self.business_context['id']
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "new_date": new_date,
            "new_time": new_time,
            "message": "Appointment rescheduled successfully"
        }
    
    @function_tool
    async def collect_feedback(self, service_rating: int, feedback_comments: str, areas_for_improvement: str) -> dict:
        """Collect customer feedback about service"""
        
        container = get_container()
        contact_interaction_use_case = container.get(ContactInteractionUseCase)
        
        feedback_data = {
            "service_rating": service_rating,
            "feedback_comments": feedback_comments,
            "areas_for_improvement": areas_for_improvement,
            "feedback_date": datetime.now().isoformat()
        }
        
        await contact_interaction_use_case.record_interaction(
            contact_id=self.target_contact['id'],
            interaction_type="feedback_call",
            details=feedback_data,
            business_id=self.business_context['id']
        )
        
        return {
            "success": True,
            "rating": service_rating,
            "message": "Feedback collected successfully"
        }
```

---

## Phase 4: Advanced Features (Week 7-8)

### 4.1 Agent Handoff System

**Multi-Agent Orchestration**:
```python
# backend/app/voice_agents/core/agent_orchestrator.py
from typing import Dict, Any, Optional, List
from enum import Enum
from .base_agent import BaseVoiceAgent
from ..personal.personal_agent import PersonalVoiceAgent
from ..outbound.sales_agent import SalesAgent
from ..outbound.support_agent import SupportAgent

class AgentType(Enum):
    PERSONAL = "personal"
    SALES = "sales"
    SUPPORT = "support"
    TECHNICAL = "technical"

class AgentOrchestrator:
    """Orchestrates multiple voice agents and handles handoffs"""
    
    def __init__(self):
        self.active_agents: Dict[str, BaseVoiceAgent] = {}
        self.agent_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_agent(self, 
                          agent_type: AgentType,
                          context: Dict[str, Any]) -> BaseVoiceAgent:
        """Create appropriate agent based on type and context"""
        
        if agent_type == AgentType.PERSONAL:
            return PersonalVoiceAgent(
                business_context=context['business'],
                user_context=context['user']
            )
        elif agent_type == AgentType.SALES:
            return SalesAgent(
                target_contact=context['contact'],
                business_context=context['business']
            )
        elif agent_type == AgentType.SUPPORT:
            return SupportAgent(
                target_contact=context['contact'],
                business_context=context['business'],
                support_reason=context.get('support_reason', 'general')
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    async def handoff_conversation(self, 
                                  current_agent_id: str,
                                  target_agent_type: AgentType,
                                  context: Dict[str, Any],
                                  handoff_reason: str) -> Dict[str, Any]:
        """Handle conversation handoff between agents"""
        
        current_agent = self.active_agents.get(current_agent_id)
        if not current_agent:
            raise ValueError(f"Current agent {current_agent_id} not found")
        
        # Create new agent
        new_agent = await self.create_agent(target_agent_type, context)
        
        # Transfer conversation context
        conversation_history = current_agent.get_conversation_history()
        new_agent.set_conversation_history(conversation_history)
        
        # Add handoff context
        handoff_message = f"This conversation was transferred from {current_agent.agent_type} agent. Reason: {handoff_reason}"
        new_agent.add_context_message(handoff_message)
        
        # Update agent registry
        self.active_agents[new_agent.id] = new_agent
        
        return {
            "success": True,
            "new_agent_id": new_agent.id,
            "handoff_reason": handoff_reason,
            "message": "Conversation transferred successfully"
        }
    
    async def determine_best_agent(self, 
                                  user_intent: str,
                                  conversation_context: Dict[str, Any]) -> AgentType:
        """Determine the best agent type for handling user intent"""
        
        # Use intent classification to determine appropriate agent
        intent_keywords = {
            AgentType.PERSONAL: ["schedule", "reminder", "job", "project", "invoice", "driving", "mobile"],
            AgentType.SALES: ["quote", "estimate", "pricing", "service", "consultation", "new customer"],
            AgentType.SUPPORT: ["reschedule", "problem", "issue", "feedback", "complaint", "help"],
            AgentType.TECHNICAL: ["technical", "equipment", "repair", "maintenance", "troubleshoot"]
        }
        
        # Simple keyword-based classification (can be enhanced with ML)
        user_intent_lower = user_intent.lower()
        
        for agent_type, keywords in intent_keywords.items():
            if any(keyword in user_intent_lower for keyword in keywords):
                return agent_type
        
        # Default to personal agent
        return AgentType.PERSONAL
```

### 4.2 Analytics and Monitoring

**Voice Agent Analytics**:
```python
# backend/app/voice_agents/analytics/voice_analytics.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.domain.repositories.activity_repository import ActivityRepository

@dataclass
class VoiceAgentMetrics:
    agent_type: str
    total_conversations: int
    average_duration: float
    success_rate: float
    user_satisfaction: float
    common_intents: List[str]
    resolution_rate: float

class VoiceAgentAnalytics:
    """Analytics and monitoring for voice agents"""
    
    def __init__(self, activity_repository: ActivityRepository):
        self.activity_repository = activity_repository
    
    async def record_conversation(self, 
                                 agent_id: str,
                                 agent_type: str,
                                 conversation_data: Dict[str, Any]) -> None:
        """Record conversation for analytics"""
        
        activity_dto = {
            "type": "voice_conversation",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "duration": conversation_data.get("duration", 0),
            "success": conversation_data.get("success", False),
            "user_satisfaction": conversation_data.get("user_satisfaction", 0),
            "intents": conversation_data.get("intents", []),
            "outcomes": conversation_data.get("outcomes", []),
            "timestamp": datetime.now()
        }
        
        await self.activity_repository.create_activity(activity_dto)
    
    async def get_agent_metrics(self, 
                               agent_type: str,
                               date_range: int = 30) -> VoiceAgentMetrics:
        """Get metrics for specific agent type"""
        
        start_date = datetime.now() - timedelta(days=date_range)
        
        conversations = await self.activity_repository.get_voice_conversations(
            agent_type=agent_type,
            start_date=start_date
        )
        
        if not conversations:
            return VoiceAgentMetrics(
                agent_type=agent_type,
                total_conversations=0,
                average_duration=0,
                success_rate=0,
                user_satisfaction=0,
                common_intents=[],
                resolution_rate=0
            )
        
        total_conversations = len(conversations)
        total_duration = sum(c.duration for c in conversations)
        successful_conversations = sum(1 for c in conversations if c.success)
        total_satisfaction = sum(c.user_satisfaction for c in conversations if c.user_satisfaction > 0)
        
        # Calculate common intents
        all_intents = []
        for conversation in conversations:
            all_intents.extend(conversation.intents)
        
        intent_counts = {}
        for intent in all_intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        common_intents = sorted(intent_counts.keys(), key=lambda x: intent_counts[x], reverse=True)[:5]
        
        return VoiceAgentMetrics(
            agent_type=agent_type,
            total_conversations=total_conversations,
            average_duration=total_duration / total_conversations,
            success_rate=successful_conversations / total_conversations,
            user_satisfaction=total_satisfaction / len([c for c in conversations if c.user_satisfaction > 0]),
            common_intents=common_intents,
            resolution_rate=successful_conversations / total_conversations
        )
```

---

## Phase 5: Production Deployment (Week 9-10)

### 5.1 Scalability and Performance

**Production Configuration**:
```python
# backend/app/voice_agents/core/production_config.py
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class VoiceAgentConfig:
    # LiveKit Configuration
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    
    # AI Provider Configuration
    openai_api_key: str
    deepgram_api_key: str
    cartesia_api_key: str
    
    # SIP Configuration
    sip_trunk_id: str
    sip_provider: str
    
    # Performance Settings
    max_concurrent_agents: int = 100
    agent_timeout: int = 3600  # 1 hour
    conversation_max_duration: int = 1800  # 30 minutes
    
    # Monitoring
    enable_analytics: bool = True
    log_level: str = "INFO"
    
    # Security
    enable_encryption: bool = True
    jwt_secret: str = os.getenv("JWT_SECRET")

class ProductionVoiceAgentManager:
    """Production-ready voice agent manager"""
    
    def __init__(self, config: VoiceAgentConfig):
        self.config = config
        self.agent_pool = {}
        self.performance_monitor = PerformanceMonitor()
    
    async def create_agent_pool(self) -> None:
        """Create pool of pre-initialized agents for better performance"""
        
        # Pre-warm agent instances
        for agent_type in [AgentType.PERSONAL, AgentType.SALES, AgentType.SUPPORT]:
            for i in range(10):  # 10 agents of each type
                agent = await self.create_agent(agent_type, {})
                self.agent_pool[f"{agent_type.value}_{i}"] = agent
    
    async def get_available_agent(self, agent_type: AgentType) -> BaseVoiceAgent:
        """Get available agent from pool or create new one"""
        
        # Find available agent in pool
        for agent_id, agent in self.agent_pool.items():
            if agent_id.startswith(agent_type.value) and not agent.is_active:
                return agent
        
        # Create new agent if pool is empty
        return await self.create_agent(agent_type, {})
    
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor system performance"""
        
        return {
            "active_agents": len([a for a in self.agent_pool.values() if a.is_active]),
            "total_agents": len(self.agent_pool),
            "memory_usage": self.performance_monitor.get_memory_usage(),
            "cpu_usage": self.performance_monitor.get_cpu_usage(),
            "response_times": self.performance_monitor.get_response_times()
        }
```

### 5.2 Security and Compliance

**Security Implementation**:
```python
# backend/app/voice_agents/security/voice_security.py
from typing import Dict, Any
import hashlib
import hmac
from cryptography.fernet import Fernet
from app.core.config import settings

class VoiceSecurityManager:
    """Handle security for voice agents"""
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def encrypt_conversation(self, conversation_data: str) -> str:
        """Encrypt conversation data"""
        return self.cipher_suite.encrypt(conversation_data.encode()).decode()
    
    def decrypt_conversation(self, encrypted_data: str) -> str:
        """Decrypt conversation data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def validate_caller_identity(self, caller_info: Dict[str, Any]) -> bool:
        """Validate caller identity and permissions"""
        
        # Implement caller ID validation
        # Check against do-not-call lists
        # Validate business context
        
        return True
    
    def sanitize_voice_input(self, voice_input: str) -> str:
        """Sanitize voice input to prevent injection attacks"""
        
        # Remove potentially harmful content
        # Validate input format
        # Check for malicious patterns
        
        return voice_input
    
    def audit_voice_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Audit voice interactions for compliance"""
        
        # Log interaction details
        # Check compliance requirements
        # Store audit trail
        
        pass
```

---

## API Documentation

### Voice Agent Endpoints

**Personal Agent API**:
```http
POST /api/v1/voice-agents/personal/start-session
Content-Type: application/json

{
    "user_id": "user_123",
    "business_id": "business_456",
    "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "preferences": {
        "voice_speed": "normal",
        "language": "en-US",
        "safety_mode": true
    }
}
```

**Outbound Calling API**:
```http
POST /api/v1/voice-agents/outbound/initiate-call
Content-Type: application/json

{
    "agent_type": "sales",
    "contact_id": "contact_789",
    "phone_number": "+1234567890",
    "call_purpose": "follow_up",
    "business_context": {
        "business_id": "business_456",
        "campaign_id": "campaign_123"
    }
}
```

---

## Testing Strategy

### Unit Tests
- Test individual voice agent tools
- Test conversation flow logic
- Test integration with existing use cases

### Integration Tests
- Test LiveKit integration
- Test SIP calling functionality
- Test agent handoff scenarios

### Performance Tests
- Load testing with multiple concurrent agents
- Latency testing for voice responses
- Memory usage monitoring

### User Acceptance Tests
- Test voice recognition accuracy
- Test conversation naturalness
- Test business process completion

---

## Deployment Architecture

### Infrastructure Requirements

**Development Environment**:
- Python 3.10+
- LiveKit Cloud or self-hosted instance
- PostgreSQL database (existing)
- Redis for caching
- Docker containers

**Production Environment**:
- Kubernetes cluster
- Load balancers
- Monitoring stack (Prometheus, Grafana)
- Logging aggregation
- CI/CD pipeline

### Monitoring and Observability

**Key Metrics**:
- Voice agent response times
- Conversation success rates
- Tool execution success rates
- User satisfaction scores
- System resource usage

**Alerting**:
- High error rates
- Poor voice recognition
- System performance degradation
- Security incidents

---

## Future Enhancements

### Phase 6: Advanced AI Features
- Sentiment analysis during conversations
- Predictive analytics for sales leads
- Advanced natural language understanding
- Multi-language support

### Phase 7: Integration Expansion
- CRM system integration
- Calendar synchronization
- Payment processing integration
- Third-party service APIs

### Phase 8: Mobile Optimization
- Offline voice capabilities
- Mobile-specific voice commands
- GPS-based contextual assistance
- Battery optimization

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building Hero365's multi-voice agent system. The incremental approach ensures that each phase builds upon the previous one, allowing for continuous testing and refinement.

Key success factors:
1. **Leverage existing architecture**: Use clean architecture principles and existing use cases
2. **Start simple**: Begin with basic functionality and gradually add complexity
3. **Focus on user experience**: Prioritize natural conversation flow and practical utility
4. **Ensure scalability**: Design for production-level performance and reliability
5. **Maintain security**: Implement proper security measures from the beginning

The system will provide Hero365 users with powerful voice-enabled capabilities for managing their business operations while driving or working, plus sophisticated outbound calling capabilities for sales and customer support. 