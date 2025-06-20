"""
Diagnostics interfaces module.

This module exports the REST controllers for the diagnostics bounded context.
"""

from .rest_controllers import DiagnosticsController

__all__ = [
    "DiagnosticsController",
]
