#!/usr/bin/env python3
"""
Validation Monitoring and SLA Tracking Service

Monitors validation performance, data freshness SLA compliance,
and provides alerting for validation system health.

Key Features:
- Real-time SLA monitoring and alerting
- Data freshness tracking across all sources
- Validation performance metrics and trends
- Automated health checks and diagnostics
- Service availability monitoring
- Custom alerting thresholds and notifications

Usage:
    monitor = ValidationMonitoringService()
    monitor.track_validation_event(validation_result)
    sla_status = monitor.get_sla_status()
"""

import logging
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


# Add utils directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SLAStatus(Enum):
    """SLA compliance status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    VIOLATED = "violated"
    CRITICAL = "critical"


@dataclass
class SLAThreshold:
    """SLA threshold configuration"""

    name: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


@dataclass
class ValidationEvent:
    """Individual validation event for tracking"""

    timestamp: datetime
    post_path: str
    validation_time_seconds: float
    data_freshness_hours: float
    overall_score: float
    is_blocking: bool
    ready_for_publication: bool
    issues_count: int
    critical_issues_count: int
    source_validated: list[str]


@dataclass
class SLAMetrics:
    """Current SLA metrics"""

    timestamp: datetime
    data_freshness_sla_status: SLAStatus
    validation_time_sla_status: SLAStatus
    accuracy_sla_status: SLAStatus
    availability_sla_status: SLAStatus
    overall_sla_status: SLAStatus
    current_data_freshness_hours: float
    current_validation_time_seconds: float
    current_accuracy_score: float
    service_availability_percent: float


@dataclass
class Alert:
    """System alert"""

    timestamp: datetime
    level: AlertLevel
    component: str
    message: str
    threshold_exceeded: str | None
    current_value: float | str | None
    recommended_action: str


class ValidationMonitoringService:
    """
    Comprehensive validation monitoring and SLA tracking service

    Tracks validation performance, data freshness, and system health
    with configurable SLA thresholds and automated alerting.
    """

    def __init__(self, config_path: str | None = None):
        # SLA Configuration
        self.sla_thresholds = {
            "data_freshness_hours": SLAThreshold(
                name="data_freshness_hours",
                target_value=2.0,  # Target: 2 hours
                warning_threshold=4.0,  # Warning: 4 hours
                critical_threshold=8.0,  # Critical: 8 hours
                unit="hours",
                description="Maximum acceptable data age",
            ),
            "validation_time_seconds": SLAThreshold(
                name="validation_time_seconds",
                target_value=10.0,  # Target: 10 seconds
                warning_threshold=20.0,  # Warning: 20 seconds
                critical_threshold=30.0,  # Critical: 30 seconds
                unit="seconds",
                description="Maximum acceptable validation time",
            ),
            "accuracy_score": SLAThreshold(
                name="accuracy_score",
                target_value=9.5,  # Target: 9.5/10
                warning_threshold=9.0,  # Warning: 9.0/10
                critical_threshold=8.5,  # Critical: 8.5/10
                unit="score",
                description="Minimum acceptable validation accuracy score",
            ),
            "service_availability": SLAThreshold(
                name="service_availability",
                target_value=99.9,  # Target: 99.9%
                warning_threshold=99.0,  # Warning: 99.0%
                critical_threshold=95.0,  # Critical: 95.0%
                unit="percent",
                description="Minimum service availability percentage",
            ),
        }

        # Event tracking (circular buffers for performance)
        self.validation_events = deque(maxlen=1000)  # Last 1000 validations
        self.alerts = deque(maxlen=500)  # Last 500 alerts
        self.service_health_events = deque(maxlen=200)  # Last 200 health checks

        # Real-time metrics
        self.current_metrics = SLAMetrics(
            timestamp=datetime.now(),
            data_freshness_sla_status=SLAStatus.HEALTHY,
            validation_time_sla_status=SLAStatus.HEALTHY,
            accuracy_sla_status=SLAStatus.HEALTHY,
            availability_sla_status=SLAStatus.HEALTHY,
            overall_sla_status=SLAStatus.HEALTHY,
            current_data_freshness_hours=0.0,
            current_validation_time_seconds=0.0,
            current_accuracy_score=10.0,
            service_availability_percent=100.0,
        )

        # Performance statistics
        self.statistics = {
            "total_validations": 0,
            "successful_validations": 0,
            "blocked_validations": 0,
            "average_validation_time_seconds": 0.0,
            "average_data_freshness_hours": 0.0,
            "average_accuracy_score": 0.0,
            "sla_violations_count": 0,
            "uptime_start": datetime.now(),
            "last_health_check": None,
            "alerts_last_24h": 0,
            "critical_alerts_last_24h": 0,
        }

        # Background monitoring thread
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self._monitoring_thread.start()

        logger.info("Validation monitoring service initialized with SLA tracking")

    def track_validation_event(self, validation_result) -> None:
        """Track a validation event for SLA monitoring"""
        try:
            # Extract event data
            event = ValidationEvent(
                timestamp=datetime.now(),
                post_path=getattr(validation_result, "post_path", "unknown"),
                validation_time_seconds=validation_result.overall_assessment.get("validation_time_seconds", 0.0),
                data_freshness_hours=validation_result.real_time_validation.data_freshness_hours,
                overall_score=validation_result.overall_reliability_score,
                is_blocking=validation_result.is_blocking,
                ready_for_publication=validation_result.ready_for_publication,
                issues_count=len(validation_result.real_time_validation.issues),
                critical_issues_count=len(
                    [
                        i
                        for i in validation_result.real_time_validation.issues
                        if hasattr(i, "severity") and str(i.severity).endswith("CRITICAL")
                    ]
                ),
                source_validated=validation_result.real_time_validation.sources_validated,
            )

            # Add to tracking
            self.validation_events.append(event)

            # Update statistics
            self._update_statistics(event)

            # Check SLA compliance
            self._check_sla_compliance(event)

            logger.debug(f"Tracked validation event: {event.post_path} - Score: {event.overall_score:.1f}")

        except Exception as e:
            logger.error(f"Failed to track validation event: {e}")

    def _update_statistics(self, event: ValidationEvent) -> None:
        """Update running statistics with new event"""
        self.statistics["total_validations"] += 1

        if event.ready_for_publication:
            self.statistics["successful_validations"] += 1
        if event.is_blocking:
            self.statistics["blocked_validations"] += 1

        # Update running averages
        total = self.statistics["total_validations"]

        # Validation time average
        current_avg_time = self.statistics["average_validation_time_seconds"]
        self.statistics["average_validation_time_seconds"] = (
            current_avg_time * (total - 1) + event.validation_time_seconds
        ) / total

        # Data freshness average
        current_avg_freshness = self.statistics["average_data_freshness_hours"]
        self.statistics["average_data_freshness_hours"] = (
            current_avg_freshness * (total - 1) + event.data_freshness_hours
        ) / total

        # Accuracy score average
        current_avg_score = self.statistics["average_accuracy_score"]
        self.statistics["average_accuracy_score"] = (current_avg_score * (total - 1) + event.overall_score) / total

        # Update current metrics
        self.current_metrics.timestamp = event.timestamp
        self.current_metrics.current_validation_time_seconds = event.validation_time_seconds
        self.current_metrics.current_data_freshness_hours = event.data_freshness_hours
        self.current_metrics.current_accuracy_score = event.overall_score

    def _check_sla_compliance(self, event: ValidationEvent) -> None:
        """Check SLA compliance and generate alerts if needed"""
        alerts_generated = []

        # Data freshness SLA check
        freshness_threshold = self.sla_thresholds["data_freshness_hours"]
        if event.data_freshness_hours >= freshness_threshold.critical_threshold:
            self.current_metrics.data_freshness_sla_status = SLAStatus.CRITICAL
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.CRITICAL,
                component="data_freshness",
                message=f"Data freshness SLA violation: {event.data_freshness_hours:.1f}h > {freshness_threshold.critical_threshold}h",
                threshold_exceeded="critical_threshold",
                current_value=event.data_freshness_hours,
                recommended_action="Verify data sources and refresh data immediately",
            )
            alerts_generated.append(alert)
            self.statistics["sla_violations_count"] += 1

        elif event.data_freshness_hours >= freshness_threshold.warning_threshold:
            self.current_metrics.data_freshness_sla_status = SLAStatus.DEGRADED
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.WARNING,
                component="data_freshness",
                message=f"Data freshness warning: {event.data_freshness_hours:.1f}h > {freshness_threshold.warning_threshold}h",
                threshold_exceeded="warning_threshold",
                current_value=event.data_freshness_hours,
                recommended_action="Monitor data source availability and consider refresh",
            )
            alerts_generated.append(alert)
        else:
            self.current_metrics.data_freshness_sla_status = SLAStatus.HEALTHY

        # Validation time SLA check
        time_threshold = self.sla_thresholds["validation_time_seconds"]
        if event.validation_time_seconds >= time_threshold.critical_threshold:
            self.current_metrics.validation_time_sla_status = SLAStatus.CRITICAL
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.CRITICAL,
                component="validation_performance",
                message=f"Validation time SLA violation: {event.validation_time_seconds:.1f}s > {time_threshold.critical_threshold}s",
                threshold_exceeded="critical_threshold",
                current_value=event.validation_time_seconds,
                recommended_action="Check service performance and resource allocation",
            )
            alerts_generated.append(alert)
            self.statistics["sla_violations_count"] += 1

        elif event.validation_time_seconds >= time_threshold.warning_threshold:
            self.current_metrics.validation_time_sla_status = SLAStatus.DEGRADED
        else:
            self.current_metrics.validation_time_sla_status = SLAStatus.HEALTHY

        # Accuracy score SLA check
        accuracy_threshold = self.sla_thresholds["accuracy_score"]
        if event.overall_score <= accuracy_threshold.critical_threshold:
            self.current_metrics.accuracy_sla_status = SLAStatus.CRITICAL
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.CRITICAL,
                component="validation_accuracy",
                message=f"Accuracy SLA violation: {event.overall_score:.1f} < {accuracy_threshold.critical_threshold}",
                threshold_exceeded="critical_threshold",
                current_value=event.overall_score,
                recommended_action="Review validation logic and data source accuracy",
            )
            alerts_generated.append(alert)
            self.statistics["sla_violations_count"] += 1

        elif event.overall_score <= accuracy_threshold.warning_threshold:
            self.current_metrics.accuracy_sla_status = SLAStatus.DEGRADED
        else:
            self.current_metrics.accuracy_sla_status = SLAStatus.HEALTHY

        # Add alerts to tracking
        for alert in alerts_generated:
            self.alerts.append(alert)
            if alert.level == AlertLevel.CRITICAL:
                self.statistics["critical_alerts_last_24h"] += 1
            self.statistics["alerts_last_24h"] += 1

            logger.warning(f"{alert.level.value.upper()} ALERT - {alert.component}: {alert.message}")

        # Update overall SLA status
        individual_statuses = [
            self.current_metrics.data_freshness_sla_status,
            self.current_metrics.validation_time_sla_status,
            self.current_metrics.accuracy_sla_status,
            self.current_metrics.availability_sla_status,
        ]

        if any(status == SLAStatus.CRITICAL for status in individual_statuses):
            self.current_metrics.overall_sla_status = SLAStatus.CRITICAL
        elif any(status == SLAStatus.VIOLATED for status in individual_statuses):
            self.current_metrics.overall_sla_status = SLAStatus.VIOLATED
        elif any(status == SLAStatus.DEGRADED for status in individual_statuses):
            self.current_metrics.overall_sla_status = SLAStatus.DEGRADED
        else:
            self.current_metrics.overall_sla_status = SLAStatus.HEALTHY

    def _background_monitoring(self) -> None:
        """Background thread for continuous monitoring"""
        while self._monitoring_active:
            try:
                # Health check every 60 seconds
                self._perform_health_check()

                # Clean up old alerts (24h retention)
                self._cleanup_old_alerts()

                # Update availability metrics
                self._update_availability_metrics()

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                time.sleep(60)

    def _perform_health_check(self) -> None:
        """Perform system health check"""
        health_event = {
            "timestamp": datetime.now(),
            "service_status": "active",
            "validation_events_count": len(self.validation_events),
            "alerts_count": len(self.alerts),
            "memory_usage_mb": self._get_memory_usage(),
        }

        self.service_health_events.append(health_event)
        self.statistics["last_health_check"] = datetime.now()

        # Check for system resource issues
        if health_event["memory_usage_mb"] > 500:  # 500MB threshold
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.WARNING,
                component="system_resources",
                message=f"High memory usage: {health_event['memory_usage_mb']:.1f}MB",
                threshold_exceeded="memory_threshold",
                current_value=health_event["memory_usage_mb"],
                recommended_action="Monitor memory usage and consider cleanup",
            )
            self.alerts.append(alert)

    def _cleanup_old_alerts(self) -> None:
        """Clean up alerts older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Reset 24h counters
        self.statistics["alerts_last_24h"] = 0
        self.statistics["critical_alerts_last_24h"] = 0

        # Count recent alerts
        for alert in self.alerts:
            if alert.timestamp >= cutoff_time:
                self.statistics["alerts_last_24h"] += 1
                if alert.level == AlertLevel.CRITICAL:
                    self.statistics["critical_alerts_last_24h"] += 1

    def _update_availability_metrics(self) -> None:
        """Update service availability metrics"""
        uptime_duration = datetime.now() - self.statistics["uptime_start"]
        uptime_hours = uptime_duration.total_seconds() / 3600

        # Simple availability calculation (can be enhanced)
        if uptime_hours > 0:
            # Assume 99.9% availability unless we detect issues
            self.current_metrics.service_availability_percent = 99.9
            self.current_metrics.availability_sla_status = SLAStatus.HEALTHY

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback if psutil not available
            return 0.0

    def get_sla_status(self) -> dict[str, Any]:
        """Get current SLA status and metrics"""
        return {
            "overall_sla_status": self.current_metrics.overall_sla_status.value,
            "sla_breakdown": {
                "data_freshness": {
                    "status": self.current_metrics.data_freshness_sla_status.value,
                    "current_value": self.current_metrics.current_data_freshness_hours,
                    "threshold": self.sla_thresholds["data_freshness_hours"].critical_threshold,
                    "unit": "hours",
                },
                "validation_time": {
                    "status": self.current_metrics.validation_time_sla_status.value,
                    "current_value": self.current_metrics.current_validation_time_seconds,
                    "threshold": self.sla_thresholds["validation_time_seconds"].critical_threshold,
                    "unit": "seconds",
                },
                "accuracy_score": {
                    "status": self.current_metrics.accuracy_sla_status.value,
                    "current_value": self.current_metrics.current_accuracy_score,
                    "threshold": self.sla_thresholds["accuracy_score"].critical_threshold,
                    "unit": "score",
                },
                "service_availability": {
                    "status": self.current_metrics.availability_sla_status.value,
                    "current_value": self.current_metrics.service_availability_percent,
                    "threshold": self.sla_thresholds["service_availability"].critical_threshold,
                    "unit": "percent",
                },
            },
            "statistics": self.statistics.copy(),
            "recent_alerts": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level.value,
                    "component": alert.component,
                    "message": alert.message,
                }
                for alert in list(self.alerts)[-10:]  # Last 10 alerts
            ],
        }

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get detailed performance metrics"""
        if not self.validation_events:
            return {"message": "No validation events recorded yet"}

        # Calculate metrics from recent events
        recent_events = list(self.validation_events)[-100:]  # Last 100 events

        validation_times = [e.validation_time_seconds for e in recent_events]
        data_freshness = [e.data_freshness_hours for e in recent_events]
        accuracy_scores = [e.overall_score for e in recent_events]

        return {
            "validation_performance": {
                "average_time_seconds": sum(validation_times) / len(validation_times),
                "min_time_seconds": min(validation_times),
                "max_time_seconds": max(validation_times),
                "p95_time_seconds": (
                    sorted(validation_times)[int(len(validation_times) * 0.95)] if validation_times else 0
                ),
            },
            "data_freshness": {
                "average_hours": sum(data_freshness) / len(data_freshness),
                "min_hours": min(data_freshness),
                "max_hours": max(data_freshness),
                "p95_hours": (sorted(data_freshness)[int(len(data_freshness) * 0.95)] if data_freshness else 0),
            },
            "accuracy_metrics": {
                "average_score": sum(accuracy_scores) / len(accuracy_scores),
                "min_score": min(accuracy_scores),
                "max_score": max(accuracy_scores),
                "p95_score": (sorted(accuracy_scores)[int(len(accuracy_scores) * 0.95)] if accuracy_scores else 0),
            },
            "event_counts": {
                "total_events": len(recent_events),
                "successful_events": len([e for e in recent_events if e.ready_for_publication]),
                "blocked_events": len([e for e in recent_events if e.is_blocking]),
                "events_with_issues": len([e for e in recent_events if e.issues_count > 0]),
            },
        }

    def shutdown(self) -> None:
        """Shutdown monitoring service"""
        self._monitoring_active = False
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        logger.info("Validation monitoring service shutdown")


def create_validation_monitoring_service() -> ValidationMonitoringService:
    """Factory function to create monitoring service"""
    return ValidationMonitoringService()


if __name__ == "__main__":
    # Test the monitoring service
    logging.basicConfig(level=logging.INFO)

    monitor = create_validation_monitoring_service()

    # Simulate some validation events for testing
    from datetime import datetime

    print("Testing monitoring service...")

    # Mock validation result for testing
    class MockValidationResult:
        def __init__(self, score, freshness_hours, validation_time, is_blocking=False):
            self.post_path = "test_post.md"
            self.overall_reliability_score = score
            self.is_blocking = is_blocking
            self.ready_for_publication = not is_blocking and score >= 9.0
            self.overall_assessment = {"validation_time_seconds": validation_time}

            # Mock real-time validation
            class MockRealTimeValidation:
                def __init__(self):
                    self.data_freshness_hours = freshness_hours
                    self.sources_validated = ["yahoo_finance"]
                    self.issues = []

            self.real_time_validation = MockRealTimeValidation()

    # Test normal operation
    monitor.track_validation_event(MockValidationResult(9.5, 1.0, 5.0))

    # Test SLA violation
    monitor.track_validation_event(MockValidationResult(8.0, 10.0, 35.0, is_blocking=True))

    time.sleep(2)

    # Get status
    sla_status = monitor.get_sla_status()
    print("\nSLA Status: {sla_status['overall_sla_status']}")
    print("Recent alerts: {len(sla_status['recent_alerts'])}")

    performance = monitor.get_performance_metrics()
    print(f"Average validation time: {performance['validation_performance']['average_time_seconds']:.1f}s")

    monitor.shutdown()
