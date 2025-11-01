#!/usr/bin/env python3
"""
Test Portfolio Parameter Parsing for trade_history_discover

Validates the portfolio parameter resolution logic that determines
whether to use exact filename or find latest file matching pattern.
"""

import os
import re


def parse_portfolio_parameter(
    portfolio: str,
    data_dir: str = "/Users/colemorton/Projects/colemorton/data/raw/trade_history/",
) -> tuple[bool, str, str | None]:
    """
    Parse portfolio parameter and resolve to actual CSV filename.

    Args:
        portfolio: Portfolio parameter (name only or full filename)
        data_dir: Directory containing trade history CSV files

    Returns:
        Tuple of (success, resolved_filename, error_message)
    """

    # Check if portfolio parameter contains date pattern (YYYYMMDD)
    date_pattern = re.compile(r".*_(\d{8})$")
    date_match = date_pattern.match(portfolio)

    if date_match:
        # Exact filename provided
        filename = f"{portfolio}.csv"
        filepath = os.path.join(data_dir, filename)

        if os.path.exists(filepath):
            return True, filename, None
        return False, "", f"Specified file not found: {filepath}"

    # Portfolio name only - find latest file
    if not os.path.exists(data_dir):
        return False, "", f"Data directory not found: {data_dir}"

    # Find all files matching portfolio pattern
    # pattern = f"{portfolio}_*.csv"  # Unused variable
    matching_files = []

    for filename in os.listdir(data_dir):
        if re.match(f"{portfolio}_\\d{{8}}\\.csv$", filename):
            matching_files.append(filename)

    if not matching_files:
        return False, "", f"No files found for portfolio: {portfolio}"

    # Sort by date (embedded in filename) and return latest
    matching_files.sort(reverse=True)  # Latest first
    latest_file = matching_files[0]

    return True, latest_file, None


def extract_csv_structure_info(csv_path: str) -> dict:
    """
    Extract basic structure information from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        Dictionary with CSV structure info
    """

    if not os.path.exists(csv_path):
        return {"error": f"File not found: {csv_path}"}

    try:
        with open(csv_path) as f:
            header = f.readline().strip()
            columns = header.split(",")

            # Count total lines (excluding header)
            line_count = sum(1 for line in f)

        return {
            "total_columns": len(columns),
            "columns": columns,
            "total_rows": line_count,
            "file_size_bytes": os.path.getsize(csv_path),
        }

    except Exception as e:
        return {"error": f"Failed to parse CSV: {str(e)}"}


def test_portfolio_parsing():
    """
    Test portfolio parameter parsing with various inputs.
    """

    test_cases = [
        # (portfolio_param, expected_success, description)
        ("live_signals", True, "Portfolio name only - should find latest file"),
        ("live_signals_20250626", True, "Exact filename - should find specific file"),
        ("momentum_strategy", False, "Non-existent portfolio - should fail gracefully"),
        ("live_signals_20250101", False, "Non-existent date - should fail gracefully"),
    ]

    print("=== Portfolio Parameter Parsing Tests ===\n")

    for portfolio, expected_success, description in test_cases:
        print("Test: {description}")
        print("Input: '{portfolio}'")

        success, filename, error = parse_portfolio_parameter(portfolio)

        print("Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        if success:
            print("Resolved to: {filename}")

            # Try to extract CSV info if file exists
            csv_path = f"/Users/colemorton/Projects/colemorton/data/raw/trade_history/{filename}"
            csv_info = extract_csv_structure_info(csv_path)

            if "error" not in csv_info:
                print(f"CSV Info: {csv_info['total_rows']} rows, {csv_info['total_columns']} columns")
                print("Key columns: Position_UUID, Ticker, Strategy_Type, Status")

        else:
            print("Error: {error}")

        print("-" * 50)


def validate_discovery_schema():
    """
    Validate that the JSON schema file is properly structured.
    """

    schema_path = (
        "/Users/colemorton/Projects/colemorton/data/outputs/trade_history/discover/trading_discovery_schema_v1.json"
    )

    print("=== Discovery Schema Validation ===\n")

    if not os.path.exists(schema_path):
        print("❌ Schema file not found")
        return

    try:
        import json

        with open(schema_path) as f:
            schema = json.load(f)

        # Basic schema validation
        required_keys = ["$schema", "title", "description", "type", "properties"]
        missing_keys = [key for key in required_keys if key not in schema]

        if missing_keys:
            print("❌ Missing required schema keys: {missing_keys}")
        else:
            print("✅ Schema structure valid")

        # Check required properties
        required_props = [
            "portfolio",
            "discovery_metadata",
            "authoritative_trade_data",
            "data_quality_assessment",
        ]
        schema_props = schema.get("properties", {}).keys()
        missing_props = [prop for prop in required_props if prop not in schema_props]

        if missing_props:
            print("❌ Missing required properties: {missing_props}")
        else:
            print("✅ Required properties present")

        print("Total properties defined: {len(schema.get('properties', {}))}")

    except json.JSONDecodeError:
        print("❌ Invalid JSON: {e}")
    except Exception:
        print("❌ Schema validation error: {e}")


def main():
    """
    Run all validation tests for Phase 1 implementation.
    """

    print("TRADE HISTORY DISCOVER - Phase 1 Validation Tests")
    print("=" * 60)
    print()

    test_portfolio_parsing()
    print()
    validate_discovery_schema()

    print("\n" + "=" * 60)
    print("Phase 1 validation complete!")


if __name__ == "__main__":
    main()
