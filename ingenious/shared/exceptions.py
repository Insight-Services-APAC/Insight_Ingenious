"""Shared domain exceptions."""


class DomainException(Exception):
    """Base exception for domain-specific errors."""

    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(DomainException):
    """Exception for validation errors."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class AuthorizationException(DomainException):
    """Exception for authorization errors."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class AuthenticationException(DomainException):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class ResourceNotFoundException(DomainException):
    """Exception for when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessRuleViolationException(DomainException):
    """Exception for business rule violations."""

    def __init__(self, message: str, rule_name: str = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule_name = rule_name
