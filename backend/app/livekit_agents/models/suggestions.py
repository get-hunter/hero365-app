"""
Contextual Suggestions Models for Hero365 LiveKit Agents
"""

from typing import List
from pydantic import BaseModel, Field


class ContextualSuggestions(BaseModel):
    """Contextual suggestions based on current business state"""
    quick_actions: List[str] = Field(
        default_factory=list,
        description="Quick actions that can be taken immediately"
    )
    follow_ups: List[str] = Field(
        default_factory=list,
        description="Follow-up tasks and reminders"
    )
    urgent_items: List[str] = Field(
        default_factory=list,
        description="Urgent items requiring immediate attention"
    )
    opportunities: List[str] = Field(
        default_factory=list,
        description="Business opportunities and potential actions"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "quick_actions": [
                    "Schedule 3 unscheduled jobs",
                    "Send follow-up email to 2 pending estimates"
                ],
                "follow_ups": [
                    "Call John Smith about kitchen renovation",
                    "Check on material delivery for bathroom project"
                ],
                "urgent_items": [
                    "Emergency plumbing job needs immediate attention",
                    "Invoice payment is 30 days overdue"
                ],
                "opportunities": [
                    "Send maintenance reminders to customers from last year",
                    "Offer seasonal service packages to active customers"
                ]
            }
        } 