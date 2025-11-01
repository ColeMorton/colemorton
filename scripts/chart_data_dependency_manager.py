#!/usr/bin/env python3
"""
Chart Data Dependency Manager

Manages chart lifecycle status by reading from chart-data-dependencies.json
to maintain consistency between Python pipeline and TypeScript frontend.

This replaces the MDX scanning approach with a single source of truth.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


# Global module-level caches to prevent repeated operations across instances
_GLOBAL_CONFIG_CACHE = None
_GLOBAL_CHART_STATUS_MAPPING_CACHE = None
_GLOBAL_CONFIG_LOGGED = False


class ChartStatus(Enum):
    """Chart lifecycle status options"""

    ACTIVE = "active"
    FROZEN = "frozen"
    STATIC = "static"


@dataclass
class ChartStatusInfo:
    """Chart status information extracted from JSON configuration"""

    chart_type: str
    status: ChartStatus
    frozen_date: str | None = None
    frozen_by: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    config_source: str = "chart-data-dependencies.json"


class ChartDataDependencyManager:
    """
    Manages chart status by reading from chart-data-dependencies.json
    """

    def __init__(self, frontend_src_path: Path | None = None):
        """Initialize chart data dependency manager"""
        self.logger = logging.getLogger("chart_data_dependency_manager")

        if frontend_src_path is None:
            # Calculate project root from this script's location
            project_root = Path(__file__).parent.parent
            self.frontend_src_path = project_root / "frontend/src"
        else:
            # Ensure we have an absolute path for reliable access
            self.frontend_src_path = Path(frontend_src_path).resolve()

        # Path to chart data dependencies configuration
        self.config_path = self.frontend_src_path / "config" / "chart-data-dependencies.json"

        # Validate that the config file exists
        if not self.config_path.exists():
            self.logger.error(f"Chart data dependencies config not found: {self.config_path}")
            raise FileNotFoundError(f"Chart data dependencies config not found: {self.config_path}")

        self.logger.debug(f"Chart data dependency manager initialized with config: {self.config_path}")

        # Data source mappings for chart types
        self.chart_data_source_mapping = {
            "trade-pnl-waterfall": "trade-history/trade_pnl_waterfall_sorted.csv",
            "closed-positions-pnl-timeseries": "portfolio/closed_positions_pnl_progression.csv",
            "open-positions-pnl-timeseries": "portfolio/open_positions_pnl_current.csv",
            "live-signals-open-positions-pnl": "open-positions/live_signals_open_positions_pnl.csv",
            "live-signals-equity-curve": "trade-history/live_signals.csv",
            "live-signals-benchmark-comparison": "portfolio/live_signals_benchmark_comparison.csv",
            "portfolio-value-comparison": "portfolio/multi_strategy_portfolio_portfolio_value.csv",
            "portfolio-drawdowns": "portfolio/multi_strategy_portfolio_drawdowns.csv",
            "returns-comparison": "portfolio/multi_strategy_portfolio_returns.csv",
            "apple-price": "raw/stocks/AAPL/daily.csv",
            "mstr-price": "raw/stocks/MSTR/daily.csv",
            "live-signals-drawdowns": "trade-history/live_signals.csv",
            "live-signals-weekly-candlestick": "trade-history/live_signals.csv",
        }

    def load_chart_dependencies_config(self) -> dict[str, Any]:
        """
        Load chart data dependencies configuration from JSON file

        Returns:
            Dictionary containing the full configuration
        """
        # Use global cache to prevent repeated file loading across ALL instances
        global _GLOBAL_CONFIG_CACHE, _GLOBAL_CONFIG_LOGGED
        if _GLOBAL_CONFIG_CACHE is not None:
            return _GLOBAL_CONFIG_CACHE

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Cache the results globally
            _GLOBAL_CONFIG_CACHE = config

            # Only log loading once globally
            if not _GLOBAL_CONFIG_LOGGED:
                self.logger.info(f"Loaded chart data dependencies configuration from {self.config_path}")
                _GLOBAL_CONFIG_LOGGED = True

            return config

        except Exception as e:
            self.logger.error(f"Failed to load chart dependencies config: {e}")
            raise

    def get_chart_statuses(self) -> list[ChartStatusInfo]:
        """
        Extract chart status information from JSON configuration

        Returns:
            List of chart status information found in configuration
        """
        config = self.load_chart_dependencies_config()
        chart_statuses = []

        dependencies = config.get("dependencies", {})

        for chart_type, chart_config in dependencies.items():
            chart_status = chart_config.get("chartStatus", "active")

            # Convert string status to enum
            try:
                status_enum = ChartStatus(chart_status)
            except ValueError:
                self.logger.warning(f"Unknown chart status '{chart_status}' for {chart_type}, defaulting to active")
                status_enum = ChartStatus.ACTIVE

            # Extract frozen metadata if available
            frozen_date = None
            frozen_by = None
            if status_enum == ChartStatus.FROZEN:
                primary_source = chart_config.get("primarySource", {})
                metadata = primary_source.get("metadata", {})
                frozen_by = metadata.get("lastUpdatedBy")
                # For now, use a default frozen date - could be enhanced later
                frozen_date = "2025-08-21"  # Date of status migration

            chart_info = ChartStatusInfo(
                chart_type=chart_type,
                status=status_enum,
                frozen_date=frozen_date,
                frozen_by=frozen_by,
                file_path="chart-data-dependencies.json",
                line_number=None,
                config_source="chart-data-dependencies.json",
            )

            chart_statuses.append(chart_info)

        self.logger.debug(f"Extracted {len(chart_statuses)} chart configurations from JSON")
        return chart_statuses

    def get_data_source_status_mapping(self) -> dict[str, ChartStatus]:
        """
        Build mapping of data source files to their aggregated chart status

        Returns:
            Dictionary mapping data source paths to chart status
        """
        # Use global cache to prevent repeated mapping operations
        global _GLOBAL_CHART_STATUS_MAPPING_CACHE
        if _GLOBAL_CHART_STATUS_MAPPING_CACHE is not None:
            return _GLOBAL_CHART_STATUS_MAPPING_CACHE

        chart_statuses = self.get_chart_statuses()
        data_source_status: dict[str, ChartStatus] = {}

        for chart_info in chart_statuses:
            # Get data source for this chart type
            data_source = self.chart_data_source_mapping.get(chart_info.chart_type)
            if not data_source:
                self.logger.debug(f"No data source mapping for chart type: {chart_info.chart_type}")
                continue

            # Track the most restrictive status for each data source
            current_status = data_source_status.get(data_source, ChartStatus.ACTIVE)

            # Priority: static > frozen > active
            if chart_info.status == ChartStatus.STATIC:
                data_source_status[data_source] = ChartStatus.STATIC
            elif chart_info.status == ChartStatus.FROZEN and current_status != ChartStatus.STATIC:
                data_source_status[data_source] = ChartStatus.FROZEN

        # Cache the results globally
        _GLOBAL_CHART_STATUS_MAPPING_CACHE = data_source_status

        self.logger.debug(f"Generated status mapping for {len(data_source_status)} data sources")

        return data_source_status

    def get_frozen_data_sources(self) -> set[str]:
        """Get set of data source paths that should be skipped in pipeline"""
        status_mapping = self.get_data_source_status_mapping()
        return {
            data_source
            for data_source, status in status_mapping.items()
            if status in [ChartStatus.FROZEN, ChartStatus.STATIC]
        }

    def should_skip_data_source(self, data_source_path: str) -> bool:
        """
        Check if a data source should be skipped based on chart status

        Args:
            data_source_path: Path to the data source file (e.g., "portfolio/closed_positions_pnl_progression.csv")

        Returns:
            True if data source should be skipped (frozen/static), False otherwise
        """
        frozen_sources = self.get_frozen_data_sources()
        return data_source_path in frozen_sources

    def should_skip_output_file(self, output_file_path: str) -> bool:
        """
        Check if an output file should be skipped based on chart status

        Args:
            output_file_path: Full path to the output file that would be generated

        Returns:
            True if output file should be skipped (frozen/static), False otherwise
        """
        # Convert absolute path to relative data source path
        from pathlib import Path

        output_path = Path(output_file_path)

        # Extract the relative path from frontend/public/data/
        # Example: /path/to/frontend/public/data/portfolio/file.csv -> portfolio/file.csv
        parts = output_path.parts
        try:
            data_index = parts.index("data")
            relative_path = "/".join(parts[data_index + 1 :])
            return self.should_skip_data_source(relative_path)
        except (ValueError, IndexError):
            # If we can't parse the path, check against frozen sources directly
            frozen_sources = self.get_frozen_data_sources()
            filename = output_path.name
            # Check if any frozen source ends with this filename
            for frozen_source in frozen_sources:
                if frozen_source.endswith(filename):
                    self.logger.info(f"Blocking update to potentially frozen file: {filename}")
                    return True
            return False

    def get_status_summary(self) -> dict[str, Any]:
        """Get summary of chart status information"""
        chart_statuses = self.get_chart_statuses()
        status_counts = {}

        for chart_info in chart_statuses:
            status_key = chart_info.status.value
            if status_key not in status_counts:
                status_counts[status_key] = 0
            status_counts[status_key] += 1

        data_source_mapping = self.get_data_source_status_mapping()

        return {
            "total_charts": len(chart_statuses),
            "status_breakdown": status_counts,
            "data_sources_affected": len(data_source_mapping),
            "frozen_data_sources": list(self.get_frozen_data_sources()),
            "chart_details": [
                {
                    "chart_type": info.chart_type,
                    "status": info.status.value,
                    "frozen_date": info.frozen_date,
                    "config_source": info.config_source,
                }
                for info in chart_statuses
                if info.status != ChartStatus.ACTIVE
            ],
        }

    # Legacy compatibility methods for seamless replacement of ChartStatusManager
    def scan_mdx_files(self) -> list[ChartStatusInfo]:
        """
        Legacy compatibility method - redirects to JSON-based status extraction

        Returns:
            List of chart status information from JSON configuration
        """
        self.logger.debug("Legacy scan_mdx_files() called - redirecting to JSON configuration")
        return self.get_chart_statuses()


def create_chart_data_dependency_manager(
    frontend_src_path: str | None = None,
) -> ChartDataDependencyManager:
    """Factory function to create chart data dependency manager"""
    return ChartDataDependencyManager(Path(frontend_src_path) if frontend_src_path else None)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    manager = create_chart_data_dependency_manager()
    summary = manager.get_status_summary()

    print("Chart Data Dependency Summary:")
    print(json.dumps(summary, indent=2))
