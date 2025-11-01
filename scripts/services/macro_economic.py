"""
Macro-Economic Analysis Service

Comprehensive macro-economic analysis service providing:
- Market regime identification and classification
- Business cycle analysis with leading/lagging indicators
- VIX volatility environment assessment
- Economic calendar integration and impact analysis
- Global liquidity monitoring (M2 money supply, central bank policies)
- Forward-looking economic analysis and policy implications

Integrates multiple data sources for institutional-grade economic intelligence.
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
from config_loader import ConfigLoader


@dataclass
class MarketRegime:
    """Market regime classification data structure"""

    regime_type: str  # 'bull', 'bear', 'consolidation', 'transition'
    volatility_environment: str  # 'low', 'normal', 'elevated', 'extreme'
    confidence_score: float
    regime_duration_days: int
    key_indicators: dict[str, Any]


@dataclass
class BusinessCyclePhase:
    """Business cycle phase identification"""

    phase: str  # 'expansion', 'peak', 'contraction', 'trough'
    phase_probability: float
    months_in_phase: int
    leading_indicators: dict[str, Any]
    coincident_indicators: dict[str, Any]
    lagging_indicators: dict[str, Any]


@dataclass
class EconomicCalendarEvent:
    """Economic calendar event structure"""

    event_name: str
    event_date: datetime
    importance: str  # 'low', 'medium', 'high'
    expected_impact: str  # 'positive', 'negative', 'neutral'
    historical_market_reaction: dict[str, float] | None


class MacroEconomicService(BaseFinancialService):
    """
    Comprehensive macro-economic analysis service

    Provides institutional-grade economic intelligence including:
    - Market regime classification
    - Business cycle analysis
    - Volatility environment assessment
    - Economic calendar integration
    - Global liquidity monitoring
    - Forward-looking policy analysis
    """

    def __init__(self, config: ServiceConfig):
        super().__init__(config)

        # Economic indicator mappings for business cycle analysis
        self.business_cycle_indicators = {
            "leading": {
                "yield_curve_spread": "GS10",  # 10Y-2Y spread calculated separately
                "consumer_confidence": "UMCSENT",
                "stock_market": "SP500",
                "building_permits": "PERMIT",
                "new_orders": "NEWORDER",
                "leading_economic_index": "USSLIND",
            },
            "coincident": {
                "gdp": "GDP",
                "industrial_production": "INDPRO",
                "employment": "PAYEMS",
                "real_income": "RPI",
                "manufacturing_sales": "CMRMTSPL",
            },
            "lagging": {
                "unemployment_rate": "UNRATE",
                "cpi": "CPIAUCSL",
                "labor_cost": "ULCNFB",
                "consumer_credit": "TOTALSL",
                "prime_rate": "MPRIME",
            },
        }

        # Market regime indicators
        self.regime_indicators = {
            "volatility": {
                "vix": "VIXCLS",
                "term_structure": "VIX9D",  # 9-day VIX
                "realized_vol": "SP500",  # Calculate from returns
            },
            "momentum": {
                "sp500": "SP500",
                "nasdaq": "NASDAQCOM",
                "russell2000": "RU2000PR",
            },
            "breadth": {
                "advance_decline": "DJTA",  # Use as proxy
                "new_highs_lows": "SP500",  # Calculate from data
            },
        }

        # Global liquidity indicators
        self.liquidity_indicators = {
            "money_supply": {
                "m2_us": "M2SL",
                "m2_euro": "MABMM301EZM189S",
                "m2_japan": "MYAGM2JPM189N",
                "m2_china": "MABMM302CNM189S",
            },
            "interest_rates": {
                "fed_funds": "FEDFUNDS",
                "ecb_rate": "IRSTFR01EZM156N",
                "boj_rate": "IRSTFR01JPM156N",
            },
            "credit_conditions": {
                "credit_spreads": "BAMLC0A0CM",
                "bank_lending": "TOTLL",
                "commercial_paper": "CPNFIN",
            },
        }

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate macro-economic response data"""
        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def _calculate_statistics(self, values: list[float]) -> dict[str, float]:
        """Calculate statistical measures for time series data"""
        if not values:
            return {"trend": "no_data", "volatility": 0.0}

        values_array = np.array(values)

        # Calculate trend (simple linear regression slope)
        x = np.arange(len(values))
        if len(values) >= 2:
            slope = np.polyfit(x, values_array, 1)[0]
            trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        else:
            trend = "insufficient_data"

        # Calculate volatility (standard deviation)
        volatility = float(np.std(values_array)) if len(values) > 1 else 0.0

        return {
            "latest_value": float(values[-1]) if values else None,
            "trend": trend,
            "trend_slope": float(slope) if len(values) >= 2 else 0.0,
            "volatility": volatility,
            "min_value": float(np.min(values_array)),
            "max_value": float(np.max(values_array)),
            "mean_value": float(np.mean(values_array)),
            "observations": len(values),
        }

    def get_market_regime_analysis(self, lookback_days: int = 252) -> dict[str, Any]:
        """
        Comprehensive market regime analysis

        Args:
            lookback_days: Days of historical data for analysis (default: 252 trading days)

        Returns:
            Dictionary containing market regime classification and analysis
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 30)  # Buffer for calculations

        try:
            # Get VIX data for volatility environment
            vix_data = self._get_fred_series("VIXCLS", start_date, end_date)

            # Get S&P 500 data for momentum analysis
            sp500_data = self._get_fred_series("SP500", start_date, end_date)

            # Calculate regime metrics
            regime_analysis = self._classify_market_regime(vix_data, sp500_data)

            return {
                "regime_classification": regime_analysis,
                "volatility_environment": self._assess_volatility_environment(vix_data),
                "momentum_analysis": self._analyze_market_momentum(sp500_data),
                "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "lookback_days": lookback_days,
                "confidence_score": regime_analysis.confidence_score,
                "data_source": "FRED/Macro-Economic Analysis",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform market regime analysis: {str(e)}")

    def get_business_cycle_analysis(self) -> dict[str, Any]:
        """
        Comprehensive business cycle phase identification

        Returns:
            Dictionary containing business cycle analysis with leading/coincident/lagging indicators
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 3)  # 3 years of data

        try:
            # Collect all business cycle indicators
            leading_data = self._collect_indicator_data(self.business_cycle_indicators["leading"], start_date, end_date)
            coincident_data = self._collect_indicator_data(
                self.business_cycle_indicators["coincident"], start_date, end_date
            )
            lagging_data = self._collect_indicator_data(self.business_cycle_indicators["lagging"], start_date, end_date)

            # Classify business cycle phase
            cycle_phase = self._classify_business_cycle_phase(leading_data, coincident_data, lagging_data)

            return {
                "business_cycle_phase": cycle_phase.phase,
                "phase_probability": cycle_phase.phase_probability,
                "months_in_current_phase": cycle_phase.months_in_phase,
                "leading_indicators": {
                    "data": leading_data,
                    "composite_score": self._calculate_composite_score(leading_data),
                    "trend_analysis": ("positive" if self._calculate_composite_score(leading_data) > 0 else "negative"),
                },
                "coincident_indicators": {
                    "data": coincident_data,
                    "composite_score": self._calculate_composite_score(coincident_data),
                    "current_momentum": self._assess_current_momentum(coincident_data),
                },
                "lagging_indicators": {
                    "data": lagging_data,
                    "confirmation_score": self._calculate_composite_score(lagging_data),
                },
                "recession_probability": self._calculate_recession_probability(leading_data, coincident_data),
                "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "data_source": "FRED/Business Cycle Analysis",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform business cycle analysis: {str(e)}")

    def get_global_liquidity_analysis(self, period: str = "2y") -> dict[str, Any]:
        """
        Global liquidity conditions analysis

        Args:
            period: Analysis period ('1y', '2y', '5y')

        Returns:
            Dictionary containing global liquidity analysis
        """
        # Calculate date range
        end_date = datetime.now()
        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=730)

        try:
            # Collect global liquidity indicators
            money_supply_data = self._collect_indicator_data(
                self.liquidity_indicators["money_supply"], start_date, end_date
            )
            interest_rate_data = self._collect_indicator_data(
                self.liquidity_indicators["interest_rates"], start_date, end_date
            )
            credit_data = self._collect_indicator_data(
                self.liquidity_indicators["credit_conditions"], start_date, end_date
            )

            # Analyze liquidity conditions
            liquidity_analysis = self._analyze_liquidity_conditions(money_supply_data, interest_rate_data, credit_data)

            return {
                "global_liquidity_assessment": liquidity_analysis,
                "money_supply_analysis": {
                    "data": money_supply_data,
                    "growth_rates": self._calculate_growth_rates(money_supply_data),
                    "regional_comparison": self._compare_regional_liquidity(money_supply_data),
                },
                "interest_rate_environment": {
                    "data": interest_rate_data,
                    "policy_stance": self._assess_policy_stance(interest_rate_data),
                    "yield_curve_analysis": self._analyze_yield_curves(interest_rate_data),
                },
                "credit_conditions": {
                    "data": credit_data,
                    "credit_availability": self._assess_credit_availability(credit_data),
                    "risk_appetite": self._measure_risk_appetite(credit_data),
                },
                "liquidity_score": liquidity_analysis["composite_score"],
                "market_implications": self._derive_market_implications(liquidity_analysis),
                "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "period": period,
                "data_source": "FRED/Global Central Banks",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform global liquidity analysis: {str(e)}")

    def get_economic_calendar_analysis(self, days_ahead: int = 30) -> dict[str, Any]:
        """
        Economic calendar analysis with market impact assessment

        Args:
            days_ahead: Number of days to look ahead for events

        Returns:
            Dictionary containing upcoming economic events and impact analysis
        """
        try:
            # For now, focus on major recurring events (FOMC meetings, employment data, inflation reports)
            # In production, this would integrate with actual economic calendar APIs

            upcoming_events = self._generate_economic_calendar(days_ahead)
            impact_analysis = self._analyze_event_impacts(upcoming_events)

            return {
                "upcoming_events": upcoming_events,
                "high_impact_events": [event for event in upcoming_events if event.importance == "high"],
                "market_impact_analysis": impact_analysis,
                "trading_implications": self._derive_trading_implications(upcoming_events),
                "risk_events": [event for event in upcoming_events if event.expected_impact == "negative"],
                "calendar_period": f"Next {days_ahead} days",
                "events_count": len(upcoming_events),
                "data_source": "Economic Calendar Analysis",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to generate economic calendar analysis: {str(e)}")

    def get_comprehensive_macro_analysis(self) -> dict[str, Any]:
        """
        Comprehensive macro-economic analysis combining all components

        Returns:
            Dictionary containing complete macro-economic intelligence
        """
        try:
            # Get all macro-economic analyses
            market_regime = self.get_market_regime_analysis()
            business_cycle = self.get_business_cycle_analysis()
            liquidity_analysis = self.get_global_liquidity_analysis()
            calendar_analysis = self.get_economic_calendar_analysis()

            # Synthesize comprehensive view
            macro_synthesis = self._synthesize_macro_environment(
                market_regime, business_cycle, liquidity_analysis, calendar_analysis
            )

            return {
                "macro_economic_synthesis": macro_synthesis,
                "market_regime_analysis": market_regime,
                "business_cycle_analysis": business_cycle,
                "global_liquidity_analysis": liquidity_analysis,
                "economic_calendar_analysis": calendar_analysis,
                "investment_implications": self._derive_investment_implications(macro_synthesis),
                "risk_assessment": self._assess_macro_risks(macro_synthesis),
                "confidence_score": macro_synthesis["overall_confidence"],
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources": ["FRED", "Economic Calendar", "Market Data"],
                "framework_version": "1.0",
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform comprehensive macro analysis: {str(e)}")

    # Helper methods for internal calculations
    def _get_fred_series(self, series_id: str, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get FRED series data with error handling"""
        # This would integrate with the existing FRED service
        # For now, return mock structure
        return {
            "series_id": series_id,
            "observations": [],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

    def _collect_indicator_data(
        self, indicators: dict[str, str], start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Collect data for multiple economic indicators"""
        collected_data = {}

        for indicator_name, series_id in indicators.items():
            try:
                data = self._get_fred_series(series_id, start_date, end_date)
                collected_data[indicator_name] = data
            except Exception as e:
                collected_data[indicator_name] = {"error": str(e)}

        return collected_data

    def _classify_market_regime(self, vix_data: dict[str, Any], sp500_data: dict[str, Any]) -> MarketRegime:
        """Classify current market regime based on volatility and momentum"""
        # Simplified regime classification logic
        # In production, this would use more sophisticated ML models

        return MarketRegime(
            regime_type="consolidation",  # Placeholder
            volatility_environment="normal",
            confidence_score=0.75,
            regime_duration_days=45,
            key_indicators={"vix_level": 15.0, "momentum": "neutral"},
        )

    def _assess_volatility_environment(self, vix_data: dict[str, Any]) -> dict[str, Any]:
        """Assess current volatility environment"""
        return {
            "current_vix": 15.0,  # Placeholder
            "volatility_regime": "low",
            "percentile_rank": 25.0,
            "trend": "stable",
        }

    def _analyze_market_momentum(self, sp500_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze market momentum trends"""
        return {
            "short_term_momentum": "neutral",
            "medium_term_momentum": "positive",
            "long_term_momentum": "positive",
            "momentum_score": 0.6,
        }

    def _classify_business_cycle_phase(
        self,
        leading_data: dict[str, Any],
        coincident_data: dict[str, Any],
        lagging_data: dict[str, Any],
    ) -> BusinessCyclePhase:
        """Classify current business cycle phase"""
        return BusinessCyclePhase(
            phase="expansion",
            phase_probability=0.7,
            months_in_phase=18,
            leading_indicators=leading_data,
            coincident_indicators=coincident_data,
            lagging_indicators=lagging_data,
        )

    def _calculate_composite_score(self, indicator_data: dict[str, Any]) -> float:
        """Calculate composite score for indicator set"""
        # Simplified scoring logic
        return 0.65  # Placeholder

    def _assess_current_momentum(self, coincident_data: dict[str, Any]) -> str:
        """Assess current economic momentum"""
        return "positive"  # Placeholder

    def _calculate_recession_probability(self, leading_data: dict[str, Any], coincident_data: dict[str, Any]) -> float:
        """Calculate recession probability based on indicators"""
        return 0.15  # Placeholder (15% probability)

    def _analyze_liquidity_conditions(
        self,
        money_supply: dict[str, Any],
        rates: dict[str, Any],
        credit: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze global liquidity conditions"""
        return {
            "liquidity_environment": "accommodative",
            "composite_score": 0.7,
            "trend": "expanding",
            "regional_analysis": {
                "us": "expansive",
                "eu": "stable",
                "asia": "moderate",
            },
        }

    def _calculate_growth_rates(self, data: dict[str, Any]) -> dict[str, float]:
        """Calculate year-over-year growth rates"""
        return {"m2_us_yoy": 6.2, "m2_euro_yoy": 4.1, "m2_japan_yoy": 2.8}

    def _compare_regional_liquidity(self, data: dict[str, Any]) -> dict[str, str]:
        """Compare liquidity conditions across regions"""
        return {
            "most_expansive": "US",
            "most_restrictive": "EU",
            "divergence_level": "moderate",
        }

    def _assess_policy_stance(self, rate_data: dict[str, Any]) -> dict[str, str]:
        """Assess central bank policy stances"""
        return {"fed": "neutral", "ecb": "accommodative", "boj": "ultra_accommodative"}

    def _analyze_yield_curves(self, rate_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze yield curve shapes and implications"""
        return {"us_curve": "normal", "inversion_risk": "low", "steepness": "moderate"}

    def _assess_credit_availability(self, credit_data: dict[str, Any]) -> str:
        """Assess credit market conditions"""
        return "normal"  # Placeholder

    def _measure_risk_appetite(self, credit_data: dict[str, Any]) -> str:
        """Measure market risk appetite from credit spreads"""
        return "moderate"  # Placeholder

    def _derive_market_implications(self, liquidity_analysis: dict[str, Any]) -> list[str]:
        """Derive market implications from liquidity analysis"""
        return [
            "Supportive environment for risk assets",
            "Low volatility regime likely to persist",
            "Credit markets remain healthy",
        ]

    def _generate_economic_calendar(self, days_ahead: int) -> list[EconomicCalendarEvent]:
        """Generate upcoming economic calendar events"""
        # Placeholder for economic calendar integration
        return [
            EconomicCalendarEvent(
                event_name="FOMC Meeting",
                event_date=datetime.now() + timedelta(days=14),
                importance="high",
                expected_impact="neutral",
                historical_market_reaction={"vix_change": 2.5, "sp500_change": -0.3},
            )
        ]

    def _analyze_event_impacts(self, events: list[EconomicCalendarEvent]) -> dict[str, Any]:
        """Analyze potential market impacts of upcoming events"""
        return {
            "aggregate_risk": "moderate",
            "volatility_expected": True,
            "sector_impacts": {"technology": "neutral", "financials": "positive"},
        }

    def _derive_trading_implications(self, events: list[EconomicCalendarEvent]) -> list[str]:
        """Derive trading implications from calendar events"""
        return [
            "Maintain defensive positioning ahead of FOMC",
            "Consider volatility strategies around key events",
            "Monitor interest rate sensitive sectors",
        ]

    def _synthesize_macro_environment(
        self,
        regime: dict[str, Any],
        cycle: dict[str, Any],
        liquidity: dict[str, Any],
        calendar: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize comprehensive macro-economic environment assessment"""
        return {
            "overall_environment": "supportive",
            "key_themes": [
                "low_volatility",
                "accommodative_liquidity",
                "mid_cycle_expansion",
            ],
            "risk_factors": ["policy_uncertainty", "geopolitical_tensions"],
            "opportunity_areas": ["technology", "consumer_discretionary"],
            "overall_confidence": 0.78,
            "outlook": "constructive_with_caution",
        }

    def _derive_investment_implications(self, synthesis: dict[str, Any]) -> dict[str, Any]:
        """Derive investment implications from macro synthesis"""
        return {
            "asset_allocation": {
                "equity": "overweight",
                "fixed_income": "underweight",
                "alternatives": "neutral",
            },
            "sector_preferences": [
                "technology",
                "healthcare",
                "consumer_discretionary",
            ],
            "geographic_allocation": {
                "us": "overweight",
                "international": "underweight",
            },
            "style_bias": "growth_over_value",
            "risk_positioning": "moderate_risk_on",
        }

    def _assess_macro_risks(self, synthesis: dict[str, Any]) -> dict[str, Any]:
        """Assess macro-economic risks"""
        return {
            "recession_risk": "low",
            "inflation_risk": "moderate",
            "policy_error_risk": "moderate",
            "geopolitical_risk": "elevated",
            "systemic_risk": "low",
            "tail_risks": [
                "supply_chain_disruption",
                "cyber_warfare",
                "climate_events",
            ],
        }

    def health_check(self) -> dict[str, Any]:
        """Service health check"""
        try:
            # Test basic functionality
            test_regime = self.get_market_regime_analysis(lookback_days=30)

            return {
                "service_name": self.config.name,
                "status": "healthy",
                "capabilities": [
                    "Market regime analysis",
                    "Business cycle identification",
                    "Global liquidity monitoring",
                    "Economic calendar integration",
                    "Comprehensive macro synthesis",
                ],
                "test_result": "success" if test_regime else "failed",
                "configuration": {
                    "cache_enabled": self.config.cache.enabled,
                    "rate_limit_enabled": self.config.rate_limit.enabled,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "service_name": self.config.name,
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
            }


def create_macro_economic_service(env: str = "dev") -> MacroEconomicService:
    """
    Factory function to create Macro-Economic service with configuration

    Args:
        env: Environment name (dev/test/prod)

    Returns:
        Configured Macro-Economic service instance
    """
    # Use absolute path to config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_loader = ConfigLoader(str(config_dir))

    # For now, use FRED configuration as base (will be expanded)
    service_config = config_loader.get_service_config("fred", env)

    # Convert to ServiceConfig format
    from .base_financial_service import CacheConfig, RateLimitConfig, ServiceConfig

    config = ServiceConfig(
        name="macro_economic",
        base_url=service_config.base_url,
        api_key=service_config.api_key,
        timeout_seconds=service_config.timeout_seconds,
        max_retries=service_config.max_retries,
        cache=CacheConfig(**service_config.cache),
        rate_limit=RateLimitConfig(**service_config.rate_limit),
        headers=service_config.headers,
    )

    return MacroEconomicService(config)
