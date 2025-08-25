"""
Booking Service

Manages the complete booking lifecycle including:
- Creating new bookings with conflict detection
- Confirming and scheduling appointments
- Rescheduling with availability validation
- Cancellation with policy enforcement
- Event sourcing for audit trail
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import logging

from supabase import Client
from ...domain.entities.booking import (
    BookingRequest, Booking, BookingResponse, BookingStatus,
    BookingConfirmationRequest, BookingRescheduleRequest, 
    BookingCancellationRequest, BookingEvent, BookingEventType,
    CustomerContact, ContactMethod
)
from .availability_service import AvailabilityService
from ..exceptions.application_exceptions import (
    BusinessNotFoundError, ServiceNotFoundError, ValidationError,
    ConflictError, NotFoundError
)

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing booking operations and lifecycle"""
    
    def __init__(self, supabase_client: Client, availability_service: AvailabilityService):
        self.supabase = supabase_client
        self.availability_service = availability_service
        
        # Booking policies
        self.max_reschedule_hours = 24  # Must reschedule 24h in advance
        self.cancellation_fee_hours = 24  # Fee applies if cancelled < 24h
        self.booking_hold_minutes = 15  # Hold slot for 15 minutes during booking
    
    async def create_booking(
        self, 
        request: BookingRequest,
        auto_confirm: bool = False
    ) -> BookingResponse:
        """
        Create a new booking request
        
        Args:
            request: Booking request details
            auto_confirm: Whether to automatically confirm the booking
            
        Returns:
            BookingResponse with booking details and next steps
        """
        try:
            # Validate the request
            await self._validate_booking_request(request)
            
            # Check for duplicate booking (idempotency)
            if request.idempotency_key:
                existing_booking = await self._get_booking_by_idempotency_key(
                    request.idempotency_key
                )
                if existing_booking:
                    logger.info(f"Returning existing booking for idempotency key {request.idempotency_key}")
                    return BookingResponse(
                        booking=existing_booking,
                        message="Booking already exists",
                        next_steps=self._get_next_steps(existing_booking)
                    )
            
            # Get or create customer contact
            customer = await self._get_or_create_customer(request)
            
            # Create the booking
            booking = await self._create_booking_record(request, customer)
            
            # Log the creation event
            await self._log_booking_event(
                booking.id,
                BookingEventType.CREATED,
                None,
                BookingStatus.PENDING,
                triggered_by="customer",
                notes=f"Booking created via {request.source.value}"
            )
            
            # Auto-confirm if requested and slot is available
            if auto_confirm:
                try:
                    booking = await self._auto_confirm_booking(booking)
                except Exception as e:
                    logger.warning(f"Auto-confirmation failed for booking {booking.id}: {str(e)}")
                    # Continue with pending status
            
            response = BookingResponse(
                booking=booking,
                message="Booking request created successfully",
                next_steps=self._get_next_steps(booking)
            )
            
            # TODO: Trigger notification workflow
            # await self._send_booking_confirmation(booking)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            raise
    
    async def confirm_booking(
        self, 
        request: BookingConfirmationRequest
    ) -> BookingResponse:
        """
        Confirm a pending booking and assign technician
        
        Args:
            request: Confirmation request with scheduling details
            
        Returns:
            BookingResponse with confirmed booking
        """
        try:
            # Get the booking
            booking = await self._get_booking(request.booking_id)
            if not booking:
                raise NotFoundError("Booking", str(request.booking_id))
            
            # Validate booking can be confirmed
            if booking.status != BookingStatus.PENDING:
                raise ValidationError(f"Booking is {booking.status.value}, cannot confirm")
            
            # Use provided scheduled time or original requested time
            scheduled_at = request.scheduled_at or booking.requested_at
            
            # Validate the scheduled time is available
            await self._validate_booking_time_available(
                booking.business_id,
                booking.service_id,
                scheduled_at,
                booking.estimated_duration_minutes,
                request.assigned_technician_id,
                exclude_booking_id=booking.id
            )
            
            # Update booking
            updates = {
                'status': BookingStatus.CONFIRMED.value,
                'scheduled_at': scheduled_at.isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if request.assigned_technician_id:
                updates['primary_technician_id'] = str(request.assigned_technician_id)
            
            result = self.supabase.table('bookings').update(updates).eq(
                'id', str(booking.id)
            ).execute()
            
            if not result.data:
                raise ConflictError("Failed to confirm booking - may have been modified")
            
            # Refresh booking object
            booking = Booking(**result.data[0])
            
            # Log the confirmation event
            await self._log_booking_event(
                booking.id,
                BookingEventType.CONFIRMED,
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                triggered_by="business",
                notes=request.notes
            )
            
            # Invalidate availability cache
            await self.availability_service.invalidate_availability_cache(
                booking.business_id,
                booking.service_id,
                (scheduled_at.date(), scheduled_at.date())
            )
            
            response = BookingResponse(
                booking=booking,
                message="Booking confirmed successfully",
                next_steps=self._get_next_steps(booking),
                estimated_arrival_time=booking.scheduled_at
            )
            
            # TODO: Send confirmation notifications
            # await self._send_booking_confirmation(booking)
            
            return response
            
        except Exception as e:
            logger.error(f"Error confirming booking {request.booking_id}: {str(e)}")
            raise
    
    async def reschedule_booking(
        self, 
        request: BookingRescheduleRequest
    ) -> BookingResponse:
        """
        Reschedule an existing booking to a new time
        
        Args:
            request: Reschedule request with new time and reason
            
        Returns:
            BookingResponse with rescheduled booking
        """
        try:
            # Get the booking
            booking = await self._get_booking(request.booking_id)
            if not booking:
                raise NotFoundError("Booking", str(request.booking_id))
            
            # Validate booking can be rescheduled
            if not booking.can_be_rescheduled:
                raise ValidationError(f"Booking status {booking.status.value} cannot be rescheduled")
            
            # Check reschedule policy (must be done with sufficient notice)
            if booking.scheduled_at:
                hours_until_appointment = (booking.scheduled_at - datetime.utcnow()).total_seconds() / 3600
                if hours_until_appointment < self.max_reschedule_hours:
                    raise ValidationError(
                        f"Bookings must be rescheduled at least {self.max_reschedule_hours} hours in advance"
                    )
            
            # Validate new time is available
            await self._validate_booking_time_available(
                booking.business_id,
                booking.service_id,
                request.new_scheduled_at,
                booking.estimated_duration_minutes,
                booking.primary_technician_id,
                exclude_booking_id=booking.id
            )
            
            # Store old scheduled time for event logging
            old_scheduled_at = booking.scheduled_at
            
            # Update booking
            updates = {
                'scheduled_at': request.new_scheduled_at.isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('bookings').update(updates).eq(
                'id', str(booking.id)
            ).execute()
            
            if not result.data:
                raise ConflictError("Failed to reschedule booking - may have been modified")
            
            # Refresh booking object
            booking = Booking(**result.data[0])
            
            # Log the reschedule event
            await self._log_booking_event(
                booking.id,
                BookingEventType.RESCHEDULED,
                booking.status,
                booking.status,
                triggered_by="customer",
                reason=request.reason,
                old_values={'scheduled_at': old_scheduled_at.isoformat() if old_scheduled_at else None},
                new_values={'scheduled_at': request.new_scheduled_at.isoformat()}
            )
            
            # Invalidate availability cache for both old and new dates
            dates_to_invalidate = [request.new_scheduled_at.date()]
            if old_scheduled_at:
                dates_to_invalidate.append(old_scheduled_at.date())
            
            for date_to_invalidate in set(dates_to_invalidate):
                await self.availability_service.invalidate_availability_cache(
                    booking.business_id,
                    booking.service_id,
                    (date_to_invalidate, date_to_invalidate)
                )
            
            response = BookingResponse(
                booking=booking,
                message="Booking rescheduled successfully",
                next_steps=self._get_next_steps(booking),
                estimated_arrival_time=booking.scheduled_at
            )
            
            # TODO: Send reschedule notifications
            if request.notify_customer:
                pass  # await self._send_reschedule_notification(booking)
            
            return response
            
        except Exception as e:
            logger.error(f"Error rescheduling booking {request.booking_id}: {str(e)}")
            raise
    
    async def cancel_booking(
        self, 
        request: BookingCancellationRequest
    ) -> BookingResponse:
        """
        Cancel an existing booking
        
        Args:
            request: Cancellation request with reason and refund info
            
        Returns:
            BookingResponse with cancelled booking
        """
        try:
            # Get the booking
            booking = await self._get_booking(request.booking_id)
            if not booking:
                raise NotFoundError("Booking", str(request.booking_id))
            
            # Validate booking can be cancelled
            if not booking.can_be_cancelled:
                raise ValidationError(f"Booking status {booking.status.value} cannot be cancelled")
            
            # Calculate cancellation fee if applicable
            cancellation_fee = 0
            if booking.scheduled_at and booking.quoted_price:
                hours_until_appointment = (booking.scheduled_at - datetime.utcnow()).total_seconds() / 3600
                if hours_until_appointment < self.cancellation_fee_hours:
                    # Apply 25% cancellation fee for short notice
                    cancellation_fee = float(booking.quoted_price) * 0.25
            
            # Update booking
            updates = {
                'status': BookingStatus.CANCELLED.value,
                'cancellation_reason': request.reason,
                'cancelled_by': request.cancelled_by,
                'cancelled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('bookings').update(updates).eq(
                'id', str(booking.id)
            ).execute()
            
            if not result.data:
                raise ConflictError("Failed to cancel booking - may have been modified")
            
            # Refresh booking object
            booking = Booking(**result.data[0])
            
            # Log the cancellation event
            await self._log_booking_event(
                booking.id,
                BookingEventType.CANCELLED,
                booking.status,
                BookingStatus.CANCELLED,
                triggered_by=request.cancelled_by,
                reason=request.reason
            )
            
            # Invalidate availability cache
            if booking.scheduled_at:
                await self.availability_service.invalidate_availability_cache(
                    booking.business_id,
                    booking.service_id,
                    (booking.scheduled_at.date(), booking.scheduled_at.date())
                )
            
            response = BookingResponse(
                booking=booking,
                message="Booking cancelled successfully",
                next_steps=["Refund will be processed within 3-5 business days"] if request.refund_amount else [],
                payment_info={
                    'cancellation_fee': cancellation_fee,
                    'refund_amount': float(request.refund_amount) if request.refund_amount else 0
                }
            )
            
            # TODO: Process refund and send notifications
            if request.notify_customer:
                pass  # await self._send_cancellation_notification(booking)
            
            return response
            
        except Exception as e:
            logger.error(f"Error cancelling booking {request.booking_id}: {str(e)}")
            raise
    
    async def get_booking(self, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID"""
        return await self._get_booking(booking_id)
    
    async def get_bookings_for_business(
        self,
        business_id: UUID,
        status: Optional[BookingStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Booking]:
        """Get bookings for a business with filters"""
        try:
            query = self.supabase.table('bookings').select('*').eq(
                'business_id', str(business_id)
            )
            
            if status:
                query = query.eq('status', status.value)
            
            if start_date:
                query = query.gte('scheduled_at', start_date.isoformat())
            
            if end_date:
                query = query.lte('scheduled_at', end_date.isoformat())
            
            result = query.order('scheduled_at', desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            return [Booking(**row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching bookings for business {business_id}: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _validate_booking_request(self, request: BookingRequest) -> None:
        """Validate booking request"""
        
        # Check if business exists
        business_result = self.supabase.table('businesses').select('id').eq(
            'id', str(request.business_id)
        ).single().execute()
        
        if not business_result.data:
            raise BusinessNotFoundError(str(request.business_id))
        
        # Check if service exists and is bookable
        service_result = self.supabase.table('bookable_services').select('*').eq(
            'id', str(request.service_id)
        ).eq('business_id', str(request.business_id)).eq(
            'is_bookable', True
        ).single().execute()
        
        if not service_result.data:
            raise ServiceNotFoundError(str(request.service_id))
        
        # Validate requested time is in the future
        if request.requested_at <= datetime.utcnow():
            raise ValidationError("Requested time must be in the future")
        
        # Validate contact information
        if not request.customer_email and not request.customer_phone:
            raise ValidationError("Either email or phone number is required")
        
        if request.sms_consent and not request.customer_phone:
            raise ValidationError("Phone number required for SMS consent")
    
    async def _get_booking_by_idempotency_key(self, idempotency_key: str) -> Optional[Booking]:
        """Get existing booking by idempotency key"""
        try:
            result = self.supabase.table('bookings').select('*').eq(
                'idempotency_key', idempotency_key
            ).single().execute()
            
            if result.data:
                return Booking(**result.data)
            return None
            
        except Exception:
            return None
    
    async def _get_or_create_customer(self, request: BookingRequest) -> CustomerContact:
        """Get existing customer or create new one"""
        try:
            # Try to find existing customer by email or phone
            query = self.supabase.table('customer_contacts').select('*').eq(
                'business_id', str(request.business_id)
            )
            
            if request.customer_email:
                query = query.eq('email', request.customer_email)
            elif request.customer_phone:
                query = query.eq('phone', request.customer_phone)
            
            result = query.single().execute()
            
            if result.data:
                # Update existing customer
                updates = {
                    'total_bookings': result.data['total_bookings'] + 1,
                    'last_booking_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Update consent if provided
                if request.sms_consent and not result.data.get('sms_consent'):
                    updates.update({
                        'sms_consent': True,
                        'sms_consent_date': datetime.utcnow().isoformat(),
                        'sms_consent_ip': str(request.ip_address) if request.ip_address else None
                    })
                
                updated_result = self.supabase.table('customer_contacts').update(updates).eq(
                    'id', result.data['id']
                ).execute()
                
                return CustomerContact(**updated_result.data[0])
            
        except Exception:
            pass  # Customer doesn't exist, create new one
        
        # Create new customer
        customer_data = {
            'id': str(uuid4()),
            'business_id': str(request.business_id),
            'email': request.customer_email,
            'phone': request.customer_phone,
            'first_name': request.customer_name.split()[0] if request.customer_name else None,
            'last_name': ' '.join(request.customer_name.split()[1:]) if len(request.customer_name.split()) > 1 else None,
            'preferred_contact_method': request.preferred_contact_method.value,
            'total_bookings': 1,
            'customer_since': datetime.utcnow().date().isoformat(),
            'sms_consent': request.sms_consent,
            'email_consent': request.email_consent,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if request.sms_consent:
            customer_data.update({
                'sms_consent_date': datetime.utcnow().isoformat(),
                'sms_consent_ip': str(request.ip_address) if request.ip_address else None
            })
        
        if request.email_consent:
            customer_data.update({
                'email_consent_date': datetime.utcnow().isoformat(),
                'email_consent_ip': str(request.ip_address) if request.ip_address else None
            })
        
        result = self.supabase.table('customer_contacts').insert(customer_data).execute()
        return CustomerContact(**result.data[0])
    
    async def _create_booking_record(
        self, 
        request: BookingRequest, 
        customer: CustomerContact
    ) -> Booking:
        """Create the booking record in database"""
        
        # Get service details for snapshot
        service_result = self.supabase.table('bookable_services').select('*').eq(
            'id', str(request.service_id)
        ).single().execute()
        
        service = service_result.data
        
        booking_data = {
            'id': str(uuid4()),
            'business_id': str(request.business_id),
            'service_id': str(request.service_id),
            'service_name': service['name'],
            'estimated_duration_minutes': service['estimated_duration_minutes'],
            'requested_at': request.requested_at.isoformat(),
            'customer_name': request.customer_name,
            'customer_email': request.customer_email,
            'customer_phone': request.customer_phone,
            'service_address': request.service_address,
            'service_city': request.service_city,
            'service_state': request.service_state,
            'service_zip': request.service_zip,
            'problem_description': request.problem_description,
            'special_instructions': request.special_instructions,
            'access_instructions': request.access_instructions,
            'quoted_price': service.get('base_price'),
            'status': BookingStatus.PENDING.value,
            'preferred_contact_method': request.preferred_contact_method.value,
            'sms_consent': request.sms_consent,
            'email_consent': request.email_consent,
            'source': request.source.value,
            'user_agent': request.user_agent,
            'ip_address': str(request.ip_address) if request.ip_address else None,
            'idempotency_key': request.idempotency_key,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table('bookings').insert(booking_data).execute()
        return Booking(**result.data[0])
    
    async def _auto_confirm_booking(self, booking: Booking) -> Booking:
        """Attempt to automatically confirm a booking"""
        
        # Check if the requested time is still available
        try:
            await self._validate_booking_time_available(
                booking.business_id,
                booking.service_id,
                booking.requested_at,
                booking.estimated_duration_minutes
            )
            
            # Auto-confirm the booking
            confirmation_request = BookingConfirmationRequest(
                booking_id=booking.id,
                scheduled_at=booking.requested_at,
                notes="Auto-confirmed"
            )
            
            response = await self.confirm_booking(confirmation_request)
            return response.booking
            
        except Exception as e:
            logger.warning(f"Auto-confirmation failed: {str(e)}")
            return booking
    
    async def _validate_booking_time_available(
        self,
        business_id: UUID,
        service_id: UUID,
        scheduled_at: datetime,
        duration_minutes: int,
        preferred_technician_id: Optional[UUID] = None,
        exclude_booking_id: Optional[UUID] = None
    ) -> None:
        """Validate that a booking time is available"""
        
        # Check for conflicting bookings
        end_time = scheduled_at + timedelta(minutes=duration_minutes)
        
        query = self.supabase.table('bookings').select(
            'id, scheduled_at, estimated_duration_minutes, primary_technician_id'
        ).eq('business_id', str(business_id)).in_(
            'status', [BookingStatus.CONFIRMED.value, BookingStatus.IN_PROGRESS.value]
        ).gte('scheduled_at', (scheduled_at - timedelta(hours=1)).isoformat()).lte(
            'scheduled_at', (end_time + timedelta(hours=1)).isoformat()
        )
        
        if exclude_booking_id:
            query = query.neq('id', str(exclude_booking_id))
        
        result = query.execute()
        
        for existing_booking in result.data:
            existing_start = datetime.fromisoformat(existing_booking['scheduled_at'])
            existing_end = existing_start + timedelta(minutes=existing_booking['estimated_duration_minutes'])
            
            # Check for time overlap
            if scheduled_at < existing_end and end_time > existing_start:
                # If same technician, it's definitely a conflict
                if (preferred_technician_id and 
                    existing_booking['primary_technician_id'] == str(preferred_technician_id)):
                    raise ConflictError("Technician is not available at the requested time")
                
                # For now, assume conflict (would need more sophisticated capacity management)
                raise ConflictError("Requested time slot is not available")
    
    async def _get_booking(self, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID"""
        try:
            result = self.supabase.table('bookings').select('*').eq(
                'id', str(booking_id)
            ).single().execute()
            
            if result.data:
                return Booking(**result.data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching booking {booking_id}: {str(e)}")
            return None
    
    async def _log_booking_event(
        self,
        booking_id: UUID,
        event_type: BookingEventType,
        old_status: Optional[BookingStatus],
        new_status: Optional[BookingStatus],
        triggered_by: str = "system",
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log booking event for audit trail"""
        try:
            event_data = {
                'id': str(uuid4()),
                'booking_id': str(booking_id),
                'event_type': event_type.value,
                'old_status': old_status.value if old_status else None,
                'new_status': new_status.value if new_status else None,
                'triggered_by': triggered_by,
                'reason': reason,
                'notes': notes,
                'old_values': old_values,
                'new_values': new_values,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('booking_events').insert(event_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging booking event: {str(e)}")
    
    def _get_next_steps(self, booking: Booking) -> List[str]:
        """Get next steps for customer based on booking status"""
        
        if booking.status == BookingStatus.PENDING:
            return [
                "We will review your request and confirm your appointment within 2 hours",
                "You will receive a confirmation email/SMS with appointment details",
                "Please ensure someone is available at the service address"
            ]
        
        elif booking.status == BookingStatus.CONFIRMED:
            steps = [
                f"Your appointment is confirmed for {booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}",
                "You will receive a reminder 24 hours before your appointment",
                "Please ensure someone is available at the service address"
            ]
            
            if booking.access_instructions:
                steps.append("Please have access instructions ready for the technician")
            
            return steps
        
        elif booking.status == BookingStatus.IN_PROGRESS:
            return [
                "Your technician is currently working on your service request",
                "You will receive an update when the work is completed",
                "Please contact us if you have any questions"
            ]
        
        elif booking.status == BookingStatus.COMPLETED:
            return [
                "Your service has been completed",
                "You will receive an invoice within 24 hours",
                "Please consider leaving a review of our service"
            ]
        
        elif booking.status == BookingStatus.CANCELLED:
            return [
                "Your booking has been cancelled",
                "Any applicable refund will be processed within 3-5 business days",
                "Feel free to book again when you're ready"
            ]
        
        else:
            return []
