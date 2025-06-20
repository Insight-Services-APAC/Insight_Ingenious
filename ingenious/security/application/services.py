from typing import Any, Dict, List, Optional

from ..application.use_cases import (
    AuthenticationUseCase,
    AuthorizationUseCase,
    SecurityAuditUseCase,
    UserManagementUseCase,
)
from ..domain.entities import Permission, UserRole


class SecurityApplicationService:
    """Application service for security operations."""

    def __init__(
        self,
        user_management_use_case: UserManagementUseCase,
        authentication_use_case: AuthenticationUseCase,
        authorization_use_case: AuthorizationUseCase,
        security_audit_use_case: SecurityAuditUseCase,
    ):
        self._user_management = user_management_use_case
        self._authentication = authentication_use_case
        self._authorization = authorization_use_case
        self._security_audit = security_audit_use_case

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return token information."""
        try:
            token = await self._authentication.login(username, password)

            if not token:
                return {
                    "success": False,
                    "message": "Invalid credentials",
                    "error": "AUTHENTICATION_FAILED",
                }

            return {
                "success": True,
                "token": token.token,
                "token_type": token.token_type,
                "expires_at": token.expires_at.isoformat(),
                "user_id": token.user_id,
                "scopes": token.scopes,
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "error": "AUTHENTICATION_ERROR",
            }

    async def validate_user_session(self, token: str) -> Dict[str, Any]:
        """Validate a user session token."""
        try:
            user = await self._authentication.validate_token(token)

            if not user:
                return {
                    "success": False,
                    "message": "Invalid or expired token",
                    "error": "INVALID_TOKEN",
                }

            return {
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions],
                    "is_active": user.is_active,
                    "last_login": user.last_login.isoformat()
                    if user.last_login
                    else None,
                },
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "VALIDATION_ERROR"}

    async def logout_user(self, token: str) -> Dict[str, Any]:
        """Logout a user."""
        try:
            await self._authentication.logout(token)
            return {"success": True, "message": "Logout successful"}
        except Exception as e:
            return {"success": False, "message": str(e), "error": "LOGOUT_ERROR"}

    async def refresh_user_token(self, token: str) -> Dict[str, Any]:
        """Refresh a user's authentication token."""
        try:
            new_token = await self._authentication.refresh_token(token)

            if not new_token:
                return {
                    "success": False,
                    "message": "Cannot refresh token",
                    "error": "REFRESH_FAILED",
                }

            return {
                "success": True,
                "token": new_token.token,
                "token_type": new_token.token_type,
                "expires_at": new_token.expires_at.isoformat(),
                "user_id": new_token.user_id,
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "REFRESH_ERROR"}

    async def create_user_account(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: str = "user",
        permissions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new user account."""
        try:
            # Convert string role to enum
            user_role = UserRole(role) if role else UserRole.USER

            # Convert string permissions to enums
            user_permissions = []
            if permissions:
                for perm in permissions:
                    try:
                        user_permissions.append(Permission(perm))
                    except ValueError:
                        return {
                            "success": False,
                            "message": f"Invalid permission: {perm}",
                            "error": "INVALID_PERMISSION",
                        }

            user = await self._user_management.create_user(
                username=username,
                password=password,
                email=email,
                full_name=full_name,
                role=user_role,
                permissions=user_permissions,
            )

            return {
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions],
                    "created_at": user.created_at.isoformat(),
                },
            }

        except ValueError as e:
            return {"success": False, "message": str(e), "error": "VALIDATION_ERROR"}
        except Exception as e:
            return {"success": False, "message": str(e), "error": "USER_CREATION_ERROR"}

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information."""
        try:
            user = await self._user_management.get_user(user_id)

            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "error": "USER_NOT_FOUND",
                }

            return {
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions],
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat()
                    if user.last_login
                    else None,
                },
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "USER_FETCH_ERROR"}

    async def check_user_permission(
        self, user_id: str, permission: str, resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if a user has a specific permission."""
        try:
            user = await self._user_management.get_user(user_id)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "error": "USER_NOT_FOUND",
                }

            try:
                perm = Permission(permission)
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid permission: {permission}",
                    "error": "INVALID_PERMISSION",
                }

            authorized = await self._authorization.check_permission(
                user, perm, resource
            )

            return {
                "success": True,
                "authorized": authorized,
                "user_id": user_id,
                "permission": permission,
                "resource": resource,
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "AUTHORIZATION_ERROR"}

    async def get_security_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get security audit log."""
        try:
            events = await self._security_audit.get_security_events(
                user_id=user_id, event_type=event_type, limit=limit
            )

            return {
                "success": True,
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "user_id": event.user_id,
                        "timestamp": event.timestamp.isoformat(),
                        "ip_address": event.ip_address,
                        "user_agent": event.user_agent,
                        "details": event.details,
                    }
                    for event in events
                ],
                "count": len(events),
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "AUDIT_LOG_ERROR"}

    async def deactivate_user_account(self, user_id: str) -> Dict[str, Any]:
        """Deactivate a user account."""
        try:
            success = await self._user_management.deactivate_user(user_id)

            if not success:
                return {
                    "success": False,
                    "message": "User not found",
                    "error": "USER_NOT_FOUND",
                }

            return {
                "success": True,
                "message": "User account deactivated successfully",
                "user_id": user_id,
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "DEACTIVATION_ERROR"}

    async def list_users(self) -> Dict[str, Any]:
        """List all users."""
        try:
            users = await self._user_management.list_users()

            return {
                "success": True,
                "users": [
                    {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role.value,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat()
                        if user.last_login
                        else None,
                    }
                    for user in users
                ],
                "count": len(users),
            }

        except Exception as e:
            return {"success": False, "message": str(e), "error": "USER_LIST_ERROR"}
