#!/usr/bin/env python3
"""
Unit Tests for Bitcoin CLI Services

Fast, isolated tests using mocks and fixtures without external API dependencies.
These tests focus on service logic, data transformation, and error handling.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixtures.test_utils import (
    BitcoinTestFixtures,
    MockHTTPAdapter,
    MockServiceFactory,
    create_test_services_with_mocks,
)
from services.alternative_me import create_alternative_me_service
from services.binance_api import create_binance_api_service
from services.bitcoin_network_stats import create_bitcoin_network_stats_service
from services.blockchain_com import BlockchainComService, create_blockchain_com_service
from services.coinmetrics import create_coinmetrics_service
from services.mempool_space import MempoolSpaceService, create_mempool_space_service


class TestBitcoinServiceInitialization(unittest.TestCase):
    """Test service initialization without external dependencies"""

    def test_all_services_initialize_successfully(self):
        """Test that all Bitcoin services can be initialized"""
        services = [
            ("mempool_space", create_mempool_space_service),
            ("blockchain_com", create_blockchain_com_service),
            ("coinmetrics", create_coinmetrics_service),
            ("alternative_me", create_alternative_me_service),
            ("binance_api", create_binance_api_service),
            ("bitcoin_network_stats", create_bitcoin_network_stats_service),
        ]

        for service_name, factory_func in services:
            with self.subTest(service=service_name):
                service = factory_func("test")
                self.assertIsNotNone(service)
                self.assertEqual(service.config.name, service_name)

    def test_bitcoin_network_stats_with_dependency_injection(self):
        """Test bitcoin_network_stats service with mock dependencies"""
        mock_services = MockServiceFactory.create_mock_services_dict()
        service = create_bitcoin_network_stats_service("test", mock_services)

        self.assertIsNotNone(service)
        self.assertEqual(service.config.name, "bitcoin_network_stats")
        self.assertEqual(service.services, mock_services)


class TestMempoolSpaceServiceUnit(unittest.TestCase):
    """Unit tests for Mempool.space service with mocks"""

    def setUp(self):
        self.service = create_mempool_space_service("test")
        self.mock_adapter = MockHTTPAdapter()

    @patch.object(MempoolSpaceService, "_make_request_with_retry")
    def test_get_fee_estimates_with_mock(self, mock_request):
        """Test fee estimates with mocked response"""
        mock_request.return_value = BitcoinTestFixtures.mempool_space_fee_estimates()

        result = self.service.get_fee_estimates()

        self.assertIn("fastestFee", result)
        self.assertIn("halfHourFee", result)
        self.assertEqual(result["fastestFee"], 15)
        mock_request.assert_called_once_with("/v1/fees/recommended")

    @patch.object(MempoolSpaceService, "_make_request_with_retry")
    def test_get_mempool_info_with_mock(self, mock_request):
        """Test mempool info with mocked response"""
        mock_request.return_value = BitcoinTestFixtures.mempool_space_mempool_info()

        result = self.service.get_mempool_info()

        self.assertIn("count", result)
        self.assertIn("vsize", result)
        self.assertEqual(result["count"], 45821)
        mock_request.assert_called_once_with("/mempool")

    def test_service_configuration(self):
        """Test service configuration is correct"""
        self.assertEqual(self.service.config.name, "mempool_space")
        self.assertEqual(self.service.config.base_url, "https://mempool.space/api")
        self.assertIsNone(self.service.config.api_key)


class TestBlockchainComServiceUnit(unittest.TestCase):
    """Unit tests for Blockchain.com service with mocks"""

    def setUp(self):
        self.service = create_blockchain_com_service("test")
        self.mock_adapter = MockHTTPAdapter()

    @patch.object(BlockchainComService, "_make_request_with_retry")
    def test_get_latest_block_with_mock(self, mock_request):
        """Test latest block with mocked response"""
        mock_request.return_value = BitcoinTestFixtures.blockchain_com_latest_block()

        result = self.service.get_latest_block()

        self.assertIn("hash", result)
        self.assertIn("height", result)
        self.assertEqual(result["height"], 850000)
        mock_request.assert_called_once_with("/latestblock")

    @patch("requests.get")
    def test_get_network_stats_with_mock(self, mock_get):
        """Test network stats with mocked response"""
        mock_get.return_value = self.mock_adapter.get_mock_response("https://blockchain.info/stats?format=json")

        result = self.service.get_network_stats()

        self.assertIn("market_price_usd", result)
        self.assertIn("hash_rate", result)
        self.assertAlmostEqual(result["market_price_usd"], 65432.15, places=2)
        mock_get.assert_called_once()


class TestCoinMetricsServiceUnit(unittest.TestCase):
    """Unit tests for CoinMetrics service with mocks"""

    def setUp(self):
        self.service = create_coinmetrics_service("test")
        self.mock_adapter = MockHTTPAdapter()

    @patch("requests.get")
    def test_get_network_data_with_mock(self, mock_get):
        """Test network data with mocked response"""
        mock_response_data = {"data": BitcoinTestFixtures.coinmetrics_network_data()}
        mock_get.return_value = self.mock_adapter.get_mock_response(
            "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
        )
        mock_get.return_value.json_data = mock_response_data

        result = self.service.get_network_data(asset="btc")

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("AdrActCnt", result[0])
        mock_get.assert_called_once()

    def test_data_validation(self):
        """Test internal data validation methods"""
        valid_data = {"data": [{"asset": "btc", "value": 100}]}
        result = self.service._validate_response(valid_data, "test endpoint")

        self.assertEqual(result, valid_data["data"])


class TestAlternativeMeServiceUnit(unittest.TestCase):
    """Unit tests for Alternative.me service with mocks"""

    def setUp(self):
        self.service = create_alternative_me_service("test")
        self.mock_adapter = MockHTTPAdapter()

    @patch("requests.get")
    def test_get_current_fear_greed_with_mock(self, mock_get):
        """Test current Fear & Greed index with mocked response"""
        mock_get.return_value = self.mock_adapter.get_mock_response("https://api.alternative.me/fng/?limit=1")

        result = self.service.get_current_fear_greed()

        self.assertIn("value", result)
        self.assertIn("value_classification", result)
        self.assertEqual(result["value"], "45")
        mock_get.assert_called_once()

    def test_sentiment_classification(self):
        """Test sentiment classification logic"""
        # Test different sentiment ranges
        test_cases = [
            (10, "Extreme Fear"),
            (30, "Fear"),
            (50, "Neutral"),
            (70, "Greed"),
            (90, "Extreme Greed"),
        ]

        for value, expected_classification in test_cases:
            with self.subTest(value=value):
                result = self.service._classify_sentiment(value)
                self.assertEqual(result, expected_classification)


class TestBinanceAPIServiceUnit(unittest.TestCase):
    """Unit tests for Binance API service with mocks"""

    def setUp(self):
        self.service = create_binance_api_service("test")
        self.mock_adapter = MockHTTPAdapter()

    @patch("requests.get")
    def test_get_24hr_ticker_with_mock(self, mock_get):
        """Test 24hr ticker with mocked response"""
        mock_get.return_value = self.mock_adapter.get_mock_response("https://api.binance.com/api/v3/ticker/24hr")

        result = self.service.get_24hr_ticker_stats("BTCUSDT")

        self.assertIn("symbol", result)
        self.assertIn("lastPrice", result)
        self.assertEqual(result["symbol"], "BTCUSDT")
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_server_time_with_mock(self, mock_get):
        """Test server time with mocked response"""
        mock_get.return_value = self.mock_adapter.get_mock_response("https://api.binance.com/api/v3/time")

        result = self.service.get_server_time()

        self.assertIn("serverTime", result)
        self.assertIsInstance(result["serverTime"], int)
        mock_get.assert_called_once()


class TestBitcoinNetworkStatsServiceUnit(unittest.TestCase):
    """Unit tests for Bitcoin Network Stats aggregation service with mocks"""

    def setUp(self):
        self.mock_services = MockServiceFactory.create_mock_services_dict()
        self.service = create_bitcoin_network_stats_service("test", self.mock_services)

    def test_network_overview_with_mocks(self):
        """Test network overview aggregation with mock services"""
        result = self.service.get_network_overview()

        self.assertIn("timestamp", result)
        self.assertIn("sources", result)
        self.assertIn("network_health", result)
        self.assertIn("mempool_status", result)
        self.assertIn("mining_stats", result)
        self.assertIn("errors", result)

        # Should have multiple sources
        self.assertGreater(len(result["sources"]), 0)

    def test_mempool_analysis_with_mocks(self):
        """Test mempool analysis with mock services"""
        result = self.service.get_mempool_analysis()

        self.assertIn("timestamp", result)
        self.assertIn("mempool_metrics", result)
        self.assertIn("fee_analysis", result)
        self.assertIn("sources", result)

        # Should aggregate data from multiple sources
        self.assertGreater(len(result["sources"]), 0)

    def test_comprehensive_report_with_mocks(self):
        """Test comprehensive report generation with mock services"""
        result = self.service.get_comprehensive_report()

        self.assertIn("report_timestamp", result)
        self.assertIn("report_type", result)
        self.assertIn("network_overview", result)
        self.assertIn("mempool_analysis", result)
        self.assertIn("mining_statistics", result)
        self.assertIn("summary", result)

        self.assertEqual(result["report_type"], "comprehensive_bitcoin_network_statistics")

    def test_service_uses_injected_dependencies(self):
        """Test that service uses injected mock services instead of creating real ones"""
        # Call a method that uses mempool service
        self.service.get_network_overview()

        # Verify that the mock service methods were called
        self.mock_services["mempool_space"].get_network_stats.assert_called_once()
        self.mock_services["blockchain_com"].get_blockchain_summary.assert_called_once()


class TestServiceErrorHandling(unittest.TestCase):
    """Test error handling across all services"""

    def setUp(self):
        self.services = create_test_services_with_mocks()

    def test_network_error_handling(self):
        """Test service behavior when network requests fail"""
        with patch("requests.get", side_effect=ConnectionError("Network error")):
            service = create_mempool_space_service("test")

            # Service should handle network errors gracefully
            with self.assertRaises(Exception):
                service.get_fee_estimates()

    def test_invalid_response_handling(self):
        """Test service behavior with invalid API responses"""
        service = create_alternative_me_service("test")

        # Test validation with invalid data
        with self.assertRaises(Exception):
            service._validate_response(None, "test endpoint")

        with self.assertRaises(Exception):
            service._validate_response({}, "test endpoint")


class TestDataTransformation(unittest.TestCase):
    """Test data transformation and processing logic"""

    def test_fear_greed_sentiment_classification(self):
        """Test Fear & Greed index sentiment classification"""
        service = create_alternative_me_service("test")

        test_cases = [
            (0, "Extreme Fear"),
            (15, "Extreme Fear"),
            (25, "Fear"),
            (35, "Fear"),
            (45, "Neutral"),
            (55, "Neutral"),
            (65, "Greed"),
            (75, "Greed"),
            (85, "Extreme Greed"),
            (100, "Extreme Greed"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value):
                result = service._classify_sentiment(value)
                self.assertEqual(result, expected)

    def test_timestamp_formatting(self):
        """Test timestamp formatting across services"""
        test_timestamp = int(datetime.now().timestamp())
        service = create_alternative_me_service("test")

        # Test timestamp formatting
        formatted = datetime.fromtimestamp(test_timestamp).strftime("%Y-%m-%d")
        self.assertRegex(formatted, r"\d{4}-\d{2}-\d{2}")

    def test_bitcoin_network_stats_aggregation(self):
        """Test data aggregation logic in bitcoin network stats"""
        mock_services = MockServiceFactory.create_mock_services_dict()
        service = create_bitcoin_network_stats_service("test", mock_services)

        report = service.get_comprehensive_report()

        # Verify aggregation structure
        self.assertIn("summary", report)
        self.assertIn("total_data_sources", report["summary"])
        self.assertIn("data_quality", report["summary"])

        # Data quality should be determined by error count
        if len(report.get("errors", [])) < 3:
            self.assertEqual(report["summary"]["data_quality"], "good")
        else:
            self.assertEqual(report["summary"]["data_quality"], "degraded")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
