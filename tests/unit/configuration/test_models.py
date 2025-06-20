"""
Unit tests for configuration domain models.

This module tests the configuration models and validation logic.
"""

import pytest
from typing import Any, Dict
from pydantic import ValidationError

from ingenious.configuration.domain.models import (
    ConfigurationItem,
    AppConfiguration,
    AuthenticationConfig,
    LLMConfig,
    FileStorageConfig,
    MinimalConfig
)


class TestConfigurationItem:
    """Test suite for ConfigurationItem model."""
    
    def test_configuration_item_creation_basic(self):
        """Test creating a basic configuration item."""
        # Act
        item = ConfigurationItem(
            key="database.host",
            value="localhost",
            description="Database host address"
        )
        
        # Assert
        assert item.key == "database.host"
        assert item.value == "localhost"
        assert item.description == "Database host address"
        assert item.is_secret is False  # Default value
        assert item.environment is None  # Default value
    
    def test_configuration_item_creation_full(self):
        """Test creating a configuration item with all fields."""
        # Act
        item = ConfigurationItem(
            key="api.secret_key",
            value="super-secret-key",
            description="API secret key for authentication",
            is_secret=True,
            environment="production"
        )
        
        # Assert
        assert item.key == "api.secret_key"
        assert item.value == "super-secret-key"
        assert item.description == "API secret key for authentication"
        assert item.is_secret is True
        assert item.environment == "production"
    
    def test_configuration_item_validation_empty_key(self):
        """Test validation fails with empty key."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ConfigurationItem(key="", value="test")
        
        assert "key" in str(exc_info.value)
    
    def test_configuration_item_validation_none_value(self):
        """Test that None value is allowed."""
        # Act
        item = ConfigurationItem(key="optional.setting", value=None)
        
        # Assert
        assert item.value is None
    
    def test_configuration_item_serialization(self):
        """Test ConfigurationItem serialization."""
        # Arrange
        item = ConfigurationItem(
            key="test.key",
            value="test.value",
            is_secret=True
        )
        
        # Act
        data = item.model_dump()
        
        # Assert
        assert data["key"] == "test.key"
        assert data["value"] == "test.value"
        assert data["is_secret"] is True


class TestAppConfiguration:
    """Test suite for AppConfiguration model."""
    
    def test_app_configuration_creation_minimal(self):
        """Test creating AppConfiguration with minimal data."""
        # Act
        config = AppConfiguration(name="test-app")
        
        # Assert
        assert config.name == "test-app"
        assert config.version == "1.0.0"  # Default value
        assert config.environment == "development"  # Default value
        assert config.debug is False  # Default value
        assert config.log_level == "INFO"  # Default value
    
    def test_app_configuration_creation_full(self):
        """Test creating AppConfiguration with all fields."""
        # Act
        config = AppConfiguration(
            name="production-app",
            version="2.1.3",
            environment="production",
            debug=False,
            log_level="ERROR",
            description="Production application configuration"
        )
        
        # Assert
        assert config.name == "production-app"
        assert config.version == "2.1.3"
        assert config.environment == "production"
        assert config.debug is False
        assert config.log_level == "ERROR"
        assert config.description == "Production application configuration"
    
    def test_app_configuration_validation_empty_name(self):
        """Test validation fails with empty name."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AppConfiguration(name="")
        
        assert "name" in str(exc_info.value)
    
    def test_app_configuration_log_level_validation(self):
        """Test log level validation."""
        # Arrange
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            # Act
            config = AppConfiguration(name="test", log_level=level)
            
            # Assert
            assert config.log_level == level
    
    def test_app_configuration_invalid_log_level(self):
        """Test invalid log level validation."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AppConfiguration(name="test", log_level="INVALID")
        
        assert "log_level" in str(exc_info.value)


class TestAuthenticationConfig:
    """Test suite for AuthenticationConfig model."""
    
    def test_authentication_config_creation_minimal(self):
        """Test creating AuthenticationConfig with minimal data."""
        # Act
        config = AuthenticationConfig()
        
        # Assert
        assert config.enabled is True  # Default value
        assert config.provider == "local"  # Default value
        assert config.token_expiry == 3600  # Default value
        assert config.secret_key is None
        assert config.issuer is None
    
    def test_authentication_config_creation_full(self):
        """Test creating AuthenticationConfig with all fields."""
        # Act
        config = AuthenticationConfig(
            enabled=True,
            provider="oauth2",
            secret_key="super-secret-jwt-key",
            token_expiry=7200,
            issuer="https://auth.example.com",
            audience="api.example.com"
        )
        
        # Assert
        assert config.enabled is True
        assert config.provider == "oauth2"
        assert config.secret_key == "super-secret-jwt-key"
        assert config.token_expiry == 7200
        assert config.issuer == "https://auth.example.com"
        assert config.audience == "api.example.com"
    
    def test_authentication_config_provider_validation(self):
        """Test authentication provider validation."""
        # Arrange
        valid_providers = ["local", "oauth2", "saml", "ldap"]
        
        for provider in valid_providers:
            # Act
            config = AuthenticationConfig(provider=provider)
            
            # Assert
            assert config.provider == provider
    
    def test_authentication_config_invalid_provider(self):
        """Test invalid authentication provider."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationConfig(provider="invalid_provider")
        
        assert "provider" in str(exc_info.value)
    
    def test_authentication_config_token_expiry_validation(self):
        """Test token expiry validation."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationConfig(token_expiry=0)  # Should be positive
        
        assert "token_expiry" in str(exc_info.value)


class TestLLMConfig:
    """Test suite for LLMConfig model."""
    
    def test_llm_config_creation_minimal(self):
        """Test creating LLMConfig with minimal data."""
        # Act
        config = LLMConfig()
        
        # Assert
        assert config.provider == "openai"  # Default value
        assert config.model == "gpt-3.5-turbo"  # Default value
        assert config.temperature == 0.7  # Default value
        assert config.max_tokens == 1000  # Default value
        assert config.api_key is None
        assert config.base_url is None
    
    def test_llm_config_creation_full(self):
        """Test creating LLMConfig with all fields."""
        # Act
        config = LLMConfig(
            provider="azure",
            model="gpt-4",
            api_key="secret-api-key",
            base_url="https://api.openai.azure.com",
            temperature=0.9,
            max_tokens=2000,
            timeout=60,
            retry_attempts=3
        )
        
        # Assert
        assert config.provider == "azure"
        assert config.model == "gpt-4"
        assert config.api_key == "secret-api-key"
        assert config.base_url == "https://api.openai.azure.com"
        assert config.temperature == 0.9
        assert config.max_tokens == 2000
        assert config.timeout == 60
        assert config.retry_attempts == 3
    
    def test_llm_config_temperature_validation(self):
        """Test temperature validation."""
        # Test valid temperatures
        valid_temps = [0.0, 0.5, 1.0, 2.0]
        for temp in valid_temps:
            config = LLMConfig(temperature=temp)
            assert config.temperature == temp
        
        # Test invalid temperatures
        invalid_temps = [-0.1, 2.1]
        for temp in invalid_temps:
            with pytest.raises(ValidationError) as exc_info:
                LLMConfig(temperature=temp)
            assert "temperature" in str(exc_info.value)
    
    def test_llm_config_max_tokens_validation(self):
        """Test max_tokens validation."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LLMConfig(max_tokens=0)  # Should be positive
        
        assert "max_tokens" in str(exc_info.value)
    
    def test_llm_config_provider_validation(self):
        """Test provider validation."""
        # Arrange
        valid_providers = ["openai", "azure", "anthropic", "local"]
        
        for provider in valid_providers:
            # Act
            config = LLMConfig(provider=provider)
            
            # Assert
            assert config.provider == provider


class TestFileStorageConfig:
    """Test suite for FileStorageConfig model."""
    
    def test_file_storage_config_creation_minimal(self):
        """Test creating FileStorageConfig with minimal data."""
        # Act
        config = FileStorageConfig()
        
        # Assert
        assert config.provider == "local"  # Default value
        assert config.base_path == "./uploads"  # Default value
        assert config.max_file_size == 10485760  # 10MB default
        assert config.allowed_extensions == [".txt", ".pdf", ".doc", ".docx"]  # Default
        assert config.bucket_name is None
        assert config.region is None
    
    def test_file_storage_config_creation_full(self):
        """Test creating FileStorageConfig with all fields."""
        # Act
        config = FileStorageConfig(
            provider="s3",
            base_path="/uploads",
            bucket_name="my-app-uploads",
            region="us-west-2",
            max_file_size=52428800,  # 50MB
            allowed_extensions=[".txt", ".pdf", ".jpg", ".png"],
            access_key="access-key",
            secret_key="secret-key"
        )
        
        # Assert
        assert config.provider == "s3"
        assert config.base_path == "/uploads"
        assert config.bucket_name == "my-app-uploads"
        assert config.region == "us-west-2"
        assert config.max_file_size == 52428800
        assert config.allowed_extensions == [".txt", ".pdf", ".jpg", ".png"]
        assert config.access_key == "access-key"
        assert config.secret_key == "secret-key"
    
    def test_file_storage_config_provider_validation(self):
        """Test storage provider validation."""
        # Arrange
        valid_providers = ["local", "s3", "azure", "gcp"]
        
        for provider in valid_providers:
            # Act
            config = FileStorageConfig(provider=provider)
            
            # Assert
            assert config.provider == provider
    
    def test_file_storage_config_max_file_size_validation(self):
        """Test max file size validation."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            FileStorageConfig(max_file_size=0)  # Should be positive
        
        assert "max_file_size" in str(exc_info.value)


class TestMinimalConfig:
    """Test suite for MinimalConfig model."""
    
    def test_minimal_config_creation_defaults(self):
        """Test creating MinimalConfig with default values."""
        # Act
        config = MinimalConfig()
        
        # Assert
        assert config.project_name == "ingenious-project"  # Default
        assert config.environment == "development"  # Default
        assert config.log_level == "INFO"  # Default
        assert config.debug is False  # Default
    
    def test_minimal_config_creation_custom(self):
        """Test creating MinimalConfig with custom values."""
        # Act
        config = MinimalConfig(
            project_name="my-custom-project",
            environment="production",
            log_level="ERROR",
            debug=True
        )
        
        # Assert
        assert config.project_name == "my-custom-project"
        assert config.environment == "production"
        assert config.log_level == "ERROR"
        assert config.debug is True
    
    def test_minimal_config_validation_empty_project_name(self):
        """Test validation fails with empty project name."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MinimalConfig(project_name="")
        
        assert "project_name" in str(exc_info.value)
    
    def test_minimal_config_serialization(self):
        """Test MinimalConfig serialization and deserialization."""
        # Arrange
        original_config = MinimalConfig(
            project_name="serialization-test",
            environment="test",
            log_level="DEBUG"
        )
        
        # Act
        config_dict = original_config.model_dump()
        restored_config = MinimalConfig(**config_dict)
        
        # Assert
        assert restored_config.project_name == original_config.project_name
        assert restored_config.environment == original_config.environment
        assert restored_config.log_level == original_config.log_level
        assert restored_config.debug == original_config.debug


@pytest.mark.unit
class TestConfigurationModelsIntegration:
    """Integration tests for configuration models."""
    
    def test_complete_configuration_setup(self):
        """Test creating a complete configuration setup."""
        # Arrange & Act
        app_config = AppConfiguration(
            name="integration-test-app",
            version="1.0.0",
            environment="production",
            log_level="WARNING"
        )
        
        auth_config = AuthenticationConfig(
            enabled=True,
            provider="oauth2",
            token_expiry=7200
        )
        
        llm_config = LLMConfig(
            provider="azure",
            model="gpt-4",
            temperature=0.8,
            max_tokens=1500
        )
        
        storage_config = FileStorageConfig(
            provider="s3",
            bucket_name="app-storage",
            max_file_size=20971520  # 20MB
        )
        
        # Assert
        assert app_config.name == "integration-test-app"
        assert app_config.environment == "production"
        assert auth_config.provider == "oauth2"
        assert llm_config.model == "gpt-4"
        assert storage_config.provider == "s3"
    
    def test_configuration_validation_scenarios(self):
        """Test various configuration validation scenarios."""
        # Test environment-specific configurations
        environments = ["development", "staging", "production"]
        
        for env in environments:
            app_config = AppConfiguration(
                name=f"app-{env}",
                environment=env,
                debug=(env == "development")  # Debug only in development
            )
            
            assert app_config.environment == env
            assert app_config.debug == (env == "development")
    
    def test_configuration_serialization_round_trip(self):
        """Test serialization and deserialization of all config models."""
        # Arrange
        configs = [
            AppConfiguration(name="test-app", environment="test"),
            AuthenticationConfig(provider="local", enabled=True),
            LLMConfig(provider="openai", model="gpt-3.5-turbo"),
            FileStorageConfig(provider="local", base_path="./test-uploads"),
            MinimalConfig(project_name="test-project")
        ]
        
        for original_config in configs:
            # Act
            config_dict = original_config.model_dump()
            
            # Create new instance from dict
            config_type = type(original_config)
            restored_config = config_type(**config_dict)
            
            # Assert
            assert restored_config.model_dump() == original_config.model_dump()
    
    def test_configuration_defaults_consistency(self):
        """Test that configuration defaults are consistent across models."""
        # Arrange & Act
        app_config = AppConfiguration(name="test")
        minimal_config = MinimalConfig()
        
        # Assert - Both should have consistent defaults where applicable
        assert app_config.environment == minimal_config.environment  # Both default to "development"
        assert app_config.log_level == minimal_config.log_level  # Both default to "INFO"
