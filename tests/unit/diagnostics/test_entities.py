"""
Unit tests for diagnostics domain entities.

This module tests the core diagnostic entities including health checks,
diagnostic results, and system health aggregates.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from ingenious.diagnostics.domain.entities import (
    HealthStatus,
    DiagnosticCheck,
    DiagnosticResult,
    SystemHealth
)


class TestHealthStatus:
    """Test suite for HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test HealthStatus enum values."""
        # Assert
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"
    
    def test_health_status_comparison(self):
        """Test HealthStatus comparison."""
        # Assert
        assert HealthStatus.HEALTHY == HealthStatus.HEALTHY
        assert HealthStatus.HEALTHY != HealthStatus.DEGRADED
        assert HealthStatus.DEGRADED != HealthStatus.UNHEALTHY
        assert HealthStatus.UNHEALTHY != HealthStatus.UNKNOWN
    
    def test_health_status_string_representation(self):
        """Test HealthStatus string representation."""
        # Assert
        assert str(HealthStatus.HEALTHY) == "HealthStatus.HEALTHY"
        assert str(HealthStatus.DEGRADED) == "HealthStatus.DEGRADED"


class TestDiagnosticCheck:
    """Test suite for DiagnosticCheck entity."""
    
    def test_diagnostic_check_creation_minimal(self):
        """Test creating DiagnosticCheck with minimal required fields."""
        # Act
        check = DiagnosticCheck(
            name="Database Connection",
            description="Check if database is reachable"
        )
        
        # Assert
        assert check.name == "Database Connection"
        assert check.description == "Check if database is reachable"
        assert check.check_id is not None
        assert check.category == "general"  # Default value
        assert check.timeout_seconds == 30  # Default value
    
    def test_diagnostic_check_creation_full(self):
        """Test creating DiagnosticCheck with all fields."""
        # Act
        check = DiagnosticCheck(
            name="API Health Check",
            description="Verify API endpoints are responding",
            check_id="api-health-001",
            category="infrastructure",
            timeout_seconds=60
        )
        
        # Assert
        assert check.name == "API Health Check"
        assert check.description == "Verify API endpoints are responding"
        assert check.check_id == "api-health-001"
        assert check.category == "infrastructure"
        assert check.timeout_seconds == 60
    
    def test_diagnostic_check_auto_generated_id(self):
        """Test that check_id is auto-generated when not provided."""
        # Act
        check1 = DiagnosticCheck(name="Test 1", description="First test")
        check2 = DiagnosticCheck(name="Test 2", description="Second test")
        
        # Assert
        assert check1.check_id is not None
        assert check2.check_id is not None
        assert check1.check_id != check2.check_id
        assert len(check1.check_id) > 0
        assert len(check2.check_id) > 0
    
    def test_diagnostic_check_equality(self):
        """Test DiagnosticCheck equality comparison."""
        # Arrange
        check1 = DiagnosticCheck(
            name="Test Check", 
            description="Test", 
            check_id="test-id-123"
        )
        check2 = DiagnosticCheck(
            name="Different Name", 
            description="Different description", 
            check_id="test-id-123"
        )
        check3 = DiagnosticCheck(
            name="Test Check", 
            description="Test", 
            check_id="different-id"
        )
        
        # Act & Assert
        assert check1 == check2  # Same check_id
        assert check1 != check3  # Different check_id
        assert check1 != "not a check"  # Different type
    
    def test_diagnostic_check_category_variations(self):
        """Test DiagnosticCheck with different categories."""
        # Arrange
        categories = ["infrastructure", "security", "performance", "connectivity", "custom"]
        
        for category in categories:
            # Act
            check = DiagnosticCheck(
                name=f"Check for {category}",
                description=f"Test check for {category} category",
                category=category
            )
            
            # Assert
            assert check.category == category
    
    def test_diagnostic_check_timeout_validation(self):
        """Test DiagnosticCheck timeout validation."""
        # Arrange
        valid_timeouts = [1, 30, 60, 300, 3600]
        
        for timeout in valid_timeouts:
            # Act
            check = DiagnosticCheck(
                name="Timeout Test",
                description="Test timeout validation",
                timeout_seconds=timeout
            )
            
            # Assert
            assert check.timeout_seconds == timeout


class TestDiagnosticResult:
    """Test suite for DiagnosticResult entity."""
    
    def test_diagnostic_result_creation_success(self):
        """Test creating a successful DiagnosticResult."""
        # Arrange
        check = DiagnosticCheck(
            name="Test Check",
            description="Test description",
            check_id="test-123"
        )
        
        # Act
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="Check passed successfully",
            execution_time=0.25
        )
        
        # Assert
        assert result.check == check
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed successfully"
        assert result.execution_time == 0.25
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
        assert result.details == {}  # Default value
    
    def test_diagnostic_result_creation_failure(self):
        """Test creating a failed DiagnosticResult."""
        # Arrange
        check = DiagnosticCheck(name="Failing Check", description="This will fail")
        error_details = {
            "error_code": "CONNECTION_FAILED",
            "error_message": "Could not connect to database",
            "retry_count": 3
        }
        
        # Act
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.UNHEALTHY,
            message="Database connection failed",
            execution_time=5.0,
            details=error_details
        )
        
        # Assert
        assert result.check == check
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Database connection failed"
        assert result.execution_time == 5.0
        assert result.details == error_details
    
    def test_diagnostic_result_with_custom_timestamp(self):
        """Test creating DiagnosticResult with custom timestamp."""
        # Arrange
        check = DiagnosticCheck(name="Test", description="Test")
        custom_timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="Test passed",
            execution_time=1.0,
            timestamp=custom_timestamp
        )
        
        # Assert
        assert result.timestamp == custom_timestamp
    
    def test_diagnostic_result_is_healthy(self):
        """Test DiagnosticResult.is_healthy property."""
        # Arrange
        check = DiagnosticCheck(name="Test", description="Test")
        
        # Act & Assert
        healthy_result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        assert healthy_result.is_healthy is True
        
        degraded_result = DiagnosticResult(
            check=check,
            status=HealthStatus.DEGRADED,
            message="Warning"
        )
        assert degraded_result.is_healthy is False
        
        unhealthy_result = DiagnosticResult(
            check=check,
            status=HealthStatus.UNHEALTHY,
            message="Error"
        )
        assert unhealthy_result.is_healthy is False
    
    def test_diagnostic_result_to_dict(self):
        """Test DiagnosticResult.to_dict method."""
        # Arrange
        check = DiagnosticCheck(
            name="Dict Test",
            description="Test dict conversion",
            check_id="dict-test-001"
        )
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="Success",
            execution_time=1.5,
            details={"custom": "data"}
        )
        
        # Act
        result_dict = result.to_dict()
        
        # Assert
        assert result_dict["check_id"] == "dict-test-001"
        assert result_dict["check_name"] == "Dict Test"
        assert result_dict["status"] == "healthy"
        assert result_dict["message"] == "Success"
        assert result_dict["execution_time"] == 1.5
        assert result_dict["details"] == {"custom": "data"}
        assert "timestamp" in result_dict


class TestSystemHealth:
    """Test suite for SystemHealth aggregate."""
    
    def test_system_health_creation_default(self):
        """Test creating SystemHealth with default values."""
        # Act
        health = SystemHealth()
        
        # Assert
        assert health.service_name == "ingenious"
        assert health.results == []
        assert health.overall_status == HealthStatus.UNKNOWN
        assert health.last_updated is not None
        assert isinstance(health.last_updated, datetime)
    
    def test_system_health_creation_custom_service(self):
        """Test creating SystemHealth with custom service name."""
        # Act
        health = SystemHealth(service_name="custom-service")
        
        # Assert
        assert health.service_name == "custom-service"
    
    def test_add_result_single_healthy(self):
        """Test adding a single healthy result."""
        # Arrange
        health = SystemHealth()
        check = DiagnosticCheck(name="Test Check", description="Test")
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="All good"
        )
        
        # Act
        health.add_result(result)
        
        # Assert
        assert len(health.results) == 1
        assert health.results[0] == result
        assert health.overall_status == HealthStatus.HEALTHY
    
    def test_add_result_single_unhealthy(self):
        """Test adding a single unhealthy result."""
        # Arrange
        health = SystemHealth()
        check = DiagnosticCheck(name="Failing Check", description="Will fail")
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.UNHEALTHY,
            message="Something is wrong"
        )
        
        # Act
        health.add_result(result)
        
        # Assert
        assert len(health.results) == 1
        assert health.overall_status == HealthStatus.UNHEALTHY
    
    def test_add_multiple_results_mixed_status(self):
        """Test adding multiple results with mixed statuses."""
        # Arrange
        health = SystemHealth()
        
        check1 = DiagnosticCheck(name="Good Check", description="Should pass")
        result1 = DiagnosticResult(
            check=check1,
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        
        check2 = DiagnosticCheck(name="Warning Check", description="Has warnings")
        result2 = DiagnosticResult(
            check=check2,
            status=HealthStatus.DEGRADED,
            message="Warning"
        )
        
        check3 = DiagnosticCheck(name="Another Good Check", description="Also good")
        result3 = DiagnosticResult(
            check=check3,
            status=HealthStatus.HEALTHY,
            message="Also OK"
        )
        
        # Act
        health.add_result(result1)
        health.add_result(result2)
        health.add_result(result3)
        
        # Assert
        assert len(health.results) == 3
        assert health.overall_status == HealthStatus.DEGRADED  # Worst status wins
    
    def test_overall_status_calculation_all_healthy(self):
        """Test overall status calculation with all healthy results."""
        # Arrange
        health = SystemHealth()
        
        for i in range(3):
            check = DiagnosticCheck(name=f"Check {i}", description=f"Test {i}")
            result = DiagnosticResult(
                check=check,
                status=HealthStatus.HEALTHY,
                message="OK"
            )
            health.add_result(result)
        
        # Assert
        assert health.overall_status == HealthStatus.HEALTHY
    
    def test_overall_status_calculation_with_unhealthy(self):
        """Test overall status calculation with unhealthy results."""
        # Arrange
        health = SystemHealth()
        
        # Add healthy results
        for i in range(2):
            check = DiagnosticCheck(name=f"Good Check {i}", description="Good")
            result = DiagnosticResult(
                check=check,
                status=HealthStatus.HEALTHY,
                message="OK"
            )
            health.add_result(result)
        
        # Add one unhealthy result
        bad_check = DiagnosticCheck(name="Bad Check", description="Bad")
        bad_result = DiagnosticResult(
            check=bad_check,
            status=HealthStatus.UNHEALTHY,
            message="Failed"
        )
        health.add_result(bad_result)
        
        # Assert
        assert health.overall_status == HealthStatus.UNHEALTHY
    
    def test_get_results_by_category(self):
        """Test filtering results by category."""
        # Arrange
        health = SystemHealth()
        
        # Add results from different categories
        infra_check = DiagnosticCheck(
            name="Database", 
            description="DB check", 
            category="infrastructure"
        )
        infra_result = DiagnosticResult(
            check=infra_check,
            status=HealthStatus.HEALTHY,
            message="DB OK"
        )
        
        security_check = DiagnosticCheck(
            name="Auth", 
            description="Auth check", 
            category="security"
        )
        security_result = DiagnosticResult(
            check=security_check,
            status=HealthStatus.HEALTHY,
            message="Auth OK"
        )
        
        health.add_result(infra_result)
        health.add_result(security_result)
        
        # Act
        infra_results = health.get_results_by_category("infrastructure")
        security_results = health.get_results_by_category("security")
        nonexistent_results = health.get_results_by_category("nonexistent")
        
        # Assert
        assert len(infra_results) == 1
        assert infra_results[0] == infra_result
        assert len(security_results) == 1
        assert security_results[0] == security_result
        assert len(nonexistent_results) == 0
    
    def test_to_dict(self):
        """Test SystemHealth.to_dict method."""
        # Arrange
        health = SystemHealth(service_name="test-service")
        
        check = DiagnosticCheck(name="Test Check", description="Test")
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        health.add_result(result)
        
        # Act
        health_dict = health.to_dict()
        
        # Assert
        assert health_dict["service_name"] == "test-service"
        assert health_dict["overall_status"] == "healthy"
        assert "last_updated" in health_dict
        assert len(health_dict["results"]) == 1
        assert health_dict["results"][0]["check_name"] == "Test Check"
    
    def test_last_updated_timestamp_updates(self):
        """Test that last_updated timestamp updates when results are added."""
        # Arrange
        health = SystemHealth()
        initial_timestamp = health.last_updated
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        check = DiagnosticCheck(name="Test", description="Test")
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        
        # Act
        health.add_result(result)
        
        # Assert
        assert health.last_updated > initial_timestamp


@pytest.mark.unit
class TestDiagnosticsEntitiesIntegration:
    """Integration tests for diagnostics entities working together."""
    
    def test_complete_health_check_workflow(self):
        """Test a complete health check workflow."""
        # Arrange
        system_health = SystemHealth(service_name="integration-test")
        
        # Create various checks
        checks_data = [
            ("Database Connection", "infrastructure", HealthStatus.HEALTHY, "Connected successfully"),
            ("API Response Time", "performance", HealthStatus.DEGRADED, "Response time is slow"),
            ("Authentication Service", "security", HealthStatus.HEALTHY, "Auth service operational"),
            ("External API", "connectivity", HealthStatus.UNHEALTHY, "External service unavailable")
        ]
        
        # Act
        for name, category, status, message in checks_data:
            check = DiagnosticCheck(
                name=name,
                description=f"Check for {name}",
                category=category
            )
            result = DiagnosticResult(
                check=check,
                status=status,
                message=message,
                execution_time=0.5
            )
            system_health.add_result(result)
        
        # Assert
        assert len(system_health.results) == 4
        assert system_health.overall_status == HealthStatus.UNHEALTHY  # Worst status
        
        # Check category filtering
        infra_results = system_health.get_results_by_category("infrastructure")
        assert len(infra_results) == 1
        assert infra_results[0].check.name == "Database Connection"
        
        security_results = system_health.get_results_by_category("security")
        assert len(security_results) == 1
        assert security_results[0].status == HealthStatus.HEALTHY
        
        # Check serialization
        health_dict = system_health.to_dict()
        assert health_dict["service_name"] == "integration-test"
        assert health_dict["overall_status"] == "unhealthy"
        assert len(health_dict["results"]) == 4
    
    def test_health_status_priority_calculation(self):
        """Test that health status calculation follows proper priority."""
        # Arrange
        health = SystemHealth()
        
        # Test different combinations to verify priority:
        # UNKNOWN < HEALTHY < DEGRADED < UNHEALTHY
        
        status_combinations = [
            ([HealthStatus.HEALTHY, HealthStatus.HEALTHY], HealthStatus.HEALTHY),
            ([HealthStatus.HEALTHY, HealthStatus.DEGRADED], HealthStatus.DEGRADED),
            ([HealthStatus.HEALTHY, HealthStatus.UNHEALTHY], HealthStatus.UNHEALTHY),
            ([HealthStatus.DEGRADED, HealthStatus.DEGRADED], HealthStatus.DEGRADED),
            ([HealthStatus.DEGRADED, HealthStatus.UNHEALTHY], HealthStatus.UNHEALTHY),
            ([HealthStatus.UNKNOWN, HealthStatus.HEALTHY], HealthStatus.HEALTHY),
            ([HealthStatus.UNKNOWN, HealthStatus.DEGRADED], HealthStatus.DEGRADED),
        ]
        
        for statuses, expected_overall in status_combinations:
            # Create fresh SystemHealth for each test
            test_health = SystemHealth()
            
            for i, status in enumerate(statuses):
                check = DiagnosticCheck(name=f"Check {i}", description=f"Test {i}")
                result = DiagnosticResult(
                    check=check,
                    status=status,
                    message="Test message"
                )
                test_health.add_result(result)
            
            # Assert
            assert test_health.overall_status == expected_overall, \
                f"Expected {expected_overall} for statuses {statuses}, got {test_health.overall_status}"
    
    def test_diagnostic_result_with_detailed_context(self):
        """Test DiagnosticResult with detailed contextual information."""
        # Arrange
        check = DiagnosticCheck(
            name="Complex API Check",
            description="Check multiple API endpoints",
            category="api",
            timeout_seconds=45
        )
        
        detailed_info = {
            "endpoints_checked": ["/health", "/api/v1/users", "/api/v1/data"],
            "response_times": {"health": 0.1, "users": 0.3, "data": 2.5},
            "status_codes": {"health": 200, "users": 200, "data": 500},
            "errors": [{"endpoint": "/api/v1/data", "error": "Internal Server Error"}],
            "recommendations": ["Check data service logs", "Verify database connection"]
        }
        
        # Act
        result = DiagnosticResult(
            check=check,
            status=HealthStatus.DEGRADED,
            message="Some endpoints are experiencing issues",
            execution_time=3.2,
            details=detailed_info
        )
        
        # Assert
        assert result.details["endpoints_checked"] == ["/health", "/api/v1/users", "/api/v1/data"]
        assert result.details["errors"][0]["endpoint"] == "/api/v1/data"
        assert len(result.details["recommendations"]) == 2
        
        # Check dict serialization includes details
        result_dict = result.to_dict()
        assert "endpoints_checked" in result_dict["details"]
        assert "recommendations" in result_dict["details"]
