from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .entities import DiagnosticCheck, DiagnosticResult, SystemHealth


class IDiagnosticService(ABC):
    """Service interface for running diagnostic checks."""

    @abstractmethod
    async def run_check(self, check: DiagnosticCheck) -> DiagnosticResult:
        """Run a single diagnostic check."""
        pass

    @abstractmethod
    async def run_all_checks(self) -> SystemHealth:
        """Run all registered diagnostic checks."""
        pass

    @abstractmethod
    def register_check(self, check: DiagnosticCheck) -> None:
        """Register a new diagnostic check."""
        pass

    @abstractmethod
    def get_registered_checks(self) -> List[DiagnosticCheck]:
        """Get all registered checks."""
        pass


class IHealthCheckRepository(ABC):
    """Repository interface for health check persistence."""

    @abstractmethod
    async def save_health_report(self, health: SystemHealth) -> None:
        """Save a health report."""
        pass

    @abstractmethod
    async def get_latest_health_report(self) -> SystemHealth:
        """Get the latest health report."""
        pass

    @abstractmethod
    async def get_health_history(self, limit: int = 10) -> List[SystemHealth]:
        """Get health report history."""
        pass


class ISystemMetricsService(ABC):
    """Service interface for system metrics collection."""

    @abstractmethod
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        pass

    @abstractmethod
    async def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        pass


class IAlertingService(ABC):
    """Service interface for alerting on health issues."""

    @abstractmethod
    async def send_health_alert(self, health: SystemHealth) -> None:
        """Send health alert if needed."""
        pass

    @abstractmethod
    async def configure_alert_rules(self, rules: Dict[str, Any]) -> None:
        """Configure alerting rules."""
        pass
