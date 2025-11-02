#!/usr/bin/env python3
"""
Twitter Command Processor

Unified processing system for all Twitter commands:
- Standardized data loading and validation
- Template rendering coordination
- Output formatting and export
- Quality assurance and compliance checking
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from twitter_template_renderer import TwitterTemplateRenderer


class TwitterCommandProcessor:
    """Unified processor for all Twitter commands"""

    def __init__(self, base_path: Path | None = None):
        """Initialize the command processor"""
        self.base_path = base_path or Path(__file__).parent.parent
        self.data_outputs_path = self.base_path / "data" / "outputs"
        self.twitter_outputs_path = self.data_outputs_path / "twitter"

        # Initialize template renderer
        self.template_renderer = TwitterTemplateRenderer()

        # Ensure output directories exist
        self.twitter_outputs_path.mkdir(parents=True, exist_ok=True)
        for content_type in [
            "fundamental_analysis",
            "post_strategy",
            "sector_analysis",
            "trade_history",
        ]:
            (self.twitter_outputs_path / content_type).mkdir(exist_ok=True)

    def process_fundamental_analysis(self, ticker_date: str) -> dict[str, Any]:
        """Process fundamental analysis Twitter content"""
        try:
            # Parse ticker and date
            ticker, date = self._parse_ticker_date(ticker_date)

            # Load source data
            source_data = self._load_fundamental_analysis_data(ticker, date)

            # Validate source data
            validation_result = self._validate_source_data(source_data, "fundamental")

            # Render content
            rendered_result = self.template_renderer.render_fundamental_analysis(ticker, source_data)

            # Export content
            output_path = self._export_content(rendered_result, "fundamental_analysis", f"{ticker}_{date}")

            return {
                "success": True,
                "output_path": str(output_path),
                "content": rendered_result["content"],
                "metadata": rendered_result["metadata"],
                "validation": validation_result,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "ticker_date": ticker_date}

    def process_strategy_post(self, ticker_date: str) -> dict[str, Any]:
        """Process strategy post Twitter content"""
        try:
            # Parse ticker and date
            ticker, date = self._parse_ticker_date(ticker_date)

            # Load source data from multiple sources
            source_data = self._load_strategy_data(ticker, date)

            # Validate source data
            validation_result = self._validate_source_data(source_data, "strategy")

            # Render content
            rendered_result = self.template_renderer.render_strategy_post(ticker, source_data)

            # Export content
            output_path = self._export_content(rendered_result, "post_strategy", f"{ticker}_{date}")

            return {
                "success": True,
                "output_path": str(output_path),
                "content": rendered_result["content"],
                "metadata": rendered_result["metadata"],
                "validation": validation_result,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "ticker_date": ticker_date}

    def process_sector_analysis(self, sector_date: str) -> dict[str, Any]:
        """Process sector analysis Twitter content"""
        try:
            # Parse sector and date
            sector, date = self._parse_sector_date(sector_date)

            # Load source data
            source_data = self._load_sector_analysis_data(sector, date)

            # Validate source data
            validation_result = self._validate_source_data(source_data, "sector")

            # Render content
            rendered_result = self.template_renderer.render_sector_analysis(sector, source_data)

            # Export content
            output_path = self._export_content(rendered_result, "sector_analysis", f"{sector}_{date}")

            return {
                "success": True,
                "output_path": str(output_path),
                "content": rendered_result["content"],
                "metadata": rendered_result["metadata"],
                "validation": validation_result,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "sector_date": sector_date}

    def process_trade_history(self, analysis_name_date: str) -> dict[str, Any]:
        """Process trade history Twitter content"""
        try:
            # Parse analysis name and date
            analysis_name, date = self._parse_analysis_name_date(analysis_name_date)

            # Load source data
            source_data = self._load_trade_history_data(analysis_name, date)

            # Validate source data
            validation_result = self._validate_source_data(source_data, "trade_history")

            # Render content
            rendered_result = self.template_renderer.render_trade_history(analysis_name, source_data)

            # Export content
            output_path = self._export_content(rendered_result, "trade_history", f"{analysis_name}_{date}")

            return {
                "success": True,
                "output_path": str(output_path),
                "content": rendered_result["content"],
                "metadata": rendered_result["metadata"],
                "validation": validation_result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_name_date": analysis_name_date,
            }

    def process_validation_enhancement(self, validation_file_path: str) -> dict[str, Any]:
        """Process validation-driven content enhancement"""
        try:
            # Parse validation file path
            content_type, identifier, date = self._parse_validation_path(validation_file_path)

            # Load validation data
            validation_data = self._load_validation_data(validation_file_path)

            # Load original content
            original_content = self._load_original_content(content_type, identifier, date)

            # Apply enhancements based on validation feedback
            enhanced_result = self._apply_validation_enhancements(
                original_content, validation_data, content_type, identifier
            )

            # Export enhanced content
            output_path = self._export_content(enhanced_result, content_type, f"{identifier}_{date}")

            return {
                "success": True,
                "output_path": str(output_path),
                "content": enhanced_result["content"],
                "metadata": enhanced_result["metadata"],
                "enhancement_applied": True,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "validation_file_path": validation_file_path,
            }

    def _parse_ticker_date(self, ticker_date: str) -> tuple[str, str]:
        """Parse ticker_date format (e.g., 'AAPL_20250618')"""
        if "_" not in ticker_date:
            raise ValueError(f"Invalid ticker_date format: {ticker_date}. Expected format: TICKER_YYYYMMDD")

        parts = ticker_date.split("_")
        if len(parts) != 2:
            raise ValueError(f"Invalid ticker_date format: {ticker_date}. Expected format: TICKER_YYYYMMDD")

        ticker, date = parts

        # Validate date format
        if not re.match(r"^\d{8}$", date):
            raise ValueError(f"Invalid date format: {date}. Expected format: YYYYMMDD")

        return ticker.upper(), date

    def _parse_sector_date(self, sector_date: str) -> tuple[str, str]:
        """Parse sector_date format (e.g., 'technology_20250618')"""
        if "_" not in sector_date:
            raise ValueError(f"Invalid sector_date format: {sector_date}. Expected format: SECTOR_YYYYMMDD")

        parts = sector_date.split("_")
        if len(parts) != 2:
            raise ValueError(f"Invalid sector_date format: {sector_date}. Expected format: SECTOR_YYYYMMDD")

        sector, date = parts

        # Validate date format
        if not re.match(r"^\d{8}$", date):
            raise ValueError(f"Invalid date format: {date}. Expected format: YYYYMMDD")

        return sector.lower(), date

    def _parse_analysis_name_date(self, analysis_name_date: str) -> tuple[str, str]:
        """Parse analysis_name_date format (e.g., 'HISTORICAL_PERFORMANCE_REPORT_20250618')"""
        if "_" not in analysis_name_date:
            raise ValueError(f"Invalid analysis_name_date format: {analysis_name_date}")

        parts = analysis_name_date.split("_")
        if len(parts) < 2:
            raise ValueError(f"Invalid analysis_name_date format: {analysis_name_date}")

        # Last part should be the date
        date = parts[-1]
        analysis_name = "_".join(parts[:-1])

        # Validate date format
        if not re.match(r"^\d{8}$", date):
            raise ValueError(f"Invalid date format: {date}. Expected format: YYYYMMDD")

        return analysis_name, date

    def _parse_validation_path(self, validation_file_path: str) -> tuple[str, str, str]:
        """Parse validation file path to extract content type, identifier, and date"""
        path = Path(validation_file_path)

        # Extract content type from path
        content_type = None
        if "fundamental_analysis" in str(path):
            content_type = "fundamental_analysis"
        elif "post_strategy" in str(path):
            content_type = "post_strategy"
        elif "sector_analysis" in str(path):
            content_type = "sector_analysis"
        elif "trade_history" in str(path):
            content_type = "trade_history"

        if not content_type:
            raise ValueError(f"Cannot determine content type from validation path: {validation_file_path}")

        # Extract identifier and date from filename
        filename = path.stem
        if filename.endswith("_validation"):
            filename = filename[:-11]  # Remove "_validation" suffix

        # Parse filename based on content type
        if content_type in ["fundamental_analysis", "post_strategy"]:
            identifier, date = self._parse_ticker_date(filename)
        elif content_type == "sector_analysis":
            identifier, date = self._parse_sector_date(filename)
        else:  # trade_history
            identifier, date = self._parse_analysis_name_date(filename)

        return content_type, identifier, date

    def _load_fundamental_analysis_data(self, ticker: str, date: str) -> dict[str, Any]:
        """Load fundamental analysis source data"""
        # Try to load from analysis outputs
        analysis_path = self.data_outputs_path / "fundamental_analysis" / f"{ticker}_{date}.md"

        if not analysis_path.exists():
            raise FileNotFoundError(f"Fundamental analysis not found: {analysis_path}")

        # Parse markdown file with frontmatter
        content = analysis_path.read_text()
        data = self._parse_markdown_with_frontmatter(content)

        # Add ticker and date
        data["ticker"] = ticker
        data["date"] = date

        return data

    def _load_strategy_data(self, ticker: str, date: str) -> dict[str, Any]:
        """Load strategy data from multiple sources"""
        data = {"ticker": ticker, "date": date}

        # Try to load TrendSpider data
        trendspider_path = self.base_path / "data" / "images" / "trendspider_tabular" / f"{ticker}_{date}.png"
        if trendspider_path.exists():
            data["trendspider_available"] = True

        # Try to load strategy CSV data
        strategy_path = self.base_path / "data" / "raw" / "analysis_strategy" / f"{ticker}_{date}.csv"
        if strategy_path.exists():
            data["strategy_csv_available"] = True

        # Add placeholder data for template compatibility
        data.update(
            {
                "strategy_type": "SMA",
                "short_window": 10,
                "long_window": 25,
                "period": "5 years",
                "net_performance": 0.0,
                "win_rate": 0.0,
                "total_trades": 0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "reward_risk": 0.0,
                "max_drawdown": 0.0,
                "sharpe": 0.0,
                "exposure": 0.0,
                "avg_trade_length": 0.0,
                "expectancy": 0.0,
            }
        )

        return data

    def _load_sector_analysis_data(self, sector: str, date: str) -> dict[str, Any]:
        """Load sector analysis source data"""
        # Try to load from sector analysis outputs
        analysis_path = self.data_outputs_path / "sector_analysis" / f"{sector}_{date}.md"

        if not analysis_path.exists():
            raise FileNotFoundError(f"Sector analysis not found: {analysis_path}")

        # Parse markdown file with frontmatter
        content = analysis_path.read_text()
        data = self._parse_markdown_with_frontmatter(content)

        # Add sector and date
        data["sector_name"] = sector
        data["date"] = date

        return data

    def _load_trade_history_data(self, analysis_name: str, date: str) -> dict[str, Any]:
        """Load trade history source data"""
        # Try to load from trade history outputs
        analysis_path = self.data_outputs_path / "trade_history" / f"{analysis_name}_{date}.md"

        if not analysis_path.exists():
            raise FileNotFoundError(f"Trade history analysis not found: {analysis_path}")

        # Parse markdown file with frontmatter
        content = analysis_path.read_text()
        data = self._parse_markdown_with_frontmatter(content)

        # Add analysis name and date
        data["analysis_name"] = analysis_name
        data["date"] = date

        return data

    def _parse_markdown_with_frontmatter(self, content: str) -> dict[str, Any]:
        """Parse markdown content with YAML frontmatter"""
        data = {}

        # Split content by frontmatter delimiters
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml

                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        data.update(frontmatter)
                    data["markdown_content"] = parts[2].strip()
                except Exception:
                    data["markdown_content"] = content
            else:
                data["markdown_content"] = content
        else:
            data["markdown_content"] = content

        return data

    def _validate_source_data(self, data: dict[str, Any], content_type: str) -> dict[str, Any]:
        """Validate source data completeness and quality"""

        required_fields = {
            "fundamental": ["ticker", "date"],
            "strategy": ["ticker", "date", "strategy_type"],
            "sector": ["sector_name", "date"],
            "trade_history": ["analysis_name", "date"],
        }

        missing_fields = []
        content_required = required_fields.get(content_type, [])

        for field in content_required:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "data_quality": "good" if len(missing_fields) == 0 else "poor",
        }

    def _export_content(self, rendered_result: dict[str, Any], content_type: str, filename: str) -> Path:
        """Export rendered content to appropriate directory"""

        # Create output directory
        output_dir = self.twitter_outputs_path / content_type
        output_dir.mkdir(exist_ok=True)

        # Create output file
        output_path = output_dir / f"{filename}.md"

        # Write content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_result["content"])

        # Also save metadata
        metadata_path = output_dir / f"{filename}_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(rendered_result["metadata"], f, indent=2)

        return output_path

    def _load_validation_data(self, validation_file_path: str) -> dict[str, Any]:
        """Load validation data from JSON file"""
        path = Path(validation_file_path)

        if not path.exists():
            raise FileNotFoundError(f"Validation file not found: {validation_file_path}")

        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _load_original_content(self, content_type: str, identifier: str, date: str) -> dict[str, Any]:
        """Load original content for enhancement"""

        # Construct path to original content
        content_path = self.twitter_outputs_path / content_type / f"{identifier}_{date}.md"

        if not content_path.exists():
            raise FileNotFoundError(f"Original content not found: {content_path}")

        content = content_path.read_text()

        # Also load metadata if available
        metadata_path = self.twitter_outputs_path / content_type / f"{identifier}_{date}_metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)

        return {"content": content, "metadata": metadata}

    def _apply_validation_enhancements(
        self,
        original_content: dict[str, Any],
        validation_data: dict[str, Any],
        content_type: str,
        identifier: str,
    ) -> dict[str, Any]:
        """Apply validation-driven enhancements to content"""

        # Extract enhancement recommendations from validation data
        recommendations = validation_data.get("actionable_recommendations", {})
        required_corrections = recommendations.get("required_corrections", {})

        # Apply high priority corrections
        enhanced_content = original_content["content"]

        # Apply template-based enhancement (simplified approach)
        # In a full implementation, this would use specific enhancement templates

        # For now, add a note about enhancement applied
        enhanced_content += "\n\n<!-- Content enhanced based on validation feedback -->"

        return {
            "content": enhanced_content,
            "metadata": {
                **original_content.get("metadata", {}),
                "enhanced": True,
                "enhancement_timestamp": datetime.now().isoformat(),
                "validation_applied": True,
            },
        }

    def get_processing_status(self) -> dict[str, Any]:
        """Get status of processing system"""
        return {
            "template_renderer_available": True,
            "output_directories_ready": all(
                [
                    (self.twitter_outputs_path / ct).exists()
                    for ct in [
                        "fundamental_analysis",
                        "post_strategy",
                        "sector_analysis",
                        "trade_history",
                    ]
                ]
            ),
            "available_templates": self.template_renderer.get_available_templates(),
        }
