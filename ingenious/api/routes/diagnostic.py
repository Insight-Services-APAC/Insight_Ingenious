"""
Legacy diagnostic routes module.

This module maintains backward compatibility by re-exporting the diagnostics router
from the new diagnostics bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.diagnostics.interfaces.rest_controllers directly.
"""

# Import the new diagnostics router from the bounded context
from ...diagnostics.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
