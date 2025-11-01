#!/usr/bin/env python3
"""
Script Configuration System

Centralized configuration management for generalized scripts:
- Environment-based configuration
- File-based configuration
- Dynamic configuration validation
- Path resolution and validation
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from error_handler import ErrorHandler
from errors import ConfigurationError


@dataclass
class ScriptConfig:
    """Configuration for generalized scripts"""

    # Base paths
    base_path: Path
    data_outputs_path: Path
    templates_path: Path

    # Twitter-specific paths
    twitter_outputs_path: Path
    twitter_templates_path: Path

    # Validation settings
    validation_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "institutional_minimum": 9.0,
            "publication_minimum": 8.5,
            "accuracy_minimum": 9.5,
            "compliance_minimum": 9.5,
        }
    )

    # Content type mappings
    content_type_mappings: dict[str, str] = field(
        default_factory=lambda: {
            "fundamental_analysis": "fundamental",
            "post_strategy": "strategy",
            "sector_analysis": "sector",
            "trade_history": "trade_history",
        }
    )

    # Template settings
    template_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "default_template_format": "jinja2",
            "template_cache_enabled": True,
            "template_validation_enabled": True,
        }
    )

    # Logging settings
    log_level: str = "INFO"
    log_file: Path | None = None
    structured_logging: bool = True

    # Processing settings
    fail_fast: bool = True
    max_retries: int = 3
    timeout_seconds: int = 300

    # Performance settings
    enable_performance_tracking: bool = True
    performance_log_file: Path | None = None

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_paths()
        self._validate_thresholds()
        self._ensure_directories()

    def _validate_paths(self) -> None:
        """Validate that required paths exist"""
        required_paths = {
            "base_path": self.base_path,
            "data_outputs_path": self.data_outputs_path,
            "templates_path": self.templates_path,
        }

        missing_paths = []
        for name, path in required_paths.items():
            if not path.exists():
                missing_paths.append(name)

        if missing_paths:
            raise ConfigurationError(
                f"Missing required paths: {', '.join(missing_paths)}",
                context={
                    "missing_paths": missing_paths,
                    "all_paths": {k: str(v) for k, v in required_paths.items()},
                },
            )

    def _validate_thresholds(self) -> None:
        """Validate that thresholds are within valid ranges"""
        for key, value in self.validation_thresholds.items():
            if not isinstance(value, (int, float)) or value < 0 or value > 10:
                raise ConfigurationError(
                    f"Invalid threshold value for {key}: {value}",
                    config_key=key,
                    context={"value": value, "valid_range": "0-10"},
                )

    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        directories_to_create = [
            self.twitter_outputs_path,
            self.twitter_outputs_path / "fundamental_analysis",
            self.twitter_outputs_path / "post_strategy",
            self.twitter_outputs_path / "sector_analysis",
            self.twitter_outputs_path / "trade_history",
        ]

        for directory in directories_to_create:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_environment(cls, base_path: Path | None = None) -> "ScriptConfig":
        """Create configuration from environment variables"""

        if base_path is None:
            base_path = Path(os.environ.get("COLEMORTON_BASE_PATH", Path.cwd()))
        else:
            base_path = Path(base_path)

        # Get paths from environment with defaults
        data_outputs_path = Path(os.environ.get("COLEMORTON_DATA_OUTPUTS", base_path / "data" / "outputs"))
        templates_path = Path(os.environ.get("COLEMORTON_TEMPLATES", base_path / "scripts" / "templates"))

        # Twitter-specific paths
        twitter_outputs_path = data_outputs_path / "twitter"
        twitter_templates_path = templates_path / "twitter"

        # Validation thresholds from environment
        validation_thresholds = {
            "institutional_minimum": float(os.environ.get("VALIDATION_INSTITUTIONAL_MIN", "9.0")),
            "publication_minimum": float(os.environ.get("VALIDATION_PUBLICATION_MIN", "8.5")),
            "accuracy_minimum": float(os.environ.get("VALIDATION_ACCURACY_MIN", "9.5")),
            "compliance_minimum": float(os.environ.get("VALIDATION_COMPLIANCE_MIN", "9.5")),
        }

        # Logging settings
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        log_file = Path(os.environ.get("LOG_FILE")) if os.environ.get("LOG_FILE") else None

        # Processing settings
        fail_fast = os.environ.get("FAIL_FAST", "true").lower() == "true"
        max_retries = int(os.environ.get("MAX_RETRIES", "3"))
        timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", "300"))

        return cls(
            base_path=base_path,
            data_outputs_path=data_outputs_path,
            templates_path=templates_path,
            twitter_outputs_path=twitter_outputs_path,
            twitter_templates_path=twitter_templates_path,
            validation_thresholds=validation_thresholds,
            log_level=log_level,
            log_file=log_file,
            fail_fast=fail_fast,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )

    @classmethod
    def from_file(cls, config_file: Path) -> "ScriptConfig":
        """Create configuration from YAML or JSON file"""

        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}", config_file=config_file)

        try:
            with open(config_file, encoding="utf-8") as f:
                if config_file.suffix.lower() in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file: {e}",
                config_file=config_file,
                context={"error": str(e)},
            )

        # Convert string paths to Path objects
        for key in [
            "base_path",
            "data_outputs_path",
            "templates_path",
            "twitter_outputs_path",
            "twitter_templates_path",
        ]:
            if key in config_data:
                config_data[key] = Path(config_data[key])

        if "log_file" in config_data and config_data["log_file"]:
            config_data["log_file"] = Path(config_data["log_file"])

        if "performance_log_file" in config_data and config_data["performance_log_file"]:
            config_data["performance_log_file"] = Path(config_data["performance_log_file"])

        return cls(**config_data)

    def get_content_type_path(self, content_type: str) -> Path:
        """Get output path for specific content type"""
        mapped_type = self.content_type_mappings.get(content_type, content_type)
        return self.twitter_outputs_path / mapped_type

    def get_template_path(self, content_type: str, template_name: str) -> Path:
        """Get template path for specific content type and template"""
        mapped_type = self.content_type_mappings.get(content_type, content_type)
        return self.twitter_templates_path / mapped_type / template_name

    def get_validation_threshold(self, threshold_type: str) -> float:
        """Get validation threshold by type"""
        return self.validation_thresholds.get(threshold_type, 8.5)

    def update_threshold(self, threshold_type: str, value: float) -> None:
        """Update validation threshold"""
        if not isinstance(value, (int, float)) or value < 0 or value > 10:
            raise ConfigurationError(
                f"Invalid threshold value: {value}",
                config_key=threshold_type,
                context={"value": value, "valid_range": "0-10"},
            )

        self.validation_thresholds[threshold_type] = value

    def export_config(self, output_file: Path) -> None:
        """Export configuration to file"""

        config_data = {
            "base_path": str(self.base_path),
            "data_outputs_path": str(self.data_outputs_path),
            "templates_path": str(self.templates_path),
            "twitter_outputs_path": str(self.twitter_outputs_path),
            "twitter_templates_path": str(self.twitter_templates_path),
            "validation_thresholds": self.validation_thresholds,
            "content_type_mappings": self.content_type_mappings,
            "template_settings": self.template_settings,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
            "structured_logging": self.structured_logging,
            "fail_fast": self.fail_fast,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "enable_performance_tracking": self.enable_performance_tracking,
            "performance_log_file": (str(self.performance_log_file) if self.performance_log_file else None),
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if output_file.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(config_data, f, default_flow_style=False)
                else:
                    json.dump(config_data, f, indent=2)

        except Exception as e:
            raise ConfigurationError(
                f"Failed to export configuration: {e}",
                config_file=output_file,
                context={"error": str(e)},
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "base_path": str(self.base_path),
            "data_outputs_path": str(self.data_outputs_path),
            "templates_path": str(self.templates_path),
            "twitter_outputs_path": str(self.twitter_outputs_path),
            "twitter_templates_path": str(self.twitter_templates_path),
            "validation_thresholds": self.validation_thresholds,
            "content_type_mappings": self.content_type_mappings,
            "template_settings": self.template_settings,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
            "structured_logging": self.structured_logging,
            "fail_fast": self.fail_fast,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "enable_performance_tracking": self.enable_performance_tracking,
            "performance_log_file": (str(self.performance_log_file) if self.performance_log_file else None),
        }


class ConfigurationManager:
    """Manages configuration across the system"""

    def __init__(self, config: ScriptConfig):
        self.config = config
        self.error_handler = ErrorHandler()

    def validate_config(self) -> bool:
        """Validate current configuration"""

        try:
            # Validate paths exist
            self.config._validate_paths()

            # Validate thresholds
            self.config._validate_thresholds()

            # Validate template settings
            self._validate_template_settings()

            return True

        except ConfigurationError as e:
            self.error_handler.log_error(e, {"operation": "config_validation"})
            return False

    def _validate_template_settings(self) -> None:
        """Validate template settings"""

        required_settings = [
            "default_template_format",
            "template_cache_enabled",
            "template_validation_enabled",
        ]

        for setting in required_settings:
            if setting not in self.config.template_settings:
                raise ConfigurationError(f"Missing required template setting: {setting}", config_key=setting)

    def get_environment_override(self, key: str) -> str | None:
        """Get environment variable override for configuration key"""

        env_key = f"COLEMORTON_{key.upper()}"
        return os.environ.get(env_key)

    def apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration"""

        # Log level override
        log_level_override = self.get_environment_override("log_level")
        if log_level_override:
            self.config.log_level = log_level_override

        # Fail fast override
        fail_fast_override = self.get_environment_override("fail_fast")
        if fail_fast_override:
            self.config.fail_fast = fail_fast_override.lower() == "true"

        # Max retries override
        max_retries_override = self.get_environment_override("max_retries")
        if max_retries_override:
            self.config.max_retries = int(max_retries_override)


# Convenience functions for common configuration scenarios
def load_default_config() -> ScriptConfig:
    """Load default configuration from environment"""
    return ScriptConfig.from_environment()


def load_config_from_file(config_file: Path) -> ScriptConfig:
    """Load configuration from file with error handling"""

    try:
        return ScriptConfig.from_file(config_file)
    except ConfigurationError:
        # Fall back to environment configuration
        print("Warning: Failed to load config file {config_file}: {e}")
        print("Falling back to environment configuration")
        return ScriptConfig.from_environment()


def create_development_config(base_path: Path) -> ScriptConfig:
    """Create development configuration with relaxed thresholds"""

    config = ScriptConfig.from_environment(base_path)

    # Relax validation thresholds for development
    config.validation_thresholds = {
        "institutional_minimum": 7.0,
        "publication_minimum": 6.0,
        "accuracy_minimum": 7.5,
        "compliance_minimum": 7.5,
    }

    # Enable more verbose logging
    config.log_level = "DEBUG"

    # Disable fail-fast for development
    config.fail_fast = False

    return config
