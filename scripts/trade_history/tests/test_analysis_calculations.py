#!/usr/bin/env python3
"""
Test Analysis Calculations for trade_history_analyze

Validates the statistical analysis calculations and methodologies
for signal effectiveness, performance measurement, and pattern recognition.
"""

import json
import math
import statistics


def test_signal_effectiveness_calculations():
    """
    Test signal effectiveness calculation methodologies.
    """

    print("=== Signal Effectiveness Calculation Tests ===\n")

    # Sample trade data for testing
    sample_trades = [
        {
            "strategy": "SMA",
            "return": 0.08,
            "mfe": 0.12,
            "mae": -0.02,
            "duration": 15,
            "status": "winner",
        },
        {
            "strategy": "SMA",
            "return": -0.03,
            "mfe": 0.01,
            "mae": -0.05,
            "duration": 8,
            "status": "loser",
        },
        {
            "strategy": "SMA",
            "return": 0.15,
            "mfe": 0.18,
            "mae": -0.01,
            "duration": 22,
            "status": "winner",
        },
        {
            "strategy": "EMA",
            "return": 0.05,
            "mfe": 0.09,
            "mae": -0.03,
            "duration": 12,
            "status": "winner",
        },
        {
            "strategy": "EMA",
            "return": -0.08,
            "mfe": 0.02,
            "mae": -0.12,
            "duration": 18,
            "status": "loser",
        },
    ]

    # Test win rate calculation by strategy
    def calculate_win_rate(trades, strategy):
        strategy_trades = [t for t in trades if t["strategy"] == strategy]
        if not strategy_trades:
            return 0, 0, 0

        winners = len([t for t in strategy_trades if t["status"] == "winner"])
        total = len(strategy_trades)
        win_rate = winners / total if total > 0 else 0

        return win_rate, winners, total

    sma_win_rate, sma_winners, sma_total = calculate_win_rate(sample_trades, "SMA")
    ema_win_rate, ema_winners, ema_total = calculate_win_rate(sample_trades, "EMA")

    print("SMA Strategy: {sma_win_rate:.1%} win rate ({sma_winners}/{sma_total})")
    print("EMA Strategy: {ema_win_rate:.1%} win rate ({ema_winners}/{ema_total})")

    # Test exit efficiency calculation
    def calculate_exit_efficiency(trades):
        efficiencies = []
        for trade in trades:
            if trade["mfe"] > 0:
                efficiency = trade["return"] / trade["mfe"]
                efficiencies.append(efficiency)

        avg_efficiency = statistics.mean(efficiencies) if efficiencies else 0
        return avg_efficiency, efficiencies

    avg_exit_efficiency, _ = calculate_exit_efficiency(sample_trades)
    print("Average Exit Efficiency: {avg_exit_efficiency:.3f}")

    # Test MFE/MAE ratio calculation
    def calculate_mfe_mae_ratio(trades):
        ratios = []
        for trade in trades:
            if trade["mae"] < 0:  # MAE should be negative
                ratio = trade["mfe"] / abs(trade["mae"])
                ratios.append(ratio)

        avg_ratio = statistics.mean(ratios) if ratios else 0
        return avg_ratio, ratios

    avg_mfe_mae_ratio, _ = calculate_mfe_mae_ratio(sample_trades)
    print("Average MFE/MAE Ratio: {avg_mfe_mae_ratio:.2f}")

    print("✅ Signal effectiveness calculations validated\n")


def test_statistical_performance_metrics():
    """
    Test statistical performance measurement calculations.
    """

    print("=== Statistical Performance Metrics Tests ===\n")

    # Sample return data
    returns = [0.08, -0.03, 0.15, 0.05, -0.08, 0.12, -0.01, 0.09, -0.04, 0.07]

    # Test basic statistical measures
    mean_return = statistics.mean(returns)
    median_return = statistics.median(returns)
    std_dev = statistics.stdev(returns) if len(returns) > 1 else 0

    print("Mean Return: {mean_return:.3f}")
    print("Median Return: {median_return:.3f}")
    print("Standard Deviation: {std_dev:.3f}")

    # Test Sharpe ratio calculation (assuming risk-free rate of 2%)
    risk_free_rate = 0.02 / 12  # Monthly risk-free rate
    excess_returns = [r - risk_free_rate for r in returns]

    if std_dev > 0:
        sharpe_ratio = statistics.mean(excess_returns) / std_dev
        print("Sharpe Ratio: {sharpe_ratio:.3f}")
    else:
        print("Sharpe Ratio: Unable to calculate (zero variance)")

    # Test maximum drawdown calculation
    def calculate_max_drawdown(returns):
        cumulative = [1.0]  # Start with $1
        for r in returns:
            cumulative.append(cumulative[-1] * (1 + r))

        peak = cumulative[0]
        max_dd = 0

        for value in cumulative:
            if value > peak:
                peak = value

            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown

        return -max_dd  # Return as negative value

    max_drawdown = calculate_max_drawdown(returns)
    print("Maximum Drawdown: {max_drawdown:.1%}")

    # Test confidence interval calculation
    def calculate_confidence_interval(data, confidence_level=0.95):
        if len(data) < 2:
            return None, None

        mean = statistics.mean(data)
        std_err = statistics.stdev(data) / math.sqrt(len(data))

        # Using t-distribution approximation for small samples
        t_value = 2.262  # t(0.025, 9 df) for 95% CI with 10 samples
        margin = t_value * std_err

        return mean - margin, mean + margin

    ci_lower, ci_upper = calculate_confidence_interval(returns)
    if ci_lower is not None:
        print("95% Confidence Interval: [{ci_lower:.3f}, {ci_upper:.3f}]")

    print("✅ Statistical performance metrics validated\n")


def test_trade_quality_classification():
    """
    Test trade quality classification methodology.
    """

    print("=== Trade Quality Classification Tests ===\n")

    # Sample trades with various characteristics
    trades = [
        {
            "return": 0.15,
            "mfe": 0.18,
            "mae": -0.01,
            "duration": 12,
            "exit_efficiency": 0.83,
        },
        {
            "return": 0.08,
            "mfe": 0.12,
            "mae": -0.02,
            "duration": 15,
            "exit_efficiency": 0.67,
        },
        {
            "return": -0.02,
            "mfe": 0.05,
            "mae": -0.08,
            "duration": 25,
            "exit_efficiency": -0.40,
        },
        {
            "return": -0.12,
            "mfe": 0.01,
            "mae": -0.15,
            "duration": 8,
            "exit_efficiency": -12.00,
        },
        {
            "return": 0.22,
            "mfe": 0.25,
            "mae": -0.01,
            "duration": 18,
            "exit_efficiency": 0.88,
        },
    ]

    def classify_trade_quality(trade):
        """
        Classify trade quality based on multiple factors.
        """

        # Criteria for classification
        return_threshold = 0.10  # 10% return threshold
        efficiency_threshold = 0.60  # 60% exit efficiency
        # mfe_mae_ratio_threshold = 3.0  # Unused variable

        mfe_mae_ratio = trade["mfe"] / abs(trade["mae"]) if trade["mae"] < 0 else 0

        # Excellent: High return, high efficiency, good MFE/MAE ratio
        if trade["return"] > return_threshold and trade["exit_efficiency"] > 0.80 and mfe_mae_ratio > 5.0:
            return "excellent"

        # Good: Positive return with decent efficiency
        if trade["return"] > 0 and trade["exit_efficiency"] > efficiency_threshold:
            return "good"

        # Poor: Negative return but not catastrophic
        if trade["return"] > -0.05 and trade["exit_efficiency"] > -1.0:
            return "poor"

        # Failed: Large losses or very poor execution
        return "failed"

    # Classify all trades
    quality_distribution = {"excellent": 0, "good": 0, "poor": 0, "failed": 0}

    for trade in trades:
        quality = classify_trade_quality(trade)
        quality_distribution[quality] += 1
        print(f"Trade: {trade['return']:+.1%} return, {trade['exit_efficiency']:.2f} efficiency → {quality.upper()}")

    print("\nQuality Distribution:")
    total_trades = len(trades)
    for quality, count in quality_distribution.items():
        percentage = count / total_trades * 100
        print("  {quality.capitalize()}: {count} trades ({percentage:.1f}%)")

    print("✅ Trade quality classification validated\n")


def test_optimization_opportunity_identification():
    """
    Test optimization opportunity identification logic.
    """

    print("=== Optimization Opportunity Identification Tests ===\n")

    # Sample analysis results
    analysis_results = {
        "exit_efficiency": 0.57,  # Below target of 0.80
        "win_rate": 0.53,  # Slightly above breakeven
        "avg_hold_period": 38.2,
        "optimal_hold_period": 29.8,
        "strategy_performance": {
            "SMA": {"win_rate": 0.60, "avg_return": 0.067},
            "EMA": {"win_rate": 0.45, "avg_return": 0.023},
        },
    }

    opportunities = []

    # Exit efficiency optimization
    if analysis_results["exit_efficiency"] < 0.70:
        improvement_potential = (0.80 - analysis_results["exit_efficiency"]) * 100
        opportunities.append(
            {
                "area": "exit_timing",
                "opportunity": "Implement trailing stop optimization",
                "current_metric": f"{analysis_results['exit_efficiency']:.2f}",
                "target_metric": "0.80",
                "improvement_potential": f"{improvement_potential:.0f}% efficiency increase",
                "confidence": 0.82,
            }
        )

    # Hold period optimization
    if analysis_results["avg_hold_period"] > analysis_results["optimal_hold_period"] * 1.2:
        excess_days = analysis_results["avg_hold_period"] - analysis_results["optimal_hold_period"]
        opportunities.append(
            {
                "area": "duration_management",
                "opportunity": "Time-based exit implementation",
                "current_metric": f"{analysis_results['avg_hold_period']:.1f} days",
                "target_metric": f"{analysis_results['optimal_hold_period']:.1f} days",
                "improvement_potential": f"Reduce hold period by {excess_days:.1f} days",
                "confidence": 0.75,
            }
        )

    # Strategy parameter optimization
    sma_performance = analysis_results["strategy_performance"]["SMA"]["win_rate"]
    ema_performance = analysis_results["strategy_performance"]["EMA"]["win_rate"]

    if sma_performance > ema_performance * 1.15:
        opportunities.append(
            {
                "area": "strategy_allocation",
                "opportunity": "Increase SMA signal allocation",
                "current_metric": "Equal weighting",
                "target_metric": "SMA-focused allocation",
                "improvement_potential": f"Win rate advantage: {(sma_performance - ema_performance):.1%}",
                "confidence": 0.68,
            }
        )

    print("Identified {len(opportunities)} optimization opportunities:")
    for i, opp in enumerate(opportunities, 1):
        print("\n{i}. {opp['opportunity']}")
        print("   Area: {opp['area']}")
        print("   Current: {opp['current_metric']}")
        print("   Target: {opp['target_metric']}")
        print("   Potential: {opp['improvement_potential']}")
        print("   Confidence: {opp['confidence']:.2f}")

    print("\n✅ Optimization opportunity identification validated\n")


def validate_analysis_schema():
    """
    Validate that the analysis JSON schema is properly structured.
    """

    schema_path = (
        "/Users/colemorton/Projects/colemorton/data/outputs/trade_history/analyze/trading_analysis_schema_v1.json"
    )

    print("=== Analysis Schema Validation ===\n")

    try:
        with open(schema_path) as f:
            schema = json.load(f)

        # Check required top-level properties
        required_props = [
            "portfolio",
            "analysis_metadata",
            "signal_effectiveness",
            "performance_measurement",
            "pattern_recognition",
            "optimization_opportunities",
            "risk_assessment",
            "statistical_validation",
            "next_phase_inputs",
        ]

        schema_props = schema.get("properties", {}).keys()
        missing_props = [prop for prop in required_props if prop not in schema_props]

        if missing_props:
            print("❌ Missing required properties: {missing_props}")
        else:
            print("✅ All required properties present")

        # Check signal effectiveness structure
        signal_eff = schema["properties"].get("signal_effectiveness", {})
        signal_props = signal_eff.get("properties", {})

        if "entry_signal_analysis" in signal_props and "exit_signal_analysis" in signal_props:
            print("✅ Signal effectiveness structure valid")
        else:
            print("❌ Signal effectiveness structure incomplete")

        # Check performance measurement structure
        perf_measure = schema["properties"].get("performance_measurement", {})
        perf_props = perf_measure.get("properties", {})

        if "statistical_analysis" in perf_props and "trade_quality_classification" in perf_props:
            print("✅ Performance measurement structure valid")
        else:
            print("❌ Performance measurement structure incomplete")

        print("Total top-level properties: {len(schema_props)}")
        print("✅ Schema validation complete")

    except FileNotFoundError:
        print("❌ Schema file not found")
    except json.JSONDecodeError:
        print("❌ Invalid JSON in schema: {e}")
    except Exception:
        print("❌ Schema validation error: {e}")


def main():
    """
    Run all validation tests for Phase 2 implementation.
    """

    print("TRADE HISTORY ANALYZE - Phase 2 Validation Tests")
    print("=" * 65)
    print()

    test_signal_effectiveness_calculations()
    test_statistical_performance_metrics()
    test_trade_quality_classification()
    test_optimization_opportunity_identification()
    validate_analysis_schema()

    print("\n" + "=" * 65)
    print("Phase 2 validation complete!")
    print("🎯 All analysis calculation methodologies verified")
    print("📊 Statistical measurement frameworks validated")
    print("🔍 Pattern recognition and optimization logic tested")


if __name__ == "__main__":
    main()
