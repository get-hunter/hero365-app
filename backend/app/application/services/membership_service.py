"""
Membership Application Service

Orchestrates membership-related business operations and use cases.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from ..dto.membership_dto import (
    MembershipPlanDTO, 
    CustomerMembershipDTO, 
    CreateMembershipPlanDTO,
    CreateCustomerMembershipDTO,
    MembershipPricingDTO
)
from ..exceptions.application_exceptions import (
    ApplicationError, 
    ValidationError, 
    BusinessRuleError,
    EntityNotFoundError
)
from ...domain.entities.customer_membership import (
    CustomerMembershipPlan, 
    CustomerMembership, 
    MembershipPlanType,
    MembershipStatus
)
from ...domain.repositories.customer_membership_repository import CustomerMembershipRepository
from ...domain.repositories.business_repository import BusinessRepository

logger = logging.getLogger(__name__)


class MembershipService:
    """
    Application service for membership operations.
    
    Handles business logic for membership plans and customer subscriptions,
    following clean architecture principles.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: CustomerMembershipRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def get_active_membership_plans(self, business_id: str) -> List[MembershipPlanDTO]:
        """
        Get all active membership plans for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            List of active membership plans as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError("Business", business_id)
            
            # Get active plans
            plans = await self.membership_repository.get_active_plans_by_business(business_uuid)
            
            # Convert to DTOs
            plan_dtos = []
            for plan in plans:
                plan_dto = MembershipPlanDTO(
                    id=str(plan.id),
                    name=plan.name,
                    plan_type=str(plan.plan_type),
                    description=plan.description,
                    tagline=plan.tagline,
                    price_monthly=float(plan.price_monthly),
                    price_yearly=float(plan.price_yearly),
                    yearly_savings=float(plan.calculate_yearly_savings()),
                    setup_fee=float(plan.setup_fee),
                    discount_percentage=plan.discount_percentage,
                    priority_service=plan.priority_service,
                    extended_warranty=plan.extended_warranty,
                    maintenance_included=plan.maintenance_included,
                    emergency_response=plan.emergency_response,
                    free_diagnostics=plan.free_diagnostics,
                    annual_tune_ups=plan.annual_tune_ups,
                    is_active=plan.is_active,
                    is_featured=plan.is_featured,
                    popular_badge=plan.popular_badge,
                    color_scheme=plan.color_scheme,
                    sort_order=plan.sort_order,
                    contract_length_months=plan.contract_length_months,
                    cancellation_policy=plan.cancellation_policy
                )
                plan_dtos.append(plan_dto)
            
            logger.info(f"Retrieved {len(plan_dtos)} active membership plans for business {business_id}")
            return plan_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving membership plans for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve membership plans: {str(e)}")
    
    async def create_membership_plan(
        self, 
        business_id: str, 
        plan_data: CreateMembershipPlanDTO
    ) -> MembershipPlanDTO:
        """
        Create a new membership plan for a business.
        
        Args:
            business_id: Business identifier
            plan_data: Plan creation data
            
        Returns:
            Created membership plan as DTO
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If plan data is invalid
            ApplicationError: If creation fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError("Business", business_id)
            
            # Create domain entity
            plan = CustomerMembershipPlan(
                business_id=business_uuid,
                name=plan_data.name,
                plan_type=MembershipPlanType(plan_data.plan_type),
                description=plan_data.description,
                tagline=plan_data.tagline,
                price_monthly=Decimal(str(plan_data.price_monthly)),
                price_yearly=Decimal(str(plan_data.price_yearly)),
                setup_fee=Decimal(str(plan_data.setup_fee or 0)),
                discount_percentage=plan_data.discount_percentage,
                priority_service=plan_data.priority_service,
                extended_warranty=plan_data.extended_warranty,
                maintenance_included=plan_data.maintenance_included,
                emergency_response=plan_data.emergency_response,
                free_diagnostics=plan_data.free_diagnostics,
                annual_tune_ups=plan_data.annual_tune_ups,
                is_featured=plan_data.is_featured,
                color_scheme=plan_data.color_scheme or "blue",
                sort_order=plan_data.sort_order or 0,
                contract_length_months=plan_data.contract_length_months or 12,
                cancellation_policy=plan_data.cancellation_policy
            )
            
            # Save to repository
            created_plan = await self.membership_repository.create_plan(plan)
            
            # Convert to DTO
            plan_dto = MembershipPlanDTO(
                id=str(created_plan.id),
                name=created_plan.name,
                plan_type=created_plan.plan_type.value,
                description=created_plan.description,
                tagline=created_plan.tagline,
                price_monthly=float(created_plan.price_monthly),
                price_yearly=float(created_plan.price_yearly),
                yearly_savings=float(created_plan.calculate_yearly_savings()),
                setup_fee=float(created_plan.setup_fee),
                discount_percentage=created_plan.discount_percentage,
                priority_service=created_plan.priority_service,
                extended_warranty=created_plan.extended_warranty,
                maintenance_included=created_plan.maintenance_included,
                emergency_response=created_plan.emergency_response,
                free_diagnostics=created_plan.free_diagnostics,
                annual_tune_ups=created_plan.annual_tune_ups,
                is_active=created_plan.is_active,
                is_featured=created_plan.is_featured,
                popular_badge=created_plan.popular_badge,
                color_scheme=created_plan.color_scheme,
                sort_order=created_plan.sort_order,
                contract_length_months=created_plan.contract_length_months,
                cancellation_policy=created_plan.cancellation_policy
            )
            
            logger.info(f"Created membership plan {created_plan.id} for business {business_id}")
            return plan_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating membership plan for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to create membership plan: {str(e)}")
    
    async def calculate_membership_pricing(
        self,
        business_id: str,
        product_price: Decimal,
        installation_price: Decimal,
        membership_plan_id: Optional[str] = None
    ) -> MembershipPricingDTO:
        """
        Calculate pricing with membership discounts applied.
        
        Args:
            business_id: Business identifier
            product_price: Base product price
            installation_price: Base installation price
            membership_plan_id: Optional membership plan to apply
            
        Returns:
            Pricing breakdown with membership discounts
            
        Raises:
            EntityNotFoundError: If business or plan doesn't exist
            ApplicationError: If calculation fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError("Business", business_id)
            
            base_total = product_price + installation_price
            
            # No membership - return base pricing
            if not membership_plan_id:
                return MembershipPricingDTO(
                    base_product_price=float(product_price),
                    base_installation_price=float(installation_price),
                    base_total=float(base_total),
                    membership_plan_id=None,
                    membership_plan_name=None,
                    discount_percentage=0,
                    discount_amount=0.0,
                    final_total=float(base_total),
                    savings=0.0
                )
            
            # Get membership plan
            plan_uuid = uuid.UUID(membership_plan_id)
            plan = await self.membership_repository.get_plan_by_id(plan_uuid)
            if not plan:
                raise EntityNotFoundError(f"Membership plan not found: {membership_plan_id}")
            
            # Calculate discount
            discount_rate = plan.get_effective_discount_rate()
            discount_amount = base_total * discount_rate
            final_total = base_total - discount_amount
            
            return MembershipPricingDTO(
                base_product_price=float(product_price),
                base_installation_price=float(installation_price),
                base_total=float(base_total),
                membership_plan_id=membership_plan_id,
                membership_plan_name=plan.name,
                discount_percentage=plan.discount_percentage,
                discount_amount=float(discount_amount),
                final_total=float(final_total),
                savings=float(discount_amount)
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating membership pricing: {str(e)}")
            raise ApplicationError(f"Failed to calculate membership pricing: {str(e)}")
    
    async def get_customer_active_membership(
        self,
        business_id: str,
        customer_id: str
    ) -> Optional[CustomerMembershipDTO]:
        """
        Get active membership for a customer.
        
        Args:
            business_id: Business identifier
            customer_id: Customer identifier
            
        Returns:
            Active customer membership DTO if found, None otherwise
            
        Raises:
            ValidationError: If IDs are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            customer_uuid = uuid.UUID(customer_id)
            
            membership = await self.membership_repository.get_active_membership_by_customer(
                business_uuid, customer_uuid
            )
            
            if not membership:
                return None
            
            # Convert to DTO
            return CustomerMembershipDTO(
                id=str(membership.id),
                business_id=str(membership.business_id),
                customer_id=str(membership.customer_id),
                plan_id=str(membership.plan_id),
                status=membership.status.value,
                start_date=membership.start_date,
                end_date=membership.end_date,
                next_billing_date=membership.next_billing_date,
                billing_cycle=membership.billing_cycle,
                locked_monthly_price=float(membership.locked_monthly_price),
                locked_yearly_price=float(membership.locked_yearly_price),
                locked_discount_percentage=membership.locked_discount_percentage,
                auto_renew=membership.auto_renew,
                total_savings_to_date=float(membership.total_savings_to_date)
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid ID format: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving customer membership: {str(e)}")
            raise ApplicationError(f"Failed to retrieve customer membership: {str(e)}")
