"""
Integration tests for diagnostics API endpoints.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.diagnostics.domain.entities import (
    DiagnosticReport,
    PerformanceMetrics,
    SystemHealth,
)


class TestDiagnosticsAPI:
    """Test cases for diagnostics API endpoints."""

    @pytest.fixture
    def mock_diagnostics_service(self):
        """Mock diagnostics service."""
        return Mock()

    @pytest.fixture
    def sample_diagnostic_report(self):
        """Sample diagnostic report for testing."""
        return DiagnosticReport(
            report_id="test-report-123",
            timestamp=datetime.utcnow(),
            system_health=SystemHealth(
                cpu_usage=45.2, memory_usage=68.5, disk_usage=32.1, is_healthy=True
            ),
            performance_metrics=PerformanceMetrics(
                response_time=150.5, throughput=1000, error_rate=0.01
            ),
            issues=["High memory usage detected"],
            recommendations=["Consider scaling up memory allocation"],
        )

    @pytest.mark.asyncio
    async def test_get_system_health(self, async_client, mock_diagnostics_service):
        """Test getting system health status."""
        health_status = {
            "status": "healthy",
            "cpu_usage": 45.2,
            "memory_usage": 68.5,
            "disk_usage": 32.1,
            "uptime": 86400,
            "last_check": "2023-01-01T12:00:00Z",
        }

        mock_diagnostics_service.get_system_health = AsyncMock(
            return_value=health_status
        )

        response = await async_client.get("/api/diagnostics/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cpu_usage"] == 45.2

    @pytest.mark.asyncio
    async def test_run_diagnostics(
        self, async_client, mock_diagnostics_service, sample_diagnostic_report
    ):
        """Test running full diagnostics."""
        mock_diagnostics_service.run_diagnostics = AsyncMock(
            return_value=sample_diagnostic_report
        )

        response = await async_client.post("/api/diagnostics/run")

        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == "test-report-123"
        assert data["system_health"]["is_healthy"] is True
        assert len(data["issues"]) == 1

    @pytest.mark.asyncio
    async def test_get_performance_metrics(
        self, async_client, mock_diagnostics_service
    ):
        """Test getting performance metrics."""
        metrics = {
            "response_time": 150.5,
            "throughput": 1000,
            "error_rate": 0.01,
            "active_connections": 50,
            "requests_per_second": 25.5,
        }

        mock_diagnostics_service.get_performance_metrics = AsyncMock(
            return_value=metrics
        )

        response = await async_client.get("/api/diagnostics/metrics")

        assert response.status_code == 200
        data = response.json()
        assert data["response_time"] == 150.5
        assert data["throughput"] == 1000

    @pytest.mark.asyncio
    async def test_get_diagnostic_reports(
        self, async_client, mock_diagnostics_service, sample_diagnostic_report
    ):
        """Test getting diagnostic reports history."""
        reports = [sample_diagnostic_report]
        mock_diagnostics_service.get_diagnostic_reports = AsyncMock(
            return_value=reports
        )

        response = await async_client.get("/api/diagnostics/reports")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["report_id"] == "test-report-123"

    @pytest.mark.asyncio
    async def test_get_diagnostic_report_by_id(
        self, async_client, mock_diagnostics_service, sample_diagnostic_report
    ):
        """Test getting a specific diagnostic report."""
        mock_diagnostics_service.get_diagnostic_report = AsyncMock(
            return_value=sample_diagnostic_report
        )

        response = await async_client.get("/api/diagnostics/reports/test-report-123")

        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == "test-report-123"

    @pytest.mark.asyncio
    async def test_get_diagnostic_report_not_found(
        self, async_client, mock_diagnostics_service
    ):
        """Test getting non-existent diagnostic report."""
        mock_diagnostics_service.get_diagnostic_report = AsyncMock(return_value=None)

        response = await async_client.get("/api/diagnostics/reports/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_check_service_dependencies(
        self, async_client, mock_diagnostics_service
    ):
        """Test checking service dependencies."""
        dependencies_status = {
            "database": {"status": "healthy", "response_time": 50},
            "cache": {"status": "healthy", "response_time": 10},
            "external_api": {"status": "degraded", "response_time": 2000},
        }

        mock_diagnostics_service.check_dependencies = AsyncMock(
            return_value=dependencies_status
        )

        response = await async_client.get("/api/diagnostics/dependencies")

        assert response.status_code == 200
        data = response.json()
        assert data["database"]["status"] == "healthy"
        assert data["external_api"]["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_run_specific_diagnostic_check(
        self, async_client, mock_diagnostics_service
    ):
        """Test running a specific diagnostic check."""
        check_result = {
            "check_name": "memory_check",
            "status": "warning",
            "details": {"usage": 85.5, "threshold": 80.0},
            "recommendations": ["Consider freeing up memory"],
        }

        mock_diagnostics_service.run_specific_check = AsyncMock(
            return_value=check_result
        )

        response = await async_client.post("/api/diagnostics/checks/memory_check")

        assert response.status_code == 200
        data = response.json()
        assert data["check_name"] == "memory_check"
        assert data["status"] == "warning"

    @pytest.mark.asyncio
    async def test_export_diagnostic_report(
        self, async_client, mock_diagnostics_service
    ):
        """Test exporting diagnostic report."""
        export_data = {
            "format": "json",
            "report_id": "test-report-123",
            "data": {"report": "exported content"},
        }

        mock_diagnostics_service.export_report = AsyncMock(return_value=export_data)

        response = await async_client.get(
            "/api/diagnostics/reports/test-report-123/export?format=json"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_diagnostics_api_error_handling(
        self, async_client, mock_diagnostics_service
    ):
        """Test API error handling for diagnostics operations."""
        mock_diagnostics_service.get_system_health = AsyncMock(
            side_effect=Exception("System monitoring unavailable")
        )

        response = await async_client.get("/api/diagnostics/health")

        assert response.status_code == 500


class TestDiagnosticsAPIIntegration:
    """Integration tests for diagnostics API workflows."""

    @pytest.mark.asyncio
    async def test_comprehensive_diagnostics_workflow(
        self, async_client, mock_diagnostics_service, sample_diagnostic_report
    ):
        """Test comprehensive diagnostics workflow."""
        # 1. Check system health
        health_status = {"status": "healthy", "cpu_usage": 45.2, "memory_usage": 68.5}
        mock_diagnostics_service.get_system_health = AsyncMock(
            return_value=health_status
        )

        health_response = await async_client.get("/api/diagnostics/health")
        assert health_response.status_code == 200

        # 2. Run full diagnostics if health check passes
        if health_response.json()["status"] == "healthy":
            mock_diagnostics_service.run_diagnostics = AsyncMock(
                return_value=sample_diagnostic_report
            )

            diagnostics_response = await async_client.post("/api/diagnostics/run")
            assert diagnostics_response.status_code == 200

            # 3. Get performance metrics
            metrics = {"response_time": 150.5, "throughput": 1000, "error_rate": 0.01}
            mock_diagnostics_service.get_performance_metrics = AsyncMock(
                return_value=metrics
            )

            metrics_response = await async_client.get("/api/diagnostics/metrics")
            assert metrics_response.status_code == 200

            # 4. Check dependencies
            dependencies = {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"},
            }
            mock_diagnostics_service.check_dependencies = AsyncMock(
                return_value=dependencies
            )

            deps_response = await async_client.get("/api/diagnostics/dependencies")
            assert deps_response.status_code == 200

    @pytest.mark.asyncio
    async def test_diagnostic_alerts_workflow(
        self, async_client, mock_diagnostics_service
    ):
        """Test diagnostic alerts and notifications workflow."""
        # Simulate degraded system health
        degraded_health = {
            "status": "degraded",
            "cpu_usage": 95.0,
            "memory_usage": 89.5,
            "issues": ["High CPU usage", "High memory usage"],
        }

        mock_diagnostics_service.get_system_health = AsyncMock(
            return_value=degraded_health
        )

        response = await async_client.get("/api/diagnostics/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert len(data["issues"]) == 2

        # Run specific checks for the issues
        cpu_check = {
            "check_name": "cpu_check",
            "status": "critical",
            "details": {"usage": 95.0, "threshold": 80.0},
        }

        mock_diagnostics_service.run_specific_check = AsyncMock(return_value=cpu_check)

        cpu_response = await async_client.post("/api/diagnostics/checks/cpu_check")
        assert cpu_response.status_code == 200
        assert cpu_response.json()["status"] == "critical"

    @pytest.mark.asyncio
    async def test_diagnostics_reporting_workflow(
        self, async_client, mock_diagnostics_service, sample_diagnostic_report
    ):
        """Test diagnostics reporting and history workflow."""
        # Generate multiple reports
        reports = [sample_diagnostic_report]
        mock_diagnostics_service.get_diagnostic_reports = AsyncMock(
            return_value=reports
        )

        # Get reports history
        response = await async_client.get("/api/diagnostics/reports")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Get specific report
        mock_diagnostics_service.get_diagnostic_report = AsyncMock(
            return_value=sample_diagnostic_report
        )

        report_response = await async_client.get(
            f"/api/diagnostics/reports/{sample_diagnostic_report.report_id}"
        )
        assert report_response.status_code == 200

        # Export report
        export_data = {
            "format": "json",
            "report_id": sample_diagnostic_report.report_id,
            "data": sample_diagnostic_report.__dict__,
        }

        mock_diagnostics_service.export_report = AsyncMock(return_value=export_data)

        export_response = await async_client.get(
            f"/api/diagnostics/reports/{sample_diagnostic_report.report_id}/export"
        )
        assert export_response.status_code == 200
