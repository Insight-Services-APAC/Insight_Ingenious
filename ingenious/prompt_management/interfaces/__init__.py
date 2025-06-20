"""
Prompt Management interfaces module.

This module exports the REST controllers for the prompt_management bounded context.
"""

from .rest_controllers import PromptManagementController, UpdatePromptRequest

__all__ = [
    "PromptManagementController",
    "UpdatePromptRequest",
]
