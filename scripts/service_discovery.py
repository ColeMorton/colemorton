#!/usr/bin/env python3
"""
Service Discovery for Trade History Analysis

Provides intelligent service discovery and execution for trade history analysis with:
- CLI service detection and fallback mechanisms
- Local-first data strategy integration
- Memory-efficient command execution
- Resource-aware processing
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli_wrapper import execute_cli_command, get_service_manager


class ServiceDiscoveryError(Exception):
    """Base exception for service discovery errors"""


class NoServiceAvailableError(ServiceDiscoveryError):
    """Raised when no service is available for the requested operation"""


class ServiceDiscoveryManager:
    """
    Manages service discovery and execution for trade history analysis
    """

    def __init__(self, local_data_dir: Path | None = None):
        self.local_data_dir = local_data_dir or Path(__file__).parent.parent / "data"
        self.logger = self._setup_logger()
        self.cli_manager = get_service_manager()

        # Local data sources
        self.fundamental_analysis_dir = self.local_data_dir / "outputs" / "fundamental_analysis"
        self.sector_analysis_dir = self.local_data_dir / "outputs" / "sector_analysis"
        self.cache_dirs = [
            self.local_data_dir / "cache",
            Path(__file__).parent / "data" / "cache",
        ]

        # Service priority for different data types
        self.service_priorities = {
            "stock_analysis": ["yahoo_finance", "alpha_vantage", "fmp"],
            "economic_data": ["fred_economic", "imf"],
            "crypto_data": ["coingecko"],
            "sec_filings": ["sec_edgar"],
            "fundamental_data": ["fmp", "yahoo_finance", "alpha_vantage"],
        }

        self.logger.info(
            f"Service discovery initialized with {len(self.cli_manager.get_available_services())} available services"
        )

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for service discovery"""
        logger = logging.getLogger("service_discovery")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def check_local_data_availability(self, ticker: str) -> dict[str, Any]:
        """
        Check availability of local data for a given ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary containing local data availability information
        """
        availability = {
            "ticker": ticker.upper(),
            "fundamental_analysis": {
                "available": False,
                "latest_file": None,
                "file_count": 0,
                "latest_date": None,
            },
            "sector_analysis": {"available": False, "files": []},
            "cache_data": {"available": False, "cache_files": []},
            "local_coverage": 0.0,
        }

        # Check fundamental analysis files
        if self.fundamental_analysis_dir.exists():
            pattern = f"{ticker}_*.md"
            fundamental_files = list(self.fundamental_analysis_dir.glob(pattern))

            if fundamental_files:
                availability["fundamental_analysis"]["available"] = True
                availability["fundamental_analysis"]["file_count"] = len(fundamental_files)

                # Find latest file
                latest_file = max(fundamental_files, key=lambda f: f.stat().st_mtime)
                availability["fundamental_analysis"]["latest_file"] = str(latest_file)
                availability["fundamental_analysis"]["latest_date"] = datetime.fromtimestamp(
                    latest_file.stat().st_mtime
                ).isoformat()

        # Check sector analysis files
        if self.sector_analysis_dir.exists():
            sector_files = list(self.sector_analysis_dir.glob("*.md"))
            availability["sector_analysis"]["available"] = len(sector_files) > 0
            availability["sector_analysis"]["files"] = [str(f) for f in sector_files]

        # Check cache data
        for cache_dir in self.cache_dirs:
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("*.json"))
                if cache_files:
                    availability["cache_data"]["available"] = True
                    availability["cache_data"]["cache_files"].extend([str(f) for f in cache_files])

        # Calculate local coverage score
        coverage_score = 0
        if availability["fundamental_analysis"]["available"]:
            coverage_score += 0.7  # 70% weight for fundamental analysis
        if availability["sector_analysis"]["available"]:
            coverage_score += 0.2  # 20% weight for sector analysis
        if availability["cache_data"]["available"]:
            coverage_score += 0.1  # 10% weight for cache data

        availability["local_coverage"] = coverage_score

        return availability

    def get_market_data_with_fallback(self, ticker: str, data_type: str = "quote") -> dict[str, Any]:
        """
        Get market data with intelligent fallback strategy

        Args:
            ticker: Stock ticker symbol
            data_type: Type of data to retrieve (quote, history, fundamental)

        Returns:
            Market data with metadata about source and method
        """
        result = {
            "ticker": ticker.upper(),
            "data_type": data_type,
            "data": None,
            "source": "unknown",
            "method": "unknown",
            "success": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        # First, check local data availability
        local_availability = self.check_local_data_availability(ticker)

        # If local data is sufficient, use it
        if local_availability["local_coverage"] > 0.7:
            try:
                local_data = self._get_local_data(ticker, data_type, local_availability)
                if local_data:
                    result["data"] = local_data
                    result["source"] = "local"
                    result["method"] = "file_system"
                    result["success"] = True
                    result["local_coverage"] = local_availability["local_coverage"]
                    return result
            except Exception as e:
                self.logger.warning(f"Failed to get local data for {ticker}: {e}")

        # Fall back to CLI services
        service_priorities = self.service_priorities.get("stock_analysis", ["yahoo_finance"])

        for service_name in service_priorities:
            try:
                if service_name not in self.cli_manager.get_available_services():
                    self.logger.debug(f"Service {service_name} not available")
                    continue

                # Execute command based on data type
                command_map = {
                    "quote": "quote",
                    "history": "history",
                    "fundamental": "analyze",
                }

                command = command_map.get(data_type, "quote")

                success, stdout, stderr = execute_cli_command(
                    service_name, command, ticker, env="dev", output_format="json"
                )

                if success and stdout:
                    try:
                        data = json.loads(stdout)
                        result["data"] = data
                        result["source"] = service_name
                        result["method"] = "cli_service"
                        result["success"] = True
                        result["local_coverage"] = local_availability["local_coverage"]
                        return result
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON response from {service_name}")
                        continue
                else:
                    self.logger.warning(f"CLI command failed for {service_name}: {stderr}")
                    continue

            except Exception as e:
                self.logger.warning(f"Failed to execute {service_name} service: {e}")
                continue

        # If all methods fail, return error
        result["error"] = f"No available service for {ticker} {data_type}"
        self.logger.error(result["error"])
        return result

    def _get_local_data(self, ticker: str, data_type: str, availability: dict[str, Any]) -> dict[str, Any] | None:
        """
        Get data from local sources

        Args:
            ticker: Stock ticker symbol
            data_type: Type of data requested
            availability: Local data availability information

        Returns:
            Local data if available, None otherwise
        """
        if data_type == "fundamental" and availability["fundamental_analysis"]["available"]:
            # Read fundamental analysis file
            file_path = Path(availability["fundamental_analysis"]["latest_file"])
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        content = f.read()

                    return {
                        "ticker": ticker.upper(),
                        "analysis_type": "fundamental",
                        "content": content,
                        "file_path": str(file_path),
                        "timestamp": availability["fundamental_analysis"]["latest_date"],
                        "source": "local_file",
                    }
                except Exception as e:
                    self.logger.warning(f"Failed to read fundamental analysis file: {e}")

        # For other data types, check cache
        if availability["cache_data"]["available"]:
            for cache_file in availability["cache_data"]["cache_files"]:
                try:
                    with open(cache_file) as f:
                        cache_data = json.load(f)

                    # Check if cache data matches ticker and data type
                    if cache_data.get("data", {}).get("ticker") == ticker.upper() or ticker.upper() in str(cache_data):
                        return cache_data.get("data")

                except Exception as e:
                    self.logger.debug(f"Failed to read cache file {cache_file}: {e}")
                    continue

        return None

    def get_service_health_summary(self) -> dict[str, Any]:
        """
        Get comprehensive health summary of all services

        Returns:
            Dictionary containing service health information
        """
        health_info = self.cli_manager.health_check_all()

        # Add local data statistics
        local_stats = {
            "fundamental_analysis_files": (
                len(list(self.fundamental_analysis_dir.glob("*.md"))) if self.fundamental_analysis_dir.exists() else 0
            ),
            "sector_analysis_files": (
                len(list(self.sector_analysis_dir.glob("*.md"))) if self.sector_analysis_dir.exists() else 0
            ),
            "cache_files": sum(
                len(list(cache_dir.glob("*.json"))) for cache_dir in self.cache_dirs if cache_dir.exists()
            ),
        }

        health_info["local_data_stats"] = local_stats
        health_info["service_priorities"] = self.service_priorities

        return health_info

    def optimize_service_usage(self, tickers: list[str]) -> dict[str, Any]:
        """
        Optimize service usage for multiple tickers

        Args:
            tickers: List of ticker symbols

        Returns:
            Optimization plan and statistics
        """
        optimization_plan = {
            "total_tickers": len(tickers),
            "local_data_available": 0,
            "external_calls_needed": 0,
            "service_plan": {},
            "recommendations": [],
        }

        # Analyze local data availability for all tickers
        for ticker in tickers:
            availability = self.check_local_data_availability(ticker)

            if availability["local_coverage"] > 0.7:
                optimization_plan["local_data_available"] += 1
                optimization_plan["service_plan"][ticker] = {
                    "method": "local",
                    "coverage": availability["local_coverage"],
                }
            else:
                optimization_plan["external_calls_needed"] += 1
                optimization_plan["service_plan"][ticker] = {
                    "method": "external",
                    "coverage": availability["local_coverage"],
                }

        # Generate recommendations
        local_coverage_ratio = optimization_plan["local_data_available"] / len(tickers)

        if local_coverage_ratio > 0.8:
            optimization_plan["recommendations"].append("Excellent local data coverage - minimal external calls needed")
        elif local_coverage_ratio > 0.5:
            optimization_plan["recommendations"].append("Good local data coverage - consider caching missing data")
        else:
            optimization_plan["recommendations"].append("Low local data coverage - prioritize data collection")

        if optimization_plan["external_calls_needed"] > 10:
            optimization_plan["recommendations"].append("High external call volume - implement request batching")

        return optimization_plan


def create_service_discovery_manager(
    local_data_dir: Path | None = None,
) -> ServiceDiscoveryManager:
    """Factory function to create service discovery manager"""
    return ServiceDiscoveryManager(local_data_dir)


if __name__ == "__main__":
    # Example usage and testing
    import pprint

    # Create service discovery manager
    discovery = create_service_discovery_manager()

    # Test service health
    print("=== Service Health Summary ===")
    health = discovery.get_service_health_summary()
    pprint.pprint(health)

    # Test local data availability
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    print("\n=== Local Data Availability for {test_tickers} ===")
    for ticker in test_tickers:
        availability = discovery.check_local_data_availability(ticker)
        print("{ticker}: {availability['local_coverage']:.1%} coverage")

    # Test optimization planning
    print("\n=== Optimization Plan ===")
    plan = discovery.optimize_service_usage(test_tickers)
    pprint.pprint(plan)
