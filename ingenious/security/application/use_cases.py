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
)


class UserManagementUseCase:
    """Use case for user management operations."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        security_event_service: ISecurityEventService,
    ):
        self._user_repo = user_repository
        self._password_service = password_service
        self._security_events = security_event_service

    async def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        permissions: Optional[List[Permission]] = None,
    ) -> User:
        """Create a new user."""
        # Validate input
        if not username or not username.strip():
            raise ValueError("Username is required")

        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Check if username already exists
        existing_user = await self._user_repo.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")

        # Hash password
        password_hash = await self._password_service.hash_password(password)

        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            permissions=permissions or [],
            metadata={"password_hash": password_hash},
        )

        # Save user
        await self._user_repo.save_user(user)

        # Log security event
        await self._security_events.log_event(
            SecurityEvent(
                event_type="user_created",
                user_id=user.user_id,
                details={"username": username, "role": role.value},
            )
        )

        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return await self._user_repo.get_user(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self._user_repo.get_user_by_username(username)

    async def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[UserRole] = None,
    ) -> Optional[User]:
        """Update user information."""
        user = await self._user_repo.get_user(user_id)
        if not user:
            return None

        # Update fields
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role

        # Save updated user
        await self._user_repo.save_user(user)

        # Log security event
        await self._security_events.log_event(
            SecurityEvent(
                event_type="user_updated",
                user_id=user.user_id,
                details={"updated_fields": ["email", "full_name", "role"]},
            )
        )

        return user

    async def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password."""
        user = await self._user_repo.get_user(user_id)
        if not user:
            return False

        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Hash new password
        password_hash = await self._password_service.hash_password(new_password)
        user.metadata["password_hash"] = password_hash

        # Save user
        await self._user_repo.save_user(user)

        # Log security event
        await self._security_events.log_event(
            SecurityEvent(
                event_type="password_changed", user_id=user.user_id, details={}
            )
        )

        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        user = await self._user_repo.get_user(user_id)
        if not user:
            return False

        user.deactivate()
        await self._user_repo.save_user(user)

        # Log security event
        await self._security_events.log_event(
            SecurityEvent(
                event_type="user_deactivated", user_id=user.user_id, details={}
            )
        )

        return True

    async def activate_user(self, user_id: str) -> bool:
        """Activate a user."""
        user = await self._user_repo.get_user(user_id)
        if not user:
            return False

        user.activate()
        await self._user_repo.save_user(user)

        # Log security event
        await self._security_events.log_event(
            SecurityEvent(event_type="user_activated", user_id=user.user_id, details={})
        )

        return True

    async def list_users(self) -> List[User]:
        """List all users."""
        return await self._user_repo.list_users()

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = await self._user_repo.get_user(user_id)
        if not user:
            return False

        success = await self._user_repo.delete_user(user_id)

        if success:
            # Log security event
            await self._security_events.log_event(
                SecurityEvent(
                    event_type="user_deleted",
                    user_id=user_id,
                    details={"username": user.username},
                )
            )

        return success


class AuthenticationUseCase:
    """Use case for authentication operations."""

    def __init__(
        self,
        auth_service: IAuthenticationService,
        security_event_service: ISecurityEventService,
    ):
        self._auth_service = auth_service
        self._security_events = security_event_service

    async def login(
        self, username: str, password: str
    ) -> Optional[AuthenticationToken]:
        """Authenticate a user."""
        return await self._auth_service.authenticate(username, password)

    async def logout(self, token: str) -> None:
        """Logout a user."""
        await self._auth_service.logout(token)

    async def validate_token(self, token: str) -> Optional[User]:
        """Validate an authentication token."""
        return await self._auth_service.validate_token(token)

    async def refresh_token(self, token: str) -> Optional[AuthenticationToken]:
        """Refresh an authentication token."""
        return await self._auth_service.refresh_token(token)


class AuthorizationUseCase:
    """Use case for authorization operations."""

    def __init__(
        self,
        auth_service: IAuthorizationService,
        security_event_service: ISecurityEventService,
    ):
        self._auth_service = auth_service
        self._security_events = security_event_service

    async def check_permission(
        self, user: User, permission: Permission, resource: Optional[str] = None
    ) -> bool:
        """Check if a user has a specific permission."""
        authorized = await self._auth_service.authorize(user, permission, resource)

        # Log authorization check
        await self._security_events.log_event(
            SecurityEvent(
                event_type="authorization_check",
                user_id=user.user_id,
                details={
                    "permission": permission.value,
                    "resource": resource,
                    "authorized": authorized,
                },
            )
        )

        return authorized

    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        return await self._auth_service.get_user_permissions(user_id)


class SecurityAuditUseCase:
    """Use case for security audit operations."""

    def __init__(self, security_event_service: ISecurityEventService):
        self._security_events = security_event_service

    async def get_security_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        return await self._security_events.get_events(user_id, event_type, limit)

    async def get_user_activity(
        self, user_id: str, limit: int = 50
    ) -> List[SecurityEvent]:
        """Get security events for a specific user."""
        return await self._security_events.get_events(user_id=user_id, limit=limit)

    async def get_failed_login_attempts(self, limit: int = 100) -> List[SecurityEvent]:
        """Get failed login attempts."""
        return await self._security_events.get_events(
            event_type="authentication_failed", limit=limit
        )
