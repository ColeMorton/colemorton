#!/usr/bin/env python3
"""
Test script for dashboard scalability features.

This script creates synthetic datasets of various sizes to test
the scalability features of the dashboard generator.
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    TradeData,
)
from scripts.utils.scalability_manager import create_scalability_manager


def generate_synthetic_trades(count: int) -> list[TradeData]:
    """Generate synthetic trade data for testing."""
    tickers = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "TSLA",
        "META",
        "NVDA",
        "AMD",
        "NFLX",
        "CRM",
        "ADBE",
        "INTC",
        "CSCO",
        "ORCL",
        "IBM",
        "PYPL",
        "SHOP",
        "SQ",
        "UBER",
        "LYFT",
        "SNOW",
        "PLTR",
        "CRWD",
        "ZM",
    ]
    qualities = ["Excellent", "Good", "Poor", "Failed", "Poor Setup"]

    trades = []
    for i in range(count):
        # Random returns with bias toward positive
        if random.random() < 0.6:  # 60% positive trades
            return_pct = random.uniform(0.5, 25.0)
        else:
            return_pct = random.uniform(-15.0, -0.5)

        duration = random.randint(1, 90)
        entry_date = datetime.now() - timedelta(days=duration + random.randint(1, 30))
        exit_date = entry_date + timedelta(days=duration)

        trade = TradeData(
            rank=i + 1,
            ticker=random.choice(tickers),
            strategy=random.choice(["Momentum", "Mean Reversion", "Breakout", "Swing"]),
            entry_date=entry_date.strftime("%Y-%m-%d"),
            exit_date=exit_date.strftime("%Y-%m-%d"),
            return_pct=return_pct,
            duration_days=duration,
            quality=random.choice(qualities),
        )
        trades.append(trade)

    return trades


def generate_synthetic_monthly_data(months: int) -> list[MonthlyPerformance]:
    """Generate synthetic monthly performance data."""
    monthly_data = []
    current_date = datetime(2024, 1, 1)

    for i in range(months):
        win_rate = random.uniform(40, 80)
        avg_return = random.uniform(-2, 8)

        monthly = MonthlyPerformance(
            month=current_date.strftime("%B"),
            year=current_date.year,
            trades_closed=random.randint(3, 15),
            win_rate=win_rate,
            average_return=avg_return,
            market_context=random.choice(["Bullish", "Bearish", "Sideways", "Volatile"]),
        )
        monthly_data.append(monthly)

        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    return monthly_data


def test_scalability_detection():
    """Test scalability manager detection capabilities."""
    print("🧪 Testing Scalability Detection\n")

    # Test configuration
    config = {
        "scalability": {
            "trade_volume_thresholds": {"small": 50, "medium": 100, "large": 200},
            "monthly_timeline_thresholds": {"compact": 3, "medium": 8, "condensed": 12},
            "density_management": {
                "scatter_plot": {
                    "low_density": 50,
                    "medium_density": 150,
                    "high_density": 200,
                }
            },
        }
    }

    scalability_manager = create_scalability_manager(config)

    # Test different dataset sizes
    test_cases = [
        (15, 3, "Small dataset (current)"),
        (75, 6, "Medium dataset"),
        (150, 9, "Large dataset"),
        (200, 12, "Maximum dataset"),
    ]

    for trade_count, month_count, description in test_cases:
        print("📊 {description}:")
        print("   Trades: {trade_count}, Months: {month_count}")

        # Generate test data
        trades = generate_synthetic_trades(trade_count)
        monthly_data = generate_synthetic_monthly_data(month_count)

        # Test detection
        trade_category = scalability_manager.detect_trade_volume_category(trades)
        monthly_category = scalability_manager.detect_monthly_timeline_category(monthly_data)
        scatter_category = scalability_manager.detect_scatter_density_category(trades)

        print("   → Trade volume: {trade_category}")
        print("   → Monthly timeline: {monthly_category}")
        print("   → Scatter density: {scatter_category}")

        # Test recommendations
        recommendations = scalability_manager.get_chart_recommendation(trades, monthly_data)
        print("   → Chart recommendations:")
        print("     - Trade performance: {recommendations['trade_performance']}")
        print("     - Monthly timeline: {recommendations['monthly_timeline']}")
        print("     - Scatter plot: {recommendations['scatter_plot']}")
        print()


def test_performance_bands():
    """Test performance bands functionality."""
    print("📈 Testing Performance Bands\n")

    config = {"scalability": {}}
    scalability_manager = create_scalability_manager(config)

    # Generate diverse trade data
    trades = generate_synthetic_trades(100)

    # Create performance bands
    bands = scalability_manager.create_performance_bands(trades)

    print("Performance Bands Distribution:")
    total_trades = sum(len(band_trades) for band_trades in bands.values())

    for band_name, band_trades in bands.items():
        percentage = (len(band_trades) / total_trades) * 100
        print("   {band_name}: {len(band_trades)} trades ({percentage:.1f}%)")

    print("\nTotal trades: {total_trades}")
    print()


def test_clustering():
    """Test clustering functionality for scatter plots."""
    print("🎯 Testing Clustering Functionality\n")

    config = {"scalability": {}}
    scalability_manager = create_scalability_manager(config)

    # Generate high-density trade data
    trades = generate_synthetic_trades(200)

    # Test clustering
    cluster_info = scalability_manager.cluster_scatter_points(trades)

    print("Clustering Results:")
    print("   Total clusters: {cluster_info['total_clusters']}")
    print("   Clustered points: {cluster_info['clustered_points']}")
    print("   Individual points: {cluster_info['noise_points']}")

    if cluster_info["clusters"]:
        print("\nCluster Details:")
        for cluster in cluster_info["clusters"][:5]:  # Show first 5 clusters
            centroid_dur, centroid_ret = cluster["centroid"]
            print("   Cluster {cluster['id']}: {cluster['size']} trades")
            print("      Centroid: {centroid_dur:.1f} days, {centroid_ret:+.1f}%")

    print()


def test_label_optimization():
    """Test label optimization for different timeline categories."""
    print("🏷️  Testing Label Optimization\n")

    config = {"scalability": {}}
    scalability_manager = create_scalability_manager(config)

    # Test different month counts
    for month_count, expected_category in [
        (3, "compact"),
        (6, "medium"),
        (12, "condensed"),
    ]:
        monthly_data = generate_synthetic_monthly_data(month_count)

        category = scalability_manager.detect_monthly_timeline_category(monthly_data)
        optimized_labels = scalability_manager.optimize_monthly_labels(monthly_data, category)

        print("Timeline: {month_count} months ({category})")
        print(
            f"   Labels: {optimized_labels[:3]}..." if len(optimized_labels) > 3 else f"   Labels: {optimized_labels}"
        )
        print()


if __name__ == "__main__":
    print("🚀 Dashboard Scalability Testing\n")
    print("=" * 50)

    try:
        test_scalability_detection()
        test_performance_bands()
        test_clustering()
        test_label_optimization()

        print("✅ All scalability tests completed successfully!")

    except Exception:
        print("❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
