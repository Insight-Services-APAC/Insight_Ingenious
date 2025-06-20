"""
Legacy events routes module.

This module maintains backward compatibility by re-exporting the events router
from the new shared interfaces.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.shared.interfaces.rest_controllers directly.
"""

# Import the new events router from the shared interfaces
from ...shared.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
