#!/usr/bin/env python3
"""
Configuration validation utilities for dashboard generation.

This module provides comprehensive validation for dashboard configuration files
to ensure proper setup and catch configuration errors early.
"""

import logging
import re
from pathlib import Path
from typing import Any


class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors."""


class DashboardConfigValidator:
    """Validates dashboard generation configuration."""

    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger(__name__)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, config: dict[str, Any]) -> bool:
        """
        Validate complete dashboard configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise

        Raises:
            ConfigValidationError: If critical configuration errors are found
        """
        self.errors.clear()
        self.warnings.clear()

        # Validate required sections
        self._validate_required_sections(config)

        # Validate design system
        if "design_system" in config:
            self._validate_design_system(config["design_system"])

        # Validate output configuration
        if "output" in config:
            self._validate_output_config(config["output"])

        # Validate scalability configuration
        if "scalability" in config:
            self._validate_scalability_config(config["scalability"])

        # Validate theme configuration
        if "theme" in config:
            self._validate_theme_config(config["theme"])

        # Validate logging configuration
        if "logging" in config:
            self._validate_logging_config(config["logging"])

        # Report results
        self._report_validation_results()

        # Return validation status
        return len(self.errors) == 0

    def _validate_required_sections(self, config: dict[str, Any]) -> None:
        """Validate that required configuration sections are present."""
        required_sections = ["design_system", "output", "scalability"]

        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required configuration section: {section}")

    def _validate_design_system(self, design_config: dict[str, Any]) -> None:
        """Validate design system configuration."""
        if "colors" not in design_config:
            self.errors.append("Missing 'colors' section in design_system")
            return

        colors = design_config["colors"]
        required_colors = ["primary_data", "secondary_data", "tertiary_data"]

        for color_name in required_colors:
            if color_name not in colors:
                self.errors.append(f"Missing required color: {color_name}")
                continue

            color_value = colors[color_name]
            if not self._is_valid_color(color_value):
                self.errors.append(f"Invalid color format for {color_name}: {color_value}")

    def _validate_output_config(self, output_config: dict[str, Any]) -> None:
        """Validate output configuration."""
        required_fields = ["directory", "filename_template", "dpi", "format"]

        for field in required_fields:
            if field not in output_config:
                self.errors.append(f"Missing required output field: {field}")

        # Validate DPI
        if "dpi" in output_config:
            dpi = output_config["dpi"]
            if not isinstance(dpi, int) or dpi < 72 or dpi > 600:
                self.errors.append(f"Invalid DPI value: {dpi} (must be integer between 72-600)")

        # Validate format
        if "format" in output_config:
            format_val = output_config["format"]
            valid_formats = ["png", "jpg", "jpeg", "svg", "pdf"]
            if format_val.lower() not in valid_formats:
                self.errors.append(f"Invalid output format: {format_val} (must be one of {valid_formats})")

        # Validate directory path
        if "directory" in output_config:
            directory = Path(output_config["directory"])
            if directory.is_absolute() and not directory.parent.exists():
                self.warnings.append(f"Output directory parent does not exist: {directory.parent}")

        # Validate filename template
        if "filename_template" in output_config:
            template = output_config["filename_template"]
            required_placeholders = ["{mode}"]
            for placeholder in required_placeholders:
                if placeholder not in template:
                    self.warnings.append(f"Filename template missing recommended placeholder: {placeholder}")

    def _validate_scalability_config(self, scalability_config: dict[str, Any]) -> None:
        """Validate scalability configuration."""
        required_sections = ["trade_volume_thresholds", "monthly_timeline_thresholds"]

        for section in required_sections:
            if section not in scalability_config:
                self.errors.append(f"Missing scalability section: {section}")

        # Validate trade volume thresholds
        if "trade_volume_thresholds" in scalability_config:
            thresholds = scalability_config["trade_volume_thresholds"]
            required_thresholds = ["small", "medium", "large"]

            for threshold in required_thresholds:
                if threshold not in thresholds:
                    self.errors.append(f"Missing trade volume threshold: {threshold}")
                    continue

                value = thresholds[threshold]
                if not isinstance(value, int) or value <= 0:
                    self.errors.append(f"Invalid trade volume threshold {threshold}: {value}")

            # Validate threshold ordering
            if all(t in thresholds for t in required_thresholds):
                if not (thresholds["small"] < thresholds["medium"] < thresholds["large"]):
                    self.errors.append("Trade volume thresholds must be in ascending order: small < medium < large")

        # Validate monthly timeline thresholds
        if "monthly_timeline_thresholds" in scalability_config:
            thresholds = scalability_config["monthly_timeline_thresholds"]
            required_thresholds = ["compact", "medium", "condensed"]

            for threshold in required_thresholds:
                if threshold not in thresholds:
                    self.errors.append(f"Missing monthly timeline threshold: {threshold}")
                    continue

                value = thresholds[threshold]
                if not isinstance(value, int) or value <= 0 or value > 12:
                    self.errors.append(f"Invalid monthly timeline threshold {threshold}: {value} (must be 1-12)")

            # Validate threshold ordering
            if all(t in thresholds for t in required_thresholds):
                if not (thresholds["compact"] < thresholds["medium"] < thresholds["condensed"]):
                    self.errors.append("Monthly timeline thresholds must be in ascending order")

    def _validate_theme_config(self, theme_config: dict[str, Any]) -> None:
        """Validate theme configuration."""
        required_themes = ["light", "dark"]

        for theme_name in required_themes:
            if theme_name not in theme_config:
                self.errors.append(f"Missing theme configuration: {theme_name}")
                continue

            theme = theme_config[theme_name]
            required_theme_fields = ["background", "primary_text", "body_text"]

            for field in required_theme_fields:
                if field not in theme:
                    self.errors.append(f"Missing {theme_name} theme field: {field}")
                    continue

                color_value = theme[field]
                if not self._is_valid_color(color_value):
                    self.errors.append(f"Invalid color in {theme_name} theme {field}: {color_value}")

    def _validate_logging_config(self, logging_config: dict[str, Any]) -> None:
        """Validate logging configuration."""
        if "level" in logging_config:
            level = logging_config["level"]
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level not in valid_levels:
                self.errors.append(f"Invalid logging level: {level} (must be one of {valid_levels})")

        if "file" in logging_config:
            log_file = Path(logging_config["file"])
            if log_file.is_absolute() and not log_file.parent.exists():
                self.warnings.append(f"Log file directory does not exist: {log_file.parent}")

    def _is_valid_color(self, color_value: str) -> bool:
        """
        Validate color format.

        Args:
            color_value: Color value to validate

        Returns:
            True if color format is valid
        """
        if not isinstance(color_value, str):
            return False

        # Check hex color format (#RGB or #RRGGBB)
        hex_pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$"
        if re.match(hex_pattern, color_value):
            return True

        # Check named colors (basic set)
        named_colors = {
            "white",
            "black",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "gray",
            "grey",
            "orange",
            "purple",
            "brown",
            "pink",
            "olive",
            "navy",
        }
        if color_value.lower() in named_colors:
            return True

        # Check RGB format rgb(r,g,b)
        rgb_pattern = r"^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$"
        if re.match(rgb_pattern, color_value):
            return True

        return False

    def _report_validation_results(self) -> None:
        """Report validation results."""
        if self.errors:
            self.logger.error(f"Configuration validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                self.logger.error(f"  - {error}")

        if self.warnings:
            self.logger.warning(f"Configuration validation found {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                self.logger.warning(f"  - {warning}")

        if not self.errors and not self.warnings:
            self.logger.info("Configuration validation passed with no issues")

    def get_validation_summary(self) -> dict[str, Any]:
        """
        Get validation summary.

        Returns:
            Dictionary with validation results
        """
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
        }


class InputFileValidator:
    """Validates input files for dashboard generation."""

    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger(__name__)

    def validate_input_file(self, file_path: Path) -> bool:
        """
        Validate input file for dashboard generation.

        Args:
            file_path: Path to input file

        Returns:
            True if file is valid for dashboard generation

        Raises:
            ConfigValidationError: If file validation fails
        """
        # Check file exists
        if not file_path.exists():
            raise ConfigValidationError(f"Input file does not exist: {file_path}")

        # Check file is readable
        if not file_path.is_file():
            raise ConfigValidationError(f"Input path is not a file: {file_path}")

        # Check file extension
        if file_path.suffix.lower() != ".md":
            self.logger.warning(f"Input file is not a markdown file: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ConfigValidationError(f"Input file is empty: {file_path}")

        if file_size > 10 * 1024 * 1024:  # 10MB
            self.logger.warning(f"Input file is very large ({file_size / 1024 / 1024:.1f}MB): {file_path}")

        # Basic content validation
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for expected content patterns
            expected_patterns = ["performance", "trading", "trade", "return", "profit"]

            content_lower = content.lower()
            found_patterns = [pattern for pattern in expected_patterns if pattern in content_lower]

            if len(found_patterns) < 2:
                self.logger.warning(f"Input file may not contain trading performance data: {file_path}")

        except UnicodeDecodeError:
            raise ConfigValidationError(f"Input file contains invalid UTF-8 encoding: {file_path}")
        except Exception as e:
            self.logger.warning(f"Could not validate input file content: {e}")

        return True


def validate_dashboard_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate dashboard configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Validation summary dictionary

    Raises:
        ConfigValidationError: If validation fails
    """
    validator = DashboardConfigValidator()
    is_valid = validator.validate(config)

    summary = validator.get_validation_summary()

    if not is_valid:
        error_message = f"Configuration validation failed with {summary['error_count']} error(s)"
        raise ConfigValidationError(error_message)

    return summary


def validate_input_file(file_path: Path) -> bool:
    """
    Validate input file for dashboard generation.

    Args:
        file_path: Path to input file

    Returns:
        True if file is valid

    Raises:
        ConfigValidationError: If validation fails
    """
    validator = InputFileValidator()
    return validator.validate_input_file(file_path)


if __name__ == "__main__":
    # Test configuration validation
    import sys
    from pathlib import Path

    from scripts.utils.config_loader import ConfigLoader

    if len(sys.argv) != 2:
        print("Usage: python config_validator.py <config_file>")
        sys.exit(1)

    config_file = Path(sys.argv[1])

    try:
        config_loader = ConfigLoader()
        config = config_loader.load_config(config_file)

        summary = validate_dashboard_config(config)

        print("✅ Configuration validation completed")
        print(f"   Errors: {summary['error_count']}")
        print(f"   Warnings: {summary['warning_count']}")

        if summary["warnings"]:
            print("\nWarnings:")
            for warning in summary["warnings"]:
                print(f"  - {warning}")

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)
