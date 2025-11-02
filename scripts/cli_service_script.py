#!/usr/bin/env python3
"""
CLI Service Script

BaseScript implementation for executing CLI services through the script registry:
- Dynamic service discovery and execution
- Type-safe results with metadata
- Fail-fast error handling
- Integration with CLI wrapper system
"""

from datetime import datetime
from typing import Any

from cli_wrapper import CLIServiceManager
from errors import ValidationError
from result_types import ProcessingResult
from script_config import ScriptConfig
from script_registry import BaseScript, twitter_script


@twitter_script(name="cli_service", content_types=["cli_service"], requires_validation=False)
class CLIServiceScript(BaseScript):
    """
    Generalized CLI service script

    Parameters:
        service_name (str): Name of the CLI service (e.g., "yahoo_finance")
        command (str): Command to execute (e.g., "quote", "analyze")
        args (List[str]): Command arguments
        options (Dict[str, Any]): Command options
        timeout (Optional[int]): Command timeout in seconds
        retry_count (Optional[int]): Number of retries on failure
    """

    SUPPORTED_CONTENT_TYPES = ["cli_service"]
    REQUIRES_VALIDATION = False

    def __init__(self, config: ScriptConfig):
        super().__init__(config)

        # Initialize CLI service manager
        self.cli_manager = CLIServiceManager(config)

        # Available services
        self.available_services = self.cli_manager.get_available_services()

        # Setup enhanced logging adapter for consistency
        self._setup_enhanced_logger_adapter()

        self.logger.info(f"CLI service script initialized with {len(self.cli_manager.services)} services")

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

    def execute(
        self,
        service_name: str,
        command: str,
        args: list[str] | None = None,
        options: dict[str, Any] | None = None,
        timeout: int | None = None,
        retry_count: int | None = None,
        **kwargs,
    ) -> ProcessingResult:
        """Execute CLI service command"""

        start_time = datetime.now()

        try:
            # Validate inputs
            self.validate_inputs(
                service_name=service_name,
                command=command,
                args=args,
                options=options,
                timeout=timeout,
                retry_count=retry_count,
            )

            # Get service wrapper
            service_wrapper = self.cli_manager.get_service(service_name)

            # Apply custom timeout if provided
            if timeout:
                service_wrapper.timeout = timeout

            # Prepare command arguments
            cmd_args = args or []
            cmd_options = options or {}

            # Execute command with retries
            last_exception = None
            max_retries = retry_count or 1

            for attempt in range(max_retries):
                try:
                    self.logger.log_operation(
                        f"Executing CLI command (attempt {attempt + 1}/{max_retries})",
                        {
                            "service_name": service_name,
                            "command": command,
                            "args": cmd_args,
                            "options": cmd_options,
                            "timeout": service_wrapper.timeout,
                        },
                    )

                    result = service_wrapper.execute_command(command, *cmd_args, **cmd_options)

                    # Add CLI-specific metadata
                    result.add_metadata("cli_service", service_name)
                    result.add_metadata("cli_command", command)
                    result.add_metadata("cli_args", cmd_args)
                    result.add_metadata("cli_options", cmd_options)
                    result.add_metadata("execution_attempt", attempt + 1)
                    result.add_metadata("max_retries", max_retries)

                    processing_time = (datetime.now() - start_time).total_seconds()
                    result.processing_time = processing_time

                    self.logger.log_operation(
                        "CLI command executed successfully",
                        {
                            "service_name": service_name,
                            "command": command,
                            "success": result.success,
                            "attempt": attempt + 1,
                            "processing_time": processing_time,
                        },
                    )

                    return result

                except Exception as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        self.logger.log_operation(
                            "CLI command failed, retrying",
                            {
                                "service_name": service_name,
                                "command": command,
                                "attempt": attempt + 1,
                                "error": str(e),
                            },
                            level="WARNING",
                        )
                    else:
                        self.logger.log_error(
                            e,
                            {
                                "service_name": service_name,
                                "command": command,
                                "total_attempts": max_retries,
                            },
                        )

            # All attempts failed
            processing_time = (datetime.now() - start_time).total_seconds()

            error_result = ProcessingResult(
                success=False,
                operation=f"cli_{service_name}_{command}",
                error=str(last_exception),
                processing_time=processing_time,
            )

            error_result.add_error_context("service_name", service_name)
            error_result.add_error_context("command", command)
            error_result.add_error_context("total_attempts", max_retries)
            error_result.add_error_context("last_error", str(last_exception))

            return error_result

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()

            error_result = ProcessingResult(
                success=False,
                operation=f"cli_{service_name}_{command}",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("service_name", service_name)
            error_result.add_error_context("command", command)

            self.logger.log_error(
                e,
                {
                    "service_name": service_name,
                    "command": command,
                    "processing_time": processing_time,
                },
            )

            return error_result

    def validate_inputs(self, **kwargs) -> None:
        """Validate inputs before execution"""

        # Validate required parameters
        self.validate_required_parameters(**kwargs)

        # Validate parameter types
        self.validate_parameter_types(**kwargs)

        # Custom validation
        service_name = kwargs.get("service_name", "")
        command = kwargs.get("command", "")
        args = kwargs.get("args", [])
        options = kwargs.get("options", {})
        timeout = kwargs.get("timeout")
        retry_count = kwargs.get("retry_count")

        # Validate service name
        if not service_name or not service_name.strip():
            raise ValidationError("Service name cannot be empty", context={"service_name": service_name})

        if service_name not in self.available_services:
            raise ValidationError(
                f"Service '{service_name}' is not available",
                context={
                    "service_name": service_name,
                    "available_services": self.available_services,
                },
            )

        # Validate command
        if not command or not command.strip():
            raise ValidationError("Command cannot be empty", context={"command": command})

        # Validate args
        if args is not None and not isinstance(args, list):
            raise ValidationError(
                f"Args must be a list, got {type(args).__name__}",
                context={"args_type": type(args).__name__},
            )

        # Validate options
        if options is not None and not isinstance(options, dict):
            raise ValidationError(
                f"Options must be a dict, got {type(options).__name__}",
                context={"options_type": type(options).__name__},
            )

        # Validate timeout
        if timeout is not None:
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValidationError(
                    f"Timeout must be a positive integer, got {timeout}",
                    context={"timeout": timeout},
                )

        # Validate retry count
        if retry_count is not None:
            if not isinstance(retry_count, int) or retry_count < 1:
                raise ValidationError(
                    f"Retry count must be a positive integer, got {retry_count}",
                    context={"retry_count": retry_count},
                )

    def get_usage_examples(self) -> list[dict[str, Any]]:
        """Get usage examples for the script"""

        examples = []

        # Add examples for each available service
        for service_name in self.available_services:
            examples.extend(
                [
                    {
                        "description": f"Get help for {service_name} service",
                        "parameters": {
                            "service_name": service_name,
                            "command": "--help",
                        },
                    },
                    {
                        "description": f"Execute {service_name} command with options",
                        "parameters": {
                            "service_name": service_name,
                            "command": "analyze",
                            "args": ["AAPL"],
                            "options": {"output": "json"},
                        },
                    },
                ]
            )

        # Add generic examples
        examples.extend(
            [
                {
                    "description": "Execute command with retry",
                    "parameters": {
                        "service_name": "yahoo_finance",
                        "command": "quote",
                        "args": ["AAPL"],
                        "retry_count": 3,
                    },
                },
                {
                    "description": "Execute command with custom timeout",
                    "parameters": {
                        "service_name": "alpha_vantage",
                        "command": "analyze",
                        "args": ["MSFT"],
                        "timeout": 60,
                    },
                },
            ]
        )

        return examples

    def get_available_services(self) -> list[str]:
        """Get list of available CLI services"""
        return self.available_services.copy()

    def get_service_health(self) -> dict[str, Any]:
        """Get health status of all CLI services"""
        return self.cli_manager.health_check_all()

    def get_service_info(self, service_name: str) -> dict[str, Any]:
        """Get information about a specific service"""

        if service_name not in self.available_services:
            raise ValidationError(
                f"Service '{service_name}' is not available",
                context={
                    "service_name": service_name,
                    "available_services": self.available_services,
                },
            )

        wrapper = self.cli_manager.get_service(service_name)
        return wrapper.get_service_info()

    def execute_service_health_check(self, service_name: str) -> ProcessingResult:
        """Execute health check for a specific service"""

        start_time = datetime.now()

        try:
            if service_name not in self.available_services:
                raise ValidationError(
                    f"Service '{service_name}' is not available",
                    context={
                        "service_name": service_name,
                        "available_services": self.available_services,
                    },
                )

            wrapper = self.cli_manager.get_service(service_name)
            health_info = wrapper.health_check()

            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                success=health_info["status"] == "healthy",
                operation=f"health_check_{service_name}",
                processing_time=processing_time,
            )

            result.add_metadata("service_name", service_name)
            result.add_metadata("health_info", health_info)
            result.add_metadata("health_status", health_info["status"])

            return result

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()

            error_result = ProcessingResult(
                success=False,
                operation=f"health_check_{service_name}",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("service_name", service_name)

            return error_result
