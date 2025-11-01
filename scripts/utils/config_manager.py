#!/usr/bin/env python3
"""
Configuration Manager for Macro-Economic Analysis

Centralized configuration loading and validation system that eliminates hardcoded values
throughout the macro-economic analysis pipeline. Provides fail-fast validation,
environment-specific overrides, and runtime configuration management.

Key Features:
- YAML configuration file loading with validation
- Environment-specific configuration overrides (dev/staging/prod)
- Fail-fast validation for required configuration values
- Runtime configuration value access with type checking
- Configuration caching and reload capabilities
- Market data parameter management
- Business logic threshold management

Usage:
    config = ConfigManager()
    fed_rate_fallback = config.get_market_data_fallback('fed_funds_rate', 5.25)
    min_services = config.get_business_logic_threshold('min_services_institutional', 4)
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails"""


class ConfigManager:
    """
    Centralized configuration management for macro-economic analysis

    Eliminates hardcoded values by providing structured access to configuration
    parameters with validation, environment overrides, and fail-fast behavior.
    """

    def __init__(self, config_path: str | None = None, environment: str = "prod"):
        """
        Initialize configuration manager

        Args:
            config_path: Path to main configuration file (defaults to macro_analysis_config.yaml)
            environment: Environment name for configuration overrides (dev/staging/prod)
        """
        self.environment = environment
        self._config_cache = {}
        self._last_reload = None
        self._cache_ttl = timedelta(minutes=15)  # Configuration cache TTL

        # Determine configuration file path
        if config_path is None:
            # Default to macro_analysis_config.yaml in config directory
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "macro_analysis_config.yaml"

        self.config_path = Path(config_path)

        # Load and validate configuration
        self._load_configuration()
        self._validate_required_configuration()

        logger.info(f"ConfigManager initialized with environment: {environment}")

    def _load_configuration(self) -> None:
        """Load configuration from YAML file with error handling"""
        try:
            if not self.config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {self.config_path}")

            with open(self.config_path) as f:
                self._config_cache = yaml.safe_load(f)

            self._last_reload = datetime.now()
            logger.info(f"Configuration loaded from: {self.config_path}")

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _validate_required_configuration(self) -> None:
        """Validate required configuration sections exist with fail-fast behavior"""
        required_sections = [
            "confidence_thresholds",
            "data_validation",
            "business_cycle",
            "regional_analysis",
            "data_sources",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in self._config_cache:
                missing_sections.append(section)

        if missing_sections:
            raise ConfigurationError(f"Required configuration sections missing: {missing_sections}")

        # Validate critical subsections
        self._validate_confidence_thresholds()
        self._validate_data_sources()

        logger.info("Configuration validation passed")

    def _validate_confidence_thresholds(self) -> None:
        """Validate confidence threshold configuration"""
        thresholds = self._config_cache.get("confidence_thresholds", {})
        required_thresholds = [
            "discovery_minimum",
            "analysis_minimum",
            "synthesis_minimum",
            "institutional_grade",
        ]

        for threshold in required_thresholds:
            if threshold not in thresholds:
                raise ConfigurationError(f"Missing confidence threshold: {threshold}")

            value = thresholds[threshold]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                raise ConfigurationError(f"Invalid confidence threshold {threshold}: {value} (must be 0-1)")

    def _validate_data_sources(self) -> None:
        """Validate data sources configuration"""
        sources = self._config_cache.get("data_sources", {})
        required_sources = ["fred", "imf", "alpha_vantage"]

        for source in required_sources:
            if source not in sources:
                raise ConfigurationError(f"Missing data source configuration: {source}")

            source_config = sources[source]
            if "reliability_score" not in source_config:
                raise ConfigurationError(f"Missing reliability_score for source: {source}")

    def reload_if_stale(self) -> bool:
        """Reload configuration if cache is stale"""
        if self._last_reload and datetime.now() - self._last_reload < self._cache_ttl:
            return False

        try:
            self._load_configuration()
            self._validate_required_configuration()
            return True
        except Exception as e:
            logger.warning(f"Failed to reload configuration: {e}")
            return False

    def get_confidence_threshold(self, threshold_type: str) -> float:
        """
        Get confidence threshold value

        Args:
            threshold_type: Type of threshold (discovery_minimum, institutional_grade, etc.)

        Returns:
            Confidence threshold value (0.0-1.0)

        Raises:
            ConfigurationError: If threshold type not found
        """
        self.reload_if_stale()

        thresholds = self._config_cache.get("confidence_thresholds", {})
        if threshold_type not in thresholds:
            raise ConfigurationError(f"Unknown confidence threshold type: {threshold_type}")

        return float(thresholds[threshold_type])

    def get_data_validation_threshold(self, validation_type: str) -> float | int:
        """
        Get data validation threshold

        Args:
            validation_type: Type of validation threshold (economic_indicator_variance_threshold, etc.)

        Returns:
            Validation threshold value
        """
        self.reload_if_stale()

        validation = self._config_cache.get("data_validation", {})
        if validation_type not in validation:
            raise ConfigurationError(f"Unknown validation threshold type: {validation_type}")

        return validation[validation_type]

    def get_business_cycle_parameter(self, parameter_name: str) -> Any:
        """
        Get business cycle modeling parameter

        Args:
            parameter_name: Parameter name (transition_probability_confidence, etc.)

        Returns:
            Parameter value
        """
        self.reload_if_stale()

        business_cycle = self._config_cache.get("business_cycle", {})
        if parameter_name not in business_cycle:
            raise ConfigurationError(f"Unknown business cycle parameter: {parameter_name}")

        return business_cycle[parameter_name]

    def get_data_source_config(self, source_name: str) -> dict[str, Any]:
        """
        Get complete data source configuration

        Args:
            source_name: Data source name (fred, imf, alpha_vantage, etc.)

        Returns:
            Data source configuration dictionary
        """
        self.reload_if_stale()

        sources = self._config_cache.get("data_sources", {})
        if source_name not in sources:
            raise ConfigurationError(f"Unknown data source: {source_name}")

        return sources[source_name].copy()

    def get_data_source_reliability(self, source_name: str) -> float:
        """
        Get data source reliability score

        Args:
            source_name: Data source name

        Returns:
            Reliability score (0.0-1.0)
        """
        source_config = self.get_data_source_config(source_name)
        return float(source_config.get("reliability_score", 0.5))

    def get_regional_indicators(self, region: str, indicator_type: str) -> list[str]:
        """
        Get regional economic indicators list

        Args:
            region: Region name (US, EU, ASIA, etc.)
            indicator_type: Indicator type (gdp_growth, employment, inflation, etc.)

        Returns:
            List of indicator codes
        """
        self.reload_if_stale()

        regional = self._config_cache.get("regional_analysis", {})
        indicators = regional.get("economic_indicators", {})

        if indicator_type not in indicators:
            raise ConfigurationError(f"Unknown indicator type: {indicator_type}")

        return indicators[indicator_type].copy()

    def get_quality_threshold(self, threshold_name: str) -> float:
        """
        Get quality assurance threshold

        Args:
            threshold_name: Threshold name (confidence_minimum, template_gap_coverage, etc.)

        Returns:
            Threshold value
        """
        self.reload_if_stale()

        qa = self._config_cache.get("quality_assurance", {})
        blocking = qa.get("blocking_thresholds", {})

        if threshold_name not in blocking:
            raise ConfigurationError(f"Unknown quality threshold: {threshold_name}")

        return float(blocking[threshold_name])

    def get_service_minimum_count(self) -> int:
        """
        Get minimum required service count for institutional analysis

        Returns:
            Minimum service count
        """
        # This is derived from data_sources configuration
        sources = self._config_cache.get("data_sources", {})
        # Count sources with priority 1-4 (critical sources)
        critical_sources = len([s for s in sources.values() if s.get("priority", 10) <= 4])
        return max(4, critical_sources)  # Minimum 4, or number of critical sources

    def get_market_data_fallback(self, data_type: str, default_value: float | int | str = None) -> Any:
        """
        Get market data fallback values (replacing hardcoded values)

        This method will be extended to provide configurable fallbacks for market data
        when real-time sources are unavailable.

        Args:
            data_type: Type of market data (fed_funds_rate, balance_sheet_size, etc.)
            default_value: Default value if no configuration found

        Returns:
            Configured fallback value or default
        """
        self.reload_if_stale()

        # Check if market_data_fallbacks section exists in config
        market_data = self._config_cache.get("market_data_fallbacks", {})

        if data_type in market_data:
            return market_data[data_type]

        # Return default value with warning
        if default_value is not None:
            logger.warning(f"Using default fallback for {data_type}: {default_value}")
            return default_value

        raise ConfigurationError(f"No fallback configured for market data type: {data_type}")

    def get_time_window(self, window_type: str) -> int | str:
        """
        Get time window configuration (replacing hardcoded time values)

        Args:
            window_type: Type of time window (economic_calendar_days, surprise_index_lookback, etc.)

        Returns:
            Time window value in appropriate units (int for days, str for timeframes like "1y", "2y")
        """
        self.reload_if_stale()

        # Check for time windows configuration
        time_windows = self._config_cache.get("time_windows", {})

        if window_type in time_windows:
            value = time_windows[window_type]
            # Return as-is for string timeframes, convert to int for day counts
            if isinstance(value, str):
                return value
            return int(value)

        # Fallback to sensible defaults with warning
        defaults = {
            "economic_calendar_days": 30,
            "surprise_index_lookback_days": 90,
            "fomc_advance_days": 15,
            "market_regime_duration_days": 45,
            "fed_rates_timeframe": "1y",
            "balance_sheet_timeframe": "2y",
            "m2_money_supply_timeframe": "2y",
        }

        if window_type in defaults:
            logger.warning(f"Using default time window for {window_type}: {defaults[window_type]}")
            return defaults[window_type]

        raise ConfigurationError(f"Unknown time window type: {window_type}")

    def get_api_performance_threshold(self, metric_type: str) -> float:
        """
        Get API performance thresholds (replacing hardcoded performance values)

        Args:
            metric_type: Performance metric type (response_time_ms, success_rate, etc.)

        Returns:
            Performance threshold value
        """
        self.reload_if_stale()

        # Check for API performance configuration
        api_perf = self._config_cache.get("api_performance", {})

        if metric_type in api_perf:
            return float(api_perf[metric_type])

        # Return sensible defaults
        defaults = {
            "max_response_time_ms": 30000,
            "min_success_rate": 0.8,
            "min_data_freshness": 0.9,
            "health_score_threshold": 0.85,
        }

        if metric_type in defaults:
            return defaults[metric_type]

        raise ConfigurationError(f"Unknown API performance metric: {metric_type}")

    def validate_runtime_value(self, value: Any, value_type: str, valid_range: tuple | None = None) -> bool:
        """
        Validate runtime values against configuration constraints

        Args:
            value: Value to validate
            value_type: Type of value for validation context
            valid_range: Optional (min, max) range for numeric values

        Returns:
            True if value is valid

        Raises:
            ConfigurationError: If value is invalid
        """
        if value_type == "confidence_score":
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                raise ConfigurationError(f"Invalid confidence score: {value} (must be 0-1)")

        elif value_type == "service_count":
            min_services = self.get_service_minimum_count()
            if not isinstance(value, int) or value < min_services:
                raise ConfigurationError(f"Invalid service count: {value} (minimum {min_services})")

        elif value_type == "percentage":
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ConfigurationError(f"Invalid percentage: {value} (must be 0-100)")

        elif value_type == "probability":
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                raise ConfigurationError(f"Invalid probability: {value} (must be 0-1)")

        if valid_range and isinstance(value, (int, float)):
            min_val, max_val = valid_range
            if value < min_val or value > max_val:
                raise ConfigurationError(f"Value {value} out of range [{min_val}, {max_val}]")

        return True

    def get_full_config(self) -> dict[str, Any]:
        """
        Get complete configuration dictionary (for debugging/inspection)

        Returns:
            Complete configuration dictionary
        """
        self.reload_if_stale()
        return self._config_cache.copy()

    def get_environment_override(self, config_key: str, default_value: Any = None) -> Any:
        """
        Get environment-specific configuration override

        Args:
            config_key: Configuration key to override
            default_value: Default value if no override found

        Returns:
            Override value or default
        """
        env_key = f"MACRO_CONFIG_{config_key.upper()}"
        env_value = os.getenv(env_key)

        if env_value is not None:
            logger.info(f"Using environment override for {config_key}: {env_value}")
            # Try to convert to appropriate type
            try:
                # Try float first
                if "." in env_value:
                    return float(env_value)
                # Try int
                return int(env_value)
            except ValueError:
                # Return as string
                return env_value

        return default_value

    def get_api_key(self, key_name: str, required: bool = False) -> str | None:
        """
        Get API key from environment variables with enhanced validation and security

        Args:
            key_name: API key name (e.g., 'FRED_API_KEY', 'ALPHA_VANTAGE_API_KEY')
            required: Whether the key is required (raises ConfigurationError if missing)

        Returns:
            API key value or None if not found

        Raises:
            ConfigurationError: If required key is missing or invalid
        """
        # First check environment variables
        env_value = os.getenv(key_name)
        if env_value and env_value.lower() not in ["none", "null", ""]:
            # Validate key format for security
            if self._validate_api_key_format(key_name, env_value):
                return env_value
            logger.warning(f"Invalid format for {key_name} from environment")
            if required:
                raise ConfigurationError(f"Invalid API key format for {key_name}")

        # Then check financial services configuration with environment substitution
        try:
            financial_services_path = (
                Path(__file__).parent.parent.parent / "config" / "services" / "financial_services.yaml"
            )
            if financial_services_path.exists():
                with open(financial_services_path) as f:
                    config_content = f.read()

                # Substitute environment variables
                import re

                env_pattern = re.compile(r"\$\{([^}]+)\}")

                def env_replacer(match):
                    env_var = match.group(1)
                    return os.getenv(env_var, match.group(0))

                config_content = env_pattern.sub(env_replacer, config_content)
                financial_config = yaml.safe_load(config_content)

                # Map key names to service configurations
                service_mapping = {
                    "FRED_API_KEY": "fred",
                    "ALPHA_VANTAGE_API_KEY": "alpha_vantage",
                    "SEC_EDGAR_API_KEY": "sec_edgar",
                    "IMF_API_KEY": "imf",
                    "FMP_API_KEY": "fmp",
                    "EIA_API_KEY": "eia",
                    "COINGECKO_API_KEY": "coingecko",
                }

                service_name = service_mapping.get(key_name)
                if service_name and service_name in financial_config.get("services", {}):
                    api_key = financial_config["services"][service_name].get("api_key")
                    # Handle services that don't require API keys
                    if api_key is None or str(api_key).lower() in ["none", "null"]:
                        if required:
                            raise ConfigurationError(f"Required API key {key_name} not configured")
                        return "not_required"
                    if api_key and self._validate_api_key_format(key_name, api_key):
                        return str(api_key)
                    if required:
                        raise ConfigurationError(f"Invalid API key format for {key_name}")

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in financial services config: {e}")
            if required:
                raise ConfigurationError(f"Failed to load configuration for {key_name}")
        except Exception as e:
            logger.warning(f"Could not load financial services config for {key_name}: {e}")
            if required:
                raise ConfigurationError(f"Failed to access configuration for {key_name}")

        # Check if key is required but not found
        if required:
            raise ConfigurationError(f"Required API key {key_name} not found in environment or configuration")

        return None

    def _validate_api_key_format(self, key_name: str, api_key: str) -> bool:
        """
        Validate API key format for security and correctness

        Args:
            key_name: Name of the API key
            api_key: The API key value to validate

        Returns:
            True if format is valid, False otherwise
        """
        if not isinstance(api_key, str) or len(api_key.strip()) == 0:
            return False

        # Check for placeholder values
        invalid_patterns = [
            "your_key_here",
            "replace_me",
            "change_this",
            "api_key_here",
            "test_key",
            "dummy_key",
        ]

        api_key_lower = api_key.lower()
        if any(pattern in api_key_lower for pattern in invalid_patterns):
            return False

        # Service-specific validation
        if key_name == "ALPHA_VANTAGE_API_KEY":
            # Alpha Vantage keys are typically 16-20 alphanumeric characters
            return len(api_key) >= 10 and api_key.isalnum()

        if key_name == "FRED_API_KEY":
            # FRED keys are typically 32 character hex strings
            return len(api_key) == 32 and all(c in "0123456789abcdef" for c in api_key.lower())

        if key_name == "SEC_EDGAR_API_KEY":
            # SEC EDGAR keys are long hex strings (64+ characters)
            return len(api_key) >= 60 and all(c in "0123456789abcdef" for c in api_key.lower())

        if key_name == "FMP_API_KEY":
            # FMP keys are typically 32 alphanumeric characters
            return len(api_key) >= 20 and api_key.replace("-", "").isalnum()

        # Generic validation for other keys
        return len(api_key) >= 8

    def get_api_key_status(self, key_name: str) -> dict[str, Any]:
        """
        Get detailed status information about an API key

        Args:
            key_name: API key name

        Returns:
            Dictionary with key status information
        """
        status = {
            "key_name": key_name,
            "found": False,
            "source": None,
            "valid_format": False,
            "obfuscated_value": None,
            "length": 0,
            "required": key_name in ["ALPHA_VANTAGE_API_KEY", "FRED_API_KEY", "FMP_API_KEY"],
        }

        try:
            api_key = self.get_api_key(key_name)
            if api_key and api_key != "not_required":
                status["found"] = True
                status["source"] = "environment" if os.getenv(key_name) else "config"
                status["valid_format"] = self._validate_api_key_format(key_name, api_key)
                status["length"] = len(api_key)
                # Obfuscate key for security (show first 4 and last 4 characters)
                if len(api_key) > 8:
                    status["obfuscated_value"] = f"{api_key[:4]}...{api_key[-4:]}"
                else:
                    status["obfuscated_value"] = f"{api_key[:2]}{'*' * (len(api_key) - 4)}{api_key[-2:]}"
            elif api_key == "not_required":
                status["found"] = True
                status["source"] = "config"
                status["obfuscated_value"] = "not_required"

        except Exception as e:
            status["error"] = str(e)

        return status

    def get_regional_volatility_parameters(self, region: str) -> dict[str, Any]:
        """
        DEPRECATED: Volatility parameters are now calculated dynamically in discovery phase

        This method now fails fast to prevent use of hardcoded values.
        Use calculated values from discovery files instead.

        Args:
            region: Region name (US, AMERICAS, EUROPE, ASIA, etc.)

        Raises:
            ConfigurationError: Always raises - method deprecated in favor of calculated values
        """
        raise ConfigurationError(
            f"Volatility parameters for region '{region}' are no longer configured as hardcoded values. "
            f"Use calculated values from discovery phase CLI market intelligence data. "
            f"Check discovery file: ./data/outputs/macro_analysis/discovery/{region.lower()}_YYYYMMDD_discovery.json"
        )

    def get_volatility_parameter(self, region: str, parameter_name: str) -> float | str:
        """
        DEPRECATED: Volatility parameters are now calculated dynamically in discovery phase

        This method now fails fast to prevent use of hardcoded values.

        Args:
            region: Region name (US, AMERICAS, EUROPE, ASIA, etc.)
            parameter_name: Parameter name (long_term_mean, reversion_speed, volatility_index, etc.)

        Raises:
            ConfigurationError: Always raises - method deprecated in favor of calculated values
        """
        raise ConfigurationError(
            f"Volatility parameter '{parameter_name}' for region '{region}' is no longer configured as hardcoded value. "
            f"Use calculated values from discovery phase CLI market intelligence data."
        )

    def validate_cross_regional_volatility_uniqueness(self, tolerance: float = 0.02) -> dict[str, Any]:
        """
        DEPRECATED: Volatility validation now handled by discovery file validation

        This method now fails fast since hardcoded volatility parameters were removed.
        Use validate_template_artifacts() in validate_macro_synthesis.py instead.

        Args:
            tolerance: Minimum relative difference between regions (default 2%)

        Returns:
            Validation results indicating deprecated status
        """
        return {
            "template_artifacts_detected": False,
            "warnings": ["Method deprecated - volatility validation moved to discovery file validation"],
            "issues": [],
            "parameter_analysis": {},
            "deprecated_notice": "Use calculated values from discovery files for volatility validation",
            "replacement_method": "validate_template_artifacts() in validate_macro_synthesis.py",
        }

    def suggest_regional_volatility_adjustments(self, base_region: str = "US") -> dict[str, dict[str, float]]:
        """
        DEPRECATED: Volatility adjustments now calculated dynamically in discovery phase

        This method contained hardcoded template artifacts and is no longer used.
        Volatility parameters are calculated from real market data in discovery phase.

        Args:
            base_region: Base region to use as reference (typically US/AMERICAS)

        Raises:
            ConfigurationError: Always raises - method deprecated to prevent hardcoded values
        """
        raise ConfigurationError(
            "Regional volatility adjustments are no longer provided as hardcoded suggestions. "
            "Volatility parameters are calculated dynamically from real market data in the discovery phase. "
            "This method was deprecated to eliminate template artifacts caused by hardcoded values."
        )
