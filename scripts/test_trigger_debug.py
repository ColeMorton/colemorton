#!/usr/bin/env python3
"""
Test Trigger Debug

Simple test to see if the collection trigger is being called at all.
"""

import logging
import sys
from pathlib import Path


# Set up detailed logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def test_trigger_call():
    """Test if the collection trigger method is being called"""
    print("🔍 Testing Collection Trigger Call")
    print("=" * 50)

    try:
        from services.yahoo_finance import create_yahoo_finance_service

        service = create_yahoo_finance_service()

        # Enable INFO logging for the service
        service.logger.setLevel(logging.INFO)

        print("📈 Making API call with INFO logging...")
        result = service.get_stock_info("NVDA")

        if result:
            print("   ✅ API call successful: {result.get('symbol', 'N/A')}")
            print("   🔍 Check the logs above for collection trigger messages")
        else:
            print("   ❌ API call failed")

        return True

    except Exception:
        print("❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_trigger_call()
