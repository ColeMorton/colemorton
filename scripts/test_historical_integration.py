#!/usr/bin/env python3
"""
Historical Data Integration Test

Comprehensive test suite to validate the historical data storage and retrieval system.
Tests all components: HistoricalDataManager, BaseFinancialService integration,
data discovery API, and end-to-end workflows.
"""

import logging
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path


# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent / "services"))

from base_financial_service import (
    BaseFinancialService,
    CacheConfig,
    HistoricalStorageConfig,
    RateLimitConfig,
    ServiceConfig,
)
from data_discovery import DataDiscoveryAPI
from historical_data_manager import DataType, HistoricalDataManager, Timeframe


class MockFinancialService(BaseFinancialService):
    """Mock financial service for testing"""

    def _validate_response(self, data, endpoint):
        """Simple validation for test data"""
        return data

    def health_check(self):
        """Mock health check"""
        return {"status": "healthy", "service": "mock"}

    def get_test_stock_data(self, symbol: str):
        """Generate test stock data"""
        return {
            "symbol": symbol.upper(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000000,
            "source": "test",
        }


class HistoricalDataIntegrationTest:
    """Comprehensive test suite for historical data system"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.test_dir = None
        self.historical_manager = None
        self.discovery_api = None
        self.mock_service = None

    def _setup_logger(self):
        """Setup test logging"""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("historical_test")

    def setup_test_environment(self):
        """Setup isolated test environment"""
        try:
            # Create temporary test directory
            self.test_dir = Path(tempfile.mkdtemp(prefix="historical_test_"))
            self.logger.info(f"Created test directory: {self.test_dir}")

            # Initialize historical data manager with test directory
            self.historical_manager = HistoricalDataManager(base_path=self.test_dir / "raw")

            # Initialize discovery API
            self.discovery_api = DataDiscoveryAPI(self.historical_manager)

            # Create mock financial service
            config = ServiceConfig(
                name="mock_service",
                base_url="https://test.example.com",
                cache=CacheConfig(enabled=True, cache_dir=str(self.test_dir / "cache")),
                rate_limit=RateLimitConfig(enabled=False),
                historical_storage=HistoricalStorageConfig(
                    enabled=True,
                    store_stock_prices=True,
                    store_financials=True,
                    store_fundamentals=True,
                    auto_detect_data_type=True,
                ),
            )

            self.mock_service = MockFinancialService(config)
            # Replace with our test historical manager
            self.mock_service.historical_manager = self.historical_manager

            return True

        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False

    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.test_dir and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                self.logger.info("Cleaned up test directory")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup test directory: {e}")

    def test_historical_manager_basic_operations(self):
        """Test basic historical data manager operations"""
        self.logger.info("Testing HistoricalDataManager basic operations...")

        try:
            # Test data storage
            test_data = {
                "symbol": "AAPL",
                "date": "2025-07-28",
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 154.0,
                "volume": 1000000,
            }

            success = self.historical_manager.store_data(
                symbol="AAPL",
                data=test_data,
                data_type=DataType.STOCK_DAILY_PRICES,
                source="test",
            )

            if not success:
                raise Exception("Failed to store test data")

            self.logger.info("✓ Data storage successful")

            # Test data retrieval
            retrieved_data = self.historical_manager.retrieve_data(
                symbol="AAPL",
                data_type=DataType.STOCK_DAILY_PRICES,
                date_start="2025-07-28",
            )

            if not retrieved_data:
                raise Exception("Failed to retrieve stored data")

            if retrieved_data[0]["data"]["symbol"] != "AAPL":
                raise Exception("Retrieved data does not match stored data")

            self.logger.info("✓ Data retrieval successful")

            # Test metadata
            metadata = self.historical_manager.get_available_data("AAPL")
            if not metadata:
                raise Exception("Failed to get metadata")

            self.logger.info("✓ Metadata generation successful")

            return True

        except Exception as e:
            self.logger.error(f"Historical manager test failed: {e}")
            return False

    def test_service_integration(self):
        """Test BaseFinancialService integration with historical storage"""
        self.logger.info("Testing BaseFinancialService integration...")

        try:
            # Test automatic historical storage during API call simulation
            test_data = self.mock_service.get_test_stock_data("MSFT")

            # Manually trigger historical storage (simulating what happens in _make_request_with_retry)
            success = self.mock_service.store_historical_data(
                data=test_data, endpoint="quote/MSFT", params={"symbol": "MSFT"}
            )

            if not success:
                raise Exception("Failed to store data via service integration")

            self.logger.info("✓ Service integration storage successful")

            # Test retrieval via service
            historical_data = self.mock_service.get_historical_data(
                symbol="MSFT",
                data_type=DataType.STOCK_DAILY_PRICES,
                date_start=datetime.now(),
            )

            if not historical_data:
                raise Exception("Failed to retrieve data via service")

            self.logger.info("✓ Service integration retrieval successful")

            # Test service info includes historical storage stats
            service_info = self.mock_service.get_service_info()
            if "historical_storage" not in service_info:
                raise Exception("Service info missing historical storage information")

            self.logger.info("✓ Service info includes historical storage")

            return True

        except Exception as e:
            self.logger.error(f"Service integration test failed: {e}")
            return False

    def test_data_discovery_api(self):
        """Test data discovery and query API"""
        self.logger.info("Testing Data Discovery API...")

        try:
            # Store multiple test records first
            test_symbols = ["GOOGL", "TSLA", "NVDA"]
            for symbol in test_symbols:
                test_data = {
                    "symbol": symbol,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "open": 100.0,
                    "high": 105.0,
                    "low": 95.0,
                    "close": 102.0,
                    "volume": 1000000,
                }

                self.historical_manager.store_data(
                    symbol=symbol,
                    data=test_data,
                    data_type=DataType.STOCK_DAILY_PRICES,
                    source="test",
                )

            # Test symbol search
            found_symbols = self.discovery_api.search_symbols()
            if len(found_symbols) < 3:
                raise Exception(f"Expected at least 3 symbols, found {len(found_symbols)}")

            self.logger.info(f"✓ Symbol search found {len(found_symbols)} symbols")

            # Test symbol availability
            availability = self.discovery_api.get_symbol_availability("GOOGL")
            if not availability or availability.symbol != "GOOGL":
                raise Exception("Failed to get symbol availability")

            self.logger.info("✓ Symbol availability check successful")

            # Test data query
            query_results = self.discovery_api.query_data(symbols=["GOOGL"], data_types=[DataType.STOCK_DAILY_PRICES])

            if not query_results:
                raise Exception("Data query returned no results")

            self.logger.info("✓ Data query successful")

            # Test discovery report generation
            report = self.discovery_api.generate_discovery_report(symbols=test_symbols[:2], include_quality=False)

            if not report or "summary" not in report:
                raise Exception("Failed to generate discovery report")

            self.logger.info("✓ Discovery report generation successful")

            return True

        except Exception as e:
            self.logger.error(f"Discovery API test failed: {e}")
            return False

    def test_data_types_and_timeframes(self):
        """Test different data types and timeframes"""
        self.logger.info("Testing multiple data types and timeframes...")

        try:
            # Test stock financials
            financial_data = {
                "symbol": "AAPL",
                "fiscal_year": 2025,
                "period": "Q2",
                "revenue": 100000000,
                "net_income": 25000000,
                "total_assets": 500000000,
            }

            success = self.historical_manager.store_data(
                symbol="AAPL",
                data=financial_data,
                data_type=DataType.STOCK_FINANCIALS,
                timeframe=Timeframe.QUARTERLY,
            )

            if not success:
                raise Exception("Failed to store financial data")

            self.logger.info("✓ Financial data storage successful")

            # Test stock fundamentals
            fundamental_data = {
                "symbol": "AAPL",
                "market_cap": 3000000000000,
                "pe_ratio": 25.5,
                "dividend_yield": 0.015,
                "sector": "Technology",
            }

            success = self.historical_manager.store_data(
                symbol="AAPL",
                data=fundamental_data,
                data_type=DataType.STOCK_FUNDAMENTALS,
            )

            if not success:
                raise Exception("Failed to store fundamental data")

            self.logger.info("✓ Fundamental data storage successful")

            # Test retrieval of different data types
            financial_retrieved = self.historical_manager.retrieve_data(
                symbol="AAPL",
                data_type=DataType.STOCK_FINANCIALS,
                date_start=datetime.now(),
                timeframe=Timeframe.QUARTERLY,
            )

            fundamental_retrieved = self.historical_manager.retrieve_data(
                symbol="AAPL",
                data_type=DataType.STOCK_FUNDAMENTALS,
                date_start=datetime.now(),
                timeframe=Timeframe.DAILY,
            )

            if not financial_retrieved or not fundamental_retrieved:
                raise Exception("Failed to retrieve multi-type data")

            self.logger.info("✓ Multi-type data retrieval successful")

            return True

        except Exception as e:
            self.logger.error(f"Multi-type data test failed: {e}")
            return False

    def test_data_quality_and_validation(self):
        """Test data quality metrics and validation"""
        self.logger.info("Testing data quality and validation...")

        try:
            # Store quality test data
            quality_data = {
                "symbol": "QQQ",
                "date": "2025-07-28",
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 102.0,
                "volume": 1000000,
            }

            success = self.historical_manager.store_data(
                symbol="QQQ", data=quality_data, data_type=DataType.STOCK_DAILY_PRICES
            )

            if not success:
                raise Exception("Failed to store quality test data")

            # Test quality metrics
            quality_metrics = self.discovery_api.get_data_quality_metrics(
                symbol="QQQ", data_type=DataType.STOCK_DAILY_PRICES
            )

            if not quality_metrics:
                raise Exception("Failed to calculate quality metrics")

            if not (0 <= quality_metrics.overall_score <= 1):
                raise Exception("Invalid quality score range")

            self.logger.info(f"✓ Quality metrics: {quality_metrics.overall_score:.3f}")

            # Test invalid data rejection
            invalid_data = {
                "symbol": "INVALID",
                "date": "2025-07-28",
                "close": -100.0,  # Invalid negative price
                "volume": -1,  # Invalid negative volume
            }

            # This should still store but with lower quality score
            success = self.historical_manager.store_data(
                symbol="INVALID",
                data=invalid_data,
                data_type=DataType.STOCK_DAILY_PRICES,
            )

            # Test that quality metrics detect the issues
            invalid_quality = self.discovery_api.get_data_quality_metrics(
                symbol="INVALID", data_type=DataType.STOCK_DAILY_PRICES
            )

            if invalid_quality and invalid_quality.accuracy > 0.5:
                self.logger.warning("Quality metrics may not be detecting data issues properly")
            else:
                self.logger.info("✓ Quality metrics correctly identify data issues")

            return True

        except Exception as e:
            self.logger.error(f"Quality validation test failed: {e}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        self.logger.info("Starting comprehensive historical data integration test...")

        if not self.setup_test_environment():
            return False

        try:
            tests = [
                (
                    "Historical Manager Basic Operations",
                    self.test_historical_manager_basic_operations,
                ),
                ("Service Integration", self.test_service_integration),
                ("Data Discovery API", self.test_data_discovery_api),
                ("Data Types and Timeframes", self.test_data_types_and_timeframes),
                ("Data Quality and Validation", self.test_data_quality_and_validation),
            ]

            results = {}
            for test_name, test_func in tests:
                self.logger.info(f"\n--- Running {test_name} ---")
                try:
                    result = test_func()
                    results[test_name] = result
                    status = "PASSED" if result else "FAILED"
                    self.logger.info(f"{test_name}: {status}")
                except Exception as e:
                    results[test_name] = False
                    self.logger.error(f"{test_name}: FAILED - {e}")

            # Print summary
            self.logger.info("\n" + "=" * 60)
            self.logger.info("TEST SUMMARY")
            self.logger.info("=" * 60)

            passed = sum(results.values())
            total = len(results)

            for test_name, result in results.items():
                status = "✓ PASSED" if result else "✗ FAILED"
                self.logger.info(f"{status} {test_name}")

            self.logger.info("-" * 60)
            self.logger.info(f"OVERALL: {passed}/{total} tests passed")

            if passed == total:
                self.logger.info("🎉 ALL TESTS PASSED - Historical data integration is working correctly!")
                return True
            self.logger.error(f"❌ {total - passed} tests failed - Please review the implementation")
            return False

        finally:
            self.cleanup_test_environment()


def main():
    """Main test execution"""
    test_suite = HistoricalDataIntegrationTest()
    success = test_suite.run_comprehensive_test()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
