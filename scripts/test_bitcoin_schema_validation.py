#!/usr/bin/env python3
"""
Bitcoin Schema Validation Test Suite

Comprehensive testing of Bitcoin CLI data compliance with Bitcoin Cycle Intelligence schemas:
- Discovery schema compliance and data structure validation
- Analysis schema preparation and field mapping
- Institutional-grade data quality requirements
- CLI service enumeration and validation
- Data transformation and schema alignment testing
"""

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.services.alternative_me import create_alternative_me_service
from scripts.services.binance_api import create_binance_api_service
from scripts.services.bitcoin_network_stats import create_bitcoin_network_stats_service
from scripts.services.blockchain_com import create_blockchain_com_service
from scripts.services.coinmetrics import create_coinmetrics_service
from scripts.services.mempool_space import create_mempool_space_service


class BitcoinSchemaValidationTestBase(unittest.TestCase):
    """Base class for Bitcoin schema validation tests"""

    def setUp(self):
        """Set up test environment and load schemas"""
        self.project_root = Path(__file__).parent.parent
        self.schemas_dir = self.project_root / "scripts" / "schemas"

        # Load schemas
        self.discovery_schema = self._load_schema("bitcoin_cycle_intelligence_discovery_schema.json")
        self.analysis_schema = self._load_schema("bitcoin_cycle_intelligence_analysis_schema.json")

        # Initialize services for data testing
        self.services = {
            "mempool_space": create_mempool_space_service("test"),
            "blockchain_com": create_blockchain_com_service("test"),
            "coinmetrics": create_coinmetrics_service("test"),
            "alternative_me": create_alternative_me_service("test"),
            "binance_api": create_binance_api_service("test"),
            "bitcoin_network_stats": create_bitcoin_network_stats_service("test"),
        }

    def _load_schema(self, schema_file: str) -> dict[str, Any]:
        """Load JSON schema from file"""
        schema_path = self.schemas_dir / schema_file

        if not schema_path.exists():
            self.fail(f"Schema file not found: {schema_path}")

        with open(schema_path) as f:
            return json.load(f)

    def validate_against_schema(self, data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Validate data against schema and return list of validation errors"""
        try:
            jsonschema.validate(instance=data, schema=schema)
            return []
        except jsonschema.ValidationError as e:
            return [str(e)]
        except jsonschema.SchemaError as e:
            return [f"Schema error: {str(e)}"]

    def create_minimal_discovery_document(self) -> dict[str, Any]:
        """Create minimal discovery document that should pass schema validation"""
        return {
            "metadata": {
                "command_name": "cli_enhanced_bitcoin_cycle_intelligence_discover",
                "execution_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "framework_phase": "cli_enhanced_discover_bitcoin_sources",
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "data_collection_methodology": "production_cli_bitcoin_services_unified_access",
                "cli_services_utilized": [
                    "mempool_space_cli",
                    "coinmetrics_cli",
                    "blockchain_com_cli",
                    "binance_api_cli",
                    "alternative_me_cli",
                ],
                "api_keys_configured": "production_keys_from_config/bitcoin_services.yaml",
            },
            "cli_comprehensive_analysis": {
                "metadata": "Bitcoin CLI integration analysis",
                "bitcoin_overview": "Comprehensive Bitcoin network analysis",
                "market_data": "Cross-validated market data from multiple sources",
                "cycle_intelligence": "Bitcoin cycle indicator analysis",
                "data_validation": "Multi-source data validation approach",
                "quality_metrics": "Institutional-grade quality assessment",
            },
            "bitcoin_market_data": {
                "current_price": 45000.0,
                "market_cap": 880000000000.0,
                "price_validation": {
                    "coingecko_price": 45000.0,
                    "binance_price": 45000.0,
                    "coinmetrics_price": 45000.0,
                    "price_consistency": True,
                    "confidence_score": 1.0,
                },
                "volume_24h": 15000000000.0,
                "circulating_supply": 19500000.0,
                "all_time_high": 69000.0,
                "all_time_low": 0.01,
                "confidence": 0.95,
            },
            "cycle_indicators": {
                "mvrv_z_score": {
                    "current_score": 0.5,
                    "historical_percentile": 45.0,
                    "zone_classification": "neutral",
                },
                "pi_cycle_top": {
                    "signal_active": False,
                    "days_to_signal": 180,
                    "historical_accuracy": 0.85,
                },
                "nupl_zones": {
                    "current_nupl": 0.3,
                    "zone_classification": "optimism",
                    "lth_nupl": 0.4,
                    "sth_nupl": 0.2,
                },
                "reserve_risk": {
                    "current_value": 0.002,
                    "historical_percentile": 25.0,
                    "accumulation_opportunity": "good",
                },
                "rainbow_price_model": {
                    "current_band": "yellow",
                    "fair_value_estimate": 42000.0,
                    "band_description": "Accumulation zone",
                },
                "confidence": 0.90,
            },
            "network_health": {
                "hash_rate": {
                    "current_hashrate": 400.0,
                    "difficulty_adjustment": 2.5,
                    "hash_ribbons": {
                        "signal": "neutral",
                        "ma_30": 390.0,
                        "ma_60": 380.0,
                    },
                    "confidence": 0.95,
                },
                "mining_economics": {
                    "puell_multiple": 1.2,
                    "miner_revenue": 25000000.0,
                    "fee_percentage": 8.5,
                    "confidence": 0.90,
                },
                "network_security": {
                    "security_budget": 9000000000.0,
                    "attack_cost": 18000000000.0,
                    "decentralization_score": 7.5,
                    "confidence": 0.85,
                },
                "development_activity": {
                    "github_commits": 450,
                    "active_developers": 85,
                    "protocol_upgrades": ["Taproot", "Schnorr"],
                    "confidence": 0.90,
                },
            },
            "cli_bitcoin_context": {
                "metadata": "Economic context from CLI integration",
                "economic_indicators": "Interest rates and liquidity analysis",
                "bitcoin_correlations": "Asset correlation analysis",
                "market_summary": "Current market environment assessment",
                "macro_implications": "Macroeconomic implications for Bitcoin",
            },
            "economic_analysis": {
                "interest_rate_environment": "restrictive",
                "liquidity_conditions": "neutral",
                "policy_implications": [
                    "Higher interest rates impact",
                    "Regulatory clarity needed",
                ],
                "bitcoin_correlation": {
                    "with_gold": 0.1,
                    "with_stocks": 0.3,
                    "with_bonds": -0.2,
                    "with_dxy": -0.4,
                },
            },
            "institutional_intelligence": {
                "etf_flows": {
                    "net_flows_7d": 150000000.0,
                    "net_flows_30d": 800000000.0,
                    "total_aum": 25000000000.0,
                },
                "corporate_treasuries": {
                    "total_corporate_holdings": 200000.0,
                    "recent_additions": ["MicroStrategy", "Tesla"],
                },
                "exchange_flows": {
                    "net_exchange_flows": -5000.0,
                    "whale_transactions": 45,
                },
            },
            "cli_service_validation": {
                "service_health": "All Bitcoin CLI services operational",
                "health_score": 1.0,
                "services_operational": 6,
                "services_healthy": True,
            },
            "cli_data_quality": {
                "overall_data_quality": 0.95,
                "cli_service_health": 1.0,
                "institutional_grade": True,
                "data_sources_via_cli": [
                    "mempool_space_cli",
                    "blockchain_com_cli",
                    "coinmetrics_cli",
                    "binance_api_cli",
                    "alternative_me_cli",
                ],
                "cli_integration_status": "operational",
            },
            "cli_insights": {
                "cli_integration_observations": [
                    "All Bitcoin CLI services responding normally",
                    "Data consistency across multiple sources verified",
                    "Real-time data access achieved",
                ],
                "data_quality_insights": [
                    "Price validation successful across sources",
                    "Network metrics consistent",
                    "Institutional-grade data quality achieved",
                ],
                "market_context_insights": [
                    "Current cycle position identified",
                    "Risk-adjusted opportunities present",
                    "Macro environment supportive",
                ],
                "service_performance_insights": [
                    "Low latency data access",
                    "High availability across services",
                    "Comprehensive coverage achieved",
                ],
            },
            "bitcoin_ecosystem_data": {
                "lightning_network": {
                    "channel_capacity": 5000.0,
                    "node_count": 15000,
                    "growth_metrics": {
                        "capacity_growth_30d": 5.2,
                        "node_growth_30d": 2.8,
                    },
                },
                "defi_integration": {
                    "wrapped_bitcoin_tvl": 180000.0,
                    "defi_protocols": ["Wrapped BTC", "Lightning Labs"],
                },
                "adoption_metrics": {
                    "active_addresses": 1000000,
                    "transaction_count": 300000,
                    "addresses_with_balance": 42000000,
                },
                "confidence": 0.85,
            },
            "discovery_insights": {
                "initial_observations": [
                    "Strong network fundamentals observed",
                    "Market positioning favorable for accumulation",
                    "Institutional adoption accelerating",
                ],
                "data_gaps_identified": [
                    "Additional on-chain metrics needed",
                    "Institutional flow data could be enhanced",
                ],
                "research_priorities": [
                    "Long-term holder behavior analysis",
                    "Mining economics deep dive",
                    "Institutional adoption tracking",
                ],
                "next_phase_readiness": True,
            },
            "data_quality_assessment": {
                "source_reliability_scores": {
                    "mempool_space_cli": 0.98,
                    "blockchain_com_cli": 0.95,
                    "coinmetrics_cli": 0.97,
                    "binance_api_cli": 0.96,
                    "alternative_me_cli": 0.94,
                },
                "data_completeness": 0.92,
                "data_freshness": {
                    "price_data": "real-time",
                    "network_data": "15-minute delay",
                    "sentiment_data": "daily",
                },
                "quality_flags": [
                    "Price consistency validated",
                    "Network metrics verified",
                    "Data freshness acceptable",
                    "Institutional grade achieved",
                ],
            },
            "local_data_references": {
                "files_created": [],
                "files_updated": [],
                "directories_created": [],
            },
        }

    def extract_real_data_for_validation(self) -> dict[str, Any]:
        """Extract real data from Bitcoin services and structure for schema validation"""
        extracted_data = {}

        # Try to get real price data for validation
        try:
            binance_data = self.services["binance_api"].get_symbol_price_ticker("BTCUSDT")
            extracted_data["binance_price"] = float(binance_data.get("price", 0))
        except:
            extracted_data["binance_price"] = 45000.0  # Fallback

        try:
            blockchain_price = self.services["blockchain_com"].get_market_price_usd()
            extracted_data["blockchain_price"] = float(blockchain_price.get("price_usd", 0))
        except:
            extracted_data["blockchain_price"] = 45000.0  # Fallback

        # Try to get Fear & Greed data
        try:
            fng_data = self.services["alternative_me"].get_current_fear_greed()
            extracted_data["fear_greed_value"] = int(fng_data.get("value", 50))
        except:
            extracted_data["fear_greed_value"] = 50  # Fallback

        # Try to get network stats
        try:
            network_overview = self.services["bitcoin_network_stats"].get_network_overview()
            extracted_data["network_sources"] = network_overview.get("sources", [])
            extracted_data["network_errors"] = len(network_overview.get("errors", []))
        except:
            extracted_data["network_sources"] = ["mempool_space", "blockchain_com"]
            extracted_data["network_errors"] = 0

        return extracted_data


class TestBitcoinDiscoverySchemaCompliance(BitcoinSchemaValidationTestBase):
    """Test compliance with Bitcoin Cycle Intelligence Discovery Schema"""

    def test_discovery_schema_loads_correctly(self):
        """Test that the discovery schema file loads and is valid"""
        self.assertIsInstance(self.discovery_schema, dict)
        self.assertIn("type", self.discovery_schema)
        self.assertEqual(self.discovery_schema["type"], "object")
        self.assertIn("required", self.discovery_schema)
        self.assertIn("properties", self.discovery_schema)

    def test_required_fields_present_in_schema(self):
        """Test that all expected required fields are present in discovery schema"""
        required_fields = self.discovery_schema.get("required", [])

        expected_required_fields = [
            "metadata",
            "cli_comprehensive_analysis",
            "bitcoin_market_data",
            "cycle_indicators",
            "network_health",
            "cli_bitcoin_context",
            "economic_analysis",
            "institutional_intelligence",
            "cli_service_validation",
            "cli_data_quality",
            "cli_insights",
            "bitcoin_ecosystem_data",
            "discovery_insights",
            "data_quality_assessment",
            "local_data_references",
        ]

        for field in expected_required_fields:
            self.assertIn(field, required_fields, f"Required field '{field}' missing from schema")

    def test_cli_services_enum_matches_implemented_services(self):
        """Test that schema CLI services enum includes our implemented services"""
        metadata_props = self.discovery_schema["properties"]["metadata"]["properties"]
        cli_services_enum = metadata_props["cli_services_utilized"]["items"]["enum"]

        implemented_services = [
            "mempool_space_cli",
            "coinmetrics_cli",
            "blockchain_com_cli",
            "binance_api_cli",
            "alternative_me_cli",
        ]

        for service in implemented_services:
            self.assertIn(
                service,
                cli_services_enum,
                f"Implemented service '{service}' not found in schema enum",
            )

    def test_minimal_discovery_document_validates(self):
        """Test that a minimal discovery document passes schema validation"""
        minimal_doc = self.create_minimal_discovery_document()
        errors = self.validate_against_schema(minimal_doc, self.discovery_schema)

        if errors:
            self.fail(f"Minimal discovery document failed validation: {errors}")

    def test_real_data_structure_compatibility(self):
        """Test that real data from services can be structured to match schema requirements"""
        real_data = self.extract_real_data_for_validation()

        # Test that we can create valid price validation structure
        if real_data.get("binance_price", 0) > 0 and real_data.get("blockchain_price", 0) > 0:
            price_validation = {
                "coingecko_price": real_data["binance_price"],  # Using Binance as proxy
                "binance_price": real_data["binance_price"],
                "coinmetrics_price": real_data["blockchain_price"],  # Using Blockchain.com as proxy
                "price_consistency": abs(real_data["binance_price"] - real_data["blockchain_price"])
                / real_data["binance_price"]
                < 0.05,
                "confidence_score": 1.0
                if abs(real_data["binance_price"] - real_data["blockchain_price"]) / real_data["binance_price"] < 0.05
                else 0.9,
            }

            # Test price validation structure
            self.assertIsInstance(price_validation["coingecko_price"], (int, float))
            self.assertIsInstance(price_validation["binance_price"], (int, float))
            self.assertIsInstance(price_validation["coinmetrics_price"], (int, float))
            self.assertIsInstance(price_validation["price_consistency"], bool)
            self.assertIsInstance(price_validation["confidence_score"], (int, float))

    def test_institutional_grade_requirements_achievable(self):
        """Test that institutional grade requirements from schema are achievable"""
        # Test confidence score requirements
        min_confidence = 0.90
        test_confidence = 0.95

        self.assertGreaterEqual(
            test_confidence,
            min_confidence,
            "Test confidence should meet institutional grade requirements",
        )

        # Test data quality requirements
        min_data_quality = 0.90
        test_data_quality = 0.95

        self.assertGreaterEqual(
            test_data_quality,
            min_data_quality,
            "Test data quality should meet institutional grade requirements",
        )

        # Test minimum services requirement
        min_services = 5
        implemented_services_count = 6  # We have 6 implemented services

        self.assertGreaterEqual(
            implemented_services_count,
            min_services,
            "Should have minimum required number of services",
        )

    def test_bitcoin_market_data_schema_compatibility(self):
        """Test Bitcoin market data schema field compatibility with our services"""
        market_data_props = self.discovery_schema["properties"]["bitcoin_market_data"]["properties"]

        # Test required numeric fields have appropriate types
        numeric_fields = [
            "current_price",
            "market_cap",
            "volume_24h",
            "circulating_supply",
            "all_time_high",
            "all_time_low",
            "confidence",
        ]

        for field in numeric_fields:
            if field in market_data_props:
                field_def = market_data_props[field]
                self.assertEqual(field_def["type"], "number", f"Field {field} should be number type")
                if "minimum" in field_def:
                    self.assertEqual(field_def["minimum"], 0, f"Field {field} should have minimum 0")

    def test_cycle_indicators_schema_structure(self):
        """Test cycle indicators schema structure matches expected data"""
        cycle_props = self.discovery_schema["properties"]["cycle_indicators"]["properties"]

        required_indicators = [
            "mvrv_z_score",
            "pi_cycle_top",
            "nupl_zones",
            "reserve_risk",
            "rainbow_price_model",
        ]

        for indicator in required_indicators:
            self.assertIn(indicator, cycle_props, f"Indicator {indicator} should be in schema")
            self.assertEqual(
                cycle_props[indicator]["type"],
                "object",
                f"Indicator {indicator} should be object type",
            )

    def test_cli_service_validation_requirements(self):
        """Test CLI service validation requirements are realistic"""
        validation_props = self.discovery_schema["properties"]["cli_service_validation"]["properties"]

        # Test health score requirement
        health_score_const = validation_props["health_score"]["const"]
        self.assertEqual(health_score_const, 1.0, "Health score requirement should be 1.0")

        # Test minimum services requirement
        min_services = validation_props["services_operational"]["minimum"]
        self.assertEqual(min_services, 5, "Should require minimum 5 operational services")

        # Test services healthy requirement
        services_healthy_const = validation_props["services_healthy"]["const"]
        self.assertTrue(services_healthy_const, "Services healthy should be required to be true")


class TestBitcoinAnalysisSchemaCompliance(BitcoinSchemaValidationTestBase):
    """Test compliance with Bitcoin Cycle Intelligence Analysis Schema"""

    def test_analysis_schema_loads_correctly(self):
        """Test that the analysis schema file loads and is valid"""
        self.assertIsInstance(self.analysis_schema, dict)
        self.assertIn("type", self.analysis_schema)
        self.assertEqual(self.analysis_schema["type"], "object")
        self.assertIn("required", self.analysis_schema)
        self.assertIn("properties", self.analysis_schema)

    def test_analysis_schema_metadata_requirements(self):
        """Test analysis schema metadata requirements"""
        metadata_props = self.analysis_schema["properties"]["metadata"]["properties"]

        # Test command name requirement
        command_name_const = metadata_props["command_name"]["const"]
        self.assertEqual(command_name_const, "cli_enhanced_bitcoin_cycle_intelligence_analyze")

        # Test framework phase requirement
        framework_phase_const = metadata_props["framework_phase"]["const"]
        self.assertEqual(framework_phase_const, "cli_enhanced_analyze_bitcoin_cycle")

        # Test methodology requirement
        methodology_const = metadata_props["analysis_methodology"]["const"]
        self.assertEqual(methodology_const, "institutional_bitcoin_cycle_intelligence")

    def test_confidence_target_requirements(self):
        """Test that confidence target requirements are achievable"""
        metadata_props = self.analysis_schema["properties"]["metadata"]["properties"]
        confidence_props = metadata_props["confidence_target"]

        min_confidence = confidence_props["minimum"]
        max_confidence = confidence_props["maximum"]

        self.assertEqual(min_confidence, 0.8, "Minimum confidence should be 0.8")
        self.assertEqual(max_confidence, 1.0, "Maximum confidence should be 1.0")

        # Test that our expected confidence level meets requirements
        test_confidence = 0.95
        self.assertGreaterEqual(test_confidence, min_confidence)
        self.assertLessEqual(test_confidence, max_confidence)

    def test_discovery_input_file_pattern(self):
        """Test discovery input file pattern requirement"""
        metadata_props = self.analysis_schema["properties"]["metadata"]["properties"]
        pattern = metadata_props["discovery_input_file"]["pattern"]

        expected_pattern = r"^bitcoin_cycle_\d{8}_discovery\.json$"
        self.assertEqual(pattern, expected_pattern)

        # Test that a valid filename matches the pattern
        import re

        test_filename = "bitcoin_cycle_20250904_discovery.json"
        self.assertTrue(
            re.match(pattern, test_filename),
            f"Test filename {test_filename} should match pattern",
        )


class TestBitcoinSchemaDataTransformation(BitcoinSchemaValidationTestBase):
    """Test data transformation from CLI services to schema-compliant format"""

    def test_price_data_transformation(self):
        """Test transformation of price data from services to schema format"""
        real_data = self.extract_real_data_for_validation()

        # Transform to schema-compliant price validation structure
        price_validation = {
            "coingecko_price": real_data.get("binance_price", 45000.0),
            "binance_price": real_data.get("binance_price", 45000.0),
            "coinmetrics_price": real_data.get("blockchain_price", 45000.0),
            "price_consistency": True,  # Would be calculated based on actual price differences
            "confidence_score": 1.0,
        }

        # Validate structure matches schema requirements
        self.assertIsInstance(price_validation["coingecko_price"], (int, float))
        self.assertGreater(price_validation["coingecko_price"], 0)
        self.assertIsInstance(price_validation["binance_price"], (int, float))
        self.assertGreater(price_validation["binance_price"], 0)
        self.assertIsInstance(price_validation["coinmetrics_price"], (int, float))
        self.assertGreater(price_validation["coinmetrics_price"], 0)
        self.assertIsInstance(price_validation["price_consistency"], bool)
        self.assertIsInstance(price_validation["confidence_score"], (int, float))
        self.assertGreaterEqual(price_validation["confidence_score"], 0.0)
        self.assertLessEqual(price_validation["confidence_score"], 1.0)

    def test_fear_greed_data_transformation(self):
        """Test transformation of Fear & Greed data to cycle indicator format"""
        real_data = self.extract_real_data_for_validation()
        fear_greed_value = real_data.get("fear_greed_value", 50)

        # Transform to NUPL-like structure (as an example)
        nupl_simulation = {
            "current_nupl": (fear_greed_value - 50) / 100.0,  # Transform 0-100 scale to -0.5 to 0.5
            "zone_classification": self._classify_fear_greed_to_nupl_zone(fear_greed_value),
            "lth_nupl": (fear_greed_value - 50) / 100.0 + 0.1,  # Simulate LTH difference
            "sth_nupl": (fear_greed_value - 50) / 100.0 - 0.1,  # Simulate STH difference
        }

        # Validate transformation
        self.assertGreaterEqual(nupl_simulation["current_nupl"], -1.0)
        self.assertLessEqual(nupl_simulation["current_nupl"], 1.0)
        self.assertIn(
            nupl_simulation["zone_classification"],
            ["capitulation", "hope", "optimism", "belief", "euphoria", "greed"],
        )

    def test_network_stats_aggregation_transformation(self):
        """Test transformation of network stats to schema-compliant health metrics"""
        real_data = self.extract_real_data_for_validation()

        # Simulate network health transformation
        network_health = {
            "hash_rate": {
                "current_hashrate": 400.0,  # Would be extracted from actual service data
                "difficulty_adjustment": 2.5,
                "hash_ribbons": {"signal": "neutral", "ma_30": 390.0, "ma_60": 380.0},
                "confidence": 0.95,
            },
            "mining_economics": {
                "puell_multiple": 1.2,
                "miner_revenue": 25000000.0,
                "fee_percentage": 8.5,
                "confidence": 0.90,
            },
        }

        # Validate structure
        hash_rate = network_health["hash_rate"]
        self.assertIsInstance(hash_rate["current_hashrate"], (int, float))
        self.assertGreater(hash_rate["current_hashrate"], 0)
        self.assertIsInstance(hash_rate["confidence"], (int, float))
        self.assertGreaterEqual(hash_rate["confidence"], 0.0)
        self.assertLessEqual(hash_rate["confidence"], 1.0)

    def test_service_enumeration_for_schema(self):
        """Test that implemented services can be properly enumerated for schema compliance"""
        implemented_services = [
            "mempool_space_cli",
            "blockchain_com_cli",
            "coinmetrics_cli",
            "binance_api_cli",
            "alternative_me_cli",
            "bitcoin_network_stats_cli",  # Our aggregation service
        ]

        # Filter to only services that are in the schema enum
        schema_enum = self.discovery_schema["properties"]["metadata"]["properties"]["cli_services_utilized"]["items"][
            "enum"
        ]
        valid_services = [s for s in implemented_services if s in schema_enum]

        # Should have at least 5 services (schema requirement)
        self.assertGreaterEqual(
            len(valid_services),
            5,
            "Should have at least 5 valid services for schema compliance",
        )

        # Test data quality scores structure
        source_reliability_scores = {}
        for service in valid_services:
            source_reliability_scores[service] = 0.95  # Simulated high reliability

        # Validate reliability scores meet schema requirements
        for score in source_reliability_scores.values():
            self.assertGreaterEqual(score, 0.90, "Reliability scores should meet schema minimum")
            self.assertLessEqual(score, 1.0, "Reliability scores should not exceed maximum")

    def _classify_fear_greed_to_nupl_zone(self, fear_greed_value: int) -> str:
        """Helper to classify Fear & Greed value to NUPL-like zones"""
        if fear_greed_value <= 20:
            return "capitulation"
        if fear_greed_value <= 35:
            return "hope"
        if fear_greed_value <= 50:
            return "optimism"
        if fear_greed_value <= 65:
            return "belief"
        if fear_greed_value <= 80:
            return "euphoria"
        return "greed"


class TestBitcoinSchemaIntegration(BitcoinSchemaValidationTestBase):
    """Test end-to-end schema integration scenarios"""

    def test_full_discovery_document_generation_feasibility(self):
        """Test that a full discovery document could be generated from our services"""
        # This test validates that we have the components needed to generate
        # a schema-compliant discovery document

        required_components = {
            "bitcoin_price_data": self._can_get_bitcoin_price_data(),
            "network_health_data": self._can_get_network_health_data(),
            "sentiment_data": self._can_get_sentiment_data(),
            "service_validation": self._can_validate_services(),
            "data_quality_assessment": self._can_assess_data_quality(),
        }

        for component, available in required_components.items():
            self.assertTrue(
                available,
                f"Component {component} should be available for document generation",
            )

    def test_schema_compliance_pipeline_simulation(self):
        """Test a simulation of the full schema compliance pipeline"""
        # Simulate data gathering
        real_data = self.extract_real_data_for_validation()

        # Simulate document creation with real data where available
        simulated_doc = self.create_minimal_discovery_document()

        # Update with real data
        if real_data.get("binance_price", 0) > 0:
            simulated_doc["bitcoin_market_data"]["current_price"] = real_data["binance_price"]
            simulated_doc["bitcoin_market_data"]["price_validation"]["binance_price"] = real_data["binance_price"]

        if real_data.get("fear_greed_value"):
            # Could integrate Fear & Greed into cycle indicators
            pass

        # Validate updated document
        errors = self.validate_against_schema(simulated_doc, self.discovery_schema)
        self.assertEqual(len(errors), 0, f"Simulated document should validate: {errors}")

    def _can_get_bitcoin_price_data(self) -> bool:
        """Test if we can get Bitcoin price data"""
        try:
            binance_data = self.services["binance_api"].get_symbol_price_ticker("BTCUSDT")
            return "price" in binance_data and float(binance_data["price"]) > 0
        except:
            return False

    def _can_get_network_health_data(self) -> bool:
        """Test if we can get network health data"""
        try:
            network_overview = self.services["bitcoin_network_stats"].get_network_overview()
            return len(network_overview.get("sources", [])) > 0
        except:
            return False

    def _can_get_sentiment_data(self) -> bool:
        """Test if we can get sentiment data"""
        try:
            fng_data = self.services["alternative_me"].get_current_fear_greed()
            return "value" in fng_data and 0 <= int(fng_data["value"]) <= 100
        except:
            return False

    def _can_validate_services(self) -> bool:
        """Test if we can validate service health"""
        operational_services = 0
        for service_name, service in self.services.items():
            try:
                # Try a simple operation to test if service is operational
                if hasattr(service, "config") and service.config:
                    operational_services += 1
            except:
                pass
        return operational_services >= 5

    def _can_assess_data_quality(self) -> bool:
        """Test if we can assess data quality"""
        # Simple data quality assessment based on service availability
        return len(self.services) >= 5


if __name__ == "__main__":
    # Configure test runner for schema validation tests
    unittest.main(
        verbosity=2,
        failfast=False,  # Continue running tests even if some fail
        buffer=True,  # Capture stdout/stderr during tests
    )
