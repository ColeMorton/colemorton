#!/usr/bin/env python3
"""
Generic stock data copy script - supports any ticker symbol
Usage: python copy_stock_data.py SYMBOL
Example: python copy_stock_data.py AAPL
         python copy_stock_data.py MSTR
"""

import argparse
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd


def get_symbol_data_years(symbol: str) -> int:
    """Get the configured data years for a symbol from consolidated config"""
    try:
        project_root = Path(__file__).parent.parent
        config_path = project_root / "frontend/src/config/chart-data-dependencies.json"

        with open(config_path) as f:
            config = json.load(f)

        symbol_config = config.get("symbolMetadata", {}).get(symbol.upper(), {})
        data_years = symbol_config.get("dataYears")

        if data_years is not None:
            print("Found dataYears configuration for {symbol}: {data_years} years")
            return data_years
        print(f"No dataYears configuration found for {symbol}, using default 1 year")
        return 1

    except Exception as e:
        print(f"Error reading chart data dependencies config: {e}, using default 1 year")
        return 1


def filter_data_by_years(df: pd.DataFrame, years: int) -> pd.DataFrame:
    """Filter dataframe to include only the last N years of data"""
    if df.empty or years <= 0:
        return df

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Calculate cutoff date (N years ago from the most recent date)
    latest_date = df["date"].max()
    cutoff_date = latest_date - timedelta(days=years * 365)

    # Filter data
    filtered_df = df[df["date"] >= cutoff_date].copy()

    # Convert date back to string format
    filtered_df["date"] = filtered_df["date"].dt.strftime("%Y-%m-%d")

    print("Filtered data from {len(df)} to {len(filtered_df)} rows ({years} years)")
    return filtered_df


def fetch_and_copy_stock_data(symbol: str) -> bool:
    """Fetch stock data for any symbol and copy to frontend directory with period filtering"""

    # Get the configured data years for this symbol
    data_years = get_symbol_data_years(symbol)

    # Define paths dynamically based on symbol
    project_root = Path(__file__).parent.parent
    frontend_csv_path = project_root / f"frontend/public/data/raw/stocks/{symbol}/daily.csv"

    # Check if data already exists in data directory (from pipeline)
    scripts_csv_path = project_root / f"data/raw/stocks/{symbol}/daily.csv"

    try:
        if scripts_csv_path.exists():
            print("Found existing processed data for {symbol}")
            # Read the existing processed data
            df = pd.read_csv(scripts_csv_path)
            print("Found existing processed data with {len(df)} rows")
        else:
            print("Fetching 1 year of {symbol} data...")
            # Use Yahoo Finance CLI to get 1 year of data for the specified symbol
            result = subprocess.run(
                [
                    sys.executable,
                    "yahoo_finance_cli.py",
                    "history",
                    symbol,
                    "--period",
                    "1y",
                    "--env",
                    "dev",
                    "--output-format",
                    "json",
                ],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("Error fetching {symbol} data: {result.stderr}")
                return False

            if not scripts_csv_path.exists():
                print("No {symbol} data found at {scripts_csv_path} after fetch")
                return False

            # Read the newly fetched data
            df = pd.read_csv(scripts_csv_path)
            print("Retrieved {len(df)} rows of data")

        # Ensure we have date column in the right format
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Sort by date to ensure chronological order
        df = df.sort_values("date")

        # Apply period filtering based on symbol configuration
        df = filter_data_by_years(df, data_years)

        # Ensure frontend directory exists
        frontend_csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to CSV
        df.to_csv(frontend_csv_path, index=False)

        print(f"Successfully copied {len(df)} rows of {symbol} data to {frontend_csv_path}")
        return True

    except Exception:
        print("Error processing {symbol} data: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Copy stock data for any symbol to frontend")
    parser.add_argument("symbol", help="Stock symbol (e.g., AAPL, MSTR, TSLA)")

    args = parser.parse_args()
    symbol = args.symbol.upper()  # Ensure uppercase

    print("Starting data copy process for symbol: {symbol}")

    success = fetch_and_copy_stock_data(symbol)

    if success:
        print("✅ Successfully completed data copy for {symbol}")
    else:
        print("❌ Failed to copy data for {symbol}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
