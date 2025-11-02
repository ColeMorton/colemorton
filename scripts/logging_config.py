#!/usr/bin/env python3
"""
Structured Logging Configuration

Centralized logging system for Twitter content generation:
- Structured logging with contextual information
- Performance monitoring and metrics
- Error tracking and debugging support
- Configurable log levels and outputs
"""

import json
import logging
import logging.config
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class TwitterSystemLogger:
    """Structured logging for Twitter system components"""

    def __init__(
        self,
        name: str = "twitter_system",
        log_level: str = "INFO",
        log_file: Path | None = None,
        structured_output: bool = True,
    ):
        """Initialize structured logger"""
        self.name = name
        self.structured_output = structured_output
        self.logger = self._setup_logger(name, log_level, log_file)
        self.start_time = time.time()

    def _setup_logger(self, name: str, log_level: str, log_file: Path | None) -> logging.Logger:
        """Setup logger with structured formatting"""

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))

        if self.structured_output:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(file_handler)

        return logger

    def log_operation(
        self,
        operation: str,
        context: dict[str, Any],
        level: str = "INFO",
        duration: float | None = None,
    ) -> None:
        """Log operations with structured context"""

        log_data = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "context": context,
        }

        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)

        message = f"Operation: {operation}"
        if duration is not None:
            message += f" (took {duration:.2f}s)"

        self.logger.log(
            getattr(logging, level.upper()),
            message,
            extra={"structured_data": log_data},
        )

    def log_error(self, error: Exception, context: dict[str, Any], operation: str | None = None) -> None:
        """Log errors with full context for debugging"""

        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context,
        }

        if operation:
            log_data["operation"] = operation

        # Add error details if it's a TwitterSystemError
        if hasattr(error, "to_dict"):
            log_data["error_details"] = error.to_dict()

        self.logger.error(f"Error: {str(error)}", extra={"structured_data": log_data})

    def log_validation_result(self, content_type: str, validation_result: dict[str, Any], identifier: str) -> None:
        """Log validation results with metrics"""

        score = validation_result.get("overall_score", 0.0)
        issues = validation_result.get("issues", [])

        log_data = {
            "validation_type": "content_validation",
            "content_type": content_type,
            "identifier": identifier,
            "score": score,
            "issues_count": len(issues),
            "timestamp": datetime.now().isoformat(),
        }

        level = "INFO" if score >= 8.5 else "WARNING" if score >= 7.0 else "ERROR"

        self.log_operation(f"Content validation - {content_type}", log_data, level=level)

    def log_template_selection(
        self,
        content_type: str,
        selected_template: str,
        scores: dict[str, float],
        identifier: str,
    ) -> None:
        """Log template selection with scoring details"""

        log_data = {
            "template_selection": {
                "content_type": content_type,
                "identifier": identifier,
                "selected_template": selected_template,
                "selection_score": scores.get(selected_template, 0.0),
                "all_scores": scores,
                "timestamp": datetime.now().isoformat(),
            }
        }

        self.log_operation(f"Template selection - {content_type}", log_data)

    def log_performance_metrics(self, operation: str, metrics: dict[str, Any], identifier: str | None = None) -> None:
        """Log performance metrics"""

        log_data = {
            "performance_metrics": {
                "operation": operation,
                "identifier": identifier,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        }

        self.log_operation(f"Performance metrics - {operation}", log_data)

    def log_data_processing(
        self,
        data_type: str,
        source_path: str | Path,
        success: bool,
        record_count: int | None = None,
    ) -> None:
        """Log data processing operations"""

        log_data = {
            "data_processing": {
                "data_type": data_type,
                "source_path": str(source_path),
                "success": success,
                "record_count": record_count,
                "timestamp": datetime.now().isoformat(),
            }
        }

        level = "INFO" if success else "ERROR"

        self.log_operation(f"Data processing - {data_type}", log_data, level=level)

    def log_system_startup(self, config: dict[str, Any]) -> None:
        """Log system startup with configuration"""

        log_data = {
            "system_startup": {
                "config": config,
                "timestamp": datetime.now().isoformat(),
                "logger_name": self.name,
            }
        }

        self.log_operation("System startup", log_data)

    def log_system_shutdown(self) -> None:
        """Log system shutdown with runtime metrics"""

        runtime = time.time() - self.start_time

        log_data = {
            "system_shutdown": {
                "runtime_seconds": round(runtime, 2),
                "timestamp": datetime.now().isoformat(),
            }
        }

        self.log_operation("System shutdown", log_data)

    def create_context_logger(self, context: dict[str, Any]) -> "ContextLogger":
        """Create logger with persistent context"""
        return ContextLogger(self, context)

    # Standard logging interface compatibility methods (use simple logging to avoid JSON bloat)
    def info(self, message: str) -> None:
        """Log info message using simple format (no JSON)"""
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """Log debug message using simple format (no JSON)"""
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        """Log warning message using simple format (no JSON)"""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message using simple format (no JSON)"""
        self.logger.error(message)


class ContextLogger:
    """Logger with persistent context for specific operations"""

    def __init__(self, parent_logger: TwitterSystemLogger, context: dict[str, Any]):
        self.parent = parent_logger
        self.base_context = context

    def log_operation(
        self,
        operation: str,
        additional_context: dict[str, Any] | None = None,
        level: str = "INFO",
        duration: float | None = None,
    ) -> None:
        """Log operation with combined context"""

        combined_context = {**self.base_context}
        if additional_context:
            combined_context.update(additional_context)

        self.parent.log_operation(operation, combined_context, level, duration)

    def log_error(
        self,
        error: Exception,
        additional_context: dict[str, Any] | None = None,
        operation: str | None = None,
    ) -> None:
        """Log error with combined context"""

        combined_context = {**self.base_context}
        if additional_context:
            combined_context.update(additional_context)

        self.parent.log_error(error, combined_context, operation)


class StructuredFormatter(logging.Formatter):
    """Formatter for structured logging output"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data"""

        # Base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add structured data if available
        if hasattr(record, "structured_data"):
            log_entry.update(record.structured_data)

        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceTimer:
    """Context manager for timing operations"""

    def __init__(self, logger: TwitterSystemLogger, operation: str, context: dict[str, Any]):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type is not None:
            self.logger.log_error(exc_val, {**self.context, "duration_seconds": duration}, self.operation)
        else:
            self.logger.log_operation(self.operation, self.context, duration=duration)


# Convenience functions for common logging scenarios
def setup_default_logger(log_level: str = "INFO", log_file: Path | None = None) -> TwitterSystemLogger:
    """Setup default logger with standard configuration"""

    return TwitterSystemLogger(
        name="twitter_system",
        log_level=log_level,
        log_file=log_file,
        structured_output=True,
    )


def log_script_execution(logger: TwitterSystemLogger, script_name: str, parameters: dict[str, Any]) -> ContextLogger:
    """Create context logger for script execution"""

    context = {
        "script_name": script_name,
        "parameters": parameters,
        "execution_id": f"{script_name}_{int(time.time())}",
    }

    return logger.create_context_logger(context)
