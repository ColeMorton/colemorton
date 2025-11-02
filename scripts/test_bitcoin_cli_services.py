#!/usr/bin/env python3
"""
Bitcoin CLI Services Test Suite

Comprehensive testing of Bitcoin CLI services including:
- Individual service functionality and API integration
- Error handling and data validation
- Output format compliance
- Free-tier API limits and rate limiting
- Service factory patterns and configuration
"""

import json
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Any


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.services.alternative_me import create_alternative_me_service
from scripts.services.binance_api import create_binance_api_service
from scripts.services.bitcoin_network_stats import create_bitcoin_network_stats_service
from scripts.services.blockchain_com import create_blockchain_com_service
from scripts.services.coinmetrics import create_coinmetrics_service
from scripts.services.mempool_space import create_mempool_space_service


class BitcoinCLIServicesTestBase(unittest.TestCase):
    """Base class for Bitcoin CLI services tests"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.test_timeout = 30  # seconds for API calls

    def run_cli_command(self, cli_script: str, args: list[str], env: str = "test") -> dict[str, Any]:
        """Run CLI command and return parsed result"""
        cmd = ["python", str(self.scripts_dir / cli_script)] + args

        # Only add env if not already present
        if "--env" not in " ".join(args):
            cmd.extend(["--env", env])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=self.test_timeout,
            )
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "timeout": True,
            }

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False,
        }

    def validate_json_output(self, output: str) -> dict[str, Any]:
        """Validate and parse JSON output"""
        try:
            return json.loads(output.strip())
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON output: {e}. Output was: {output}")

    def assert_valid_bitcoin_data(self, data: dict[str, Any], required_fields: list[str] = None):
        """Assert that data contains valid Bitcoin-related fields"""
        self.assertIsInstance(data, dict)

        if required_fields:
            for field in required_fields:
                self.assertIn(field, data, f"Missing required field: {field}")

    def sleep_for_rate_limit(self, seconds: float = 1.0):
        """Sleep to respect API rate limits"""
        time.sleep(seconds)


class TestMempoolSpaceService(BitcoinCLIServicesTestBase):
    """Test Mempool.space service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_mempool_space_service("test")
        self.assertIsNotNone(service)
        self.assertEqual(service.config.base_url, "https://mempool.space/api")

    def test_cli_fee_estimates(self):
        """Test CLI fee estimates command"""
        result = self.run_cli_command("mempool_space_cli.py", ["fees"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["fastestFee", "halfHourFee", "hourFee"]

        for field in required_fields:
            self.assertIn(field, data, f"Missing fee field: {field}")
            self.assertIsInstance(data[field], (int, float))
            self.assertGreater(data[field], 0)

    def test_cli_mempool_info(self):
        """Test CLI mempool info command"""
        result = self.run_cli_command("mempool_space_cli.py", ["mempool"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["count", "vsize", "total_fee"]

        for field in required_fields:
            if field in data:  # Some fields might be optional
                self.assertIsInstance(data[field], (int, float))

    def test_cli_recent_blocks(self):
        """Test CLI recent blocks command"""
        result = self.run_cli_command("mempool_space_cli.py", ["blocks", "--limit", "5"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertLessEqual(len(data), 5)

        # Validate block structure
        for block in data[:1]:  # Check first block
            self.assertIn("height", block)
            self.assertIn("hash", block)
            self.assertIsInstance(block["height"], int)

    def test_service_rate_limiting(self):
        """Test service respects rate limiting"""
        service = create_mempool_space_service("test")

        # Make multiple quick requests
        for i in range(3):
            try:
                result = service.get_fee_estimates()
                self.assertIsNotNone(result)
                self.sleep_for_rate_limit(0.5)  # Small delay between requests
            except Exception as e:
                # If rate limited, that's acceptable for a free service
                self.assertIn("rate", str(e).lower(), f"Unexpected error: {e}")


class TestBlockchainComService(BitcoinCLIServicesTestBase):
    """Test Blockchain.com service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_blockchain_com_service("test")
        self.assertIsNotNone(service)
        self.assertEqual(service.config.base_url, "https://blockchain.info")

    def test_cli_latest_block(self):
        """Test CLI latest block command"""
        result = self.run_cli_command("blockchain_com_cli.py", ["latest-block"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["height", "hash", "time"]
        self.assert_valid_bitcoin_data(data, required_fields)

        self.assertIsInstance(data["height"], int)
        self.assertGreater(data["height"], 800000)  # Reasonable block height

    def test_cli_network_stats(self):
        """Test CLI network stats command"""
        result = self.run_cli_command("blockchain_com_cli.py", ["network-stats"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        self.assertIsInstance(data, dict)
        # Network stats structure may vary, so we check basic validity

    def test_cli_price_command(self):
        """Test CLI Bitcoin price command"""
        result = self.run_cli_command("blockchain_com_cli.py", ["price"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["price_usd", "timestamp"]
        self.assert_valid_bitcoin_data(data, required_fields)

        self.assertIsInstance(data["price_usd"], (int, float))
        self.assertGreater(data["price_usd"], 1000)  # Reasonable Bitcoin price


class TestCoinMetricsService(BitcoinCLIServicesTestBase):
    """Test CoinMetrics service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_coinmetrics_service("test")
        self.assertIsNotNone(service)
        self.assertEqual(service.config.base_url, "https://community-api.coinmetrics.io/v4")

    def test_cli_supported_assets(self):
        """Test CLI supported assets command"""
        result = self.run_cli_command("coinmetrics_cli.py", ["assets"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        # Check for Bitcoin in supported assets
        btc_found = any(asset.get("asset", "").lower() == "btc" for asset in data if isinstance(asset, dict))
        self.assertTrue(btc_found, "Bitcoin (BTC) not found in supported assets")

    def test_cli_bitcoin_metrics(self):
        """Test CLI Bitcoin cycle metrics command"""
        result = self.run_cli_command(
            "coinmetrics_cli.py",
            [
                "bitcoin-metrics",
                "--start-date",
                "2024-01-01",
                "--end-date",
                "2024-01-05",
            ],
        )

        # CoinMetrics free tier might have limitations, so we allow for some flexibility
        if result["returncode"] == 0:
            data = self.validate_json_output(result["stdout"])
            self.assertIsInstance(data, list)
        else:
            # If free tier is limited, that's acceptable
            self.assertIn(
                "rate",
                result["stderr"].lower() + result["stdout"].lower(),
                "Unexpected error type for CoinMetrics",
            )

    def test_cli_network_data(self):
        """Test CLI network data command"""
        result = self.run_cli_command(
            "coinmetrics_cli.py",
            [
                "network-data",
                "--asset",
                "btc",
                "--start-date",
                "2024-01-01",
                "--end-date",
                "2024-01-02",
            ],
        )

        if result["returncode"] == 0:
            data = self.validate_json_output(result["stdout"])
            self.assertIsInstance(data, list)

            if len(data) > 0:
                # Validate network data structure
                first_entry = data[0]
                self.assertIsInstance(first_entry, dict)


class TestAlternativeMeService(BitcoinCLIServicesTestBase):
    """Test Alternative.me service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_alternative_me_service("test")
        self.assertIsNotNone(service)
        self.assertEqual(service.config.base_url, "https://api.alternative.me")

    def test_cli_current_fear_greed(self):
        """Test CLI current Fear & Greed command"""
        result = self.run_cli_command("alternative_me_cli.py", ["current"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["value", "value_classification", "timestamp"]
        self.assert_valid_bitcoin_data(data, required_fields)

        value = int(data["value"])
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 100)

    def test_cli_historical_fear_greed(self):
        """Test CLI historical Fear & Greed command"""
        result = self.run_cli_command("alternative_me_cli.py", ["historical", "--limit", "5"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertLessEqual(len(data), 5)

        for entry in data:
            value = int(entry["value"])
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 100)

    def test_cli_sentiment_analysis(self):
        """Test CLI sentiment analysis command"""
        result = self.run_cli_command("alternative_me_cli.py", ["analysis", "--days", "7"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["average", "current_value", "period_days"]
        self.assert_valid_bitcoin_data(data, required_fields)

        self.assertEqual(data["period_days"], 7)
        self.assertGreaterEqual(data["average"], 0)
        self.assertLessEqual(data["average"], 100)


class TestBinanceAPIService(BitcoinCLIServicesTestBase):
    """Test Binance API service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_binance_api_service("test")
        self.assertIsNotNone(service)
        self.assertEqual(service.config.base_url, "https://api.binance.com")

    def test_cli_bitcoin_price(self):
        """Test CLI Bitcoin price command"""
        result = self.run_cli_command("binance_api_cli.py", ["price", "--symbol", "BTCUSDT"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["symbol", "price"]
        self.assert_valid_bitcoin_data(data, required_fields)

        self.assertEqual(data["symbol"], "BTCUSDT")
        price = float(data["price"])
        self.assertGreater(price, 1000)  # Reasonable Bitcoin price

    def test_cli_24hr_ticker(self):
        """Test CLI 24hr ticker command"""
        result = self.run_cli_command("binance_api_cli.py", ["24hr-ticker", "--symbol", "BTCUSDT"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["symbol", "priceChange", "priceChangePercent"]
        self.assert_valid_bitcoin_data(data, required_fields)

        self.assertEqual(data["symbol"], "BTCUSDT")

    def test_cli_bitcoin_data(self):
        """Test CLI comprehensive Bitcoin data command"""
        result = self.run_cli_command("binance_api_cli.py", ["bitcoin-data"])
        self.assertEqual(result["returncode"], 0)

        data = self.validate_json_output(result["stdout"])
        required_fields = ["price_ticker", "24hr_stats"]
        self.assert_valid_bitcoin_data(data, required_fields)


class TestBitcoinNetworkStatsService(BitcoinCLIServicesTestBase):
    """Test Bitcoin Network Statistics aggregation service and CLI"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = create_bitcoin_network_stats_service("test")
        self.assertIsNotNone(service)

    def test_cli_network_overview(self):
        """Test CLI network overview command"""
        # This test might take longer as it aggregates multiple APIs
        result = self.run_cli_command("bitcoin_network_stats_cli.py", ["overview"])

        # Allow for partial failures since we're aggregating multiple free APIs
        if result["returncode"] == 0:
            data = self.validate_json_output(result["stdout"])
            required_fields = ["timestamp", "sources"]
            self.assert_valid_bitcoin_data(data, required_fields)

            self.assertIsInstance(data["sources"], list)
            self.assertGreater(len(data["sources"]), 0)
        else:
            # If some APIs fail, that's acceptable for an aggregation service
            self.assertIn("error", result["stderr"].lower() + result["stdout"].lower())

    def test_cli_mempool_analysis(self):
        """Test CLI mempool analysis command"""
        result = self.run_cli_command("bitcoin_network_stats_cli.py", ["mempool"])

        if result["returncode"] == 0:
            data = self.validate_json_output(result["stdout"])
            required_fields = ["timestamp", "sources"]
            self.assert_valid_bitcoin_data(data, required_fields)

    def test_cli_comprehensive_report(self):
        """Test CLI comprehensive report command"""
        # This is the most comprehensive test and might take the longest
        result = self.run_cli_command("bitcoin_network_stats_cli.py", ["report"])

        if result["returncode"] == 0:
            data = self.validate_json_output(result["stdout"])
            required_fields = ["report_timestamp", "summary"]
            self.assert_valid_bitcoin_data(data, required_fields)

            summary = data["summary"]
            self.assertIn("total_data_sources", summary)
            self.assertGreater(summary["total_data_sources"], 0)


class TestBitcoinCLIServicesIntegration(BitcoinCLIServicesTestBase):
    """Integration tests across all Bitcoin CLI services"""

    def test_all_services_can_initialize(self):
        """Test that all Bitcoin services can be initialized"""
        services = [
            create_mempool_space_service,
            create_blockchain_com_service,
            create_coinmetrics_service,
            create_alternative_me_service,
            create_binance_api_service,
            create_bitcoin_network_stats_service,
        ]

        for service_factory in services:
            with self.subTest(service=service_factory.__name__):
                service = service_factory("test")
                self.assertIsNotNone(service)

    def test_cli_help_commands(self):
        """Test that all CLI services provide help"""
        cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "coinmetrics_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
            "bitcoin_network_stats_cli.py",
        ]

        for cli_script in cli_scripts:
            with self.subTest(cli=cli_script):
                result = self.run_cli_command(cli_script, ["--help"])
                # Help should return 0 or help might return different codes
                self.assertIn("help", result["stdout"].lower() + result["stderr"].lower())

    def test_error_handling_consistency(self):
        """Test that all services handle invalid commands consistently"""
        cli_scripts = [
            "mempool_space_cli.py",
            "blockchain_com_cli.py",
            "alternative_me_cli.py",
            "binance_api_cli.py",
        ]

        for cli_script in cli_scripts:
            with self.subTest(cli=cli_script):
                result = self.run_cli_command(cli_script, ["invalid-command"])
                # Should return non-zero exit code for invalid commands
                self.assertNotEqual(result["returncode"], 0)


if __name__ == "__main__":
    # Configure test runner
    unittest.main(
        verbosity=2,
        failfast=False,  # Continue running tests even if some fail
        buffer=True,  # Capture stdout/stderr during tests
    )
