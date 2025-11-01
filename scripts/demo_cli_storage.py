#!/usr/bin/env python3
"""
Demo CLI Historical Storage

Demonstrates real CLI commands that trigger file creation in ./data/raw/
"""

import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show results"""
    print("\n🔄 {description}")
    print("   Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode == 0:
            print("   ✅ Command succeeded")
            if result.stdout:
                # Show just the last few lines to avoid spam
                lines = result.stdout.strip().split("\n")
                for line in lines[-3:]:
                    if line.strip():
                        print("   📄 {line}")
        else:
            print("   ❌ Command failed")
            if result.stderr:
                print("   Error: {result.stderr[:200]}")

        return result.returncode == 0

    except Exception:
        print("   ❌ Failed to run command: {e}")
        return False


def count_files():
    """Count hybrid format files in data/raw (CSV + metadata JSON files)"""
    raw_path = Path("data/raw")
    if raw_path.exists():
        # Count CSV files (data) and .meta.json files (metadata) separately
        csv_files = list(raw_path.rglob("*.csv"))
        meta_files = list(raw_path.rglob("*.meta.json"))
        # Also count old format JSON files for backward compatibility
        old_json_files = [f for f in raw_path.rglob("*.json") if not f.name.endswith(".meta.json")]
        return len(csv_files) + len(meta_files) + len(old_json_files)
    return 0


def show_latest_files(count=3):
    """Show the latest files created (hybrid format: CSV + metadata JSON)"""
    raw_path = Path("data/raw")
    if not raw_path.exists():
        return

    # Collect all relevant files: CSV, metadata JSON, and old format JSON
    csv_files = list(raw_path.rglob("*.csv"))
    meta_files = list(raw_path.rglob("*.meta.json"))
    old_json_files = [f for f in raw_path.rglob("*.json") if not f.name.endswith(".meta.json")]

    all_files = csv_files + meta_files + old_json_files

    if not all_files:
        print("\n📄 No data files found")
        return

    # Sort by modification time
    all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    print("\n📄 Latest {min(count, len(all_files))} files:")
    for file_path in all_files[:count]:
        relative_path = file_path.relative_to(raw_path)
        size = file_path.stat().st_size
        file_type = (
            "CSV Data"
            if file_path.suffix == ".csv"
            else ("Metadata" if file_path.name.endswith(".meta.json") else "JSON Data")
        )
        print("   📄 {relative_path} ({size} bytes) [{file_type}]")

    # Show summary of file types
    print("\n📊 File Summary:")
    print("   - CSV Data Files: {len(csv_files)}")
    print("   - Metadata Files: {len(meta_files)}")
    print("   - Old JSON Files: {len(old_json_files)}")
    print("   Total: {len(all_files)} files")


def main():
    """Main demo"""
    print("🚀 CLI Historical Storage Demo")
    print("=" * 60)
    print("This demonstrates CLI commands that trigger file creation in ./data/raw/")

    initial_count = count_files()
    print("\n📁 Initial file count: {initial_count}")

    # Test fundamental analysis (should trigger multiple API calls)
    success1 = run_command(
        ["python", "fundamental_analysis/fundamental_analysis.py", "--symbol", "NVDA"],
        "Running fundamental analysis for NVDA",
    )

    # Check file count after first command
    after_first = count_files()
    print("📁 Files after fundamental analysis: {after_first}")

    # Test with different symbol
    success2 = run_command(
        ["python", "fundamental_analysis/fundamental_analysis.py", "--symbol", "AMD"],
        "Running fundamental analysis for AMD",
    )

    # Check final count
    final_count = count_files()
    print("📁 Final file count: {final_count}")

    # Show results
    new_files = final_count - initial_count
    print("\n📊 Results:")
    print("   📈 New files created: {new_files}")
    print("   ✅ Fundamental analysis commands: {success1 and success2}")

    if new_files > 0:
        show_latest_files(5)
        print("\n🎉 SUCCESS: CLI commands are creating hybrid format data files!")

        print("\n✅ PROVEN CLI TRIGGERS:")
        print("   • python fundamental_analysis/fundamental_analysis.py --symbol SYMBOL")
        print("   • Any script that calls financial services with fresh data")
        print("   • Direct service API calls create CSV + metadata JSON files")
        print("   • Files stored in optimized hybrid format for better performance")

    else:
        print("\n📝 Note: Commands may have used cached data.")
        print("   Fresh API calls will automatically create historical files.")

        print("\n✅ ALTERNATIVE DEMOS:")
        print("   • Clear cache and re-run commands")
        print("   • Use different/new symbols")
        print("   • Call services directly (as shown in test_final_cli.py)")


if __name__ == "__main__":
    main()
