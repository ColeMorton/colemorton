#!/usr/bin/env python3
"""
Data Consolidation Utility

Migrates existing fragmented period-based files to consolidated single-file format.
This tool eliminates the file fragmentation issue and significantly improves performance.

Usage:
    python consolidate_data_files.py [--dry-run] [--symbol SYMBOL] [--backup]
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from historical_data_manager import DataType, HistoricalDataManager, Timeframe


class DataConsolidator:
    """Consolidates fragmented historical data files into optimized single-file format"""

    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.hdm = HistoricalDataManager()
        self.stats = {
            "symbols_processed": 0,
            "files_consolidated": 0,
            "files_removed": 0,
            "space_saved": 0,
            "errors": 0,
        }

    def consolidate_all_data(self, target_symbol: str = None):
        """
        Consolidate all fragmented data files or specific symbol

        Args:
            target_symbol: Optional symbol to consolidate (None = all symbols)
        """
        raw_path = Path("data/raw")
        if not raw_path.exists():
            print("❌ No data/raw directory found")
            return

        # Find all stock symbols with fragmented data
        stocks_path = raw_path / "stocks"
        if not stocks_path.exists():
            print("❌ No stocks directory found")
            return

        symbols = []
        for symbol_dir in stocks_path.iterdir():
            if symbol_dir.is_dir():
                if target_symbol is None or symbol_dir.name == target_symbol.upper():
                    symbols.append(symbol_dir.name)

        if not symbols:
            print("❌ No symbols found" + (f" for {target_symbol}" if target_symbol else ""))
            return

        print("🚀 Starting consolidation for {len(symbols)} symbols")
        print("   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("   Backup: {'Enabled' if self.backup else 'Disabled'}")
        print("=" * 60)

        for symbol in sorted(symbols):
            try:
                self._consolidate_symbol(symbol)
                self.stats["symbols_processed"] += 1
            except Exception:
                print("❌ Error consolidating {symbol}: {e}")
                self.stats["errors"] += 1

        self._print_summary()

    def _consolidate_symbol(self, symbol: str):
        """Consolidate all data types for a specific symbol"""
        print("\n📊 Processing {symbol}...")

        symbol_path = Path("data/raw/stocks") / symbol

        # Find fragmented data directories
        fragmented_dirs = self._find_fragmented_directories(symbol_path)

        if not fragmented_dirs:
            print("   ✅ {symbol}: Already consolidated or no fragmented data found")
            return

        for data_type, timeframe, frag_dir in fragmented_dirs:
            self._consolidate_timeframe_data(symbol, data_type, timeframe, frag_dir)

    def _find_fragmented_directories(self, symbol_path: Path) -> list[tuple]:
        """Find directories with fragmented period-based files"""
        fragmented = []

        for item in symbol_path.iterdir():
            if not item.is_dir():
                continue

            # Check for period-based fragmentation patterns
            dir_name = item.name

            # Price data fragmentation patterns
            if dir_name in ["daily", "weekly", "monthly", "quarterly", "yearly"]:
                # Check if it contains period-based subdirectories
                period_files = list(item.glob("*.csv")) + list(item.glob("*.json"))
                if len(period_files) > 1:  # Multiple period files = fragmented
                    data_type = DataType.STOCK_DAILY_PRICES
                    timeframe_map = {
                        "daily": Timeframe.DAILY,
                        "weekly": Timeframe.WEEKLY,
                        "monthly": Timeframe.MONTHLY,
                        "quarterly": Timeframe.QUARTERLY,
                        "yearly": Timeframe.YEARLY,
                    }
                    timeframe = timeframe_map[dir_name]
                    fragmented.append((data_type, timeframe, item))

            # Old structure patterns (e.g., daily_prices, weekly_prices)
            elif dir_name.endswith("_prices"):
                timeframe_name = dir_name.replace("_prices", "")
                if timeframe_name in [
                    "daily",
                    "weekly",
                    "monthly",
                    "quarterly",
                    "yearly",
                ]:
                    data_type = DataType.STOCK_DAILY_PRICES
                    timeframe_map = {
                        "daily": Timeframe.DAILY,
                        "weekly": Timeframe.WEEKLY,
                        "monthly": Timeframe.MONTHLY,
                        "quarterly": Timeframe.QUARTERLY,
                        "yearly": Timeframe.YEARLY,
                    }
                    timeframe = timeframe_map[timeframe_name]
                    fragmented.append((data_type, timeframe, item))

            # Other data types with potential fragmentation
            elif dir_name in ["fundamentals", "financials", "news_sentiment"]:
                period_files = list(item.glob("*.json"))
                if len(period_files) > 1:
                    if dir_name == "fundamentals":
                        data_type = DataType.STOCK_FUNDAMENTALS
                    elif dir_name == "financials":
                        data_type = DataType.STOCK_FINANCIALS
                    else:
                        data_type = DataType.STOCK_NEWS_SENTIMENT
                    fragmented.append((data_type, Timeframe.DAILY, item))

        return fragmented

    def _consolidate_timeframe_data(self, symbol: str, data_type: DataType, timeframe: Timeframe, frag_dir: Path):
        """Consolidate fragmented files for a specific timeframe"""
        print("   🔄 Consolidating {symbol} {timeframe.value} {data_type.value}...")

        # Collect all fragmented files
        csv_files = list(frag_dir.rglob("*.csv"))
        json_files = [f for f in frag_dir.rglob("*.json") if not f.name.endswith(".meta.json")]
        meta_files = list(frag_dir.rglob("*.meta.json"))

        all_files = csv_files + json_files + meta_files

        if not all_files:
            print("      ⚠️  No files to consolidate")
            return

        print(f"      📄 Found {len(csv_files)} CSV, {len(json_files)} JSON, {len(meta_files)} metadata files")

        # Backup if requested
        if self.backup and not self.dry_run:
            self._backup_directory(frag_dir)

        # Consolidate based on data type
        if data_type == DataType.STOCK_DAILY_PRICES and csv_files:
            consolidated_count = self._consolidate_csv_files(symbol, data_type, timeframe, csv_files, meta_files)
        else:
            consolidated_count = self._consolidate_json_files(symbol, data_type, timeframe, json_files, meta_files)

        if consolidated_count > 0:
            # Calculate space savings
            original_size = sum(f.stat().st_size for f in all_files)

            # Remove fragmented files after successful consolidation
            if not self.dry_run:
                self._remove_fragmented_files(all_files)
                self._remove_empty_directories(frag_dir)

            self.stats["files_consolidated"] += consolidated_count
            self.stats["files_removed"] += len(all_files)
            self.stats["space_saved"] += original_size

            print(f"      ✅ Consolidated {len(all_files)} files → 2 files ({original_size:,} bytes)")
        else:
            print("      ❌ Consolidation failed")

    def _consolidate_csv_files(
        self,
        symbol: str,
        data_type: DataType,
        timeframe: Timeframe,
        csv_files: list[Path],
        meta_files: list[Path],
    ) -> int:
        """Consolidate CSV files into single consolidated file"""
        all_records = []
        sources = set()

        # Read all CSV files and combine records
        for csv_file in csv_files:
            try:
                records = self.hdm._deserialize_from_csv(csv_file)
                all_records.extend(records)

                # Find corresponding metadata
                meta_file = None
                for mf in meta_files:
                    if mf.parent == csv_file.parent and mf.stem.startswith(csv_file.stem):
                        meta_file = mf
                        break

                if meta_file and meta_file.exists():
                    with open(meta_file) as f:
                        meta = json.load(f)
                        if meta.get("source"):
                            sources.add(meta["source"])

            except Exception:
                print("         ⚠️  Failed to read {csv_file}: {e}")
                continue

        if not all_records:
            return 0

        # Remove duplicates and sort by date
        seen_dates = set()
        unique_records = []
        for record in all_records:
            date_key = record.get("date")
            if date_key and date_key not in seen_dates:
                seen_dates.add(date_key)
                unique_records.append(record)

        unique_records.sort(key=lambda x: x.get("date", ""))

        if self.dry_run:
            print("         📊 Would consolidate {len(unique_records)} unique records")
            return len(csv_files)

        # Store consolidated data using the new system
        consolidated_data = {"symbol": symbol, "data": unique_records}

        success = self.hdm.store_data(
            symbol=symbol,
            data=consolidated_data,
            data_type=data_type,
            timeframe=timeframe,
            source=", ".join(sources) if sources else "consolidated",
        )

        return len(csv_files) if success else 0

    def _consolidate_json_files(
        self,
        symbol: str,
        data_type: DataType,
        timeframe: Timeframe,
        json_files: list[Path],
        meta_files: list[Path],
    ) -> int:
        """Consolidate JSON files (for non-time-series data)"""
        if not json_files:
            return 0

        # For non-time-series data, take the most recent file
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(latest_file) as f:
                data = json.load(f)

            if self.dry_run:
                print(f"         📊 Would consolidate latest JSON data from {latest_file.name}")
                return len(json_files)

            # Store consolidated data
            success = self.hdm.store_data(
                symbol=symbol,
                data=data,
                data_type=data_type,
                timeframe=timeframe,
                source="consolidated",
            )

            return len(json_files) if success else 0

        except Exception:
            print("         ❌ Failed to consolidate JSON files: {e}")
            return 0

    def _backup_directory(self, directory: Path):
        """Create backup of directory before consolidation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = directory.with_suffix(f".backup_{timestamp}")

        try:
            shutil.copytree(directory, backup_dir)
            print("      💾 Backup created: {backup_dir}")
        except Exception:
            print("      ⚠️  Backup failed: {e}")

    def _remove_fragmented_files(self, files: list[Path]):
        """Remove fragmented files after successful consolidation"""
        for file_path in files:
            try:
                file_path.unlink()
            except Exception:
                print("      ⚠️  Failed to remove {file_path}: {e}")

    def _remove_empty_directories(self, directory: Path):
        """Remove empty directories after file removal"""
        try:
            # Remove empty subdirectories first
            for subdir in directory.rglob("*"):
                if subdir.is_dir() and not any(subdir.iterdir()):
                    subdir.rmdir()

            # Remove main directory if empty
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                print("      🗑️  Removed empty directory: {directory}")
        except Exception:
            print("      ⚠️  Failed to clean directories: {e}")

    def _print_summary(self):
        """Print consolidation summary"""
        print("\n" + "=" * 60)
        print("📊 CONSOLIDATION SUMMARY")
        print("=" * 60)
        print("   Symbols processed: {self.stats['symbols_processed']}")
        print("   Files consolidated: {self.stats['files_consolidated']}")
        print("   Files removed: {self.stats['files_removed']}")
        print("   Space saved: {self.stats['space_saved']:,} bytes")
        print("   Errors: {self.stats['errors']}")

        if self.stats["symbols_processed"] > 0 and self.stats["files_removed"] > 0:
            efficiency = (
                (self.stats["files_removed"] - self.stats["files_consolidated"] * 2) / self.stats["files_removed"] * 100
            )
            print("   File reduction: {efficiency:.1f}%")

        print(f"\n🎉 Consolidation {'simulation' if self.dry_run else 'completed'} successfully!")


def main():
    parser = argparse.ArgumentParser(description="Consolidate fragmented historical data files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--symbol", help="Consolidate specific symbol only")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backups")

    args = parser.parse_args()

    consolidator = DataConsolidator(dry_run=args.dry_run, backup=not args.no_backup)

    consolidator.consolidate_all_data(args.symbol)


if __name__ == "__main__":
    main()
