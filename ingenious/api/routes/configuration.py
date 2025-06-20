"""
Legacy configuration routes module.

This module maintains backward compatibility by re-exporting the configuration router
from the new configuration bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.configuration.interfaces.rest_controllers directly.
"""

# Import the new configuration router from the bounded context
from ...configuration.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
