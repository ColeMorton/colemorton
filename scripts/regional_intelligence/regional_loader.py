#!/usr/bin/env python3
"""
Regional Intelligence Loader
Loads and manages sophisticated regional economic intelligence configurations
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CentralBankInfo:
    """Central bank information structure"""

    name: str
    short_name: str
    policy_rate_name: str
    policy_framework: str
    meeting_frequency: int
    policy_tools: list[str]


@dataclass
class CurrencyInfo:
    """Currency information structure"""

    code: str
    name: str
    regime: str
    is_reserve_currency: bool = False
    safe_haven_status: bool = False
    correlation_with_risk_sentiment: float = 0.0


@dataclass
class EconomicIndicator:
    """Economic indicator structure"""

    name: str
    code: str
    frequency: str
    importance: str
    typical_range: list[float]
    target_level: float | None = None
    fred_code: str | None = None
    expansion_threshold: float | None = None


class RegionalIntelligenceLoader:
    """Loads and manages regional intelligence configurations"""

    def __init__(self, config_dir: str | None = None):
        if config_dir is None:
            # Default to configs directory relative to this file
            current_dir = Path(__file__).parent
            config_dir = current_dir / "configs"

        self.config_dir = Path(config_dir)
        self.loaded_configs: dict[str, dict[str, Any]] = {}
        self._load_all_configs()

    def _load_all_configs(self) -> None:
        """Load all available regional configurations"""
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Regional intelligence config directory not found: {self.config_dir}")

        for config_file in self.config_dir.glob("*.yaml"):
            region = config_file.stem.upper()
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    self.loaded_configs[region] = config
                    print("Loaded regional intelligence for {region}")
            except Exception:
                print("Error loading config for {region}: {e}")

    def get_region_config(self, region: str) -> dict[str, Any]:
        """Get complete configuration for a region"""
        region = region.upper()
        if region not in self.loaded_configs:
            # Try to find closest match
            available_regions = list(self.loaded_configs.keys())
            # Simple matching - could be enhanced
            if region == "EU":
                region = "EUROPE"
            elif region in available_regions:
                pass
            else:
                # Fallback to US as default
                print("Region {region} not found, using US as fallback")
                region = "US"

        return self.loaded_configs.get(region, self.loaded_configs.get("US", {}))

    def get_central_bank_info(self, region: str) -> CentralBankInfo:
        """Get central bank information for region"""
        config = self.get_region_config(region)
        cb_config = config.get("central_bank", {})

        return CentralBankInfo(
            name=cb_config.get("name", "Central Bank"),
            short_name=cb_config.get("short_name", "CB"),
            policy_rate_name=cb_config.get("policy_rate_name", "Policy Rate"),
            policy_framework=cb_config.get("policy_framework", "unknown"),
            meeting_frequency=cb_config.get("meeting_frequency", 8),
            policy_tools=cb_config.get("policy_tools", []),
        )

    def get_currency_info(self, region: str) -> CurrencyInfo:
        """Get currency information for region"""
        config = self.get_region_config(region)
        currency_config = config.get("currency", {})

        return CurrencyInfo(
            code=currency_config.get("code", "USD"),
            name=currency_config.get("name", "Currency"),
            regime=currency_config.get("regime", "floating"),
            is_reserve_currency=currency_config.get("is_reserve_currency", False),
            safe_haven_status=currency_config.get("safe_haven_status", False),
            correlation_with_risk_sentiment=currency_config.get("correlation_with_risk_sentiment", 0.0),
        )

    def get_key_economic_indicators(self, region: str) -> list[EconomicIndicator]:
        """Get key economic indicators for region"""
        config = self.get_region_config(region)
        indicators_config = config.get("key_economic_indicators", {})

        indicators = []

        # Handle different structures (primary/secondary vs direct)
        if "primary" in indicators_config:
            for indicator_data in indicators_config.get("primary", []):
                indicators.append(self._parse_indicator(indicator_data))
            for indicator_data in indicators_config.get("secondary", []):
                indicators.append(self._parse_indicator(indicator_data))
        else:
            # Handle regional structure (like Asia with country-specific indicators)
            for key, value in indicators_config.items():
                if isinstance(value, list):
                    for indicator_data in value:
                        if isinstance(indicator_data, dict):
                            indicators.append(self._parse_indicator(indicator_data))

        return indicators

    def _parse_indicator(self, indicator_data: dict[str, Any]) -> EconomicIndicator:
        """Parse individual indicator data"""
        return EconomicIndicator(
            name=indicator_data.get("name", "Unknown Indicator"),
            code=indicator_data.get("code", "UNKNOWN"),
            frequency=indicator_data.get("frequency", "unknown"),
            importance=indicator_data.get("importance", "medium"),
            typical_range=indicator_data.get("typical_range", [0.0, 100.0]),
            target_level=indicator_data.get("target_level"),
            fred_code=indicator_data.get("fred_code"),
            expansion_threshold=indicator_data.get("expansion_threshold"),
        )

    def get_benchmark_securities(self, region: str) -> dict[str, Any]:
        """Get benchmark securities for region"""
        config = self.get_region_config(region)
        return config.get("benchmark_securities", {})

    def get_risk_factors(self, region: str) -> dict[str, list[dict[str, Any]]]:
        """Get risk factors for region"""
        config = self.get_region_config(region)
        return config.get("risk_factors", {})

    def get_correlation_patterns(self, region: str) -> dict[str, float]:
        """Get typical correlation patterns for region"""
        config = self.get_region_config(region)
        return config.get("correlation_patterns", {})

    def get_market_structure(self, region: str) -> dict[str, Any]:
        """Get market structure information for region"""
        config = self.get_region_config(region)
        return config.get("market_structure", {})

    def get_transmission_channels(self, region: str) -> dict[str, Any]:
        """Get economic transmission channels for region"""
        config = self.get_region_config(region)
        return config.get("economic_transmission_channels", {})

    def get_regional_specifics(self, region: str) -> dict[str, Any]:
        """Get regional specific characteristics"""
        config = self.get_region_config(region)
        return config.get("regional_specifics", {})

    def get_data_sources(self, region: str) -> dict[str, list[str]]:
        """Get data sources for region"""
        config = self.get_region_config(region)
        return config.get("data_sources", {})

    def get_quality_standards(self, region: str) -> dict[str, Any]:
        """Get quality standards for region"""
        config = self.get_region_config(region)
        return config.get(
            "quality_standards",
            {
                "min_confidence_threshold": 0.85,
                "data_freshness_requirement": 30,
                "cross_validation_threshold": 0.90,
                "regional_specificity_target": 0.95,
            },
        )

    def get_special_features(self, region: str) -> dict[str, Any]:
        """Get special features for region (like green transition for Europe)"""
        config = self.get_region_config(region)
        return config.get("special_features", {})

    def list_available_regions(self) -> list[str]:
        """List all available regions"""
        return list(self.loaded_configs.keys())

    def validate_region_config(self, region: str) -> dict[str, Any]:
        """Validate region configuration completeness"""
        config = self.get_region_config(region)
        validation_results = {
            "region": region,
            "config_found": region.upper() in self.loaded_configs,
            "required_sections": {},
            "completeness_score": 0.0,
        }

        required_sections = [
            "central_bank",
            "currency",
            "key_economic_indicators",
            "benchmark_securities",
            "risk_factors",
            "correlation_patterns",
        ]

        present_sections = 0
        for section in required_sections:
            is_present = section in config and config[section]
            validation_results["required_sections"][section] = is_present
            if is_present:
                present_sections += 1

        validation_results["completeness_score"] = present_sections / len(required_sections)

        return validation_results

    def get_regional_policy_rate_mapping(self, region: str) -> dict[str, str]:
        """Get mapping of policy rate names and typical ranges"""
        config = self.get_region_config(region)
        cb_info = config.get("central_bank", {})

        # Handle multi-bank regions
        if "primary_banks" in cb_info:
            banks = cb_info["primary_banks"]
            return {bank["short"]: bank.get("policy_rate", "policy_rate") for bank in banks}
        return {cb_info.get("short_name", "CB"): cb_info.get("policy_rate_name", "policy_rate")}

    def get_regional_analysis_priorities(self, region: str) -> dict[str, float]:
        """Get analysis priorities and weights for different economic factors"""
        config = self.get_region_config(region)

        # Extract weights from market structure and regional characteristics
        priorities = {
            "monetary_policy": 0.25,
            "fiscal_policy": 0.15,
            "trade_flows": 0.20,
            "commodity_exposure": 0.10,
            "financial_stability": 0.20,
            "structural_factors": 0.10,
        }

        # Adjust based on regional characteristics
        market_structure = config.get("market_structure", {})
        regional_specifics = config.get("regional_specifics", {})

        # Enhance priorities based on regional characteristics
        if market_structure.get("banking_system") == "bank_based":
            priorities["monetary_policy"] *= 1.2
            priorities["financial_stability"] *= 1.3

        if "commodity" in str(config.get("currency", {}).get("name", "")).lower():
            priorities["commodity_exposure"] *= 2.0
            priorities["trade_flows"] *= 1.3

        # Normalize to sum to 1.0
        total_weight = sum(priorities.values())
        priorities = {k: v / total_weight for k, v in priorities.items()}

        return priorities


def main():
    """Test the regional intelligence loader"""
    loader = RegionalIntelligenceLoader()

    print("Available regions:", loader.list_available_regions())

    for region in ["US", "EUROPE", "ASIA"]:
        print("\n=== {region} ===")

        # Test central bank info
        cb_info = loader.get_central_bank_info(region)
        print("Central Bank: {cb_info.name} ({cb_info.short_name})")
        print("Policy Rate: {cb_info.policy_rate_name}")

        # Test currency info
        currency_info = loader.get_currency_info(region)
        print("Currency: {currency_info.code} - {currency_info.name}")
        print("Regime: {currency_info.regime}")

        # Test key indicators
        indicators = loader.get_key_economic_indicators(region)
        print("Key Indicators: {len(indicators)} found")
        if indicators:
            print("  - {indicators[0].name} ({indicators[0].importance})")

        # Test validation
        validation = loader.validate_region_config(region)
        print("Completeness: {validation['completeness_score']:.2f}")


if __name__ == "__main__":
    main()
