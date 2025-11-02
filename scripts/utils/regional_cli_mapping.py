#!/usr/bin/env python3
"""
Regional CLI Service Mapping
Maps regions to appropriate CLI services and data sources
"""

import logging
from typing import Any


logger = logging.getLogger(__name__)


class RegionalCLIMapping:
    """Regional CLI service mapping for macro-economic analysis"""

    def __init__(self):
        self.service_mappings = self._initialize_service_mappings()
        self.priority_mappings = self._initialize_priority_mappings()

    def _initialize_service_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize region-specific service mappings"""
        return {
            "US": {
                "primary_services": [
                    "fred_economic_cli",
                    "alpha_vantage_cli",
                    "eia_energy_cli",
                    "yahoo_finance_cli",
                ],
                "secondary_services": ["imf_cli", "fmp_cli", "coingecko_cli"],
                "regional_specialties": {
                    "central_bank_data": "fred_economic_cli",
                    "energy_data": "eia_energy_cli",
                    "market_data": "alpha_vantage_cli",
                    "currency_data": "fmp_cli",
                },
                "data_focus": {
                    "policy_rate": "fed_funds_rate",
                    "central_bank": "Federal Reserve",
                    "currency": "USD/DXY",
                    "volatility_index": "VIX",
                    "yield_curve": "US Treasury",
                },
            },
            "EUROPE": {
                "primary_services": [
                    "fred_economic_cli",  # Still needed for cross-regional data
                    "alpha_vantage_cli",
                    "imf_cli",
                    "yahoo_finance_cli",
                ],
                "secondary_services": ["fmp_cli", "eia_energy_cli", "coingecko_cli"],
                "regional_specialties": {
                    "central_bank_data": "fred_economic_cli",  # ECB data often available through FRED
                    "energy_data": "eia_energy_cli",  # Global energy data
                    "market_data": "alpha_vantage_cli",
                    "currency_data": "fmp_cli",
                },
                "data_focus": {
                    "policy_rate": "ecb_deposit_rate",
                    "central_bank": "European Central Bank",
                    "currency": "EUR/USD",
                    "volatility_index": "VSTOXX",
                    "yield_curve": "German Bunds",
                },
            },
            "ASIA": {
                "primary_services": [
                    "fred_economic_cli",
                    "alpha_vantage_cli",
                    "yahoo_finance_cli",
                    "imf_cli",
                ],
                "secondary_services": ["fmp_cli", "eia_energy_cli", "coingecko_cli"],
                "regional_specialties": {
                    "central_bank_data": "fred_economic_cli",  # Regional central bank data
                    "energy_data": "eia_energy_cli",
                    "market_data": "alpha_vantage_cli",
                    "currency_data": "fmp_cli",
                },
                "data_focus": {
                    "policy_rate": "regional_policy_rates",
                    "central_bank": "Regional Central Banks",
                    "currency": "Regional/USD",
                    "volatility_index": "Regional VIX",
                    "yield_curve": "Regional Bonds",
                },
            },
            "GLOBAL": {
                "primary_services": [
                    "fred_economic_cli",
                    "imf_cli",
                    "alpha_vantage_cli",
                    "eia_energy_cli",
                ],
                "secondary_services": ["fmp_cli", "yahoo_finance_cli", "coingecko_cli"],
                "regional_specialties": {
                    "central_bank_data": "fred_economic_cli",
                    "global_coordination": "imf_cli",
                    "energy_data": "eia_energy_cli",
                    "market_data": "alpha_vantage_cli",
                    "currency_data": "fmp_cli",
                },
                "data_focus": {
                    "policy_rate": "global_policy_coordination",
                    "central_bank": "Multi-Central Bank",
                    "currency": "Multi-Currency",
                    "volatility_index": "Global VIX",
                    "yield_curve": "Global Yield Curves",
                },
            },
        }

    def _initialize_priority_mappings(self) -> dict[str, list[str]]:
        """Initialize service priority by region"""
        return {
            "US": [
                "fred_economic_cli",  # Highest priority for US data
                "alpha_vantage_cli",  # Market data
                "eia_energy_cli",  # Energy data
                "yahoo_finance_cli",  # Market data backup
                "imf_cli",  # Global context
                "fmp_cli",  # Advanced financial data
                "coingecko_cli",  # Crypto/risk appetite
            ],
            "EUROPE": [
                "fred_economic_cli",  # ECB data often available
                "imf_cli",  # European/global data
                "alpha_vantage_cli",  # Market data
                "yahoo_finance_cli",  # Market data backup
                "fmp_cli",  # Currency data
                "eia_energy_cli",  # Energy data
                "coingecko_cli",  # Risk appetite
            ],
            "ASIA": [
                "fred_economic_cli",  # Regional data available
                "imf_cli",  # Regional/global context
                "alpha_vantage_cli",  # Market data
                "yahoo_finance_cli",  # Market data
                "fmp_cli",  # Currency data
                "eia_energy_cli",  # Energy data
                "coingecko_cli",  # Risk appetite
            ],
            "GLOBAL": [
                "imf_cli",  # Highest priority for global
                "fred_economic_cli",  # US anchor data
                "alpha_vantage_cli",  # Global market data
                "eia_energy_cli",  # Global energy
                "fmp_cli",  # Multi-currency
                "yahoo_finance_cli",  # Market backup
                "coingecko_cli",  # Global risk appetite
            ],
        }

    def get_services_for_region(self, region: str) -> dict[str, list[str]]:
        """Get prioritized service list for region"""
        region = region.upper()

        if region not in self.service_mappings:
            logger.warning(f"Unknown region {region}, defaulting to US")
            region = "US"

        mapping = self.service_mappings[region]

        return {
            "primary": mapping["primary_services"],
            "secondary": mapping["secondary_services"],
            "all": mapping["primary_services"] + mapping["secondary_services"],
            "prioritized": self.priority_mappings[region],
        }

    def get_regional_specialties(self, region: str) -> dict[str, str]:
        """Get regional service specialties"""
        region = region.upper()
        return self.service_mappings.get(region, self.service_mappings["US"])["regional_specialties"]

    def get_data_focus(self, region: str) -> dict[str, str]:
        """Get regional data focus mappings"""
        region = region.upper()
        return self.service_mappings.get(region, self.service_mappings["US"])["data_focus"]

    def get_minimum_services_required(self, region: str) -> int:
        """Get minimum number of services required for institutional grade"""
        region = region.upper()

        # Regional requirements
        requirements = {
            "US": 4,  # Need comprehensive US coverage
            "EUROPE": 4,  # Need ECB + global context
            "ASIA": 4,  # Need regional + global coverage
            "GLOBAL": 5,  # Need broader coverage for global analysis
        }

        return requirements.get(region, 4)  # Default to 4

    def validate_service_coverage(self, region: str, available_services: list[str]) -> dict[str, Any]:
        """Validate if available services provide adequate regional coverage"""
        region = region.upper()
        region_services = self.get_services_for_region(region)
        specialties = self.get_regional_specialties(region)
        min_required = self.get_minimum_services_required(region)

        # Check coverage
        primary_coverage = len([s for s in region_services["primary"] if s in available_services])
        total_coverage = len([s for s in region_services["all"] if s in available_services])

        # Check specialty coverage
        specialty_coverage = {}
        for specialty, service in specialties.items():
            specialty_coverage[specialty] = service in available_services

        # Assess adequacy
        is_adequate = total_coverage >= min_required and primary_coverage >= 2

        return {
            "is_adequate": is_adequate,
            "total_coverage": total_coverage,
            "primary_coverage": primary_coverage,
            "minimum_required": min_required,
            "specialty_coverage": specialty_coverage,
            "missing_primary": [s for s in region_services["primary"] if s not in available_services],
            "available_services": available_services,
            "coverage_percentage": total_coverage / len(region_services["all"]) * 100,
        }

    def get_service_alternatives(self, region: str, unavailable_service: str) -> list[str]:
        """Get alternative services if one is unavailable"""
        region = region.upper()

        alternatives = {
            "fred_economic_cli": ["imf_cli", "alpha_vantage_cli"],
            "alpha_vantage_cli": ["yahoo_finance_cli", "fmp_cli"],
            "imf_cli": ["fred_economic_cli", "fmp_cli"],
            "eia_energy_cli": ["alpha_vantage_cli", "fred_economic_cli"],
            "yahoo_finance_cli": ["alpha_vantage_cli", "fmp_cli"],
            "fmp_cli": ["alpha_vantage_cli", "yahoo_finance_cli"],
            "coingecko_cli": ["alpha_vantage_cli", "fmp_cli"],
        }

        return alternatives.get(unavailable_service, [])

    def get_regional_data_priorities(self, region: str) -> list[dict[str, Any]]:
        """Get regional data collection priorities"""
        region = region.upper()

        priorities = {
            "US": [
                {
                    "data_type": "fed_policy",
                    "priority": 1,
                    "services": ["fred_economic_cli"],
                },
                {
                    "data_type": "us_market_data",
                    "priority": 2,
                    "services": ["alpha_vantage_cli", "yahoo_finance_cli"],
                },
                {
                    "data_type": "energy_data",
                    "priority": 3,
                    "services": ["eia_energy_cli"],
                },
                {"data_type": "global_context", "priority": 4, "services": ["imf_cli"]},
            ],
            "EUROPE": [
                {
                    "data_type": "ecb_policy",
                    "priority": 1,
                    "services": ["fred_economic_cli"],
                },
                {
                    "data_type": "european_markets",
                    "priority": 2,
                    "services": ["alpha_vantage_cli", "yahoo_finance_cli"],
                },
                {"data_type": "global_context", "priority": 3, "services": ["imf_cli"]},
                {
                    "data_type": "energy_security",
                    "priority": 4,
                    "services": ["eia_energy_cli"],
                },
            ],
            "ASIA": [
                {
                    "data_type": "regional_policy",
                    "priority": 1,
                    "services": ["fred_economic_cli", "imf_cli"],
                },
                {
                    "data_type": "asian_markets",
                    "priority": 2,
                    "services": ["alpha_vantage_cli", "yahoo_finance_cli"],
                },
                {"data_type": "global_context", "priority": 3, "services": ["imf_cli"]},
                {
                    "data_type": "energy_data",
                    "priority": 4,
                    "services": ["eia_energy_cli"],
                },
            ],
            "GLOBAL": [
                {
                    "data_type": "global_coordination",
                    "priority": 1,
                    "services": ["imf_cli"],
                },
                {
                    "data_type": "anchor_economies",
                    "priority": 2,
                    "services": ["fred_economic_cli"],
                },
                {
                    "data_type": "global_markets",
                    "priority": 3,
                    "services": ["alpha_vantage_cli"],
                },
                {
                    "data_type": "global_energy",
                    "priority": 4,
                    "services": ["eia_energy_cli"],
                },
            ],
        }

        return priorities.get(region, priorities["US"])


def create_regional_cli_mapping() -> RegionalCLIMapping:
    """Factory function to create regional CLI mapping"""
    return RegionalCLIMapping()


def get_services_for_region(region: str) -> dict[str, list[str]]:
    """Convenience function to get services for region"""
    mapping = create_regional_cli_mapping()
    return mapping.get_services_for_region(region)


def validate_regional_service_coverage(region: str, available_services: list[str]) -> dict[str, Any]:
    """Convenience function to validate service coverage"""
    mapping = create_regional_cli_mapping()
    return mapping.validate_service_coverage(region, available_services)


if __name__ == "__main__":
    # Test the regional CLI mapping
    mapping = create_regional_cli_mapping()

    for region in ["US", "EUROPE", "ASIA", "GLOBAL"]:
        services = mapping.get_services_for_region(region)
        specialties = mapping.get_regional_specialties(region)
        data_focus = mapping.get_data_focus(region)

        print("\n{region} Configuration:")
        print("  Primary Services: {services['primary']}")
        print("  Central Bank: {data_focus['central_bank']}")
        print("  Currency Focus: {data_focus['currency']}")
        print("  Specialties: {list(specialties.keys())}")
        print("  Min Required: {mapping.get_minimum_services_required(region)}")

        # Test coverage validation
        test_services = services["primary"][:3]  # Simulate partial availability
        coverage = mapping.validate_service_coverage(region, test_services)
        print(
            f"  Coverage (3 services): {coverage['coverage_percentage']:.1f}% - {'Adequate' if coverage['is_adequate'] else 'Inadequate'}"
        )
