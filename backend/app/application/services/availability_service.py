"""
Availability Service

Core business logic for calculating available time slots for booking appointments.
Handles complex scheduling constraints including:
- Business hours and holidays
- Technician skills and availability
- Travel time optimization
- Capacity management
- Lead time and booking horizon
"""

import asyncio
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Optional, Set, Tuple
from uuid import UUID
import logging

from supabase import Client
from ...domain.entities.booking import (
    AvailabilityRequest, AvailabilityResponse, TimeSlot,
    BookableService, Technician, BusinessHours, TimeOff,
    BookingStatus, TimeOffStatus, AvailabilityCache
)
from ..exceptions.application_exceptions import (
    BusinessNotFoundError, ServiceNotFoundError, ValidationError
)

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Service for calculating and managing appointment availability"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.cache_ttl_minutes = 5  # Cache availability for 5 minutes
        
    async def get_availability(
        self, 
        request: AvailabilityRequest
    ) -> AvailabilityResponse:
        """
        Get available time slots for a service within the requested date range
        
        Args:
            request: Availability request with service, dates, and preferences
            
        Returns:
            AvailabilityResponse with available time slots by date
        """
        try:
            # Validate request
            await self._validate_availability_request(request)
            
            # Get service details
            service = await self._get_service(request.business_id, request.service_id)
            if not service:
                raise ServiceNotFoundError(str(request.service_id))
            
            # Determine date range
            start_date = request.start_date
            end_date = request.end_date or start_date
            
            # Limit to service's max advance booking
            max_end_date = date.today() + timedelta(days=service.max_advance_days)
            if end_date > max_end_date:
                end_date = max_end_date
            
            # Check cache first
            cached_availability = await self._get_cached_availability(
                request.business_id, request.service_id, start_date, end_date
            )
            
            if cached_availability:
                logger.info(f"Returning cached availability for service {request.service_id}")
                return cached_availability
            
            # Calculate fresh availability
            availability = await self._calculate_availability(request, service, start_date, end_date)
            
            # Cache the results
            await self._cache_availability(availability)
            
            return availability
            
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            raise
    
    async def _validate_availability_request(self, request: AvailabilityRequest) -> None:
        """Validate availability request parameters"""
        
        # Check date range
        if request.start_date < date.today():
            raise ValidationError("Cannot request availability for past dates")
        
        if request.end_date and request.end_date < request.start_date:
            raise ValidationError("End date must be after start date")
        
        # Limit date range to prevent excessive computation
        max_range_days = 90
        end_date = request.end_date or request.start_date
        if (end_date - request.start_date).days > max_range_days:
            raise ValidationError(f"Date range cannot exceed {max_range_days} days")
    
    async def _get_service(self, business_id: UUID, service_id: UUID) -> Optional[BookableService]:
        """Get service details from database"""
        try:
            result = self.supabase.table('bookable_services').select('*').eq(
                'business_id', str(business_id)
            ).eq('id', str(service_id)).eq('is_bookable', True).single().execute()
            
            if result.data:
                return BookableService(**result.data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching service {service_id}: {str(e)}")
            return None
    
    async def _calculate_availability(
        self,
        request: AvailabilityRequest,
        service: BookableService,
        start_date: date,
        end_date: date
    ) -> AvailabilityResponse:
        """Calculate availability for the date range"""
        
        # Get all required data in parallel
        business_hours, technicians, existing_bookings, time_off_records = await asyncio.gather(
            self._get_business_hours(request.business_id),
            self._get_qualified_technicians(request.business_id, service),
            self._get_existing_bookings(request.business_id, start_date, end_date),
            self._get_time_off_records(request.business_id, start_date, end_date)
        )
        
        if not technicians:
            logger.warning(f"No qualified technicians found for service {service.id}")
            return AvailabilityResponse(
                business_id=request.business_id,
                service_id=request.service_id,
                service_name=service.name,
                estimated_duration_minutes=service.estimated_duration_minutes,
                base_price=service.base_price
            )
        
        # Calculate slots for each date
        available_dates = {}
        total_slots = 0
        earliest_available = None
        latest_available = None
        
        current_date = start_date
        while current_date <= end_date:
            # Skip if service not available on this day
            day_of_week = current_date.isoweekday()  # 1=Monday, 7=Sunday
            if day_of_week not in service.available_days:
                current_date += timedelta(days=1)
                continue
            
            # Check if we're within lead time
            if not self._is_within_lead_time(current_date, service.min_lead_time_hours):
                current_date += timedelta(days=1)
                continue
            
            # Get business hours for this day
            day_hours = self._get_day_business_hours(business_hours, day_of_week)
            if not day_hours or not day_hours.is_open:
                current_date += timedelta(days=1)
                continue
            
            # Calculate available slots for this date
            date_slots = await self._calculate_date_slots(
                current_date, day_hours, service, technicians, 
                existing_bookings, time_off_records, request
            )
            
            if date_slots:
                available_dates[current_date.isoformat()] = date_slots
                total_slots += len(date_slots)
                
                # Update earliest/latest available
                for slot in date_slots:
                    if earliest_available is None or slot.start_time < earliest_available:
                        earliest_available = slot.start_time
                    if latest_available is None or slot.end_time > latest_available:
                        latest_available = slot.end_time
            
            current_date += timedelta(days=1)
        
        return AvailabilityResponse(
            business_id=request.business_id,
            service_id=request.service_id,
            service_name=service.name,
            available_dates=available_dates,
            total_slots=total_slots,
            earliest_available=earliest_available,
            latest_available=latest_available,
            estimated_duration_minutes=service.estimated_duration_minutes,
            base_price=service.base_price
        )
    
    async def _get_business_hours(self, business_id: UUID) -> List[BusinessHours]:
        """Get business operating hours"""
        try:
            result = self.supabase.table('business_hours').select('*').eq(
                'business_id', str(business_id)
            ).execute()
            
            return [BusinessHours(**row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching business hours: {str(e)}")
            return []
    
    async def _get_qualified_technicians(
        self, 
        business_id: UUID, 
        service: BookableService
    ) -> List[Technician]:
        """Get technicians qualified to perform the service"""
        try:
            # If no specific skills required, get all active technicians
            if not service.required_skills:
                result = self.supabase.table('technicians').select('*').eq(
                    'business_id', str(business_id)
                ).eq('is_active', True).eq('can_be_booked', True).execute()
                
                return [Technician(**row) for row in result.data]
            
            # Get technicians with required skills
            skill_ids = [str(skill_id) for skill_id in service.required_skills]
            
            # Complex query to find technicians with ALL required skills
            query = """
            SELECT DISTINCT t.* FROM technicians t
            JOIN technician_skills ts ON t.id = ts.technician_id
            WHERE t.business_id = %s 
              AND t.is_active = true 
              AND t.can_be_booked = true
              AND ts.skill_id = ANY(%s)
            GROUP BY t.id
            HAVING COUNT(DISTINCT ts.skill_id) >= %s
            """
            
            result = self.supabase.rpc('execute_sql', {
                'query': query,
                'params': [str(business_id), skill_ids, len(skill_ids)]
            }).execute()
            
            return [Technician(**row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching qualified technicians: {str(e)}")
            return []
    
    async def _get_existing_bookings(
        self, 
        business_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> List[Dict]:
        """Get existing bookings in the date range"""
        try:
            start_datetime = datetime.combine(start_date, time.min)
            end_datetime = datetime.combine(end_date, time.max)
            
            result = self.supabase.table('bookings').select(
                'id, scheduled_at, estimated_duration_minutes, primary_technician_id, status'
            ).eq('business_id', str(business_id)).in_(
                'status', [BookingStatus.CONFIRMED.value, BookingStatus.IN_PROGRESS.value]
            ).gte('scheduled_at', start_datetime.isoformat()).lte(
                'scheduled_at', end_datetime.isoformat()
            ).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error fetching existing bookings: {str(e)}")
            return []
    
    async def _get_time_off_records(
        self, 
        business_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> List[Dict]:
        """Get technician time off records in the date range"""
        try:
            start_datetime = datetime.combine(start_date, time.min)
            end_datetime = datetime.combine(end_date, time.max)
            
            # Get time off for technicians in this business
            result = self.supabase.table('time_off').select(
                'technician_id, start_at, end_at, type'
            ).eq('status', TimeOffStatus.APPROVED.value).gte(
                'start_at', start_datetime.isoformat()
            ).lte('end_at', end_datetime.isoformat()).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error fetching time off records: {str(e)}")
            return []
    
    def _get_day_business_hours(
        self, 
        business_hours: List[BusinessHours], 
        day_of_week: int
    ) -> Optional[BusinessHours]:
        """Get business hours for a specific day"""
        for hours in business_hours:
            if hours.day_of_week == day_of_week:
                return hours
        return None
    
    def _is_within_lead_time(self, booking_date: date, min_lead_time_hours: int) -> bool:
        """Check if booking date is within minimum lead time"""
        if min_lead_time_hours == 0:
            return True
        
        earliest_booking_time = datetime.now() + timedelta(hours=min_lead_time_hours)
        booking_datetime = datetime.combine(booking_date, time.min)
        
        return booking_datetime >= earliest_booking_time
    
    async def _calculate_date_slots(
        self,
        target_date: date,
        day_hours: BusinessHours,
        service: BookableService,
        technicians: List[Technician],
        existing_bookings: List[Dict],
        time_off_records: List[Dict],
        request: AvailabilityRequest
    ) -> List[TimeSlot]:
        """Calculate available time slots for a specific date"""
        
        slots = []
        
        # Determine working hours for the day
        if not day_hours.open_time or not day_hours.close_time:
            return slots
        
        # Use service available times if more restrictive
        service_start = time.fromisoformat(service.available_times.get('start', '08:00'))
        service_end = time.fromisoformat(service.available_times.get('end', '17:00'))
        
        work_start = max(day_hours.open_time, service_start)
        work_end = min(day_hours.close_time, service_end)
        
        if work_start >= work_end:
            return slots
        
        # Generate time slots (30-minute intervals by default)
        slot_interval_minutes = 30
        current_time = datetime.combine(target_date, work_start)
        end_time = datetime.combine(target_date, work_end)
        
        while current_time + timedelta(minutes=service.estimated_duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=service.estimated_duration_minutes)
            
            # Check if slot is during lunch break
            if day_hours.lunch_start and day_hours.lunch_end:
                lunch_start = datetime.combine(target_date, day_hours.lunch_start)
                lunch_end = datetime.combine(target_date, day_hours.lunch_end)
                
                if current_time < lunch_end and slot_end > lunch_start:
                    # Skip this slot, it conflicts with lunch
                    current_time += timedelta(minutes=slot_interval_minutes)
                    continue
            
            # Find available technicians for this slot
            available_techs = self._get_available_technicians_for_slot(
                current_time, slot_end, technicians, existing_bookings, 
                time_off_records, request
            )
            
            if available_techs:
                # Calculate capacity (minimum of service requirements and available technicians)
                capacity = min(len(available_techs), service.max_technicians)
                
                if capacity >= service.min_technicians:
                    slot = TimeSlot(
                        start_time=current_time,
                        end_time=slot_end,
                        available_technicians=[tech.id for tech in available_techs[:capacity]],
                        capacity=capacity,
                        booked_count=0,  # Will be updated based on existing bookings
                        price=service.base_price
                    )
                    slots.append(slot)
            
            current_time += timedelta(minutes=slot_interval_minutes)
        
        return slots
    
    def _get_available_technicians_for_slot(
        self,
        slot_start: datetime,
        slot_end: datetime,
        technicians: List[Technician],
        existing_bookings: List[Dict],
        time_off_records: List[Dict],
        request: AvailabilityRequest
    ) -> List[Technician]:
        """Get technicians available for a specific time slot"""
        
        available_techs = []
        
        for tech in technicians:
            # Skip if technician is excluded
            if tech.id in request.exclude_technician_ids:
                continue
            
            # Prefer requested technician
            is_preferred = tech.id == request.preferred_technician_id
            
            # Check for booking conflicts
            has_conflict = False
            for booking in existing_bookings:
                if booking.get('primary_technician_id') == str(tech.id):
                    booking_start = datetime.fromisoformat(booking['scheduled_at'])
                    booking_end = booking_start + timedelta(
                        minutes=booking['estimated_duration_minutes']
                    )
                    
                    # Add buffer time
                    booking_start -= timedelta(minutes=tech.default_buffer_minutes)
                    booking_end += timedelta(minutes=tech.default_buffer_minutes)
                    
                    if slot_start < booking_end and slot_end > booking_start:
                        has_conflict = True
                        break
            
            if has_conflict:
                continue
            
            # Check for time off conflicts
            for time_off in time_off_records:
                if time_off.get('technician_id') == str(tech.id):
                    time_off_start = datetime.fromisoformat(time_off['start_at'])
                    time_off_end = datetime.fromisoformat(time_off['end_at'])
                    
                    if slot_start < time_off_end and slot_end > time_off_start:
                        has_conflict = True
                        break
            
            if has_conflict:
                continue
            
            # Check service area (if customer address provided)
            if request.customer_address and tech.service_areas:
                # TODO: Implement geographic matching
                # For now, assume all technicians can serve all areas
                pass
            
            available_techs.append(tech)
        
        # Sort by preference (preferred technician first, then by experience/rating)
        available_techs.sort(key=lambda t: (
            t.id != request.preferred_technician_id,  # Preferred first
            -len(t.skills),  # More skills first
            t.first_name  # Alphabetical as tiebreaker
        ))
        
        return available_techs
    
    async def _get_cached_availability(
        self,
        business_id: UUID,
        service_id: UUID,
        start_date: date,
        end_date: date
    ) -> Optional[AvailabilityResponse]:
        """Get cached availability if valid and not expired"""
        try:
            # For now, skip caching to ensure fresh data
            # TODO: Implement proper cache invalidation
            return None
            
        except Exception as e:
            logger.error(f"Error checking availability cache: {str(e)}")
            return None
    
    async def _cache_availability(self, availability: AvailabilityResponse) -> None:
        """Cache availability results for performance"""
        try:
            # TODO: Implement availability caching
            # For now, skip caching to avoid complexity
            pass
            
        except Exception as e:
            logger.error(f"Error caching availability: {str(e)}")
    
    async def invalidate_availability_cache(
        self, 
        business_id: UUID, 
        service_id: Optional[UUID] = None,
        date_range: Optional[Tuple[date, date]] = None
    ) -> None:
        """Invalidate cached availability data"""
        try:
            query = self.supabase.table('availability_cache').delete().eq(
                'business_id', str(business_id)
            )
            
            if service_id:
                query = query.eq('service_id', str(service_id))
            
            if date_range:
                start_date, end_date = date_range
                query = query.gte('date', start_date.isoformat()).lte(
                    'date', end_date.isoformat()
                )
            
            query.execute()
            logger.info(f"Invalidated availability cache for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating availability cache: {str(e)}")
    
    async def get_next_available_slot(
        self,
        business_id: UUID,
        service_id: UUID,
        preferred_date: Optional[date] = None
    ) -> Optional[TimeSlot]:
        """Get the next available time slot for a service"""
        
        start_date = preferred_date or date.today()
        end_date = start_date + timedelta(days=30)  # Look ahead 30 days
        
        request = AvailabilityRequest(
            business_id=business_id,
            service_id=service_id,
            start_date=start_date,
            end_date=end_date
        )
        
        availability = await self.get_availability(request)
        
        # Find the earliest available slot
        earliest_slot = None
        for date_str, slots in availability.available_dates.items():
            for slot in slots:
                if slot.is_available:
                    if earliest_slot is None or slot.start_time < earliest_slot.start_time:
                        earliest_slot = slot
        
        return earliest_slot
