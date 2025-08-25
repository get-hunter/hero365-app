"""
Supabase Service Template Repository Implementation

Implements service template data access operations using Supabase as the database backend.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from supabase import Client
from app.domain.service_templates.models import (
    ServiceCategory, 
    ServiceTemplate,
    BusinessService,
    ServiceTemplateAdoption,
    BusinessServiceBundle,
    ServiceTemplateListRequest,
    ServiceCategoryWithServices,
    ServiceTemplateWithStats,
    BusinessServiceWithTemplate
)
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, 
    DuplicateEntityError, 
    DatabaseError, 
    DomainValidationError
)

logger = logging.getLogger(__name__)


class SupabaseServiceCategoryRepository:
    """Supabase implementation for service category operations."""

    def __init__(self, client: Client):
        self.client = client

    async def list_categories(
        self,
        trade_types: Optional[List[str]] = None,
        category_type: Optional[str] = None,
        is_active: bool = True
    ) -> List[ServiceCategory]:
        """List service categories with optional filtering."""
        try:
            query = self.client.table('service_categories').select('*')
            
            if is_active:
                query = query.eq('is_active', True)
            
            if trade_types:
                query = query.overlaps('trade_types', trade_types)
            
            if category_type:
                query = query.eq('category_type', category_type)
            
            query = query.order('sort_order', 'name')
            
            response = query.execute()
            
            if response.data:
                return [ServiceCategory(**item) for item in response.data]
            return []
            
        except Exception as e:
            logger.error(f"Error listing service categories: {str(e)}")
            raise DatabaseError(f"Failed to list service categories: {str(e)}")

    async def get_category_by_id(self, category_id: UUID) -> Optional[ServiceCategory]:
        """Get a specific service category by ID."""
        try:
            response = self.client.table('service_categories').select('*').eq('id', str(category_id)).execute()
            
            if response.data:
                return ServiceCategory(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting service category {category_id}: {str(e)}")
            raise DatabaseError(f"Failed to get service category: {str(e)}")

    async def get_category_by_slug(self, slug: str) -> Optional[ServiceCategory]:
        """Get a service category by slug."""
        try:
            response = self.client.table('service_categories').select('*').eq('slug', slug).execute()
            
            if response.data:
                return ServiceCategory(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting service category with slug {slug}: {str(e)}")
            raise DatabaseError(f"Failed to get service category: {str(e)}")

    async def get_categories_with_services(
        self,
        business_id: UUID,
        trade_types: Optional[List[str]] = None
    ) -> List[ServiceCategoryWithServices]:
        """Get categories that have active services for a business."""
        try:
            # Get categories that have services for this business
            query = self.client.table('service_categories').select(
                '*, business_services!inner(id, business_id, name, description, unit_price, is_active, is_featured, sort_order)'
            ).eq('business_services.business_id', str(business_id)).eq('business_services.is_active', True)
            
            if trade_types:
                query = query.overlaps('trade_types', trade_types)
            
            response = query.order('sort_order', 'name').execute()
            
            result = []
            if response.data:
                for item in response.data:
                    category = ServiceCategoryWithServices(**{k: v for k, v in item.items() if k != 'business_services'})
                    services = []
                    service_data = item.get('business_services', [])
                    if isinstance(service_data, list):
                        services = [BusinessService(**svc) for svc in service_data]
                    elif service_data:  # Single service
                        services = [BusinessService(**service_data)]
                    
                    category.services = sorted(services, key=lambda x: (x.sort_order, x.name))
                    category.service_count = len(services)
                    result.append(category)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting categories with services for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get categories with services: {str(e)}")


class SupabaseServiceTemplateRepository:
    """Supabase implementation for service template operations."""

    def __init__(self, client: Client):
        self.client = client

    async def list_templates(self, request: ServiceTemplateListRequest) -> Tuple[List[ServiceTemplate], int]:
        """List service templates with filtering and pagination."""
        try:
            query = self.client.table('service_templates').select('*', count='exact').eq('is_active', True)
            
            # Apply filters
            if request.trade_types:
                query = query.overlaps('trade_types', request.trade_types)
            
            if request.category_id:
                query = query.eq('category_id', str(request.category_id))
            
            if request.is_common_only:
                query = query.eq('is_common', True)
            
            if request.is_emergency_only:
                query = query.eq('is_emergency', True)
            
            if request.tags:
                query = query.overlaps('tags', request.tags)
            
            if request.skill_level:
                query = query.eq('skill_level', request.skill_level)
            
            if request.search:
                search_term = f"%{request.search.lower()}%"
                query = query.or_(
                    f"name.ilike.{search_term},description.ilike.{search_term}"
                )
            
            # Apply pagination and ordering
            response = query.order('is_common', {'ascending': False}).order('usage_count', {'ascending': False}).order('name').range(request.offset, request.offset + request.limit - 1).execute()
            
            templates = []
            if response.data:
                templates = [ServiceTemplate(**item) for item in response.data]
            
            total = response.count or 0
            return (templates, total)
            
        except Exception as e:
            logger.error(f"Error listing service templates: {str(e)}")
            raise DatabaseError(f"Failed to list service templates: {str(e)}")

    async def get_template_by_id(self, template_id: UUID) -> Optional[ServiceTemplate]:
        """Get a specific service template by ID."""
        try:
            response = self.client.table('service_templates').select('*').eq('id', str(template_id)).eq('is_active', True).execute()
            
            if response.data:
                return ServiceTemplate(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting service template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to get service template: {str(e)}")

    async def get_common_templates_for_trades(self, trade_types: List[str]) -> List[ServiceTemplate]:
        """Get common service templates for specific trade types."""
        try:
            response = self.client.table('service_templates').select('*').eq('is_active', True).eq('is_common', True).overlaps('trade_types', trade_types).order('service_type', 'name').execute()
            
            if response.data:
                return [ServiceTemplate(**item) for item in response.data]
            return []
            
        except Exception as e:
            logger.error(f"Error getting common templates for trades {trade_types}: {str(e)}")
            raise DatabaseError(f"Failed to get common templates: {str(e)}")

    async def increment_usage_count(self, template_id: UUID) -> None:
        """Increment the usage count for a template."""
        try:
            # Get current usage count
            response = self.client.table('service_templates').select('usage_count').eq('id', str(template_id)).execute()
            
            if response.data:
                current_count = response.data[0].get('usage_count', 0)
                self.client.table('service_templates').update({'usage_count': current_count + 1}).eq('id', str(template_id)).execute()
            
        except Exception as e:
            logger.error(f"Error incrementing usage count for template {template_id}: {str(e)}")
            # Don't raise error for this operation as it's not critical


class SupabaseBusinessServiceRepository:
    """Supabase implementation for business service operations."""

    def __init__(self, client: Client):
        self.client = client

    async def list_business_services(
        self,
        business_id: UUID,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
        is_featured: Optional[bool] = None,
        include_template: bool = False
    ) -> List[BusinessService]:
        """List services for a business."""
        try:
            select_fields = '*'
            if include_template:
                select_fields = '*, service_templates(*), service_categories(*)'
            
            query = self.client.table('business_services').select(select_fields).eq('business_id', str(business_id))
            
            if is_active is not None:
                query = query.eq('is_active', is_active)
            
            if is_featured is not None:
                query = query.eq('is_featured', is_featured)
            
            if category_id:
                query = query.eq('category_id', str(category_id))
            
            response = query.order('is_featured', {'ascending': False}).order('sort_order').order('name').execute()
            
            services = []
            if response.data:
                for item in response.data:
                    if include_template:
                        service = BusinessServiceWithTemplate(**{k: v for k, v in item.items() if k not in ['service_templates', 'service_categories']})
                        if item.get('service_templates'):
                            service.template = ServiceTemplate(**item['service_templates'])
                        if item.get('service_categories'):
                            service.category = ServiceCategory(**item['service_categories'])
                        services.append(service)
                    else:
                        services.append(BusinessService(**item))
            
            return services
            
        except Exception as e:
            logger.error(f"Error listing business services for {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to list business services: {str(e)}")

    async def get_business_service_by_id(
        self, 
        business_id: UUID, 
        service_id: UUID
    ) -> Optional[BusinessService]:
        """Get a specific business service."""
        try:
            response = self.client.table('business_services').select('*').eq('id', str(service_id)).eq('business_id', str(business_id)).execute()
            
            if response.data:
                return BusinessService(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting business service {service_id}: {str(e)}")
            raise DatabaseError(f"Failed to get business service: {str(e)}")

    async def create_business_service(self, service_data: Dict) -> BusinessService:
        """Create a new business service."""
        try:
            # Convert UUID objects to strings
            processed_data = self._prepare_service_data(service_data)
            
            response = self.client.table('business_services').insert(processed_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create business service")
            
            return BusinessService(**response.data[0])
            
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise DuplicateEntityError("Service name already exists for this business")
            logger.error(f"Error creating business service: {str(e)}")
            raise DatabaseError(f"Failed to create business service: {str(e)}")

    async def update_business_service(
        self,
        business_id: UUID,
        service_id: UUID, 
        update_data: Dict
    ) -> Optional[BusinessService]:
        """Update a business service."""
        try:
            processed_data = self._prepare_service_data(update_data)
            processed_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.client.table('business_services').update(processed_data).eq('id', str(service_id)).eq('business_id', str(business_id)).execute()
            
            if not response.data:
                return None
            
            return BusinessService(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error updating business service {service_id}: {str(e)}")
            raise DatabaseError(f"Failed to update business service: {str(e)}")

    async def delete_business_service(self, business_id: UUID, service_id: UUID) -> bool:
        """Delete a business service."""
        try:
            response = self.client.table('business_services').delete().eq('id', str(service_id)).eq('business_id', str(business_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting business service {service_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete business service: {str(e)}")

    async def check_service_name_exists(self, business_id: UUID, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a service name already exists for the business."""
        try:
            query = self.client.table('business_services').select('id').eq('business_id', str(business_id)).ilike('name', name)
            
            if exclude_id:
                query = query.neq('id', str(exclude_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking service name exists: {str(e)}")
            return False

    async def adopt_service_template(
        self,
        business_id: UUID,
        template_id: UUID,
        customizations: Dict = None
    ) -> BusinessService:
        """Create a business service from a template."""
        try:
            # Get the template
            template_response = self.client.table('service_templates').select('*').eq('id', str(template_id)).eq('is_active', True).execute()
            
            if not template_response.data:
                raise EntityNotFoundError(f"Template {template_id} not found or inactive")
            
            template = ServiceTemplate(**template_response.data[0])
            
            # Check if business already has this template
            existing_response = self.client.table('business_services').select('id').eq('business_id', str(business_id)).eq('template_id', str(template_id)).execute()
            
            if existing_response.data:
                raise DuplicateEntityError("Business already has a service from this template")
            
            # Apply customizations or use template defaults
            customizations = customizations or {}
            
            service_data = {
                'business_id': business_id,
                'template_id': template_id,
                'category_id': template.category_id,
                'name': customizations.get('name', template.name),
                'description': customizations.get('description', template.description),
                'pricing_model': customizations.get('pricing_model', template.pricing_model),
                'unit_price': customizations.get('unit_price', template.default_unit_price),
                'unit_of_measure': customizations.get('unit_of_measure', template.unit_of_measure),
                'estimated_duration_hours': customizations.get('estimated_duration_hours', template.estimated_duration_hours),
                'is_emergency': customizations.get('is_emergency', template.is_emergency),
                'requires_booking': customizations.get('requires_booking', True),
                'service_areas': customizations.get('service_areas', []),
                'warranty_terms': customizations.get('warranty_terms'),
                'terms_and_conditions': customizations.get('terms_and_conditions'),
                'custom_fields': customizations.get('custom_fields', {}),
                'is_active': True,
                'is_featured': customizations.get('is_featured', False)
            }
            
            # Check for duplicate name
            if await self.check_service_name_exists(business_id, service_data['name']):
                raise DuplicateEntityError(f"Service name '{service_data['name']}' already exists")
            
            # Create the service
            business_service = await self.create_business_service(service_data)
            
            # Track the adoption
            adoption_data = {
                'template_id': str(template_id),
                'business_id': str(business_id),
                'business_service_id': str(business_service.id),
                'customizations': customizations or {},
                'adopted_at': datetime.utcnow().isoformat()
            }
            
            self.client.table('service_template_adoptions').insert(adoption_data).execute()
            
            # Increment template usage count (async)
            template_repo = SupabaseServiceTemplateRepository(self.client)
            await template_repo.increment_usage_count(template_id)
            
            return business_service
            
        except (EntityNotFoundError, DuplicateEntityError):
            raise
        except Exception as e:
            logger.error(f"Error adopting service template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to adopt service template: {str(e)}")

    def _prepare_service_data(self, data: Dict) -> Dict:
        """Prepare service data for database insertion by converting UUIDs to strings."""
        processed = data.copy()
        
        # Convert UUID fields to strings
        for field in ['business_id', 'template_id', 'category_id', 'id']:
            if field in processed and processed[field] is not None:
                processed[field] = str(processed[field])
        
        # Ensure lists and dicts are properly serialized
        for field in ['service_areas', 'custom_fields', 'booking_settings', 'availability_schedule']:
            if field in processed and processed[field] is not None:
                if field in ['custom_fields', 'booking_settings', 'availability_schedule']:
                    processed[field] = processed[field] if isinstance(processed[field], dict) else {}
                else:
                    processed[field] = processed[field] if isinstance(processed[field], list) else []
        
        return processed


class SupabaseServiceTemplateAdoptionRepository:
    """Supabase implementation for tracking template adoptions."""

    def __init__(self, client: Client):
        self.client = client

    async def get_adoptions_for_business(self, business_id: UUID) -> List[ServiceTemplateAdoption]:
        """Get all template adoptions for a business."""
        try:
            response = self.client.table('service_template_adoptions').select('*').eq('business_id', str(business_id)).execute()
            
            if response.data:
                return [ServiceTemplateAdoption(**item) for item in response.data]
            return []
            
        except Exception as e:
            logger.error(f"Error getting adoptions for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get template adoptions: {str(e)}")

    async def get_adoption_stats(self, template_id: UUID) -> Dict:
        """Get adoption statistics for a template."""
        try:
            response = self.client.table('service_template_adoptions').select('customizations').eq('template_id', str(template_id)).execute()
            
            adoptions = response.data or []
            total_adoptions = len(adoptions)
            
            if total_adoptions == 0:
                return {
                    'total_adoptions': 0,
                    'customization_rate': 0.0,
                    'custom_pricing_rate': 0.0,
                    'custom_description_rate': 0.0
                }
            
            customizations = [adoption.get('customizations', {}) for adoption in adoptions]
            
            # Calculate customization statistics
            custom_pricing_count = sum(1 for c in customizations if c.get('custom_pricing'))
            custom_description_count = sum(1 for c in customizations if c.get('custom_description'))
            
            return {
                'total_adoptions': total_adoptions,
                'customization_rate': (custom_pricing_count + custom_description_count) / max(total_adoptions * 2, 1),
                'custom_pricing_rate': custom_pricing_count / total_adoptions,
                'custom_description_rate': custom_description_count / total_adoptions
            }
            
        except Exception as e:
            logger.error(f"Error getting adoption stats for template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to get adoption statistics: {str(e)}")
