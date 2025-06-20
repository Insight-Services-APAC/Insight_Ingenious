from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .entities import AuthenticationToken, Permission, SecurityEvent, User


class IUserRepository(ABC):
    """Repository interface for user persistence."""

    @abstractmethod
    async def save_user(self, user: User) -> None:
        """Save a user."""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        pass

    @abstractmethod
    async def list_users(self) -> List[User]:
        """List all users."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        pass


class IAuthenticationService(ABC):
    """Service interface for authentication."""

    @abstractmethod
    async def authenticate(
        self, username: str, password: str
    ) -> Optional[AuthenticationToken]:
        """Authenticate a user and return a token."""
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[User]:
        """Validate a token and return the associated user."""
        pass

    @abstractmethod
    async def refresh_token(self, token: str) -> Optional[AuthenticationToken]:
        """Refresh an authentication token."""
        pass

    @abstractmethod
    async def logout(self, token: str) -> None:
        """Invalidate a token (logout)."""
        pass


class IAuthorizationService(ABC):
    """Service interface for authorization."""

    @abstractmethod
    async def authorize(
        self, user: User, permission: Permission, resource: Optional[str] = None
    ) -> bool:
        """Check if a user is authorized for a specific action."""
        pass

    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        pass


class ISecurityEventService(ABC):
    """Service interface for security event logging."""

    @abstractmethod
    async def log_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        pass

    @abstractmethod
    async def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        pass


class IPasswordService(ABC):
    """Service interface for password operations."""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        pass

    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pass

    @abstractmethod
    async def generate_password(self, length: int = 12) -> str:
        """Generate a secure password."""
        pass


class ITokenService(ABC):
    """Service interface for token operations."""

    @abstractmethod
    async def generate_token(
        self, user: User, expires_in_seconds: int = 3600
    ) -> AuthenticationToken:
        """Generate an authentication token."""
        pass

    @abstractmethod
    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a token."""
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> None:
        """Revoke a token."""
        pass
