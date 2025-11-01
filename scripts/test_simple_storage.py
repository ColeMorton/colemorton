#!/usr/bin/env python3
"""
Simple Historical Storage Test

Direct test of the HistoricalDataManager to verify basic functionality.
"""

import sys
from datetime import datetime
from pathlib import Path


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def test_direct_storage():
    """Test direct storage with HistoricalDataManager"""
    print("🔄 Testing direct HistoricalDataManager storage...")

    try:
        from historical_data_manager import DataType, HistoricalDataManager

        # Create manager
        hdm = HistoricalDataManager()
        print("📁 Base path: {hdm.base_path}")

        # Test stock data
        stock_data = {
            "symbol": "AAPL",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 154.0,
            "volume": 1000000,
        }

        print("📈 Storing AAPL stock data...")
        success = hdm.store_data(
            symbol="AAPL",
            data=stock_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            source="test",
        )
        print("Storage result: {success}")

        # Test different symbol
        stock_data2 = {
            "symbol": "GOOGL",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "open": 2800.0,
            "high": 2850.0,
            "low": 2780.0,
            "close": 2820.0,
            "volume": 800000,
        }

        print("📈 Storing GOOGL stock data...")
        success2 = hdm.store_data(
            symbol="GOOGL",
            data=stock_data2,
            data_type=DataType.STOCK_DAILY_PRICES,
            source="test",
        )
        print("Storage result: {success2}")

        # Test fundamentals
        fundamental_data = {
            "symbol": "MSFT",
            "market_cap": 3000000000000,
            "pe_ratio": 25.5,
            "sector": "Technology",
        }

        print("📊 Storing MSFT fundamental data...")
        success3 = hdm.store_data(
            symbol="MSFT",
            data=fundamental_data,
            data_type=DataType.STOCK_FUNDAMENTALS,
            source="test",
        )
        print("Storage result: {success3}")

        return success and success2 and success3

    except Exception:
        print("❌ Direct storage test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_files():
    """Check what files exist"""
    print("\n📁 Checking files...")

    raw_path = Path("data/raw")

    if not raw_path.exists():
        print("❌ data/raw doesn't exist")
        return []

    # Find all files
    all_files = list(raw_path.rglob("*"))
    json_files = [f for f in all_files if f.suffix == ".json"]

    print("📂 Total items in data/raw: {len(all_files)}")
    print("📄 JSON files: {len(json_files)}")

    # Show directory structure
    for item in sorted(all_files):
        if item.is_file():
            relative_path = item.relative_to(raw_path)
            size = item.stat().st_size
            print("  📄 {relative_path} ({size} bytes)")
        elif item.is_dir() and item != raw_path:
            relative_path = item.relative_to(raw_path)
            print("  📁 {relative_path}/")

    return json_files


def main():
    """Main test"""
    print("🚀 Simple Historical Storage Test")
    print("=" * 50)

    # Test direct storage
    success = test_direct_storage()

    # Check files
    files = check_files()

    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)

    if success:
        print("✅ Direct storage test PASSED")
    else:
        print("❌ Direct storage test FAILED")

    print("📁 Files created: {len(files)}")

    if success and len(files) > 0:
        print("🎉 SUCCESS: Files are being created!")
    else:
        print("❌ ISSUE: No files created despite successful storage")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
