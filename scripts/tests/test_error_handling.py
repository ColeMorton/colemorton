#!/usr/bin/env python3
"""
Test Suite for Error Handling

Tests for centralized error handling system:
- Error hierarchy and context
- Fail-fast behavior
- Error recovery and logging
- Error serialization and reporting
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest


# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from error_handler import (
    ErrorHandler,
    fail_if_below_threshold,
    fail_if_invalid_data,
    fail_if_missing_file,
)
from errors import (
    ConfigurationError,
    DataError,
    ProcessingError,
    TemplateError,
    TwitterSystemError,
    TypeValidationError,
    ValidationError,
    data_file_not_found,
    invalid_data_format,
    missing_required_field,
    template_not_found,
    validation_failed,
)
from logging_config import TwitterSystemLogger


class TestErrorHierarchy:
    """Test error hierarchy and context"""

    def test_base_error_creation(self):
        """Test TwitterSystemError base functionality"""

        error = TwitterSystemError("Test error", context={"key": "value"}, error_code="TEST_001")

        assert error.message == "Test error"
        assert error.context == {"key": "value"}
        assert error.error_code == "TEST_001"

        # Test context addition
        error.add_context("new_key", "new_value")
        assert error.context["new_key"] == "new_value"

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "TwitterSystemError"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"]["key"] == "value"

    def test_validation_error(self):
        """Test ValidationError with specific context"""

        error = ValidationError(
            "Validation failed",
            content_type="fundamental",
            validation_score=6.5,
            failed_criteria=["disclaimer", "accuracy"],
        )

        assert error.content_type == "fundamental"
        assert error.validation_score == 6.5
        assert len(error.failed_criteria) == 2

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["content_type"] == "fundamental"
        assert error_dict["validation_score"] == 6.5
        assert error_dict["failed_criteria"] == ["disclaimer", "accuracy"]

    def test_template_error(self):
        """Test TemplateError with template context"""

        error = TemplateError(
            "Template rendering failed",
            template_name="A_valuation",
            template_variant="fundamental",
            data_context={"ticker": "AAPL", "price": 150},
        )

        assert error.template_name == "A_valuation"
        assert error.template_variant == "fundamental"
        assert error.data_context["ticker"] == "AAPL"

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["template_name"] == "A_valuation"
        assert "ticker" in error_dict["data_context_keys"]

    def test_data_error(self):
        """Test DataError with file context"""

        error = DataError(
            "File not found",
            source_path=Path("/test/path.json"),
            operation="load_data",
            data_type="fundamental_analysis",
        )

        assert error.source_path == "/test/path.json"
        assert error.operation == "load_data"
        assert error.data_type == "fundamental_analysis"

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["source_path"] == "/test/path.json"
        assert error_dict["operation"] == "load_data"

    def test_configuration_error(self):
        """Test ConfigurationError with config context"""

        error = ConfigurationError(
            "Invalid configuration",
            config_key="validation_threshold",
            config_file=Path("/config/settings.yaml"),
        )

        assert error.config_key == "validation_threshold"
        assert error.config_file == "/config/settings.yaml"

    def test_processing_error(self):
        """Test ProcessingError with pipeline context"""

        error = ProcessingError(
            "Processing failed",
            pipeline_stage="template_rendering",
            input_data={"ticker": "AAPL", "content_type": "fundamental"},
        )

        assert error.pipeline_stage == "template_rendering"
        assert error.input_data["ticker"] == "AAPL"

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["pipeline_stage"] == "template_rendering"
        assert "ticker" in error_dict["input_data_keys"]

    def test_type_validation_error(self):
        """Test TypeValidationError with type context"""

        error = TypeValidationError(
            "Invalid type",
            expected_type="float",
            actual_type="str",
            field_name="validation_score",
        )

        assert error.expected_type == "float"
        assert error.actual_type == "str"
        assert error.field_name == "validation_score"

        # Test serialization
        error_dict = error.to_dict()
        assert error_dict["expected_type"] == "float"
        assert error_dict["actual_type"] == "str"
        assert error_dict["field_name"] == "validation_score"


class TestConvenienceFunctions:
    """Test convenience functions for creating errors"""

    def test_validation_failed_function(self):
        """Test validation_failed convenience function"""

        error = validation_failed("Score too low", "fundamental", 6.5, ["disclaimer", "accuracy"])

        assert isinstance(error, ValidationError)
        assert error.content_type == "fundamental"
        assert error.validation_score == 6.5
        assert "fundamental" in error.message

    def test_template_not_found_function(self):
        """Test template_not_found convenience function"""

        error = template_not_found("A_valuation", "fundamental")

        assert isinstance(error, TemplateError)
        assert error.template_name == "A_valuation"
        assert "fundamental" in error.context["content_type"]

    def test_data_file_not_found_function(self):
        """Test data_file_not_found convenience function"""

        test_path = Path("/test/missing.json")
        error = data_file_not_found(test_path, "load_analysis")

        assert isinstance(error, DataError)
        assert error.source_path == str(test_path)
        assert error.operation == "load_analysis"

    def test_invalid_data_format_function(self):
        """Test invalid_data_format convenience function"""

        test_path = Path("/test/data.txt")
        error = invalid_data_format(test_path, "json", "text")

        assert isinstance(error, DataError)
        assert error.source_path == str(test_path)
        assert "json" in error.context["expected_format"]
        assert "text" in error.context["actual_format"]

    def test_missing_required_field_function(self):
        """Test missing_required_field convenience function"""

        error = missing_required_field("ticker", "fundamental_analysis")

        assert isinstance(error, TypeValidationError)
        assert error.field_name == "ticker"
        assert "fundamental_analysis" in error.context["data_type"]


class TestErrorHandler:
    """Test ErrorHandler centralized error handling"""

    def setup_method(self):
        """Setup error handler for testing"""
        self.error_handler = ErrorHandler()

    def test_file_error_handling(self):
        """Test file error handling"""

        # Test FileNotFoundError
        with pytest.raises(DataError):
            self.error_handler.handle_file_error(
                "/nonexistent/file.json",
                "load_data",
                FileNotFoundError("File not found"),
            )

        # Test PermissionError
        with pytest.raises(DataError):
            self.error_handler.handle_file_error(
                "/restricted/file.json",
                "load_data",
                PermissionError("Permission denied"),
            )

        # Test with fail_fast=False
        error = self.error_handler.handle_file_error(
            "/nonexistent/file.json",
            "load_data",
            FileNotFoundError("File not found"),
            fail_fast=False,
        )

        assert isinstance(error, DataError)
        assert error.operation == "load_data"

    def test_validation_error_handling(self):
        """Test validation error handling"""

        validation_result = {
            "overall_score": 6.5,
            "issues": ["Missing disclaimer", "Invalid formatting"],
            "failed_criteria": ["disclaimer", "formatting"],
        }

        # Test with fail_fast=True
        with pytest.raises(ValidationError):
            self.error_handler.handle_validation_error("fundamental", validation_result)

        # Test with fail_fast=False
        error = self.error_handler.handle_validation_error("fundamental", validation_result, fail_fast=False)

        assert isinstance(error, ValidationError)
        assert error.validation_score == 6.5

    def test_template_error_handling(self):
        """Test template error handling"""

        data_context = {"ticker": "AAPL", "content_type": "fundamental"}

        # Test template not found
        with pytest.raises(TemplateError):
            self.error_handler.handle_template_error(
                "nonexistent_template", data_context, Exception("Template not found")
            )

        # Test other template errors
        with pytest.raises(TemplateError):
            self.error_handler.handle_template_error("A_valuation", data_context, Exception("Rendering failed"))

    def test_data_validation_error_handling(self):
        """Test data validation error handling"""

        incomplete_data = {"ticker": "AAPL"}
        required_fields = ["ticker", "date", "fair_value"]

        # Test with missing fields
        with pytest.raises(TypeValidationError):
            self.error_handler.handle_data_validation_error(incomplete_data, required_fields, "fundamental_analysis")

        # Test with complete data (no error)
        complete_data = {"ticker": "AAPL", "date": "20240101", "fair_value": 185}
        result = self.error_handler.handle_data_validation_error(complete_data, required_fields, "fundamental_analysis")

        assert result is None  # No error expected

    def test_type_validation_error_handling(self):
        """Test type validation error handling"""

        # Test invalid type
        with pytest.raises(TypeValidationError):
            self.error_handler.handle_type_validation_error(
                "150",
                float,
                "validation_score",  # String instead of float
            )

        # Test valid type (no error)
        result = self.error_handler.handle_type_validation_error(8.5, float, "validation_score")

        assert result is None  # No error expected

    def test_processing_error_handling(self):
        """Test processing error handling"""

        input_data = {"ticker": "AAPL", "content_type": "fundamental"}

        with pytest.raises(ProcessingError):
            self.error_handler.handle_processing_error("template_rendering", input_data, Exception("Processing failed"))

    def test_file_format_validation(self):
        """Test file format validation"""

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            # Test wrong format
            with pytest.raises(DataError):
                self.error_handler.validate_file_format(temp_path, ".json")

            # Test correct format
            result = self.error_handler.validate_file_format(temp_path, ".txt")

            assert result is None  # No error expected

        # Clean up
        temp_path.unlink()

        # Test missing file
        with pytest.raises(DataError):
            self.error_handler.validate_file_format(Path("/nonexistent/file.json"), ".json")

    def test_error_history_tracking(self):
        """Test error history tracking"""

        # Generate some errors
        try:
            self.error_handler.handle_file_error(
                "/test/file.json",
                "load_data",
                FileNotFoundError("File not found"),
                fail_fast=False,
            )
        except:
            pass

        try:
            self.error_handler.handle_validation_error(
                "fundamental",
                {"overall_score": 6.5, "issues": ["test"], "failed_criteria": ["test"]},
                fail_fast=False,
            )
        except:
            pass

        # Check error history
        summary = self.error_handler.get_error_summary()
        assert summary["total_errors"] == 2
        assert "DataError" in summary["error_types"]
        assert "ValidationError" in summary["error_types"]

        # Test clearing history
        self.error_handler.clear_error_history()
        summary = self.error_handler.get_error_summary()
        assert summary["total_errors"] == 0

    def test_error_log_export(self):
        """Test error log export"""

        # Generate an error
        try:
            self.error_handler.handle_file_error(
                "/test/file.json",
                "load_data",
                FileNotFoundError("File not found"),
                fail_fast=False,
            )
        except:
            pass

        # Export error log
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            self.error_handler.export_error_log(temp_path)

            # Verify export
            with open(temp_path) as f:
                log_data = json.load(f)

            assert "error_summary" in log_data
            assert "error_history" in log_data
            assert log_data["error_summary"]["total_errors"] == 1

        # Clean up
        temp_path.unlink()


class TestFailFastFunctions:
    """Test fail-fast convenience functions"""

    def test_fail_if_missing_file(self):
        """Test fail_if_missing_file function"""

        # Test with missing file
        with pytest.raises(DataError):
            fail_if_missing_file(Path("/nonexistent/file.json"), "load_data")

        # Test with existing file
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = Path(temp_file.name)
            # Should not raise error
            fail_if_missing_file(temp_path, "load_data")

    def test_fail_if_invalid_data(self):
        """Test fail_if_invalid_data function"""

        # Test with invalid data
        with pytest.raises(TypeValidationError):
            fail_if_invalid_data(
                {"ticker": "AAPL"},
                ["ticker", "date", "fair_value"],
                "fundamental_analysis",
            )

        # Test with valid data
        fail_if_invalid_data(
            {"ticker": "AAPL", "date": "20240101", "fair_value": 185},
            ["ticker", "date", "fair_value"],
            "fundamental_analysis",
        )

    def test_fail_if_below_threshold(self):
        """Test fail_if_below_threshold function"""

        # Test below threshold
        with pytest.raises(ValidationError):
            fail_if_below_threshold(6.5, 8.5, "fundamental")

        # Test above threshold
        fail_if_below_threshold(9.2, 8.5, "fundamental")


class TestErrorHandlerWithLogger:
    """Test ErrorHandler with logger integration"""

    def setup_method(self):
        """Setup error handler with logger"""
        self.logger = TwitterSystemLogger("test_logger")
        self.error_handler = ErrorHandler(self.logger)

    def test_error_logging(self):
        """Test error logging functionality"""

        # Generate an error
        try:
            self.error_handler.handle_file_error(
                "/test/file.json",
                "load_data",
                FileNotFoundError("File not found"),
                fail_fast=False,
            )
        except:
            pass

        # Check that error was logged
        summary = self.error_handler.get_error_summary()
        assert summary["total_errors"] == 1

        # Error should be in history
        assert len(self.error_handler.error_history) == 1
        assert self.error_handler.error_history[0]["error_type"] == "DataError"


class TestErrorRecovery:
    """Test error recovery strategies"""

    def test_graceful_degradation(self):
        """Test graceful degradation on errors"""

        error_handler = ErrorHandler()

        # Test that processing can continue after non-fatal errors
        try:
            error_handler.handle_validation_error(
                "fundamental",
                {
                    "overall_score": 7.5,
                    "issues": ["minor issue"],
                    "failed_criteria": ["minor"],
                },
                fail_fast=False,
            )
        except:
            pass

        # Should be able to continue processing
        summary = error_handler.get_error_summary()
        assert summary["total_errors"] == 1

    def test_error_context_preservation(self):
        """Test that error context is preserved through handling"""

        error_handler = ErrorHandler()

        original_error = ValidationError(
            "Test validation error",
            content_type="fundamental",
            validation_score=6.5,
            failed_criteria=["test"],
        )

        # Add additional context
        original_error.add_context("additional_info", "test_value")

        # Handle the error
        try:
            raise original_error
        except ValidationError as e:
            # Context should be preserved
            assert e.content_type == "fundamental"
            assert e.validation_score == 6.5
            assert e.context["additional_info"] == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
