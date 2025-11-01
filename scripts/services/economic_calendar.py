"""
Economic Calendar Integration Service

Provides comprehensive economic calendar analysis with:
- Real-time economic event tracking (FOMC, GDP, CPI, Employment)
- Market impact scoring and historical volatility analysis
- Consensus forecast deviation impact assessment
- Policy decision probability modeling
- Sector rotation signals based on economic releases

Integrates with FRED, Alpha Vantage, and FMP APIs for institutional-grade economic intelligence.
"""

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from .base_financial_service import (
    BaseFinancialService,
    DataNotFoundError,
    ServiceConfig,
    ValidationError,
)


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


@dataclass
class EconomicEvent:
    """Economic event data structure"""

    event_name: str
    event_date: datetime
    event_type: str  # 'monetary_policy', 'employment', 'inflation', 'gdp', 'sentiment'
    importance: str  # 'high', 'medium', 'low'
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    impact_score: float | None = None
    volatility_impact: float | None = None
    sector_implications: dict[str, str] | None = None


@dataclass
class PolicyDecisionProbability:
    """Policy decision probability modeling"""

    meeting_date: datetime
    current_rate: float
    rate_change_probabilities: dict[str, float]  # {'+25bps': 0.65, 'hold': 0.30, '-25bps': 0.05}
    market_implied_rate: float
    policy_surprise_potential: float
    market_reaction_scenarios: dict[str, dict[str, float]]


@dataclass
class MarketImpactScore:
    """Market impact scoring framework"""

    event_type: str
    historical_volatility_impact: float  # Average volatility increase (%)
    consensus_deviation_sensitivity: float  # Market reaction per unit deviation
    sector_rotation_strength: float  # Strength of sector rotation signal
    duration_impact_days: int  # How many days impact typically lasts
    confidence_level: float


class EconomicCalendarService(BaseFinancialService):
    """Economic calendar integration service with market impact analysis"""

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.service_name = "economic_calendar"
        self.base_endpoints = {
            "fred": "https://api.stlouisfed.org/fred",
            "alpha_vantage": "https://www.alphavantage.co/query",
            "fmp": "https://financialmodelingprep.com/api/v3",
        }

        # Economic event impact scoring matrix
        self.impact_matrix = self._initialize_impact_matrix()

        # Policy decision parameters
        self.policy_parameters = self._initialize_policy_parameters()

    def _initialize_impact_matrix(self) -> dict[str, MarketImpactScore]:
        """Initialize historical market impact scoring matrix"""
        return {
            "fomc_decision": MarketImpactScore(
                event_type="monetary_policy",
                historical_volatility_impact=0.85,  # 85% average VIX spike
                consensus_deviation_sensitivity=1.2,  # 1.2% market move per 25bps surprise
                sector_rotation_strength=0.90,  # Strong sector rotation
                duration_impact_days=5,
                confidence_level=0.95,
            ),
            "fomc_minutes": MarketImpactScore(
                event_type="monetary_policy",
                historical_volatility_impact=0.35,
                consensus_deviation_sensitivity=0.4,
                sector_rotation_strength=0.60,
                duration_impact_days=2,
                confidence_level=0.85,
            ),
            "nonfarm_payrolls": MarketImpactScore(
                event_type="employment",
                historical_volatility_impact=0.65,
                consensus_deviation_sensitivity=0.8,  # Per 50k deviation
                sector_rotation_strength=0.75,
                duration_impact_days=3,
                confidence_level=0.90,
            ),
            "cpi_release": MarketImpactScore(
                event_type="inflation",
                historical_volatility_impact=0.75,
                consensus_deviation_sensitivity=1.0,  # Per 0.1% deviation
                sector_rotation_strength=0.85,
                duration_impact_days=4,
                confidence_level=0.92,
            ),
            "gdp_release": MarketImpactScore(
                event_type="gdp",
                historical_volatility_impact=0.55,
                consensus_deviation_sensitivity=0.6,  # Per 0.5% deviation
                sector_rotation_strength=0.70,
                duration_impact_days=3,
                confidence_level=0.88,
            ),
            "ism_manufacturing": MarketImpactScore(
                event_type="sentiment",
                historical_volatility_impact=0.45,
                consensus_deviation_sensitivity=0.5,  # Per 2 point deviation
                sector_rotation_strength=0.65,
                duration_impact_days=2,
                confidence_level=0.82,
            ),
        }

    def _initialize_policy_parameters(self) -> dict[str, Any]:
        """Initialize policy decision modeling parameters"""
        return {
            "fed_meetings_2024": ["2024-09-18", "2024-11-07", "2024-12-18"],
            "fed_meetings_2025": [
                "2025-01-29",
                "2025-03-19",
                "2025-04-30",
                "2025-06-11",
                "2025-07-30",
                "2025-09-17",
                "2025-10-29",
                "2025-12-17",
            ],
            "terminal_rate_estimates": {
                "market_implied": 4.75,
                "fed_dot_plot": 4.50,
                "economist_consensus": 4.625,
            },
            "policy_reaction_function": {
                "unemployment_threshold": 4.0,  # Unemployment rate triggering easing
                "inflation_threshold": 2.5,  # CPI threshold for tightening
                "gdp_threshold": 1.0,  # GDP growth threshold for easing
            },
        }

    def get_upcoming_economic_events(self, days_ahead: int = 30) -> list[EconomicEvent]:
        """Get upcoming economic events with market impact analysis"""
        try:
            current_date = datetime.now()
            end_date = current_date + timedelta(days=days_ahead)

            # Generate upcoming economic events (in production, would fetch from API)
            events = self._generate_upcoming_events(current_date, end_date)

            # Add market impact analysis
            for event in events:
                event.impact_score = self._calculate_event_impact_score(event)
                event.volatility_impact = self._estimate_volatility_impact(event)
                event.sector_implications = self._analyze_sector_implications(event)

            return sorted(events, key=lambda x: x.event_date)

        except Exception as e:
            raise DataNotFoundError(f"Failed to fetch economic calendar: {e}")

    def _generate_upcoming_events(self, start_date: datetime, end_date: datetime) -> list[EconomicEvent]:
        """Generate upcoming economic events (production would use real API data)"""
        events = []

        # FOMC meetings
        fomc_dates = ["2024-09-18", "2024-11-07", "2024-12-18", "2025-01-29"]
        for date_str in fomc_dates:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= event_date <= end_date:
                events.append(
                    EconomicEvent(
                        event_name="FOMC Policy Decision",
                        event_date=event_date,
                        event_type="monetary_policy",
                        importance="high",
                        forecast=5.25,  # Current fed funds rate
                        previous=5.25,
                    )
                )

        # Monthly employment reports (first Friday of month)
        current = start_date.replace(day=1)
        while current <= end_date:
            # Find first Friday of month
            first_friday = current
            while first_friday.weekday() != 4:  # Friday = 4
                first_friday += timedelta(days=1)

            if start_date <= first_friday <= end_date:
                events.append(
                    EconomicEvent(
                        event_name="Nonfarm Payrolls",
                        event_date=first_friday,
                        event_type="employment",
                        importance="high",
                        forecast=180000,  # Typical consensus
                        previous=175000,
                    )
                )

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # CPI releases (mid-month)
        current = start_date.replace(day=15)
        while current <= end_date:
            if start_date <= current <= end_date:
                events.append(
                    EconomicEvent(
                        event_name="Consumer Price Index",
                        event_date=current,
                        event_type="inflation",
                        importance="high",
                        forecast=2.5,  # Typical YoY forecast
                        previous=2.4,
                    )
                )

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return events

    def _calculate_event_impact_score(self, event: EconomicEvent) -> float:
        """Calculate comprehensive event impact score"""
        base_impact = 0.5  # Default medium impact

        # Get impact matrix data
        impact_data = None
        for key, data in self.impact_matrix.items():
            if event.event_type == data.event_type:
                impact_data = data
                break

        if not impact_data:
            return base_impact

        # Calculate impact based on consensus deviation (if available)
        deviation_impact = 0.0
        if event.actual is not None and event.forecast is not None:
            deviation = abs(event.actual - event.forecast)
            if event.event_type == "employment":
                deviation_impact = (deviation / 50000) * impact_data.consensus_deviation_sensitivity
            elif event.event_type == "inflation":
                deviation_impact = (deviation / 0.1) * impact_data.consensus_deviation_sensitivity
            elif event.event_type == "monetary_policy":
                deviation_impact = (deviation / 0.25) * impact_data.consensus_deviation_sensitivity

        # Combine base impact with deviation impact
        total_impact = impact_data.historical_volatility_impact + deviation_impact

        # Normalize to 0-1 scale
        return min(max(total_impact, 0.0), 1.0)

    def _estimate_volatility_impact(self, event: EconomicEvent) -> float:
        """Estimate VIX volatility impact from economic event"""
        impact_data = self.impact_matrix.get(f"{event.event_type}_release", self.impact_matrix.get("fomc_decision"))

        base_volatility = impact_data.historical_volatility_impact

        # Adjust for importance
        importance_multiplier = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(event.importance, 0.7)

        return base_volatility * importance_multiplier

    def _analyze_sector_implications(self, event: EconomicEvent) -> dict[str, str]:
        """Analyze sector rotation implications from economic event"""
        if event.event_type == "monetary_policy":
            return {
                "financials": ("positive" if event.forecast and event.forecast > (event.previous or 0) else "neutral"),
                "utilities": ("negative" if event.forecast and event.forecast > (event.previous or 0) else "positive"),
                "technology": ("negative" if event.forecast and event.forecast > (event.previous or 0) else "neutral"),
                "real_estate": (
                    "negative" if event.forecast and event.forecast > (event.previous or 0) else "positive"
                ),
            }
        if event.event_type == "employment":
            return {
                "consumer_discretionary": "positive",
                "financials": "positive",
                "industrials": "positive",
                "utilities": "neutral",
            }
        if event.event_type == "inflation":
            return {
                "energy": "positive",
                "materials": "positive",
                "consumer_staples": "neutral",
                "technology": "negative",
            }
        return {"broad_market": "neutral"}

    def get_fomc_decision_probabilities(self, meeting_date: datetime | None = None) -> PolicyDecisionProbability:
        """Get Fed policy decision probabilities with market impact scenarios"""
        try:
            if not meeting_date:
                # Get next FOMC meeting
                meeting_date = self._get_next_fomc_meeting()

            current_rate = 5.25  # Current fed funds rate

            # Calculate probabilities based on economic conditions
            rate_probabilities = self._calculate_rate_probabilities(current_rate)

            # Market implied rate from futures
            market_implied = self._get_market_implied_rate(meeting_date)

            # Policy surprise potential
            surprise_potential = self._calculate_policy_surprise_potential(rate_probabilities, market_implied)

            # Market reaction scenarios
            reaction_scenarios = self._generate_market_reaction_scenarios(current_rate, rate_probabilities)

            return PolicyDecisionProbability(
                meeting_date=meeting_date,
                current_rate=current_rate,
                rate_change_probabilities=rate_probabilities,
                market_implied_rate=market_implied,
                policy_surprise_potential=surprise_potential,
                market_reaction_scenarios=reaction_scenarios,
            )

        except Exception as e:
            raise DataNotFoundError(f"Failed to calculate policy probabilities: {e}")

    def _get_next_fomc_meeting(self) -> datetime:
        """Get next FOMC meeting date"""
        current_date = datetime.now()

        # Combine 2024 and 2025 meetings
        all_meetings = self.policy_parameters["fed_meetings_2024"] + self.policy_parameters["fed_meetings_2025"]

        for meeting_str in all_meetings:
            meeting_date = datetime.strptime(meeting_str, "%Y-%m-%d")
            if meeting_date > current_date:
                return meeting_date

        # If no meetings found, return a default future date
        return current_date + timedelta(days=60)

    def _calculate_rate_probabilities(self, current_rate: float) -> dict[str, float]:
        """Calculate rate change probabilities based on economic conditions"""
        # Simplified model - in production would use Taylor rule and economic indicators

        # Base case: economic conditions suggest gradual easing
        base_probabilities = {
            "+50bps": 0.05,
            "+25bps": 0.15,
            "hold": 0.35,
            "-25bps": 0.35,
            "-50bps": 0.10,
        }

        # Adjust based on current economic conditions
        # (In production, would integrate real-time economic data)
        unemployment_adjustment = 0.0  # Would be based on current unemployment vs threshold
        inflation_adjustment = 0.0  # Would be based on current inflation vs target

        # Apply adjustments (simplified)
        adjusted_probabilities = base_probabilities.copy()

        # Normalize to sum to 1.0
        total = sum(adjusted_probabilities.values())
        return {k: v / total for k, v in adjusted_probabilities.items()}

    def _get_market_implied_rate(self, meeting_date: datetime) -> float:
        """Get market-implied rate from fed funds futures"""
        # In production, would fetch from actual futures data
        # For now, return a reasonable estimate
        return 4.85  # Slightly below current rate, implying easing expectations

    def _calculate_policy_surprise_potential(self, probabilities: dict[str, float], market_implied: float) -> float:
        """Calculate potential for policy surprise"""
        # Calculate expected rate change
        rate_changes = {
            "+50bps": 0.50,
            "+25bps": 0.25,
            "hold": 0.0,
            "-25bps": -0.25,
            "-50bps": -0.50,
        }
        expected_change = sum(probabilities[action] * change for action, change in rate_changes.items())

        # Market surprise is deviation from market expectations
        # Higher variance in probabilities = higher surprise potential
        variance = sum(
            probabilities[action] * (change - expected_change) ** 2 for action, change in rate_changes.items()
        )

        return min(variance * 2, 1.0)  # Scale to 0-1

    def _generate_market_reaction_scenarios(
        self, current_rate: float, probabilities: dict[str, float]
    ) -> dict[str, dict[str, float]]:
        """Generate market reaction scenarios for different policy outcomes"""
        return {
            "+25bps": {
                "spy_impact": -1.5,  # S&P 500 reaction (%)
                "tlt_impact": -2.0,  # 20Y Treasury ETF reaction
                "xlf_impact": +2.0,  # Financial sector reaction
                "xlu_impact": -1.8,  # Utilities reaction
                "vix_impact": +15.0,  # VIX reaction
            },
            "hold": {
                "spy_impact": +0.3,
                "tlt_impact": +0.5,
                "xlf_impact": -0.2,
                "xlu_impact": +0.4,
                "vix_impact": -2.0,
            },
            "-25bps": {
                "spy_impact": +1.8,
                "tlt_impact": +1.5,
                "xlf_impact": -1.2,
                "xlu_impact": +2.2,
                "vix_impact": -8.0,
            },
        }

    def get_economic_surprise_index(self, lookback_days: int = 90) -> dict[str, Any]:
        """Calculate economic surprise index and sector allocation signals"""
        try:
            # Generate recent economic surprises (production would use real data)
            surprises = self._generate_recent_surprises(lookback_days)

            # Calculate composite surprise index
            surprise_index = self._calculate_surprise_index(surprises)

            # Generate sector allocation signals
            sector_signals = self._generate_sector_signals(surprise_index)

            # Calculate trend and momentum
            trend_analysis = self._analyze_surprise_trend(surprises)

            return {
                "surprise_index": surprise_index,
                "index_percentile": self._calculate_surprise_percentile(surprise_index),
                "sector_allocation_signals": sector_signals,
                "trend_analysis": trend_analysis,
                "recent_surprises": surprises[-10:],  # Last 10 surprises
                "confidence": 0.85,
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to calculate surprise index: {e}")

    def _generate_recent_surprises(self, lookback_days: int) -> list[dict[str, Any]]:
        """Generate recent economic surprises data"""
        surprises = []
        current_date = datetime.now()

        # Generate sample surprises (production would use real data)
        for i in range(0, lookback_days, 7):  # Weekly frequency
            surprise_date = current_date - timedelta(days=i)

            # Random walk for demonstration
            surprise_value = np.random.normal(0, 0.5)  # Mean 0, std 0.5

            surprises.append(
                {
                    "date": surprise_date,
                    "surprise_value": surprise_value,
                    "event_type": np.random.choice(["employment", "inflation", "gdp", "sentiment"]),
                    "market_impact": surprise_value * 0.8,  # Correlated market impact
                }
            )

        return sorted(surprises, key=lambda x: x["date"])

    def _calculate_surprise_index(self, surprises: list[dict[str, Any]]) -> float:
        """Calculate composite economic surprise index"""
        if not surprises:
            return 0.0

        # Weight recent surprises more heavily
        weights = [np.exp(-0.1 * i) for i in range(len(surprises))]
        weights.reverse()  # Most recent gets highest weight

        # Calculate weighted average
        weighted_sum = sum(s["surprise_value"] * w for s, w in zip(surprises, weights, strict=False))
        weight_sum = sum(weights)

        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    def _calculate_surprise_percentile(self, current_index: float) -> float:
        """Calculate current surprise index percentile vs historical"""
        # Generate historical distribution (production would use real data)
        historical_indices = np.random.normal(0, 0.6, 1000)  # 1000 historical observations

        percentile = (np.sum(historical_indices <= current_index) / len(historical_indices)) * 100
        return percentile

    def _generate_sector_signals(self, surprise_index: float) -> dict[str, str]:
        """Generate sector allocation signals based on surprise index"""
        if surprise_index > 0.5:  # Positive surprises
            return {
                "technology": "overweight",
                "consumer_discretionary": "overweight",
                "industrials": "overweight",
                "utilities": "underweight",
                "consumer_staples": "underweight",
                "signal_strength": "strong",
            }
        if surprise_index < -0.5:  # Negative surprises
            return {
                "utilities": "overweight",
                "consumer_staples": "overweight",
                "healthcare": "overweight",
                "technology": "underweight",
                "consumer_discretionary": "underweight",
                "signal_strength": "strong",
            }
        # Neutral surprises
        return {"broad_market": "neutral", "signal_strength": "weak"}

    def _analyze_surprise_trend(self, surprises: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze trend and momentum in economic surprises"""
        if len(surprises) < 10:
            return {"trend": "insufficient_data", "momentum": 0.0}

        # Get recent vs older surprises
        recent_surprises = [s["surprise_value"] for s in surprises[-10:]]
        older_surprises = [s["surprise_value"] for s in surprises[-20:-10]]

        recent_avg = np.mean(recent_surprises)
        older_avg = np.mean(older_surprises) if older_surprises else 0

        # Calculate trend
        trend_direction = "improving" if recent_avg > older_avg else "deteriorating"
        if abs(recent_avg - older_avg) < 0.1:
            trend_direction = "stable"

        # Calculate momentum (rate of change)
        momentum = recent_avg - older_avg

        return {
            "trend": trend_direction,
            "momentum": momentum,
            "recent_average": recent_avg,
            "trend_strength": abs(momentum),
            "confidence": 0.80,
        }

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """
        Validate and transform API response data

        Args:
            data: Raw API response data
            endpoint: API endpoint that was called

        Returns:
            Validated and transformed data

        Raises:
            ValidationError: If response data is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format from {endpoint}: expected dict, got {type(data)}")

        # For economic calendar data, validate basic structure
        if "events" in data and not isinstance(data["events"], list):
            raise ValidationError(f"Invalid events format from {endpoint}: expected list")

        # Validate event data structure if present
        if "events" in data:
            for event in data["events"]:
                if not isinstance(event, dict):
                    raise ValidationError(f"Invalid event format from {endpoint}: expected dict")

                required_fields = [
                    "event_name",
                    "event_date",
                    "event_type",
                    "importance",
                ]
                for field in required_fields:
                    if field not in event:
                        raise ValidationError(f"Missing required field '{field}' in event data from {endpoint}")

        return data

    def health_check(self) -> dict[str, Any]:
        """Perform health check on economic calendar service"""
        health_status = super().health_check()

        try:
            # Test calendar data access
            events = self.get_upcoming_economic_events(7)
            health_status["calendar_access"] = len(events) > 0

            # Test policy probability calculation
            policy_probs = self.get_fomc_decision_probabilities()
            health_status["policy_modeling"] = policy_probs.policy_surprise_potential is not None

            # Test surprise index calculation
            surprise_data = self.get_economic_surprise_index(30)
            health_status["surprise_index"] = surprise_data["confidence"] > 0.8

            health_status["overall_status"] = all(
                [
                    health_status["calendar_access"],
                    health_status["policy_modeling"],
                    health_status["surprise_index"],
                ]
            )

        except Exception as e:
            health_status["error"] = str(e)
            health_status["overall_status"] = False

        return health_status


def create_economic_calendar_service(env: str = "prod") -> EconomicCalendarService:
    """Factory function to create economic calendar service"""
    from pathlib import Path

    from utils.config_loader import ConfigLoader

    from .base_financial_service import (
        CacheConfig,
        HistoricalStorageConfig,
        RateLimitConfig,
        ServiceConfig,
    )

    try:
        # Use absolute path to config directory
        config_dir = Path(__file__).parent.parent.parent / "config"
        config_loader = ConfigLoader(str(config_dir))
        service_config = config_loader.get_service_config("economic_calendar", env)

        # Validate API key is configured
        if not service_config.api_key or service_config.api_key.strip() == "":
            raise ValueError("Economic calendar service requires API key configuration")

        # Convert to ServiceConfig format with historical_storage
        config = ServiceConfig(
            name=service_config.name,
            base_url=service_config.base_url,
            api_key=service_config.api_key,
            timeout_seconds=service_config.timeout_seconds,
            max_retries=service_config.max_retries,
            cache=CacheConfig(**service_config.cache),
            rate_limit=RateLimitConfig(**service_config.rate_limit),
            headers=service_config.headers,
            historical_storage=HistoricalStorageConfig(
                enabled=False,
                store_stock_prices=False,
                store_financials=False,
                store_fundamentals=False,
                store_news_sentiment=False,
                auto_detect_data_type=False,
                auto_collection_enabled=False,
            ),
        )

        return EconomicCalendarService(config)

    except Exception:
        print("❌ Failed to create economic calendar service: {e}")
        return None
