#!/usr/bin/env python3
"""
Data Quality Monitoring and Alerting System

Continuous monitoring of data quality with automated alerting for degradation,
staleness detection, variance monitoring, and institutional quality compliance.

Features:
- Real-time data quality monitoring
- Automated alerting for quality degradation
- Staleness detection across all data sources
- Variance threshold monitoring with alerts
- Quality trend analysis and reporting
- Integration with validation framework

Usage:
    python scripts/utils/data_quality_monitor.py --start-monitoring
    python scripts/utils/data_quality_monitor.py --check-quality --region US
    python scripts/utils/data_quality_monitor.py --generate-report --days 7
"""

import json
import logging
import os
import smtplib
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import numpy as np


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.utils.dasv_cross_validator import DASVCrossValidator
    from scripts.utils.fed_rate_validation import FedRateValidator
except ImportError as e:
    print(f"Warning: Could not import validation components: {e}")


@dataclass
class QualityAlert:
    """Data quality alert container"""

    alert_type: str  # 'staleness', 'variance', 'quality_degradation', 'validation_failure'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    details: dict[str, Any]
    timestamp: str
    region: str | None = None
    indicator: str | None = None


@dataclass
class QualityMetrics:
    """Quality metrics snapshot"""

    timestamp: str
    overall_score: float
    freshness_score: float
    variance_score: float
    validation_score: float
    alerts_count: int
    critical_alerts: int
    region: str | None = None


class DataQualityMonitor:
    """
    Data quality monitoring and alerting system
    """

    def __init__(self, config_file: str | None = None):
        self.config = self._load_config(config_file)
        self.alerts = []
        self.metrics_history = []

        # Monitoring thresholds
        self.thresholds = {
            "staleness_hours": 6,
            "variance_threshold": 0.02,
            "quality_score_threshold": 0.85,
            "critical_quality_threshold": 0.7,
            "alert_frequency_minutes": 15,
        }

        # Update thresholds from config
        if "thresholds" in self.config:
            self.thresholds.update(self.config["thresholds"])

        # Setup logging
        self._setup_logging()

        # Initialize validators
        try:
            self.cross_validator = DASVCrossValidator(
                variance_threshold=self.thresholds["variance_threshold"],
                staleness_hours=self.thresholds["staleness_hours"],
            )
            self.fed_validator = FedRateValidator()
        except Exception as e:
            self.logger.warning(f"Could not initialize validators: {e}")
            self.cross_validator = None
            self.fed_validator = None

    def _load_config(self, config_file: str | None) -> dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "email_notifications": {
                "enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "from_email": "monitor@colemorton.com",
                "to_emails": [],
                "password": "",
            },
            "monitoring": {
                "check_interval_minutes": 15,
                "regions_to_monitor": ["US", "GLOBAL", "EUROPE", "ASIA"],
                "data_sources": ["discovery", "analysis", "synthesis", "validation"],
            },
            "thresholds": {
                "staleness_hours": 6,
                "variance_threshold": 0.02,
                "quality_score_threshold": 0.85,
            },
            "storage": {
                "alerts_file": "data/monitoring/alerts.json",
                "metrics_file": "data/monitoring/metrics.json",
                "reports_dir": "data/monitoring/reports",
            },
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")

        return default_config

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file", "data/monitoring/quality_monitor.log")

        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)

    def start_monitoring(self, duration_hours: int | None = None):
        """Start continuous monitoring"""
        self.logger.info("Starting data quality monitoring...")

        start_time = datetime.now()
        check_interval = self.config["monitoring"]["check_interval_minutes"] * 60

        try:
            while True:
                # Check if duration limit reached
                if duration_hours:
                    elapsed = datetime.now() - start_time
                    if elapsed.total_seconds() > duration_hours * 3600:
                        self.logger.info("Monitoring duration limit reached")
                        break

                # Run quality check
                self._run_monitoring_cycle()

                # Sleep until next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
            raise

    def _run_monitoring_cycle(self):
        """Run single monitoring cycle"""
        self.logger.info("Running monitoring cycle...")

        regions = self.config["monitoring"]["regions_to_monitor"]
        cycle_alerts = []
        cycle_metrics = []

        for region in regions:
            try:
                # Check region quality
                region_metrics, region_alerts = self._check_region_quality(region)

                if region_metrics:
                    cycle_metrics.append(region_metrics)

                cycle_alerts.extend(region_alerts)

            except Exception as e:
                self.logger.error(f"Error checking region {region}: {e}")
                cycle_alerts.append(
                    QualityAlert(
                        alert_type="monitoring_error",
                        severity="medium",
                        message=f"Error monitoring region {region}: {str(e)}",
                        details={"region": region, "error": str(e)},
                        timestamp=datetime.now().isoformat(),
                        region=region,
                    )
                )

        # Process alerts
        if cycle_alerts:
            self._process_alerts(cycle_alerts)

        # Store metrics
        if cycle_metrics:
            self._store_metrics(cycle_metrics)

        # Check for hardcoded values
        self._check_hardcoded_values()

        self.logger.info(f"Monitoring cycle complete. Found {len(cycle_alerts)} alerts")

    def _check_region_quality(self, region: str) -> tuple[QualityMetrics | None, list[QualityAlert]]:
        """Check quality for a specific region"""
        alerts = []

        # Find latest files for region
        latest_files = self._find_latest_files(region)

        if not latest_files:
            return None, alerts

        # Extract date from latest file
        latest_date = None
        for file_info in latest_files.values():
            if file_info and "date" in file_info:
                latest_date = file_info["date"]
                break

        if not latest_date:
            return None, alerts

        region_date = f"{region}_{latest_date}"

        # Run cross-validation if validator available
        validation_score = 1.0
        if self.cross_validator:
            try:
                report = self.cross_validator.validate_full_pipeline(region_date)
                validation_score = report.overall_score

                # Generate alerts from validation issues
                for issue in report.blocking_issues:
                    alerts.append(
                        QualityAlert(
                            alert_type="validation_failure",
                            severity="critical",
                            message=f"Blocking validation issue: {issue}",
                            details={"issue": issue, "phase": "cross_validation"},
                            timestamp=datetime.now().isoformat(),
                            region=region,
                        )
                    )

                for issue in report.critical_issues:
                    alerts.append(
                        QualityAlert(
                            alert_type="quality_degradation",
                            severity="high",
                            message=f"Critical quality issue: {issue}",
                            details={"issue": issue, "phase": "cross_validation"},
                            timestamp=datetime.now().isoformat(),
                            region=region,
                        )
                    )

            except Exception as e:
                self.logger.warning(f"Cross-validation failed for {region_date}: {e}")
                validation_score = 0.5

        # Check data freshness
        freshness_score, freshness_alerts = self._check_data_freshness(latest_files, region)
        alerts.extend(freshness_alerts)

        # Check variance compliance
        variance_score, variance_alerts = self._check_variance_compliance(latest_files, region)
        alerts.extend(variance_alerts)

        # Calculate overall score
        overall_score = np.mean([validation_score, freshness_score, variance_score])

        # Generate quality degradation alerts
        if overall_score < self.thresholds["critical_quality_threshold"]:
            alerts.append(
                QualityAlert(
                    alert_type="quality_degradation",
                    severity="critical",
                    message=f"Critical quality degradation in {region}: {overall_score:.3f}",
                    details={
                        "overall_score": overall_score,
                        "threshold": self.thresholds["critical_quality_threshold"],
                    },
                    timestamp=datetime.now().isoformat(),
                    region=region,
                )
            )
        elif overall_score < self.thresholds["quality_score_threshold"]:
            alerts.append(
                QualityAlert(
                    alert_type="quality_degradation",
                    severity="high",
                    message=f"Quality degradation in {region}: {overall_score:.3f}",
                    details={
                        "overall_score": overall_score,
                        "threshold": self.thresholds["quality_score_threshold"],
                    },
                    timestamp=datetime.now().isoformat(),
                    region=region,
                )
            )

        # Create metrics snapshot
        metrics = QualityMetrics(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            freshness_score=freshness_score,
            variance_score=variance_score,
            validation_score=validation_score,
            alerts_count=len(alerts),
            critical_alerts=len([a for a in alerts if a.severity == "critical"]),
            region=region,
        )

        return metrics, alerts

    def _find_latest_files(self, region: str) -> dict[str, dict[str, Any] | None]:
        """Find latest files for each data source"""
        latest_files = {}

        base_paths = {
            "discovery": "data/outputs/macro_analysis/discovery",
            "analysis": "data/outputs/macro_analysis/analysis",
            "synthesis": "data/outputs/macro_analysis",
            "validation": "data/outputs/macro_analysis/validation",
        }

        for source, base_path in base_paths.items():
            if not os.path.exists(base_path):
                latest_files[source] = None
                continue

            # Find files matching region pattern
            import glob

            if source == "synthesis":
                pattern = f"{base_path}/{region}_*.md"
            else:
                pattern = f"{base_path}/{region}_*_{source}.json"

            files = glob.glob(pattern)

            if files:
                # Get most recent file
                latest_file = max(files, key=os.path.getctime)

                # Extract date from filename
                filename = os.path.basename(latest_file)
                try:
                    if source == "synthesis":
                        # Format: REGION_YYYYMMDD.md
                        date_part = filename.split("_")[1].split(".")[0]
                    else:
                        # Format: REGION_YYYYMMDD_source.json
                        date_part = filename.split("_")[1]

                    latest_files[source] = {
                        "file_path": latest_file,
                        "date": date_part,
                        "timestamp": os.path.getctime(latest_file),
                    }
                except Exception as e:
                    self.logger.warning(f"Could not parse date from {filename}: {e}")
                    latest_files[source] = None
            else:
                latest_files[source] = None

        return latest_files

    def _check_data_freshness(
        self, files: dict[str, dict[str, Any] | None], region: str
    ) -> tuple[float, list[QualityAlert]]:
        """Check data freshness and generate staleness alerts"""
        alerts = []
        freshness_scores = []

        current_time = datetime.now()
        staleness_threshold = timedelta(hours=self.thresholds["staleness_hours"])

        for source, file_info in files.items():
            if not file_info:
                continue

            file_timestamp = datetime.fromtimestamp(file_info["timestamp"])
            age = current_time - file_timestamp

            if age > staleness_threshold:
                alerts.append(
                    QualityAlert(
                        alert_type="staleness",
                        severity="high" if age > staleness_threshold * 2 else "medium",
                        message=f"Stale data in {source} for {region}: {age.total_seconds() / 3600:.1f}h old",
                        details={
                            "source": source,
                            "age_hours": age.total_seconds() / 3600,
                            "threshold_hours": self.thresholds["staleness_hours"],
                        },
                        timestamp=datetime.now().isoformat(),
                        region=region,
                    )
                )
                freshness_scores.append(0.0)
            else:
                # Score based on how fresh the data is
                freshness_ratio = 1.0 - (age.total_seconds() / staleness_threshold.total_seconds())
                freshness_scores.append(max(0.0, freshness_ratio))

        overall_freshness = np.mean(freshness_scores) if freshness_scores else 1.0
        return overall_freshness, alerts

    def _check_variance_compliance(
        self, files: dict[str, dict[str, Any] | None], region: str
    ) -> tuple[float, list[QualityAlert]]:
        """Check variance compliance for key indicators"""
        alerts = []
        variance_scores = []

        # Check discovery file for variance data if available
        discovery_info = files.get("discovery")
        if discovery_info and discovery_info["file_path"].endswith(".json"):
            try:
                with open(discovery_info["file_path"]) as f:
                    discovery_data = json.load(f)

                # Check for variance analysis in CLI data quality
                cli_quality = discovery_data.get("cli_data_quality", {})
                consistency = cli_quality.get("consistency_validation", {})

                if "variance_analysis" in consistency:
                    variance_analysis = consistency["variance_analysis"]
                    violations = variance_analysis.get("violations", [])

                    for violation in violations:
                        alerts.append(
                            QualityAlert(
                                alert_type="variance",
                                severity="high",
                                message=f"Variance threshold exceeded: {violation}",
                                details={"violation": violation, "source": "discovery"},
                                timestamp=datetime.now().isoformat(),
                                region=region,
                            )
                        )

                    # Score based on violations
                    max_variance = variance_analysis.get(
                        "max_variance_threshold", self.thresholds["variance_threshold"]
                    )
                    if violations:
                        variance_scores.append(0.0)
                    else:
                        variance_scores.append(1.0)

            except Exception as e:
                self.logger.warning(f"Could not check variance in discovery file: {e}")

        # Check analysis file for variance compliance
        analysis_info = files.get("analysis")
        if analysis_info and analysis_info["file_path"].endswith(".json"):
            try:
                with open(analysis_info["file_path"]) as f:
                    analysis_data = json.load(f)

                # Check analysis quality metrics
                quality_metrics = analysis_data.get("analysis_quality_metrics", {})
                variance_compliance = quality_metrics.get("variance_compliance", {})

                exceeded_thresholds = variance_compliance.get("exceeded_thresholds", [])
                for threshold_violation in exceeded_thresholds:
                    alerts.append(
                        QualityAlert(
                            alert_type="variance",
                            severity="high",
                            message=f"Analysis variance exceeded: {threshold_violation.get('indicator')}",
                            details=threshold_violation,
                            timestamp=datetime.now().isoformat(),
                            region=region,
                            indicator=threshold_violation.get("indicator"),
                        )
                    )

                variance_score = variance_compliance.get("variance_score", 1.0)
                variance_scores.append(variance_score)

            except Exception as e:
                self.logger.warning(f"Could not check variance in analysis file: {e}")

        overall_variance = np.mean(variance_scores) if variance_scores else 1.0
        return overall_variance, alerts

    def _check_hardcoded_values(self):
        """Check for hardcoded values across output files"""
        if not self.fed_validator:
            return

        try:
            # Check output directories for hardcoded values
            directories = [
                "data/outputs/macro_analysis/discovery",
                "data/outputs/macro_analysis/analysis",
                "data/outputs/macro_analysis",
            ]

            for directory in directories:
                if os.path.exists(directory):
                    issues = self.fed_validator.check_directory(directory)

                    for issue in issues:
                        self.alerts.append(
                            QualityAlert(
                                alert_type="hardcoded_values",
                                severity="medium",
                                message=f"Hardcoded value detected in {issue['file']}",
                                details={
                                    "file": issue["file"],
                                    "line": issue["line"],
                                    "matched_text": issue["matched_text"],
                                    "severity": issue["severity"],
                                },
                                timestamp=datetime.now().isoformat(),
                            )
                        )

        except Exception as e:
            self.logger.warning(f"Could not check hardcoded values: {e}")

    def _process_alerts(self, alerts: list[QualityAlert]):
        """Process and handle alerts"""
        self.alerts.extend(alerts)

        # Log alerts
        for alert in alerts:
            log_level = {
                "low": logging.INFO,
                "medium": logging.WARNING,
                "high": logging.ERROR,
                "critical": logging.CRITICAL,
            }.get(alert.severity, logging.WARNING)

            self.logger.log(log_level, f"ALERT [{alert.alert_type}]: {alert.message}")

        # Send email notifications if enabled
        if self.config["email_notifications"]["enabled"]:
            self._send_email_alerts(alerts)

        # Store alerts
        self._store_alerts(alerts)

    def _store_alerts(self, alerts: list[QualityAlert]):
        """Store alerts to file"""
        alerts_file = self.config["storage"]["alerts_file"]
        os.makedirs(os.path.dirname(alerts_file), exist_ok=True)

        # Load existing alerts
        existing_alerts = []
        if os.path.exists(alerts_file):
            try:
                with open(alerts_file) as f:
                    existing_alerts = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load existing alerts: {e}")

        # Add new alerts
        for alert in alerts:
            existing_alerts.append(asdict(alert))

        # Keep only recent alerts (last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        recent_alerts = [alert for alert in existing_alerts if datetime.fromisoformat(alert["timestamp"]) > cutoff_time]

        # Save alerts
        try:
            with open(alerts_file, "w") as f:
                json.dump(recent_alerts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save alerts: {e}")

    def _store_metrics(self, metrics: list[QualityMetrics]):
        """Store quality metrics"""
        metrics_file = self.config["storage"]["metrics_file"]
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

        # Load existing metrics
        existing_metrics = []
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file) as f:
                    existing_metrics = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load existing metrics: {e}")

        # Add new metrics
        for metric in metrics:
            existing_metrics.append(asdict(metric))

        # Keep only recent metrics (last 30 days)
        cutoff_time = datetime.now() - timedelta(days=30)
        recent_metrics = [
            metric for metric in existing_metrics if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]

        # Save metrics
        try:
            with open(metrics_file, "w") as f:
                json.dump(recent_metrics, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save metrics: {e}")

    def _send_email_alerts(self, alerts: list[QualityAlert]):
        """Send email notifications for alerts"""
        if not alerts:
            return

        email_config = self.config["email_notifications"]

        try:
            # Create email content
            subject = f"Data Quality Alert - {len(alerts)} issues detected"

            body_lines = [
                "Data Quality Monitoring Alert",
                "=" * 40,
                f"Timestamp: {datetime.now().isoformat()}",
                f"Total Alerts: {len(alerts)}",
                "",
                "ALERTS:",
                "-" * 20,
            ]

            for alert in alerts:
                body_lines.extend(
                    [
                        f"Type: {alert.alert_type}",
                        f"Severity: {alert.severity.upper()}",
                        f"Message: {alert.message}",
                        f"Region: {alert.region or 'N/A'}",
                        f"Time: {alert.timestamp}",
                        "",
                    ]
                )

            body = "\n".join(body_lines)

            # Send email
            msg = MIMEMultipart()
            msg["From"] = email_config["from_email"]
            msg["To"] = ", ".join(email_config["to_emails"])
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()

            if email_config.get("password"):
                server.login(email_config["from_email"], email_config["password"])

            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email alert sent to {len(email_config['to_emails'])} recipients")

        except Exception as e:
            self.logger.error(f"Could not send email alert: {e}")

    def generate_quality_report(self, days: int = 7) -> dict[str, Any]:
        """Generate quality report for specified number of days"""
        cutoff_time = datetime.now() - timedelta(days=days)

        # Load alerts and metrics
        alerts_file = self.config["storage"]["alerts_file"]
        metrics_file = self.config["storage"]["metrics_file"]

        alerts = []
        metrics = []

        if os.path.exists(alerts_file):
            try:
                with open(alerts_file) as f:
                    all_alerts = json.load(f)
                alerts = [alert for alert in all_alerts if datetime.fromisoformat(alert["timestamp"]) > cutoff_time]
            except Exception as e:
                self.logger.warning(f"Could not load alerts for report: {e}")

        if os.path.exists(metrics_file):
            try:
                with open(metrics_file) as f:
                    all_metrics = json.load(f)
                metrics = [
                    metric for metric in all_metrics if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
                ]
            except Exception as e:
                self.logger.warning(f"Could not load metrics for report: {e}")

        # Generate report
        report = {
            "report_period_days": days,
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
                "high_alerts": len([a for a in alerts if a["severity"] == "high"]),
                "quality_checks": len(metrics),
            },
            "alert_breakdown": {},
            "quality_trends": {},
            "regional_analysis": {},
            "recommendations": [],
        }

        # Alert breakdown by type
        alert_types = {}
        for alert in alerts:
            alert_type = alert["alert_type"]
            if alert_type not in alert_types:
                alert_types[alert_type] = 0
            alert_types[alert_type] += 1

        report["alert_breakdown"] = alert_types

        # Quality trends
        if metrics:
            overall_scores = [m["overall_score"] for m in metrics]
            freshness_scores = [m["freshness_score"] for m in metrics]
            variance_scores = [m["variance_score"] for m in metrics]

            report["quality_trends"] = {
                "average_overall_score": np.mean(overall_scores),
                "average_freshness_score": np.mean(freshness_scores),
                "average_variance_score": np.mean(variance_scores),
                "quality_trend": (
                    "improving" if len(overall_scores) > 1 and overall_scores[-1] > overall_scores[0] else "stable"
                ),
                "total_measurements": len(metrics),
            }

        # Regional analysis
        regional_metrics = {}
        for metric in metrics:
            region = metric.get("region")
            if region:
                if region not in regional_metrics:
                    regional_metrics[region] = []
                regional_metrics[region].append(metric["overall_score"])

        for region, scores in regional_metrics.items():
            report["regional_analysis"][region] = {
                "average_score": np.mean(scores),
                "measurements": len(scores),
                "status": "good" if np.mean(scores) > 0.85 else "needs_attention",
            }

        # Recommendations
        if report["summary"]["critical_alerts"] > 0:
            report["recommendations"].append("Address critical alerts immediately")

        if report["quality_trends"].get("average_overall_score", 1.0) < 0.85:
            report["recommendations"].append("Overall quality below threshold - investigate data sources")

        if alert_types.get("staleness", 0) > 0:
            report["recommendations"].append("Address data staleness issues")

        if alert_types.get("variance", 0) > 0:
            report["recommendations"].append("Investigate variance threshold violations")

        return report


def main():
    """Command-line interface for data quality monitoring"""
    parser = argparse.ArgumentParser(description="Data Quality Monitoring and Alerting")

    parser.add_argument("--start-monitoring", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--duration-hours", type=int, help="Monitoring duration in hours")
    parser.add_argument("--check-quality", action="store_true", help="Run single quality check")
    parser.add_argument("--region", help="Region to check (for single check)")
    parser.add_argument("--generate-report", action="store_true", help="Generate quality report")
    parser.add_argument("--days", type=int, default=7, help="Report period in days")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file for reports")

    args = parser.parse_args()

    if not any([args.start_monitoring, args.check_quality, args.generate_report]):
        parser.print_help()
        sys.exit(1)

    # Initialize monitor
    monitor = DataQualityMonitor(args.config)

    try:
        if args.start_monitoring:
            monitor.start_monitoring(args.duration_hours)

        elif args.check_quality:
            if args.region:
                metrics, alerts = monitor._check_region_quality(args.region)
                print("Quality check for {args.region}:")
                if metrics:
                    print("  Overall Score: {metrics.overall_score:.3f}")
                    print("  Alerts: {len(alerts)}")
                else:
                    print("  No data found")
            else:
                print("Error: --region required for quality check")
                sys.exit(1)

        elif args.generate_report:
            report = monitor.generate_quality_report(args.days)

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
                print("Report saved to {args.output}")
            else:
                print(json.dumps(report, indent=2))

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    import argparse

    main()
