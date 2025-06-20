"""
Security REST controllers for the security bounded context.

This module contains FastAPI route handlers for security operations including
authentication, authorization, and user management.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ingenious.shared.domain.models import HTTPError

from ..application.services import SecurityApplicationService

logger = logging.getLogger(__name__)


# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user_id: Optional[str] = None
    message: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str = "user"


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool


class SecurityController:
    """REST controller for security operations."""

    def __init__(self, security_app_service: SecurityApplicationService):
        self._security_app_service = security_app_service
        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup the security routes."""
        self._router.post(
            "/auth/login",
            responses={
                200: {"model": LoginResponse, "description": "Login successful"},
                401: {"model": HTTPError, "description": "Authentication failed"},
            },
        )(self.login)

        self._router.post(
            "/auth/logout",
            responses={
                200: {"model": dict, "description": "Logout successful"},
            },
        )(self.logout)

        self._router.post(
            "/users",
            responses={
                201: {"model": UserResponse, "description": "User created"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.create_user)

        self._router.get(
            "/users",
            responses={
                200: {"model": List[UserResponse], "description": "Users list"},
            },
        )(self.list_users)

        self._router.get(
            "/users/{user_id}",
            responses={
                200: {"model": UserResponse, "description": "User details"},
                404: {"model": HTTPError, "description": "User not found"},
            },
        )(self.get_user)

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    async def login(self, login_request: LoginRequest) -> LoginResponse:
        """Authenticate a user and return a token."""
        try:
            result = await self._security_app_service.authenticate_user(
                login_request.username, login_request.password
            )

            if result["success"]:
                return LoginResponse(
                    success=True,
                    token=result["token"],
                    user_id=result.get("user_id"),
                    message="Login successful",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=result["message"]
                )
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed",
            )

    async def logout(self, token: str) -> dict:
        """Logout a user by invalidating their token."""
        try:
            result = await self._security_app_service.logout_user(token)
            return {"success": result["success"], "message": result["message"]}
        except Exception as e:
            logger.exception(e)
            return {"success": False, "message": "Logout failed"}

    async def create_user(self, user_request: CreateUserRequest) -> UserResponse:
        """Create a new user."""
        try:
            result = await self._security_app_service.create_user(
                username=user_request.username,
                password=user_request.password,
                email=user_request.email,
                role=user_request.role,
            )

            if result["success"]:
                user = result["user"]
                return UserResponse(
                    user_id=user["user_id"],
                    username=user["username"],
                    email=user["email"],
                    role=user["role"],
                    is_active=user["is_active"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

    async def list_users(self) -> List[UserResponse]:
        """List all users."""
        try:
            result = await self._security_app_service.list_users()

            if result["success"]:
                return [
                    UserResponse(
                        user_id=user["user_id"],
                        username=user["username"],
                        email=user["email"],
                        role=user["role"],
                        is_active=user["is_active"],
                    )
                    for user in result["users"]
                ]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"],
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list users",
            )

    async def get_user(self, user_id: str) -> UserResponse:
        """Get user details by ID."""
        try:
            result = await self._security_app_service.get_user(user_id)

            if result["success"]:
                user = result["user"]
                return UserResponse(
                    user_id=user["user_id"],
                    username=user["username"],
                    email=user["email"],
                    role=user["role"],
                    is_active=user["is_active"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=result["message"]
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user",
            )


# Create router instance for FastAPI integration
# Note: In production, this should be managed by a DI container
from ..application.use_cases import (
    AuthenticationUseCase,
    AuthorizationUseCase,
    SecurityAuditUseCase,
    UserManagementUseCase,
)
from ..infrastructure.services import (
    BCryptPasswordService,
    DefaultAuthenticationService,
    DefaultAuthorizationService,
    InMemorySecurityEventService,
    InMemoryUserRepository,
    JWTTokenService,
)

# Default service instances (TODO: Move to proper DI configuration)
user_repo = InMemoryUserRepository()
password_service = BCryptPasswordService()
token_service = JWTTokenService()
security_event_service = InMemorySecurityEventService()
auth_service = DefaultAuthenticationService(
    user_repo, password_service, token_service, security_event_service
)
authz_service = DefaultAuthorizationService()
# security_event_service already defined above

user_mgmt_use_case = UserManagementUseCase(
    user_repo, password_service, security_event_service
)
auth_use_case = AuthenticationUseCase(auth_service, security_event_service)
authz_use_case = AuthorizationUseCase(authz_service, security_event_service)
audit_use_case = SecurityAuditUseCase(security_event_service)

security_app_service = SecurityApplicationService(
    user_mgmt_use_case, auth_use_case, authz_use_case, audit_use_case
)

controller = SecurityController(security_app_service)
router = controller.router
