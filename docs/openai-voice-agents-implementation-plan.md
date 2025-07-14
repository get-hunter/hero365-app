# OpenAI Voice Agents SDK Implementation Plan
## Hero365 Multi-Agent Voice System

### Executive Summary

This document outlines the implementation plan for Hero365's voice multi-agent system using OpenAI's latest Agents SDK. The system will feature a TTS-LLM-STT architecture with a triage agent that seamlessly routes to specialist agents for contacts, jobs, estimates, invoices, payments, and more.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Hero365 Voice Multi-Agent System              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Mobile App        │    │    Voice Pipeline               │ │
│  │                     │    │                                 │ │
│  │ • Voice Input       │◄──►│ • OpenAI Voice Model           │ │
│  │ • Audio Output      │    │ • TTS-LLM-STT Pipeline         │ │
│  │ • Context Display   │    │ • Real-time Processing         │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     Multi-Agent Orchestration                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Triage Agent      │    │    Specialist Agents           │ │
│  │                     │    │                                 │ │
│  │ • Intent Detection  │◄──►│ • Contact Agent                │ │
│  │ • Context Analysis  │    │ • Job Agent                    │ │
│  │ • Agent Routing     │    │ • Estimate Agent               │ │
│  │ • Conversation Flow │    │ • Invoice Agent                │ │
│  └─────────────────────┘    │ • Payment Agent                │ │
│                             │ • Project Agent                │ │
│                             │ • Scheduling Agent             │ │
│                             └─────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Shared Context & Tools                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Context Manager   │    │    Agent Tools                 │ │
│  │                     │    │                                 │ │
│  │ • User Context      │    │ • Hero365 Use Cases           │ │
│  │ • Business Context  │    │ • Database Operations          │ │
│  │ • Conversation      │    │ • External APIs               │ │
│  │ • World Context     │    │ • Weather, Maps, etc.         │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Foundation & Setup

### 1.1 Dependencies and Environment Setup

**Install OpenAI Agents SDK:**
```bash
uv add openai-agents[voice]
uv add openai-agents-realtime
uv add openai-agents-tools  # For web search and other built-in tools
```

**Additional dependencies:**
```bash
# Voice processing
uv add sounddevice
uv add numpy
uv add asyncio

# Context management
uv add mem0ai  # For persistent memory
uv add redis   # For session management

# Additional utilities
uv add python-dotenv
uv add pydantic
```

**Environment Configuration:**
```bash
# .env additions
OPENAI_API_KEY=sk-...
OPENAI_VOICE_MODEL=gpt-4o-realtime-preview
OPENAI_SPEECH_MODEL=whisper-1
OPENAI_TTS_MODEL=tts-1-hd
OPENAI_TTS_VOICE=alloy

# Memory and context
MEM0_API_KEY=...
REDIS_URL=redis://localhost:6379

# Hero365 specific
HERO365_API_BASE_URL=http://localhost:8000
WEATHER_API_KEY=...
MAPS_API_KEY=...
```

### 1.2 Project Structure

```
backend/app/
├── voice_agents/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── context_manager.py
│   │   ├── voice_pipeline.py
│   │   └── agent_tools.py
│   ├── triage/
│   │   ├── __init__.py
│   │   ├── triage_agent.py
│   │   └── intent_classifier.py
│   ├── specialists/
│   │   ├── __init__.py
│   │   ├── contact_agent.py
│   │   ├── job_agent.py
│   │   ├── estimate_agent.py
│   │   ├── invoice_agent.py
│   │   ├── payment_agent.py
│   │   ├── project_agent.py
│   │   └── scheduling_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── hero365_tools.py
│   │   ├── external_tools.py
│   │   └── world_context_tools.py
│   └── api/
│       ├── __init__.py
│       ├── voice_endpoints.py
│       └── mobile_integration.py
```

## Phase 2: Core Agent Architecture

### 2.1 Base Agent with Shared Context

```python
# backend/app/voice_agents/core/base_agent.py
from typing import Dict, Any, List, Optional
from openai_agents import Agent, tool
from openai_agents.voice import VoiceAgent
from .context_manager import ContextManager
from .agent_tools import AgentTools

class BaseVoiceAgent(Agent):
    """Base class for all Hero365 voice agents with shared context"""
    
    def __init__(self, 
                 name: str,
                 instructions: str,
                 context_manager: ContextManager,
                 tools: List[Any] = None):
        super().__init__(
            name=name,
            instructions=instructions,
            tools=tools or [],
            model="gpt-4o"
        )
        self.context_manager = context_manager
        self.agent_tools = AgentTools(context_manager)
        
    async def get_context(self) -> Dict[str, Any]:
        """Get current context for agent"""
        return await self.context_manager.get_current_context()
    
    async def update_context(self, updates: Dict[str, Any]):
        """Update context with new information"""
        await self.context_manager.update_context(updates)
    
    def get_system_prompt(self) -> str:
        """Get enhanced system prompt with context"""
        base_prompt = f"""
        You are {self.name}, a specialist AI assistant for Hero365, an AI-native ERP system 
        for home services businesses and independent contractors.
        
        CURRENT CONTEXT:
        {{context}}
        
        INSTRUCTIONS:
        {self.instructions}
        
        BEHAVIOR GUIDELINES:
        - Be conversational and natural - you're speaking, not typing
        - Keep responses concise but informative
        - Always consider the user's current context and location
        - Seamlessly hand off to other specialists when needed
        - Never mention the handoff process to the user
        - Maintain conversation continuity across agents
        """
        return base_prompt
```

### 2.2 Context Manager

```python
# backend/app/voice_agents/core/context_manager.py
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import redis
from mem0 import AsyncMemoryClient

@dataclass
class AgentContext:
    """Shared context across all agents"""
    user_id: str
    business_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    user_info: Dict[str, Any]
    business_info: Dict[str, Any]
    world_context: Dict[str, Any]
    current_location: Optional[Dict[str, Any]] = None
    active_tasks: List[Dict[str, Any]] = None
    
class ContextManager:
    """Manages shared context across all voice agents"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.memory_client = AsyncMemoryClient()
        
    async def initialize_context(self, 
                                user_id: str, 
                                business_id: str,
                                session_id: str) -> AgentContext:
        """Initialize context for a new voice session"""
        
        # Get user and business info
        user_info = await self._get_user_info(user_id)
        business_info = await self._get_business_info(business_id)
        
        # Get world context
        world_context = await self._get_world_context()
        
        # Load relevant memories
        conversation_history = await self._load_conversation_history(
            user_id, business_id
        )
        
        context = AgentContext(
            user_id=user_id,
            business_id=business_id,
            session_id=session_id,
            conversation_history=conversation_history,
            user_info=user_info,
            business_info=business_info,
            world_context=world_context,
            active_tasks=[]
        )
        
        # Store in Redis for quick access
        await self._store_context(context)
        
        return context
    
    async def get_current_context(self) -> Dict[str, Any]:
        """Get current context formatted for agent prompts"""
        context = await self._load_context()
        
        return {
            "user_name": context.user_info.get("name", ""),
            "user_role": context.user_info.get("role", ""),
            "business_name": context.business_info.get("name", ""),
            "business_type": context.business_info.get("type", ""),
            "current_date": context.world_context.get("date", ""),
            "current_time": context.world_context.get("time", ""),
            "location": context.current_location,
            "weather": context.world_context.get("weather", {}),
            "recent_conversation": context.conversation_history[-5:] if context.conversation_history else [],
            "active_tasks": context.active_tasks
        }
    
    async def update_context(self, updates: Dict[str, Any]):
        """Update context with new information"""
        context = await self._load_context()
        
        # Update specific fields
        if "conversation" in updates:
            context.conversation_history.append(updates["conversation"])
        
        if "location" in updates:
            context.current_location = updates["location"]
            
        if "active_task" in updates:
            context.active_tasks.append(updates["active_task"])
            
        # Store updated context
        await self._store_context(context)
        
        # Store important information in long-term memory
        await self._store_in_memory(context, updates)
```

### 2.3 Voice Pipeline

```python
# backend/app/voice_agents/core/voice_pipeline.py
from typing import AsyncGenerator, Dict, Any
from openai_agents.voice import VoiceAgent, VoiceWorkflow
from openai_agents.voice.input import AudioInput
from openai_agents.voice.output import AudioOutput
import asyncio

class Hero365VoicePipeline:
    """Voice pipeline using OpenAI agents SDK with TTS-LLM-STT"""
    
    def __init__(self, triage_agent: VoiceAgent):
        self.triage_agent = triage_agent
        self.workflow = VoiceWorkflow(triage_agent)
        
    async def process_audio(self, audio_input: AudioInput) -> AsyncGenerator[AudioOutput, None]:
        """Process audio input through the multi-agent system"""
        
        # Process through OpenAI voice model
        async for output in self.workflow.process(audio_input):
            yield output
    
    async def start_voice_session(self, 
                                 user_id: str, 
                                 business_id: str) -> str:
        """Start a new voice session"""
        session_id = f"voice_session_{user_id}_{datetime.now().timestamp()}"
        
        # Initialize context
        await self.triage_agent.context_manager.initialize_context(
            user_id=user_id,
            business_id=business_id,
            session_id=session_id
        )
        
        return session_id
    
    async def end_voice_session(self, session_id: str):
        """End voice session and cleanup"""
        # Store final conversation state
        # Clean up resources
        pass
```

## Phase 3: Triage Agent Implementation

### 3.1 Triage Agent with Handoffs

```python
# backend/app/voice_agents/triage/triage_agent.py
from typing import List, Dict, Any
from openai_agents import Agent, tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..specialists import (
    ContactAgent, JobAgent, EstimateAgent, 
    InvoiceAgent, PaymentAgent, ProjectAgent, SchedulingAgent
)

class TriageAgent(BaseVoiceAgent):
    """Main triage agent that routes to specialist agents"""
    
    def __init__(self, context_manager, specialist_agents: Dict[str, Agent]):
        self.specialist_agents = specialist_agents
        
        instructions = """
        You are the main assistant for Hero365. Your role is to understand what the user needs 
        and seamlessly connect them with the right specialist to help them.
        
        You can help users with:
        - Contact management (creating, updating, searching contacts)
        - Job management (scheduling, tracking, updating jobs)
        - Estimates (creating, sending, converting to invoices)
        - Invoicing (creating, sending, tracking payments)
        - Project management (tracking progress, milestones)
        - Scheduling (appointments, availability, calendar management)
        - Payments (processing, tracking, collections)
        
        When you understand what they need, transfer them to the appropriate specialist.
        Never tell the user about the transfer - just seamlessly continue the conversation.
        """
        
        super().__init__(
            name="Hero365 Assistant",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.get_system_status,
                self.get_quick_stats,
                self.search_everything,
                self.search_web  # OpenAI web search for real-time information
            ]
        )
    
    @tool
    async def get_system_status(self) -> str:
        """Get current system status and recent activity"""
        context = await self.get_context()
        
        stats = {
            "pending_jobs": await self.agent_tools.get_pending_jobs_count(),
            "overdue_invoices": await self.agent_tools.get_overdue_invoices_count(),
            "today_appointments": await self.agent_tools.get_today_appointments_count(),
            "recent_activity": await self.agent_tools.get_recent_activity()
        }
        
        return f"""
        Here's your current status:
        - {stats['pending_jobs']} jobs pending
        - {stats['overdue_invoices']} overdue invoices
        - {stats['today_appointments']} appointments today
        - Recent activity: {stats['recent_activity']}
        """
    
    @tool
    async def search_everything(self, query: str) -> str:
        """Search across all Hero365 data"""
        results = await self.agent_tools.universal_search(query)
        return f"Found {len(results)} results for '{query}': {results}"
    
    @tool
    async def search_web(self, query: str) -> str:
        """Search the web for real-time information relevant to business operations"""
        try:
            # Use OpenAI's built-in web search tool for real-time information
            from openai_agents.tools import web_search_preview
            
            result = await web_search_preview(query)
            
            # Format response for voice agent consumption
            summary = result.content[:500]  # Limit for voice response
            sources = [source.url for source in result.sources[:2]]
            
            return f"""
            Based on web search for "{query}":
            
            {summary}
            
            Key sources: {', '.join(sources)}
            """
        except Exception as e:
            return f"Unable to search the web: {str(e)}"
    
    @handoff
    def transfer_to_contact_specialist(self) -> Agent:
        """Transfer to contact management specialist"""
        return self.specialist_agents["contact"]
    
    @handoff
    def transfer_to_job_specialist(self) -> Agent:
        """Transfer to job management specialist"""
        return self.specialist_agents["job"]
    
    @handoff
    def transfer_to_estimate_specialist(self) -> Agent:
        """Transfer to estimate specialist"""
        return self.specialist_agents["estimate"]
    
    @handoff
    def transfer_to_invoice_specialist(self) -> Agent:
        """Transfer to invoice specialist"""
        return self.specialist_agents["invoice"]
    
    @handoff
    def transfer_to_payment_specialist(self) -> Agent:
        """Transfer to payment specialist"""
        return self.specialist_agents["payment"]
    
    @handoff
    def transfer_to_project_specialist(self) -> Agent:
        """Transfer to project specialist"""
        return self.specialist_agents["project"]
    
    @handoff
    def transfer_to_scheduling_specialist(self) -> Agent:
        """Transfer to scheduling specialist"""
        return self.specialist_agents["scheduling"]
```

## Phase 4: Voice Agent Tools Organization

### 4.1 Tools Directory Structure

All Hero365 feature tools will be organized following clean architecture principles and the existing use case patterns:

```
backend/app/voice_agents/
├── tools/
│   ├── __init__.py
│   ├── base_tools.py                    # Base tool infrastructure
│   ├── hero365_tools.py                 # Main tools orchestrator
│   │
│   ├── contact_tools.py                 # Contact management tools
│   ├── job_tools.py                     # Job management tools
│   ├── estimate_tools.py                # Estimate management tools
│   ├── invoice_tools.py                 # Invoice management tools
│   ├── payment_tools.py                 # Payment processing tools
│   ├── project_tools.py                 # Project management tools
│   ├── scheduling_tools.py              # Calendar/scheduling tools
│   ├── product_tools.py                 # Product/inventory tools
│   │
│   ├── world_context_tools.py           # Weather, maps, time, etc.
│   ├── business_intelligence_tools.py    # Analytics and insights
│   └── system_tools.py                  # System status and operations
```

### 4.2 Tool Integration with Existing Use Cases

Each tool file will integrate directly with existing Hero365 use cases:

#### **Contact Tools (contact_tools.py)**
- Maps to `app.application.use_cases.contact.*`
- Tools: create_contact, update_contact, search_contacts, get_contact_details, add_contact_note, schedule_contact_follow_up, get_contact_interaction_history, bulk_contact_operations

#### **Job Tools (job_tools.py)**
- Maps to `app.application.use_cases.job.*`
- Tools: create_job, update_job_status, get_job_details, get_upcoming_jobs, reschedule_job, mark_job_complete, get_jobs_by_status, job_bulk_operations

#### **Estimate Tools (estimate_tools.py)**
- Maps to `app.application.use_cases.estimate.*`
- Tools: create_estimate, update_estimate, get_estimate_details, search_estimates, convert_estimate_to_invoice, get_estimate_templates, send_estimate

#### **Invoice Tools (invoice_tools.py)**
- Maps to `app.application.use_cases.invoice.*`
- Tools: create_invoice, update_invoice, get_invoice_details, search_invoices, process_payment, send_invoice_reminder, get_invoice_status

#### **Payment Tools (payment_tools.py)**
- Maps to payment-related use cases
- Tools: process_payment, get_payment_status, handle_payment_failed, setup_payment_plan, get_payment_history, send_payment_reminder

#### **Project Tools (project_tools.py)**
- Maps to `app.application.use_cases.project.*`
- Tools: create_project, update_project, get_project_details, search_projects, create_project_milestone, assign_project_team, get_project_analytics

#### **Scheduling Tools (scheduling_tools.py)**
- Maps to `app.application.use_cases.scheduling.*`
- Tools: get_available_time_slots, book_appointment, check_availability, create_calendar_event, get_today_schedule, reschedule_appointment, intelligent_scheduling

#### **Product Tools (product_tools.py)**
- Maps to `app.application.use_cases.product.*`
- Tools: create_product, manage_inventory, process_purchase_order, check_stock_levels, get_low_stock_alerts, update_product_pricing

### 4.3 Base Tools Infrastructure

#### **BaseVoiceTools Class**
- Common functionality for all voice agent tools
- Dependency injection integration
- Error handling and exception management
- Context management
- Response formatting for voice output

#### **VoiceToolsRegistry**
- Registry for managing voice agent tools
- Categorization of tools by domain
- Tool discovery and registration
- Dynamic tool loading for agents

#### **voice_tool Decorator**
- Combines OpenAI `@tool` decorator with our registry
- Automatic tool registration by category
- Error handling integration
- Context injection

### 4.4 Tool-to-Use Case Mapping Pattern

Each tool will follow this pattern:

```python
# Example structure (not implemented)
class ContactVoiceTools(BaseVoiceTools):
    @voice_tool("contact")
    async def create_contact(self, name: str, phone: str = None, email: str = None) -> str:
        """Create a new contact"""
        user_id, business_id = await self.get_user_and_business_ids()
        
        # Get use case from container
        create_contact_use_case = self.container.get(CreateContactUseCase)
        
        # Execute use case
        result = await create_contact_use_case.execute(
            CreateContactDTO(
                name=name,
                phone=phone,
                email=email,
                business_id=business_id
            ),
            user_id=user_id
        )
        
        return await self.format_success_response(
            "Contact creation", 
            result,
            f"Created contact {name} with ID {result.id}"
        )
```

### 4.5 World Context and System Tools

#### **World Context Tools (world_context_tools.py)**
- Weather information integration
- Maps and directions
- Current date/time
- Location services
- Reminder system
- **OpenAI Web Search** - Real-time web search capabilities

#### **Business Intelligence Tools (business_intelligence_tools.py)**
- Analytics and reporting
- Performance metrics
- Business insights
- Revenue tracking
- Customer analytics

#### **System Tools (system_tools.py)**
- System status checks
- Health monitoring
- Performance metrics
- Error reporting
- Configuration management

## Phase 5: Specialist Agents Implementation

### 5.1 Contact Agent

```python
# backend/app/voice_agents/specialists/contact_agent.py
from typing import Dict, Any, List
from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent

class ContactAgent(BaseVoiceAgent):
    """Specialist agent for contact management"""
    
    def __init__(self, context_manager):
        instructions = """
        You are the contact management specialist for Hero365. You help users manage their 
        contacts, including creating new contacts, updating existing ones, searching for 
        contacts, and managing contact interactions.
        
        You have access to all contact management tools and can perform any contact-related 
        operation. Always ask for clarification if you need more information.
        """
        
        super().__init__(
            name="Contact Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.create_contact,
                self.update_contact,
                self.search_contacts,
                self.get_contact_details,
                self.add_contact_note,
                self.schedule_contact_follow_up,
                self.get_contact_interaction_history
            ]
        )
    
    @tool
    async def create_contact(self, 
                            name: str, 
                            phone: str = None, 
                            email: str = None,
                            address: str = None,
                            contact_type: str = "client") -> str:
        """Create a new contact"""
        context = await self.get_context()
        
        # Use Hero365 contact creation use case
        result = await self.agent_tools.create_contact({
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "contact_type": contact_type,
            "business_id": context["business_id"]
        })
        
        await self.update_context({
            "conversation": {
                "agent": "contact",
                "action": "create_contact",
                "result": result
            }
        })
        
        return f"Created contact {name} successfully. Contact ID: {result['id']}"
    
    @tool
    async def search_contacts(self, query: str) -> str:
        """Search for contacts"""
        results = await self.agent_tools.search_contacts(query)
        
        if not results:
            return f"No contacts found for '{query}'"
        
        contact_list = []
        for contact in results[:5]:  # Limit to top 5
            contact_list.append(f"- {contact['name']} ({contact['phone']}) - {contact['contact_type']}")
        
        return f"Found {len(results)} contacts:\n" + "\n".join(contact_list)
    
    @tool
    async def get_contact_details(self, contact_id: str) -> str:
        """Get detailed information about a contact"""
        contact = await self.agent_tools.get_contact_by_id(contact_id)
        
        if not contact:
            return f"Contact not found with ID: {contact_id}"
        
        return f"""
        Contact Details:
        - Name: {contact['name']}
        - Phone: {contact['phone']}
        - Email: {contact['email']}
        - Type: {contact['contact_type']}
        - Address: {contact['address']}
        - Last interaction: {contact['last_interaction_date']}
        """
    
    @handoff
    def transfer_to_job_specialist(self) -> Agent:
        """Transfer to job specialist for job-related tasks"""
        return self.specialist_agents["job"]
    
    @handoff
    def transfer_to_scheduling_specialist(self) -> Agent:
        """Transfer to scheduling specialist for appointment booking"""
        return self.specialist_agents["scheduling"]
```

### 4.2 Job Agent

```python
# backend/app/voice_agents/specialists/job_agent.py
from typing import Dict, Any, List
from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent

class JobAgent(BaseVoiceAgent):
    """Specialist agent for job management"""
    
    def __init__(self, context_manager):
        instructions = """
        You are the job management specialist for Hero365. You help users manage their jobs, 
        including creating new jobs, updating job status, scheduling jobs, and tracking job progress.
        
        You understand the job lifecycle and can help with scheduling, status updates, 
        completion tracking, and job-related documentation.
        """
        
        super().__init__(
            name="Job Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.create_job,
                self.update_job_status,
                self.get_job_details,
                self.get_upcoming_jobs,
                self.get_jobs_by_status,
                self.reschedule_job,
                self.add_job_note,
                self.mark_job_complete
            ]
        )
    
    @tool
    async def create_job(self, 
                        title: str,
                        description: str,
                        contact_id: str,
                        scheduled_date: str,
                        estimated_duration: int = 120) -> str:
        """Create a new job"""
        context = await self.get_context()
        
        result = await self.agent_tools.create_job({
            "title": title,
            "description": description,
            "contact_id": contact_id,
            "scheduled_date": scheduled_date,
            "estimated_duration": estimated_duration,
            "business_id": context["business_id"],
            "assigned_user_id": context["user_id"]
        })
        
        return f"Created job '{title}' scheduled for {scheduled_date}. Job ID: {result['id']}"
    
    @tool
    async def get_upcoming_jobs(self, days_ahead: int = 7) -> str:
        """Get upcoming jobs for the next few days"""
        context = await self.get_context()
        
        jobs = await self.agent_tools.get_upcoming_jobs(
            user_id=context["user_id"],
            days_ahead=days_ahead
        )
        
        if not jobs:
            return f"No jobs scheduled for the next {days_ahead} days"
        
        job_list = []
        for job in jobs:
            job_list.append(f"- {job['title']} on {job['scheduled_date']} with {job['contact_name']}")
        
        return f"Upcoming jobs:\n" + "\n".join(job_list)
    
    @tool
    async def update_job_status(self, job_id: str, new_status: str) -> str:
        """Update job status"""
        result = await self.agent_tools.update_job_status(job_id, new_status)
        
        await self.update_context({
            "conversation": {
                "agent": "job",
                "action": "update_status",
                "job_id": job_id,
                "new_status": new_status
            }
        })
        
        return f"Updated job status to {new_status}"
    
    @handoff
    def transfer_to_estimate_specialist(self) -> Agent:
        """Transfer to estimate specialist for creating estimates"""
        return self.specialist_agents["estimate"]
    
    @handoff
    def transfer_to_scheduling_specialist(self) -> Agent:
        """Transfer to scheduling specialist for appointment management"""
        return self.specialist_agents["scheduling"]
```

## Phase 6: Mobile Integration & API Endpoints

### 6.1 Mobile-Optimized Voice API

```python
# backend/app/voice_agents/api/voice_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
from ...core.voice_pipeline import Hero365VoicePipeline
from ...core.context_manager import ContextManager
from ...triage.triage_agent import TriageAgent
from ...specialists import *

router = APIRouter(prefix="/voice", tags=["voice"])

# Initialize voice system
context_manager = ContextManager()
specialist_agents = {
    "contact": ContactAgent(context_manager),
    "job": JobAgent(context_manager),
    "estimate": EstimateAgent(context_manager),
    "invoice": InvoiceAgent(context_manager),
    "payment": PaymentAgent(context_manager),
    "project": ProjectAgent(context_manager),
    "scheduling": SchedulingAgent(context_manager)
}

triage_agent = TriageAgent(context_manager, specialist_agents)
voice_pipeline = Hero365VoicePipeline(triage_agent)

@router.post("/start-session")
async def start_voice_session(
    user_id: str,
    business_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start a new voice session"""
    try:
        session_id = await voice_pipeline.start_voice_session(user_id, business_id)
        
        return {
            "session_id": session_id,
            "status": "active",
            "message": "Voice session started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-audio/{session_id}")
async def process_audio(
    session_id: str,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Process audio input and return agent response"""
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Process through voice pipeline
        audio_input = AudioInput(buffer=audio_data)
        
        async def generate_response():
            async for output in voice_pipeline.process_audio(audio_input):
                if output.type == "audio":
                    yield output.data
                elif output.type == "text":
                    yield f"data: {output.data}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="audio/wav",
            headers={
                "X-Session-ID": session_id,
                "X-Agent-Status": "processing"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end-session/{session_id}")
async def end_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """End voice session"""
    try:
        await voice_pipeline.end_voice_session(session_id)
        
        return {
            "session_id": session_id,
            "status": "ended",
            "message": "Voice session ended successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/{session_id}")
async def get_session_context(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current session context for mobile display"""
    try:
        context = await context_manager.get_current_context()
        
        return {
            "session_id": session_id,
            "context": context,
            "active_tasks": context.get("active_tasks", []),
            "recent_actions": context.get("recent_conversation", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 6.2 Real-time WebSocket Integration

```python
# backend/app/voice_agents/api/websocket_voice.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import asyncio

class VoiceWebSocketManager:
    """Manage WebSocket connections for real-time voice interaction"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.voice_pipeline = Hero365VoicePipeline(triage_agent)
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # Send initial context
        context = await context_manager.get_current_context()
        await websocket.send_json({
            "type": "context_update",
            "data": context
        })
    
    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def handle_voice_message(self, websocket: WebSocket, session_id: str, message: Dict[str, Any]):
        """Handle incoming voice messages"""
        try:
            if message["type"] == "audio_data":
                # Process audio through voice pipeline
                audio_input = AudioInput(buffer=message["data"])
                
                async for output in self.voice_pipeline.process_audio(audio_input):
                    await websocket.send_json({
                        "type": "agent_response",
                        "session_id": session_id,
                        "data": output.data,
                        "output_type": output.type
                    })
            
            elif message["type"] == "context_update":
                # Update context
                await context_manager.update_context(message["data"])
                
                # Broadcast context update
                await websocket.send_json({
                    "type": "context_updated",
                    "data": await context_manager.get_current_context()
                })
        
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })

manager = VoiceWebSocketManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            message = await websocket.receive_json()
            await manager.handle_voice_message(websocket, session_id, message)
            
    except WebSocketDisconnect:
        await manager.disconnect(session_id)
```

## Phase 7: Advanced Features

### 7.1 OpenAI Web Search Integration

All voice agents will have access to real-time web search capabilities using OpenAI's built-in web search tool. This enables agents to:

#### **Real-time Information Access**
- Current market prices for materials and services
- Weather conditions affecting job scheduling
- Business hours and contact information for suppliers
- Recent regulatory changes affecting home services
- Emergency contact information for utilities

#### **Business Intelligence Enhancement**
- Competitor pricing research
- Industry trends and best practices
- Local market conditions and opportunities
- Customer reviews and feedback analysis
- Regulatory compliance updates

#### **Contextual Search Integration**
- Agents can search web when internal data is insufficient
- Results are formatted for voice consumption (concise, relevant)
- Sources are provided for verification
- Search queries are contextually aware of business operations

#### **Example Web Search Use Cases**
```python
# User: "What's the current price of copper pipes?"
# Agent searches web and responds with current market prices

# User: "Are there any weather warnings for our job site today?"
# Agent gets real-time weather alerts for specific location

# User: "What are the permit requirements for electrical work in San Francisco?"
# Agent finds current regulatory information
```

### 7.2 Voice-Friendly Parameter Collection

Creating, editing, and managing complex entities like estimates, invoices, and jobs through voice requires sophisticated conversational parameter collection. Based on current best practices with OpenAI agents SDK, here's how to make this process natural and user-friendly:

#### **Progressive Information Gathering Pattern**

Instead of requiring all parameters at once, agents collect information progressively through natural conversation:

```python
# Example: Creating an estimate through voice conversation
class EstimateBuilder:
    """Builds estimates progressively through conversation"""
    
    def __init__(self):
        self.estimate_data = {
            "client_contact_id": None,
            "line_items": [],
            "notes": None,
            "valid_until": None,
            "discount": None
        }
        self.current_step = "client_identification"
    
    @voice_tool("estimate")
    async def start_estimate_creation(self) -> str:
        """Begin the estimate creation process"""
        context = await self.get_context()
        
        # Check if we can identify client from recent conversation
        recent_contacts = await self._get_recent_contacts(context["user_id"])
        
        if recent_contacts:
            return f"""
            I'll help you create a new estimate. 
            
            I see you've recently worked with these clients:
            {self._format_recent_contacts(recent_contacts)}
            
            Which client is this estimate for? You can say their name or "new client" for someone new.
            """
        else:
            return "I'll help you create a new estimate. Which client is this for?"
    
    @voice_tool("estimate")  
    async def collect_client_info(self, client_input: str) -> str:
        """Collect and validate client information"""
        # Use existing contact search capabilities
        search_results = await self.agent_tools.search_contacts(client_input)
        
        if len(search_results) == 1:
            self.estimate_data["client_contact_id"] = search_results[0]["id"]
            self.current_step = "line_items"
            return f"""
            Perfect! I found {search_results[0]["name"]}.
            
            Now, what services or products should I include in this estimate? 
            You can say them one at a time, like "electrical inspection" or "2 hours of plumbing work".
            """
        elif len(search_results) > 1:
            options = [f"- {contact['name']} ({contact['phone']})" for contact in search_results[:3]]
            return f"""
            I found multiple clients matching "{client_input}":
            {chr(10).join(options)}
            
            Which one did you mean?
            """
        else:
            return f"""
            I couldn't find a client named "{client_input}". 
            
            Would you like me to create a new contact, or try searching with a different name or phone number?
            """
    
    @voice_tool("estimate")
    async def add_line_item(self, item_description: str, quantity: str = "1", rate: str = None) -> str:
        """Add a line item to the estimate"""
        
        # Parse natural language input
        parsed_item = await self._parse_line_item(item_description, quantity, rate)
        
        if not parsed_item["rate"] and not rate:
            # Look up standard rates from business data
            suggested_rate = await self._suggest_rate(parsed_item["description"])
            
            if suggested_rate:
                return f"""
                For "{parsed_item['description']}", I typically see a rate of ${suggested_rate}.
                
                Should I use ${suggested_rate}, or what rate would you like to charge?
                """
            else:
                return f"""
                I've added "{parsed_item['description']}" to the estimate.
                
                What rate should I charge for this item?
                """
        
        self.estimate_data["line_items"].append(parsed_item)
        
        current_total = sum(item["total"] for item in self.estimate_data["line_items"])
        
        return f"""
        Added: {parsed_item['description']} - ${parsed_item['total']}
        
        Current estimate total: ${current_total}
        
        Would you like to add another item, or shall we continue with the estimate details?
        """
```

#### **Context-Aware Default Values**

Leverage existing business and user context to minimize questions:

```python
class ContextAwareParameterCollection:
    """Uses context to reduce parameter collection friction"""
    
    async def smart_defaults_for_job(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart defaults based on context"""
        
        defaults = {}
        
        # Use location context for scheduling
        if context.get("current_location"):
            defaults["location"] = context["current_location"]
            
        # Use recent job patterns
        recent_jobs = await self.agent_tools.get_recent_jobs(context["user_id"], limit=3)
        if recent_jobs:
            defaults["estimated_duration"] = self._average_duration(recent_jobs)
            defaults["typical_services"] = self._common_services(recent_jobs)
        
        # Use business patterns
        business_info = context.get("business_info", {})
        if business_info.get("type") == "hvac":
            defaults["common_tools"] = ["HVAC diagnostic equipment", "Basic hand tools"]
        
        return defaults
    
    @voice_tool("job")
    async def start_job_creation_with_context(self) -> str:
        """Start job creation using context for smart defaults"""
        context = await self.get_context()
        defaults = await self.smart_defaults_for_job(context)
        
        response = "I'll help you create a new job. "
        
        if defaults.get("location"):
            response += f"I see you're near {defaults['location']['city']}. Is this job in the same area? "
        else:
            response += "Where is this job located? "
            
        return response
```

#### **Natural Language Validation Tools**

Create validation tools that understand voice input nuances:

```python
@voice_tool("validation")
async def validate_date_input(self, date_input: str) -> str:
    """Validate and parse natural language date input"""
    
    # Handle various voice input formats
    date_patterns = {
        "today": datetime.now().date(),
        "tomorrow": datetime.now().date() + timedelta(days=1),
        "next week": datetime.now().date() + timedelta(weeks=1),
        "monday": self._next_weekday(0),  # Monday
        "tuesday": self._next_weekday(1),
        # ... more patterns
    }
    
    # Try parsing natural language
    try:
        parsed_date = dateutil.parser.parse(date_input, fuzzy=True).date()
        
        # Validate business rules
        if parsed_date < datetime.now().date():
            return f"The date {parsed_date.strftime('%A, %B %d')} is in the past. Did you mean next {parsed_date.strftime('%A')}?"
        
        if parsed_date > datetime.now().date() + timedelta(days=365):
            return f"That's quite far in the future. Did you mean {parsed_date.strftime('%B %d')} of this year?"
        
        return f"Scheduled for {parsed_date.strftime('%A, %B %d, %Y')}. Is that correct?"
        
    except ValueError:
        return f"I didn't understand '{date_input}' as a date. Could you try something like 'next Monday' or 'March 15th'?"

@voice_tool("validation")
async def validate_currency_input(self, amount_input: str) -> str:
    """Validate and parse currency amounts from voice"""
    
    # Handle voice-to-text currency variations
    currency_replacements = {
        "dollars": "$",
        "dollar": "$", 
        "bucks": "$",
        "hundred": "00",
        "thousand": "000",
        "k": "000",
    }
    
    # Clean up voice-to-text artifacts
    cleaned = amount_input.lower().strip()
    for word, replacement in currency_replacements.items():
        cleaned = cleaned.replace(word, replacement)
    
    # Extract numeric value
    import re
    numbers = re.findall(r'[\d.]+', cleaned)
    
    if numbers:
        try:
            amount = float(numbers[0])
            formatted = f"${amount:,.2f}"
            
            return f"I heard {formatted}. Is that correct?"
        except ValueError:
            pass
    
    return f"I couldn't understand '{amount_input}' as an amount. Could you try something like 'two hundred fifty dollars' or '$250'?"
```

#### **Conversation Flow Management**

Manage complex parameter collection workflows:

```python
class VoiceParameterCollector:
    """Manages parameter collection flow for complex entities"""
    
    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.collected_params = {}
        self.required_fields = self._get_required_fields(entity_type)
        self.optional_fields = self._get_optional_fields(entity_type)
        self.current_field = None
        
    @voice_tool("parameter_collection")
    async def collect_next_parameter(self, user_input: str = None) -> str:
        """Intelligently collect the next required parameter"""
        
        if user_input:
            # Try to extract multiple parameters from user input
            extracted = await self._extract_parameters(user_input)
            self.collected_params.update(extracted)
        
        # Check what's still needed
        missing_required = [field for field in self.required_fields 
                          if field not in self.collected_params]
        
        if not missing_required:
            return await self._handle_completion()
        
        # Get next field to collect
        next_field = missing_required[0]
        return await self._prompt_for_field(next_field)
    
    async def _prompt_for_field(self, field_name: str) -> str:
        """Generate natural voice prompt for specific field"""
        
        prompts = {
            "client_name": "Who is this estimate for?",
            "job_title": "What's the name or title for this job?",
            "description": "Could you describe what work needs to be done?",
            "scheduled_date": "When would you like to schedule this?",
            "estimated_hours": "How many hours do you think this will take?",
            "hourly_rate": "What's your hourly rate for this type of work?",
            "materials_cost": "Are there any materials costs to include?",
            "address": "What's the job site address?",
            "contact_phone": "What's the best phone number to reach them?",
            "notes": "Any special notes or requirements?",
        }
        
        # Add context-aware hints
        context = await self.get_context()
        base_prompt = prompts.get(field_name, f"I need {field_name.replace('_', ' ')}")
        
        # Add examples or hints based on field type
        if field_name == "scheduled_date":
            base_prompt += " You can say something like 'next Tuesday' or 'March 15th'."
        elif field_name == "estimated_hours":
            base_prompt += " You can say something like 'about 3 hours' or 'half a day'."
        elif field_name in ["hourly_rate", "materials_cost"]:
            base_prompt += " Just say the amount, like 'seventy-five dollars' or '$75'."
            
        return base_prompt
    
    async def _extract_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract multiple parameters from natural language input"""
        
        # Use LLM to parse complex input
        extraction_prompt = f"""
        Extract parameter values from this user input for a {self.entity_type}:
        "{user_input}"
        
        Look for these fields: {', '.join(self.required_fields + self.optional_fields)}
        
        Return only the values you can confidently identify.
        """
        
        # This would use the LLM to parse the input
        # Implementation details depend on your specific needs
        extracted = {}
        
        # Example extractions (simplified)
        if "next tuesday" in user_input.lower():
            extracted["scheduled_date"] = self._parse_date("next tuesday")
        
        if "$" in user_input or "dollar" in user_input.lower():
            extracted["amount"] = self._parse_currency(user_input)
            
        return extracted
```

#### **Error Recovery and Clarification**

Handle voice input errors gracefully:

```python
class VoiceErrorRecovery:
    """Handles voice input errors and clarifications"""
    
    @voice_tool("error_recovery")
    async def handle_unclear_input(self, field_name: str, user_input: str, attempt_count: int = 1) -> str:
        """Handle unclear or invalid voice input"""
        
        if attempt_count == 1:
            return f"""
            I didn't quite catch that for {field_name.replace('_', ' ')}. 
            
            Could you repeat that, maybe a bit more slowly?
            """
        
        elif attempt_count == 2:
            # Provide examples or alternatives
            examples = self._get_examples_for_field(field_name)
            return f"""
            I'm still having trouble understanding. Here are some examples of what I'm looking for:
            
            {examples}
            
            Could you try one of these formats?
            """
        
        else:
            # Offer to skip or get help
            return f"""
            I'm having trouble with this field. Would you like to:
            
            1. Skip this for now and come back to it
            2. Have me suggest a default value
            3. Continue without this information
            
            What would you prefer?
            """
    
    def _get_examples_for_field(self, field_name: str) -> str:
        """Get voice-friendly examples for specific fields"""
        
        examples_map = {
            "scheduled_date": "• 'Tomorrow at 2 PM'\n• 'Next Monday morning'\n• 'March 15th'",
            "estimated_hours": "• 'About 3 hours'\n• 'Half a day'\n• 'Two to three hours'",
            "hourly_rate": "• 'Seventy-five dollars'\n• 'One hundred per hour'\n• '$85'",
            "contact_phone": "• 'Five five five, one two three, four five six seven'\n• 'Area code 555, 123-4567'",
            "address": "• '123 Main Street'\n• '456 Oak Avenue, apartment 2B'\n• 'The house on Elm Street'"
        }
        
        return examples_map.get(field_name, "Please provide the information clearly")
```

#### **Integration with Existing Use Cases**

Connect voice parameter collection with Hero365 use cases:

```python
class VoiceParameterToUseCaseAdapter:
    """Adapts voice-collected parameters to existing use cases"""
    
    async def create_estimate_from_voice(self, collected_params: Dict[str, Any]) -> str:
        """Convert voice-collected parameters to estimate creation"""
        
        # Transform voice parameters to DTO format
        create_estimate_dto = CreateEstimateDTO(
            client_contact_id=collected_params["client_contact_id"],
            title=collected_params.get("title", "Service Estimate"),
            description=collected_params.get("description", ""),
            line_items=self._format_line_items(collected_params["line_items"]),
            notes=collected_params.get("notes"),
            valid_until=collected_params.get("valid_until"),
            discount_percentage=collected_params.get("discount", 0)
        )
        
        # Use existing use case
        context = await self.get_context()
        create_estimate_use_case = self.container.get(CreateEstimateUseCase)
        
        result = await create_estimate_use_case.execute(
            create_estimate_dto,
            user_id=context["user_id"]
        )
        
        return f"""
        Perfect! I've created estimate #{result.estimate_number} for {collected_params["client_name"]}.
        
        Total amount: ${result.total_amount}
        Valid until: {result.valid_until}
        
        Would you like me to send this estimate to the client?
        """
```

This approach makes voice parameter collection natural and efficient by:

1. **Progressive Collection**: Gathering information step-by-step in natural conversation
2. **Context Awareness**: Using existing data to reduce required input
3. **Intelligent Parsing**: Understanding various voice input formats
4. **Error Recovery**: Gracefully handling unclear or invalid input
5. **Smart Defaults**: Pre-filling information when possible
6. **Natural Validation**: Confirming details in conversational way

### 7.3 World Context Tools

```python
# backend/app/voice_agents/tools/world_context_tools.py
from typing import Dict, Any
from openai_agents import tool
import httpx
from datetime import datetime
import asyncio

class WorldContextTools:
    """Tools for providing world context to agents"""
    
    def __init__(self):
        self.weather_api_key = settings.WEATHER_API_KEY
        self.maps_api_key = settings.MAPS_API_KEY
    
    @tool
    async def get_current_weather(self, location: str = None) -> str:
        """Get current weather information"""
        if not location:
            # Use user's current location from context
            context = await self.get_context()
            location = context.get("location", {}).get("city", "")
        
        if not location:
            return "Location not available for weather information"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": location,
                        "appid": self.weather_api_key,
                        "units": "metric"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"""
                    Current weather in {location}:
                    - Temperature: {data['main']['temp']}°C
                    - Condition: {data['weather'][0]['description']}
                    - Humidity: {data['main']['humidity']}%
                    - Wind: {data['wind']['speed']} m/s
                    """
                else:
                    return f"Weather information not available for {location}"
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    @tool
    async def get_travel_directions(self, destination: str) -> str:
        """Get travel directions to a destination"""
        context = await self.get_context()
        current_location = context.get("location", {})
        
        if not current_location:
            return "Current location not available"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://maps.googleapis.com/maps/api/directions/json",
                    params={
                        "origin": f"{current_location['lat']},{current_location['lng']}",
                        "destination": destination,
                        "key": self.maps_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["status"] == "OK":
                        route = data["routes"][0]
                        leg = route["legs"][0]
                        
                        return f"""
                        Directions to {destination}:
                        - Distance: {leg['distance']['text']}
                        - Duration: {leg['duration']['text']}
                        - Start: {leg['start_address']}
                        - End: {leg['end_address']}
                        """
                    else:
                        return f"Unable to get directions: {data['status']}"
                else:
                    return "Error getting directions"
        except Exception as e:
            return f"Error getting directions: {str(e)}"
    
    @tool
    async def get_current_date_time(self) -> str:
        """Get current date and time"""
        now = datetime.now()
        return f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"
    
    @tool
    async def search_web(self, query: str) -> str:
        """Search the web for real-time information"""
        try:
            # Use OpenAI's built-in web search tool
            # This integrates with OpenAI agents SDK web search capabilities
            from openai_agents.tools import web_search_preview
            
            result = await web_search_preview(query)
            
            return f"""
            Web search results for "{query}":
            
            {result.content}
            
            Sources: {', '.join([source.url for source in result.sources[:3]])}
            """
        except Exception as e:
            return f"Unable to search the web: {str(e)}"
    
    @tool
    async def set_reminder(self, reminder_text: str, reminder_time: str) -> str:
        """Set a reminder for the user"""
        context = await self.get_context()
        
        # Integration with Hero365 reminder system
        reminder_data = {
            "user_id": context["user_id"],
            "business_id": context["business_id"],
            "reminder_text": reminder_text,
            "reminder_time": reminder_time,
            "created_via": "voice_agent"
        }
        
        # Store reminder (implement based on your reminder system)
        # This could integrate with your existing reminder/notification system
        
        return f"Reminder set: '{reminder_text}' for {reminder_time}"
```

### 7.2 Integration with Existing Use Cases

```python
# backend/app/voice_agents/tools/hero365_tools.py
from typing import Dict, Any, List
from ...application.use_cases.contact import *
from ...application.use_cases.job import *
from ...application.use_cases.estimate import *
from ...application.use_cases.invoice import *
from ...infrastructure.config.dependency_injection import get_container

class Hero365Tools:
    """Integration layer with existing Hero365 use cases"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.container = get_container()
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact using existing use case"""
        create_contact_use_case = self.container.get(CreateContactUseCase)
        
        result = await create_contact_use_case.execute(
            CreateContactDTO(**contact_data)
        )
        
        return result.to_dict()
    
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job using existing use case"""
        create_job_use_case = self.container.get(CreateJobUseCase)
        
        result = await create_job_use_case.execute(
            CreateJobDTO(**job_data)
        )
        
        return result.to_dict()
    
    async def create_estimate(self, estimate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create estimate using existing use case"""
        create_estimate_use_case = self.container.get(CreateEstimateUseCase)
        
        result = await create_estimate_use_case.execute(
            CreateEstimateDTO(**estimate_data)
        )
        
        return result.to_dict()
    
    async def get_upcoming_jobs(self, user_id: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming jobs"""
        get_jobs_use_case = self.container.get(GetJobsUseCase)
        
        result = await get_jobs_use_case.execute(
            GetJobsDTO(
                user_id=user_id,
                date_filter="upcoming",
                days_ahead=days_ahead
            )
        )
        
        return [job.to_dict() for job in result.jobs]
    
    async def universal_search(self, query: str) -> List[Dict[str, Any]]:
        """Universal search across all Hero365 entities"""
        # This would integrate with your existing search functionality
        # or implement a new universal search use case
        
        search_results = []
        
        # Search contacts
        contacts = await self._search_contacts(query)
        search_results.extend([{**contact, "type": "contact"} for contact in contacts])
        
        # Search jobs
        jobs = await self._search_jobs(query)
        search_results.extend([{**job, "type": "job"} for job in jobs])
        
        # Search estimates
        estimates = await self._search_estimates(query)
        search_results.extend([{**estimate, "type": "estimate"} for estimate in estimates])
        
        return search_results[:10]  # Limit results
```

## Phase 8: Testing and Deployment

### 8.1 Testing Strategy

```python
# backend/app/tests/voice_agents/test_voice_pipeline.py
import pytest
from unittest.mock import AsyncMock, patch
from ...voice_agents.core.voice_pipeline import Hero365VoicePipeline
from ...voice_agents.triage.triage_agent import TriageAgent

class TestVoicePipeline:
    """Test suite for voice pipeline functionality"""
    
    @pytest.fixture
    async def voice_pipeline(self):
        """Create test voice pipeline"""
        context_manager = AsyncMock()
        triage_agent = AsyncMock()
        
        return Hero365VoicePipeline(triage_agent)
    
    @pytest.mark.asyncio
    async def test_start_voice_session(self, voice_pipeline):
        """Test starting a voice session"""
        session_id = await voice_pipeline.start_voice_session("user123", "business456")
        
        assert session_id.startswith("voice_session_user123_")
        
    @pytest.mark.asyncio
    async def test_process_audio(self, voice_pipeline):
        """Test audio processing"""
        # Mock audio input
        audio_input = AsyncMock()
        
        # Process audio
        outputs = []
        async for output in voice_pipeline.process_audio(audio_input):
            outputs.append(output)
        
        assert len(outputs) > 0
    
    @pytest.mark.asyncio
    async def test_agent_handoff(self):
        """Test agent handoff functionality"""
        # Test that triage agent can successfully hand off to specialists
        pass
```

### 8.2 Performance Monitoring

```python
# backend/app/voice_agents/monitoring/performance_monitor.py
from typing import Dict, Any
import time
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VoiceMetrics:
    """Voice agent performance metrics"""
    session_id: str
    response_time: float
    agent_switches: int
    successful_completions: int
    error_count: int
    audio_quality_score: float
    
class VoicePerformanceMonitor:
    """Monitor voice agent performance and metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
    
    async def start_session_monitoring(self, session_id: str):
        """Start monitoring a voice session"""
        self.metrics[session_id] = VoiceMetrics(
            session_id=session_id,
            response_time=0.0,
            agent_switches=0,
            successful_completions=0,
            error_count=0,
            audio_quality_score=0.0
        )
    
    async def record_response_time(self, session_id: str, start_time: float):
        """Record response time for a session"""
        if session_id in self.metrics:
            response_time = time.time() - start_time
            self.metrics[session_id].response_time = response_time
            
            # Log slow responses
            if response_time > 3.0:
                self.logger.warning(f"Slow response: {response_time}s for session {session_id}")
    
    async def record_agent_handoff(self, session_id: str, from_agent: str, to_agent: str):
        """Record agent handoff"""
        if session_id in self.metrics:
            self.metrics[session_id].agent_switches += 1
            
            self.logger.info(f"Agent handoff: {from_agent} -> {to_agent} in session {session_id}")
    
    async def generate_performance_report(self, session_id: str) -> Dict[str, Any]:
        """Generate performance report for a session"""
        if session_id not in self.metrics:
            return {}
        
        metrics = self.metrics[session_id]
        
        return {
            "session_id": session_id,
            "average_response_time": metrics.response_time,
            "total_agent_switches": metrics.agent_switches,
            "success_rate": metrics.successful_completions / (metrics.successful_completions + metrics.error_count) if (metrics.successful_completions + metrics.error_count) > 0 else 0,
            "error_count": metrics.error_count,
            "audio_quality_score": metrics.audio_quality_score
        }
```

## Phase 9: Implementation Timeline

### Week 1-2: Foundation Setup
- [ ] Set up OpenAI agents SDK dependencies
- [ ] Create project structure
- [ ] Implement base agent architecture
- [ ] Set up context management system

### Week 3-4: Core Agent Implementation
- [ ] Implement triage agent with handoff capabilities
- [ ] Create specialist agents (Contact, Job, Estimate, Invoice)
- [ ] Integrate with existing Hero365 use cases
- [ ] Implement voice pipeline with TTS-LLM-STT
- [ ] Implement voice-friendly parameter collection system

### Week 5-6: Advanced Features
- [ ] Add world context tools (weather, maps, time)
- [ ] Integrate OpenAI web search across all agents
- [ ] Implement mobile-optimized API endpoints
- [ ] Add WebSocket support for real-time interaction
- [ ] Create performance monitoring system

### Week 7-8: Testing & Optimization
- [ ] Write comprehensive tests
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation completion

### Week 9-10: Deployment & Monitoring
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] User training
- [ ] Performance tuning

## Key Success Factors

1. **Seamless Agent Handoffs**: Users should never know they're being transferred between agents
2. **Context Continuity**: All agents must share and maintain conversation context
3. **Performance**: Response times under 2 seconds for optimal user experience
4. **Reliability**: System must handle errors gracefully and maintain conversation flow
5. **Scalability**: Architecture must support adding new specialist agents easily

This implementation leverages OpenAI's latest agents SDK capabilities while maintaining Hero365's clean architecture principles and existing use case patterns. 