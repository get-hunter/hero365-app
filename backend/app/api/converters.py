"""
Pydantic Converters

Utilities for safely converting between domain objects and API models using Pydantic.
Handles validation errors gracefully and provides consistent error handling.
"""

import json
import logging
from datetime import datetime
from typing import TypeVar, Type, Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ValidationError, field_validator
from fastapi import HTTPException, status

from ..domain.enums import (
    ContactType, ContactStatus, ContactPriority, ContactSource,
    RelationshipStatus, LifecycleStage, JobType, JobStatus, JobPriority, JobSource
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class SafeConverter:
    """Utility class for safe conversions with error handling."""
    
    @staticmethod
    def safe_convert_to_api_model(data: Any, api_model: Type[T]) -> T:
        """
        Safely convert any data to API model with comprehensive error handling.
        
        Args:
            data: Source data (dict, domain object, etc.)
            api_model: Target Pydantic model class
            
        Returns:
            Validated API model instance
            
        Raises:
            HTTPException: If conversion fails
        """
        try:
            if isinstance(data, dict):
                return api_model.model_validate(data)
            else:
                # Handle domain objects
                return api_model.model_validate(data, from_attributes=True)
        except ValidationError as e:
            logger.error(f"Validation error converting to {api_model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data validation error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error converting to {api_model.__name__}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal conversion error"
            )
    
    @staticmethod
    def safe_convert_list_to_api_models(data_list: List[Any], api_model: Type[T]) -> List[T]:
        """
        Safely convert list of data to API models.
        
        Args:
            data_list: List of source data
            api_model: Target Pydantic model class
            
        Returns:
            List of validated API model instances
        """
        results = []
        for i, item in enumerate(data_list):
            try:
                converted = SafeConverter.safe_convert_to_api_model(item, api_model)
                results.append(converted)
            except HTTPException:
                logger.warning(f"Skipping invalid item at index {i} in list conversion")
                # Skip invalid items instead of failing the entire list
                continue
        return results


class EnumConverter:
    """Utility for safe enum conversions from Supabase string values."""
    
    @staticmethod
    def safe_contact_type(value: Any) -> ContactType:
        """Safely convert to ContactType enum."""
        if value is None:
            return ContactType.PROSPECT
        try:
            return ContactType(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid contact_type value: {value}, using default")
            return ContactType.PROSPECT
    
    @staticmethod
    def safe_contact_status(value: Any) -> ContactStatus:
        """Safely convert to ContactStatus enum."""
        if value is None:
            return ContactStatus.ACTIVE
        try:
            return ContactStatus(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid contact_status value: {value}, using default")
            return ContactStatus.ACTIVE
    
    @staticmethod
    def safe_contact_priority(value: Any) -> ContactPriority:
        """Safely convert to ContactPriority enum."""
        if value is None:
            return ContactPriority.MEDIUM
        try:
            return ContactPriority(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid contact_priority value: {value}, using default")
            return ContactPriority.MEDIUM
    
    @staticmethod
    def safe_contact_source(value: Any) -> Optional[ContactSource]:
        """Safely convert to ContactSource enum."""
        if value is None:
            return None
        try:
            return ContactSource(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid contact_source value: {value}, using None")
            return None
    
    @staticmethod
    def safe_relationship_status(value: Any) -> RelationshipStatus:
        """Safely convert to RelationshipStatus enum."""
        if value is None:
            return RelationshipStatus.PROSPECT
        try:
            return RelationshipStatus(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid relationship_status value: {value}, using default")
            return RelationshipStatus.PROSPECT
    
    @staticmethod
    def safe_lifecycle_stage(value: Any) -> LifecycleStage:
        """Safely convert to LifecycleStage enum."""
        if value is None:
            return LifecycleStage.AWARENESS
        try:
            return LifecycleStage(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid lifecycle_stage value: {value}, using default")
            return LifecycleStage.AWARENESS
    
    @staticmethod
    def safe_job_type(value: Any) -> JobType:
        """Safely convert to JobType enum."""
        if value is None:
            return JobType.SERVICE
        try:
            return JobType(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid job_type value: {value}, using default")
            return JobType.SERVICE
    
    @staticmethod
    def safe_job_status(value: Any) -> JobStatus:
        """Safely convert to JobStatus enum."""
        if value is None:
            return JobStatus.DRAFT
        try:
            return JobStatus(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid job_status value: {value}, using default")
            return JobStatus.DRAFT
    
    @staticmethod
    def safe_job_priority(value: Any) -> JobPriority:
        """Safely convert to JobPriority enum."""
        if value is None:
            return JobPriority.MEDIUM
        try:
            return JobPriority(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid job_priority value: {value}, using default")
            return JobPriority.MEDIUM
    
    @staticmethod
    def safe_job_source(value: Any) -> JobSource:
        """Safely convert to JobSource enum."""
        if value is None:
            return JobSource.OTHER
        try:
            return JobSource(str(value).lower())
        except (ValueError, AttributeError):
            logger.warning(f"Invalid job_source value: {value}, using default")
            return JobSource.OTHER


class SupabaseConverter:
    """Utility for converting Supabase data to Python objects."""
    
    @staticmethod
    def parse_json_field(value: Any, default: Any = None) -> Any:
        """Safely parse JSON field from Supabase."""
        if value is None:
            return default
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse JSON: {value}")
                return default
        return value
    
    @staticmethod
    def parse_datetime(value: Any) -> Optional[datetime]:
        """Safely parse datetime from Supabase."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Handle ISO format with Z suffix
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse datetime: {value}")
                return None
        return value
    
    @staticmethod
    def parse_uuid(value: Any) -> Optional[UUID]:
        """Safely parse UUID from Supabase."""
        if value is None:
            return None
        try:
            return UUID(str(value))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse UUID: {value}")
            return None
    
    @staticmethod
    def parse_list_field(value: Any, default: Optional[List] = None) -> List:
        """Safely parse list field from Supabase."""
        if default is None:
            default = []
        if value is None:
            return default
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else default
            except (json.JSONDecodeError, ValueError):
                return default
        if isinstance(value, list):
            return value
        return default
    
    @staticmethod
    def parse_dict_field(value: Any, default: Optional[Dict] = None) -> Dict:
        """Safely parse dict field from Supabase."""
        if default is None:
            default = {}
        if value is None:
            return default
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, dict) else default
            except (json.JSONDecodeError, ValueError):
                return default
        if isinstance(value, dict):
            return value
        return default 