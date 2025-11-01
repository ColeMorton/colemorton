#!/usr/bin/env python3
"""
Matplotlib implementation of the abstract chart generator interface.

This module wraps the existing AdvancedChartGenerator to implement the
AbstractChartGenerator interface for backward compatibility.
"""

import matplotlib.pyplot as plt

from scripts.utils.abstract_chart_generator import AbstractChartGenerator
from scripts.utils.chart_generators import AdvancedChartGenerator
from scripts.utils.dashboard_parser import (
    MonthlyPerformance,
    QualityDistribution,
    TradeData,
)


class MatplotlibChartGenerator(AbstractChartGenerator):
    """Matplotlib implementation of the chart generator interface."""

    def __init__(self, theme_manager, scalability_manager=None):
        """
        Initialize matplotlib chart generator.

        Args:
            theme_manager: Theme manager instance
            scalability_manager: Optional scalability manager for volume optimization
        """
        super().__init__(theme_manager, scalability_manager)
        # Create the legacy chart generator instance
        self._legacy_generator = AdvancedChartGenerator(theme_manager, scalability_manager)

    def create_enhanced_gauge(
        self,
        ax: plt.Axes,
        value: float,
        title: str,
        max_value: float = 100,
        mode: str = "light",
    ) -> None:
        """
        Create sophisticated gauge chart for metrics using matplotlib.

        Args:
            ax: Matplotlib Axes object
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_enhanced_gauge(ax, value, title, max_value, mode)

    def create_enhanced_monthly_bars(
        self, ax: plt.Axes, monthly_data: list[MonthlyPerformance], mode: str = "light"
    ) -> None:
        """
        Create enhanced monthly performance bar chart using matplotlib.

        Args:
            ax: Matplotlib Axes object
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_enhanced_monthly_bars(ax, monthly_data, mode)

    def create_enhanced_donut_chart(
        self, ax: plt.Axes, quality_data: list[QualityDistribution], mode: str = "light"
    ) -> None:
        """
        Create sophisticated donut chart for quality distribution using matplotlib.

        Args:
            ax: Matplotlib Axes object
            quality_data: Quality distribution data
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_enhanced_donut_chart(ax, quality_data, mode)

    def create_waterfall_chart(self, ax: plt.Axes, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create sophisticated waterfall chart using matplotlib.

        Args:
            ax: Matplotlib Axes object
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_waterfall_chart(ax, trades, mode)

    def create_enhanced_scatter(self, ax: plt.Axes, trades: list[TradeData], mode: str = "light") -> None:
        """
        Create enhanced scatter plot using matplotlib.

        Args:
            ax: Matplotlib Axes object
            trades: Trade data
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_enhanced_scatter(ax, trades, mode)

    def create_performance_summary_panel(
        self,
        ax: plt.Axes,
        trades: list[TradeData],
        monthly_data: list[MonthlyPerformance],
        mode: str = "light",
    ) -> None:
        """
        Create summary performance panel with key insights using matplotlib.

        Args:
            ax: Matplotlib Axes object
            trades: Trade data
            monthly_data: Monthly performance data
            mode: 'light' or 'dark' mode
        """
        self._legacy_generator.create_performance_summary_panel(ax, trades, monthly_data, mode)
