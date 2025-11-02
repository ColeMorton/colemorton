#!/usr/bin/env python3
"""
Comprehensive Macro-Economic Analysis Framework Demonstration

This script demonstrates the complete macro-economic analysis framework
that has been built for trading strategy enhancement. It showcases:

1. Business cycle analysis with statistical modeling
2. VIX volatility environment assessment
3. Market regime identification
4. Recession probability calculation
5. Integration with existing trade reports

The demo uses mock data to demonstrate capabilities without API dependencies.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.business_cycle_engine import BusinessCycleEngine, IndicatorScore
from utils.vix_volatility_analyzer import VIXVolatilityAnalyzer


class MacroEconomicFrameworkDemo:
    """
    Comprehensive demonstration of the macro-economic analysis framework
    """

    def __init__(self):
        self.business_cycle_engine = BusinessCycleEngine()
        self.vix_analyzer = VIXVolatilityAnalyzer()

    def demonstrate_comprehensive_analysis(self) -> dict[str, Any]:
        """
        Demonstrate the complete macro-economic analysis framework
        """
        print("🏦 Comprehensive Macro-Economic Analysis Framework Demo")
        print("=" * 60)

        # 1. Business Cycle Analysis
        print("\n📊 1. Business Cycle Analysis")
        print("-" * 30)
        business_cycle_result = self._demo_business_cycle_analysis()

        # 2. VIX Volatility Analysis
        print("\n📈 2. VIX Volatility Environment")
        print("-" * 30)
        vix_result = self._demo_vix_analysis()

        # 3. Recession Probability
        print("\n⚠️  3. Recession Probability Assessment")
        print("-" * 30)
        recession_result = self._demo_recession_probability()

        # 4. Market Regime Classification
        print("\n🎯 4. Market Regime Classification")
        print("-" * 30)
        regime_result = self._demo_market_regime()

        # 5. Integrated Analysis
        print("\n🔗 5. Integrated Macro Analysis")
        print("-" * 30)
        integrated_result = self._demo_integrated_analysis(
            business_cycle_result, vix_result, recession_result, regime_result
        )

        # 6. Trading Strategy Implications
        print("\n💼 6. Trading Strategy Implications")
        print("-" * 30)
        strategy_implications = self._demo_strategy_implications(integrated_result)

        # Compile comprehensive result
        comprehensive_result = {
            "framework_version": "1.0",
            "analysis_timestamp": datetime.now().isoformat(),
            "business_cycle_analysis": business_cycle_result,
            "vix_volatility_analysis": vix_result,
            "recession_probability": recession_result,
            "market_regime": regime_result,
            "integrated_assessment": integrated_result,
            "trading_implications": strategy_implications,
            "framework_capabilities": {
                "business_cycle_modeling": "NBER-style statistical analysis",
                "volatility_assessment": "VIX regime identification with mean reversion",
                "recession_modeling": "Multi-indicator probability assessment",
                "market_regime": "Statistical regime switching models",
                "integration_level": "Comprehensive cross-factor analysis",
            },
        }

        print("\n✅ Framework Demo Complete")
        print("Total Analysis Components: {len(comprehensive_result) - 2}")

        return comprehensive_result

    def _demo_business_cycle_analysis(self) -> dict[str, Any]:
        """Demonstrate business cycle analysis capabilities"""

        # Create realistic mock indicators
        leading_indicators = {
            "yield_curve_spread": {
                "observations": [
                    {"value": "1.2"},
                    {"value": "1.0"},
                    {"value": "0.8"},
                    {"value": "0.5"},
                    {"value": "0.3"},
                    {"value": "0.1"},
                ]
            },
            "consumer_confidence": {
                "observations": [
                    {"value": "95.5"},
                    {"value": "93.2"},
                    {"value": "91.8"},
                    {"value": "89.5"},
                    {"value": "87.1"},
                    {"value": "85.3"},
                ]
            },
            "stock_market": {
                "observations": [
                    {"value": "4200"},
                    {"value": "4150"},
                    {"value": "4100"},
                    {"value": "4050"},
                    {"value": "4000"},
                    {"value": "3950"},
                ]
            },
        }

        coincident_indicators = {
            "gdp": {
                "observations": [
                    {"value": "2.1"},
                    {"value": "1.9"},
                    {"value": "1.7"},
                    {"value": "1.5"},
                    {"value": "1.3"},
                    {"value": "1.1"},
                ]
            },
            "employment": {
                "observations": [
                    {"value": "150000"},
                    {"value": "145000"},
                    {"value": "140000"},
                    {"value": "135000"},
                    {"value": "130000"},
                    {"value": "125000"},
                ]
            },
            "industrial_production": {
                "observations": [
                    {"value": "105.2"},
                    {"value": "104.8"},
                    {"value": "104.4"},
                    {"value": "104.0"},
                    {"value": "103.6"},
                    {"value": "103.2"},
                ]
            },
        }

        lagging_indicators = {
            "unemployment_rate": {
                "observations": [
                    {"value": "3.8"},
                    {"value": "3.9"},
                    {"value": "4.0"},
                    {"value": "4.1"},
                    {"value": "4.2"},
                    {"value": "4.3"},
                ]
            },
            "cpi": {
                "observations": [
                    {"value": "2.4"},
                    {"value": "2.5"},
                    {"value": "2.6"},
                    {"value": "2.7"},
                    {"value": "2.8"},
                    {"value": "2.9"},
                ]
            },
            "prime_rate": {
                "observations": [
                    {"value": "5.5"},
                    {"value": "5.5"},
                    {"value": "5.75"},
                    {"value": "5.75"},
                    {"value": "6.0"},
                    {"value": "6.0"},
                ]
            },
        }

        # Run business cycle analysis
        result = self.business_cycle_engine.analyze_business_cycle(
            leading_indicators, coincident_indicators, lagging_indicators
        )

        # Extract key insights for display
        phase = result.get("business_cycle_phase")
        composite = result.get("composite_index", {})
        recession = result.get("recession_analysis")

        print(f"📈 Current Phase: {phase.phase_name.title()} (Confidence: {phase.phase_probability:.1%})")
        print(
            f"🎯 Composite Index: {composite.get('overall_composite', 0):.2f} ({composite.get('interpretation', 'N/A')})"
        )
        print(f"⚠️  Recession Risk: {recession.recession_probability:.1%} ({recession.signal_strength})")
        print(f"⏱️  Phase Duration: {phase.duration_months} months (Expected: {phase.expected_duration or 'Unknown'})")

        return result

    def _demo_vix_analysis(self) -> dict[str, Any]:
        """Demonstrate VIX volatility analysis"""

        # Create VIX time series showing elevated volatility
        mock_vix_data = {
            "observations": [
                {"date": "2024-07-30", "value": "15.2"},
                {"date": "2024-07-31", "value": "16.8"},
                {"date": "2024-08-01", "value": "18.5"},
                {"date": "2024-08-02", "value": "22.1"},
                {"date": "2024-08-03", "value": "24.3"},
                {"date": "2024-08-04", "value": "21.7"},
            ]
        }

        # Run VIX analysis
        result = self.vix_analyzer.analyze_volatility_environment(mock_vix_data)

        # Extract key insights
        regime = result.get("volatility_regime")
        current_vix = result.get("current_vix_level", 0)
        mean_reversion = result.get("mean_reversion_analysis", {})
        signals = result.get("trading_signals", [])

        print("📊 Current VIX: {current_vix}")
        print(f"🎭 Volatility Regime: {regime.regime_type.title()} (Confidence: {regime.regime_probability:.1%})")
        print(f"📈 Mean Reversion: {mean_reversion.get('reversion_strength', 'Unknown')} strength")
        print("🎯 Trading Signals: {len(signals)} generated")

        if signals:
            primary_signal = signals[0]
            print(
                f"   → Primary: {primary_signal.signal_type} {primary_signal.direction} (Confidence: {primary_signal.confidence:.1%})"
            )

        return result

    def _demo_recession_probability(self) -> dict[str, Any]:
        """Demonstrate recession probability calculation"""

        # Create mock recession indicator scores
        leading_scores = {
            "yield_curve": IndicatorScore(
                indicator_name="yield_curve",
                raw_value=0.1,  # Flattened curve
                normalized_score=-1.5,  # Concerning signal
                contribution_weight=0.25,
                trend_direction="deteriorating",
                significance_level=0.85,
            ),
            "consumer_confidence": IndicatorScore(
                indicator_name="consumer_confidence",
                raw_value=85.3,
                normalized_score=-1.0,  # Below average
                contribution_weight=0.20,
                trend_direction="deteriorating",
                significance_level=0.75,
            ),
        }

        coincident_scores = {
            "employment": IndicatorScore(
                indicator_name="employment",
                raw_value=125000,
                normalized_score=-0.5,  # Weakening
                contribution_weight=0.30,
                trend_direction="deteriorating",
                significance_level=0.70,
            )
        }

        # Calculate recession probability
        recession_signal = self.business_cycle_engine._calculate_recession_probability(
            leading_scores, coincident_scores
        )

        print(f"⚠️  Recession Probability: {recession_signal.recession_probability:.1%}")
        print("💪 Signal Strength: {recession_signal.signal_strength.title()}")
        print("⏰ Time Horizon: {recession_signal.time_horizon}")
        print(
            f"📊 Confidence Range: {recession_signal.confidence_interval[0]:.1%} - {recession_signal.confidence_interval[1]:.1%}"
        )
        print("🔑 Key Drivers: {', '.join(recession_signal.key_drivers)}")

        return {
            "recession_probability": recession_signal.recession_probability,
            "signal_strength": recession_signal.signal_strength,
            "time_horizon": recession_signal.time_horizon,
            "confidence_interval": recession_signal.confidence_interval,
            "key_drivers": recession_signal.key_drivers,
        }

    def _demo_market_regime(self) -> dict[str, Any]:
        """Demonstrate market regime classification"""

        # Mock market regime based on current conditions
        regime_data = {
            "regime_type": "transition",
            "volatility_environment": "elevated",
            "confidence_score": 0.72,
            "regime_duration_days": 18,
            "key_indicators": {
                "market_momentum": -0.3,
                "volatility_trend": 0.8,
                "breadth_indicators": -0.2,
                "risk_appetite": 0.1,
            },
            "regime_characteristics": [
                "Increased market uncertainty",
                "Elevated volatility levels",
                "Defensive positioning increasing",
                "Economic data mixed",
            ],
            "trading_implications": [
                "Reduce position sizing",
                "Increase hedging activities",
                "Focus on quality names",
                "Monitor regime shift signals",
            ],
        }

        print("🎭 Market Regime: {regime_data['regime_type'].title()}")
        print(f"🌪️  Volatility Environment: {regime_data['volatility_environment'].title()}")
        print("📊 Confidence: {regime_data['confidence_score']:.1%}")
        print("⏱️  Duration: {regime_data['regime_duration_days']} days")

        return regime_data

    def _demo_integrated_analysis(
        self, business_cycle: dict, vix: dict, recession: dict, regime: dict
    ) -> dict[str, Any]:
        """Demonstrate integrated cross-factor analysis"""

        # Calculate integrated assessment scores
        cycle_score = self._score_business_cycle(business_cycle)
        volatility_score = self._score_volatility_environment(vix)
        recession_score = 1.0 - recession.get("recession_probability", 0.2)  # Invert for consistency
        regime_score = regime.get("confidence_score", 0.7)

        # Weighted composite score
        composite_score = 0.3 * cycle_score + 0.25 * volatility_score + 0.25 * recession_score + 0.2 * regime_score

        # Overall assessment
        if composite_score > 0.7:
            overall_assessment = "favorable"
            risk_level = "low"
        elif composite_score > 0.5:
            overall_assessment = "neutral"
            risk_level = "moderate"
        elif composite_score > 0.3:
            overall_assessment = "cautionary"
            risk_level = "elevated"
        else:
            overall_assessment = "defensive"
            risk_level = "high"

        integrated_result = {
            "composite_score": composite_score,
            "overall_assessment": overall_assessment,
            "risk_level": risk_level,
            "component_scores": {
                "business_cycle": cycle_score,
                "volatility_environment": volatility_score,
                "recession_risk": recession_score,
                "market_regime": regime_score,
            },
            "cross_factor_analysis": {
                "cycle_volatility_correlation": "negative",
                "regime_recession_consistency": "aligned",
                "overall_coherence": "high",
            },
            "confidence_level": min(0.9, composite_score + 0.1),
        }

        print("🎯 Composite Score: {composite_score:.2f}")
        print("📊 Overall Assessment: {overall_assessment.title()}")
        print("⚠️  Risk Level: {risk_level.title()}")
        print(f"🔗 Factor Coherence: {integrated_result['cross_factor_analysis']['overall_coherence'].title()}")

        return integrated_result

    def _demo_strategy_implications(self, integrated_analysis: dict) -> dict[str, Any]:
        """Demonstrate trading strategy implications"""

        assessment = integrated_analysis.get("overall_assessment", "neutral")
        risk_level = integrated_analysis.get("risk_level", "moderate")
        composite_score = integrated_analysis.get("composite_score", 0.5)

        # Generate strategy recommendations based on assessment
        if assessment == "favorable":
            portfolio_stance = "risk_on"
            position_sizing = "standard_to_aggressive"
            sector_rotation = "growth_cyclicals"
            hedging_approach = "minimal"
        elif assessment == "neutral":
            portfolio_stance = "balanced"
            position_sizing = "standard"
            sector_rotation = "diversified"
            hedging_approach = "selective"
        elif assessment == "cautionary":
            portfolio_stance = "risk_aware"
            position_sizing = "reduced"
            sector_rotation = "quality_defensive"
            hedging_approach = "increased"
        else:  # defensive
            portfolio_stance = "risk_off"
            position_sizing = "conservative"
            sector_rotation = "defensive_utilities"
            hedging_approach = "comprehensive"

        # Specific trading recommendations
        trading_recommendations = []

        if composite_score < 0.4:
            trading_recommendations.extend(
                [
                    "Reduce overall portfolio beta",
                    "Increase cash allocation",
                    "Focus on dividend-paying stocks",
                    "Consider defensive sectors (utilities, consumer staples)",
                ]
            )
        elif composite_score > 0.7:
            trading_recommendations.extend(
                [
                    "Increase exposure to growth sectors",
                    "Consider leveraged ETFs for amplified exposure",
                    "Reduce hedging positions",
                    "Focus on momentum strategies",
                ]
            )
        else:
            trading_recommendations.extend(
                [
                    "Maintain balanced portfolio allocation",
                    "Use volatility for tactical rebalancing",
                    "Selective sector rotation based on fundamentals",
                    "Monitor for regime change signals",
                ]
            )

        strategy_implications = {
            "portfolio_stance": portfolio_stance,
            "position_sizing_approach": position_sizing,
            "sector_rotation_strategy": sector_rotation,
            "hedging_approach": hedging_approach,
            "risk_budget_adjustment": f"{(composite_score - 0.5) * 100:+.0f}%",
            "trading_recommendations": trading_recommendations,
            "monitoring_priorities": [
                "Business cycle transition signals",
                "Volatility regime changes",
                "Recession indicator divergences",
                "Market regime shift patterns",
            ],
            "strategy_confidence": integrated_analysis.get("confidence_level", 0.7),
        }

        print("💼 Portfolio Stance: {portfolio_stance.replace('_', ' ').title()}")
        print("📏 Position Sizing: {position_sizing.replace('_', ' ').title()}")
        print("🔄 Sector Strategy: {sector_rotation.replace('_', ' ').title()}")
        print("🛡️  Hedging: {hedging_approach.title()}")
        print("📊 Risk Budget: {strategy_implications['risk_budget_adjustment']}")
        print(f"🎯 Strategy Confidence: {strategy_implications['strategy_confidence']:.1%}")

        return strategy_implications

    def _score_business_cycle(self, business_cycle: dict) -> float:
        """Score business cycle health (0-1)"""
        phase = business_cycle.get("business_cycle_phase")
        composite = business_cycle.get("composite_index", {})

        if not phase:
            return 0.5

        # Score based on phase and composite
        phase_scores = {
            "expansion": 0.8,
            "peak": 0.6,
            "contraction": 0.2,
            "trough": 0.4,
        }

        base_score = phase_scores.get(phase.phase_name, 0.5)
        composite_adjustment = composite.get("overall_composite", 0) * 0.2

        return max(0.0, min(1.0, base_score + composite_adjustment))

    def _score_volatility_environment(self, vix: dict) -> float:
        """Score volatility environment favorability (0-1)"""
        regime = vix.get("volatility_regime")
        current_vix = vix.get("current_vix_level", 20)

        if not regime:
            return 0.5

        # Lower VIX generally better for risk assets
        vix_score = max(0.0, min(1.0, (30 - current_vix) / 20))

        # Regime stability bonus/penalty
        regime_scores = {
            "low": 0.9,
            "normal": 0.7,
            "elevated": 0.4,
            "extreme": 0.1,
            "crisis": 0.0,
        }

        regime_score = regime_scores.get(regime.regime_type, 0.5)

        return (vix_score + regime_score) / 2


def main():
    """Main demonstration entry point"""
    demo = MacroEconomicFrameworkDemo()

    # Run comprehensive demonstration
    results = demo.demonstrate_comprehensive_analysis()

    # Save results for reference
    output_path = Path(__file__).parent / "data" / "outputs" / "macro_analysis_demo.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n💾 Demo results saved to: {output_path}")
    print("\n🎉 Macro-Economic Analysis Framework Demo Complete!")
    print("\nFramework Capabilities Demonstrated:")
    print("✅ Business cycle analysis with statistical modeling")
    print("✅ VIX volatility environment assessment")
    print("✅ Recession probability calculation")
    print("✅ Market regime classification")
    print("✅ Integrated cross-factor analysis")
    print("✅ Trading strategy implications")

    return results


if __name__ == "__main__":
    main()
