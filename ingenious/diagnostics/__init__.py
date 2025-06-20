"""
Diagnostics bounded context for the Ingenious application.

This module contains all diagnostics and health monitoring functionality
organized according to Domain-Driven Design principles:

- domain: Core business logic and entities for health checks and system monitoring
- application: Use cases and application services for diagnostics operations
- infrastructure: External adapters for metrics collection and alerting
"""

from .domain.entities import (
    DiagnosticCheck,
    DiagnosticResult,
    SystemHealth,
    HealthStatus,
)
from .domain.services import (
    IDiagnosticService,
    IHealthCheckRepository,
    ISystemMetricsService,
    IAlertingService,
)
from .application.use_cases import HealthMonitoringUseCase, SystemMetricsUseCase
from .application.services import DiagnosticsApplicationService
from .infrastructure.services import (
    DefaultDiagnosticService,
    InMemoryHealthCheckRepository,
    SystemMetricsService,
    LoggingAlertingService,
)
from .interfaces.rest_controllers import DiagnosticsController

__all__ = [
    # Domain
    "DiagnosticCheck",
    "DiagnosticResult",
    "SystemHealth",
    "HealthStatus",
    "IDiagnosticService",
    "IHealthCheckRepository",
    "ISystemMetricsService",
    "IAlertingService",
    # Application
    "HealthMonitoringUseCase",
    "SystemMetricsUseCase",
    "DiagnosticsApplicationService",
    # Infrastructure
    "DefaultDiagnosticService",
    "InMemoryHealthCheckRepository",
    "SystemMetricsService",
    "LoggingAlertingService",
    # Interfaces
    "DiagnosticsController",
]
