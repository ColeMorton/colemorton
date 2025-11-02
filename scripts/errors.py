#!/usr/bin/env python3
"""
Centralized Error Handling System

Hierarchical error types with fail-fast approach and contextual information:
- Base exception with structured context
- Specialized exceptions for different error categories
- Fail-fast design with meaningful error messages
"""

from pathlib import Path
from typing import Any


class TwitterSystemError(Exception):
    """Base exception for Twitter system with contextual information"""

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        error_code: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.error_code = error_code or self.__class__.__name__

    def add_context(self, key: str, value: Any) -> "TwitterSystemError":
        """Add contextual information to error"""
        self.context[key] = value
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for structured logging"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


class ValidationError(TwitterSystemError):
    """Validation-specific errors with detailed context"""

    def __init__(
        self,
        message: str,
        content_type: str | None = None,
        validation_score: float | None = None,
        failed_criteria: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.content_type = content_type
        self.validation_score = validation_score
        self.failed_criteria = failed_criteria or []

    def to_dict(self) -> dict[str, Any]:
        """Convert validation error to dictionary"""
        result = super().to_dict()
        result.update(
            {
                "content_type": self.content_type,
                "validation_score": self.validation_score,
                "failed_criteria": self.failed_criteria,
            }
        )
        return result


class TemplateError(TwitterSystemError):
    """Template processing errors with template context"""

    def __init__(
        self,
        message: str,
        template_name: str | None = None,
        template_variant: str | None = None,
        data_context: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.template_name = template_name
        self.template_variant = template_variant
        self.data_context = data_context or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert template error to dictionary"""
        result = super().to_dict()
        result.update(
            {
                "template_name": self.template_name,
                "template_variant": self.template_variant,
                "data_context_keys": (list(self.data_context.keys()) if self.data_context else []),
            }
        )
        return result


class DataError(TwitterSystemError):
    """Data loading/processing errors with source context"""

    def __init__(
        self,
        message: str,
        source_path: str | Path | None = None,
        operation: str | None = None,
        data_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.source_path = str(source_path) if source_path else None
        self.operation = operation
        self.data_type = data_type

    def to_dict(self) -> dict[str, Any]:
        """Convert data error to dictionary"""
        result = super().to_dict()
        result.update(
            {
                "source_path": self.source_path,
                "operation": self.operation,
                "data_type": self.data_type,
            }
        )
        return result


class ConfigurationError(TwitterSystemError):
    """Configuration-related errors"""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_file: str | Path | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.config_key = config_key
        self.config_file = str(config_file) if config_file else None

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration error to dictionary"""
        result = super().to_dict()
        result.update({"config_key": self.config_key, "config_file": self.config_file})
        return result


class ProcessingError(TwitterSystemError):
    """Processing pipeline errors"""

    def __init__(
        self,
        message: str,
        pipeline_stage: str | None = None,
        input_data: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.pipeline_stage = pipeline_stage
        self.input_data = input_data or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert processing error to dictionary"""
        result = super().to_dict()
        result.update(
            {
                "pipeline_stage": self.pipeline_stage,
                "input_data_keys": (list(self.input_data.keys()) if self.input_data else []),
            }
        )
        return result


class TypeValidationError(TwitterSystemError):
    """Type validation errors with type context"""

    def __init__(
        self,
        message: str,
        expected_type: str | None = None,
        actual_type: str | None = None,
        field_name: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, context)
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.field_name = field_name

    def to_dict(self) -> dict[str, Any]:
        """Convert type validation error to dictionary"""
        result = super().to_dict()
        result.update(
            {
                "expected_type": self.expected_type,
                "actual_type": self.actual_type,
                "field_name": self.field_name,
            }
        )
        return result


# Convenience functions for creating specific errors
def validation_failed(message: str, content_type: str, score: float, criteria: list[str]) -> ValidationError:
    """Create validation error with fail-fast context"""
    return ValidationError(
        message=f"Validation failed for {content_type}: {message}",
        content_type=content_type,
        validation_score=score,
        failed_criteria=criteria,
    )


def template_not_found(template_name: str, content_type: str) -> TemplateError:
    """Create template not found error"""
    return TemplateError(
        message=f"Template '{template_name}' not found for content type '{content_type}'",
        template_name=template_name,
        context={"content_type": content_type},
    )


def data_file_not_found(file_path: Path, operation: str) -> DataError:
    """Create data file not found error"""
    return DataError(
        message=f"Data file not found: {file_path}",
        source_path=file_path,
        operation=operation,
        context={"file_exists": file_path.exists()},
    )


def invalid_data_format(file_path: Path, expected_format: str, actual_format: str) -> DataError:
    """Create invalid data format error"""
    return DataError(
        message=f"Invalid data format in {file_path}: expected {expected_format}, got {actual_format}",
        source_path=file_path,
        operation="format_validation",
        context={"expected_format": expected_format, "actual_format": actual_format},
    )


def missing_required_field(field_name: str, data_type: str) -> TypeValidationError:
    """Create missing required field error"""
    return TypeValidationError(
        message=f"Missing required field '{field_name}' in {data_type}",
        field_name=field_name,
        context={"data_type": data_type},
    )
