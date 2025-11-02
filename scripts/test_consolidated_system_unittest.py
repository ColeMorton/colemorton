#!/usr/bin/env python3
"""
Consolidated Storage System Unit Tests

Comprehensive unittest-based validation of the consolidated file structure.
Converted from utility script to proper unittest framework.
"""

import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from historical_data_manager import (
    DataType,
    HistoricalDataManager,
    Timeframe,
)


class TestConsolidatedStorageSystem(unittest.TestCase):
    """Unit tests for consolidated storage system functionality"""

    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.hdm = HistoricalDataManager(base_path=self.test_dir)

        # Sample test data - multiple records for time series
        self.test_data = {
            "symbol": "TEST_CONSOLIDATED",
            "data": [
                {
                    "Date": "2025-07-28",
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 98.0,
                    "Close": 103.0,
                    "Volume": 1000000,
                    "Adj Close": 103.0,
                },
                {
                    "Date": "2025-07-27",
                    "Open": 98.0,
                    "High": 102.0,
                    "Low": 96.0,
                    "Close": 100.0,
                    "Volume": 800000,
                    "Adj Close": 100.0,
                },
                {
                    "Date": "2025-07-26",
                    "Open": 95.0,
                    "High": 99.0,
                    "Low": 94.0,
                    "Close": 98.0,
                    "Volume": 900000,
                    "Adj Close": 98.0,
                },
            ],
        }

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_consolidated_data_storage(self):
        """Test consolidated data storage functionality"""
        # Store data
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )

        self.assertTrue(success, "Data storage should succeed")

    def test_consolidated_file_structure(self):
        """Test that consolidated file structure is correct"""
        # Store data first
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Check file structure
        expected_csv = self.test_dir / "stocks" / "TEST_CONSOLIDATED" / "daily.csv"
        expected_meta = self.test_dir / "stocks" / "TEST_CONSOLIDATED" / "daily.meta.json"

        self.assertTrue(expected_csv.exists(), f"CSV file should exist: {expected_csv}")
        self.assertTrue(expected_meta.exists(), f"Metadata file should exist: {expected_meta}")

        # Verify file has content
        csv_size = expected_csv.stat().st_size
        self.assertGreater(csv_size, 0, "CSV file should not be empty")

    def test_data_retrieval(self):
        """Test consolidated data retrieval"""
        # Store data first
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Retrieve data
        retrieved = self.hdm.retrieve_data(
            symbol="TEST_CONSOLIDATED",
            data_type=DataType.STOCK_DAILY_PRICES,
            date_start="2025-07-26",
            date_end="2025-07-28",
            timeframe=Timeframe.DAILY,
        )

        self.assertEqual(len(retrieved), 3, "Should retrieve all 3 records")

        # Verify data integrity
        retrieved_dates = [record["date"] for record in retrieved]
        expected_dates = ["2025-07-26", "2025-07-27", "2025-07-28"]
        self.assertEqual(sorted(retrieved_dates), sorted(expected_dates))

    def test_append_with_deduplication(self):
        """Test appending data with automatic deduplication"""
        # Store initial data
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Prepare additional data with one duplicate and one new record
        additional_data = {
            "symbol": "TEST_CONSOLIDATED",
            "data": [
                {
                    "Date": "2025-07-28",  # Duplicate - should be ignored
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 98.0,
                    "Close": 103.0,
                    "Volume": 1000000,
                    "Adj Close": 103.0,
                },
                {
                    "Date": "2025-07-29",  # New record - should be added
                    "Open": 103.0,
                    "High": 107.0,
                    "Low": 102.0,
                    "Close": 106.0,
                    "Volume": 1200000,
                    "Adj Close": 106.0,
                },
            ],
        }

        # Append additional data
        success_append = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=additional_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test_append",
        )
        self.assertTrue(success_append, "Append operation should succeed")

        # Verify deduplication worked
        final_retrieved = self.hdm.retrieve_data(
            symbol="TEST_CONSOLIDATED",
            data_type=DataType.STOCK_DAILY_PRICES,
            date_start="2025-07-26",
            date_end="2025-07-29",
            timeframe=Timeframe.DAILY,
        )

        self.assertEqual(len(final_retrieved), 4, "Should have 4 unique records (3 + 1 new)")

        # Verify dates are unique
        dates = [record["date"] for record in final_retrieved]
        self.assertEqual(len(set(dates)), 4, "All dates should be unique")

    def test_file_system_efficiency(self):
        """Test that consolidated format improves file system efficiency"""
        # Store data
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Count actual files created
        symbol_dir = self.test_dir / "stocks" / "TEST_CONSOLIDATED"
        all_files = list(symbol_dir.rglob("*"))
        actual_files = [f for f in all_files if f.is_file()]

        # Should have exactly 2 files (CSV + metadata)
        self.assertEqual(len(actual_files), 2, "Should create exactly 2 files in consolidated format")

        # Calculate theoretical improvement
        old_structure_files = 3 * 2  # 3 periods × 2 files each (CSV + meta)
        new_structure_files = 2  # 1 CSV + 1 meta

        reduction_percentage = (old_structure_files - new_structure_files) / old_structure_files * 100
        self.assertGreaterEqual(reduction_percentage, 60, "Should achieve at least 60% file reduction")

    def test_metadata_integrity(self):
        """Test metadata file integrity and content"""
        # Store data
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Read and verify metadata
        meta_path = self.test_dir / "stocks" / "TEST_CONSOLIDATED" / "daily.meta.json"
        self.assertTrue(meta_path.exists())

        with open(meta_path) as f:
            metadata = json.load(f)

        # Verify required fields
        required_fields = [
            "symbol",
            "data_type",
            "timeframe",
            "records",
            "format_version",
        ]
        for field in required_fields:
            self.assertIn(field, metadata, f"Metadata missing required field: {field}")

        # Verify values
        self.assertEqual(metadata["symbol"], "TEST_CONSOLIDATED")
        self.assertEqual(metadata["data_type"], "daily_prices")
        self.assertEqual(metadata["timeframe"], "daily")
        self.assertEqual(metadata["records"], 3)
        self.assertEqual(metadata["format_version"], "consolidated_v1")

    def test_csv_data_integrity(self):
        """Test CSV data format and integrity"""
        # Store data
        success = self.hdm.store_data(
            symbol="TEST_CONSOLIDATED",
            data=self.test_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            timeframe=Timeframe.DAILY,
            source="test",
        )
        self.assertTrue(success)

        # Read and verify CSV data
        csv_path = self.test_dir / "stocks" / "TEST_CONSOLIDATED" / "daily.csv"
        self.assertTrue(csv_path.exists())

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            csv_records = list(reader)

        self.assertEqual(len(csv_records), 3, "CSV should contain 3 records")

        # Verify CSV headers
        expected_headers = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "adjusted_close",
        ]
        first_record = csv_records[0]
        for header in expected_headers:
            self.assertIn(header, first_record, f"CSV missing required column: {header}")

        # Verify data types and values
        for record in csv_records:
            self.assertIsNotNone(record["date"], "Date should not be None")

            # Verify numeric fields can be converted
            try:
                float(record["open"])
                float(record["high"])
                float(record["low"])
                float(record["close"])
                int(record["volume"])
            except ValueError as e:
                self.fail(f"CSV contains invalid numeric data: {e}")

    def test_multiple_timeframes(self):
        """Test consolidated storage across multiple timeframes"""
        timeframes_to_test = [
            (Timeframe.DAILY, "daily.csv"),
            (Timeframe.WEEKLY, "weekly.csv"),
            (Timeframe.MONTHLY, "monthly.csv"),
        ]

        for timeframe, expected_filename in timeframes_to_test:
            with self.subTest(timeframe=timeframe):
                # Store data with specific timeframe
                success = self.hdm.store_data(
                    symbol="TEST_CONSOLIDATED",
                    data=self.test_data,
                    data_type=DataType.STOCK_DAILY_PRICES,
                    timeframe=timeframe,
                    source="test",
                )
                self.assertTrue(success, f"Storage should succeed for {timeframe}")

                # Verify correct file created
                expected_path = self.test_dir / "stocks" / "TEST_CONSOLIDATED" / expected_filename
                self.assertTrue(expected_path.exists(), f"File should exist: {expected_path}")


def run_test_suite():
    """Run the complete test suite with detailed reporting"""
    print("🧪 Consolidated Storage System Unit Test Suite")
    print("=" * 60)

    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(TestConsolidatedStorageSystem)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    test_results = runner.run(test_suite)

    # Generate summary
    print("\n📊 Test Suite Summary:")
    print("   Tests run: {test_results.testsRun}")
    print("   Failures: {len(test_results.failures)}")
    print("   Errors: {len(test_results.errors)}")
    success_rate = (
        (test_results.testsRun - len(test_results.failures) - len(test_results.errors)) / test_results.testsRun * 100
    )
    print("   Success rate: {success_rate:.1f}%")

    if test_results.failures:
        print("\n❌ Failures:")
        for test, traceback in test_results.failures:
            print("   - {test}: {traceback}")

    if test_results.errors:
        print("\n💥 Errors:")
        for test, traceback in test_results.errors:
            print("   - {test}: {traceback}")

    overall_success = len(test_results.failures) == 0 and len(test_results.errors) == 0
    print("\n{'✅ All tests passed!' if overall_success else '❌ Some tests failed!'}")

    return overall_success


if __name__ == "__main__":
    success = run_test_suite()
    exit(0 if success else 1)
