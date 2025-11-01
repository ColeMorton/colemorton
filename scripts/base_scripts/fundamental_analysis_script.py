#!/usr/bin/env python3
"""
Fundamental Analysis Script

Generalized, parameter-driven script for fundamental analysis content generation:
- Dynamic ticker and date parameters
- Template-based content generation
- Fail-fast validation
- Type-safe results
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from errors import DataError, ValidationError
from result_types import ProcessingResult
from script_config import ScriptConfig
from script_registry import BaseScript, twitter_script
from twitter_template_renderer import TwitterTemplateRenderer
from twitter_template_selector_refactored import TwitterTemplateSelector
from unified_validation_framework import UnifiedValidationFramework


@twitter_script(name="fundamental_analysis", content_types=["fundamental"], requires_validation=True)
class FundamentalAnalysisScript(BaseScript):
    """
    Generalized fundamental analysis script

    Parameters:
        ticker (str): Stock ticker symbol
        date (str): Analysis date in YYYYMMDD format
        data_path (Optional[str]): Path to analysis data file
        template_variant (Optional[str]): Specific template to use
        output_path (Optional[str]): Custom output path
        validate_content (bool): Whether to validate generated content
    """

    SUPPORTED_CONTENT_TYPES = ["fundamental"]
    REQUIRES_VALIDATION = True

    def __init__(self, config: ScriptConfig):
        super().__init__(config)

        # Initialize components
        self.template_selector = TwitterTemplateSelector()
        self.validation_framework = UnifiedValidationFramework()
        self.template_renderer = TwitterTemplateRenderer()

        # Default paths
        self.data_outputs_path = config.data_outputs_path / "fundamental_analysis"
        self.template_outputs_path = config.data_outputs_path / "twitter_fundamental_analysis"

    def execute(
        self,
        ticker: str,
        date: str,
        data_path: str | None = None,
        template_variant: str | None = None,
        output_path: str | None = None,
        validate_content: bool = True,
        **kwargs,
    ) -> ProcessingResult:
        """Execute fundamental analysis script"""

        start_time = datetime.now()

        try:
            # Validate inputs
            self.validate_inputs(
                ticker=ticker,
                date=date,
                data_path=data_path,
                template_variant=template_variant,
                output_path=output_path,
                validate_content=validate_content,
            )

            # Load analysis data
            analysis_data = self._load_analysis_data(ticker, date, data_path)

            # Select template
            if template_variant:
                selected_template = template_variant
                template_metadata = {"manual_selection": True}
            else:
                (
                    selected_template,
                    template_metadata,
                ) = self.template_selector.select_optimal_template("fundamental", analysis_data)

            # Generate content
            content = self._generate_content(analysis_data, selected_template)

            # Validate content if requested
            validation_result = None
            if validate_content:
                validation_result = self.validation_framework.validate_content(content, "fundamental", analysis_data)

                # Fail-fast if validation score is too low
                overall_score = float(
                    validation_result["overall_assessment"]["overall_reliability_score"].split("/")[0]
                )
                if overall_score < 8.5:
                    raise ValidationError(
                        f"Generated content quality too low: {overall_score}/10.0",
                        context={"validation_result": validation_result},
                    )

            # Save content
            output_file = self._save_content(content, ticker, date, output_path)

            # Create processing result
            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                success=True,
                operation="fundamental_analysis_generation",
                content=content,
                output_path=output_file,
                processing_time=processing_time,
            )

            # Add metadata
            result.add_metadata("ticker", ticker)
            result.add_metadata("date", date)
            result.add_metadata("selected_template", selected_template)
            result.add_metadata("template_metadata", template_metadata)

            if validation_result:
                result.validation_score = float(
                    validation_result["overall_assessment"]["overall_reliability_score"].split("/")[0]
                )
                result.add_metadata("validation_result", validation_result)

            self.logger.log_operation(
                f"Fundamental analysis generated for {ticker}",
                {
                    "template": selected_template,
                    "validation_score": result.validation_score,
                    "processing_time": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()

            error_result = ProcessingResult(
                success=False,
                operation="fundamental_analysis_generation",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("ticker", ticker)
            error_result.add_error_context("date", date)
            error_result.add_error_context("data_path", data_path)

            self.logger.log_error(e, {"ticker": ticker, "date": date, "processing_time": processing_time})

            return error_result

    def validate_inputs(self, **kwargs) -> None:
        """Validate inputs before execution"""

        # Validate required parameters
        self.validate_required_parameters(**kwargs)

        # Validate parameter types
        self.validate_parameter_types(**kwargs)

        # Custom validation
        ticker = kwargs.get("ticker", "")
        date = kwargs.get("date", "")

        # Validate ticker format
        if not ticker or not ticker.isalnum() or len(ticker) > 10:
            raise ValidationError(
                f"Invalid ticker format: {ticker}",
                context={"valid_format": "Alphanumeric, 1-10 characters"},
            )

        # Validate date format
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValidationError(f"Invalid date format: {date}", context={"valid_format": "YYYYMMDD"})

        # Validate data path if provided
        data_path = kwargs.get("data_path")
        if data_path and not Path(data_path).exists():
            raise DataError(
                f"Data file not found: {data_path}",
                source_path=Path(data_path),
                operation="input_validation",
            )

    def _load_analysis_data(self, ticker: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Load fundamental analysis data"""

        if data_path:
            # Load from custom path
            data_file = Path(data_path)
        else:
            # Load from default path
            data_file = self.data_outputs_path / f"{ticker}_{date}.json"

        if not data_file.exists():
            raise DataError(
                f"Analysis data not found: {data_file}",
                source_path=data_file,
                operation="data_loading",
            )

        try:
            with open(data_file, encoding="utf-8") as f:
                data = json.load(f)

            # Ensure required fields
            data.setdefault("ticker", ticker)
            data.setdefault("date", date)

            return data

        except json.JSONDecodeError as e:
            raise DataError(
                f"Invalid JSON in data file: {data_file}",
                source_path=data_file,
                operation="data_loading",
                context={"json_error": str(e)},
            )

    def _generate_content(self, analysis_data: dict[str, Any], template_variant: str) -> str:
        """Generate Twitter content using template"""

        try:
            # Render template using correct method
            result = self.template_renderer.render_fundamental_analysis(
                ticker=analysis_data.get("ticker", ""),
                data=analysis_data,
                template_variant=template_variant,
            )

            content = result.get("content", "")

            if not content or not content.strip():
                raise ValidationError(
                    "Template rendering produced empty content",
                    context={"template_variant": template_variant},
                )

            return content.strip()

        except Exception as e:
            raise ValidationError(
                f"Template rendering failed: {str(e)}",
                context={
                    "template_variant": template_variant,
                    "data_keys": list(analysis_data.keys()),
                },
            )

    def _save_content(self, content: str, ticker: str, date: str, output_path: str | None = None) -> Path:
        """Save generated content to file"""

        if output_path:
            output_file = Path(output_path)
        else:
            # Create output directory if it doesn't exist
            self.template_outputs_path.mkdir(parents=True, exist_ok=True)
            output_file = self.template_outputs_path / f"{ticker}_{date}.md"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            return output_file

        except Exception as e:
            raise DataError(
                f"Failed to save content: {str(e)}",
                source_path=output_file,
                operation="content_saving",
            )

    def get_usage_examples(self) -> list[dict[str, Any]]:
        """Get usage examples for the script"""

        return [
            {
                "description": "Generate fundamental analysis for AAPL",
                "parameters": {"ticker": "AAPL", "date": "20240118"},
            },
            {
                "description": "Generate with custom data file",
                "parameters": {
                    "ticker": "MSFT",
                    "date": "20240118",
                    "data_path": "/path/to/custom/data.json",
                },
            },
            {
                "description": "Generate with specific template",
                "parameters": {
                    "ticker": "GOOGL",
                    "date": "20240118",
                    "template_variant": "A_valuation",
                },
            },
            {
                "description": "Generate without validation",
                "parameters": {
                    "ticker": "TSLA",
                    "date": "20240118",
                    "validate_content": False,
                },
            },
        ]

    def get_available_templates(self) -> list[str]:
        """Get available templates for fundamental analysis"""

        return self.template_selector.get_available_templates("fundamental")

    def preview_template_selection(self, ticker: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Preview template selection without generating content"""

        try:
            analysis_data = self._load_analysis_data(ticker, date, data_path)

            recommendations = self.template_selector.get_template_recommendations("fundamental", analysis_data)

            return {
                "ticker": ticker,
                "date": date,
                "data_summary": {
                    "fields": list(analysis_data.keys()),
                    "has_valuation": "fair_value" in analysis_data,
                    "has_catalysts": "catalysts" in analysis_data,
                    "has_moat": "moat_strength" in analysis_data,
                },
                "recommendations": recommendations,
            }

        except Exception as e:
            return {
                "ticker": ticker,
                "date": date,
                "error": str(e),
                "recommendations": [],
            }
