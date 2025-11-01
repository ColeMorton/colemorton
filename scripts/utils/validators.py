"""
Data validation utilities.
"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd


class ValidationError(Exception):
    """Custom exception for validation failures."""


class DataValidator:
    """Validates data integrity and schema compliance."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def validate_file_exists(self, file_path: str | Path) -> Path:
        """Validate that a file exists."""
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        return path

    def validate_directory_exists(self, dir_path: str | Path) -> Path:
        """Validate that a directory exists."""
        path = Path(dir_path)
        if not path.exists():
            raise ValidationError(f"Directory does not exist: {dir_path}")
        if not path.is_dir():
            raise ValidationError(f"Path is not a directory: {dir_path}")
        return path

    def validate_config_schema(self, config: dict[str, Any], required_keys: list[str]) -> None:
        """Validate that config contains required keys."""
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValidationError(f"Missing required config keys: {missing_keys}")

    def validate_dataframe_schema(self, df: pd.DataFrame, required_columns: list[str]) -> None:
        """Validate that DataFrame contains required columns."""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(f"Missing required columns: {missing_columns}")

    def validate_dataframe_not_empty(self, df: pd.DataFrame) -> None:
        """Validate that DataFrame is not empty."""
        if df.empty:
            raise ValidationError("DataFrame is empty")

    def validate_no_null_values(self, df: pd.DataFrame, columns: list[str] | None = None) -> None:
        """Validate that specified columns contain no null values."""
        check_columns = columns if columns else list(df.columns)

        for col in check_columns:
            if col not in df.columns:
                raise ValidationError(f"Column not found: {col}")

            null_count = df[col].isnull().sum()
            if null_count > 0:
                raise ValidationError(f"Column '{col}' contains {null_count} null values")

    def validate_numeric_range(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> None:
        """Validate that numeric column values are within specified range."""
        if column not in df.columns:
            raise ValidationError(f"Column not found: {column}")

        out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
        if not out_of_range.empty:
            raise ValidationError(
                f"Column '{column}' has {len(out_of_range)} values outside range [{min_val}, {max_val}]"
            )


def validate_config_structure(config: dict[str, Any]) -> None:
    """Validate basic configuration structure."""
    validator = DataValidator()

    # Standard config sections
    required_sections = ["metadata", "input", "output"]
    validator.validate_config_schema(config, required_sections)

    # Metadata validation
    metadata = config.get("metadata", {})
    required_metadata = ["name", "version"]
    validator.validate_config_schema(metadata, required_metadata)

    # Output validation
    output = config.get("output", {})
    required_output = ["file_path"]
    validator.validate_config_schema(output, required_output)
