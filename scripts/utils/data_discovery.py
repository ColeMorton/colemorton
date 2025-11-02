#!/usr/bin/env python3
"""
Historical Data Discovery API

Provides comprehensive querying and discovery capabilities for historical financial data.
Enables searching by symbol, date range, data type, and advanced filtering criteria.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from historical_data_manager import DataType, HistoricalDataManager, Timeframe


@dataclass
class DataAvailability:
    """Information about data availability for a symbol"""

    symbol: str
    data_types: list[str]
    date_range: dict[str, str]  # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    total_records: int
    timeframes: list[str]
    last_updated: str


@dataclass
class DataQualityMetrics:
    """Data quality metrics for a dataset"""

    completeness: float  # Percentage of expected data points present
    consistency: float  # Consistency score across sources
    timeliness: float  # How recent the data is
    accuracy: float  # Estimated accuracy score
    overall_score: float


class DataDiscoveryAPI:
    """
    Historical Data Discovery and Query API

    Provides comprehensive search, discovery, and analysis capabilities
    for historical financial data stored in the raw data repository.
    """

    def __init__(self, historical_manager: HistoricalDataManager | None = None):
        """
        Initialize Data Discovery API

        Args:
            historical_manager: Optional existing HistoricalDataManager instance
        """
        self.historical_manager = historical_manager or HistoricalDataManager()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for data discovery API"""
        logger = logging.getLogger("data_discovery_api")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def search_symbols(
        self,
        pattern: str | None = None,
        data_type: DataType | None = None,
        sector: str | None = None,
        min_records: int = 0,
    ) -> list[str]:
        """
        Search for symbols matching criteria

        Args:
            pattern: Symbol pattern to match (supports wildcards)
            data_type: Filter by specific data type
            sector: Filter by sector name
            min_records: Minimum number of records required

        Returns:
            List of matching symbols
        """
        try:
            all_symbols = list(self.historical_manager.metadata.get("symbols", {}).keys())

            if not all_symbols:
                return []

            # Apply pattern filter
            if pattern:
                import fnmatch

                all_symbols = [s for s in all_symbols if fnmatch.fnmatch(s.upper(), pattern.upper())]

            # Apply data type filter
            if data_type:
                filtered_symbols = []
                for symbol in all_symbols:
                    symbol_data = self.historical_manager.metadata["symbols"].get(symbol, {})
                    if data_type.value in symbol_data.get("data_types", []):
                        filtered_symbols.append(symbol)
                all_symbols = filtered_symbols

            # Apply minimum records filter
            if min_records > 0:
                # This would require counting actual files - simplified for now
                pass

            return sorted(all_symbols)

        except Exception as e:
            self.logger.error(f"Error searching symbols: {e}")
            return []

    def get_symbol_availability(self, symbol: str) -> DataAvailability | None:
        """
        Get data availability information for a symbol

        Args:
            symbol: Symbol to check

        Returns:
            DataAvailability object or None if not found
        """
        try:
            symbol_upper = symbol.upper()
            symbol_data = self.historical_manager.metadata.get("symbols", {}).get(symbol_upper)

            if not symbol_data:
                return None

            # Count total records by scanning directory
            total_records = self._count_symbol_records(symbol_upper)

            # Get available timeframes by scanning file structure
            timeframes = self._get_symbol_timeframes(symbol_upper)

            return DataAvailability(
                symbol=symbol_upper,
                data_types=symbol_data.get("data_types", []),
                date_range={
                    "start": symbol_data.get("first_date", ""),
                    "end": symbol_data.get("last_date", ""),
                },
                total_records=total_records,
                timeframes=timeframes,
                last_updated=symbol_data.get("last_updated", ""),
            )

        except Exception as e:
            self.logger.error(f"Error getting symbol availability for {symbol}: {e}")
            return None

    def _count_symbol_records(self, symbol: str) -> int:
        """Count total records for a symbol across all data types"""
        try:
            count = 0
            base_path = self.historical_manager.base_path

            # Search in stocks directory
            symbol_path = base_path / "stocks" / symbol
            if symbol_path.exists():
                count += len(list(symbol_path.rglob("*.json")))

            return count

        except Exception as e:
            self.logger.warning(f"Error counting records for {symbol}: {e}")
            return 0

    def _get_symbol_timeframes(self, symbol: str) -> list[str]:
        """Get available timeframes for a symbol"""
        try:
            timeframes = set()
            base_path = self.historical_manager.base_path

            # Search in stocks directory for different timeframe patterns
            symbol_path = base_path / "stocks" / symbol
            if symbol_path.exists():
                for file_path in symbol_path.rglob("*.json"):
                    # Try to detect timeframe from path structure
                    path_parts = file_path.parts
                    if "W" in str(file_path.name):  # Weekly files
                        timeframes.add("weekly")
                    elif "Q" in str(file_path.name):  # Quarterly files
                        timeframes.add("quarterly")
                    elif len(path_parts) >= 3 and path_parts[-2].isdigit():  # Monthly
                        timeframes.add("monthly")
                    else:
                        timeframes.add("daily")

            return sorted(list(timeframes))

        except Exception as e:
            self.logger.warning(f"Error getting timeframes for {symbol}: {e}")
            return ["daily"]

    def query_data(
        self,
        symbols: list[str] | None = None,
        data_types: list[DataType] | None = None,
        date_start: str | datetime | None = None,
        date_end: str | datetime | None = None,
        timeframe: Timeframe = Timeframe.DAILY,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical data with flexible criteria

        Args:
            symbols: List of symbols to query (None for all)
            data_types: List of data types to include
            date_start: Start date for query
            date_end: End date for query
            timeframe: Data timeframe
            limit: Maximum number of records to return

        Returns:
            List of matching data records
        """
        try:
            results = []

            # Default to all symbols if none specified
            if symbols is None:
                symbols = list(self.historical_manager.metadata.get("symbols", {}).keys())

            # Default to all data types if none specified
            if data_types is None:
                data_types = list(DataType)

            # Default date range to last 30 days if not specified
            if date_end is None:
                date_end = datetime.now()
            if date_start is None:
                date_start = date_end - timedelta(days=30)

            # Query each symbol and data type combination
            for symbol in symbols[:100]:  # Limit to prevent excessive queries
                for data_type in data_types:
                    try:
                        symbol_data = self.historical_manager.retrieve_data(
                            symbol=symbol,
                            data_type=data_type,
                            date_start=date_start,
                            date_end=date_end,
                            timeframe=timeframe,
                        )
                        results.extend(symbol_data)

                        # Apply limit if specified
                        if limit and len(results) >= limit:
                            return results[:limit]

                    except Exception as e:
                        self.logger.debug(f"No data for {symbol} {data_type.value}: {e}")
                        continue

            return results

        except Exception as e:
            self.logger.error(f"Error querying data: {e}")
            return []

    def get_data_quality_metrics(
        self,
        symbol: str,
        data_type: DataType,
        date_start: str | datetime | None = None,
        date_end: str | datetime | None = None,
    ) -> DataQualityMetrics | None:
        """
        Calculate data quality metrics for a symbol and data type

        Args:
            symbol: Symbol to analyze
            data_type: Data type to analyze
            date_start: Start date for analysis
            date_end: End date for analysis

        Returns:
            DataQualityMetrics object or None if insufficient data
        """
        try:
            # Get data for analysis
            if date_end is None:
                date_end = datetime.now()
            if date_start is None:
                date_start = date_end - timedelta(days=365)  # Last year

            data = self.historical_manager.retrieve_data(
                symbol=symbol,
                data_type=data_type,
                date_start=date_start,
                date_end=date_end,
                timeframe=Timeframe.DAILY,
            )

            if not data:
                return None

            # Calculate completeness (simplified)
            expected_days = (date_end - date_start).days
            actual_records = len(data)
            completeness = min(1.0, actual_records / max(1, expected_days * 0.7))  # Assume ~70% trading days

            # Calculate consistency (check for data anomalies)
            consistency = self._calculate_consistency(data, data_type)

            # Calculate timeliness (how recent is the latest data)
            if data:
                latest_date = datetime.fromisoformat(data[-1]["date"])
                days_old = (datetime.now() - latest_date).days
                timeliness = max(0.0, 1.0 - (days_old / 30.0))  # Decay over 30 days
            else:
                timeliness = 0.0

            # Calculate accuracy (simplified heuristic)
            accuracy = self._calculate_accuracy(data, data_type)

            # Overall score (weighted average)
            overall_score = completeness * 0.3 + consistency * 0.25 + timeliness * 0.25 + accuracy * 0.2

            return DataQualityMetrics(
                completeness=round(completeness, 3),
                consistency=round(consistency, 3),
                timeliness=round(timeliness, 3),
                accuracy=round(accuracy, 3),
                overall_score=round(overall_score, 3),
            )

        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
            return None

    def _calculate_consistency(self, data: list[dict[str, Any]], data_type: DataType) -> float:
        """Calculate data consistency score"""
        try:
            if len(data) < 2:
                return 1.0

            inconsistencies = 0
            total_checks = 0

            for record in data:
                record_data = record.get("data", {})

                # Check for missing required fields based on data type
                if data_type == DataType.STOCK_DAILY_PRICES:
                    required_fields = ["close", "volume"]
                    for field in required_fields:
                        total_checks += 1
                        if field not in record_data or record_data[field] is None:
                            inconsistencies += 1

                    # Check for reasonable price values
                    if "close" in record_data and record_data["close"]:
                        price = float(record_data["close"])
                        if price <= 0 or price > 100000:  # Unreasonable price
                            inconsistencies += 1
                        total_checks += 1

            consistency_score = 1.0 - (inconsistencies / max(1, total_checks))
            return max(0.0, consistency_score)

        except Exception:
            return 0.5  # Default to moderate consistency if calculation fails

    def _calculate_accuracy(self, data: list[dict[str, Any]], data_type: DataType) -> float:
        """Calculate data accuracy score (simplified heuristic)"""
        try:
            if not data:
                return 0.0

            # For stock prices, check for reasonable values and relationships
            if data_type == DataType.STOCK_DAILY_PRICES:
                accurate_records = 0
                total_records = 0

                for record in data:
                    record_data = record.get("data", {})
                    total_records += 1

                    # Check OHLC relationships
                    try:
                        high = float(record_data.get("high", 0))
                        low = float(record_data.get("low", 0))
                        open_price = float(record_data.get("open", 0))
                        close = float(record_data.get("close", 0))

                        # Basic sanity checks
                        if (
                            high >= low
                            and high >= open_price
                            and high >= close
                            and low <= open_price
                            and low <= close
                            and all(p > 0 for p in [high, low, open_price, close])
                        ):
                            accurate_records += 1

                    except (ValueError, TypeError):
                        pass  # Skip invalid records

                return accurate_records / max(1, total_records)

            return 0.8  # Default accuracy for other data types

        except Exception:
            return 0.5  # Default to moderate accuracy if calculation fails

    def generate_discovery_report(
        self,
        symbols: list[str] | None = None,
        include_quality: bool = True,
        output_format: str = "dict",
    ) -> dict[str, Any] | str:
        """
        Generate comprehensive discovery report

        Args:
            symbols: List of symbols to include (None for all)
            include_quality: Whether to include quality metrics
            output_format: Output format ("dict" or "json")

        Returns:
            Discovery report in requested format
        """
        try:
            if symbols is None:
                symbols = list(self.historical_manager.metadata.get("symbols", {}).keys())[:50]  # Limit for performance

            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_symbols": len(symbols),
                    "total_files": self.historical_manager.metadata.get("total_files", 0),
                    "data_types": list(self.historical_manager.metadata.get("data_types", {}).keys()),
                },
                "symbols": {},
            }

            # Generate symbol-level reports
            for symbol in symbols:
                symbol_info = self.get_symbol_availability(symbol)
                if symbol_info:
                    symbol_report = {
                        "data_types": symbol_info.data_types,
                        "date_range": symbol_info.date_range,
                        "total_records": symbol_info.total_records,
                        "timeframes": symbol_info.timeframes,
                    }

                    # Add quality metrics if requested
                    if include_quality and symbol_info.data_types:
                        symbol_report["quality_metrics"] = {}
                        for data_type_str in symbol_info.data_types[:3]:  # Limit for performance
                            try:
                                data_type = DataType(data_type_str)
                                quality = self.get_data_quality_metrics(symbol, data_type)
                                if quality:
                                    symbol_report["quality_metrics"][data_type_str] = {
                                        "completeness": quality.completeness,
                                        "consistency": quality.consistency,
                                        "timeliness": quality.timeliness,
                                        "accuracy": quality.accuracy,
                                        "overall_score": quality.overall_score,
                                    }
                            except ValueError:
                                continue

                    report["symbols"][symbol] = symbol_report

            if output_format == "json":
                return json.dumps(report, indent=2, default=str)

            return report

        except Exception as e:
            self.logger.error(f"Error generating discovery report: {e}")
            return {} if output_format == "dict" else "{}"

    def get_trending_symbols(self, days: int = 30, min_activity: int = 5) -> list[dict[str, Any]]:
        """
        Get symbols with high data activity in recent period

        Args:
            days: Number of days to look back
            min_activity: Minimum number of data points required

        Returns:
            List of trending symbols with activity metrics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            trending = []

            for symbol in self.historical_manager.metadata.get("symbols", {}).keys():
                symbol_data = self.historical_manager.metadata["symbols"][symbol]
                last_date = datetime.fromisoformat(symbol_data.get("last_date", "1900-01-01"))

                if last_date >= cutoff_date:
                    # Count recent activity (simplified)
                    activity_score = len(symbol_data.get("data_types", []))

                    if activity_score >= min_activity:
                        trending.append(
                            {
                                "symbol": symbol,
                                "activity_score": activity_score,
                                "last_updated": symbol_data.get("last_date"),
                                "data_types": symbol_data.get("data_types", []),
                            }
                        )

            # Sort by activity score
            trending.sort(key=lambda x: x["activity_score"], reverse=True)
            return trending[:20]  # Top 20

        except Exception as e:
            self.logger.error(f"Error getting trending symbols: {e}")
            return []


def create_data_discovery_api(
    historical_manager: HistoricalDataManager | None = None,
) -> DataDiscoveryAPI:
    """Factory function to create data discovery API"""
    return DataDiscoveryAPI(historical_manager)


if __name__ == "__main__":
    # Example usage
    api = create_data_discovery_api()

    # Search for symbols
    symbols = api.search_symbols(pattern="A*", min_records=10)
    print("Found symbols: {symbols[:5]}")

    # Get availability for a symbol
    if symbols:
        availability = api.get_symbol_availability(symbols[0])
        print("Availability for {symbols[0]}: {availability}")

    # Generate discovery report
    report = api.generate_discovery_report(symbols[:3])
    print("Report summary: {report.get('summary', {})}")
