#!/usr/bin/env python3
"""
Test Integrated CLI Services

Test the CLI services with the integrated historical storage.
"""

import sys
from pathlib import Path


# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "services"))
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def test_cli_with_real_api():
    """Test CLI services with real API calls to trigger storage"""
    print("🚀 Testing CLI Services with Real API Calls")
    print("=" * 60)

    # Count existing files
    raw_path = Path("data/raw")
    initial_files = len(list(raw_path.rglob("*.json"))) if raw_path.exists() else 0
    print("📁 Initial files in data/raw: {initial_files}")

    try:
        from services.yahoo_finance import create_yahoo_finance_service

        # Create Yahoo Finance service
        yf_service = create_yahoo_finance_service(env="dev")
        print("✅ Yahoo Finance service created")

        # Test with different symbols to avoid cache hits
        test_symbols = ["AMZN", "NFLX", "SHOP"]

        for symbol in test_symbols:
            print("\n📈 Getting data for {symbol}...")

            # Get stock info (should trigger historical storage)
            try:
                stock_data = yf_service.get_stock_info(symbol)
                print("  ✅ Stock info retrieved for {symbol}")
                print("  📊 Current price: ${stock_data.get('current_price', 'N/A')}")

                # Small delay to ensure different timestamps
                import time

                time.sleep(0.1)

            except Exception:
                print("  ❌ Failed to get {symbol}: {e}")

        # Test FMP service
        print("\n🔄 Testing FMP service...")
        try:
            from services.fmp import create_fmp_service

            fmp_service = create_fmp_service(env="dev")
            print("✅ FMP service created")

            # Test with a symbol
            fmp_data = fmp_service.get_stock_quote("CRM")
            print("  ✅ FMP quote retrieved for CRM: {len(fmp_data)} records")

        except Exception:
            print("  ❌ FMP test failed: {e}")

        # Count final files
        final_files = len(list(raw_path.rglob("*.json"))) if raw_path.exists() else 0
        new_files = final_files - initial_files

        print("\n📊 Results:")
        print("  📁 Initial files: {initial_files}")
        print("  📁 Final files: {final_files}")
        print("  📈 New files created: {new_files}")

        # Show new files
        if new_files > 0:
            print("\n📄 New files created:")
            all_files = sorted(list(raw_path.rglob("*.json")))
            for file_path in all_files[-new_files:]:  # Show last N files
                relative_path = file_path.relative_to(raw_path)
                size = file_path.stat().st_size
                print("  📄 {relative_path} ({size} bytes)")

        return new_files > 0

    except Exception:
        print("❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def show_directory_structure():
    """Show the complete directory structure"""
    print("\n📁 Complete data/raw structure:")

    raw_path = Path("data/raw")
    if not raw_path.exists():
        print("  ❌ data/raw doesn't exist")
        return

    def print_tree(path, prefix=""):
        """Print directory tree"""
        items = sorted(list(path.iterdir()))
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "

            if item.is_dir():
                print("{prefix}{current_prefix}📁 {item.name}/")
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix)
            else:
                size = item.stat().st_size
                print("{prefix}{current_prefix}📄 {item.name} ({size} bytes)")

    print_tree(raw_path)


def main():
    """Main test"""
    success = test_cli_with_real_api()

    show_directory_structure()

    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: CLI services are creating historical data files!")
    else:
        print("❌ No new files were created by CLI services")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
