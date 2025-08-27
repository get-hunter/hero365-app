"""
Availability Application Service

Service layer for availability and scheduling management operations.
"""

import uuid
import logging
from typing import Optional, List
from datetime import date, time, datetime, timedelta

from ..dto.availability_dto import (
    AvailabilitySlotDTO, BusinessHoursDTO, AvailabilitySearchCriteria, CalendarEventDTO
)
from ...domain.repositories.business_repository import BusinessRepository
from ..exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)
from ...core.db import get_supabase_client

logger = logging.getLogger(__name__)


class AvailabilityService:
    """
    Application service for availability and scheduling management.
    
    Encapsulates business logic for availability operations and coordinates
    between the domain and infrastructure layers.
    """
    
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository
        self.supabase = get_supabase_client()
        logger.info("AvailabilityService initialized")
    
    async def get_availability_slots(
        self, 
        business_id: str, 
        search_criteria: AvailabilitySearchCriteria
    ) -> List[AvailabilitySlotDTO]:
        """
        Get availability slots for a business within a date range.
        
        Args:
            business_id: Business identifier
            search_criteria: Search and filter criteria
            
        Returns:
            List of availability slots as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get business hours for the date range
            business_hours = await self._get_business_hours(business_id)
            
            # Get existing calendar events (bookings, blocks, etc.)
            calendar_events = await self._get_calendar_events(business_id, search_criteria)
            
            # Generate availability slots based on business hours and existing events
            availability_slots = self._generate_availability_slots(
                business_id, 
                business_hours, 
                calendar_events, 
                search_criteria
            )
            
            logger.info(f"Generated {len(availability_slots)} availability slots for business {business_id}")
            return availability_slots
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving availability for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve availability: {str(e)}")
    
    async def get_business_hours(self, business_id: str) -> List[BusinessHoursDTO]:
        """
        Get business hours for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            List of business hours as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            return await self._get_business_hours(business_id)
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving business hours for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve business hours: {str(e)}")
    
    async def check_slot_availability(
        self, 
        business_id: str, 
        slot_date: date, 
        start_time: time, 
        duration_minutes: int
    ) -> bool:
        """
        Check if a specific time slot is available.
        
        Args:
            business_id: Business identifier
            slot_date: Date of the slot
            start_time: Start time of the slot
            duration_minutes: Duration in minutes
            
        Returns:
            True if slot is available, False otherwise
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If check fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Create search criteria for the specific slot
            end_time = (datetime.combine(slot_date, start_time) + timedelta(minutes=duration_minutes)).time()
            search_criteria = AvailabilitySearchCriteria(
                start_date=slot_date,
                end_date=slot_date,
                duration_minutes=duration_minutes,
                available_only=True
            )
            
            # Get availability slots
            slots = await self.get_availability_slots(business_id, search_criteria)
            
            # Check if any slot matches the requested time
            for slot in slots:
                if (slot.date == slot_date and 
                    slot.start_time <= start_time and 
                    slot.end_time >= end_time and 
                    slot.is_available):
                    return True
            
            return False
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error checking slot availability for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to check slot availability: {str(e)}")
    
    async def _get_business_hours(self, business_id: str) -> List[BusinessHoursDTO]:
        """Get business hours from database."""
        try:
            # Query business hours table
            result = self.supabase.table("business_hours").select(
                "day_of_week, is_open, open_time, close_time, break_start, break_end, is_emergency_available"
            ).eq("business_id", business_id).order("day_of_week").execute()
            
            business_hours = []
            for hours_data in result.data:
                hours_dto = BusinessHoursDTO(
                    business_id=business_id,
                    day_of_week=hours_data["day_of_week"],
                    is_open=hours_data.get("is_open", True),
                    open_time=time.fromisoformat(hours_data["open_time"]) if hours_data.get("open_time") else None,
                    close_time=time.fromisoformat(hours_data["close_time"]) if hours_data.get("close_time") else None,
                    break_start=time.fromisoformat(hours_data["break_start"]) if hours_data.get("break_start") else None,
                    break_end=time.fromisoformat(hours_data["break_end"]) if hours_data.get("break_end") else None,
                    is_emergency_available=hours_data.get("is_emergency_available", False)
                )
                business_hours.append(hours_dto)
            
            # If no business hours found, return default hours (9 AM - 5 PM, Monday-Friday)
            if not business_hours:
                for day in range(7):
                    is_weekday = day < 5  # Monday-Friday
                    hours_dto = BusinessHoursDTO(
                        business_id=business_id,
                        day_of_week=day,
                        is_open=is_weekday,
                        open_time=time(9, 0) if is_weekday else None,
                        close_time=time(17, 0) if is_weekday else None,
                        is_emergency_available=True
                    )
                    business_hours.append(hours_dto)
            
            return business_hours
            
        except Exception as e:
            logger.error(f"Error getting business hours: {str(e)}")
            raise
    
    async def _get_calendar_events(
        self, 
        business_id: str, 
        search_criteria: AvailabilitySearchCriteria
    ) -> List[CalendarEventDTO]:
        """Get calendar events from database."""
        try:
            # Query calendar events table
            result = self.supabase.table("calendar_events").select(
                "id, title, start_datetime, end_datetime, event_type, status, customer_id, service_id, notes"
            ).eq("business_id", business_id).gte(
                "start_datetime", search_criteria.start_date.isoformat()
            ).lte(
                "end_datetime", (search_criteria.end_date + timedelta(days=1)).isoformat()
            ).execute()
            
            calendar_events = []
            for event_data in result.data:
                event_dto = CalendarEventDTO(
                    id=str(event_data["id"]),
                    business_id=business_id,
                    title=event_data["title"],
                    start_datetime=datetime.fromisoformat(event_data["start_datetime"]),
                    end_datetime=datetime.fromisoformat(event_data["end_datetime"]),
                    event_type=event_data.get("event_type", "booking"),
                    status=event_data.get("status", "confirmed"),
                    customer_id=event_data.get("customer_id"),
                    service_id=event_data.get("service_id"),
                    notes=event_data.get("notes")
                )
                calendar_events.append(event_dto)
            
            return calendar_events
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            # Return empty list if table doesn't exist or other error
            return []
    
    def _generate_availability_slots(
        self,
        business_id: str,
        business_hours: List[BusinessHoursDTO],
        calendar_events: List[CalendarEventDTO],
        search_criteria: AvailabilitySearchCriteria
    ) -> List[AvailabilitySlotDTO]:
        """Generate availability slots based on business hours and existing events."""
        
        slots = []
        current_date = search_criteria.start_date
        
        while current_date <= search_criteria.end_date:
            day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
            
            # Find business hours for this day
            day_hours = next((h for h in business_hours if h.day_of_week == day_of_week), None)
            
            if day_hours and day_hours.is_open and day_hours.open_time and day_hours.close_time:
                # Generate slots for this day
                day_slots = self._generate_day_slots(
                    business_id,
                    current_date,
                    day_hours,
                    calendar_events,
                    search_criteria
                )
                slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _generate_day_slots(
        self,
        business_id: str,
        slot_date: date,
        business_hours: BusinessHoursDTO,
        calendar_events: List[CalendarEventDTO],
        search_criteria: AvailabilitySearchCriteria
    ) -> List[AvailabilitySlotDTO]:
        """Generate availability slots for a single day."""
        
        slots = []
        slot_duration = 60  # Default 1-hour slots
        
        if search_criteria.duration_minutes:
            slot_duration = search_criteria.duration_minutes
        
        # Start from opening time
        current_time = business_hours.open_time
        end_time = business_hours.close_time
        
        slot_counter = 0
        while current_time < end_time:
            # Calculate slot end time
            slot_end = (datetime.combine(slot_date, current_time) + timedelta(minutes=slot_duration)).time()
            
            # Don't create slots that extend past closing time
            if slot_end > end_time:
                break
            
            # Check if slot conflicts with break time
            is_during_break = (business_hours.break_start and business_hours.break_end and
                             current_time < business_hours.break_end and slot_end > business_hours.break_start)
            
            # Check if slot conflicts with existing events
            is_booked = self._is_slot_booked(slot_date, current_time, slot_end, calendar_events)
            
            # Create slot
            slot_id = f"{business_id}-{slot_date.isoformat()}-{current_time.strftime('%H%M')}"
            slot = AvailabilitySlotDTO(
                id=slot_id,
                business_id=business_id,
                date=slot_date,
                start_time=current_time,
                end_time=slot_end,
                duration_minutes=slot_duration,
                is_available=not (is_during_break or is_booked),
                is_emergency=business_hours.is_emergency_available,
                service_types=[],  # TODO: Add service type filtering
                max_bookings=1,
                current_bookings=1 if is_booked else 0
            )
            
            # Apply filters
            if search_criteria.available_only and not slot.is_available:
                current_time = (datetime.combine(slot_date, current_time) + timedelta(minutes=30)).time()
                continue
            
            if search_criteria.emergency_only and not slot.is_emergency:
                current_time = (datetime.combine(slot_date, current_time) + timedelta(minutes=30)).time()
                continue
            
            slots.append(slot)
            
            # Move to next slot (30-minute intervals)
            current_time = (datetime.combine(slot_date, current_time) + timedelta(minutes=30)).time()
            slot_counter += 1
            
            # Limit number of slots per day to prevent excessive generation
            if slot_counter >= 20:
                break
        
        return slots
    
    def _is_slot_booked(
        self, 
        slot_date: date, 
        start_time: time, 
        end_time: time, 
        calendar_events: List[CalendarEventDTO]
    ) -> bool:
        """Check if a slot conflicts with existing calendar events."""
        
        slot_start = datetime.combine(slot_date, start_time)
        slot_end = datetime.combine(slot_date, end_time)
        
        for event in calendar_events:
            # Check if event overlaps with slot
            if (event.start_datetime < slot_end and event.end_datetime > slot_start and
                event.status in ["confirmed", "pending"]):
                return True
        
        return False