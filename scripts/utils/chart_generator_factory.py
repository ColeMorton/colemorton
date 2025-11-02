#!/usr/bin/env python3
"""
Factory for creating chart generators based on configuration.

This module provides a factory pattern implementation for creating chart
generators with the appropriate rendering engine.
"""

from typing import Any

from scripts.utils.abstract_chart_generator import AbstractChartGenerator
from scripts.utils.matplotlib_chart_generator import MatplotlibChartGenerator
from scripts.utils.plotly_chart_generator import PlotlyChartGenerator


class ChartGeneratorFactory:
    """Factory class for creating chart generators."""

    ENGINES = {
        "matplotlib": MatplotlibChartGenerator,
        "plotly": PlotlyChartGenerator,
    }

    @classmethod
    def create_chart_generator(
        cls,
        engine: str,
        theme_manager,
        scalability_manager=None,
    ) -> AbstractChartGenerator:
        """
        Create a chart generator instance based on the specified engine.

        Args:
            engine: Chart engine to use ('matplotlib' or 'plotly')
            theme_manager: Theme manager instance
            scalability_manager: Optional scalability manager

        Returns:
            Chart generator instance

        Raises:
            ValueError: If engine is not supported
        """
        if engine not in cls.ENGINES:
            raise ValueError(f"Unsupported chart engine: {engine}. Supported engines: {list(cls.ENGINES.keys())}")

        generator_class = cls.ENGINES[engine]
        return generator_class(theme_manager, scalability_manager)

    @classmethod
    def get_default_engine(cls, config: dict[str, Any] | None = None) -> str:
        """
        Get the default chart engine from configuration.

        Args:
            config: Optional configuration dictionary

        Returns:
            Default chart engine name
        """
        if config and "chart_engine" in config:
            return config["chart_engine"]
        return "matplotlib"  # Default to matplotlib for backward compatibility
