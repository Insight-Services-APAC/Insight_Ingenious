"""
Common error types for the Ingenious framework.

This module defines common error types that are used throughout the application.
"""

from typing import Dict, Optional

from ingenious.common.errors.base import IngeniousError


class ValidationError(IngeniousError):
    """Error raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        fields: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Initialize the validation error.

        Args:
            message: Human-readable error message
            fields: Dictionary of field-specific validation errors
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {"fields": fields or {}}
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs,
        )


class NotFoundError(IngeniousError):
    """Error raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the not found error.

        Args:
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
            message: Optional custom error message
            **kwargs: Additional arguments to pass to the parent class
        """
        if message is None:
            message = f"{resource_type} with ID '{resource_id}' not found"

        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
            **kwargs,
        )


class AuthenticationError(IngeniousError):
    """Error raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        """
        Initialize the authentication error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            **kwargs,
        )


class AuthorizationError(IngeniousError):
    """Error raised when authorization fails."""

    def __init__(
        self, message: str = "Not authorized to perform this action", **kwargs
    ):
        """
        Initialize the authorization error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(
            message=message, status_code=403, error_code="AUTHORIZATION_ERROR", **kwargs
        )


class ServiceError(IngeniousError):
    """Error raised when an external service fails."""

    def __init__(
        self, service_name: str, message: str = "External service error", **kwargs
    ):
        """
        Initialize the service error.

        Args:
            service_name: Name of the external service that failed
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {"service": service_name}
        super().__init__(
            message=message,
            status_code=502,
            error_code="SERVICE_ERROR",
            details=details,
            **kwargs,
        )


class ConfigurationError(IngeniousError):
    """Error raised when there's a configuration issue."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the configuration error.

        Args:
            message: Human-readable error message
            config_key: The configuration key that has an issue
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs,
        )
