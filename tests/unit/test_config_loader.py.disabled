#!/usr/bin/env python3
"""
Configuration Loader Unit Tests

Test-driven development for configuration loading functionality including:
- Base configuration loading
- Environment overlay handling
- Missing environment file graceful fallback
- Environment variable substitution
- API key validation requirements
- Configuration error handling
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from utils.config_loader import (
    ConfigLoader,
    FinancialServiceConfig
)


class TestConfigLoaderInitialization:
    """Test ConfigLoader initialization and setup"""

    def test_config_loader_initialization_with_default_path(self):
        """Test ConfigLoader initializes with default config directory"""
        # Act
        loader = ConfigLoader()

        # Assert
        assert loader.config_dir.name == "config"
        assert loader.env_pattern is not None

    def test_config_loader_initialization_with_custom_path(self):
        """Test ConfigLoader initializes with custom config directory"""
        # Arrange
        custom_path = "/tmp/test_config"

        # Act
        loader = ConfigLoader(custom_path)

        # Assert
        assert str(loader.config_dir) == custom_path


class TestBaseConfigurationLoading:
    """Test basic configuration file loading"""

    def test_load_base_config_success(self, temporary_config_file):
        """Test successful loading of base configuration file"""
        # Arrange
        loader = ConfigLoader()

        # Act
        config = loader.load_config(temporary_config_file)

        # Assert
        assert config is not None
        assert isinstance(config, dict)
        assert "services" in config
        assert "test_service" in config["services"]
        assert config["services"]["test_service"]["name"] == "test_service"

    def test_load_nonexistent_config_file_raises_error(self):
        """Test loading nonexistent config file raises FileNotFoundError"""
        # Arrange
        loader = ConfigLoader()
        nonexistent_file = "/tmp/nonexistent_config.yaml"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            loader.load_config(nonexistent_file)

    def test_load_invalid_yaml_raises_error(self):
        """Test loading invalid YAML file raises appropriate error"""
        # Arrange
        loader = ConfigLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML
            invalid_file = f.name

        try:
            # Act & Assert
            with pytest.raises(yaml.YAMLError):
                loader.load_config(invalid_file)
        finally:
            # Cleanup
            os.unlink(invalid_file)


class TestEnvironmentOverlayHandling:
    """Test environment-specific configuration overlay"""

    def test_load_missing_environment_config_graceful_fallback(self, temporary_config_file):
        """Test graceful fallback when environment config is missing"""
        # Arrange
        loader = ConfigLoader()

        # Act - Try to load with environment that doesn't exist
        config = loader.load_with_environment(temporary_config_file, "nonexistent_env")

        # Assert - Should still load base config successfully
        assert config is not None
        assert isinstance(config, dict)
        assert "services" in config
        assert "test_service" in config["services"]

    def test_load_with_environment_overlay_merges_correctly(self):
        """Test environment overlay merges correctly with base config"""
        # Arrange
        base_config = {
            "services": {
                "test_service": {
                    "name": "test_service",
                    "base_url": "https://base-api.example.com",
                    "timeout_seconds": 30
                }
            }
        }

        env_config = {
            "services": {
                "test_service": {
                    "base_url": "https://dev-api.example.com",  # Override
                    "debug": True  # Addition
                }
            }
        }

        loader = ConfigLoader()

        # Mock the config loading
        with patch.object(loader, 'load_config') as mock_load:
            mock_load.side_effect = [base_config, env_config]

            with patch('pathlib.Path.exists', return_value=True):
                # Act
                result = loader.load_with_environment("/tmp/base.yaml", "dev")

        # Assert
        assert result["services"]["test_service"]["name"] == "test_service"  # Original
        assert result["services"]["test_service"]["base_url"] == "https://dev-api.example.com"  # Overridden
        assert result["services"]["test_service"]["timeout_seconds"] == 30  # Original
        assert result["services"]["test_service"]["debug"] is True  # Added

    def test_environment_config_loading_error_continues_gracefully(self, temporary_config_file):
        """Test that environment config loading errors don't break base config loading"""
        # Arrange
        loader = ConfigLoader()

        # Mock environment config path to exist but fail to load
        with patch('pathlib.Path.exists', return_value=True):
            with patch.object(loader, 'load_config') as mock_load:
                # First call succeeds (base config), second call fails (env config)
                mock_load.side_effect = [
                    {"services": {"test_service": {"name": "test"}}},  # Base config
                    Exception("Simulated env config error")  # Env config failure
                ]

                # Act
                result = loader.load_with_environment(temporary_config_file, "dev")

        # Assert - Should still have base config
        assert result is not None
        assert "services" in result
        assert result["services"]["test_service"]["name"] == "test"


class TestEnvironmentVariableSubstitution:
    """Test environment variable substitution in configurations"""

    def test_environment_variable_substitution_success(self, test_environment_variables):
        """Test successful environment variable substitution"""
        # Arrange
        config_with_env_vars = {
            "services": {
                "test_service": {
                    "api_key": "${TEST_API_KEY}",
                    "base_url": "https://api.example.com"
                }
            }
        }

        loader = ConfigLoader()

        # Act
        result = loader._substitute_variables(config_with_env_vars)

        # Assert
        assert result["services"]["test_service"]["api_key"] == "test_key_12345"
        assert result["services"]["test_service"]["base_url"] == "https://api.example.com"

    def test_missing_environment_variable_preserves_placeholder(self):
        """Test that missing environment variables preserve the placeholder"""
        # Arrange
        config_with_missing_env = {
            "services": {
                "test_service": {
                    "api_key": "${MISSING_API_KEY}",
                    "base_url": "https://api.example.com"
                }
            }
        }

        loader = ConfigLoader()

        # Act
        result = loader._substitute_variables(config_with_missing_env)

        # Assert
        assert result["services"]["test_service"]["api_key"] == "${MISSING_API_KEY}"
        assert result["services"]["test_service"]["base_url"] == "https://api.example.com"


class TestFinancialServicesConfigLoading:
    """Test financial services specific configuration loading"""

    def test_load_financial_services_config_success(self):
        """Test successful loading of financial services configuration"""
        # Arrange
        mock_config = {
            "services": {
                "test_service": {
                    "name": "test_service",
                    "base_url": "https://api.example.com",
                    "api_key": "${TEST_API_KEY}"
                }
            },
            "global": {
                "cache": {"enabled": True},
                "rate_limiting": {"enabled": True}
            }
        }

        loader = ConfigLoader("/tmp/test_config")

        with patch.object(loader, 'load_with_environment', return_value=mock_config):
            # Act
            result = loader.load_financial_services_config("dev")

        # Assert
        assert result == mock_config
        assert "services" in result
        assert "global" in result

    def test_load_financial_services_config_missing_file_raises_error(self):
        """Test that missing financial services config file raises FileNotFoundError"""
        # Arrange
        loader = ConfigLoader("/tmp/nonexistent_config_dir")

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_financial_services_config("dev")

        assert "Financial services config not found" in str(exc_info.value)


class TestServiceConfigRetrieval:
    """Test service-specific configuration retrieval"""

    def test_get_service_config_success(self, test_environment_variables):
        """Test successful retrieval of service configuration"""
        # Arrange
        mock_full_config = {
            "services": {
                "test_service": {
                    "name": "test_service",
                    "base_url": "https://api.example.com",
                    "api_key": "${TEST_API_KEY}",
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "cache": {"enabled": True, "ttl_seconds": 900},
                    "rate_limit": {"enabled": True, "requests_per_minute": 60},
                    "headers": {"Accept": "application/json"}
                }
            },
            "global": {
                "cache": {"ttl_seconds": 600},
                "rate_limiting": {"default_requests_per_minute": 30}
            }
        }

        loader = ConfigLoader()

        with patch.object(loader, 'load_financial_services_config', return_value=mock_full_config):
            # Act
            service_config = loader.get_service_config("test_service", "dev")

        # Assert
        assert isinstance(service_config, FinancialServiceConfig)
        assert service_config.name == "test_service"
        assert service_config.base_url == "https://api.example.com"
        assert service_config.api_key == "test_key_12345"  # Environment variable substituted
        assert service_config.timeout_seconds == 30

    def test_get_service_config_missing_service_raises_error(self):
        """Test that missing service configuration raises KeyError"""
        # Arrange
        mock_config = {
            "services": {
                "other_service": {"name": "other_service"}
            }
        }

        loader = ConfigLoader()

        with patch.object(loader, 'load_financial_services_config', return_value=mock_config):
            # Act & Assert
            with pytest.raises(KeyError) as exc_info:
                loader.get_service_config("missing_service", "dev")

            assert "Service 'missing_service' not found" in str(exc_info.value)

    def test_get_service_config_missing_services_section_raises_error(self):
        """Test that missing services section raises KeyError"""
        # Arrange
        mock_config = {"global": {"some": "config"}}  # No services section

        loader = ConfigLoader()

        with patch.object(loader, 'load_financial_services_config', return_value=mock_config):
            # Act & Assert
            with pytest.raises(KeyError) as exc_info:
                loader.get_service_config("any_service", "dev")

            assert "No services configuration found" in str(exc_info.value)


class TestConfigValidation:
    """Test configuration validation functionality"""

    def test_validate_financial_services_config_success(self, test_environment_variables):
        """Test successful validation of financial services configuration"""
        # Arrange
        valid_config = {
            "services": {
                "test_service": {
                    "name": "test_service",
                    "base_url": "https://api.example.com",
                    "api_key": "${TEST_API_KEY}",
                    "cache": {"enabled": True},
                    "rate_limit": {"enabled": True}
                }
            }
        }

        loader = ConfigLoader()

        with patch.object(loader, 'load_financial_services_config', return_value=valid_config):
            # Act
            validation_result = loader.validate_financial_services_config("dev")

        # Assert
        assert validation_result["valid"] is True
        assert validation_result["services_validated"] == 1
        assert len(validation_result["errors"]) == 0

    def test_validate_config_with_missing_api_key_reports_error(self):
        """Test validation reports error for missing API key"""
        # Arrange
        loader = ConfigLoader()

        # Mock missing environment variable
        with patch.dict(os.environ, {}, clear=True):
            # Act
            validation_result = loader.validate_financial_services_config("dev")

        # Assert
        assert validation_result["valid"] is False
        assert any("API key" in error for error in validation_result["errors"])


@pytest.mark.unit
class TestConfigurationErrorHandling:
    """Test configuration loading error handling"""

    def test_config_loading_handles_yaml_parse_errors(self):
        """Test graceful handling of YAML parsing errors"""
        # Arrange
        loader = ConfigLoader()

        # Create invalid YAML content
        invalid_yaml = "invalid: yaml: content: ["

        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act & Assert
                with pytest.raises(yaml.YAMLError):
                    loader.load_config("/tmp/invalid.yaml")

    def test_config_loading_handles_file_permission_errors(self):
        """Test graceful handling of file permission errors"""
        # Arrange
        loader = ConfigLoader()

        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('pathlib.Path.exists', return_value=True):
                # Act & Assert
                with pytest.raises(PermissionError):
                    loader.load_config("/tmp/restricted.yaml")
