#!/usr/bin/env python3
"""
Scalability manager for high-volume dataset optimization.

This module provides intelligent data volume detection and chart type selection
for datasets ranging from 15 trades to 200+ trades and 1-12 months of data.
"""

import math
import sys
from collections import defaultdict
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN


# Configure path before imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Local imports after path configuration
from scripts.utils.dashboard_parser import MonthlyPerformance, TradeData


@dataclass
class VolumeThresholds:
    """Configuration for volume-based chart selection."""

    small_trades: int = 50  # ≤50 trades: individual trade waterfall
    medium_trades: int = 100  # 51-100 trades: grouped performance bands
    large_trades: int = 200  # 101-200 trades: statistical distribution

    compact_months: int = 3  # 1-3 months: full names, wider bars
    medium_months: int = 8  # 4-8 months: abbreviations, medium bars
    condensed_months: int = 12  # 9-12 months: compact view, thin bars

    low_density: int = 50  # Scatter plot density thresholds
    medium_density: int = 150
    high_density: int = 200


@dataclass
class ScalabilityConfig:
    """Configuration for scalability features."""

    enable_clustering: bool = True
    enable_compression: bool = True
    enable_adaptive_labels: bool = True
    max_labels: int = 20
    min_cluster_size: int = 3
    cluster_eps: float = 0.3


class ScalabilityManager:
    """Manages chart scalability and optimization for high-volume datasets."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize scalability manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.scalability_config = config.get("scalability", {})
        self.thresholds = self._create_thresholds()
        self.scalability_settings = self._create_scalability_config()

    def _create_thresholds(self) -> VolumeThresholds:
        """Create volume thresholds from configuration."""
        thresholds_config = self.scalability_config

        return VolumeThresholds(
            small_trades=thresholds_config.get("trade_volume_thresholds", {}).get("small", 50),
            medium_trades=thresholds_config.get("trade_volume_thresholds", {}).get("medium", 100),
            large_trades=thresholds_config.get("trade_volume_thresholds", {}).get("large", 200),
            compact_months=thresholds_config.get("monthly_timeline_thresholds", {}).get("compact", 3),
            medium_months=thresholds_config.get("monthly_timeline_thresholds", {}).get("medium", 8),
            condensed_months=thresholds_config.get("monthly_timeline_thresholds", {}).get("condensed", 12),
            low_density=thresholds_config.get("density_management", {}).get("scatter_plot", {}).get("low_density", 50),
            medium_density=thresholds_config.get("density_management", {})
            .get("scatter_plot", {})
            .get("medium_density", 150),
            high_density=thresholds_config.get("density_management", {})
            .get("scatter_plot", {})
            .get("high_density", 200),
        )

    def _create_scalability_config(self) -> ScalabilityConfig:
        """Create scalability configuration."""
        return ScalabilityConfig(
            enable_clustering=True,
            enable_compression=True,
            enable_adaptive_labels=True,
            max_labels=20,
            min_cluster_size=3,
            cluster_eps=0.3,
        )

    def detect_trade_volume_category(self, trades: list[TradeData]) -> str:
        """
        Detect trade volume category for chart selection.

        Args:
            trades: List of trade data

        Returns:
            Volume category: 'small', 'medium', or 'large'
        """
        trade_count = len(trades)

        if trade_count <= self.thresholds.small_trades:
            return "small"
        if trade_count <= self.thresholds.medium_trades:
            return "medium"
        return "large"

    def detect_monthly_timeline_category(self, monthly_data: list[MonthlyPerformance]) -> str:
        """
        Detect monthly timeline category for display optimization.

        Args:
            monthly_data: List of monthly performance data

        Returns:
            Timeline category: 'compact', 'medium', or 'condensed'
        """
        month_count = len(monthly_data)

        if month_count <= self.thresholds.compact_months:
            return "compact"
        if month_count <= self.thresholds.medium_months:
            return "medium"
        return "condensed"

    def detect_scatter_density_category(self, trades: list[TradeData]) -> str:
        """
        Detect scatter plot density category.

        Args:
            trades: List of trade data

        Returns:
            Density category: 'low', 'medium', or 'high'
        """
        trade_count = len(trades)

        if trade_count <= self.thresholds.low_density:
            return "low"
        if trade_count <= self.thresholds.medium_density:
            return "medium"
        return "high"

    def create_performance_histogram(
        self, trades: list[TradeData], bins: int = 20
    ) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """
        Create performance histogram for high-volume datasets.

        Args:
            trades: List of trade data
            bins: Number of histogram bins

        Returns:
            Tuple of (counts, bin_edges, labels)
        """
        returns = [trade.return_pct for trade in trades]

        # Create histogram
        counts, bin_edges = np.histogram(returns, bins=bins)

        # Create labels for bins
        labels = []
        for i in range(len(bin_edges) - 1):
            start = bin_edges[i]
            end = bin_edges[i + 1]
            labels.append(f"{start:.1f}% to {end:.1f}%")

        return counts, bin_edges, labels

    def create_performance_bands(self, trades: list[TradeData]) -> dict[str, list[TradeData]]:
        """
        Group trades into performance bands for medium-volume datasets.

        Args:
            trades: List of trade data

        Returns:
            Dictionary of performance bands
        """
        bands: dict[str, list[TradeData]] = {
            "Large Winners (>10%)": [],
            "Winners (2-10%)": [],
            "Small Winners (0-2%)": [],
            "Small Losers (0 to -2%)": [],
            "Losers (-2 to -10%)": [],
            "Large Losers (<-10%)": [],
        }

        for trade in trades:
            ret = trade.return_pct
            if ret > 10:
                bands["Large Winners (>10%)"].append(trade)
            elif ret > 2:
                bands["Winners (2-10%)"].append(trade)
            elif ret > 0:
                bands["Small Winners (0-2%)"].append(trade)
            elif ret > -2:
                bands["Small Losers (0 to -2%)"].append(trade)
            elif ret > -10:
                bands["Losers (-2 to -10%)"].append(trade)
            else:
                bands["Large Losers (<-10%)"].append(trade)

        # Remove empty bands
        return {k: v for k, v in bands.items() if v}

    def cluster_scatter_points(self, trades: list[TradeData]) -> dict[str, Any]:
        """
        Cluster scatter plot points for high-density management.

        Args:
            trades: List of trade data

        Returns:
            Clustering information with centroids and point counts
        """
        if len(trades) < self.scalability_settings.min_cluster_size:
            return {"clusters": [], "noise": trades}

        # Prepare data for clustering
        durations = [trade.duration_days for trade in trades]
        returns = [trade.return_pct for trade in trades]

        # Normalize data for clustering
        durations_array = np.array(durations)
        returns_array = np.array(returns)
        X = np.column_stack(
            [
                (durations_array - np.mean(durations_array)) / (np.std(durations_array) + 1e-8),
                (returns_array - np.mean(returns_array)) / (np.std(returns_array) + 1e-8),
            ]
        )

        # Perform DBSCAN clustering
        clustering = DBSCAN(
            eps=self.scalability_settings.cluster_eps,
            min_samples=self.scalability_settings.min_cluster_size,
        ).fit(X)

        # Process clusters
        clusters = defaultdict(list)
        noise = []

        for i, label in enumerate(clustering.labels_):
            if label == -1:
                noise.append(trades[i])
            else:
                clusters[label].append(trades[i])

        # Calculate cluster centroids and metadata
        cluster_info = []
        for cluster_id, cluster_trades in clusters.items():
            if len(cluster_trades) >= self.scalability_settings.min_cluster_size:
                centroid_duration = np.mean([t.duration_days for t in cluster_trades])
                centroid_return = np.mean([t.return_pct for t in cluster_trades])

                cluster_info.append(
                    {
                        "id": cluster_id,
                        "trades": cluster_trades,
                        "centroid": (centroid_duration, centroid_return),
                        "size": len(cluster_trades),
                        "avg_return": centroid_return,
                        "avg_duration": centroid_duration,
                    }
                )

        return {
            "clusters": cluster_info,
            "noise": noise,
            "total_clusters": len(cluster_info),
            "clustered_points": sum(len(c["trades"]) for c in cluster_info),
            "noise_points": len(noise),
        }

    def optimize_monthly_labels(self, monthly_data: list[MonthlyPerformance], category: str) -> list[str]:
        """
        Optimize monthly labels based on timeline category.

        Args:
            monthly_data: List of monthly performance data
            category: Timeline category ('compact', 'medium', 'condensed')

        Returns:
            Optimized labels
        """
        if category == "compact":
            # Full month names for 1-3 months
            return [f"{data.month} {data.year}" for data in monthly_data]
        if category == "medium":
            # Month abbreviations for 4-8 months
            return [f"{data.month[:3]} '{str(data.year)[2:]}" for data in monthly_data]
        # Condensed view for 9-12 months
        return [f"{data.month[0]}{str(data.year)[2:]}" for data in monthly_data]

    def calculate_adaptive_label_frequency(self, data_length: int, max_labels: int = None) -> int:
        """
        Calculate adaptive label frequency to avoid overcrowding.

        Args:
            data_length: Length of the dataset
            max_labels: Maximum number of labels to display

        Returns:
            Label frequency (show every nth label)
        """
        if max_labels is None:
            max_labels = self.scalability_settings.max_labels

        if data_length <= max_labels:
            return 1
        return math.ceil(data_length / max_labels)

    def optimize_chart_performance(self, chart_type: str, data_size: int) -> dict[str, Any]:
        """
        Optimize chart performance settings based on data size.

        Args:
            chart_type: Type of chart
            data_size: Size of dataset

        Returns:
            Performance optimization settings
        """
        settings = {
            "line_width": 1.0,
            "marker_size": 6,
            "alpha": 0.8,
            "rasterization": False,
            "simplify_threshold": None,
        }

        if data_size > 100:
            settings.update(
                {
                    "line_width": 0.8,
                    "marker_size": 4,
                    "alpha": 0.6,
                    "rasterization": True if data_size > 500 else False,
                }
            )

        if data_size > 500:
            settings.update(
                {
                    "line_width": 0.5,
                    "marker_size": 2,
                    "alpha": 0.4,
                    "simplify_threshold": 0.1,
                }
            )

        return settings

    def create_summary_statistics(self, trades: list[TradeData]) -> dict[str, Any]:
        """
        Create summary statistics for large datasets.

        Args:
            trades: List of trade data

        Returns:
            Summary statistics
        """
        returns = [trade.return_pct for trade in trades]
        durations = [trade.duration_days for trade in trades]

        return {
            "total_trades": len(trades),
            "returns": {
                "mean": np.mean(returns),
                "median": np.median(returns),
                "std": np.std(returns),
                "min": np.min(returns),
                "max": np.max(returns),
                "percentiles": {
                    "25th": np.percentile(returns, 25),
                    "75th": np.percentile(returns, 75),
                    "90th": np.percentile(returns, 90),
                    "95th": np.percentile(returns, 95),
                },
            },
            "durations": {
                "mean": np.mean(durations),
                "median": np.median(durations),
                "std": np.std(durations),
                "min": np.min(durations),
                "max": np.max(durations),
            },
            "quality_distribution": self._calculate_quality_distribution(trades),
            "win_rate": len([t for t in trades if t.return_pct > 0]) / len(trades) * 100,
        }

    def _calculate_quality_distribution(self, trades: list[TradeData]) -> dict[str, int]:
        """Calculate quality distribution for trades."""
        quality_counts: dict[str, int] = defaultdict(int)
        for trade in trades:
            quality_counts[trade.quality] += 1
        return dict(quality_counts)

    def get_chart_recommendation(
        self, trades: list[TradeData], monthly_data: list[MonthlyPerformance]
    ) -> dict[str, str | Collection[str]]:
        """
        Get chart type recommendations based on data volume.

        Args:
            trades: List of trade data
            monthly_data: List of monthly performance data

        Returns:
            Chart recommendations
        """
        trade_category = self.detect_trade_volume_category(trades)
        monthly_category = self.detect_monthly_timeline_category(monthly_data)
        scatter_category = self.detect_scatter_density_category(trades)

        recommendations = {
            "trade_performance": {
                "small": "waterfall",
                "medium": "performance_bands",
                "large": "histogram",
            }[trade_category],
            "monthly_timeline": {
                "compact": "full_bars",
                "medium": "medium_bars",
                "condensed": "thin_bars",
            }[monthly_category],
            "scatter_plot": {
                "low": "standard_scatter",
                "medium": "reduced_opacity",
                "high": "clustered_scatter",
            }[scatter_category],
            "categories": {
                "trade_volume": trade_category,
                "monthly_timeline": monthly_category,
                "scatter_density": scatter_category,
            },
        }

        return recommendations


def create_scalability_manager(config: dict[str, Any]) -> ScalabilityManager:
    """
    Factory function to create a ScalabilityManager instance.

    Args:
        config: Configuration dictionary

    Returns:
        Configured ScalabilityManager instance
    """
    return ScalabilityManager(config)


if __name__ == "__main__":
    # Test scalability manager
    from scripts.utils.dashboard_parser import parse_dashboard_data

    # Load test data
    test_file = "data/outputs/trade_history/HISTORICAL_PERFORMANCE_REPORT_20250626.md"

    try:
        data = parse_dashboard_data(test_file)

        # Test configuration
        test_config = {
            "scalability": {
                "trade_volume_thresholds": {"small": 50, "medium": 100, "large": 200},
                "monthly_timeline_thresholds": {
                    "compact": 3,
                    "medium": 8,
                    "condensed": 12,
                },
                "density_management": {
                    "scatter_plot": {
                        "low_density": 50,
                        "medium_density": 150,
                        "high_density": 200,
                    }
                },
            }
        }

        scalability_manager = create_scalability_manager(test_config)

        # Test volume detection
        trades = data["trades"]
        monthly_data = data["monthly_performance"]

        print("Trades: {len(trades)}")
        print(f"Trade volume category: {scalability_manager.detect_trade_volume_category(trades)}")
        print(f"Monthly timeline category: {scalability_manager.detect_monthly_timeline_category(monthly_data)}")
        print(f"Scatter density category: {scalability_manager.detect_scatter_density_category(trades)}")

        # Test recommendations
        recommendations = scalability_manager.get_chart_recommendation(trades, monthly_data)
        print("Chart recommendations: {recommendations}")

        print("Scalability manager test completed successfully!")

    except Exception:
        print("Test failed: {e}")
        import traceback

        traceback.print_exc()
