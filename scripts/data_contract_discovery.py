#!/usr/bin/env python3
"""
Data Contract Discovery System

Automatically discovers frontend data contracts by scanning the frontend/public/data/
directory structure and inferring schemas from existing CSV files.

This implements a contract-first architecture where the frontend directory structure
serves as the authoritative source of truth for data requirements.
"""

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from errors import ConfigurationError, ValidationError
from result_types import ProcessingResult
from utils.logging_setup import setup_logging


@dataclass
class ColumnSchema:
    """Schema information for a single CSV column"""

    name: str
    data_type: str
    sample_values: list[str] = field(default_factory=list)
    nullable: bool = True
    unique_values: int = 0
    format_pattern: str | None = None


@dataclass
class DataContract:
    """Represents a discovered data contract from frontend requirements"""

    # Contract identification
    contract_id: str
    category: str  # e.g., 'portfolio', 'trade-history', 'live-signals'
    file_path: Path
    relative_path: str  # Path relative to frontend/public/data/

    # Schema information
    schema: list[ColumnSchema]
    row_count: int = 0
    last_modified: datetime | None = None
    file_size_bytes: int = 0

    # Contract metadata
    dependencies: list[str] = field(default_factory=list)
    refresh_frequency: str = "daily"  # daily, hourly, on-demand
    data_sources: list[str] = field(default_factory=list)  # CLI services that can provide this data

    # Quality requirements
    freshness_threshold_hours: int = 24
    minimum_rows: int = 1
    required_columns: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        """Convert contract to dictionary for serialization"""
        result = asdict(self)
        result["file_path"] = str(self.file_path)
        result["last_modified"] = self.last_modified.isoformat() if self.last_modified else None
        result["required_columns"] = list(self.required_columns)
        return result


@dataclass
class ContractDiscoveryResult:
    """Result of contract discovery operation"""

    contracts: list[DataContract]
    categories: set[str]
    total_files: int
    successful_discoveries: int
    failed_discoveries: list[str] = field(default_factory=list)
    discovery_time: float = 0.0

    def get_contracts_by_category(self, category: str) -> list[DataContract]:
        """Get all contracts for a specific category"""
        return [contract for contract in self.contracts if contract.category == category]

    def get_contract_by_id(self, contract_id: str) -> DataContract | None:
        """Get contract by ID"""
        for contract in self.contracts:
            if contract.contract_id == contract_id:
                return contract
        return None


class DataContractDiscovery:
    """
    Discovers frontend data contracts by scanning directory structure and inferring schemas

    This class implements contract-first architecture where the frontend/public/data/
    directory serves as the authoritative contract definition.
    """

    def __init__(self, frontend_data_path: Path | None = None):
        """Initialize contract discovery with frontend data path"""
        setup_logging("INFO")
        self.logger = logging.getLogger("data_contract_discovery")

        # Set default frontend data path
        if frontend_data_path is None:
            project_root = Path(__file__).parent.parent
            self.frontend_data_path = project_root / "frontend/public/data"
        else:
            self.frontend_data_path = Path(frontend_data_path)

        # Validate path exists
        if not self.frontend_data_path.exists():
            raise ConfigurationError(
                f"Frontend data directory does not exist: {self.frontend_data_path}",
                context={"frontend_data_path": str(self.frontend_data_path)},
            )

        self.logger.info(f"Initialized contract discovery for: {self.frontend_data_path}")

        # Contract discovery configuration
        self.max_sample_values = 5
        self.max_schema_inference_rows = 1000

        # Data type inference patterns
        self.data_type_patterns = {
            "datetime": [
                r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",  # YYYY-MM-DD HH:MM:SS
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO format
            ],
            "numeric": [
                r"^-?\d+\.?\d*$",  # Integer or float
                r"^-?\d+$",  # Integer
            ],
            "uuid": [
                r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
                r"^[A-Z]+_[A-Z]+_\d+_\d+_\d{4}-\d{2}-\d{2}$",  # Position UUID pattern
            ],
            "categorical": [
                r"^(Long|Short)$",  # Direction
                r"^(Closed|Open)$",  # Status
                r"^(SMA|EMA)$",  # Strategy type
            ],
        }

    def discover_all_contracts(self) -> ContractDiscoveryResult:
        """
        Discover all data contracts from frontend directory structure

        Returns:
            ContractDiscoveryResult with discovered contracts and metadata
        """
        start_time = datetime.now()

        self.logger.info("Starting comprehensive contract discovery")

        contracts = []
        categories = set()
        failed_discoveries = []
        total_files = 0

        try:
            # Walk through all CSV files in the frontend data directory
            for csv_file in self.frontend_data_path.rglob("*.csv"):
                total_files += 1

                try:
                    contract = self._discover_contract_from_file(csv_file)
                    contracts.append(contract)
                    categories.add(contract.category)

                    self.logger.info(
                        f"Discovered contract: {contract.contract_id} "
                        f"({contract.category}, {len(contract.schema)} columns)"
                    )

                except Exception as e:
                    error_msg = f"Failed to discover contract from {csv_file}: {e}"
                    self.logger.error(error_msg)
                    failed_discoveries.append(error_msg)

            discovery_time = (datetime.now() - start_time).total_seconds()

            result = ContractDiscoveryResult(
                contracts=contracts,
                categories=categories,
                total_files=total_files,
                successful_discoveries=len(contracts),
                failed_discoveries=failed_discoveries,
                discovery_time=discovery_time,
            )

            self.logger.info(
                f"Contract discovery completed: {len(contracts)}/{total_files} files successful "
                f"in {discovery_time:.2f}s, found {len(categories)} categories"
            )

            return result

        except Exception as e:
            discovery_time = (datetime.now() - start_time).total_seconds()

            self.logger.error(f"Contract discovery failed: {e}")
            raise ValidationError(
                f"Failed to discover data contracts: {e}",
                context={
                    "frontend_data_path": str(self.frontend_data_path),
                    "discovery_time": discovery_time,
                    "total_files": total_files,
                },
            )

    def _discover_contract_from_file(self, csv_file: Path) -> DataContract:
        """Discover contract from a single CSV file"""

        # Generate contract ID and category from file path
        relative_path = csv_file.relative_to(self.frontend_data_path)
        contract_id = self._generate_contract_id(relative_path)
        category = self._extract_category_from_path(relative_path)

        # Get file metadata
        file_stats = csv_file.stat()
        last_modified = datetime.fromtimestamp(file_stats.st_mtime)
        file_size_bytes = file_stats.st_size

        # Infer schema from CSV content
        schema, row_count = self._infer_schema_from_csv(csv_file)

        # Determine data sources and dependencies
        data_sources = self._determine_data_sources(category, contract_id)
        dependencies = self._extract_dependencies(relative_path)

        # Set quality requirements based on contract type
        freshness_threshold, minimum_rows = self._determine_quality_requirements(category)
        required_columns = self._extract_required_columns(schema)

        contract = DataContract(
            contract_id=contract_id,
            category=category,
            file_path=csv_file,
            relative_path=str(relative_path),
            schema=schema,
            row_count=row_count,
            last_modified=last_modified,
            file_size_bytes=file_size_bytes,
            data_sources=data_sources,
            dependencies=dependencies,
            freshness_threshold_hours=freshness_threshold,
            minimum_rows=minimum_rows,
            required_columns=required_columns,
        )

        return contract

    def _generate_contract_id(self, relative_path: Path) -> str:
        """Generate unique contract ID from file path"""
        # Convert path to contract ID: portfolio/live_signals_equity.csv -> portfolio_live_signals_equity
        parts = list(relative_path.parts)

        # Remove .csv extension from last part
        if parts:
            parts[-1] = parts[-1].replace(".csv", "")

        return "_".join(parts)

    def _extract_category_from_path(self, relative_path: Path) -> str:
        """Extract category from file path"""
        parts = relative_path.parts

        if len(parts) == 1:
            # File in root data directory
            return "general"

        # Use first directory as category
        return parts[0]

    def _infer_schema_from_csv(self, csv_file: Path) -> tuple[list[ColumnSchema], int]:
        """Infer schema from CSV file content"""

        try:
            # Read CSV file with pandas for better handling
            df = pd.read_csv(csv_file, nrows=self.max_schema_inference_rows)

            if df.empty:
                raise ValidationError(f"CSV file is empty: {csv_file}")

            schema = []

            for column in df.columns:
                col_data = df[column].dropna()  # Remove NaN values for analysis

                # Infer data type
                data_type = self._infer_column_data_type(col_data)

                # Get sample values (first few non-null values)
                sample_values = col_data.head(self.max_sample_values).astype(str).tolist()

                # Calculate metadata
                nullable = df[column].isnull().any()
                unique_values = col_data.nunique()
                format_pattern = self._detect_format_pattern(col_data, data_type)

                column_schema = ColumnSchema(
                    name=column.strip(),
                    data_type=data_type,
                    sample_values=sample_values,
                    nullable=nullable,
                    unique_values=unique_values,
                    format_pattern=format_pattern,
                )

                schema.append(column_schema)

            return schema, len(df)

        except Exception as e:
            raise ValidationError(
                f"Failed to infer schema from CSV file: {e}",
                context={"csv_file": str(csv_file)},
            )

    def _infer_column_data_type(self, series: pd.Series) -> str:
        """Infer data type for a pandas Series"""

        # Check if all values are empty/null
        if series.empty:
            return "string"

        # Get sample of values as strings for pattern matching
        sample_values = series.head(100).astype(str).tolist()

        # Count matches for each data type
        type_scores = {}

        for data_type, patterns in self.data_type_patterns.items():
            score = 0
            for value in sample_values:
                for pattern in patterns:
                    if re.match(pattern, value):
                        score += 1
                        break
            type_scores[data_type] = score / len(sample_values) if sample_values else 0

        # Return type with highest score if above threshold
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0.8:  # 80% of values match pattern
                return best_type

        # Fall back to pandas dtype inference
        try:
            # Try to convert to numeric
            pd.to_numeric(series, errors="raise")
            return "numeric"
        except (ValueError, TypeError):
            pass

        try:
            # Try to convert to datetime with explicit format to avoid warnings
            pd.to_datetime(series, errors="raise", format="ISO8601")
            return "datetime"
        except (ValueError, TypeError):
            try:
                # Fallback to mixed format parsing
                pd.to_datetime(series, errors="raise", format="mixed")
                return "datetime"
            except (ValueError, TypeError):
                pass

        # Default to string
        return "string"

    def _detect_format_pattern(self, series: pd.Series, data_type: str) -> str | None:
        """Detect format pattern for a column"""

        if data_type == "datetime":
            # Try to detect datetime format
            sample_value = str(series.iloc[0]) if not series.empty else ""

            if re.match(r"^\d{4}-\d{2}-\d{2}$", sample_value):
                return "%Y-%m-%d"
            if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", sample_value):
                return "%Y-%m-%d %H:%M:%S"
            if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", sample_value):
                return "%Y-%m-%dT%H:%M:%S"

        elif data_type == "numeric":
            # Check if all values are integers or floats
            try:
                if all(float(val).is_integer() for val in series.astype(str)):
                    return "integer"
                return "float"
            except (ValueError, TypeError):
                pass

        return None

    def _determine_data_sources(self, category: str, contract_id: str) -> list[str]:
        """Determine which CLI services can provide data for this contract"""

        # Map categories to CLI services
        category_mappings = {
            "portfolio": ["yahoo_finance", "alpha_vantage"],
            "trade-history": ["trade_history_cli"],
            "open-positions": ["trade_history_cli"],
            "live-signals": ["live_signals_dashboard"],
            "raw": ["yahoo_finance", "alpha_vantage"],  # Add mapping for raw stock data
        }

        # Handle nested categories (e.g., portfolio/live-signals)
        for cat, services in category_mappings.items():
            if cat in category or cat in contract_id:
                return services

        return ["unknown"]

    def _extract_dependencies(self, relative_path: Path) -> list[str]:
        """Extract dependencies from file path analysis"""
        dependencies = []

        # If file is in a subdirectory, it may depend on parent category data
        if len(relative_path.parts) > 1:
            parent_category = relative_path.parts[0]
            dependencies.append(parent_category)

        return dependencies

    def _determine_quality_requirements(self, category: str) -> tuple[int, int]:
        """Determine quality requirements based on category"""

        quality_mappings = {
            "portfolio": (24, 100),  # 24 hours freshness, minimum 100 rows
            "trade-history": (6, 1),  # 6 hours freshness, minimum 1 row
            "open-positions": (1, 1),  # 1 hour freshness, minimum 1 row
            "live-signals": (1, 50),  # 1 hour freshness, minimum 50 rows
        }

        return quality_mappings.get(category, (24, 1))  # Default: 24 hours, 1 row

    def _extract_required_columns(self, schema: list[ColumnSchema]) -> set[str]:
        """Extract required columns based on schema analysis"""

        required_columns = set()

        for column in schema:
            # Consider columns required if they have low nullability and seem important
            if not column.nullable or column.name.lower() in [
                "date",
                "timestamp",
                "ticker",
                "position_uuid",
                "pnl",
            ]:
                required_columns.add(column.name)

        return required_columns

    def export_contracts_to_json(self, contracts: list[DataContract], output_file: Path) -> None:
        """Export discovered contracts to JSON file"""

        try:
            output_data = {
                "discovery_timestamp": datetime.now().isoformat(),
                "total_contracts": len(contracts),
                "contracts": [contract.to_dict() for contract in contracts],
            }

            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2, default=str)

            self.logger.info(f"Exported {len(contracts)} contracts to {output_file}")

        except Exception as e:
            raise ValidationError(
                f"Failed to export contracts to JSON: {e}",
                context={
                    "output_file": str(output_file),
                    "contract_count": len(contracts),
                },
            )

    def validate_contract_completeness(self, result: ContractDiscoveryResult) -> ProcessingResult:
        """Validate that all expected contracts were discovered"""

        # Expected contract categories based on frontend analysis
        expected_categories = {"portfolio", "trade-history", "open-positions"}
        discovered_categories = result.categories

        missing_categories = expected_categories - discovered_categories
        unexpected_categories = discovered_categories - expected_categories

        issues = []

        if missing_categories:
            issues.append(f"Missing expected categories: {missing_categories}")

        if result.failed_discoveries:
            issues.append(f"Failed to discover {len(result.failed_discoveries)} contracts")

        success = len(issues) == 0

        validation_result = ProcessingResult(
            success=success,
            operation="validate_contract_completeness",
            error="; ".join(issues) if issues else None,
        )

        validation_result.add_metadata("total_contracts", len(result.contracts))
        validation_result.add_metadata("discovered_categories", list(discovered_categories))
        validation_result.add_metadata("expected_categories", list(expected_categories))
        validation_result.add_metadata("missing_categories", list(missing_categories))
        validation_result.add_metadata("unexpected_categories", list(unexpected_categories))

        return validation_result


if __name__ == "__main__":
    # Example usage and testing
    discovery = DataContractDiscovery()

    print("🔍 Discovering data contracts...")
    result = discovery.discover_all_contracts()

    print("\n📋 Discovery Results:")
    print("   Total files: {result.total_files}")
    print("   Successful discoveries: {result.successful_discoveries}")
    print("   Categories found: {len(result.categories)}")
    print("   Discovery time: {result.discovery_time:.2f}s")

    if result.failed_discoveries:
        print("\n❌ Failed discoveries:")
        for failure in result.failed_discoveries:
            print("   - {failure}")

    print("\n📊 Discovered Categories:")
    for category in sorted(result.categories):
        contracts = result.get_contracts_by_category(category)
        print("   {category}: {len(contracts)} contracts")

        for contract in contracts:
            print(f"     - {contract.contract_id} ({len(contract.schema)} columns, {contract.row_count} rows)")

    # Validate contract completeness
    validation = discovery.validate_contract_completeness(result)
    print("\n✅ Contract validation: {'PASSED' if validation.success else 'FAILED'}")
    if not validation.success:
        print("   Issues: {validation.error}")

    # Export contracts to JSON
    output_file = Path(__file__).parent / "data_contracts.json"
    discovery.export_contracts_to_json(result.contracts, output_file)
    print("\n💾 Contracts exported to: {output_file}")
