"""
Security bounded context for the Ingenious application.

This module contains all security-related functionality organized according to
Domain-Driven Design principles:

- domain: Core security entities and business logic
- application: Security use cases and application services
- infrastructure: Security adapters (authentication, authorization)
- interfaces: Security API controllers
"""

from .application.services import SecurityApplicationService
from .application.use_cases import AuthenticationUseCase, AuthorizationUseCase
from .domain.entities import AuthenticationToken, User
from .domain.services import IAuthenticationService, IAuthorizationService
from .infrastructure.services import (
    BCryptPasswordService,
    DefaultAuthenticationService,
    DefaultAuthorizationService,
    HTTPBasicCredentialsAdapter,
    InMemorySecurityEventService,
    InMemoryUserRepository,
    JWTTokenService,
)
from .interfaces.rest_controllers import SecurityController

__all__ = [
    # Domain
    "User",
    "AuthenticationToken",
    "IAuthenticationService",
    "IAuthorizationService",
    # Application
    "AuthenticationUseCase",
    "AuthorizationUseCase",
    "SecurityApplicationService",
    # Infrastructure
    "BCryptPasswordService",
    "DefaultAuthenticationService",
    "DefaultAuthorizationService",
    "HTTPBasicCredentialsAdapter",
    "InMemorySecurityEventService",
    "InMemoryUserRepository",
    "JWTTokenService",
    # Interfaces
    "SecurityController",
]
