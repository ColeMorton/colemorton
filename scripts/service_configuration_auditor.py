#!/usr/bin/env python3
"""
Service Configuration Auditor

Comprehensive audit of financial service configurations to verify:
- Historical storage is properly enabled
- Configuration loading works correctly
- Services are properly initialized
- Integration with HistoricalDataManager works
"""

import sys
from pathlib import Path
from typing import Any


# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "services"))
sys.path.insert(0, str(Path(__file__).parent / "utils"))


def audit_service_config(service_name: str, create_function_name: str) -> dict[str, Any]:
    """
    Audit a specific service configuration

    Args:
        service_name: Name of the service to audit
        create_function_name: Name of the create function

    Returns:
        Audit results dictionary
    """
    results = {
        "service_name": service_name,
        "config_loaded": False,
        "service_created": False,
        "historical_storage_enabled": False,
        "historical_manager_initialized": False,
        "cache_type": "unknown",
        "configuration_details": {},
        "errors": [],
    }

    try:
        # Import the service module
        if service_name == "yahoo_finance":
            from services.yahoo_finance import create_yahoo_finance_service

            create_function = create_yahoo_finance_service
        elif service_name == "fmp":
            from services.fmp import create_fmp_service

            create_function = create_fmp_service
        elif service_name == "alpha_vantage":
            from services.alpha_vantage import create_alpha_vantage_service

            create_function = create_alpha_vantage_service
        else:
            results["errors"].append(f"Unknown service: {service_name}")
            return results

        results["config_loaded"] = True

        # Create service instance
        service = create_function(env="dev")
        results["service_created"] = True

        # Check service configuration
        service_info = service.get_service_info()
        results["configuration_details"] = service_info

        # Check historical storage
        historical_config = service_info.get("historical_storage", {})
        results["historical_storage_enabled"] = historical_config.get("enabled", False)

        # Check if historical manager is initialized
        results["historical_manager_initialized"] = (
            hasattr(service, "historical_manager") and service.historical_manager is not None
        )

        # Check cache type
        if hasattr(service, "cache"):
            cache_type = type(service.cache).__name__
            results["cache_type"] = cache_type

        print("✅ {service_name}: Configuration audit completed successfully")

    except Exception as e:
        error_msg = f"Error auditing {service_name}: {str(e)}"
        results["errors"].append(error_msg)
        print("❌ {service_name}: {error_msg}")

    return results


def test_historical_data_manager_directly():
    """Test HistoricalDataManager directly"""
    print("\n🔄 Testing HistoricalDataManager directly...")

    try:
        from utils.historical_data_manager import DataType, HistoricalDataManager

        # Create instance
        hdm = HistoricalDataManager()
        print("✅ HistoricalDataManager created successfully")

        # Test basic functionality with sample data
        sample_data = {
            "symbol": "TEST",
            "data": [
                {
                    "Date": "2025-07-28",
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 95.0,
                    "Close": 102.0,
                    "Volume": 1000000,
                    "Adj Close": 102.0,
                }
            ],
        }

        # Test storage
        success = hdm.store_data(
            symbol="TEST",
            data=sample_data,
            data_type=DataType.STOCK_DAILY_PRICES,
            source="configuration_test",
        )

        if success:
            print("✅ Test data stored successfully")

            # Check if files were created
            data_path = Path("data/raw")
            csv_files = list(data_path.rglob("*.csv"))
            meta_files = list(data_path.rglob("*.meta.json"))

            print("📄 CSV files found: {len(csv_files)}")
            print("📄 Metadata files found: {len(meta_files)}")

            if csv_files:
                print("   Latest CSV: {csv_files[-1]}")
            if meta_files:
                print("   Latest Meta: {meta_files[-1]}")

        else:
            print("❌ Test data storage failed")

        return success

    except Exception:
        print("❌ HistoricalDataManager test failed: {e}")
        return False


def test_unified_cache_integration():
    """Test UnifiedCache integration"""
    print("\n🔄 Testing UnifiedCache integration...")

    try:
        from utils.historical_data_manager import HistoricalDataManager
        from utils.unified_cache import UnifiedCache

        # Create components
        hdm = HistoricalDataManager()
        cache = UnifiedCache(historical_manager=hdm, ttl_seconds=300, service_name="test")

        print("✅ UnifiedCache created successfully")

        # Test cache operations with proper parameters for UnifiedCache
        test_key = "test_key"
        test_data = {
            "symbol": "TEST_CACHE",
            "current_price": 100.0,
            "timestamp": "2025-07-28",
        }
        test_endpoint = "stock_info_TEST_CACHE"
        test_params = {"symbol": "TEST_CACHE"}

        # Store data with endpoint and params (required for UnifiedCache)
        cache.set(test_key, test_data, endpoint=test_endpoint, params=test_params)
        print("✅ Data stored in cache")

        # Retrieve data
        retrieved_data = cache.get(test_key)
        if retrieved_data:
            print("✅ Data retrieved from cache")
        else:
            print("❌ Data not found in cache")

        return retrieved_data is not None

    except Exception:
        print("❌ UnifiedCache test failed: {e}")
        return False


def main():
    """Main audit function"""
    print("🔍 Financial Services Configuration Audit")
    print("=" * 60)

    # Services to audit
    services_to_test = [
        ("yahoo_finance", "create_yahoo_finance_service"),
        ("fmp", "create_fmp_service"),
        ("alpha_vantage", "create_alpha_vantage_service"),
    ]

    audit_results = []

    # Audit each service
    for service_name, create_function in services_to_test:
        print("\n🔄 Auditing {service_name}...")
        result = audit_service_config(service_name, create_function)
        audit_results.append(result)

    # Test core components
    hdm_success = test_historical_data_manager_directly()
    cache_success = test_unified_cache_integration()

    # Summary
    print("\n📊 AUDIT SUMMARY")
    print("=" * 60)

    successful_services = []
    failed_services = []

    for result in audit_results:
        service_name = result["service_name"]

        if (
            result["service_created"]
            and result["historical_storage_enabled"]
            and result["historical_manager_initialized"]
        ):
            successful_services.append(service_name)
            print("✅ {service_name}: PASS")
            print("   - Historical Storage: {result['historical_storage_enabled']}")
            print(f"   - Historical Manager: {result['historical_manager_initialized']}")
            print("   - Cache Type: {result['cache_type']}")
        else:
            failed_services.append(service_name)
            print("❌ {service_name}: FAIL")
            if result["errors"]:
                for error in result["errors"]:
                    print("     Error: {error}")

    print("\n📈 Core Components:")
    print("   - HistoricalDataManager: {'✅ PASS' if hdm_success else '❌ FAIL'}")
    print("   - UnifiedCache: {'✅ PASS' if cache_success else '❌ FAIL'}")

    print("\n📈 Overall Results:")
    print("   - Services Passing: {len(successful_services)}/{len(audit_results)}")
    print(f"   - Successful Services: {', '.join(successful_services) if successful_services else 'None'}")
    print(f"   - Failed Services: {', '.join(failed_services) if failed_services else 'None'}")

    # Determine overall success
    overall_success = len(successful_services) == len(audit_results) and hdm_success and cache_success

    if overall_success:
        print("\n🎉 CONFIGURATION AUDIT PASSED!")
        print("All services are properly configured for hybrid storage.")
    else:
        print("\n⚠️  CONFIGURATION ISSUES DETECTED")
        print("Some services are not properly configured. See details above.")

    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
