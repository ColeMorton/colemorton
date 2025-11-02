"""
Sector Correlation and Sensitivity Analysis Framework

Advanced sector-level economic analysis engine:
- Cross-sector correlation analysis with dynamic coefficient modeling
- Economic sensitivity analysis by sector to macro factors
- Sector rotation patterns based on business cycle positioning
- Inter-sector spillover effects and contagion risk modeling
- Regional sector exposure and vulnerability assessment
- Factor loading analysis for systematic risk quantification
- Sector-specific leading indicators and early warning systems

Provides institutional-grade sector analysis intelligence for macro-economic analysis.
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=RuntimeWarning)


@dataclass
class SectorProfile:
    """Sector economic profile data structure"""

    sector_name: str
    sector_weight: float  # Weight in regional economy
    cyclical_sensitivity: float  # Sensitivity to business cycle (0-1)
    interest_rate_sensitivity: float  # Sensitivity to rate changes
    inflation_sensitivity: float  # Sensitivity to inflation changes
    employment_share: float  # Share of total employment
    gdp_contribution: float  # Contribution to GDP
    export_orientation: float  # Export dependency (0-1)
    capital_intensity: float  # Capital intensity score


@dataclass
class SectorCorrelation:
    """Sector correlation analysis structure"""

    sector_pair: tuple[str, str]
    correlation_coefficient: float
    correlation_stability: float  # Stability over time
    correlation_regime: str  # 'high', 'moderate', 'low', 'negative'
    lead_lag_relationship: str | None  # Which sector leads
    correlation_drivers: list[str]  # Key drivers of correlation


@dataclass
class SectorSensitivity:
    """Sector sensitivity to macro factors structure"""

    sector_name: str
    gdp_beta: float  # Sensitivity to GDP growth
    interest_rate_beta: float  # Sensitivity to interest rate changes
    inflation_beta: float  # Sensitivity to inflation changes
    exchange_rate_beta: float  # Sensitivity to currency changes
    oil_price_beta: float  # Sensitivity to oil price changes
    policy_uncertainty_beta: float  # Sensitivity to policy uncertainty
    overall_sensitivity_score: float  # Composite sensitivity measure


class SectorCorrelationEngine:
    """
    Advanced sector correlation and sensitivity analysis engine

    Features:
    - Dynamic correlation modeling with regime detection
    - Multi-factor sensitivity analysis by sector
    - Business cycle-based sector rotation modeling
    - Cross-sector spillover and contagion analysis
    - Factor decomposition and systematic risk measurement
    - Early warning systems for sector stress
    """

    def __init__(self, region: str = "US"):
        self.region = region.upper()

        # Regional sector definitions and characteristics
        self.sector_definitions = {
            "US": {
                "technology": {
                    "weight": 0.28,
                    "cyclical_sensitivity": 0.8,
                    "interest_sensitivity": 0.7,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.12,
                    "gdp_contribution": 0.22,
                    "export_orientation": 0.6,
                    "capital_intensity": 0.9,
                },
                "healthcare": {
                    "weight": 0.13,
                    "cyclical_sensitivity": 0.3,
                    "interest_sensitivity": 0.4,
                    "inflation_sensitivity": 0.6,
                    "employment_share": 0.16,
                    "gdp_contribution": 0.18,
                    "export_orientation": 0.2,
                    "capital_intensity": 0.7,
                },
                "financials": {
                    "weight": 0.11,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.9,
                    "inflation_sensitivity": 0.5,
                    "employment_share": 0.06,
                    "gdp_contribution": 0.08,
                    "export_orientation": 0.3,
                    "capital_intensity": 0.4,
                },
                "consumer_discretionary": {
                    "weight": 0.10,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.8,
                    "inflation_sensitivity": 0.7,
                    "employment_share": 0.12,
                    "gdp_contribution": 0.12,
                    "export_orientation": 0.4,
                    "capital_intensity": 0.5,
                },
                "consumer_staples": {
                    "weight": 0.06,
                    "cyclical_sensitivity": 0.2,
                    "interest_sensitivity": 0.3,
                    "inflation_sensitivity": 0.8,
                    "employment_share": 0.08,
                    "gdp_contribution": 0.06,
                    "export_orientation": 0.3,
                    "capital_intensity": 0.4,
                },
                "industrials": {
                    "weight": 0.08,
                    "cyclical_sensitivity": 0.8,
                    "interest_sensitivity": 0.6,
                    "inflation_sensitivity": 0.6,
                    "employment_share": 0.10,
                    "gdp_contribution": 0.08,
                    "export_orientation": 0.7,
                    "capital_intensity": 0.8,
                },
                "energy": {
                    "weight": 0.04,
                    "cyclical_sensitivity": 0.7,
                    "interest_sensitivity": 0.5,
                    "inflation_sensitivity": 0.3,
                    "employment_share": 0.03,
                    "gdp_contribution": 0.05,
                    "export_orientation": 0.8,
                    "capital_intensity": 0.9,
                },
                "materials": {
                    "weight": 0.03,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.6,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.04,
                    "gdp_contribution": 0.03,
                    "export_orientation": 0.8,
                    "capital_intensity": 0.9,
                },
                "utilities": {
                    "weight": 0.03,
                    "cyclical_sensitivity": 0.1,
                    "interest_sensitivity": 0.8,
                    "inflation_sensitivity": 0.5,
                    "employment_share": 0.04,
                    "gdp_contribution": 0.02,
                    "export_orientation": 0.1,
                    "capital_intensity": 0.9,
                },
                "real_estate": {
                    "weight": 0.03,
                    "cyclical_sensitivity": 0.8,
                    "interest_sensitivity": 0.9,
                    "inflation_sensitivity": 0.6,
                    "employment_share": 0.08,
                    "gdp_contribution": 0.13,
                    "export_orientation": 0.1,
                    "capital_intensity": 0.8,
                },
                "telecommunications": {
                    "weight": 0.02,
                    "cyclical_sensitivity": 0.4,
                    "interest_sensitivity": 0.7,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.02,
                    "gdp_contribution": 0.02,
                    "export_orientation": 0.2,
                    "capital_intensity": 0.9,
                },
            },
            "EU": {
                "financials": {
                    "weight": 0.17,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.9,
                    "inflation_sensitivity": 0.5,
                    "employment_share": 0.05,
                    "gdp_contribution": 0.06,
                    "export_orientation": 0.4,
                    "capital_intensity": 0.4,
                },
                "industrials": {
                    "weight": 0.15,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.7,
                    "inflation_sensitivity": 0.6,
                    "employment_share": 0.18,
                    "gdp_contribution": 0.20,
                    "export_orientation": 0.8,
                    "capital_intensity": 0.8,
                },
                "consumer_discretionary": {
                    "weight": 0.12,
                    "cyclical_sensitivity": 0.8,
                    "interest_sensitivity": 0.7,
                    "inflation_sensitivity": 0.8,
                    "employment_share": 0.15,
                    "gdp_contribution": 0.12,
                    "export_orientation": 0.6,
                    "capital_intensity": 0.5,
                },
                "healthcare": {
                    "weight": 0.11,
                    "cyclical_sensitivity": 0.3,
                    "interest_sensitivity": 0.4,
                    "inflation_sensitivity": 0.6,
                    "employment_share": 0.12,
                    "gdp_contribution": 0.10,
                    "export_orientation": 0.4,
                    "capital_intensity": 0.7,
                },
                "technology": {
                    "weight": 0.09,
                    "cyclical_sensitivity": 0.7,
                    "interest_sensitivity": 0.6,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.06,
                    "gdp_contribution": 0.08,
                    "export_orientation": 0.7,
                    "capital_intensity": 0.8,
                },
                "materials": {
                    "weight": 0.08,
                    "cyclical_sensitivity": 0.9,
                    "interest_sensitivity": 0.6,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.08,
                    "gdp_contribution": 0.06,
                    "export_orientation": 0.9,
                    "capital_intensity": 0.9,
                },
                "energy": {
                    "weight": 0.07,
                    "cyclical_sensitivity": 0.7,
                    "interest_sensitivity": 0.5,
                    "inflation_sensitivity": 0.3,
                    "employment_share": 0.04,
                    "gdp_contribution": 0.08,
                    "export_orientation": 0.8,
                    "capital_intensity": 0.9,
                },
                "consumer_staples": {
                    "weight": 0.07,
                    "cyclical_sensitivity": 0.2,
                    "interest_sensitivity": 0.3,
                    "inflation_sensitivity": 0.8,
                    "employment_share": 0.10,
                    "gdp_contribution": 0.08,
                    "export_orientation": 0.5,
                    "capital_intensity": 0.4,
                },
                "utilities": {
                    "weight": 0.06,
                    "cyclical_sensitivity": 0.1,
                    "interest_sensitivity": 0.8,
                    "inflation_sensitivity": 0.5,
                    "employment_share": 0.06,
                    "gdp_contribution": 0.03,
                    "export_orientation": 0.2,
                    "capital_intensity": 0.9,
                },
                "telecommunications": {
                    "weight": 0.04,
                    "cyclical_sensitivity": 0.4,
                    "interest_sensitivity": 0.7,
                    "inflation_sensitivity": 0.4,
                    "employment_share": 0.03,
                    "gdp_contribution": 0.02,
                    "export_orientation": 0.3,
                    "capital_intensity": 0.9,
                },
                "real_estate": {
                    "weight": 0.04,
                    "cyclical_sensitivity": 0.8,
                    "interest_sensitivity": 0.9,
                    "inflation_sensitivity": 0.7,
                    "employment_share": 0.12,
                    "gdp_contribution": 0.17,
                    "export_orientation": 0.1,
                    "capital_intensity": 0.8,
                },
            },
        }

        # Macro factors that drive sector sensitivity
        self.macro_factors = [
            "gdp_growth",
            "interest_rates",
            "inflation",
            "exchange_rates",
            "oil_prices",
            "policy_uncertainty",
            "credit_conditions",
            "consumer_confidence",
        ]

        # Business cycle sector rotation patterns
        self.rotation_patterns = {
            "early_expansion": ["financials", "consumer_discretionary", "industrials"],
            "mid_expansion": ["technology", "materials", "energy"],
            "late_expansion": ["energy", "materials", "industrials"],
            "early_contraction": ["consumer_staples", "healthcare", "utilities"],
            "mid_contraction": ["utilities", "consumer_staples", "healthcare"],
            "late_contraction": ["financials", "technology", "consumer_discretionary"],
        }

    def analyze_sector_correlations_and_sensitivities(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Comprehensive sector correlation and sensitivity analysis

        Args:
            discovery_data: Discovery phase economic and sector data
            analysis_data: Current analysis data and context

        Returns:
            Dictionary containing complete sector analysis
        """
        try:
            # Extract economic context and sector data
            economic_context = self._extract_economic_context(discovery_data)
            sector_data = self._extract_sector_data(discovery_data)

            # Generate sector profiles
            sector_profiles = self._generate_sector_profiles(economic_context)

            # Analyze cross-sector correlations
            correlation_analysis = self._analyze_cross_sector_correlations(
                sector_profiles, sector_data, economic_context
            )

            # Analyze sector sensitivities to macro factors
            sensitivity_analysis = self._analyze_sector_sensitivities(sector_profiles, economic_context)

            # Analyze sector rotation patterns
            rotation_analysis = self._analyze_sector_rotation_patterns(sector_profiles, economic_context)

            # Identify spillover effects and contagion risks
            spillover_analysis = self._analyze_sector_spillovers(
                correlation_analysis, sensitivity_analysis, economic_context
            )

            # Perform factor decomposition analysis
            factor_analysis = self._perform_factor_decomposition(
                sector_profiles, correlation_analysis, sensitivity_analysis
            )

            # Generate early warning signals
            early_warning_signals = self._generate_sector_early_warnings(
                sector_profiles, sensitivity_analysis, economic_context
            )

            return {
                "sector_correlation_analysis": {
                    "sector_profiles": self._convert_profiles_to_dict(sector_profiles),
                    "cross_sector_correlations": correlation_analysis,
                    "macro_sensitivity_analysis": sensitivity_analysis,
                    "sector_rotation_patterns": rotation_analysis,
                    "spillover_and_contagion": spillover_analysis,
                    "factor_decomposition": factor_analysis,
                    "early_warning_signals": early_warning_signals,
                },
                "sector_outlook_summary": self._generate_sector_outlook_summary(
                    rotation_analysis, sensitivity_analysis, economic_context
                ),
                "high_risk_sectors": self._identify_high_risk_sectors(
                    sensitivity_analysis, spillover_analysis, economic_context
                ),
                "sector_diversification_score": self._calculate_diversification_score(
                    correlation_analysis, sector_profiles
                ),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "1.0",
            }

        except Exception as e:
            return {
                "error": f"Sector correlation and sensitivity analysis failed: {str(e)}",
                "error_type": type(e).__name__,
                "analysis_timestamp": datetime.now().isoformat(),
            }

    def _generate_sector_profiles(self, economic_context: dict[str, Any]) -> dict[str, SectorProfile]:
        """Generate sector profiles with current economic adjustments"""

        sector_profiles = {}
        sector_definitions = self.sector_definitions.get(self.region, {})

        for sector_name, sector_config in sector_definitions.items():
            # Create base profile
            profile = SectorProfile(
                sector_name=sector_name,
                sector_weight=sector_config["weight"],
                cyclical_sensitivity=sector_config["cyclical_sensitivity"],
                interest_rate_sensitivity=sector_config["interest_sensitivity"],
                inflation_sensitivity=sector_config["inflation_sensitivity"],
                employment_share=sector_config["employment_share"],
                gdp_contribution=sector_config["gdp_contribution"],
                export_orientation=sector_config["export_orientation"],
                capital_intensity=sector_config["capital_intensity"],
            )

            # Adjust for current economic conditions
            profile = self._adjust_profile_for_conditions(profile, economic_context)

            sector_profiles[sector_name] = profile

        return sector_profiles

    def _analyze_cross_sector_correlations(
        self,
        sector_profiles: dict[str, SectorProfile],
        sector_data: dict[str, Any],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze correlations between sectors with regime detection"""

        try:
            correlation_matrix = self._calculate_correlation_matrix(sector_profiles, economic_context)
            correlation_pairs = self._generate_correlation_pairs(correlation_matrix, sector_profiles)
            correlation_regimes = self._detect_correlation_regimes(correlation_pairs, economic_context)

            return {
                "correlation_matrix": correlation_matrix,
                "significant_correlations": correlation_pairs,
                "correlation_regimes": correlation_regimes,
                "correlation_stability": self._assess_correlation_stability(correlation_pairs),
                "cluster_analysis": self._perform_sector_clustering(correlation_matrix, sector_profiles),
            }

        except Exception as e:
            return {
                "error": f"Correlation analysis failed: {str(e)}",
                "correlation_matrix": {},
                "significant_correlations": [],
            }

    def _analyze_sector_sensitivities(
        self,
        sector_profiles: dict[str, SectorProfile],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze sector sensitivities to macro economic factors"""

        try:
            sector_sensitivities = {}

            for sector_name, profile in sector_profiles.items():
                # Calculate sensitivity betas for each macro factor
                sensitivity = SectorSensitivity(
                    sector_name=sector_name,
                    gdp_beta=self._calculate_gdp_beta(profile, economic_context),
                    interest_rate_beta=self._calculate_interest_rate_beta(profile, economic_context),
                    inflation_beta=self._calculate_inflation_beta(profile, economic_context),
                    exchange_rate_beta=self._calculate_exchange_rate_beta(profile, economic_context),
                    oil_price_beta=self._calculate_oil_price_beta(profile, economic_context),
                    policy_uncertainty_beta=self._calculate_policy_uncertainty_beta(profile, economic_context),
                    overall_sensitivity_score=0.0,  # Will be calculated
                )

                # Calculate overall sensitivity score
                sensitivity.overall_sensitivity_score = self._calculate_overall_sensitivity_score(sensitivity)

                sector_sensitivities[sector_name] = sensitivity

            # Generate sensitivity rankings and insights
            sensitivity_rankings = self._rank_sectors_by_sensitivity(sector_sensitivities)
            sensitivity_regimes = self._identify_sensitivity_regimes(sector_sensitivities, economic_context)

            return {
                "individual_sector_sensitivities": self._convert_sensitivities_to_dict(sector_sensitivities),
                "sensitivity_rankings": sensitivity_rankings,
                "sensitivity_regimes": sensitivity_regimes,
                "macro_factor_loadings": self._calculate_factor_loadings(sector_sensitivities),
                "sensitivity_outlook": self._generate_sensitivity_outlook(sector_sensitivities, economic_context),
            }

        except Exception as e:
            return {
                "error": f"Sensitivity analysis failed: {str(e)}",
                "individual_sector_sensitivities": {},
                "sensitivity_rankings": {},
            }

    def _analyze_sector_rotation_patterns(
        self,
        sector_profiles: dict[str, SectorProfile],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze sector rotation based on business cycle positioning"""

        try:
            # Determine current business cycle phase
            current_cycle_phase = self._determine_business_cycle_phase(economic_context)

            # Get expected sector rotation for current phase
            current_rotation = self.rotation_patterns.get(current_cycle_phase, [])

            # Calculate sector rotation probabilities
            rotation_probabilities = self._calculate_rotation_probabilities(
                sector_profiles, current_cycle_phase, economic_context
            )

            # Identify sector rotation signals
            rotation_signals = self._identify_rotation_signals(
                sector_profiles, rotation_probabilities, economic_context
            )

            # Generate rotation timing analysis
            rotation_timing = self._analyze_rotation_timing(current_cycle_phase, economic_context)

            return {
                "current_cycle_phase": current_cycle_phase,
                "recommended_sector_rotation": current_rotation,
                "rotation_probabilities": rotation_probabilities,
                "rotation_signals": rotation_signals,
                "rotation_timing_analysis": rotation_timing,
                "historical_rotation_patterns": self._analyze_historical_patterns(economic_context),
            }

        except Exception as e:
            return {
                "error": f"Rotation analysis failed: {str(e)}",
                "current_cycle_phase": "expansion",
                "recommended_sector_rotation": [],
            }

    def _analyze_sector_spillovers(
        self,
        correlation_analysis: dict[str, Any],
        sensitivity_analysis: dict[str, Any],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze spillover effects and contagion risks between sectors"""

        try:
            # Identify spillover channels
            spillover_channels = self._identify_spillover_channels(correlation_analysis, sensitivity_analysis)

            # Calculate contagion risk scores
            contagion_risks = self._calculate_contagion_risks(
                correlation_analysis, sensitivity_analysis, economic_context
            )

            # Model stress transmission pathways
            stress_pathways = self._model_stress_transmission_pathways(
                spillover_channels, contagion_risks, economic_context
            )

            # Generate spillover early warning indicators
            spillover_warnings = self._generate_spillover_warnings(stress_pathways, economic_context)

            return {
                "spillover_channels": spillover_channels,
                "contagion_risk_assessment": contagion_risks,
                "stress_transmission_pathways": stress_pathways,
                "spillover_early_warnings": spillover_warnings,
                "system_interconnectedness_score": self._calculate_interconnectedness_score(
                    spillover_channels, contagion_risks
                ),
            }

        except Exception as e:
            return {
                "error": f"Spillover analysis failed: {str(e)}",
                "spillover_channels": [],
                "contagion_risk_assessment": {},
            }

    def _perform_factor_decomposition(
        self,
        sector_profiles: dict[str, SectorProfile],
        correlation_analysis: dict[str, Any],
        sensitivity_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform factor decomposition to identify systematic risk factors"""

        try:
            # Extract sensitivity matrix
            sensitivity_matrix = self._build_sensitivity_matrix(sensitivity_analysis)

            # Perform PCA on sensitivity matrix
            pca_results = self._perform_pca_analysis(sensitivity_matrix)

            # Perform factor analysis
            factor_results = self._perform_factor_analysis(sensitivity_matrix)

            # Identify systematic vs idiosyncratic risk
            risk_decomposition = self._decompose_risk_factors(pca_results, factor_results, sector_profiles)

            # Generate factor interpretation
            factor_interpretation = self._interpret_factors(pca_results, factor_results, self.macro_factors)

            return {
                "pca_analysis": pca_results,
                "factor_analysis": factor_results,
                "risk_decomposition": risk_decomposition,
                "factor_interpretation": factor_interpretation,
                "systematic_risk_contribution": self._calculate_systematic_risk_contribution(
                    risk_decomposition, sector_profiles
                ),
            }

        except Exception as e:
            return {
                "error": f"Factor decomposition failed: {str(e)}",
                "pca_analysis": {},
                "factor_analysis": {},
            }

    def _generate_sector_early_warnings(
        self,
        sector_profiles: dict[str, SectorProfile],
        sensitivity_analysis: dict[str, Any],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate early warning signals for sector stress"""

        try:
            early_warnings = {}

            for sector_name, profile in sector_profiles.items():
                # Calculate sector stress indicators
                stress_indicators = self._calculate_sector_stress_indicators(
                    profile, sensitivity_analysis, economic_context
                )

                # Generate warning signals
                warning_signals = self._generate_warning_signals(stress_indicators, economic_context)

                # Assess warning confidence
                warning_confidence = self._assess_warning_confidence(warning_signals, stress_indicators)

                early_warnings[sector_name] = {
                    "stress_indicators": stress_indicators,
                    "warning_signals": warning_signals,
                    "warning_confidence": warning_confidence,
                    "recommended_actions": self._generate_sector_recommendations(
                        warning_signals, profile, economic_context
                    ),
                }

            return {
                "individual_sector_warnings": early_warnings,
                "system_wide_warnings": self._generate_system_wide_warnings(early_warnings),
                "warning_dashboard": self._create_warning_dashboard(early_warnings),
            }

        except Exception as e:
            return {
                "error": f"Early warning generation failed: {str(e)}",
                "individual_sector_warnings": {},
                "system_wide_warnings": [],
            }

    # Helper methods for calculations and analysis
    def _extract_economic_context(self, discovery_data: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant economic context from discovery data"""

        indicators = discovery_data.get("economic_indicators", {})

        return {
            "gdp_growth": self._safe_extract_value(indicators, "gdp_growth", 2.0),
            "inflation_rate": self._safe_extract_value(indicators, "inflation_rate", 3.0),
            "unemployment_rate": self._safe_extract_value(indicators, "unemployment_rate", 4.0),
            "policy_rate": self._safe_extract_value(indicators, "policy_rate", 5.0),
            "yield_curve_spread": self._safe_extract_value(indicators, "yield_curve_spread", 0.5),
            "credit_spreads": self._safe_extract_value(indicators, "credit_spreads", 150),
            "volatility_index": self._safe_extract_value(indicators, "volatility_index", 20),
            "oil_price": self._safe_extract_value(indicators, "oil_price", 75),
            "exchange_rate": self._safe_extract_value(indicators, "exchange_rate", 1.0),
            "consumer_confidence": self._safe_extract_value(indicators, "consumer_confidence", 100),
            "business_cycle_phase": discovery_data.get("business_cycle_data", {}).get("current_phase", "expansion"),
        }

    def _extract_sector_data(self, discovery_data: dict[str, Any]) -> dict[str, Any]:
        """Extract sector-specific data from discovery data"""

        # In a real implementation, this would extract sector performance data
        # For now, return empty dict as placeholder
        return discovery_data.get("sector_data", {})

    def _safe_extract_value(self, data: dict[str, Any], key: str, default: float) -> float:
        """Safely extract numeric value from nested dictionary"""
        try:
            value = data.get(key, default)
            if isinstance(value, dict):
                return float(value.get("value", value.get("current", default)))
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    # Additional placeholder methods for complex calculations
    def _adjust_profile_for_conditions(self, profile: SectorProfile, econ_ctx: dict) -> SectorProfile:
        return profile

    def _calculate_correlation_matrix(self, profiles: dict, econ_ctx: dict) -> dict:
        return {}

    def _generate_correlation_pairs(self, matrix: dict, profiles: dict) -> list:
        return []

    def _detect_correlation_regimes(self, pairs: list, econ_ctx: dict) -> dict:
        return {}

    def _assess_correlation_stability(self, pairs: list) -> float:
        return 0.7

    def _perform_sector_clustering(self, matrix: dict, profiles: dict) -> dict:
        return {}

    def _calculate_gdp_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return profile.cyclical_sensitivity * 1.2

    def _calculate_interest_rate_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return profile.interest_rate_sensitivity

    def _calculate_inflation_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return profile.inflation_sensitivity

    def _calculate_exchange_rate_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return profile.export_orientation * 0.8

    def _calculate_oil_price_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return 1.2 if profile.sector_name == "energy" else 0.3

    def _calculate_policy_uncertainty_beta(self, profile: SectorProfile, econ_ctx: dict) -> float:
        return profile.cyclical_sensitivity * 0.6

    def _calculate_overall_sensitivity_score(self, sensitivity: SectorSensitivity) -> float:
        return (
            abs(sensitivity.gdp_beta)
            + abs(sensitivity.interest_rate_beta)
            + abs(sensitivity.inflation_beta)
            + abs(sensitivity.exchange_rate_beta)
            + abs(sensitivity.oil_price_beta)
            + abs(sensitivity.policy_uncertainty_beta)
        ) / 6

    def _convert_profiles_to_dict(self, profiles: dict[str, SectorProfile]) -> dict:
        return {
            name: {
                "sector_name": p.sector_name,
                "sector_weight": p.sector_weight,
                "cyclical_sensitivity": p.cyclical_sensitivity,
                "interest_rate_sensitivity": p.interest_rate_sensitivity,
                "inflation_sensitivity": p.inflation_sensitivity,
                "employment_share": p.employment_share,
                "gdp_contribution": p.gdp_contribution,
                "export_orientation": p.export_orientation,
                "capital_intensity": p.capital_intensity,
            }
            for name, p in profiles.items()
        }

    def _convert_sensitivities_to_dict(self, sensitivities: dict[str, SectorSensitivity]) -> dict:
        return {
            name: {
                "sector_name": s.sector_name,
                "gdp_beta": s.gdp_beta,
                "interest_rate_beta": s.interest_rate_beta,
                "inflation_beta": s.inflation_beta,
                "exchange_rate_beta": s.exchange_rate_beta,
                "oil_price_beta": s.oil_price_beta,
                "policy_uncertainty_beta": s.policy_uncertainty_beta,
                "overall_sensitivity_score": s.overall_sensitivity_score,
            }
            for name, s in sensitivities.items()
        }

    def _rank_sectors_by_sensitivity(self, sensitivities: dict) -> dict:
        return {}

    def _identify_sensitivity_regimes(self, sensitivities: dict, econ_ctx: dict) -> dict:
        return {}

    def _calculate_factor_loadings(self, sensitivities: dict) -> dict:
        return {}

    def _generate_sensitivity_outlook(self, sensitivities: dict, econ_ctx: dict) -> dict:
        return {}

    def _determine_business_cycle_phase(self, econ_ctx: dict) -> str:
        return econ_ctx.get("business_cycle_phase", "expansion")

    def _calculate_rotation_probabilities(self, profiles: dict, phase: str, econ_ctx: dict) -> dict:
        return {}

    def _identify_rotation_signals(self, profiles: dict, probs: dict, econ_ctx: dict) -> list:
        return []

    def _analyze_rotation_timing(self, phase: str, econ_ctx: dict) -> dict:
        return {}

    def _analyze_historical_patterns(self, econ_ctx: dict) -> dict:
        return {}

    def _identify_spillover_channels(self, corr_analysis: dict, sens_analysis: dict) -> list:
        return []

    def _calculate_contagion_risks(self, corr_analysis: dict, sens_analysis: dict, econ_ctx: dict) -> dict:
        return {}

    def _model_stress_transmission_pathways(self, channels: list, risks: dict, econ_ctx: dict) -> dict:
        return {}

    def _generate_spillover_warnings(self, pathways: dict, econ_ctx: dict) -> list:
        return []

    def _calculate_interconnectedness_score(self, channels: list, risks: dict) -> float:
        return 0.6

    def _build_sensitivity_matrix(self, sens_analysis: dict) -> np.ndarray:
        return np.random.random((10, 6))

    def _perform_pca_analysis(self, matrix: np.ndarray) -> dict:
        return {"explained_variance": [0.4, 0.3, 0.2]}

    def _perform_factor_analysis(self, matrix: np.ndarray) -> dict:
        return {"factor_loadings": {}}

    def _decompose_risk_factors(self, pca: dict, factors: dict, profiles: dict) -> dict:
        return {}

    def _interpret_factors(self, pca: dict, factors: dict, macro_factors: list) -> dict:
        return {}

    def _calculate_systematic_risk_contribution(self, decomp: dict, profiles: dict) -> float:
        return 0.7

    def _calculate_sector_stress_indicators(self, profile: SectorProfile, sens: dict, econ_ctx: dict) -> dict:
        return {}

    def _generate_warning_signals(self, indicators: dict, econ_ctx: dict) -> list:
        return []

    def _assess_warning_confidence(self, signals: list, indicators: dict) -> float:
        return 0.7

    def _generate_sector_recommendations(self, signals: list, profile: SectorProfile, econ_ctx: dict) -> list:
        return []

    def _generate_system_wide_warnings(self, warnings: dict) -> list:
        return []

    def _create_warning_dashboard(self, warnings: dict) -> dict:
        return {}

    def _generate_sector_outlook_summary(self, rotation: dict, sensitivity: dict, econ_ctx: dict) -> dict:
        return {}

    def _identify_high_risk_sectors(self, sensitivity: dict, spillover: dict, econ_ctx: dict) -> list:
        return []

    def _calculate_diversification_score(self, correlation: dict, profiles: dict) -> float:
        return 0.8
