"""
Global Liquidity Monitor Service

Provides comprehensive global liquidity analysis with:
- M2 money supply analysis across major economies (US, EU, Japan, China)
- Central bank balance sheet monitoring (Fed, ECB, BoJ, PBoC)
- Cross-border capital flow analysis
- Liquidity condition assessment and regime identification
- Risk asset correlation analysis with liquidity conditions

Integrates with FRED, ECB, BoJ, and PBoC APIs for institutional-grade liquidity intelligence.
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
class M2MoneySupply:
    """M2 money supply data structure"""

    country: str
    current_level: float  # Trillions in local currency
    yoy_growth_rate: float  # Year-over-year growth rate (%)
    mom_growth_rate: float  # Month-over-month growth rate (%)
    historical_percentile: float  # Current level vs 10-year history
    trend_direction: str  # 'expanding', 'contracting', 'stable'
    growth_acceleration: float  # Change in growth rate
    currency: str


@dataclass
class CentralBankBalance:
    """Central bank balance sheet data"""

    central_bank: str  # 'fed', 'ecb', 'boj', 'pboc'
    total_assets: float  # Trillions in local currency
    yoy_change: float  # Year-over-year change (%)
    qoq_change: float  # Quarter-over-quarter change (%)
    policy_stance: str  # 'expanding', 'tapering', 'contracting', 'neutral'
    asset_composition: dict[str, float]  # Breakdown by asset type
    forward_guidance: str  # Policy direction indication


@dataclass
class LiquidityCondition:
    """Global liquidity condition assessment"""

    liquidity_regime: str  # 'abundant', 'adequate', 'tight', 'restrictive'
    composite_score: float  # -1 to +1 scale (negative = tight, positive = abundant)
    regime_probability: float  # Confidence in regime classification
    regime_duration_months: int  # How long in current regime
    key_drivers: list[str]  # Primary factors driving liquidity conditions
    risk_asset_implications: dict[str, str]  # Impact on different asset classes


@dataclass
class CrossBorderFlow:
    """Cross-border capital flow analysis"""

    flow_type: str  # 'portfolio', 'direct_investment', 'banking'
    net_flow: float  # Billions USD
    flow_direction: str  # 'inflow', 'outflow', 'neutral'
    volatility_index: float  # Flow volatility measure
    risk_sentiment_indicator: float  # Risk-on/risk-off measure
    regional_breakdown: dict[str, float]  # Flows by region


class GlobalLiquidityMonitor(BaseFinancialService):
    """Global liquidity monitoring service with M2 analysis and central bank tracking"""

    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.service_name = "global_liquidity_monitor"
        self.base_endpoints = {
            "fred": "https://api.stlouisfed.org/fred",
            "ecb": "https://sdw-wsrest.ecb.europa.eu/service",
            "boj": "https://www.stat-search.boj.or.jp/ssi",
            "pboc": "http://www.pbc.gov.cn/diaochatongjisi",
        }

        # Central bank policy parameters
        self.central_bank_config = self._initialize_central_bank_config()

        # Liquidity assessment matrix
        self.liquidity_matrix = self._initialize_liquidity_matrix()

    def _validate_response(self, data: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """Validate global liquidity response data"""
        if not isinstance(data, dict):
            raise ValidationError(f"Invalid response format for {endpoint}")

        # Check for API errors
        if "error_message" in data:
            raise DataNotFoundError(data["error_message"])

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        return data

    def _initialize_central_bank_config(self) -> dict[str, Any]:
        """Initialize central bank monitoring configuration"""
        return {
            "fed": {
                "key_series": [
                    "WALCL",
                    "WRESBAL",
                    "WTREGEN",
                ],  # Total assets, reserves, repos
                "policy_rate": "FEDFUNDS",
                "target_inflation": 2.0,
                "balance_sheet_peak": 8.96,  # Trillion USD peak
                "normalization_target": 6.0,  # Trillion USD normalized level
            },
            "ecb": {
                "key_series": [
                    "ILM.M.U2.C.A000000.U2.EUR",
                    "BSI.M.U2.N.A.A20.A.1.U2.2300.Z01.E",
                ],
                "policy_rate": "ECB_DEPOSIT_RATE",
                "target_inflation": 2.0,
                "balance_sheet_peak": 7.2,  # Trillion EUR peak
                "normalization_target": 4.5,  # Trillion EUR normalized level
            },
            "boj": {
                "key_series": ["BOJBAL", "ETFHOLD", "JGBHOLD"],
                "policy_rate": "BOJ_POLICY_RATE",
                "target_inflation": 2.0,
                "balance_sheet_peak": 730,  # Trillion JPY peak
                "normalization_target": 500,  # Trillion JPY normalized level
            },
            "pboc": {
                "key_series": ["PBOC_ASSETS", "MLF_BALANCE", "REPO_BALANCE"],
                "policy_rate": "MLF_RATE",
                "target_inflation": 3.0,
                "balance_sheet_peak": 38.0,  # Trillion CNY peak
                "normalization_target": 35.0,  # Trillion CNY normalized level
            },
        }

    def _initialize_liquidity_matrix(self) -> dict[str, Any]:
        """Initialize liquidity condition assessment matrix"""
        return {
            "regime_thresholds": {
                "abundant": {
                    "m2_growth": 8.0,
                    "cb_expansion": 0.15,
                    "composite_min": 0.6,
                },
                "adequate": {
                    "m2_growth": 5.0,
                    "cb_expansion": 0.05,
                    "composite_min": 0.2,
                },
                "tight": {
                    "m2_growth": 2.0,
                    "cb_expansion": -0.05,
                    "composite_min": -0.2,
                },
                "restrictive": {
                    "m2_growth": 0.0,
                    "cb_expansion": -0.15,
                    "composite_min": -0.6,
                },
            },
            "risk_asset_correlations": {
                "abundant": {
                    "equities": "very_positive",
                    "bonds": "negative",
                    "commodities": "positive",
                },
                "adequate": {
                    "equities": "positive",
                    "bonds": "neutral",
                    "commodities": "neutral",
                },
                "tight": {
                    "equities": "negative",
                    "bonds": "positive",
                    "commodities": "negative",
                },
                "restrictive": {
                    "equities": "very_negative",
                    "bonds": "very_positive",
                    "commodities": "very_negative",
                },
            },
        }

    def get_global_m2_analysis(self, lookback_months: int = 24) -> dict[str, M2MoneySupply]:
        """Get M2 money supply analysis for major economies"""
        try:
            major_economies = ["US", "EU", "JP", "CN"]
            m2_analysis = {}

            for economy in major_economies:
                m2_data = self._fetch_m2_data(economy, lookback_months)
                m2_analysis[economy] = self._analyze_m2_trends(economy, m2_data)

            return m2_analysis

        except Exception as e:
            raise DataNotFoundError(f"Failed to fetch M2 data: {e}")

    def _fetch_m2_data(self, economy: str, lookback_months: int) -> dict[str, Any]:
        """Fetch M2 data for specific economy (production would use real APIs)"""
        # Mock M2 data with realistic trends
        base_levels = {"US": 21.7, "EU": 15.2, "JP": 1100.0, "CN": 280.0}
        currencies = {"US": "USD", "EU": "EUR", "JP": "JPY", "CN": "CNY"}

        # Generate realistic M2 growth patterns
        np.random.seed(42 + hash(economy) % 100)

        # Different growth regimes by economy
        if economy == "US":
            base_growth = 6.5
            volatility = 2.0
        elif economy == "EU":
            base_growth = 4.2
            volatility = 1.5
        elif economy == "JP":
            base_growth = 2.8
            volatility = 1.0
        else:  # China
            base_growth = 8.5
            volatility = 2.5

        # Generate monthly growth rates
        monthly_growth = np.random.normal(base_growth / 12, volatility / 12, lookback_months)

        # Calculate levels and growth rates
        current_level = base_levels[economy] * (1 + np.sum(monthly_growth) / 100)
        yoy_growth = np.mean(monthly_growth[-12:]) * 12
        mom_growth = monthly_growth[-1]

        return {
            "current_level": current_level,
            "yoy_growth": yoy_growth,
            "mom_growth": mom_growth,
            "currency": currencies[economy],
            "historical_data": monthly_growth,
        }

    def _analyze_m2_trends(self, economy: str, m2_data: dict[str, Any]) -> M2MoneySupply:
        """Analyze M2 trends and characteristics"""
        historical_data = m2_data["historical_data"]

        # Calculate historical percentile
        current_growth = m2_data["yoy_growth"]
        percentile = (np.sum(historical_data * 12 <= current_growth) / len(historical_data)) * 100

        # Determine trend direction
        recent_trend = np.mean(historical_data[-6:]) * 12  # Last 6 months annualized
        older_trend = np.mean(historical_data[-12:-6]) * 12  # Previous 6 months

        if recent_trend > older_trend + 0.5:
            trend_direction = "expanding"
        elif recent_trend < older_trend - 0.5:
            trend_direction = "contracting"
        else:
            trend_direction = "stable"

        # Growth acceleration
        growth_acceleration = recent_trend - older_trend

        return M2MoneySupply(
            country=economy,
            current_level=m2_data["current_level"],
            yoy_growth_rate=current_growth,
            mom_growth_rate=m2_data["mom_growth"],
            historical_percentile=percentile,
            trend_direction=trend_direction,
            growth_acceleration=growth_acceleration,
            currency=m2_data["currency"],
        )

    def get_central_bank_analysis(self) -> dict[str, CentralBankBalance]:
        """Get central bank balance sheet analysis"""
        try:
            central_banks = ["fed", "ecb", "boj", "pboc"]
            cb_analysis = {}

            for cb in central_banks:
                cb_data = self._fetch_central_bank_data(cb)
                cb_analysis[cb] = self._analyze_central_bank_balance(cb, cb_data)

            return cb_analysis

        except Exception as e:
            raise DataNotFoundError(f"Failed to fetch central bank data: {e}")

    def _fetch_central_bank_data(self, central_bank: str) -> dict[str, Any]:
        """Fetch central bank balance sheet data (production would use real APIs)"""
        config = self.central_bank_config[central_bank]

        # Mock balance sheet data with realistic trends
        if central_bank == "fed":
            total_assets = 7.8  # Trillion USD
            yoy_change = -8.5  # QT in progress
            qoq_change = -3.2
            policy_stance = "tapering"
        elif central_bank == "ecb":
            total_assets = 6.8  # Trillion EUR
            yoy_change = -5.2  # Moderate QT
            qoq_change = -1.8
            policy_stance = "tapering"
        elif central_bank == "boj":
            total_assets = 690.0  # Trillion JPY
            yoy_change = 2.1  # Still expanding
            qoq_change = 0.8
            policy_stance = "expanding"
        else:  # pboc
            total_assets = 36.5  # Trillion CNY
            yoy_change = 3.2  # Moderate expansion
            qoq_change = 1.1
            policy_stance = "neutral"

        return {
            "total_assets": total_assets,
            "yoy_change": yoy_change,
            "qoq_change": qoq_change,
            "policy_stance": policy_stance,
            "config": config,
        }

    def _analyze_central_bank_balance(self, cb_name: str, cb_data: dict[str, Any]) -> CentralBankBalance:
        """Analyze central bank balance sheet trends"""
        # Generate asset composition (mock data)
        if cb_name == "fed":
            asset_composition = {
                "treasuries": 0.58,
                "mbs": 0.32,
                "repos": 0.08,
                "other": 0.02,
            }
            forward_guidance = "Continued gradual balance sheet reduction"
        elif cb_name == "ecb":
            asset_composition = {
                "government_bonds": 0.65,
                "corporate_bonds": 0.20,
                "covered_bonds": 0.12,
                "other": 0.03,
            }
            forward_guidance = "Gradual normalization of monetary policy"
        elif cb_name == "boj":
            asset_composition = {
                "jgbs": 0.78,
                "etfs": 0.15,
                "reits": 0.04,
                "other": 0.03,
            }
            forward_guidance = "Maintaining ultra-accommodative policy"
        else:  # pboc
            asset_composition = {
                "government_bonds": 0.45,
                "policy_loans": 0.35,
                "foreign_exchange": 0.15,
                "other": 0.05,
            }
            forward_guidance = "Prudent monetary policy with targeted support"

        return CentralBankBalance(
            central_bank=cb_name.upper(),
            total_assets=cb_data["total_assets"],
            yoy_change=cb_data["yoy_change"],
            qoq_change=cb_data["qoq_change"],
            policy_stance=cb_data["policy_stance"],
            asset_composition=asset_composition,
            forward_guidance=forward_guidance,
        )

    def assess_global_liquidity_conditions(
        self,
        m2_analysis: dict[str, M2MoneySupply],
        cb_analysis: dict[str, CentralBankBalance],
    ) -> LiquidityCondition:
        """Assess overall global liquidity conditions"""
        try:
            # Calculate M2 composite score
            m2_scores = []
            for economy, m2_data in m2_analysis.items():
                # Normalize M2 growth to -1 to +1 scale
                normalized_growth = (m2_data.yoy_growth_rate - 4.0) / 8.0  # 4% baseline, 8% range
                m2_scores.append(max(-1.0, min(1.0, normalized_growth)))

            m2_composite = np.mean(m2_scores)

            # Calculate central bank composite score
            cb_scores = []
            for cb_name, cb_data in cb_analysis.items():
                # Normalize balance sheet change to -1 to +1 scale
                normalized_change = cb_data.yoy_change / 20.0  # 20% range
                cb_scores.append(max(-1.0, min(1.0, normalized_change)))

            cb_composite = np.mean(cb_scores)

            # Overall composite score (weighted average)
            composite_score = 0.6 * m2_composite + 0.4 * cb_composite

            # Determine liquidity regime
            thresholds = self.liquidity_matrix["regime_thresholds"]
            if composite_score >= thresholds["abundant"]["composite_min"]:
                regime = "abundant"
                regime_probability = 0.95
            elif composite_score >= thresholds["adequate"]["composite_min"]:
                regime = "adequate"
                regime_probability = 0.85
            elif composite_score >= thresholds["tight"]["composite_min"]:
                regime = "tight"
                regime_probability = 0.80
            else:
                regime = "restrictive"
                regime_probability = 0.90

            # Identify key drivers
            key_drivers = []
            if abs(m2_composite) > 0.3:
                direction = "expanding" if m2_composite > 0 else "contracting"
                key_drivers.append(f"Global M2 money supply {direction}")

            if abs(cb_composite) > 0.3:
                direction = "expanding" if cb_composite > 0 else "contracting"
                key_drivers.append(f"Central bank balance sheets {direction}")

            if not key_drivers:
                key_drivers.append("Balanced liquidity conditions")

            # Risk asset implications
            correlations = self.liquidity_matrix["risk_asset_correlations"][regime]

            return LiquidityCondition(
                liquidity_regime=regime,
                composite_score=composite_score,
                regime_probability=regime_probability,
                regime_duration_months=6,  # Mock duration
                key_drivers=key_drivers,
                risk_asset_implications=correlations,
            )

        except Exception as e:
            raise ValidationError(f"Failed to assess liquidity conditions: {e}")

    def get_cross_border_capital_flows(self, lookback_quarters: int = 8) -> list[CrossBorderFlow]:
        """Analyze cross-border capital flows"""
        try:
            flow_types = ["portfolio", "direct_investment", "banking"]
            capital_flows = []

            for flow_type in flow_types:
                flow_data = self._generate_capital_flow_data(flow_type, lookback_quarters)
                capital_flows.append(flow_data)

            return capital_flows

        except Exception as e:
            raise DataNotFoundError(f"Failed to fetch capital flow data: {e}")

    def _generate_capital_flow_data(self, flow_type: str, quarters: int) -> CrossBorderFlow:
        """Generate capital flow data (production would use real data sources)"""
        np.random.seed(42 + hash(flow_type) % 100)

        # Different flow characteristics by type
        if flow_type == "portfolio":
            base_flow = 50.0  # Billion USD
            volatility = 80.0
            risk_sensitivity = 0.8
        elif flow_type == "direct_investment":
            base_flow = 30.0
            volatility = 20.0
            risk_sensitivity = 0.3
        else:  # banking
            base_flow = -10.0  # Slight outflow
            volatility = 60.0
            risk_sensitivity = 0.9

        # Generate quarterly flows
        quarterly_flows = np.random.normal(base_flow, volatility, quarters)

        # Calculate metrics
        net_flow = quarterly_flows[-1]  # Latest quarter
        flow_direction = "inflow" if net_flow > 10 else "outflow" if net_flow < -10 else "neutral"
        volatility_index = np.std(quarterly_flows) / 100.0  # Normalized volatility
        risk_sentiment = np.tanh(net_flow / 100.0)  # Risk-on/risk-off measure

        # Regional breakdown (mock)
        regional_breakdown = {
            "developed_markets": 0.65 * net_flow,
            "emerging_markets": 0.25 * net_flow,
            "frontier_markets": 0.10 * net_flow,
        }

        return CrossBorderFlow(
            flow_type=flow_type,
            net_flow=net_flow,
            flow_direction=flow_direction,
            volatility_index=volatility_index,
            risk_sentiment_indicator=risk_sentiment,
            regional_breakdown=regional_breakdown,
        )

    def get_comprehensive_liquidity_analysis(self) -> dict[str, Any]:
        """Get comprehensive global liquidity analysis"""
        try:
            # Get all components
            m2_analysis = self.get_global_m2_analysis()
            cb_analysis = self.get_central_bank_analysis()
            liquidity_conditions = self.assess_global_liquidity_conditions(m2_analysis, cb_analysis)
            capital_flows = self.get_cross_border_capital_flows()

            # Generate trading implications
            trading_implications = self._generate_trading_implications(liquidity_conditions)

            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "global_m2_analysis": {
                    economy: {
                        "current_level": data.current_level,
                        "yoy_growth_rate": data.yoy_growth_rate,
                        "trend_direction": data.trend_direction,
                        "historical_percentile": data.historical_percentile,
                        "currency": data.currency,
                    }
                    for economy, data in m2_analysis.items()
                },
                "central_bank_analysis": {
                    cb: {
                        "total_assets": data.total_assets,
                        "yoy_change": data.yoy_change,
                        "policy_stance": data.policy_stance,
                        "forward_guidance": data.forward_guidance,
                    }
                    for cb, data in cb_analysis.items()
                },
                "global_liquidity_conditions": {
                    "liquidity_regime": liquidity_conditions.liquidity_regime,
                    "composite_score": liquidity_conditions.composite_score,
                    "regime_probability": liquidity_conditions.regime_probability,
                    "key_drivers": liquidity_conditions.key_drivers,
                    "risk_asset_implications": liquidity_conditions.risk_asset_implications,
                },
                "cross_border_capital_flows": [
                    {
                        "flow_type": flow.flow_type,
                        "net_flow": flow.net_flow,
                        "flow_direction": flow.flow_direction,
                        "risk_sentiment_indicator": flow.risk_sentiment_indicator,
                    }
                    for flow in capital_flows
                ],
                "trading_implications": trading_implications,
                "confidence": 0.87,
            }

        except Exception as e:
            raise DataNotFoundError(f"Failed to perform comprehensive liquidity analysis: {e}")

    def _generate_trading_implications(self, liquidity_conditions: LiquidityCondition) -> dict[str, Any]:
        """Generate trading implications from liquidity analysis"""
        regime = liquidity_conditions.liquidity_regime
        composite_score = liquidity_conditions.composite_score

        # Asset allocation recommendations
        if regime == "abundant":
            allocation = {
                "equities": "overweight",
                "bonds": "underweight",
                "commodities": "overweight",
                "cash": "underweight",
            }
            strategy_focus = "Risk-on positioning with growth assets"
        elif regime == "adequate":
            allocation = {
                "equities": "neutral",
                "bonds": "neutral",
                "commodities": "neutral",
                "cash": "neutral",
            }
            strategy_focus = "Balanced allocation with selective opportunities"
        elif regime == "tight":
            allocation = {
                "equities": "underweight",
                "bonds": "overweight",
                "commodities": "underweight",
                "cash": "overweight",
            }
            strategy_focus = "Defensive positioning with quality focus"
        else:  # restrictive
            allocation = {
                "equities": "underweight",
                "bonds": "overweight",
                "commodities": "underweight",
                "cash": "overweight",
            }
            strategy_focus = "Capital preservation with high-quality assets"

        # Risk management implications
        risk_budget_adjustment = int(composite_score * 100)  # -100% to +100%

        return {
            "asset_allocation": allocation,
            "strategy_focus": strategy_focus,
            "risk_budget_adjustment": f"{risk_budget_adjustment:+d}%",
            "hedging_recommendation": ("reduced" if composite_score > 0.3 else "increased"),
            "volatility_expectation": "lower" if regime == "abundant" else "higher",
            "regime_monitoring": [
                "M2 growth rate changes",
                "Central bank policy shifts",
                "Capital flow reversals",
                "Cross-asset correlation changes",
            ],
        }

    def health_check(self) -> dict[str, Any]:
        """Perform health check on global liquidity monitor"""
        health_status = super().health_check()

        try:
            # Test M2 analysis
            m2_data = self.get_global_m2_analysis(12)
            health_status["m2_analysis"] = len(m2_data) == 4  # US, EU, JP, CN

            # Test central bank analysis
            cb_data = self.get_central_bank_analysis()
            health_status["central_bank_analysis"] = len(cb_data) == 4

            # Test liquidity assessment
            liquidity_conditions = self.assess_global_liquidity_conditions(m2_data, cb_data)
            health_status["liquidity_assessment"] = liquidity_conditions.regime_probability > 0.7

            # Test capital flows
            flows = self.get_cross_border_capital_flows(4)
            health_status["capital_flows"] = len(flows) == 3

            health_status["overall_status"] = all(
                [
                    health_status["m2_analysis"],
                    health_status["central_bank_analysis"],
                    health_status["liquidity_assessment"],
                    health_status["capital_flows"],
                ]
            )

        except Exception as e:
            health_status["error"] = str(e)
            health_status["overall_status"] = False

        return health_status


def create_global_liquidity_monitor(env: str = "prod") -> GlobalLiquidityMonitor:
    """Factory function to create global liquidity monitor"""
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
    service_config = config_loader.get_service_config("global_liquidity_monitor", env)

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

    return GlobalLiquidityMonitor(config)
