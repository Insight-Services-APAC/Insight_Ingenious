"""
Unit tests for chat domain entities.

This module tests the core business entities in the chat bounded context,
including Message, Thread, and ChatSession.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from ingenious.chat.domain.entities import Message, Thread, ChatSession


class TestMessage:
    """Test suite for Message entity."""
    
    def test_message_creation_with_defaults(self):
        """Test creating a message with default values."""
        # Arrange & Act
        message = Message(
            content="Hello, world!",
            user_id="user-123"
        )
        
        # Assert
        assert message.content == "Hello, world!"
        assert message.user_id == "user-123"
        assert message.message_id is not None
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
        assert message.thread_id is None
        assert message.event_type is None
    
    def test_message_creation_with_all_fields(self):
        """Test creating a message with all fields specified."""
        # Arrange
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        message = Message(
            content="Test message",
            user_id="user-456",
            thread_id="thread-789",
            message_id="msg-001",
            timestamp=timestamp,
            event_type="user_message"
        )
        
        # Assert
        assert message.content == "Test message"
        assert message.user_id == "user-456"
        assert message.thread_id == "thread-789"
        assert message.message_id == "msg-001"
        assert message.timestamp == timestamp
        assert message.event_type == "user_message"
    
    def test_message_equality(self):
        """Test message equality comparison."""
        # Arrange
        message1 = Message(content="Test", user_id="user-1", message_id="msg-1")
        message2 = Message(content="Different", user_id="user-2", message_id="msg-1")
        message3 = Message(content="Test", user_id="user-1", message_id="msg-2")
        
        # Act & Assert
        assert message1 == message2  # Same message_id
        assert message1 != message3  # Different message_id
        assert message1 != "not a message"  # Different type
    
    def test_message_string_representation(self):
        """Test message string representation."""
        # Arrange
        message = Message(content="Test", user_id="user-1", message_id="msg-1")
        
        # Act
        str_repr = str(message)
        
        # Assert
        assert "msg-1" in str_repr
        assert "user-1" in str_repr


class TestThread:
    """Test suite for Thread entity."""
    
    def test_thread_creation_with_defaults(self):
        """Test creating a thread with default values."""
        # Arrange & Act
        thread = Thread()
        
        # Assert
        assert thread.thread_id is not None
        assert thread.user_id is None
        assert thread.topic is None
        assert thread.created_at is not None
        assert isinstance(thread.created_at, datetime)
        assert thread.messages == []
        assert thread.memory_summary is None
    
    def test_thread_creation_with_all_fields(self):
        """Test creating a thread with all fields specified."""
        # Arrange
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        thread = Thread(
            thread_id="thread-123",
            user_id="user-456",
            topic="General discussion",
            created_at=created_at
        )
        
        # Assert
        assert thread.thread_id == "thread-123"
        assert thread.user_id == "user-456"
        assert thread.topic == "General discussion"
        assert thread.created_at == created_at
        assert thread.messages == []
    
    def test_add_message_to_thread(self):
        """Test adding a message to a thread."""
        # Arrange
        thread = Thread(thread_id="thread-123")
        message = Message(content="Test message", user_id="user-456")
        
        # Act
        thread.add_message(message)
        
        # Assert
        assert len(thread.messages) == 1
        assert thread.messages[0] == message
        assert message.thread_id == "thread-123"
    
    def test_add_multiple_messages_to_thread(self):
        """Test adding multiple messages to a thread."""
        # Arrange
        thread = Thread(thread_id="thread-123")
        message1 = Message(content="First message", user_id="user-456")
        message2 = Message(content="Second message", user_id="user-456")
        
        # Act
        thread.add_message(message1)
        thread.add_message(message2)
        
        # Assert
        assert len(thread.messages) == 2
        assert thread.messages[0] == message1
        assert thread.messages[1] == message2
        assert message1.thread_id == "thread-123"
        assert message2.thread_id == "thread-123"
    
    def test_get_recent_messages_default_limit(self):
        """Test getting recent messages with default limit."""
        # Arrange
        thread = Thread()
        messages = []
        
        # Create 15 messages with different timestamps
        for i in range(15):
            message = Message(
                content=f"Message {i}",
                user_id="user-456",
                timestamp=datetime(2023, 1, 1, 12, i, 0)
            )
            messages.append(message)
            thread.add_message(message)
        
        # Act
        recent_messages = thread.get_recent_messages()
        
        # Assert
        assert len(recent_messages) == 10  # Default limit
        # Should get the last 10 messages (sorted by timestamp)
        assert recent_messages[0].content == "Message 5"
        assert recent_messages[-1].content == "Message 14"
    
    def test_get_recent_messages_custom_limit(self):
        """Test getting recent messages with custom limit."""
        # Arrange
        thread = Thread()
        
        for i in range(8):
            message = Message(
                content=f"Message {i}",
                user_id="user-456",
                timestamp=datetime(2023, 1, 1, 12, i, 0)
            )
            thread.add_message(message)
        
        # Act
        recent_messages = thread.get_recent_messages(limit=3)
        
        # Assert
        assert len(recent_messages) == 3
        assert recent_messages[0].content == "Message 5"
        assert recent_messages[-1].content == "Message 7"
    
    def test_get_recent_messages_fewer_than_limit(self):
        """Test getting recent messages when fewer messages exist than limit."""
        # Arrange
        thread = Thread()
        
        for i in range(3):
            message = Message(content=f"Message {i}", user_id="user-456")
            thread.add_message(message)
        
        # Act
        recent_messages = thread.get_recent_messages(limit=10)
        
        # Assert
        assert len(recent_messages) == 3
    
    def test_thread_equality(self):
        """Test thread equality comparison."""
        # Arrange
        thread1 = Thread(thread_id="thread-1")
        thread2 = Thread(thread_id="thread-1")
        thread3 = Thread(thread_id="thread-2")
        
        # Act & Assert
        assert thread1 == thread2  # Same thread_id
        assert thread1 != thread3  # Different thread_id
        assert thread1 != "not a thread"  # Different type


class TestChatSession:
    """Test suite for ChatSession entity."""
    
    def test_chat_session_creation(self):
        """Test creating a chat session."""
        # Arrange & Act
        session = ChatSession(
            user_id="user-123",
            conversation_flow="general"
        )
        
        # Assert
        assert session.user_id == "user-123"
        assert session.conversation_flow == "general"
        assert session.session_id is not None
        assert session.created_at is not None
        assert isinstance(session.created_at, datetime)
        assert session.threads == {}
    
    def test_chat_session_creation_with_session_id(self):
        """Test creating a chat session with specified session ID."""
        # Arrange & Act
        session = ChatSession(
            user_id="user-123",
            conversation_flow="general",
            session_id="session-456"
        )
        
        # Assert
        assert session.session_id == "session-456"
        assert session.user_id == "user-123"
        assert session.conversation_flow == "general"
    
    def test_get_or_create_thread_new_thread(self):
        """Test creating a new thread in the session."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="general")
        
        # Act
        thread = session.get_or_create_thread()
        
        # Assert
        assert thread is not None
        assert thread.user_id == "user-123"
        assert thread.thread_id in session.threads
        assert session.threads[thread.thread_id] == thread
    
    def test_get_or_create_thread_existing_thread(self):
        """Test getting an existing thread from the session."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="general")
        
        # Create a thread first
        original_thread = session.get_or_create_thread(thread_id="thread-456")
        
        # Act
        retrieved_thread = session.get_or_create_thread(thread_id="thread-456")
        
        # Assert
        assert retrieved_thread == original_thread
        assert len(session.threads) == 1
    
    def test_get_or_create_thread_with_specific_id(self):
        """Test creating a thread with a specific ID."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="general")
        
        # Act
        thread = session.get_or_create_thread(thread_id="custom-thread-id")
        
        # Assert
        assert thread.thread_id == "custom-thread-id"
        assert thread.user_id == "user-123"
        assert "custom-thread-id" in session.threads
    
    def test_multiple_threads_in_session(self):
        """Test managing multiple threads in a session."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="general")
        
        # Act
        thread1 = session.get_or_create_thread(thread_id="thread-1")
        thread2 = session.get_or_create_thread(thread_id="thread-2")
        thread3 = session.get_or_create_thread(thread_id="thread-1")  # Should return existing
        
        # Assert
        assert len(session.threads) == 2
        assert thread1 == thread3  # Same thread returned
        assert thread1 != thread2  # Different threads
        assert "thread-1" in session.threads
        assert "thread-2" in session.threads


@pytest.mark.unit
class TestChatEntitiesIntegration:
    """Integration tests for chat entities working together."""
    
    def test_complete_chat_flow(self):
        """Test a complete chat flow with session, thread, and messages."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="support")
        
        # Act
        # Create a thread
        thread = session.get_or_create_thread(thread_id="support-thread")
        
        # Add user message
        user_message = Message(
            content="I need help with my account",
            user_id="user-123",
            event_type="user_message"
        )
        thread.add_message(user_message)
        
        # Add agent response
        agent_message = Message(
            content="I'll be happy to help you with your account",
            user_id="agent-456",
            event_type="agent_response"
        )
        thread.add_message(agent_message)
        
        # Assert
        assert len(thread.messages) == 2
        assert thread.messages[0].content == "I need help with my account"
        assert thread.messages[1].content == "I'll be happy to help you with your account"
        assert all(msg.thread_id == "support-thread" for msg in thread.messages)
        
        # Test getting recent messages
        recent_messages = thread.get_recent_messages(limit=5)
        assert len(recent_messages) == 2
        assert recent_messages[0] == user_message
        assert recent_messages[1] == agent_message
    
    def test_session_with_multiple_threads_and_messages(self):
        """Test session with multiple threads, each containing messages."""
        # Arrange
        session = ChatSession(user_id="user-123", conversation_flow="general")
        
        # Act
        # Thread 1: General conversation
        thread1 = session.get_or_create_thread(thread_id="general")
        thread1.add_message(Message(content="Hello!", user_id="user-123"))
        thread1.add_message(Message(content="Hi there!", user_id="agent-456"))
        
        # Thread 2: Technical support
        thread2 = session.get_or_create_thread(thread_id="support")
        thread2.add_message(Message(content="I have a technical issue", user_id="user-123"))
        thread2.add_message(Message(content="Let me help you with that", user_id="agent-789"))
        
        # Assert
        assert len(session.threads) == 2
        assert len(thread1.messages) == 2
        assert len(thread2.messages) == 2
        
        # Each thread should have its own messages
        assert thread1.messages[0].content == "Hello!"
        assert thread2.messages[0].content == "I have a technical issue"
        
        # Messages should be properly associated with their threads
        assert all(msg.thread_id == "general" for msg in thread1.messages)
        assert all(msg.thread_id == "support" for msg in thread2.messages)
