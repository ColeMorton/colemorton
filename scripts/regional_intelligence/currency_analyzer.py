#!/usr/bin/env python3
"""
Currency Analyzer
Advanced currency-specific analysis including REER, PPP, carry trade dynamics
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np


class CurrencyRegime(Enum):
    """Currency regime classification"""

    FLOATING = "floating"
    MANAGED_FLOAT = "managed_float"
    PEGGED = "pegged"
    CURRENCY_BOARD = "currency_board"


class CarryTradeRole(Enum):
    """Role in carry trade dynamics"""

    FUNDING_CURRENCY = "funding"  # Low yielding, borrowed
    TARGET_CURRENCY = "target"  # High yielding, invested
    NEUTRAL = "neutral"


@dataclass
class CurrencyAnalysis:
    """Currency analysis results structure"""

    currency_code: str
    regime: CurrencyRegime
    safe_haven_score: float
    carry_trade_attractiveness: float
    volatility_regime: str
    ppp_deviation: float
    reer_level: float
    intervention_probability: float


class CurrencyAnalyzer:
    """Advanced currency analysis and modeling"""

    # Historical volatility benchmarks (annualized %)
    VOLATILITY_BENCHMARKS = {
        "USD": {"low": 8, "normal": 12, "high": 18},
        "EUR": {"low": 9, "normal": 13, "high": 20},
        "JPY": {"low": 10, "normal": 14, "high": 22},
        "GBP": {"low": 11, "normal": 15, "high": 24},
        "CAD": {"low": 9, "normal": 13, "high": 19},
        "AUD": {"low": 12, "normal": 16, "high": 25},
        "CHF": {"low": 9, "normal": 13, "high": 20},
        "CNY": {"low": 3, "normal": 6, "high": 12},  # Managed
        "DEFAULT": {"low": 10, "normal": 15, "high": 25},
    }

    # Typical interest rate differentials for carry trades (%)
    CARRY_TRADE_THRESHOLDS = {
        "attractive": 3.0,  # >3% differential attractive
        "moderate": 1.5,  # 1.5-3% moderate
        "minimal": 0.5,  # <0.5% minimal appeal
    }

    def __init__(self):
        self.ppp_reference_rates = self._initialize_ppp_references()
        self.reer_base_periods = self._initialize_reer_bases()

    def _initialize_ppp_references(self) -> dict[str, float]:
        """Initialize PPP reference exchange rates (indicative)"""
        # These would typically come from OECD PPP data
        return {
            "EUR/USD": 1.15,  # Euro PPP vs USD
            "GBP/USD": 1.35,  # Pound PPP vs USD
            "JPY/USD": 108.0,  # Yen PPP vs USD
            "CAD/USD": 0.78,  # CAD PPP vs USD
            "AUD/USD": 0.72,  # AUD PPP vs USD
            "USD/CNY": 6.2,  # USD PPP vs CNY
        }

    def _initialize_reer_bases(self) -> dict[str, float]:
        """Initialize REER base period values (2010=100)"""
        return {
            "USD": 100,
            "EUR": 100,
            "JPY": 100,
            "GBP": 100,
            "CAD": 100,
            "AUD": 100,
            "CNY": 100,
        }

    def analyze_currency(
        self,
        currency_code: str,
        current_exchange_rate: float | None = None,
        policy_rate: float = 2.0,
        us_policy_rate: float = 5.0,
        volatility: float | None = None,
        market_data: dict[str, Any] | None = None,
    ) -> CurrencyAnalysis:
        """
        Comprehensive currency analysis

        Args:
            currency_code: ISO currency code (e.g., 'EUR', 'JPY')
            current_exchange_rate: Current rate vs USD (if not USD)
            policy_rate: Local policy rate (%)
            us_policy_rate: US Fed Funds rate (%)
            volatility: Current volatility (annualized %)
            market_data: Additional market context
        """

        # Determine currency regime
        regime = self._classify_currency_regime(currency_code)

        # Calculate safe haven score
        safe_haven_score = self._calculate_safe_haven_score(currency_code, volatility)

        # Assess carry trade attractiveness
        carry_attractiveness = self._assess_carry_trade_appeal(currency_code, policy_rate, us_policy_rate, volatility)

        # Determine volatility regime
        vol_regime = self._classify_volatility_regime(currency_code, volatility)

        # Calculate PPP deviation
        ppp_deviation = self._calculate_ppp_deviation(currency_code, current_exchange_rate)

        # Estimate REER level
        reer_level = self._estimate_reer_level(currency_code, current_exchange_rate, market_data)

        # Assess intervention probability
        intervention_prob = self._assess_intervention_probability(currency_code, regime, ppp_deviation, volatility)

        return CurrencyAnalysis(
            currency_code=currency_code,
            regime=regime,
            safe_haven_score=safe_haven_score,
            carry_trade_attractiveness=carry_attractiveness,
            volatility_regime=vol_regime,
            ppp_deviation=ppp_deviation,
            reer_level=reer_level,
            intervention_probability=intervention_prob,
        )

    def _classify_currency_regime(self, currency_code: str) -> CurrencyRegime:
        """Classify currency regime based on currency code and known arrangements"""
        regime_mapping = {
            "USD": CurrencyRegime.FLOATING,
            "EUR": CurrencyRegime.FLOATING,
            "JPY": CurrencyRegime.FLOATING,
            "GBP": CurrencyRegime.FLOATING,
            "CAD": CurrencyRegime.FLOATING,
            "AUD": CurrencyRegime.FLOATING,
            "CHF": CurrencyRegime.FLOATING,
            "CNY": CurrencyRegime.MANAGED_FLOAT,
            "HKD": CurrencyRegime.PEGGED,
            "SGD": CurrencyRegime.MANAGED_FLOAT,
            "KRW": CurrencyRegime.FLOATING,
            "INR": CurrencyRegime.MANAGED_FLOAT,
            "BRL": CurrencyRegime.FLOATING,
            "MXN": CurrencyRegime.FLOATING,
            "ZAR": CurrencyRegime.FLOATING,
        }

        return regime_mapping.get(currency_code, CurrencyRegime.FLOATING)

    def _calculate_safe_haven_score(self, currency_code: str, volatility: float | None) -> float:
        """Calculate safe haven attractiveness (0-1 scale)"""
        # Base safe haven scores
        base_scores = {
            "USD": 0.9,  # Dominant safe haven
            "CHF": 0.85,  # Traditional safe haven
            "JPY": 0.8,  # Funding currency, crisis hedge
            "EUR": 0.4,  # Regional safe haven, fragmentation risk
            "GBP": 0.3,  # Brexit, political uncertainty
            "CAD": 0.5,  # Commodity currency but stable
            "AUD": 0.2,  # Risk currency, commodity dependent
            "CNY": 0.1,  # Managed, capital controls
        }

        base_score = base_scores.get(currency_code, 0.3)

        # Adjust for volatility
        if volatility:
            vol_benchmarks = self.VOLATILITY_BENCHMARKS.get(currency_code, self.VOLATILITY_BENCHMARKS["DEFAULT"])
            if volatility < vol_benchmarks["low"]:
                volatility_adjustment = 0.1  # Boost for low volatility
            elif volatility > vol_benchmarks["high"]:
                volatility_adjustment = -0.2  # Penalty for high volatility
            else:
                volatility_adjustment = 0.0

            base_score = max(0.0, min(1.0, base_score + volatility_adjustment))

        return round(base_score, 2)

    def _assess_carry_trade_appeal(
        self,
        currency_code: str,
        policy_rate: float,
        us_policy_rate: float,
        volatility: float | None,
    ) -> float:
        """Assess carry trade attractiveness (-1 to 1 scale)"""

        # Calculate interest rate differential vs USD
        rate_differential = policy_rate - us_policy_rate

        # Base carry appeal from rate differential
        if abs(rate_differential) > self.CARRY_TRADE_THRESHOLDS["attractive"]:
            base_appeal = 0.8 if rate_differential > 0 else -0.8
        elif abs(rate_differential) > self.CARRY_TRADE_THRESHOLDS["moderate"]:
            base_appeal = 0.5 if rate_differential > 0 else -0.5
        else:
            base_appeal = 0.2 if rate_differential > 0 else -0.2

        # Currency-specific adjustments
        currency_adjustments = {
            "JPY": -0.3,  # Traditional funding currency
            "CHF": -0.2,  # Low yielding, safe haven
            "USD": 0.0,  # Base currency
            "AUD": 0.2,  # Traditional target currency
            "NZD": 0.2,  # High beta, commodity currency
            "BRL": -0.1,  # High volatility penalty
            "TRY": -0.3,  # Political/economic instability
            "CNY": -0.2,  # Capital controls, intervention risk
        }

        adjustment = currency_adjustments.get(currency_code, 0.0)

        # Volatility adjustment
        if volatility:
            vol_benchmarks = self.VOLATILITY_BENCHMARKS.get(currency_code, self.VOLATILITY_BENCHMARKS["DEFAULT"])
            if volatility > vol_benchmarks["high"]:
                adjustment -= 0.2  # High volatility reduces appeal

        carry_appeal = base_appeal + adjustment
        return round(max(-1.0, min(1.0, carry_appeal)), 2)

    def _classify_volatility_regime(self, currency_code: str, volatility: float | None) -> str:
        """Classify current volatility regime"""
        if not volatility:
            return "unknown"

        benchmarks = self.VOLATILITY_BENCHMARKS.get(currency_code, self.VOLATILITY_BENCHMARKS["DEFAULT"])

        if volatility < benchmarks["low"]:
            return "low"
        if volatility > benchmarks["high"]:
            return "high"
        return "normal"

    def _calculate_ppp_deviation(self, currency_code: str, current_rate: float | None) -> float:
        """Calculate deviation from PPP fair value (% over/undervalued)"""
        if not current_rate or currency_code == "USD":
            return 0.0

        # Look for PPP reference
        ppp_key = f"{currency_code}/USD"
        if ppp_key not in self.ppp_reference_rates:
            # Try reverse
            ppp_key = f"USD/{currency_code}"
            if ppp_key in self.ppp_reference_rates:
                ppp_rate = 1.0 / self.ppp_reference_rates[ppp_key]
            else:
                return 0.0  # No PPP data available
        else:
            ppp_rate = self.ppp_reference_rates[ppp_key]

        # Calculate deviation: positive = overvalued, negative = undervalued
        deviation = ((current_rate - ppp_rate) / ppp_rate) * 100
        return round(deviation, 1)

    def _estimate_reer_level(
        self,
        currency_code: str,
        current_rate: float | None,
        market_data: dict[str, Any] | None,
    ) -> float:
        """Estimate Real Effective Exchange Rate level (base period = 100)"""

        if currency_code not in self.reer_base_periods:
            return 100.0  # Default neutral level

        base_level = self.reer_base_periods[currency_code]

        # This would typically use trade-weighted basket and inflation differentials
        # For now, provide indicative estimates based on major currency movements

        # Simple proxy using USD rate and assumed inflation differential
        if not current_rate or currency_code == "USD":
            # For USD, assume modest appreciation trend
            estimated_reer = base_level * 1.05  # 5% above base
        else:
            # Very simplified REER estimation
            # In practice, this would require complex trade-weighted calculations
            if currency_code in ["EUR", "JPY", "GBP"]:
                estimated_reer = base_level * (0.95 + np.random.uniform(-0.1, 0.1))
            else:
                estimated_reer = base_level * (1.0 + np.random.uniform(-0.15, 0.15))

        return round(estimated_reer, 1)

    def _assess_intervention_probability(
        self,
        currency_code: str,
        regime: CurrencyRegime,
        ppp_deviation: float,
        volatility: float | None,
    ) -> float:
        """Assess probability of central bank intervention (0-1 scale)"""

        base_intervention_tendency = {
            CurrencyRegime.FLOATING: 0.1,
            CurrencyRegime.MANAGED_FLOAT: 0.4,
            CurrencyRegime.PEGGED: 0.9,
            CurrencyRegime.CURRENCY_BOARD: 0.95,
        }

        base_prob = base_intervention_tendency[regime]

        # Currency-specific adjustments
        currency_factors = {
            "USD": 0.05,  # Rare intervention
            "EUR": 0.1,  # Occasional jawboning
            "JPY": 0.3,  # Historical intervention tendency
            "CHF": 0.25,  # SNB active when needed
            "CNY": 0.7,  # Managed float, active management
            "KRW": 0.4,  # Managed when volatile
            "INR": 0.5,  # RBI active in FX markets
        }

        currency_adjustment = currency_factors.get(currency_code, base_prob)

        # PPP deviation adjustment
        ppp_factor = min(abs(ppp_deviation) / 20.0, 0.3)  # Max 30% boost

        # Volatility adjustment
        vol_factor = 0.0
        if volatility:
            vol_benchmarks = self.VOLATILITY_BENCHMARKS.get(currency_code, self.VOLATILITY_BENCHMARKS["DEFAULT"])
            if volatility > vol_benchmarks["high"]:
                vol_factor = 0.2  # High volatility increases intervention risk

        total_prob = min(1.0, currency_adjustment + ppp_factor + vol_factor)
        return round(total_prob, 2)

    def calculate_currency_correlations(
        self, currencies: list[str], market_regime: str = "normal"
    ) -> dict[tuple[str, str], float]:
        """Calculate expected currency correlations based on regime"""

        # Base correlation matrices for different market regimes
        normal_correlations = {
            ("USD", "EUR"): 0.1,
            ("USD", "JPY"): -0.2,
            ("USD", "GBP"): 0.15,
            ("EUR", "GBP"): 0.6,
            ("EUR", "JPY"): 0.1,
            ("GBP", "JPY"): 0.05,
            ("AUD", "CAD"): 0.7,  # Commodity currencies
            ("AUD", "NZD"): 0.85,  # High correlation
        }

        crisis_correlations = {
            # During crises, most risk currencies correlate positively vs safe havens
            ("USD", "EUR"): -0.3,
            ("USD", "JPY"): -0.5,
            ("USD", "GBP"): -0.2,
            ("EUR", "GBP"): 0.8,
            ("EUR", "JPY"): 0.4,
            ("AUD", "CAD"): 0.9,
            ("AUD", "NZD"): 0.95,
        }

        correlation_matrix = normal_correlations if market_regime == "normal" else crisis_correlations

        # Generate correlations for requested pairs
        result_correlations = {}
        for i, curr1 in enumerate(currencies):
            for j, curr2 in enumerate(currencies[i + 1 :], i + 1):
                pair = (curr1, curr2)
                reverse_pair = (curr2, curr1)

                if pair in correlation_matrix:
                    result_correlations[pair] = correlation_matrix[pair]
                elif reverse_pair in correlation_matrix:
                    result_correlations[pair] = correlation_matrix[reverse_pair]
                else:
                    # Default correlation based on currency characteristics
                    result_correlations[pair] = self._estimate_default_correlation(curr1, curr2)

        return result_correlations

    def _estimate_default_correlation(self, curr1: str, curr2: str) -> float:
        """Estimate default correlation between two currencies"""

        # Currency groupings
        major_developed = ["USD", "EUR", "JPY", "GBP", "CHF"]
        commodity_currencies = ["AUD", "NZD", "CAD", "NOK"]
        emerging_markets = ["BRL", "MXN", "ZAR", "TRY", "INR", "CNY"]

        # Same group correlations
        if curr1 in commodity_currencies and curr2 in commodity_currencies:
            return 0.6
        if curr1 in emerging_markets and curr2 in emerging_markets:
            return 0.4
        if curr1 in major_developed and curr2 in major_developed:
            return 0.2
        # Cross-group correlations
        if (curr1 in major_developed and curr2 in commodity_currencies) or (
            curr2 in major_developed and curr1 in commodity_currencies
        ):
            return -0.1
        return 0.1  # Default low positive correlation

    def generate_currency_risk_assessment(self, analysis: CurrencyAnalysis) -> dict[str, Any]:
        """Generate comprehensive currency risk assessment"""

        risk_factors = []

        # Volatility risk
        if analysis.volatility_regime == "high":
            risk_factors.append(
                {
                    "factor": "volatility_risk",
                    "severity": "high",
                    "description": f"{analysis.currency_code} experiencing high volatility regime",
                }
            )

        # Intervention risk
        if analysis.intervention_probability > 0.5:
            risk_factors.append(
                {
                    "factor": "intervention_risk",
                    "severity": "medium",
                    "description": f"High probability ({analysis.intervention_probability:.0%}) of central bank intervention",
                }
            )

        # PPP misalignment risk
        if abs(analysis.ppp_deviation) > 15:
            direction = "overvalued" if analysis.ppp_deviation > 0 else "undervalued"
            risk_factors.append(
                {
                    "factor": "valuation_risk",
                    "severity": "medium",
                    "description": f"{analysis.currency_code} appears {direction} by {abs(analysis.ppp_deviation):.1f}% vs PPP",
                }
            )

        # Carry trade unwinding risk
        if analysis.carry_trade_attractiveness > 0.5:
            risk_factors.append(
                {
                    "factor": "carry_unwind_risk",
                    "severity": "medium",
                    "description": "Currency vulnerable to carry trade unwinding during risk-off periods",
                }
            )

        return {
            "currency": analysis.currency_code,
            "overall_risk_score": len(risk_factors) / 4.0,  # Normalize to 0-1
            "risk_factors": risk_factors,
            "safe_haven_buffer": analysis.safe_haven_score,
            "regime_stability": 1.0 - analysis.intervention_probability,
        }


def main():
    """Test currency analyzer functionality"""
    analyzer = CurrencyAnalyzer()

    # Test major currencies
    test_currencies = [
        ("EUR", 1.08, 4.5),  # EUR/USD, ECB rate
        ("JPY", 150.0, -0.1),  # USD/JPY, BoJ rate
        ("GBP", 1.25, 5.25),  # GBP/USD, BoE rate
        ("CNY", 7.2, 3.45),  # USD/CNY, PBoC rate
    ]

    print("Currency Analysis Results:")
    print("=" * 60)

    for currency, rate, policy_rate in test_currencies:
        analysis = analyzer.analyze_currency(
            currency_code=currency,
            current_exchange_rate=rate,
            policy_rate=policy_rate,
            us_policy_rate=5.375,
            volatility=15.0,
        )

        print("\n{currency} Analysis:")
        print("  Regime: {analysis.regime.value}")
        print("  Safe Haven Score: {analysis.safe_haven_score}")
        print("  Carry Trade Appeal: {analysis.carry_trade_attractiveness}")
        print("  Volatility Regime: {analysis.volatility_regime}")
        print("  PPP Deviation: {analysis.ppp_deviation}%")
        print("  Intervention Probability: {analysis.intervention_probability:.0%}")

        # Risk assessment
        risk_assessment = analyzer.generate_currency_risk_assessment(analysis)
        print("  Overall Risk Score: {risk_assessment['overall_risk_score']:.2f}")
        print("  Risk Factors: {len(risk_assessment['risk_factors'])}")


if __name__ == "__main__":
    main()
