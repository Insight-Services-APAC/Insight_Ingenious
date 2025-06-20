from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class HealthStatus(Enum):
    """Enumeration for health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DiagnosticCheck:
    """Domain entity representing a diagnostic check."""

    def __init__(
        self,
        name: str,
        description: str,
        check_id: Optional[str] = None,
        category: str = "general",
        timeout_seconds: int = 30,
    ):
        self.check_id = check_id or str(uuid4())
        self.name = name
        self.description = description
        self.category = category
        self.timeout_seconds = timeout_seconds

    def __eq__(self, other):
        if not isinstance(other, DiagnosticCheck):
            return False
        return self.check_id == other.check_id


class DiagnosticResult:
    """Value object representing the result of a diagnostic check."""

    def __init__(
        self,
        check: DiagnosticCheck,
        status: HealthStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
        checked_at: Optional[datetime] = None,
        error: Optional[str] = None,
    ):
        self.check = check
        self.status = status
        self.message = message
        self.details = details or {}
        self.execution_time_ms = execution_time_ms
        self.checked_at = checked_at or datetime.utcnow()
        self.error = error

    @property
    def is_healthy(self) -> bool:
        """Check if the result indicates healthy status."""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "check_id": self.check.check_id,
            "check_name": self.check.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "execution_time": self.execution_time_ms,  # Keep legacy field name for tests
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.checked_at.isoformat()
            if self.checked_at
            else None,  # Legacy field
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
            "error": self.error,
        }


class SystemHealth:
    """Aggregate representing overall system health."""

    def __init__(self, service_name: str = "ingenious"):
        self.service_name = service_name
        self.results: List[DiagnosticResult] = []
        self.overall_status = HealthStatus.UNKNOWN
        self.last_updated = datetime.utcnow()

    def add_result(self, result: DiagnosticResult) -> None:
        """Add a diagnostic result."""
        self.results.append(result)
        self._calculate_overall_status()
        self.last_updated = datetime.utcnow()

    def _calculate_overall_status(self) -> None:
        """Calculate overall system status based on individual results."""
        if not self.results:
            self.overall_status = HealthStatus.UNKNOWN
            return

        statuses = [result.status for result in self.results]

        if all(status == HealthStatus.HEALTHY for status in statuses):
            self.overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            self.overall_status = HealthStatus.UNHEALTHY
        else:
            self.overall_status = HealthStatus.DEGRADED

    def get_results_by_category(self, category: str) -> List[DiagnosticResult]:
        """Get results filtered by category."""
        return [result for result in self.results if result.check.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert system health to dictionary."""
        return {
            "service_name": self.service_name,
            "overall_status": self.overall_status.value,
            "last_updated": self.last_updated.isoformat(),
            "results": [result.to_dict() for result in self.results],
            "checks": [
                result.to_dict() for result in self.results
            ],  # Keep both for compatibility
            "summary": {
                "total_checks": len(self.results),
                "healthy_checks": len([r for r in self.results if r.is_healthy]),
                "unhealthy_checks": len([r for r in self.results if not r.is_healthy]),
            },
        }
