#!/usr/bin/env python3
"""
Quarterly Financial Statement Collection Triggers

Implements event-driven collection triggers for quarterly financial statements
based on earnings announcement schedules and SEC filing patterns.
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from historical_data_manager import DataType, HistoricalDataManager


class QuarterlyTriggerType(Enum):
    """Types of quarterly collection triggers"""

    EARNINGS_ANNOUNCEMENT = "earnings_announcement"
    SEC_FILING_10Q = "sec_filing_10q"
    SEC_FILING_10K = "sec_filing_10k"
    SCHEDULED_QUARTERLY = "scheduled_quarterly"


class QuarterlyCollectionTrigger:
    """
    Manages quarterly financial statement collection triggers

    Features:
    - Earnings calendar integration
    - SEC filing detection
    - Quarterly schedule management
    - Event-driven collection triggering
    """

    def __init__(
        self,
        historical_manager: HistoricalDataManager | None = None,
        lookback_days: int = 7,  # Days before earnings to start watching
        lookahead_days: int = 30,  # Days after earnings to continue collection
    ):
        """
        Initialize Quarterly Collection Trigger

        Args:
            historical_manager: HistoricalDataManager instance
            lookback_days: Days before earnings to start collection
            lookahead_days: Days after earnings to continue collection
        """
        self.hdm = historical_manager or HistoricalDataManager()
        self.lookback_days = lookback_days
        self.lookahead_days = lookahead_days

        self.logger = self._setup_logger()

        # Trigger state tracking
        self.trigger_state_file = self.hdm.base_path / "quarterly_triggers.json"
        self.trigger_state = self._load_trigger_state()

        # Quarterly calendar cache
        self.earnings_calendar = {}
        self.quarterly_schedule = self._generate_quarterly_schedule()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for quarterly triggers"""
        logger = logging.getLogger("quarterly_collection_triggers")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _load_trigger_state(self) -> dict[str, Any]:
        """Load trigger state for persistence"""
        if self.trigger_state_file.exists():
            try:
                with open(self.trigger_state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load trigger state: {e}")

        return {
            "last_updated": None,
            "active_triggers": {},
            "completed_collections": {},
            "quarterly_schedule": {},
        }

    def _save_trigger_state(self) -> None:
        """Save trigger state for persistence"""
        try:
            self.trigger_state["last_updated"] = datetime.now().isoformat()
            with open(self.trigger_state_file, "w") as f:
                json.dump(self.trigger_state, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save trigger state: {e}")

    def _generate_quarterly_schedule(self) -> dict[str, list[datetime]]:
        """Generate standard quarterly reporting schedule"""
        current_year = datetime.now().year
        quarters = {}

        # Generate quarterly dates for current and next year
        for year in [current_year, current_year + 1]:
            quarters[str(year)] = [
                # Q1 earnings typically released in April-May
                datetime(year, 4, 15),  # Q1 earnings season start
                datetime(year, 5, 15),  # Q1 earnings season end
                # Q2 earnings typically released in July-August
                datetime(year, 7, 15),  # Q2 earnings season start
                datetime(year, 8, 15),  # Q2 earnings season end
                # Q3 earnings typically released in October-November
                datetime(year, 10, 15),  # Q3 earnings season start
                datetime(year, 11, 15),  # Q3 earnings season end
                # Q4 earnings typically released in January-March (of next year)
                (
                    datetime(year + 1, 1, 15) if year == current_year else datetime(year, 1, 15)
                ),  # Q4 earnings season start
                (
                    datetime(year + 1, 3, 15) if year == current_year else datetime(year, 3, 15)
                ),  # Q4 earnings season end
            ]

        return quarters

    def get_current_earnings_season(self) -> str | None:
        """Determine current earnings season"""
        now = datetime.now()
        current_year = str(now.year)

        if current_year not in self.quarterly_schedule:
            return None

        year_schedule = self.quarterly_schedule[current_year]

        # Check which earnings season we're in
        if year_schedule[0] <= now <= year_schedule[1]:  # Q1 season
            return "Q1"
        if year_schedule[2] <= now <= year_schedule[3]:  # Q2 season
            return "Q2"
        if year_schedule[4] <= now <= year_schedule[5]:  # Q3 season
            return "Q3"
        if year_schedule[6] <= now <= year_schedule[7]:  # Q4 season
            return "Q4"

        return None

    def is_earnings_season(self, lookback_days: int | None = None) -> bool:
        """Check if we're currently in or approaching earnings season"""
        if lookback_days is None:
            lookback_days = self.lookback_days

        now = datetime.now()
        current_year = str(now.year)

        if current_year not in self.quarterly_schedule:
            return False

        year_schedule = self.quarterly_schedule[current_year]

        # Check if we're within lookback_days of any earnings season
        for earnings_date in year_schedule:
            if (
                earnings_date - timedelta(days=lookback_days)
                <= now
                <= earnings_date + timedelta(days=self.lookahead_days)
            ):
                return True

        return False

    def should_trigger_collection(self, symbol: str, trigger_type: QuarterlyTriggerType) -> bool:
        """
        Determine if quarterly collection should be triggered for a symbol

        Args:
            symbol: Stock symbol
            trigger_type: Type of trigger event

        Returns:
            True if collection should be triggered
        """
        trigger_key = f"{symbol}_{trigger_type.value}"

        # Check if we've already triggered collection recently
        if trigger_key in self.trigger_state["completed_collections"]:
            last_collection = datetime.fromisoformat(self.trigger_state["completed_collections"][trigger_key])

            # Don't re-trigger within 60 days (roughly one quarter)
            if datetime.now() - last_collection < timedelta(days=60):
                return False

        # Earnings season trigger
        if trigger_type == QuarterlyTriggerType.EARNINGS_ANNOUNCEMENT:
            return self.is_earnings_season()

        # Scheduled quarterly trigger (every ~90 days)
        if trigger_type == QuarterlyTriggerType.SCHEDULED_QUARTERLY:
            if trigger_key not in self.trigger_state["completed_collections"]:
                return True  # First time collection

            last_collection = datetime.fromisoformat(self.trigger_state["completed_collections"][trigger_key])
            return datetime.now() - last_collection >= timedelta(days=85)  # ~3 months

        # SEC filing triggers (would require SEC filing detection)
        if trigger_type in [
            QuarterlyTriggerType.SEC_FILING_10Q,
            QuarterlyTriggerType.SEC_FILING_10K,
        ]:
            # Placeholder for SEC filing detection logic
            # In practice, this would check for recent 10-Q/10-K filings
            return self.is_earnings_season()

        return False

    def trigger_quarterly_collection(
        self,
        symbol: str,
        trigger_type: QuarterlyTriggerType,
        service_name: str = "yahoo_finance",
    ) -> dict[str, Any]:
        """
        Trigger quarterly financial statement collection for a symbol

        Args:
            symbol: Stock symbol to collect data for
            trigger_type: Type of trigger that initiated collection
            service_name: Financial service to use for collection

        Returns:
            Collection results
        """
        if not self.should_trigger_collection(symbol, trigger_type):
            return {
                "triggered": False,
                "reason": "Collection not needed or recently completed",
            }

        self.logger.info(f"Triggering quarterly collection for {symbol} ({trigger_type.value})")

        try:
            # Import here to avoid circular imports
            import sys
            from pathlib import Path

            utils_path = str(Path(__file__).parent)
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)

            from historical_data_collector import create_historical_data_collector

            # Create specialized collector for quarterly data
            collector = create_historical_data_collector(
                base_path=self.hdm.base_path,
                rate_limit_delay=0.1,  # Faster for quarterly events
            )

            # Get the service for financial statement collection
            service = collector._get_service(service_name)
            if not service:
                return {
                    "triggered": False,
                    "error": f"Failed to load service {service_name}",
                }

            results = {
                "triggered": True,
                "symbol": symbol,
                "trigger_type": trigger_type.value,
                "timestamp": datetime.now().isoformat(),
                "files_created": 0,
                "success": False,
            }

            # Attempt to collect financial statement data
            # This would depend on the specific service's financial data endpoints
            if hasattr(service, "get_financial_statements"):
                # Try to get recent financial statements
                financial_data = service.get_financial_statements(symbol)

                if financial_data:
                    # Store the financial data
                    service.store_historical_data(
                        data=financial_data,
                        endpoint=f"financial_statements_{symbol}",
                        params={"symbol": symbol, "trigger": trigger_type.value},
                        data_type=DataType.STOCK_FINANCIALS,
                        symbol=symbol,
                    )
                    results["files_created"] += 1
                    results["success"] = True

            # Also attempt to collect updated fundamentals
            if hasattr(service, "get_stock_info"):
                fundamentals_data = service.get_stock_info(symbol)

                if fundamentals_data:
                    service.store_historical_data(
                        data=fundamentals_data,
                        endpoint=f"fundamentals_{symbol}",
                        params={"symbol": symbol, "trigger": trigger_type.value},
                        data_type=DataType.STOCK_FUNDAMENTALS,
                        symbol=symbol,
                    )
                    results["files_created"] += 1
                    results["success"] = True

            # Mark collection as completed
            trigger_key = f"{symbol}_{trigger_type.value}"
            self.trigger_state["completed_collections"][trigger_key] = datetime.now().isoformat()
            self._save_trigger_state()

            self.logger.info(f"Quarterly collection completed for {symbol}: {results['files_created']} files created")
            return results

        except Exception as e:
            self.logger.error(f"Error during quarterly collection for {symbol}: {e}")
            return {"triggered": False, "error": str(e)}

    def scan_for_triggers(self, symbols: list[str] | None = None) -> dict[str, Any]:
        """
        Scan for symbols that need quarterly collection triggered

        Args:
            symbols: List of symbols to check (uses default set if None)

        Returns:
            Summary of triggered collections
        """
        if symbols is None:
            # Use default high-value symbols for quarterly monitoring
            symbols = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "META",
                "TSLA",
                "NVDA",
                "JPM",
                "BAC",
                "WFC",
                "GS",
                "C",
                "JNJ",
                "PFE",
                "UNH",
                "MRK",
                "KO",
                "PEP",
                "WMT",
                "HD",
            ]

        self.logger.info(f"Scanning {len(symbols)} symbols for quarterly triggers")

        results = {
            "scanned_symbols": len(symbols),
            "triggered_collections": 0,
            "symbols_triggered": [],
            "errors": [],
        }

        current_season = self.get_current_earnings_season()
        if current_season:
            self.logger.info(f"Currently in {current_season} earnings season")

        for symbol in symbols:
            try:
                # Check for earnings announcement trigger
                if self.should_trigger_collection(symbol, QuarterlyTriggerType.EARNINGS_ANNOUNCEMENT):
                    collection_result = self.trigger_quarterly_collection(
                        symbol, QuarterlyTriggerType.EARNINGS_ANNOUNCEMENT
                    )

                    if collection_result.get("triggered"):
                        results["triggered_collections"] += 1
                        results["symbols_triggered"].append(symbol)

                # Check for scheduled quarterly trigger
                elif self.should_trigger_collection(symbol, QuarterlyTriggerType.SCHEDULED_QUARTERLY):
                    collection_result = self.trigger_quarterly_collection(
                        symbol, QuarterlyTriggerType.SCHEDULED_QUARTERLY
                    )

                    if collection_result.get("triggered"):
                        results["triggered_collections"] += 1
                        results["symbols_triggered"].append(symbol)

            except Exception as e:
                error_msg = f"{symbol}: {str(e)}"
                results["errors"].append(error_msg)
                self.logger.error(f"Error checking triggers for {symbol}: {e}")

        self.logger.info(f"Quarterly trigger scan completed: {results['triggered_collections']} collections triggered")
        return results

    def get_trigger_status(self) -> dict[str, Any]:
        """Get current trigger status and statistics"""
        return {
            "current_earnings_season": self.get_current_earnings_season(),
            "is_earnings_season": self.is_earnings_season(),
            "trigger_state": self.trigger_state,
            "quarterly_schedule": self.quarterly_schedule,
            "total_completed_collections": len(self.trigger_state["completed_collections"]),
        }


def create_quarterly_trigger_manager(
    base_path: Path | None = None,
) -> QuarterlyCollectionTrigger:
    """Factory function to create quarterly trigger manager"""
    hdm = HistoricalDataManager(base_path=base_path)
    return QuarterlyCollectionTrigger(historical_manager=hdm)


if __name__ == "__main__":
    # Example usage
    trigger_manager = create_quarterly_trigger_manager()

    print("🔔 Quarterly Collection Trigger Manager")
    print("=" * 50)

    # Check current status
    status = trigger_manager.get_trigger_status()
    print("Current earnings season: {status['current_earnings_season']}")
    print("Is earnings season: {status['is_earnings_season']}")
    print("Completed collections: {status['total_completed_collections']}")

    # Scan for triggers
    print("\n🔍 Scanning for quarterly triggers...")
    scan_results = trigger_manager.scan_for_triggers(["AAPL", "MSFT", "GOOGL"])

    print("Symbols scanned: {scan_results['scanned_symbols']}")
    print("Collections triggered: {scan_results['triggered_collections']}")
    if scan_results["symbols_triggered"]:
        print("Symbols triggered: {', '.join(scan_results['symbols_triggered'])}")
    if scan_results["errors"]:
        print("Errors: {len(scan_results['errors'])}")
