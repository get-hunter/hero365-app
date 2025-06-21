"""
Error Handling Middleware

Centralized error handling for the application using clean architecture principles.
"""

import logging
import traceback
from typing import Callable, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...application.exceptions.application_exceptions import (
    ApplicationException, AuthenticationFailedException, AuthorizationFailedException,
    UserNotFoundError, ItemNotFoundError, PermissionDeniedError,
    ValidationError as AppValidationError, ServiceUnavailableError
)
from ...domain.exceptions.domain_exceptions import (
    DomainException, DomainValidationError, BusinessRuleViolationError,
    EntityNotFoundError, DuplicateEntityError, InsufficientPermissionsError,
    InvalidOperationError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for centralized error handling.
    
    This middleware catches all exceptions and converts them to appropriate
    HTTP responses with consistent error format.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions."""
        # Log ALL requests to see what's being processed
        logger.info(f"ErrorHandlerMiddleware processing: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            logger.info(f"ErrorHandlerMiddleware completed: {request.method} {request.url.path} -> {response.status_code}")
            return response
        
        except HTTPException as e:
            logger.error(f"HTTPException in ErrorHandlerMiddleware: {request.method} {request.url.path} -> {e.status_code}: {e.detail}")
            # Re-raise HTTPExceptions as they are already properly formatted
            raise
        
        except Exception as exc:
            logger.error(f"Exception in ErrorHandlerMiddleware: {request.method} {request.url.path} -> {type(exc).__name__}: {str(exc)}")
            return await self._handle_exception(request, exc)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle different types of exceptions and return appropriate responses.
        
        Args:
            request: The incoming request
            exc: The exception that occurred
            
        Returns:
            JSONResponse with error details
        """
        # Log the exception
        logger.error(
            f"Exception occurred: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
                "client": request.client.host if request.client else None
            }
        )
        
        # Handle domain exceptions
        if isinstance(exc, DomainException):
            return self._handle_domain_exception(exc)
        
        # Handle application exceptions
        if isinstance(exc, ApplicationException):
            return self._handle_application_exception(exc)
        
        # Handle validation errors (Pydantic)
        if "ValidationError" in str(type(exc)):
            return self._handle_validation_error(exc)
        
        # Handle unexpected exceptions
        return self._handle_unexpected_exception(exc)
    
    def _handle_domain_exception(self, exc: DomainException) -> JSONResponse:
        """Handle domain layer exceptions."""
        error_mappings = {
            DomainValidationError: (status.HTTP_400_BAD_REQUEST, "validation_error"),
            BusinessRuleViolationError: (status.HTTP_409_CONFLICT, "business_rule_violation"),
            EntityNotFoundError: (status.HTTP_404_NOT_FOUND, "entity_not_found"),
            DuplicateEntityError: (status.HTTP_409_CONFLICT, "duplicate_entity"),
            InsufficientPermissionsError: (status.HTTP_403_FORBIDDEN, "insufficient_permissions"),
            InvalidOperationError: (status.HTTP_400_BAD_REQUEST, "invalid_operation"),
            DatabaseError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "database_error"),
        }
        
        status_code, error_type = error_mappings.get(
            type(exc), 
            (status.HTTP_500_INTERNAL_SERVER_ERROR, "domain_error")
        )
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": error_type,
                    "message": str(exc),
                    "code": getattr(exc, 'error_code', None),
                    "details": self._get_exception_details(exc)
                }
            }
        )
    
    def _handle_application_exception(self, exc: ApplicationException) -> JSONResponse:
        """Handle application layer exceptions."""
        error_mappings = {
            AuthenticationFailedException: (status.HTTP_401_UNAUTHORIZED, "authentication_failed"),
            AuthorizationFailedException: (status.HTTP_403_FORBIDDEN, "authorization_failed"),
            UserNotFoundError: (status.HTTP_404_NOT_FOUND, "user_not_found"),
            ItemNotFoundError: (status.HTTP_404_NOT_FOUND, "item_not_found"),
            PermissionDeniedError: (status.HTTP_403_FORBIDDEN, "permission_denied"),
            AppValidationError: (status.HTTP_400_BAD_REQUEST, "validation_error"),
            ServiceUnavailableError: (status.HTTP_503_SERVICE_UNAVAILABLE, "service_unavailable"),
        }
        
        status_code, error_type = error_mappings.get(
            type(exc),
            (status.HTTP_500_INTERNAL_SERVER_ERROR, "application_error")
        )
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": error_type,
                    "message": str(exc),
                    "code": getattr(exc, 'error_code', None),
                    "details": self._get_exception_details(exc)
                }
            }
        )
    
    def _handle_validation_error(self, exc: Exception) -> JSONResponse:
        """Handle Pydantic validation errors."""
        # Extract validation error details
        details = []
        if hasattr(exc, 'errors'):
            for error in exc.errors():
                details.append({
                    "field": ".".join(str(loc) for loc in error.get("loc", [])),
                    "message": error.get("msg", ""),
                    "type": error.get("type", ""),
                })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "validation_error",
                    "message": "Request validation failed",
                    "details": details
                }
            }
        )
    
    def _handle_unexpected_exception(self, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Log full traceback for debugging
        logger.critical(
            f"Unexpected exception: {type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "code": "INTERNAL_ERROR"
                }
            }
        )
    
    def _get_exception_details(self, exc: Exception) -> dict:
        """Extract additional details from exception."""
        details = {}
        
        # Add specific attributes based on exception type
        if hasattr(exc, 'entity_type'):
            details['entity_type'] = exc.entity_type
        if hasattr(exc, 'entity_id'):
            details['entity_id'] = exc.entity_id
        if hasattr(exc, 'operation'):
            details['operation'] = exc.operation
        if hasattr(exc, 'field'):
            details['field'] = exc.field
        
        return details


def create_error_response(
    error_type: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: dict = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        error_type: Type of error
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JSONResponse with error information
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": error_type,
                "message": message,
                "details": details or {}
            }
        }
    ) 