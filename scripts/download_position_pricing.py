#!/usr/bin/env python3
"""
Position Pricing Data Download Script

Downloads Yahoo Finance price data for open positions in trading portfolios
and generates consolidated PnL time series data for frontend consumption.

This script follows the established data pipeline pattern:
Backend Python → Raw Data Storage → Frontend Copy

Usage:
    python download_position_pricing.py --portfolio live_signals
    python download_position_pricing.py --portfolio live_signals --start-date 2025-01-01
"""

import argparse
import csv
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# Add scripts directory to path for importing services
sys.path.append(str(Path(__file__).parent))
from yahoo_finance_service import YahooFinanceService


class PositionPricingDownloader:
    """Downloads pricing data for open trading positions"""

    def __init__(self, portfolio_name: str, base_data_path: str | None = None):
        self.portfolio_name = portfolio_name
        self.base_data_path = Path(base_data_path) if base_data_path else Path(__file__).parent.parent / "data"

        # Initialize Yahoo Finance service
        self.yahoo_service = YahooFinanceService()

        # Setup paths
        self.trade_history_path = self.base_data_path / "raw" / "trade_history" / f"{portfolio_name}.csv"
        self.pricing_output_path = self.base_data_path / "raw" / "financial_data" / "pricing" / portfolio_name
        self.consolidated_output_path = (
            self.base_data_path / "raw" / "financial_data" / "pricing" / f"{portfolio_name}_open_positions_pnl.csv"
        )

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging for the script"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(f"download_position_pricing_{self.portfolio_name}.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def parse_open_positions(self) -> list[dict]:
        """Extract open positions from trade history CSV"""
        self.logger.info(f"Parsing open positions from {self.trade_history_path}")

        if not self.trade_history_path.exists():
            raise FileNotFoundError(f"Trade history file not found: {self.trade_history_path}")

        open_positions = []

        with open(self.trade_history_path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Status", "").strip() == "Open":
                    try:
                        position = {
                            "ticker": row["Ticker"].strip(),
                            "entry_date": datetime.strptime(row["Entry_Timestamp"].strip(), "%Y-%m-%d %H:%M:%S").date(),
                            "entry_price": float(row["Avg_Entry_Price"].strip()),
                            "position_size": float(row["Position_Size"].strip()),
                            "direction": row["Direction"].strip(),  # Long/Short
                            "position_uuid": row["Position_UUID"].strip(),
                        }
                        open_positions.append(position)
                        self.logger.info(
                            f"Found open position: {position['ticker']} entered on {position['entry_date']}"
                        )
                    except (ValueError, KeyError) as e:
                        self.logger.error(f"Error parsing position row: {row}. Error: {e}")
                        continue

        self.logger.info(f"Found {len(open_positions)} open positions")
        return open_positions

    def download_ticker_prices(
        self, ticker: str, start_date: datetime, end_date: datetime | None = None
    ) -> pd.DataFrame:
        """Download daily price data for a specific ticker using direct yfinance"""
        if end_date is None:
            end_date = datetime.now()

        self.logger.info(f"Downloading price data for {ticker} from {start_date} to {end_date}")

        try:
            # Import yfinance directly since the service doesn't support date ranges
            import yfinance as yf

            # Create ticker object and get historical data with date range
            ticker_obj = yf.Ticker(ticker)
            price_data = ticker_obj.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),  # Add 1 day to include end_date
            )

            if price_data is None or price_data.empty:
                self.logger.warning(f"No price data available for {ticker}")
                return pd.DataFrame()

            # Ensure we have the required columns
            required_columns = ["Open", "High", "Low", "Close", "Volume"]
            for col in required_columns:
                if col not in price_data.columns:
                    self.logger.error(f"Missing required column {col} for {ticker}")
                    return pd.DataFrame()

            # Reset index to make Date a column
            if price_data.index.name == "Date":
                price_data.reset_index(inplace=True)
            elif "Date" not in price_data.columns:
                price_data["Date"] = price_data.index
                price_data.reset_index(drop=True, inplace=True)

            self.logger.info(f"Downloaded {len(price_data)} price records for {ticker}")
            return price_data

        except Exception as e:
            self.logger.error(f"Failed to download price data for {ticker}: {e}")
            return pd.DataFrame()

    def save_individual_price_file(self, ticker: str, price_data: pd.DataFrame) -> None:
        """Save individual ticker price data to CSV"""
        if price_data.empty:
            self.logger.warning(f"No data to save for {ticker}")
            return

        # Create output directory if it doesn't exist
        self.pricing_output_path.mkdir(parents=True, exist_ok=True)

        output_file = self.pricing_output_path / f"{ticker}_daily_prices.csv"

        # Select and order columns
        columns_to_save = ["Date", "Open", "High", "Low", "Close", "Volume"]
        price_data_clean = price_data[columns_to_save].copy()

        # Ensure Date is properly formatted
        if price_data_clean["Date"].dtype == "object":
            price_data_clean["Date"] = pd.to_datetime(price_data_clean["Date"]).dt.date

        price_data_clean.to_csv(output_file, index=False)
        self.logger.info(f"Saved {len(price_data_clean)} price records to {output_file}")

    def calculate_position_pnl_timeseries(self, positions: list[dict]) -> pd.DataFrame:
        """Generate consolidated PnL time series for all open positions"""
        self.logger.info("Calculating PnL time series for all open positions")

        all_pnl_data = []

        for position in positions:
            ticker = position["ticker"]
            entry_date = position["entry_date"]
            entry_price = position["entry_price"]
            position_size = position["position_size"]
            direction_multiplier = 1 if position["direction"] == "Long" else -1

            # Download price data for this position
            price_data = self.download_ticker_prices(ticker, entry_date)

            if price_data.empty:
                self.logger.warning(f"Skipping PnL calculation for {ticker} due to missing price data")
                continue

            # Save individual price file
            self.save_individual_price_file(ticker, price_data)

            # Calculate daily PnL
            for _, row in price_data.iterrows():
                date = row["Date"]
                if pd.isna(date):
                    continue

                # Convert pandas Timestamp to date object
                if hasattr(date, "date") and callable(date.date):
                    # It's a datetime-like object (Timestamp) with a date() method
                    date = date.date()
                elif isinstance(date, str):
                    # Convert string to date
                    date = pd.to_datetime(date)
                # If it's already a date object, keep it as is

                close_price = float(row["Close"])

                # Calculate PnL: (Current Price - Entry Price) * Position Size * Direction
                pnl = (close_price - entry_price) * position_size * direction_multiplier

                pnl_record = {
                    "Date": date,
                    "Ticker": ticker,
                    "Price": close_price,
                    "PnL": pnl,
                    "Position_Size": position_size,
                    "Entry_Date": entry_date,
                    "Entry_Price": entry_price,
                    "Direction": position["direction"],
                    "Position_UUID": position["position_uuid"],
                }

                all_pnl_data.append(pnl_record)

        if not all_pnl_data:
            self.logger.warning("No PnL data generated")
            return pd.DataFrame()

        # Convert to DataFrame and sort by date
        pnl_df = pd.DataFrame(all_pnl_data)
        pnl_df = pnl_df.sort_values(["Date", "Ticker"])

        self.logger.info(f"Generated {len(pnl_df)} PnL records across {len(positions)} positions")
        return pnl_df

    def save_consolidated_pnl_file(self, pnl_data: pd.DataFrame) -> None:
        """Save consolidated PnL time series to CSV"""
        if pnl_data.empty:
            self.logger.warning("No PnL data to save")
            return

        # Create output directory if it doesn't exist
        self.consolidated_output_path.parent.mkdir(parents=True, exist_ok=True)

        pnl_data.to_csv(self.consolidated_output_path, index=False)
        self.logger.info(f"Saved consolidated PnL data to {self.consolidated_output_path}")

        # Log summary statistics
        unique_tickers = pnl_data["Ticker"].nunique()
        date_range = f"{pnl_data['Date'].min()} to {pnl_data['Date'].max()}"
        total_records = len(pnl_data)

        self.logger.info(f"Summary: {unique_tickers} tickers, {total_records} records, date range: {date_range}")

    def run(self, start_date: str | None = None) -> None:
        """Execute the full pricing data download and processing pipeline"""
        self.logger.info(f"Starting position pricing download for portfolio: {self.portfolio_name}")

        try:
            # Parse open positions from trade history
            open_positions = self.parse_open_positions()

            if not open_positions:
                self.logger.warning("No open positions found. Exiting.")
                return

            # Override start date if provided
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                for position in open_positions:
                    if position["entry_date"] > start_date_obj:
                        position["entry_date"] = start_date_obj
                self.logger.info(f"Override start date set to {start_date}")

            # Calculate PnL time series for all positions
            pnl_data = self.calculate_position_pnl_timeseries(open_positions)

            if pnl_data.empty:
                self.logger.error("Failed to generate PnL time series data")
                return

            # Save consolidated PnL file
            self.save_consolidated_pnl_file(pnl_data)

            self.logger.info("Position pricing download completed successfully")

        except Exception as e:
            self.logger.error(f"Error in position pricing download: {e}")
            raise


def main():
    """Command-line interface for the position pricing downloader"""
    parser = argparse.ArgumentParser(description="Download pricing data for open trading positions")
    parser.add_argument("--portfolio", required=True, help="Portfolio name (e.g., live_signals)")
    parser.add_argument("--start-date", help="Override start date for price data download (YYYY-MM-DD)")
    parser.add_argument(
        "--data-path",
        help="Base path to data directory (default: ../data relative to script)",
    )

    args = parser.parse_args()

    try:
        downloader = PositionPricingDownloader(portfolio_name=args.portfolio, base_data_path=args.data_path)
        downloader.run(start_date=args.start_date)

    except Exception as e:
        logging.error(f"Script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
