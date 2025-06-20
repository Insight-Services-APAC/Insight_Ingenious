"""
Unit tests for security domain entities.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from ingenious.security.domain.entities import (
    AuthenticationToken,
    Permission,
    SecurityEvent,
    User,
    UserRole,
)


class TestUserRole:
    """Test cases for UserRole enum."""

    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
        assert UserRole.GUEST.value == "guest"
        assert UserRole.SERVICE.value == "service"


class TestPermission:
    """Test cases for Permission enum."""

    def test_permission_values(self):
        """Test Permission enum values."""
        assert Permission.READ.value == "read"
        assert Permission.WRITE.value == "write"
        assert Permission.DELETE.value == "delete"
        assert Permission.ADMIN.value == "admin"
        assert Permission.CHAT.value == "chat"
        assert Permission.CONFIGURE.value == "configure"


class TestUser:
    """Test cases for User entity."""

    def test_user_creation_with_defaults(self):
        """Test creating a user with default values."""
        user = User(username="testuser")

        assert user.username == "testuser"
        assert user.user_id is not None
        assert user.email is None
        assert user.full_name is None
        assert user.role == UserRole.USER
        assert user.permissions == []
        assert isinstance(user.created_at, datetime)
        assert user.is_active is True
        assert user.metadata == {}
        assert user.last_login is None

    def test_user_creation_with_all_parameters(self):
        """Test creating a user with all parameters."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        permissions = [Permission.READ, Permission.WRITE]
        metadata = {"department": "engineering", "level": "senior"}

        user = User(
            username="admin",
            user_id="custom-id",
            email="admin@example.com",
            full_name="Admin User",
            role=UserRole.ADMIN,
            permissions=permissions,
            created_at=created_at,
            is_active=False,
            metadata=metadata,
        )

        assert user.username == "admin"
        assert user.user_id == "custom-id"
        assert user.email == "admin@example.com"
        assert user.full_name == "Admin User"
        assert user.role == UserRole.ADMIN
        assert user.permissions == permissions
        assert user.created_at == created_at
        assert user.is_active is False
        assert user.metadata == metadata

    def test_has_permission_with_explicit_permission(self):
        """Test has_permission with explicitly granted permission."""
        user = User(
            username="testuser", permissions=[Permission.READ, Permission.WRITE]
        )

        assert user.has_permission(Permission.READ) is True
        assert user.has_permission(Permission.WRITE) is True
        assert user.has_permission(Permission.DELETE) is False

    def test_has_permission_with_admin_role(self):
        """Test has_permission with admin role (has all permissions)."""
        user = User(username="admin", role=UserRole.ADMIN)

        assert user.has_permission(Permission.READ) is True
        assert user.has_permission(Permission.WRITE) is True
        assert user.has_permission(Permission.DELETE) is True
        assert user.has_permission(Permission.ADMIN) is True

    def test_add_permission(self):
        """Test adding permissions to a user."""
        user = User(username="testuser")

        assert Permission.READ not in user.permissions

        user.add_permission(Permission.READ)
        assert Permission.READ in user.permissions

        # Adding same permission again should not duplicate
        user.add_permission(Permission.READ)
        assert user.permissions.count(Permission.READ) == 1

    def test_remove_permission(self):
        """Test removing permissions from a user."""
        user = User(
            username="testuser", permissions=[Permission.READ, Permission.WRITE]
        )

        assert Permission.READ in user.permissions

        user.remove_permission(Permission.READ)
        assert Permission.READ not in user.permissions
        assert Permission.WRITE in user.permissions

        # Removing non-existent permission should not raise error
        user.remove_permission(Permission.DELETE)

    def test_activate_deactivate(self):
        """Test user activation and deactivation."""
        user = User(username="testuser", is_active=True)

        user.deactivate()
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    @patch("ingenious.security.domain.entities.datetime")
    def test_record_login(self, mock_datetime):
        """Test recording user login."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        user = User(username="testuser")
        assert user.last_login is None

        user.record_login()
        assert user.last_login == mock_now

    def test_user_equality(self):
        """Test user equality based on user_id."""
        user1 = User(username="user1", user_id="same-id")
        user2 = User(username="user2", user_id="same-id")
        user3 = User(username="user1", user_id="different-id")

        assert user1 == user2  # Same ID
        assert user1 != user3  # Different ID
        assert user1 != "not a user"  # Different type


class TestAuthenticationToken:
    """Test cases for AuthenticationToken value object."""

    def test_token_creation(self):
        """Test creating an authentication token."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        scopes = ["read", "write"]

        token = AuthenticationToken(
            token="abc123",
            user_id="user-id",
            expires_at=expires_at,
            token_type="bearer",
            scopes=scopes,
        )

        assert token.token == "abc123"
        assert token.user_id == "user-id"
        assert token.expires_at == expires_at
        assert token.token_type == "bearer"
        assert token.scopes == scopes
        assert isinstance(token.created_at, datetime)

    def test_token_creation_with_defaults(self):
        """Test creating a token with default values."""
        expires_at = datetime.utcnow() + timedelta(hours=1)

        token = AuthenticationToken(
            token="abc123",
            user_id="user-id",
            expires_at=expires_at,
        )

        assert token.token_type == "bearer"
        assert token.scopes == []

    def test_is_expired_property(self):
        """Test is_expired property."""
        # Expired token
        expired_token = AuthenticationToken(
            token="expired",
            user_id="user-id",
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert expired_token.is_expired is True

        # Valid token
        valid_token = AuthenticationToken(
            token="valid",
            user_id="user-id",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert valid_token.is_expired is False

    def test_is_valid_property(self):
        """Test is_valid property."""
        # Expired token
        expired_token = AuthenticationToken(
            token="expired",
            user_id="user-id",
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert expired_token.is_valid is False

        # Valid token
        valid_token = AuthenticationToken(
            token="valid",
            user_id="user-id",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert valid_token.is_valid is True

    def test_has_scope(self):
        """Test has_scope method."""
        token = AuthenticationToken(
            token="abc123",
            user_id="user-id",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["read", "write", "admin"],
        )

        assert token.has_scope("read") is True
        assert token.has_scope("write") is True
        assert token.has_scope("delete") is False


class TestSecurityEvent:
    """Test cases for SecurityEvent entity."""

    def test_security_event_creation_with_defaults(self):
        """Test creating a security event with default values."""
        event = SecurityEvent(event_type="login_attempt")

        assert event.event_type == "login_attempt"
        assert event.event_id is not None
        assert event.user_id is None
        assert event.ip_address is None
        assert event.user_agent is None
        assert event.details == {}
        assert isinstance(event.timestamp, datetime)

    def test_security_event_creation_with_all_parameters(self):
        """Test creating a security event with all parameters."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        details = {"reason": "invalid_password", "attempts": 3}

        event = SecurityEvent(
            event_type="login_failed",
            user_id="user-123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details=details,
            event_id="custom-event-id",
            timestamp=timestamp,
        )

        assert event.event_type == "login_failed"
        assert event.user_id == "user-123"
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Mozilla/5.0"
        assert event.details == details
        assert event.event_id == "custom-event-id"
        assert event.timestamp == timestamp

    def test_security_event_equality(self):
        """Test security event equality based on event_id."""
        event1 = SecurityEvent(event_type="login", event_id="same-id")
        event2 = SecurityEvent(event_type="logout", event_id="same-id")
        event3 = SecurityEvent(event_type="login", event_id="different-id")

        assert event1 == event2  # Same ID
        assert event1 != event3  # Different ID
        assert event1 != "not an event"  # Different type


class TestDomainEntityInteractions:
    """Test interactions between domain entities."""

    def test_user_with_token_workflow(self):
        """Test user authentication workflow with tokens."""
        user = User(username="testuser", user_id="user-123")

        # Create token for user
        token = AuthenticationToken(
            token="auth-token",
            user_id=user.user_id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            scopes=["read", "write"],
        )

        # Verify token belongs to user
        assert token.user_id == user.user_id
        assert token.is_valid is True
        assert token.has_scope("read") is True

        # Record login
        user.record_login()
        assert user.last_login is not None

    def test_security_event_logging_workflow(self):
        """Test security event logging for user actions."""
        user = User(username="admin", role=UserRole.ADMIN)

        # User performs action
        has_permission = user.has_permission(Permission.DELETE)
        assert has_permission is True

        # Log security event
        event = SecurityEvent(
            event_type="permission_check",
            user_id=user.user_id,
            details={
                "permission": Permission.DELETE.value,
                "granted": has_permission,
                "user_role": user.role.value,
            },
        )

        assert event.user_id == user.user_id
        assert event.details["granted"] is True
        assert event.details["user_role"] == "admin"

    def test_user_permission_management(self):
        """Test comprehensive user permission management."""
        user = User(username="developer", role=UserRole.USER)

        # Initially no permissions
        assert user.has_permission(Permission.READ) is False
        assert user.has_permission(Permission.WRITE) is False

        # Add permissions
        user.add_permission(Permission.READ)
        user.add_permission(Permission.WRITE)

        assert user.has_permission(Permission.READ) is True
        assert user.has_permission(Permission.WRITE) is True
        assert user.has_permission(Permission.DELETE) is False

        # Remove permission
        user.remove_permission(Permission.WRITE)
        assert user.has_permission(Permission.READ) is True
        assert user.has_permission(Permission.WRITE) is False
