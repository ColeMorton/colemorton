"""
CLI Service Logging Utility

Comprehensive logging system for CLI service interactions including:
- Service health monitoring
- Performance tracking
- Error logging and analysis
- Request/response logging
- Service availability statistics
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


@dataclass
class ServiceHealthEvent:
    """Service health event data structure"""

    timestamp: str
    service_name: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: float
    error_message: str | None = None
    endpoint: str | None = None
    request_id: str | None = None


@dataclass
class ServicePerformanceMetrics:
    """Service performance metrics"""

    service_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    uptime_percentage: float
    last_health_check: str
    errors_last_24h: int


class ServiceLogger:
    """Comprehensive logging for CLI service interactions"""

    def __init__(self, logs_directory: str = "./logs"):
        self.logs_dir = Path(logs_directory)
        self.logs_dir.mkdir(exist_ok=True)

        # Initialize loggers
        self._setup_loggers()

        # Storage for metrics
        self.health_events: list[ServiceHealthEvent] = []
        self.performance_cache: dict[str, ServicePerformanceMetrics] = {}

    def _setup_loggers(self):
        """Setup specialized loggers for different aspects"""

        # Main service logger
        self.service_logger = logging.getLogger("cli_service_interactions")
        self.service_logger.setLevel(logging.INFO)

        # Health monitoring logger
        self.health_logger = logging.getLogger("service_health_monitoring")
        self.health_logger.setLevel(logging.INFO)

        # Performance logger
        self.performance_logger = logging.getLogger("service_performance")
        self.performance_logger.setLevel(logging.INFO)

        # Setup file handlers
        self._setup_file_handlers()

    def _setup_file_handlers(self):
        """Setup rotating file handlers for different log types"""

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Service interactions log
        service_handler = RotatingFileHandler(
            self.logs_dir / "service_interactions.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
        )
        service_handler.setFormatter(formatter)
        self.service_logger.addHandler(service_handler)

        # Health monitoring log
        health_handler = RotatingFileHandler(
            self.logs_dir / "service_health.log",
            maxBytes=25 * 1024 * 1024,  # 25MB
            backupCount=3,
        )
        health_handler.setFormatter(formatter)
        self.health_logger.addHandler(health_handler)

        # Performance log
        performance_handler = RotatingFileHandler(
            self.logs_dir / "service_performance.log",
            maxBytes=25 * 1024 * 1024,  # 25MB
            backupCount=3,
        )
        performance_handler.setFormatter(formatter)
        self.performance_logger.addHandler(performance_handler)

    def log_service_request(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        request_id: str = None,
    ):
        """Log service request initiation"""

        self.service_logger.info(
            f"Service request initiated - Service: {service_name}, "
            f"Endpoint: {endpoint}, Method: {method}, ID: {request_id}"
        )

    def log_service_response(
        self,
        service_name: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float,
        request_id: str = None,
        error: str = None,
    ):
        """Log service response completion"""

        level = logging.INFO if status_code < 400 else logging.ERROR

        self.service_logger.log(
            level,
            f"Service response received - Service: {service_name}, "
            f"Endpoint: {endpoint}, Status: {status_code}, "
            f"Response Time: {response_time_ms:.2f}ms, ID: {request_id}"
            f"{f', Error: {error}' if error else ''}",
        )

    def log_health_check(
        self,
        service_name: str,
        status: str,
        response_time_ms: float,
        error_message: str = None,
        endpoint: str = None,
    ):
        """Log service health check result"""

        timestamp = datetime.now().isoformat()

        # Create health event
        health_event = ServiceHealthEvent(
            timestamp=timestamp,
            service_name=service_name,
            status=status,
            response_time_ms=response_time_ms,
            error_message=error_message,
            endpoint=endpoint,
        )

        # Store event
        self.health_events.append(health_event)

        # Keep only last 1000 events per service
        self._cleanup_health_events()

        # Log to health logger
        level = logging.INFO if status == "healthy" else logging.WARNING
        self.health_logger.log(
            level,
            f"Health check - Service: {service_name}, Status: {status}, "
            f"Response Time: {response_time_ms:.2f}ms"
            f"{f', Error: {error_message}' if error_message else ''}",
        )

    def log_performance_metrics(self, service_name: str, metrics: dict[str, Any]):
        """Log service performance metrics"""

        self.performance_logger.info(
            f"Performance metrics - Service: {service_name}, Metrics: {json.dumps(metrics, indent=None)}"
        )

    def get_service_health_summary(self, service_name: str, hours: int = 24) -> dict[str, Any]:
        """Get service health summary for specified time period"""

        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter events for this service and time period
        service_events = [
            event
            for event in self.health_events
            if (event.service_name == service_name and datetime.fromisoformat(event.timestamp) > cutoff_time)
        ]

        if not service_events:
            return {
                "service_name": service_name,
                "status": "no_data",
                "events_count": 0,
                "time_period_hours": hours,
            }

        # Calculate metrics
        total_events = len(service_events)
        healthy_events = len([e for e in service_events if e.status == "healthy"])
        degraded_events = len([e for e in service_events if e.status == "degraded"])
        unhealthy_events = len([e for e in service_events if e.status == "unhealthy"])

        avg_response_time = sum(e.response_time_ms for e in service_events) / total_events

        uptime_percentage = (healthy_events / total_events) * 100

        latest_event = max(service_events, key=lambda e: e.timestamp)

        return {
            "service_name": service_name,
            "current_status": latest_event.status,
            "uptime_percentage": round(uptime_percentage, 2),
            "total_checks": total_events,
            "healthy_checks": healthy_events,
            "degraded_checks": degraded_events,
            "unhealthy_checks": unhealthy_events,
            "average_response_time_ms": round(avg_response_time, 2),
            "last_check": latest_event.timestamp,
            "time_period_hours": hours,
        }

    def get_all_services_health(self, hours: int = 24) -> dict[str, Any]:
        """Get health summary for all monitored services"""

        services = set(event.service_name for event in self.health_events)

        return {
            "summary_timestamp": datetime.now().isoformat(),
            "time_period_hours": hours,
            "services": {
                service_name: self.get_service_health_summary(service_name, hours) for service_name in services
            },
        }

    def export_health_report(self, output_file: str, hours: int = 24):
        """Export comprehensive health report to JSON file"""

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "time_period_hours": hours,
                "total_events": len(self.health_events),
            },
            "services_health": self.get_all_services_health(hours),
            "recent_failures": self._get_recent_failures(hours),
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        self.service_logger.info(f"Health report exported to {output_file}")

    def _get_recent_failures(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent service failures"""

        cutoff_time = datetime.now() - timedelta(hours=hours)

        failures = [
            asdict(event)
            for event in self.health_events
            if (event.status in ["degraded", "unhealthy"] and datetime.fromisoformat(event.timestamp) > cutoff_time)
        ]

        return sorted(failures, key=lambda x: x["timestamp"], reverse=True)

    def _cleanup_health_events(self):
        """Keep only recent health events to prevent memory bloat"""

        if len(self.health_events) > 5000:
            # Keep only most recent 3000 events
            self.health_events = sorted(self.health_events, key=lambda e: e.timestamp, reverse=True)[:3000]


# Global service logger instance
_service_logger: ServiceLogger | None = None


def get_service_logger() -> ServiceLogger:
    """Get global service logger instance"""
    global _service_logger

    if _service_logger is None:
        _service_logger = ServiceLogger()

    return _service_logger


def log_cli_service_health(service_name: str, health_data: dict[str, Any]):
    """Convenience function to log CLI service health check"""

    logger = get_service_logger()

    status = health_data.get("status", "unknown")
    response_time = health_data.get("response_time_ms", 0.0)
    error = health_data.get("error")
    endpoint = health_data.get("test_endpoint") or health_data.get("test_symbol")

    logger.log_health_check(
        service_name=service_name,
        status=status,
        response_time_ms=response_time,
        error_message=error,
        endpoint=endpoint,
    )


def generate_daily_health_report():
    """Generate daily health report for all services"""

    logger = get_service_logger()

    timestamp = datetime.now().strftime("%Y%m%d")
    report_file = f"./logs/daily_health_report_{timestamp}.json"

    logger.export_health_report(report_file, hours=24)

    return report_file
