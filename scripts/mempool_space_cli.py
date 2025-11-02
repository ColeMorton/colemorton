#!/usr/bin/env python3
"""
Mempool.space CLI

Command-line interface for Mempool.space Bitcoin blockchain data with:
- Real-time Bitcoin mempool monitoring and fee estimation
- Block data and transaction analysis
- Mining statistics and hash rate information
- Network health metrics and confirmation tracking
- Lightning Network statistics and node information
- Completely free API with no authentication required
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.mempool_space import create_mempool_space_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class MempoolSpaceCLI(BaseFinancialCLI):
    """CLI for Mempool.space Bitcoin blockchain service"""

    def __init__(self):
        super().__init__(
            service_name="mempool_space",
            description="Mempool.space Bitcoin blockchain data service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_mempool_space_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Mempool.space service health check"""
        try:
            service = self._get_service(env)
            service.get_fee_estimates()
            return {"status": "healthy", "service": "mempool_space", "env": env}
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "mempool_space",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "mempool_space",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add Mempool.space specific commands"""

        @self.app.command("fees")
        def get_fee_estimates(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get recommended Bitcoin transaction fees"""
            try:
                service = self._get_service(env)

                result = service.get_fee_estimates()
                self._output_result(result, output_format, "Bitcoin Fee Estimates")

            except Exception as e:
                self._handle_error(e, "Failed to get fee estimates")

        @self.app.command("mempool")
        def get_mempool_info(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current mempool statistics"""
            try:
                service = self._get_service(env)

                result = service.get_mempool_info()
                self._output_result(result, output_format, "Mempool Statistics")

            except Exception as e:
                self._handle_error(e, "Failed to get mempool info")

        @self.app.command("blocks")
        def get_recent_blocks(
            limit: int = typer.Option(10, help="Number of recent blocks (max 25)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get recent Bitcoin blocks"""
            try:
                service = self._get_service(env)

                if limit > 25:
                    limit = 25

                result = service.get_recent_blocks(limit)
                self._output_result(result, output_format, f"Recent {limit} Blocks")

            except Exception as e:
                self._handle_error(e, "Failed to get recent blocks")

        @self.app.command("block")
        def get_block_info(
            block_hash: str = typer.Argument(..., help="Block hash or block height"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed information about a specific block"""
            try:
                service = self._get_service(env)

                result = service.get_block_info(block_hash)
                self._output_result(result, output_format, f"Block Info: {block_hash}")

            except Exception as e:
                self._handle_error(e, f"Failed to get block info for {block_hash}")

        @self.app.command("transaction")
        def get_transaction_info(
            txid: str = typer.Argument(..., help="Transaction ID (txid)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed information about a Bitcoin transaction"""
            try:
                service = self._get_service(env)

                result = service.get_transaction_info(txid)
                self._output_result(result, output_format, f"Transaction: {txid}")

            except Exception as e:
                self._handle_error(e, f"Failed to get transaction info for {txid}")

        @self.app.command("difficulty")
        def get_difficulty_info(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin mining difficulty information"""
            try:
                service = self._get_service(env)

                result = service.get_difficulty_info()
                self._output_result(result, output_format, "Mining Difficulty Info")

            except Exception as e:
                self._handle_error(e, "Failed to get difficulty info")

        @self.app.command("hashrate")
        def get_hashrate_info(
            timeframe: str = typer.Option("1w", help="Timeframe (1d, 1w, 1m, 3m, 6m, 1y)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin network hash rate statistics"""
            try:
                service = self._get_service(env)

                result = service.get_hashrate_info(timeframe)
                self._output_result(result, output_format, f"Hash Rate ({timeframe})")

            except Exception as e:
                self._handle_error(e, f"Failed to get hashrate info for {timeframe}")

        @self.app.command("price")
        def get_bitcoin_price(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current Bitcoin price from Mempool.space"""
            try:
                service = self._get_service(env)

                result = service.get_bitcoin_price()
                self._output_result(result, output_format, "Bitcoin Price")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin price")

        @self.app.command("address")
        def get_address_info(
            address: str = typer.Argument(..., help="Bitcoin address"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get information about a Bitcoin address"""
            try:
                service = self._get_service(env)

                result = service.get_address_info(address)
                self._output_result(result, output_format, f"Address Info: {address}")

            except Exception as e:
                self._handle_error(e, f"Failed to get address info for {address}")

        @self.app.command("lightning")
        def get_lightning_stats(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Lightning Network statistics"""
            try:
                service = self._get_service(env)

                result = service.get_lightning_stats()
                self._output_result(result, output_format, "Lightning Network Stats")

            except Exception as e:
                self._handle_error(e, "Failed to get Lightning Network stats")


def main():
    """Main entry point for the Mempool.space CLI"""
    cli = MempoolSpaceCLI()
    cli.run()


if __name__ == "__main__":
    main()
