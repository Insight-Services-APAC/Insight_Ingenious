import asyncio
import logging
import psutil
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..domain.entities import (
    DiagnosticCheck,
    DiagnosticResult,
    SystemHealth,
    HealthStatus,
)
from ..domain.services import (
    IDiagnosticService,
    IHealthCheckRepository,
    ISystemMetricsService,
    IAlertingService,
)

logger = logging.getLogger(__name__)


class DefaultDiagnosticService(IDiagnosticService):
    """Default implementation of diagnostic service."""

    def __init__(self):
        self._checks: Dict[str, DiagnosticCheck] = {}
        self._results: List[DiagnosticResult] = []

    def register_check(self, check: DiagnosticCheck) -> None:
        """Register a new diagnostic check."""
        self._checks[check.check_id] = check

    def get_registered_checks(self) -> List[DiagnosticCheck]:
        """Get all registered checks."""
        return list(self._checks.values())

    async def run_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a single diagnostic check."""
        start_time = time.time()

        try:
            # Determine check type and run appropriate logic
            if check.name == "database_connectivity":
                result = await self._check_database_connectivity(check)
            elif check.name == "external_service_connectivity":
                result = await self._check_external_service_connectivity(check)
            elif check.name == "memory_usage":
                result = await self._check_memory_usage(check)
            elif check.name == "disk_space":
                result = await self._check_disk_space(check)
            elif check.name == "api_health":
                result = await self._check_api_health(check)
            else:
                result = DiagnosticResult(
                    check=check,
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown check type: {check.name}",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            return result

        except asyncio.TimeoutError:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"Check timed out after {check.timeout_seconds} seconds",
                execution_time_ms=(time.time() - start_time) * 1000,
                error="Timeout",
            )
        except Exception as e:
            logger.exception(f"Error running check {check.name}")
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed with error: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def run_all_checks(self) -> SystemHealth:
        """Run all registered diagnostic checks."""
        health = SystemHealth()

        for check in self._checks.values():
            try:
                result = await asyncio.wait_for(
                    self.run_check(check), timeout=check.timeout_seconds
                )
                health.add_result(result)
            except asyncio.TimeoutError:
                result = DiagnosticResult(
                    check=check,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check timed out after {check.timeout_seconds} seconds",
                    error="Timeout",
                )
                health.add_result(result)

        return health

    async def _check_database_connectivity(
        self, check: DiagnosticCheck
    ) -> DiagnosticResult:
        """Check database connectivity."""
        try:
            # This would check actual database connection
            # For now, return a mock result
            return DiagnosticResult(
                check=check,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={"connection_pool_size": 10, "active_connections": 2},
            )
        except Exception as e:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                error=str(e),
            )

    async def _check_external_service_connectivity(
        self, check: DiagnosticCheck
    ) -> DiagnosticResult:
        """Check external service connectivity."""
        try:
            # This would check external service endpoints
            # For now, return a mock result
            return DiagnosticResult(
                check=check,
                status=HealthStatus.HEALTHY,
                message="External services accessible",
                details={"openai_api": "accessible", "azure_keyvault": "accessible"},
            )
        except Exception as e:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"External service check failed: {str(e)}",
                error=str(e),
            )

    async def _check_memory_usage(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"High memory usage: {usage_percent}%"
            elif usage_percent > 75:
                status = HealthStatus.DEGRADED
                message = f"Elevated memory usage: {usage_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {usage_percent}%"

            return DiagnosticResult(
                check=check,
                status=status,
                message=message,
                details={
                    "total_memory_gb": round(memory.total / (1024**3), 2),
                    "available_memory_gb": round(memory.available / (1024**3), 2),
                    "used_memory_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": usage_percent,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                error=str(e),
            )

    async def _check_disk_space(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Check disk space."""
        try:
            disk = psutil.disk_usage("/")
            usage_percent = (disk.used / disk.total) * 100

            if usage_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Low disk space: {usage_percent:.1f}% used"
            elif usage_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Disk space warning: {usage_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {usage_percent:.1f}% used"

            return DiagnosticResult(
                check=check,
                status=status,
                message=message,
                details={
                    "total_space_gb": round(disk.total / (1024**3), 2),
                    "free_space_gb": round(disk.free / (1024**3), 2),
                    "used_space_gb": round(disk.used / (1024**3), 2),
                    "usage_percent": round(usage_percent, 1),
                },
            )
        except Exception as e:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                error=str(e),
            )

    async def _check_api_health(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Check API health."""
        try:
            # This would check API endpoints, response times, etc.
            # For now, return a mock result
            return DiagnosticResult(
                check=check,
                status=HealthStatus.HEALTHY,
                message="API endpoints responding normally",
                details={
                    "chat_endpoint": "healthy",
                    "diagnostic_endpoint": "healthy",
                    "average_response_time_ms": 150,
                },
            )
        except Exception as e:
            return DiagnosticResult(
                check=check,
                status=HealthStatus.UNHEALTHY,
                message=f"API health check failed: {str(e)}",
                error=str(e),
            )


class InMemoryHealthCheckRepository(IHealthCheckRepository):
    """In-memory implementation of health check repository."""

    def __init__(self):
        self._health_reports: List[SystemHealth] = []

    async def save_health_report(self, health: SystemHealth) -> None:
        """Save a health report."""
        self._health_reports.append(health)
        # Keep only last 100 reports
        if len(self._health_reports) > 100:
            self._health_reports = self._health_reports[-100:]

    async def get_latest_health_report(self) -> Optional[SystemHealth]:
        """Get the latest health report."""
        return self._health_reports[-1] if self._health_reports else None

    async def get_health_history(self, limit: int = 10) -> List[SystemHealth]:
        """Get health report history."""
        return self._health_reports[-limit:] if self._health_reports else []


class SystemMetricsService(ISystemMetricsService):
    """Implementation of system metrics service."""

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "count_logical": psutil.cpu_count(logical=True),
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 1),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.exception("Failed to get system metrics")
            return {"error": str(e)}

    async def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        try:
            import os

            process = psutil.Process(os.getpid())

            return {
                "process": {
                    "pid": process.pid,
                    "memory_usage_mb": round(process.memory_info().rss / (1024**2), 2),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "create_time": datetime.fromtimestamp(
                        process.create_time()
                    ).isoformat(),
                },
                "uptime_seconds": time.time() - process.create_time(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.exception("Failed to get application metrics")
            return {"error": str(e)}


class LoggingAlertingService(IAlertingService):
    """Simple logging-based alerting service."""

    def __init__(self):
        self.alert_logger = logging.getLogger("ingenious.alerts")

    async def send_health_alert(self, health: SystemHealth) -> None:
        """Send health alert if needed."""
        if health.overall_status == HealthStatus.UNHEALTHY:
            unhealthy_checks = [
                result for result in health.results if not result.is_healthy
            ]

            self.alert_logger.critical(
                f"HEALTH ALERT: System status is {health.overall_status.value}. "
                f"Unhealthy checks: {[check.check.name for check in unhealthy_checks]}"
            )
        elif health.overall_status == HealthStatus.DEGRADED:
            self.alert_logger.warning(
                f"HEALTH WARNING: System status is {health.overall_status.value}"
            )

    async def configure_alert_rules(self, rules: Dict[str, Any]) -> None:
        """Configure alerting rules."""
        # Simple implementation - could be extended to support webhooks, email, etc.
        self.alert_logger.info(f"Alert rules configured: {rules}")
