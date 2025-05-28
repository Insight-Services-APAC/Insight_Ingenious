"""
This module re-exports the Message class from ingenious.domain.model.chat.message
to maintain backward compatibility and simplify imports.
"""

from ingenious.domain.model.chat.message import Message, MessageRole

__all__ = ["Message", "MessageRole"]
