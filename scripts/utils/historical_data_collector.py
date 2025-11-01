#!/usr/bin/env python3
"""
Historical Data Collector Service

Comprehensive historical data collection service that automatically collects:
- 365 days of daily price data for tracked symbols
- 5 years of weekly price data for tracked symbols
- Batch processing with rate limiting
- Gap detection and filling capabilities
- Integration with existing financial services
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from historical_data_manager import DataType, HistoricalDataManager, Timeframe


class HistoricalDataCollector:
    """
    Comprehensive historical data collector for financial market data

    Features:
    - Automatic collection of 365 days daily + 5 years weekly data
    - Intelligent gap detection and filling
    - Rate limiting and batch processing
    - Progress tracking and resumption
    - Integration with all financial services
    """

    def __init__(
        self,
        historical_manager: HistoricalDataManager | None = None,
        rate_limit_delay: float = 0.5,  # Seconds between API calls
        batch_size: int = 10,  # Symbols per batch
        max_retries: int = 3,
    ):
        """
        Initialize Historical Data Collector

        Args:
            historical_manager: HistoricalDataManager instance
            rate_limit_delay: Delay between API calls in seconds
            batch_size: Number of symbols to process per batch
            max_retries: Maximum retry attempts for failed requests
        """
        self.hdm = historical_manager or HistoricalDataManager()
        self.rate_limit_delay = rate_limit_delay
        self.batch_size = batch_size
        self.max_retries = max_retries

        self.logger = self._setup_logger()

        # Collection tracking
        self.collection_state_file = self.hdm.base_path / "collection_state.json"
        self.collection_state = self._load_collection_state()

        # Service instances (lazy loaded)
        self._services = {}

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for data collector"""
        logger = logging.getLogger("historical_data_collector")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _load_collection_state(self) -> dict[str, Any]:
        """Load collection state for resuming interrupted collections"""
        if self.collection_state_file.exists():
            try:
                with open(self.collection_state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load collection state: {e}")

        return {
            "last_collection": None,
            "symbols_completed": [],
            "symbols_failed": [],
            "collection_sessions": [],
        }

    def _save_collection_state(self) -> None:
        """Save collection state for resumption"""
        try:
            with open(self.collection_state_file, "w") as f:
                json.dump(self.collection_state, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save collection state: {e}")

    def _get_service(self, service_name: str):
        """Lazy load financial services"""
        if service_name not in self._services:
            try:
                # Add the scripts directory to the path for imports
                import sys
                from pathlib import Path

                scripts_path = str(Path(__file__).parent.parent)
                if scripts_path not in sys.path:
                    sys.path.insert(0, scripts_path)

                if service_name == "yahoo_finance":
                    from services.yahoo_finance import create_yahoo_finance_service

                    self._services[service_name] = create_yahoo_finance_service()
                elif service_name == "fmp":
                    from services.fmp import create_fmp_service

                    self._services[service_name] = create_fmp_service()
                elif service_name == "alpha_vantage":
                    from services.alpha_vantage import create_alpha_vantage_service

                    self._services[service_name] = create_alpha_vantage_service()
                else:
                    raise ValueError(f"Unknown service: {service_name}")
            except Exception as e:
                self.logger.error(f"Failed to load service {service_name}: {e}")
                return None

        return self._services[service_name]

    def get_target_symbols(self, custom_symbols: list[str] | None = None) -> list[str]:
        """
        Get list of symbols to collect data for

        Args:
            custom_symbols: Optional list of custom symbols to collect

        Returns:
            List of symbols to collect comprehensive data for
        """
        if custom_symbols:
            return [s.upper() for s in custom_symbols]

        # Default high-value symbols for comprehensive collection
        default_symbols = [
            # Tech Giants
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "TSLA",
            "NVDA",
            # Financial
            "JPM",
            "BAC",
            "WFC",
            "GS",
            "MS",
            "C",
            # Healthcare
            "JNJ",
            "PFE",
            "UNH",
            "MRK",
            "ABT",
            # Consumer
            "KO",
            "PEP",
            "WMT",
            "HD",
            "MCD",
            # Industrial
            "BA",
            "CAT",
            "GE",
            "MMM",
            # Energy
            "XOM",
            "CVX",
            "COP",
        ]

        return default_symbols

    def detect_data_gaps(
        self,
        symbol: str,
        data_type: DataType,
        target_days: int,
        timeframe: Timeframe = Timeframe.DAILY,
    ) -> list[datetime]:
        """
        Detect gaps in historical data for a symbol

        Args:
            symbol: Stock symbol to check
            data_type: Type of data to check for gaps
            target_days: Number of days back to check
            timeframe: Data timeframe to check

        Returns:
            List of dates with missing data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=target_days)

        # Get existing data
        existing_data = self.hdm.retrieve_data(
            symbol=symbol,
            data_type=data_type,
            date_start=start_date,
            date_end=end_date,
            timeframe=timeframe,
        )

        # Extract dates from existing data
        existing_dates = set()
        for record in existing_data:
            if "date" in record:
                try:
                    date_obj = datetime.fromisoformat(record["date"].replace("Z", "+00:00"))
                    existing_dates.add(date_obj.date())
                except Exception:
                    continue

        # Find missing dates (excluding weekends for daily data)
        missing_dates = []
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends for daily stock data
            if timeframe == Timeframe.DAILY and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            if current_date.date() not in existing_dates:
                missing_dates.append(current_date)

            # Increment based on timeframe
            if timeframe == Timeframe.DAILY:
                current_date += timedelta(days=1)
            elif timeframe == Timeframe.WEEKLY:
                current_date += timedelta(weeks=1)
            else:
                current_date += timedelta(days=30)  # Monthly approximation

        return missing_dates

    def collect_daily_prices(
        self, symbols: list[str], days: int = 365, service_name: str = "yahoo_finance"
    ) -> dict[str, Any]:
        """
        Collect daily price data for symbols

        Args:
            symbols: List of stock symbols
            days: Number of days of data to collect (default 365)
            service_name: Financial service to use

        Returns:
            Collection results summary
        """
        self.logger.info(f"Starting daily price collection for {len(symbols)} symbols ({days} days)")

        service = self._get_service(service_name)
        if not service:
            return {"error": f"Failed to load service {service_name}"}

        results = {
            "symbols_processed": 0,
            "symbols_successful": [],
            "symbols_failed": [],
            "files_created": 0,
            "errors": [],
        }

        for i, symbol in enumerate(symbols):
            try:
                self.logger.info(f"Processing {symbol} ({i + 1}/{len(symbols)})")

                # Detect gaps in daily data
                gaps = self.detect_data_gaps(
                    symbol=symbol,
                    data_type=DataType.STOCK_DAILY_PRICES,
                    target_days=days,
                    timeframe=Timeframe.DAILY,
                )

                if not gaps:
                    self.logger.info(f"  {symbol}: No gaps detected, skipping")
                    results["symbols_successful"].append(symbol)
                    continue

                self.logger.info(f"  {symbol}: Found {len(gaps)} missing days")

                # Get historical data (Yahoo Finance supports up to 2 years in one call)
                if hasattr(service, "get_historical_data"):
                    # Determine period based on days needed
                    if days <= 7:
                        period = "5d"
                    elif days <= 30:
                        period = "1mo"
                    elif days <= 90:
                        period = "3mo"
                    elif days <= 180:
                        period = "6mo"
                    elif days <= 365:
                        period = "1y"
                    elif days <= 730:
                        period = "2y"
                    else:
                        period = "5y"  # Maximum available

                    # Get data from service
                    data = service.get_historical_data(symbol, period)

                    if data and "data" in data:
                        # Store the data (service will automatically handle historical storage)
                        service.store_historical_data(
                            data=data,
                            endpoint=f"historical_{symbol}_{period}",
                            params={"symbol": symbol, "period": period},
                            data_type=DataType.STOCK_DAILY_PRICES,
                            symbol=symbol,
                            timeframe=Timeframe.DAILY,
                        )

                        results["files_created"] += 1
                        results["symbols_successful"].append(symbol)
                        self.logger.info(f"  {symbol}: Successfully collected {period} data")
                    else:
                        results["symbols_failed"].append(symbol)
                        results["errors"].append(f"{symbol}: No data returned")

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                results["errors"].append(error_msg)
                results["symbols_failed"].append(symbol)
                self.logger.error(f"  {error_msg}")

            results["symbols_processed"] += 1

        return results

    def collect_weekly_prices(
        self, symbols: list[str], years: int = 5, service_name: str = "yahoo_finance"
    ) -> dict[str, Any]:
        """
        Collect weekly price data for symbols

        Args:
            symbols: List of stock symbols
            years: Number of years of weekly data to collect (default 5)
            service_name: Financial service to use

        Returns:
            Collection results summary
        """
        self.logger.info(f"Starting weekly price collection for {len(symbols)} symbols ({years} years)")

        service = self._get_service(service_name)
        if not service:
            return {"error": f"Failed to load service {service_name}"}

        results = {
            "symbols_processed": 0,
            "symbols_successful": [],
            "symbols_failed": [],
            "files_created": 0,
            "errors": [],
        }

        for i, symbol in enumerate(symbols):
            try:
                self.logger.info(f"Processing weekly data for {symbol} ({i + 1}/{len(symbols)})")

                # For weekly data, we'll get longer historical data and aggregate to weekly
                period = "5y" if years <= 5 else "max"

                if hasattr(service, "get_historical_data"):
                    # Get daily data first
                    data = service.get_historical_data(symbol, period)

                    if data and "data" in data:
                        # Convert daily data to weekly aggregation
                        weekly_data = self._aggregate_to_weekly(data["data"])

                        if weekly_data:
                            # Store weekly data
                            weekly_data_wrapper = {
                                "symbol": symbol,
                                "period": f"{years}y_weekly",
                                "data": weekly_data,
                                "source": service_name,
                                "aggregated_from": "daily",
                            }

                            service.store_historical_data(
                                data=weekly_data_wrapper,
                                endpoint=f"weekly_{symbol}_{years}y",
                                params={
                                    "symbol": symbol,
                                    "period": f"{years}y",
                                    "interval": "weekly",
                                },
                                data_type=DataType.STOCK_DAILY_PRICES,  # Using same type for now
                                symbol=symbol,
                                timeframe=Timeframe.WEEKLY,
                            )

                            results["files_created"] += 1
                            results["symbols_successful"].append(symbol)
                            self.logger.info(f"  {symbol}: Successfully aggregated and stored weekly data")
                        else:
                            results["symbols_failed"].append(symbol)
                            results["errors"].append(f"{symbol}: Failed to aggregate weekly data")
                    else:
                        results["symbols_failed"].append(symbol)
                        results["errors"].append(f"{symbol}: No daily data for weekly aggregation")

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                results["errors"].append(error_msg)
                results["symbols_failed"].append(symbol)
                self.logger.error(f"  {error_msg}")

            results["symbols_processed"] += 1

        return results

    def _aggregate_to_weekly(self, daily_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Aggregate daily price data to weekly data

        Args:
            daily_data: List of daily price records

        Returns:
            List of weekly aggregated price records
        """
        if not daily_data:
            return []

        # Sort by date
        sorted_data = sorted(daily_data, key=lambda x: x.get("Date", ""))

        weekly_data = []
        current_week = []
        current_week_start = None

        for record in sorted_data:
            try:
                date_str = record.get("Date", "")
                if not date_str:
                    continue

                # Handle different date formats from pandas Timestamp
                if hasattr(date_str, "strftime"):
                    date_obj = date_str
                else:
                    date_obj = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
                week_start = date_obj - timedelta(days=date_obj.weekday())  # Monday of the week

                if current_week_start is None or week_start != current_week_start:
                    # Process previous week
                    if current_week:
                        weekly_record = self._create_weekly_record(current_week)
                        if weekly_record:
                            weekly_data.append(weekly_record)

                    # Start new week
                    current_week = [record]
                    current_week_start = week_start
                else:
                    current_week.append(record)

            except Exception as e:
                self.logger.warning(f"Failed to process daily record for weekly aggregation: {e}")
                continue

        # Process final week
        if current_week:
            weekly_record = self._create_weekly_record(current_week)
            if weekly_record:
                weekly_data.append(weekly_record)

        return weekly_data

    def _create_weekly_record(self, week_data: list[dict[str, Any]]) -> dict[str, Any] | None:
        """
        Create a weekly aggregated record from daily data

        Args:
            week_data: List of daily records for the week

        Returns:
            Weekly aggregated record or None if insufficient data
        """
        if not week_data:
            return None

        try:
            # Get first and last days
            first_day = week_data[0]
            last_day = week_data[-1]

            # Extract prices
            opens = [float(d.get("Open", 0)) for d in week_data if d.get("Open")]
            highs = [float(d.get("High", 0)) for d in week_data if d.get("High")]
            lows = [float(d.get("Low", 0)) for d in week_data if d.get("Low")]
            closes = [float(d.get("Close", 0)) for d in week_data if d.get("Close")]
            volumes = [int(d.get("Volume", 0)) for d in week_data if d.get("Volume")]

            if not (opens and highs and lows and closes):
                return None

            weekly_record = {
                "Date": first_day.get("Date"),  # Use first day of week
                "Open": opens[0],  # Open of first day
                "High": max(highs),  # Highest high of the week
                "Low": min(lows),  # Lowest low of the week
                "Close": closes[-1],  # Close of last day
                "Volume": sum(volumes),  # Total volume for the week
                "trading_days": len(week_data),
                "week_start": first_day.get("Date"),
                "week_end": last_day.get("Date"),
            }

            return weekly_record

        except Exception as e:
            self.logger.warning(f"Failed to create weekly record: {e}")
            return None

    def collect_comprehensive_data(
        self,
        symbols: list[str] | None = None,
        daily_days: int = 365,
        weekly_years: int = 0,
        service_name: str = "yahoo_finance",
    ) -> dict[str, Any]:
        """
        Collect comprehensive historical data (daily only by default, weekly disabled)

        Args:
            symbols: List of symbols (uses default high-value symbols if None)
            daily_days: Days of daily data to collect
            weekly_years: Years of weekly data to collect (0 = disabled by default)
            service_name: Financial service to use

        Returns:
            Comprehensive collection results
        """
        if symbols is None:
            symbols = self.get_target_symbols()

        self.logger.info("Starting comprehensive data collection")
        self.logger.info(f"  Symbols: {len(symbols)}")
        self.logger.info(f"  Daily: {daily_days} days")
        self.logger.info(f"  Weekly: {weekly_years} years")

        # Start collection session
        session_id = datetime.now().isoformat()
        self.collection_state["collection_sessions"].append(
            {
                "session_id": session_id,
                "started": session_id,
                "symbols": symbols,
                "daily_days": daily_days,
                "weekly_years": weekly_years,
                "service": service_name,
            }
        )

        results = {
            "session_id": session_id,
            "total_symbols": len(symbols),
            "daily_collection": {},
            "weekly_collection": {},
            "overall_success": False,
            "total_files_created": 0,
        }

        try:
            # Collect daily data
            self.logger.info("🔄 Phase 1: Collecting daily price data")
            daily_results = self.collect_daily_prices(symbols=symbols, days=daily_days, service_name=service_name)
            results["daily_collection"] = daily_results

            # Collect weekly data only if enabled (weekly_years > 0)
            if weekly_years > 0:
                self.logger.info("🔄 Phase 2: Collecting weekly price data")
                weekly_results = self.collect_weekly_prices(
                    symbols=symbols, years=weekly_years, service_name=service_name
                )
                results["weekly_collection"] = weekly_results
            else:
                self.logger.info("📋 Phase 2: Weekly data collection disabled (weekly_years=0)")
                weekly_results = {
                    "symbols_processed": 0,
                    "symbols_successful": [],
                    "symbols_failed": [],
                    "files_created": 0,
                    "errors": [],
                }
                results["weekly_collection"] = weekly_results

            # Calculate overall results
            total_files = daily_results.get("files_created", 0) + weekly_results.get("files_created", 0)
            results["total_files_created"] = total_files
            results["overall_success"] = total_files > 0

            # Update collection state
            self.collection_state["last_collection"] = session_id
            self.collection_state["symbols_completed"].extend(daily_results.get("symbols_successful", []))

            self._save_collection_state()

            self.logger.info("✅ Comprehensive collection completed")
            self.logger.info(f"   Total files created: {total_files}")
            self.logger.info(f"   Daily successful: {len(daily_results.get('symbols_successful', []))}")
            self.logger.info(f"   Weekly successful: {len(weekly_results.get('symbols_successful', []))}")

            return results

        except Exception as e:
            self.logger.error(f"Comprehensive collection failed: {e}")
            results["error"] = str(e)
            return results

    def get_collection_status(self) -> dict[str, Any]:
        """Get current collection status and statistics"""
        return {
            "collection_state": self.collection_state,
            "available_data": self.hdm.get_available_data(),
            "services_loaded": list(self._services.keys()),
            "storage_location": str(self.hdm.base_path),
        }


def create_historical_data_collector(
    base_path: Path | None = None, rate_limit_delay: float = 0.5
) -> HistoricalDataCollector:
    """Factory function to create historical data collector"""
    hdm = HistoricalDataManager(base_path=base_path)
    return HistoricalDataCollector(historical_manager=hdm, rate_limit_delay=rate_limit_delay)


if __name__ == "__main__":
    # Example usage
    collector = create_historical_data_collector()

    # Test with small subset
    test_symbols = ["AAPL", "MSFT", "GOOGL"]

    print("🚀 Testing Historical Data Collector")
    print("=" * 50)

    # Collect comprehensive data
    results = collector.collect_comprehensive_data(
        symbols=test_symbols,
        daily_days=30,  # Start with 30 days for testing
        weekly_years=1,  # Start with 1 year for testing
    )

    print("\n📊 Collection Results:")
    print("   Session ID: {results.get('session_id')}")
    print("   Total files created: {results.get('total_files_created')}")
    print("   Overall success: {results.get('overall_success')}")

    if results.get("daily_collection"):
        daily = results["daily_collection"]
        print("\n📈 Daily Collection:")
        print("   Successful: {len(daily.get('symbols_successful', []))}")
        print("   Failed: {len(daily.get('symbols_failed', []))}")

    if results.get("weekly_collection"):
        weekly = results["weekly_collection"]
        print("\n📊 Weekly Collection:")
        print("   Successful: {len(weekly.get('symbols_successful', []))}")
        print("   Failed: {len(weekly.get('symbols_failed', []))}")

    # Show collection status
    status = collector.get_collection_status()
    print("\n📁 Storage Status:")
    print("   Total files: {status['available_data'].get('total_files', 0)}")
    print("   Symbols tracked: {status['available_data'].get('symbol_count', 0)}")
