#!/usr/bin/env python3
"""
Indicator Mapper
Intelligent mapping of discovery data to region-specific economic indicators
"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from .regional_loader import EconomicIndicator, RegionalIntelligenceLoader


@dataclass
class IndicatorMapping:
    """Mapping between discovery data and regional indicators"""

    regional_indicator: EconomicIndicator
    discovery_path: str
    extraction_method: str
    confidence_adjustment: float
    regional_weight: float


@dataclass
class ExtractedIndicator:
    """Extracted and processed indicator data"""

    name: str
    code: str
    current_value: float
    trend_direction: str
    percentile_rank: float
    target_deviation: float
    confidence: float
    regional_significance: float


class IndicatorMapper:
    """Maps discovery data to region-specific economic indicators"""

    def __init__(self):
        self.regional_loader = RegionalIntelligenceLoader()
        self.indicator_mappings = self._build_indicator_mappings()

    def _build_indicator_mappings(self) -> dict[str, list[IndicatorMapping]]:
        """Build comprehensive mapping between discovery data and regional indicators"""

        mappings = {}

        for region in self.regional_loader.list_available_regions():
            region_mappings = []
            indicators = self.regional_loader.get_key_economic_indicators(region)

            for indicator in indicators:
                # Map to discovery data paths based on indicator codes and names
                discovery_path = self._map_indicator_to_discovery_path(indicator, region)
                if discovery_path:
                    extraction_method = self._determine_extraction_method(indicator)
                    confidence_adj = self._calculate_confidence_adjustment(indicator, region)
                    regional_weight = self._calculate_regional_weight(indicator, region)

                    mapping = IndicatorMapping(
                        regional_indicator=indicator,
                        discovery_path=discovery_path,
                        extraction_method=extraction_method,
                        confidence_adjustment=confidence_adj,
                        regional_weight=regional_weight,
                    )
                    region_mappings.append(mapping)

            mappings[region] = region_mappings

        return mappings

    def _map_indicator_to_discovery_path(self, indicator: EconomicIndicator, region: str) -> str | None:
        """Map regional indicator to discovery data path"""

        # Common discovery paths for different indicator types
        mapping_rules = {
            # Inflation indicators
            "CPI": "cli_comprehensive_analysis.central_bank_economic_data.inflation_rate.current_value",
            "HICP": "cli_comprehensive_analysis.central_bank_economic_data.inflation_rate.current_value",
            "CORE_CPI": "cli_comprehensive_analysis.central_bank_economic_data.inflation_rate.current_value",
            "PCE": "cli_comprehensive_analysis.central_bank_economic_data.inflation_rate.current_value",
            # Employment indicators
            "INITIAL_CLAIMS": "cli_comprehensive_analysis.central_bank_economic_data.employment_trends.initial_claims_avg",
            "JOLTS": "cli_comprehensive_analysis.central_bank_economic_data.employment_trends.monthly_average",
            "PAYEMS": "cli_comprehensive_analysis.central_bank_economic_data.employment_trends.monthly_average",
            # Growth indicators
            "GDP": "cli_comprehensive_analysis.central_bank_economic_data.gdp_growth.current_value",
            "INDUSTRIAL_PRODUCTION": "cli_comprehensive_analysis.central_bank_economic_data.industrial_production.current_value",
            # PMI indicators
            "ISM_MFG": "business_cycle_data.pmi_analysis.manufacturing_pmi",
            "ISM_SERVICES": "business_cycle_data.pmi_analysis.services_pmi",
            "PMI_MFG": "business_cycle_data.pmi_analysis.manufacturing_pmi",
            "PMI_SERVICES": "business_cycle_data.pmi_analysis.services_pmi",
            "CAIXIN_MFG_PMI": "business_cycle_data.pmi_analysis.manufacturing_pmi",
            # Confidence indicators
            "CONSUMER_CONFIDENCE": "cli_market_intelligence.sentiment_analysis.consumer_confidence",
            "ZEW": "cli_market_intelligence.sentiment_analysis.business_confidence",
            "TANKAN_LMF": "cli_market_intelligence.sentiment_analysis.business_confidence",
            # Policy rates
            "FED_FUNDS_RATE": "monetary_policy_context.policy_stance.policy_rate",
            "ECB_RATE": "monetary_policy_context.policy_stance.policy_rate",
            "BOJ_RATE": "monetary_policy_context.policy_stance.policy_rate",
            # Market indicators
            "VIX": "cli_market_intelligence.volatility_indices.vix",
            "YIELD_CURVE": "cli_market_intelligence.yield_curve.10y_2y_spread",
        }

        # Try exact code match first
        if indicator.code in mapping_rules:
            return mapping_rules[indicator.code]

        # Try partial matching based on indicator name
        name_lower = indicator.name.lower()
        if "inflation" in name_lower or "cpi" in name_lower:
            return mapping_rules["CPI"]
        if "employment" in name_lower or "jobless" in name_lower:
            return mapping_rules["INITIAL_CLAIMS"]
        if "pmi" in name_lower and "manufacturing" in name_lower:
            return mapping_rules["PMI_MFG"]
        if "pmi" in name_lower and "services" in name_lower:
            return mapping_rules["PMI_SERVICES"]
        if "confidence" in name_lower:
            return mapping_rules["CONSUMER_CONFIDENCE"]
        if "gdp" in name_lower:
            return mapping_rules["GDP"]

        return None

    def _determine_extraction_method(self, indicator: EconomicIndicator) -> str:
        """Determine how to extract the indicator value"""

        # Different extraction methods based on data structure
        if indicator.frequency == "quarterly":
            return "quarterly_latest"
        if indicator.frequency == "monthly":
            return "monthly_latest"
        if indicator.frequency == "weekly":
            return "weekly_average"
        if "index" in indicator.name.lower():
            return "index_current"
        return "direct_value"

    def _calculate_confidence_adjustment(self, indicator: EconomicIndicator, region: str) -> float:
        """Calculate confidence adjustment based on indicator and region"""

        # Base confidence adjustments
        importance_adjustments = {
            "critical": 0.05,
            "high": 0.02,
            "medium": 0.0,
            "low": -0.02,
        }

        base_adjustment = importance_adjustments.get(indicator.importance, 0.0)

        # Region-specific adjustments
        regional_data_quality = {
            "US": 0.05,  # High quality, frequent updates
            "EUROPE": 0.03,  # Good quality, some lags
            "ASIA": -0.02,  # Mixed quality, diverse sources
            "AMERICAS": -0.05,  # Emerging market challenges
            "GLOBAL": -0.03,  # Aggregation uncertainties
        }

        regional_adjustment = regional_data_quality.get(region, 0.0)

        return base_adjustment + regional_adjustment

    def _calculate_regional_weight(self, indicator: EconomicIndicator, region: str) -> float:
        """Calculate how important this indicator is for the specific region"""

        # Base weights by importance
        base_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}

        base_weight = base_weights.get(indicator.importance, 0.6)

        # Regional priority adjustments
        regional_priorities = self.regional_loader.get_regional_analysis_priorities(region)

        # Map indicator types to analysis priorities
        if "inflation" in indicator.name.lower() or "cpi" in indicator.code.lower():
            adjustment = regional_priorities.get("monetary_policy", 0.25)
        elif "employment" in indicator.name.lower() or "job" in indicator.name.lower():
            adjustment = regional_priorities.get("structural_factors", 0.10)
        elif "pmi" in indicator.name.lower() or "confidence" in indicator.name.lower():
            adjustment = regional_priorities.get("trade_flows", 0.20)
        elif "gdp" in indicator.name.lower():
            adjustment = regional_priorities.get("structural_factors", 0.10)
        else:
            adjustment = 0.25  # Default

        return min(1.0, base_weight + adjustment)

    def extract_regional_indicators(self, discovery_data: dict[str, Any], region: str) -> list[ExtractedIndicator]:
        """Extract and process regional indicators from discovery data"""

        if region not in self.indicator_mappings:
            return []

        extracted_indicators = []
        mappings = self.indicator_mappings[region]

        for mapping in mappings:
            try:
                # Extract value from discovery data
                value = self._extract_value_from_path(discovery_data, mapping.discovery_path)

                if value is not None:
                    # Process the extracted value
                    processed_indicator = self._process_extracted_value(mapping, value, discovery_data, region)
                    extracted_indicators.append(processed_indicator)

            except Exception:
                print("Error extracting {mapping.regional_indicator.name}: {e}")
                continue

        return extracted_indicators

    def _extract_value_from_path(self, data: dict[str, Any], path: str) -> float | None:
        """Extract value from nested dictionary using dot notation path"""

        try:
            keys = path.split(".")
            current = data

            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None

            # Handle different value formats
            if isinstance(current, (int, float)):
                return float(current)
            if isinstance(current, dict) and "value" in current:
                return float(current["value"])
            if isinstance(current, dict) and "current_value" in current:
                return float(current["current_value"])
            if isinstance(current, dict) and "latest" in current:
                return float(current["latest"])
            return None

        except (KeyError, TypeError, ValueError):
            return None

    def _process_extracted_value(
        self,
        mapping: IndicatorMapping,
        raw_value: float,
        discovery_data: dict[str, Any],
        region: str,
    ) -> ExtractedIndicator:
        """Process extracted value into structured indicator data"""

        indicator = mapping.regional_indicator

        # Determine trend direction
        trend = self._analyze_trend(raw_value, indicator, discovery_data)

        # Calculate percentile rank within typical range
        percentile = self._calculate_percentile_rank(raw_value, indicator.typical_range)

        # Calculate deviation from target
        target_deviation = self._calculate_target_deviation(raw_value, indicator)

        # Calculate confidence score
        confidence = self._calculate_indicator_confidence(mapping, raw_value, discovery_data, region)

        return ExtractedIndicator(
            name=indicator.name,
            code=indicator.code,
            current_value=raw_value,
            trend_direction=trend,
            percentile_rank=percentile,
            target_deviation=target_deviation,
            confidence=confidence,
            regional_significance=mapping.regional_weight,
        )

    def _analyze_trend(
        self,
        current_value: float,
        indicator: EconomicIndicator,
        discovery_data: dict[str, Any],
    ) -> str:
        """Analyze trend direction for the indicator"""

        # Try to get historical values from discovery data
        # This is simplified - in practice would analyze time series

        mid_point = sum(indicator.typical_range) / 2

        if hasattr(indicator, "target_level") and indicator.target_level:
            if abs(current_value - indicator.target_level) < abs(mid_point - indicator.target_level):
                return "improving"
            return "deteriorating"
        # Use typical range positioning
        range_position = (current_value - indicator.typical_range[0]) / (
            indicator.typical_range[1] - indicator.typical_range[0]
        )

        if range_position > 0.6:
            return "elevated"
        if range_position < 0.4:
            return "subdued"
        return "stable"

    def _calculate_percentile_rank(self, value: float, typical_range: list[float]) -> float:
        """Calculate percentile rank within typical range"""

        if len(typical_range) >= 2:
            min_val, max_val = typical_range[0], typical_range[1]
            if max_val > min_val:
                percentile = (value - min_val) / (max_val - min_val)
                return max(0.0, min(1.0, percentile))  # Clamp to 0-1

        return 0.5  # Default to median if can't calculate

    def _calculate_target_deviation(self, value: float, indicator: EconomicIndicator) -> float:
        """Calculate deviation from target level (if available)"""

        if hasattr(indicator, "target_level") and indicator.target_level:
            return ((value - indicator.target_level) / indicator.target_level) * 100

        return 0.0  # No target available

    def _calculate_indicator_confidence(
        self,
        mapping: IndicatorMapping,
        value: float,
        discovery_data: dict[str, Any],
        region: str,
    ) -> float:
        """Calculate confidence score for extracted indicator"""

        base_confidence = 0.85  # Base confidence for extracted data

        # Apply mapping confidence adjustment
        confidence = base_confidence + mapping.confidence_adjustment

        # Check if value is within reasonable range
        typical_range = mapping.regional_indicator.typical_range
        if len(typical_range) >= 2:
            if typical_range[0] <= value <= typical_range[1]:
                range_adjustment = 0.05  # Boost for reasonable values
            else:
                # Penalize values outside typical range
                deviation = min(abs(value - typical_range[0]), abs(value - typical_range[1]))
                max_deviation = abs(typical_range[1] - typical_range[0])
                if max_deviation > 0:
                    range_adjustment = -0.1 * (deviation / max_deviation)
                else:
                    range_adjustment = -0.05
            confidence += range_adjustment

        # Data freshness adjustment (if available in discovery metadata)
        metadata = discovery_data.get("metadata", {})
        if "analysis_date" in metadata:
            # Would check staleness here - simplified for now
            confidence += 0.02  # Small boost for having metadata

        return max(0.0, min(1.0, confidence))  # Clamp to valid range

    def generate_regional_indicator_summary(
        self, extracted_indicators: list[ExtractedIndicator], region: str
    ) -> dict[str, Any]:
        """Generate summary of regional indicators"""

        if not extracted_indicators:
            return {
                "region": region,
                "indicator_count": 0,
                "average_confidence": 0.0,
                "coverage_score": 0.0,
                "key_signals": [],
            }

        # Calculate summary statistics
        avg_confidence = np.mean([ind.confidence for ind in extracted_indicators])

        # Count by importance levels
        importance_counts = {}
        for mapping in self.indicator_mappings.get(region, []):
            importance = mapping.regional_indicator.importance
            importance_counts[importance] = importance_counts.get(importance, 0) + 1

        # Calculate coverage score
        total_expected = sum(importance_counts.values())
        coverage_score = len(extracted_indicators) / total_expected if total_expected > 0 else 0.0

        # Identify key signals
        key_signals = []
        for indicator in extracted_indicators:
            if indicator.regional_significance > 0.8:  # High significance
                if indicator.target_deviation != 0 and abs(indicator.target_deviation) > 25:
                    direction = "above" if indicator.target_deviation > 0 else "below"
                    key_signals.append(
                        {
                            "indicator": indicator.name,
                            "signal": f"significantly_{direction}_target",
                            "deviation": indicator.target_deviation,
                            "confidence": indicator.confidence,
                        }
                    )
                elif indicator.percentile_rank > 0.8 or indicator.percentile_rank < 0.2:
                    level = "elevated" if indicator.percentile_rank > 0.8 else "depressed"
                    key_signals.append(
                        {
                            "indicator": indicator.name,
                            "signal": f"{level}_level",
                            "percentile": indicator.percentile_rank,
                            "confidence": indicator.confidence,
                        }
                    )

        return {
            "region": region,
            "indicator_count": len(extracted_indicators),
            "average_confidence": round(avg_confidence, 3),
            "coverage_score": round(coverage_score, 3),
            "key_signals": key_signals[:5],  # Top 5 signals
            "indicator_breakdown": {
                "by_importance": importance_counts,
                "high_significance": len([ind for ind in extracted_indicators if ind.regional_significance > 0.8]),
            },
        }

    def get_indicator_priorities_for_region(self, region: str) -> dict[str, float]:
        """Get indicator priorities for analysis focus"""

        if region not in self.indicator_mappings:
            return {}

        priorities = {}
        for mapping in self.indicator_mappings[region]:
            indicator = mapping.regional_indicator
            priority_score = mapping.regional_weight * {
                "critical": 1.0,
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4,
            }.get(indicator.importance, 0.6)

            priorities[indicator.code] = priority_score

        return priorities


def main():
    """Test indicator mapper functionality"""

    # Create sample discovery data
    sample_discovery = {
        "cli_comprehensive_analysis": {
            "central_bank_economic_data": {
                "gdp_growth": {"current_value": 2.1},
                "inflation_rate": {"current_value": 2.5},
                "employment_trends": {
                    "monthly_average": 177000,
                    "initial_claims_avg": 220000,
                },
            }
        },
        "business_cycle_data": {"pmi_analysis": {"manufacturing_pmi": 52.3, "services_pmi": 54.1}},
        "cli_market_intelligence": {
            "sentiment_analysis": {"consumer_confidence": 102.5},
            "volatility_indices": {"vix": 17.5},
        },
        "metadata": {"analysis_date": "2025-08-08"},
    }

    mapper = IndicatorMapper()

    # Test indicator extraction for different regions
    for region in ["US", "EUROPE", "ASIA"]:
        print("\n=== {region} Regional Indicators ===")

        extracted = mapper.extract_regional_indicators(sample_discovery, region)
        print("Extracted {len(extracted)} indicators")

        if extracted:
            for indicator in extracted[:3]:  # Show first 3
                print("  {indicator.name}: {indicator.current_value}")
                print("    Trend: {indicator.trend_direction}")
                print("    Confidence: {indicator.confidence:.3f}")
                print(f"    Regional Significance: {indicator.regional_significance:.2f}")

        # Generate summary
        summary = mapper.generate_regional_indicator_summary(extracted, region)
        print("\nSummary:")
        print("  Coverage Score: {summary['coverage_score']:.2f}")
        print("  Average Confidence: {summary['average_confidence']:.3f}")
        print("  Key Signals: {len(summary['key_signals'])}")


if __name__ == "__main__":
    main()
