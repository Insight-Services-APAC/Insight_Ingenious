import hashlib
import secrets
import string
import jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from ..domain.entities import (
    User,
    AuthenticationToken,
    SecurityEvent,
    Permission,
    UserRole,
)
from ..domain.services import (
    IUserRepository,
    IAuthenticationService,
    IAuthorizationService,
    ISecurityEventService,
    IPasswordService,
    ITokenService,
)


class InMemoryUserRepository(IUserRepository):
    """In-memory implementation of user repository."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._usernames: Dict[str, str] = {}  # username -> user_id mapping

    async def save_user(self, user: User) -> None:
        """Save a user."""
        self._users[user.user_id] = user
        self._usernames[user.username] = user.user_id

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self._users.get(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        user_id = self._usernames.get(username)
        return self._users.get(user_id) if user_id else None

    async def list_users(self) -> List[User]:
        """List all users."""
        return list(self._users.values())

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            del self._usernames[user.username]
            return True
        return False


class BCryptPasswordService(IPasswordService):
    """BCrypt-based password service."""

    async def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        # Note: In production, use actual bcrypt library
        # For now, using simple hash (NOT secure for production)
        salt = secrets.token_hex(16)
        return (
            hashlib.pbkdf2_hmac(
                "sha256", password.encode(), salt.encode(), 100000
            ).hex()
            + ":"
            + salt
        )

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            hash_part, salt = hashed_password.split(":")
            return (
                hashlib.pbkdf2_hmac(
                    "sha256", password.encode(), salt.encode(), 100000
                ).hex()
                == hash_part
            )
        except ValueError:
            return False

    async def generate_password(self, length: int = 12) -> str:
        """Generate a secure password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))


class JWTTokenService(ITokenService):
    """JWT-based token service."""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self._revoked_tokens: set = set()

    async def generate_token(
        self, user: User, expires_in_seconds: int = 3600
    ) -> AuthenticationToken:
        """Generate a JWT token."""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow() + timedelta(seconds=expires_in_seconds),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return AuthenticationToken(
            token=token,
            user_id=user.user_id,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in_seconds),
            scopes=[p.value for p in user.permissions],
        )

    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        if token in self._revoked_tokens:
            return None

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def revoke_token(self, token: str) -> None:
        """Revoke a token."""
        self._revoked_tokens.add(token)


class DefaultAuthenticationService(IAuthenticationService):
    """Default authentication service implementation."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
        security_event_service: ISecurityEventService,
    ):
        self._user_repo = user_repository
        self._password_service = password_service
        self._token_service = token_service
        self._security_events = security_event_service

    async def authenticate(
        self, username: str, password: str
    ) -> Optional[AuthenticationToken]:
        """Authenticate a user and return a token."""
        user = await self._user_repo.get_user_by_username(username)

        if not user or not user.is_active:
            await self._security_events.log_event(
                SecurityEvent(
                    event_type="authentication_failed",
                    user_id=user.user_id if user else None,
                    details={
                        "username": username,
                        "reason": "user_not_found_or_inactive",
                    },
                )
            )
            return None

        # For demo purposes, assume password is stored as user metadata
        stored_password_hash = user.metadata.get("password_hash")
        if not stored_password_hash:
            return None

        if not await self._password_service.verify_password(
            password, stored_password_hash
        ):
            await self._security_events.log_event(
                SecurityEvent(
                    event_type="authentication_failed",
                    user_id=user.user_id,
                    details={"username": username, "reason": "invalid_password"},
                )
            )
            return None

        # Authentication successful
        user.record_login()
        await self._user_repo.save_user(user)

        token = await self._token_service.generate_token(user)

        await self._security_events.log_event(
            SecurityEvent(
                event_type="authentication_successful",
                user_id=user.user_id,
                details={"username": username},
            )
        )

        return token

    async def validate_token(self, token: str) -> Optional[User]:
        """Validate a token and return the associated user."""
        payload = await self._token_service.decode_token(token)

        if not payload:
            return None

        user = await self._user_repo.get_user(payload.get("user_id"))
        return user if user and user.is_active else None

    async def refresh_token(self, token: str) -> Optional[AuthenticationToken]:
        """Refresh an authentication token."""
        user = await self.validate_token(token)

        if not user:
            return None

        # Revoke old token
        await self._token_service.revoke_token(token)

        # Generate new token
        return await self._token_service.generate_token(user)

    async def logout(self, token: str) -> None:
        """Invalidate a token (logout)."""
        await self._token_service.revoke_token(token)

        # Log logout event
        payload = await self._token_service.decode_token(token)
        if payload:
            await self._security_events.log_event(
                SecurityEvent(
                    event_type="logout", user_id=payload.get("user_id"), details={}
                )
            )


class DefaultAuthorizationService(IAuthorizationService):
    """Default authorization service implementation."""

    async def authorize(
        self, user: User, permission: Permission, resource: Optional[str] = None
    ) -> bool:
        """Check if a user is authorized for a specific action."""
        if not user.is_active:
            return False

        # Admin role has all permissions
        if user.role == UserRole.ADMIN:
            return True

        # Check if user has specific permission
        return user.has_permission(permission)

    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        # This would typically query the user repository
        # For simplicity, return empty list
        return []


class InMemorySecurityEventService(ISecurityEventService):
    """In-memory security event service."""

    def __init__(self):
        self._events: List[SecurityEvent] = []

    async def log_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        self._events.append(event)
        # Keep only last 1000 events
        if len(self._events) > 1000:
            self._events = self._events[-1000:]

    async def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        filtered_events = self._events

        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        return filtered_events[-limit:] if filtered_events else []


class HTTPBasicCredentialsAdapter:
    """Adapter for HTTP Basic authentication."""

    def __init__(self, auth_service: IAuthenticationService):
        self._auth_service = auth_service

    async def authenticate_credentials(
        self, username: str, password: str
    ) -> Optional[User]:
        """Authenticate HTTP basic credentials."""
        token = await self._auth_service.authenticate(username, password)
        if token:
            return await self._auth_service.validate_token(token.token)
        return None
