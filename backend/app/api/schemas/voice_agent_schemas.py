"""
Voice Agent API Schemas

This module provides Pydantic schemas for voice agent API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class LocationSchema(BaseModel):
    """Location information schema"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    
    class Config:
        schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class VoiceAgentStartRequest(BaseModel):
    """Request schema for starting a voice agent"""
    
    is_driving: bool = Field(default=False, description="Whether user is currently driving")
    safety_mode: bool = Field(default=True, description="Enable safety mode for driving")
    voice_speed: Optional[str] = Field(default="normal", description="Voice speed: slow, normal, fast")
    max_duration: Optional[int] = Field(default=3600, description="Maximum conversation duration in seconds")
    enable_noise_cancellation: bool = Field(default=True, description="Enable noise cancellation")
    location: Optional[LocationSchema] = Field(default=None, description="User's current location")
    
    class Config:
        schema_extra = {
            "example": {
                "is_driving": True,
                "safety_mode": True,
                "voice_speed": "normal",
                "max_duration": 3600,
                "enable_noise_cancellation": True,
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            }
        }


class LiveKitConnectionSchema(BaseModel):
    """LiveKit connection information schema"""
    room_name: str = Field(..., description="LiveKit room name")
    room_url: str = Field(..., description="LiveKit server URL")
    user_token: str = Field(..., description="User access token for room")
    room_sid: str = Field(..., description="Room session identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "room_name": "voice-session-user123-a1b2c3d4",
                "room_url": "wss://hero365.livekit.cloud",
                "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "room_sid": "RM_abc123def456"
            }
        }


class VoiceAgentStartResponse(BaseModel):
    """Response schema for starting a voice agent"""
    
    success: bool = Field(..., description="Whether agent started successfully")
    agent_id: str = Field(..., description="Unique agent identifier")
    greeting: str = Field(..., description="Personalized greeting message")
    available_tools: int = Field(..., description="Number of available tools")
    config: Dict[str, Any] = Field(..., description="Agent configuration settings")
    livekit_connection: Optional[LiveKitConnectionSchema] = Field(default=None, description="LiveKit room connection details")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "agent_id": "agent_123456",
                "greeting": "Hello John! I'm your ABC Home Services voice assistant. How can I help you today?",
                "available_tools": 11,
                "config": {
                    "voice_profile": "a0e99841-438c-4a64-b679-ae501e7d6091",
                    "voice_model": "sonic-2",
                    "safety_mode": True,
                    "max_duration": 3600
                },
                "livekit_connection": {
                    "room_name": "voice-session-user123-a1b2c3d4",
                    "room_url": "wss://hero365.livekit.cloud",
                    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "room_sid": "RM_abc123def456"
                },
                "message": "Voice agent started successfully"
            }
        }


class VoiceAgentStatusRequest(BaseModel):
    """Request schema for getting agent status"""
    
    agent_id: str = Field(..., description="Agent identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123456"
            }
        }


class VoiceAgentStatusResponse(BaseModel):
    """Response schema for agent status"""
    
    success: bool = Field(..., description="Whether status retrieved successfully")
    agent_id: str = Field(..., description="Agent identifier")
    is_active: bool = Field(..., description="Whether agent is currently active")
    conversation_stage: str = Field(..., description="Current conversation stage")
    duration: int = Field(..., description="Conversation duration in seconds")
    interactions_count: int = Field(..., description="Number of interactions")
    current_intent: Optional[str] = Field(default=None, description="Current detected intent")
    user_context: Dict[str, Any] = Field(..., description="Current user context")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "agent_id": "agent_123456",
                "is_active": True,
                "conversation_stage": "information_gathering",
                "duration": 120,
                "interactions_count": 5,
                "current_intent": "job_management",
                "user_context": {
                    "is_driving": True,
                    "safety_mode": True
                },
                "message": "Agent status retrieved successfully"
            }
        }


class VoiceAgentStopRequest(BaseModel):
    """Request schema for stopping a voice agent"""
    
    agent_id: str = Field(..., description="Agent identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123456"
            }
        }


class VoiceAgentStopResponse(BaseModel):
    """Response schema for stopping a voice agent"""
    
    success: bool = Field(..., description="Whether agent stopped successfully")
    agent_id: str = Field(..., description="Agent identifier")
    session_summary: Dict[str, Any] = Field(..., description="Session summary statistics")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "agent_id": "agent_123456",
                "session_summary": {
                    "duration": 300,
                    "interactions": 8,
                    "completed_tasks": 2
                },
                "message": "Voice agent stopped successfully"
            }
        }


class VoiceAgentConfigRequest(BaseModel):
    """Request schema for updating agent configuration"""
    
    agent_id: str = Field(..., description="Agent identifier")
    voice_profile: Optional[str] = Field(default=None, description="Voice profile ID")
    voice_model: Optional[str] = Field(default=None, description="Voice model")
    safety_mode: Optional[bool] = Field(default=None, description="Safety mode setting")
    voice_speed: Optional[str] = Field(default=None, description="Voice speed setting")
    location: Optional[LocationSchema] = Field(default=None, description="Updated location")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123456",
                "voice_profile": "b7d50908-b17c-442d-ad8d-810c63997ed9",
                "voice_model": "sonic-2",
                "safety_mode": False,
                "voice_speed": "fast",
                "location": {
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            }
        }


class VoiceAgentConfigResponse(BaseModel):
    """Response schema for updating agent configuration"""
    
    success: bool = Field(..., description="Whether configuration updated successfully")
    agent_id: str = Field(..., description="Agent identifier")
    updated_config: Dict[str, Any] = Field(..., description="Updated configuration settings")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "agent_id": "agent_123456",
                "updated_config": {
                    "voice_profile": "b7d50908-b17c-442d-ad8d-810c63997ed9",
                    "voice_model": "sonic-2",
                    "safety_mode": False,
                    "voice_speed": "fast"
                },
                "message": "Voice agent configuration updated successfully"
            }
        }


class VoiceToolSchema(BaseModel):
    """Schema for voice agent tools"""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "create_job",
                "description": "Create new jobs"
            }
        }


class VoiceToolCategorySchema(BaseModel):
    """Schema for voice agent tool categories"""
    
    job_management: List[VoiceToolSchema] = Field(..., description="Job management tools")
    personal_assistant: List[VoiceToolSchema] = Field(..., description="Personal assistant tools")
    
    class Config:
        schema_extra = {
            "example": {
                "job_management": [
                    {"name": "create_job", "description": "Create new jobs"},
                    {"name": "get_upcoming_jobs", "description": "View upcoming jobs"}
                ],
                "personal_assistant": [
                    {"name": "get_current_time", "description": "Get current time"},
                    {"name": "set_reminder", "description": "Set voice reminders"}
                ]
            }
        }


class VoiceAgentHealthResponse(BaseModel):
    """Response schema for voice agent health check"""
    
    success: bool = Field(..., description="Whether system is healthy")
    status: str = Field(..., description="System status")
    active_agents: int = Field(..., description="Number of active agents")
    system_info: Dict[str, bool] = Field(..., description="System component status")
    message: str = Field(..., description="Health status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "status": "healthy",
                "active_agents": 3,
                "system_info": {
                    "livekit_agents_available": True,
                    "job_tools_available": True,
                    "personal_agent_available": True
                },
                "message": "Voice agent system is operational"
            }
        }


class VoiceAgentAvailableToolsResponse(BaseModel):
    """Response schema for available tools endpoint"""
    
    success: bool = Field(..., description="Whether tools retrieved successfully")
    total_tools: int = Field(..., description="Total number of available tools")
    categories: VoiceToolCategorySchema = Field(..., description="Tool categories")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_tools": 11,
                "categories": {
                    "job_management": [
                        {"name": "create_job", "description": "Create new jobs"},
                        {"name": "get_upcoming_jobs", "description": "View upcoming jobs"}
                    ],
                    "personal_assistant": [
                        {"name": "get_current_time", "description": "Get current time"},
                        {"name": "set_reminder", "description": "Set voice reminders"}
                    ]
                },
                "message": "Found 11 available tools"
            }
        } 