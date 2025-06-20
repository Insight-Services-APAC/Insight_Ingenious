"""
Legacy external integrations routes module.

This module maintains backward compatibility by re-exporting the external integrations router
from the new external_integrations bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.external_integrations.interfaces.rest_controllers directly.
"""

# Import the new external integrations router from the bounded context
from ...external_integrations.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
