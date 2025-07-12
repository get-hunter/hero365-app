"""
Voice Agent API Schemas

This module provides Pydantic schemas for OpenAI voice agent API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class LocationSchema(BaseModel):
    """Location information schema"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class VoiceAgentStartRequest(BaseModel):
    """Request schema for starting an OpenAI voice agent with triage-based routing"""
    
    voice_settings: Optional[Dict[str, Any]] = Field(default=None, description="Voice configuration settings")
    instructions: Optional[str] = Field(default=None, description="Custom instructions for the agent")
    temperature: Optional[float] = Field(default=0.7, description="Response creativity (0.0-1.0)")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens per response")
    location: Optional[LocationSchema] = Field(default=None, description="User's current location")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the session")
    is_driving: Optional[bool] = Field(default=False, description="Whether the user is currently driving (enables safety mode)")
    safety_mode: Optional[bool] = Field(default=False, description="Enable safety mode for hands-free operation")
    voice_speed: Optional[str] = Field(default="normal", description="Voice speed: slow, normal, fast")
    device_type: Optional[str] = Field(default=None, description="Type of device being used (mobile, desktop, headset)")
    time_zone: Optional[str] = Field(default=None, description="User's time zone")
    
    class Config:
        json_schema_extra = {
            "example": {
                "voice_settings": {
                    "voice": "alloy",
                    "speed": 1.0,
                    "format": "pcm16"
                },
                "temperature": 0.7,
                "max_tokens": 1000,
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "context": {
                    "user_preferences": {"preferred_communication_style": "professional"}
                },
                "is_driving": False,
                "safety_mode": False,
                "voice_speed": "normal",
                "device_type": "mobile",
                "time_zone": "America/New_York"
            }
        }


class WebSocketConnectionSchema(BaseModel):
    """WebSocket connection information schema for OpenAI voice agents"""
    websocket_url: str = Field(..., description="WebSocket URL for voice communication")
    session_id: str = Field(..., description="Unique session identifier")
    audio_format: str = Field(default="pcm16", description="Audio format specification")
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    
    class Config:
        json_schema_extra = {
            "example": {
                "websocket_url": "wss://api.hero365.com/ws/voice-agent/session_abc123",
                "session_id": "session_abc123def456",
                "audio_format": "pcm16",
                "sample_rate": 16000
            }
        }


class VoiceAgentStartResponse(BaseModel):
    """Response schema for starting an OpenAI voice agent with triage-based routing"""
    
    success: bool = Field(..., description="Whether agent started successfully")
    session_id: str = Field(..., description="Unique session identifier")
    agent_name: str = Field(..., description="Name of the triage agent")
    greeting: str = Field(..., description="Personalized greeting message")
    available_capabilities: Dict[str, List[str]] = Field(..., description="Available capabilities organized by specialist")
    available_tools: int = Field(..., description="Total number of available tools across all specialists")
    websocket_connection: WebSocketConnectionSchema = Field(..., description="WebSocket connection details")
    agent_config: Dict[str, Any] = Field(..., description="Agent configuration settings")
    context_summary: str = Field(..., description="Summary of current context")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "session_abc123def456",
                "agent_name": "Hero365 AI Assistant",
                "greeting": "Good morning John! I'm your Hero365 assistant. I can help you with scheduling, jobs, invoicing, contacts, and more. What would you like to do?",
                "available_capabilities": {
                    "scheduling": ["Schedule appointments", "Check availability", "Reschedule meetings"],
                    "job_management": ["Create new jobs", "Update job status", "Track job progress"],
                    "invoice_management": ["Create invoices", "Track payments", "Send payment reminders"],
                    "estimate_management": ["Create estimates", "Convert estimates to invoices", "Track estimate status"],
                    "contact_management": ["Manage client information", "Record interactions", "Schedule follow-ups"],
                    "project_management": ["Track project progress", "Manage milestones", "Update project status"]
                },
                "available_tools": 26,
                "websocket_connection": {
                    "websocket_url": "wss://api.hero365.com/ws/voice-agent/session_abc123",
                    "session_id": "session_abc123def456",
                    "audio_format": "pcm16",
                    "sample_rate": 16000
                },
                "agent_config": {
                    "voice_model": "gpt-4o-realtime-preview",
                    "voice_settings": {
                        "voice": "alloy",
                        "speed": 1.0,
                        "format": "pcm16"
                    },
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "context_summary": "Business: Hero365 (home_services), User: John Doe (admin), Time: 2024-01-15T10:30:00 (Monday), Location: New York, Driving: No, Business Hours: Yes",
                "message": "Triage-based voice agent started successfully"
            }
        }


class VoiceAgentStatusRequest(BaseModel):
    """Request schema for getting OpenAI voice agent status"""
    
    session_id: str = Field(..., description="Session identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123def456"
            }
        }


class VoiceAgentStatusResponse(BaseModel):
    """Response schema for OpenAI voice agent status"""
    
    success: bool = Field(..., description="Whether status retrieved successfully")
    session_id: str = Field(..., description="Session identifier")
    agent_name: str = Field(..., description="Name of the triage agent")
    is_active: bool = Field(..., description="Whether agent is currently active")
    connection_status: str = Field(..., description="WebSocket connection status")
    duration: int = Field(..., description="Session duration in seconds")
    message_count: int = Field(..., description="Number of messages exchanged")
    tools_used: List[str] = Field(..., description="List of tools used in session")
    current_context: Dict[str, Any] = Field(..., description="Current session context")
    specialist_status: Dict[str, Any] = Field(..., description="Status of specialist agents")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "session_abc123def456",
                "agent_name": "Hero365 AI Assistant",
                "is_active": True,
                "connection_status": "connected",
                "duration": 120,
                "message_count": 8,
                "tools_used": ["route_to_scheduling", "route_to_job_management", "get_current_time"],
                "current_context": {
                    "last_specialist_used": "scheduling",
                    "user_location": {"latitude": 40.7128, "longitude": -74.0060}
                },
                "specialist_status": {
                    "available_specialists": 6,
                    "cached_agents": ["scheduling", "job_management"],
                    "routing_accuracy": "95%"
                },
                "message": "Triage-based voice agent status retrieved successfully"
            }
        }


class VoiceAgentStopRequest(BaseModel):
    """Request schema for stopping an OpenAI voice agent"""
    
    session_id: str = Field(..., description="Session identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123def456"
            }
        }


class VoiceAgentStopResponse(BaseModel):
    """Response schema for stopping an OpenAI voice agent"""
    
    success: bool = Field(..., description="Whether agent stopped successfully")
    session_id: str = Field(..., description="Session identifier")
    session_summary: Dict[str, Any] = Field(..., description="Session summary statistics")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "session_abc123def456",
                "session_summary": {
                    "duration": 300,
                    "total_messages": 12,
                    "tools_used": ["get_upcoming_jobs", "create_job", "get_current_time"],
                    "completed_tasks": 2,
                    "audio_duration": 285
                },
                "message": "OpenAI voice agent stopped successfully"
            }
        }


class VoiceAgentConfigRequest(BaseModel):
    """Request schema for updating OpenAI voice agent configuration"""
    
    session_id: str = Field(..., description="Session identifier")
    voice_settings: Optional[Dict[str, Any]] = Field(default=None, description="Voice settings to update")
    temperature: Optional[float] = Field(default=None, description="Response creativity (0.0-1.0)")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens per response")
    instructions: Optional[str] = Field(default=None, description="Updated instructions")
    location: Optional[LocationSchema] = Field(default=None, description="Updated location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123def456",
                "voice_settings": {
                    "voice": "nova",
                    "speed": 1.2,
                    "format": "pcm16"
                },
                "temperature": 0.8,
                "max_tokens": 1500,
                "instructions": "Be more concise in your responses",
                "location": {
                    "latitude": 40.7589,
                    "longitude": -73.9851
                }
            }
        }


class VoiceAgentConfigResponse(BaseModel):
    """Response schema for updating OpenAI voice agent configuration"""
    
    success: bool = Field(..., description="Whether configuration updated successfully")
    session_id: str = Field(..., description="Session identifier")
    updated_config: Dict[str, Any] = Field(..., description="Updated configuration settings")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "session_abc123def456",
                "updated_config": {
                    "voice_settings": {
                        "voice": "nova",
                        "speed": 1.2,
                        "format": "pcm16"
                    },
                    "temperature": 0.8,
                    "max_tokens": 1500,
                    "instructions": "Be more concise in your responses"
                },
                "message": "OpenAI voice agent configuration updated successfully"
            }
        }


class VoiceToolSchema(BaseModel):
    """Schema for voice agent tools"""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "create_job",
                "description": "Create new jobs"
            }
        }


class VoiceToolCategorySchema(BaseModel):
    """Schema for OpenAI voice agent tool categories"""
    
    job_management: List[VoiceToolSchema] = Field(..., description="Job management tools")
    project_management: List[VoiceToolSchema] = Field(..., description="Project management tools")
    invoice_management: List[VoiceToolSchema] = Field(..., description="Invoice management tools")
    estimate_management: List[VoiceToolSchema] = Field(..., description="Estimate management tools")
    contact_management: List[VoiceToolSchema] = Field(..., description="Contact management tools")
    general_tools: List[VoiceToolSchema] = Field(..., description="General utility tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_management": [
                    {"name": "create_job", "description": "Create new jobs"},
                    {"name": "get_upcoming_jobs", "description": "View upcoming jobs"},
                    {"name": "update_job_status", "description": "Update job status"}
                ],
                "project_management": [
                    {"name": "get_project_status", "description": "Get project status"},
                    {"name": "update_project_progress", "description": "Update project progress"}
                ],
                "invoice_management": [
                    {"name": "create_invoice", "description": "Create new invoices"},
                    {"name": "get_pending_invoices", "description": "View pending invoices"}
                ],
                "estimate_management": [
                    {"name": "create_estimate", "description": "Create new estimates"},
                    {"name": "convert_estimate_to_invoice", "description": "Convert estimate to invoice"}
                ],
                "contact_management": [
                    {"name": "get_contact_info", "description": "Get contact information"},
                    {"name": "search_contacts", "description": "Search contacts"}
                ],
                "general_tools": [
                    {"name": "get_current_time", "description": "Get current time"},
                    {"name": "set_reminder", "description": "Set voice reminders"}
                ]
            }
        }


class VoiceAgentHealthResponse(BaseModel):
    """Response schema for OpenAI voice agent health check"""
    
    success: bool = Field(..., description="Whether system is healthy")
    status: str = Field(..., description="System status")
    active_sessions: int = Field(..., description="Number of active sessions")
    system_info: Dict[str, bool] = Field(..., description="System component status")
    message: str = Field(..., description="Health status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "healthy",
                "active_sessions": 3,
                "system_info": {
                    "openai_agents_available": True,
                    "websocket_transport_available": True,
                    "business_tools_available": True,
                    "orchestration_available": True
                },
                "message": "OpenAI voice agent system is operational"
            }
        }


class VoiceAgentAvailableToolsResponse(BaseModel):
    """Response schema for available OpenAI voice agent tools endpoint"""
    
    success: bool = Field(..., description="Whether tools retrieved successfully")
    total_tools: int = Field(..., description="Total number of available tools")
    categories: VoiceToolCategorySchema = Field(..., description="Tool categories")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_tools": 26,
                "categories": {
                    "job_management": [
                        {"name": "create_job", "description": "Create new jobs"},
                        {"name": "get_upcoming_jobs", "description": "View upcoming jobs"},
                        {"name": "update_job_status", "description": "Update job status"}
                    ],
                    "project_management": [
                        {"name": "get_project_status", "description": "Get project status"},
                        {"name": "update_project_progress", "description": "Update project progress"}
                    ],
                    "invoice_management": [
                        {"name": "create_invoice", "description": "Create new invoices"},
                        {"name": "get_pending_invoices", "description": "View pending invoices"}
                    ],
                    "estimate_management": [
                        {"name": "create_estimate", "description": "Create new estimates"},
                        {"name": "convert_estimate_to_invoice", "description": "Convert estimate to invoice"}
                    ],
                    "contact_management": [
                        {"name": "get_contact_info", "description": "Get contact information"},
                        {"name": "search_contacts", "description": "Search contacts"}
                    ],
                    "general_tools": [
                        {"name": "get_current_time", "description": "Get current time"},
                        {"name": "set_reminder", "description": "Set voice reminders"}
                    ]
                },
                "message": "Found 26 available tools across 6 categories"
            }
        }


# WebSocket-specific schemas for OpenAI voice agents
class WebSocketMessageSchema(BaseModel):
    """Schema for WebSocket messages in OpenAI voice agent communication"""
    
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="Message timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "audio_chunk",
                "data": {
                    "audio": "base64_encoded_audio_data",
                    "format": "pcm16",
                    "sample_rate": 16000
                },
                "session_id": "session_abc123def456",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class VoiceAgentSessionListResponse(BaseModel):
    """Response schema for listing active voice agent sessions"""
    
    success: bool = Field(..., description="Whether sessions retrieved successfully")
    active_sessions: List[Dict[str, Any]] = Field(..., description="List of active sessions")
    total_sessions: int = Field(..., description="Total number of active sessions")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "active_sessions": [
                    {
                        "session_id": "session_abc123def456",
                        "agent_name": "Hero365 AI Assistant",
                        "user_id": "user_123",
                        "business_id": "business_456",
                        "started_at": "2024-01-15T10:30:00Z",
                        "duration": 120,
                        "status": "active"
                    }
                ],
                "total_sessions": 1,
                "message": "Found 1 active session"
            }
        }


class AudioConfigSchema(BaseModel):
    """Schema for audio configuration in OpenAI voice agents"""
    
    format: str = Field(default="pcm16", description="Audio format")
    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(default=1024, description="Audio chunk size in bytes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "pcm16",
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 1024
            }
        } 