#!/usr/bin/env python3
"""
Unified Command Interface

Single entry point for all DASV command execution with consistent interface.
Integrates command execution service, workflow orchestrator, and script resolver
to provide a unified experience across all analysis domains.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.command_execution_service import (
    CommandExecutionService,
    ExecutionMode,
    ExecutionStatus,
)
from scripts.utils.command_script_resolver import CommandScriptResolver
from scripts.utils.dasv_workflow_orchestrator import (
    DASVWorkflowOrchestrator,
)


class UnifiedCommandInterface:
    """
    Unified interface for all DASV command execution.

    Provides:
    - Single entry point for all commands
    - Consistent parameter handling
    - Automatic workflow routing
    - Quality gate enforcement
    - Comprehensive logging and monitoring
    """

    def __init__(self):
        """Initialize the unified command interface"""
        self.execution_service = CommandExecutionService()
        self.orchestrator = DASVWorkflowOrchestrator()
        self.resolver = CommandScriptResolver()

        # Command aliases and shortcuts
        self.command_aliases = {
            "fa": "fundamental_analysis",
            "sa": "sector_analysis",
            "ia": "industry_analysis",
            "ca": "comparative_analysis",
            "ma": "macro_analysis",
            "th": "trade_history",
        }

        # Phase aliases
        self.phase_aliases = {
            "d": "discover",
            "a": "analyze",
            "s": "synthesize",
            "v": "validate",
        }

    def _resolve_aliases(self, command: str, phase: str) -> tuple[str, str]:
        """Resolve command and phase aliases"""
        resolved_command = self.command_aliases.get(command, command)
        resolved_phase = self.phase_aliases.get(phase, phase)
        return resolved_command, resolved_phase

    def _validate_command_parameters(
        self, domain: str, phase: str, parameters: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate command parameters"""
        errors = []

        # Domain-specific parameter validation
        if domain == "fundamental_analysis":
            if "ticker" not in parameters:
                errors.append("ticker parameter required for fundamental analysis")

        elif domain == "sector_analysis":
            if "sector" not in parameters:
                errors.append("sector parameter required for sector analysis")

        elif domain == "industry_analysis":
            if "industry" not in parameters:
                errors.append("industry parameter required for industry analysis")

        elif domain == "comparative_analysis":
            if "ticker_1" not in parameters or "ticker_2" not in parameters:
                errors.append("ticker_1 and ticker_2 parameters required for comparative analysis")

        elif domain == "macro_analysis":
            if "region" not in parameters:
                errors.append("region parameter required for macro analysis")

        elif domain == "trade_history":
            if phase == "discover" and "ticker" not in parameters:
                errors.append("ticker parameter required for trade history")

        # Common parameter validation
        if "date" not in parameters:
            # Generate current date if not provided
            parameters["date"] = datetime.now().strftime("%Y%m%d")

        return len(errors) == 0, errors

    def execute_single_phase(
        self,
        domain: str,
        phase: str,
        parameters: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.DIRECT,
    ) -> dict[str, Any]:
        """
        Execute a single DASV phase

        Args:
            domain: Analysis domain
            phase: DASV phase
            parameters: Command parameters
            mode: Execution mode

        Returns:
            Execution result dictionary
        """
        # Resolve aliases
        domain, phase = self._resolve_aliases(domain, phase)

        # Validate parameters
        is_valid, validation_errors = self._validate_command_parameters(domain, phase, parameters)
        if not is_valid:
            return {
                "status": "validation_failed",
                "errors": validation_errors,
                "domain": domain,
                "phase": phase,
            }

        print("🔧 Executing {domain}:{phase}")
        print("   📋 Parameters: {parameters}")

        # Execute command
        result = self.execution_service.execute_command(domain, phase, parameters, mode)

        # Format response
        response = {
            "status": result.status.value,
            "domain": domain,
            "phase": phase,
            "execution_time": result.execution_time,
            "output_files": result.output_files,
            "confidence_score": result.confidence_score,
            "metadata": result.metadata,
        }

        if result.error_message:
            response["error_message"] = result.error_message

        if result.warnings:
            response["warnings"] = result.warnings

        # Print results
        status_emoji = "✅" if result.status == ExecutionStatus.SUCCESS else "❌"
        print("   {status_emoji} Status: {result.status.value}")
        print("   ⏱️  Time: {result.execution_time:.2f}s")

        if result.output_files:
            print("   📄 Output: {result.output_files[0]}")

        if result.confidence_score:
            print("   🎯 Confidence: {result.confidence_score:.2f}")

        if result.warnings:
            for warning in result.warnings:
                print("   ⚠️  {warning}")

        return response

    def execute_full_workflow(
        self,
        domain: str,
        parameters: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.DIRECT,
        workflow_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a complete DASV workflow

        Args:
            domain: Analysis domain
            parameters: Workflow parameters
            mode: Execution mode
            workflow_id: Optional workflow identifier

        Returns:
            Workflow result dictionary
        """
        # Resolve aliases
        domain = self.command_aliases.get(domain, domain)

        # Validate parameters
        is_valid, validation_errors = self._validate_command_parameters(domain, "discover", parameters)
        if not is_valid:
            return {
                "status": "validation_failed",
                "errors": validation_errors,
                "domain": domain,
            }

        print("🚀 Starting full DASV workflow for {domain}")
        print("   📋 Parameters: {parameters}")

        # Execute workflow
        result = self.orchestrator.execute_workflow(domain, parameters, mode, workflow_id)

        # Format response
        response = {
            "status": result.status.value,
            "domain": result.domain,
            "workflow_id": result.workflow_id,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration": (str(result.end_time - result.start_time) if result.end_time else None),
            "phases_completed": len(result.phase_results),
            "final_outputs": result.final_outputs,
            "overall_confidence": result.overall_confidence,
            "quality_summary": result.quality_summary,
        }

        # Add phase details
        response["phase_results"] = {}
        for phase, phase_result in result.phase_results.items():
            response["phase_results"][phase] = {
                "status": phase_result.execution_result.status.value,
                "quality_gate": phase_result.quality_gate_result.value,
                "confidence_score": phase_result.confidence_score,
                "quality_issues": phase_result.quality_issues,
                "output_files": phase_result.execution_result.output_files,
            }

        return response

    def get_command_info(self, domain: str, phase: str | None = None) -> dict[str, Any]:
        """Get information about available commands"""
        # Resolve aliases
        domain = self.command_aliases.get(domain, domain)

        if phase:
            phase = self.phase_aliases.get(phase, phase)
            # Get specific command info
            command_info = self.execution_service.get_command_info(domain, phase)
            if command_info:
                return command_info
            return {"error": f"Command not found: {domain}:{phase}"}
        # Get all phases for domain
        available_commands = self.execution_service.get_available_commands()
        if domain in available_commands:
            return {"domain": domain, "phases": available_commands[domain]}
        return {"error": f"Domain not found: {domain}"}

    def list_all_commands(self) -> dict[str, Any]:
        """List all available commands and workflows"""
        commands = self.execution_service.get_available_commands()
        workflows = self.orchestrator.list_available_workflows()

        return {
            "commands": commands,
            "workflows": workflows,
            "command_aliases": self.command_aliases,
            "phase_aliases": self.phase_aliases,
        }

    def execute_command_string(self, command_string: str, mode: ExecutionMode = ExecutionMode.DIRECT) -> dict[str, Any]:
        """
        Execute a command from a string format

        Examples:
            "fa:d AAPL"  # fundamental_analysis discover AAPL
            "sa:workflow XLRE"  # sector_analysis full workflow for XLRE
            "ca:s ticker_1=AAPL ticker_2=MSFT date=20250814"  # comparative_analysis synthesize
        """
        try:
            parts = command_string.strip().split()
            if len(parts) < 2:
                return {"error": "Invalid command format. Expected: domain:phase parameters"}

            # Parse command and phase
            command_phase = parts[0]
            if ":" not in command_phase:
                return {"error": "Invalid command format. Expected: domain:phase"}

            domain, phase = command_phase.split(":", 1)

            # Parse parameters
            parameters = {}

            # Handle simple ticker/symbol/identifier case
            if len(parts) == 2 and "=" not in parts[1]:
                # Simple case: domain:phase TICKER
                if domain in ["fundamental_analysis", "fa", "trade_history", "th"]:
                    parameters["ticker"] = parts[1]
                elif domain in ["sector_analysis", "sa"]:
                    parameters["sector"] = parts[1]
                elif domain in ["industry_analysis", "ia"]:
                    parameters["industry"] = parts[1]
                elif domain in ["macro_analysis", "ma"]:
                    parameters["region"] = parts[1]
            else:
                # Parse key=value parameters
                for param in parts[1:]:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        parameters[key] = value
                    else:
                        # Assume first positional parameter
                        if (
                            domain in ["fundamental_analysis", "fa", "trade_history", "th"]
                            and "ticker" not in parameters
                        ):
                            parameters["ticker"] = param
                        elif domain in ["sector_analysis", "sa"] and "sector" not in parameters:
                            parameters["sector"] = param
                        elif domain in ["industry_analysis", "ia"] and "industry" not in parameters:
                            parameters["industry"] = param
                        elif domain in ["macro_analysis", "ma"] and "region" not in parameters:
                            parameters["region"] = param

            # Execute based on phase
            if phase == "workflow":
                return self.execute_full_workflow(domain, parameters, mode)
            return self.execute_single_phase(domain, phase, parameters, mode)

        except Exception as e:
            return {"error": f"Failed to parse command: {str(e)}"}


def main():
    """CLI interface for the unified command system"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified DASV Command Interface",
        epilog="""
Examples:
  %(prog)s fa:d AAPL                          # fundamental_analysis discover for AAPL
  %(prog)s sa:workflow XLRE                   # full sector_analysis workflow for XLRE
  %(prog)s ca:s ticker_1=AAPL ticker_2=MSFT   # comparative_analysis synthesize
  %(prog)s --list                             # list all available commands
  %(prog)s --info fa                          # get info about fundamental_analysis
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("command", nargs="?", help="Command string (domain:phase parameters)")
    parser.add_argument(
        "--mode",
        choices=["direct", "sub_agent"],
        default="direct",
        help="Execution mode",
    )
    parser.add_argument("--list", action="store_true", help="List all available commands")
    parser.add_argument("--info", metavar="DOMAIN", help="Get information about a domain")
    parser.add_argument("--workflow-id", help="Custom workflow identifier")

    args = parser.parse_args()

    # Initialize interface
    interface = UnifiedCommandInterface()

    # Handle special commands
    if args.list:
        commands_info = interface.list_all_commands()
        print("📋 Available Commands:")
        for domain, phases in commands_info["commands"].items():
            print("  {domain}: {', '.join(phases)}")

        print("\n🔄 Available Workflows:")
        for workflow in commands_info["workflows"]:
            print("  {workflow}")

        print("\n📝 Command Aliases:")
        for alias, full_name in commands_info["command_aliases"].items():
            print("  {alias} → {full_name}")

        print("\n⚡ Phase Aliases:")
        for alias, full_name in commands_info["phase_aliases"].items():
            print("  {alias} → {full_name}")

        return

    if args.info:
        info = interface.get_command_info(args.info)
        print("ℹ️  Command Information:")
        print(json.dumps(info, indent=2))
        return

    if not args.command:
        parser.print_help()
        return

    # Execute command
    mode = ExecutionMode.DIRECT if args.mode == "direct" else ExecutionMode.SUB_AGENT

    print("🎯 Executing: {args.command}")
    result = interface.execute_command_string(args.command, mode)

    # Print results
    print("\n" + "=" * 60)
    print("EXECUTION RESULT")
    print("=" * 60)

    if "error" in result:
        print("❌ Error: {result['error']}")
    else:
        print("Status: {result['status']}")

        if "workflow_id" in result:
            # Workflow result
            print("Workflow ID: {result['workflow_id']}")
            print("Domain: {result['domain']}")
            print("Duration: {result.get('duration', 'N/A')}")
            print("Phases Completed: {result['phases_completed']}")
            print("Final Outputs: {len(result['final_outputs'])}")

            if result.get("overall_confidence"):
                print("Overall Confidence: {result['overall_confidence']:.2f}")

            print("\nPhase Results:")
            for phase, phase_info in result.get("phase_results", {}).items():
                status_emoji = "✅" if phase_info["status"] == "success" else "❌"
                quality_emoji = "✅" if phase_info["quality_gate"] == "pass" else "⚠️"
                print(
                    f"  {status_emoji} {phase}: {phase_info['status']} (Quality: {quality_emoji} {phase_info['quality_gate']})"
                )

        else:
            # Single phase result
            print("Domain: {result['domain']}")
            print("Phase: {result['phase']}")
            print("Execution Time: {result['execution_time']:.2f}s")

            if result.get("confidence_score"):
                print("Confidence Score: {result['confidence_score']:.2f}")

            if result.get("output_files"):
                print("Output Files: {result['output_files']}")

        if result.get("warnings"):
            print("\nWarnings:")
            for warning in result["warnings"]:
                print("  ⚠️  {warning}")


if __name__ == "__main__":
    main()
