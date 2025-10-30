#!/usr/bin/env python3
"""
Service Factory Unit Tests

Test-driven development for service factory functionality including:
- Service creation with valid configuration
- API key validation requirements
- Factory returns None on missing API key
- Configuration error handling
- Service instance validation
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from services.economic_calendar import create_economic_calendar_service
from services.base_financial_service import (
    ServiceConfig,
    CacheConfig,
    RateLimitConfig,
    HistoricalStorageConfig
)


class TestEconomicCalendarServiceFactory:
    """Test economic calendar service factory functionality"""

    def test_factory_returns_service_with_valid_config(self, test_environment_variables):
        """Test factory returns valid service instance with proper configuration"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
        mock_service_config.api_key = "test_fred_key"
        mock_service_config.timeout_seconds = 30
        mock_service_config.max_retries = 3
        mock_service_config.cache = {
            "enabled": True,
            "ttl_seconds": 900,
            "cache_dir": "/tmp/test_cache",
            "max_size_mb": 100
        }
        mock_service_config.rate_limit = {
            "enabled": True,
            "requests_per_minute": 120,
            "burst_limit": 10
        }
        mock_service_config.headers = {"Accept": "application/json"}

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is not None
        assert hasattr(service, 'health_check')
        assert hasattr(service, 'get_upcoming_economic_events')
        assert hasattr(service, 'get_fomc_decision_probabilities')

    def test_factory_returns_none_on_missing_api_key(self):
        """Test factory returns None when API key is missing"""
        # Arrange - Clear environment and disable auto env loading
        with patch.dict('os.environ', {}, clear=True):  # Clear all environment variables
            mock_service_config = Mock()
            mock_service_config.name = "economic_calendar"
            mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
            mock_service_config.api_key = None  # Missing API key
            mock_service_config.timeout_seconds = 30
            mock_service_config.max_retries = 3
            mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
            mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
            mock_service_config.headers = {}

            mock_config_loader = Mock()
            mock_config_loader.get_service_config.return_value = mock_service_config

            # Mock ConfigLoader at the correct import path
            with patch('utils.config_loader.ConfigLoader') as mock_loader_class:
                mock_loader_class.return_value = mock_config_loader

                # Act
                service = create_economic_calendar_service("prod")

            # Assert
            assert service is None

    def test_factory_returns_none_on_empty_api_key(self):
        """Test factory returns None when API key is empty string"""
        # Arrange - Clear environment and disable auto env loading
        with patch.dict('os.environ', {}, clear=True):  # Clear all environment variables
            mock_service_config = Mock()
            mock_service_config.name = "economic_calendar"
            mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
            mock_service_config.api_key = ""  # Empty API key
            mock_service_config.timeout_seconds = 30
            mock_service_config.max_retries = 3
            mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
            mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
            mock_service_config.headers = {}

            mock_config_loader = Mock()
            mock_config_loader.get_service_config.return_value = mock_service_config

            # Mock ConfigLoader at the correct import path
            with patch('utils.config_loader.ConfigLoader') as mock_loader_class:
                mock_loader_class.return_value = mock_config_loader

                # Act
                service = create_economic_calendar_service("prod")

            # Assert
            assert service is None

    def test_factory_returns_none_on_whitespace_api_key(self):
        """Test factory returns None when API key is only whitespace"""
        # Arrange - Clear environment and disable auto env loading
        with patch.dict('os.environ', {}, clear=True):  # Clear all environment variables
            mock_service_config = Mock()
            mock_service_config.name = "economic_calendar"
            mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
            mock_service_config.api_key = "   "  # Whitespace-only API key
            mock_service_config.timeout_seconds = 30
            mock_service_config.max_retries = 3
            mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
            mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
            mock_service_config.headers = {}

            mock_config_loader = Mock()
            mock_config_loader.get_service_config.return_value = mock_service_config

            # Mock ConfigLoader at the correct import path
            with patch('utils.config_loader.ConfigLoader') as mock_loader_class:
                mock_loader_class.return_value = mock_config_loader

                # Act
                service = create_economic_calendar_service("prod")

            # Assert
            assert service is None


class TestServiceFactoryConfigurationHandling:
    """Test service factory configuration loading and error handling"""

    def test_factory_handles_configuration_loading_errors(self):
        """Test factory handles configuration loading errors gracefully"""
        # Arrange
        mock_config_loader = Mock()
        mock_config_loader.get_service_config.side_effect = Exception("Config loading failed")

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is None

    def test_factory_handles_missing_config_file(self):
        """Test factory handles missing configuration file"""
        # Arrange
        mock_config_loader = Mock()
        mock_config_loader.get_service_config.side_effect = FileNotFoundError("Config file not found")

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is None

    def test_factory_handles_invalid_config_format(self):
        """Test factory handles invalid configuration format"""
        # Arrange
        mock_config_loader = Mock()
        mock_config_loader.get_service_config.side_effect = KeyError("Missing required config key")

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is None

    def test_factory_validates_configuration_format(self, test_environment_variables):
        """Test factory validates that configuration has proper format"""
        # Arrange - Missing required configuration fields
        incomplete_config = Mock()
        incomplete_config.name = "economic_calendar"
        # Missing other required fields like base_url, etc.

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = incomplete_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

            # Assert - Factory should return None on invalid configuration
            assert service is None


class TestServiceFactoryEnvironmentHandling:
    """Test service factory environment parameter handling"""

    def test_factory_handles_different_environments(self, test_environment_variables):
        """Test factory works with different environment parameters"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
        mock_service_config.api_key = "test_key"
        mock_service_config.timeout_seconds = 30
        mock_service_config.max_retries = 3
        mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
        mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
        mock_service_config.headers = {}

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        environments = ["dev", "test", "prod"]

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            for env in environments:
                # Act
                service = create_economic_calendar_service(env)

                # Assert
                assert service is not None
                # Verify that config loader was called with correct environment
                mock_config_loader.get_service_config.assert_called_with("economic_calendar", env)

    def test_factory_defaults_to_prod_environment(self, test_environment_variables):
        """Test factory defaults to 'prod' environment when not specified"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
        mock_service_config.api_key = "test_key"
        mock_service_config.timeout_seconds = 30
        mock_service_config.max_retries = 3
        mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
        mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
        mock_service_config.headers = {}

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service()  # No environment specified

        # Assert
        assert service is not None
        mock_config_loader.get_service_config.assert_called_with("economic_calendar", "prod")


class TestServiceFactoryInstanceValidation:
    """Test service factory creates properly configured service instances"""

    def test_factory_creates_proper_service_instance(self, test_environment_variables):
        """Test factory creates service instance with proper configuration"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
        mock_service_config.api_key = "valid_test_key"
        mock_service_config.timeout_seconds = 45
        mock_service_config.max_retries = 2
        mock_service_config.cache = {
            "enabled": True,
            "ttl_seconds": 1800,
            "cache_dir": "/tmp/test_cache",
            "max_size_mb": 50
        }
        mock_service_config.rate_limit = {
            "enabled": True,
            "requests_per_minute": 100,
            "burst_limit": 20
        }
        mock_service_config.headers = {"Accept": "application/json", "User-Agent": "Test"}

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("dev")

        # Assert
        assert service is not None
        assert service.config.name == "economic_calendar"
        assert service.config.base_url == "https://api.stlouisfed.org/fred/series"
        assert service.config.api_key == "valid_test_key"
        assert service.config.timeout_seconds == 45
        assert service.config.max_retries == 2

    def test_factory_creates_service_with_proper_historical_storage_config(self, test_environment_variables):
        """Test factory creates service with proper historical storage configuration"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
        mock_service_config.api_key = "test_key"
        mock_service_config.timeout_seconds = 30
        mock_service_config.max_retries = 3
        mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
        mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
        mock_service_config.headers = {}

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("dev")

        # Assert
        assert service is not None
        assert hasattr(service.config, 'historical_storage')
        assert service.config.historical_storage.enabled is False  # Economic calendar doesn't store historical data
        assert service.config.historical_storage.store_stock_prices is False
        assert service.config.historical_storage.store_financials is False


class TestServiceFactoryErrorMessages:
    """Test service factory error message handling"""

    @patch('builtins.print')  # Mock print to capture error messages
    def test_factory_prints_helpful_error_for_missing_api_key(self, mock_print):
        """Test factory prints helpful error message for missing API key"""
        # Arrange
        mock_service_config = Mock()
        mock_service_config.name = "economic_calendar"
        mock_service_config.api_key = None

        mock_config_loader = Mock()
        mock_config_loader.get_service_config.return_value = mock_service_config

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is None
        mock_print.assert_called()

        # Check that error message was printed
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        assert any("Failed to create economic calendar service" in msg for msg in printed_messages)

    @patch('builtins.print')
    def test_factory_prints_helpful_error_for_config_loading_failure(self, mock_print):
        """Test factory prints helpful error message for configuration loading failure"""
        # Arrange
        mock_config_loader = Mock()
        mock_config_loader.get_service_config.side_effect = FileNotFoundError("Config file missing")

        with patch('utils.config_loader.ConfigLoader', return_value=mock_config_loader):
            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is None
        mock_print.assert_called()

        # Check that error message contains helpful information
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        assert any("Failed to create economic calendar service" in msg for msg in printed_messages)
        assert any("Config file missing" in msg for msg in printed_messages)


@pytest.mark.unit
class TestServiceFactoryIntegration:
    """Test service factory integration with other components"""

    def test_factory_integrates_with_real_config_structure(self):
        """Test factory works with realistic configuration structure"""
        # Arrange - This mimics the actual config structure from financial_services.yaml
        realistic_config = {
            "services": {
                "economic_calendar": {
                    "name": "economic_calendar",
                    "base_url": "https://api.stlouisfed.org/fred/series",
                    "api_key": "${FRED_API_KEY}",
                    "rate_limit": {"requests_per_minute": 120},
                    "cache": {"ttl_seconds": 900},
                    "headers": {"Accept": "application/json"},
                    "timeout_seconds": 30,
                    "historical_storage": {
                        "enabled": False,
                        "store_stock_prices": False,
                        "store_financials": False,
                        "store_fundamentals": False,
                        "store_news_sentiment": False,
                        "auto_detect_data_type": False,
                        "auto_collection_enabled": False
                    }
                }
            }
        }

        # Mock the config loading to return realistic structure
        with patch('utils.config_loader.ConfigLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_service_config = Mock()
            mock_service_config.name = "economic_calendar"
            mock_service_config.base_url = "https://api.stlouisfed.org/fred/series"
            mock_service_config.api_key = "valid_fred_key"
            mock_service_config.timeout_seconds = 30
            mock_service_config.max_retries = 3
            mock_service_config.cache = {"enabled": True, "ttl_seconds": 900}
            mock_service_config.rate_limit = {"enabled": True, "requests_per_minute": 120}
            mock_service_config.headers = {"Accept": "application/json"}

            mock_loader.get_service_config.return_value = mock_service_config
            mock_loader_class.return_value = mock_loader

            # Act
            service = create_economic_calendar_service("prod")

        # Assert
        assert service is not None
        mock_loader.get_service_config.assert_called_once_with("economic_calendar", "prod")
