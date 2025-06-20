"""
Domain Exceptions

Custom exceptions for domain-specific business rule violations.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DomainValidationError(DomainException):
    """Raised when domain validation rules are violated."""
    
    def __init__(self, message: str):
        super().__init__(message, "DOMAIN_VALIDATION_ERROR")


class BusinessRuleViolationError(DomainException):
    """Raised when business rules are violated."""
    
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")


class EntityNotFoundError(DomainException):
    """Raised when a required entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, "ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityError(DomainException):
    """Raised when attempting to create an entity that already exists."""
    
    def __init__(self, entity_type: str, identifier: str):
        message = f"{entity_type} with identifier '{identifier}' already exists"
        super().__init__(message, "DUPLICATE_ENTITY")
        self.entity_type = entity_type
        self.identifier = identifier


class InsufficientPermissionsError(DomainException):
    """Raised when user lacks required permissions for an operation."""
    
    def __init__(self, operation: str):
        message = f"Insufficient permissions to perform operation: {operation}"
        super().__init__(message, "INSUFFICIENT_PERMISSIONS")
        self.operation = operation


class InvalidOperationError(DomainException):
    """Raised when attempting an invalid operation on an entity."""
    
    def __init__(self, operation: str, reason: str):
        message = f"Invalid operation '{operation}': {reason}"
        super().__init__(message, "INVALID_OPERATION")
        self.operation = operation
        self.reason = reason


class DatabaseError(DomainException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR") 