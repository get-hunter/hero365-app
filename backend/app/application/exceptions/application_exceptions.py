"""
Application Exceptions

Custom exceptions for application-specific scenarios and use case failures.
"""


class ApplicationException(Exception):
    """Base exception for all application-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UseCaseException(ApplicationException):
    """Base exception for use case execution failures."""
    
    def __init__(self, message: str, use_case: str = None):
        super().__init__(message, "USE_CASE_ERROR")
        self.use_case = use_case


class AuthenticationFailedException(ApplicationException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED")


class AuthorizationFailedException(ApplicationException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, "AUTHORIZATION_FAILED")


class UserNotFoundError(ApplicationException):
    """Raised when a user is not found."""
    
    def __init__(self, identifier: str):
        message = f"User not found: {identifier}"
        super().__init__(message, "USER_NOT_FOUND")
        self.identifier = identifier


class ItemNotFoundError(ApplicationException):
    """Raised when an item is not found."""
    
    def __init__(self, item_id: str):
        message = f"Item not found: {item_id}"
        super().__init__(message, "ITEM_NOT_FOUND")
        self.item_id = item_id


class UserAlreadyExistsError(ApplicationException):
    """Raised when attempting to create a user that already exists."""
    
    def __init__(self, identifier: str):
        message = f"User already exists: {identifier}"
        super().__init__(message, "USER_ALREADY_EXISTS")
        self.identifier = identifier


class InvalidCredentialsError(ApplicationException):
    """Raised when provided credentials are invalid."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "INVALID_CREDENTIALS")


class AccountInactiveError(ApplicationException):
    """Raised when attempting to authenticate with an inactive account."""
    
    def __init__(self, message: str = "Account is inactive"):
        super().__init__(message, "ACCOUNT_INACTIVE")


class PermissionDeniedError(ApplicationException):
    """Raised when user lacks permission for an operation."""
    
    def __init__(self, operation: str, resource: str = None):
        if resource:
            message = f"Permission denied for operation '{operation}' on resource '{resource}'"
        else:
            message = f"Permission denied for operation '{operation}'"
        super().__init__(message, "PERMISSION_DENIED")
        self.operation = operation
        self.resource = resource


class ValidationError(ApplicationException):
    """Raised when input validation fails at the application layer."""
    
    def __init__(self, field: str, message: str):
        full_message = f"Validation error for field '{field}': {message}"
        super().__init__(full_message, "VALIDATION_ERROR")
        self.field = field
        self.validation_message = message


class ServiceUnavailableError(ApplicationException):
    """Raised when an external service is unavailable."""
    
    def __init__(self, service_name: str, message: str = None):
        if message:
            full_message = f"Service '{service_name}' is unavailable: {message}"
        else:
            full_message = f"Service '{service_name}' is unavailable"
        super().__init__(full_message, "SERVICE_UNAVAILABLE")
        self.service_name = service_name


class ConcurrencyError(ApplicationException):
    """Raised when a concurrency conflict occurs."""
    
    def __init__(self, resource: str, message: str = None):
        if message:
            full_message = f"Concurrency conflict for resource '{resource}': {message}"
        else:
            full_message = f"Concurrency conflict for resource '{resource}'"
        super().__init__(full_message, "CONCURRENCY_ERROR")
        self.resource = resource


class RateLimitExceededError(ApplicationException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, operation: str, limit: int, window: str):
        message = f"Rate limit exceeded for operation '{operation}': {limit} requests per {window}"
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.operation = operation
        self.limit = limit
        self.window = window 