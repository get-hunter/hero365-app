# Hero365 Voice Agent Implementation Guide

## Quick Start Guide

This guide provides practical steps for implementing Hero365's multi-voice agent system using LiveKit agents framework.

## Prerequisites

- Python 3.11+
- LiveKit server setup
- Redis for caching
- Hero365 backend running
- Required API keys (OpenAI, Google Cloud, Twilio)

## Installation & Setup

```bash
# Install LiveKit agents SDK
pip install livekit-agents livekit-api livekit-protocol

# Install additional dependencies
pip install openai google-cloud-speech google-cloud-texttospeech
pip install redis asyncio websockets

# Install Hero365 voice agent package
pip install -e ./backend/voice-agents
```

## Project Structure

```
backend/
├── voice-agents/
│   ├── __init__.py
│   ├── core/
│   │   ├── gateway.py          # Main voice agent gateway
│   │   ├── orchestrator.py     # Agent orchestration
│   │   └── config.py          # Configuration management
│   ├── agents/
│   │   ├── internal_agent.py   # Internal voice agent
│   │   ├── external_agent.py   # External voice agent
│   │   └── base_agent.py      # Base agent class
│   ├── tools/
│   │   ├── job_tool.py        # Job management tools
│   │   ├── invoice_tool.py    # Invoice management tools
│   │   ├── contact_tool.py    # Contact management tools
│   │   └── scheduling_tool.py # Scheduling tools
│   ├── services/
│   │   ├── auth_service.py    # Authentication
│   │   ├── nlp_service.py     # NLP processing
│   │   └── cache_service.py   # Caching layer
│   └── api/
│       ├── routes.py          # API routes
│       └── schemas.py         # Pydantic schemas
```

## Step 1: Create Base Voice Agent

```python
# voice-agents/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from livekit.agents import VoiceAssistant
from livekit.agents.llm import LLM
from livekit.agents.stt import STT
from livekit.agents.tts import TTS

class BaseVoiceAgent(ABC):
    """Base class for all voice agents."""
    
    def __init__(self, business_context: Dict[str, Any]):
        self.business_context = business_context
        self.llm = self._setup_llm()
        self.stt = self._setup_stt()
        self.tts = self._setup_tts()
        
    def _setup_llm(self) -> LLM:
        """Setup language model."""
        from livekit.agents.llm import openai
        return openai.LLM(model="gpt-4")
    
    def _setup_stt(self) -> STT:
        """Setup speech-to-text."""
        from livekit.agents.stt import google
        return google.STT()
    
    def _setup_tts(self) -> TTS:
        """Setup text-to-speech."""
        from livekit.agents.tts import google
        return google.TTS()
    
    @abstractmethod
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice input and return response."""
        pass
```

## Step 2: Implement Internal Voice Agent

```python
# voice-agents/agents/internal_agent.py
from .base_agent import BaseVoiceAgent
from ..tools import JobTool, InvoiceTool, ContactTool, SchedulingTool

class InternalVoiceAgent(BaseVoiceAgent):
    """Internal voice agent for user ERP operations."""
    
    def __init__(self, business_context: Dict[str, Any]):
        super().__init__(business_context)
        self.tools = {
            "job": JobTool(business_context),
            "invoice": InvoiceTool(business_context),
            "contact": ContactTool(business_context),
            "scheduling": SchedulingTool(business_context)
        }
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice input for ERP operations."""
        
        # 1. Convert speech to text
        text = await self.stt.recognize(audio_data)
        
        # 2. Extract intent and parameters
        intent = await self._extract_intent(text)
        
        # 3. Execute operation
        result = await self._execute_operation(intent)
        
        # 4. Generate response
        response_text = await self._generate_response(result)
        response_audio = await self.tts.synthesize(response_text)
        
        return {
            "text": response_text,
            "audio": response_audio,
            "operation_result": result
        }
    
    async def _extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract intent from user speech."""
        
        # Use LLM to extract intent
        prompt = f"""
        Extract the intent and parameters from this user command:
        "{text}"
        
        Available intents:
        - create_job: Create a new job
        - update_job: Update job status
        - create_invoice: Create invoice
        - check_schedule: Check schedule
        - inventory_check: Check inventory
        
        Return JSON with intent and parameters.
        """
        
        response = await self.llm.chat([{"role": "user", "content": prompt}])
        return json.loads(response.content)
    
    async def _execute_operation(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute business operation based on intent."""
        
        intent_name = intent.get("intent")
        parameters = intent.get("parameters", {})
        
        if intent_name == "create_job":
            return await self.tools["job"].create_job(parameters)
        elif intent_name == "update_job":
            return await self.tools["job"].update_job_status(parameters)
        elif intent_name == "create_invoice":
            return await self.tools["invoice"].create_invoice(parameters)
        elif intent_name == "check_schedule":
            return await self.tools["scheduling"].get_schedule(parameters)
        else:
            return {"success": False, "message": "Unknown intent"}
```

## Step 3: Create Voice Agent Tools

```python
# voice-agents/tools/job_tool.py
from typing import Dict, Any
from hero365.infrastructure.config.dependency_injection import get_container

class JobTool:
    """Tool for job management operations."""
    
    def __init__(self, business_context: Dict[str, Any]):
        self.business_context = business_context
        self.container = get_container()
    
    async def create_job(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create new job via voice command."""
        
        try:
            # Get use case
            create_job_use_case = self.container.get_create_job_use_case()
            
            # Create job
            job = await create_job_use_case.execute(
                business_id=self.business_context["business_id"],
                job_data=parameters,
                user_id=self.business_context["user_id"]
            )
            
            return {
                "success": True,
                "message": f"Job #{job.job_number} created successfully",
                "data": job.to_dict()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create job: {str(e)}"
            }
    
    async def update_job_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update job status via voice command."""
        
        try:
            update_job_use_case = self.container.get_update_job_use_case()
            
            job = await update_job_use_case.execute(
                business_id=self.business_context["business_id"],
                job_id=parameters["job_id"],
                updates={"status": parameters["status"]},
                user_id=self.business_context["user_id"]
            )
            
            return {
                "success": True,
                "message": f"Job #{job.job_number} status updated to {parameters['status']}",
                "data": job.to_dict()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update job: {str(e)}"
            }
```

## Step 4: Setup Voice Agent Gateway

```python
# voice-agents/core/gateway.py
from fastapi import FastAPI, HTTPException, Depends
from livekit import RoomService, AccessToken
from .orchestrator import AgentOrchestrator
from ..services.auth_service import VoiceAgentAuthService

app = FastAPI(title="Hero365 Voice Agent Gateway")

orchestrator = AgentOrchestrator()
auth_service = VoiceAgentAuthService()

@app.post("/voice/start-session")
async def start_voice_session(
    token: str,
    business_id: str,
    agent_type: str = "internal"
):
    """Start a new voice agent session."""
    
    try:
        # Authenticate user
        user_context = await auth_service.authenticate_voice_request(token)
        
        # Validate business access
        business_context = await auth_service.validate_business_access(
            user_context, business_id
        )
        
        # Create LiveKit room
        room_service = RoomService()
        room_name = f"voice-session-{user_context.user_id}-{business_id}"
        
        # Get or create agent
        agent = await orchestrator.get_agent(agent_type, business_context)
        
        # Generate access token
        access_token = AccessToken()
        access_token.with_identity(user_context.user_id)
        access_token.with_grants(RoomGrants(room_join=True, room=room_name))
        
        return {
            "room_name": room_name,
            "token": access_token.to_jwt(),
            "agent_id": agent.agent_id,
            "session_id": f"session-{user_context.user_id}-{business_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/voice/process-command")
async def process_voice_command(
    session_id: str,
    audio_data: bytes,
    token: str
):
    """Process voice command."""
    
    try:
        # Authenticate request
        user_context = await auth_service.authenticate_voice_request(token)
        
        # Get active agent
        agent = await orchestrator.get_agent_by_session(session_id)
        
        # Process voice input
        result = await agent.process_voice_input(audio_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Step 5: Configuration

```python
# voice-agents/core/config.py
from pydantic import BaseSettings

class VoiceAgentSettings(BaseSettings):
    """Voice agent configuration."""
    
    # LiveKit settings
    livekit_url: str = "wss://hero365.livekit.cloud"
    livekit_api_key: str
    livekit_secret: str
    
    # AI service settings
    openai_api_key: str
    google_cloud_project: str
    
    # Hero365 integration
    hero365_api_url: str = "http://localhost:8000"
    hero365_api_key: str
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

settings = VoiceAgentSettings()
```

## Step 6: Docker Setup

```dockerfile
# voice-agents/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Install voice agents package
RUN pip install -e .

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "voice_agents.core.gateway:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Step 7: Testing Setup

```python
# tests/test_voice_agent.py
import pytest
from voice_agents.agents.internal_agent import InternalVoiceAgent

@pytest.fixture
def business_context():
    return {
        "business_id": "test-business-id",
        "user_id": "test-user-id",
        "permissions": ["create_job", "update_job", "create_invoice"]
    }

@pytest.fixture
def internal_agent(business_context):
    return InternalVoiceAgent(business_context)

@pytest.mark.asyncio
async def test_create_job_intent(internal_agent):
    """Test job creation via voice command."""
    
    # Mock audio data (in real test, use actual audio)
    audio_data = b"mock_audio_data"
    
    # Mock speech-to-text result
    text = "Create a new job for John Smith at 123 Main Street"
    
    # Test intent extraction
    intent = await internal_agent._extract_intent(text)
    
    assert intent["intent"] == "create_job"
    assert "John Smith" in intent["parameters"]["customer_name"]
    assert "123 Main Street" in intent["parameters"]["address"]

@pytest.mark.asyncio
async def test_job_tool_create_job():
    """Test job creation tool."""
    
    from voice_agents.tools.job_tool import JobTool
    
    business_context = {
        "business_id": "test-business",
        "user_id": "test-user"
    }
    
    job_tool = JobTool(business_context)
    
    parameters = {
        "customer_name": "John Smith",
        "address": "123 Main Street",
        "description": "Plumbing repair"
    }
    
    result = await job_tool.create_job(parameters)
    
    assert result["success"] is True
    assert "Job #" in result["message"]
```

## Step 8: Deployment

```yaml
# docker-compose.voice-agents.yml
version: '3.8'

services:
  voice-agent-gateway:
    build: ./voice-agents
    ports:
      - "8080:8080"
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_SECRET=${LIVEKIT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HERO365_API_URL=${HERO365_API_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
      - livekit

  livekit:
    image: livekit/livekit-server:latest
    ports:
      - "7880:7880"
    environment:
      - LIVEKIT_CONFIG_FILE=/etc/livekit.yaml
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Mobile App Integration

```swift
// iOS Integration Example
import LiveKitClient

class VoiceAgentService {
    private var room: Room?
    private var localAudioTrack: LocalAudioTrack?
    
    func startVoiceSession(token: String, roomName: String) async {
        room = Room()
        
        // Connect to LiveKit room
        try await room?.connect(
            url: "wss://hero365.livekit.cloud",
            token: token
        )
        
        // Enable microphone
        localAudioTrack = LocalAudioTrack.createTrack()
        try await room?.localParticipant.publishAudioTrack(track: localAudioTrack!)
        
        // Listen for voice agent responses
        room?.add(delegate: self)
    }
    
    func sendVoiceCommand(audioData: Data) async {
        // Send audio to voice agent via API
        let response = await Hero365API.shared.processVoiceCommand(
            audioData: audioData,
            sessionId: currentSessionId
        )
        
        // Handle response
        if let audioResponse = response.audioData {
            playAudioResponse(audioResponse)
        }
    }
}
```

## Next Steps

1. **Start with Step 1**: Implement base voice agent class
2. **Add LiveKit integration**: Set up LiveKit server and client connections
3. **Create voice tools**: Implement job, invoice, and scheduling tools
4. **Test voice commands**: Create comprehensive test suite
5. **Deploy and monitor**: Set up production deployment with monitoring

This implementation guide provides the foundation for building Hero365's voice agent system. Follow each step sequentially and refer to the architecture document for detailed system design. 