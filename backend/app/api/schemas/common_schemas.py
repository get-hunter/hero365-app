"""
Common Response Schemas

Shared response schemas used across multiple endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer

from ...utils import format_datetime_utc


class Message(BaseModel):
    """Generic message response (legacy compatibility)."""
    message: str


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    details: dict = {}


class StatusResponse(BaseModel):
    """Health/status check response."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    status: str
    version: str
    timestamp: str  # Keep as string for backward compatibility 