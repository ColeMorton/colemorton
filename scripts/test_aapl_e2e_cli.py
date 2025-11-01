#!/usr/bin/env python3
"""
AAPL End-to-End CLI Test Suite

Demonstrates complete CLI workflow for AAPL daily and weekly price data creation.
Tests the full pipeline from CLI commands to consolidated file storage.

Key features tested:
- CLI command execution for AAPL daily and weekly data
- Consolidated CSV + metadata JSON file creation
- Data integrity verification across the complete pipeline
- File structure validation for consolidated format
"""

import csv
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class AAPLEndToEndTest:
    """AAPL End-to-End CLI Testing Framework"""

    def __init__(self):
        self.test_start_time = datetime.now()
        self.script_dir = Path(__file__).parent
        self.data_dir = Path("data/raw")
        self.aapl_dir = self.data_dir / "stocks" / "AAPL"
        self.results = []

        print("🍎 AAPL End-to-End CLI Test Suite")
        print("=" * 60)
        print("Test started: {self.test_start_time}")
        print("Working directory: {self.script_dir}")

    def get_file_counts(self) -> tuple[int, int]:
        """Get current count of AAPL CSV and metadata files"""
        if not self.aapl_dir.exists():
            return 0, 0

        csv_files = len(list(self.aapl_dir.rglob("*.csv")))
        meta_files = len(list(self.aapl_dir.rglob("*.meta.json")))

        return csv_files, meta_files

    def run_cli_command(self, cmd: list[str], description: str, timeout: int = 60) -> dict:
        """Execute CLI command and capture results"""
        result = {
            "command": " ".join(cmd),
            "description": description,
            "success": False,
            "stdout": "",
            "stderr": "",
            "execution_time": 0,
            "files_before": self.get_file_counts(),
            "files_after": (0, 0),
            "files_created": 0,
        }

        print("\n🔄 {description}")
        print("   Command: {result['command']}")

        start_time = time.time()

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.script_dir,
            )

            result["execution_time"] = time.time() - start_time
            result["returncode"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            result["success"] = process.returncode == 0
            result["files_after"] = self.get_file_counts()

            # Calculate files created
            csv_before, meta_before = result["files_before"]
            csv_after, meta_after = result["files_after"]
            result["files_created"] = (csv_after + meta_after) - (csv_before + meta_before)

            if result["success"]:
                print(f"   ✅ Success ({result['execution_time']:.2f}s, {result['files_created']} files)")
            else:
                print(f"   ❌ Failed (code: {process.returncode}, {result['execution_time']:.2f}s)")
                if result["stderr"]:
                    print("   Error: {result['stderr'][:200]}...")

        except subprocess.TimeoutExpired:
            result["execution_time"] = timeout
            result["stderr"] = f"Command timed out after {timeout} seconds"
            print("   ⏰ Timeout ({timeout}s)")
        except Exception as e:
            result["execution_time"] = time.time() - start_time
            result["stderr"] = str(e)
            print("   ❌ Exception: {e}")

        self.results.append(result)
        return result

    def verify_consolidated_files(self) -> dict:
        """Verify AAPL consolidated files exist and contain valid data"""
        verification = {
            "daily_csv_exists": False,
            "daily_meta_exists": False,
            "weekly_csv_exists": False,
            "weekly_meta_exists": False,
            "daily_records": 0,
            "weekly_records": 0,
            "data_integrity": True,
            "errors": [],
        }

        print("\n🔍 Verifying AAPL consolidated files...")

        # Check file existence
        daily_csv = self.aapl_dir / "daily.csv"
        daily_meta = self.aapl_dir / "daily.meta.json"
        weekly_csv = self.aapl_dir / "weekly.csv"
        weekly_meta = self.aapl_dir / "weekly.meta.json"

        verification["daily_csv_exists"] = daily_csv.exists()
        verification["daily_meta_exists"] = daily_meta.exists()
        verification["weekly_csv_exists"] = weekly_csv.exists()
        verification["weekly_meta_exists"] = weekly_meta.exists()

        # Verify daily data
        if verification["daily_csv_exists"]:
            try:
                with open(daily_csv) as f:
                    reader = csv.DictReader(f)
                    daily_records = list(reader)
                    verification["daily_records"] = len(daily_records)

                    # Check required fields
                    if daily_records:
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        first_record = daily_records[0]
                        missing_fields = [f for f in required_fields if f not in first_record]
                        if missing_fields:
                            verification["errors"].append(f"Daily CSV missing fields: {missing_fields}")
                            verification["data_integrity"] = False

                        print(f"   📄 Daily CSV: {verification['daily_records']} records")
                    else:
                        verification["errors"].append("Daily CSV is empty")
                        verification["data_integrity"] = False

            except Exception as e:
                verification["errors"].append(f"Failed to read daily CSV: {e}")
                verification["data_integrity"] = False

        # Verify daily metadata
        if verification["daily_meta_exists"]:
            try:
                with open(daily_meta) as f:
                    daily_metadata = json.load(f)

                    # Check required metadata fields
                    required_meta_fields = [
                        "symbol",
                        "data_type",
                        "timeframe",
                        "records",
                        "format_version",
                    ]
                    missing_meta = [f for f in required_meta_fields if f not in daily_metadata]
                    if missing_meta:
                        verification["errors"].append(f"Daily metadata missing fields: {missing_meta}")
                        verification["data_integrity"] = False

                    # Verify metadata matches data
                    if "records" in daily_metadata and daily_metadata["records"] != verification["daily_records"]:
                        verification["errors"].append(
                            f"Daily metadata record count mismatch: {daily_metadata['records']} vs {verification['daily_records']}"
                        )
                        verification["data_integrity"] = False

                    print(
                        f"   📋 Daily Meta: {daily_metadata.get('records', 0)} records, format {daily_metadata.get('format_version', 'unknown')}"
                    )

            except Exception as e:
                verification["errors"].append(f"Failed to read daily metadata: {e}")
                verification["data_integrity"] = False

        # Verify weekly data
        if verification["weekly_csv_exists"]:
            try:
                with open(weekly_csv) as f:
                    reader = csv.DictReader(f)
                    weekly_records = list(reader)
                    verification["weekly_records"] = len(weekly_records)
                    print("   📄 Weekly CSV: {verification['weekly_records']} records")

            except Exception as e:
                verification["errors"].append(f"Failed to read weekly CSV: {e}")
                verification["data_integrity"] = False

        # Verify weekly metadata
        if verification["weekly_meta_exists"]:
            try:
                with open(weekly_meta) as f:
                    weekly_metadata = json.load(f)
                    print(
                        f"   📋 Weekly Meta: {weekly_metadata.get('records', 0)} records, format {weekly_metadata.get('format_version', 'unknown')}"
                    )

            except Exception as e:
                verification["errors"].append(f"Failed to read weekly metadata: {e}")
                verification["data_integrity"] = False

        return verification

    def analyze_file_structure(self):
        """Analyze the AAPL directory structure"""
        print("\n📁 AAPL File Structure Analysis")
        print("-" * 40)

        if not self.aapl_dir.exists():
            print("❌ AAPL directory does not exist")
            return

        print("📂 AAPL Directory: {self.aapl_dir}")

        # List all files in AAPL directory
        all_files = list(self.aapl_dir.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]

        if not files_only:
            print("   📄 No files found")
            return

        # Categorize files
        csv_files = [f for f in files_only if f.suffix == ".csv"]
        meta_files = [f for f in files_only if f.name.endswith(".meta.json")]
        other_files = [f for f in files_only if f not in csv_files and f not in meta_files]

        print("   📊 File Summary:")
        print("      - CSV files: {len(csv_files)}")
        print("      - Metadata files: {len(meta_files)}")
        print("      - Other files: {len(other_files)}")

        # Show file details
        for file_path in sorted(files_only, key=lambda x: x.stat().st_mtime, reverse=True):
            relative_path = file_path.relative_to(self.aapl_dir)
            size = file_path.stat().st_size
            file_type = (
                "CSV" if file_path.suffix == ".csv" else ("META" if file_path.name.endswith(".meta.json") else "OTHER")
            )
            print("      📄 {relative_path} ({size}b) [{file_type}]")

    def test_yahoo_finance_comprehensive(self) -> dict:
        """Test Yahoo Finance CLI for AAPL comprehensive data (daily + weekly)"""
        return self.run_cli_command(
            ["python", "yahoo_finance_cli.py", "history", "AAPL", "--env", "dev"],
            "Yahoo Finance CLI - AAPL Comprehensive Historical (max daily + max weekly)",
            timeout=120,
        )

    def test_yahoo_finance_quote(self) -> dict:
        """Test Yahoo Finance CLI for AAPL quote data"""
        return self.run_cli_command(
            ["python", "yahoo_finance_cli.py", "quote", "AAPL", "--env", "dev"],
            "Yahoo Finance CLI - AAPL Quote",
        )

    def test_direct_service_calls(self) -> list[dict]:
        """Test direct service calls to ensure data creation"""
        results = []

        # Test comprehensive data creation
        comprehensive_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "services"))
from services.yahoo_finance import create_yahoo_finance_service

print("Creating Yahoo Finance service...")
service = create_yahoo_finance_service(env="dev")

print("Fetching AAPL comprehensive data (daily max + weekly max)...")
# Get daily data (max) - this should trigger comprehensive collection
daily_data = service.get_historical_data("AAPL", "max")
print("Daily data retrieved: {len(daily_data.get('data', []))} records")

# Get weekly data (max) explicitly
weekly_data = service.get_historical_data_weekly("AAPL", "max")
print("Weekly data retrieved: {len(weekly_data.get('data', []))} records")

print("Total records: {len(daily_data.get('data', [])) + len(weekly_data.get('data', []))}")
"""

        comprehensive_result = self.run_cli_command(
            ["python", "-c", comprehensive_script],
            "Direct Service Call - AAPL Comprehensive Data (max daily + max weekly)",
            timeout=120,
        )
        results.append(comprehensive_result)

        return results

    def run_complete_test(self):
        """Execute the complete AAPL E2E test suite"""
        print("\n🚀 Starting Complete AAPL E2E Test...")

        # Initial state
        self.analyze_file_structure()
        initial_csv, initial_meta = self.get_file_counts()
        print(f"\n📊 Initial State: {initial_csv} CSV files, {initial_meta} metadata files")

        # Test 1: Direct service calls (most reliable for file creation)
        print("\n📡 Phase 1: Direct Service Integration")
        service_results = self.test_direct_service_calls()

        # Brief pause
        time.sleep(3)

        # Test 2: CLI commands
        print("\n🖥️  Phase 2: CLI Commands")
        cli_results = [
            self.test_yahoo_finance_comprehensive(),
            self.test_yahoo_finance_quote(),
        ]

        # Test 3: File verification
        print("\n✅ Phase 3: File Verification")
        verification = self.verify_consolidated_files()

        # Final analysis
        self.analyze_file_structure()
        final_csv, final_meta = self.get_file_counts()
        total_files_created = (final_csv + final_meta) - (initial_csv + initial_meta)

        # Generate report
        self.generate_final_report(service_results + cli_results, verification, total_files_created)

        return verification["data_integrity"] and total_files_created > 0

    def generate_final_report(self, all_results: list[dict], verification: dict, total_files_created: int):
        """Generate comprehensive test report"""
        test_duration = datetime.now() - self.test_start_time

        print("\n📊 AAPL E2E CLI TEST REPORT")
        print("=" * 60)
        print("Test Duration: {test_duration}")
        print("Total Files Created: {total_files_created}")

        # Command results
        successful_commands = [r for r in all_results if r["success"]]
        failed_commands = [r for r in all_results if not r["success"]]

        print("\n🖥️  Command Execution Results:")
        print(f"   - Successful Commands: {len(successful_commands)}/{len(all_results)}")
        print(f"   - Total Execution Time: {sum(r['execution_time'] for r in all_results):.2f}s")

        for result in all_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['description']} ({result['execution_time']:.2f}s)")
            if not result["success"] and result["stderr"]:
                print("      Error: {result['stderr'][:100]}...")

        # File verification results
        print("\n📄 File Verification Results:")
        files_exist = (
            verification["daily_csv_exists"]
            and verification["daily_meta_exists"]
            and verification["weekly_csv_exists"]
            and verification["weekly_meta_exists"]
        )

        print(
            f"   - Daily CSV: {'✅' if verification['daily_csv_exists'] else '❌'} ({verification['daily_records']} records)"
        )
        print(f"   - Daily Metadata: {'✅' if verification['daily_meta_exists'] else '❌'}")
        print(
            f"   - Weekly CSV: {'✅' if verification['weekly_csv_exists'] else '❌'} ({verification['weekly_records']} records)"
        )
        print(f"   - Weekly Metadata: {'✅' if verification['weekly_meta_exists'] else '❌'}")
        print("   - Data Integrity: {'✅' if verification['data_integrity'] else '❌'}")

        if verification["errors"]:
            print("\n⚠️  Data Verification Errors:")
            for error in verification["errors"]:
                print("   - {error}")

        # Overall assessment
        command_success_rate = len(successful_commands) / len(all_results) if all_results else 0

        # Check for comprehensive data volumes
        daily_records_sufficient = (
            verification["daily_records"] >= 1000
        )  # At least 1000 days (max data should have years)
        weekly_records_sufficient = (
            verification["weekly_records"] >= 500
        )  # At least 500 weeks (max data should have 10+ years)

        overall_success = (
            command_success_rate >= 0.5
            and total_files_created > 0
            and verification["data_integrity"]
            and files_exist
            and daily_records_sufficient
            and weekly_records_sufficient
        )

        print("\n🎯 OVERALL ASSESSMENT:")
        print("   - Command Success Rate: {command_success_rate:.0%}")
        print("   - Files Created: {total_files_created}")
        print("   - Data Integrity: {'✅' if verification['data_integrity'] else '❌'}")
        print("   - Complete File Set: {'✅' if files_exist else '❌'}")
        print(
            f"   - Daily Data Volume: {'✅' if daily_records_sufficient else '❌'} ({verification['daily_records']} records, need ≥1000)"
        )
        print(
            f"   - Weekly Data Volume: {'✅' if weekly_records_sufficient else '❌'} ({verification['weekly_records']} records, need ≥500)"
        )

        if overall_success:
            print("\n🎉 AAPL E2E CLI TEST: SUCCESS!")
            print("   - CLI commands executed successfully")
            print("   - Consolidated CSV + metadata files created")
            print("   - Data integrity verified")
            print("   - Complete AAPL daily and weekly data pipeline working")
        else:
            print("\n⚠️  AAPL E2E CLI TEST: ISSUES DETECTED")
            print("   - Some commands failed or files missing")
            print("   - Check individual command results above")
            print("   - May need API keys or network connectivity")

        return overall_success


def main():
    """Main test execution"""
    tester = AAPLEndToEndTest()
    success = tester.run_complete_test()

    print("\n{'='*60}")
    if success:
        print("🏆 AAPL End-to-End CLI Test Suite: PASSED")
    else:
        print("❌ AAPL End-to-End CLI Test Suite: FAILED")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
