"""
Legacy prompts routes module.

This module maintains backward compatibility by re-exporting the prompts router
from the new prompt_management bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.prompt_management.interfaces.rest_controllers directly.
"""

# Import the new prompts router from the bounded context
from ...prompt_management.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
