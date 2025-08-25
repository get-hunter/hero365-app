from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models import (
    BusinessService as DBBusinessService,
    ServiceCategory as DBServiceCategory,
    ServiceTemplate as DBServiceTemplate,
    ServiceTemplateAdoption as DBServiceTemplateAdoption,
    BusinessServiceBundle as DBBusinessServiceBundle,
    Business as DBBusiness
)
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


class ServiceCategoryRepository:
    """Repository for service category operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_categories(
        self,
        trade_types: Optional[List[str]] = None,
        category_type: Optional[str] = None,
        is_active: bool = True
    ) -> List[ServiceCategory]:
        """List service categories with optional filtering."""
        query = self.db.query(DBServiceCategory)
        
        if is_active:
            query = query.filter(DBServiceCategory.is_active == True)
        
        if trade_types:
            query = query.filter(DBServiceCategory.trade_types.op('&&')(trade_types))
        
        if category_type:
            query = query.filter(DBServiceCategory.category_type == category_type)
        
        query = query.order_by(DBServiceCategory.sort_order, DBServiceCategory.name)
        
        categories = query.all()
        return [ServiceCategory.from_orm(cat) for cat in categories]

    def get_category_by_id(self, category_id: UUID) -> Optional[ServiceCategory]:
        """Get a specific service category by ID."""
        category = self.db.query(DBServiceCategory).filter(
            DBServiceCategory.id == category_id
        ).first()
        
        if category:
            return ServiceCategory.from_orm(category)
        return None

    def get_category_by_slug(self, slug: str) -> Optional[ServiceCategory]:
        """Get a service category by slug."""
        category = self.db.query(DBServiceCategory).filter(
            DBServiceCategory.slug == slug
        ).first()
        
        if category:
            return ServiceCategory.from_orm(category)
        return None

    def get_categories_with_services(
        self,
        business_id: UUID,
        trade_types: Optional[List[str]] = None
    ) -> List[ServiceCategoryWithServices]:
        """Get categories that have active services for a business."""
        query = self.db.query(DBServiceCategory).join(
            DBBusinessService,
            DBServiceCategory.id == DBBusinessService.category_id
        ).filter(
            DBBusinessService.business_id == business_id,
            DBBusinessService.is_active == True
        )
        
        if trade_types:
            query = query.filter(DBServiceCategory.trade_types.op('&&')(trade_types))
        
        categories = query.distinct().order_by(
            DBServiceCategory.sort_order, 
            DBServiceCategory.name
        ).all()
        
        result = []
        for category in categories:
            # Get services for this category
            services = self.db.query(DBBusinessService).filter(
                DBBusinessService.business_id == business_id,
                DBBusinessService.category_id == category.id,
                DBBusinessService.is_active == True
            ).order_by(DBBusinessService.sort_order, DBBusinessService.name).all()
            
            cat_with_services = ServiceCategoryWithServices.from_orm(category)
            cat_with_services.services = [BusinessService.from_orm(svc) for svc in services]
            cat_with_services.service_count = len(services)
            
            result.append(cat_with_services)
        
        return result


class ServiceTemplateRepository:
    """Repository for service template operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_templates(self, request: ServiceTemplateListRequest) -> Tuple[List[ServiceTemplate], int]:
        """List service templates with filtering and pagination."""
        query = self.db.query(DBServiceTemplate).filter(
            DBServiceTemplate.is_active == True
        )
        
        # Apply filters
        if request.trade_types:
            query = query.filter(DBServiceTemplate.trade_types.op('&&')(request.trade_types))
        
        if request.category_id:
            query = query.filter(DBServiceTemplate.category_id == request.category_id)
        
        if request.is_common_only:
            query = query.filter(DBServiceTemplate.is_common == True)
        
        if request.is_emergency_only:
            query = query.filter(DBServiceTemplate.is_emergency == True)
        
        if request.tags:
            query = query.filter(DBServiceTemplate.tags.op('&&')(request.tags))
        
        if request.skill_level:
            query = query.filter(DBServiceTemplate.skill_level == request.skill_level)
        
        if request.search:
            search_term = f"%{request.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(DBServiceTemplate.name).like(search_term),
                    func.lower(DBServiceTemplate.description).like(search_term),
                    DBServiceTemplate.tags.op('&&')([request.search.lower()])
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        templates = query.order_by(
            DBServiceTemplate.is_common.desc(),
            DBServiceTemplate.usage_count.desc(),
            DBServiceTemplate.name
        ).offset(request.offset).limit(request.limit).all()
        
        return ([ServiceTemplate.from_orm(tmpl) for tmpl in templates], total)

    def get_template_by_id(self, template_id: UUID) -> Optional[ServiceTemplate]:
        """Get a specific service template by ID."""
        template = self.db.query(DBServiceTemplate).filter(
            DBServiceTemplate.id == template_id,
            DBServiceTemplate.is_active == True
        ).first()
        
        if template:
            return ServiceTemplate.from_orm(template)
        return None

    def get_common_templates_for_trades(self, trade_types: List[str]) -> List[ServiceTemplate]:
        """Get common service templates for specific trade types."""
        templates = self.db.query(DBServiceTemplate).filter(
            DBServiceTemplate.is_active == True,
            DBServiceTemplate.is_common == True,
            DBServiceTemplate.trade_types.op('&&')(trade_types)
        ).order_by(
            DBServiceTemplate.service_type,
            DBServiceTemplate.name
        ).all()
        
        return [ServiceTemplate.from_orm(tmpl) for tmpl in templates]

    def get_templates_with_stats(self, trade_types: Optional[List[str]] = None) -> List[ServiceTemplateWithStats]:
        """Get templates with usage statistics."""
        query = self.db.query(
            DBServiceTemplate,
            func.count(DBServiceTemplateAdoption.id).label('adoptions'),
            func.count(DBBusiness.id).label('total_businesses')
        ).outerjoin(DBServiceTemplateAdoption).outerjoin(DBBusiness)
        
        if trade_types:
            query = query.filter(DBServiceTemplate.trade_types.op('&&')(trade_types))
        
        query = query.filter(DBServiceTemplate.is_active == True).group_by(
            DBServiceTemplate.id
        ).order_by(DBServiceTemplate.usage_count.desc())
        
        results = query.all()
        
        templates_with_stats = []
        for template, adoptions, total_businesses in results:
            template_obj = ServiceTemplateWithStats.from_orm(template)
            template_obj.adoption_rate = (adoptions / max(total_businesses, 1)) * 100
            # We'll calculate customization rate separately if needed
            templates_with_stats.append(template_obj)
        
        return templates_with_stats

    def increment_usage_count(self, template_id: UUID) -> None:
        """Increment the usage count for a template."""
        self.db.query(DBServiceTemplate).filter(
            DBServiceTemplate.id == template_id
        ).update({
            DBServiceTemplate.usage_count: DBServiceTemplate.usage_count + 1
        })


class BusinessServiceRepository:
    """Repository for business service operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_business_services(
        self,
        business_id: UUID,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
        is_featured: Optional[bool] = None,
        include_template: bool = False
    ) -> List[BusinessService]:
        """List services for a business."""
        query = self.db.query(DBBusinessService).filter(
            DBBusinessService.business_id == business_id
        )
        
        if is_active is not None:
            query = query.filter(DBBusinessService.is_active == is_active)
        
        if is_featured is not None:
            query = query.filter(DBBusinessService.is_featured == is_featured)
        
        if category_id:
            query = query.filter(DBBusinessService.category_id == category_id)
        
        if include_template:
            query = query.options(joinedload(DBBusinessService.template))
        
        services = query.order_by(
            DBBusinessService.is_featured.desc(),
            DBBusinessService.sort_order,
            DBBusinessService.name
        ).all()
        
        if include_template:
            result = []
            for service in services:
                service_with_template = BusinessServiceWithTemplate.from_orm(service)
                if service.template:
                    service_with_template.template = ServiceTemplate.from_orm(service.template)
                result.append(service_with_template)
            return result
        else:
            return [BusinessService.from_orm(svc) for svc in services]

    def get_business_service_by_id(
        self, 
        business_id: UUID, 
        service_id: UUID
    ) -> Optional[BusinessService]:
        """Get a specific business service."""
        service = self.db.query(DBBusinessService).filter(
            DBBusinessService.id == service_id,
            DBBusinessService.business_id == business_id
        ).first()
        
        if service:
            return BusinessService.from_orm(service)
        return None

    def create_business_service(self, service_data: Dict) -> BusinessService:
        """Create a new business service."""
        db_service = DBBusinessService(**service_data)
        self.db.add(db_service)
        self.db.flush()  # Get the ID without committing
        
        return BusinessService.from_orm(db_service)

    def update_business_service(
        self,
        business_id: UUID,
        service_id: UUID, 
        update_data: Dict
    ) -> Optional[BusinessService]:
        """Update a business service."""
        service = self.db.query(DBBusinessService).filter(
            DBBusinessService.id == service_id,
            DBBusinessService.business_id == business_id
        ).first()
        
        if not service:
            return None
        
        for field, value in update_data.items():
            setattr(service, field, value)
        
        self.db.flush()
        return BusinessService.from_orm(service)

    def delete_business_service(self, business_id: UUID, service_id: UUID) -> bool:
        """Delete a business service."""
        deleted = self.db.query(DBBusinessService).filter(
            DBBusinessService.id == service_id,
            DBBusinessService.business_id == business_id
        ).delete()
        
        return deleted > 0

    def check_service_name_exists(self, business_id: UUID, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a service name already exists for the business."""
        query = self.db.query(DBBusinessService).filter(
            DBBusinessService.business_id == business_id,
            func.lower(DBBusinessService.name) == name.lower()
        )
        
        if exclude_id:
            query = query.filter(DBBusinessService.id != exclude_id)
        
        return query.first() is not None

    def adopt_service_template(
        self,
        business_id: UUID,
        template_id: UUID,
        customizations: Dict = None
    ) -> BusinessService:
        """Create a business service from a template."""
        # Get the template
        template = self.db.query(DBServiceTemplate).filter(
            DBServiceTemplate.id == template_id,
            DBServiceTemplate.is_active == True
        ).first()
        
        if not template:
            raise ValueError(f"Template {template_id} not found or inactive")
        
        # Check if business already has this template
        existing = self.db.query(DBBusinessService).filter(
            DBBusinessService.business_id == business_id,
            DBBusinessService.template_id == template_id
        ).first()
        
        if existing:
            raise ValueError("Business already has a service from this template")
        
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
        if self.check_service_name_exists(business_id, service_data['name']):
            raise ValueError(f"Service name '{service_data['name']}' already exists")
        
        # Create the service
        business_service = self.create_business_service(service_data)
        
        # Track the adoption
        adoption = DBServiceTemplateAdoption(
            template_id=template_id,
            business_id=business_id,
            business_service_id=business_service.id,
            customizations=customizations or {}
        )
        self.db.add(adoption)
        
        return business_service


class ServiceTemplateAdoptionRepository:
    """Repository for tracking template adoptions."""

    def __init__(self, db: Session):
        self.db = db

    def get_adoptions_for_business(self, business_id: UUID) -> List[ServiceTemplateAdoption]:
        """Get all template adoptions for a business."""
        adoptions = self.db.query(DBServiceTemplateAdoption).filter(
            DBServiceTemplateAdoption.business_id == business_id
        ).all()
        
        return [ServiceTemplateAdoption.from_orm(adoption) for adoption in adoptions]

    def get_adoption_stats(self, template_id: UUID) -> Dict:
        """Get adoption statistics for a template."""
        adoptions = self.db.query(DBServiceTemplateAdoption).filter(
            DBServiceTemplateAdoption.template_id == template_id
        ).all()
        
        total_adoptions = len(adoptions)
        customizations = [adoption.customizations for adoption in adoptions]
        
        # Calculate customization statistics
        custom_pricing_count = sum(1 for c in customizations if c.get('custom_pricing'))
        custom_description_count = sum(1 for c in customizations if c.get('custom_description'))
        
        return {
            'total_adoptions': total_adoptions,
            'customization_rate': (custom_pricing_count + custom_description_count) / max(total_adoptions * 2, 1),
            'custom_pricing_rate': custom_pricing_count / max(total_adoptions, 1),
            'custom_description_rate': custom_description_count / max(total_adoptions, 1)
        }
