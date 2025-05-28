# Error Handling Improvements

## Overview of Changes

The error handling system in the Ingenious framework has been refactored to:

1. Eliminate duplicate logic across files
2. Improve maintainability through better organization
3. Maintain backward compatibility
4. Provide explicit export lists using `__all__`

## Key Improvements

### 1. Centralized Import System

- Replaced multiple try/except blocks with a more elegant import system
- Specialized error modules now use `__all__` to explicitly declare public classes
- Base `IngeniousError` is defined before imports to avoid circular dependencies

### 2. Module Organization

- Each specialized error type (database, cache, rate limit) has its own module
- All error classes are available directly from the main `ingenious.common.errors` module
- Specialized error modules inherit from the base class properly

### 3. Usage Examples

#### Importing and using errors

```python
# Import from the main module
from ingenious.common.errors import ValidationError, DatabaseError

# Create a validation error
error = ValidationError("Invalid input", fields={"username": "Must be at least 3 characters"})

# Convert to dictionary format for API responses
response = error.to_dict()
```

#### Handling errors

```python
from ingenious.common.errors import handle_exception

try:
    # Some code that might raise an exception
    result = perform_operation()
except Exception as e:
    # Convert any exception to a standardized error response
    error_response = handle_exception(e)
    return error_response
```

## Adding New Error Types

To add a new error type:

1. Create a new module in `ingenious/common/errors/` if it's a specialized domain
2. Define your error class extending `IngeniousError`
3. Add an `__all__` list declaring the public classes
4. Import your module in `__init__.py` if needed

Example:

```python
# In a new file like notification_errors.py
from ingenious.common.errors import IngeniousError

__all__ = ["NotificationError", "DeliveryFailedError"]

class NotificationError(IngeniousError):
    """Base class for notification-related errors."""
    # Implementation...

class DeliveryFailedError(NotificationError):
    """Error raised when a notification fails to deliver."""
    # Implementation...
```
