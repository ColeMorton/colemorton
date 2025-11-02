#!/usr/bin/env python3
"""
Regional Schema Selector for Macro Analysis
Dynamically selects appropriate schema based on region parameter
"""

import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class SchemaSelector:
    """Dynamic schema selection based on region"""

    def __init__(self):
        self.schema_dir = Path(__file__).parent.parent / "schemas"
        self._schema_cache = {}

    def get_schema_for_region(self, region: str, analysis_type: str = "discovery") -> dict[str, Any]:
        """
        Get appropriate schema for region and analysis type

        Args:
            region: Region code (US, EUROPE, ASIA, GLOBAL)
            analysis_type: Type of analysis (discovery, analysis, synthesis, validation)

        Returns:
            Dict containing the appropriate schema

        Raises:
            FileNotFoundError: If schema file not found
            ValueError: If region not supported
        """
        region = region.upper()
        schema_key = f"{region}_{analysis_type}"

        # Check cache first
        if schema_key in self._schema_cache:
            return self._schema_cache[schema_key]

        # Determine schema file path
        schema_file = self._get_schema_file_path(region, analysis_type)

        if not schema_file.exists():
            logger.warning(f"Region-specific schema not found: {schema_file}")
            # Fallback to default schema
            schema_file = self._get_default_schema_path(analysis_type)

        if not schema_file.exists():
            raise FileNotFoundError(f"No schema found for {region} {analysis_type}")

        # Load and cache schema
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)

        self._schema_cache[schema_key] = schema
        logger.info(f"Loaded schema for {region} {analysis_type}: {schema_file.name}")

        return schema

    def _get_schema_file_path(self, region: str, analysis_type: str) -> Path:
        """Get region-specific schema file path"""
        region_mapping = {
            "US": "",  # Default US schema has no suffix
            "EUROPE": "_europe",
            "ASIA": "_asia",
            "GLOBAL": "_global",
            "AMERICAS": "_americas",
        }

        suffix = region_mapping.get(region, "")
        filename = f"macro_analysis_{analysis_type}_schema{suffix}.json"

        return self.schema_dir / filename

    def _get_default_schema_path(self, analysis_type: str) -> Path:
        """Get default (US) schema file path"""
        return self.schema_dir / f"macro_analysis_{analysis_type}_schema.json"

    def validate_region_support(self, region: str) -> bool:
        """Check if region has schema support"""
        region = region.upper()
        supported_regions = ["US", "EUROPE", "ASIA", "GLOBAL", "AMERICAS"]
        return region in supported_regions

    def get_regional_requirements(self, region: str) -> dict[str, Any]:
        """Get region-specific requirements and mappings"""
        region = region.upper()

        requirements = {
            "US": {
                "central_bank": "Fed",
                "policy_rate_field": "fed_funds_rate",
                "volatility_index": "VIX",
                "currency_focus": "DXY",
                "main_currency_pair": "USD/EUR",
                "business_cycle_authority": "NBER",
                "required_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                ],
            },
            "AMERICAS": {
                "central_bank": "Regional_CBs",
                "policy_rate_field": "regional_policy_rates",
                "volatility_index": "VIX",
                "currency_focus": "Multi_Currency",
                "main_currency_pair": "USD/Regional",
                "business_cycle_authority": "Regional",
                "required_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                    "fmp_cli",
                ],
            },
            "EUROPE": {
                "central_bank": "ECB",
                "policy_rate_field": "ecb_deposit_rate",
                "volatility_index": "VSTOXX",
                "currency_focus": "EUR/USD",
                "main_currency_pair": "EUR/USD",
                "business_cycle_authority": "OECD",
                "required_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                    "ecb_cli",
                ],
            },
            "ASIA": {
                "central_bank": "Regional",
                "policy_rate_field": "policy_rates",
                "volatility_index": "Regional_VIX",
                "currency_focus": "Regional",
                "main_currency_pair": "USD/Asia",
                "business_cycle_authority": "Regional",
                "required_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                ],
            },
            "GLOBAL": {
                "central_bank": "Multi",
                "policy_rate_field": "global_policy_rates",
                "volatility_index": "Global_VIX",
                "currency_focus": "Multi",
                "main_currency_pair": "Multi",
                "business_cycle_authority": "IMF/OECD",
                "required_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                    "world_bank_cli",
                ],
            },
        }

        return requirements.get(region, requirements["US"])  # Default to US

    def get_field_mapping(self, region: str) -> dict[str, str]:
        """Get field name mappings for region-specific data structures"""
        region = region.upper()

        mappings = {
            "US": {
                "policy_rate": "fed_funds_rate",
                "central_bank_balance_sheet": "fed_balance_sheet",
                "volatility_index": "vix_analysis",
                "currency_analysis": "dxy_analysis",
            },
            "AMERICAS": {
                "policy_rate": "regional_policy_rates",
                "central_bank_balance_sheet": "regional_balance_sheets",
                "volatility_index": "vix_analysis",
                "currency_analysis": "regional_currency_analysis",
            },
            "EUROPE": {
                "policy_rate": "ecb_deposit_rate",
                "central_bank_balance_sheet": "ecb_balance_sheet",
                "volatility_index": "vstoxx_analysis",
                "currency_analysis": "eur_usd_analysis",
            },
            "ASIA": {
                "policy_rate": "regional_policy_rates",
                "central_bank_balance_sheet": "regional_balance_sheets",
                "volatility_index": "regional_vix_analysis",
                "currency_analysis": "regional_currency_analysis",
            },
            "GLOBAL": {
                "policy_rate": "global_policy_rates",
                "central_bank_balance_sheet": "global_balance_sheets",
                "volatility_index": "global_vix_analysis",
                "currency_analysis": "global_currency_analysis",
            },
        }

        return mappings.get(region, mappings["US"])  # Default to US


def create_schema_selector() -> SchemaSelector:
    """Factory function to create schema selector instance"""
    return SchemaSelector()


def get_schema_for_region(region: str, analysis_type: str = "discovery") -> dict[str, Any]:
    """Convenience function to get schema for region"""
    selector = create_schema_selector()
    return selector.get_schema_for_region(region, analysis_type)


def validate_data_against_regional_schema(
    data: dict[str, Any], region: str, analysis_type: str = "discovery"
) -> tuple[bool, list]:
    """
    Validate data against region-appropriate schema

    Returns:
        tuple: (is_valid, list_of_errors)
    """
    try:
        import jsonschema
    except ImportError:
        logger.warning("jsonschema not available, skipping validation")
        return True, []

    try:
        schema = get_schema_for_region(region, analysis_type)
        jsonschema.validate(data, schema)
        return True, []

    except jsonschema.ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        return False, [e.message]

    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        return False, [str(e)]


if __name__ == "__main__":
    # Test the schema selector
    selector = create_schema_selector()

    # Test different regions
    for region in ["US", "EUROPE", "ASIA", "GLOBAL"]:
        try:
            schema = selector.get_schema_for_region(region)
            requirements = selector.get_regional_requirements(region)
            mappings = selector.get_field_mapping(region)

            print("\n{region} Schema:")
            print("  Central Bank: {requirements['central_bank']}")
            print("  Policy Rate Field: {requirements['policy_rate_field']}")
            print("  Volatility Index: {requirements['volatility_index']}")
            print("  Schema ID: {schema.get('$id', 'Unknown')}")

        except Exception:
            print("{region} Schema Error: {e}")
