from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class UserRole(Enum):
    """Enumeration for user roles."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    SERVICE = "service"


class Permission(Enum):
    """Enumeration for permissions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CHAT = "chat"
    CONFIGURE = "configure"


class User:
    """Domain entity representing a user."""

    def __init__(
        self,
        username: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        permissions: Optional[List[Permission]] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id or str(uuid4())
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.permissions = permissions or []
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        self.metadata = metadata or {}
        self.last_login: Optional[datetime] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions or self.role == UserRole.ADMIN

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True

    def record_login(self) -> None:
        """Record user login timestamp."""
        self.last_login = datetime.utcnow()

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id


class AuthenticationToken:
    """Value object representing an authentication token."""

    def __init__(
        self,
        token: str,
        user_id: str,
        expires_at: datetime,
        token_type: str = "bearer",
        scopes: Optional[List[str]] = None,
    ):
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at
        self.token_type = token_type
        self.scopes = scopes or []
        self.created_at = datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired)."""
        return not self.is_expired

    def has_scope(self, scope: str) -> bool:
        """Check if token has a specific scope."""
        return scope in self.scopes


class SecurityEvent:
    """Domain entity representing a security event."""

    def __init__(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.event_id = event_id or str(uuid4())
        self.event_type = event_type
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()

    def __eq__(self, other):
        if not isinstance(other, SecurityEvent):
            return False
        return self.event_id == other.event_id
