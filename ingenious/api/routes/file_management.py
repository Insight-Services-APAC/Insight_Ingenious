"""
Legacy file management routes module.

This module maintains backward compatibility by re-exporting the file management router
from the new file_management bounded context.

Note: This is part of the migration strategy. After migration is complete,
imports should use ingenious.file_management.interfaces.rest_controllers directly.
"""

# Import the new file management router from the bounded context
from ...file_management.interfaces.rest_controllers import router

# Maintain backward compatibility
__all__ = ["router"]
