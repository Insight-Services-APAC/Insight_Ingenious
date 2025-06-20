from typing import Any, Dict

from ..domain.entities import DiagnosticCheck, SystemHealth
from ..domain.services import (
    IAlertingService,
    IDiagnosticService,
    IHealthCheckRepository,
    ISystemMetricsService,
)


class HealthMonitoringUseCase:
    """Use case for health monitoring operations."""

    def __init__(
        self,
        diagnostic_service: IDiagnosticService,
        health_repository: IHealthCheckRepository,
        metrics_service: ISystemMetricsService,
        alerting_service: IAlertingService,
    ):
        self._diagnostic_service = diagnostic_service
        self._health_repository = health_repository
        self._metrics_service = metrics_service
        self._alerting_service = alerting_service

    async def run_health_check(self) -> SystemHealth:
        """Run a complete health check."""
        # Run all diagnostic checks
        health = await self._diagnostic_service.run_all_checks()

        # Save health report
        await self._health_repository.save_health_report(health)

        # Send alerts if necessary
        await self._alerting_service.send_health_alert(health)

        return health

    async def run_specific_check(self, check_name: str) -> Dict[str, Any]:
        """Run a specific diagnostic check."""
        checks = self._diagnostic_service.get_registered_checks()
        target_check = next((c for c in checks if c.name == check_name), None)

        if not target_check:
            return {
                "error": f"Check '{check_name}' not found",
                "available_checks": [c.name for c in checks],
                "success": False,
            }

        result = await self._diagnostic_service.run_check(target_check)
        return result.to_dict()

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        latest_health = await self._health_repository.get_latest_health_report()

        if not latest_health:
            return {
                "status": "unknown",
                "message": "No health checks have been run",
                "success": True,
            }

        return {
            "status": latest_health.overall_status.value,
            "last_updated": latest_health.last_updated.isoformat(),
            "checks_summary": latest_health.to_dict()["summary"],
            "success": True,
        }

    async def get_health_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get health check history."""
        history = await self._health_repository.get_health_history(limit)

        return {
            "history": [
                {
                    "status": h.overall_status.value,
                    "timestamp": h.last_updated.isoformat(),
                    "summary": h.to_dict()["summary"],
                }
                for h in history
            ],
            "count": len(history),
            "success": True,
        }

    async def register_health_check(
        self,
        name: str,
        description: str,
        category: str = "general",
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """Register a new health check."""
        check = DiagnosticCheck(
            name=name,
            description=description,
            category=category,
            timeout_seconds=timeout_seconds,
        )

        self._diagnostic_service.register_check(check)

        return {
            "check_id": check.check_id,
            "name": check.name,
            "registered": True,
            "success": True,
        }

    async def list_available_checks(self) -> Dict[str, Any]:
        """List all available health checks."""
        checks = self._diagnostic_service.get_registered_checks()

        return {
            "checks": [
                {
                    "check_id": c.check_id,
                    "name": c.name,
                    "description": c.description,
                    "category": c.category,
                    "timeout_seconds": c.timeout_seconds,
                }
                for c in checks
            ],
            "count": len(checks),
            "success": True,
        }


class SystemMetricsUseCase:
    """Use case for system metrics operations."""

    def __init__(self, metrics_service: ISystemMetricsService):
        self._metrics_service = metrics_service

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            system_metrics = await self._metrics_service.get_system_metrics()
            app_metrics = await self._metrics_service.get_application_metrics()

            return {
                "system": system_metrics,
                "application": app_metrics,
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_system_metrics_only(self) -> Dict[str, Any]:
        """Get only system-level metrics."""
        try:
            metrics = await self._metrics_service.get_system_metrics()
            return {**metrics, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_application_metrics_only(self) -> Dict[str, Any]:
        """Get only application-level metrics."""
        try:
            metrics = await self._metrics_service.get_application_metrics()
            return {**metrics, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
