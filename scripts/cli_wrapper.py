#!/usr/bin/env python3
"""
CLI Wrapper System

Provides unified interface for CLI service execution with:
- Global command detection and fallback to local execution
- Service discovery and health checking
- Memory-efficient command execution
- Local-first data strategy integration
- Fail-fast error handling with contextual information
- Structured logging and type-safe results

Standardized Logging Levels:
- INFO: API calls, primary operations, performance metrics, successful completions
- WARNING: Retries, fallbacks, degraded performance, missing optional data, recoverable errors
- ERROR: Service failures, critical issues, infrastructure problems, unrecoverable errors
"""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from error_handler import ErrorHandler

# Import new architectural components
from errors import ConfigurationError, ProcessingError, ValidationError
from result_types import ProcessingResult
from script_config import ScriptConfig
from script_registry import get_global_registry


# Global service discovery cache to prevent repeated operations
_GLOBAL_SERVICE_REGISTRY = None
_GLOBAL_SERVICE_DISCOVERY_DONE = False


class CLIServiceWrapper:
    """
    Wrapper for CLI services that handles both global and local execution modes

    Integrated with new architectural components:
    - Hierarchical error handling with context
    - Structured logging with performance tracking
    - Type-safe results with metadata
    """

    def __init__(
        self,
        service_name: str,
        config: ScriptConfig | None = None,
        scripts_dir: Path | None = None,
    ):
        self.service_name = service_name

        # Validate service name
        self._validate_service_name(service_name)

        # Initialize configuration
        if config:
            self.config = config
            self.scripts_dir = config.base_path / "scripts"
        else:
            self.scripts_dir = scripts_dir or Path(__file__).parent
            self.config = None

        # Initialize new architectural components
        self.error_handler = ErrorHandler()
        # Disable structured JSON logging to reduce verbosity - use standard logging instead
        import logging

        self.logger = logging.getLogger(f"cli_wrapper.{service_name}")

        # Enhanced logging adapter with consistent method binding
        self._setup_enhanced_logger_adapter()

        # CLI service configuration
        self.cli_script_name = f"{service_name}_cli.py"
        self.cli_script_path = self.scripts_dir / self.cli_script_name
        self.global_command_name = f"{service_name}_cli"

        # Configuration-based settings
        self.timeout = 30  # Default timeout
        self.retry_count = 1  # Default retry count
        self.use_cache = False  # Default cache usage

        if self.config:
            # Apply configuration-based settings
            self.timeout = getattr(self.config, "cli_timeout", 30)
            self.retry_count = getattr(self.config, "cli_retry_count", 1)
            self.use_cache = getattr(self.config, "cli_use_cache", False)

        # Execution modes
        self.global_available = self._check_global_availability()
        self.local_available = self._check_local_availability()

        # Log initialization success at INFO level without verbose context
        self.logger.info(f"CLI wrapper initialized for {service_name}")

        # Log detailed configuration at DEBUG level
        self.logger.debug(
            f"CLI wrapper config for {service_name}: global={self.global_available}, local={self.local_available}"
        )

    def _setup_enhanced_logger_adapter(self):
        """Setup enhanced logger with consistent adapter methods"""

        def log_operation(message, context=None, level="INFO"):
            """Enhanced operation logging with context and performance data"""
            if context:
                context_str = f" | Context: {context}"
            else:
                context_str = ""

            log_message = f"Operation: {message}{context_str}"

            if level == "WARNING":
                self.logger.warning(log_message)
            elif level == "ERROR":
                self.logger.error(log_message)
            else:
                self.logger.info(log_message)

        def log_error(message, error=None, context=None):
            """Enhanced error logging with structured context"""
            error_details = ""
            if error:
                error_details = f" | Error: {str(error)}"
            if context:
                error_details += f" | Context: {context}"

            self.logger.error(f"Operation failed: {message}{error_details}")

        def log_api_call(service, command, args=None, response_time=None, status=None, details=None):
            """Detailed API call logging"""
            args_str = f"({', '.join(map(str, args))})" if args else ""
            timing_str = f" [{response_time:.2f}s]" if response_time else ""
            status_str = f" -> {status}" if status else ""
            details_str = f" | {details}" if details else ""

            message = f"API Call: {service}.{command}{args_str}{timing_str}{status_str}{details_str}"
            self.logger.info(message)

        # Bind enhanced methods to logger instance
        self.logger.log_operation = log_operation
        self.logger.log_error = log_error
        self.logger.log_api_call = log_api_call

    def _validate_service_name(self, service_name: str) -> None:
        """Validate service name using fail-fast approach"""
        if not service_name or not service_name.strip():
            raise ValidationError("Service name cannot be empty", context={"service_name": service_name})

        if not service_name.replace("_", "").isalnum():
            raise ValidationError(
                f"Invalid service name format: {service_name}",
                context={"valid_format": "Alphanumeric with underscores only"},
            )

        if len(service_name) > 50:
            raise ValidationError(
                f"Service name too long: {len(service_name)} characters",
                context={"max_length": 50},
            )

    def _check_global_availability(self) -> bool:
        """Check if CLI service is available as global command"""
        try:
            # Check if command exists in PATH
            global_path = shutil.which(self.global_command_name)
            is_available = global_path is not None

            # Log availability check at DEBUG level to reduce verbosity
            self.logger.debug(f"Global availability check for {self.service_name}: {is_available}")

            return is_available
        except Exception as e:
            self.error_handler.handle_processing_error(
                "global_availability_check",
                {
                    "service_name": self.service_name,
                    "global_command": self.global_command_name,
                },
                e,
                fail_fast=False,
            )
            return False

    def _check_local_availability(self) -> bool:
        """Check if CLI service is available as local Python script"""
        try:
            is_available = self.cli_script_path.exists() and self.cli_script_path.is_file()

            # Log availability check at DEBUG level to reduce verbosity
            self.logger.debug(f"Local availability check for {self.service_name}: {is_available}")

            return is_available
        except Exception as e:
            self.error_handler.handle_processing_error(
                "local_availability_check",
                {
                    "service_name": self.service_name,
                    "cli_script_path": str(self.cli_script_path),
                },
                e,
                fail_fast=False,
            )
            return False

    def is_available(self) -> bool:
        """Check if CLI service is available in any form"""
        available = self.global_available or self.local_available

        if not available:
            self.logger.log_operation(  # type: ignore[attr-defined]
                f"Service {self.service_name} is not available",
                {
                    "global_available": self.global_available,
                    "local_available": self.local_available,
                    "cli_script_path": str(self.cli_script_path),
                    "global_command": self.global_command_name,
                },
                level="WARNING",
            )

        return available

    def execute_command(self, command: str, *args, **kwargs) -> ProcessingResult:
        """
        Execute CLI command with fallback mechanisms

        Args:
            command: Command to execute (e.g., 'analyze', 'quote')
            *args: Command arguments
            **kwargs: Command options

        Returns:
            ProcessingResult with execution details and metadata
        """
        start_time = datetime.now()

        # Validate inputs
        if not command or not command.strip():
            raise ValidationError("Command cannot be empty", context={"service_name": self.service_name})

        if not self.is_available():
            raise ConfigurationError(
                f"CLI service '{self.service_name}' is not available",
                context={
                    "service_name": self.service_name,
                    "global_available": self.global_available,
                    "local_available": self.local_available,
                    "cli_script_path": str(self.cli_script_path),
                },
            )

        try:
            # Build command arguments
            cmd_args = [command] + list(args)

            # Add options from kwargs
            for key, value in kwargs.items():
                if key.startswith("_"):
                    continue
                option_name = f"--{key.replace('_', '-')}"
                if isinstance(value, bool):
                    if value:
                        cmd_args.append(option_name)
                else:
                    cmd_args.extend([option_name, str(value)])

            # Demote verbose command start logging to DEBUG level to reduce noise
            self.logger.debug(f"Starting CLI command: {self.service_name}.{command}")

            # Try global command first
            if self.global_available:
                try:
                    success, stdout, stderr = self._execute_global_command(cmd_args)
                    execution_time = (datetime.now() - start_time).total_seconds()

                    return self._create_result(success, stdout, stderr, "global", execution_time, cmd_args)
                except Exception as e:
                    self.logger.log_operation(  # type: ignore[attr-defined]
                        "Global command failed, falling back to local",
                        {
                            "service_name": self.service_name,
                            "error": str(e),
                            "command": command,
                        },
                        level="WARNING",
                    )

            # Fall back to local execution
            if self.local_available:
                try:
                    success, stdout, stderr = self._execute_local_command(cmd_args)
                    execution_time = (datetime.now() - start_time).total_seconds()

                    return self._create_result(success, stdout, stderr, "local", execution_time, cmd_args)
                except Exception as e:
                    self.error_handler.handle_processing_error(
                        "local_command_execution",
                        {
                            "service_name": self.service_name,
                            "command": command,
                            "cmd_args": cmd_args,
                        },
                        e,
                    )

            raise ConfigurationError(
                f"No execution method available for {self.service_name}",
                context={
                    "service_name": self.service_name,
                    "global_available": self.global_available,
                    "local_available": self.local_available,
                },
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            if not isinstance(e, (ValidationError, ConfigurationError, ProcessingError)):
                # Wrap unexpected errors in ProcessingError
                raise ProcessingError(
                    f"CLI command execution failed: {str(e)}",
                    pipeline_stage="cli_command_execution",
                    input_data={
                        "service_name": self.service_name,
                        "command": command,
                        "args": list(args),
                        "execution_time": execution_time,
                    },
                    context={"original_error": str(e)},
                )
            raise

    def _create_result(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        execution_mode: str,
        execution_time: float,
        cmd_args: list[str],
    ) -> ProcessingResult:
        """Create ProcessingResult from CLI execution"""

        result = ProcessingResult(
            success=success,
            operation=f"cli_{self.service_name}_{cmd_args[0]}",
            content=stdout if success else None,
            error=stderr if not success else None,
            processing_time=execution_time,
        )

        # Add metadata
        result.add_metadata("service_name", self.service_name)
        result.add_metadata("execution_mode", execution_mode)
        result.add_metadata("command", cmd_args[0] if cmd_args else "")
        result.add_metadata("full_command", cmd_args)

        if not success:
            result.add_error_context("stderr", stderr)
            result.add_error_context("stdout", stdout)
            result.add_error_context("execution_mode", execution_mode)

        # Demote verbose completion logging to DEBUG level to reduce noise
        status = "SUCCESS" if success else "FAILED"
        self.logger.debug(
            f"CLI command {status}: {self.service_name}.{cmd_args[0] if cmd_args else 'unknown'} [{execution_time:.2f}s]"
        )

        return result

    def _execute_global_command(self, args: list[str]) -> tuple[bool, str, str]:
        """Execute command as global CLI"""
        cmd = [self.global_command_name] + args
        command_name = args[0] if args else "unknown"
        start_time = datetime.now()

        self.logger.log_operation(  # type: ignore[attr-defined]
            f"Executing global command: {self.service_name}.{command_name}",
            {
                "service_name": self.service_name,
                "full_command": " ".join(cmd),
                "args_count": len(args),
                "timeout": self.timeout,
                "execution_mode": "global",
            },
        )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.scripts_dir.parent,
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            success = result.returncode == 0

            # Enhanced API call logging
            status = f"SUCCESS (rc={result.returncode})" if success else f"FAILED (rc={result.returncode})"
            details = f"stdout={len(result.stdout)} chars, stderr={len(result.stderr)} chars"

            self.logger.log_api_call(  # type: ignore[attr-defined]
                service=self.service_name,
                command=command_name,
                args=args[1:] if len(args) > 1 else None,
                response_time=execution_time,
                status=status,
                details=details,
            )

            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            # Log timeout as failed API call
            self.logger.log_api_call(  # type: ignore[attr-defined]
                service=self.service_name,
                command=command_name,
                args=args[1:] if len(args) > 1 else None,
                response_time=execution_time,
                status="TIMEOUT",
                details=f"Timed out after {self.timeout}s",
            )

            raise ProcessingError(
                f"Global command timed out: {' '.join(cmd)}",
                pipeline_stage="global_command_execution",
                input_data={
                    "service_name": self.service_name,
                    "command": cmd,
                    "timeout": self.timeout,
                },
                context={"timeout_error": str(e)},
            )
        except subprocess.CalledProcessError as e:
            raise ProcessingError(
                f"Global command failed with return code {e.returncode}",
                pipeline_stage="global_command_execution",
                input_data={
                    "service_name": self.service_name,
                    "command": cmd,
                    "return_code": e.returncode,
                },
                context={"stderr": e.stderr, "stdout": e.stdout},
            )
        except Exception as e:
            raise ProcessingError(
                f"Global command execution failed: {str(e)}",
                pipeline_stage="global_command_execution",
                input_data={"service_name": self.service_name, "command": cmd},
                context={"original_error": str(e)},
            )

    def _execute_local_command(self, args: list[str]) -> tuple[bool, str, str]:
        """Execute command as local Python script"""
        cmd = [sys.executable, str(self.cli_script_path)] + args
        command_name = args[0] if args else "unknown"
        start_time = datetime.now()

        # Demote verbose local execution logging to DEBUG level to reduce noise
        self.logger.debug(f"Executing local CLI: {self.service_name}.{command_name}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.scripts_dir.parent,
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            success = result.returncode == 0

            # Enhanced API call logging
            status = f"SUCCESS (rc={result.returncode})" if success else f"FAILED (rc={result.returncode})"
            details = f"stdout={len(result.stdout)} chars, stderr={len(result.stderr)} chars, script={self.cli_script_path.name}"

            self.logger.log_api_call(  # type: ignore[attr-defined]
                service=self.service_name,
                command=command_name,
                args=args[1:] if len(args) > 1 else None,
                response_time=execution_time,
                status=status,
                details=details,
            )

            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            # Log timeout as failed API call
            self.logger.log_api_call(  # type: ignore[attr-defined]
                service=self.service_name,
                command=command_name,
                args=args[1:] if len(args) > 1 else None,
                response_time=execution_time,
                status="TIMEOUT",
                details=f"Timed out after {self.timeout}s, script={self.cli_script_path.name}",
            )

            raise ProcessingError(
                f"Local command timed out: {' '.join(cmd)}",
                pipeline_stage="local_command_execution",
                input_data={
                    "service_name": self.service_name,
                    "command": cmd,
                    "timeout": self.timeout,
                },
                context={"timeout_error": str(e)},
            )
        except subprocess.CalledProcessError as e:
            raise ProcessingError(
                f"Local command failed with return code {e.returncode}",
                pipeline_stage="local_command_execution",
                input_data={
                    "service_name": self.service_name,
                    "command": cmd,
                    "return_code": e.returncode,
                },
                context={"stderr": e.stderr, "stdout": e.stdout},
            )
        except Exception as e:
            raise ProcessingError(
                f"Local command execution failed: {str(e)}",
                pipeline_stage="local_command_execution",
                input_data={"service_name": self.service_name, "command": cmd},
                context={"original_error": str(e)},
            )

    def get_service_info(self) -> dict[str, Any]:
        """Get service information and availability"""
        return {
            "service_name": self.service_name,
            "cli_script_path": str(self.cli_script_path),
            "global_command_name": self.global_command_name,
            "global_available": self.global_available,
            "local_available": self.local_available,
            "is_available": self.is_available(),
            "execution_mode": (
                "global" if self.global_available else "local" if self.local_available else "unavailable"
            ),
        }

    def health_check(self) -> dict[str, Any]:
        """Perform health check on CLI service"""
        health_info = {
            "service_name": self.service_name,
            "status": "unknown",
            "details": {},
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        }

        try:
            if not self.is_available():
                health_info["status"] = "unavailable"
                health_info["details"]["error"] = "CLI service not found"
                return health_info

            # Try to get version or help info
            try:
                result = self.execute_command("--help")
                if result.success:
                    health_info["status"] = "healthy"
                    health_info["details"]["help_available"] = True
                else:
                    health_info["status"] = "unhealthy"
                    health_info["details"]["error"] = result.error
            except Exception as e:
                health_info["status"] = "unhealthy"
                health_info["details"]["error"] = str(e)

            health_info["details"]["service_info"] = self.get_service_info()

        except Exception as e:
            health_info["status"] = "error"
            health_info["details"]["error"] = str(e)

        return health_info


class CLIServiceManager:
    """
    Manager for all CLI services with discovery and health checking

    Integrated with new architectural components:
    - Structured logging for service management
    - Error handling for service discovery
    """

    def __init__(self, config: ScriptConfig | None = None, scripts_dir: Path | None = None):
        # Initialize configuration
        if config:
            self.config = config
            self.scripts_dir = config.base_path / "scripts"
        else:
            self.scripts_dir = scripts_dir or Path(__file__).parent
            self.config = None

        # Use standard logging with enhanced adapter
        import logging

        self.logger = logging.getLogger("cli_service_manager")

        # Apply the same enhanced logging adapter as CLIServiceWrapper
        self._setup_enhanced_logger_adapter()
        self.error_handler = ErrorHandler()
        self.services = {}

        # Initialize script registry integration
        self.script_registry = None
        if config:
            try:
                self.script_registry = get_global_registry(config)
            except Exception as e:
                self.logger.log_operation(  # type: ignore[attr-defined]
                    "Could not initialize script registry",
                    {"error": str(e)},
                    level="WARNING",
                )

        # Validate scripts directory
        self._validate_scripts_directory()

        self._discover_services()

        # Register CLI services with script registry if available
        if self.script_registry:
            self._register_cli_services()

    def _setup_enhanced_logger_adapter(self):
        """Setup enhanced logger with consistent adapter methods (shared with CLIServiceWrapper)"""

        def log_operation(message, context=None, level="INFO"):
            """Enhanced operation logging with context and performance data"""
            if context:
                context_str = f" | Context: {context}"
            else:
                context_str = ""

            log_message = f"Operation: {message}{context_str}"

            if level == "WARNING":
                self.logger.warning(log_message)
            elif level == "ERROR":
                self.logger.error(log_message)
            else:
                self.logger.info(log_message)

        def log_error(message, error=None, context=None):
            """Enhanced error logging with structured context"""
            error_details = ""
            if error:
                error_details = f" | Error: {str(error)}"
            if context:
                error_details += f" | Context: {context}"

            self.logger.error(f"Operation failed: {message}{error_details}")

        def log_api_call(service, command, args=None, response_time=None, status=None, details=None):
            """Detailed API call logging"""
            args_str = f"({', '.join(map(str, args))})" if args else ""
            timing_str = f" [{response_time:.2f}s]" if response_time else ""
            status_str = f" -> {status}" if status else ""
            details_str = f" | {details}" if details else ""

            message = f"API Call: {service}.{command}{args_str}{timing_str}{status_str}{details_str}"
            self.logger.info(message)

        # Bind enhanced methods to logger instance
        self.logger.log_operation = log_operation
        self.logger.log_error = log_error
        self.logger.log_api_call = log_api_call

    def _validate_scripts_directory(self) -> None:
        """Validate scripts directory using fail-fast approach"""
        if not self.scripts_dir.exists():
            raise ConfigurationError(
                f"Scripts directory does not exist: {self.scripts_dir}",
                context={"scripts_dir": str(self.scripts_dir)},
            )

        if not self.scripts_dir.is_dir():
            raise ConfigurationError(
                f"Scripts path is not a directory: {self.scripts_dir}",
                context={"scripts_dir": str(self.scripts_dir)},
            )

    def _discover_services(self) -> None:
        """Discover available CLI services"""
        # Use global cache to prevent repeated service discovery
        global _GLOBAL_SERVICE_REGISTRY, _GLOBAL_SERVICE_DISCOVERY_DONE

        if _GLOBAL_SERVICE_DISCOVERY_DONE and _GLOBAL_SERVICE_REGISTRY:
            # Use cached services instead of rediscovering
            self.services = _GLOBAL_SERVICE_REGISTRY
            return

        # Only log service discovery start once globally
        if not _GLOBAL_SERVICE_DISCOVERY_DONE:
            self.logger.debug(f"Starting CLI service discovery in {self.scripts_dir}")
            _GLOBAL_SERVICE_DISCOVERY_DONE = True

        # Expected financial CLI services
        expected_services = [
            "yahoo_finance",
            "alpha_vantage",
            "fred_economic",
            "coingecko",
            "fmp",
            "sec_edgar",
            "imf",
            "trade_history",
        ]

        discovered_count = 0
        available_count = 0

        for service_name in expected_services:
            try:
                wrapper = CLIServiceWrapper(service_name, self.config, self.scripts_dir)
                self.services[service_name] = wrapper
                discovered_count += 1

                if wrapper.is_available():
                    available_count += 1
                    # Log service availability at DEBUG level to reduce verbosity
                    self.logger.debug(f"Service {service_name} available")
                else:
                    # Log service unavailability at WARNING level without verbose context
                    self.logger.warning(f"Service {service_name} not available")

            except Exception as e:
                self.error_handler.handle_processing_error(
                    "service_discovery",
                    {
                        "service_name": service_name,
                        "scripts_dir": str(self.scripts_dir),
                    },
                    e,
                    fail_fast=False,
                )

        # Cache the discovered services globally to prevent repeated discovery
        _GLOBAL_SERVICE_REGISTRY = self.services

        # Demote service discovery completion to DEBUG to reduce noise
        self.logger.debug(
            f"CLI service discovery completed: {available_count}/{len(expected_services)} services available"
        )

    def _register_cli_services(self) -> None:
        """Register CLI services with the script registry"""
        if not self.script_registry:
            return

        try:
            # Import and register CLI service script
            from cli_service_script import CLIServiceScript

            # Check if already registered
            if "cli_service" not in self.script_registry.list_available_scripts():
                self.script_registry.register_script(CLIServiceScript, "cli_service")

                self.logger.log_operation(  # type: ignore[attr-defined]
                    "Registered CLI service script with registry",
                    {
                        "available_services": self.get_available_services(),
                        "total_services": len(self.services),
                    },
                )

        except Exception as e:
            self.error_handler.handle_processing_error(
                "cli_service_registration",
                {"available_services": self.get_available_services()},
                e,
                fail_fast=False,
            )

    def execute_via_registry(self, service_name: str, command: str, *args, **kwargs) -> ProcessingResult:
        """Execute CLI service via script registry"""
        if not self.script_registry:
            raise ConfigurationError(
                "Script registry not available for CLI service execution",
                context={"service_name": service_name, "command": command},
            )

        try:
            return self.script_registry.execute_script(
                "cli_service",
                service_name=service_name,
                command=command,
                args=list(args),
                options=kwargs,
            )
        except Exception as e:
            self.error_handler.handle_processing_error(
                "registry_cli_execution",
                {"service_name": service_name, "command": command},
                e,
            )

    def get_service(self, service_name: str) -> CLIServiceWrapper:
        """Get CLI service wrapper"""
        if not service_name or not service_name.strip():
            raise ValidationError("Service name cannot be empty", context={"service_name": service_name})

        if service_name not in self.services:
            raise ConfigurationError(
                f"Service '{service_name}' not found",
                context={
                    "service_name": service_name,
                    "available_services": list(self.services.keys()),
                },
            )

        wrapper = self.services[service_name]
        if not wrapper.is_available():
            raise ConfigurationError(
                f"Service '{service_name}' is not available",
                context={
                    "service_name": service_name,
                    "global_available": wrapper.global_available,
                    "local_available": wrapper.local_available,
                },
            )

        return wrapper

    def get_available_services(self) -> list[str]:
        """Get list of available service names"""
        return [name for name, wrapper in self.services.items() if wrapper.is_available()]

    def get_service_status(self) -> dict[str, Any]:
        """Get status of all services"""
        status = {
            "total_services": len(self.services),
            "available_services": len(self.get_available_services()),
            "services": {},
        }

        for name, wrapper in self.services.items():
            status["services"][name] = wrapper.get_service_info()

        return status

    def health_check_all(self) -> dict[str, Any]:
        """Perform health check on all services"""
        health_results = {
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "summary": {
                "total": len(self.services),
                "healthy": 0,
                "unhealthy": 0,
                "unavailable": 0,
            },
            "services": {},
        }

        for name, wrapper in self.services.items():
            health_info = wrapper.health_check()
            health_results["services"][name] = health_info

            status = health_info["status"]
            if status == "healthy":
                health_results["summary"]["healthy"] += 1
            elif status == "unavailable":
                health_results["summary"]["unavailable"] += 1
            else:
                health_results["summary"]["unhealthy"] += 1

        return health_results


# Global service manager instance
_service_manager = None


def get_service_manager(config: ScriptConfig | None = None) -> CLIServiceManager:
    """Get global service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = CLIServiceManager(config)
    return _service_manager


def get_cli_service(service_name: str) -> CLIServiceWrapper:
    """Get CLI service wrapper by name"""
    return get_service_manager().get_service(service_name)


def execute_cli_command(service_name: str, command: str, *args, **kwargs) -> ProcessingResult:
    """
    Execute CLI command with automatic service discovery and fallback

    Args:
        service_name: Name of the service (e.g., 'yahoo_finance')
        command: Command to execute (e.g., 'analyze')
        *args: Command arguments
        **kwargs: Command options

    Returns:
        ProcessingResult with execution details and metadata
    """
    service = get_cli_service(service_name)
    return service.execute_command(command, *args, **kwargs)


def execute_cli_command_legacy(service_name: str, command: str, *args, **kwargs) -> tuple[bool, str, str]:
    """
    Execute CLI command with legacy tuple return for backward compatibility

    Args:
        service_name: Name of the service (e.g., 'yahoo_finance')
        command: Command to execute (e.g., 'analyze')
        *args: Command arguments
        **kwargs: Command options

    Returns:
        Tuple of (success, stdout, stderr)
    """
    result = execute_cli_command(service_name, command, *args, **kwargs)
    return result.success, result.content or "", result.error or ""


if __name__ == "__main__":
    # Example usage and testing
    import pprint

    # Test service discovery
    manager = get_service_manager()

    print("=== CLI Service Status ===")
    pprint.pprint(manager.get_service_status())

    print("\n=== Health Check ===")
    pprint.pprint(manager.health_check_all())

    # Test individual service
    available_services = manager.get_available_services()
    if available_services:
        test_service = available_services[0]
        print("\n=== Testing {test_service} service ===")
        try:
            service = get_cli_service(test_service)
            result = service.execute_command("--help")
            print("Success: {result.success}")
            print(f"Output: {result.content[:200] if result.content else 'No output'}...")
        except Exception:
            print("Error: {e}")
