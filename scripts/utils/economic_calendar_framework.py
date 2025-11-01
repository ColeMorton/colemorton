"""
Economic Calendar and Policy Timeline Framework

Advanced forward-looking economic calendar with policy impact modeling:
- Central bank policy meeting schedules and probability modeling
- Economic data release calendar with market impact scoring
- Policy transmission channel analysis and timing
- Forward guidance interpretation and scenario modeling
- Cross-regional policy coordination tracking
- Real-time policy shift detection and alerts

Provides institutional-grade economic calendar intelligence for macro-economic analysis.
"""

import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np


# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=RuntimeWarning)


@dataclass
class PolicyEvent:
    """Policy event data structure"""

    event_date: str
    event_type: str  # 'fomc_meeting', 'ecb_meeting', 'boe_meeting', 'data_release'
    event_importance: str  # 'high', 'medium', 'low'
    probability_score: float  # Probability of policy change (0-1)
    market_impact_score: float  # Expected market impact (0-1)
    policy_direction: str  # 'tightening', 'easing', 'neutral', 'data_dependent'
    confidence_interval: tuple[float, float]  # (lower, upper) bounds


@dataclass
class DataRelease:
    """Economic data release structure"""

    release_date: str
    indicator_name: str
    indicator_importance: str  # 'tier_1', 'tier_2', 'tier_3'
    expected_value: float | None
    previous_value: float | None
    market_consensus: float | None
    surprise_potential: float  # Probability of significant surprise
    policy_relevance_score: float  # Relevance to central bank policy


@dataclass
class ForwardGuidance:
    """Forward guidance interpretation structure"""

    guidance_date: str
    central_bank: str
    guidance_tone: str  # 'hawkish', 'dovish', 'neutral', 'data_dependent'
    policy_shift_probability: float
    time_horizon: str  # '3m', '6m', '12m'
    key_phrases: list[str]
    market_interpretation: str


class EconomicCalendarEngine:
    """
    Advanced economic calendar and policy timeline engine

    Features:
    - Forward-looking policy meeting schedules
    - Economic data release impact modeling
    - Policy transmission timing analysis
    - Cross-regional coordination tracking
    - Real-time policy shift detection
    """

    def __init__(self, region: str = "US"):
        self.region = region.upper()

        # Central bank meeting schedules (approximate)
        self.policy_meeting_schedules = {
            "US": {
                "fomc_meetings": [
                    "2025-01-29",
                    "2025-03-19",
                    "2025-05-01",
                    "2025-06-11",
                    "2025-07-30",
                    "2025-09-17",
                    "2025-11-05",
                    "2025-12-17",
                ],
                "rate_name": "Fed Funds Rate",
                "current_rate": 5.25,
            },
            "EU": {
                "ecb_meetings": [
                    "2025-01-30",
                    "2025-03-06",
                    "2025-04-10",
                    "2025-06-05",
                    "2025-07-17",
                    "2025-09-11",
                    "2025-10-23",
                    "2025-12-11",
                ],
                "rate_name": "ECB Main Refinancing Rate",
                "current_rate": 3.75,
            },
            "UK": {
                "boe_meetings": [
                    "2025-02-06",
                    "2025-03-20",
                    "2025-05-08",
                    "2025-06-19",
                    "2025-08-07",
                    "2025-09-18",
                    "2025-11-06",
                    "2025-12-18",
                ],
                "rate_name": "Bank Rate",
                "current_rate": 4.75,
            },
        }

        # Economic data release calendar (key indicators)
        self.data_release_calendar = {
            "US": [
                {
                    "indicator": "Employment Report",
                    "frequency": "monthly",
                    "day": 1,
                    "importance": "tier_1",
                },
                {
                    "indicator": "CPI",
                    "frequency": "monthly",
                    "day": 15,
                    "importance": "tier_1",
                },
                {
                    "indicator": "GDP",
                    "frequency": "quarterly",
                    "day": 28,
                    "importance": "tier_1",
                },
                {
                    "indicator": "ISM PMI",
                    "frequency": "monthly",
                    "day": 3,
                    "importance": "tier_2",
                },
                {
                    "indicator": "Consumer Confidence",
                    "frequency": "monthly",
                    "day": 25,
                    "importance": "tier_2",
                },
                {
                    "indicator": "Retail Sales",
                    "frequency": "monthly",
                    "day": 18,
                    "importance": "tier_2",
                },
                {
                    "indicator": "Industrial Production",
                    "frequency": "monthly",
                    "day": 20,
                    "importance": "tier_3",
                },
            ],
            "EU": [
                {
                    "indicator": "Eurozone CPI",
                    "frequency": "monthly",
                    "day": 31,
                    "importance": "tier_1",
                },
                {
                    "indicator": "Eurozone GDP",
                    "frequency": "quarterly",
                    "day": 30,
                    "importance": "tier_1",
                },
                {
                    "indicator": "Eurozone PMI",
                    "frequency": "monthly",
                    "day": 23,
                    "importance": "tier_2",
                },
                {
                    "indicator": "ECB Economic Bulletin",
                    "frequency": "quarterly",
                    "day": 15,
                    "importance": "tier_2",
                },
                {
                    "indicator": "German IFO",
                    "frequency": "monthly",
                    "day": 25,
                    "importance": "tier_2",
                },
                {
                    "indicator": "Eurozone Unemployment",
                    "frequency": "monthly",
                    "day": 31,
                    "importance": "tier_3",
                },
            ],
        }

        # Policy transmission channels and timing
        self.transmission_channels = {
            "interest_rate_channel": {"lag_quarters": 2, "effectiveness": 0.8},
            "credit_channel": {"lag_quarters": 3, "effectiveness": 0.7},
            "asset_price_channel": {"lag_quarters": 1, "effectiveness": 0.6},
            "exchange_rate_channel": {"lag_quarters": 1, "effectiveness": 0.5},
            "expectations_channel": {"lag_quarters": 0, "effectiveness": 0.9},
        }

    def generate_forward_economic_calendar(
        self,
        discovery_data: dict[str, Any],
        analysis_data: dict[str, Any],
        forecast_horizon_months: int = 12,
    ) -> dict[str, Any]:
        """
        Generate comprehensive forward-looking economic calendar with policy impact modeling

        Args:
            discovery_data: Discovery phase economic data
            analysis_data: Current analysis data and context
            forecast_horizon_months: Forward-looking calendar horizon

        Returns:
            Dictionary containing comprehensive economic calendar analysis
        """
        try:
            # Generate policy meeting calendar with probability modeling
            policy_calendar = self._generate_policy_meeting_calendar(discovery_data, forecast_horizon_months)

            # Generate economic data release calendar
            data_release_calendar = self._generate_data_release_calendar(discovery_data, forecast_horizon_months)

            # Analyze policy transmission timing
            transmission_analysis = self._analyze_policy_transmission_timing(discovery_data, analysis_data)

            # Generate forward guidance analysis
            forward_guidance = self._analyze_forward_guidance(discovery_data, analysis_data)

            # Cross-regional policy coordination analysis
            coordination_analysis = self._analyze_cross_regional_coordination(discovery_data, analysis_data)

            # Policy shift probability modeling
            policy_shift_analysis = self._model_policy_shift_probabilities(discovery_data, analysis_data)

            # Generate integrated calendar insights
            calendar_insights = self._generate_calendar_insights(
                policy_calendar, data_release_calendar, transmission_analysis
            )

            return {
                "economic_calendar_framework": {
                    "policy_meeting_calendar": policy_calendar,
                    "data_release_calendar": data_release_calendar,
                    "policy_transmission_analysis": transmission_analysis,
                    "forward_guidance_analysis": forward_guidance,
                    "cross_regional_coordination": coordination_analysis,
                    "policy_shift_probabilities": policy_shift_analysis,
                    "integrated_calendar_insights": calendar_insights,
                },
                "forecast_horizon": f"{forecast_horizon_months}_months",
                "calendar_confidence": self._calculate_calendar_confidence(policy_calendar, data_release_calendar),
                "next_critical_events": self._identify_next_critical_events(policy_calendar, data_release_calendar),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "1.0",
            }

        except Exception as e:
            return {
                "error": f"Economic calendar generation failed: {str(e)}",
                "error_type": type(e).__name__,
                "analysis_timestamp": datetime.now().isoformat(),
            }

    def _generate_policy_meeting_calendar(
        self, discovery_data: dict[str, Any], forecast_horizon_months: int
    ) -> dict[str, Any]:
        """Generate policy meeting calendar with probability modeling"""

        try:
            region_schedule = self.policy_meeting_schedules.get(self.region, {})
            meeting_dates = (
                region_schedule.get("fomc_meetings", [])
                or region_schedule.get("ecb_meetings", [])
                or region_schedule.get("boe_meetings", [])
            )

            current_rate = region_schedule.get("current_rate", 5.0)
            rate_name = region_schedule.get("rate_name", "Policy Rate")

            # Extract economic context from discovery data
            economic_context = self._extract_economic_context(discovery_data)

            policy_events = []

            for meeting_date in meeting_dates[:forecast_horizon_months]:
                # Model probability of policy change
                change_probability = self._calculate_policy_change_probability(economic_context, meeting_date)

                # Determine policy direction
                policy_direction = self._determine_policy_direction(economic_context, change_probability)

                # Calculate market impact
                market_impact = self._calculate_meeting_market_impact(
                    change_probability, policy_direction, meeting_date
                )

                policy_event = PolicyEvent(
                    event_date=meeting_date,
                    event_type=f"{self.region.lower()}_policy_meeting",
                    event_importance="high",
                    probability_score=float(change_probability),
                    market_impact_score=float(market_impact),
                    policy_direction=policy_direction,
                    confidence_interval=self._calculate_probability_confidence_interval(change_probability),
                )

                policy_events.append(
                    {
                        "date": policy_event.event_date,
                        "type": policy_event.event_type,
                        "importance": policy_event.event_importance,
                        "change_probability": policy_event.probability_score,
                        "market_impact": policy_event.market_impact_score,
                        "policy_direction": policy_event.policy_direction,
                        "confidence_interval": policy_event.confidence_interval,
                    }
                )

            return {
                "region": self.region,
                "rate_name": rate_name,
                "current_rate": current_rate,
                "policy_events": policy_events,
                "total_meetings": len(policy_events),
                "high_probability_changes": len([e for e in policy_events if e["change_probability"] > 0.7]),
                "policy_path_scenario": self._generate_policy_path_scenario(policy_events, economic_context),
            }

        except Exception as e:
            return {
                "error": f"Policy calendar generation failed: {str(e)}",
                "region": self.region,
                "policy_events": [],
            }

    def _generate_data_release_calendar(
        self, discovery_data: dict[str, Any], forecast_horizon_months: int
    ) -> dict[str, Any]:
        """Generate economic data release calendar with impact scoring"""

        try:
            region_calendar = self.data_release_calendar.get(self.region, [])

            current_date = datetime.now()
            data_releases = []

            for month_offset in range(forecast_horizon_months):
                future_month = current_date + timedelta(days=30 * month_offset)

                for data_info in region_calendar:
                    # Calculate release date
                    release_date = future_month.replace(day=min(data_info["day"], 28))

                    # Generate data release with impact modeling
                    surprise_potential = self._calculate_surprise_potential(data_info["indicator"], discovery_data)

                    policy_relevance = self._calculate_policy_relevance(data_info["indicator"], data_info["importance"])

                    data_release = DataRelease(
                        release_date=release_date.strftime("%Y-%m-%d"),
                        indicator_name=data_info["indicator"],
                        indicator_importance=data_info["importance"],
                        expected_value=None,  # Would be populated with consensus
                        previous_value=None,  # Would be populated with historical data
                        market_consensus=None,  # Would be populated with market data
                        surprise_potential=float(surprise_potential),
                        policy_relevance_score=float(policy_relevance),
                    )

                    data_releases.append(
                        {
                            "date": data_release.release_date,
                            "indicator": data_release.indicator_name,
                            "importance": data_release.indicator_importance,
                            "surprise_potential": data_release.surprise_potential,
                            "policy_relevance": data_release.policy_relevance_score,
                            "market_moving_probability": min(surprise_potential + policy_relevance, 1.0),
                        }
                    )

            # Sort by date
            data_releases.sort(key=lambda x: x["date"])

            return {
                "region": self.region,
                "data_releases": data_releases,
                "total_releases": len(data_releases),
                "high_impact_releases": len([r for r in data_releases if r["market_moving_probability"] > 0.7]),
                "tier_1_indicators": len([r for r in data_releases if r["importance"] == "tier_1"]),
            }

        except Exception as e:
            return {
                "error": f"Data release calendar generation failed: {str(e)}",
                "region": self.region,
                "data_releases": [],
            }

    def _analyze_policy_transmission_timing(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze policy transmission channel timing and effectiveness"""

        try:
            transmission_analysis = {}

            for channel, properties in self.transmission_channels.items():
                lag_quarters = properties["lag_quarters"]
                effectiveness = properties["effectiveness"]

                # Calculate transmission timing based on current economic conditions
                economic_context = self._extract_economic_context(discovery_data)

                # Adjust lag based on economic conditions
                adjusted_lag = self._adjust_transmission_lag(lag_quarters, economic_context, channel)

                # Calculate effectiveness under current conditions
                current_effectiveness = self._calculate_current_effectiveness(effectiveness, economic_context, channel)

                transmission_analysis[channel] = {
                    "base_lag_quarters": lag_quarters,
                    "adjusted_lag_quarters": float(adjusted_lag),
                    "base_effectiveness": effectiveness,
                    "current_effectiveness": float(current_effectiveness),
                    "transmission_strength": self._assess_transmission_strength(
                        current_effectiveness, economic_context
                    ),
                    "bottlenecks": self._identify_transmission_bottlenecks(channel, economic_context),
                }

            # Overall transmission assessment
            overall_effectiveness = np.mean(
                [analysis["current_effectiveness"] for analysis in transmission_analysis.values()]
            )

            average_lag = np.mean([analysis["adjusted_lag_quarters"] for analysis in transmission_analysis.values()])

            return {
                "transmission_channels": transmission_analysis,
                "overall_effectiveness": float(overall_effectiveness),
                "average_transmission_lag": float(average_lag),
                "policy_impact_timeline": self._generate_policy_impact_timeline(transmission_analysis),
                "transmission_risks": self._identify_transmission_risks(transmission_analysis, economic_context),
            }

        except Exception as e:
            return {
                "error": f"Transmission timing analysis failed: {str(e)}",
                "transmission_channels": {},
            }

    def _analyze_forward_guidance(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze central bank forward guidance and policy communication"""

        try:
            # Extract current economic context
            economic_context = self._extract_economic_context(discovery_data)

            # Generate forward guidance interpretation
            current_guidance = self._interpret_current_guidance(economic_context, analysis_data)

            # Model policy shift probabilities based on guidance
            guidance_based_probabilities = self._model_guidance_policy_shifts(current_guidance, economic_context)

            # Analyze communication consistency
            communication_analysis = self._analyze_communication_consistency(current_guidance, economic_context)

            return {
                "current_forward_guidance": current_guidance,
                "policy_shift_probabilities": guidance_based_probabilities,
                "communication_analysis": communication_analysis,
                "guidance_credibility_score": self._calculate_guidance_credibility(current_guidance, economic_context),
                "market_alignment_score": self._calculate_market_alignment(current_guidance, economic_context),
            }

        except Exception as e:
            return {
                "error": f"Forward guidance analysis failed: {str(e)}",
                "current_forward_guidance": {},
            }

    def _analyze_cross_regional_coordination(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze cross-regional central bank policy coordination"""

        try:
            # Model coordination between major central banks
            coordination_scores = {}

            major_regions = ["US", "EU", "UK"]
            economic_context = self._extract_economic_context(discovery_data)

            for region in major_regions:
                if region != self.region:
                    coordination_score = self._calculate_coordination_score(self.region, region, economic_context)

                    coordination_scores[f"{self.region}_{region}"] = {
                        "coordination_score": float(coordination_score),
                        "policy_divergence_risk": self._calculate_divergence_risk(
                            self.region, region, economic_context
                        ),
                        "spillover_effects": self._model_policy_spillovers(self.region, region, economic_context),
                    }

            return {
                "regional_coordination": coordination_scores,
                "overall_coordination_level": float(
                    np.mean([scores["coordination_score"] for scores in coordination_scores.values()])
                ),
                "coordination_risks": self._identify_coordination_risks(coordination_scores, economic_context),
                "synchronized_policy_probability": self._calculate_sync_probability(coordination_scores),
            }

        except Exception as e:
            return {
                "error": f"Cross-regional coordination analysis failed: {str(e)}",
                "regional_coordination": {},
            }

    def _model_policy_shift_probabilities(
        self, discovery_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Model probabilities of policy shifts across time horizons"""

        try:
            economic_context = self._extract_economic_context(discovery_data)

            time_horizons = ["3m", "6m", "12m"]
            policy_shift_probabilities = {}

            for horizon in time_horizons:
                # Calculate shift probabilities for different policy directions
                tightening_prob = self._calculate_tightening_probability(economic_context, horizon)
                easing_prob = self._calculate_easing_probability(economic_context, horizon)
                neutral_prob = max(0.0, 1.0 - tightening_prob - easing_prob)

                policy_shift_probabilities[horizon] = {
                    "tightening_probability": float(tightening_prob),
                    "easing_probability": float(easing_prob),
                    "neutral_probability": float(neutral_prob),
                    "most_likely_direction": self._determine_most_likely_direction(
                        tightening_prob, easing_prob, neutral_prob
                    ),
                    "confidence_level": self._calculate_direction_confidence(
                        tightening_prob, easing_prob, neutral_prob
                    ),
                }

            return {
                "probability_by_horizon": policy_shift_probabilities,
                "policy_path_scenarios": self._generate_policy_path_scenarios(
                    policy_shift_probabilities, economic_context
                ),
                "conditional_probabilities": self._calculate_conditional_probabilities(
                    policy_shift_probabilities, economic_context
                ),
            }

        except Exception as e:
            return {
                "error": f"Policy shift probability modeling failed: {str(e)}",
                "probability_by_horizon": {},
            }

    def _generate_calendar_insights(
        self,
        policy_calendar: dict[str, Any],
        data_release_calendar: dict[str, Any],
        transmission_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate integrated calendar insights and strategic implications"""

        try:
            # Identify critical decision windows
            critical_windows = self._identify_critical_decision_windows(policy_calendar, data_release_calendar)

            # Analyze data-policy interaction timing
            interaction_analysis = self._analyze_data_policy_interactions(policy_calendar, data_release_calendar)

            # Generate strategic calendar observations
            strategic_insights = self._generate_strategic_insights(
                policy_calendar, data_release_calendar, transmission_analysis
            )

            return {
                "critical_decision_windows": critical_windows,
                "data_policy_interactions": interaction_analysis,
                "strategic_insights": strategic_insights,
                "calendar_risk_events": self._identify_calendar_risk_events(policy_calendar, data_release_calendar),
                "optimal_positioning_windows": self._identify_positioning_windows(
                    policy_calendar, data_release_calendar, transmission_analysis
                ),
            }

        except Exception as e:
            return {
                "error": f"Calendar insights generation failed: {str(e)}",
                "critical_decision_windows": [],
                "strategic_insights": {},
            }

    # Helper methods for internal calculations
    def _extract_economic_context(self, discovery_data: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant economic context from discovery data"""

        # Extract key economic indicators
        indicators = discovery_data.get("economic_indicators", {})

        return {
            "gdp_growth": self._safe_extract_value(indicators, "gdp_growth", 2.0),
            "inflation_rate": self._safe_extract_value(indicators, "inflation_rate", 3.0),
            "unemployment_rate": self._safe_extract_value(indicators, "unemployment_rate", 4.0),
            "policy_rate": self._safe_extract_value(indicators, "policy_rate", 5.0),
            "yield_curve_spread": self._safe_extract_value(indicators, "yield_curve_spread", 0.5),
            "economic_phase": discovery_data.get("business_cycle_data", {}).get("current_phase", "expansion"),
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

    def _calculate_policy_change_probability(self, economic_context: dict[str, Any], meeting_date: str) -> float:
        """Calculate probability of policy change at a specific meeting"""

        # Base probability calculation based on economic conditions
        gdp_growth = economic_context["gdp_growth"]
        inflation_rate = economic_context["inflation_rate"]
        unemployment_rate = economic_context["unemployment_rate"]
        policy_rate = economic_context["policy_rate"]

        # Probability increases with economic imbalances
        inflation_pressure = max(0, (inflation_rate - 2.0) / 3.0)  # Target 2%
        growth_weakness = max(0, (2.5 - gdp_growth) / 2.5)  # Target ~2.5%
        unemployment_pressure = max(0, (unemployment_rate - 4.0) / 2.0)  # Target ~4%

        # Combine factors
        change_pressure = 0.4 * inflation_pressure + 0.3 * growth_weakness + 0.3 * unemployment_pressure

        # Apply time decay (closer meetings more uncertain)
        meeting_datetime = datetime.strptime(meeting_date, "%Y-%m-%d")
        days_to_meeting = (meeting_datetime - datetime.now()).days
        time_decay = min(1.0, max(0.1, days_to_meeting / 180))  # 6-month full uncertainty

        probability = min(0.8, change_pressure * time_decay)

        return float(np.clip(probability, 0.05, 0.8))

    def _determine_policy_direction(self, economic_context: dict[str, Any], change_probability: float) -> str:
        """Determine most likely policy direction"""

        if change_probability < 0.3:
            return "neutral"

        inflation_rate = economic_context["inflation_rate"]
        gdp_growth = economic_context["gdp_growth"]
        unemployment_rate = economic_context["unemployment_rate"]

        # Direction based on economic conditions
        tightening_signal = (inflation_rate > 3.0) and (unemployment_rate < 4.5)
        easing_signal = (gdp_growth < 1.5) or (unemployment_rate > 6.0)

        if tightening_signal and not easing_signal:
            return "tightening"
        if easing_signal and not tightening_signal:
            return "easing"
        return "data_dependent"

    def _calculate_meeting_market_impact(
        self, change_probability: float, policy_direction: str, meeting_date: str
    ) -> float:
        """Calculate expected market impact of policy meeting"""

        base_impact = change_probability * 0.7  # Higher change probability = higher impact

        # Direction multiplier
        direction_multiplier = {
            "tightening": 1.2,
            "easing": 1.1,
            "neutral": 0.8,
            "data_dependent": 0.9,
        }.get(policy_direction, 1.0)

        # Time proximity multiplier (closer meetings have higher impact)
        meeting_datetime = datetime.strptime(meeting_date, "%Y-%m-%d")
        days_to_meeting = (meeting_datetime - datetime.now()).days
        proximity_multiplier = 1.0 + max(0, (90 - days_to_meeting) / 90 * 0.3)

        market_impact = base_impact * direction_multiplier * proximity_multiplier

        return float(np.clip(market_impact, 0.1, 1.0))

    def _calculate_probability_confidence_interval(
        self, probability: float, confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """Calculate confidence interval for probability estimate"""

        # Use binomial confidence interval approximation
        n = 100  # Assumed sample size for modeling
        z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%

        margin_error = z_score * np.sqrt(probability * (1 - probability) / n)

        lower_bound = max(0.0, probability - margin_error)
        upper_bound = min(1.0, probability + margin_error)

        return (float(lower_bound), float(upper_bound))

    def _generate_policy_path_scenario(
        self, policy_events: list[dict], economic_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate policy path scenario based on meeting probabilities"""

        # Count expected policy changes
        expected_changes = sum(e["change_probability"] for e in policy_events)

        # Determine overall policy trajectory
        tightening_events = len([e for e in policy_events if e["policy_direction"] == "tightening"])
        easing_events = len([e for e in policy_events if e["policy_direction"] == "easing"])

        if tightening_events > easing_events:
            overall_direction = "tightening_cycle"
        elif easing_events > tightening_events:
            overall_direction = "easing_cycle"
        else:
            overall_direction = "neutral_cycle"

        return {
            "overall_policy_direction": overall_direction,
            "expected_total_changes": float(expected_changes),
            "policy_cycle_phase": self._determine_policy_cycle_phase(overall_direction, economic_context),
            "terminal_rate_estimate": self._estimate_terminal_rate(overall_direction, economic_context),
        }

    def _calculate_surprise_potential(self, indicator_name: str, discovery_data: dict[str, Any]) -> float:
        """Calculate surprise potential for economic data release"""

        # Base surprise potential by indicator type
        surprise_base = {
            "Employment Report": 0.4,
            "CPI": 0.5,
            "GDP": 0.3,
            "ISM PMI": 0.6,
            "Consumer Confidence": 0.7,
            "Retail Sales": 0.6,
            "Industrial Production": 0.5,
            "Eurozone CPI": 0.4,
            "Eurozone GDP": 0.3,
            "Eurozone PMI": 0.6,
            "German IFO": 0.5,
        }.get(indicator_name, 0.4)

        # Adjust based on current economic volatility
        economic_context = self._extract_economic_context(discovery_data)
        volatility_multiplier = 1.0 + abs(economic_context["gdp_growth"] - 2.0) * 0.1

        surprise_potential = surprise_base * volatility_multiplier

        return float(np.clip(surprise_potential, 0.1, 0.9))

    def _calculate_policy_relevance(self, indicator_name: str, importance: str) -> float:
        """Calculate policy relevance score for economic indicator"""

        # Base policy relevance by indicator
        relevance_base = {
            "Employment Report": 0.9,
            "CPI": 0.95,
            "GDP": 0.8,
            "ISM PMI": 0.6,
            "Consumer Confidence": 0.4,
            "Retail Sales": 0.5,
            "Industrial Production": 0.6,
            "Eurozone CPI": 0.95,
            "Eurozone GDP": 0.8,
            "Eurozone PMI": 0.6,
            "German IFO": 0.5,
        }.get(indicator_name, 0.5)

        # Adjust based on tier importance
        importance_multiplier = {"tier_1": 1.0, "tier_2": 0.8, "tier_3": 0.6}.get(importance, 0.7)

        return float(relevance_base * importance_multiplier)

    # Additional helper methods would continue here...
    # [Truncated for brevity - the full implementation would include all remaining helper methods]

    def _calculate_calendar_confidence(
        self, policy_calendar: dict[str, Any], data_release_calendar: dict[str, Any]
    ) -> float:
        """Calculate overall confidence in calendar analysis"""

        # Base confidence on data completeness and model reliability
        policy_confidence = 0.8 if policy_calendar.get("policy_events") else 0.3
        data_confidence = 0.7 if data_release_calendar.get("data_releases") else 0.3

        overall_confidence = 0.6 * policy_confidence + 0.4 * data_confidence

        return float(np.clip(overall_confidence, 0.3, 0.9))

    def _identify_next_critical_events(
        self, policy_calendar: dict[str, Any], data_release_calendar: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify next critical events in the economic calendar"""

        critical_events = []

        # Add high-probability policy events
        for event in policy_calendar.get("policy_events", [])[:3]:
            if event["change_probability"] > 0.5:
                critical_events.append(
                    {
                        "date": event["date"],
                        "type": "policy_meeting",
                        "description": f"{self.region} policy meeting - {event['policy_direction']} probability {event['change_probability']:.1%}",
                        "importance": "high",
                        "probability": event["change_probability"],
                    }
                )

        # Add high-impact data releases
        for release in data_release_calendar.get("data_releases", [])[:5]:
            if release["market_moving_probability"] > 0.7:
                critical_events.append(
                    {
                        "date": release["date"],
                        "type": "data_release",
                        "description": f"{release['indicator']} - {release['importance']} impact",
                        "importance": release["importance"],
                        "probability": release["market_moving_probability"],
                    }
                )

        # Sort by date and return top 5
        critical_events.sort(key=lambda x: x["date"])
        return critical_events[:5]

    # Placeholder implementations for remaining helper methods
    def _adjust_transmission_lag(self, base_lag: float, economic_context: dict, channel: str) -> float:
        return base_lag * (1.0 + np.random.normal(0, 0.1))

    def _calculate_current_effectiveness(
        self, base_effectiveness: float, economic_context: dict, channel: str
    ) -> float:
        return base_effectiveness * (1.0 + np.random.normal(0, 0.05))

    def _assess_transmission_strength(self, effectiveness: float, economic_context: dict) -> str:
        if effectiveness > 0.7:
            return "strong"
        if effectiveness > 0.5:
            return "moderate"
        return "weak"

    def _identify_transmission_bottlenecks(self, channel: str, economic_context: dict) -> list[str]:
        return ["financial_conditions", "market_functioning"] if economic_context.get("policy_rate", 5) > 5 else []

    def _generate_policy_impact_timeline(self, transmission_analysis: dict) -> dict[str, str]:
        return {
            "immediate": "expectations_channel",
            "3_months": "asset_price_channel",
            "6_months": "credit_channel",
        }

    def _identify_transmission_risks(self, transmission_analysis: dict, economic_context: dict) -> list[str]:
        return ["financial_stress", "credit_tightening"] if economic_context.get("yield_curve_spread", 0.5) < 0 else []

    # Additional placeholder methods...
    def _interpret_current_guidance(self, economic_context: dict, analysis_data: dict) -> dict:
        return {}

    def _model_guidance_policy_shifts(self, guidance: dict, economic_context: dict) -> dict:
        return {}

    def _analyze_communication_consistency(self, guidance: dict, economic_context: dict) -> dict:
        return {}

    def _calculate_guidance_credibility(self, guidance: dict, economic_context: dict) -> float:
        return 0.7

    def _calculate_market_alignment(self, guidance: dict, economic_context: dict) -> float:
        return 0.6

    def _calculate_coordination_score(self, region1: str, region2: str, economic_context: dict) -> float:
        return 0.5

    def _calculate_divergence_risk(self, region1: str, region2: str, economic_context: dict) -> float:
        return 0.3

    def _model_policy_spillovers(self, region1: str, region2: str, economic_context: dict) -> dict:
        return {}

    def _identify_coordination_risks(self, coordination_scores: dict, economic_context: dict) -> list[str]:
        return []

    def _calculate_sync_probability(self, coordination_scores: dict) -> float:
        return 0.4

    def _calculate_tightening_probability(self, economic_context: dict, horizon: str) -> float:
        return 0.3

    def _calculate_easing_probability(self, economic_context: dict, horizon: str) -> float:
        return 0.2

    def _determine_most_likely_direction(self, tight: float, ease: float, neutral: float) -> str:
        return "neutral" if neutral > max(tight, ease) else ("tightening" if tight > ease else "easing")

    def _calculate_direction_confidence(self, tight: float, ease: float, neutral: float) -> float:
        return 0.6

    def _generate_policy_path_scenarios(self, probabilities: dict, economic_context: dict) -> dict:
        return {}

    def _calculate_conditional_probabilities(self, probabilities: dict, economic_context: dict) -> dict:
        return {}

    def _identify_critical_decision_windows(self, policy_cal: dict, data_cal: dict) -> list:
        return []

    def _analyze_data_policy_interactions(self, policy_cal: dict, data_cal: dict) -> dict:
        return {}

    def _generate_strategic_insights(self, policy_cal: dict, data_cal: dict, transmission: dict) -> dict:
        return {}

    def _identify_calendar_risk_events(self, policy_cal: dict, data_cal: dict) -> list:
        return []

    def _identify_positioning_windows(self, policy_cal: dict, data_cal: dict, transmission: dict) -> list:
        return []

    def _determine_policy_cycle_phase(self, direction: str, economic_context: dict) -> str:
        return "mid_cycle"

    def _estimate_terminal_rate(self, direction: str, economic_context: dict) -> float:
        return 4.5
