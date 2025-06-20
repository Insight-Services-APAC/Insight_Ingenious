"""
Legacy API routes module.

This module provides backward compatibility by re-exporting routers from
the new DDD bounded context interfaces.

Note: This is part of the migration strategy. After migration is complete,
these legacy routes will be removed and imports should use the new
bounded context interfaces directly.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

# Re-export routers from new bounded contexts for backward compatibility
from ...chat.interfaces.rest_controllers import router as chat_router
from ...diagnostics.interfaces.rest_controllers import router as diagnostic_router
from ...prompt_management.interfaces.rest_controllers import router as prompts_router
from ...shared.interfaces.rest_controllers import router as events_router


# Create legacy route modules for backward compatibility
class LegacyRouteModule:
    """Helper class to create legacy route modules."""

    def __init__(self, router):
        self.router = router


# Legacy modules
chat = LegacyRouteModule(chat_router)
conversation = LegacyRouteModule(
    chat_router
)  # conversation routes are now part of chat
diagnostic = LegacyRouteModule(diagnostic_router)
events = LegacyRouteModule(events_router)
message_feedback = LegacyRouteModule(
    chat_router
)  # message feedback routes are now part of chat
prompts = LegacyRouteModule(prompts_router)
