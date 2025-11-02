#!/usr/bin/env python3
"""
Type-Safe Result Structures

Structured result types to replace Dict[str, Any] usage:
- Type-safe processing results
- Validation results with structured data
- Template selection results
- Error handling results
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from errors import TwitterSystemError


@dataclass
class ProcessingResult:
    """Type-safe processing result"""

    success: bool
    operation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Content results
    content: str | None = None
    output_path: Path | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Validation results
    validation_score: float | None = None
    validation_issues: list[str] = field(default_factory=list)

    # Error information
    error: str | None = None
    error_context: dict[str, Any] = field(default_factory=dict)

    # Performance metrics
    processing_time: float | None = None

    def is_successful(self) -> bool:
        """Check if processing was successful"""
        return self.success and self.error is None

    def meets_quality_threshold(self, threshold: float = 8.5) -> bool:
        """Check if result meets quality threshold"""
        return self.validation_score is not None and self.validation_score >= threshold

    def add_metadata(self, key: str, value: Any) -> "ProcessingResult":
        """Add metadata to result"""
        self.metadata[key] = value
        return self

    def add_error_context(self, key: str, value: Any) -> "ProcessingResult":
        """Add error context to result"""
        self.error_context[key] = value
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "content": self.content,
            "output_path": str(self.output_path) if self.output_path else None,
            "metadata": self.metadata,
            "validation_score": self.validation_score,
            "validation_issues": self.validation_issues,
            "error": self.error,
            "error_context": self.error_context,
            "processing_time": self.processing_time,
        }


@dataclass
class ValidationResult:
    """Type-safe validation result"""

    content_type: str
    identifier: str
    overall_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Validation breakdown
    validation_scores: dict[str, float] = field(default_factory=dict)
    validation_issues: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)

    # Quality assessment
    quality_grade: str = "F"
    compliance_status: str = "NON_COMPLIANT"
    ready_for_publication: bool = False

    # Recommendations
    required_corrections: list[str] = field(default_factory=list)
    optimization_opportunities: list[str] = field(default_factory=list)

    # Validation metadata
    validation_framework: str = "unified_validation_v1.0"
    validation_criteria: dict[str, Any] = field(default_factory=dict)

    def is_compliant(self) -> bool:
        """Check if content is compliant"""
        return self.compliance_status == "COMPLIANT"

    def has_critical_issues(self) -> bool:
        """Check if there are critical issues"""
        return len(self.required_corrections) > 0

    def get_score_summary(self) -> dict[str, Any]:
        """Get summary of validation scores"""
        return {
            "overall_score": self.overall_score,
            "detailed_scores": self.validation_scores,
            "quality_grade": self.quality_grade,
            "compliance_status": self.compliance_status,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "content_type": self.content_type,
            "identifier": self.identifier,
            "overall_score": self.overall_score,
            "timestamp": self.timestamp,
            "validation_scores": self.validation_scores,
            "validation_issues": self.validation_issues,
            "validation_warnings": self.validation_warnings,
            "quality_grade": self.quality_grade,
            "compliance_status": self.compliance_status,
            "ready_for_publication": self.ready_for_publication,
            "required_corrections": self.required_corrections,
            "optimization_opportunities": self.optimization_opportunities,
            "validation_framework": self.validation_framework,
            "validation_criteria": self.validation_criteria,
        }


@dataclass
class TemplateSelectionResult:
    """Type-safe template selection result"""

    content_type: str
    identifier: str
    selected_template: str
    selection_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Selection details
    all_scores: dict[str, float] = field(default_factory=dict)
    selection_reason: str = "Template selected based on scoring algorithm"
    selection_confidence: float = 0.0

    # Template metadata
    template_variant: str | None = None
    template_path: Path | None = None

    # Data context
    data_completeness: float = 0.0
    required_indicators: list[str] = field(default_factory=list)
    available_indicators: list[str] = field(default_factory=list)

    def get_second_best(self) -> str | None:
        """Get second-best template option"""
        if len(self.all_scores) < 2:
            return None

        sorted_scores = sorted(self.all_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[1][0] if len(sorted_scores) > 1 else None

    def get_selection_margin(self) -> float:
        """Get margin between selected and second-best template"""
        second_best = self.get_second_best()
        if second_best is None:
            return 0.0

        return self.selection_score - self.all_scores[second_best]

    def is_confident_selection(self, threshold: float = 0.1) -> bool:
        """Check if selection is confident based on margin"""
        return self.get_selection_margin() >= threshold

    def get_confidence_score(self) -> float:
        """Get confidence score for the selection"""
        return self.selection_confidence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "content_type": self.content_type,
            "identifier": self.identifier,
            "selected_template": self.selected_template,
            "selection_score": self.selection_score,
            "timestamp": self.timestamp,
            "all_scores": self.all_scores,
            "selection_reason": self.selection_reason,
            "selection_confidence": self.selection_confidence,
            "template_variant": self.template_variant,
            "template_path": str(self.template_path) if self.template_path else None,
            "data_completeness": self.data_completeness,
            "required_indicators": self.required_indicators,
            "available_indicators": self.available_indicators,
        }


@dataclass
class ErrorResult:
    """Type-safe error result"""

    error_type: str
    error_message: str
    operation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Error context
    error_context: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None

    # Recovery information
    recoverable: bool = False
    recovery_suggestions: list[str] = field(default_factory=list)

    # Source information
    source_file: str | None = None
    source_line: int | None = None

    @classmethod
    def from_exception(cls, error: Exception, operation: str, context: dict[str, Any] | None = None) -> "ErrorResult":
        """Create ErrorResult from exception"""

        error_context = context or {}

        # Add exception-specific context
        if isinstance(error, TwitterSystemError):
            error_context.update(error.context)
            error_code = error.error_code
        else:
            error_code = type(error).__name__

        return cls(
            error_type=type(error).__name__,
            error_message=str(error),
            operation=operation,
            error_context=error_context,
            error_code=error_code,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "error_context": self.error_context,
            "error_code": self.error_code,
            "recoverable": self.recoverable,
            "recovery_suggestions": self.recovery_suggestions,
            "source_file": self.source_file,
            "source_line": self.source_line,
        }


@dataclass
class DataLoadResult:
    """Type-safe data loading result"""

    success: bool
    data_type: str
    source_path: Path
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Data information
    data: dict[str, Any] = field(default_factory=dict)
    record_count: int | None = None
    data_size: int | None = None

    # Validation information
    schema_valid: bool = True
    missing_fields: list[str] = field(default_factory=list)
    invalid_fields: list[str] = field(default_factory=list)

    # Processing metrics
    load_time: float | None = None

    # Error information
    error: str | None = None
    error_context: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if data is valid"""
        return self.success and self.schema_valid and len(self.missing_fields) == 0

    def has_required_fields(self, required_fields: list[str]) -> bool:
        """Check if data has all required fields"""
        return all(field in self.data for field in required_fields)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "data_type": self.data_type,
            "source_path": str(self.source_path),
            "timestamp": self.timestamp,
            "data": self.data,
            "record_count": self.record_count,
            "data_size": self.data_size,
            "schema_valid": self.schema_valid,
            "missing_fields": self.missing_fields,
            "invalid_fields": self.invalid_fields,
            "load_time": self.load_time,
            "error": self.error,
            "error_context": self.error_context,
        }


# Convenience functions for creating results
def success_result(
    operation: str,
    content: str | None = None,
    output_path: Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> ProcessingResult:
    """Create successful processing result"""

    return ProcessingResult(
        success=True,
        operation=operation,
        content=content,
        output_path=output_path,
        metadata=metadata or {},
    )


def error_result(
    operation: str,
    error: str | Exception,
    error_context: dict[str, Any] | None = None,
) -> ProcessingResult:
    """Create error processing result"""

    error_message = str(error)
    context = error_context or {}

    if isinstance(error, Exception):
        context["error_type"] = type(error).__name__

    return ProcessingResult(success=False, operation=operation, error=error_message, error_context=context)


def validation_success(content_type: str, identifier: str, score: float, quality_grade: str = "A") -> ValidationResult:
    """Create successful validation result"""

    return ValidationResult(
        content_type=content_type,
        identifier=identifier,
        overall_score=score,
        quality_grade=quality_grade,
        compliance_status="COMPLIANT",
        ready_for_publication=True,
    )


def validation_failure(
    content_type: str,
    identifier: str,
    score: float,
    issues: list[str],
    corrections: list[str],
) -> ValidationResult:
    """Create failed validation result"""

    return ValidationResult(
        content_type=content_type,
        identifier=identifier,
        overall_score=score,
        validation_issues=issues,
        required_corrections=corrections,
        quality_grade="F",
        compliance_status="NON_COMPLIANT",
        ready_for_publication=False,
    )
