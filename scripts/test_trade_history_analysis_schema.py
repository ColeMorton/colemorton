#!/usr/bin/env python3
"""
Test script to validate trade history analysis JSON files against the dedicated schema.
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
    """Load the trade history analysis schema from the schemas directory."""
    schema_path = Path(__file__).parent / "schemas" / "trade_history_analysis_schema.json"

    if not schema_path.exists():
        print("Error: Schema file not found at {schema_path}")
        return None

    try:
        with open(schema_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in schema file: {e}")
        return None


def load_analysis_file(file_path):
    """Load a trade history analysis JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in {file_path}: {e}")
        return None
    except FileNotFoundError:
        print("Error: File not found: {file_path}")
        return None


def validate_analysis_file(analysis_data, schema, file_path):
    """Validate a trade history analysis file against the schema."""
    try:
        validate(instance=analysis_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def analyze_institutional_quality(analysis_data, file_name):
    """Analyze institutional-grade quality metrics from trade analysis data."""
    quality_metrics = {
        "overall_confidence": None,
        "sample_size_adequacy": None,
        "statistical_significance": None,
        "win_rate": None,
        "profit_factor": None,
        "sample_size": None,
        "statistical_power": None,
        "methodology_compliance": None,
        "institutional_grade": False,
    }

    # Extract analysis metadata
    if "analysis_metadata" in analysis_data:
        metadata = analysis_data["analysis_metadata"]
        quality_metrics["overall_confidence"] = metadata.get("confidence_score", 0)
        quality_metrics["sample_size_adequacy"] = metadata.get("sample_size_adequacy", 0)
        quality_metrics["statistical_significance"] = metadata.get("statistical_significance", 0)

    # Extract sample validation metrics
    if "sample_validation" in analysis_data:
        sample_val = analysis_data["sample_validation"]
        quality_metrics["sample_size"] = sample_val.get("total_trades", 0)
        quality_metrics["statistical_power"] = sample_val.get("statistical_power", 0)

    # Extract performance metrics
    if "statistical_analysis" in analysis_data and "performance_metrics" in analysis_data["statistical_analysis"]:
        perf = analysis_data["statistical_analysis"]["performance_metrics"]
        quality_metrics["win_rate"] = perf.get("win_rate", 0)
        quality_metrics["profit_factor"] = perf.get("profit_factor", 0)

    # Extract quality assessment
    if "analysis_quality_assessment" in analysis_data:
        quality_assess = analysis_data["analysis_quality_assessment"]
        quality_metrics["overall_confidence"] = quality_assess.get(
            "overall_confidence", quality_metrics["overall_confidence"]
        )
        quality_metrics["methodology_compliance"] = quality_assess.get("methodology_compliance", False)

    # Assess institutional grade
    confidence = quality_metrics["overall_confidence"] or 0
    statistical_power = quality_metrics["statistical_power"] or 0
    sample_size = quality_metrics["sample_size"] or 0
    win_rate = quality_metrics["win_rate"] or 0
    profit_factor = quality_metrics["profit_factor"] or 0

    # Institutional grade criteria
    institutional_criteria = [
        confidence >= 0.8,
        statistical_power >= 0.8,
        sample_size >= 10,
        win_rate >= 0.45,
        profit_factor >= 1.0,
    ]

    quality_metrics["institutional_grade"] = sum(institutional_criteria) >= 4  # At least 4 of 5 criteria

    return quality_metrics


def print_quality_assessment(metrics, file_name):
    """Print institutional quality assessment for trade history analysis."""
    print("  📊 Institutional Trading Quality Assessment:")

    # Overall Confidence
    confidence = metrics["overall_confidence"]
    if confidence is not None:
        status = "✅" if confidence >= 0.8 else "⚠️" if confidence >= 0.7 else "❌"
        print(f"     Overall Confidence: {status} {confidence:.3f} (institutional threshold: >0.80)")

    # Sample Size Adequacy
    sample_adequacy = metrics["sample_size_adequacy"]
    if sample_adequacy is not None:
        status = "✅" if sample_adequacy >= 0.8 else "⚠️" if sample_adequacy >= 0.6 else "❌"
        print(f"     Sample Size Adequacy: {status} {sample_adequacy:.3f} (institutional threshold: >0.80)")

    # Statistical Power
    statistical_power = metrics["statistical_power"]
    if statistical_power is not None:
        status = "✅" if statistical_power >= 0.8 else "⚠️" if statistical_power >= 0.7 else "❌"
        print(f"     Statistical Power: {status} {statistical_power:.3f} (institutional minimum: >0.80)")

    # Sample Size
    sample_size = metrics["sample_size"]
    if sample_size is not None:
        status = "✅" if sample_size >= 10 else "❌"
        print(f"     Sample Size: {status} {sample_size} trades (institutional minimum: 10)")

    # Win Rate
    win_rate = metrics["win_rate"]
    if win_rate is not None:
        status = "✅" if win_rate >= 0.45 else "⚠️" if win_rate >= 0.40 else "❌"
        print(f"     Win Rate: {status} {win_rate:.3f} (institutional benchmark: >0.45)")

    # Profit Factor
    profit_factor = metrics["profit_factor"]
    if profit_factor is not None:
        status = "✅" if profit_factor >= 1.0 else "❌"
        print(f"     Profit Factor: {status} {profit_factor:.2f} (institutional threshold: >1.0)")

    # Statistical Significance
    statistical_significance = metrics["statistical_significance"]
    if statistical_significance is not None:
        status = "✅" if statistical_significance >= 0.8 else "⚠️" if statistical_significance >= 0.5 else "❌"
        print("     Statistical Significance: {status} {statistical_significance:.3f}")

    # Methodology Compliance
    methodology_compliance = metrics["methodology_compliance"]
    if methodology_compliance is not None:
        status = "✅" if methodology_compliance else "❌"
        print("     Methodology Compliance: {status} {methodology_compliance}")

    # Institutional Grade
    institutional_grade = metrics["institutional_grade"]
    grade_icon = "🏆" if institutional_grade else "⚠️"
    grade_text = "INSTITUTIONAL GRADE" if institutional_grade else "BELOW INSTITUTIONAL THRESHOLD"
    print("     Quality Grade: {grade_icon} {grade_text}")


def main():
    """Main validation function."""
    print("🔍 Testing Trade History Analysis Schema")
    print("=" * 80)

    # Load schema
    schema = load_schema()
    if not schema:
        sys.exit(1)

    print("✅ Trade history analysis schema loaded successfully")

    # Test files (all available trade history analysis files)
    analysis_dir = Path(__file__).parent.parent / "data" / "outputs" / "trade_history" / "analysis"
    test_files = [
        "live_signals_20250719.json",  # Most recent - institutional grade
        "live_signals_20250718.json",  # Legacy format
        "live_signals_20250717.json",  # Legacy format
        "live_signals_20250716.json",  # Comprehensive legacy format
    ]

    validation_results = []

    print("\\n📁 Testing {len(test_files)} trade history analysis files:")
    print("-" * 80)

    for file_name in test_files:
        file_path = analysis_dir / file_name

        # Load analysis data
        analysis_data = load_analysis_file(file_path)
        if not analysis_data:
            validation_results.append((file_name, False, "Failed to load file"))
            continue

        # Validate against schema
        is_valid, error_message = validate_analysis_file(analysis_data, schema, file_path)
        validation_results.append((file_name, is_valid, error_message))

        # Print immediate result
        status_icon = "✅" if is_valid else "❌"
        print("{status_icon} {file_name}: {'VALID' if is_valid else 'INVALID'}")

        if is_valid:
            # Analyze institutional quality metrics
            quality_metrics = analyze_institutional_quality(analysis_data, file_name)
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

    # Analyze institutional quality for valid files
    institutional_count = 0
    for file_name, is_valid, _ in validation_results:
        if is_valid:
            file_path = analysis_dir / file_name
            analysis_data = load_analysis_file(file_path)
            if analysis_data:
                quality_metrics = analyze_institutional_quality(analysis_data, file_name)
                if quality_metrics["institutional_grade"]:
                    institutional_count += 1

    print("✅ Valid files: {valid_count}/{total_count}")
    print("❌ Invalid files: {total_count - valid_count}/{total_count}")
    print("🏆 Institutional grade files: {institutional_count}/{valid_count}")

    if valid_count == total_count:
        print("\\n🎉 ALL TRADE HISTORY ANALYSIS FILES PASS SCHEMA VALIDATION!")
        print("Schema successfully validates institutional-grade trading analysis requirements.")
        if institutional_count > 0:
            print(f"🏆 {institutional_count} files meet institutional trading standards.")
        print("Ready for production algorithmic trading validation.")
        return 0
    print("\\n⚠️  {total_count - valid_count} files failed validation.")
    print("Schema may need adjustments for legacy format compatibility.")

    # Print detailed errors for failed validations
    print("\\n🔍 DETAILED VALIDATION ERRORS:")
    print("-" * 80)
    for file_name, is_valid, error_message in validation_results:
        if not is_valid:
            print("\\n❌ {file_name}:")
            print("   {error_message}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
