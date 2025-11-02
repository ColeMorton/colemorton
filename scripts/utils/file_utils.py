"""
File operation utilities.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd


class FileUtils:
    """Utilities for file operations."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def ensure_directory(self, dir_path: str | Path) -> Path:
        """Ensure directory exists, create if necessary."""
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def atomic_write(self, content: str, file_path: str | Path) -> Path:
        """Write content to file atomically using temporary file."""
        path = Path(file_path)
        temp_path = path.with_suffix(path.suffix + ".tmp")

        try:
            # Ensure directory exists
            self.ensure_directory(path.parent)

            # Write to temporary file
            with open(temp_path, "w") as f:
                f.write(content)

            # Atomic rename
            temp_path.rename(path)
            self.logger.info(f"File written atomically to {path}")
            return path

        except Exception as e:
            # Cleanup temporary file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def backup_file(self, file_path: str | Path, backup_dir: str | Path | None = None) -> Path:
        """Create backup of file with timestamp."""
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {file_path}")

        # Determine backup directory
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = source_path.parent / "backups"

        self.ensure_directory(backup_path)

        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_file_path = backup_path / backup_filename

        # Copy file
        shutil.copy2(source_path, backup_file_path)
        self.logger.info(f"Backup created: {backup_file_path}")
        return backup_file_path

    def clean_old_files(self, directory: str | Path, pattern: str = "*", keep_count: int = 5) -> list[Path]:
        """Clean old files in directory, keeping only the most recent."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []

        # Get files matching pattern, sorted by modification time (newest first)
        files = sorted(dir_path.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)

        # Files to remove (everything after keep_count)
        files_to_remove = files[keep_count:]

        removed_files = []
        for file_path in files_to_remove:
            if file_path.is_file():
                file_path.unlink()
                removed_files.append(file_path)
                self.logger.info(f"Removed old file: {file_path}")

        return removed_files

    def get_timestamp_filename(self, base_name: str, extension: str = "", format_str: str = "%Y-%m-%d_%H-%M-%S") -> str:
        """Generate timestamped filename."""
        timestamp = datetime.now().strftime(format_str)
        if extension and not extension.startswith("."):
            extension = "." + extension
        return f"{base_name}_{timestamp}{extension}"

    def read_dataframe(self, file_path: str | Path) -> pd.DataFrame:
        """Read DataFrame from various file formats."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        suffix = path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(path)
        if suffix == ".parquet":
            return pd.read_parquet(path)
        if suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        if suffix == ".json":
            return pd.read_json(path)
        raise ValueError(f"Unsupported file format: {suffix}")

    def write_dataframe(
        self,
        df: pd.DataFrame,
        file_path: str | Path,
        format_override: str | None = None,
    ) -> Path:
        """Write DataFrame to file, format determined by extension or override."""
        path = Path(file_path)
        self.ensure_directory(path.parent)

        # Determine format
        if format_override:
            file_format = format_override.lower()
        else:
            file_format = path.suffix.lower().lstrip(".")

        if file_format == "csv":
            df.to_csv(path, index=False)
        elif file_format == "parquet":
            df.to_parquet(path, index=False)
        elif file_format in ["xlsx", "excel"]:
            df.to_excel(path, index=False)
        elif file_format == "json":
            df.to_json(path, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported output format: {file_format}")

        self.logger.info(f"DataFrame written to {path} in {file_format} format")
        return path
