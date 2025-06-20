"""
Legacy conversation routes module.

This module maintains backward compatibility by re-exporting the chat router
from the new chat bounded context (conversation functionality is now part of chat).

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.chat.interfaces.rest_controllers directly.
"""

# Import the new chat router from the bounded context (contains conversation routes)
from ...chat.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
