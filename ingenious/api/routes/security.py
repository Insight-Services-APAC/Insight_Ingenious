"""
Legacy security routes module.

This module maintains backward compatibility by re-exporting the security router
from the new security bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.security.interfaces.rest_controllers directly.
"""

# Import the new security router from the bounded context
from ...security.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
