#!/usr/bin/env python3
"""
Historical Data Manager

Manages long-term storage and organization of financial data in ./data/raw/
for comprehensive historical analysis and discovery. Provides organized,
file-based storage with multiple timeframes and data types.
"""

import csv
import hashlib
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class DataType(Enum):
    """Supported historical data types"""

    STOCK_DAILY_PRICES = "daily_prices"
    STOCK_FINANCIALS = "financials"
    STOCK_FUNDAMENTALS = "fundamentals"
    STOCK_NEWS_SENTIMENT = "news_sentiment"
    STOCK_OPTIONS = "options"
    ETF_HOLDINGS = "etf_holdings"
    ETF_FLOWS = "etf_flows"
    INSIDER_TRANSACTIONS = "insider_transactions"
    TECHNICAL_INDICATORS = "technical_indicators"
    CORPORATE_ACTIONS = "corporate_actions"
    SECTOR_PERFORMANCE = "performance"
    SECTOR_CONSTITUENTS = "constituents"
    INDUSTRY_ANALYSIS = "analysis"
    INDUSTRY_METRICS = "metrics"
    ECONOMIC_INDICATORS = "indicators"
    ECONOMIC_REPORTS = "reports"
    MARKET_INDICES = "indices"
    DERIVATIVES = "derivatives"


class Timeframe(Enum):
    """Supported data organization timeframes"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class HistoricalDataManager:
    """
    Manages historical financial data storage with organized file structure

    Features:
    - Hierarchical data organization by type, symbol, and date
    - Multiple timeframe support (daily to yearly)
    - Automatic deduplication and validation
    - Data quality tracking and metadata
    - Integration with existing cache systems
    """

    def __init__(self, base_path: Path | None = None, config_path: str | None = None):
        """
        Initialize Historical Data Manager

        Args:
            base_path: Base directory for raw data storage (defaults to ./data/raw/)
            config_path: Path to historical data configuration file
        """
        self.base_path = base_path or Path(__file__).parent.parent.parent / "data" / "raw"
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()

        # Initialize directory structure
        self._initialize_directories()

        # Data quality tracking
        self.metadata_file = self.base_path / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_config(self, config_path: str | None = None) -> dict[str, Any]:
        """Load historical data configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "services" / "cache_config.yaml"

        try:
            with open(config_path) as f:
                full_config = yaml.safe_load(f)
                # Extract historical data config or use defaults
                return full_config.get("historical_storage", self._default_config())
        except (FileNotFoundError, Exception) as e:
            if hasattr(self, "logger"):
                self.logger.warning(f"Config not found at {config_path}, using defaults: {e}")
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Default configuration for historical data storage"""
        return {
            "enabled": True,
            "compression": True,
            "deduplication": True,
            "data_retention_days": {
                "daily_data": 365 * 5,  # 5 years
                "financial_statements": 365 * 10,  # 10 years
                "economic_data": 365 * 20,  # 20 years
            },
            "data_quality": {
                "validate_on_store": True,
                "require_metadata": True,
                "check_duplicates": True,
            },
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for historical data manager"""
        logger = logging.getLogger("historical_data_manager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _initialize_directories(self) -> None:
        """Initialize the directory structure for raw data storage"""
        directories = [
            "stocks",
            "etfs",
            "sectors",
            "industries",
            "economic/indicators",
            "economic/reports",
            "market/indices",
            "market/derivatives",
        ]

        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> dict[str, Any]:
        """Load metadata tracking file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                self.logger.warning("Corrupted metadata file, creating new one")

        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_files": 0,
            "data_types": {},
            "symbols": {},
            "date_ranges": {},
        }

    def _save_global_metadata(self) -> None:
        """Save global metadata tracking information"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")

    def _get_file_path(
        self,
        symbol: str,
        data_type: DataType,
        date: str | datetime = None,
        timeframe: Timeframe = Timeframe.DAILY,
        file_type: str = "data",  # "data" for CSV, "meta" for JSON metadata
    ) -> Path:
        """
        Generate consolidated file path - one file per stock+timeframe combination

        New optimized structure eliminates file fragmentation:
        - data/raw/stocks/AAPL/daily.csv (all daily data)
        - data/raw/stocks/AAPL/weekly.csv (all weekly data)
        - data/raw/stocks/AAPL/daily.meta.json (metadata)
        - data/raw/stocks/AAPL/weekly.meta.json (metadata)

        Args:
            symbol: Stock symbol, sector, or industry name
            data_type: Type of data being stored
            date: Date of the data (unused in consolidated approach)
            timeframe: Data timeframe organization
            file_type: "data" for CSV files, "meta" for JSON metadata

        Returns:
            Path object for the consolidated data or metadata file
        """
        # Determine base category
        if data_type in [
            DataType.STOCK_DAILY_PRICES,
            DataType.STOCK_FINANCIALS,
            DataType.STOCK_FUNDAMENTALS,
            DataType.STOCK_NEWS_SENTIMENT,
            DataType.STOCK_OPTIONS,
            DataType.INSIDER_TRANSACTIONS,
            DataType.TECHNICAL_INDICATORS,
            DataType.CORPORATE_ACTIONS,
        ]:
            category = "stocks"
        elif data_type in [DataType.ETF_HOLDINGS, DataType.ETF_FLOWS]:
            category = "etfs"
        elif data_type in [DataType.SECTOR_PERFORMANCE, DataType.SECTOR_CONSTITUENTS]:
            category = "sectors"
        elif data_type in [DataType.INDUSTRY_ANALYSIS, DataType.INDUSTRY_METRICS]:
            category = "industries"
        elif data_type in [DataType.ECONOMIC_INDICATORS, DataType.ECONOMIC_REPORTS]:
            category = "economic"
        elif data_type in [DataType.MARKET_INDICES, DataType.DERIVATIVES]:
            category = "market"
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        # Generate consolidated filename based on timeframe and data type
        if data_type == DataType.STOCK_DAILY_PRICES:
            # Price data: single file per timeframe
            base_name = timeframe.value.lower()
        else:
            # Non-price data: single file per data type
            base_name = data_type.value

        # Determine file extension
        if file_type == "meta":
            filename = f"{base_name}.meta.json"
        elif data_type == DataType.STOCK_DAILY_PRICES:
            # Time series price data uses CSV for optimal performance
            filename = f"{base_name}.csv"
        else:
            # Other data types use JSON for complex structures
            filename = f"{base_name}.json"

        return self.base_path / category / symbol.upper() / filename

    def _generate_data_hash(self, data: dict[str, Any]) -> str:
        """Generate hash for deduplication"""
        # Remove metadata fields that shouldn't affect deduplication
        clean_data = {k: v for k, v in data.items() if k not in ["timestamp", "stored_at", "source_request_id"]}
        data_str = json.dumps(clean_data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _validate_data(self, data: dict[str, Any], data_type: DataType) -> bool:
        """Validate data quality before storage"""
        data_quality_config = self.config.get("data_quality", {})
        if not data_quality_config.get("validate_on_store", True):
            return True

        # Basic validation
        if not isinstance(data, dict) or not data:
            return False

        # Type-specific validation
        if data_type == DataType.STOCK_DAILY_PRICES:
            # Handle Yahoo Finance data format: {"symbol": "TSLA", "data": [{"Date": ..., "Open": ...}]}
            if "symbol" in data and "data" in data:
                # Validate nested data array from Yahoo Finance
                if isinstance(data["data"], list) and data["data"]:
                    first_record = data["data"][0]
                    price_fields = [
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume",
                    ]  # Yahoo Finance format
                    date_fields = ["Date"]  # Yahoo Finance uses "Date"
                    return any(field in first_record for field in date_fields) and any(
                        field in first_record for field in price_fields
                    )

            # Handle direct price data format: {"symbol": "TSLA", "date": "2025-01-01", "open": 150.0}
            required_fields = ["symbol", "date"]
            price_fields = [
                "open",
                "high",
                "low",
                "close",
                "volume",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            return all(field in data for field in required_fields) and any(field in data for field in price_fields)
        if data_type == DataType.STOCK_FUNDAMENTALS:
            # Handle stock info/quote data with fundamental information
            fundamental_fields = [
                "market_cap",
                "pe_ratio",
                "sector",
                "industry",
                "current_price",
                "name",
            ]
            return "symbol" in data and any(field in data for field in fundamental_fields)
        if data_type == DataType.STOCK_FINANCIALS:
            return "symbol" in data and (
                "revenue" in data
                or "net_income" in data
                or "total_assets" in data
                or "income_statement" in data
                or "balance_sheet" in data
                or "cash_flow" in data
            )
        if data_type == DataType.STOCK_OPTIONS:
            # Options data should have strike, expiry, option type, and pricing info
            options_fields = [
                "strike",
                "expiry",
                "option_type",
                "bid",
                "ask",
                "last_price",
                "implied_volatility",
            ]
            return "symbol" in data and "date" in data and any(field in data for field in options_fields)
        if data_type == DataType.ETF_HOLDINGS:
            # ETF holdings should have holdings list or constituent information
            return "symbol" in data and ("holdings" in data or "constituents" in data or "top_holdings" in data)
        if data_type == DataType.ETF_FLOWS:
            # ETF flows should have flow amounts and dates
            return "symbol" in data and "date" in data and ("net_flow" in data or "inflow" in data or "outflow" in data)
        if data_type == DataType.INSIDER_TRANSACTIONS:
            # Insider transactions should have transaction details
            insider_fields = [
                "insider_name",
                "transaction_type",
                "shares",
                "price",
                "transaction_date",
            ]
            return "symbol" in data and any(field in data for field in insider_fields)
        if data_type == DataType.TECHNICAL_INDICATORS:
            # Technical indicators should have indicator name and value
            return (
                "symbol" in data
                and "date" in data
                and ("indicator_name" in data or "sma" in data or "rsi" in data or "macd" in data)
            )
        if data_type == DataType.CORPORATE_ACTIONS:
            # Corporate actions should have action type and details
            action_fields = [
                "action_type",
                "ex_date",
                "record_date",
                "split_ratio",
                "dividend_amount",
            ]
            return "symbol" in data and any(field in data for field in action_fields)
        if data_type in [DataType.ECONOMIC_INDICATORS, DataType.ECONOMIC_REPORTS]:
            return "date" in data and "value" in data

        return True  # Default validation passes

    def _serialize_to_csv(self, data_records: list[dict[str, Any]], file_path: Path) -> bool:
        """
        Serialize time series data to CSV format for optimal performance

        Args:
            data_records: List of data records to write
            file_path: Path to CSV file

        Returns:
            True if successful, False otherwise
        """
        if not data_records:
            return False

        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract field names from first record
            first_record = data_records[0]
            fieldnames = ["date", "open", "high", "low", "close", "volume"]

            # Add any additional fields that exist (like adjusted_close)
            additional_fields = [key for key in first_record.keys() if key not in fieldnames and key not in ["symbol"]]
            fieldnames.extend(sorted(additional_fields))

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for record in data_records:
                    # Create row dict with only the needed fields
                    row = {field: record.get(field, "") for field in fieldnames}
                    writer.writerow(row)

            self.logger.debug(f"Wrote {len(data_records)} records to CSV: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to write CSV file {file_path}: {e}")
            return False

    def _deserialize_from_csv(self, file_path: Path) -> list[dict[str, Any]]:
        """
        Deserialize time series data from CSV format

        Args:
            file_path: Path to CSV file

        Returns:
            List of data records, empty list if failed
        """
        if not file_path.exists():
            return []

        try:
            records = []
            with open(file_path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    # Convert string values to appropriate types
                    record = {}
                    for key, value in row.items():
                        if key == "date":
                            record[key] = value  # Keep as string for now
                        elif key in ["open", "high", "low", "close", "adjusted_close"]:
                            try:
                                record[key] = float(value) if value else 0.0
                            except ValueError:
                                record[key] = 0.0
                        elif key == "volume":
                            try:
                                record[key] = int(float(value)) if value else 0
                            except ValueError:
                                record[key] = 0
                        else:
                            record[key] = value

                    records.append(record)

            self.logger.debug(f"Read {len(records)} records from CSV: {file_path}")
            return records

        except Exception as e:
            self.logger.error(f"Failed to read CSV file {file_path}: {e}")
            return []

    def _save_metadata(self, metadata: dict[str, Any], file_path: Path) -> bool:
        """
        Save metadata to JSON file

        Args:
            metadata: Metadata dictionary
            file_path: Path to metadata file

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, default=str)

            return True

        except Exception as e:
            self.logger.error(f"Failed to save metadata {file_path}: {e}")
            return False

    def store_data(
        self,
        symbol: str,
        data: dict[str, Any],
        data_type: DataType,
        date: str | datetime | None = None,
        timeframe: Timeframe = Timeframe.DAILY,
        source: str | None = None,
    ) -> bool:
        """
        Store historical data using hybrid CSV+JSON format for optimal performance

        Args:
            symbol: Stock symbol, sector, or industry identifier
            data: Data to store
            data_type: Type of data being stored
            date: Data date (defaults to current timestamp)
            timeframe: Organization timeframe
            source: Data source identifier

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.config["enabled"]:
            return False

        # Validate data quality first
        if not self._validate_data(data, data_type):
            self.logger.warning(f"Data validation failed for {symbol} {data_type.value}")
            return False

        # Handle nested data format with multiple records (Yahoo Finance format)
        if "data" in data and isinstance(data["data"], list) and data_type == DataType.STOCK_DAILY_PRICES:
            return self._store_time_series_data(symbol, data, data_type, timeframe, source)

        # Handle single record or other data types
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.fromisoformat(date.replace("Z", "+00:00"))

        return self._store_single_record(symbol, data, data_type, date, timeframe, source)

    def _store_time_series_data(
        self,
        symbol: str,
        data: dict[str, Any],
        data_type: DataType,
        timeframe: Timeframe,
        source: str | None,
    ) -> bool:
        """
        Store time series data using consolidated CSV format with deduplication

        New approach: Single CSV file per stock+timeframe with append-based storage

        Args:
            symbol: Stock symbol
            data: Data containing list of records
            data_type: Type of data (should be STOCK_DAILY_PRICES)
            timeframe: Data timeframe
            source: Data source identifier

        Returns:
            True if stored successfully, False otherwise
        """
        if not data.get("data") or not isinstance(data["data"], list):
            return False

        raw_records = data["data"]
        if not raw_records:
            return False

        # Get consolidated file paths
        data_file_path = self._get_file_path(symbol, data_type, None, timeframe, "data")
        meta_file_path = self._get_file_path(symbol, data_type, None, timeframe, "meta")

        # Ensure directories exist
        data_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Normalize incoming records
        new_records = []
        for record in raw_records:
            try:
                # Extract and parse date
                record_date = None
                if "Date" in record:
                    date_value = record["Date"]
                    if hasattr(date_value, "strftime"):
                        record_date = date_value
                    else:
                        record_date = datetime.strptime(str(date_value)[:10], "%Y-%m-%d")
                elif "date" in record:
                    record_date = datetime.strptime(record["date"], "%Y-%m-%d")

                if record_date is None:
                    continue

                # Normalize record format
                normalized_record = {
                    "date": record_date.strftime("%Y-%m-%d"),
                    "open": float(record.get("Open", record.get("open", 0))),
                    "high": float(record.get("High", record.get("high", 0))),
                    "low": float(record.get("Low", record.get("low", 0))),
                    "close": float(record.get("Close", record.get("close", 0))),
                    "volume": int(record.get("Volume", record.get("volume", 0))),
                }

                # Add adjusted_close if available
                if "Adj Close" in record or "adjusted_close" in record:
                    normalized_record["adjusted_close"] = float(
                        record.get(
                            "Adj Close",
                            record.get("adjusted_close", normalized_record["close"]),
                        )
                    )

                new_records.append(normalized_record)

            except Exception as e:
                self.logger.warning(f"Failed to process record for {symbol}: {e}")
                continue

        if not new_records:
            return False

        # Append new records to consolidated file with deduplication
        return self._append_to_consolidated_csv(
            data_file_path,
            meta_file_path,
            new_records,
            symbol,
            data_type,
            timeframe,
            source,
        )

    def _append_to_consolidated_csv(
        self,
        data_file_path: Path,
        meta_file_path: Path,
        new_records: list[dict[str, Any]],
        symbol: str,
        data_type: DataType,
        timeframe: Timeframe,
        source: str | None,
    ) -> bool:
        """
        Append new records to consolidated CSV file with efficient deduplication

        Args:
            data_file_path: Path to consolidated CSV file
            meta_file_path: Path to metadata file
            new_records: New records to append
            symbol: Stock symbol
            data_type: Data type
            timeframe: Data timeframe
            source: Data source

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read existing records for deduplication
            existing_records = []
            existing_dates = set()

            if data_file_path.exists():
                existing_records = self._deserialize_from_csv(data_file_path)
                existing_dates = {record["date"] for record in existing_records}

            # Filter out duplicates
            unique_new_records = []
            for record in new_records:
                if record["date"] not in existing_dates:
                    unique_new_records.append(record)
                    existing_dates.add(record["date"])

            if not unique_new_records:
                self.logger.debug(f"No new records to append for {symbol} {timeframe.value}")
                return True

            # Combine and sort all records
            all_records = existing_records + unique_new_records
            all_records.sort(key=lambda x: x["date"])

            # Write consolidated CSV file
            if self._serialize_to_csv(all_records, data_file_path):
                # Update metadata
                data_hash = self._generate_data_hash({"records": all_records})
                metadata = self._create_consolidated_metadata(
                    symbol, data_type, timeframe, len(all_records), data_hash, source
                )

                if self._save_metadata(metadata, meta_file_path):
                    self.logger.info(
                        f"Appended {len(unique_new_records)} new records to {symbol} {timeframe.value} (total: {len(all_records)})"
                    )

                    # Update global metadata
                    self._update_metadata(symbol, data_type, datetime.now(), data_file_path)
                    return True
                self.logger.error(f"Failed to save metadata for {symbol} {timeframe.value}")
            else:
                self.logger.error(f"Failed to write consolidated CSV for {symbol} {timeframe.value}")

            return False

        except Exception as e:
            self.logger.error(f"Failed to append to consolidated CSV for {symbol}: {e}")
            return False

    def _create_consolidated_metadata(
        self,
        symbol: str,
        data_type: DataType,
        timeframe: Timeframe,
        record_count: int,
        data_hash: str,
        source: str | None = None,
    ) -> dict[str, Any]:
        """
        Create metadata for consolidated CSV files

        Args:
            symbol: Stock symbol
            data_type: Data type
            timeframe: Data timeframe
            record_count: Total number of records in consolidated file
            data_hash: Hash of all data for integrity
            source: Data source

        Returns:
            Metadata dictionary for consolidated format
        """
        return {
            "symbol": symbol.upper(),
            "data_type": data_type.value,
            "timeframe": timeframe.value,
            "format": "consolidated_csv",
            "records": record_count,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "source": source,
            "data_hash": data_hash,
            "format_version": "consolidated_v1",
            "data_quality": {
                "completeness": 1.0,
                "accuracy_score": 1.0,
                "deduplication": True,
            },
        }

    def _store_single_record(
        self,
        symbol: str,
        data: dict[str, Any],
        data_type: DataType,
        date: datetime,
        timeframe: Timeframe,
        source: str | None,
    ) -> bool:
        """Store a single data record using consolidated file approach"""
        try:
            # Generate consolidated file paths
            data_file_path = self._get_file_path(symbol, data_type, None, timeframe, "data")
            meta_file_path = self._get_file_path(symbol, data_type, None, timeframe, "meta")

            # Ensure directories exist
            data_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Store data file (JSON for non-time-series data)
            with open(data_file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            # Create and store metadata for consolidated format
            data_hash = self._generate_data_hash(data)
            metadata = self._create_consolidated_metadata(
                symbol=symbol,
                data_type=data_type,
                timeframe=timeframe,
                record_count=1,
                data_hash=data_hash,
                source=source,
            )

            with open(meta_file_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            # Update global metadata
            self._update_metadata(symbol, data_type, date, data_file_path)

            self.logger.debug(f"Stored {data_type.value} record for {symbol} at {data_file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to store record for {symbol}: {e}")
            return False

    def retrieve_data(
        self,
        symbol: str,
        data_type: DataType,
        date_start: str | datetime,
        date_end: str | datetime | None = None,
        timeframe: Timeframe = Timeframe.DAILY,
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical data from hybrid CSV+JSON format

        Args:
            symbol: Symbol to retrieve data for
            data_type: Type of data to retrieve
            date_start: Start date for retrieval
            date_end: End date (defaults to date_start)
            timeframe: Data timeframe

        Returns:
            List of matching data records
        """
        if isinstance(date_start, str):
            date_start = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
        if date_end and isinstance(date_end, str):
            date_end = datetime.fromisoformat(date_end.replace("Z", "+00:00"))
        elif not date_end:
            date_end = date_start

        return self._retrieve_hybrid_format(symbol, data_type, date_start, date_end, timeframe)

    def _retrieve_hybrid_format(
        self,
        symbol: str,
        data_type: DataType,
        date_start: datetime,
        date_end: datetime,
        timeframe: Timeframe,
    ) -> list[dict[str, Any]]:
        """Retrieve data from consolidated CSV+JSON format - optimized single-file access"""
        results = []

        try:
            if data_type == DataType.STOCK_DAILY_PRICES:
                # Single consolidated CSV file approach
                csv_path = self._get_file_path(symbol, data_type, None, timeframe, "data")
                meta_path = self._get_file_path(symbol, data_type, None, timeframe, "meta")

                if csv_path.exists():
                    # Read all data from consolidated CSV file
                    csv_records = self._deserialize_from_csv(csv_path)

                    # Read metadata if available
                    metadata = {}
                    if meta_path.exists():
                        try:
                            with open(meta_path) as f:
                                metadata = json.load(f)
                        except Exception as e:
                            self.logger.warning(f"Failed to read metadata for {symbol}: {e}")

                    # Filter records within date range (in-memory filtering - efficient for CSV)
                    for record in csv_records:
                        try:
                            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
                            if date_start <= record_date <= date_end:
                                # Add metadata fields directly to the record
                                enhanced_record = record.copy()
                                enhanced_record["symbol"] = symbol
                                enhanced_record["data_type"] = data_type.value
                                enhanced_record["timeframe"] = timeframe.value
                                enhanced_record["source"] = metadata.get("source", "unknown")
                                results.append(enhanced_record)
                        except Exception as e:
                            self.logger.warning(f"Failed to process record for {symbol}: {e}")
                            continue

                    self.logger.debug(
                        f"Retrieved {len(results)} records for {symbol} {timeframe.value} from consolidated file"
                    )

            else:
                # For non-time-series data, read from consolidated JSON file
                data_path = self._get_file_path(symbol, data_type, None, timeframe, "data")
                meta_path = self._get_file_path(symbol, data_type, None, timeframe, "meta")

                if data_path.exists():
                    # Read JSON data
                    with open(data_path) as f:
                        data = json.load(f)

                    # Read metadata if available
                    metadata = {}
                    if meta_path.exists():
                        try:
                            with open(meta_path) as f:
                                metadata = json.load(f)
                        except Exception as e:
                            self.logger.warning(f"Failed to read metadata for {symbol}: {e}")

                    # Return direct data format with metadata fields
                    enhanced_data = data.copy() if isinstance(data, dict) else {"data": data}
                    enhanced_data["symbol"] = symbol
                    enhanced_data["data_type"] = data_type.value
                    enhanced_data["timeframe"] = timeframe.value
                    enhanced_data["source"] = metadata.get("source", "unknown")
                    enhanced_data["date"] = date_start.isoformat()
                    results.append(enhanced_data)

                    self.logger.debug(f"Retrieved consolidated data for {symbol} {data_type.value}")

        except Exception as e:
            self.logger.warning(f"Failed to retrieve hybrid format data: {e}")

        return results

    def _update_metadata(self, symbol: str, data_type: DataType, date: datetime, file_path: Path) -> None:
        """Update metadata tracking"""
        self.metadata["total_files"] += 1

        # Track data types
        if data_type.value not in self.metadata["data_types"]:
            self.metadata["data_types"][data_type.value] = 0
        self.metadata["data_types"][data_type.value] += 1

        # Track symbols
        if symbol not in self.metadata["symbols"]:
            self.metadata["symbols"][symbol] = {
                "first_date": date.isoformat(),
                "last_date": date.isoformat(),
                "data_types": [],
            }
        else:
            self.metadata["symbols"][symbol]["last_date"] = date.isoformat()

        if data_type.value not in self.metadata["symbols"][symbol]["data_types"]:
            self.metadata["symbols"][symbol]["data_types"].append(data_type.value)

        self._save_global_metadata()

    def get_available_data(self, symbol: str | None = None) -> dict[str, Any]:
        """Get summary of available historical data"""
        if symbol:
            return self.metadata["symbols"].get(symbol.upper(), {})
        return {
            "total_files": self.metadata["total_files"],
            "data_types": self.metadata["data_types"],
            "symbols": list(self.metadata["symbols"].keys()),
            "symbol_count": len(self.metadata["symbols"]),
        }

    def cleanup_old_data(self, data_type: DataType, retention_days: int) -> int:
        """Clean up old data beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        # This would implement cleanup logic based on data type and retention
        # For now, return 0 as a placeholder
        self.logger.info(f"Cleanup for {data_type.value} with {retention_days} day retention")
        return deleted_count


def create_historical_data_manager(
    config_path: str | None = None,
) -> HistoricalDataManager:
    """Factory function to create historical data manager"""
    return HistoricalDataManager(config_path=config_path)


if __name__ == "__main__":
    # Example usage
    hdm = create_historical_data_manager()

    # Store sample stock data
    sample_data = {
        "symbol": "AAPL",
        "date": "2025-07-28",
        "open": 150.0,
        "high": 155.0,
        "low": 149.0,
        "close": 154.0,
        "volume": 1000000,
    }

    success = hdm.store_data(
        symbol="AAPL",
        data=sample_data,
        data_type=DataType.STOCK_DAILY_PRICES,
        source="yahoo_finance",
    )

    print("Storage success: {success}")
    print("Available data: {hdm.get_available_data('AAPL')}")
