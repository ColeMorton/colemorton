#!/usr/bin/env python3
"""
Script Registry System

Dynamic script discovery and execution system:
- Registry for script types and implementations
- Parameter validation and type checking
- Dynamic script loading and execution
- Script metadata and documentation
"""

import importlib
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from error_handler import ErrorHandler
from errors import ConfigurationError
from logging_config import TwitterSystemLogger
from result_types import ErrorResult, ProcessingResult
from script_config import ScriptConfig


@dataclass
class ScriptMetadata:
    """Metadata for registered scripts"""

    name: str
    description: str
    script_class: type

    # Parameter information
    required_parameters: list[str] = field(default_factory=list)
    optional_parameters: list[str] = field(default_factory=list)
    parameter_types: dict[str, type] = field(default_factory=dict)

    # Content type support
    supported_content_types: list[str] = field(default_factory=list)

    # Execution metadata
    estimated_runtime: float | None = None
    resource_requirements: dict[str, Any] = field(default_factory=dict)

    # Version and compatibility
    version: str = "1.0.0"
    requires_validation: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "script_class": self.script_class.__name__,
            "required_parameters": self.required_parameters,
            "optional_parameters": self.optional_parameters,
            "parameter_types": {k: v.__name__ for k, v in self.parameter_types.items()},
            "supported_content_types": self.supported_content_types,
            "estimated_runtime": self.estimated_runtime,
            "resource_requirements": self.resource_requirements,
            "version": self.version,
            "requires_validation": self.requires_validation,
        }


class BaseScript(ABC):
    """Base class for all generalized scripts"""

    def __init__(self, config: ScriptConfig):
        self.config = config
        self.error_handler = ErrorHandler()
        # Use standard logging instead of structured JSON logging to reduce verbosity
        import logging

        self.logger = logging.getLogger(self.__class__.__name__)

        # Script metadata
        self.metadata = self._get_script_metadata()

    @abstractmethod
    def execute(self, **kwargs) -> ProcessingResult:
        """Execute script with parameters"""

    @abstractmethod
    def validate_inputs(self, **kwargs) -> None:
        """Validate inputs before execution (fail-fast)"""

    def _get_script_metadata(self) -> ScriptMetadata:
        """Get script metadata from class annotations"""

        # Get type hints from execute method
        execute_method = self.__class__.execute
        type_hints = get_type_hints(execute_method)

        # Extract parameter information
        signature = inspect.signature(execute_method)
        required_params = []
        optional_params = []
        param_types = {}

        for param_name, param in signature.parameters.items():
            if param_name in ["self", "kwargs"]:
                continue

            param_types[param_name] = type_hints.get(param_name, Any)

            if param.default == inspect.Parameter.empty:
                required_params.append(param_name)
            else:
                optional_params.append(param_name)

        return ScriptMetadata(
            name=self.__class__.__name__,
            description=self.__class__.__doc__ or "No description available",
            script_class=self.__class__,
            required_parameters=required_params,
            optional_parameters=optional_params,
            parameter_types=param_types,
            supported_content_types=getattr(self, "SUPPORTED_CONTENT_TYPES", []),
            requires_validation=getattr(self, "REQUIRES_VALIDATION", True),
        )

    def validate_parameter_types(self, **kwargs) -> None:
        """Validate parameter types against metadata"""

        for param_name, param_value in kwargs.items():
            if param_name in self.metadata.parameter_types:
                expected_type = self.metadata.parameter_types[param_name]

                if expected_type != Any and not self._is_valid_type(param_value, expected_type):
                    self.error_handler.handle_type_validation_error(param_value, expected_type, param_name)

    def _is_valid_type(self, value: Any, expected_type: type[Any]) -> bool:
        """Check if value matches expected type, handling generic types properly"""

        if expected_type == Any:
            return True

        # Handle None values for Optional types
        if value is None:
            origin = get_origin(expected_type)
            if origin is Union:
                args = get_args(expected_type)
                return type(None) in args
            return False

        # Get the origin and args for generic types
        origin = get_origin(expected_type)

        if origin is None:
            # Simple type (not generic)
            return isinstance(value, expected_type)

        # Handle Union types (including Optional)
        if origin is Union:
            args = get_args(expected_type)
            return any(self._is_valid_type(value, arg) for arg in args)

        # Handle List types
        if origin is list or origin is list:
            if not isinstance(value, list):
                return False
            args = get_args(expected_type)
            if args:
                element_type = args[0]
                return all(self._is_valid_type(item, element_type) for item in value)
            return True

        # Handle Dict types
        if origin is dict or origin is dict:
            if not isinstance(value, dict):
                return False
            args = get_args(expected_type)
            if len(args) >= 2:
                key_type, value_type = args[0], args[1]
                return all(
                    self._is_valid_type(k, key_type) and self._is_valid_type(v, value_type) for k, v in value.items()
                )
            return True

        # For other generic types, just check the origin
        return isinstance(value, origin)

    def validate_required_parameters(self, **kwargs) -> None:
        """Validate required parameters are present"""

        missing_params = []
        for required_param in self.metadata.required_parameters:
            if required_param not in kwargs or kwargs[required_param] is None:
                missing_params.append(required_param)

        if missing_params:
            self.error_handler.handle_data_validation_error(
                kwargs, self.metadata.required_parameters, self.__class__.__name__
            )

    def get_parameter_documentation(self) -> dict[str, str]:
        """Get parameter documentation from docstring"""

        if not self.__doc__:
            return {}

        # Simple parameter documentation extraction
        # In a full implementation, this would parse docstring formats like Google or Sphinx
        return {}

    def get_usage_examples(self) -> list[dict[str, Any]]:
        """Get usage examples for the script"""

        # This would be implemented by subclasses
        return []


class ScriptRegistry:
    """Registry for dynamically discovering and executing scripts"""

    def __init__(self, config: ScriptConfig):
        self.config = config
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger(name="ScriptRegistry", log_level=config.log_level)

        # Registry storage
        self._scripts: dict[str, ScriptMetadata] = {}
        self._script_instances: dict[str, BaseScript] = {}

    def register_script(self, script_class: type[BaseScript], name: str | None = None) -> None:
        """Register a script class for dynamic discovery"""

        if not issubclass(script_class, BaseScript):
            raise ConfigurationError(
                f"Script class {script_class.__name__} must inherit from BaseScript",
                context={"script_class": script_class.__name__},
            )

        script_name = name or script_class.__name__

        # Create instance to get metadata
        try:
            instance = script_class(self.config)
            self._scripts[script_name] = instance.metadata
            self._script_instances[script_name] = instance

            # Log registration success at INFO level without metadata bloat
            self.logger.info(f"Registered script: {script_name}")

            # Log detailed metadata at DEBUG level only
            self.logger.debug(f"Script {script_name} metadata: {instance.metadata.to_dict()}")

        except Exception as e:
            self.error_handler.handle_processing_error(
                "script_registration",
                {"script_class": script_class.__name__, "script_name": script_name},
                e,
            )

    def register_script_module(self, module_path: str) -> None:
        """Register all scripts from a module"""

        try:
            module = importlib.import_module(module_path)

            for name in dir(module):
                obj = getattr(module, name)

                if inspect.isclass(obj) and issubclass(obj, BaseScript) and obj != BaseScript:
                    self.register_script(obj)

        except Exception as e:
            self.error_handler.handle_processing_error("module_registration", {"module_path": module_path}, e)

    def get_script(self, script_name: str) -> BaseScript | None:
        """Get script instance by name"""

        return self._script_instances.get(script_name)

    def get_script_metadata(self, script_name: str) -> ScriptMetadata | None:
        """Get script metadata by name"""

        return self._scripts.get(script_name)

    def list_available_scripts(self) -> list[str]:
        """List all available script names"""

        return list(self._scripts.keys())

    def list_scripts_for_content_type(self, content_type: str) -> list[str]:
        """List scripts that support a specific content type"""

        matching_scripts = []
        for script_name, metadata in self._scripts.items():
            if content_type in metadata.supported_content_types:
                matching_scripts.append(script_name)

        return matching_scripts

    def execute_script(self, script_name: str, **kwargs) -> ProcessingResult:
        """Execute a script by name with parameters"""

        script = self.get_script(script_name)
        if not script:
            return ErrorResult.from_exception(
                ConfigurationError(f"Script not found: {script_name}"),
                "script_execution",
                {
                    "script_name": script_name,
                    "available_scripts": self.list_available_scripts(),
                },
            )

        try:
            # Validate inputs
            script.validate_inputs(**kwargs)

            # Execute script
            self.logger.log_operation(f"Executing script: {script_name}", {"parameters": list(kwargs.keys())})

            result = script.execute(**kwargs)

            self.logger.log_operation(
                f"Script execution completed: {script_name}",
                {"success": result.success, "processing_time": result.processing_time},
            )

            return result

        except Exception as e:
            error_result = ErrorResult.from_exception(
                e,
                "script_execution",
                {"script_name": script_name, "parameters": kwargs},
            )

            self.logger.log_error(e, {"script_name": script_name, "parameters": kwargs})

            return error_result

    def validate_script_parameters(self, script_name: str, **kwargs) -> list[str]:
        """Validate parameters for a script without executing"""

        script = self.get_script(script_name)
        if not script:
            return [f"Script not found: {script_name}"]

        validation_errors = []

        try:
            script.validate_inputs(**kwargs)
        except Exception as e:
            validation_errors.append(str(e))

        return validation_errors

    def get_script_documentation(self, script_name: str) -> dict[str, Any]:
        """Get comprehensive documentation for a script"""

        metadata = self.get_script_metadata(script_name)
        if not metadata:
            return {}

        script = self.get_script(script_name)
        if not script:
            return metadata.to_dict()

        doc = metadata.to_dict()
        doc["parameter_documentation"] = script.get_parameter_documentation()
        doc["usage_examples"] = script.get_usage_examples()

        return doc

    def export_registry_info(self, output_file: Path) -> None:
        """Export registry information to file"""

        registry_info = {
            "total_scripts": len(self._scripts),
            "scripts": {name: metadata.to_dict() for name, metadata in self._scripts.items()},
            "content_type_support": self._get_content_type_support(),
            "export_timestamp": (
                TwitterSystemLogger().logger.handlers[0].formatter.formatTime(None, None)
                if TwitterSystemLogger().logger.handlers
                else "unknown"
            ),
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                import json

                json.dump(registry_info, f, indent=2)

        except Exception as e:
            self.error_handler.handle_processing_error("registry_export", {"output_file": str(output_file)}, e)

    def _get_content_type_support(self) -> dict[str, list[str]]:
        """Get mapping of content types to supporting scripts"""

        content_type_support: dict[str, list[str]] = {}

        for script_name, metadata in self._scripts.items():
            for content_type in metadata.supported_content_types:
                if content_type not in content_type_support:
                    content_type_support[content_type] = []
                content_type_support[content_type].append(script_name)

        return content_type_support

    def auto_discover_scripts(self, search_paths: list[Path]) -> None:
        """Auto-discover scripts in specified paths"""

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for python_file in search_path.rglob("*.py"):
                if python_file.name.startswith("_"):
                    continue

                try:
                    # Convert path to module name
                    relative_path = python_file.relative_to(search_path.parent)
                    module_name = str(relative_path.with_suffix("")).replace("/", ".")

                    self.register_script_module(module_name)

                except Exception as e:
                    self.logger.log_error(e, {"file": str(python_file), "search_path": str(search_path)})

    def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics"""

        content_type_counts: dict[str, int] = {}
        for metadata in self._scripts.values():
            for content_type in metadata.supported_content_types:
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1

        return {
            "total_scripts": len(self._scripts),
            "content_type_support": content_type_counts,
            "validation_required": sum(1 for m in self._scripts.values() if m.requires_validation),
            "average_parameters": (
                sum(len(m.required_parameters) + len(m.optional_parameters) for m in self._scripts.values())
                / len(self._scripts)
                if self._scripts
                else 0
            ),
        }


# Global registry instance
_global_registry: ScriptRegistry | None = None


def get_global_registry(config: ScriptConfig | None = None) -> ScriptRegistry:
    """Get or create global script registry"""

    global _global_registry

    if _global_registry is None:
        if config is None:
            from script_config import load_default_config

            config = load_default_config()

        _global_registry = ScriptRegistry(config)

    return _global_registry


def register_script(script_class: type[BaseScript], name: str | None = None) -> None:
    """Register a script in the global registry"""

    registry = get_global_registry()
    registry.register_script(script_class, name)


# Decorator for automatic script registration
def twitter_script(
    name: str | None = None,
    content_types: list[str] | None = None,
    requires_validation: bool = True,
):
    """Decorator for automatic script registration"""

    def decorator(script_class: type[BaseScript]):
        # Add metadata to class
        if content_types:
            script_class.SUPPORTED_CONTENT_TYPES = content_types
        script_class.REQUIRES_VALIDATION = requires_validation

        # Register script
        register_script(script_class, name)

        return script_class

    return decorator
