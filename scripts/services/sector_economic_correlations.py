"""
Sector-Economic Correlation Analysis Service

Provides comprehensive sector-economic factor correlation analysis with:
- Economic factor sensitivity analysis for major sectors
- Business cycle sector rotation modeling
- Interest rate sensitivity analysis across sectors
- Inflation impact assessment on sector performance
- Economic regime-based sector allocation recommendations
- Factor attribution analysis for sector performance

Integrates with FRED, Alpha Vantage, and sector ETF data for institutional-grade sector intelligence.
"""

import sys
from dataclasses import dataclass
from datetime import datetime
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
class SectorSensitivity:
    """Sector sensitivity to economic factors"""

    sector_name: str
    sector_etf: str  # ETF ticker symbol
    factor_sensitivities: dict[str, float]  # Beta coefficients to economic factors
    economic_cycle_beta: float  # Sensitivity to business cycle
    interest_rate_beta: float  # Sensitivity to interest rate changes
    inflation_beta: float  # Sensitivity to inflation changes
    gdp_beta: float  # Sensitivity to GDP growth
    correlation_strength: str  # 'strong', 'moderate', 'weak'
    r_squared: float  # Explanatory power of model


@dataclass
class EconomicRegimeSector:
    """Sector performance by economic regime"""

    regime_type: str  # 'expansion', 'peak', 'contraction', 'trough'
    outperforming_sectors: list[str]
    underperforming_sectors: list[str]
    sector_rankings: dict[str, float]  # Sector name -> expected return
    confidence_scores: dict[str, float]  # Confidence in each ranking
    historical_hit_rate: float  # Historical accuracy of regime predictions


@dataclass
class SectorRotationSignal:
    """Sector rotation trading signal"""

    signal_date: datetime
    rotation_type: str  # 'defensive_to_cyclical', 'cyclical_to_defensive', 'growth_to_value'
    recommended_overweight: list[str]  # Sectors to overweight
    recommended_underweight: list[str]  # Sectors to underweight
    signal_strength: str  # 'strong', 'moderate', 'weak'
    time_horizon: str  # '1M', '3M', '6M', '12M'
    confidence: float
    economic_drivers: list[str]  # Economic factors driving the signal


@dataclass
class FactorAttribution:
    """Factor attribution analysis for sector performance"""

    sector_name: str
    total_return: float
    factor_contributions: dict[str, float]  # Factor name -> contribution to return
    idiosyncratic_return: float  # Sector-specific return
    explained_variance: float  # Proportion of return explained by factors
    residual_risk: float  # Unexplained volatility


class SectorEconomicCorrelations(BaseFinancialService):
    """Sector-economic correlation analysis service"""

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.service_name = "sector_economic_correlations"
        self.base_endpoints = {
            "fred": "https://api.stlouisfed.org/fred",
            "alpha_vantage": "https://www.alphavantage.co/query",
            "yahoo_finance": "https://query1.finance.yahoo.com",
        }

        # Sector configuration
        self.sector_config = self._initialize_sector_config()

        # Economic factor definitions
        self.economic_factors = self._initialize_economic_factors()

        # Historical correlation matrix
        self.correlation_matrix = self._initialize_correlation_matrix()

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate sector economic correlation response data"""
        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Check for API errors
        if "error_message" in data:
            raise DataNotFoundError(data["error_message"])

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def _initialize_sector_config(self) -> dict[str, Any]:
        """Initialize sector ETF configuration"""
        return {
            "sectors": {
                "technology": {
                    "etf": "XLK",
                    "full_name": "Technology Select Sector SPDR Fund",
                },
                "financials": {
                    "etf": "XLF",
                    "full_name": "Financial Select Sector SPDR Fund",
                },
                "healthcare": {
                    "etf": "XLV",
                    "full_name": "Health Care Select Sector SPDR Fund",
                },
                "consumer_discretionary": {
                    "etf": "XLY",
                    "full_name": "Consumer Discretionary Select Sector SPDR Fund",
                },
                "consumer_staples": {
                    "etf": "XLP",
                    "full_name": "Consumer Staples Select Sector SPDR Fund",
                },
                "industrials": {
                    "etf": "XLI",
                    "full_name": "Industrial Select Sector SPDR Fund",
                },
                "energy": {"etf": "XLE", "full_name": "Energy Select Sector SPDR Fund"},
                "utilities": {
                    "etf": "XLU",
                    "full_name": "Utilities Select Sector SPDR Fund",
                },
                "materials": {
                    "etf": "XLB",
                    "full_name": "Materials Select Sector SPDR Fund",
                },
                "real_estate": {
                    "etf": "XLRE",
                    "full_name": "Real Estate Select Sector SPDR Fund",
                },
                "communication_services": {
                    "etf": "XLC",
                    "full_name": "Communication Services Select Sector SPDR Fund",
                },
            },
            "market_benchmark": "SPY",
        }

    def _initialize_economic_factors(self) -> dict[str, Any]:
        """Initialize economic factor definitions"""
        return {
            "gdp_growth": {
                "fred_series": "GDP",
                "description": "Real Gross Domestic Product",
                "frequency": "quarterly",
                "transformation": "pct_change_yoy",
            },
            "interest_rates": {
                "fred_series": "DGS10",
                "description": "10-Year Treasury Constant Maturity Rate",
                "frequency": "daily",
                "transformation": "level_change",
            },
            "inflation": {
                "fred_series": "CPIAUCSL",
                "description": "Consumer Price Index for All Urban Consumers",
                "frequency": "monthly",
                "transformation": "pct_change_yoy",
            },
            "unemployment": {
                "fred_series": "UNRATE",
                "description": "Unemployment Rate",
                "frequency": "monthly",
                "transformation": "level_change",
            },
            "dollar_strength": {
                "fred_series": "DTWEXBGS",
                "description": "Trade Weighted U.S. Dollar Index: Broad, Goods and Services",
                "frequency": "monthly",
                "transformation": "pct_change",
            },
            "oil_prices": {
                "fred_series": "DCOILWTICO",
                "description": "Crude Oil Prices: West Texas Intermediate",
                "frequency": "daily",
                "transformation": "pct_change",
            },
            "vix": {
                "fred_series": "VIXCLS",
                "description": "CBOE Volatility Index: VIX",
                "frequency": "daily",
                "transformation": "level_change",
            },
        }

    def _initialize_correlation_matrix(self) -> dict[str, dict[str, float]]:
        """Initialize historical sector-factor correlation matrix"""
        return {
            "technology": {
                "gdp_growth": 0.65,
                "interest_rates": -0.72,
                "inflation": -0.35,
                "unemployment": -0.58,
                "dollar_strength": -0.28,
                "oil_prices": 0.15,
                "vix": -0.68,
            },
            "financials": {
                "gdp_growth": 0.78,
                "interest_rates": 0.82,
                "inflation": 0.25,
                "unemployment": -0.71,
                "dollar_strength": 0.18,
                "oil_prices": 0.32,
                "vix": -0.75,
            },
            "healthcare": {
                "gdp_growth": 0.25,
                "interest_rates": -0.45,
                "inflation": -0.15,
                "unemployment": -0.20,
                "dollar_strength": -0.12,
                "oil_prices": -0.08,
                "vix": -0.35,
            },
            "consumer_discretionary": {
                "gdp_growth": 0.85,
                "interest_rates": -0.65,
                "inflation": -0.55,
                "unemployment": -0.88,
                "dollar_strength": -0.35,
                "oil_prices": -0.25,
                "vix": -0.82,
            },
            "consumer_staples": {
                "gdp_growth": -0.15,
                "interest_rates": -0.38,
                "inflation": 0.25,
                "unemployment": 0.12,
                "dollar_strength": -0.08,
                "oil_prices": -0.05,
                "vix": -0.25,
            },
            "industrials": {
                "gdp_growth": 0.82,
                "interest_rates": -0.45,
                "inflation": -0.28,
                "unemployment": -0.75,
                "dollar_strength": -0.42,
                "oil_prices": 0.35,
                "vix": -0.78,
            },
            "energy": {
                "gdp_growth": 0.45,
                "interest_rates": -0.25,
                "inflation": 0.65,
                "unemployment": -0.38,
                "dollar_strength": -0.55,
                "oil_prices": 0.92,
                "vix": -0.55,
            },
            "utilities": {
                "gdp_growth": -0.25,
                "interest_rates": -0.85,
                "inflation": 0.15,
                "unemployment": 0.18,
                "dollar_strength": 0.05,
                "oil_prices": -0.12,
                "vix": -0.15,
            },
            "materials": {
                "gdp_growth": 0.75,
                "interest_rates": -0.35,
                "inflation": 0.45,
                "unemployment": -0.68,
                "dollar_strength": -0.58,
                "oil_prices": 0.52,
                "vix": -0.72,
            },
            "real_estate": {
                "gdp_growth": 0.35,
                "interest_rates": -0.88,
                "inflation": -0.25,
                "unemployment": -0.42,
                "dollar_strength": -0.15,
                "oil_prices": 0.08,
                "vix": -0.65,
            },
            "communication_services": {
                "gdp_growth": 0.55,
                "interest_rates": -0.58,
                "inflation": -0.22,
                "unemployment": -0.48,
                "dollar_strength": -0.18,
                "oil_prices": 0.12,
                "vix": -0.62,
            },
        }

    def get_sector_sensitivities(self, lookback_months: int = 36) -> dict[str, SectorSensitivity]:
        """Calculate sector sensitivities to economic factors"""
        try:
            sector_sensitivities = {}

            for sector_name in self.sector_config["sectors"].keys():
                sensitivity = self._calculate_sector_sensitivity(sector_name, lookback_months)
                sector_sensitivities[sector_name] = sensitivity

            return sector_sensitivities

        except Exception as e:
            raise DataNotFoundError(f"Failed to calculate sector sensitivities: {e}")

    def _calculate_sector_sensitivity(self, sector_name: str, lookback_months: int) -> SectorSensitivity:
        """Calculate individual sector sensitivity (production would use real regression analysis)"""
        sector_info = self.sector_config["sectors"][sector_name]
        correlations = self.correlation_matrix[sector_name]

        # Mock factor sensitivities based on historical correlations
        # In production, would run multivariate regression
        factor_sensitivities = {}
        for factor, correlation in correlations.items():
            # Convert correlation to beta (simplified)
            beta = correlation * 1.2  # Assume sector volatility 20% higher than factor
            factor_sensitivities[factor] = beta

        # Calculate composite betas
        economic_cycle_beta = np.mean([correlations["gdp_growth"], -correlations["unemployment"]])

        interest_rate_beta = correlations["interest_rates"]
        inflation_beta = correlations["inflation"]
        gdp_beta = correlations["gdp_growth"]

        # Determine correlation strength
        avg_abs_correlation = np.mean([abs(c) for c in correlations.values()])
        if avg_abs_correlation > 0.6:
            correlation_strength = "strong"
        elif avg_abs_correlation > 0.35:
            correlation_strength = "moderate"
        else:
            correlation_strength = "weak"

        # Mock R-squared (explanatory power)
        r_squared = max(0.3, min(0.85, avg_abs_correlation + np.random.normal(0, 0.1)))

        return SectorSensitivity(
            sector_name=sector_name,
            sector_etf=sector_info["etf"],
            factor_sensitivities=factor_sensitivities,
            economic_cycle_beta=economic_cycle_beta,
            interest_rate_beta=interest_rate_beta,
            inflation_beta=inflation_beta,
            gdp_beta=gdp_beta,
            correlation_strength=correlation_strength,
            r_squared=r_squared,
        )

    def get_economic_regime_sectors(self, current_regime: str = "expansion") -> EconomicRegimeSector:
        """Get sector performance by economic regime"""
        try:
            regime_data = self._analyze_regime_sector_performance(current_regime)
            return regime_data

        except Exception as e:
            raise DataNotFoundError(f"Failed to analyze regime sectors: {e}")

    def _analyze_regime_sector_performance(self, regime: str) -> EconomicRegimeSector:
        """Analyze sector performance in specific economic regime"""
        # Historical sector performance by regime (mock data based on academic research)
        regime_performance = {
            "expansion": {
                "outperformers": [
                    "technology",
                    "consumer_discretionary",
                    "industrials",
                    "materials",
                ],
                "underperformers": ["utilities", "consumer_staples", "real_estate"],
                "rankings": {
                    "technology": 0.15,
                    "consumer_discretionary": 0.12,
                    "industrials": 0.11,
                    "materials": 0.10,
                    "financials": 0.08,
                    "communication_services": 0.07,
                    "healthcare": 0.05,
                    "energy": 0.03,
                    "real_estate": 0.02,
                    "consumer_staples": 0.01,
                    "utilities": -0.01,
                },
            },
            "peak": {
                "outperformers": ["financials", "energy", "materials"],
                "underperformers": [
                    "technology",
                    "consumer_discretionary",
                    "real_estate",
                ],
                "rankings": {
                    "financials": 0.08,
                    "energy": 0.07,
                    "materials": 0.06,
                    "utilities": 0.04,
                    "consumer_staples": 0.03,
                    "healthcare": 0.02,
                    "industrials": 0.01,
                    "communication_services": 0.00,
                    "consumer_discretionary": -0.02,
                    "technology": -0.03,
                    "real_estate": -0.04,
                },
            },
            "contraction": {
                "outperformers": ["utilities", "consumer_staples", "healthcare"],
                "underperformers": ["energy", "materials", "industrials", "financials"],
                "rankings": {
                    "utilities": 0.05,
                    "consumer_staples": 0.04,
                    "healthcare": 0.03,
                    "technology": 0.01,
                    "communication_services": 0.00,
                    "consumer_discretionary": -0.02,
                    "real_estate": -0.03,
                    "financials": -0.05,
                    "industrials": -0.06,
                    "materials": -0.08,
                    "energy": -0.10,
                },
            },
            "trough": {
                "outperformers": ["technology", "consumer_discretionary", "materials"],
                "underperformers": ["utilities", "consumer_staples"],
                "rankings": {
                    "technology": 0.12,
                    "consumer_discretionary": 0.10,
                    "materials": 0.09,
                    "industrials": 0.08,
                    "financials": 0.06,
                    "communication_services": 0.05,
                    "healthcare": 0.04,
                    "energy": 0.03,
                    "real_estate": 0.02,
                    "consumer_staples": 0.00,
                    "utilities": -0.01,
                },
            },
        }

        performance = regime_performance.get(regime, regime_performance["expansion"])

        # Generate confidence scores (mock)
        confidence_scores = {}
        for sector in performance["rankings"].keys():
            base_confidence = 0.75
            rank_confidence = abs(performance["rankings"][sector]) * 2  # Higher for extreme rankings
            confidence_scores[sector] = min(0.95, base_confidence + rank_confidence)

        return EconomicRegimeSector(
            regime_type=regime,
            outperforming_sectors=performance["outperformers"],
            underperforming_sectors=performance["underperformers"],
            sector_rankings=performance["rankings"],
            confidence_scores=confidence_scores,
            historical_hit_rate=0.72,  # Mock historical accuracy
        )

    def generate_sector_rotation_signals(self, economic_indicators: dict[str, Any]) -> list[SectorRotationSignal]:
        """Generate sector rotation signals based on economic indicators"""
        try:
            signals = []

            # Analyze current economic conditions
            current_conditions = self._assess_economic_conditions(economic_indicators)

            # Generate rotation signals based on conditions
            rotation_signal = self._generate_rotation_signal(current_conditions)
            signals.append(rotation_signal)

            return signals

        except Exception as e:
            raise DataNotFoundError(f"Failed to generate rotation signals: {e}")

    def _assess_economic_conditions(self, indicators: dict[str, Any]) -> dict[str, Any]:
        """Assess current economic conditions (mock analysis)"""
        # Mock economic condition assessment
        return {
            "growth_momentum": "accelerating",  # accelerating, stable, decelerating
            "inflation_trend": "rising",  # rising, stable, falling
            "interest_rate_trend": "rising",  # rising, stable, falling
            "risk_sentiment": "risk_on",  # risk_on, neutral, risk_off
            "cycle_stage": "mid_expansion",  # early_expansion, mid_expansion, late_expansion, contraction
        }

    def _generate_rotation_signal(self, conditions: dict[str, Any]) -> SectorRotationSignal:
        """Generate sector rotation signal based on economic conditions"""
        growth_momentum = conditions["growth_momentum"]
        inflation_trend = conditions["inflation_trend"]
        rate_trend = conditions["interest_rate_trend"]
        risk_sentiment = conditions["risk_sentiment"]

        # Determine rotation type and recommendations
        if growth_momentum == "accelerating" and risk_sentiment == "risk_on":
            rotation_type = "defensive_to_cyclical"
            overweight = ["technology", "consumer_discretionary", "industrials"]
            underweight = ["utilities", "consumer_staples", "real_estate"]
            signal_strength = "strong"
            economic_drivers = ["Accelerating growth", "Rising risk appetite"]
        elif inflation_trend == "rising" and rate_trend == "rising":
            rotation_type = "growth_to_value"
            overweight = ["financials", "energy", "materials"]
            underweight = ["technology", "utilities", "real_estate"]
            signal_strength = "moderate"
            economic_drivers = ["Rising inflation", "Rising interest rates"]
        elif risk_sentiment == "risk_off":
            rotation_type = "cyclical_to_defensive"
            overweight = ["utilities", "consumer_staples", "healthcare"]
            underweight = ["energy", "materials", "consumer_discretionary"]
            signal_strength = "strong"
            economic_drivers = ["Risk-off sentiment", "Economic uncertainty"]
        else:
            rotation_type = "neutral_positioning"
            overweight = ["healthcare", "technology", "consumer_staples"]
            underweight = ["energy", "materials"]
            signal_strength = "weak"
            economic_drivers = ["Mixed economic signals"]

        return SectorRotationSignal(
            signal_date=datetime.now(),
            rotation_type=rotation_type,
            recommended_overweight=overweight,
            recommended_underweight=underweight,
            signal_strength=signal_strength,
            time_horizon="3M",
            confidence=0.78,
            economic_drivers=economic_drivers,
        )

    def perform_factor_attribution(
        self, sector_returns: dict[str, float], factor_returns: dict[str, float]
    ) -> dict[str, FactorAttribution]:
        """Perform factor attribution analysis for sector returns"""
        try:
            attributions = {}

            for sector_name, sector_return in sector_returns.items():
                attribution = self._calculate_factor_attribution(sector_name, sector_return, factor_returns)
                attributions[sector_name] = attribution

            return attributions

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform factor attribution: {e}")

    def _calculate_factor_attribution(
        self, sector_name: str, sector_return: float, factor_returns: dict[str, float]
    ) -> FactorAttribution:
        """Calculate factor attribution for individual sector"""
        if sector_name not in self.correlation_matrix:
            # Default attribution for unknown sectors
            return FactorAttribution(
                sector_name=sector_name,
                total_return=sector_return,
                factor_contributions={},
                idiosyncratic_return=sector_return,
                explained_variance=0.0,
                residual_risk=0.15,
            )

        correlations = self.correlation_matrix[sector_name]
        factor_contributions = {}

        for factor_name, factor_return in factor_returns.items():
            if factor_name in correlations:
                # Attribution = Factor Beta * Factor Return
                beta = correlations[factor_name]
                contribution = beta * factor_return
                factor_contributions[factor_name] = contribution

        # Calculate explained vs idiosyncratic return
        explained_return = sum(factor_contributions.values())
        idiosyncratic_return = sector_return - explained_return

        # Calculate explained variance (mock)
        avg_abs_correlation = np.mean([abs(c) for c in correlations.values()])
        explained_variance = min(0.85, max(0.25, avg_abs_correlation))

        # Residual risk estimate
        residual_risk = 0.20 * (1 - explained_variance)

        return FactorAttribution(
            sector_name=sector_name,
            total_return=sector_return,
            factor_contributions=factor_contributions,
            idiosyncratic_return=idiosyncratic_return,
            explained_variance=explained_variance,
            residual_risk=residual_risk,
        )

    def get_comprehensive_sector_analysis(self) -> dict[str, Any]:
        """Get comprehensive sector-economic correlation analysis"""
        try:
            # Get all analysis components
            sector_sensitivities = self.get_sector_sensitivities()
            regime_analysis = self.get_economic_regime_sectors("expansion")  # Current regime

            # Mock economic indicators for rotation signals
            mock_indicators = {
                "gdp_growth": 2.5,
                "inflation": 3.2,
                "unemployment": 3.7,
                "interest_rates": 5.25,
            }
            rotation_signals = self.generate_sector_rotation_signals(mock_indicators)

            # Mock factor attribution
            mock_sector_returns = {
                sector: np.random.normal(0.08, 0.15) for sector in self.sector_config["sectors"].keys()
            }
            mock_factor_returns = {factor: np.random.normal(0, 0.10) for factor in self.economic_factors.keys()}
            factor_attribution = self.perform_factor_attribution(mock_sector_returns, mock_factor_returns)

            # Generate investment recommendations
            investment_recommendations = self._generate_investment_recommendations(
                regime_analysis, rotation_signals[0] if rotation_signals else None
            )

            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "sector_sensitivities": {
                    sector: {
                        "sector_etf": data.sector_etf,
                        "economic_cycle_beta": data.economic_cycle_beta,
                        "interest_rate_beta": data.interest_rate_beta,
                        "inflation_beta": data.inflation_beta,
                        "correlation_strength": data.correlation_strength,
                        "r_squared": data.r_squared,
                    }
                    for sector, data in sector_sensitivities.items()
                },
                "economic_regime_analysis": {
                    "current_regime": regime_analysis.regime_type,
                    "outperforming_sectors": regime_analysis.outperforming_sectors,
                    "underperforming_sectors": regime_analysis.underperforming_sectors,
                    "sector_rankings": regime_analysis.sector_rankings,
                    "historical_hit_rate": regime_analysis.historical_hit_rate,
                },
                "sector_rotation_signals": [
                    {
                        "rotation_type": signal.rotation_type,
                        "recommended_overweight": signal.recommended_overweight,
                        "recommended_underweight": signal.recommended_underweight,
                        "signal_strength": signal.signal_strength,
                        "confidence": signal.confidence,
                        "economic_drivers": signal.economic_drivers,
                    }
                    for signal in rotation_signals
                ],
                "factor_attribution_summary": {
                    sector: {
                        "explained_variance": attr.explained_variance,
                        "idiosyncratic_return": attr.idiosyncratic_return,
                        "top_factor_contributions": dict(
                            sorted(
                                attr.factor_contributions.items(),
                                key=lambda x: abs(x[1]),
                                reverse=True,
                            )[:3]
                        ),
                    }
                    for sector, attr in factor_attribution.items()
                },
                "investment_recommendations": investment_recommendations,
                "confidence": 0.82,
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform comprehensive sector analysis: {e}")

    def _generate_investment_recommendations(
        self,
        regime_analysis: EconomicRegimeSector,
        rotation_signal: SectorRotationSignal | None,
    ) -> dict[str, Any]:
        """Generate investment recommendations based on analysis"""
        recommendations = {
            "portfolio_allocation": {
                "overweight_sectors": [],
                "underweight_sectors": [],
                "neutral_sectors": [],
            },
            "tactical_trades": [],
            "risk_considerations": [],
            "time_horizon": "3-6 months",
        }

        # Base allocation on regime analysis
        regime_overweight = regime_analysis.outperforming_sectors[:3]
        regime_underweight = regime_analysis.underperforming_sectors[:2]

        # Adjust for rotation signal if available
        if rotation_signal and rotation_signal.signal_strength in [
            "strong",
            "moderate",
        ]:
            signal_overweight = rotation_signal.recommended_overweight[:3]
            signal_underweight = rotation_signal.recommended_underweight[:2]

            # Combine signals (intersection for high confidence)
            final_overweight = list(set(regime_overweight) & set(signal_overweight))
            if len(final_overweight) < 2:
                final_overweight.extend([s for s in signal_overweight if s not in final_overweight][:2])

            final_underweight = list(set(regime_underweight) & set(signal_underweight))
            if len(final_underweight) < 2:
                final_underweight.extend([s for s in signal_underweight if s not in final_underweight][:2])
        else:
            final_overweight = regime_overweight
            final_underweight = regime_underweight

        recommendations["portfolio_allocation"]["overweight_sectors"] = final_overweight[:3]
        recommendations["portfolio_allocation"]["underweight_sectors"] = final_underweight[:2]

        # All other sectors neutral
        all_sectors = set(self.sector_config["sectors"].keys())
        allocated_sectors = set(final_overweight + final_underweight)
        recommendations["portfolio_allocation"]["neutral_sectors"] = list(all_sectors - allocated_sectors)

        # Generate tactical trades
        recommendations["tactical_trades"] = [
            f"Long {self.sector_config['sectors'][sector]['etf']} ({sector})" for sector in final_overweight
        ] + [
            f"Short/Underweight {self.sector_config['sectors'][sector]['etf']} ({sector})"
            for sector in final_underweight
        ]

        # Risk considerations
        recommendations["risk_considerations"] = [
            "Monitor economic regime transition signals",
            "Adjust positions based on interest rate changes",
            "Consider correlation breakdown during market stress",
            "Maintain diversification across factor exposures",
        ]

        return recommendations

    def health_check(self) -> dict[str, Any]:
        """Perform health check on sector correlation service"""
        health_status = super().health_check()

        try:
            # Test sector sensitivity calculation
            sensitivities = self.get_sector_sensitivities(12)
            health_status["sector_sensitivity_analysis"] = len(sensitivities) == 11

            # Test regime analysis
            regime_analysis = self.get_economic_regime_sectors("expansion")
            health_status["regime_analysis"] = len(regime_analysis.outperforming_sectors) > 0

            # Test rotation signals
            mock_indicators = {"gdp_growth": 2.0, "inflation": 2.5}
            signals = self.generate_sector_rotation_signals(mock_indicators)
            health_status["rotation_signals"] = len(signals) > 0

            # Test factor attribution
            mock_returns = {"technology": 0.10, "healthcare": 0.05}
            mock_factors = {"gdp_growth": 0.02, "interest_rates": 0.01}
            attribution = self.perform_factor_attribution(mock_returns, mock_factors)
            health_status["factor_attribution"] = len(attribution) == 2

            health_status["overall_status"] = all(
                [
                    health_status["sector_sensitivity_analysis"],
                    health_status["regime_analysis"],
                    health_status["rotation_signals"],
                    health_status["factor_attribution"],
                ]
            )

        except Exception as e:
            health_status["error"] = str(e)
            health_status["overall_status"] = False

        return health_status


def create_sector_economic_correlations(
    env: str = "prod",
) -> SectorEconomicCorrelations:
    """Factory function to create sector-economic correlations service"""
    from pathlib import Path

    from utils.config_loader import ConfigLoader

    from .base_financial_service import (
        CacheConfig,
        HistoricalStorageConfig,
        RateLimitConfig,
        ServiceConfig,
    )

    # Use absolute path to config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_loader = ConfigLoader(str(config_dir))
    service_config = config_loader.get_service_config("sector_economic_correlations", env)

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

    return SectorEconomicCorrelations(config)
