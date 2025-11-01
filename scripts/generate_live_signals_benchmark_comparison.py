#!/usr/bin/env python3
"""
Generate Live Signals Benchmark Comparison Data

This script:
1. Reads live signals trades from the CSV file
2. Calculates daily portfolio equity curve from trades
3. Reads benchmark data for SPY, QQQ, BTC-USD
4. Normalizes all series to start at 0% on 2025-04-01
5. Outputs a CSV with cumulative returns for comparison
"""

import logging
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
LIVE_SIGNALS_PATH = PROJECT_ROOT / "frontend/public/data/trade-history/live_signals.csv"
BENCHMARK_DATA_PATH = PROJECT_ROOT / "data/raw/stocks"
OUTPUT_PATH = PROJECT_ROOT / "frontend/public/data/portfolio/live_signals_benchmark_comparison.csv"

# Constants
START_DATE = "2025-04-01"
BENCHMARKS = ["SPY", "QQQ", "BTC-USD"]
INITIAL_CAPITAL = 10000  # Assumed starting capital for percentage calculations


def load_live_signals_data():
    """Load and parse live signals trade data"""
    logger.info(f"Loading live signals data from {LIVE_SIGNALS_PATH}")

    try:
        df = pd.read_csv(LIVE_SIGNALS_PATH)

        # Convert timestamps
        df["Entry_Timestamp"] = pd.to_datetime(df["Entry_Timestamp"])
        df["Exit_Timestamp"] = pd.to_datetime(df["Exit_Timestamp"])

        # Filter closed trades only
        closed_trades = df[df["Status"] == "Closed"].copy()

        logger.info(f"Loaded {len(closed_trades)} closed trades")
        return closed_trades

    except Exception as e:
        logger.error(f"Error loading live signals data: {e}")
        raise


def load_benchmark_data(ticker):
    """Load benchmark price data for a given ticker"""
    file_path = BENCHMARK_DATA_PATH / ticker / "daily.csv"

    try:
        logger.info(f"Loading benchmark data for {ticker} from {file_path}")

        df = pd.read_csv(file_path)
        # Handle mixed date formats
        df["date"] = pd.to_datetime(df["date"], format="mixed")
        df = df.set_index("date")

        # Filter from start date
        df = df[df.index >= START_DATE]

        logger.info(f"Loaded {len(df)} days of data for {ticker}")
        return df["close"]

    except Exception as e:
        logger.error(f"Error loading benchmark data for {ticker}: {e}")
        raise


def calculate_portfolio_equity_curve(trades_df):
    """Calculate daily portfolio equity curve from trades"""
    logger.info("Calculating portfolio equity curve")

    # Get date range
    min_date = pd.Timestamp(START_DATE)
    max_date = trades_df["Exit_Timestamp"].max()

    # Create daily date index
    date_range = pd.date_range(start=min_date, end=max_date, freq="D")

    # Initialize equity curve
    equity_curve = pd.Series(index=date_range, dtype=float)
    equity_curve.iloc[0] = 0.0  # Start at 0 P&L

    # Calculate daily P&L
    for date in date_range:
        daily_pnl = 0.0

        # Add P&L from trades that closed on this date
        closed_today = trades_df[trades_df["Exit_Timestamp"].dt.date == date.date()]
        if not closed_today.empty:
            daily_pnl += closed_today["PnL"].sum()

        # Set cumulative P&L
        if date == date_range[0]:
            equity_curve[date] = daily_pnl
        else:
            prev_date = date - timedelta(days=1)
            while prev_date not in equity_curve.index and prev_date >= min_date:
                prev_date -= timedelta(days=1)

            if prev_date in equity_curve.index:
                equity_curve[date] = equity_curve[prev_date] + daily_pnl
            else:
                equity_curve[date] = daily_pnl

    # Forward fill for missing dates (weekends, holidays)
    equity_curve = equity_curve.ffill()

    # Convert to percentage returns
    portfolio_returns = (equity_curve / INITIAL_CAPITAL) * 100

    logger.info(f"Portfolio equity curve calculated with final return: {portfolio_returns.iloc[-1]:.2f}%")
    return portfolio_returns


def calculate_benchmark_returns(prices, start_date):
    """Calculate cumulative returns for benchmark prices"""
    # Filter from start date
    prices = prices[prices.index >= start_date]

    if prices.empty:
        raise ValueError(f"No benchmark data available from {start_date}")

    # Calculate cumulative returns
    start_price = prices.iloc[0]
    returns = ((prices / start_price) - 1) * 100

    return returns


def align_data(portfolio_returns, benchmark_data):
    """Align all data to common dates"""
    logger.info("Aligning data to common dates")

    # Get common date range
    all_dates = portfolio_returns.index

    # Create aligned dataframe
    aligned_df = pd.DataFrame(index=all_dates)
    aligned_df["Portfolio"] = portfolio_returns

    # Add benchmark data
    for ticker, data in benchmark_data.items():
        # Reindex to match portfolio dates and forward fill
        aligned_data = data.reindex(all_dates).ffill()
        aligned_df[ticker] = aligned_data

    # Drop any rows with NaN values
    initial_len = len(aligned_df)
    aligned_df = aligned_df.dropna()

    if len(aligned_df) < initial_len:
        logger.warning(f"Dropped {initial_len - len(aligned_df)} rows with missing data")

    return aligned_df


def main():
    """Main execution function"""
    logger.info("Starting benchmark comparison generation")

    try:
        # Load live signals data
        trades_df = load_live_signals_data()

        # Calculate portfolio equity curve
        portfolio_returns = calculate_portfolio_equity_curve(trades_df)

        # Load and calculate benchmark returns
        benchmark_data = {}
        for ticker in BENCHMARKS:
            try:
                prices = load_benchmark_data(ticker)
                returns = calculate_benchmark_returns(prices, START_DATE)
                benchmark_data[ticker] = returns
            except Exception as e:
                logger.error(f"Failed to process benchmark {ticker}: {e}")
                # Continue with other benchmarks

        # Align all data
        aligned_df = align_data(portfolio_returns, benchmark_data)

        # Reset index to have Date as a column
        aligned_df = aligned_df.reset_index()
        aligned_df = aligned_df.rename(columns={"index": "Date"})

        # Format date column
        aligned_df["Date"] = aligned_df["Date"].dt.strftime("%Y-%m-%d")

        # Round all numeric columns to 4 decimal places
        numeric_columns = aligned_df.select_dtypes(include=[np.number]).columns
        aligned_df[numeric_columns] = aligned_df[numeric_columns].round(4)

        # Save to CSV
        output_dir = OUTPUT_PATH.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        aligned_df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"Saved benchmark comparison data to {OUTPUT_PATH}")

        # Print summary
        logger.info("\nSummary:")
        logger.info(f"Date range: {aligned_df['Date'].iloc[0]} to {aligned_df['Date'].iloc[-1]}")
        logger.info(f"Number of days: {len(aligned_df)}")
        logger.info("\nFinal cumulative returns:")
        for col in aligned_df.columns[1:]:  # Skip Date column
            logger.info(f"  {col}: {aligned_df[col].iloc[-1]:.2f}%")

        return aligned_df

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
