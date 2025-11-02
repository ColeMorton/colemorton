#!/usr/bin/env python3
"""
Comprehensive Geopolitical Risk Integration Framework
Quantified geopolitical risk analysis with economic impact modeling
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
class GeopoliticalRiskEvent:
    """Individual geopolitical risk event structure"""

    event_type: str  # 'trade_war', 'sanctions', 'conflict', 'policy_shift'
    probability: float  # 0-1 probability of occurrence
    severity: str  # 'low', 'moderate', 'high', 'extreme'
    time_horizon: str  # 'immediate', '3m', '6m', '12m', '24m'
    affected_regions: list[str]  # Regions impacted
    economic_channels: list[str]  # How it affects economy
    confidence: float  # Confidence in assessment


@dataclass
class EconomicImpactAssessment:
    """Economic impact assessment for geopolitical risks"""

    gdp_impact: float  # GDP growth impact (percentage points)
    inflation_impact: float  # Inflation impact (percentage points)
    trade_impact: float  # Trade volume impact (percentage)
    currency_impact: float  # Currency impact (percentage)
    market_impact: float  # Market impact (percentage)
    duration_months: int  # Expected duration of impact


@dataclass
class ContagionAnalysis:
    """Cross-regional contagion analysis"""

    contagion_probability: float
    transmission_channels: list[str]
    affected_regions: list[str]
    severity_multiplier: float
    time_to_transmission: int  # Months


class GeopoliticalRiskEngine:
    """Comprehensive geopolitical risk analysis and economic impact modeling"""

    def __init__(self, region: str = "US"):
        self.region = region

        # Risk categorization framework
        self.risk_categories = {
            "trade_tensions": {
                "base_probability": 0.6,
                "severity_multiplier": 1.2,
                "economic_channels": [
                    "trade_flows",
                    "supply_chains",
                    "investment",
                    "sentiment",
                ],
                "typical_duration": 24,  # months
            },
            "sanctions": {
                "base_probability": 0.3,
                "severity_multiplier": 1.8,
                "economic_channels": [
                    "financial_flows",
                    "commodity_prices",
                    "trade_flows",
                ],
                "typical_duration": 36,
            },
            "military_conflict": {
                "base_probability": 0.15,
                "severity_multiplier": 2.5,
                "economic_channels": [
                    "commodity_prices",
                    "safe_haven_flows",
                    "supply_chains",
                    "sentiment",
                ],
                "typical_duration": 12,
            },
            "policy_uncertainty": {
                "base_probability": 0.7,
                "severity_multiplier": 0.8,
                "economic_channels": ["investment", "sentiment", "currency_volatility"],
                "typical_duration": 18,
            },
            "cyber_warfare": {
                "base_probability": 0.4,
                "severity_multiplier": 1.5,
                "economic_channels": [
                    "financial_infrastructure",
                    "supply_chains",
                    "sentiment",
                ],
                "typical_duration": 6,
            },
            "energy_disruption": {
                "base_probability": 0.25,
                "severity_multiplier": 2.0,
                "economic_channels": ["commodity_prices", "inflation", "supply_chains"],
                "typical_duration": 12,
            },
        }

        # Regional vulnerability factors
        self.regional_vulnerabilities = {
            "US": {
                "trade_dependency": 0.3,
                "energy_dependence": 0.4,
                "financial_centrality": 0.9,
                "safe_haven_status": 0.8,
                "policy_stability": 0.6,
            },
            "EU": {
                "trade_dependency": 0.8,
                "energy_dependence": 0.7,
                "financial_centrality": 0.6,
                "safe_haven_status": 0.3,
                "policy_stability": 0.7,
            },
            "ASIA": {
                "trade_dependency": 0.9,
                "energy_dependence": 0.8,
                "financial_centrality": 0.4,
                "safe_haven_status": 0.2,
                "policy_stability": 0.5,
            },
            "EMERGING_MARKETS": {
                "trade_dependency": 0.9,
                "energy_dependence": 0.6,
                "financial_centrality": 0.2,
                "safe_haven_status": 0.1,
                "policy_stability": 0.4,
            },
        }

        # Economic transmission channels with impact coefficients
        self.transmission_channels = {
            "trade_flows": {
                "gdp_coefficient": -0.15,  # -15% trade = -0.15pp GDP
                "inflation_coefficient": 0.1,  # Supply constraints
                "duration_factor": 1.2,
            },
            "supply_chains": {
                "gdp_coefficient": -0.08,
                "inflation_coefficient": 0.15,
                "duration_factor": 0.8,
            },
            "commodity_prices": {
                "gdp_coefficient": -0.05,
                "inflation_coefficient": 0.25,
                "duration_factor": 0.6,
            },
            "financial_flows": {
                "gdp_coefficient": -0.12,
                "inflation_coefficient": -0.05,  # Disinflationary
                "duration_factor": 1.5,
            },
            "sentiment": {
                "gdp_coefficient": -0.06,
                "inflation_coefficient": 0.02,
                "duration_factor": 0.4,
            },
            "investment": {
                "gdp_coefficient": -0.10,
                "inflation_coefficient": -0.03,
                "duration_factor": 2.0,
            },
        }

        # Contagion mapping
        self.contagion_matrix = {
            "US": {"EU": 0.7, "ASIA": 0.8, "EMERGING_MARKETS": 0.9},
            "EU": {"US": 0.6, "ASIA": 0.5, "EMERGING_MARKETS": 0.7},
            "ASIA": {"US": 0.7, "EU": 0.5, "EMERGING_MARKETS": 0.8},
            "EMERGING_MARKETS": {"US": 0.4, "EU": 0.3, "ASIA": 0.6},
        }

    def analyze_geopolitical_risks(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Comprehensive geopolitical risk analysis"""

        # Extract current geopolitical context
        current_context = self._extract_geopolitical_context(discovery_data, analysis_data)

        # Identify and quantify active risk factors
        active_risks = self._identify_active_risks(current_context)

        # Calculate economic impact assessments
        economic_impacts = self._calculate_economic_impacts(active_risks, current_context)

        # Analyze cross-regional contagion
        contagion_analysis = self._analyze_contagion_risks(active_risks, current_context)

        # Generate risk scenarios
        risk_scenarios = self._generate_risk_scenarios(active_risks, economic_impacts)

        # Create geopolitical risk index
        gpr_index = self._calculate_geopolitical_risk_index(active_risks, economic_impacts)

        # Generate investment implications
        investment_implications = self._generate_investment_implications(
            active_risks, economic_impacts, contagion_analysis
        )

        return {
            "geopolitical_risk_metadata": {
                "methodology": "quantified_geopolitical_risk_modeling",
                "region": self.region,
                "analysis_timestamp": datetime.now().isoformat(),
                "risk_assessment_confidence": self._calculate_assessment_confidence(current_context),
            },
            "current_geopolitical_context": current_context,
            "active_risk_factors": active_risks,
            "economic_impact_assessments": economic_impacts,
            "cross_regional_contagion_analysis": contagion_analysis,
            "risk_scenario_analysis": risk_scenarios,
            "geopolitical_risk_index": gpr_index,
            "investment_implications": investment_implications,
            "integrated_risk_assessment": self._create_integrated_assessment(
                active_risks, economic_impacts, contagion_analysis, gpr_index
            ),
        }

    def _extract_geopolitical_context(self, discovery_data: dict, analysis_data: dict) -> dict[str, Any]:
        """Extract current geopolitical context from available data"""

        # Extract from discovery data
        global_context = discovery_data.get("global_economic_context", {})
        geopolitical_data = global_context.get("geopolitical_assessment", {})

        # Trade tensions
        trade_flows = global_context.get("trade_flows", {})
        trade_tension_level = self._assess_trade_tension_level(trade_flows, geopolitical_data)

        # Policy uncertainty
        policy_uncertainty_level = self._assess_policy_uncertainty(discovery_data, analysis_data)

        # Market stress indicators
        market_stress = self._assess_market_stress_indicators(discovery_data)

        # Currency dynamics
        currency_stress = self._assess_currency_stress(global_context.get("currency_dynamics", {}))

        # Energy/commodity stress
        energy_data = discovery_data.get("energy_market_integration", {})
        commodity_stress = self._assess_commodity_stress(energy_data)

        return {
            "overall_risk_level": geopolitical_data.get("risk_level", "moderate"),
            "key_conflicts": geopolitical_data.get("key_conflicts", []),
            "economic_impact_assessment": geopolitical_data.get("economic_impact", "moderate"),
            "trade_tension_level": trade_tension_level,
            "policy_uncertainty_index": policy_uncertainty_level,
            "market_stress_level": market_stress,
            "currency_stress_index": currency_stress,
            "commodity_stress_level": commodity_stress,
            "regional_vulnerabilities": self.regional_vulnerabilities.get(self.region, {}),
            "current_safe_haven_flows": (
                "high" if market_stress > 0.6 else "moderate" if market_stress > 0.3 else "low"
            ),
        }

    def _assess_trade_tension_level(self, trade_flows: dict, geopolitical_data: dict) -> float:
        """Assess current trade tension level"""

        # Base assessment from trade growth
        trade_growth = trade_flows.get("global_trade_growth", 0)
        base_tension = max(0, -trade_growth / 5.0)  # Negative growth indicates tensions

        # Adjust for trade tension indicators
        trade_tensions = trade_flows.get("trade_tensions", "moderate")
        tension_multipliers = {"low": 0.5, "moderate": 1.0, "high": 1.8, "extreme": 2.5}
        tension_factor = tension_multipliers.get(trade_tensions, 1.0)

        # Supply chain stress
        supply_chain_status = trade_flows.get("supply_chain_status", "normal")
        supply_multipliers = {"normal": 1.0, "stressed": 1.3, "disrupted": 1.8}
        supply_factor = supply_multipliers.get(supply_chain_status, 1.0)

        # Key conflicts adjustment
        key_conflicts = geopolitical_data.get("key_conflicts", [])
        conflict_adjustment = len([c for c in key_conflicts if "trade" in c or "tariff" in c]) * 0.2

        tension_level = (base_tension * tension_factor * supply_factor) + conflict_adjustment

        return round(min(1.0, tension_level), 3)

    def _assess_policy_uncertainty(self, discovery_data: dict, analysis_data: dict) -> float:
        """Assess policy uncertainty level"""

        uncertainty_indicators = []

        # Look for policy uncertainty mentions
        insights = discovery_data.get("cli_insights", {}).get("primary_insights", [])
        for insight in insights:
            if "policy_uncertainty" in insight.get("insight", "").lower():
                uncertainty_indicators.append(0.7)

        # Market sentiment indicators
        market_sentiment = discovery_data.get("alpha_vantage_market_data", {}).get("market_sentiment", {})
        key_drivers = market_sentiment.get("key_drivers", [])
        policy_mentions = len([d for d in key_drivers if "policy" in d or "tariff" in d or "uncertainty" in d])
        if policy_mentions > 0:
            uncertainty_indicators.append(policy_mentions * 0.3)

        # Volatility proxy
        volatility_data = discovery_data.get("cli_market_intelligence", {}).get("volatility_analysis", {})
        vix_level = volatility_data.get("vix_analysis", {}).get("current_level", 20.0)
        if vix_level > 25:
            uncertainty_indicators.append((vix_level - 20) / 20)

        # Business cycle uncertainty
        business_cycle = discovery_data.get("business_cycle_data", {})
        recession_prob = business_cycle.get("transition_probabilities", {}).get("next_12m", 0.2)
        if recession_prob > 0.25:
            uncertainty_indicators.append(recession_prob * 0.8)

        # Calculate average if indicators exist
        if uncertainty_indicators:
            policy_uncertainty = np.mean(uncertainty_indicators)
        else:
            policy_uncertainty = 0.4  # Default moderate uncertainty

        return round(min(1.0, policy_uncertainty), 3)

    def _assess_market_stress_indicators(self, discovery_data: dict) -> float:
        """Assess market stress level"""

        stress_indicators = []

        # VIX level
        volatility_data = discovery_data.get("cli_market_intelligence", {}).get("volatility_analysis", {})
        vix_level = volatility_data.get("vix_analysis", {}).get("current_level", 20.0)
        vix_stress = min(1.0, max(0, (vix_level - 15) / 25))  # Normalize 15-40 range
        stress_indicators.append(vix_stress)

        # Market sentiment
        market_sentiment = discovery_data.get("alpha_vantage_market_data", {}).get("market_sentiment", {})
        sentiment_score = market_sentiment.get("sentiment_score", 0.5)
        sentiment_stress = 1.0 - sentiment_score  # Invert sentiment
        stress_indicators.append(sentiment_stress)

        # Risk appetite
        risk_appetite = discovery_data.get("cli_market_intelligence", {}).get("risk_appetite", {})
        risk_level = risk_appetite.get("current_level", "neutral")
        risk_stress = {"low": 0.8, "moderate": 0.5, "neutral": 0.4, "high": 0.2}.get(risk_level, 0.4)
        stress_indicators.append(risk_stress)

        return round(np.mean(stress_indicators), 3)

    def _assess_currency_stress(self, currency_dynamics: dict) -> float:
        """Assess currency stress level"""

        stress_indicators = []

        # DXY strength (high USD strength indicates stress elsewhere)
        dxy_data = currency_dynamics.get("dxy_analysis", {})
        dxy_level = dxy_data.get("current_level", 100.0)
        dxy_stress = max(0, (dxy_level - 95) / 15)  # Normalize 95-110 range
        stress_indicators.append(dxy_stress)

        # Emerging market currency stress
        em_currencies = currency_dynamics.get("emerging_market_currencies", {})
        em_stress_level = em_currencies.get("stress_level", "moderate")
        em_stress = {"low": 0.2, "moderate": 0.5, "elevated": 0.7, "high": 0.9}.get(em_stress_level, 0.5)
        stress_indicators.append(em_stress)

        # Capital flow pressures
        capital_flows = em_currencies.get("capital_flows", "neutral")
        flow_stress = {
            "inflow_pressures": 0.3,
            "neutral": 0.4,
            "outflow_pressures": 0.8,
        }.get(capital_flows, 0.4)
        stress_indicators.append(flow_stress)

        return round(np.mean(stress_indicators), 3)

    def _assess_commodity_stress(self, energy_data: dict) -> float:
        """Assess commodity/energy stress level"""

        stress_indicators = []

        # Oil price volatility
        oil_analysis = energy_data.get("oil_analysis", {})
        geopolitical_premium = oil_analysis.get("geopolitical_premium", 0)
        oil_stress = min(1.0, geopolitical_premium / 10.0)  # $10 premium = 100% stress
        stress_indicators.append(oil_stress)

        # Supply-demand balance
        supply_demand = oil_analysis.get("supply_demand", {})
        balance = supply_demand.get("balance", "balanced")
        balance_stress = {
            "oversupply": 0.2,
            "balanced": 0.3,
            "tight": 0.6,
            "shortage": 0.9,
        }.get(balance, 0.3)
        stress_indicators.append(balance_stress)

        # Natural gas stress
        gas_analysis = energy_data.get("natural_gas_analysis", {})
        storage_levels = gas_analysis.get("storage_levels", {})
        storage_status = storage_levels.get("current_level", "adequate")
        storage_stress = {
            "abundant": 0.1,
            "adequate": 0.3,
            "tight": 0.7,
            "critical": 0.9,
        }.get(storage_status, 0.3)
        stress_indicators.append(storage_stress)

        return round(np.mean(stress_indicators), 3)

    def _identify_active_risks(self, context: dict[str, Any]) -> dict[str, Any]:
        """Identify and quantify currently active geopolitical risks"""

        active_risks = {}

        # Trade tensions risk
        if context["trade_tension_level"] > 0.3:
            active_risks["trade_tensions"] = GeopoliticalRiskEvent(
                event_type="trade_tensions",
                probability=min(0.9, context["trade_tension_level"] * 1.2),
                severity=self._classify_risk_severity(context["trade_tension_level"]),
                time_horizon="6m",
                affected_regions=["US", "ASIA", "EU"],
                economic_channels=["trade_flows", "supply_chains", "investment"],
                confidence=0.85,
            )

        # Policy uncertainty risk
        if context["policy_uncertainty_index"] > 0.4:
            active_risks["policy_uncertainty"] = GeopoliticalRiskEvent(
                event_type="policy_uncertainty",
                probability=context["policy_uncertainty_index"],
                severity=self._classify_risk_severity(context["policy_uncertainty_index"]),
                time_horizon="12m",
                affected_regions=[self.region],
                economic_channels=["investment", "sentiment", "currency_volatility"],
                confidence=0.80,
            )

        # Market stress risk (proxy for broader instability)
        if context["market_stress_level"] > 0.5:
            active_risks["market_instability"] = GeopoliticalRiskEvent(
                event_type="market_instability",
                probability=context["market_stress_level"],
                severity=self._classify_risk_severity(context["market_stress_level"]),
                time_horizon="3m",
                affected_regions=["US", "EU", "ASIA", "EMERGING_MARKETS"],
                economic_channels=["financial_flows", "sentiment", "investment"],
                confidence=0.75,
            )

        # Currency stress risk
        if context["currency_stress_index"] > 0.5:
            active_risks["currency_instability"] = GeopoliticalRiskEvent(
                event_type="currency_instability",
                probability=context["currency_stress_index"],
                severity=self._classify_risk_severity(context["currency_stress_index"]),
                time_horizon="6m",
                affected_regions=["EMERGING_MARKETS", "ASIA"],
                economic_channels=["financial_flows", "trade_flows", "inflation"],
                confidence=0.70,
            )

        # Commodity/energy stress risk
        if context["commodity_stress_level"] > 0.4:
            active_risks["energy_disruption"] = GeopoliticalRiskEvent(
                event_type="energy_disruption",
                probability=context["commodity_stress_level"],
                severity=self._classify_risk_severity(context["commodity_stress_level"]),
                time_horizon="12m",
                affected_regions=["EU", "ASIA"],
                economic_channels=["commodity_prices", "inflation", "supply_chains"],
                confidence=0.78,
            )

        return {
            risk_name: {
                "event_type": risk.event_type,
                "probability": round(risk.probability, 3),
                "severity": risk.severity,
                "time_horizon": risk.time_horizon,
                "affected_regions": risk.affected_regions,
                "economic_channels": risk.economic_channels,
                "confidence": risk.confidence,
            }
            for risk_name, risk in active_risks.items()
        }

    def _classify_risk_severity(self, risk_level: float) -> str:
        """Classify risk severity based on quantified level"""

        if risk_level >= 0.8:
            return "extreme"
        if risk_level >= 0.6:
            return "high"
        if risk_level >= 0.4:
            return "moderate"
        return "low"

    def _calculate_economic_impacts(self, active_risks: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Calculate economic impacts of identified geopolitical risks"""

        impact_assessments = {}

        for risk_name, risk_data in active_risks.items():
            event_type = risk_data["event_type"]
            probability = risk_data["probability"]
            severity = risk_data["severity"]
            economic_channels = risk_data["economic_channels"]

            # Calculate impact through each economic channel
            total_gdp_impact = 0
            total_inflation_impact = 0
            total_trade_impact = 0

            for channel in economic_channels:
                if channel in self.transmission_channels:
                    channel_data = self.transmission_channels[channel]

                    # Base impact adjusted for severity and probability
                    severity_multiplier = {
                        "low": 0.5,
                        "moderate": 1.0,
                        "high": 1.5,
                        "extreme": 2.0,
                    }[severity]

                    gdp_impact = channel_data["gdp_coefficient"] * severity_multiplier * probability
                    inflation_impact = channel_data["inflation_coefficient"] * severity_multiplier * probability

                    total_gdp_impact += gdp_impact
                    total_inflation_impact += inflation_impact

                    # Trade impact (simplified)
                    if channel in ["trade_flows", "supply_chains"]:
                        total_trade_impact += -15 * severity_multiplier * probability  # Negative trade impact

            # Regional vulnerability adjustment
            regional_vuln = context.get("regional_vulnerabilities", {})
            vulnerability_factor = 1.0

            if event_type == "trade_tensions":
                vulnerability_factor = regional_vuln.get("trade_dependency", 0.5)
            elif event_type == "energy_disruption":
                vulnerability_factor = regional_vuln.get("energy_dependence", 0.5)
            elif "currency" in event_type:
                vulnerability_factor = 1.0 - regional_vuln.get("safe_haven_status", 0.5)

            # Apply vulnerability adjustment
            total_gdp_impact *= 0.5 + vulnerability_factor
            total_inflation_impact *= 0.5 + vulnerability_factor
            total_trade_impact *= vulnerability_factor

            # Duration estimate
            risk_category = self.risk_categories.get(event_type, {})
            duration = risk_category.get("typical_duration", 12)

            impact_assessments[risk_name] = {
                "gdp_impact_percentage_points": round(total_gdp_impact, 3),
                "inflation_impact_percentage_points": round(total_inflation_impact, 3),
                "trade_impact_percentage": round(total_trade_impact, 1),
                "currency_impact_percentage": round(total_gdp_impact * -5, 1),  # GDP impact drives currency
                "market_impact_percentage": round(total_gdp_impact * -8, 1),  # Market multiple of GDP impact
                "expected_duration_months": duration,
                "peak_impact_timeline": "3-6_months",
                "recovery_timeline": f"{duration // 2}-{duration}_months",
            }

        return impact_assessments

    def _analyze_contagion_risks(self, active_risks: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Analyze cross-regional contagion risks"""

        contagion_assessments = {}

        for risk_name, risk_data in active_risks.items():
            affected_regions = risk_data["affected_regions"]
            probability = risk_data["probability"]

            # Calculate contagion probabilities to other regions
            contagion_map = {}

            for source_region in affected_regions:
                if source_region in self.contagion_matrix:
                    for target_region, contagion_coeff in self.contagion_matrix[source_region].items():
                        if target_region not in affected_regions:  # Not already affected
                            contagion_prob = probability * contagion_coeff * 0.8  # Reduced probability for contagion

                            if target_region not in contagion_map:
                                contagion_map[target_region] = {
                                    "contagion_probability": 0,
                                    "transmission_channels": [],
                                    "time_to_transmission_months": 12,
                                }

                            contagion_map[target_region]["contagion_probability"] = max(
                                contagion_map[target_region]["contagion_probability"],
                                contagion_prob,
                            )
                            contagion_map[target_region]["transmission_channels"] = list(
                                set(
                                    contagion_map[target_region]["transmission_channels"]
                                    + [
                                        "trade_links",
                                        "financial_flows",
                                        "sentiment",
                                    ]
                                )
                            )

            # Clean up probabilities
            for region in contagion_map:
                contagion_map[region]["contagion_probability"] = round(
                    contagion_map[region]["contagion_probability"], 3
                )

            contagion_assessments[risk_name] = {
                "primary_affected_regions": affected_regions,
                "contagion_mapping": contagion_map,
                "overall_contagion_risk": (
                    "high"
                    if any(region_data["contagion_probability"] > 0.4 for region_data in contagion_map.values())
                    else (
                        "moderate"
                        if any(region_data["contagion_probability"] > 0.2 for region_data in contagion_map.values())
                        else "low"
                    )
                ),
            }

        return contagion_assessments

    def _generate_risk_scenarios(
        self, active_risks: dict[str, Any], economic_impacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate risk scenario analysis"""

        scenarios = {}

        # Base case: Current risks don't escalate
        base_case_impact = self._calculate_aggregate_impact(active_risks, economic_impacts, 0.6)
        scenarios["base_case"] = {
            "description": "Current geopolitical risks remain at present levels",
            "probability": 0.5,
            "aggregate_economic_impact": base_case_impact,
            "key_assumptions": [
                "Trade tensions remain elevated but stable",
                "Policy uncertainty continues at current levels",
                "No major new geopolitical events",
            ],
        }

        # Escalation case: Risks intensify
        escalation_impact = self._calculate_aggregate_impact(active_risks, economic_impacts, 1.4)
        scenarios["escalation_case"] = {
            "description": "Geopolitical risks escalate significantly",
            "probability": 0.25,
            "aggregate_economic_impact": escalation_impact,
            "key_assumptions": [
                "Trade war intensifies with broader tariffs",
                "Policy uncertainty spikes around major events",
                "Additional geopolitical tensions emerge",
            ],
        }

        # De-escalation case: Risks subside
        deescalation_impact = self._calculate_aggregate_impact(active_risks, economic_impacts, 0.3)
        scenarios["de_escalation_case"] = {
            "description": "Geopolitical tensions ease substantially",
            "probability": 0.25,
            "aggregate_economic_impact": deescalation_impact,
            "key_assumptions": [
                "Trade agreements reached or tensions cool",
                "Policy clarity reduces uncertainty",
                "Diplomatic solutions to key conflicts",
            ],
        }

        return scenarios

    def _calculate_aggregate_impact(
        self,
        active_risks: dict[str, Any],
        economic_impacts: dict[str, Any],
        scenario_multiplier: float,
    ) -> dict[str, float]:
        """Calculate aggregate economic impact across all risks"""

        total_gdp_impact = 0
        total_inflation_impact = 0
        total_trade_impact = 0

        for risk_name, impact_data in economic_impacts.items():
            if risk_name in active_risks:
                # Weight by risk probability
                probability = active_risks[risk_name]["probability"]

                total_gdp_impact += impact_data["gdp_impact_percentage_points"] * probability * scenario_multiplier
                total_inflation_impact += (
                    impact_data["inflation_impact_percentage_points"] * probability * scenario_multiplier
                )
                total_trade_impact += impact_data["trade_impact_percentage"] * probability * scenario_multiplier

        return {
            "gdp_impact_percentage_points": round(total_gdp_impact, 3),
            "inflation_impact_percentage_points": round(total_inflation_impact, 3),
            "trade_impact_percentage": round(total_trade_impact, 1),
            "market_impact_percentage": round(total_gdp_impact * -8, 1),
        }

    def _calculate_geopolitical_risk_index(
        self, active_risks: dict[str, Any], economic_impacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate composite geopolitical risk index"""

        # Weight risks by probability and severity
        risk_scores = []
        risk_contributions = {}

        for risk_name, risk_data in active_risks.items():
            probability = risk_data["probability"]
            severity = risk_data["severity"]

            # Convert severity to numeric
            severity_scores = {
                "low": 0.25,
                "moderate": 0.5,
                "high": 0.75,
                "extreme": 1.0,
            }
            severity_score = severity_scores[severity]

            # Risk contribution (probability * severity)
            risk_score = probability * severity_score
            risk_scores.append(risk_score)
            risk_contributions[risk_name] = round(risk_score, 3)

        # Overall index (average of risk scores, scaled 0-100)
        if risk_scores:
            gpr_index = np.mean(risk_scores) * 100
        else:
            gpr_index = 30  # Baseline risk level

        # Classification
        if gpr_index >= 75:
            risk_classification = "extreme"
        elif gpr_index >= 60:
            risk_classification = "high"
        elif gpr_index >= 40:
            risk_classification = "moderate"
        else:
            risk_classification = "low"

        return {
            "geopolitical_risk_index": round(gpr_index, 1),
            "risk_classification": risk_classification,
            "index_components": risk_contributions,
            "historical_percentile": min(95, max(5, gpr_index)),  # Approximate percentile
            "trend": "increasing" if gpr_index > 50 else "stable",
            "next_review_priority": "high" if gpr_index > 60 else "moderate",
        }

    def _generate_investment_implications(
        self,
        active_risks: dict[str, Any],
        economic_impacts: dict[str, Any],
        contagion_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate investment implications from geopolitical risk analysis"""

        # Asset allocation adjustments
        allocation_adjustments = self._calculate_allocation_adjustments(active_risks, economic_impacts)

        # Regional positioning
        regional_positioning = self._determine_regional_positioning(active_risks, contagion_analysis)

        # Sector implications
        sector_implications = self._analyze_sector_implications(active_risks, economic_impacts)

        # Hedging strategies
        hedging_strategies = self._recommend_hedging_strategies(active_risks, economic_impacts)

        return {
            "asset_allocation_adjustments": allocation_adjustments,
            "regional_positioning_guidance": regional_positioning,
            "sector_impact_analysis": sector_implications,
            "risk_hedging_strategies": hedging_strategies,
            "portfolio_positioning_summary": self._create_positioning_summary(
                allocation_adjustments, regional_positioning, sector_implications
            ),
        }

    def _calculate_allocation_adjustments(
        self, active_risks: dict[str, Any], economic_impacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate recommended asset allocation adjustments"""

        # Calculate aggregate impact
        base_impact = self._calculate_aggregate_impact(active_risks, economic_impacts, 1.0)

        gdp_impact = base_impact["gdp_impact_percentage_points"]
        inflation_impact = base_impact["inflation_impact_percentage_points"]

        # Asset class recommendations based on impacts
        recommendations = {}

        # Equities: Negative GDP impact = reduce equity allocation
        if gdp_impact < -0.5:
            recommendations["equities"] = "significant_underweight"
        elif gdp_impact < -0.2:
            recommendations["equities"] = "modest_underweight"
        else:
            recommendations["equities"] = "neutral"

        # Bonds: Flight to quality during geopolitical stress
        if any(risk_data["severity"] in ["high", "extreme"] for risk_data in active_risks.values()):
            recommendations["government_bonds"] = "overweight"
            recommendations["corporate_bonds"] = "underweight"
        else:
            recommendations["government_bonds"] = "neutral"
            recommendations["corporate_bonds"] = "neutral"

        # Commodities: Energy disruption = overweight commodities
        if "energy_disruption" in active_risks:
            recommendations["commodities"] = "overweight"
        else:
            recommendations["commodities"] = "neutral"

        # Cash: Higher geopolitical risk = higher cash allocation
        risk_count = len(active_risks)
        if risk_count >= 3:
            recommendations["cash"] = "overweight"
        else:
            recommendations["cash"] = "neutral"

        return {
            "asset_class_recommendations": recommendations,
            "rationale": f"Based on {gdp_impact:.2f}pp GDP impact and {inflation_impact:.2f}pp inflation impact from geopolitical risks",
            "rebalancing_urgency": "high" if gdp_impact < -0.5 else "moderate",
            "monitoring_frequency": "weekly" if risk_count >= 3 else "monthly",
        }

    def _determine_regional_positioning(
        self, active_risks: dict[str, Any], contagion_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine regional investment positioning"""

        regional_recommendations = {}

        # Analyze each major region
        for region in ["US", "EU", "ASIA", "EMERGING_MARKETS"]:
            risk_exposure = self._calculate_regional_risk_exposure(region, active_risks, contagion_analysis)

            if risk_exposure < 0.3:
                recommendation = "overweight"
            elif risk_exposure < 0.6:
                recommendation = "neutral"
            else:
                recommendation = "underweight"

            regional_recommendations[region] = {
                "positioning": recommendation,
                "risk_exposure_score": round(risk_exposure, 3),
                "primary_risk_factors": self._identify_regional_risk_factors(region, active_risks),
            }

        return {
            "regional_allocation_guidance": regional_recommendations,
            "safe_haven_preferences": (
                ["US", "EU"]
                if "US" in regional_recommendations and regional_recommendations["US"]["risk_exposure_score"] < 0.4
                else ["US"]
            ),
            "highest_risk_regions": [
                region for region, data in regional_recommendations.items() if data["risk_exposure_score"] > 0.6
            ],
        }

    def _calculate_regional_risk_exposure(
        self,
        region: str,
        active_risks: dict[str, Any],
        contagion_analysis: dict[str, Any],
    ) -> float:
        """Calculate risk exposure score for a region"""

        exposure_scores = []

        # Direct exposure from active risks
        for risk_name, risk_data in active_risks.items():
            if region in risk_data["affected_regions"]:
                exposure_scores.append(risk_data["probability"])

        # Contagion exposure
        for risk_name, contagion_data in contagion_analysis.items():
            contagion_map = contagion_data.get("contagion_mapping", {})
            if region in contagion_map:
                exposure_scores.append(contagion_map[region]["contagion_probability"])

        # Regional vulnerability
        regional_vuln = self.regional_vulnerabilities.get(region, {})
        avg_vulnerability = np.mean(list(regional_vuln.values()))
        exposure_scores.append(avg_vulnerability)

        return np.mean(exposure_scores) if exposure_scores else 0.3

    def _identify_regional_risk_factors(self, region: str, active_risks: dict[str, Any]) -> list[str]:
        """Identify primary risk factors for a region"""

        risk_factors = []

        for risk_name, risk_data in active_risks.items():
            if region in risk_data["affected_regions"]:
                risk_factors.append(risk_data["event_type"])

        return list(set(risk_factors))

    def _analyze_sector_implications(
        self, active_risks: dict[str, Any], economic_impacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze sector-specific implications of geopolitical risks"""

        sector_impacts = {}

        # Define sector sensitivities to different risk types
        sector_sensitivities = {
            "technology": {
                "trade_tensions": -0.8,  # Very negative
                "policy_uncertainty": -0.4,
                "currency_instability": -0.3,
            },
            "energy": {
                "energy_disruption": 0.6,  # Positive for energy companies
                "trade_tensions": -0.2,
                "market_instability": -0.4,
            },
            "financials": {
                "market_instability": -0.7,
                "currency_instability": -0.5,
                "policy_uncertainty": -0.3,
            },
            "consumer_staples": {
                "trade_tensions": -0.2,  # Defensive characteristics
                "market_instability": 0.1,  # Flight to quality
                "policy_uncertainty": 0.0,
            },
            "industrials": {
                "trade_tensions": -0.6,
                "policy_uncertainty": -0.5,
                "energy_disruption": -0.4,
            },
        }

        for sector, sensitivities in sector_sensitivities.items():
            sector_impact = 0
            contributing_risks = []

            for risk_name, risk_data in active_risks.items():
                risk_type = risk_data["event_type"]
                if risk_type in sensitivities:
                    impact = sensitivities[risk_type] * risk_data["probability"]
                    sector_impact += impact
                    if abs(impact) > 0.1:
                        contributing_risks.append(risk_type)

            # Classification
            if sector_impact > 0.2:
                classification = "beneficial"
            elif sector_impact > -0.2:
                classification = "neutral"
            elif sector_impact > -0.4:
                classification = "negative"
            else:
                classification = "severely_negative"

            sector_impacts[sector] = {
                "impact_score": round(sector_impact, 3),
                "impact_classification": classification,
                "primary_risk_drivers": contributing_risks,
                "investment_recommendation": (
                    "overweight" if sector_impact > 0.2 else "underweight" if sector_impact < -0.3 else "neutral"
                ),
            }

        return sector_impacts

    def _recommend_hedging_strategies(
        self, active_risks: dict[str, Any], economic_impacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Recommend risk hedging strategies"""

        hedging_strategies = []

        # Currency hedging
        if "currency_instability" in active_risks:
            hedging_strategies.append(
                {
                    "strategy_type": "currency_hedging",
                    "instruments": ["currency_forwards", "currency_ETFs"],
                    "rationale": "Hedge against currency volatility from geopolitical instability",
                    "urgency": ("high" if active_risks["currency_instability"]["probability"] > 0.6 else "moderate"),
                }
            )

        # Volatility hedging
        high_vol_risks = [r for r in active_risks.values() if r["severity"] in ["high", "extreme"]]
        if high_vol_risks:
            hedging_strategies.append(
                {
                    "strategy_type": "volatility_hedging",
                    "instruments": ["VIX_calls", "protective_puts", "volatility_ETFs"],
                    "rationale": "Protection against market volatility from geopolitical events",
                    "urgency": "high",
                }
            )

        # Commodity hedging
        if "energy_disruption" in active_risks:
            hedging_strategies.append(
                {
                    "strategy_type": "commodity_hedging",
                    "instruments": [
                        "energy_ETFs",
                        "commodity_futures",
                        "energy_stocks",
                    ],
                    "rationale": "Hedge against energy price spikes from supply disruptions",
                    "urgency": "moderate",
                }
            )

        # Safe haven allocation
        if len(active_risks) >= 2:
            hedging_strategies.append(
                {
                    "strategy_type": "safe_haven_allocation",
                    "instruments": ["treasury_bonds", "gold_ETFs", "USD_assets"],
                    "rationale": "Flight to quality allocation during geopolitical uncertainty",
                    "urgency": "moderate",
                }
            )

        return {
            "recommended_strategies": hedging_strategies,
            "portfolio_hedge_ratio": "10-15%" if len(active_risks) >= 3 else "5-10%",
            "rebalancing_triggers": [
                "geopolitical_risk_index > 70",
                "new_major_geopolitical_event",
            ],
            "monitoring_indicators": [
                "VIX",
                "USD_index",
                "commodity_prices",
                "credit_spreads",
            ],
        }

    def _create_positioning_summary(
        self,
        allocation_adjustments: dict[str, Any],
        regional_positioning: dict[str, Any],
        sector_implications: dict[str, Any],
    ) -> dict[str, Any]:
        """Create integrated portfolio positioning summary"""

        # Overall risk stance
        equity_rec = allocation_adjustments["asset_class_recommendations"].get("equities", "neutral")
        if equity_rec in ["significant_underweight", "modest_underweight"]:
            overall_stance = "defensive"
        elif equity_rec == "overweight":
            overall_stance = "aggressive"
        else:
            overall_stance = "balanced"

        # Key themes
        themes = []

        if allocation_adjustments["rebalancing_urgency"] == "high":
            themes.append("Immediate portfolio repositioning recommended due to elevated geopolitical risks")

        safe_havens = regional_positioning.get("safe_haven_preferences", [])
        if len(safe_havens) <= 2:
            themes.append("Limited safe haven options increase portfolio vulnerability")

        negative_sectors = [
            s
            for s, data in sector_implications.items()
            if data["impact_classification"] in ["negative", "severely_negative"]
        ]
        if len(negative_sectors) >= 3:
            themes.append("Broad-based sector headwinds require selective stock picking")

        return {
            "overall_positioning_stance": overall_stance,
            "key_positioning_themes": themes,
            "immediate_actions_required": allocation_adjustments["rebalancing_urgency"] == "high",
            "monitoring_frequency": allocation_adjustments["monitoring_frequency"],
            "risk_budget_allocation": "Conservative - limit geopolitical risk exposure to 10-15% of portfolio",
        }

    def _create_integrated_assessment(
        self,
        active_risks: dict[str, Any],
        economic_impacts: dict[str, Any],
        contagion_analysis: dict[str, Any],
        gpr_index: dict[str, Any],
    ) -> dict[str, Any]:
        """Create integrated geopolitical risk assessment"""

        # Overall assessment
        index_level = gpr_index["geopolitical_risk_index"]
        risk_classification = gpr_index["risk_classification"]

        if index_level >= 70:
            overall_assessment = "critical_risk_environment"
        elif index_level >= 55:
            overall_assessment = "elevated_risk_environment"
        else:
            overall_assessment = "manageable_risk_environment"

        # Key findings
        findings = []

        high_prob_risks = [name for name, data in active_risks.items() if data["probability"] > 0.7]
        if high_prob_risks:
            findings.append(f"High-probability risks identified: {', '.join(high_prob_risks)}")

        severe_impacts = [
            name for name, data in economic_impacts.items() if abs(data["gdp_impact_percentage_points"]) > 0.5
        ]
        if severe_impacts:
            findings.append(f"Severe economic impact potential: {', '.join(severe_impacts)}")

        high_contagion = [name for name, data in contagion_analysis.items() if data["overall_contagion_risk"] == "high"]
        if high_contagion:
            findings.append(f"High contagion risk events: {', '.join(high_contagion)}")

        return {
            "overall_risk_assessment": overall_assessment,
            "geopolitical_risk_index": index_level,
            "risk_classification": risk_classification,
            "key_findings": findings,
            "investment_impact": "significant" if index_level > 60 else "moderate",
            "recommended_actions": self._generate_recommended_actions(index_level, active_risks),
            "next_review_timeline": "1_month" if index_level > 65 else "3_months",
        }

    def _generate_recommended_actions(self, index_level: float, active_risks: dict[str, Any]) -> list[str]:
        """Generate recommended actions based on risk assessment"""

        actions = []

        if index_level > 70:
            actions.append("Implement immediate defensive portfolio positioning")
            actions.append("Activate crisis management protocols")

        if index_level > 55:
            actions.append("Increase portfolio hedging ratios")
            actions.append("Reduce exposure to high-risk regions")

        if "trade_tensions" in active_risks:
            actions.append("Monitor supply chain disruption impacts")

        if "currency_instability" in active_risks:
            actions.append("Implement currency hedging strategies")

        if len(active_risks) >= 3:
            actions.append("Enhance risk monitoring frequency to weekly reviews")

        return actions

    def _calculate_assessment_confidence(self, context: dict[str, Any]) -> float:
        """Calculate confidence in geopolitical risk assessment"""

        confidence_factors = []

        # Data quality factor
        confidence_factors.append(0.8)  # Base assumption

        # Risk clarity factor
        overall_risk = context.get("overall_risk_level", "moderate")
        if overall_risk in ["low", "high"]:
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.7)

        # Multiple risk sources factor
        if len(context.get("key_conflicts", [])) > 1:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.75)

        return round(np.mean(confidence_factors), 3)


# Testing and validation functions
def validate_geopolitical_risk_engine():
    """Validate the geopolitical risk engine"""

    # Sample data
    sample_discovery = {
        "global_economic_context": {
            "geopolitical_assessment": {
                "risk_level": "high",
                "key_conflicts": ["trade_tensions_us_china", "policy_uncertainty"],
                "economic_impact": "significant",
            },
            "trade_flows": {
                "global_trade_growth": -2.5,
                "trade_tensions": "high",
                "supply_chain_status": "stressed",
            },
            "currency_dynamics": {
                "dxy_analysis": {"current_level": 98.5},
                "emerging_market_currencies": {
                    "stress_level": "elevated",
                    "capital_flows": "outflow_pressures",
                },
            },
        },
        "cli_market_intelligence": {"volatility_analysis": {"vix_analysis": {"current_level": 22.3}}},
        "energy_market_integration": {"oil_analysis": {"geopolitical_premium": 5.0}},
    }

    sample_analysis = {"region": "US"}

    # Create engine and run analysis
    engine = GeopoliticalRiskEngine("US")
    results = engine.analyze_geopolitical_risks(sample_discovery, sample_analysis)

    return results


if __name__ == "__main__":
    # Run validation
    test_results = validate_geopolitical_risk_engine()
    print(json.dumps(test_results, indent=2))
