#!/usr/bin/env python3
"""
Active Chart Requirements Detection

Dynamically determines data requirements by scanning only active (non-frozen) charts
at runtime, eliminating the need for static contract discovery.

This module replaces the contract discovery system with runtime active chart scanning.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from chart_data_dependency_manager import ChartDataDependencyManager, ChartStatus


# Global module-level cache to prevent repeated discovery operations
_GLOBAL_DISCOVERY_CACHE = None
_GLOBAL_DISCOVERY_LOGGED = False


@dataclass
class ActiveChartRequirement:
    """Represents a data requirement from an active chart"""

    chart_type: str
    data_source: str
    file_path: str
    category: str
    chart_file: str
    required_services: list[str]


@dataclass
class ActiveRequirementsResult:
    """Result of active chart requirements detection"""

    requirements: list[ActiveChartRequirement]
    total_active_charts: int
    total_frozen_charts: int
    categories_needed: set[str]
    services_needed: set[str]
    discovery_time_seconds: float


class ActiveChartRequirementsDetector:
    """Detects data requirements from active charts only at runtime"""

    def __init__(
        self,
        frontend_src_path: Path | None = None,
        frontend_data_path: Path | None = None,
    ):
        self.frontend_src_path = frontend_src_path or Path.cwd() / "frontend" / "src"
        self.frontend_data_path = frontend_data_path or Path.cwd() / "frontend" / "public" / "data"
        self.logger = logging.getLogger(__name__)

        # Initialize chart data dependency manager
        self.chart_status_manager = ChartDataDependencyManager(self.frontend_src_path)

        # Chart type to data source mapping
        self.chart_data_mapping = {
            # Portfolio charts
            "portfolio-value-comparison": {
                "data_source": "portfolio/multi_strategy_portfolio_portfolio_value.csv",
                "category": "portfolio",
                "services": ["yahoo_finance"],
            },
            "portfolio-drawdowns": {
                "data_source": "portfolio/multi_strategy_portfolio_drawdowns.csv",
                "category": "portfolio",
                "services": ["yahoo_finance"],
            },
            "returns-comparison": {
                "data_source": "portfolio/multi_strategy_portfolio_returns.csv",
                "category": "portfolio",
                "services": ["yahoo_finance"],
            },
            "live-signals-benchmark-comparison": {
                "data_source": "portfolio/live_signals_benchmark_comparison.csv",
                "category": "portfolio",
                "services": ["yahoo_finance"],
            },
            "closed-positions-pnl-timeseries": {
                "data_source": "portfolio/closed_positions_pnl_progression.csv",
                "category": "portfolio",
                "services": ["trade_history"],
            },
            "open-positions-pnl-timeseries": {
                "data_source": "portfolio/open_positions_pnl_current.csv",
                "category": "portfolio",
                "services": ["trade_history"],
            },
            # Trade history charts
            "trade-pnl-waterfall": {
                "data_source": "trade-history/trade_pnl_waterfall_sorted.csv",
                "category": "trade-history",
                "services": ["trade_history"],
            },
            "live-signals-equity-curve": {
                "data_source": "trade-history/live_signals.csv",
                "category": "trade-history",
                "services": ["trade_history"],
            },
            # Open positions charts
            "live-signals-open-positions-pnl": {
                "data_source": "open-positions/live_signals_open_positions_pnl.csv",
                "category": "open-positions",
                "services": ["trade_history"],
            },
            # Raw data charts
            "apple-price": {
                "data_source": "raw/stocks/AAPL/daily.csv",
                "category": "raw",
                "services": ["yahoo_finance"],
            },
            "mstr-price": {
                "data_source": "raw/stocks/MSTR/daily.csv",
                "category": "raw",
                "services": ["yahoo_finance"],
            },
        }

    def discover_active_requirements(self) -> ActiveRequirementsResult:
        """
        Discover data requirements from active charts only

        Returns:
            ActiveRequirementsResult with requirements for active charts only
        """
        # Use global cache to prevent repeated discovery across ALL instances
        global _GLOBAL_DISCOVERY_CACHE, _GLOBAL_DISCOVERY_LOGGED
        if _GLOBAL_DISCOVERY_CACHE is not None:
            return _GLOBAL_DISCOVERY_CACHE

        import time

        start_time = time.time()

        # Only log discovery start once globally across all instances
        if not _GLOBAL_DISCOVERY_LOGGED:
            self.logger.info("Discovering active chart data requirements")
            _GLOBAL_DISCOVERY_LOGGED = True
        # All subsequent discovery calls are silent to eliminate noise

        # Get all chart statuses
        chart_statuses = self.chart_status_manager.get_chart_statuses()

        # Separate active and frozen charts
        active_charts = [chart for chart in chart_statuses if chart.status != ChartStatus.FROZEN]
        frozen_charts = [chart for chart in chart_statuses if chart.status == ChartStatus.FROZEN]

        # Only log chart counts if this is the first discovery globally
        if _GLOBAL_DISCOVERY_LOGGED:  # Only log if we logged discovery start
            self.logger.info(f"Found {len(active_charts)} active charts, {len(frozen_charts)} frozen charts")

            # Log frozen charts being skipped (only once globally)
            if frozen_charts:
                frozen_types = [chart.chart_type for chart in frozen_charts]
                self.logger.info(f"Skipping data requirements for frozen charts: {sorted(set(frozen_types))}")
        # All subsequent calls are silent to eliminate noise

        # Build requirements from active charts only
        requirements = []
        categories_needed: set[str] = set()
        services_needed: set[str] = set()

        for chart in active_charts:
            chart_type = chart.chart_type

            if chart_type in self.chart_data_mapping:
                mapping = self.chart_data_mapping[chart_type]

                requirement = ActiveChartRequirement(
                    chart_type=chart_type,
                    data_source=str(mapping["data_source"]),
                    file_path=str(self.frontend_data_path / str(mapping["data_source"])),
                    category=str(mapping["category"]),
                    chart_file=str(chart.file_path),
                    required_services=list(mapping["services"]),
                )

                requirements.append(requirement)
                categories_needed.add(str(mapping["category"]))
                services_needed.update(list(mapping["services"]))

                self.logger.debug(f"Active chart '{chart_type}' requires: {mapping['data_source']}")
            else:
                self.logger.warning(f"No data mapping found for active chart type: {chart_type}")

        discovery_time = time.time() - start_time

        # Create result object
        result = ActiveRequirementsResult(
            requirements=requirements,
            total_active_charts=len(active_charts),
            total_frozen_charts=len(frozen_charts),
            categories_needed=categories_needed,
            services_needed=services_needed,
            discovery_time_seconds=discovery_time,
        )

        # Cache the results globally to prevent repeated discovery operations
        _GLOBAL_DISCOVERY_CACHE = result

        # Only log completion details if this is the first discovery globally
        if _GLOBAL_DISCOVERY_LOGGED:  # Only log if we logged discovery start
            self.logger.info(
                f"Active requirements discovery completed: {len(requirements)} data files needed "
                f"for {len(active_charts)} active charts across {len(categories_needed)} categories "
                f"[Time: {discovery_time:.2f}s]"
            )

            if categories_needed:
                self.logger.info(f"Categories needed: {sorted(categories_needed)}")
            if services_needed:
                self.logger.info(f"Services needed: {sorted(services_needed)}")
        # All subsequent discovery calls are silent to eliminate noise

        return result

    def get_requirements_by_category(self, category: str) -> list[ActiveChartRequirement]:
        """Get active chart requirements for a specific category"""
        all_requirements = self.discover_active_requirements()
        return [req for req in all_requirements.requirements if req.category == category]

    def get_required_services_for_category(self, category: str) -> set[str]:
        """Get services required for a specific category based on active charts"""
        category_requirements = self.get_requirements_by_category(category)
        services = set()
        for req in category_requirements:
            services.update(req.required_services)
        return services

    def should_process_category(self, category: str) -> bool:
        """Check if a category should be processed based on active chart requirements"""
        return len(self.get_requirements_by_category(category)) > 0


def create_active_chart_detector(
    frontend_src_path: str | None = None, frontend_data_path: str | None = None
) -> ActiveChartRequirementsDetector:
    """Factory function to create active chart requirements detector"""
    src_path = Path(frontend_src_path) if frontend_src_path else None
    data_path = Path(frontend_data_path) if frontend_data_path else None
    return ActiveChartRequirementsDetector(src_path, data_path)


if __name__ == "__main__":
    # Test the active chart requirements detector
    detector = create_active_chart_detector()
    result = detector.discover_active_requirements()

    print("Active Chart Requirements Discovery Results:")
    print("  Active charts: {result.total_active_charts}")
    print("  Frozen charts: {result.total_frozen_charts}")
    print("  Data files needed: {len(result.requirements)}")
    print("  Categories needed: {sorted(result.categories_needed)}")
    print("  Services needed: {sorted(result.services_needed)}")
    print("  Discovery time: {result.discovery_time_seconds:.2f}s")

    if result.requirements:
        print("\nRequired data files:")
        for req in result.requirements:
            print("  {req.chart_type} → {req.data_source}")
