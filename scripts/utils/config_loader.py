"""
Configuration loading utilities with environment support.

Enhanced to support financial services configuration with:
- Environment variable substitution
- Multi-environment configuration merging
- Service-specific configuration extraction
- Validation and defaults
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class FinancialServiceConfig(BaseModel):
    """Pydantic model for financial service configuration validation"""

    name: str
    base_url: str
    api_key: str | None = None
    timeout_seconds: int = 30
    max_retries: int = 3
    cache: dict[str, Any] = Field(default_factory=dict)
    rate_limit: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)


class ConfigLoader:
    """Loads and merges YAML configurations with environment support."""

    def __init__(self, config_dir: str | None = None, auto_load_env: bool = True) -> None:
        self.env_pattern = re.compile(r"\$\{([^}]+)\}")
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"

        # Automatically detect and load environment files
        if auto_load_env:
            self._auto_detect_and_load_env()

    def _auto_detect_and_load_env(self) -> None:
        """Automatically detect and load .env files from project root or current directory."""
        try:
            # Look for .env files in common locations
            search_paths = [
                Path.cwd(),  # Current working directory
                Path.cwd().parent,  # Parent directory
                Path(__file__).parent.parent.parent,  # Project root (3 levels up from utils)
            ]

            env_files_found = []

            for search_path in search_paths:
                if search_path.exists():
                    # Check for various .env file patterns
                    env_patterns = [
                        ".env",
                        ".env.local",
                        ".env.dev",
                        ".env.development",
                    ]

                    for pattern in env_patterns:
                        env_file = search_path / pattern
                        if env_file.exists() and env_file.is_file():
                            env_files_found.append(env_file)
                            break  # Use first found env file per directory

                    # Stop searching once we find an env file
                    if env_files_found:
                        break

            # Load the most appropriate .env file
            if env_files_found:
                env_file = env_files_found[0]  # Use the first (most specific) one found
                self._load_env_file(env_file)

        except Exception:
            # Silently continue if env file detection fails
            # This ensures ConfigLoader still works even if env detection has issues
            pass

    def _load_env_file(self, env_file_path: Path) -> None:
        """Load environment variables from a .env file."""
        try:
            with open(env_file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        # Only set if not already in environment
                        if key and key not in os.environ:
                            os.environ[key] = value

        except Exception:
            # Silently continue if env file loading fails
            pass

    def load_config(self, config_path: str) -> dict[str, Any]:
        """Load a single YAML configuration file."""
        path = Path(config_path)

        # Backward compatibility: check old configs/ path if new path doesn't exist
        if not path.exists() and "configs/" in str(config_path):
            # Map old paths to new structure
            path_str = str(config_path)
            if "configs/dashboard_generation.yaml" in path_str:
                new_path = Path(
                    path_str.replace(
                        "configs/dashboard_generation.yaml",
                        "config/pipelines/dashboard_generation.yaml",
                    )
                )
            elif "configs/data_extraction.yaml" in path_str:
                new_path = Path(
                    path_str.replace(
                        "configs/data_extraction.yaml",
                        "config/pipelines/data_extraction.yaml",
                    )
                )
            elif "configs/feature_engineering.yaml" in path_str:
                new_path = Path(
                    path_str.replace(
                        "configs/feature_engineering.yaml",
                        "config/pipelines/feature_engineering.yaml",
                    )
                )
            elif "configs/model_training.yaml" in path_str:
                new_path = Path(
                    path_str.replace(
                        "configs/model_training.yaml",
                        "config/pipelines/model_training.yaml",
                    )
                )
            elif "configs/report_generation.yaml" in path_str:
                new_path = Path(
                    path_str.replace(
                        "configs/report_generation.yaml",
                        "config/pipelines/report_generation.yaml",
                    )
                )
            else:
                new_path = Path(path_str.replace("configs/", "config/"))

            if new_path.exists():
                print(f"WARNING: Using deprecated path {config_path}. Please update to {new_path}")
                path = new_path

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path) as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError(f"Configuration file must contain a YAML dictionary: {config_path}")

        return self._substitute_variables(config)

    def load_with_environment(self, config_path: str, env: str = "dev") -> dict[str, Any]:
        """Load base config and overlay environment-specific settings."""
        try:
            base_config = self.load_config(config_path)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load base config from {config_path}: {e}")

        # Try to load environment-specific config (optional)
        config_dir = Path(config_path).parent
        env_config_path = config_dir / "environments" / f"{env}.yaml"

        if env_config_path.exists():
            try:
                env_config = self.load_config(str(env_config_path))
                base_config = self._merge_configs(base_config, env_config)
            except Exception as e:
                # Log warning but continue with base config
                print(f"Warning: Failed to load environment config {env_config_path}: {e}")

        # Load shared configs (optional)
        shared_dir = config_dir / "shared"
        if shared_dir.exists():
            try:
                for shared_file in shared_dir.glob("*.yaml"):
                    shared_config = self.load_config(str(shared_file))
                    base_config = self._merge_configs(shared_config, base_config)
            except Exception:
                # Log warning but continue with base config
                print("Warning: Failed to load shared config from {shared_dir}: {e}")

        return base_config

    def _substitute_variables(self, config: dict[str, Any]) -> dict[str, Any]:
        """Recursively substitute environment variables in config."""
        return self._substitute_variables_recursive(config)  # type: ignore

    def _substitute_variables_recursive(self, config: Any) -> Any:
        """Internal recursive substitution method."""
        if isinstance(config, dict):
            return {key: self._substitute_variables_recursive(value) for key, value in config.items()}
        if isinstance(config, list):
            return [self._substitute_variables_recursive(item) for item in config]
        if isinstance(config, str):
            return self._substitute_string_variables(config)
        return config

    def _substitute_string_variables(self, value: str) -> str:
        """Substitute environment variables in a string."""

        def replacer(match: Any) -> str:
            var_name = match.group(1)
            # Handle nested variable references like ${base_paths.data_root}
            if "." in var_name:
                # Return original for complex references (handle in post-processing)
                return value
            return os.getenv(var_name, match.group(0))

        return self.env_pattern.sub(replacer, value)

    def _merge_configs(self, base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()

        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def load_financial_services_config(self, env: str = "dev") -> dict[str, Any]:
        """
        Load financial services configuration with environment overlay

        Args:
            env: Environment name (dev, test, prod)

        Returns:
            Complete financial services configuration
        """
        # Check new location first
        config_file = self.config_dir / "services" / "financial_services.yaml"
        if not config_file.exists():
            # Try old location for backward compatibility
            config_file = self.config_dir / "financial_services.yaml"
            if not config_file.exists():
                raise FileNotFoundError(f"Financial services config not found: {config_file}")

        return self.load_with_environment(str(config_file), env)

    def get_service_config(self, service_name: str, env: str = "dev") -> FinancialServiceConfig:
        """
        Get configuration for a specific financial service

        Args:
            service_name: Name of the financial service
            env: Environment name

        Returns:
            Validated service configuration

        Raises:
            KeyError: If service not found in configuration
            ValidationError: If configuration is invalid
        """
        full_config = self.load_financial_services_config(env)

        if "services" not in full_config:
            raise KeyError("No services configuration found")

        if service_name not in full_config["services"]:
            raise KeyError(f"Service '{service_name}' not found in configuration")

        service_config = full_config["services"][service_name]

        # Merge with global defaults
        global_config = full_config.get("global", {})
        merged_config = self._merge_service_with_global(service_config, global_config)

        return FinancialServiceConfig(**merged_config)

    def get_orchestration_config(self, env: str = "dev") -> dict[str, Any]:
        """Get orchestration configuration"""
        full_config = self.load_financial_services_config(env)
        return full_config.get("orchestration", {})

    def get_cli_config(self, env: str = "dev") -> dict[str, Any]:
        """Get CLI configuration"""
        full_config = self.load_financial_services_config(env)
        return full_config.get("cli", {})

    def list_available_services(self, env: str = "dev") -> list[str]:
        """List all available financial services"""
        full_config = self.load_financial_services_config(env)
        return list(full_config.get("services", {}).keys())

    def _merge_service_with_global(
        self, service_config: dict[str, Any], global_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge service-specific config with global defaults"""

        # Start with service config
        merged = service_config.copy()

        # Apply global defaults where service config doesn't specify
        for global_key, global_value in global_config.items():
            if global_key == "cache" and "cache" not in merged:
                merged["cache"] = global_value
            elif global_key == "rate_limiting" and "rate_limit" not in merged:
                merged["rate_limit"] = global_value
            elif global_key == "request":
                # Merge request settings
                for req_key, req_value in global_value.items():
                    if req_key not in merged:
                        merged[req_key] = req_value

        return merged

    def validate_configuration(self, env: str = "dev") -> dict[str, Any]:
        """
        Validate entire configuration and return validation results

        Args:
            env: Environment to validate

        Returns:
            Validation results with any errors found
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "services_validated": 0,
            "environment": env,
        }

        try:
            full_config = self.load_financial_services_config(env)

            # Validate each service
            services = full_config.get("services", {})
            for service_name in services:
                try:
                    self.get_service_config(service_name, env)
                    validation_results["services_validated"] += 1
                except Exception as e:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Service {service_name}: {str(e)}")

            # Check for required environment variables
            self._check_required_env_vars(full_config, validation_results)

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Configuration loading failed: {str(e)}")

        return validation_results

    def _check_required_env_vars(self, config: dict[str, Any], validation_results: dict[str, Any]) -> None:
        """Check for required environment variables"""
        required_env_vars = {
            "ALPHA_VANTAGE_API_KEY": "Alpha Vantage service",
            "FRED_API_KEY": "FRED Economic service",
            "FMP_API_KEY": "Financial Modeling Prep service",
        }

        for env_var, service_name in required_env_vars.items():
            if not os.getenv(env_var):
                validation_results["warnings"].append(
                    f"Environment variable {env_var} not set - {service_name} may not work"
                )
