"""
Main CLI entry point.

This module provides the main command-line interface for Insight Ingenious.
It has been refactored to use the DDD-based CLI structure.
"""

from ingenious.cli.main import app

# Re-export the app for backward compatibility
__all__ = ["app"]
