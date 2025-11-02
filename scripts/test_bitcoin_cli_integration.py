#!/usr/bin/env python3
"""
Bitcoin CLI Integration Test Suite

Multi-service integration testing for Bitcoin CLI ecosystem including:
- Cross-service data validation and consistency checks
- Bitcoin Cycle Intelligence workflow integration
- Multi-source aggregation and error resilience
- End-to-end Bitcoin analysis pipeline testing
- Performance and reliability under production scenarios
"""

import json
import statistics
import subprocess
import sys
import time
import unittest
from datetime import datetime, timedelta
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


class BitcoinCLIIntegrationTestBase(unittest.TestCase):
    """Base class for Bitcoin CLI integration tests"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.test_timeout = 60  # longer timeout for integration tests
        self.price_tolerance = 0.05  # 5% price difference tolerance between services

        # Initialize services for direct testing
        self.services = {
            "mempool_space": create_mempool_space_service("test"),
            "blockchain_com": create_blockchain_com_service("test"),
            "coinmetrics": create_coinmetrics_service("test"),
            "alternative_me": create_alternative_me_service("test"),
            "binance_api": create_binance_api_service("test"),
            "bitcoin_network_stats": create_bitcoin_network_stats_service("test"),
        }

    def run_cli_command(self, cli_script: str, args: list[str], env: str = "test") -> dict[str, Any]:
        """Run CLI command and return parsed result"""
        cmd = ["python", str(self.scripts_dir / cli_script)] + args

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

    def get_bitcoin_price_from_multiple_sources(self) -> dict[str, float | None]:
        """Get Bitcoin prices from multiple sources for comparison"""
        prices = {}

        # Binance price
        try:
            binance_data = self.services["binance_api"].get_symbol_price_ticker("BTCUSDT")
            prices["binance"] = float(binance_data.get("price", 0))
        except:
            prices["binance"] = None

        # Blockchain.com price
        try:
            blockchain_data = self.services["blockchain_com"].get_market_price_usd()
            prices["blockchain_com"] = float(blockchain_data.get("price_usd", 0))
        except:
            prices["blockchain_com"] = None

        # Mempool.space price
        try:
            mempool_data = self.services["mempool_space"].get_bitcoin_price()
            if isinstance(mempool_data, dict) and "USD" in mempool_data:
                prices["mempool_space"] = float(mempool_data["USD"])
        except:
            prices["mempool_space"] = None

        return prices

    def validate_price_consistency(self, prices: dict[str, float | None]) -> bool:
        """Validate that prices from different sources are reasonably consistent"""
        valid_prices = [p for p in prices.values() if p is not None and p > 0]

        if len(valid_prices) < 2:
            return True  # Can't validate with fewer than 2 prices

        avg_price = statistics.mean(valid_prices)

        for price in valid_prices:
            deviation = abs(price - avg_price) / avg_price
            if deviation > self.price_tolerance:
                return False

        return True

    def sleep_for_rate_limit(self, seconds: float = 2.0):
        """Sleep to respect API rate limits in integration tests"""
        time.sleep(seconds)


class TestBitcoinPriceConsistency(BitcoinCLIIntegrationTestBase):
    """Test Bitcoin price consistency across multiple services"""

    def test_price_consistency_across_sources(self):
        """Test that Bitcoin prices are consistent across different services"""
        prices = self.get_bitcoin_price_from_multiple_sources()

        # Filter out None values
        valid_prices = {k: v for k, v in prices.items() if v is not None and v > 0}

        self.assertGreater(len(valid_prices), 0, "No valid prices retrieved from any source")

        if len(valid_prices) > 1:
            is_consistent = self.validate_price_consistency(prices)

            if not is_consistent:
                # Log the prices for debugging
                price_details = ", ".join([f"{k}: ${v:,.2f}" for k, v in valid_prices.items()])
                self.fail(f"Bitcoin prices show significant deviation: {price_details}")

    def test_price_cli_integration(self):
        """Test price retrieval through CLI interfaces"""
        cli_tests = [
            ("binance_api_cli.py", ["price", "--symbol", "BTCUSDT"]),
            ("blockchain_com_cli.py", ["price"]),
            ("mempool_space_cli.py", ["price"]),
        ]

        prices = {}

        for cli_script, args in cli_tests:
            result = self.run_cli_command(cli_script, args)

            if result["returncode"] == 0:
                try:
                    data = self.validate_json_output(result["stdout"])

                    # Extract price based on service
                    if "binance" in cli_script:
                        price = float(data.get("price", 0))
                    elif "blockchain" in cli_script:
                        price = float(data.get("price_usd", 0))
                    elif "mempool" in cli_script:
                        price = float(data.get("USD", 0)) if isinstance(data, dict) and "USD" in data else 0
                    else:
                        price = 0

                    if price > 0:
                        prices[cli_script] = price

                except Exception:
                    # Individual service failures are acceptable
                    continue

            self.sleep_for_rate_limit(1.0)

        self.assertGreater(len(prices), 0, "No prices retrieved via CLI interfaces")


class TestBitcoinNetworkMetricsIntegration(BitcoinCLIIntegrationTestBase):
    """Test integration of Bitcoin network metrics across services"""

    def test_mempool_data_consistency(self):
        """Test mempool data consistency between Mempool.space and Blockchain.com"""
        mempool_data = {}

        # Get mempool info from Mempool.space
        try:
            mempool_result = self.services["mempool_space"].get_mempool_info()
            if mempool_result:
                mempool_data["mempool_space"] = mempool_result
        except:
            pass

        # Get mempool info from Blockchain.com
        try:
            blockchain_result = self.services["blockchain_com"].get_mempool_info()
            if blockchain_result:
                mempool_data["blockchain_com"] = blockchain_result
        except:
            pass

        self.assertGreater(len(mempool_data), 0, "No mempool data retrieved from any source")

        # Validate that both sources report reasonable mempool sizes
        for source, data in mempool_data.items():
            if isinstance(data, dict):
                # Look for transaction count indicators
                tx_indicators = ["count", "unconfirmed_transactions", "size"]
                found_indicator = any(indicator in data for indicator in tx_indicators)
                self.assertTrue(
                    found_indicator,
                    f"No transaction count indicator found in {source} data",
                )

    def test_mining_difficulty_correlation(self):
        """Test mining difficulty data correlation between services"""
        difficulty_data = {}

        # Get difficulty from Mempool.space
        try:
            mempool_diff = self.services["mempool_space"].get_difficulty_info()
            if mempool_diff and isinstance(mempool_diff, dict):
                difficulty_data["mempool_space"] = mempool_diff
        except:
            pass

        # Get difficulty from Blockchain.com
        try:
            blockchain_diff = self.services["blockchain_com"].get_difficulty()
            if blockchain_diff and isinstance(blockchain_diff, dict):
                difficulty_data["blockchain_com"] = blockchain_diff
        except:
            pass

        self.assertGreater(len(difficulty_data), 0, "No difficulty data retrieved")

        # Validate reasonable difficulty values (Bitcoin difficulty is typically very large)
        for source, data in difficulty_data.items():
            if isinstance(data, dict) and "difficulty" in data:
                difficulty = float(data["difficulty"])
                self.assertGreater(
                    difficulty,
                    1e12,
                    f"Difficulty from {source} seems too low: {difficulty}",
                )

    def test_network_aggregation_service(self):
        """Test the Bitcoin Network Stats aggregation service"""
        try:
            overview = self.services["bitcoin_network_stats"].get_network_overview()

            self.assertIsInstance(overview, dict)
            self.assertIn("sources", overview)
            self.assertIn("timestamp", overview)

            sources = overview.get("sources", [])
            self.assertIsInstance(sources, list)
            self.assertGreater(
                len(sources),
                0,
                "Network stats service should aggregate from multiple sources",
            )

            # Validate that known sources are present
            expected_sources = ["mempool.space", "blockchain.com", "coinmetrics"]
            found_sources = [s for s in expected_sources if s in sources]
            self.assertGreater(
                len(found_sources),
                0,
                f"Expected at least one of {expected_sources} in sources: {sources}",
            )

        except Exception as e:
            self.fail(f"Network aggregation service failed: {e}")


class TestBitcoinCycleIntelligenceWorkflow(BitcoinCLIIntegrationTestBase):
    """Test Bitcoin Cycle Intelligence workflow integration"""

    def test_fear_and_greed_data_pipeline(self):
        """Test Fear & Greed Index data pipeline integration"""
        try:
            # Get current Fear & Greed Index
            current_fng = self.services["alternative_me"].get_current_fear_greed()

            self.assertIsInstance(current_fng, dict)
            self.assertIn("value", current_fng)

            value = int(current_fng["value"])
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 100)

            # Get sentiment analysis
            analysis = self.services["alternative_me"].get_sentiment_analysis(30)

            self.assertIsInstance(analysis, dict)
            self.assertIn("average", analysis)
            self.assertIn("current_value", analysis)

            # Validate that current value matches
            self.assertEqual(analysis["current_value"], value)

        except Exception as e:
            self.fail(f"Fear & Greed data pipeline failed: {e}")

    def test_multi_source_bitcoin_analysis(self):
        """Test multi-source Bitcoin analysis workflow"""
        analysis_data = {
            "price_sources": {},
            "network_metrics": {},
            "sentiment_data": {},
            "errors": [],
        }

        # Collect price data from multiple sources
        try:
            binance_price = self.services["binance_api"].get_bitcoin_data()
            if binance_price:
                analysis_data["price_sources"]["binance"] = binance_price
        except Exception as e:
            analysis_data["errors"].append(f"Binance error: {str(e)}")

        try:
            blockchain_price = self.services["blockchain_com"].get_market_price_usd()
            if blockchain_price:
                analysis_data["price_sources"]["blockchain_com"] = blockchain_price
        except Exception as e:
            analysis_data["errors"].append(f"Blockchain.com error: {str(e)}")

        # Collect network metrics
        try:
            network_overview = self.services["bitcoin_network_stats"].get_network_overview()
            if network_overview:
                analysis_data["network_metrics"] = network_overview
        except Exception as e:
            analysis_data["errors"].append(f"Network stats error: {str(e)}")

        # Collect sentiment data
        try:
            sentiment = self.services["alternative_me"].get_sentiment_analysis(7)
            if sentiment:
                analysis_data["sentiment_data"] = sentiment
        except Exception as e:
            analysis_data["errors"].append(f"Sentiment error: {str(e)}")

        # Validate that we have comprehensive data
        self.assertGreater(len(analysis_data["price_sources"]), 0, "No price sources available")

        # Allow for some errors in integration scenarios
        total_sources = (
            len(analysis_data["price_sources"])
            + (1 if analysis_data["network_metrics"] else 0)
            + (1 if analysis_data["sentiment_data"] else 0)
        )

        self.assertGreater(
            total_sources,
            1,
            "Multi-source analysis requires data from multiple sources",
        )

    def test_historical_data_correlation(self):
        """Test historical data correlation across services"""
        # This test focuses on ensuring services can provide historical data
        # for Bitcoin cycle analysis

        historical_data = {}

        # Try to get historical sentiment data
        try:
            historical_fng = self.services["alternative_me"].get_historical_fear_greed(30)
            if historical_fng and len(historical_fng) > 0:
                historical_data["sentiment"] = len(historical_fng)
        except:
            pass

        # Try to get historical price data from Binance
        try:
            price_history = self.services["binance_api"].get_bitcoin_price_history(7)
            if price_history and price_history.get("price_history"):
                historical_data["price"] = len(price_history["price_history"])
        except:
            pass

        # Try to get network data from CoinMetrics
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            network_data = self.services["coinmetrics"].get_network_data(
                asset="btc", start_date=start_date, end_date=end_date
            )

            if network_data and len(network_data) > 0:
                historical_data["network"] = len(network_data)
        except:
            pass

        self.assertGreater(len(historical_data), 0, "No historical data available from any source")


class TestBitcoinCLIErrorResilience(BitcoinCLIIntegrationTestBase):
    """Test error handling and resilience across Bitcoin CLI services"""

    def test_service_fallback_behavior(self):
        """Test that aggregation services handle individual service failures gracefully"""
        # Test the network stats service which aggregates multiple APIs
        try:
            comprehensive_report = self.services["bitcoin_network_stats"].get_comprehensive_report()

            self.assertIsInstance(comprehensive_report, dict)
            self.assertIn("errors", comprehensive_report)

            # Even with some errors, we should get some data
            sections = [
                "network_overview",
                "mempool_analysis",
                "mining_statistics",
                "network_health",
                "market_data",
            ]
            successful_sections = sum(1 for section in sections if comprehensive_report.get(section))

            self.assertGreater(
                successful_sections,
                0,
                "Aggregation service should provide at least some data even with partial failures",
            )

        except Exception as e:
            self.fail(f"Aggregation service completely failed: {e}")

    def test_invalid_parameter_handling(self):
        """Test handling of invalid parameters across CLI services"""
        invalid_tests = [
            ("alternative_me_cli.py", ["historical", "--limit", "2000"]),  # Over limit
            ("binance_api_cli.py", ["price", "--symbol", "INVALID"]),  # Invalid symbol
            (
                "coinmetrics_cli.py",
                ["network-data", "--start-date", "invalid-date"],
            ),  # Invalid date
        ]

        for cli_script, args in invalid_tests:
            with self.subTest(cli=cli_script, args=args):
                result = self.run_cli_command(cli_script, args)

                # Should handle gracefully (non-zero exit code or error message)
                if result["returncode"] == 0:
                    # If it succeeds, it should have handled the invalid input gracefully
                    # (e.g., corrected the limit, returned an error message)
                    output = result["stdout"].lower() + result["stderr"].lower()
                    self.assertTrue(
                        any(word in output for word in ["error", "invalid", "limit", "corrected"]),
                        f"Service should acknowledge invalid input: {output}",
                    )

    def test_rate_limiting_handling(self):
        """Test that services handle rate limiting appropriately"""
        # Make rapid requests to test rate limiting behavior
        services_to_test = [
            (self.services["mempool_space"], "get_fee_estimates"),
            (self.services["blockchain_com"], "get_latest_block"),
            (self.services["binance_api"], "get_server_time"),
        ]

        for service, method_name in services_to_test:
            with self.subTest(service=type(service).__name__, method=method_name):
                method = getattr(service, method_name)

                successful_calls = 0
                rate_limited_calls = 0

                # Make several rapid calls
                for i in range(5):
                    try:
                        result = method()
                        if result:
                            successful_calls += 1
                    except Exception as e:
                        if "rate" in str(e).lower() or "limit" in str(e).lower():
                            rate_limited_calls += 1
                        # Other errors are acceptable

                    time.sleep(0.2)  # Brief delay

                # We should get at least some successful calls or appropriate rate limiting
                self.assertTrue(
                    successful_calls > 0 or rate_limited_calls > 0,
                    f"Service {type(service).__name__} should either succeed or handle rate limiting",
                )


class TestBitcoinCLIPerformance(BitcoinCLIIntegrationTestBase):
    """Test performance and reliability of Bitcoin CLI services"""

    def test_cli_response_times(self):
        """Test that CLI commands respond within reasonable time limits"""
        fast_commands = [
            ("alternative_me_cli.py", ["current"]),
            ("binance_api_cli.py", ["price", "--symbol", "BTCUSDT"]),
            ("mempool_space_cli.py", ["fees"]),
        ]

        for cli_script, args in fast_commands:
            with self.subTest(cli=cli_script):
                start_time = time.time()

                result = self.run_cli_command(cli_script, args)

                end_time = time.time()
                response_time = end_time - start_time

                # Most simple API calls should complete within 10 seconds
                self.assertLess(
                    response_time,
                    10.0,
                    f"{cli_script} took too long: {response_time:.2f}s",
                )

                if result["returncode"] == 0:
                    # If successful, response should be valid JSON
                    self.validate_json_output(result["stdout"])

    def test_concurrent_service_usage(self):
        """Test that multiple services can be used concurrently without conflicts"""
        import concurrent.futures

        def call_service(service_info):
            service_name, service, method_name = service_info
            try:
                method = getattr(service, method_name)
                result = method()
                return (service_name, True, result)
            except Exception as e:
                return (service_name, False, str(e))

        service_calls = [
            (
                "alternative_me",
                self.services["alternative_me"],
                "get_current_fear_greed",
            ),
            ("binance_api", self.services["binance_api"], "get_server_time"),
            ("mempool_space", self.services["mempool_space"], "get_fee_estimates"),
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(call_service, service_info) for service_info in service_calls]
            results = [future.result(timeout=15) for future in concurrent.futures.as_completed(futures, timeout=20)]

        successful_calls = [r for r in results if r[1]]
        self.assertGreater(
            len(successful_calls),
            0,
            "At least some concurrent service calls should succeed",
        )


if __name__ == "__main__":
    # Configure test runner for integration tests
    unittest.main(
        verbosity=2,
        failfast=False,  # Continue running tests even if some fail
        buffer=True,  # Capture stdout/stderr during tests
    )
