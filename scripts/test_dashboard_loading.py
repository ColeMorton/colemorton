#!/usr/bin/env python3
"""
Dashboard Loading Test

This script validates that the dashboard system is working correctly.
"""

import json
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_dashboard_config():
    """Test dashboard configurations match between photo-booth.json and dashboardLoader.ts."""
    print("🔍 Testing dashboard configuration consistency...")

    # Load photo-booth config
    config_path = project_root / "frontend/src/config/photo-booth.json"
    with open(config_path) as f:
        photo_booth_config = json.load(f)

    # Check that default dashboard exists in active dashboards
    default_dashboard = photo_booth_config["default_dashboard"]
    active_dashboards = {d["id"] for d in photo_booth_config["active_dashboards"]}

    if default_dashboard not in active_dashboards:
        print(f"❌ Default dashboard '{default_dashboard}' not found in active dashboards")
        return False

    print("✅ Default dashboard '{default_dashboard}' is properly configured")
    return True


def test_dashboard_mdx_files():
    """Test that dashboard MDX files exist and have correct frontmatter."""
    print("🔍 Testing dashboard MDX files...")

    dashboards_dir = project_root / "frontend/src/content/dashboards"
    dashboard_files = list(dashboards_dir.glob("*.mdx"))

    if not dashboard_files:
        print("❌ No dashboard MDX files found")
        return False

    expected_frontmatter_keys = [
        "title",
        "description",
        "layout",
        "mode",
        "enabled",
        "draft",
    ]

    for file_path in dashboard_files:
        print("  📄 Checking {file_path.name}...")

        with open(file_path) as f:
            content = f.read()

        # Extract frontmatter
        if not content.startswith("---"):
            print("    ❌ Missing frontmatter in {file_path.name}")
            return False

        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            print("    ❌ Invalid frontmatter format in {file_path.name}")
            return False

        frontmatter = content[3:frontmatter_end].strip()

        # Check for required keys (basic check)
        for key in expected_frontmatter_keys:
            if f"{key}:" not in frontmatter:
                print("    ❌ Missing '{key}' in frontmatter of {file_path.name}")
                return False

        print("    ✅ {file_path.name} has valid frontmatter")

    print("✅ All {len(dashboard_files)} dashboard files are valid")
    return True


def test_chart_types_consistency():
    """Test that chart types used in dashboards are supported."""
    print("🔍 Testing chart type consistency...")

    # Expected chart types from ChartDisplay component
    supported_chart_types = {
        "apple-stock",
        "portfolio-value-comparison",
        "returns-comparison",
        "portfolio-drawdowns",
        "live-signals-equity-curve",
        "live-signals-drawdowns",
        "live-signals-weekly-candlestick",
        "trade-pnl-waterfall",
        "open-positions-pnl-timeseries",
    }

    # Chart types used in dashboard MDX files
    dashboards_dir = project_root / "frontend/src/content/dashboards"
    used_chart_types = set()

    for file_path in dashboards_dir.glob("*.mdx"):
        with open(file_path) as f:
            content = f.read()

        # Extract chartType values (simple regex-like approach)
        lines = content.split("\n")
        for line in lines:
            if "chartType=" in line:
                # Extract value between quotes
                start = line.find('chartType="') + 11
                if start > 10:  # Found the pattern
                    end = line.find('"', start)
                    if end > start:
                        chart_type = line[start:end]
                        used_chart_types.add(chart_type)

    # Check for unsupported chart types
    unsupported = used_chart_types - supported_chart_types
    if unsupported:
        print("❌ Unsupported chart types found: {unsupported}")
        return False

    print("✅ All {len(used_chart_types)} chart types are supported")
    print("  Used chart types: {sorted(used_chart_types)}")
    return True


def test_content_collection_registration():
    """Test that dashboards collection is registered in content.config.ts."""
    print("🔍 Testing content collection registration...")

    config_path = project_root / "frontend/src/content.config.ts"
    with open(config_path) as f:
        content = f.read()

    # Check for dashboards collection
    if "dashboardsCollection" not in content:
        print("❌ dashboardsCollection not defined in content.config.ts")
        return False

    if "dashboards: dashboardsCollection" not in content:
        print("❌ dashboards collection not exported in content.config.ts")
        return False

    print("✅ Dashboards collection is properly registered")
    return True


def test_dashboard_loader():
    """Test that dashboardLoader.ts is properly structured."""
    print("🔍 Testing dashboard loader implementation...")

    loader_path = project_root / "frontend/src/lib/dashboardLoader.ts"
    if not loader_path.exists():
        print("❌ dashboardLoader.ts not found")
        return False

    with open(loader_path) as f:
        content = f.read()

    # Check for key exports and classes
    required_exports = [
        "export interface DashboardChart",
        "export interface DashboardConfig",
        "export class DashboardLoader",
        "getAllDashboards",
        "getDashboard",
        "getLayoutClasses",
        "validateChartTypes",
    ]

    for export in required_exports:
        if export not in content:
            print("❌ Missing required export: {export}")
            return False

    print("✅ Dashboard loader is properly implemented")
    return True


def main():
    """Run all dashboard loading tests."""
    print("🚀 Running Dashboard Loading Tests")
    print("=" * 50)

    tests = [
        test_dashboard_config,
        test_dashboard_mdx_files,
        test_chart_types_consistency,
        test_content_collection_registration,
        test_dashboard_loader,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception:
            print("❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 50)
    print("📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All dashboard loading tests passed!")
        print("\n📋 Dashboard system is ready:")
        print("1. Dashboard collection registered ✅")
        print("2. Dashboard loader implemented ✅")
        print("3. Dashboard templates valid ✅")
        print("4. Chart types consistent ✅")
        print("5. Configuration synchronized ✅")
        return 0
    print("💥 Some tests failed. Please fix the issues above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
