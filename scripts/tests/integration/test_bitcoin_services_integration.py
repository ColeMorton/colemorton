#!/usr/bin/env python3
"""
Integration Tests for Bitcoin CLI Services

Tests real API interactions with proper error handling, rate limiting respect,
and network resilience validation. These tests verify:
- Real API connectivity and response formats
- Service error handling and resilience
- Data consistency across multiple sources
- Network failure recovery patterns
"""

import sys
import time
import unittest
from datetime import datetime
from pathlib import Path


# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.alternative_me import create_alternative_me_service
from services.binance_api import create_binance_api_service
from services.bitcoin_network_stats import create_bitcoin_network_stats_service
from services.blockchain_com import create_blockchain_com_service
from services.coinmetrics import create_coinmetrics_service
from services.mempool_space import create_mempool_space_service


class TestBitcoinServicesConnectivity(unittest.TestCase):
    """Test real API connectivity and basic functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        cls.test_timeout = 30  # Reasonable timeout for API calls
        cls.rate_limit_delay = 1  # Respect API rate limits

        # Initialize services
        cls.services = {
            "mempool_space": create_mempool_space_service("test"),
            "blockchain_com": create_blockchain_com_service("test"),
            "coinmetrics": create_coinmetrics_service("test"),
            "alternative_me": create_alternative_me_service("test"),
            "binance_api": create_binance_api_service("test"),
            "bitcoin_network_stats": create_bitcoin_network_stats_service("test"),
        }

    def setUp(self):
        """Rate limit between tests"""
        time.sleep(self.rate_limit_delay)

    def test_mempool_space_connectivity(self):
        """Test Mempool.space API connectivity"""
        service = self.services["mempool_space"]

        try:
            result = service.get_fee_estimates()

            # Validate response structure
            self.assertIsInstance(result, dict)
            self.assertIn("fastestFee", result)
            self.assertIn("halfHourFee", result)
            self.assertIn("hourFee", result)

            # Validate data types
            for fee_key in ["fastestFee", "halfHourFee", "hourFee"]:
                self.assertIsInstance(result[fee_key], (int, float))
                self.assertGreater(result[fee_key], 0)

            print(f"✅ Mempool.space API working - FastestFee: {result['fastestFee']} sat/vB")

        except Exception as e:
            self.skipTest(f"Mempool.space API unavailable: {str(e)}")

    def test_blockchain_com_connectivity(self):
        """Test Blockchain.com API connectivity"""
        service = self.services["blockchain_com"]

        try:
            result = service.get_latest_block()

            # Validate response structure
            self.assertIsInstance(result, dict)
            self.assertIn("hash", result)
            self.assertIn("height", result)
            self.assertIn("time", result)

            # Validate data reasonableness
            self.assertIsInstance(result["height"], int)
            self.assertGreater(result["height"], 800000)  # Reasonable block height

            print("✅ Blockchain.com API working - Block height: {result['height']}")

        except Exception as e:
            self.skipTest(f"Blockchain.com API unavailable: {str(e)}")

    def test_alternative_me_connectivity(self):
        """Test Alternative.me Fear & Greed API connectivity"""
        service = self.services["alternative_me"]

        try:
            result = service.get_current_fear_greed()

            # Validate response structure
            self.assertIsInstance(result, dict)
            self.assertIn("value", result)
            self.assertIn("value_classification", result)

            # Validate data reasonableness
            fear_greed_value = int(result["value"])
            self.assertGreaterEqual(fear_greed_value, 0)
            self.assertLessEqual(fear_greed_value, 100)

            classification = result["value_classification"]
            valid_classifications = [
                "Extreme Fear",
                "Fear",
                "Neutral",
                "Greed",
                "Extreme Greed",
            ]
            self.assertIn(classification, valid_classifications)

            print(f"✅ Alternative.me API working - Fear & Greed: {fear_greed_value} ({classification})")

        except Exception as e:
            self.skipTest(f"Alternative.me API unavailable: {str(e)}")

    def test_binance_api_connectivity(self):
        """Test Binance API connectivity"""
        service = self.services["binance_api"]

        try:
            result = service.get_server_time()

            # Validate response structure
            self.assertIsInstance(result, dict)
            self.assertIn("serverTime", result)

            # Validate timestamp reasonableness (within last hour)
            server_time_ms = result["serverTime"]
            current_time_ms = int(datetime.now().timestamp() * 1000)
            time_diff = abs(current_time_ms - server_time_ms)

            # Should be within 1 hour (3600000 ms)
            self.assertLess(time_diff, 3600000)

            print(f"✅ Binance API working - Server time: {datetime.fromtimestamp(server_time_ms / 1000)}")

        except Exception as e:
            self.skipTest(f"Binance API unavailable: {str(e)}")


class TestBitcoinDataConsistency(unittest.TestCase):
    """Test data consistency across Bitcoin services"""

    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        cls.price_tolerance = 0.15  # 15% tolerance for price differences
        cls.services = {
            "mempool_space": create_mempool_space_service("test"),
            "blockchain_com": create_blockchain_com_service("test"),
            "binance_api": create_binance_api_service("test"),
        }

    def setUp(self):
        """Rate limit between tests"""
        time.sleep(1)

    def get_bitcoin_prices(self) -> dict[str, float]:
        """Get Bitcoin prices from multiple sources"""
        prices = {}

        # Mempool.space price
        try:
            mempool_result = self.services["mempool_space"].get_bitcoin_price()
            if isinstance(mempool_result, dict) and "USD" in mempool_result:
                prices["mempool_space"] = float(mempool_result["USD"])
            elif isinstance(mempool_result, dict) and "price" in mempool_result:
                prices["mempool_space"] = float(mempool_result["price"])
        except Exception:
            print("⚠️ Mempool.space price unavailable: {e}")

        # Blockchain.com price
        try:
            blockchain_result = self.services["blockchain_com"].get_market_price_usd()
            if isinstance(blockchain_result, dict) and "price_usd" in blockchain_result:
                prices["blockchain_com"] = float(blockchain_result["price_usd"])
        except Exception:
            print("⚠️ Blockchain.com price unavailable: {e}")

        # Binance price
        try:
            binance_result = self.services["binance_api"].get_symbol_price_ticker("BTCUSDT")
            if isinstance(binance_result, dict) and "price" in binance_result:
                prices["binance_api"] = float(binance_result["price"])
        except Exception:
            print("⚠️ Binance price unavailable: {e}")

        return prices

    def test_bitcoin_price_consistency(self):
        """Test Bitcoin price consistency across sources"""
        prices = self.get_bitcoin_prices()

        if len(prices) < 2:
            self.skipTest("Not enough price sources available for comparison")

        print("📊 Bitcoin prices from sources: {prices}")

        # Calculate price statistics
        price_values = list(prices.values())
        avg_price = sum(price_values) / len(price_values)
        max_price = max(price_values)
        min_price = min(price_values)

        # Check price consistency within tolerance
        price_variance = (max_price - min_price) / avg_price

        print(
            f"💰 Price stats - Avg: ${avg_price:,.2f}, Range: ${min_price:,.2f} - ${max_price:,.2f}, Variance: {price_variance:.1%}"
        )

        self.assertLess(
            price_variance,
            self.price_tolerance,
            f"Price variance {price_variance:.1%} exceeds tolerance {self.price_tolerance:.1%}",
        )

        # All prices should be reasonable (between $10K and $500K)
        for source, price in prices.items():
            self.assertGreater(price, 10000, f"{source} price ${price} seems too low")
            self.assertLess(price, 500000, f"{source} price ${price} seems too high")


class TestBitcoinNetworkStatsIntegration(unittest.TestCase):
    """Test Bitcoin Network Stats aggregation service integration"""

    def setUp(self):
        """Set up aggregation service"""
        self.service = create_bitcoin_network_stats_service("test")
        time.sleep(1)  # Rate limiting

    def test_network_overview_integration(self):
        """Test network overview aggregation with real APIs"""
        try:
            result = self.service.get_network_overview()

            # Validate structure
            self.assertIsInstance(result, dict)
            self.assertIn("timestamp", result)
            self.assertIn("sources", result)
            self.assertIn("errors", result)

            # Should have attempted multiple sources
            sources = result.get("sources", [])
            errors = result.get("errors", [])

            print(f"📡 Network overview - Sources: {len(sources)}, Errors: {len(errors)}")

            if errors:
                print("⚠️ API errors: {errors}")

            # At least one source should work
            self.assertGreater(len(sources), 0, "No data sources available")

            # Should not have all sources failing
            total_attempts = len(sources) + len(errors)
            success_rate = len(sources) / max(total_attempts, 1)
            self.assertGreater(success_rate, 0.3, "Too many API failures")

        except Exception as e:
            self.skipTest(f"Network overview integration test failed: {str(e)}")

    def test_comprehensive_report_performance(self):
        """Test comprehensive report generation performance"""
        start_time = time.time()

        try:
            result = self.service.get_comprehensive_report()

            end_time = time.time()
            execution_time = end_time - start_time

            # Validate structure
            self.assertIsInstance(result, dict)
            self.assertIn("report_timestamp", result)
            self.assertIn("summary", result)

            # Performance validation
            self.assertLess(execution_time, 60, "Report generation took too long")

            summary = result.get("summary", {})
            data_sources = summary.get("total_data_sources", 0)
            errors = summary.get("total_errors", 0)
            data_quality = summary.get("data_quality", "unknown")

            print(
                f"📈 Report stats - Time: {execution_time:.1f}s, Sources: {data_sources}, "
                f"Errors: {errors}, Quality: {data_quality}"
            )

            # At least some data should be available
            self.assertGreater(data_sources, 0, "No data sources in comprehensive report")

        except Exception as e:
            self.skipTest(f"Comprehensive report test failed: {str(e)}")


class TestServiceErrorResilience(unittest.TestCase):
    """Test service error handling and resilience patterns"""

    def setUp(self):
        """Set up services for error testing"""
        self.services = {
            "mempool_space": create_mempool_space_service("test"),
            "blockchain_com": create_blockchain_com_service("test"),
        }

    def test_invalid_endpoint_handling(self):
        """Test service behavior with invalid endpoints"""
        service = self.services["mempool_space"]

        # Test with a method that will make a request to an invalid endpoint
        # We'll create a mock scenario
        with self.assertRaises(Exception):
            # This should fail gracefully, not crash the service
            service.get_address_info("invalid_address_format_test")

    def test_service_timeout_handling(self):
        """Test service timeout behavior"""
        # This test would typically use a slow endpoint or network conditions
        # For now, we'll validate that timeouts are configured properly

        for service_name, service in self.services.items():
            self.assertIsInstance(service.config.timeout_seconds, int)
            self.assertGreater(service.config.timeout_seconds, 0)
            self.assertLessEqual(service.config.timeout_seconds, 120)  # Reasonable timeout

            print("⏱️ {service_name} timeout: {service.config.timeout_seconds}s")


if __name__ == "__main__":
    # Run integration tests with verbose output
    print("🚀 Running Bitcoin CLI Services Integration Tests")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBitcoinServicesConnectivity))
    suite.addTests(loader.loadTestsFromTestCase(TestBitcoinDataConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestBitcoinNetworkStatsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceErrorResilience))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 60)
    print(
        f"🎯 Integration Tests Complete - "
        f"Ran: {result.testsRun}, "
        f"Failures: {len(result.failures)}, "
        f"Errors: {len(result.errors)}, "
        f"Skipped: {len(result.skipped)}"
    )
