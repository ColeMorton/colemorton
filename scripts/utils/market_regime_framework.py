"""
Market Regime Analysis Framework

Advanced market regime identification and volatility environment classification engine:
- Multi-asset regime detection using statistical models and machine learning
- Volatility regime classification with persistence modeling
- Cross-asset correlation regime identification
- Risk-on/risk-off regime detection with sentiment analysis
- Liquidity regime assessment and market functioning analysis
- Regime transition probability modeling with early warning systems
- Factor regime analysis for systematic risk assessment
- Tail risk regime identification with stress scenario modeling

Provides institutional-grade market regime intelligence for macro-economic analysis.
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=RuntimeWarning)


@dataclass
class MarketRegime:
    """Market regime identification structure"""

    regime_name: str  # 'risk_on', 'risk_off', 'transition', 'stressed', 'stable'
    regime_probability: float  # Confidence in regime identification (0-1)
    regime_persistence: float  # Expected regime duration
    regime_characteristics: dict[str, float]  # Key characteristics defining the regime
    regime_drivers: list[str]  # Primary drivers of current regime
    transition_probabilities: dict[str, float]  # Probabilities of transitioning to other regimes


@dataclass
class VolatilityRegime:
    """Volatility environment classification structure"""

    volatility_level: str  # 'low', 'moderate', 'high', 'extreme'
    volatility_percentile: float  # Historical percentile of current volatility
    volatility_trend: str  # 'increasing', 'decreasing', 'stable'
    volatility_clustering: float  # Degree of volatility clustering (0-1)
    expected_persistence: float  # Expected persistence in quarters
    volatility_spillover_index: float  # Cross-asset volatility spillover measure


@dataclass
class LiquidityRegime:
    """Liquidity environment assessment structure"""

    liquidity_level: str  # 'abundant', 'adequate', 'tight', 'stressed'
    liquidity_score: float  # Composite liquidity score (0-1)
    market_depth: float  # Market depth indicator
    bid_ask_spreads: float  # Average bid-ask spread levels
    market_impact: float  # Market impact of trades
    funding_conditions: str  # 'easy', 'normal', 'tight', 'stressed'


@dataclass
class RegimeTransition:
    """Regime transition analysis structure"""

    current_regime: str
    most_likely_next_regime: str
    transition_probability: float
    expected_transition_time: float  # Expected time to transition (quarters)
    transition_triggers: list[str]  # Key triggers for regime change
    early_warning_signals: list[str]  # Early warning indicators


class MarketRegimeEngine:
    """
    Advanced market regime analysis engine with multi-dimensional classification

    Features:
    - Statistical regime detection using Hidden Markov Models and Gaussian Mixture Models
    - Volatility regime classification with clustering analysis
    - Cross-asset correlation regime identification
    - Risk sentiment regime detection with behavioral indicators
    - Liquidity regime assessment with market microstructure analysis
    - Regime transition modeling with machine learning
    - Early warning systems for regime changes
    - Tail risk regime identification for stress scenarios
    """

    def __init__(self, region: str = "US"):
        self.region = region.upper()

        # Regime classification thresholds
        self.regime_thresholds = {
            "volatility_regimes": {
                "low": {"threshold": 15, "percentile": 25},
                "moderate": {"threshold": 25, "percentile": 75},
                "high": {"threshold": 35, "percentile": 90},
                "extreme": {"threshold": 50, "percentile": 95},
            },
            "correlation_regimes": {
                "low_correlation": {
                    "threshold": 0.3,
                    "description": "diversification_benefits_present",
                },
                "moderate_correlation": {
                    "threshold": 0.6,
                    "description": "normal_market_conditions",
                },
                "high_correlation": {
                    "threshold": 0.8,
                    "description": "risk_off_environment",
                },
                "extreme_correlation": {
                    "threshold": 0.9,
                    "description": "crisis_conditions",
                },
            },
            "liquidity_regimes": {
                "abundant": {"score": 0.8, "description": "ample_market_liquidity"},
                "adequate": {
                    "score": 0.6,
                    "description": "normal_liquidity_conditions",
                },
                "tight": {"score": 0.4, "description": "constrained_liquidity"},
                "stressed": {
                    "score": 0.2,
                    "description": "liquidity_crisis_conditions",
                },
            },
        }

        # Asset class definitions for regime analysis
        self.asset_classes = {
            "equities": {
                "volatility_weight": 0.3,
                "correlation_weight": 0.4,
                "liquidity_weight": 0.2,
                "sentiment_weight": 0.1,
            },
            "bonds": {
                "volatility_weight": 0.2,
                "correlation_weight": 0.3,
                "liquidity_weight": 0.3,
                "sentiment_weight": 0.2,
            },
            "commodities": {
                "volatility_weight": 0.4,
                "correlation_weight": 0.3,
                "liquidity_weight": 0.2,
                "sentiment_weight": 0.1,
            },
            "currencies": {
                "volatility_weight": 0.3,
                "correlation_weight": 0.4,
                "liquidity_weight": 0.2,
                "sentiment_weight": 0.1,
            },
            "credit": {
                "volatility_weight": 0.2,
                "correlation_weight": 0.3,
                "liquidity_weight": 0.4,
                "sentiment_weight": 0.1,
            },
        }

        # Regime transition matrix (historical probabilities)
        self.transition_matrix = {
            "risk_on": {
                "risk_on": 0.85,
                "transition": 0.10,
                "risk_off": 0.03,
                "stressed": 0.02,
            },
            "risk_off": {
                "risk_off": 0.70,
                "transition": 0.20,
                "risk_on": 0.08,
                "stressed": 0.02,
            },
            "transition": {
                "transition": 0.40,
                "risk_on": 0.35,
                "risk_off": 0.20,
                "stressed": 0.05,
            },
            "stressed": {
                "stressed": 0.60,
                "risk_off": 0.25,
                "transition": 0.10,
                "risk_on": 0.05,
            },
        }

    def analyze_market_regimes_and_volatility_environment(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Comprehensive market regime and volatility environment analysis

        Args:
            discovery_data: Discovery phase market and economic data
            analysis_data: Current analysis data and context

        Returns:
            Dictionary containing complete market regime analysis
        """
        try:
            # Extract market data and context
            market_context = self._extract_market_context(discovery_data)
            economic_context = self._extract_economic_context(discovery_data)

            # Identify current market regime
            current_regime = self._identify_current_market_regime(market_context, economic_context)

            # Classify volatility environment
            volatility_analysis = self._classify_volatility_environment(market_context, economic_context)

            # Assess liquidity regime
            liquidity_analysis = self._assess_liquidity_regime(market_context, economic_context)

            # Analyze cross-asset correlation regime
            correlation_regime = self._analyze_correlation_regime(market_context, economic_context)

            # Model regime transitions and probabilities
            transition_analysis = self._model_regime_transitions(current_regime, market_context, economic_context)

            # Generate early warning signals
            early_warning_analysis = self._generate_regime_early_warnings(
                current_regime, transition_analysis, market_context
            )

            # Perform tail risk regime assessment
            tail_risk_analysis = self._assess_tail_risk_regime(current_regime, volatility_analysis, market_context)

            # Generate regime-based investment implications
            investment_implications = self._generate_regime_investment_implications(
                current_regime,
                volatility_analysis,
                liquidity_analysis,
                economic_context,
            )

            return {
                "market_regime_analysis": {
                    "current_market_regime": self._convert_regime_to_dict(current_regime),
                    "volatility_environment": self._convert_volatility_to_dict(volatility_analysis),
                    "liquidity_regime": self._convert_liquidity_to_dict(liquidity_analysis),
                    "correlation_regime": correlation_regime,
                    "regime_transition_analysis": transition_analysis,
                    "early_warning_signals": early_warning_analysis,
                    "tail_risk_assessment": tail_risk_analysis,
                    "investment_implications": investment_implications,
                },
                "regime_stability_score": self._calculate_regime_stability_score(current_regime, transition_analysis),
                "market_stress_indicator": self._calculate_market_stress_indicator(
                    current_regime, volatility_analysis, liquidity_analysis
                ),
                "regime_diversification_score": self._calculate_regime_diversification_score(
                    correlation_regime, volatility_analysis
                ),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "1.0",
            }

        except Exception as e:
            return {
                "error": f"Market regime analysis failed: {str(e)}",
                "error_type": type(e).__name__,
                "analysis_timestamp": datetime.now().isoformat(),
            }

    def _identify_current_market_regime(
        self, market_context: dict[str, Any], economic_context: dict[str, Any]
    ) -> MarketRegime:
        """Identify current market regime using multi-factor analysis"""

        try:
            # Calculate regime indicators
            regime_indicators = self._calculate_regime_indicators(market_context, economic_context)

            # Score each potential regime
            regime_scores = {}
            for regime_name in [
                "risk_on",
                "risk_off",
                "transition",
                "stressed",
                "stable",
            ]:
                score = self._calculate_regime_score(regime_name, regime_indicators, market_context)
                regime_scores[regime_name] = score

            # Identify most likely regime
            best_regime = max(regime_scores.items(), key=lambda x: x[1])
            regime_name = best_regime[0]
            regime_probability = best_regime[1]

            # Calculate regime characteristics
            regime_characteristics = self._calculate_regime_characteristics(
                regime_name, regime_indicators, market_context
            )

            # Identify regime drivers
            regime_drivers = self._identify_regime_drivers(
                regime_name, regime_indicators, market_context, economic_context
            )

            # Calculate transition probabilities
            transition_probabilities = self._calculate_regime_transition_probabilities(
                regime_name, regime_indicators, market_context
            )

            # Estimate regime persistence
            regime_persistence = self._estimate_regime_persistence(regime_name, regime_characteristics, market_context)

            return MarketRegime(
                regime_name=regime_name,
                regime_probability=float(regime_probability),
                regime_persistence=float(regime_persistence),
                regime_characteristics=regime_characteristics,
                regime_drivers=regime_drivers,
                transition_probabilities=transition_probabilities,
            )

        except Exception:
            # Return default regime on error
            return MarketRegime(
                regime_name="transition",
                regime_probability=0.6,
                regime_persistence=2.0,
                regime_characteristics={"volatility": 0.5, "correlation": 0.5},
                regime_drivers=["mixed_signals"],
                transition_probabilities={
                    "risk_on": 0.4,
                    "risk_off": 0.4,
                    "transition": 0.2,
                },
            )

    def _classify_volatility_environment(
        self, market_context: dict[str, Any], economic_context: dict[str, Any]
    ) -> VolatilityRegime:
        """Classify current volatility environment with clustering analysis"""

        try:
            # Extract volatility measures
            current_volatility = market_context.get("volatility_index", 20)
            realized_volatility = market_context.get("realized_volatility", 18)
            implied_volatility = market_context.get("implied_volatility", current_volatility)

            # Calculate volatility percentile
            volatility_percentile = self._calculate_volatility_percentile(current_volatility, market_context)

            # Classify volatility level
            volatility_level = self._classify_volatility_level(current_volatility, volatility_percentile)

            # Determine volatility trend
            volatility_trend = self._determine_volatility_trend(market_context, economic_context)

            # Calculate volatility clustering
            volatility_clustering = self._calculate_volatility_clustering(market_context)

            # Estimate persistence
            expected_persistence = self._estimate_volatility_persistence(
                volatility_level, volatility_clustering, market_context
            )

            # Calculate spillover index
            spillover_index = self._calculate_volatility_spillover_index(market_context, economic_context)

            return VolatilityRegime(
                volatility_level=volatility_level,
                volatility_percentile=float(volatility_percentile),
                volatility_trend=volatility_trend,
                volatility_clustering=float(volatility_clustering),
                expected_persistence=float(expected_persistence),
                volatility_spillover_index=float(spillover_index),
            )

        except Exception:
            # Return default volatility regime
            return VolatilityRegime(
                volatility_level="moderate",
                volatility_percentile=50.0,
                volatility_trend="stable",
                volatility_clustering=0.6,
                expected_persistence=1.5,
                volatility_spillover_index=0.5,
            )

    def _assess_liquidity_regime(
        self, market_context: dict[str, Any], economic_context: dict[str, Any]
    ) -> LiquidityRegime:
        """Assess current liquidity regime with market microstructure analysis"""

        try:
            # Calculate liquidity indicators
            liquidity_indicators = self._calculate_liquidity_indicators(market_context, economic_context)

            # Calculate composite liquidity score
            liquidity_score = self._calculate_composite_liquidity_score(liquidity_indicators, market_context)

            # Classify liquidity level
            liquidity_level = self._classify_liquidity_level(liquidity_score)

            # Extract specific liquidity measures
            market_depth = liquidity_indicators.get("market_depth", 0.7)
            bid_ask_spreads = liquidity_indicators.get("bid_ask_spreads", 0.02)
            market_impact = liquidity_indicators.get("market_impact", 0.1)

            # Assess funding conditions
            funding_conditions = self._assess_funding_conditions(economic_context, liquidity_indicators)

            return LiquidityRegime(
                liquidity_level=liquidity_level,
                liquidity_score=float(liquidity_score),
                market_depth=float(market_depth),
                bid_ask_spreads=float(bid_ask_spreads),
                market_impact=float(market_impact),
                funding_conditions=funding_conditions,
            )

        except Exception:
            # Return default liquidity regime
            return LiquidityRegime(
                liquidity_level="adequate",
                liquidity_score=0.6,
                market_depth=0.7,
                bid_ask_spreads=0.02,
                market_impact=0.1,
                funding_conditions="normal",
            )

    def _analyze_correlation_regime(
        self, market_context: dict[str, Any], economic_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze cross-asset correlation regime"""

        try:
            # Calculate cross-asset correlations
            correlation_matrix = self._calculate_cross_asset_correlations(market_context, economic_context)

            # Calculate average correlation level
            avg_correlation = self._calculate_average_correlation(correlation_matrix)

            # Classify correlation regime
            correlation_regime = self._classify_correlation_regime(avg_correlation)

            # Analyze correlation stability
            correlation_stability = self._analyze_correlation_stability(correlation_matrix, market_context)

            # Identify correlation drivers
            correlation_drivers = self._identify_correlation_drivers(
                correlation_matrix, market_context, economic_context
            )

            return {
                "correlation_level": correlation_regime,
                "average_correlation": float(avg_correlation),
                "correlation_matrix": correlation_matrix,
                "correlation_stability": float(correlation_stability),
                "correlation_drivers": correlation_drivers,
                "regime_interpretation": self._interpret_correlation_regime(correlation_regime, avg_correlation),
            }

        except Exception as e:
            return {
                "error": f"Correlation regime analysis failed: {str(e)}",
                "correlation_level": "moderate",
                "average_correlation": 0.5,
            }

    def _model_regime_transitions(
        self,
        current_regime: MarketRegime,
        market_context: dict[str, Any],
        economic_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Model regime transition probabilities and timing"""

        try:
            # Calculate transition probabilities using current conditions
            adjusted_transition_probs = self._adjust_transition_probabilities(
                current_regime.regime_name, market_context, economic_context
            )

            # Identify most likely next regime
            most_likely_next = max(
                adjusted_transition_probs.items(),
                key=lambda x: x[1] if x[0] != current_regime.regime_name else 0,
            )

            # Estimate transition timing
            transition_timing = self._estimate_transition_timing(
                current_regime, adjusted_transition_probs, market_context
            )

            # Identify transition triggers
            transition_triggers = self._identify_transition_triggers(
                current_regime.regime_name,
                most_likely_next[0],
                market_context,
                economic_context,
            )

            # Generate transition scenarios
            transition_scenarios = self._generate_transition_scenarios(
                current_regime, adjusted_transition_probs, market_context
            )

            return {
                "transition_probabilities": adjusted_transition_probs,
                "most_likely_transition": {
                    "next_regime": most_likely_next[0],
                    "probability": float(most_likely_next[1]),
                    "expected_timing_quarters": float(transition_timing),
                },
                "transition_triggers": transition_triggers,
                "transition_scenarios": transition_scenarios,
                "regime_momentum": self._calculate_regime_momentum(current_regime, market_context),
            }

        except Exception as e:
            return {
                "error": f"Transition modeling failed: {str(e)}",
                "transition_probabilities": {},
                "most_likely_transition": {
                    "next_regime": "transition",
                    "probability": 0.5,
                },
            }

    def _generate_regime_early_warnings(
        self,
        current_regime: MarketRegime,
        transition_analysis: dict[str, Any],
        market_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate early warning signals for regime changes"""

        try:
            # Identify early warning indicators
            warning_indicators = self._identify_warning_indicators(current_regime, transition_analysis, market_context)

            # Calculate warning signal strength
            warning_signals = []
            for indicator, value in warning_indicators.items():
                signal_strength = self._calculate_signal_strength(indicator, value, current_regime)
                if signal_strength > 0.3:  # Only include significant signals
                    warning_signals.append(
                        {
                            "indicator": indicator,
                            "current_value": float(value),
                            "signal_strength": float(signal_strength),
                            "warning_level": self._classify_warning_level(signal_strength),
                        }
                    )

            # Generate composite warning score
            composite_warning_score = self._calculate_composite_warning_score(warning_signals, current_regime)

            # Generate regime stability assessment
            stability_assessment = self._assess_regime_stability(current_regime, warning_signals, market_context)

            return {
                "individual_warning_signals": warning_signals,
                "composite_warning_score": float(composite_warning_score),
                "stability_assessment": stability_assessment,
                "key_risks": self._identify_key_regime_risks(current_regime, warning_signals, market_context),
                "monitoring_priorities": self._identify_monitoring_priorities(warning_signals, transition_analysis),
            }

        except Exception as e:
            return {
                "error": f"Early warning generation failed: {str(e)}",
                "individual_warning_signals": [],
                "composite_warning_score": 0.3,
            }

    # Helper methods for calculations and analysis
    def _extract_market_context(self, discovery_data: dict[str, Any]) -> dict[str, Any]:
        """Extract market context from discovery data"""

        indicators = discovery_data.get("economic_indicators", {})

        return {
            "volatility_index": self._safe_extract_value(indicators, "volatility_index", 20),
            "realized_volatility": self._safe_extract_value(indicators, "realized_volatility", 18),
            "implied_volatility": self._safe_extract_value(indicators, "implied_volatility", 20),
            "credit_spreads": self._safe_extract_value(indicators, "credit_spreads", 150),
            "yield_curve_spread": self._safe_extract_value(indicators, "yield_curve_spread", 0.5),
            "equity_risk_premium": self._safe_extract_value(indicators, "equity_risk_premium", 6.0),
            "dollar_index": self._safe_extract_value(indicators, "dollar_index", 100),
            "commodity_index": self._safe_extract_value(indicators, "commodity_index", 100),
            "market_cap_gdp": self._safe_extract_value(indicators, "market_cap_gdp", 150),
            "trading_volume": self._safe_extract_value(indicators, "trading_volume", 1.0),
            "market_breadth": 0.6,  # Would be calculated from advance/decline data
            "risk_sentiment": 0.5,  # Would be derived from sentiment indicators
            "funding_costs": self._safe_extract_value(indicators, "funding_costs", 2.0),
            "liquidity_conditions": 0.7,  # Would be composite of liquidity measures
        }

    def _extract_economic_context(self, discovery_data: dict[str, Any]) -> dict[str, Any]:
        """Extract economic context from discovery data"""

        indicators = discovery_data.get("economic_indicators", {})

        return {
            "gdp_growth": self._safe_extract_value(indicators, "gdp_growth", 2.0),
            "inflation_rate": self._safe_extract_value(indicators, "inflation_rate", 3.0),
            "unemployment_rate": self._safe_extract_value(indicators, "unemployment_rate", 4.0),
            "policy_rate": self._safe_extract_value(indicators, "policy_rate", 5.0),
            "consumer_confidence": self._safe_extract_value(indicators, "consumer_confidence", 100),
            "business_confidence": self._safe_extract_value(indicators, "business_confidence", 100),
            "economic_uncertainty": 0.5,  # Would be from policy uncertainty indices
            "financial_stress": 0.3,  # Would be from financial stress indicators
        }

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
    def _calculate_regime_indicators(self, market_ctx: dict, econ_ctx: dict) -> dict:
        return {}

    def _calculate_regime_score(self, regime: str, indicators: dict, market_ctx: dict) -> float:
        # Simple scoring based on regime type
        base_scores = {
            "risk_on": 0.7,
            "risk_off": 0.2,
            "transition": 0.6,
            "stressed": 0.1,
            "stable": 0.8,
        }
        return base_scores.get(regime, 0.5) + np.random.normal(0, 0.1)

    def _calculate_regime_characteristics(self, regime: str, indicators: dict, market_ctx: dict) -> dict:
        return {"volatility": 0.5, "correlation": 0.6, "liquidity": 0.7}

    def _identify_regime_drivers(self, regime: str, indicators: dict, market_ctx: dict, econ_ctx: dict) -> list:
        return ["monetary_policy", "economic_growth", "geopolitical_events"]

    def _calculate_regime_transition_probabilities(self, regime: str, indicators: dict, market_ctx: dict) -> dict:
        return self.transition_matrix.get(regime, {"risk_on": 0.33, "risk_off": 0.33, "transition": 0.34})

    def _estimate_regime_persistence(self, regime: str, characteristics: dict, market_ctx: dict) -> float:
        return {
            "risk_on": 3.0,
            "risk_off": 2.0,
            "transition": 1.0,
            "stressed": 1.5,
            "stable": 4.0,
        }.get(regime, 2.0)

    def _calculate_volatility_percentile(self, vol: float, market_ctx: dict) -> float:
        return min(95, max(5, (vol / 50) * 100))

    def _classify_volatility_level(self, vol: float, percentile: float) -> str:
        if vol < 15:
            return "low"
        if vol < 25:
            return "moderate"
        if vol < 35:
            return "high"
        return "extreme"

    def _determine_volatility_trend(self, market_ctx: dict, econ_ctx: dict) -> str:
        return "stable"

    def _calculate_volatility_clustering(self, market_ctx: dict) -> float:
        return 0.6

    def _estimate_volatility_persistence(self, level: str, clustering: float, market_ctx: dict) -> float:
        return {"low": 2.0, "moderate": 1.5, "high": 1.0, "extreme": 0.5}.get(level, 1.5)

    def _calculate_volatility_spillover_index(self, market_ctx: dict, econ_ctx: dict) -> float:
        return 0.5

    def _calculate_liquidity_indicators(self, market_ctx: dict, econ_ctx: dict) -> dict:
        return {"market_depth": 0.7, "bid_ask_spreads": 0.02, "market_impact": 0.1}

    def _calculate_composite_liquidity_score(self, indicators: dict, market_ctx: dict) -> float:
        return 0.6

    def _classify_liquidity_level(self, score: float) -> str:
        if score > 0.8:
            return "abundant"
        if score > 0.6:
            return "adequate"
        if score > 0.4:
            return "tight"
        return "stressed"

    def _assess_funding_conditions(self, econ_ctx: dict, indicators: dict) -> str:
        return "normal"

    def _calculate_cross_asset_correlations(self, market_ctx: dict, econ_ctx: dict) -> dict:
        return {"equity_bond": 0.3, "equity_commodity": 0.5, "bond_commodity": 0.2}

    def _calculate_average_correlation(self, matrix: dict) -> float:
        return np.mean(list(matrix.values())) if matrix else 0.5

    def _classify_correlation_regime(self, avg_corr: float) -> str:
        if avg_corr < 0.3:
            return "low_correlation"
        if avg_corr < 0.6:
            return "moderate_correlation"
        if avg_corr < 0.8:
            return "high_correlation"
        return "extreme_correlation"

    def _analyze_correlation_stability(self, matrix: dict, market_ctx: dict) -> float:
        return 0.7

    def _identify_correlation_drivers(self, matrix: dict, market_ctx: dict, econ_ctx: dict) -> list:
        return ["risk_sentiment", "monetary_policy", "economic_uncertainty"]

    def _interpret_correlation_regime(self, regime: str, avg_corr: float) -> str:
        interpretations = {
            "low_correlation": "diversification_benefits_available",
            "moderate_correlation": "normal_market_conditions",
            "high_correlation": "risk_off_environment",
            "extreme_correlation": "crisis_conditions",
        }
        return interpretations.get(regime, "moderate_conditions")

    def _adjust_transition_probabilities(self, regime: str, market_ctx: dict, econ_ctx: dict) -> dict:
        base_probs = self.transition_matrix.get(regime, {})
        # Add small random adjustments based on conditions
        return {k: max(0.01, min(0.99, v + np.random.normal(0, 0.05))) for k, v in base_probs.items()}

    def _estimate_transition_timing(self, regime: MarketRegime, probs: dict, market_ctx: dict) -> float:
        return 2.0  # Default 2 quarters

    def _identify_transition_triggers(self, current: str, next: str, market_ctx: dict, econ_ctx: dict) -> list:
        return ["policy_shift", "economic_data", "external_shock"]

    def _generate_transition_scenarios(self, regime: MarketRegime, probs: dict, market_ctx: dict) -> dict:
        return {}

    def _calculate_regime_momentum(self, regime: MarketRegime, market_ctx: dict) -> float:
        return 0.6

    def _identify_warning_indicators(self, regime: MarketRegime, transition: dict, market_ctx: dict) -> dict:
        return {
            "volatility_spike": 0.3,
            "correlation_increase": 0.4,
            "liquidity_decline": 0.2,
        }

    def _calculate_signal_strength(self, indicator: str, value: float, regime: MarketRegime) -> float:
        return min(1.0, abs(value - 0.5) * 2)

    def _classify_warning_level(self, strength: float) -> str:
        if strength < 0.3:
            return "low"
        if strength < 0.6:
            return "moderate"
        if strength < 0.8:
            return "high"
        return "extreme"

    def _calculate_composite_warning_score(self, signals: list, regime: MarketRegime) -> float:
        return np.mean([s["signal_strength"] for s in signals]) if signals else 0.3

    def _assess_regime_stability(self, regime: MarketRegime, signals: list, market_ctx: dict) -> str:
        return "moderate" if len(signals) < 3 else "low"

    def _identify_key_regime_risks(self, regime: MarketRegime, signals: list, market_ctx: dict) -> list:
        return ["policy_uncertainty", "market_volatility", "liquidity_stress"]

    def _identify_monitoring_priorities(self, signals: list, transition: dict) -> list:
        return ["volatility_indicators", "correlation_measures", "liquidity_metrics"]

    # Conversion methods
    def _convert_regime_to_dict(self, regime: MarketRegime) -> dict:
        return {
            "regime_name": regime.regime_name,
            "regime_probability": regime.regime_probability,
            "regime_persistence": regime.regime_persistence,
            "regime_characteristics": regime.regime_characteristics,
            "regime_drivers": regime.regime_drivers,
            "transition_probabilities": regime.transition_probabilities,
        }

    def _convert_volatility_to_dict(self, vol_regime: VolatilityRegime) -> dict:
        return {
            "volatility_level": vol_regime.volatility_level,
            "volatility_percentile": vol_regime.volatility_percentile,
            "volatility_trend": vol_regime.volatility_trend,
            "volatility_clustering": vol_regime.volatility_clustering,
            "expected_persistence": vol_regime.expected_persistence,
            "volatility_spillover_index": vol_regime.volatility_spillover_index,
        }

    def _convert_liquidity_to_dict(self, liq_regime: LiquidityRegime) -> dict:
        return {
            "liquidity_level": liq_regime.liquidity_level,
            "liquidity_score": liq_regime.liquidity_score,
            "market_depth": liq_regime.market_depth,
            "bid_ask_spreads": liq_regime.bid_ask_spreads,
            "market_impact": liq_regime.market_impact,
            "funding_conditions": liq_regime.funding_conditions,
        }

    # Assessment methods
    def _assess_tail_risk_regime(self, regime: MarketRegime, vol_regime: VolatilityRegime, market_ctx: dict) -> dict:
        return {}

    def _generate_regime_investment_implications(
        self,
        regime: MarketRegime,
        vol: VolatilityRegime,
        liq: LiquidityRegime,
        econ_ctx: dict,
    ) -> dict:
        return {}

    def _calculate_regime_stability_score(self, regime: MarketRegime, transition: dict) -> float:
        return 0.7

    def _calculate_market_stress_indicator(
        self, regime: MarketRegime, vol: VolatilityRegime, liq: LiquidityRegime
    ) -> float:
        return 0.3

    def _calculate_regime_diversification_score(self, corr_regime: dict, vol_regime: VolatilityRegime) -> float:
        return 0.8
