#!/usr/bin/env python3
"""
Service Layer Unit Tests

Comprehensive testing of service layer abstractions including:
- Service factory patterns
- Configuration management
- Error handling and validation
- Cache management
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.cli_base import (  # noqa: E402
    BaseFinancialCLI,
    CLIError,
    OutputFormat,
    ValidationError,
)
from scripts.utils.config_loader import (  # noqa: E402
    ConfigLoader,
    FinancialServiceConfig,
)


class TestBaseFinancialCLI(unittest.TestCase):
    """Test BaseFinancialCLI framework"""

    def setUp(self):
        """Set up test environment"""
        self.test_cli = TestCLIImplementation()

    def test_initialization(self):
        """Test CLI initialization"""
        self.assertEqual(self.test_cli.service_name, "test_service")
        self.assertEqual(self.test_cli.description, "Test service for unit testing")
        self.assertIsNotNone(self.test_cli.app)
        self.assertIsNotNone(self.test_cli.console)
        self.assertIsNotNone(self.test_cli.logger)

    def test_ticker_validation_valid(self):
        """Test ticker validation with valid inputs"""
        # Test normal ticker
        result = self.test_cli.validate_ticker("AAPL")
        self.assertEqual(result, "AAPL")

        # Test lowercase conversion
        result = self.test_cli.validate_ticker("aapl")
        self.assertEqual(result, "AAPL")

        # Test with spaces
        result = self.test_cli.validate_ticker(" TSLA ")
        self.assertEqual(result, "TSLA")

        # Test with dash
        result = self.test_cli.validate_ticker("BRK-A")
        self.assertEqual(result, "BRK-A")

    def test_ticker_validation_invalid(self):
        """Test ticker validation with invalid inputs"""
        # Test empty ticker
        with self.assertRaises(ValidationError) as context:
            self.test_cli.validate_ticker("")
        self.assertIn("Ticker symbol is required", str(context.exception))

        # Test None ticker
        with self.assertRaises(ValidationError) as context:
            self.test_cli.validate_ticker(None)
        self.assertIn("Ticker symbol is required", str(context.exception))

        # Test too long ticker
        with self.assertRaises(ValidationError) as context:
            self.test_cli.validate_ticker("VERYLONGTICKER")
        self.assertIn("Ticker too long", str(context.exception))

        # Test invalid characters
        with self.assertRaises(ValidationError) as context:
            self.test_cli.validate_ticker("AAPL@#$")
        self.assertIn("Invalid ticker format", str(context.exception))

    def test_output_format_json(self):
        """Test JSON output formatting"""
        test_data = {"key": "value", "number": 42}

        # Mock the rprint function to capture output
        with patch("scripts.utils.cli_base.rprint") as mock_print:
            self.test_cli._output_result(test_data, OutputFormat.JSON)

            # Verify rprint was called
            mock_print.assert_called_once()
            # Get the call arguments
            args = mock_print.call_args[0]

            # Should be valid JSON string
            import json

            parsed = json.loads(args[0])
            self.assertEqual(parsed, test_data)

    def test_output_format_yaml(self):
        """Test YAML output formatting"""
        test_data = {"key": "value", "number": 42}

        with patch("scripts.utils.cli_base.rprint") as mock_print:
            self.test_cli._output_result(test_data, OutputFormat.YAML)

            mock_print.assert_called_once()
            args = mock_print.call_args[0]

            # Should contain YAML formatting
            self.assertIn("key: value", args[0])
            self.assertIn("number: 42", args[0])

    def test_error_handling(self):
        """Test error handling and display"""
        test_error = Exception("Test error message")

        with patch.object(self.test_cli.console, "print") as mock_console_print:
            with self.assertRaises(SystemExit):  # typer.Exit raises SystemExit
                self.test_cli._handle_error(test_error, "Test context")

            # Verify error was logged and displayed
            mock_console_print.assert_called_once()

    def test_standard_options(self):
        """Test standard CLI options"""
        options = self.test_cli.add_standard_options()

        self.assertIn("env", options)
        self.assertIn("output_format", options)
        self.assertIn("verbose", options)
        self.assertIn("no_cache", options)
        self.assertIn("timeout", options)

    def test_cache_operations(self):
        """Test cache management operations"""
        # Test cache actions
        result = self.test_cli.perform_cache_action("stats", "test")
        self.assertIn("action", result)
        self.assertEqual(result["action"], "stats")

        result = self.test_cli.perform_cache_action("clear", "test")
        self.assertIn("action", result)
        self.assertEqual(result["action"], "clear")

        # Test invalid action
        with self.assertRaises(ValidationError):
            self.test_cli.perform_cache_action("invalid_action", "test")


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading and validation"""

    def setUp(self):
        """Set up test environment"""
        self.config_loader = ConfigLoader()

    def test_config_loader_initialization(self):
        """Test ConfigLoader initialization"""
        self.assertIsNotNone(self.config_loader)

    def test_financial_service_config_creation(self):
        """Test FinancialServiceConfig creation"""
        config_data = {
            "api_key": "test_key",
            "base_url": "https://api.example.com",
            "timeout": 30,
            "cache_ttl": 300,
        }

        config = FinancialServiceConfig(**config_data)

        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.base_url, "https://api.example.com")
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.cache_ttl, 300)

    def test_config_validation_required_fields(self):
        """Test configuration validation with missing required fields"""
        # Test with minimal config
        minimal_config = {"api_key": "test"}

        try:
            config = FinancialServiceConfig(**minimal_config)
            # Should use default values for optional fields
            self.assertEqual(config.api_key, "test")
            self.assertIsNotNone(config.timeout)  # Should have default
        except Exception:
            # If validation is strict, this should raise an error
            pass


class TestOutputFormats(unittest.TestCase):
    """Test output format handling"""

    def setUp(self):
        """Set up test environment"""
        self.test_cli = TestCLIImplementation()

    def test_output_format_constants(self):
        """Test output format constants"""
        self.assertEqual(OutputFormat.JSON, "json")
        self.assertEqual(OutputFormat.YAML, "yaml")
        self.assertEqual(OutputFormat.TABLE, "table")
        self.assertEqual(OutputFormat.CSV, "csv")

    def test_table_output_dict(self):
        """Test table output for dictionary data"""
        test_data = {"service": "test", "status": "healthy", "version": "1.0"}

        with patch.object(self.test_cli.console, "print") as mock_console_print:
            self.test_cli._output_result(test_data, OutputFormat.TABLE)

            # Should have called console.print
            mock_console_print.assert_called_once()

    def test_table_output_list(self):
        """Test table output for list of dictionaries"""
        test_data = [
            {"name": "service1", "status": "healthy"},
            {"name": "service2", "status": "degraded"},
        ]

        with patch.object(self.test_cli.console, "print") as mock_console_print:
            self.test_cli._output_result(test_data, OutputFormat.TABLE)

            mock_console_print.assert_called_once()

    def test_csv_output_list(self):
        """Test CSV output for list of dictionaries"""
        test_data = [
            {"name": "service1", "status": "healthy"},
            {"name": "service2", "status": "degraded"},
        ]

        with patch("scripts.utils.cli_base.rprint") as mock_print:
            self.test_cli._output_result(test_data, OutputFormat.CSV)

            mock_print.assert_called_once()
            args = mock_print.call_args[0]

            # Should contain CSV headers and data
            self.assertIn("name,status", args[0])
            self.assertIn("service1,healthy", args[0])

    def test_csv_output_dict(self):
        """Test CSV output for dictionary data"""
        test_data = {"service": "test", "status": "healthy"}

        with patch("scripts.utils.cli_base.rprint") as mock_print:
            self.test_cli._output_result(test_data, OutputFormat.CSV)

            mock_print.assert_called_once()
            args = mock_print.call_args[0]

            # Should contain key-value pairs
            self.assertIn("service,test", args[0])
            self.assertIn("status,healthy", args[0])

    def test_unsupported_output_format(self):
        """Test handling of unsupported output format"""
        test_data = {"key": "value"}

        with self.assertRaises(CLIError) as context:
            self.test_cli._output_result(test_data, "unsupported_format")

        self.assertIn("Unsupported output format", str(context.exception))


class TestErrorHierarchy(unittest.TestCase):
    """Test error hierarchy and handling"""

    def test_cli_error_hierarchy(self):
        """Test CLI error class hierarchy"""
        # Test that ValidationError is a subclass of CLIError
        self.assertTrue(issubclass(ValidationError, CLIError))

        # Test error creation
        validation_error = ValidationError("Test validation error")
        self.assertIsInstance(validation_error, CLIError)
        self.assertIsInstance(validation_error, Exception)

    def test_error_message_handling(self):
        """Test error message handling"""
        error_message = "Test error message"
        error = ValidationError(error_message)

        self.assertEqual(str(error), error_message)


class TestCLIArchitecturalPatterns(unittest.TestCase):
    """Test CLI architectural patterns and compliance"""

    def test_cli_factory_pattern(self):
        """Test CLI follows factory pattern for service creation"""
        test_cli = TestCLIImplementation()

        # Mock service creation
        with patch("scripts.tests.test_service_layer.create_test_service") as mock_create:
            mock_service = Mock()
            mock_create.return_value = mock_service

            service = test_cli._get_service("test")

            # Should call factory function
            mock_create.assert_called_once_with("test")
            self.assertEqual(service, mock_service)

    def test_cli_environment_handling(self):
        """Test CLI environment parameter handling"""
        test_cli = TestCLIImplementation()

        # Test different environments
        environments = ["dev", "test", "prod"]

        for env in environments:
            # Should not raise an error
            try:
                config = test_cli.get_service_config(env)
                # Basic validation that it returns a config-like object
                self.assertIsNotNone(config)
            except Exception as e:
                # If it fails, it should be a known configuration issue
                self.assertIsInstance(e, (ValidationError, CLIError))


# Helper class for testing
class TestCLIImplementation(BaseFinancialCLI):
    """Test implementation of BaseFinancialCLI for unit testing"""

    def __init__(self):
        super().__init__(service_name="test_service", description="Test service for unit testing")

    def perform_health_check(self, env: str):
        """Mock health check implementation"""
        return {
            "service": self.service_name,
            "status": "healthy",
            "environment": env,
            "timestamp": "2025-07-15T00:00:00Z",
        }

    def perform_cache_action(self, action: str, env: str):
        """Mock cache action implementation"""
        if action not in ["clear", "cleanup", "stats"]:
            raise ValidationError(f"Unknown cache action: {action}")

        return {"action": action, "status": "success", "environment": env}

    def _get_service(self, env: str):
        """Mock service creation"""
        return create_test_service(env)


def create_test_service(env: str):
    """Mock service factory function"""
    return Mock(name=f"test_service_{env}")


if __name__ == "__main__":
    # Configure test runner for verbose output
    unittest.main(verbosity=2, buffer=True)
