#!/usr/bin/env python3
"""
Error Handler

Centralized error handling with fail-fast approach:
- Structured error handling with context
- Fail-fast validation with meaningful messages
- Standardized file I/O error handling
- Error recovery strategies
"""

import json
import traceback
from pathlib import Path
from typing import Any

from errors import (
    ConfigurationError,
    DataError,
    ProcessingError,
    TemplateError,
    TwitterSystemError,
    TypeValidationError,
    data_file_not_found,
    invalid_data_format,
    missing_required_field,
    template_not_found,
    validation_failed,
)


class ErrorHandler:
    """Centralized error handling with fail-fast approach"""

    def __init__(self, logger: Any | None = None):
        """Initialize error handler with optional logger"""
        self.logger = logger
        self.error_count = 0
        self.error_history: list[dict[str, Any]] = []

    def handle_file_error(
        self,
        path: str | Path,
        operation: str,
        error: Exception,
        fail_fast: bool = True,
    ) -> None:
        """Handle file operation errors with fail-fast approach"""

        path_obj = Path(path)

        if isinstance(error, FileNotFoundError):
            data_error = data_file_not_found(path_obj, operation)
        elif isinstance(error, PermissionError):
            data_error = DataError(
                message=f"Permission denied accessing {path_obj}",
                source_path=path_obj,
                operation=operation,
                context={"permissions": (oct(path_obj.stat().st_mode) if path_obj.exists() else "unknown")},
            )
        elif isinstance(error, IsADirectoryError):
            data_error = DataError(
                message=f"Expected file but found directory: {path_obj}",
                source_path=path_obj,
                operation=operation,
                context={"is_directory": True},
            )
        else:
            data_error = DataError(
                message=f"File operation failed: {str(error)}",
                source_path=path_obj,
                operation=operation,
                context={"original_error": str(error)},
            )

        self._record_error(data_error)

        if fail_fast:
            raise data_error

        return data_error

    def handle_validation_error(
        self,
        content_type: str,
        validation_result: dict[str, Any],
        fail_fast: bool = True,
    ) -> None:
        """Handle validation errors with fail-fast approach"""

        score = validation_result.get("overall_score", 0.0)
        issues = validation_result.get("issues", [])
        failed_criteria = validation_result.get("failed_criteria", [])

        if score < 8.5:  # Below publication threshold
            validation_error = validation_failed(
                message=f"Content quality below threshold: {score:.1f}/10.0",
                content_type=content_type,
                score=score,
                criteria=failed_criteria,
            )
            validation_error.add_context("issues", issues)
            validation_error.add_context("threshold", 8.5)

            self._record_error(validation_error)

            if fail_fast:
                raise validation_error

            return validation_error

    def handle_template_error(
        self,
        template_name: str,
        data_context: dict[str, Any],
        error: Exception,
        fail_fast: bool = True,
    ) -> None:
        """Handle template processing errors with fail-fast approach"""

        if "not found" in str(error).lower():
            template_error = template_not_found(template_name, data_context.get("content_type", "unknown"))
        else:
            template_error = TemplateError(
                message=f"Template processing failed: {str(error)}",
                template_name=template_name,
                data_context=data_context,
                context={"original_error": str(error)},
            )

        self._record_error(template_error)

        if fail_fast:
            raise template_error

        return template_error

    def handle_data_validation_error(
        self,
        data: dict[str, Any],
        expected_fields: list[str],
        data_type: str,
        fail_fast: bool = True,
    ) -> None:
        """Handle data validation errors with fail-fast approach"""

        missing_fields = [field for field in expected_fields if field not in data or data[field] is None]

        if missing_fields:
            for field in missing_fields:
                field_error = missing_required_field(field, data_type)
                field_error.add_context("available_fields", list(data.keys()))
                field_error.add_context("missing_fields", missing_fields)

                self._record_error(field_error)

                if fail_fast:
                    raise field_error

            return field_error

    def handle_type_validation_error(
        self, value: Any, expected_type: type, field_name: str, fail_fast: bool = True
    ) -> None:
        """Handle type validation errors with fail-fast approach"""

        type_error = TypeValidationError(
            message=f"Invalid type for field '{field_name}': expected {expected_type.__name__}, got {type(value).__name__}",
            expected_type=expected_type.__name__,
            actual_type=type(value).__name__,
            field_name=field_name,
            context={"value": str(value)[:100]},  # Truncate long values
        )

        self._record_error(type_error)

        if fail_fast:
            raise type_error

        return type_error

    def handle_processing_error(
        self,
        stage: str,
        input_data: dict[str, Any],
        error: Exception,
        fail_fast: bool = True,
    ) -> None:
        """Handle processing pipeline errors with fail-fast approach"""

        processing_error = ProcessingError(
            message=f"Processing failed at stage '{stage}': {str(error)}",
            pipeline_stage=stage,
            input_data=input_data,
            context={"original_error": str(error), "traceback": traceback.format_exc()},
        )

        self._record_error(processing_error)

        if fail_fast:
            raise processing_error

        return processing_error

    def validate_file_format(self, file_path: Path, expected_format: str, fail_fast: bool = True) -> None:
        """Validate file format with fail-fast approach"""

        if not file_path.exists():
            error = data_file_not_found(file_path, "format_validation")
            self._record_error(error)
            if fail_fast:
                raise error
            return error

        actual_format = file_path.suffix.lower()

        if expected_format.lower() != actual_format:
            error = invalid_data_format(file_path, expected_format, actual_format)
            self._record_error(error)
            if fail_fast:
                raise error
            return error

    def validate_required_paths(self, paths: dict[str, Path], fail_fast: bool = True) -> None:
        """Validate required paths exist with fail-fast approach"""

        missing_paths = []
        for name, path in paths.items():
            if not path.exists():
                missing_paths.append(name)

        if missing_paths:
            config_error = ConfigurationError(
                message=f"Missing required paths: {', '.join(missing_paths)}",
                context={
                    "missing_paths": missing_paths,
                    "all_paths": {name: str(path) for name, path in paths.items()},
                },
            )

            self._record_error(config_error)

            if fail_fast:
                raise config_error

            return config_error

    def _record_error(self, error: TwitterSystemError) -> None:
        """Record error in history and log if logger available"""

        self.error_count += 1
        error_dict = error.to_dict()
        error_dict["error_id"] = self.error_count

        self.error_history.append(error_dict)

        if self.logger:
            self.logger.error(f"Error #{self.error_count}: {error.message}", extra=error_dict)

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of all errors encountered"""

        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": self.error_count,
            "error_types": error_types,
            "last_error": self.error_history[-1] if self.error_history else None,
        }

    def clear_error_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0

    def export_error_log(self, output_path: Path) -> None:
        """Export error history to JSON file"""

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error_summary": self.get_error_summary(),
                        "error_history": self.error_history,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            # Don't fail-fast on logging errors
            if self.logger:
                self.logger.warning(f"Failed to export error log: {e}")


# Convenience functions for common error scenarios
def fail_if_missing_file(file_path: Path, operation: str) -> None:
    """Fail fast if file doesn't exist"""
    if not file_path.exists():
        raise data_file_not_found(file_path, operation)


def fail_if_invalid_data(data: dict[str, Any], required_fields: list[str], data_type: str) -> None:
    """Fail fast if data is invalid"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise missing_required_field(missing_fields[0], data_type)


def fail_if_below_threshold(score: float, threshold: float, content_type: str) -> None:
    """Fail fast if score is below threshold"""
    if score < threshold:
        raise validation_failed(
            message=f"Score {score:.1f} below threshold {threshold}",
            content_type=content_type,
            score=score,
            criteria=[f"minimum_score_{threshold}"],
        )
