#!/usr/bin/env python3
"""
Test script to validate trade history discovery JSON files against the schema.
Designed for institutional-grade trading system validation with comprehensive error reporting.
"""

import json
import sys
from pathlib import Path


try:
    from jsonschema import ValidationError, validate
except ImportError:
    print("Error: jsonschema library not found. Install it with: pip install jsonschema")
    sys.exit(1)


def load_schema():
    """Load the trade history discovery schema from the schemas directory."""
    schema_path = Path(__file__).parent / "schemas" / "trade_history_discovery_schema.json"

    if not schema_path.exists():
        print("Error: Schema file not found at {schema_path}")
        return None

    try:
        with open(schema_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in schema file: {e}")
        return None


def load_discovery_file(file_path):
    """Load a trade history discovery JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in {file_path}: {e}")
        return None
    except FileNotFoundError:
        print("Error: File not found: {file_path}")
        return None


def validate_discovery_file(discovery_data, schema, file_path):
    """Validate a trade history discovery file against the schema."""
    try:
        validate(instance=discovery_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def analyze_institutional_quality(discovery_data, file_name):
    """Analyze institutional-grade quality metrics from discovery data."""
    quality_metrics = {
        "overall_confidence": None,
        "data_completeness": None,
        "win_rate": None,
        "profit_factor": None,
        "closed_trades": None,
        "statistical_adequacy": None,
    }

    # Extract quality metrics
    if "discovery_metadata" in discovery_data:
        quality_metrics["overall_confidence"] = discovery_data["discovery_metadata"].get("confidence_score", 0)
        quality_metrics["data_completeness"] = discovery_data["discovery_metadata"].get("data_completeness", 0)

    if "performance_metrics" in discovery_data:
        quality_metrics["win_rate"] = discovery_data["performance_metrics"].get("win_rate", 0)
        quality_metrics["profit_factor"] = discovery_data["performance_metrics"].get("profit_factor", 0)
        quality_metrics["closed_trades"] = discovery_data["performance_metrics"].get("total_closed_trades", 0)

    # Assess statistical adequacy
    closed_trades = quality_metrics["closed_trades"]
    quality_metrics["statistical_adequacy"] = closed_trades >= 5 if closed_trades else False

    return quality_metrics


def print_quality_assessment(metrics, file_name):
    """Print institutional quality assessment."""
    print("  📊 Institutional Quality Assessment:")

    # Confidence Score
    confidence = metrics["overall_confidence"]
    if confidence:
        status = "✅" if confidence >= 0.75 else "⚠️" if confidence >= 0.7 else "❌"
        print("     Confidence Score: {status} {confidence:.3f} (threshold: >0.75)")

    # Data Completeness
    completeness = metrics["data_completeness"]
    if completeness:
        status = "✅" if completeness >= 0.7 else "⚠️" if completeness >= 0.6 else "❌"
        print("     Data Completeness: {status} {completeness:.3f} (threshold: >0.70)")

    # Win Rate
    win_rate = metrics["win_rate"]
    if win_rate is not None:
        status = "✅" if win_rate >= 0.45 else "⚠️" if win_rate >= 0.40 else "❌"
        print("     Win Rate: {status} {win_rate:.3f} (benchmark: >0.45)")

    # Profit Factor
    profit_factor = metrics["profit_factor"]
    if profit_factor:
        status = "✅" if profit_factor >= 1.0 else "❌"
        print("     Profit Factor: {status} {profit_factor:.2f} (threshold: >1.0)")

    # Statistical Adequacy
    closed_trades = metrics["closed_trades"]
    if closed_trades is not None:
        status = "✅" if closed_trades >= 5 else "❌"
        print(f"     Statistical Adequacy: {status} {closed_trades} trades (minimum: 5)")


def main():
    """Main validation function."""
    print("🔍 Testing Trade History Discovery Schema")
    print("=" * 80)

    # Load schema
    schema = load_schema()
    if not schema:
        sys.exit(1)

    print("✅ Trade history discovery schema loaded successfully")

    # Test files (all available trade history discovery files)
    discovery_dir = Path(__file__).parent.parent / "data" / "outputs" / "trade_history" / "discovery"
    test_files = [
        "live_signals_20250719.json",  # Most recent
        "live_signals_20250718.json",  # Recent
        "live_signals_20250717.json",  # Evolving structure
        "live_signals_20250716.json",  # Most comprehensive
    ]

    validation_results = []

    print("\n📁 Testing {len(test_files)} trade history discovery files:")
    print("-" * 60)

    for file_name in test_files:
        file_path = discovery_dir / file_name

        # Load discovery data
        discovery_data = load_discovery_file(file_path)
        if not discovery_data:
            validation_results.append((file_name, False, "Failed to load file"))
            continue

        # Validate against schema
        is_valid, error_message = validate_discovery_file(discovery_data, schema, file_path)
        validation_results.append((file_name, is_valid, error_message))

        # Print immediate result
        status_icon = "✅" if is_valid else "❌"
        print("{status_icon} {file_name}: {'VALID' if is_valid else 'INVALID'}")

        if is_valid:
            # Analyze institutional quality metrics
            quality_metrics = analyze_institutional_quality(discovery_data, file_name)
            print_quality_assessment(quality_metrics, file_name)
        else:
            print("   Error: {error_message}")

        print()  # Add spacing between files

    # Summary
    print("=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)

    valid_count = sum(1 for _, is_valid, _ in validation_results if is_valid)
    total_count = len(validation_results)

    print("✅ Valid files: {valid_count}/{total_count}")
    print("❌ Invalid files: {total_count - valid_count}/{total_count}")

    if valid_count == total_count:
        print("\n🎉 ALL TRADE HISTORY DISCOVERY FILES PASS SCHEMA VALIDATION!")
        print("Schema validates institutional-grade trading framework requirements.")
        print("Ready for production algorithmic trading validation.")
        return 0
    print("\n⚠️  {total_count - valid_count} files failed validation.")
    print("Schema may need adjustments for framework evolution.")

    # Print detailed errors for failed validations
    print("\n🔍 DETAILED VALIDATION ERRORS:")
    print("-" * 60)
    for file_name, is_valid, error_message in validation_results:
        if not is_valid:
            print("\n❌ {file_name}:")
            print("   {error_message}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
