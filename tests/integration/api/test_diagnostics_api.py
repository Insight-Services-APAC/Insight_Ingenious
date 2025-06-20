"""
Integration tests for diagnostics API endpoints.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.diagnostics.domain.entities import (
    DiagnosticCheck,
    DiagnosticResult,
    HealthStatus,
    SystemHealth,
)


class TestDiagnosticsAPI:
    """Test cases for diagnostics API endpoints."""

    @pytest.fixture
    def mock_diagnostics_service(self):
        """Mock diagnostics service."""
        service = Mock()

        # Create sample diagnostic results
        check1 = DiagnosticCheck(
            name="Database Connection",
            description="Check database connectivity",
            category="database",
        )
        result1 = DiagnosticResult(
            check=check1,
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            execution_time_ms=25.5,
        )

        check2 = DiagnosticCheck(
            name="Memory Usage",
            description="Check system memory usage",
            category="system",
        )
        result2 = DiagnosticResult(
            check=check2,
            status=HealthStatus.HEALTHY,
            message="Memory usage within normal range",
            execution_time_ms=10.2,
        )

        system_health = SystemHealth(service_name="test_service")
        system_health.add_result(result1)
        system_health.add_result(result2)

        service.get_system_health = AsyncMock(return_value=system_health)
        service.run_diagnostic_check = AsyncMock(return_value=result1)
        service.get_performance_metrics = AsyncMock(
            return_value={
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1,
                "response_time": 125.6,
            }
        )
        return service

    @pytest.fixture
    def mock_app(self, mock_diagnostics_service):
        """Mock FastAPI app with diagnostics endpoints."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/api/v1/health")
        async def get_health():
            health = await mock_diagnostics_service.get_system_health()
            return {
                "service_name": health.service_name,
                "overall_status": health.overall_status.value,
                "last_updated": health.last_updated.isoformat(),
                "results": [result.to_dict() for result in health.results],
            }

        @app.post("/api/v1/diagnostics/check/{check_name}")
        async def run_diagnostic_check(check_name: str):
            result = await mock_diagnostics_service.run_diagnostic_check(check_name)
            return {"result": result.to_dict()}

        @app.get("/api/v1/metrics")
        async def get_metrics():
            metrics = await mock_diagnostics_service.get_performance_metrics()
            return {"metrics": metrics}

        return TestClient(app)

    async def test_get_health_success(self, mock_app, mock_diagnostics_service):
        """Test successful health status retrieval."""
        # Act
        response = mock_app.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "test_service"
        assert data["overall_status"] == "healthy"
        assert "last_updated" in data
        assert len(data["results"]) == 2
        mock_diagnostics_service.get_system_health.assert_called_once()

    async def test_run_diagnostic_check_success(
        self, mock_app, mock_diagnostics_service
    ):
        """Test successful diagnostic check execution."""
        # Arrange
        check_name = "database_connection"

        # Act
        response = mock_app.post(f"/api/v1/diagnostics/check/{check_name}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["result"]["status"] == "healthy"
        mock_diagnostics_service.run_diagnostic_check.assert_called_once_with(
            check_name
        )

    async def test_get_metrics_success(self, mock_app, mock_diagnostics_service):
        """Test successful performance metrics retrieval."""
        # Act
        response = mock_app.get("/api/v1/metrics")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        metrics = data["metrics"]
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "response_time" in metrics
        mock_diagnostics_service.get_performance_metrics.assert_called_once()


class TestDiagnosticsModels:
    """Test diagnostics model functionality in API context."""

    def test_diagnostic_check_creation(self):
        """Test diagnostic check model creation."""
        check = DiagnosticCheck(
            name="Test Check",
            description="Test description",
            category="test",
            timeout_seconds=60,
        )
        assert check.name == "Test Check"
        assert check.description == "Test description"
        assert check.category == "test"
        assert check.timeout_seconds == 60
        assert check.check_id is not None

    def test_diagnostic_result_creation(self):
        """Test diagnostic result model creation."""
        check = DiagnosticCheck(name="Test Check", description="Test description")
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="All good",
            execution_time_ms=15.5,
        )
        assert result.check == check
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        assert result.execution_time_ms == 15.5
        assert result.is_healthy() is True

    def test_system_health_aggregation(self):
        """Test system health aggregation functionality."""
        system_health = SystemHealth(service_name="test")

        # Add healthy result
        check1 = DiagnosticCheck(name="Check1", description="Test")
        result1 = DiagnosticResult(
            check=check1, status=HealthStatus.HEALTHY, message="OK"
        )
        system_health.add_result(result1)
        assert system_health.overall_status == HealthStatus.HEALTHY

        # Add unhealthy result - should change overall status
        check2 = DiagnosticCheck(name="Check2", description="Test")
        result2 = DiagnosticResult(
            check=check2, status=HealthStatus.UNHEALTHY, message="Not OK"
        )
        system_health.add_result(result2)
        assert system_health.overall_status == HealthStatus.UNHEALTHY

    def test_health_status_enum_values(self):
        """Test health status enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestDiagnosticsAPIIntegration:
    """Integration tests for diagnostics API workflows."""

    async def test_complete_health_check_workflow(
        self, mock_app, mock_diagnostics_service
    ):
        """Test complete health check workflow."""
        # 1. Get initial health status
        response = mock_app.get("/api/v1/health")
        assert response.status_code == 200
        initial_health = response.json()
        assert initial_health["overall_status"] == "healthy"

        # 2. Run specific diagnostic check
        response = mock_app.post("/api/v1/diagnostics/check/database_connection")
        assert response.status_code == 200
        check_result = response.json()
        assert check_result["result"]["status"] == "healthy"

        # 3. Get performance metrics
        response = mock_app.get("/api/v1/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert "metrics" in metrics

    async def test_error_handling_workflow(self, mock_app, mock_diagnostics_service):
        """Test error handling in diagnostics API."""
        # Simulate service error
        mock_diagnostics_service.get_system_health.side_effect = Exception(
            "Service error"
        )

        response = mock_app.get("/api/v1/health")
        assert response.status_code == 500
