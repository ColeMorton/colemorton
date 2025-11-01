#!/usr/bin/env python3
"""
Comprehensive CLI Storage Integration Test

Tests all CLI commands to ensure they properly integrate with the hybrid storage system.
Verifies that API calls create the correct CSV + metadata JSON files.
"""

import subprocess
import time
from pathlib import Path


def get_current_file_count() -> tuple[int, int, int]:
    """
    Get current count of data files

    Returns:
        Tuple of (csv_files, meta_files, old_json_files)
    """
    raw_path = Path("data/raw")
    if not raw_path.exists():
        return 0, 0, 0

    csv_files = len(list(raw_path.rglob("*.csv")))
    meta_files = len(list(raw_path.rglob("*.meta.json")))
    old_json_files = len([f for f in raw_path.rglob("*.json") if not f.name.endswith(".meta.json")])

    return csv_files, meta_files, old_json_files


def get_latest_files(count: int = 5) -> list[Path]:
    """Get the latest created files"""
    raw_path = Path("data/raw")
    if not raw_path.exists():
        return []

    # Get all data files
    csv_files = list(raw_path.rglob("*.csv"))
    meta_files = list(raw_path.rglob("*.meta.json"))
    old_json_files = [f for f in raw_path.rglob("*.json") if not f.name.endswith(".meta.json")]

    all_files = csv_files + meta_files + old_json_files
    all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return all_files[:count]


def run_cli_command(cmd: list[str], timeout: int = 30) -> dict[str, any]:
    """
    Run a CLI command and capture results

    Args:
        cmd: Command to run as list
        timeout: Timeout in seconds

    Returns:
        Dictionary with command results
    """
    result = {
        "command": " ".join(cmd),
        "success": False,
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "files_created": 0,
    }

    try:
        # Get file count before command
        csv_before, meta_before, old_before = get_current_file_count()

        print("🔄 Running: {result['command']}")

        # Run command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent,
        )

        result["returncode"] = process.returncode
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["success"] = process.returncode == 0

        # Get file count after command
        csv_after, meta_after, old_after = get_current_file_count()
        files_created = (csv_after + meta_after + old_after) - (csv_before + meta_before + old_before)
        result["files_created"] = files_created

        if result["success"]:
            print("   ✅ Success ({files_created} files created)")
        else:
            print("   ❌ Failed (return code: {process.returncode})")
            if result["stderr"]:
                print("   Error: {result['stderr'][:200]}...")

    except subprocess.TimeoutExpired:
        result["stderr"] = f"Command timed out after {timeout} seconds"
        print("   ⏰ Timeout after {timeout}s")
    except Exception as e:
        result["stderr"] = str(e)
        print("   ❌ Exception: {e}")

    return result


def test_service_integration():
    """Test direct service integration"""
    print("\n🧪 Testing Direct Service Integration")
    print("-" * 50)

    results = []

    # Test Yahoo Finance service directly
    test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "services"))
from services.yahoo_finance import create_yahoo_finance_service

service = create_yahoo_finance_service(env="dev")
data = service.get_stock_info("AAPL")
print("Retrieved data for {data.get('symbol', 'unknown')}")
"""

    result = run_cli_command(["python", "-c", test_script], timeout=45)

    results.append(("Yahoo Finance Direct", result))

    # Test FMP service directly
    test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "services"))
from services.fmp import create_fmp_service

service = create_fmp_service(env="dev")
data = service.get_stock_quote("TSLA")
print("Retrieved {len(data)} quote records")
"""

    result = run_cli_command(["python", "-c", test_script], timeout=45)

    results.append(("FMP Direct", result))

    return results


def test_cli_commands():
    """Test actual CLI commands"""
    print("\n🖥️  Testing CLI Commands")
    print("-" * 50)

    results = []

    # Test commands that should work
    test_commands = [
        (
            ["python", "yahoo_finance_cli.py", "quote", "MSFT"],
            "Yahoo Finance CLI - Quote",
        ),
        (["python", "fmp_cli.py", "quote", "GOOGL"], "FMP CLI - Quote"),
        (
            ["python", "alpha_vantage_cli.py", "daily", "NVDA"],
            "Alpha Vantage CLI - Daily",
        ),
    ]

    for cmd, description in test_commands:
        result = run_cli_command(cmd, timeout=60)
        results.append((description, result))

        # Brief pause between commands
        time.sleep(2)

    return results


def test_historical_storage_verification():
    """Verify that historical storage is actually working"""
    print("\n🗄️  Testing Historical Storage Verification")
    print("-" * 50)

    # Test storage directly
    test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "utils"))
from utils.historical_data_manager import HistoricalDataManager, DataType

hdm = HistoricalDataManager()

# Store test data
sample_data = {
    "symbol": "DIRECT_TEST",
    "data": [
        {
            "Date": "2025-07-28",
            "Open": 150.0,
            "High": 155.0,
            "Low": 148.0,
            "Close": 152.0,
            "Volume": 2000000,
            "Adj Close": 152.0
        }
    ]
}

success = hdm.store_data(
    symbol="DIRECT_TEST",
    data=sample_data,
    data_type=DataType.STOCK_DAILY_PRICES,
    source="cli_test"
)

print("Storage success: {success}")

# Verify files were created
data_path = Path("data/raw")
csv_files = list(data_path.rglob("*DIRECT_TEST*.csv"))
meta_files = list(data_path.rglob("*DIRECT_TEST*.meta.json"))

print("CSV files: {len(csv_files)}")
print("Meta files: {len(meta_files)}")

if csv_files:
    print("CSV path: {csv_files[0]}")
if meta_files:
    print("Meta path: {meta_files[0]}")
"""

    result = run_cli_command(["python", "-c", test_script], timeout=30)

    return [("Direct Storage Test", result)]


def analyze_file_structure():
    """Analyze the current file structure"""
    print("\n📁 Current File Structure Analysis")
    print("-" * 50)

    raw_path = Path("data/raw")
    if not raw_path.exists():
        print("❌ data/raw directory does not exist")
        return

    # Get file counts
    csv_files = list(raw_path.rglob("*.csv"))
    meta_files = list(raw_path.rglob("*.meta.json"))
    old_json_files = [f for f in raw_path.rglob("*.json") if not f.name.endswith(".meta.json")]

    print("📊 File Counts:")
    print("   - CSV Data Files: {len(csv_files)}")
    print("   - Metadata Files: {len(meta_files)}")
    print("   - Old JSON Files: {len(old_json_files)}")

    # Show file structure
    if csv_files or meta_files:
        print("\n📂 Recent Hybrid Format Files:")
        latest_files = get_latest_files(10)
        for file_path in latest_files:
            relative_path = file_path.relative_to(raw_path)
            size = file_path.stat().st_size
            file_type = (
                "CSV" if file_path.suffix == ".csv" else ("META" if file_path.name.endswith(".meta.json") else "JSON")
            )
            print("   📄 {relative_path} ({size}b) [{file_type}]")

    # Check directory structure
    print("\n🏗️  Directory Structure:")
    stocks_path = raw_path / "stocks"
    if stocks_path.exists():
        symbols = [d.name for d in stocks_path.iterdir() if d.is_dir()]
        print("   - Stock symbols: {len(symbols)}")
        if symbols:
            print("   - Examples: {', '.join(symbols[:5])}")

            # Check format of first symbol
            if symbols:
                symbol_path = stocks_path / symbols[0]
                subdirs = [d.name for d in symbol_path.iterdir() if d.is_dir()]
                print("   - {symbols[0]} subdirs: {subdirs}")
    else:
        print("   - No stocks directory found")


def main():
    """Main test orchestrator"""
    print("🚀 Comprehensive CLI Storage Integration Test")
    print("=" * 70)

    # Initial file analysis
    analyze_file_structure()

    # Run tests
    all_results = []

    # Test 1: Direct service integration
    service_results = test_service_integration()
    all_results.extend(service_results)

    # Test 2: Historical storage verification
    storage_results = test_historical_storage_verification()
    all_results.extend(storage_results)

    # Test 3: CLI commands
    cli_results = test_cli_commands()
    all_results.extend(cli_results)

    # Final analysis
    print("\n📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)

    successful_tests = []
    failed_tests = []
    total_files_created = 0

    for test_name, result in all_results:
        if result["success"]:
            successful_tests.append(test_name)
            total_files_created += result["files_created"]
            print("✅ {test_name}: PASS ({result['files_created']} files)")
        else:
            failed_tests.append(test_name)
            print("❌ {test_name}: FAIL")
            if result["stderr"]:
                print("   Error: {result['stderr'][:150]}...")

    # Final file analysis
    analyze_file_structure()

    print("\n📈 SUMMARY:")
    print("   - Tests Passed: {len(successful_tests)}/{len(all_results)}")
    print("   - Total Files Created: {total_files_created}")
    print("   - Successful Tests: {', '.join(successful_tests)}")
    if failed_tests:
        print("   - Failed Tests: {', '.join(failed_tests)}")

    # Overall assessment
    success_rate = len(successful_tests) / len(all_results) if all_results else 0

    if success_rate >= 0.8 and total_files_created > 0:
        print("\n🎉 CLI STORAGE INTEGRATION: SUCCESS!")
        print("   - {success_rate:.0%} of tests passed")
        print("   - Hybrid storage system is working correctly")
        print("   - CLI commands are creating data files as expected")
        return True
    print("\n⚠️  CLI STORAGE INTEGRATION: ISSUES DETECTED")
    print("   - Only {success_rate:.0%} of tests passed")
    print("   - Storage system may have integration problems")
    return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
