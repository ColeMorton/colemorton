#!/usr/bin/env python3
"""
Abstract chart generator interface for unified chart generation.

This module provides the abstract base class for chart generators, enabling
seamless switching between different chart rendering engines (matplotlib, plotly).
"""

from abc import ABC, abstractmethod
from typing import Any

from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
)


class AbstractChartGenerator(ABC):
    """Abstract base class for chart generation engines."""

    def __init__(self, theme_manager, scalability_manager=None):
        """
        Initialize chart generator.

        Args:
            theme_manager: Theme manager instance
            scalability_manager: Optional scalability manager for volume optimization
        """
        self.theme_manager = theme_manager
        self.scalability_manager = scalability_manager

    @abstractmethod
    def create_enhanced_gauge(
        self,
        ax: Any,  # Can be plt.Axes or plotly figure
        value: float,
        title: str,
        max_value: float = 100,
        mode: str = "light",
    ) -> None:
        """
        Create sophisticated gauge chart for metrics.

        Args:
            ax: Axes/figure object (implementation specific)
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            mode: 'light' or 'dark' mode
        """

    @abstractmethod
    def create_enhanced_monthly_bars(
        self, ax: Any, monthly_data: list[MonthlyPerformance], mode: str = "light"
    ) -> None:
        """
        Create enhanced monthly performance bar chart.

        Args:
            ax: Axes/figure object (implementation specific)
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """

    @abstractmethod
    def create_enhanced_donut_chart(
        self, ax: Any, quality_data: list[QualityDistribution], mode: str = "light"
    ) -> None:
        """
        Create sophisticated donut chart for quality distribution.

        Args:
            ax: Axes/figure object (implementation specific)
            quality_data: Quality distribution data
            mode: 'light' or 'dark' mode
        """

    @abstractmethod
    def create_waterfall_chart(self, ax: Any, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create sophisticated waterfall chart.

        Args:
            ax: Axes/figure object (implementation specific)
            trades: Trade data
            mode: 'light' or 'dark' mode
        """

    @abstractmethod
    def create_enhanced_scatter(self, ax: Any, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create enhanced scatter plot.

        Args:
            ax: Axes/figure object (implementation specific)
            trades: Trade data
            mode: 'light' or 'dark' mode
        """

    @abstractmethod
    def create_performance_summary_panel(
        self,
        ax: Any,
        trades: list[TradeData],
        monthly_data: list[MonthlyPerformance],
        mode: str = "light",
    ) -> None:
        """
        Create summary performance panel with key insights.

        Args:
            ax: Axes/figure object (implementation specific)
            trades: Trade data
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """

    def get_chart_config(self, chart_type: str, mode: str = "light") -> dict[str, Any]:
        """
        Get configuration for a specific chart type.

        Args:
            chart_type: Type of chart
            mode: 'light' or 'dark' mode

        Returns:
            Dictionary containing chart configuration
        """
        theme = self.theme_manager.get_theme_colors(mode)
        colors = self.theme_manager.get_monthly_colors()

        return {
            "theme": theme,
            "colors": colors,
            "mode": mode,
            "chart_type": chart_type,
        }
