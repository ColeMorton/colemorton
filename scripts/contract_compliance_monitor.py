#!/usr/bin/env python3
"""
Contract Compliance Monitoring System

Provides comprehensive reporting and monitoring of data contract compliance,
quality metrics, and overall system health for the contract-first pipeline.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
from data_contract_discovery import (
    ContractDiscoveryResult,
    DataContract,
    DataContractDiscovery,
)
from data_pipeline_manager import DataPipelineManager
from result_types import ProcessingResult
from utils.logging_setup import setup_logging


class ComplianceStatus(Enum):
    """Contract compliance status levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MISSING = "missing"


@dataclass
class ContractComplianceReport:
    """Individual contract compliance report"""

    contract_id: str
    category: str
    status: ComplianceStatus
    file_path: str

    # File metadata
    exists: bool = False
    file_size_bytes: int = 0
    last_modified: datetime | None = None
    age_hours: float = 0.0

    # Schema compliance
    schema_valid: bool = False
    row_count: int = 0
    column_count: int = 0
    missing_columns: list[str] = None
    extra_columns: list[str] = None

    # Data quality metrics
    data_quality_score: float = 0.0
    null_percentage: float = 0.0
    duplicate_percentage: float = 0.0
    data_type_violations: int = 0

    # Service fulfillment
    capable_services: list[str] = None
    fulfillment_possible: bool = False

    # Issues and recommendations
    issues: list[str] = None
    recommendations: list[str] = None

    def __post_init__(self):
        if self.missing_columns is None:
            self.missing_columns = []
        if self.extra_columns is None:
            self.extra_columns = []
        if self.capable_services is None:
            self.capable_services = []
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result["status"] = self.status.value
        result["last_modified"] = self.last_modified.isoformat() if self.last_modified else None
        return result


@dataclass
class SystemComplianceReport:
    """Overall system compliance report"""

    report_timestamp: datetime
    total_contracts: int

    # Status breakdown
    healthy_contracts: int = 0
    warning_contracts: int = 0
    critical_contracts: int = 0
    missing_contracts: int = 0

    # Category breakdown
    category_summary: dict[str, dict[str, int]] = None

    # Overall metrics
    overall_compliance_score: float = 0.0
    data_freshness_score: float = 0.0
    schema_compliance_score: float = 0.0
    service_availability_score: float = 0.0

    # Contract reports
    contract_reports: list[ContractComplianceReport] = None

    # System health indicators
    critical_issues: list[str] = None
    warnings: list[str] = None
    recommendations: list[str] = None

    def __post_init__(self):
        if self.category_summary is None:
            self.category_summary = {}
        if self.contract_reports is None:
            self.contract_reports = []
        if self.critical_issues is None:
            self.critical_issues = []
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result["report_timestamp"] = self.report_timestamp.isoformat()
        result["contract_reports"] = [report.to_dict() for report in self.contract_reports]
        return result


class ContractComplianceMonitor:
    """
    Monitors and reports on contract compliance across the entire system
    """

    def __init__(self, frontend_data_path: Path | None = None):
        """Initialize compliance monitor"""
        setup_logging("INFO")
        self.logger = logging.getLogger("contract_compliance_monitor")

        # Initialize discovery and pipeline systems
        self.discovery = DataContractDiscovery(frontend_data_path)
        self.pipeline = DataPipelineManager(frontend_data_path)

        # Compliance thresholds
        self.freshness_warning_hours = 6
        self.freshness_critical_hours = 24
        self.min_data_quality_score = 7.0
        self.min_compliance_score = 8.0

        self.logger.info("Contract compliance monitor initialized")

    def generate_compliance_report(self) -> SystemComplianceReport:
        """Generate comprehensive compliance report"""
        self.logger.info("Generating contract compliance report")
        start_time = datetime.now()

        try:
            # Discover all contracts
            discovery_result = self.discovery.discover_all_contracts()

            # Generate individual contract reports
            contract_reports = []
            for contract in discovery_result.contracts:
                report = self._analyze_contract_compliance(contract)
                contract_reports.append(report)

            # Calculate overall system metrics
            system_report = self._generate_system_report(contract_reports, discovery_result)

            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Compliance report generated in {processing_time:.2f}s")

            return system_report

        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            raise

    def _analyze_contract_compliance(self, contract: DataContract) -> ContractComplianceReport:
        """Analyze compliance for a single contract"""

        report = ContractComplianceReport(
            contract_id=contract.contract_id,
            category=contract.category,
            status=ComplianceStatus.HEALTHY,
            file_path=str(contract.file_path),
        )

        try:
            # Check file existence and metadata
            self._analyze_file_metadata(contract, report)

            # Analyze schema compliance if file exists
            if report.exists:
                self._analyze_schema_compliance(contract, report)
                self._analyze_data_quality(contract, report)

            # Check service availability
            self._analyze_service_fulfillment(contract, report)

            # Determine overall status and recommendations
            self._determine_contract_status(report)

        except Exception as e:
            report.status = ComplianceStatus.CRITICAL
            report.issues.append(f"Analysis failed: {str(e)}")
            self.logger.error(f"Failed to analyze contract {contract.contract_id}: {e}")

        return report

    def _analyze_file_metadata(self, contract: DataContract, report: ContractComplianceReport):
        """Analyze file metadata and freshness"""

        if contract.file_path.exists() and contract.file_path.is_file():
            report.exists = True
            report.file_size_bytes = contract.file_path.stat().st_size
            report.last_modified = datetime.fromtimestamp(contract.file_path.stat().st_mtime)
            report.age_hours = (datetime.now() - report.last_modified).total_seconds() / 3600

            # Check freshness
            if report.age_hours > self.freshness_critical_hours:
                report.issues.append(f"Data is critically stale ({report.age_hours:.1f}h old)")
            elif report.age_hours > self.freshness_warning_hours:
                report.issues.append(f"Data is stale ({report.age_hours:.1f}h old)")

        else:
            report.exists = False
            report.status = ComplianceStatus.MISSING
            report.issues.append("Contract file does not exist")
            report.recommendations.append("Run data pipeline to generate missing contract data")

    def _analyze_schema_compliance(self, contract: DataContract, report: ContractComplianceReport):
        """Analyze schema compliance"""

        try:
            df = pd.read_csv(contract.file_path)
            report.row_count = len(df)
            report.column_count = len(df.columns)

            # Check schema compliance
            expected_columns = {col.name for col in contract.schema}
            actual_columns = set(df.columns)

            report.missing_columns = list(expected_columns - actual_columns)
            report.extra_columns = list(actual_columns - expected_columns)

            report.schema_valid = len(report.missing_columns) == 0

            if report.missing_columns:
                report.issues.append(f"Missing required columns: {report.missing_columns}")

            if len(df) < contract.minimum_rows:
                report.issues.append(f"Insufficient data: {len(df)} rows < {contract.minimum_rows} required")

        except Exception as e:
            report.schema_valid = False
            report.issues.append(f"Schema validation failed: {str(e)}")

    def _analyze_data_quality(self, contract: DataContract, report: ContractComplianceReport):
        """Analyze data quality metrics"""

        try:
            df = pd.read_csv(contract.file_path)

            if df.empty:
                report.data_quality_score = 0.0
                report.issues.append("Dataset is empty")
                return

            # Calculate quality metrics
            total_cells = df.size
            null_cells = df.isnull().sum().sum()
            report.null_percentage = (null_cells / total_cells) * 100 if total_cells > 0 else 0

            # Check for duplicates
            duplicate_rows = df.duplicated().sum()
            report.duplicate_percentage = (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0

            # Data type validation
            report.data_type_violations = self._validate_data_types(df, contract)

            # Calculate overall data quality score (0-10)
            quality_score = 10.0

            # Penalty for high null percentage
            if report.null_percentage > 50:
                quality_score -= 4.0
            elif report.null_percentage > 20:
                quality_score -= 2.0
            elif report.null_percentage > 5:
                quality_score -= 1.0

            # Penalty for duplicates
            if report.duplicate_percentage > 20:
                quality_score -= 2.0
            elif report.duplicate_percentage > 5:
                quality_score -= 1.0

            # Penalty for data type violations
            quality_score -= min(report.data_type_violations * 0.5, 3.0)

            report.data_quality_score = max(0.0, quality_score)

            # Add quality issues
            if report.null_percentage > 20:
                report.issues.append(f"High null percentage: {report.null_percentage:.1f}%")

            if report.duplicate_percentage > 5:
                report.issues.append(f"High duplicate percentage: {report.duplicate_percentage:.1f}%")

            if report.data_type_violations > 0:
                report.issues.append(f"Data type violations: {report.data_type_violations}")

        except Exception as e:
            report.data_quality_score = 0.0
            report.issues.append(f"Data quality analysis failed: {str(e)}")

    def _validate_data_types(self, df: pd.DataFrame, contract: DataContract) -> int:
        """Validate data types against contract schema"""
        violations = 0

        for column_schema in contract.schema:
            if column_schema.name not in df.columns:
                continue

            column_data = df[column_schema.name].dropna()
            if column_data.empty:
                continue

            expected_type = column_schema.data_type

            try:
                if expected_type == "numeric":
                    pd.to_numeric(column_data, errors="raise")
                elif expected_type == "datetime":
                    pd.to_datetime(column_data, errors="raise")
                # String type is always valid

            except (ValueError, TypeError):
                violations += 1

        return violations

    def _analyze_service_fulfillment(self, contract: DataContract, report: ContractComplianceReport):
        """Analyze service fulfillment capabilities"""

        report.capable_services = self.pipeline.map_contract_to_services(contract)
        report.fulfillment_possible = len(report.capable_services) > 0

        if not report.fulfillment_possible:
            report.issues.append("No CLI services available to fulfill this contract")
            report.recommendations.append("Configure CLI services or add data source mapping")

    def _determine_contract_status(self, report: ContractComplianceReport):
        """Determine overall contract status based on analysis"""

        if not report.exists:
            report.status = ComplianceStatus.MISSING
            return

        critical_issues = 0
        warning_issues = 0

        # Critical conditions
        if not report.schema_valid:
            critical_issues += 1

        if report.age_hours > self.freshness_critical_hours:
            critical_issues += 1

        if report.data_quality_score < 5.0:
            critical_issues += 1

        if not report.fulfillment_possible:
            critical_issues += 1

        # Warning conditions
        if report.age_hours > self.freshness_warning_hours:
            warning_issues += 1

        if report.data_quality_score < self.min_data_quality_score:
            warning_issues += 1

        if report.null_percentage > 20:
            warning_issues += 1

        # Determine final status
        if critical_issues > 0:
            report.status = ComplianceStatus.CRITICAL
        elif warning_issues > 0:
            report.status = ComplianceStatus.WARNING
        else:
            report.status = ComplianceStatus.HEALTHY

    def _generate_system_report(
        self,
        contract_reports: list[ContractComplianceReport],
        discovery_result: ContractDiscoveryResult,
    ) -> SystemComplianceReport:
        """Generate overall system compliance report"""

        system_report = SystemComplianceReport(report_timestamp=datetime.now(), total_contracts=len(contract_reports))

        system_report.contract_reports = contract_reports

        # Count status breakdown
        for report in contract_reports:
            if report.status == ComplianceStatus.HEALTHY:
                system_report.healthy_contracts += 1
            elif report.status == ComplianceStatus.WARNING:
                system_report.warning_contracts += 1
            elif report.status == ComplianceStatus.CRITICAL:
                system_report.critical_contracts += 1
            elif report.status == ComplianceStatus.MISSING:
                system_report.missing_contracts += 1

        # Generate category breakdown
        for category in discovery_result.categories:
            category_reports = [r for r in contract_reports if r.category == category]
            system_report.category_summary[category] = {
                "total": len(category_reports),
                "healthy": len([r for r in category_reports if r.status == ComplianceStatus.HEALTHY]),
                "warning": len([r for r in category_reports if r.status == ComplianceStatus.WARNING]),
                "critical": len([r for r in category_reports if r.status == ComplianceStatus.CRITICAL]),
                "missing": len([r for r in category_reports if r.status == ComplianceStatus.MISSING]),
            }

        # Calculate overall scores
        self._calculate_system_scores(system_report)

        # Generate system-level issues and recommendations
        self._generate_system_issues_and_recommendations(system_report)

        return system_report

    def _calculate_system_scores(self, system_report: SystemComplianceReport):
        """Calculate overall system health scores"""

        if system_report.total_contracts == 0:
            return

        # Overall compliance score (0-10)
        healthy_weight = 10.0
        warning_weight = 6.0
        critical_weight = 2.0
        missing_weight = 0.0

        weighted_score = (
            system_report.healthy_contracts * healthy_weight
            + system_report.warning_contracts * warning_weight
            + system_report.critical_contracts * critical_weight
            + system_report.missing_contracts * missing_weight
        ) / system_report.total_contracts

        system_report.overall_compliance_score = weighted_score

        # Data freshness score
        fresh_contracts = 0
        total_existing = 0

        for report in system_report.contract_reports:
            if report.exists:
                total_existing += 1
                if report.age_hours <= self.freshness_warning_hours:
                    fresh_contracts += 1

        system_report.data_freshness_score = (fresh_contracts / total_existing * 10.0) if total_existing > 0 else 0.0

        # Schema compliance score
        valid_schemas = len([r for r in system_report.contract_reports if r.schema_valid])
        system_report.schema_compliance_score = (valid_schemas / system_report.total_contracts) * 10.0

        # Service availability score
        fulfillable_contracts = len([r for r in system_report.contract_reports if r.fulfillment_possible])
        system_report.service_availability_score = (fulfillable_contracts / system_report.total_contracts) * 10.0

    def _generate_system_issues_and_recommendations(self, system_report: SystemComplianceReport):
        """Generate system-level issues and recommendations"""

        # Critical issues
        if system_report.missing_contracts > 0:
            system_report.critical_issues.append(f"{system_report.missing_contracts} contracts have missing data files")

        if system_report.critical_contracts > 0:
            system_report.critical_issues.append(
                f"{system_report.critical_contracts} contracts have critical compliance issues"
            )

        if system_report.overall_compliance_score < 5.0:
            system_report.critical_issues.append(
                f"Overall compliance score is critically low: {system_report.overall_compliance_score:.1f}/10"
            )

        # Warnings
        if system_report.warning_contracts > 0:
            system_report.warnings.append(f"{system_report.warning_contracts} contracts have compliance warnings")

        if system_report.data_freshness_score < 7.0:
            system_report.warnings.append(f"Data freshness score is low: {system_report.data_freshness_score:.1f}/10")

        # Recommendations
        if system_report.missing_contracts > 0 or system_report.critical_contracts > 0:
            system_report.recommendations.append("Run data pipeline to refresh all contract data")

        if system_report.data_freshness_score < 8.0:
            system_report.recommendations.append("Schedule more frequent data refreshes")

        if system_report.schema_compliance_score < 8.0:
            system_report.recommendations.append("Review and fix schema compliance issues")

    def export_report(self, report: SystemComplianceReport, output_file: Path) -> ProcessingResult:
        """Export compliance report to JSON file"""

        try:
            with open(output_file, "w") as f:
                json.dump(report.to_dict(), f, indent=2, default=str)

            self.logger.info(f"Compliance report exported to {output_file}")

            return ProcessingResult(success=True, operation="export_compliance_report")

        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            return ProcessingResult(success=False, operation="export_compliance_report", error=str(e))

    def print_summary_report(self, report: SystemComplianceReport):
        """Print a human-readable summary of the compliance report"""

        print("📊 Contract Compliance Report")
        print("=" * 60)
        print("Generated: {report.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Total Contracts: {report.total_contracts}")
        print()

        # Status breakdown
        print("📈 Status Breakdown:")
        print(
            f"   ✅ Healthy: {report.healthy_contracts} ({report.healthy_contracts / report.total_contracts * 100:.1f}%)"
        )
        print(
            f"   ⚠️  Warning: {report.warning_contracts} ({report.warning_contracts / report.total_contracts * 100:.1f}%)"
        )
        print(
            f"   🚨 Critical: {report.critical_contracts} ({report.critical_contracts / report.total_contracts * 100:.1f}%)"
        )
        print(
            f"   ❌ Missing: {report.missing_contracts} ({report.missing_contracts / report.total_contracts * 100:.1f}%)"
        )
        print()

        # Overall scores
        print("🏆 System Health Scores:")
        print("   Overall Compliance: {report.overall_compliance_score:.1f}/10")
        print("   Data Freshness: {report.data_freshness_score:.1f}/10")
        print("   Schema Compliance: {report.schema_compliance_score:.1f}/10")
        print("   Service Availability: {report.service_availability_score:.1f}/10")
        print()

        # Category breakdown
        if report.category_summary:
            print("📂 Category Breakdown:")
            for category, stats in report.category_summary.items():
                print(f"   {category.title()}: {stats['healthy']}/{stats['total']} healthy")
        print()

        # Critical issues
        if report.critical_issues:
            print("🚨 Critical Issues:")
            for issue in report.critical_issues:
                print("   - {issue}")
            print()

        # Warnings
        if report.warnings:
            print("⚠️  Warnings:")
            for warning in report.warnings:
                print("   - {warning}")
            print()

        # Recommendations
        if report.recommendations:
            print("💡 Recommendations:")
            for rec in report.recommendations:
                print("   - {rec}")
            print()

        # Overall health indicator
        if report.overall_compliance_score >= 8.0:
            print("🎉 System is in excellent health!")
        elif report.overall_compliance_score >= 6.0:
            print("👍 System is in good health with minor issues.")
        elif report.overall_compliance_score >= 4.0:
            print("⚠️  System has significant issues that need attention.")
        else:
            print("🚨 System is in critical condition and requires immediate attention!")


def main():
    """Main entry point for compliance monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="Contract compliance monitoring and reporting")
    parser.add_argument("--output", "-o", help="Output file for JSON report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize monitor
    monitor = ContractComplianceMonitor()

    # Generate compliance report
    print("🔍 Analyzing contract compliance...")
    report = monitor.generate_compliance_report()

    # Print summary
    monitor.print_summary_report(report)

    # Export to file if requested
    if args.output:
        output_file = Path(args.output)
        result = monitor.export_report(report, output_file)
        if result.success:
            print("📄 Full report exported to: {args.output}")
        else:
            print("❌ Failed to export report: {result.error}")

    # Exit with appropriate code based on system health
    if report.critical_contracts > 0 or report.missing_contracts > 0:
        exit(1)
    elif report.warning_contracts > 0:
        exit(2)
    else:
        exit(0)


if __name__ == "__main__":
    main()
