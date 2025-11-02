#!/usr/bin/env python3
"""
Command Execution Service

Provides a unified DASV interface for consistent script execution across all commands.
This service leverages the command-script mapping registry to provide standardized
execution patterns, parameter validation, and error handling.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.command_script_resolver import CommandScriptResolver


class ExecutionMode(Enum):
    """Execution modes for command execution"""

    DIRECT = "direct"  # Direct script execution
    SUB_AGENT = "sub_agent"  # Execute via Claude sub-agent
    CLI_ONLY = "cli_only"  # CLI services only
    VALIDATION = "validation"  # Validation-specific execution


class ExecutionStatus(Enum):
    """Execution status codes"""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    VALIDATION_FAILED = "validation_failed"
    NOT_FOUND = "not_found"


@dataclass
class ExecutionResult:
    """Result of command execution"""

    status: ExecutionStatus
    output_files: list[str]
    metadata: dict[str, Any]
    execution_time: float
    confidence_score: float | None = None
    error_message: str | None = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class CommandExecutionService:
    """
    Unified service for executing DASV commands with consistent interface.

    Provides standardized execution patterns across all command types:
    - Fundamental Analysis (discover, analyze, synthesize, validate)
    - Sector Analysis (discover, analyze, synthesize, validate)
    - Industry Analysis (discover, analyze, synthesize, validate)
    - Comparative Analysis (discover, analyze, synthesize, validate)
    - Macro Analysis (discover, analyze, synthesize, validate)
    - Trade History (discover, analyze, synthesize, validate)
    - Twitter Content Generation (all synthesis types)
    """

    def __init__(self, config_path: str = None):
        """Initialize the execution service"""
        if config_path is None:
            config_path = project_root / "scripts" / "command_script_registry.json"

        self.config_path = Path(config_path)
        self.resolver = CommandScriptResolver()
        self.base_path = project_root

        # Load path variables
        with open(self.config_path) as f:
            registry_data = json.load(f)
            self.path_variables = registry_data.get("path_variables", {})

        # Initialize execution context
        self.execution_context = {
            "start_time": None,
            "current_command": None,
            "current_phase": None,
            "temp_files": [],
        }

    def _resolve_path_variables(self, path: str) -> str:
        """Resolve path variables in a path string"""
        resolved = path
        for var, value in self.path_variables.items():
            resolved = resolved.replace(f"{{{var}}}", value)
        return resolved

    def _validate_parameters(self, domain: str, phase: str, parameters: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters for command execution"""
        errors = []

        # Get command mapping
        command_mapping = self.resolver.get_scripts_for_command(domain, phase)
        if not command_mapping:
            errors.append(f"No mapping found for {domain}:{phase}")
            return False, errors

        # Basic parameter validation based on phase
        if phase == "discover":
            # Discovery phase typically needs ticker/symbol parameters
            if domain in ["fundamental_analysis", "trade_history"] and "ticker" not in parameters:
                errors.append("ticker parameter required for discovery phase")
            elif domain in ["sector_analysis"] and "sector" not in parameters:
                errors.append("sector parameter required for discovery phase")
            elif domain in ["industry_analysis"] and "industry" not in parameters:
                errors.append("industry parameter required for discovery phase")
            elif domain in ["comparative_analysis"] and ("ticker_1" not in parameters or "ticker_2" not in parameters):
                errors.append("ticker_1 and ticker_2 parameters required for comparative analysis discovery")

        elif phase == "analyze":
            # Analysis phase needs discovery file
            if "discovery_file" not in parameters:
                errors.append("discovery_file parameter required for analysis phase")

        elif phase == "synthesize":
            # Synthesis phase needs analysis file
            if "analysis_file" not in parameters:
                errors.append("analysis_file parameter required for synthesis phase")

        elif phase == "validate":
            # Validation phase needs synthesis file
            if "synthesis_file" not in parameters:
                errors.append("synthesis_file parameter required for validation phase")

        return len(errors) == 0, errors

    def _prepare_execution_environment(self, domain: str, phase: str, parameters: dict[str, Any]) -> dict[str, str]:
        """Prepare execution environment variables"""
        env = os.environ.copy()

        # Add path variables to environment
        for var, value in self.path_variables.items():
            env[var] = self._resolve_path_variables(value)

        # Add execution metadata
        env["EXECUTION_DOMAIN"] = domain
        env["EXECUTION_PHASE"] = phase
        env["EXECUTION_TIMESTAMP"] = datetime.now().isoformat()

        # Add parameters as environment variables (prefixed)
        for key, value in parameters.items():
            env[f"PARAM_{key.upper()}"] = str(value)

        return env

    def _execute_direct_script(
        self, script_path: str, parameters: dict[str, Any], env: dict[str, str]
    ) -> ExecutionResult:
        """Execute a script directly via subprocess"""
        start_time = datetime.now()

        try:
            resolved_script = self._resolve_path_variables(script_path)
            script_file = self.base_path / resolved_script.lstrip("./")

            if not script_file.exists():
                return ExecutionResult(
                    status=ExecutionStatus.NOT_FOUND,
                    output_files=[],
                    metadata={"error": f"Script not found: {script_file}"},
                    execution_time=0.0,
                    error_message=f"Script not found: {script_file}",
                )

            # Build command arguments
            cmd = ["python", str(script_file)]
            for key, value in parameters.items():
                cmd.extend([f"--{key.replace('_', '-')}", str(value)])

            # Execute script
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=300,  # 5 minute timeout
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            if result.returncode == 0:
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output_files=self._extract_output_files(result.stdout),
                    metadata={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                        "command": " ".join(cmd),
                    },
                    execution_time=execution_time,
                )
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output_files=[],
                metadata={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "command": " ".join(cmd),
                },
                execution_time=execution_time,
                error_message=result.stderr,
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output_files=[],
                metadata={"error": "Script execution timeout"},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message="Script execution timeout (5 minutes)",
            )

        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output_files=[],
                metadata={"error": str(e)},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    def _execute_via_sub_agent(self, domain: str, phase: str, parameters: dict[str, Any]) -> ExecutionResult:
        """Execute command via Claude sub-agent"""
        start_time = datetime.now()

        try:
            # Get the appropriate sub-agent for this command/phase
            command_mapping = self.resolver.get_scripts_for_command(domain, phase)
            if not command_mapping:
                return ExecutionResult(
                    status=ExecutionStatus.NOT_FOUND,
                    output_files=[],
                    metadata={"error": f"No mapping found for {domain}:{phase}"},
                    execution_time=0.0,
                    error_message=f"No mapping found for {domain}:{phase}",
                )

            sub_agent_type = command_mapping.sub_agent

            # Prepare sub-agent prompt
            prompt = self._build_sub_agent_prompt(domain, phase, parameters, command_mapping)

            # Note: In a real implementation, this would integrate with Claude's sub-agent system
            # For now, we'll return a placeholder indicating sub-agent execution would be needed

            return ExecutionResult(
                status=ExecutionStatus.PARTIAL,
                output_files=[],
                metadata={
                    "sub_agent_type": sub_agent_type,
                    "prompt": prompt,
                    "execution_mode": "sub_agent_required",
                    "note": "Sub-agent execution requires Claude API integration",
                },
                execution_time=(datetime.now() - start_time).total_seconds(),
                warnings=["Sub-agent execution placeholder - requires Claude API integration"],
            )

        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output_files=[],
                metadata={"error": str(e)},
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    def _build_sub_agent_prompt(self, domain: str, phase: str, parameters: dict[str, Any], mapping: Any) -> str:
        """Build prompt for sub-agent execution"""
        prompt_parts = [
            f"Execute {domain} {phase} phase with the following specifications:",
            "",
            f"**Domain**: {domain}",
            f"**Phase**: {phase}",
            f"**Sub-Agent Type**: {mapping.sub_agent}",
            "",
            "**Parameters**:",
        ]

        for key, value in parameters.items():
            prompt_parts.append(f"- {key}: {value}")

        prompt_parts.extend(
            [
                "",
                f"**Primary Script**: {mapping.primary_script}",
                f"**Schema**: {mapping.schema}",
                f"**Output Directory**: {mapping.output_dir}",
                f"**File Pattern**: {mapping.file_pattern}",
                "",
                "Execute this command using the DASV framework standards with institutional-quality output.",
            ]
        )

        return "\n".join(prompt_parts)

    def _extract_output_files(self, stdout: str) -> list[str]:
        """Extract output file paths from script stdout"""
        output_files = []

        # Look for common output patterns
        lines = stdout.split("\n")
        for line in lines:
            # Look for file paths
            if "saved to" in line.lower() or "written to" in line.lower() or "output:" in line.lower():
                # Extract file path (simple heuristic)
                parts = line.split()
                for part in parts:
                    if ("/" in part or "\\" in part) and ("." in part):
                        output_files.append(part)

        return output_files

    def execute_command(
        self,
        domain: str,
        phase: str,
        parameters: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.DIRECT,
    ) -> ExecutionResult:
        """
        Execute a DASV command with unified interface

        Args:
            domain: Command domain (e.g., 'fundamental_analysis', 'sector_analysis')
            phase: DASV phase ('discover', 'analyze', 'synthesize', 'validate')
            parameters: Command parameters (ticker, date, etc.)
            mode: Execution mode (direct, sub_agent, cli_only, validation)

        Returns:
            ExecutionResult with status, output files, and metadata
        """
        start_time = datetime.now()
        self.execution_context.update(
            {
                "start_time": start_time,
                "current_command": f"{domain}:{phase}",
                "current_phase": phase,
            }
        )

        try:
            # Validate parameters
            is_valid, validation_errors = self._validate_parameters(domain, phase, parameters)
            if not is_valid:
                return ExecutionResult(
                    status=ExecutionStatus.VALIDATION_FAILED,
                    output_files=[],
                    metadata={"validation_errors": validation_errors},
                    execution_time=0.0,
                    error_message=f"Parameter validation failed: {', '.join(validation_errors)}",
                )

            # Prepare execution environment
            env = self._prepare_execution_environment(domain, phase, parameters)

            # Execute based on mode
            if mode == ExecutionMode.DIRECT:
                # Get primary script for direct execution
                command_mapping = self.resolver.get_scripts_for_command(domain, phase)
                if not command_mapping:
                    return ExecutionResult(
                        status=ExecutionStatus.NOT_FOUND,
                        output_files=[],
                        metadata={"error": f"No mapping found for {domain}:{phase}"},
                        execution_time=0.0,
                        error_message=f"No mapping found for {domain}:{phase}",
                    )

                return self._execute_direct_script(command_mapping.primary_script, parameters, env)

            if mode == ExecutionMode.SUB_AGENT:
                return self._execute_via_sub_agent(domain, phase, parameters)

            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output_files=[],
                metadata={"error": f"Unsupported execution mode: {mode}"},
                execution_time=0.0,
                error_message=f"Unsupported execution mode: {mode}",
            )

        finally:
            # Cleanup
            self.execution_context["start_time"] = None

    def execute_full_dasv_workflow(
        self,
        domain: str,
        parameters: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.DIRECT,
    ) -> dict[str, ExecutionResult]:
        """
        Execute a complete DASV workflow (Discover → Analyze → Synthesize → Validate)

        Args:
            domain: Command domain (e.g., 'fundamental_analysis')
            parameters: Base parameters for the workflow
            mode: Execution mode for all phases

        Returns:
            Dictionary mapping phases to their execution results
        """
        phases = ["discover", "analyze", "synthesize", "validate"]
        results = {}

        # Execute phases sequentially, passing outputs forward
        current_params = parameters.copy()

        for phase in phases:
            print("Executing {domain}:{phase}...")

            result = self.execute_command(domain, phase, current_params, mode)
            results[phase] = result

            # If phase failed, stop workflow
            if result.status == ExecutionStatus.FAILED:
                print(f"Workflow stopped at {phase} due to failure: {result.error_message}")
                break

            # Pass outputs to next phase
            if result.output_files:
                if phase == "discover":
                    current_params["discovery_file"] = result.output_files[0]
                elif phase == "analyze":
                    current_params["analysis_file"] = result.output_files[0]
                elif phase == "synthesize":
                    current_params["synthesis_file"] = result.output_files[0]

        return results

    def get_available_commands(self) -> dict[str, list[str]]:
        """Get list of all available commands and their phases"""
        with open(self.config_path) as f:
            registry_data = json.load(f)

        commands = {}
        for domain, phases in registry_data.get("command_mappings", {}).items():
            commands[domain] = list(phases.keys())

        return commands

    def get_command_info(self, domain: str, phase: str) -> dict[str, Any] | None:
        """Get detailed information about a specific command"""
        command_mapping = self.resolver.get_scripts_for_command(domain, phase)
        if not command_mapping:
            return None

        return {
            "domain": domain,
            "phase": phase,
            "sub_agent": command_mapping.sub_agent,
            "primary_script": command_mapping.primary_script,
            "cli_services": getattr(command_mapping, "cli_services", []),
            "schema": command_mapping.schema,
            "template": getattr(command_mapping, "template", None),
            "output_dir": command_mapping.output_dir,
            "file_pattern": command_mapping.file_pattern,
        }


def main():
    """CLI interface for the command execution service"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Command Execution Service")
    parser.add_argument("domain", help="Command domain (e.g., fundamental_analysis)")
    parser.add_argument("phase", help="DASV phase (discover, analyze, synthesize, validate)")
    parser.add_argument(
        "--mode",
        choices=["direct", "sub_agent"],
        default="direct",
        help="Execution mode",
    )
    parser.add_argument("--ticker", help="Ticker symbol (for applicable commands)")
    parser.add_argument("--sector", help="Sector symbol (for sector analysis)")
    parser.add_argument("--industry", help="Industry identifier (for industry analysis)")
    parser.add_argument("--region", help="Region identifier (for macro analysis)")
    parser.add_argument("--date", help="Analysis date (YYYYMMDD format)")
    parser.add_argument("--discovery-file", help="Discovery file path (for analyze phase)")
    parser.add_argument("--analysis-file", help="Analysis file path (for synthesize phase)")
    parser.add_argument("--synthesis-file", help="Synthesis file path (for validate phase)")
    parser.add_argument("--full-workflow", action="store_true", help="Execute complete DASV workflow")
    parser.add_argument("--list-commands", action="store_true", help="List all available commands")
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about the specified command",
    )

    args = parser.parse_args()

    # Initialize service
    service = CommandExecutionService()

    # Handle special commands
    if args.list_commands:
        commands = service.get_available_commands()
        print("Available commands:")
        for domain, phases in commands.items():
            print("  {domain}: {', '.join(phases)}")
        return

    if args.info:
        info = service.get_command_info(args.domain, args.phase)
        if info:
            print("Command Information for {args.domain}:{args.phase}")
            for key, value in info.items():
                print("  {key}: {value}")
        else:
            print("Command not found: {args.domain}:{args.phase}")
        return

    # Build parameters
    parameters = {}
    if args.ticker:
        parameters["ticker"] = args.ticker
    if args.sector:
        parameters["sector"] = args.sector
    if args.industry:
        parameters["industry"] = args.industry
    if args.region:
        parameters["region"] = args.region
    if args.date:
        parameters["date"] = args.date
    if args.discovery_file:
        parameters["discovery_file"] = args.discovery_file
    if args.analysis_file:
        parameters["analysis_file"] = args.analysis_file
    if args.synthesis_file:
        parameters["synthesis_file"] = args.synthesis_file

    # Execute command
    mode = ExecutionMode.DIRECT if args.mode == "direct" else ExecutionMode.SUB_AGENT

    if args.full_workflow:
        print("Executing full DASV workflow for {args.domain}...")
        results = service.execute_full_dasv_workflow(args.domain, parameters, mode)

        print("\nWorkflow Results:")
        for phase, result in results.items():
            print("  {phase}: {result.status.value}")
            if result.output_files:
                print("    Output files: {result.output_files}")
            if result.error_message:
                print("    Error: {result.error_message}")
    else:
        print("Executing {args.domain}:{args.phase}...")
        result = service.execute_command(args.domain, args.phase, parameters, mode)

        print("Status: {result.status.value}")
        print("Execution time: {result.execution_time:.2f}s")

        if result.output_files:
            print("Output files: {result.output_files}")

        if result.error_message:
            print("Error: {result.error_message}")

        if result.warnings:
            print("Warnings: {result.warnings}")


if __name__ == "__main__":
    main()
