#!/usr/bin/env python3
"""
Enhanced Economic Forecasting Framework
Multi-method forecasting with scenario analysis and probabilistic outcomes
Part of Phase 2 optimization for macro analysis system
"""

import json
from datetime import datetime
from typing import Any

import numpy as np


class EconomicForecastingEngine:
    """Advanced economic forecasting with multi-method approaches and scenario analysis"""

    def __init__(self, region: str = "US", forecast_horizon_quarters: int = 8):
        self.region = region
        self.forecast_horizon = forecast_horizon_quarters
        self.scenario_weights = {"base": 0.50, "bear": 0.25, "bull": 0.25}

        # Regional economic parameters
        self.regional_params = self._load_regional_parameters()

    def _load_regional_parameters(self) -> dict[str, Any]:
        """Load region-specific economic parameters"""
        # Default US parameters - can be extended for other regions
        return {
            "US": {
                "trend_growth": 2.0,
                "natural_unemployment": 4.0,
                "inflation_target": 2.0,
                "potential_growth_volatility": 0.5,
                "cycle_duration_quarters": 40,
                "recovery_speed": 0.7,
            },
            "EU": {
                "trend_growth": 1.2,
                "natural_unemployment": 6.5,
                "inflation_target": 2.0,
                "potential_growth_volatility": 0.4,
                "cycle_duration_quarters": 36,
                "recovery_speed": 0.5,
            },
        }.get(
            self.region,
            {
                "trend_growth": 2.0,
                "natural_unemployment": 5.0,
                "inflation_target": 2.0,
                "potential_growth_volatility": 0.4,
                "cycle_duration_quarters": 38,
                "recovery_speed": 0.6,
            },
        )

    def generate_enhanced_forecasts(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate comprehensive economic forecasts with multiple methods"""

        # Extract current indicators
        current_indicators = self._extract_current_indicators(discovery_data, analysis_data)

        # Generate scenario-based forecasts
        scenario_forecasts = self._generate_scenario_forecasts(current_indicators)

        # Create probabilistic outcomes
        probabilistic_outcomes = self._calculate_probabilistic_outcomes(scenario_forecasts)

        # Generate forward-looking indicators
        forward_indicators = self._generate_forward_indicators(current_indicators)

        # Policy impact simulations
        policy_simulations = self._simulate_policy_impacts(current_indicators)

        # Calculate forecast confidence
        forecast_confidence = self._calculate_forecast_confidence(current_indicators, scenario_forecasts)

        return {
            "forecast_metadata": {
                "methodology": "multi_method_scenario_based_forecasting",
                "horizon_quarters": self.forecast_horizon,
                "base_date": datetime.now().isoformat(),
                "region": self.region,
                "forecast_confidence": forecast_confidence,
            },
            "scenario_based_forecasts": scenario_forecasts,
            "probabilistic_outcomes": probabilistic_outcomes,
            "forward_looking_indicators": forward_indicators,
            "policy_impact_simulations": policy_simulations,
            "integrated_forecast_summary": self._create_forecast_summary(
                scenario_forecasts, probabilistic_outcomes, forward_indicators
            ),
        }

    def _extract_current_indicators(self, discovery_data: dict, analysis_data: dict) -> dict[str, Any]:
        """Extract current economic indicators from discovery and analysis data"""

        # GDP data
        gdp_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("gdp_data", {})
        )
        current_gdp = 2.0  # Default
        if gdp_data.get("observations"):
            latest_gdp = gdp_data["observations"][0]
            current_gdp = latest_gdp.get("value", 2.0)

        # Employment data
        employment_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("employment_data", {})
        )
        current_unemployment = 4.0  # Default
        if employment_data.get("unemployment_data", {}).get("observations"):
            current_unemployment = employment_data["unemployment_data"]["observations"][0].get("value", 4.0)

        # Inflation data
        inflation_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("inflation_data", {})
        )
        current_inflation = 2.5  # Default
        if inflation_data.get("cpi_data", {}).get("observations"):
            current_inflation = inflation_data["cpi_data"]["observations"][0].get("value", 2.5)

        # Policy rate
        policy_data = (
            discovery_data.get("cli_comprehensive_analysis", {})
            .get("central_bank_economic_data", {})
            .get("monetary_policy_data", {})
        )
        current_policy_rate = 4.5  # Default
        if policy_data.get("fed_funds_rate", {}).get("current_rate"):
            current_policy_rate = policy_data["fed_funds_rate"]["current_rate"].get("value", 4.5)

        # Recession probability
        recession_prob = (
            discovery_data.get("economic_indicators", {}).get("composite_scores", {}).get("recession_probability", 0.25)
        )

        return {
            "gdp_growth": current_gdp,
            "unemployment_rate": current_unemployment,
            "inflation_rate": current_inflation,
            "policy_rate": current_policy_rate,
            "recession_probability": recession_prob,
            "trend_growth": self.regional_params["trend_growth"],
            "natural_unemployment": self.regional_params["natural_unemployment"],
            "inflation_target": self.regional_params["inflation_target"],
        }

    def _generate_scenario_forecasts(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Generate base/bear/bull scenario forecasts"""

        current_gdp = indicators["gdp_growth"]
        current_unemployment = indicators["unemployment_rate"]
        current_inflation = indicators["inflation_rate"]
        current_policy_rate = indicators["policy_rate"]
        recession_prob = indicators["recession_probability"]

        # Base Case Scenario (most likely)
        base_scenario = self._generate_base_scenario(indicators)

        # Bear Case Scenario (economic stress)
        bear_scenario = self._generate_bear_scenario(indicators, recession_prob)

        # Bull Case Scenario (economic acceleration)
        bull_scenario = self._generate_bull_scenario(indicators)

        return {
            "base_case": {
                "probability": self.scenario_weights["base"],
                "description": "Most likely economic trajectory based on current indicators",
                "forecasts": base_scenario,
                "key_assumptions": [
                    f"GDP growth moderates to trend of {self.regional_params['trend_growth']}%",
                    f"Unemployment stabilizes near natural rate of {self.regional_params['natural_unemployment']}%",
                    f"Inflation converges to target of {self.regional_params['inflation_target']}%",
                    "Policy remains data-dependent with gradual normalization",
                ],
            },
            "bear_case": {
                "probability": self.scenario_weights["bear"],
                "description": "Economic stress scenario with potential recession",
                "forecasts": bear_scenario,
                "key_assumptions": [
                    f"Recession probability {recession_prob:.0%} materializes",
                    "Employment deteriorates significantly",
                    "Policy becomes accommodative to support growth",
                    "Financial conditions tighten substantially",
                ],
            },
            "bull_case": {
                "probability": self.scenario_weights["bull"],
                "description": "Economic acceleration scenario with above-trend growth",
                "forecasts": bull_scenario,
                "key_assumptions": [
                    "Productivity gains accelerate growth potential",
                    "Employment remains robust with wage growth",
                    "Inflation remains contained despite strong growth",
                    "Policy tightening more gradual than feared",
                ],
            },
        }

    def _generate_base_scenario(self, indicators: dict[str, Any]) -> dict[str, list[float]]:
        """Generate base case quarterly forecasts"""

        gdp_path = []
        unemployment_path = []
        inflation_path = []
        policy_rate_path = []

        # Starting values
        current_gdp = indicators["gdp_growth"]
        current_unemployment = indicators["unemployment_rate"]
        current_inflation = indicators["inflation_rate"]
        current_policy_rate = indicators["policy_rate"]

        # Trend targets
        trend_growth = self.regional_params["trend_growth"]
        natural_unemployment = self.regional_params["natural_unemployment"]
        inflation_target = self.regional_params["inflation_target"]

        for quarter in range(self.forecast_horizon):
            # GDP: gradual convergence to trend with some volatility
            gdp_target = trend_growth
            gdp_adjustment = (gdp_target - current_gdp) * 0.15  # 15% quarterly adjustment
            current_gdp += gdp_adjustment + np.random.normal(0, 0.2)
            gdp_path.append(round(current_gdp, 2))

            # Unemployment: Phillips curve relationship with some lag
            unemployment_target = natural_unemployment
            unemployment_adjustment = (unemployment_target - current_unemployment) * 0.1
            # GDP impact on unemployment (Okun's law approximation)
            gdp_impact = -(current_gdp - trend_growth) * 0.3
            current_unemployment += unemployment_adjustment + gdp_impact + np.random.normal(0, 0.1)
            current_unemployment = max(2.5, min(8.5, current_unemployment))  # Dynamic bounds
            unemployment_path.append(round(current_unemployment, 2))

            # Inflation: gradual convergence to target with some persistence
            inflation_adjustment = (inflation_target - current_inflation) * 0.12
            current_inflation += inflation_adjustment + np.random.normal(0, 0.15)
            inflation_path.append(round(current_inflation, 2))

            # Policy rate: Taylor rule approximation
            neutral_rate = inflation_target + 1.0  # Approximate neutral rate
            inflation_gap = current_inflation - inflation_target
            output_gap = (current_gdp - trend_growth) / trend_growth
            taylor_rate = neutral_rate + 1.5 * inflation_gap + 0.5 * output_gap

            rate_adjustment = (taylor_rate - current_policy_rate) * 0.2  # Gradual adjustment
            current_policy_rate += rate_adjustment
            current_policy_rate = max(0.0, min(8.0, current_policy_rate))  # Bounds
            policy_rate_path.append(round(current_policy_rate, 2))

        return {
            "gdp_growth": gdp_path,
            "unemployment_rate": unemployment_path,
            "inflation_rate": inflation_path,
            "policy_rate": policy_rate_path,
        }

    def _generate_bear_scenario(self, indicators: dict[str, Any], recession_prob: float) -> dict[str, list[float]]:
        """Generate bear case with recession scenario"""

        # Start with base scenario structure but apply stress
        base_forecasts = self._generate_base_scenario(indicators)

        # Apply recession stress in first 4 quarters if recession probability > 25%
        recession_intensity = min(recession_prob * 2.0, 1.0)  # Scale recession impact

        gdp_path = []
        unemployment_path = []
        inflation_path = []
        policy_rate_path = []

        for quarter, (gdp, unemployment, inflation, policy_rate) in enumerate(
            zip(
                base_forecasts["gdp_growth"],
                base_forecasts["unemployment_rate"],
                base_forecasts["inflation_rate"],
                base_forecasts["policy_rate"],
                strict=False,
            )
        ):
            # Apply recession stress in first half of forecast
            if quarter < 4:
                stress_factor = recession_intensity * (1 - quarter / 4.0)  # Declining stress

                # GDP stress: significant contraction
                gdp_stress = gdp - stress_factor * (3.0 + gdp)  # Deeper contraction for higher growth
                gdp_path.append(round(gdp_stress, 2))

                # Unemployment stress: significant rise
                unemployment_stress = unemployment + stress_factor * 3.0  # Up to 3pp increase
                unemployment_path.append(round(min(unemployment_stress, 10.0), 2))

                # Inflation stress: disinflationary pressure
                inflation_stress = inflation - stress_factor * 1.5  # Disinflation
                inflation_path.append(round(max(inflation_stress, -1.0), 2))

                # Policy rate stress: aggressive accommodation
                policy_stress = policy_rate - stress_factor * (policy_rate - 0.25)  # Toward zero
                policy_rate_path.append(round(max(policy_stress, 0.0), 2))

            else:
                # Recovery phase: gradual improvement
                recovery_factor = (quarter - 4) / 4.0 * self.regional_params["recovery_speed"]

                gdp_recovery = gdp + recovery_factor * 1.0  # Gradual recovery
                gdp_path.append(round(gdp_recovery, 2))

                unemployment_recovery = unemployment - recovery_factor * 0.5  # Slow employment recovery
                unemployment_path.append(
                    round(
                        max(
                            unemployment_recovery,
                            indicators["natural_unemployment"] - 1.0,
                        ),
                        2,
                    )
                )

                inflation_path.append(round(inflation, 2))  # Base inflation
                policy_rate_path.append(round(policy_rate, 2))  # Base policy

        return {
            "gdp_growth": gdp_path,
            "unemployment_rate": unemployment_path,
            "inflation_rate": inflation_path,
            "policy_rate": policy_rate_path,
        }

    def _generate_bull_scenario(self, indicators: dict[str, Any]) -> dict[str, list[float]]:
        """Generate bull case with accelerated growth"""

        # Start with base scenario and apply positive shocks
        base_forecasts = self._generate_base_scenario(indicators)

        gdp_path = []
        unemployment_path = []
        inflation_path = []
        policy_rate_path = []

        for quarter, (gdp, unemployment, inflation, policy_rate) in enumerate(
            zip(
                base_forecasts["gdp_growth"],
                base_forecasts["unemployment_rate"],
                base_forecasts["inflation_rate"],
                base_forecasts["policy_rate"],
                strict=False,
            )
        ):
            # Apply positive productivity shock
            productivity_boost = 0.8 * (1 - quarter / self.forecast_horizon)  # Declining boost

            # GDP boost: above-trend growth
            gdp_boost = gdp + productivity_boost
            gdp_path.append(round(min(gdp_boost, 5.0), 2))  # Cap at 5%

            # Unemployment: faster decline to natural rate
            unemployment_boost = unemployment - productivity_boost * 0.3
            natural_unemployment = self.regional_params["natural_unemployment"]
            unemployment_path.append(round(max(unemployment_boost, natural_unemployment - 1.5), 2))  # Dynamic floor

            # Inflation: modest increase but contained
            inflation_boost = inflation + productivity_boost * 0.2  # Limited passthrough
            inflation_path.append(round(min(inflation_boost, 4.0), 2))  # Cap at 4%

            # Policy rate: more gradual tightening
            policy_boost = policy_rate + productivity_boost * 0.1  # Slower tightening
            policy_rate_path.append(round(min(policy_boost, 6.0), 2))  # Cap at 6%

        return {
            "gdp_growth": gdp_path,
            "unemployment_rate": unemployment_path,
            "inflation_rate": inflation_path,
            "policy_rate": policy_rate_path,
        }

    def _calculate_probabilistic_outcomes(self, scenario_forecasts: dict[str, Any]) -> dict[str, Any]:
        """Calculate probability-weighted outcomes and confidence intervals"""

        indicators = [
            "gdp_growth",
            "unemployment_rate",
            "inflation_rate",
            "policy_rate",
        ]
        probabilistic_outcomes = {}

        for indicator in indicators:
            # Extract forecast paths
            base_path = scenario_forecasts["base_case"]["forecasts"][indicator]
            bear_path = scenario_forecasts["bear_case"]["forecasts"][indicator]
            bull_path = scenario_forecasts["bull_case"]["forecasts"][indicator]

            # Calculate probability-weighted path
            weighted_path = []
            confidence_intervals = []

            for quarter in range(self.forecast_horizon):
                base_val = base_path[quarter]
                bear_val = bear_path[quarter]
                bull_val = bull_path[quarter]

                # Probability-weighted expected value
                expected_val = (
                    self.scenario_weights["base"] * base_val
                    + self.scenario_weights["bear"] * bear_val
                    + self.scenario_weights["bull"] * bull_val
                )
                weighted_path.append(round(expected_val, 2))

                # Confidence intervals (10th and 90th percentiles)
                values = [base_val, bear_val, bull_val]
                weights = [
                    self.scenario_weights["base"],
                    self.scenario_weights["bear"],
                    self.scenario_weights["bull"],
                ]

                # Simple confidence interval approximation
                lower_bound = min(values)
                upper_bound = max(values)
                confidence_intervals.append(
                    {
                        "lower_10th": round(lower_bound, 2),
                        "upper_90th": round(upper_bound, 2),
                        "range_width": round(upper_bound - lower_bound, 2),
                    }
                )

            probabilistic_outcomes[indicator] = {
                "expected_path": weighted_path,
                "confidence_intervals": confidence_intervals,
                "scenario_dispersion": self._calculate_scenario_dispersion(base_path, bear_path, bull_path),
            }

        return probabilistic_outcomes

    def _calculate_scenario_dispersion(
        self, base_path: list[float], bear_path: list[float], bull_path: list[float]
    ) -> dict[str, float]:
        """Calculate dispersion metrics across scenarios"""

        # Calculate standard deviation across scenarios for each quarter
        quarterly_stds = []
        for quarter in range(len(base_path)):
            values = [base_path[quarter], bear_path[quarter], bull_path[quarter]]
            quarterly_stds.append(np.std(values))

        return {
            "average_std_deviation": round(np.mean(quarterly_stds), 3),
            "maximum_std_deviation": round(np.max(quarterly_stds), 3),
            "dispersion_trend": ("increasing" if quarterly_stds[-1] > quarterly_stds[0] else "decreasing"),
        }

    def _generate_forward_indicators(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Generate forward-looking economic indicators"""

        current_gdp = indicators["gdp_growth"]
        current_unemployment = indicators["unemployment_rate"]
        current_inflation = indicators["inflation_rate"]
        recession_prob = indicators["recession_probability"]

        # Leading indicator composite
        leading_composite = self._calculate_leading_composite(indicators)

        # Consumer expectations
        consumer_expectations = self._project_consumer_expectations(indicators)

        # Business investment intentions
        business_investment = self._project_business_investment(indicators)

        # Financial conditions index
        financial_conditions = self._calculate_financial_conditions_index(indicators)

        return {
            "leading_indicators_composite": {
                "current_level": round(leading_composite, 1),
                "trend": "declining" if leading_composite < 100 else "rising",
                "recession_signal": leading_composite < 95,
                "confidence": 0.85,
            },
            "consumer_expectations": consumer_expectations,
            "business_investment_intentions": business_investment,
            "financial_conditions_index": financial_conditions,
            "integrated_nowcast": {
                "nowcast_gdp": round(current_gdp + (leading_composite - 100) * 0.02, 2),
                "nowcast_confidence": 0.75,
                "revision_risk": ("medium" if abs(leading_composite - 100) > 5 else "low"),
            },
        }

    def _calculate_leading_composite(self, indicators: dict[str, Any]) -> float:
        """Calculate composite leading indicator"""

        # Simple composite based on current indicators
        gdp_component = (indicators["gdp_growth"] / indicators["trend_growth"]) * 100
        unemployment_component = (indicators["natural_unemployment"] / indicators["unemployment_rate"]) * 100
        inflation_component = 100 - abs(indicators["inflation_rate"] - indicators["inflation_target"]) * 10

        # Recession probability impact
        recession_impact = (1 - indicators["recession_probability"]) * 100

        # Weighted average
        composite = (
            0.3 * gdp_component + 0.25 * unemployment_component + 0.2 * inflation_component + 0.25 * recession_impact
        )

        return composite

    def _project_consumer_expectations(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Project consumer expectations"""

        # Base consumer confidence from economic conditions
        natural_rate = indicators["natural_unemployment"]
        base_confidence = 100 - (indicators["unemployment_rate"] - natural_rate) * 5
        base_confidence -= (indicators["inflation_rate"] - indicators["inflation_target"]) * 3
        base_confidence = max(40, min(base_confidence, 120))

        return {
            "consumer_confidence_projection": round(base_confidence, 1),
            "spending_intentions": "positive" if base_confidence > 90 else "cautious",
            "employment_expectations": (
                "improving" if indicators["unemployment_rate"] < indicators["natural_unemployment"] else "stable"
            ),
            "confidence": 0.78,
        }

    def _project_business_investment(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Project business investment intentions"""

        # Investment based on growth expectations and financing costs
        trend_growth = indicators["trend_growth"]
        investment_index = 100 + (indicators["gdp_growth"] - trend_growth) * 10
        neutral_rate = indicators["inflation_target"] + 1.0
        investment_index -= (indicators["policy_rate"] - neutral_rate) * 5  # Cost of capital impact
        investment_index = max(60, min(investment_index, 140))

        return {
            "investment_intentions_index": round(investment_index, 1),
            "capex_outlook": "expanding" if investment_index > 100 else "cautious",
            "financing_conditions": ("favorable" if indicators["policy_rate"] < neutral_rate + 1.0 else "restrictive"),
            "confidence": 0.82,
        }

    def _calculate_financial_conditions_index(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Calculate financial conditions index"""

        # Simplified financial conditions based on policy rate and growth
        neutral_rate = indicators["inflation_target"] + 1.0
        trend_growth = indicators["trend_growth"]
        fci = 100 - (indicators["policy_rate"] - neutral_rate) * 8  # Tighter conditions = lower index
        fci += (indicators["gdp_growth"] - trend_growth) * 5  # Stronger growth = easier conditions
        fci = max(50, min(fci, 150))

        return {
            "financial_conditions_index": round(fci, 1),
            "conditions_assessment": ("loose" if fci > 110 else "tight" if fci < 90 else "neutral"),
            "credit_availability": "ample" if fci > 105 else "limited",
            "market_stress": "low" if fci > 95 else "elevated",
            "confidence": 0.80,
        }

    def _simulate_policy_impacts(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Simulate various policy scenarios and their impacts"""

        # Rate cut scenario
        rate_cut_impact = self._simulate_rate_change(indicators, -0.5)

        # Rate hike scenario
        rate_hike_impact = self._simulate_rate_change(indicators, 0.5)

        # Fiscal stimulus scenario
        fiscal_stimulus = self._simulate_fiscal_policy(indicators, stimulus=True)

        # Trade policy scenario
        trade_impact = self._simulate_trade_policy(indicators)

        return {
            "monetary_policy_scenarios": {
                "50bp_rate_cut": rate_cut_impact,
                "50bp_rate_hike": rate_hike_impact,
                "policy_effectiveness": ("high" if indicators["policy_rate"] > 2.0 else "limited"),
            },
            "fiscal_policy_scenarios": fiscal_stimulus,
            "trade_policy_scenarios": trade_impact,
            "policy_coordination": {
                "monetary_fiscal_alignment": (
                    "supportive"
                    if indicators["inflation_rate"] < indicators["inflation_target"] + 1.0
                    else "conflicted"
                ),
                "international_coordination": "limited",
                "policy_uncertainty_index": round(50 + indicators["recession_probability"] * 100, 0),
            },
        }

    def _simulate_rate_change(self, indicators: dict[str, Any], rate_change: float) -> dict[str, Any]:
        """Simulate impact of interest rate changes"""

        # GDP impact (with lag)
        gdp_impact = -rate_change * 0.8  # 50bp = 40bp impact on growth
        new_gdp = indicators["gdp_growth"] + gdp_impact

        # Unemployment impact (Okun's law)
        unemployment_impact = -gdp_impact * 0.4
        new_unemployment = indicators["unemployment_rate"] + unemployment_impact

        # Inflation impact
        inflation_impact = gdp_impact * 0.3  # Phillips curve
        new_inflation = indicators["inflation_rate"] + inflation_impact

        return {
            "gdp_impact": round(gdp_impact, 2),
            "unemployment_impact": round(unemployment_impact, 2),
            "inflation_impact": round(inflation_impact, 2),
            "new_gdp_forecast": round(new_gdp, 2),
            "new_unemployment_forecast": round(new_unemployment, 2),
            "new_inflation_forecast": round(new_inflation, 2),
            "transmission_lag_quarters": 2,
            "peak_impact_quarters": 4,
        }

    def _simulate_fiscal_policy(self, indicators: dict[str, Any], stimulus: bool = True) -> dict[str, Any]:
        """Simulate fiscal policy impacts"""

        multiplier = 1.5 if stimulus else -1.2  # Stimulus vs austerity multiplier
        fiscal_impulse = 2.0 if stimulus else -1.5  # % of GDP

        gdp_impact = fiscal_impulse * multiplier * 0.01  # Convert to growth impact
        new_gdp = indicators["gdp_growth"] + gdp_impact

        # Inflation impact
        inflation_impact = gdp_impact * 0.4 if stimulus else gdp_impact * 0.2
        new_inflation = indicators["inflation_rate"] + inflation_impact

        return {
            "fiscal_impulse_pct_gdp": fiscal_impulse,
            "multiplier_effect": multiplier,
            "gdp_impact": round(gdp_impact, 2),
            "inflation_impact": round(inflation_impact, 2),
            "new_gdp_forecast": round(new_gdp, 2),
            "new_inflation_forecast": round(new_inflation, 2),
            "debt_impact": "increasing" if stimulus else "decreasing",
            "sustainability_risk": "medium" if abs(fiscal_impulse) > 2.0 else "low",
        }

    def _simulate_trade_policy(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Simulate trade policy impacts"""

        # Assume trade tensions increase costs and reduce growth
        trade_tension_impact = -0.3  # GDP impact
        inflation_impact = 0.5  # Import price impact

        new_gdp = indicators["gdp_growth"] + trade_tension_impact
        new_inflation = indicators["inflation_rate"] + inflation_impact

        return {
            "trade_tension_gdp_impact": round(trade_tension_impact, 2),
            "import_price_impact": round(inflation_impact, 2),
            "new_gdp_forecast": round(new_gdp, 2),
            "new_inflation_forecast": round(new_inflation, 2),
            "supply_chain_disruption": "moderate",
            "competitiveness_impact": "negative",
        }

    def _calculate_forecast_confidence(self, indicators: dict[str, Any], scenario_forecasts: dict[str, Any]) -> float:
        """Calculate overall forecast confidence"""

        confidence_factors = []

        # Data quality factor
        data_quality = 0.85  # Base assumption
        confidence_factors.append(data_quality)

        # Economic stability factor
        volatility = abs(indicators["gdp_growth"] - indicators["trend_growth"])
        stability_factor = max(0.6, 1.0 - volatility * 0.1)
        confidence_factors.append(stability_factor)

        # Scenario dispersion factor (lower dispersion = higher confidence)
        base_gdp = np.mean(scenario_forecasts["base_case"]["forecasts"]["gdp_growth"])
        bear_gdp = np.mean(scenario_forecasts["bear_case"]["forecasts"]["gdp_growth"])
        bull_gdp = np.mean(scenario_forecasts["bull_case"]["forecasts"]["gdp_growth"])

        scenario_range = bull_gdp - bear_gdp
        dispersion_factor = max(0.5, 1.0 - scenario_range * 0.05)
        confidence_factors.append(dispersion_factor)

        # Recession probability factor (higher uncertainty near turning points)
        recession_factor = 1.0 - indicators["recession_probability"] * 0.3
        confidence_factors.append(recession_factor)

        # Calculate weighted average
        overall_confidence = np.mean(confidence_factors)

        return round(overall_confidence, 3)

    def _create_forecast_summary(
        self,
        scenario_forecasts: dict[str, Any],
        probabilistic_outcomes: dict[str, Any],
        forward_indicators: dict[str, Any],
    ) -> dict[str, Any]:
        """Create integrated forecast summary"""

        # Extract key forecasts
        base_gdp_path = scenario_forecasts["base_case"]["forecasts"]["gdp_growth"]
        expected_gdp_path = probabilistic_outcomes["gdp_growth"]["expected_path"]

        # Calculate growth trajectory
        current_quarter = 0
        one_year = 4
        two_year = 7

        return {
            "growth_trajectory": {
                "current_quarter_forecast": (expected_gdp_path[current_quarter] if expected_gdp_path else 2.0),
                "one_year_forecast": (expected_gdp_path[one_year] if len(expected_gdp_path) > one_year else 2.0),
                "two_year_forecast": (expected_gdp_path[two_year] if len(expected_gdp_path) > two_year else 2.0),
                "average_growth_forecast": round(np.mean(expected_gdp_path), 2),
            },
            "key_themes": [
                "Scenario-based analysis shows significant uncertainty around central forecasts",
                f"Leading indicators suggest {'economic momentum building' if forward_indicators['leading_indicators_composite']['current_level'] > 100 else 'economic softening ahead'}",
                f"Policy transmission remains {'effective' if forward_indicators['financial_conditions_index']['financial_conditions_index'] > 90 else 'constrained'} under current conditions",
                "Forward-looking indicators provide early warning signals for policy adjustments",
            ],
            "risk_assessment": {
                "upside_risks": [
                    "Productivity acceleration",
                    "Consumer resilience",
                    "Policy coordination",
                ],
                "downside_risks": [
                    "Recession materialization",
                    "Policy errors",
                    "External shocks",
                ],
                "key_monitoring_indicators": [
                    "Leading composite index",
                    "Financial conditions",
                    "Consumer expectations",
                ],
            },
            "policy_implications": [
                "Scenario diversity suggests need for flexible policy approach",
                "Forward indicators provide early signals for policy adjustment timing",
                "Policy effectiveness varies significantly across economic conditions",
            ],
        }


# Testing and validation functions
def validate_forecasting_engine():
    """Validate the forecasting engine with sample data"""

    # Sample discovery data
    sample_discovery = {
        "cli_comprehensive_analysis": {
            "central_bank_economic_data": {
                "gdp_data": {"observations": [{"value": 2.5}]},
                "employment_data": {"unemployment_data": {"observations": [{"value": 4.2}]}},
                "inflation_data": {"cpi_data": {"observations": [{"value": 2.8}]}},
                "monetary_policy_data": {"fed_funds_rate": {"current_rate": {"value": 4.5}}},
            }
        },
        "economic_indicators": {"composite_scores": {"recession_probability": 0.25}},
    }

    # Sample analysis data
    sample_analysis = {}

    # Create engine and generate forecasts
    engine = EconomicForecastingEngine("US", 8)
    forecasts = engine.generate_enhanced_forecasts(sample_discovery, sample_analysis)

    return forecasts


if __name__ == "__main__":
    # Run validation
    test_forecasts = validate_forecasting_engine()
    print(json.dumps(test_forecasts, indent=2))
