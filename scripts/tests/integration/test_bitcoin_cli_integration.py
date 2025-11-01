#!/usr/bin/env python3
"""
Bitcoin CLI Integration Test Suite

Comprehensive testing of Bitcoin CLI services following BaseFinancialCLI patterns:
- Command → CLI → Service workflows
- Environment configuration handling
- Error handling across layers
- Output format validation
- Architectural compliance with existing financial CLIs
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class BitcoinCLIIntegrationTestBase(unittest.TestCase):
    """Base class for Bitcoin CLI integration tests"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.timeout = 30  # seconds for CLI commands

    def run_cli_command(self, cli_script: str, args: list[str], env: str = "test") -> dict[str, Any]:
        """Run CLI command and return parsed result"""
        cmd = ["python", str(self.scripts_dir / cli_script)] + args

        # Only add env if not already present and not using help
        if "--env" not in " ".join(args) and "--help" not in args:
            cmd.extend(["--env", env])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "timeout": True,
                "command": " ".join(cmd),
            }

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False,
            "command": " ".join(cmd),
        }

    def parse_json_output(self, result: dict[str, Any]) -> dict[str, Any]:
        """Parse JSON output from CLI command"""
        if result["returncode"] != 0:
            self.fail(
                f"Command failed: {result['command']}\n"
                f"Return code: {result['returncode']}\n"
                f"Stderr: {result['stderr']}\n"
                f"Stdout: {result['stdout']}"
            )

        # Handle table format output (default for health checks)
        if "Service Data" in result["stdout"] or "┏━━" in result["stdout"]:
            # For health checks, we just verify the command succeeded
            return {"status": "success", "output_format": "table"}

        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            # If not JSON, return success indicator for table format
            return {
                "status": "success",
                "output_format": "table",
                "raw_output": result["stdout"],
            }


class TestMempoolSpaceCLI(BitcoinCLIIntegrationTestBase):
    """Test Mempool.space CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("mempool_space_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        # Should indicate success for table format or have service info for JSON
        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "mempool_space")

    def test_config_validation(self):
        """Test configuration validation"""
        result = self.run_cli_command("mempool_space_cli.py", ["config", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        # Config should return YAML format, so we just verify success
        self.assertTrue(len(result["stdout"]) > 0)

    def test_cache_operations(self):
        """Test cache management operations"""
        # Test cache stats
        result = self.run_cli_command("mempool_space_cli.py", ["cache", "stats"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("action", data)
        self.assertEqual(data["action"], "stats")

    @patch("scripts.services.mempool_space.MempoolSpaceService.get_fee_estimates")
    def test_fees_command_with_mock(self, mock_get_fees):
        """Test fees command with mocked service response"""
        # Mock successful fee response
        mock_get_fees.return_value = {
            "fastestFee": 20,
            "halfHourFee": 15,
            "hourFee": 10,
            "economyFee": 8,
        }

        result = self.run_cli_command("mempool_space_cli.py", ["fees"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("fastestFee", data)
        self.assertEqual(data["fastestFee"], 20)

    def test_output_format_support(self):
        """Test different output formats are supported"""
        # Test JSON format (should work with mocked data)
        with patch("scripts.services.mempool_space.MempoolSpaceService.get_fee_estimates") as mock_fees:
            mock_fees.return_value = {"fastestFee": 15, "halfHourFee": 12}

            result = self.run_cli_command("mempool_space_cli.py", ["fees", "--output-format", "json"])

            self.assertEqual(result["returncode"], 0)
            # Should be valid JSON
            data = json.loads(result["stdout"])
            self.assertIn("fastestFee", data)


class TestBlockchainComCLI(BitcoinCLIIntegrationTestBase):
    """Test Blockchain.com CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("blockchain_com_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "blockchain_com")

    def test_config_validation(self):
        """Test configuration validation"""
        result = self.run_cli_command("blockchain_com_cli.py", ["config", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        self.assertTrue(len(result["stdout"]) > 0)

    @patch("scripts.services.blockchain_com.BlockchainComService.get_latest_block")
    def test_latest_block_command_with_mock(self, mock_get_block):
        """Test latest block command with mocked service response"""
        mock_get_block.return_value = {
            "height": 820000,
            "hash": "000000000000000000031c5f6ad8b7c8e98c05d7f9b3c1e8d4a6e7b2c9f1a3d5",
            "time": 1703001600,
        }

        result = self.run_cli_command("blockchain_com_cli.py", ["latest-block"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("height", data)
        self.assertEqual(data["height"], 820000)


class TestCoinMetricsCLI(BitcoinCLIIntegrationTestBase):
    """Test CoinMetrics CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("coinmetrics_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "coinmetrics")

    @patch("scripts.services.coinmetrics.CoinMetricsService.get_supported_assets")
    def test_assets_command_with_mock(self, mock_get_assets):
        """Test assets command with mocked service response"""
        mock_get_assets.return_value = [
            {"asset": "btc", "full_name": "Bitcoin"},
            {"asset": "eth", "full_name": "Ethereum"},
        ]

        result = self.run_cli_command("coinmetrics_cli.py", ["assets"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


class TestAlternativeMeCLI(BitcoinCLIIntegrationTestBase):
    """Test Alternative.me CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("alternative_me_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "alternative_me")

    @patch("scripts.services.alternative_me.AlternativeMeService.get_current_fear_greed")
    def test_current_fear_greed_with_mock(self, mock_get_fear_greed):
        """Test current fear & greed command with mocked service response"""
        mock_get_fear_greed.return_value = {
            "value": "75",
            "value_classification": "Greed",
            "timestamp": "1703001600",
        }

        result = self.run_cli_command("alternative_me_cli.py", ["current"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("value", data)
        self.assertEqual(data["value"], "75")
        self.assertEqual(data["value_classification"], "Greed")


class TestBinanceAPICLI(BitcoinCLIIntegrationTestBase):
    """Test Binance API CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("binance_api_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "binance_api")

    @patch("scripts.services.binance_api.BinanceAPIService.get_symbol_price_ticker")
    def test_price_command_with_mock(self, mock_get_price):
        """Test price command with mocked service response"""
        mock_get_price.return_value = {"symbol": "BTCUSDT", "price": "65000.00"}

        result = self.run_cli_command("binance_api_cli.py", ["price", "--symbol", "BTCUSDT"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("symbol", data)
        self.assertEqual(data["symbol"], "BTCUSDT")
        self.assertIn("price", data)


class TestBitcoinNetworkStatsCLI(BitcoinCLIIntegrationTestBase):
    """Test Bitcoin Network Stats CLI integration"""

    def test_health_check(self):
        """Test health check command"""
        result = self.run_cli_command("bitcoin_network_stats_cli.py", ["health", "--env", "test"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("status", data)
        if data.get("output_format") != "table":
            self.assertIn("service", data)
            self.assertEqual(data["service"], "bitcoin_network_stats")

    @patch("scripts.services.bitcoin_network_stats.BitcoinNetworkStatsService.get_network_overview")
    def test_overview_command_with_mock(self, mock_get_overview):
        """Test overview command with mocked service response"""
        mock_get_overview.return_value = {
            "timestamp": "2024-01-01T12:00:00",
            "sources": ["mempool_space", "blockchain_com"],
            "summary": {"total_data_sources": 2, "successful_sources": 2, "errors": []},
        }

        result = self.run_cli_command("bitcoin_network_stats_cli.py", ["overview"])

        self.assertEqual(result["returncode"], 0)
        data = self.parse_json_output(result)

        self.assertIn("timestamp", data)
        self.assertIn("sources", data)
        self.assertIsInstance(data["sources"], list)


class TestBitcoinCLIArchitecturalCompliance(BitcoinCLIIntegrationTestBase):
    """Test Bitcoin CLI architectural compliance with BaseFinancialCLI patterns"""

    def test_all_bitcoin_cli_scripts_follow_base_pattern(self):
        """Test that all Bitcoin CLI scripts follow BaseFinancialCLI pattern"""
        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "coinmetrics_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
            "bitcoin_network_stats_cli.py",
        ]

        for script in bitcoin_cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test that the script has health and config commands
                result = self.run_cli_command(script, ["--help"])

                self.assertEqual(result["returncode"], 0)
                help_output = result["stdout"]

                # Check for standard commands
                self.assertIn("health", help_output, f"{script} missing health command")
                self.assertIn("config", help_output, f"{script} missing config command")
                self.assertIn("cache", help_output, f"{script} missing cache command")

                # Check for proper CLI structure (Rich format uses different styling)
                commands_indicators = ["Commands", "╭─ Commands", "Commands:"]
                has_commands_section = any(indicator in help_output for indicator in commands_indicators)
                self.assertTrue(has_commands_section, f"{script} missing proper CLI structure")

    def test_environment_parameter_support(self):
        """Test that all Bitcoin CLI scripts support environment parameters"""
        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "coinmetrics_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
            "bitcoin_network_stats_cli.py",
        ]

        for script in bitcoin_cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test dev environment
                result = self.run_cli_command(script, ["health", "--env", "dev"])
                self.assertEqual(result["returncode"], 0, f"{script} failed with dev environment")

                # Test test environment
                result = self.run_cli_command(script, ["health", "--env", "test"])
                self.assertEqual(result["returncode"], 0, f"{script} failed with test environment")

    def test_output_format_consistency(self):
        """Test output format consistency across Bitcoin CLI scripts"""
        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
        ]

        for script in bitcoin_cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                # Test verbose JSON output for health checks (using --verbose flag)
                result = self.run_cli_command(script, ["health", "--verbose"])

                self.assertEqual(
                    result["returncode"],
                    0,
                    f"{script} failed with verbose health check",
                )

                # Should produce output
                self.assertTrue(len(result["stdout"]) > 0)

    def test_error_handling_consistency(self):
        """Test error handling consistency across Bitcoin CLI scripts"""
        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "coinmetrics_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
            "bitcoin_network_stats_cli.py",
        ]

        for script in bitcoin_cli_scripts:
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
                # Should provide some error indication
                error_present = (
                    len(result["stderr"]) > 0
                    or "error" in result["stdout"].lower()
                    or "invalid" in result["stdout"].lower()
                )
                self.assertTrue(error_present, f"{script} should provide error message")

    def test_help_command_completeness(self):
        """Test that help commands provide comprehensive information"""
        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "coinmetrics_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
            "bitcoin_network_stats_cli.py",
        ]

        for script in bitcoin_cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                result = self.run_cli_command(script, ["--help"])

                self.assertEqual(result["returncode"], 0)
                help_output = result["stdout"]

                # Should contain service description
                self.assertTrue(len(help_output) > 100, f"{script} help output too brief")

                # Should mention Bitcoin or blockchain
                help_lower = help_output.lower()
                bitcoin_related = any(
                    term in help_lower
                    for term in [
                        "bitcoin",
                        "blockchain",
                        "btc",
                        "cryptocurrency",
                        "mempool",
                    ]
                )
                self.assertTrue(bitcoin_related, f"{script} help should mention Bitcoin/blockchain")


class TestBitcoinCLIPerformance(BitcoinCLIIntegrationTestBase):
    """Test Bitcoin CLI performance characteristics"""

    def test_cli_startup_time(self):
        """Test Bitcoin CLI startup time is reasonable"""
        import time

        bitcoin_cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "alternative_me_cli.py",
        ]

        for script in bitcoin_cli_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                start_time = time.time()
                result = self.run_cli_command(script, ["health"])
                end_time = time.time()

                startup_time = end_time - start_time

                # CLI should start within 3 seconds (generous for Bitcoin API calls)
                self.assertLess(
                    startup_time,
                    3.0,
                    f"{script} startup time too slow: {startup_time:.2f}s",
                )
                self.assertEqual(result["returncode"], 0)


if __name__ == "__main__":
    # Configure test runner for verbose output
    unittest.main(verbosity=2, buffer=True)
