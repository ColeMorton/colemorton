#!/usr/bin/env python3
"""
Test CLI Historical Storage

Direct test of the historical data storage system using the integrated services.
This demonstrates file creation in ./data/raw/ through API calls.
"""

import sys
from pathlib import Path


# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "services"))
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def test_yahoo_finance_storage():
    """Test Yahoo Finance service with historical storage"""
    print("🔄 Testing Yahoo Finance with historical storage...")

    try:
        from services.yahoo_finance import create_yahoo_finance_service

        # Create service with historical storage enabled
        service = create_yahoo_finance_service(env="dev")

        print(f"📊 Service info: {service.get_service_info()['historical_storage']['enabled']}")

        # Get stock data - this should trigger historical storage
        print("📈 Getting AAPL stock data...")
        aapl_data = service.get_stock_info("AAPL")
        print("✅ AAPL data retrieved: {aapl_data['symbol']}")

        # Get another stock
        print("📈 Getting GOOGL stock data...")
        googl_data = service.get_stock_info("GOOGL")
        print("✅ GOOGL data retrieved: {googl_data['symbol']}")

        # Get historical data
        print("📈 Getting MSFT historical data...")
        msft_historical = service.get_historical_data("MSFT", "1mo")
        print(f"✅ MSFT historical data retrieved: {len(msft_historical.get('data', []))} records")

        return True

    except Exception:
        print("❌ Yahoo Finance test failed: {e}")
        return False


def test_fmp_storage():
    """Test FMP service with historical storage"""
    print("\n🔄 Testing FMP with historical storage...")

    try:
        from services.fmp import create_fmp_service

        # Create service
        service = create_fmp_service(env="dev")

        print(f"📊 Service info: {service.get_service_info()['historical_storage']['enabled']}")

        # Get stock quote - this should trigger historical storage
        print("📈 Getting TSLA quote...")
        tsla_data = service.get_stock_quote("TSLA")
        print("✅ TSLA quote retrieved: {len(tsla_data)} records")

        # Get company profile
        print("📈 Getting NVDA profile...")
        nvda_profile = service.get_company_profile("NVDA")
        print("✅ NVDA profile retrieved: {len(nvda_profile)} records")

        return True

    except Exception:
        print("❌ FMP test failed: {e}")
        return False


def test_alpha_vantage_storage():
    """Test Alpha Vantage service with historical storage"""
    print("\n🔄 Testing Alpha Vantage with historical storage...")

    try:
        from services.alpha_vantage import create_alpha_vantage_service

        # Create service
        service = create_alpha_vantage_service(env="dev")

        print(f"📊 Service info: {service.get_service_info()['historical_storage']['enabled']}")

        # Get stock quote - this should trigger historical storage
        print("📈 Getting META quote...")
        meta_data = service.get_stock_quote("META")
        print("✅ META quote retrieved: {meta_data.get('symbol', 'unknown')}")

        return True

    except Exception:
        print("❌ Alpha Vantage test failed: {e}")
        return False


def check_created_files():
    """Check what files were created in data/raw"""
    print("\n📁 Checking created files in ./data/raw/...")

    raw_path = Path("data/raw")

    if not raw_path.exists():
        print("❌ data/raw directory doesn't exist")
        return []

    # Find all JSON files
    json_files = list(raw_path.rglob("*.json"))

    if not json_files:
        print("📝 No JSON files found in data/raw")
        return []

    print("📝 Found {len(json_files)} files:")
    for file_path in sorted(json_files):
        relative_path = file_path.relative_to(raw_path)
        file_size = file_path.stat().st_size
        print("  📄 {relative_path} ({file_size} bytes)")

        # Show a snippet of the file content
        try:
            with open(file_path) as f:
                import json

                data = json.load(f)
                symbol = data.get("symbol", "unknown")
                data_type = data.get("data_type", "unknown")
                print("      Symbol: {symbol}, Type: {data_type}")
        except Exception:
            print("      (Could not read file: {e})")

    return json_files


def test_metadata_file():
    """Check if metadata.json was created"""
    print("\n📊 Checking metadata file...")

    metadata_path = Path("data/raw/metadata.json")

    if metadata_path.exists():
        try:
            with open(metadata_path) as f:
                import json

                metadata = json.load(f)

            print("✅ Metadata file found:")
            print("  📈 Total files: {metadata.get('total_files', 0)}")
            print("  📊 Data types: {list(metadata.get('data_types', {}).keys())}")
            print("  🏢 Symbols: {len(metadata.get('symbols', {}))}")

            # Show symbols
            symbols = list(metadata.get("symbols", {}).keys())
            if symbols:
                print("  📋 Symbol list: {', '.join(symbols[:10])}")

        except Exception:
            print("❌ Could not read metadata: {e}")
    else:
        print("📝 No metadata file found")


def main():
    """Main test execution"""
    print("🚀 Testing Historical Data Storage via CLI Services")
    print("=" * 60)

    # Test all services
    results = []
    results.append(("Yahoo Finance", test_yahoo_finance_storage()))
    results.append(("FMP", test_fmp_storage()))
    results.append(("Alpha Vantage", test_alpha_vantage_storage()))

    # Check created files
    created_files = check_created_files()

    # Check metadata
    test_metadata_file()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    for service_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print("{status} {service_name}")

    print("\n📁 Files created: {len(created_files)}")

    # Overall result
    successful_tests = sum(result[1] for result in results)
    total_tests = len(results)

    if successful_tests > 0 and len(created_files) > 0:
        print("🎉 SUCCESS: Historical data storage is working!")
        print("📈 {successful_tests}/{total_tests} services succeeded")
        print("📁 {len(created_files)} files created in ./data/raw/")
    else:
        print("❌ FAILED: No files were created")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
