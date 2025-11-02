#!/usr/bin/env python3
"""
Feature Flag System for Plotly Migration.

This module provides a comprehensive feature flag system to enable gradual
rollout of Plotly features, A/B testing, and safe deployment practices.
"""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class FeatureState(Enum):
    """Feature flag states."""

    DISABLED = "disabled"
    ENABLED = "enabled"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


@dataclass
class FeatureFlag:
    """Feature flag configuration."""

    name: str
    state: FeatureState
    description: str
    rollout_percentage: float = 0.0
    user_groups: list[str] | None = None
    conditions: dict[str, Any] | None = None
    created_at: str = ""
    updated_at: str = ""
    expires_at: str | None = None

    def __post_init__(self):
        if self.user_groups is None:
            self.user_groups = []
        if self.conditions is None:
            self.conditions = {}
        if not self.created_at:
            self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at


class FeatureFlagManager:
    """Manages feature flags for Plotly migration."""

    def __init__(self, config_path: str | None = None):
        """
        Initialize feature flag manager.

        Args:
            config_path: Optional path to feature flag configuration file
        """
        self.config_path = config_path or "configs/feature_flags.json"
        self.flags: dict[str, FeatureFlag] = {}
        self.evaluation_cache: dict[str, tuple[bool, float]] = {}
        self.cache_ttl = 300  # 5 minutes

        # Load default flags
        self._initialize_default_flags()

        # Load from config file if exists
        self._load_from_file()

    def _initialize_default_flags(self):
        """Initialize default feature flags for Plotly migration."""
        default_flags = [
            FeatureFlag(
                name="plotly_enabled",
                state=FeatureState.ENABLED,
                description="Enable Plotly chart generation system",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_monthly_bars",
                state=FeatureState.ENABLED,
                description="Use Plotly for monthly bars charts",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_donut_charts",
                state=FeatureState.ENABLED,
                description="Use Plotly for donut charts",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_waterfall",
                state=FeatureState.ENABLED,
                description="Use Plotly for waterfall charts",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_scatter",
                state=FeatureState.ENABLED,
                description="Use Plotly for scatter plots",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_layout_manager",
                state=FeatureState.ENABLED,
                description="Use Plotly layout manager for subplots",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_themes",
                state=FeatureState.ENABLED,
                description="Use Plotly theme system",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_high_dpi_export",
                state=FeatureState.ENABLED,
                description="Enable high-DPI export with Plotly",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="plotly_multi_format_export",
                state=FeatureState.ENABLED,
                description="Enable multi-format export system",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="frontend_config_export",
                state=FeatureState.ENABLED,
                description="Export chart configurations for frontend",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="json_schema_validation",
                state=FeatureState.ENABLED,
                description="Enable JSON schema validation",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="production_optimization",
                state=FeatureState.ENABLED,
                description="Enable production performance optimizations",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="template_caching",
                state=FeatureState.ENABLED,
                description="Enable template caching for performance",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="data_sampling",
                state=FeatureState.ENABLED,
                description="Enable intelligent data sampling for large datasets",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="webgl_acceleration",
                state=FeatureState.ENABLED,
                description="Enable WebGL acceleration for scatter plots",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="clustering_analysis",
                state=FeatureState.ENABLED,
                description="Enable DBSCAN clustering for scatter plots",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="performance_monitoring",
                state=FeatureState.ENABLED,
                description="Enable performance monitoring and metrics",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="batch_processing",
                state=FeatureState.ENABLED,
                description="Enable batch chart processing",
                rollout_percentage=100.0,
            ),
            FeatureFlag(
                name="experimental_features",
                state=FeatureState.DISABLED,
                description="Enable experimental Plotly features",
                rollout_percentage=0.0,
            ),
            FeatureFlag(
                name="legacy_matplotlib_fallback",
                state=FeatureState.ENABLED,
                description="Enable fallback to matplotlib on Plotly errors",
                rollout_percentage=100.0,
            ),
        ]

        for flag in default_flags:
            self.flags[flag.name] = flag

    def _load_from_file(self):
        """Load feature flags from configuration file."""
        try:
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)

                # Update flags from file
                for flag_name, flag_data in data.items():
                    if flag_name in self.flags:
                        # Update existing flag
                        flag = self.flags[flag_name]
                        flag.state = FeatureState(flag_data.get("state", flag.state.value))
                        flag.rollout_percentage = flag_data.get("rollout_percentage", flag.rollout_percentage)
                        flag.user_groups = flag_data.get("user_groups", flag.user_groups)
                        flag.conditions = flag_data.get("conditions", flag.conditions)
                        flag.expires_at = flag_data.get("expires_at", flag.expires_at)
                        flag.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # Create new flag from file
                        self.flags[flag_name] = FeatureFlag(
                            name=flag_name,
                            state=FeatureState(flag_data["state"]),
                            description=flag_data.get("description", ""),
                            rollout_percentage=flag_data.get("rollout_percentage", 0.0),
                            user_groups=flag_data.get("user_groups", []),
                            conditions=flag_data.get("conditions", {}),
                            expires_at=flag_data.get("expires_at"),
                        )
        except Exception:
            print("Warning: Could not load feature flags from {self.config_path}: {e}")

    def save_to_file(self):
        """Save current feature flags to configuration file."""
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            data = {}
            for name, flag in self.flags.items():
                data[name] = {
                    "state": flag.state.value,
                    "description": flag.description,
                    "rollout_percentage": flag.rollout_percentage,
                    "user_groups": flag.user_groups,
                    "conditions": flag.conditions,
                    "created_at": flag.created_at,
                    "updated_at": flag.updated_at,
                    "expires_at": flag.expires_at,
                }

            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception:
            print("Warning: Could not save feature flags to {self.config_path}: {e}")

    def is_enabled(self, flag_name: str, context: dict[str, Any] | None = None) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_name: Name of the feature flag
            context: Optional context for evaluation (user_id, environment, etc.)

        Returns:
            True if feature is enabled
        """
        # Check cache first
        cache_key = f"{flag_name}_{hash(str(context))}"
        if cache_key in self.evaluation_cache:
            result, timestamp = self.evaluation_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result

        # Evaluate flag
        result = self._evaluate_flag(flag_name, context or {})

        # Cache result
        self.evaluation_cache[cache_key] = (result, time.time())

        return result

    def _evaluate_flag(self, flag_name: str, context: dict[str, Any]) -> bool:
        """
        Evaluate a feature flag based on its configuration and context.

        Args:
            flag_name: Name of the feature flag
            context: Evaluation context

        Returns:
            True if feature should be enabled
        """
        if flag_name not in self.flags:
            # Unknown flags default to disabled
            return False

        flag = self.flags[flag_name]

        # Check if flag is disabled
        if flag.state == FeatureState.DISABLED:
            return False

        # Check if flag is deprecated
        if flag.state == FeatureState.DEPRECATED:
            print("Warning: Feature flag '{flag_name}' is deprecated")
            return False

        # Check expiration
        if flag.expires_at:
            try:
                expires = time.strptime(flag.expires_at, "%Y-%m-%d %H:%M:%S")
                if time.time() > time.mktime(expires):
                    return False
            except:
                pass

        # Check conditions
        if not self._evaluate_conditions(flag.conditions, context):
            return False

        # Check user groups
        if flag.user_groups and context.get("user_group"):
            if context["user_group"] not in flag.user_groups:
                return False

        # Check rollout percentage
        if flag.rollout_percentage < 100.0:
            # Use deterministic hash for consistent rollout
            user_id = context.get("user_id", "default")
            hash_input = f"{flag_name}_{user_id}"
            hash_value = hash(hash_input) % 100

            if hash_value >= flag.rollout_percentage:
                return False

        # If all checks pass, feature is enabled
        return True

    def _evaluate_conditions(self, conditions: dict[str, Any], context: dict[str, Any]) -> bool:
        """
        Evaluate feature flag conditions.

        Args:
            conditions: Flag conditions to evaluate
            context: Evaluation context

        Returns:
            True if all conditions are met
        """
        for condition_name, condition_value in conditions.items():
            context_value = context.get(condition_name)

            if isinstance(condition_value, dict):
                # Complex condition (e.g., {"min": 10, "max": 100})
                if "min" in condition_value and context_value < condition_value["min"]:
                    return False
                if "max" in condition_value and context_value > condition_value["max"]:
                    return False
                if "in" in condition_value and context_value not in condition_value["in"]:
                    return False
                if "not_in" in condition_value and context_value in condition_value["not_in"]:
                    return False
            else:
                # Simple condition (exact match)
                if context_value != condition_value:
                    return False

        return True

    def get_flag(self, flag_name: str) -> FeatureFlag | None:
        """
        Get feature flag configuration.

        Args:
            flag_name: Name of the feature flag

        Returns:
            FeatureFlag object or None if not found
        """
        return self.flags.get(flag_name)

    def set_flag(
        self,
        flag_name: str,
        state: FeatureState,
        rollout_percentage: float = 100.0,
        description: str = "",
        user_groups: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        expires_at: str | None = None,
    ):
        """
        Set or update a feature flag.

        Args:
            flag_name: Name of the feature flag
            state: Feature state
            rollout_percentage: Percentage of users to enable for
            description: Flag description
            user_groups: List of user groups to enable for
            conditions: Conditions for enabling the flag
            expires_at: Expiration timestamp
        """
        if flag_name in self.flags:
            flag = self.flags[flag_name]
            flag.state = state
            flag.rollout_percentage = rollout_percentage
            if description:
                flag.description = description
            if user_groups is not None:
                flag.user_groups = user_groups
            if conditions is not None:
                flag.conditions = conditions
            if expires_at is not None:
                flag.expires_at = expires_at
            flag.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.flags[flag_name] = FeatureFlag(
                name=flag_name,
                state=state,
                description=description,
                rollout_percentage=rollout_percentage,
                user_groups=user_groups or [],
                conditions=conditions or {},
                expires_at=expires_at,
            )

        # Clear cache for this flag
        self._clear_flag_cache(flag_name)

    def _clear_flag_cache(self, flag_name: str):
        """Clear cache entries for a specific flag."""
        keys_to_remove = [key for key in self.evaluation_cache.keys() if key.startswith(f"{flag_name}_")]
        for key in keys_to_remove:
            del self.evaluation_cache[key]

    def list_flags(self, state_filter: FeatureState | None = None) -> list[FeatureFlag]:
        """
        List all feature flags.

        Args:
            state_filter: Optional filter by state

        Returns:
            List of FeatureFlag objects
        """
        flags = list(self.flags.values())

        if state_filter:
            flags = [flag for flag in flags if flag.state == state_filter]

        return sorted(flags, key=lambda f: f.name)

    def get_enabled_features(self, context: dict[str, Any] | None = None) -> list[str]:
        """
        Get list of currently enabled features.

        Args:
            context: Optional evaluation context

        Returns:
            List of enabled feature names
        """
        enabled = []
        for flag_name in self.flags:
            if self.is_enabled(flag_name, context):
                enabled.append(flag_name)

        return enabled

    def clear_cache(self):
        """Clear evaluation cache."""
        self.evaluation_cache.clear()


def feature_flag(flag_name: str, default: bool = False):
    """
    Decorator for feature flag controlled functions.

    Args:
        flag_name: Name of the feature flag
        default: Default return value if flag is disabled

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if _global_flag_manager.is_enabled(flag_name):
                return func(*args, **kwargs)
            return default

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def conditional_import(flag_name: str, module_name: str, fallback_module: str = None):
    """
    Conditionally import modules based on feature flags.

    Args:
        flag_name: Name of the feature flag
        module_name: Module to import if flag is enabled
        fallback_module: Module to import if flag is disabled

    Returns:
        Imported module
    """
    if _global_flag_manager.is_enabled(flag_name):
        return __import__(module_name)
    if fallback_module:
        return __import__(fallback_module)
    raise ImportError(f"Feature '{flag_name}' is disabled and no fallback provided")


# Global feature flag manager instance
_global_flag_manager = FeatureFlagManager()


def get_feature_flag_manager() -> FeatureFlagManager:
    """Get the global feature flag manager instance."""
    return _global_flag_manager


def is_feature_enabled(flag_name: str, context: dict[str, Any] | None = None) -> bool:
    """
    Check if a feature is enabled using the global manager.

    Args:
        flag_name: Name of the feature flag
        context: Optional evaluation context

    Returns:
        True if feature is enabled
    """
    return _global_flag_manager.is_enabled(flag_name, context)


if __name__ == "__main__":
    # Test feature flag system
    manager = FeatureFlagManager()

    print("🏁 Feature Flag System Test")
    print("=" * 40)

    # Test basic functionality
    enabled_features = manager.get_enabled_features()
    print("✅ Enabled features: {len(enabled_features)}")

    for feature in enabled_features[:5]:  # Show first 5
        print("  - {feature}")

    if len(enabled_features) > 5:
        print("  ... and {len(enabled_features) - 5} more")

    # Test specific flags
    test_flags = [
        "plotly_enabled",
        "plotly_monthly_bars",
        "production_optimization",
        "experimental_features",
    ]

    print("\n🔍 Testing specific flags:")
    for flag in test_flags:
        enabled = manager.is_enabled(flag)
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        print("  {flag}: {status}")

    # Test rollout percentage
    manager.set_flag("test_rollout", FeatureState.ENABLED, rollout_percentage=50.0)

    enabled_count = 0
    for i in range(100):
        context = {"user_id": f"user_{i}"}
        if manager.is_enabled("test_rollout", context):
            enabled_count += 1

    print("\n📊 Rollout test (50%): {enabled_count}/100 users enabled")

    # Save configuration
    manager.save_to_file()
    print("\n💾 Configuration saved to: {manager.config_path}")

    print("\n✅ Feature flag system ready for production")
