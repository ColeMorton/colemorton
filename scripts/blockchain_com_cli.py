#!/usr/bin/env python3
"""
Blockchain.com CLI

Command-line interface for Blockchain.com blockchain explorer with:
- Free blockchain explorer API with comprehensive Bitcoin data
- Block information and transaction data access
- Address balance and transaction history
- Network statistics and mempool information
- Raw blockchain data for in-depth analysis
- Completely free API with no authentication required
"""

import sys
from pathlib import Path
from typing import Any

import typer


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from services.blockchain_com import create_blockchain_com_service
from utils.cli_base import BaseFinancialCLI, OutputFormat


class BlockchainComCLI(BaseFinancialCLI):
    """CLI for Blockchain.com blockchain explorer service"""

    def __init__(self):
        super().__init__(
            service_name="blockchain_com",
            description="Blockchain.com blockchain explorer service CLI",
        )
        self.service = None
        self._add_service_commands()

    def _get_service(self, env: str):
        """Get or create service instance"""
        if self.service is None:
            self.service = create_blockchain_com_service(env)
        return self.service

    def perform_health_check(self, env: str) -> dict[str, Any]:
        """Perform Blockchain.com service health check"""
        try:
            service = self._get_service(env)
            service.get_latest_block()
            return {"status": "healthy", "service": "blockchain_com", "env": env}
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "blockchain_com",
                "env": env,
                "error": str(e),
            }

    def perform_cache_action(self, action: str, env: str) -> dict[str, Any]:
        """Perform cache management action"""
        return {
            "action": action,
            "service": "blockchain_com",
            "env": env,
            "status": "no_cache_implemented",
        }

    def _add_service_commands(self) -> None:
        """Add Blockchain.com specific commands"""

        @self.app.command("latest-block")
        def get_latest_block(
            env: str = typer.Option("dev", help="Environment (dev/test/prod)"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get latest block information"""
            try:
                service = self._get_service(env)

                result = service.get_latest_block()
                self._output_result(result, output_format, "Latest Block")

            except Exception as e:
                self._handle_error(e, "Failed to get latest block")

        @self.app.command("block")
        def get_block_info(
            block_hash: str = typer.Argument(..., help="Block hash or height"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed information about a specific block"""
            try:
                service = self._get_service(env)

                result = service.get_block_info(block_hash)
                self._output_result(result, output_format, f"Block {block_hash}")

            except Exception as e:
                self._handle_error(e, f"Failed to get block info for {block_hash}")

        @self.app.command("block-height")
        def get_block_height(
            height: int = typer.Argument(..., help="Block height number"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get block information by height"""
            try:
                service = self._get_service(env)

                result = service.get_block_height(height)
                self._output_result(result, output_format, f"Block Height {height}")

            except Exception as e:
                self._handle_error(e, f"Failed to get block at height {height}")

        @self.app.command("transaction")
        def get_transaction_info(
            tx_hash: str = typer.Argument(..., help="Transaction hash"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get detailed information about a specific transaction"""
            try:
                service = self._get_service(env)

                result = service.get_transaction_info(tx_hash)
                self._output_result(result, output_format, f"Transaction {tx_hash}")

            except Exception as e:
                self._handle_error(e, f"Failed to get transaction info for {tx_hash}")

        @self.app.command("address")
        def get_address_info(
            address: str = typer.Argument(..., help="Bitcoin address"),
            limit: int = typer.Option(50, help="Transaction limit (max 100)"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get address information including balance and transactions"""
            try:
                service = self._get_service(env)

                if limit > 100:
                    limit = 100
                elif limit < 1:
                    limit = 1

                result = service.get_address_info(address, limit)
                self._output_result(result, output_format, f"Address {address}")

            except Exception as e:
                self._handle_error(e, f"Failed to get address info for {address}")

        @self.app.command("balance")
        def get_address_balance(
            address: str = typer.Argument(..., help="Bitcoin address"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get address balance only"""
            try:
                service = self._get_service(env)

                result = service.get_address_balance(address)
                self._output_result(result, output_format, f"Balance for {address}")

            except Exception as e:
                self._handle_error(e, f"Failed to get balance for {address}")

        @self.app.command("multi-balance")
        def get_multiple_addresses_balance(
            addresses: str = typer.Argument(..., help="Comma-separated Bitcoin addresses"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.TABLE, help="Output format"),
        ):
            """Get balances for multiple addresses"""
            try:
                service = self._get_service(env)

                address_list = [addr.strip() for addr in addresses.split(",")]
                if len(address_list) > 100:
                    address_list = address_list[:100]

                result = service.get_multiple_addresses_balance(address_list)
                self._output_result(result, output_format, "Multiple Address Balances")

            except Exception as e:
                self._handle_error(e, "Failed to get multiple address balances")

        @self.app.command("unspent")
        def get_unspent_outputs(
            address: str = typer.Argument(..., help="Bitcoin address"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get unspent transaction outputs for an address"""
            try:
                service = self._get_service(env)

                result = service.get_unspent_outputs(address)
                self._output_result(result, output_format, f"Unspent Outputs for {address}")

            except Exception as e:
                self._handle_error(e, f"Failed to get unspent outputs for {address}")

        @self.app.command("network-stats")
        def get_network_stats(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get Bitcoin network statistics"""
            try:
                service = self._get_service(env)

                result = service.get_network_stats()
                self._output_result(result, output_format, "Network Statistics")

            except Exception as e:
                self._handle_error(e, "Failed to get network statistics")

        @self.app.command("mempool")
        def get_mempool_info(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get mempool statistics"""
            try:
                service = self._get_service(env)

                result = service.get_mempool_info()
                self._output_result(result, output_format, "Mempool Information")

            except Exception as e:
                self._handle_error(e, "Failed to get mempool information")

        @self.app.command("difficulty")
        def get_difficulty(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current Bitcoin mining difficulty"""
            try:
                service = self._get_service(env)

                result = service.get_difficulty()
                self._output_result(result, output_format, "Mining Difficulty")

            except Exception as e:
                self._handle_error(e, "Failed to get mining difficulty")

        @self.app.command("hashrate")
        def get_hashrate(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get estimated network hash rate"""
            try:
                service = self._get_service(env)

                result = service.get_hashrate()
                self._output_result(result, output_format, "Network Hash Rate")

            except Exception as e:
                self._handle_error(e, "Failed to get network hash rate")

        @self.app.command("total-bitcoins")
        def get_total_bitcoins(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get total bitcoins in circulation"""
            try:
                service = self._get_service(env)

                result = service.get_total_bitcoins()
                self._output_result(result, output_format, "Total Bitcoins in Circulation")

            except Exception as e:
                self._handle_error(e, "Failed to get total bitcoins")

        @self.app.command("price")
        def get_market_price_usd(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get current Bitcoin price in USD"""
            try:
                service = self._get_service(env)

                result = service.get_market_price_usd()
                self._output_result(result, output_format, "Bitcoin Price USD")

            except Exception as e:
                self._handle_error(e, "Failed to get Bitcoin price")

        @self.app.command("fees")
        def get_transaction_fee_per_kb(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get average transaction fee per KB"""
            try:
                service = self._get_service(env)

                result = service.get_transaction_fee_per_kb()
                self._output_result(result, output_format, "Transaction Fees")

            except Exception as e:
                self._handle_error(e, "Failed to get transaction fees")

        @self.app.command("blocks-today")
        def get_blocks_mined_today(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get number of blocks mined in the last 24 hours"""
            try:
                service = self._get_service(env)

                result = service.get_blocks_mined_today()
                self._output_result(result, output_format, "Blocks Mined Today")

            except Exception as e:
                self._handle_error(e, "Failed to get blocks mined today")

        @self.app.command("address-transactions")
        def get_address_transactions(
            address: str = typer.Argument(..., help="Bitcoin address"),
            offset: int = typer.Option(0, help="Transaction offset for pagination"),
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get transactions for a specific address with pagination"""
            try:
                service = self._get_service(env)

                if offset < 0:
                    offset = 0

                result = service.get_address_transactions(address, offset)
                self._output_result(result, output_format, f"Transactions for {address}")

            except Exception as e:
                self._handle_error(e, f"Failed to get transactions for {address}")

        @self.app.command("summary")
        def get_blockchain_summary(
            env: str = typer.Option("dev", help="Environment"),
            output_format: str = typer.Option(OutputFormat.JSON, help="Output format"),
        ):
            """Get comprehensive blockchain summary"""
            try:
                service = self._get_service(env)

                result = service.get_blockchain_summary()
                self._output_result(result, output_format, "Blockchain Summary")

            except Exception as e:
                self._handle_error(e, "Failed to get blockchain summary")


def main():
    """Main entry point for the Blockchain.com CLI"""
    cli = BlockchainComCLI()
    cli.run()


if __name__ == "__main__":
    main()
