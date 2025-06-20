"""
Test data fixtures and sample data for testing.

This module provides consistent test data across all test cases.
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


class TestDataProvider:
    """Centralized test data provider."""

    def __init__(self):
        self.base_timestamp = datetime(2023, 1, 1, 12, 0, 0)

    # Chat Test Data
    @property
    def sample_chat_request(self) -> Dict[str, Any]:
        """Sample chat request for testing."""
        return {
            "user_prompt": "Hello, how are you?",
            "conversation_flow": "general",
            "user_id": "test-user-123",
            "thread_id": "test-thread-123",
        }

    @property
    def sample_chat_response(self) -> Dict[str, Any]:
        """Sample chat response for testing."""
        return {
            "thread_id": "test-thread-123",
            "message_id": "test-message-123",
            "agent_response": "I'm doing well, thank you for asking!",
            "event_type": "response",
            "token_count": 25,
        }

    @property
    def sample_message(self) -> Dict[str, Any]:
        """Sample message for testing."""
        return {
            "message_id": str(uuid4()),
            "thread_id": "test-thread-123",
            "content": "Test message content",
            "user_id": "test-user-123",
            "timestamp": self.base_timestamp.isoformat(),
            "event_type": "user_message",
        }

    @property
    def sample_thread(self) -> Dict[str, Any]:
        """Sample thread for testing."""
        return {
            "thread_id": "test-thread-123",
            "user_id": "test-user-123",
            "topic": "General conversation",
            "created_at": self.base_timestamp.isoformat(),
            "messages": [],
        }

    # Configuration Test Data
    @property
    def sample_config(self) -> Dict[str, Any]:
        """Sample configuration for testing."""
        return {
            "application": {
                "name": "test-project",
                "environment": "test",
                "log_level": "DEBUG",
            },
            "server": {"host": "127.0.0.1", "port": 8000},
            "llm": {"default_model": "gpt-4", "max_tokens": 4000, "temperature": 0.7},
        }

    @property
    def sample_profile(self) -> Dict[str, Any]:
        """Sample profile configuration for testing."""
        return {
            "name": "test",
            "models": [
                {
                    "model": "gpt-4",
                    "api_key": "test_api_key",
                    "base_url": "https://test.openai.azure.com",
                    "api_version": "2023-05-15",
                }
            ],
        }

    # CLI Test Data
    @property
    def sample_project_config(self) -> Dict[str, Any]:
        """Sample project configuration for CLI testing."""
        return {"name": "test-project", "path": "/tmp/test-project", "profile": "dev"}

    @property
    def sample_server_config(self) -> Dict[str, Any]:
        """Sample server configuration for CLI testing."""
        return {
            "host": "127.0.0.1",
            "port": 8000,
            "project_dir": "/tmp/test-project",
            "profile_dir": "/tmp/profiles",
        }

    # Diagnostics Test Data
    @property
    def sample_diagnostic_check(self) -> Dict[str, Any]:
        """Sample diagnostic check for testing."""
        return {
            "name": "Database Connection",
            "description": "Check database connectivity",
            "category": "infrastructure",
            "timeout_seconds": 30,
        }

    @property
    def sample_diagnostic_result(self) -> Dict[str, Any]:
        """Sample diagnostic result for testing."""
        return {
            "check_id": "check-123",
            "name": "Database Connection",
            "status": "healthy",
            "message": "Database connection successful",
            "execution_time": 0.25,
            "timestamp": self.base_timestamp.isoformat(),
        }

    @property
    def sample_system_health(self) -> Dict[str, Any]:
        """Sample system health data for testing."""
        return {
            "service_name": "ingenious",
            "overall_status": "healthy",
            "results": [self.sample_diagnostic_result],
            "last_updated": self.base_timestamp.isoformat(),
        }

    # External Integrations Test Data
    @property
    def sample_llm_request(self) -> Dict[str, Any]:
        """Sample LLM request for testing."""
        return {
            "prompt": "What is the weather like?",
            "model": "gpt-4",
            "max_tokens": 100,
            "temperature": 0.7,
        }

    @property
    def sample_llm_response(self) -> Dict[str, Any]:
        """Sample LLM response for testing."""
        return {
            "response": "I don't have access to real-time weather data.",
            "model": "gpt-4",
            "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
            "finish_reason": "stop",
        }

    @property
    def sample_moderation_request(self) -> Dict[str, Any]:
        """Sample content moderation request for testing."""
        return {"text": "This is a safe message to test."}

    @property
    def sample_moderation_response(self) -> Dict[str, Any]:
        """Sample content moderation response for testing."""
        return {
            "flagged": False,
            "categories": {
                "hate": False,
                "violence": False,
                "sexual": False,
                "self-harm": False,
            },
            "category_scores": {
                "hate": 0.001,
                "violence": 0.002,
                "sexual": 0.001,
                "self-harm": 0.001,
            },
        }

    # File Management Test Data
    @property
    def sample_file_data(self) -> Dict[str, Any]:
        """Sample file data for testing."""
        return {
            "file_id": "file-123",
            "filename": "test_document.txt",
            "content_type": "text/plain",
            "size": 1024,
            "upload_date": self.base_timestamp.isoformat(),
            "checksum": "abc123def456",
        }

    @property
    def sample_directory_data(self) -> Dict[str, Any]:
        """Sample directory data for testing."""
        return {
            "directory_id": "dir-123",
            "name": "test_directory",
            "path": "/uploads/test_directory",
            "created_date": self.base_timestamp.isoformat(),
            "file_count": 5,
        }

    # Security Test Data
    @property
    def sample_user(self) -> Dict[str, Any]:
        """Sample user for testing."""
        return {
            "user_id": "user-123",
            "username": "testuser",
            "email": "test@example.com",
            "created_at": self.base_timestamp.isoformat(),
            "is_active": True,
            "roles": ["user"],
        }

    @property
    def sample_auth_token(self) -> Dict[str, Any]:
        """Sample authentication token for testing."""
        return {
            "token_id": "token-123",
            "user_id": "user-123",
            "token_type": "bearer",
            "expires_at": "2023-12-31T23:59:59",
            "is_valid": True,
        }

    @property
    def sample_permission(self) -> Dict[str, Any]:
        """Sample permission for testing."""
        return {
            "permission_id": "perm-123",
            "name": "read_chat",
            "description": "Permission to read chat messages",
            "resource": "chat",
            "action": "read",
        }

    # Error Test Data
    @property
    def sample_error_response(self) -> Dict[str, Any]:
        """Sample error response for testing."""
        return {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "details": "The user_prompt field is required",
            },
            "timestamp": self.base_timestamp.isoformat(),
        }

    # Utility methods
    def get_batch_data(self, data_type: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate a batch of test data items."""
        base_data = getattr(self, f"sample_{data_type}", {})
        batch = []

        for i in range(count):
            item = base_data.copy()
            # Add unique identifiers
            for key, value in item.items():
                if key.endswith("_id") and isinstance(value, str):
                    item[key] = f"{value}-{i}"
            batch.append(item)

        return batch

    def get_invalid_data(self, data_type: str) -> Dict[str, Any]:
        """Get invalid test data for negative testing."""
        invalid_data_map = {
            "chat_request": {
                "user_prompt": "",  # Empty prompt
                "conversation_flow": None,  # Missing required field
                "user_id": None,
            },
            "config": {
                "application": None,  # Missing required section
                "server": {"port": "invalid"},  # Invalid port type
            },
            "user": {
                "username": "",  # Empty username
                "email": "invalid-email",  # Invalid email format
                "user_id": None,
            },
        }

        return invalid_data_map.get(data_type, {})
