#!/usr/bin/env python3
"""
BGeometrics CLI

Command-line interface for BGeometrics Bitcoin on-chain data with:
- MVRV (Market Value to Realized Value) ratio with daily updates
- MVRV Z-Score for statistical market analysis and cycle detection
- LTH-MVRV (Long Term Holder) metrics for institutional analysis
- Completely free API with no authentication required
- Perfect for Bitcoin cycle analysis and on-chain metrics tracking
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.bgeometrics import create_bgeometrics_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class BGeometricsCLI(BaseFinancialCLI):
    """CLI for BGeometrics Bitcoin on-chain data service"""

    def __init__(self):
        super().__init__(
            service_name="bgeometrics",
            description="BGeometrics Bitcoin on-chain data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_bgeometrics_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform BGeometrics service health check"""
        try:
            service = self._get_service(env)
            # Test with a simple current MVRV call
            result = service.get_current_mvrv()
            if result:
                return {"status": "healthy", "service": "bgeometrics", "env": env}
            return {
                "status": "degraded",
                "service": "bgeometrics",
                "env": env,
                "note": "No data returned",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "bgeometrics",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        service = self._get_service(env)
        if action == "clear":
            service.clear_cache()
            return {
                "action": "clear",
                "service": "bgeometrics",
                "env": env,
                "status": "completed",
            }
        if action == "cleanup":
            service.cleanup_cache()
            return {
                "action": "cleanup",
                "service": "bgeometrics",
                "env": env,
                "status": "completed",
            }
        return {
            "action": action,
            "service": "bgeometrics",
            "env": env,
            "status": "unknown_action",
        }

    def _add_service_commands(self) -> None:
        """Add BGeometrics specific commands"""

        @self.app.command("mvrv")
        def get_mvrv_ratio(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get MVRV (Market Value to Realized Value) ratio data"""
            try:
                service = self._get_service(env)

                result = service.get_mvrv_ratio(start_date=start_date, end_date=end_date if end_date else None)
                self._output_result(result, output_format, "MVRV Ratio")

            except Exception as e:
                self._handle_error(e, "Failed to get MVRV ratio data")

        @self.app.command("mvrv-zscore")
        def get_mvrv_zscore(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get MVRV Z-Score for statistical market analysis"""
            try:
                service = self._get_service(env)

                result = service.get_mvrv_zscore(start_date=start_date, end_date=end_date if end_date else None)
                self._output_result(result, output_format, "MVRV Z-Score")

            except Exception as e:
                self._handle_error(e, "Failed to get MVRV Z-Score data")

        @self.app.command("lth-mvrv")
        def get_lth_mvrv(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Long Term Holder MVRV (155+ days) data"""
            try:
                service = self._get_service(env)

                result = service.get_lth_mvrv(start_date=start_date, end_date=end_date if end_date else None)
                self._output_result(result, output_format, "LTH-MVRV")

            except Exception as e:
                self._handle_error(e, "Failed to get LTH-MVRV data")

        @self.app.command("cycle-metrics")
        def get_bitcoin_cycle_metrics(
            start_date: str = typer.Option("2024-01-01", help="Start date (YYYY-MM-DD)"),
            end_date: str = typer.Option("", help="End date (YYYY-MM-DD, default: latest)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive Bitcoin cycle metrics including all MVRV variants"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_cycle_metrics(
                    start_date=start_date, end_date=end_date if end_date else None
                )
                self._output_result(result, output_format, "Bitcoin Cycle Metrics")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin cycle metrics")

        @self.app.command("current")
        def get_current_mvrv(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current MVRV ratio with analysis and interpretation"""
            try:
                service = self._get_service(env)

                result = service.get_current_mvrv()
                self._output_result(result, output_format, "Current MVRV Analysis")

            except Exception as e:
                self._handle_error(e, "Failed to get current MVRV analysis")

        @self.app.command("status")
        def get_market_status(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get current Bitcoin market status based on MVRV indicators"""
            try:
                service = self._get_service(env)

                # Get current data for all MVRV metrics
                current_mvrv = service.get_current_mvrv()

                if not current_mvrv:
                    self._handle_error(Exception("No data available"), "No MVRV data available")
                    return

                # Create market status summary
                status = {
                    "timestamp": current_mvrv.get("date", "N/A"),
                    "mvrv_ratio": current_mvrv.get("mvrv") or current_mvrv.get("value", "N/A"),
                    "market_zone": current_mvrv.get("mvrv_zone", "N/A"),
                    "analysis": current_mvrv.get("analysis", {}),
                    "service": "BGeometrics",
                    "data_source": "bitcoin-data.com",
                }

                self._output_result(status, output_format, "Bitcoin Market Status")

            except Exception as e:
                self._handle_error(e, "Failed to get market status")

        @self.app.command("zones")
        def analyze_mvrv_zones(
            days: int = typer.Option(365, help="Number of days to analyze"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Analyze time spent in different MVRV zones over specified period"""
            try:
                service = self._get_service(env)

                # Calculate date range
                from datetime import datetime, timedelta

                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

                # Get MVRV data for the period
                mvrv_data = service.get_mvrv_ratio(start_date, end_date)

                if not mvrv_data:
                    self._handle_error(
                        Exception("No data available"),
                        "No MVRV data available for analysis",
                    )
                    return

                # Analyze zones
                zones = {
                    "Deep Value Zone (≤0.5)": 0,
                    "Accumulation Zone (0.5-1.0)": 0,
                    "Normal Zone (1.0-2.0)": 0,
                    "Euphoria Zone (2.0-3.5)": 0,
                    "Extreme Bubble Zone (>3.5)": 0,
                }

                total_days = len(mvrv_data)

                for item in mvrv_data:
                    mvrv_value = float(item.get("mvrv") or item.get("value", 0))
                    if mvrv_value <= 0.5:
                        zones["Deep Value Zone (≤0.5)"] += 1
                    elif mvrv_value <= 1.0:
                        zones["Accumulation Zone (0.5-1.0)"] += 1
                    elif mvrv_value <= 2.0:
                        zones["Normal Zone (1.0-2.0)"] += 1
                    elif mvrv_value <= 3.5:
                        zones["Euphoria Zone (2.0-3.5)"] += 1
                    else:
                        zones["Extreme Bubble Zone (>3.5)"] += 1

                # Calculate percentages
                analysis = {
                    "period_days": days,
                    "total_data_points": total_days,
                    "zone_distribution": {
                        zone: {
                            "days": count,
                            "percentage": round((count / total_days) * 100, 1) if total_days > 0 else 0,
                        }
                        for zone, count in zones.items()
                    },
                    "dominant_zone": max(zones, key=zones.get) if zones else "N/A",
                }

                self._output_result(analysis, output_format, f"MVRV Zone Analysis ({days} days)")

            except Exception as e:
                self._handle_error(e, "Failed to analyze MVRV zones")


def main():
    """Main entry point for the BGeometrics CLI"""
    cli = BGeometricsCLI()
    cli.run()


if __name__ == "__main__":
    main()
