#!/usr/bin/env python3
"""
CLI Integration Test Suite

Comprehensive testing of CLI-centric architecture patterns including:
- Command → CLI → Service workflows
- Environment configuration handling
- Error handling across layers
- Output format validation
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CLIIntegrationTestBase(unittest.TestCase):
    """Base class for CLI integration tests"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"

    def run_cli_command(self, cli_script: str, args: list[str], env: str = "test") -> dict[str, Any]:
        """Run CLI command and return parsed result"""
        cmd = ["python", str(self.scripts_dir / cli_script)] + args

        # Only add env if not already present and command supports it
        if "--env" not in " ".join(args):
            cmd.extend(["--env", env])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
        }

    def parse_json_output(self, result: dict[str, Any]) -> dict[str, Any]:
        """Parse JSON output from CLI command"""
        if result["returncode"] != 0:
            self.fail(f"Command failed: {result['command']}\nStderr: {result['stderr']}")

        # Handle table format output (default for health checks)
        if "Service Data" in result["stdout"] or "┏━━" in result["stdout"]:
            # For health checks, we just verify the command succeeded
            return {"status": "success", "output_format": "table"}

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            # If not JSON, just return success indicator for table format
            return {
                "status": "success",
                "output_format": "table",
                "raw_output": result["stdout"],
            }


class TestAlphaVantageCLI(CLIIntegrationTestBase):
    """Test Alpha Vantage CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("alpha_vantage_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("service", data)
        self.assertEqual(data["service"], "alpha_vantage")
        self.assertIn("status", data)

    def test_config_validation(self):
        """Test configuration validation"""
        result = self.run_cli_command("alpha_vantage_cli.py", ["config", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIsInstance(data, dict)

    def test_invalid_ticker_validation(self):
        """Test ticker validation with invalid input"""
        result = self.run_cli_command("alpha_vantage_cli.py", ["quote", "INVALID_TICKER_SYMBOL_TOO_LONG"])

        # Should fail due to ticker validation
        self.assertNotEqual(result["returncode"], 0)
        self.assertIn("Ticker too long", result["stderr"])

    def test_cache_operations(self):
        """Test cache management operations"""
        # Test cache stats
        result = self.run_cli_command("alpha_vantage_cli.py", ["cache", "stats"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("action", data)
        self.assertEqual(data["action"], "stats")


class TestYahooFinanceCLI(CLIIntegrationTestBase):
    """Test Yahoo Finance CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("yahoo_finance_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("service", data)
        self.assertEqual(data["service"], "yahoo_finance")

    def test_quote_command_structure(self):
        """Test quote command structure (without actual API call)"""
        # Test with invalid ticker to check validation
        result = self.run_cli_command("yahoo_finance_cli.py", ["quote", ""])

        # Should fail due to empty ticker
        self.assertNotEqual(result["returncode"], 0)


class TestFMPCLI(CLIIntegrationTestBase):
    """Test Financial Modeling Prep CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("fmp_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("service", data)
        self.assertEqual(data["service"], "fmp")


class TestDashboardGeneratorCLI(CLIIntegrationTestBase):
    """Test Dashboard Generator CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("dashboard_generator_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        # For table format output, just verify success
        self.assertIn("status", data)
        self.assertEqual(data["status"], "success")

    def test_list_themes(self):
        """Test theme listing functionality"""
        result = self.run_cli_command("dashboard_generator_cli.py", ["list-themes", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("available_themes", data)
        self.assertIn("light", data["available_themes"])
        self.assertIn("dark", data["available_themes"])

    def test_config_validation(self):
        """Test configuration validation"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
output:
  directory: "test_output"
theme:
  default: "light"
chart_engine: "matplotlib"
"""
            )
            temp_config = f.name

        try:
            result = self.run_cli_command(
                "dashboard_generator_cli.py",
                ["validate", "--config-file", temp_config, "--env", "test"],
            )

            self.assertEqual(result["returncode"], 0)
            data = self.parse_json_output(result)

            self.assertIn("status", data)
            self.assertEqual(data["status"], "valid")
        finally:
            Path(temp_config).unlink()

    def test_invalid_config_file(self):
        """Test handling of non-existent config file"""
        result = self.run_cli_command(
            "dashboard_generator_cli.py",
            ["validate", "--config-file", "nonexistent_config.yaml", "--env", "test"],
        )

        # Should fail due to missing config file
        self.assertNotEqual(result["returncode"], 0)
        self.assertIn("Config file does not exist", result["stderr"])


class TestTradeHistoryCLI(CLIIntegrationTestBase):
    """Test Trade History CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("trade_history_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("service", data)
        self.assertEqual(data["service"], "trade_history")

    def test_list_report_types(self):
        """Test report type listing"""
        result = self.run_cli_command("trade_history_cli.py", ["list-types", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("available_types", data)
        self.assertIn("type_descriptions", data)
        self.assertIsInstance(data["available_types"], list)

    def test_date_validation(self):
        """Test date format validation"""
        # Test invalid date format
        result = self.run_cli_command("trade_history_cli.py", ["validate", "invalid_date"])

        self.assertNotEqual(result["returncode"], 0)
        self.assertIn("Invalid date format", result["stderr"])

        # Test valid date format but invalid date
        result = self.run_cli_command("trade_history_cli.py", ["validate", "20250230"])  # Feb 30th doesn't exist

        self.assertNotEqual(result["returncode"], 0)
        self.assertIn("Invalid date", result["stderr"])

    def test_valid_date_validation(self):
        """Test validation with valid date"""
        result = self.run_cli_command("trade_history_cli.py", ["validate", "20250715"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        self.assertEqual(data["status"], "validation_complete")
        self.assertEqual(data["date"], "20250715")


class TestCLIArchitecturalCompliance(CLIIntegrationTestBase):
    """Test CLI architectural compliance patterns"""

    def test_all_cli_scripts_follow_base_pattern(self):
        """Test that all CLI scripts follow BaseFinancialCLI pattern"""
        cli_scripts = [
            "alpha_vantage_cli.py",
            "yahoo_finance_cli.py",
            "fmp_cli.py",
            "dashboard_generator_cli.py",
            "trade_history_cli.py",
        ]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test that the script has health and config commands
                result = self.run_cli_command(script, ["--help"])

                self.assertEqual(result["returncode"], 0)
                help_output = result["stdout"]

                # Check for standard commands
                self.assertIn("health", help_output, f"{script} missing health command")

                # Check for proper CLI structure
                self.assertIn("Commands:", help_output, f"{script} missing proper CLI structure")

    def test_environment_parameter_support(self):
        """Test that all CLI scripts support environment parameters"""
        cli_scripts = [
            "alpha_vantage_cli.py",
            "dashboard_generator_cli.py",
            "trade_history_cli.py",
        ]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test dev environment
                result = self.run_cli_command(script, ["health", "--env", "dev"])
                self.assertEqual(result["returncode"], 0, f"{script} failed with dev environment")

                # Test test environment
                result = self.run_cli_command(script, ["health", "--env", "test"])
                self.assertEqual(result["returncode"], 0, f"{script} failed with test environment")

    def test_output_format_consistency(self):
        """Test output format consistency across CLI scripts"""
        cli_scripts = [
            "alpha_vantage_cli.py",
            "dashboard_generator_cli.py",
            "trade_history_cli.py",
        ]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test JSON output format
                result = self.run_cli_command(script, ["health", "--output-format", "json"])

                self.assertEqual(result["returncode"], 0, f"{script} failed with JSON format")

                # Verify it's valid JSON
                try:
                    json.loads(result["stdout"])
                except json.JSONDecodeError:
                    self.fail(f"{script} produced invalid JSON output")

    def test_error_handling_consistency(self):
        """Test error handling consistency across CLI scripts"""
        cli_scripts = [
            "alpha_vantage_cli.py",
            "dashboard_generator_cli.py",
            "trade_history_cli.py",
        ]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test with invalid command
                result = self.run_cli_command(script, ["invalid_command"])

                # Should fail gracefully
                self.assertNotEqual(
                    result["returncode"],
                    0,
                    f"{script} should fail with invalid command",
                )
                self.assertTrue(len(result["stderr"]) > 0, f"{script} should provide error message")


class TestCLIPerformance(CLIIntegrationTestBase):
    """Test CLI performance characteristics"""

    def test_cli_startup_time(self):
        """Test CLI startup time is reasonable"""
        import time

        cli_scripts = ["alpha_vantage_cli.py", "dashboard_generator_cli.py"]

        for script in cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                start_time = time.time()
                result = self.run_cli_command(script, ["health"])
                end_time = time.time()

                startup_time = end_time - start_time

                # CLI should start within 2 seconds (generous for CI environments)
                self.assertLess(
                    startup_time,
                    2.0,
                    f"{script} startup time too slow: {startup_time:.2f}s",
                )
                self.assertEqual(result["returncode"], 0)


if __name__ == "__main__":
    # Configure test runner for verbose output
    unittest.main(verbosity=2, buffer=True)
