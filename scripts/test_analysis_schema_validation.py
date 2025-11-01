#!/usr/bin/env python3
"""
Test script to validate fundamental analysis analysis JSON files against the schema.
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
    """Load the analysis schema from the schemas directory."""
    schema_path = Path(__file__).parent / "schemas" / "fundamental_analysis_analysis_schema.json"

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
    """Load an analysis JSON file."""
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
    """Validate an analysis file against the schema."""
    try:
        validate(instance=analysis_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def main():
    """Main validation function."""
    print("🔍 Testing Fundamental Analysis Analysis Schema Validation")
    print("=" * 60)

    # Load schema
    schema = load_schema()
    if not schema:
        sys.exit(1)

    print("✅ Schema loaded successfully")

    # Test files (7 most recent)
    analysis_dir = Path(__file__).parent.parent / "data" / "outputs" / "fundamental_analysis" / "analysis"
    test_files = [
        "VTRS_20250725_analysis.json",  # Most recent
        "FANG_20250724_analysis.json",
        "PKG_20250724_analysis.json",
        "TFC_20250724_analysis.json",
        "ADBE_20250723_analysis.json",
        "CMA_20250723_analysis.json",
        "TEAM_20250723_analysis.json",
    ]

    validation_results = []

    print("\n📁 Testing {len(test_files)} analysis files:")
    print("-" * 40)

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

        if not is_valid:
            print("   Error: {error_message}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    valid_count = sum(1 for _, is_valid, _ in validation_results if is_valid)
    total_count = len(validation_results)

    print("✅ Valid files: {valid_count}/{total_count}")
    print("❌ Invalid files: {total_count - valid_count}/{total_count}")

    if valid_count == total_count:
        print("\n🎉 ALL FILES PASS VALIDATION!")
        print("Schema is ready for production use.")
        return 0
    print("\n⚠️  {total_count - valid_count} files failed validation.")
    print("Schema may need adjustments.")

    # Print detailed errors for failed validations
    print("\n🔍 DETAILED ERRORS:")
    print("-" * 40)
    for file_name, is_valid, error_message in validation_results:
        if not is_valid:
            print("\n❌ {file_name}:")
            print("   {error_message}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
