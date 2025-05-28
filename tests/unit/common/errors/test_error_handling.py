"""
Tests for the error converters and handlers in ingenious.common.errors.
"""

from ingenious.common.errors.base import IngeniousError
from ingenious.common.errors.common import NotFoundError
from ingenious.common.errors.converters import (
    convert_exception,
    register_converter,
    reset_converters,
)
from ingenious.common.errors.handlers import (
    get_error_handler,
    handle_exception,
    register_error_handler,
    reset_error_handlers,
)


class TestErrorConverters:
    """Test suite for error converters."""

    def setup_method(self):
        """Reset converters before each test."""
        reset_converters()

    def test_register_converter(self):
        """Test registering a custom converter."""

        class CustomError(Exception):
            pass

        @register_converter(CustomError)
        def convert_custom_error(exc):
            return NotFoundError(
                message=f"Converted: {str(exc)}",
                resource_id="test_resource",
                resource_type="test_type",
            )

        # Test converting the error
        original = CustomError("Test error")
        converted = convert_exception(original)

        assert isinstance(converted, NotFoundError)
        assert "Converted: Test error" in str(converted)

    def test_convert_exception_no_converter(self):
        """Test converting an exception without a registered converter."""

        class UnregisteredError(Exception):
            pass

        # When no converter is registered, it should return a generic IngeniousError
        original = UnregisteredError("No converter")
        converted = convert_exception(original)

        assert isinstance(converted, IngeniousError)
        assert "UnregisteredError: No converter" in str(converted)

    def test_convert_exception_already_ingenious_error(self):
        """Test converting an exception that's already an IngeniousError."""
        error = NotFoundError(
            message="Already an IngeniousError",
            resource_id="test_resource",
            resource_type="test_type",
        )
        converted = convert_exception(error)

        # Should return the original error
        assert converted is error


class TestErrorHandlers:
    """Test suite for error handlers."""

    def setup_method(self):
        """Reset handlers before each test."""
        reset_error_handlers()

    def test_register_error_handler(self):
        """Test registering a custom error handler."""
        handled_errors = []

        @register_error_handler(NotFoundError)
        def handle_not_found(error):
            handled_errors.append(("not_found", error))
            return {"status": "error", "message": str(error)}

        # Test handling the error
        error = NotFoundError(
            message="Resource not found",
            resource_id="test_resource",
            resource_type="test_type",
        )
        result = handle_exception(error)

        assert len(handled_errors) == 1
        assert handled_errors[0][0] == "not_found"
        assert handled_errors[0][1] is error
        assert result == {"status": "error", "message": "Resource not found"}

    def test_handle_exception_no_handler(self):
        """Test handling an exception without a registered handler."""

        class UnhandledError(IngeniousError):
            pass

        # When no handler is registered, it should use the default handler
        error = UnhandledError("No handler")
        result = handle_exception(error)

        # Default handler should return a dict with status and message
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "No handler" in result["message"]

    def test_get_error_handler(self):
        """Test getting a registered error handler."""

        @register_error_handler(NotFoundError)
        def handle_not_found(error):
            return {"custom": "handler"}

        handler = get_error_handler(NotFoundError)
        assert handler is not None
        assert handler(
            NotFoundError(
                message="test", resource_id="test_resource", resource_type="test_type"
            )
        ) == {"custom": "handler"}

    def test_get_error_handler_inheritance(self):
        """Test handler inheritance for subclasses."""

        @register_error_handler(IngeniousError)
        def handle_ingenious(error):
            return {"handled_by": "ingenious"}

        # NotFoundError is a subclass of IngeniousError, so it should use
        # the IngeniousError handler if no specific handler is registered
        handler = get_error_handler(NotFoundError)
        assert handler is not None
        assert handler(
            NotFoundError(
                message="test", resource_id="test_resource", resource_type="test_type"
            )
        ) == {"handled_by": "ingenious"}
