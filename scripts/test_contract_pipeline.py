#!/usr/bin/env python3
"""
End-to-End Contract Pipeline Validation Test Suite

Comprehensive testing framework for the contract-first data pipeline architecture.
Validates the entire flow from contract discovery through data generation and compliance.
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from data_contract_discovery import DataContract, DataContractDiscovery
from data_pipeline_manager import DataPipelineManager
from result_types import ProcessingResult


class ContractDiscoveryTests(unittest.TestCase):
    """Test contract discovery functionality"""

    def setUp(self):
        """Set up test environment with sample CSV files"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.frontend_data_dir = self.test_dir / "frontend/public/data"

        # Create test directory structure
        (self.frontend_data_dir / "portfolio").mkdir(parents=True)
        (self.frontend_data_dir / "trade-history").mkdir(parents=True)
        (self.frontend_data_dir / "open-positions").mkdir(parents=True)

        # Create sample CSV files
        self._create_sample_portfolio_file()
        self._create_sample_trade_history_file()
        self._create_sample_open_positions_file()

        self.discovery = DataContractDiscovery(self.frontend_data_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.test_dir)

    def _create_sample_portfolio_file(self):
        """Create sample portfolio CSV file"""
        portfolio_file = self.frontend_data_dir / "portfolio/portfolio_value.csv"
        portfolio_data = pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "Portfolio_Value": [1000.0, 1010.0, 1020.0],
                "Normalized_Value": [1.0, 1.01, 1.02],
            }
        )
        portfolio_data.to_csv(portfolio_file, index=False)

    def _create_sample_trade_history_file(self):
        """Create sample trade history CSV file"""
        trade_file = self.frontend_data_dir / "trade-history/trades.csv"
        trade_data = pd.DataFrame(
            {
                "Position_UUID": ["AAPL_SMA_2025-01-01", "GOOGL_EMA_2025-01-02"],
                "Ticker": ["AAPL", "GOOGL"],
                "Strategy_Type": ["SMA", "EMA"],
                "PnL": [100.50, -25.75],
                "Status": ["Closed", "Closed"],
            }
        )
        trade_data.to_csv(trade_file, index=False)

    def _create_sample_open_positions_file(self):
        """Create sample open positions CSV file"""
        positions_file = self.frontend_data_dir / "open-positions/positions.csv"
        positions_data = pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02"],
                "Ticker": ["NVDA", "NVDA"],
                "PnL": [50.25, 75.50],
                "Position_UUID": ["NVDA_SMA_2025-01-01", "NVDA_SMA_2025-01-01"],
            }
        )
        positions_data.to_csv(positions_file, index=False)

    def test_contract_discovery_finds_all_files(self):
        """Test that contract discovery finds all CSV files"""
        result = self.discovery.discover_all_contracts()

        self.assertEqual(result.total_files, 3)
        self.assertEqual(result.successful_discoveries, 3)
        self.assertEqual(len(result.failed_discoveries), 0)

        # Check categories
        expected_categories = {"portfolio", "trade-history", "open-positions"}
        self.assertEqual(result.categories, expected_categories)

    def test_contract_schema_inference(self):
        """Test that schema inference works correctly"""
        result = self.discovery.discover_all_contracts()

        # Find portfolio contract
        portfolio_contract = None
        for contract in result.contracts:
            if contract.category == "portfolio":
                portfolio_contract = contract
                break

        self.assertIsNotNone(portfolio_contract)
        self.assertEqual(len(portfolio_contract.schema), 3)

        # Check schema details
        column_names = [col.name for col in portfolio_contract.schema]
        self.assertIn("Date", column_names)
        self.assertIn("Portfolio_Value", column_names)
        self.assertIn("Normalized_Value", column_names)

    def test_contract_id_generation(self):
        """Test that contract IDs are generated correctly"""
        result = self.discovery.discover_all_contracts()

        contract_ids = [contract.contract_id for contract in result.contracts]
        self.assertIn("portfolio_portfolio_value", contract_ids)
        self.assertIn("trade-history_trades", contract_ids)
        self.assertIn("open-positions_positions", contract_ids)

    def test_data_type_inference(self):
        """Test that data types are inferred correctly"""
        result = self.discovery.discover_all_contracts()

        # Find trade history contract
        trade_contract = None
        for contract in result.contracts:
            if "trades" in contract.contract_id:
                trade_contract = contract
                break

        self.assertIsNotNone(trade_contract)

        # Check data types
        schema_by_name = {col.name: col for col in trade_contract.schema}
        self.assertEqual(schema_by_name["PnL"].data_type, "numeric")
        self.assertEqual(schema_by_name["Ticker"].data_type, "string")

    def test_contract_export_to_json(self):
        """Test that contracts can be exported to JSON"""
        result = self.discovery.discover_all_contracts()
        output_file = self.test_dir / "contracts.json"

        self.discovery.export_contracts_to_json(result.contracts, output_file)

        self.assertTrue(output_file.exists())

        # Validate JSON structure
        with open(output_file) as f:
            data = json.load(f)

        self.assertIn("discovery_timestamp", data)
        self.assertIn("total_contracts", data)
        self.assertIn("contracts", data)
        self.assertEqual(data["total_contracts"], 3)


class DataPipelineManagerTests(unittest.TestCase):
    """Test contract-driven data pipeline manager"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.frontend_data_dir = self.test_dir / "frontend/public/data"

        # Create minimal directory structure
        (self.frontend_data_dir / "portfolio").mkdir(parents=True)

        # Create a sample contract file
        portfolio_file = self.frontend_data_dir / "portfolio/test_portfolio.csv"
        portfolio_data = pd.DataFrame({"Date": ["2025-01-01", "2025-01-02"], "Portfolio_Value": [1000.0, 1010.0]})
        portfolio_data.to_csv(portfolio_file, index=False)

        self.pipeline = DataPipelineManager(self.frontend_data_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_contract_discovery_integration(self):
        """Test that pipeline integrates with contract discovery"""
        result = self.pipeline.discover_contracts()

        self.assertIsNotNone(result)
        self.assertGreater(len(result.contracts), 0)
        self.assertIn("portfolio", result.categories)

    def test_service_capability_mapping(self):
        """Test CLI service capability mapping"""
        capabilities = self.pipeline.cli_service_capabilities

        self.assertIn("yahoo_finance", capabilities)
        self.assertIn("trade_history_cli", capabilities)
        self.assertIn("live_signals_dashboard", capabilities)

        # Check capability structure
        yahoo_caps = capabilities["yahoo_finance"]
        self.assertIn("categories", yahoo_caps)
        self.assertIn("provides", yahoo_caps)
        self.assertIn("portfolio", yahoo_caps["categories"])

    def test_contract_to_service_mapping(self):
        """Test that contracts are mapped to correct services"""
        result = self.pipeline.discover_contracts()

        # Find a portfolio contract
        portfolio_contract = None
        for contract in result.contracts:
            if contract.category == "portfolio":
                portfolio_contract = contract
                break

        self.assertIsNotNone(portfolio_contract)

        capable_services = self.pipeline.map_contract_to_services(portfolio_contract)
        self.assertIn("yahoo_finance", capable_services)

    def test_contract_validation(self):
        """Test contract validation functionality"""
        result = self.pipeline.discover_contracts()
        contract = result.contracts[0]

        validation_result = self.pipeline.validate_contract_fulfillment(contract)

        # Should succeed since file exists and has recent data
        self.assertTrue(validation_result.success)
        self.assertIn("capable_services", validation_result.metadata)

    def test_stale_data_detection(self):
        """Test that stale data is detected"""
        result = self.pipeline.discover_contracts()
        contract = result.contracts[0]

        # Make the contract appear stale by setting old timestamp
        old_time = datetime.now() - timedelta(days=2)
        contract.last_modified = old_time
        contract.freshness_threshold_hours = 1

        validation_result = self.pipeline.validate_contract_fulfillment(contract)

        # Should fail due to staleness
        self.assertFalse(validation_result.success)
        self.assertIn("stale", validation_result.error.lower())


class DataGenerationTests(unittest.TestCase):
    """Test contract-driven data generation"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.frontend_data_dir = self.test_dir / "frontend/public/data"

        # Create directory structure
        (self.frontend_data_dir / "portfolio").mkdir(parents=True)

        self.pipeline = DataPipelineManager(self.frontend_data_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_portfolio_data_generation(self):
        """Test portfolio data generation matches schema"""
        # Create a mock contract
        from data_contract_discovery import ColumnSchema

        schema = [
            ColumnSchema(name="Date", data_type="datetime"),
            ColumnSchema(name="Portfolio_Value", data_type="numeric"),
            ColumnSchema(name="Normalized_Value", data_type="numeric"),
        ]

        mock_contract = DataContract(
            contract_id="test_portfolio",
            category="portfolio",
            file_path=self.frontend_data_dir / "portfolio/test.csv",
            relative_path="portfolio/test.csv",
            schema=schema,
            minimum_rows=10,
        )

        result = self.pipeline._generate_portfolio_contract_data(mock_contract)

        self.assertTrue(result.success)
        self.assertTrue(mock_contract.file_path.exists())

        # Validate generated data
        df = pd.read_csv(mock_contract.file_path)
        self.assertGreaterEqual(len(df), 10)
        self.assertIn("Date", df.columns)
        self.assertIn("Portfolio_Value", df.columns)

    def test_generic_data_generation(self):
        """Test generic data generation based on schema"""
        from data_contract_discovery import ColumnSchema

        schema = [
            ColumnSchema(name="test_date", data_type="datetime"),
            ColumnSchema(name="test_numeric", data_type="numeric"),
            ColumnSchema(name="test_string", data_type="string", sample_values=["A", "B", "C"]),
        ]

        mock_contract = DataContract(
            contract_id="test_generic",
            category="test",
            file_path=self.frontend_data_dir / "test.csv",
            relative_path="test.csv",
            schema=schema,
            minimum_rows=50,
        )

        result = self.pipeline._generate_generic_contract_data(mock_contract)

        self.assertTrue(result.success)
        self.assertTrue(mock_contract.file_path.exists())

        # Validate generated data
        df = pd.read_csv(mock_contract.file_path)
        self.assertEqual(len(df), 50)
        self.assertEqual(len(df.columns), 3)

        # Check data types
        self.assertTrue(all(val in ["A", "B", "C"] for val in df["test_string"]))

    def test_schema_compliance(self):
        """Test that generated data complies with contract schema"""
        from data_contract_discovery import ColumnSchema

        schema = [
            ColumnSchema(name="required_col", data_type="string"),
            ColumnSchema(name="optional_col", data_type="numeric"),
        ]

        mock_contract = DataContract(
            contract_id="test_compliance",
            category="test",
            file_path=self.frontend_data_dir / "compliance.csv",
            relative_path="compliance.csv",
            schema=schema,
            minimum_rows=20,
            required_columns={"required_col"},
        )

        # Generate data
        result = self.pipeline._generate_generic_contract_data(mock_contract)
        self.assertTrue(result.success)

        # Validate compliance
        validation_result = self.pipeline._validate_contract_data(mock_contract)
        self.assertTrue(validation_result.success)


class EndToEndIntegrationTests(unittest.TestCase):
    """End-to-end integration tests for the entire pipeline"""

    def setUp(self):
        """Set up test environment with realistic data"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.frontend_data_dir = self.test_dir / "frontend/public/data"

        # Create realistic frontend data structure
        self._create_realistic_test_data()

        self.pipeline = DataPipelineManager(self.frontend_data_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.test_dir)

    def _create_realistic_test_data(self):
        """Create realistic test data structure"""
        # Portfolio data
        portfolio_dir = self.frontend_data_dir / "portfolio"
        portfolio_dir.mkdir(parents=True)

        portfolio_value_data = pd.DataFrame(
            {
                "Date": pd.date_range("2024-01-01", periods=100, freq="D").strftime("%Y-%m-%d"),
                "Portfolio_Value": np.random.normal(1000, 100, 100),
                "Normalized_Value": np.random.normal(1.0, 0.1, 100),
            }
        )
        portfolio_value_data.to_csv(portfolio_dir / "portfolio_value.csv", index=False)

        # Trade history data
        trade_dir = self.frontend_data_dir / "trade-history"
        trade_dir.mkdir(parents=True)

        trade_data = pd.DataFrame(
            {
                "Position_UUID": [f"TRADE_{i}" for i in range(20)],
                "Ticker": np.random.choice(["AAPL", "GOOGL", "MSFT", "AMZN"], 20),
                "Strategy_Type": np.random.choice(["SMA", "EMA"], 20),
                "PnL": np.random.normal(50, 200, 20),
                "Status": ["Closed"] * 20,
            }
        )
        trade_data.to_csv(trade_dir / "trades.csv", index=False)

        # Open positions data
        positions_dir = self.frontend_data_dir / "open-positions"
        positions_dir.mkdir(parents=True)

        positions_data = pd.DataFrame(
            {
                "Date": pd.date_range("2024-12-01", periods=30, freq="D").strftime("%Y-%m-%d"),
                "Ticker": np.random.choice(["NVDA", "AMD"], 30),
                "PnL": np.random.normal(25, 50, 30),
                "Position_UUID": [f"POS_{i}" for i in range(30)],
            }
        )
        positions_data.to_csv(positions_dir / "positions.csv", index=False)

    def test_full_pipeline_execution(self):
        """Test complete pipeline execution"""
        # Mock CLI service failures to test fallback behavior
        with (
            patch.object(self.pipeline, "_fetch_live_signals_data") as mock_live_signals,
            patch.object(self.pipeline, "_fetch_yahoo_finance_data") as mock_yahoo,
            patch.object(self.pipeline, "_fetch_trade_history_data") as mock_trade,
        ):
            # Make CLI services fail to test data generation fallback
            mock_live_signals.return_value = ProcessingResult(success=False, operation="test", error="Mock failure")
            mock_yahoo.return_value = ProcessingResult(success=False, operation="test", error="Mock failure")
            mock_trade.return_value = ProcessingResult(success=False, operation="test", error="Mock failure")

            result = self.pipeline.refresh_all_chart_data(skip_errors=True)

            # Should succeed with data generation fallback
            self.assertTrue(result.success)
            self.assertGreater(result.metadata.get("successful_contracts", 0), 0)
            self.assertIn("discovery_stats", result.metadata)

    def test_contract_freshness_validation(self):
        """Test end-to-end freshness validation"""
        # First discover contracts
        discovery_result = self.pipeline.discover_contracts()
        self.assertGreater(len(discovery_result.contracts), 0)

        # Test freshness validation for each contract
        for contract in discovery_result.contracts:
            validation_result = self.pipeline.validate_contract_fulfillment(contract)

            # Should succeed since we just created the data
            self.assertTrue(validation_result.success)
            self.assertIn("file_age_hours", validation_result.metadata)
            self.assertLess(validation_result.metadata["file_age_hours"], 1.0)

    def test_schema_discovery_and_validation(self):
        """Test that schemas are discovered and validated correctly"""
        discovery_result = self.pipeline.discover_contracts()

        # Validate each discovered contract
        for contract in discovery_result.contracts:
            # Check that schema was inferred
            self.assertGreater(len(contract.schema), 0)

            # Check that data meets schema requirements
            validation_result = self.pipeline._validate_contract_data(contract)
            self.assertTrue(validation_result.success)

    def test_contract_regeneration(self):
        """Test that contracts can be regenerated when needed"""
        discovery_result = self.pipeline.discover_contracts()

        # Delete a contract file to trigger regeneration
        contract = discovery_result.contracts[0]
        original_path = contract.file_path

        if original_path.exists():
            original_path.unlink()

        # Regenerate the contract
        result = self.pipeline._fulfill_contract(contract)

        self.assertTrue(result.success)
        self.assertTrue(original_path.exists())

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        # Test with skip_errors=False (should fail fast)
        with patch.object(self.pipeline, "_generate_portfolio_contract_data") as mock_gen:
            mock_gen.return_value = ProcessingResult(success=False, operation="test", error="Mock error")

            result = self.pipeline.refresh_all_chart_data(skip_errors=False)

            # Should fail due to error
            self.assertFalse(result.success)

        # Test with skip_errors=True (should continue)
        with patch.object(self.pipeline, "_generate_portfolio_contract_data") as mock_gen:
            mock_gen.return_value = ProcessingResult(success=False, operation="test", error="Mock error")

            result = self.pipeline.refresh_all_chart_data(skip_errors=True)

            # Should continue and report partial success
            self.assertIsNotNone(result)
            self.assertIn("contract_results", result.metadata)


def run_all_tests():
    """Run all contract pipeline tests"""
    print("🧪 Running Contract Pipeline Test Suite")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        ContractDiscoveryTests,
        DataPipelineManagerTests,
        DataGenerationTests,
        EndToEndIntegrationTests,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("   Tests run: {result.testsRun}")
    print("   Failures: {len(result.failures)}")
    print("   Errors: {len(result.errors)}")
    print(
        f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ Failures:")
        for test, error in result.failures:
            print(f"   - {test}: {error.split('AssertionError: ')[-1].split(chr(10))[0]}")

    if result.errors:
        print("\n💥 Errors:")
        for test, error in result.errors:
            print("   - {test}: {error.split(chr(10))[-2]}")

    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\n✅ All tests passed! Contract pipeline is working correctly.")
        return True
    print("\n⚠️ Some tests failed. Please review the issues above.")
    return False


if __name__ == "__main__":
    # Run the test suite
    success = run_all_tests()

    if success:
        print("\n🎉 Contract-First Data Pipeline Test Suite: PASSED")
        exit(0)
    else:
        print("\n💥 Contract-First Data Pipeline Test Suite: FAILED")
        exit(1)
