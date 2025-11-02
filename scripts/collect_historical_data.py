#!/usr/bin/env python3
"""
Comprehensive Historical Data Collection CLI

Command-line interface for collecting comprehensive historical market data:
- 365 days of daily price data
- 5 years of weekly price data
- Gap detection and filling
- Batch processing with progress tracking
"""

import argparse
import json
import sys
from pathlib import Path


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from utils.historical_data_collector import create_historical_data_collector
from utils.historical_data_manager import HistoricalDataManager


def print_banner():
    """Print application banner"""
    print("🚀 Comprehensive Historical Data Collector")
    print("=" * 60)
    print("Automatically collects:")
    print("  📈 365 days of daily price data")
    print("  📊 5 years of weekly price data")
    print("  🔍 Gap detection and filling")
    print("  ⚡ Rate-limited batch processing")
    print()


def parse_symbol_list(symbols_arg: str) -> list[str]:
    """Parse comma-separated symbol list"""
    return [s.strip().upper() for s in symbols_arg.split(",") if s.strip()]


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Collect comprehensive historical market data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data for default high-value symbols
  python collect_historical_data.py

  # Collect data for specific symbols
  python collect_historical_data.py --symbols AAPL,MSFT,GOOGL

  # Custom timeframes
  python collect_historical_data.py --daily-days 180 --weekly-years 3

  # Use different service
  python collect_historical_data.py --service fmp

  # Show current status
  python collect_historical_data.py --status

  # Quick test with minimal data
  python collect_historical_data.py --symbols AAPL --daily-days 30 --weekly-years 1
        """,
    )

    # Symbol selection
    parser.add_argument(
        "--symbols",
        "-s",
        type=str,
        help="Comma-separated list of symbols (e.g., AAPL,MSFT,GOOGL)",
    )

    # Timeframe options
    parser.add_argument(
        "--daily-days",
        type=int,
        default=365,
        help="Number of days of daily data to collect (default: 365)",
    )

    parser.add_argument(
        "--weekly-years",
        type=int,
        default=5,
        help="Number of years of weekly data to collect (default: 5)",
    )

    # Service selection
    parser.add_argument(
        "--service",
        choices=["yahoo_finance", "fmp", "alpha_vantage"],
        default="yahoo_finance",
        help="Financial service to use (default: yahoo_finance)",
    )

    # Rate limiting
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.5,
        help="Delay between API calls in seconds (default: 0.5)",
    )

    # Status and information
    parser.add_argument("--status", action="store_true", help="Show current collection status and exit")

    parser.add_argument(
        "--list-available",
        action="store_true",
        help="List currently available data and exit",
    )

    # Collection options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force collection even if data appears complete",
    )

    parser.add_argument(
        "--daily-only",
        action="store_true",
        help="Collect only daily data (skip weekly aggregation)",
    )

    parser.add_argument(
        "--weekly-only",
        action="store_true",
        help="Collect only weekly data (skip daily collection)",
    )

    # Output options
    parser.add_argument("--quiet", "-q", action="store_true", help="Reduce output verbosity")

    parser.add_argument("--output-json", type=str, help="Save results to JSON file")

    args = parser.parse_args()

    if not args.quiet:
        print_banner()

    # Create collector
    try:
        collector = create_historical_data_collector(rate_limit_delay=args.rate_limit)
    except Exception:
        print("❌ Failed to initialize collector: {e}")
        return 1

    # Handle status request
    if args.status:
        try:
            status = collector.get_collection_status()
            print("📊 Current Collection Status:")
            print("-" * 40)

            available = status.get("available_data", {})
            print("Total files stored: {available.get('total_files', 0)}")
            print("Symbols tracked: {available.get('symbol_count', 0)}")
            print("Data types: {list(available.get('data_types', {}).keys())}")
            print("Storage location: {status.get('storage_location')}")

            if available.get("symbols"):
                print("\nTracked symbols: {', '.join(available['symbols'][:10])}")
                if len(available["symbols"]) > 10:
                    print("... and {len(available['symbols']) - 10} more")

            collection_state = status.get("collection_state", {})
            if collection_state.get("last_collection"):
                print("\nLast collection: {collection_state['last_collection']}")

            return 0

        except Exception:
            print("❌ Failed to get status: {e}")
            return 1

    # Handle list available request
    if args.list_available:
        try:
            hdm = HistoricalDataManager()
            all_data = hdm.get_available_data()

            print("📁 Available Historical Data:")
            print("-" * 40)

            for symbol in sorted(all_data.get("symbols", [])):
                symbol_data = hdm.get_available_data(symbol)
                data_types = symbol_data.get("data_types", [])
                print("  {symbol}: {', '.join(data_types)}")

            return 0

        except Exception:
            print("❌ Failed to list available data: {e}")
            return 1

    # Parse symbols
    if args.symbols:
        symbols = parse_symbol_list(args.symbols)
        if not symbols:
            print("❌ No valid symbols provided")
            return 1
    else:
        symbols = None  # Will use default symbols

    # Validate conflicting options
    if args.daily_only and args.weekly_only:
        print("❌ Cannot specify both --daily-only and --weekly-only")
        return 1

    if not args.quiet:
        if symbols:
            print("🎯 Target symbols: {', '.join(symbols)}")
        else:
            print("🎯 Using default high-value symbols")

        if not args.weekly_only:
            print("📈 Daily data: {args.daily_days} days")
        if not args.daily_only:
            print("📊 Weekly data: {args.weekly_years} years")
        print("🔧 Service: {args.service}")
        print("⏱️  Rate limit: {args.rate_limit}s between calls")
        print()

    # Start collection
    try:
        if args.daily_only:
            # Daily only
            if not args.quiet:
                print("🔄 Starting daily data collection...")

            results = collector.collect_daily_prices(
                symbols=symbols or collector.get_target_symbols(),
                days=args.daily_days,
                service_name=args.service,
            )

            collection_results = {
                "daily_collection": results,
                "total_files_created": results.get("files_created", 0),
                "overall_success": len(results.get("symbols_successful", [])) > 0,
            }

        elif args.weekly_only:
            # Weekly only
            if not args.quiet:
                print("🔄 Starting weekly data collection...")

            results = collector.collect_weekly_prices(
                symbols=symbols or collector.get_target_symbols(),
                years=args.weekly_years,
                service_name=args.service,
            )

            collection_results = {
                "weekly_collection": results,
                "total_files_created": results.get("files_created", 0),
                "overall_success": len(results.get("symbols_successful", [])) > 0,
            }

        else:
            # Comprehensive collection
            if not args.quiet:
                print("🔄 Starting comprehensive data collection...")

            collection_results = collector.collect_comprehensive_data(
                symbols=symbols,
                daily_days=args.daily_days,
                weekly_years=args.weekly_years,
                service_name=args.service,
            )

        # Display results
        if not args.quiet:
            print("\n" + "=" * 60)
            print("📊 COLLECTION RESULTS")
            print("=" * 60)

            if collection_results.get("overall_success"):
                print("✅ Collection completed successfully!")
            else:
                print("⚠️  Collection completed with issues")

            print(f"📁 Total files created: {collection_results.get('total_files_created', 0)}")

            # Daily results
            if "daily_collection" in collection_results:
                daily = collection_results["daily_collection"]
                print("\n📈 Daily Collection:")
                print("   ✅ Successful: {len(daily.get('symbols_successful', []))}")
                print("   ❌ Failed: {len(daily.get('symbols_failed', []))}")
                if daily.get("errors") and not args.quiet:
                    print("   Errors: {len(daily['errors'])}")

            # Weekly results
            if "weekly_collection" in collection_results:
                weekly = collection_results["weekly_collection"]
                print("\n📊 Weekly Collection:")
                print("   ✅ Successful: {len(weekly.get('symbols_successful', []))}")
                print("   ❌ Failed: {len(weekly.get('symbols_failed', []))}")
                if weekly.get("errors") and not args.quiet:
                    print("   Errors: {len(weekly['errors'])}")

            # Storage location
            print("\n📂 Data stored in: ./data/raw/")
            print("🔍 Use --status to view collection status")
            print("📋 Use --list-available to see all available data")

        # Save JSON output if requested
        if args.output_json:
            try:
                with open(args.output_json, "w") as f:
                    json.dump(collection_results, f, indent=2, default=str)
                if not args.quiet:
                    print("\n💾 Results saved to: {args.output_json}")
            except Exception:
                print("⚠️  Failed to save JSON output: {e}")

        # Return appropriate exit code
        return 0 if collection_results.get("overall_success") else 1

    except KeyboardInterrupt:
        print("\n🛑 Collection interrupted by user")
        return 1
    except Exception:
        print("❌ Collection failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
