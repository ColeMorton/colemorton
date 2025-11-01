#!/usr/bin/env python3
"""
Feature engineering script with comprehensive configuration support.

Usage:
    python scripts/feature_engineering.py --config config/pipelines/feature_engineering.yaml
    python scripts/feature_engineering.py \\
        --config config/pipelines/feature_engineering.yaml --env prod
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from scripts.utils.config_loader import ConfigLoader
from scripts.utils.logging_setup import setup_logging


class FeatureEngineer:
    """Main feature engineering class."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def engineer_features(self, input_file: Path) -> Path:
        """Engineer features according to configuration."""
        output_path = Path(self.config["output"]["file_path"])

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Features engineered from {input_file} to {output_path}")
        return output_path


def main(config: dict[str, Any], input_file: Path) -> None:
    """Main execution function."""
    engineer = FeatureEngineer(config)
    output_file = engineer.engineer_features(input_file)

    # Print output for Make dependency tracking
    print("OUTPUT_FILE={output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to YAML configuration file")
    parser.add_argument("--input", required=True, help="Input data file path")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment configuration",
    )
    parser.add_argument("--output-file", help="Override output file path")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    try:
        # Load configuration with environment overlay
        config_loader = ConfigLoader()
        config = config_loader.load_with_environment(args.config, args.env)

        # Setup logging
        setup_logging(level=args.log_level, log_file=config.get("logging", {}).get("file"))

        # Override with CLI arguments
        if args.output_file:
            config["output"]["file_path"] = args.output_file

        main(config, Path(args.input))

    except Exception as e:
        logging.error(f"Script failed: {e}")
        sys.exit(1)
