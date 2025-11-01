#!/usr/bin/env python3
"""
Direct Auto-Collection Test

Simple test to directly verify that a single API call triggers
comprehensive data collection as required.
"""

import sys
import time
from pathlib import Path


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def count_data_files():
    """Count files in data/raw directory"""
    data_path = Path("data/raw")
    if not data_path.exists():
        return 0

    files = list(data_path.rglob("*.json"))
    return len(files)


def test_single_api_call_triggers_collection():
    """Test that a single API call triggers comprehensive collection"""
    print("🧪 Direct Auto-Collection Test")
    print("=" * 50)

    # Count files before
    files_before = count_data_files()
    print("📁 Files before: {files_before}")

    try:
        from services.yahoo_finance import create_yahoo_finance_service

        service = create_yahoo_finance_service()

        print("📈 Making single API call for TSLA...")
        result = service.get_stock_info("TSLA")

        if result:
            print("   ✅ API successful: {result.get('symbol', 'N/A')}")

            # Wait for background collection (longer wait)
            print("   ⏳ Waiting 15 seconds for background collection...")
            time.sleep(15)

            # Count files after
            files_after = count_data_files()
            print("📁 Files after: {files_after}")

            new_files = files_after - files_before
            print("📈 New files created: {new_files}")

            if new_files > 0:
                print("🎉 SUCCESS: Auto-collection created new files!")

                # Show what was created
                data_path = Path("data/raw")
                recent_files = []
                for file_path in data_path.rglob("*.json"):
                    if file_path.stat().st_mtime > time.time() - 20:  # Modified in last 20 seconds
                        recent_files.append(file_path)

                if recent_files:
                    print("📄 Recent files created:")
                    for file_path in recent_files[:5]:  # Show first 5
                        rel_path = file_path.relative_to(data_path)
                        size = file_path.stat().st_size
                        print("   • {rel_path} ({size} bytes)")

                    if len(recent_files) > 5:
                        print("   • ... and {len(recent_files) - 5} more")

                return True
            print("⚠️  No new files created - collection may still be running")
            return False
        print("❌ API call failed")
        return False

    except Exception:
        print("❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_api_call_triggers_collection()

    if success:
        print("\n✅ DIRECT TEST PASSED")
        print("Auto-collection is working - single API calls trigger comprehensive data collection!")
    else:
        print("\n⚠️  Test needs investigation")
        print("Auto-collection may need debugging or more time to complete")

    sys.exit(0 if success else 1)
