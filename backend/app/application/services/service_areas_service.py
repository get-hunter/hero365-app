"""
Service Areas Application Service
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from app.domain.entities.service_areas import (
    ServiceArea,
    ServiceAreaCreate,
    ServiceAreaUpdate,
    ServiceAreaBulkUpsert,
    ServiceAreaCheckRequest,
    ServiceAreaCheckResponse,
    NormalizedLocation,
    ServiceAreaSuggestion,
    AvailabilityRequestCreate,
    AvailabilityRequest,
    AvailabilityRequestResponse
)
from app.core.db import get_supabase_client
from app.application.exceptions.application_exceptions import (
    ApplicationException,
    BusinessNotFoundError,
    DataCompositionError
)

logger = logging.getLogger(__name__)


class ServiceAreasService:
    """Service for managing service areas and availability requests"""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def check_service_area_support(self, request: ServiceAreaCheckRequest) -> ServiceAreaCheckResponse:
        """Check if a postal code is supported by a business"""
        try:
            # Call the database function for service area check
            result = self.supabase.rpc(
                'check_service_area_support',
                {
                    'p_business_id': request.business_id,
                    'p_postal_code': request.postal_code,
                    'p_country_code': request.country_code
                }
            ).execute()

            if not result.data:
                return ServiceAreaCheckResponse(
                    supported=False,
                    message="Unable to check service area"
                )

            area_data = result.data[0]
            
            if area_data['supported']:
                normalized = NormalizedLocation(
                    postal_code=request.postal_code,
                    country_code=request.country_code,
                    city=area_data['city'],
                    region=area_data['region'],
                    timezone=area_data['timezone'],
                    dispatch_fee_cents=area_data['dispatch_fee_cents'] or 0,
                    min_response_time_hours=area_data['min_response_time_hours'],
                    max_response_time_hours=area_data['max_response_time_hours'],
                    emergency_available=area_data['emergency_available'],
                    regular_available=area_data['regular_available']
                )

                return ServiceAreaCheckResponse(
                    supported=True,
                    normalized=normalized,
                    message="Service available in your area"
                )
            else:
                # Get nearby suggestions
                suggestions = await self._get_nearby_suggestions(
                    request.business_id,
                    request.postal_code,
                    request.country_code
                )

                return ServiceAreaCheckResponse(
                    supported=False,
                    suggestions=suggestions,
                    message="Service not yet available in your area"
                )

        except Exception as e:
            logger.error(f"Error checking service area support: {e}")
            raise DataCompositionError(f"Failed to check service area: {str(e)}")

    async def _get_nearby_suggestions(
        self, 
        business_id: str, 
        postal_code: str, 
        country_code: str
    ) -> List[ServiceAreaSuggestion]:
        """Get nearby service area suggestions"""
        try:
            result = self.supabase.rpc(
                'get_nearby_service_areas',
                {
                    'p_business_id': business_id,
                    'p_postal_code': postal_code,
                    'p_country_code': country_code,
                    'p_limit': 5
                }
            ).execute()

            if not result.data:
                return []

            return [
                ServiceAreaSuggestion(
                    postal_code=row['postal_code'],
                    city=row['city'],
                    region=row['region'],
                    distance_estimate=row['distance_estimate']
                )
                for row in result.data
            ]

        except Exception as e:
            logger.warning(f"Error getting nearby suggestions: {e}")
            return []

    async def create_availability_request(self, request: AvailabilityRequestCreate) -> AvailabilityRequestResponse:
        """Create an availability request for unsupported areas"""
        try:
            # Insert availability request
            result = self.supabase.table('availability_requests').insert({
                'business_id': request.business_id,
                'contact_name': request.contact_name,
                'phone_e164': request.phone_e164,
                'email': request.email,
                'postal_code': request.postal_code,
                'country_code': request.country_code,
                'city': request.city,
                'region': request.region,
                'service_category': request.service_category,
                'service_type': request.service_type,
                'urgency_level': request.urgency_level,
                'preferred_contact_method': request.preferred_contact_method,
                'notes': request.notes,
                'source': request.source,
                'referrer_url': request.referrer_url,
                'user_agent': request.user_agent
            }).execute()

            if not result.data:
                raise DataCompositionError("Failed to create availability request")

            request_id = result.data[0]['id']

            return AvailabilityRequestResponse(
                created=True,
                id=request_id,
                message="We'll contact you when service becomes available in your area"
            )

        except Exception as e:
            logger.error(f"Error creating availability request: {e}")
            raise DataCompositionError(f"Failed to create availability request: {str(e)}")

    async def get_service_areas(
        self,
        business_id: str,
        q: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ServiceArea]:
        """Get service areas for a business"""
        try:
            query = self.supabase.table('service_areas').select('*').eq('business_id', business_id)

            if q:
                query = query.or_(f'postal_code.ilike.%{q}%,city.ilike.%{q}%,region.ilike.%{q}%')

            result = query.order('postal_code').range(offset, offset + limit - 1).execute()

            return [ServiceArea(**row) for row in result.data]

        except Exception as e:
            logger.error(f"Error getting service areas: {e}")
            raise DataCompositionError(f"Failed to get service areas: {str(e)}")

    async def bulk_upsert_service_areas(self, request: ServiceAreaBulkUpsert) -> Dict[str, Any]:
        """Bulk upsert service areas"""
        try:
            # Prepare data for upsert
            areas_data = []
            for area in request.areas:
                area_dict = area.dict()
                area_dict['business_id'] = request.business_id
                areas_data.append(area_dict)

            # Use upsert with conflict resolution
            result = self.supabase.table('service_areas').upsert(
                areas_data,
                on_conflict='business_id,postal_code,country_code'
            ).execute()

            return {
                'success': True,
                'upserted_count': len(result.data),
                'message': f'Successfully processed {len(result.data)} service areas'
            }

        except Exception as e:
            logger.error(f"Error bulk upserting service areas: {e}")
            raise DataCompositionError(f"Failed to bulk upsert service areas: {str(e)}")

    async def update_service_area(self, area_id: str, update_data: ServiceAreaUpdate) -> ServiceArea:
        """Update a service area"""
        try:
            # Only include non-None fields in update
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            if not update_dict:
                raise ApplicationException("No fields to update", "INVALID_UPDATE")

            result = self.supabase.table('service_areas').update(update_dict).eq('id', area_id).execute()

            if not result.data:
                raise ApplicationException("Service area not found", "NOT_FOUND")

            return ServiceArea(**result.data[0])

        except Exception as e:
            logger.error(f"Error updating service area: {e}")
            raise DataCompositionError(f"Failed to update service area: {str(e)}")

    async def delete_service_area(self, area_id: str) -> bool:
        """Delete a service area"""
        try:
            result = self.supabase.table('service_areas').delete().eq('id', area_id).execute()
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Error deleting service area: {e}")
            raise DataCompositionError(f"Failed to delete service area: {str(e)}")

    async def get_availability_requests(
        self,
        business_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AvailabilityRequest]:
        """Get availability requests for a business"""
        try:
            query = self.supabase.table('availability_requests').select('*').eq('business_id', business_id)

            if status:
                query = query.eq('status', status)

            result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()

            return [AvailabilityRequest(**row) for row in result.data]

        except Exception as e:
            logger.error(f"Error getting availability requests: {e}")
            raise DataCompositionError(f"Failed to get availability requests: {str(e)}")

    async def update_availability_request_status(
        self,
        request_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> AvailabilityRequest:
        """Update availability request status"""
        try:
            update_data = {'status': status}
            
            if status == 'contacted':
                update_data['contacted_at'] = datetime.utcnow().isoformat()
            elif status == 'converted':
                update_data['converted_at'] = datetime.utcnow().isoformat()
            
            if notes:
                update_data['notes'] = notes

            result = self.supabase.table('availability_requests').update(update_data).eq('id', request_id).execute()

            if not result.data:
                raise ApplicationException("Availability request not found", "NOT_FOUND")

            return AvailabilityRequest(**result.data[0])

        except Exception as e:
            logger.error(f"Error updating availability request status: {e}")
            raise DataCompositionError(f"Failed to update availability request: {str(e)}")

    async def export_service_areas_csv(self, business_id: str) -> str:
        """Export service areas as CSV string"""
        try:
            areas = await self.get_service_areas(business_id, limit=10000)
            
            if not areas:
                return "postal_code,country_code,city,region,timezone,is_active\n"

            csv_lines = ["postal_code,country_code,city,region,timezone,is_active"]
            
            for area in areas:
                csv_lines.append(
                    f"{area.postal_code},{area.country_code},"
                    f"{area.city or ''},{area.region or ''},"
                    f"{area.timezone},{area.is_active}"
                )

            return "\n".join(csv_lines)

        except Exception as e:
            logger.error(f"Error exporting service areas CSV: {e}")
            raise DataCompositionError(f"Failed to export service areas: {str(e)}")

    async def import_service_areas_csv(self, business_id: str, csv_content: str) -> Dict[str, Any]:
        """Import service areas from CSV content"""
        try:
            lines = csv_content.strip().split('\n')
            if len(lines) < 2:
                raise ApplicationException("CSV must contain header and at least one data row", "INVALID_CSV")

            header = lines[0].lower()
            expected_fields = ['postal_code', 'country_code', 'city', 'region', 'timezone']
            
            # Validate header
            for field in expected_fields:
                if field not in header:
                    raise ApplicationException(f"CSV missing required field: {field}", "INVALID_CSV")

            areas = []
            errors = []

            for i, line in enumerate(lines[1:], 2):
                try:
                    values = [v.strip() for v in line.split(',')]
                    if len(values) < len(expected_fields):
                        errors.append(f"Line {i}: Not enough columns")
                        continue

                    area_data = {
                        'postal_code': values[0],
                        'country_code': values[1] or 'US',
                        'city': values[2] if len(values) > 2 else None,
                        'region': values[3] if len(values) > 3 else None,
                        'timezone': values[4] if len(values) > 4 else 'America/New_York',
                        'is_active': values[5].lower() in ('true', '1', 'yes') if len(values) > 5 else True
                    }

                    # Validate required fields
                    if not area_data['postal_code']:
                        errors.append(f"Line {i}: Missing postal code")
                        continue

                    areas.append(area_data)

                except Exception as e:
                    errors.append(f"Line {i}: {str(e)}")

            if not areas:
                raise ApplicationException("No valid service areas found in CSV", "INVALID_CSV")

            # Bulk insert
            for area_data in areas:
                area_data['business_id'] = business_id

            result = self.supabase.table('service_areas').upsert(
                areas,
                on_conflict='business_id,postal_code,country_code'
            ).execute()

            return {
                'success': True,
                'imported_count': len(result.data),
                'total_processed': len(areas),
                'errors': errors,
                'message': f'Successfully imported {len(result.data)} service areas'
            }

        except Exception as e:
            logger.error(f"Error importing service areas CSV: {e}")
            raise DataCompositionError(f"Failed to import service areas: {str(e)}")
