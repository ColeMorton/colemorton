#!/usr/bin/env python3
"""
Chart Status Manager

Manages chart lifecycle status by scanning MDX files for chart configurations
and building a mapping of data sources to chart status for pipeline filtering.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


# Global module-level caches to prevent repeated operations across instances
_GLOBAL_MDX_SCAN_CACHE = None
_GLOBAL_CHART_STATUS_MAPPING_CACHE = None
_GLOBAL_SCAN_LOGGED = False


class ChartStatus(Enum):
    """Chart lifecycle status options"""

    ACTIVE = "active"
    FROZEN = "frozen"
    STATIC = "static"


@dataclass
class ChartStatusInfo:
    """Chart status information extracted from MDX files"""

    chart_type: str
    status: ChartStatus
    frozen_date: str | None = None
    frozen_by: str | None = None
    file_path: str | None = None
    line_number: int | None = None


class ChartStatusManager:
    """
    Manages chart status by scanning MDX files and mapping to data sources
    """

    def __init__(self, frontend_src_path: Path | None = None):
        """Initialize chart status manager"""
        self.logger = logging.getLogger("chart_status_manager")

        if frontend_src_path is None:
            # Calculate project root from this script's location
            project_root = Path(__file__).parent.parent
            self.frontend_src_path = project_root / "frontend/src"
        else:
            # Ensure we have an absolute path for reliable access
            self.frontend_src_path = Path(frontend_src_path).resolve()

        # Validate that the frontend src path exists
        if not self.frontend_src_path.exists():
            self.logger.error(f"Frontend src path does not exist: {self.frontend_src_path}")
            raise FileNotFoundError(f"Frontend src directory not found: {self.frontend_src_path}")

        # Demote initialization log to DEBUG to reduce noise (this gets called 11+ times)
        self.logger.debug(f"Chart status manager initialized with frontend path: {self.frontend_src_path}")

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
            # Add more mappings as needed
        }

    def scan_mdx_files(self) -> list[ChartStatusInfo]:
        """
        Scan all MDX files for ChartDisplay components and extract status information

        Returns:
            List of chart status information found in MDX files
        """
        # Use global cache to prevent repeated scanning across ALL instances
        global _GLOBAL_MDX_SCAN_CACHE, _GLOBAL_SCAN_LOGGED
        if _GLOBAL_MDX_SCAN_CACHE is not None:
            return _GLOBAL_MDX_SCAN_CACHE

        chart_statuses = []

        # Find all MDX files
        mdx_files = list(self.frontend_src_path.glob("**/*.mdx"))

        # Only log scan start once globally across all instances
        if not _GLOBAL_SCAN_LOGGED:
            self.logger.info(f"Found {len(mdx_files)} MDX files to scan for chart status")
            _GLOBAL_SCAN_LOGGED = True
        else:
            # All subsequent scans are silent (not even DEBUG) to eliminate noise
            pass

        if len(mdx_files) == 0:
            self.logger.warning(f"No MDX files found in {self.frontend_src_path}")
            # List directory contents for debugging
            if self.frontend_src_path.exists():
                contents = list(self.frontend_src_path.iterdir())
                self.logger.debug(f"Directory contents: {[p.name for p in contents]}")
            return []

        for mdx_file in mdx_files:
            self.logger.debug(f"Scanning MDX file: {mdx_file}")
            try:
                file_charts = self._extract_chart_status_from_file(mdx_file)
                chart_statuses.extend(file_charts)
                if file_charts:
                    self.logger.debug(f"Found {len(file_charts)} charts in {mdx_file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to scan {mdx_file}: {e}")

        # Cache the results globally to prevent any repeated scanning
        _GLOBAL_MDX_SCAN_CACHE = chart_statuses

        # Only log completion if we logged the start (first time only)
        if _GLOBAL_SCAN_LOGGED and len(chart_statuses) > 0:
            self.logger.info(
                f"Completed scan: found {len(chart_statuses)} chart configurations across {len(mdx_files)} files"
            )

        return chart_statuses

    def _extract_chart_status_from_file(self, mdx_file: Path) -> list[ChartStatusInfo]:
        """Extract chart status information from a single MDX file"""
        chart_statuses = []

        try:
            content = mdx_file.read_text(encoding="utf-8")

            # Pattern to match ChartDisplay components
            chart_pattern = r"<ChartDisplay\s+([^>]+)/>"

            for match in re.finditer(chart_pattern, content, re.MULTILINE | re.DOTALL):
                props_str = match.group(1)
                line_number = content[: match.start()].count("\n") + 1

                # Extract properties
                chart_info = self._parse_chart_props(props_str, mdx_file, line_number)
                if chart_info:
                    chart_statuses.append(chart_info)

        except Exception as e:
            self.logger.error(f"Error reading {mdx_file}: {e}")

        return chart_statuses

    def _parse_chart_props(self, props_str: str, file_path: Path, line_number: int) -> ChartStatusInfo | None:
        """Parse ChartDisplay component properties"""
        try:
            # Extract key properties using regex
            chart_type = self._extract_prop_value(props_str, "chartType")
            status = self._extract_prop_value(props_str, "status") or "active"
            frozen_date = self._extract_prop_value(props_str, "frozenDate")
            frozen_by = self._extract_prop_value(props_str, "frozenBy")

            if not chart_type:
                return None

            return ChartStatusInfo(
                chart_type=chart_type,
                status=ChartStatus(status),
                frozen_date=frozen_date,
                frozen_by=frozen_by,
                file_path=str(file_path),
                line_number=line_number,
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse chart props at {file_path}:{line_number}: {e}")
            return None

    def _extract_prop_value(self, props_str: str, prop_name: str) -> str | None:
        """Extract a property value from component props string"""
        # Pattern to match prop="value" or prop='value'
        pattern = rf'{prop_name}=["\'](.*?)["\']'
        match = re.search(pattern, props_str)
        return match.group(1) if match else None

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

        chart_statuses = self.scan_mdx_files()
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

        # Log generation only once globally (demote to DEBUG level to reduce noise)
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
        chart_statuses = self.scan_mdx_files()
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
                    "file": info.file_path,
                    "line": info.line_number,
                }
                for info in chart_statuses
                if info.status != ChartStatus.ACTIVE
            ],
        }


def create_chart_status_manager(
    frontend_src_path: str | None = None,
) -> ChartStatusManager:
    """Factory function to create chart status manager"""
    return ChartStatusManager(Path(frontend_src_path) if frontend_src_path else None)


if __name__ == "__main__":
    # Example usage
    import json

    logging.basicConfig(level=logging.INFO)

    manager = create_chart_status_manager()
    summary = manager.get_status_summary()

    print("Chart Status Summary:")
    print(json.dumps(summary, indent=2))
