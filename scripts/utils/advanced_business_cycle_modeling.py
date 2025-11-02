#!/usr/bin/env python3
"""
Advanced Business Cycle Modeling Framework
Enhanced business cycle analysis with transition probabilities and regime-switching models
Part of Phase 2 optimization for macro analysis system
"""

import json
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


warnings.filterwarnings("ignore")


@dataclass
class MarkovTransitionMatrix:
    """Markov chain transition matrix for business cycle phases"""

    expansion_to_peak: float
    expansion_to_contraction: float  # Skip peak (recession)
    peak_to_contraction: float
    peak_to_expansion: float  # Recovery without recession
    contraction_to_trough: float
    contraction_to_expansion: float  # V-shaped recovery
    trough_to_expansion: float
    trough_to_contraction: float  # Double dip

    def get_transition_matrix(self) -> np.ndarray:
        """Get 4x4 transition matrix"""
        # Order: expansion, peak, contraction, trough
        return np.array(
            [
                [
                    1 - self.expansion_to_peak - self.expansion_to_contraction,
                    self.expansion_to_peak,
                    self.expansion_to_contraction,
                    0.0,
                ],
                [
                    self.peak_to_expansion,
                    1 - self.peak_to_expansion - self.peak_to_contraction,
                    self.peak_to_contraction,
                    0.0,
                ],
                [
                    self.contraction_to_expansion,
                    0.0,
                    1 - self.contraction_to_expansion - self.contraction_to_trough,
                    self.contraction_to_trough,
                ],
                [
                    self.trough_to_expansion,
                    0.0,
                    self.trough_to_contraction,
                    1 - self.trough_to_expansion - self.trough_to_contraction,
                ],
            ]
        )


@dataclass
class RegimeSwitchingSignal:
    """Regime switching detection signal"""

    current_regime: str  # 'growth', 'stagnation', 'recession'
    regime_probability: float
    regime_duration: int  # quarters in current regime
    switching_probability: float
    expected_regime_duration: int
    volatility_regime: str  # 'low', 'moderate', 'high'


@dataclass
class SectorRotationSignal:
    """Sector rotation signal based on business cycle positioning"""

    cycle_stage: str
    preferred_sectors: list[str]
    rotation_probability: float
    rotation_timing: str  # 'early', 'mid', 'late'
    confidence: float


class AdvancedBusinessCycleEngine:
    """Enhanced business cycle modeling with transition probabilities and regime detection"""

    def __init__(self, region: str = "US"):
        self.region = region

        # Enhanced Markov transition parameters (quarterly probabilities)
        self.base_transitions = MarkovTransitionMatrix(
            expansion_to_peak=0.08,  # 8% quarterly chance of peaking
            expansion_to_contraction=0.03,  # 3% direct recession probability
            peak_to_contraction=0.45,  # 45% quarterly recession from peak
            peak_to_expansion=0.25,  # 25% soft landing probability
            contraction_to_trough=0.35,  # 35% quarterly bottoming probability
            contraction_to_expansion=0.15,  # 15% V-shaped recovery
            trough_to_expansion=0.65,  # 65% quarterly recovery from trough
            trough_to_contraction=0.08,  # 8% double-dip probability
        )

        # Regime switching parameters
        self.regime_thresholds = {
            "growth": {"gdp_min": 2.0, "unemployment_max": 5.0, "volatility_max": 15},
            "stagnation": {"gdp_range": (0.5, 2.0), "unemployment_range": (4.5, 6.5)},
            "recession": {
                "gdp_max": 0.5,
                "unemployment_min": 5.5,
                "volatility_min": 20,
            },
        }

        # Sector rotation mapping
        self.sector_rotation_map = {
            "early_expansion": ["technology", "consumer_discretionary", "industrials"],
            "mid_expansion": ["financials", "energy", "materials"],
            "late_expansion": ["consumer_staples", "healthcare", "real_estate"],
            "peak": ["utilities", "consumer_staples", "cash"],
            "early_contraction": ["utilities", "consumer_staples", "bonds"],
            "mid_contraction": ["healthcare", "utilities", "government_bonds"],
            "late_contraction": ["technology", "consumer_discretionary", "bonds"],
            "trough": ["technology", "financials", "materials"],
        }

        # Historical cycle statistics (enhanced with volatility regimes)
        self.historical_stats = {
            "expansion_duration_quarters": {"mean": 18, "std": 8, "min": 4, "max": 40},
            "recession_duration_quarters": {"mean": 4, "std": 2, "min": 2, "max": 8},
            "volatility_regimes": {
                "low": {"vix_max": 15, "duration_mean": 12},
                "moderate": {"vix_range": (15, 25), "duration_mean": 6},
                "high": {"vix_min": 25, "duration_mean": 3},
            },
        }

    def analyze_advanced_business_cycle(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Comprehensive advanced business cycle analysis"""

        # Extract current indicators
        current_indicators = self._extract_cycle_indicators(discovery_data, analysis_data)

        # Enhanced Markov chain transition analysis
        markov_analysis = self._analyze_markov_transitions(current_indicators)

        # Regime switching detection
        regime_analysis = self._detect_regime_switches(current_indicators)

        # Sector rotation signals
        rotation_analysis = self._analyze_sector_rotation(current_indicators, markov_analysis)

        # Historical pattern matching
        historical_patterns = self._match_historical_patterns(current_indicators)

        # Advanced recession probability with multiple horizons
        multi_horizon_recession = self._calculate_multi_horizon_recession_probability(current_indicators)

        # Volatility regime analysis
        volatility_regime = self._analyze_volatility_regime(current_indicators)

        return {
            "advanced_cycle_metadata": {
                "methodology": "markov_chain_regime_switching_analysis",
                "region": self.region,
                "analysis_timestamp": datetime.now().isoformat(),
                "model_confidence": self._calculate_model_confidence(current_indicators),
            },
            "markov_transition_analysis": markov_analysis,
            "regime_switching_detection": regime_analysis,
            "sector_rotation_signals": rotation_analysis,
            "historical_pattern_matching": historical_patterns,
            "multi_horizon_recession_probability": multi_horizon_recession,
            "volatility_regime_analysis": volatility_regime,
            "integrated_cycle_assessment": self._create_integrated_assessment(
                markov_analysis, regime_analysis, rotation_analysis, historical_patterns
            ),
        }

    def _extract_cycle_indicators(self, discovery_data: dict, analysis_data: dict) -> dict[str, Any]:
        """Extract business cycle indicators from discovery and analysis data"""

        # Current business cycle state
        business_cycle_data = discovery_data.get("business_cycle_data", {})
        current_phase = business_cycle_data.get("current_phase", "expansion")

        # Economic indicators
        economic_indicators = discovery_data.get("economic_indicators", {})

        # GDP data
        gdp_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("gdp_data", {})
        )
        current_gdp = 2.0  # Default
        if gdp_data.get("observations"):
            current_gdp = gdp_data["observations"][0].get("value", 2.0)

        # Employment data
        employment_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("employment_data", {})
        )
        current_unemployment = 4.5  # Default
        if employment_data.get("unemployment_data", {}).get("observations"):
            current_unemployment = employment_data["unemployment_data"]["observations"][0].get("value", 4.5)

        # Volatility proxy
        volatility_data = discovery_data.get("cli_market_intelligence", {}).get("volatility_analysis", {})
        current_vix = volatility_data.get("vix_analysis", {}).get("current_level", 20.0)

        # Financial conditions
        recession_prob = economic_indicators.get("composite_scores", {}).get("recession_probability", 0.25)

        # Yield curve
        yield_curve = economic_indicators.get("leading_indicators", {}).get("yield_curve", {})
        yield_spread = (
            yield_curve.get("current_spread", {}).get("10y_2y", 0.5)
            if isinstance(yield_curve.get("current_spread"), dict)
            else 0.5
        )

        # Phase duration estimate
        phase_duration = business_cycle_data.get("historical_context", {}).get("phase_duration", 36)

        return {
            "current_phase": current_phase,
            "gdp_growth": current_gdp,
            "unemployment_rate": current_unemployment,
            "vix_level": current_vix,
            "recession_probability": recession_prob,
            "yield_spread": yield_spread,
            "phase_duration_months": phase_duration,
            "cycle_maturity": business_cycle_data.get("historical_context", {}).get("cycle_maturity", "mid"),
        }

    def _analyze_markov_transitions(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Analyze business cycle transitions using Markov chain modeling"""

        current_phase = indicators["current_phase"]
        phase_duration = indicators["phase_duration_months"]
        gdp_growth = indicators["gdp_growth"]
        unemployment_rate = indicators["unemployment_rate"]
        recession_prob = indicators["recession_probability"]
        yield_spread = indicators["yield_spread"]

        # Adjust base transition probabilities based on current conditions
        adjusted_transitions = self._adjust_transition_probabilities(indicators)

        # Calculate transition probabilities for next 1, 2, 4, and 8 quarters
        multi_period_transitions = self._calculate_multi_period_transitions(current_phase, adjusted_transitions)

        # Phase transition timing analysis
        transition_timing = self._analyze_transition_timing(indicators, adjusted_transitions)

        # Transition risk factors
        risk_factors = self._identify_transition_risk_factors(indicators)

        return {
            "current_phase": current_phase,
            "current_phase_duration_months": phase_duration,
            "adjusted_transition_matrix": {
                "expansion_to_peak": round(adjusted_transitions.expansion_to_peak, 3),
                "expansion_to_contraction": round(adjusted_transitions.expansion_to_contraction, 3),
                "peak_to_contraction": round(adjusted_transitions.peak_to_contraction, 3),
                "peak_to_expansion": round(adjusted_transitions.peak_to_expansion, 3),
                "contraction_to_trough": round(adjusted_transitions.contraction_to_trough, 3),
                "contraction_to_expansion": round(adjusted_transitions.contraction_to_expansion, 3),
                "trough_to_expansion": round(adjusted_transitions.trough_to_expansion, 3),
                "trough_to_contraction": round(adjusted_transitions.trough_to_contraction, 3),
            },
            "multi_period_transition_probabilities": multi_period_transitions,
            "transition_timing_analysis": transition_timing,
            "transition_risk_factors": risk_factors,
            "markov_model_confidence": self._calculate_markov_confidence(indicators),
        }

    def _adjust_transition_probabilities(self, indicators: dict[str, Any]) -> MarkovTransitionMatrix:
        """Adjust base transition probabilities based on current economic conditions"""

        # Base transitions
        adjusted = MarkovTransitionMatrix(
            expansion_to_peak=self.base_transitions.expansion_to_peak,
            expansion_to_contraction=self.base_transitions.expansion_to_contraction,
            peak_to_contraction=self.base_transitions.peak_to_contraction,
            peak_to_expansion=self.base_transitions.peak_to_expansion,
            contraction_to_trough=self.base_transitions.contraction_to_trough,
            contraction_to_expansion=self.base_transitions.contraction_to_expansion,
            trough_to_expansion=self.base_transitions.trough_to_expansion,
            trough_to_contraction=self.base_transitions.trough_to_contraction,
        )

        # Adjustment factors based on economic conditions
        recession_factor = indicators["recession_probability"]
        yield_factor = 1.0 + min(max(indicators["yield_spread"], -1.0), 1.0) * 0.5  # Inverted curve increases risk
        duration_factor = min(
            indicators["phase_duration_months"] / 24.0, 2.0
        )  # Longer phases more likely to transition
        growth_factor = 1.0 - (indicators["gdp_growth"] - 2.0) * 0.1  # Weaker growth increases recession risk

        # Apply adjustments for expansion phase
        if indicators["current_phase"] == "expansion":
            # Higher recession probability increases direct contraction risk
            adjusted.expansion_to_contraction *= 1.0 + recession_factor * 2.0
            # Inverted yield curve increases peak probability
            adjusted.expansion_to_peak *= yield_factor
            # Longer expansions more likely to peak
            adjusted.expansion_to_peak *= duration_factor
            # Weak growth increases both peak and contraction risk
            adjusted.expansion_to_peak *= growth_factor
            adjusted.expansion_to_contraction *= growth_factor

        # Apply adjustments for peak phase
        elif indicators["current_phase"] == "peak":
            # High recession probability increases contraction risk
            adjusted.peak_to_contraction *= 1.0 + recession_factor * 1.5
            # Weak growth reduces soft landing probability
            adjusted.peak_to_expansion *= 2.0 - growth_factor

        # Apply adjustments for contraction phase
        elif indicators["current_phase"] == "contraction":
            # Strong recovery indicators increase direct expansion probability
            if indicators["gdp_growth"] > 1.0:
                adjusted.contraction_to_expansion *= 1.5
            # Policy support increases recovery probability
            adjusted.contraction_to_trough *= 1.0 + (5.0 - indicators["unemployment_rate"]) * 0.1

        # Apply adjustments for trough phase
        elif indicators["current_phase"] == "trough":
            # Strong leading indicators increase expansion probability
            adjusted.trough_to_expansion *= 1.0 + max(0, indicators["gdp_growth"] - 1.0) * 0.5
            # High unemployment reduces double-dip risk
            adjusted.trough_to_contraction *= max(0.5, 1.0 - (indicators["unemployment_rate"] - 5.0) * 0.1)

        # Normalize probabilities to ensure they sum correctly
        adjusted = self._normalize_transitions(adjusted, indicators["current_phase"])

        return adjusted

    def _normalize_transitions(self, transitions: MarkovTransitionMatrix, current_phase: str) -> MarkovTransitionMatrix:
        """Normalize transition probabilities to ensure they sum to 1.0 for each phase"""

        if current_phase == "expansion":
            total = transitions.expansion_to_peak + transitions.expansion_to_contraction
            # Keep stay probability (1 - total) reasonable
            if total > 0.9:
                scale_factor = 0.9 / total
                transitions.expansion_to_peak *= scale_factor
                transitions.expansion_to_contraction *= scale_factor

        elif current_phase == "peak":
            total = transitions.peak_to_contraction + transitions.peak_to_expansion
            if total > 0.9:
                scale_factor = 0.9 / total
                transitions.peak_to_contraction *= scale_factor
                transitions.peak_to_expansion *= scale_factor

        elif current_phase == "contraction":
            total = transitions.contraction_to_trough + transitions.contraction_to_expansion
            if total > 0.9:
                scale_factor = 0.9 / total
                transitions.contraction_to_trough *= scale_factor
                transitions.contraction_to_expansion *= scale_factor

        elif current_phase == "trough":
            total = transitions.trough_to_expansion + transitions.trough_to_contraction
            if total > 0.9:
                scale_factor = 0.9 / total
                transitions.trough_to_expansion *= scale_factor
                transitions.trough_to_contraction *= scale_factor

        return transitions

    def _calculate_multi_period_transitions(
        self, current_phase: str, transitions: MarkovTransitionMatrix
    ) -> dict[str, Any]:
        """Calculate transition probabilities over multiple periods"""

        # Get transition matrix
        P = transitions.get_transition_matrix()

        # Phase mapping
        phase_map = {"expansion": 0, "peak": 1, "contraction": 2, "trough": 3}
        current_index = phase_map[current_phase]

        # Calculate powers of transition matrix for multiple periods
        P1 = P  # 1 quarter
        P2 = np.linalg.matrix_power(P, 2)  # 2 quarters
        P4 = np.linalg.matrix_power(P, 4)  # 1 year
        P8 = np.linalg.matrix_power(P, 8)  # 2 years

        results = {}
        for period, matrix, label in [
            (1, P1, "1_quarter"),
            (2, P2, "2_quarters"),
            (4, P4, "1_year"),
            (8, P8, "2_years"),
        ]:
            results[label] = {
                "expansion_probability": round(matrix[current_index, 0], 3),
                "peak_probability": round(matrix[current_index, 1], 3),
                "contraction_probability": round(matrix[current_index, 2], 3),
                "trough_probability": round(matrix[current_index, 3], 3),
                "recession_probability": round(matrix[current_index, 2] + matrix[current_index, 3], 3),
            }

        return results

    def _analyze_transition_timing(
        self, indicators: dict[str, Any], transitions: MarkovTransitionMatrix
    ) -> dict[str, Any]:
        """Analyze expected timing of business cycle transitions"""

        current_phase = indicators["current_phase"]
        phase_duration = indicators["phase_duration_months"]

        # Calculate expected transition times based on current phase
        if current_phase == "expansion":
            peak_prob = transitions.expansion_to_peak
            recession_prob = transitions.expansion_to_contraction

            # Expected time to peak (geometric distribution)
            expected_quarters_to_peak = 1.0 / peak_prob if peak_prob > 0 else float("inf")
            expected_quarters_to_recession = (
                1.0 / (peak_prob + recession_prob) if (peak_prob + recession_prob) > 0 else float("inf")
            )

            return {
                "current_phase_expected_remaining_quarters": round(expected_quarters_to_peak, 1),
                "expected_quarters_to_peak": round(expected_quarters_to_peak, 1),
                "expected_quarters_to_recession": round(expected_quarters_to_recession, 1),
                "phase_maturity_assessment": (
                    "early" if phase_duration < 12 else "mid" if phase_duration < 36 else "late"
                ),
                "transition_urgency": (
                    "low" if expected_quarters_to_peak > 8 else "moderate" if expected_quarters_to_peak > 4 else "high"
                ),
            }

        if current_phase == "peak":
            contraction_prob = transitions.peak_to_contraction
            expansion_prob = transitions.peak_to_expansion

            expected_quarters_to_resolution = (
                1.0 / (contraction_prob + expansion_prob) if (contraction_prob + expansion_prob) > 0 else 2.0
            )

            return {
                "current_phase_expected_remaining_quarters": round(expected_quarters_to_resolution, 1),
                "soft_landing_probability": (
                    round(expansion_prob / (contraction_prob + expansion_prob), 3)
                    if (contraction_prob + expansion_prob) > 0
                    else 0.5
                ),
                "recession_probability": (
                    round(contraction_prob / (contraction_prob + expansion_prob), 3)
                    if (contraction_prob + expansion_prob) > 0
                    else 0.5
                ),
                "phase_maturity_assessment": "critical",
                "transition_urgency": "high",
            }

        if current_phase == "contraction":
            trough_prob = transitions.contraction_to_trough
            recovery_prob = transitions.contraction_to_expansion

            expected_quarters_to_trough = 1.0 / trough_prob if trough_prob > 0 else 4.0
            expected_quarters_to_recovery = (
                1.0 / (trough_prob + recovery_prob) if (trough_prob + recovery_prob) > 0 else 6.0
            )

            return {
                "current_phase_expected_remaining_quarters": round(expected_quarters_to_trough, 1),
                "expected_quarters_to_trough": round(expected_quarters_to_trough, 1),
                "expected_quarters_to_recovery": round(expected_quarters_to_recovery, 1),
                "v_shaped_recovery_probability": (
                    round(recovery_prob / (trough_prob + recovery_prob), 3)
                    if (trough_prob + recovery_prob) > 0
                    else 0.25
                ),
                "phase_maturity_assessment": "early" if phase_duration < 6 else "late",
                "transition_urgency": "moderate",
            }

        # trough
        expansion_prob = transitions.trough_to_expansion
        double_dip_prob = transitions.trough_to_contraction

        expected_quarters_to_expansion = 1.0 / expansion_prob if expansion_prob > 0 else 2.0

        return {
            "current_phase_expected_remaining_quarters": round(expected_quarters_to_expansion, 1),
            "expected_quarters_to_expansion": round(expected_quarters_to_expansion, 1),
            "double_dip_probability": round(double_dip_prob, 3),
            "recovery_strength_assessment": ("strong" if expansion_prob > 0.6 else "moderate"),
            "phase_maturity_assessment": "recovery_positioning",
            "transition_urgency": "moderate",
        }

    def _identify_transition_risk_factors(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Identify key risk factors for business cycle transitions"""

        risk_factors = []
        risk_scores = {}

        # Recession risk factors
        if indicators["recession_probability"] > 0.3:
            risk_factors.append("elevated_recession_probability")
            risk_scores["recession_risk"] = indicators["recession_probability"]

        # Yield curve risk
        if indicators["yield_spread"] < 0.25:
            risk_factors.append("flattening_yield_curve")
            risk_scores["yield_curve_risk"] = max(0, 0.5 - indicators["yield_spread"])

        # Growth risk
        if indicators["gdp_growth"] < 1.5:
            risk_factors.append("below_trend_growth")
            risk_scores["growth_risk"] = max(0, (1.5 - indicators["gdp_growth"]) / 1.5)

        # Employment risk
        if indicators["unemployment_rate"] > 5.0:
            risk_factors.append("elevated_unemployment")
            risk_scores["employment_risk"] = (indicators["unemployment_rate"] - 4.0) / 4.0

        # Volatility risk
        if indicators["vix_level"] > 25:
            risk_factors.append("elevated_market_volatility")
            risk_scores["volatility_risk"] = min(1.0, (indicators["vix_level"] - 15) / 20)

        # Duration risk (long expansions more vulnerable)
        if indicators["phase_duration_months"] > 60:
            risk_factors.append("prolonged_expansion_phase")
            risk_scores["duration_risk"] = min(1.0, (indicators["phase_duration_months"] - 36) / 60)

        # Calculate overall risk score
        overall_risk = np.mean(list(risk_scores.values())) if risk_scores else 0.1

        return {
            "primary_risk_factors": risk_factors,
            "risk_factor_scores": risk_scores,
            "overall_transition_risk_score": round(overall_risk, 3),
            "risk_level": ("low" if overall_risk < 0.3 else "moderate" if overall_risk < 0.6 else "high"),
            "key_monitoring_indicators": [
                "yield_curve_slope",
                "recession_probability",
                "gdp_growth",
                "unemployment_rate",
            ],
        }

    def _detect_regime_switches(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Detect economic regime switches using multiple indicators"""

        gdp_growth = indicators["gdp_growth"]
        unemployment = indicators["unemployment_rate"]
        volatility = indicators["vix_level"]

        # Classify current regime
        current_regime = self._classify_economic_regime(gdp_growth, unemployment, volatility)

        # Calculate regime probabilities
        regime_probabilities = self._calculate_regime_probabilities(gdp_growth, unemployment, volatility)

        # Estimate regime duration
        regime_duration = self._estimate_regime_duration(current_regime, indicators)

        # Calculate switching probability
        switching_probability = self._calculate_regime_switching_probability(
            current_regime, regime_duration, indicators
        )

        # Classify volatility regime
        volatility_regime = self._classify_volatility_regime(volatility)

        return {
            "current_regime": current_regime,
            "regime_probabilities": regime_probabilities,
            "regime_duration_quarters": regime_duration,
            "regime_switching_probability": switching_probability,
            "expected_regime_duration_quarters": self._get_expected_regime_duration(current_regime),
            "volatility_regime": volatility_regime,
            "regime_characteristics": self._describe_regime_characteristics(current_regime),
            "switching_signals": self._identify_regime_switching_signals(indicators),
        }

    def _classify_economic_regime(self, gdp_growth: float, unemployment: float, volatility: float) -> str:
        """Classify current economic regime"""

        if gdp_growth >= 2.0 and unemployment <= 5.0 and volatility <= 15:
            return "growth"
        if gdp_growth <= 0.5 or unemployment >= 5.5 or volatility >= 20:
            return "recession"
        return "stagnation"

    def _calculate_regime_probabilities(
        self, gdp_growth: float, unemployment: float, volatility: float
    ) -> dict[str, float]:
        """Calculate probabilities for each economic regime"""

        # Simple logistic-style probability calculation
        growth_score = max(0, min(1, (gdp_growth - 0.5) / 2.5))
        employment_score = max(0, min(1, (6.0 - unemployment) / 2.0))
        stability_score = max(0, min(1, (25 - volatility) / 15))

        # Regime probabilities
        growth_prob = (growth_score + employment_score + stability_score) / 3.0
        recession_prob = 1.0 - growth_prob
        stagnation_prob = 1.0 - abs(growth_prob - 0.5) * 2.0  # Peak at middle values

        # Normalize
        total = growth_prob + recession_prob + stagnation_prob

        return {
            "growth": round(growth_prob / total, 3),
            "recession": round(recession_prob / total, 3),
            "stagnation": round(stagnation_prob / total, 3),
        }

    def _estimate_regime_duration(self, regime: str, indicators: dict[str, Any]) -> int:
        """Estimate how long current regime has been in place"""

        # Use phase duration as proxy (convert months to quarters)
        phase_duration_quarters = max(1, indicators["phase_duration_months"] // 3)

        # Adjust based on regime type
        if regime == "recession":
            return min(phase_duration_quarters, 8)  # Recessions rarely last > 2 years
        if regime == "growth":
            return phase_duration_quarters
        # stagnation
        return min(phase_duration_quarters, 12)  # Stagnation periods moderate length

    def _calculate_regime_switching_probability(self, regime: str, duration: int, indicators: dict[str, Any]) -> float:
        """Calculate probability of regime switch in next quarter"""

        base_switching_probs = {
            "growth": 0.05,  # 5% quarterly chance of leaving growth
            "stagnation": 0.15,  # 15% quarterly chance of leaving stagnation
            "recession": 0.25,  # 25% quarterly chance of leaving recession
        }

        base_prob = base_switching_probs.get(regime, 0.1)

        # Duration effect: longer regimes more likely to switch
        duration_multiplier = 1.0 + (duration - 4) * 0.05  # Increase 5% per quarter above 1 year

        # Economic momentum effect
        gdp_momentum = (indicators["gdp_growth"] - 2.0) * 0.1
        if regime == "recession" and gdp_momentum > 0:
            duration_multiplier *= 1.5  # Positive growth increases recession exit probability
        elif regime == "growth" and gdp_momentum < 0:
            duration_multiplier *= 1.3  # Negative growth increases growth exit probability

        switching_prob = min(0.8, base_prob * duration_multiplier)

        return round(switching_prob, 3)

    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify volatility regime"""

        if volatility <= 15:
            return "low_volatility"
        if volatility <= 25:
            return "moderate_volatility"
        return "high_volatility"

    def _get_expected_regime_duration(self, regime: str) -> int:
        """Get expected duration for regime type"""

        expected_durations = {
            "growth": 20,  # ~5 years
            "stagnation": 8,  # ~2 years
            "recession": 4,  # ~1 year
        }

        return expected_durations.get(regime, 8)

    def _describe_regime_characteristics(self, regime: str) -> dict[str, Any]:
        """Describe characteristics of current regime"""

        characteristics = {
            "growth": {
                "description": "Robust economic expansion with low unemployment and stable prices",
                "typical_duration_years": "3-7",
                "asset_class_performance": "Equities outperform, credit spreads tight",
                "policy_stance": "Neutral to tightening monetary policy",
                "key_risks": ["Overheating", "Asset bubbles", "Policy errors"],
            },
            "stagnation": {
                "description": "Below-trend growth with elevated uncertainty",
                "typical_duration_years": "1-3",
                "asset_class_performance": "Mixed performance, defensive sectors preferred",
                "policy_stance": "Accommodative monetary policy, fiscal stimulus considered",
                "key_risks": [
                    "Deflation",
                    "Secular stagnation",
                    "Political instability",
                ],
            },
            "recession": {
                "description": "Economic contraction with rising unemployment",
                "typical_duration_years": "0.5-1.5",
                "asset_class_performance": "Bonds outperform, equities decline significantly",
                "policy_stance": "Aggressive accommodation, emergency measures",
                "key_risks": ["Financial crisis", "Debt deflation", "Social unrest"],
            },
        }

        return characteristics.get(regime, {})

    def _identify_regime_switching_signals(self, indicators: dict[str, Any]) -> list[str]:
        """Identify signals that suggest regime switching"""

        signals = []

        # Leading indicators for regime change
        if abs(indicators["yield_spread"]) < 0.25:
            signals.append("yield_curve_flattening_near_inversion")

        if indicators["vix_level"] > 30:
            signals.append("elevated_market_stress")

        if indicators["recession_probability"] > 0.4:
            signals.append("high_recession_probability")

        if indicators["gdp_growth"] < 0:
            signals.append("negative_gdp_growth")

        if indicators["unemployment_rate"] > 6.0:
            signals.append("elevated_unemployment")

        # Policy regime signals
        cycle_maturity = indicators.get("cycle_maturity", "mid")
        if cycle_maturity == "late":
            signals.append("late_cycle_positioning")

        return signals

    def _analyze_sector_rotation(self, indicators: dict[str, Any], markov_analysis: dict[str, Any]) -> dict[str, Any]:
        """Analyze sector rotation signals based on business cycle positioning"""

        current_phase = indicators["current_phase"]
        cycle_maturity = indicators.get("cycle_maturity", "mid")

        # Determine cycle stage for sector rotation
        cycle_stage = self._determine_cycle_stage(current_phase, cycle_maturity, indicators)

        # Get preferred sectors
        preferred_sectors = self.sector_rotation_map.get(cycle_stage, [])

        # Calculate rotation probability
        rotation_probability = self._calculate_rotation_probability(indicators, markov_analysis)

        # Determine rotation timing
        rotation_timing = self._determine_rotation_timing(indicators, markov_analysis)

        return {
            "current_cycle_stage": cycle_stage,
            "preferred_sectors": preferred_sectors,
            "rotation_probability_next_quarter": rotation_probability,
            "rotation_timing": rotation_timing,
            "sector_rotation_confidence": self._calculate_rotation_confidence(indicators),
            "rotation_catalysts": self._identify_rotation_catalysts(indicators, markov_analysis),
            "contrarian_opportunities": self._identify_contrarian_opportunities(cycle_stage),
        }

    def _determine_cycle_stage(self, phase: str, maturity: str, indicators: dict[str, Any]) -> str:
        """Determine detailed cycle stage for sector rotation"""

        if phase == "expansion":
            if maturity == "early" or indicators["phase_duration_months"] < 12:
                return "early_expansion"
            if maturity == "late" or indicators["phase_duration_months"] > 36:
                return "late_expansion"
            return "mid_expansion"
        if phase == "peak":
            return "peak"
        if phase == "contraction":
            if indicators["phase_duration_months"] < 6:
                return "early_contraction"
            if indicators["phase_duration_months"] > 12:
                return "late_contraction"
            return "mid_contraction"
        # trough
        return "trough"

    def _calculate_rotation_probability(self, indicators: dict[str, Any], markov_analysis: dict[str, Any]) -> float:
        """Calculate sector rotation probability"""

        # Base rotation probability from transition analysis
        transition_probs = markov_analysis.get("multi_period_transition_probabilities", {})
        one_quarter = transition_probs.get("1_quarter", {})

        # Probability of phase change drives sector rotation
        current_phase_prob = one_quarter.get(f"{indicators['current_phase']}_probability", 0.7)
        rotation_base_prob = 1.0 - current_phase_prob

        # Adjust for market volatility (higher vol = more rotation)
        volatility_adjustment = min(1.5, indicators["vix_level"] / 20)

        # Adjust for cycle maturity (late cycle = more rotation)
        maturity_adjustment = 1.3 if indicators.get("cycle_maturity") == "late" else 1.0

        rotation_prob = rotation_base_prob * volatility_adjustment * maturity_adjustment

        return round(min(0.8, rotation_prob), 3)

    def _determine_rotation_timing(self, indicators: dict[str, Any], markov_analysis: dict[str, Any]) -> str:
        """Determine sector rotation timing"""

        transition_timing = markov_analysis.get("transition_timing_analysis", {})
        transition_urgency = transition_timing.get("transition_urgency", "moderate")

        if transition_urgency == "high":
            return "immediate"
        if transition_urgency == "moderate":
            return "next_1_2_quarters"
        return "longer_term"

    def _calculate_rotation_confidence(self, indicators: dict[str, Any]) -> float:
        """Calculate confidence in sector rotation signals"""

        confidence_factors = []

        # Business cycle clarity
        if indicators.get("cycle_maturity") in ["early", "late"]:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)

        # Economic indicator clarity
        if abs(indicators["gdp_growth"] - 2.0) > 1.0:  # Clear above/below trend
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.6)

        # Market volatility (moderate vol = better signals)
        if 15 <= indicators["vix_level"] <= 25:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)

        return round(np.mean(confidence_factors), 3)

    def _identify_rotation_catalysts(self, indicators: dict[str, Any], markov_analysis: dict[str, Any]) -> list[str]:
        """Identify catalysts for sector rotation"""

        catalysts = []

        # Economic catalysts
        if indicators["gdp_growth"] < 1.0:
            catalysts.append("economic_slowdown_favoring_defensives")

        if indicators["unemployment_rate"] > 5.0:
            catalysts.append("labor_market_weakness_rotation")

        # Policy catalysts
        risk_factors = markov_analysis.get("transition_risk_factors", {})
        if "yield_curve_risk" in risk_factors.get("risk_factor_scores", {}):
            catalysts.append("yield_curve_dynamics")

        # Market catalysts
        if indicators["vix_level"] > 25:
            catalysts.append("volatility_spike_defensive_rotation")

        # Cycle catalysts
        transition_timing = markov_analysis.get("transition_timing_analysis", {})
        if transition_timing.get("transition_urgency") == "high":
            catalysts.append("imminent_cycle_transition")

        return catalysts

    def _identify_contrarian_opportunities(self, cycle_stage: str) -> list[str]:
        """Identify contrarian sector opportunities"""

        contrarian_map = {
            "early_expansion": ["utilities", "consumer_staples"],  # Oversold defensives
            "mid_expansion": [
                "technology",
                "consumer_discretionary",
            ],  # Early positioning
            "late_expansion": ["energy", "materials"],  # Value opportunities
            "peak": ["financials", "industrials"],  # Cycle peak plays
            "early_contraction": ["technology", "growth"],  # Quality at discount
            "mid_contraction": [
                "consumer_discretionary",
                "materials",
            ],  # Recovery positioning
            "late_contraction": ["financials", "real_estate"],  # Early recovery
            "trough": ["utilities", "consumer_staples"],  # Late defensives
        }

        return contrarian_map.get(cycle_stage, [])

    def _match_historical_patterns(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Match current conditions to historical business cycle patterns"""

        # Simplified historical pattern matching
        current_pattern = self._classify_current_pattern(indicators)

        # Historical analogies
        historical_matches = self._find_historical_analogies(indicators)

        # Pattern-based forecasts
        pattern_forecasts = self._generate_pattern_forecasts(current_pattern, indicators)

        return {
            "current_pattern_classification": current_pattern,
            "historical_analogies": historical_matches,
            "pattern_based_forecasts": pattern_forecasts,
            "pattern_confidence": self._calculate_pattern_confidence(indicators),
        }

    def _classify_current_pattern(self, indicators: dict[str, Any]) -> str:
        """Classify current economic pattern"""

        gdp_growth = indicators["gdp_growth"]
        unemployment = indicators["unemployment_rate"]
        phase_duration = indicators["phase_duration_months"]

        if gdp_growth > 2.5 and unemployment < 4.5 and phase_duration > 24:
            return "late_cycle_boom"
        if gdp_growth < 1.0 and unemployment > 5.0:
            return "economic_slowdown"
        if 1.0 <= gdp_growth <= 2.5 and 4.0 <= unemployment <= 5.5:
            return "moderate_growth"
        if phase_duration > 60:
            return "extended_expansion"
        return "typical_mid_cycle"

    def _find_historical_analogies(self, indicators: dict[str, Any]) -> list[dict[str, Any]]:
        """Find historical periods with similar economic conditions"""

        # Simplified historical analogies (would use actual historical data in production)
        analogies = []

        gdp_growth = indicators["gdp_growth"]
        unemployment = indicators["unemployment_rate"]

        if gdp_growth > 3.0 and unemployment < 4.0:
            analogies.append(
                {
                    "period": "1990s_tech_boom",
                    "similarity_score": 0.85,
                    "outcome": "Overheating followed by correction",
                    "duration": "~7 years",
                    "lessons": "Monitor asset bubbles and policy tightening",
                }
            )

        elif 1.5 <= gdp_growth <= 2.5:
            analogies.append(
                {
                    "period": "2010s_recovery",
                    "similarity_score": 0.75,
                    "outcome": "Extended but moderate expansion",
                    "duration": "~10 years",
                    "lessons": "Low inflation allows policy patience",
                }
            )

        elif gdp_growth < 1.0:
            analogies.append(
                {
                    "period": "2000s_stagflation_concerns",
                    "similarity_score": 0.70,
                    "outcome": "Policy accommodation, eventual recovery",
                    "duration": "~2 years",
                    "lessons": "Supply side reforms important",
                }
            )

        return analogies

    def _generate_pattern_forecasts(self, pattern: str, indicators: dict[str, Any]) -> dict[str, Any]:
        """Generate forecasts based on historical pattern matching"""

        pattern_forecasts = {
            "late_cycle_boom": {
                "expected_duration_quarters": 4,
                "probability_soft_landing": 0.3,
                "probability_recession": 0.6,
                "expected_peak_timing": "within_2_quarters",
            },
            "economic_slowdown": {
                "expected_duration_quarters": 6,
                "probability_recession": 0.4,
                "recovery_timeline": "6_12_months",
                "policy_response_expected": "accommodative",
            },
            "moderate_growth": {
                "expected_duration_quarters": 12,
                "sustainability_probability": 0.7,
                "inflation_risk": "low",
                "policy_stance": "neutral",
            },
            "extended_expansion": {
                "expected_duration_quarters": 8,
                "vulnerability_assessment": "high",
                "transition_risk": "elevated",
                "monitoring_priority": "high",
            },
        }

        return pattern_forecasts.get(pattern, {})

    def _calculate_pattern_confidence(self, indicators: dict[str, Any]) -> float:
        """Calculate confidence in historical pattern matching"""

        # Simple confidence based on data quality and economic clarity
        confidence_factors = []

        # GDP clarity
        if abs(indicators["gdp_growth"] - 2.0) > 0.5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)

        # Employment clarity
        if abs(indicators["unemployment_rate"] - 5.0) > 1.0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)

        # Phase duration clarity
        phase_duration = indicators["phase_duration_months"]
        if phase_duration < 6 or phase_duration > 48:
            confidence_factors.append(0.9)  # Clear early or late
        else:
            confidence_factors.append(0.7)

        return round(np.mean(confidence_factors), 3)

    def _calculate_multi_horizon_recession_probability(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Calculate recession probability over multiple time horizons"""

        base_recession_prob = indicators["recession_probability"]

        # Adjust base probability for different horizons
        horizons = {
            "3_months": base_recession_prob * 0.5,  # Near-term lower
            "6_months": base_recession_prob * 0.8,
            "12_months": base_recession_prob,  # Base case
            "24_months": min(0.8, base_recession_prob * 1.4),  # Longer-term higher
        }

        # Add confidence intervals
        for horizon in horizons:
            prob = horizons[horizon]
            # Simple confidence interval (±20%)
            horizons[horizon] = {
                "probability": round(prob, 3),
                "confidence_interval_lower": round(max(0, prob - 0.2), 3),
                "confidence_interval_upper": round(min(1, prob + 0.2), 3),
            }

        return {
            "multi_horizon_probabilities": horizons,
            "methodology": "nber_indicators_with_time_decay",
            "key_drivers": [
                "yield_curve",
                "employment_trends",
                "gdp_momentum",
                "financial_conditions",
            ],
            "model_confidence": 0.85,
        }

    def _analyze_volatility_regime(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Analyze current volatility regime"""

        vix_level = indicators["vix_level"]

        # Classify regime
        if vix_level <= 12:
            regime = "ultra_low_volatility"
        elif vix_level <= 20:
            regime = "low_volatility"
        elif vix_level <= 30:
            regime = "moderate_volatility"
        elif vix_level <= 40:
            regime = "high_volatility"
        else:
            regime = "extreme_volatility"

        # Expected duration
        expected_duration = self._get_expected_volatility_duration(regime)

        # Mean reversion analysis
        long_term_vix = 19.5  # Historical average
        reversion_signal = abs(vix_level - long_term_vix) / long_term_vix

        return {
            "current_volatility_regime": regime,
            "vix_level": vix_level,
            "expected_regime_duration_months": expected_duration,
            "mean_reversion_signal": round(reversion_signal, 3),
            "volatility_clustering": vix_level > 25,  # High vol tends to cluster
            "regime_switching_probability": self._calculate_volatility_regime_switching_prob(vix_level),
            "investment_implications": self._get_volatility_investment_implications(regime),
        }

    def _get_expected_volatility_duration(self, regime: str) -> int:
        """Get expected duration for volatility regime"""

        durations = {
            "ultra_low_volatility": 6,  # Rare, short-lived
            "low_volatility": 12,  # Typical bull market
            "moderate_volatility": 6,  # Transition periods
            "high_volatility": 3,  # Crisis periods
            "extreme_volatility": 1,  # Panic periods
        }

        return durations.get(regime, 6)

    def _calculate_volatility_regime_switching_prob(self, vix_level: float) -> float:
        """Calculate probability of volatility regime switch"""

        # Mean reversion tendency
        long_term_mean = 19.5
        deviation = abs(vix_level - long_term_mean)

        # Higher deviations have higher switching probability
        base_switching_prob = min(0.3, deviation / 20)

        return round(base_switching_prob, 3)

    def _get_volatility_investment_implications(self, regime: str) -> dict[str, Any]:
        """Get investment implications of volatility regime"""

        implications = {
            "ultra_low_volatility": {
                "environment": "Complacency risk, bubble conditions possible",
                "strategy": "Defensive positioning, volatility selling opportunities",
                "asset_preferences": [
                    "low_vol_stocks",
                    "covered_calls",
                    "credit_spreads",
                ],
            },
            "low_volatility": {
                "environment": "Stable growth, risk-taking environment",
                "strategy": "Growth and momentum strategies",
                "asset_preferences": ["growth_stocks", "emerging_markets", "credit"],
            },
            "moderate_volatility": {
                "environment": "Normal market conditions",
                "strategy": "Balanced approach, sector rotation",
                "asset_preferences": ["diversified_equities", "balanced_funds"],
            },
            "high_volatility": {
                "environment": "Market stress, flight to quality",
                "strategy": "Defensive positioning, volatility hedging",
                "asset_preferences": ["treasuries", "gold", "defensive_sectors"],
            },
            "extreme_volatility": {
                "environment": "Crisis conditions, forced selling",
                "strategy": "Capital preservation, opportunistic buying",
                "asset_preferences": [
                    "cash",
                    "treasuries",
                    "quality_stocks_at_discount",
                ],
            },
        }

        return implications.get(regime, {})

    def _create_integrated_assessment(
        self,
        markov_analysis: dict[str, Any],
        regime_analysis: dict[str, Any],
        rotation_analysis: dict[str, Any],
        historical_patterns: dict[str, Any],
    ) -> dict[str, Any]:
        """Create integrated business cycle assessment"""

        # Extract key insights
        current_phase = markov_analysis["current_phase"]
        transition_urgency = markov_analysis["transition_timing_analysis"].get("transition_urgency", "moderate")
        current_regime = regime_analysis["current_regime"]
        rotation_timing = rotation_analysis["rotation_timing"]

        # Overall assessment
        if transition_urgency == "high" and current_regime == "recession":
            assessment = "critical_transition_period"
        elif current_regime == "growth" and transition_urgency == "low":
            assessment = "stable_expansion"
        elif current_regime == "stagnation":
            assessment = "uncertain_transition"
        else:
            assessment = "moderate_risk_environment"

        # Key themes
        themes = []

        transition_risk_factors = markov_analysis.get("transition_risk_factors", {})
        overall_risk_score = transition_risk_factors.get("overall_transition_risk_score", 0.3)

        if overall_risk_score > 0.5:
            themes.append("Elevated business cycle transition risk requires defensive positioning")

        if regime_analysis["regime_switching_probability"] > 0.2:
            themes.append("Economic regime switching signals suggest tactical allocation adjustments")

        if rotation_analysis["rotation_probability_next_quarter"] > 0.4:
            themes.append("Sector rotation dynamics favor active portfolio management")

        # Investment implications
        investment_implications = self._generate_integrated_investment_implications(
            markov_analysis, regime_analysis, rotation_analysis, overall_risk_score
        )

        return {
            "overall_cycle_assessment": assessment,
            "key_investment_themes": themes,
            "business_cycle_confidence": self._calculate_integrated_confidence(
                markov_analysis, regime_analysis, rotation_analysis, historical_patterns
            ),
            "investment_implications": investment_implications,
            "risk_monitoring_priorities": self._identify_risk_monitoring_priorities(markov_analysis, regime_analysis),
            "tactical_positioning_recommendations": self._generate_tactical_recommendations(
                rotation_analysis, regime_analysis
            ),
        }

    def _generate_integrated_investment_implications(
        self,
        markov_analysis: dict[str, Any],
        regime_analysis: dict[str, Any],
        rotation_analysis: dict[str, Any],
        overall_risk_score: float,
    ) -> dict[str, Any]:
        """Generate integrated investment implications"""

        current_phase = markov_analysis["current_phase"]
        current_regime = regime_analysis["current_regime"]
        preferred_sectors = rotation_analysis["preferred_sectors"]

        # Asset allocation guidance
        if current_regime == "growth" and current_phase == "expansion":
            allocation = "risk_on_growth_focused"
            equity_weight = "overweight"
        elif current_regime == "recession" or current_phase == "contraction":
            allocation = "defensive_capital_preservation"
            equity_weight = "underweight"
        else:
            allocation = "balanced_opportunistic"
            equity_weight = "neutral"

        # Duration positioning
        if overall_risk_score > 0.6:
            duration = "extend_duration_defensive"
        else:
            duration = "neutral_duration"

        return {
            "asset_allocation_stance": allocation,
            "equity_positioning": equity_weight,
            "sector_preferences": preferred_sectors,
            "duration_positioning": duration,
            "volatility_positioning": (
                "hedge" if regime_analysis["volatility_regime"] == "low_volatility" else "opportunistic"
            ),
            "rebalancing_urgency": markov_analysis["transition_timing_analysis"].get("transition_urgency", "moderate"),
        }

    def _calculate_integrated_confidence(
        self,
        markov_analysis: dict[str, Any],
        regime_analysis: dict[str, Any],
        rotation_analysis: dict[str, Any],
        historical_patterns: dict[str, Any],
    ) -> float:
        """Calculate overall confidence in business cycle analysis"""

        confidence_components = [
            markov_analysis.get("markov_model_confidence", 0.8),
            rotation_analysis.get("sector_rotation_confidence", 0.7),
            historical_patterns.get("pattern_confidence", 0.75),
        ]

        return round(np.mean(confidence_components), 3)

    def _identify_risk_monitoring_priorities(
        self, markov_analysis: dict[str, Any], regime_analysis: dict[str, Any]
    ) -> list[str]:
        """Identify key risk monitoring priorities"""

        priorities = []

        # Transition risk priorities
        risk_factors = markov_analysis.get("transition_risk_factors", {})
        overall_transition_risk = risk_factors.get("overall_transition_risk_score", 0.3)
        if overall_transition_risk > 0.5:
            priorities.extend(risk_factors.get("key_monitoring_indicators", []))

        # Regime switching priorities
        if regime_analysis.get("regime_switching_probability", 0) > 0.15:
            priorities.extend(["gdp_momentum", "employment_trends", "financial_conditions"])

        # Remove duplicates and return top priorities
        return list(set(priorities))[:6]

    def _generate_tactical_recommendations(
        self, rotation_analysis: dict[str, Any], regime_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate tactical positioning recommendations"""

        return {
            "sector_rotation": {
                "timing": rotation_analysis.get("rotation_timing", "next_1_2_quarters"),
                "preferred_sectors": rotation_analysis.get("preferred_sectors", []),
                "rotation_probability": rotation_analysis.get("rotation_probability_next_quarter", 0.3),
            },
            "regime_positioning": {
                "current_regime": regime_analysis.get("current_regime", "stagnation"),
                "regime_duration": regime_analysis.get("regime_duration_quarters", 4),
                "switching_probability": regime_analysis.get("regime_switching_probability", 0.1),
            },
            "volatility_management": {
                "volatility_regime": regime_analysis.get("volatility_regime", "moderate_volatility"),
                "hedging_recommendations": (
                    "moderate" if regime_analysis.get("volatility_regime") == "low_volatility" else "defensive"
                ),
            },
        }

    def _calculate_model_confidence(self, indicators: dict[str, Any]) -> float:
        """Calculate overall model confidence"""

        confidence_factors = []

        # Data quality factor
        confidence_factors.append(0.85)  # Base assumption

        # Economic clarity factor
        gdp_clarity = 1.0 - abs(indicators["gdp_growth"] - 2.0) * 0.2
        confidence_factors.append(max(0.5, gdp_clarity))

        # Phase clarity factor
        if indicators.get("cycle_maturity") in ["early", "late"]:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)

        # Volatility factor (moderate volatility = better signals)
        vix_level = indicators["vix_level"]
        if 15 <= vix_level <= 25:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.65)

        return round(np.mean(confidence_factors), 3)

    def _calculate_markov_confidence(self, indicators: dict[str, Any]) -> float:
        """Calculate confidence in Markov chain analysis"""

        # Similar to model confidence but specific to transition modeling
        confidence_factors = []

        # Phase duration clarity (very short or very long phases = higher confidence)
        duration = indicators["phase_duration_months"]
        if duration < 6 or duration > 48:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.75)

        # Economic momentum clarity
        gdp_growth = indicators["gdp_growth"]
        if abs(gdp_growth - 2.0) > 1.0:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.65)

        # Recession signal clarity
        recession_prob = indicators["recession_probability"]
        if recession_prob < 0.2 or recession_prob > 0.4:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.7)

        return round(np.mean(confidence_factors), 3)


# Testing and validation functions
def validate_advanced_business_cycle_engine():
    """Validate the advanced business cycle modeling engine"""

    # Sample data
    sample_discovery = {
        "business_cycle_data": {
            "current_phase": "expansion",
            "historical_context": {"phase_duration": 30, "cycle_maturity": "mid"},
        },
        "economic_indicators": {
            "composite_scores": {"recession_probability": 0.25},
            "leading_indicators": {"yield_curve": {"current_spread": {"10y_2y": 0.35}}},
        },
        "cli_comprehensive_analysis": {
            "central_bank_economic_data": {
                "gdp_data": {"observations": [{"value": 2.2}]},
                "employment_data": {"unemployment_data": {"observations": [{"value": 4.3}]}},
            }
        },
        "cli_market_intelligence": {"volatility_analysis": {"vix_analysis": {"current_level": 21.5}}},
    }

    sample_analysis = {"region": "US"}

    # Create engine and run analysis
    engine = AdvancedBusinessCycleEngine("US")
    results = engine.analyze_advanced_business_cycle(sample_discovery, sample_analysis)

    return results


if __name__ == "__main__":
    # Run validation
    test_results = validate_advanced_business_cycle_engine()
    print(json.dumps(test_results, indent=2))
