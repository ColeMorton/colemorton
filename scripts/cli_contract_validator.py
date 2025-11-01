#!/usr/bin/env python3
"""
CLI Contract Validator

Validates that CLI service contracts are properly implemented and that
all expected commands exist before attempting to execute them.

This prevents runtime failures due to missing commands or method mismatches.
"""

from pathlib import Path
from typing import Any


class CLIContractValidator:
    """Validates CLI service contracts before execution"""

    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.validation_cache = {}

    def validate_service_command(self, service_name: str, command: str) -> dict[str, Any]:
        """
        Validate that a specific command exists for a service

        Args:
            service_name: Name of the service (e.g., 'yahoo_finance', 'alpha_vantage')
            command: Command to validate (e.g., 'history', 'analyze')

        Returns:
            Dictionary with validation results
        """
        cache_key = f"{service_name}:{command}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        result: dict[str, Any] = {
            "valid": False,
            "service_name": service_name,
            "command": command,
            "cli_file_exists": False,
            "command_exists": False,
            "available_commands": [],
            "errors": [],
        }

        try:
            # Check if CLI file exists
            cli_file = self.scripts_dir / f"{service_name}_cli.py"
            if not cli_file.exists():
                result["errors"].append(f"CLI file not found: {cli_file}")
                self.validation_cache[cache_key] = result
                return result

            result["cli_file_exists"] = True

            # Get available commands from the CLI file
            available_commands = self._get_cli_commands(cli_file, service_name)
            result["available_commands"] = available_commands

            # Check if the specific command exists
            if command in available_commands:
                result["command_exists"] = True
                result["valid"] = True
            else:
                result["errors"].append(
                    f"Command '{command}' not found in {service_name}_cli.py. "
                    f"Available commands: {', '.join(available_commands)}"
                )

        except Exception as e:
            result["errors"].append(f"Error validating {service_name}:{command}: {str(e)}")

        self.validation_cache[cache_key] = result
        return result

    def _get_cli_commands(self, cli_file: Path, service_name: str) -> list[str]:
        """
        Extract available commands from a CLI file

        Args:
            cli_file: Path to the CLI file
            service_name: Name of the service

        Returns:
            List of available command names
        """
        commands = []

        try:
            with open(cli_file) as f:
                content = f.read()

            # Look for @self.app.command() decorators
            import re

            # Pattern to match @self.app.command("command_name")
            pattern = r'@self\.app\.command\(["\']([^"\']+)["\']\)'
            matches = re.findall(pattern, content)

            commands.extend(matches)

            # Also look for @self.app.command without explicit name (uses function name)
            # Pattern: @self.app.command() followed by def function_name(
            pattern_bare = r"@self\.app\.command\(\)\s*\n\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
            bare_matches = re.findall(pattern_bare, content, re.MULTILINE)

            # Convert function names to command names (remove get_ prefix if present)
            for func_name in bare_matches:
                command_name = func_name
                if func_name.startswith("get_"):
                    command_name = func_name[4:]  # Remove 'get_' prefix
                commands.append(command_name)

        except Exception:
            print("Warning: Could not extract commands from {cli_file}: {e}")

        return sorted(list(set(commands)))  # Remove duplicates and sort

    def validate_class_method(self, module_name: str, class_name: str, method_name: str) -> dict[str, Any]:
        """
        Validate that a specific method exists in a class

        Args:
            module_name: Name of the module (e.g., 'trade_history_images')
            class_name: Name of the class (e.g., 'TradeHistoryImageGenerator')
            method_name: Name of the method (e.g., 'process_date')

        Returns:
            Dictionary with validation results
        """
        cache_key = f"{module_name}:{class_name}:{method_name}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        result: dict[str, Any] = {
            "valid": False,
            "module_name": module_name,
            "class_name": class_name,
            "method_name": method_name,
            "module_exists": False,
            "class_exists": False,
            "method_exists": False,
            "available_methods": [],
            "errors": [],
        }

        try:
            # Check if module file exists
            module_file = self.scripts_dir / f"{module_name}.py"
            if not module_file.exists():
                result["errors"].append(f"Module file not found: {module_file}")
                self.validation_cache[cache_key] = result
                return result

            result["module_exists"] = True

            # Get available methods from the class
            available_methods = self._get_class_methods(module_file, class_name)
            result["available_methods"] = available_methods

            if class_name in available_methods:
                result["class_exists"] = True

                if method_name in available_methods[class_name]:
                    result["method_exists"] = True
                    result["valid"] = True
                else:
                    result["errors"].append(
                        f"Method '{method_name}' not found in class '{class_name}'. "
                        f"Available methods: {', '.join(available_methods[class_name])}"
                    )
            else:
                result["errors"].append(f"Class '{class_name}' not found in module '{module_name}'")

        except Exception as e:
            result["errors"].append(f"Error validating {module_name}:{class_name}:{method_name}: {str(e)}")

        self.validation_cache[cache_key] = result
        return result

    def _get_class_methods(self, module_file: Path, class_name: str) -> dict[str, list[str]]:
        """
        Extract available methods from a class in a module

        Args:
            module_file: Path to the module file
            class_name: Name of the class to examine

        Returns:
            Dictionary mapping class names to lists of method names
        """
        classes = {}

        try:
            with open(module_file) as f:
                content = f.read()

            # Find class definitions and their methods
            import re

            # Pattern to find class definitions
            class_pattern = r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]"
            class_matches = re.findall(class_pattern, content)

            for found_class in class_matches:
                # Find methods in this class
                methods = []

                # Split content into lines and find class start
                lines = content.split("\n")
                in_class = False
                indent_level = 0

                for line in lines:
                    stripped = line.strip()

                    # Check if we're entering the target class
                    if f"class {found_class}" in line and ":" in line:
                        in_class = True
                        indent_level = len(line) - len(line.lstrip())
                        continue

                    if in_class:
                        # Check if we've left the class (next class or function at same/higher level)
                        if stripped and not line.startswith(" " * (indent_level + 1)):
                            if stripped.startswith("class ") or stripped.startswith("def "):
                                break

                        # Look for method definitions
                        if re.match(r"\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line):
                            method_match = re.match(r"\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
                            if method_match:
                                method_name = method_match.group(1)
                                # Skip private methods (starting with _)
                                if not method_name.startswith("_"):
                                    methods.append(method_name)

                classes[found_class] = sorted(methods)

        except Exception:
            print("Warning: Could not extract methods from {module_file}: {e}")

        return classes

    def validate_batch(self, validations: list[dict[str, str]]) -> dict[str, Any]:
        """
        Validate multiple CLI contracts in batch

        Args:
            validations: List of validation specs, each containing:
                - For CLI commands: {"type": "cli", "service": "...", "command": "..."}
                - For class methods: {"type": "method", "module": "...", "class": "...", "method": "..."}

        Returns:
            Dictionary with batch validation results
        """
        results: dict[str, Any] = {
            "overall_valid": True,
            "total_validations": len(validations),
            "passed": 0,
            "failed": 0,
            "details": [],
        }

        for validation in validations:
            if validation.get("type") == "cli":
                result = self.validate_service_command(validation["service"], validation["command"])
            elif validation.get("type") == "method":
                result = self.validate_class_method(validation["module"], validation["class"], validation["method"])
            else:
                result = {
                    "valid": False,
                    "errors": [f"Unknown validation type: {validation.get('type')}"],
                }

            results["details"].append(result)

            if result["valid"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["overall_valid"] = False

        return results

    def clear_cache(self):
        """Clear the validation cache"""
        self.validation_cache.clear()


def main():
    """Test the CLI contract validator"""
    validator = CLIContractValidator()

    # Test the known issues we just fixed
    test_cases = [
        {"type": "cli", "service": "yahoo_finance", "command": "history"},
        {
            "type": "cli",
            "service": "yahoo_finance",
            "command": "historical",
        },  # Should fail
        {
            "type": "method",
            "module": "trade_history_images",
            "class": "TradeHistoryImageGenerator",
            "method": "generate_images_for_date",
        },
        {
            "type": "method",
            "module": "trade_history_images",
            "class": "TradeHistoryImageGenerator",
            "method": "process_date",
        },  # Should fail
    ]

    results = validator.validate_batch(test_cases)

    print("CLI Contract Validation Results:")
    print("Overall Valid: {results['overall_valid']}")
    print("Passed: {results['passed']}/{results['total_validations']}")
    print("Failed: {results['failed']}/{results['total_validations']}")
    print()

    for detail in results["details"]:
        status = "✅ PASS" if detail["valid"] else "❌ FAIL"

        if "service_name" in detail:
            print("{status} CLI Command: {detail['service_name']}.{detail['command']}")
        elif "class_name" in detail:
            print(f"{status} Class Method: {detail['class_name']}.{detail['method_name']}")

        if detail.get("errors"):
            for error in detail["errors"]:
                print("   Error: {error}")

        if detail.get("available_commands"):
            print("   Available commands: {', '.join(detail['available_commands'])}")

        if detail.get("available_methods"):
            for class_name, methods in detail["available_methods"].items():
                print("   Available methods in {class_name}: {', '.join(methods)}")

        print()


if __name__ == "__main__":
    main()
