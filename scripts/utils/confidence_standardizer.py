"""
Confidence Score Standardization Utility

Standardizes confidence scoring across industry analysis files to consistent 0.0-1.0 decimal format.
Handles conversion from various formats:
- "9.1/10.0" -> "0.91"
- "0.91" (already correct)
- 9.1 (numeric) -> "0.91"
"""

import json
import re
from pathlib import Path
from typing import Any


class ConfidenceStandardizer:
    """Utility to standardize confidence scoring formats"""

    def __init__(self):
        self.conversion_count = 0
        self.files_processed = 0

    def normalize_confidence_value(self, value: str | float | int) -> str:
        """Convert various confidence formats to 0.0-1.0 decimal string"""

        if isinstance(value, str):
            # Handle "X.X/10.0" format
            if "/10.0" in value:
                try:
                    numeric_part = float(value.split("/10.0")[0])
                    normalized = numeric_part / 10.0
                    self.conversion_count += 1
                    return f"{normalized:.2f}"
                except ValueError:
                    return value

            # Handle "X.X/10" format
            elif "/10" in value and "/10.0" not in value:
                try:
                    numeric_part = float(value.split("/10")[0])
                    normalized = numeric_part / 10.0
                    self.conversion_count += 1
                    return f"{normalized:.2f}"
                except ValueError:
                    return value

            # Already in correct format (0.XX)
            elif re.match(r"^0\.\d{1,2}$", value):
                return value

            # Handle raw decimal string
            else:
                try:
                    numeric_value = float(value)
                    if numeric_value > 1.0:
                        # Assume it's on 10-point scale
                        normalized = numeric_value / 10.0
                        self.conversion_count += 1
                        return f"{normalized:.2f}"
                    return f"{numeric_value:.2f}"
                except ValueError:
                    return value

        elif isinstance(value, (int, float)):
            if value > 1.0:
                # Assume it's on 10-point scale
                normalized = value / 10.0
                self.conversion_count += 1
                return f"{normalized:.2f}"
            return f"{value:.2f}"

        return str(value)

    def standardize_dict(self, data: Any) -> Any:
        """Recursively standardize confidence scores in a dictionary"""

        if not isinstance(data, dict):
            return data

        result = {}

        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.standardize_dict(value)
            elif isinstance(value, list):
                standardized_items = []
                for item in value:
                    if isinstance(item, dict):
                        standardized_items.append(self.standardize_dict(item))
                    else:
                        standardized_items.append(item)
                result[key] = standardized_items
            elif "confidence" in key.lower() or "score" in key.lower():
                result[key] = self.normalize_confidence_value(value)
            else:
                result[key] = value

        return result

    def standardize_file(self, file_path: str) -> bool:
        """Standardize confidence scores in a JSON file"""

        try:
            with open(file_path) as f:
                data = json.load(f)

            original_count = self.conversion_count
            standardized_data = self.standardize_dict(data)
            conversions_made = self.conversion_count - original_count

            if conversions_made > 0:
                # Write back standardized data
                with open(file_path, "w") as f:
                    json.dump(standardized_data, f, indent=2)

                print(f"Standardized {conversions_made} confidence scores in {file_path}")
                self.files_processed += 1
                return True
            print("No confidence scores to standardize in {file_path}")
            return False

        except Exception:
            print("Error processing {file_path}: {e}")
            return False

    def standardize_directory(self, directory_path: str, file_pattern: str = "*.json") -> dict[str, Any]:
        """Standardize confidence scores in all matching files in a directory"""

        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        files_found = list(directory.glob(file_pattern))

        if not files_found:
            print("No files matching {file_pattern} found in {directory_path}")
            return {"files_processed": 0, "conversions_made": 0, "files_found": 0}

        initial_conversions = self.conversion_count
        initial_files = self.files_processed

        for file_path in files_found:
            self.standardize_file(str(file_path))

        return {
            "files_found": len(files_found),
            "files_processed": self.files_processed - initial_files,
            "conversions_made": self.conversion_count - initial_conversions,
            "total_conversions": self.conversion_count,
            "total_files_processed": self.files_processed,
        }


def standardize_industry_analysis_files(
    base_directory: str = "./data/outputs/industry_analysis",
) -> dict[str, Any]:
    """Standardize confidence scores across all industry analysis files"""

    standardizer = ConfidenceStandardizer()
    results = {}

    # Process validation files
    validation_dir = Path(base_directory) / "validation"
    if validation_dir.exists():
        results["validation"] = standardizer.standardize_directory(str(validation_dir))

    # Process analysis files
    analysis_dir = Path(base_directory) / "analysis"
    if analysis_dir.exists():
        results["analysis"] = standardizer.standardize_directory(str(analysis_dir))

    # Process discovery files
    discovery_dir = Path(base_directory) / "discovery"
    if discovery_dir.exists():
        results["discovery"] = standardizer.standardize_directory(str(discovery_dir))

    return {
        "summary": {
            "total_files_processed": standardizer.files_processed,
            "total_conversions_made": standardizer.conversion_count,
        },
        "by_directory": results,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "./data/outputs/industry_analysis"

    print("Standardizing confidence scores in {directory}")
    results = standardize_industry_analysis_files(directory)

    print("\nStandardization Results:")
    print(json.dumps(results, indent=2))
