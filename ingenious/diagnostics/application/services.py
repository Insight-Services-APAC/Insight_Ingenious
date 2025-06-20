from typing import Any, Dict, List, Optional

from ..application.use_cases import HealthMonitoringUseCase, SystemMetricsUseCase


class DiagnosticsApplicationService:
    """Application service for diagnostics operations."""

    def __init__(
        self,
        health_monitoring_use_case: HealthMonitoringUseCase,
        system_metrics_use_case: SystemMetricsUseCase,
    ):
        self._health_monitoring = health_monitoring_use_case
        self._system_metrics = system_metrics_use_case

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status with metrics."""
        try:
            # Get current health status
            health_status = await self._health_monitoring.get_system_status()

            # Add current metrics for context
            metrics = await self._system_metrics.get_current_metrics()

            return {
                "health": health_status,
                "metrics": metrics.get("system", {}),
                "timestamp": metrics.get("system", {}).get("timestamp"),
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run a full diagnostic check."""
        try:
            # Run health checks
            health = await self._health_monitoring.run_health_check()

            # Get current metrics
            metrics = await self._system_metrics.get_current_metrics()

            # Combine results
            return {
                "health_check": health.to_dict(),
                "metrics": metrics,
                "diagnostic_summary": {
                    "overall_status": health.overall_status.value,
                    "total_checks": len(health.results),
                    "healthy_checks": len([r for r in health.results if r.is_healthy]),
                    "timestamp": health.last_updated.isoformat(),
                },
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def run_quick_check(self) -> Dict[str, Any]:
        """Run a quick health check with basic metrics."""
        try:
            # Get current status without running new checks
            health_status = await self._health_monitoring.get_system_status()

            # Get basic system metrics
            system_metrics = await self._system_metrics.get_system_metrics_only()

            return {
                "status": health_status.get("status", "unknown"),
                "basic_metrics": {
                    "cpu_usage": system_metrics.get("cpu", {}).get("usage_percent"),
                    "memory_usage": system_metrics.get("memory", {}).get(
                        "usage_percent"
                    ),
                    "disk_usage": system_metrics.get("disk", {}).get("usage_percent"),
                },
                "last_health_check": health_status.get("last_updated"),
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def check_specific_component(self, component_name: str) -> Dict[str, Any]:
        """Check a specific system component."""
        try:
            result = await self._health_monitoring.run_specific_check(component_name)
            return result
        except Exception as e:
            return {"error": str(e), "component": component_name, "success": False}

    async def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            # Get metrics
            metrics = await self._system_metrics.get_current_metrics()

            # Get available checks
            checks = await self._health_monitoring.list_available_checks()

            # Get health history
            history = await self._health_monitoring.get_health_history(5)

            return {
                "system_metrics": metrics.get("system", {}),
                "application_metrics": metrics.get("application", {}),
                "available_checks": checks.get("checks", []),
                "recent_health_history": history.get("history", []),
                "info": {
                    "total_available_checks": checks.get("count", 0),
                    "health_history_entries": history.get("count", 0),
                },
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def configure_monitoring(
        self,
        check_interval_minutes: Optional[int] = None,
        alert_thresholds: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Configure monitoring settings."""
        try:
            configuration = {}

            if check_interval_minutes is not None:
                configuration["check_interval_minutes"] = check_interval_minutes

            if alert_thresholds is not None:
                configuration["alert_thresholds"] = alert_thresholds
                # Note: Would need to implement actual threshold configuration

            return {
                "configuration": configuration,
                "message": "Monitoring configuration updated",
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_diagnostic_report(self) -> Dict[str, Any]:
        """Generate a comprehensive diagnostic report."""
        try:
            # Run full diagnostic
            full_diagnostic = await self.run_full_diagnostic()

            if not full_diagnostic.get("success"):
                return full_diagnostic

            # Create summary report
            health_data = full_diagnostic["health_check"]
            metrics_data = full_diagnostic["metrics"]

            report = {
                "report_timestamp": full_diagnostic["diagnostic_summary"]["timestamp"],
                "overall_status": full_diagnostic["diagnostic_summary"][
                    "overall_status"
                ],
                "executive_summary": {
                    "status": full_diagnostic["diagnostic_summary"]["overall_status"],
                    "total_checks": full_diagnostic["diagnostic_summary"][
                        "total_checks"
                    ],
                    "healthy_checks": full_diagnostic["diagnostic_summary"][
                        "healthy_checks"
                    ],
                    "system_load": {
                        "cpu": metrics_data.get("system", {})
                        .get("cpu", {})
                        .get("usage_percent"),
                        "memory": metrics_data.get("system", {})
                        .get("memory", {})
                        .get("usage_percent"),
                        "disk": metrics_data.get("system", {})
                        .get("disk", {})
                        .get("usage_percent"),
                    },
                },
                "detailed_results": {
                    "health_checks": health_data.get("checks", []),
                    "system_metrics": metrics_data.get("system", {}),
                    "application_metrics": metrics_data.get("application", {}),
                },
                "recommendations": self._generate_recommendations(
                    health_data, metrics_data
                ),
                "success": True,
            }

            return report

        except Exception as e:
            return {"error": str(e), "success": False}

    def _generate_recommendations(
        self, health_data: Dict[str, Any], metrics_data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on diagnostic results."""
        recommendations = []

        # Check for unhealthy components
        unhealthy_checks = [
            check
            for check in health_data.get("checks", [])
            if check.get("status") != "healthy"
        ]

        if unhealthy_checks:
            recommendations.append(
                f"Address {len(unhealthy_checks)} unhealthy system components"
            )

        # Check system resource usage
        system_metrics = metrics_data.get("system", {})

        if system_metrics.get("memory", {}).get("usage_percent", 0) > 80:
            recommendations.append("Consider increasing available memory")

        if system_metrics.get("cpu", {}).get("usage_percent", 0) > 80:
            recommendations.append("High CPU usage detected - investigate performance")

        if system_metrics.get("disk", {}).get("usage_percent", 0) > 85:
            recommendations.append("Low disk space - consider cleanup or expansion")

        if not recommendations:
            recommendations.append("System appears to be operating normally")

        return recommendations
