"""
Common Response Schemas

Shared response schemas used across multiple endpoints.
"""

from pydantic import BaseModel


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
    status: str
    version: str
    timestamp: str 