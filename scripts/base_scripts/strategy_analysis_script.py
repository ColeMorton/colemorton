#!/usr/bin/env python3
"""
Strategy Analysis Script

Generalized, parameter-driven script for strategy analysis content generation:
- Dynamic ticker and strategy parameters
- Performance metrics integration
- Template-based content generation
- Fail-fast validation
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


@twitter_script(name="strategy_analysis", content_types=["strategy"], requires_validation=True)
class StrategyAnalysisScript(BaseScript):
    """
    Generalized strategy analysis script

    Parameters:
        ticker (str): Stock ticker symbol
        strategy_name (str): Strategy name/identifier
        date (str): Analysis date in YYYYMMDD format
        data_path (Optional[str]): Path to strategy data file
        template_variant (Optional[str]): Specific template to use
        output_path (Optional[str]): Custom output path
        validate_content (bool): Whether to validate generated content
        performance_threshold (float): Minimum performance threshold
    """

    SUPPORTED_CONTENT_TYPES = ["strategy"]
    REQUIRES_VALIDATION = True

    def __init__(self, config: ScriptConfig):
        super().__init__(config)

        # Initialize components
        self.template_selector = TwitterTemplateSelector()
        self.validation_framework = UnifiedValidationFramework()
        self.template_renderer = TwitterTemplateRenderer()

        # Default paths
        self.data_outputs_path = config.data_outputs_path / "strategy_analysis"
        self.template_outputs_path = config.data_outputs_path / "twitter_strategy"

    def execute(
        self,
        ticker: str,
        strategy_name: str,
        date: str,
        data_path: str | None = None,
        template_variant: str | None = None,
        output_path: str | None = None,
        validate_content: bool = True,
        performance_threshold: float = 0.0,
        **kwargs,
    ) -> ProcessingResult:
        """Execute strategy analysis script"""

        start_time = datetime.now()

        try:
            # Validate inputs
            self.validate_inputs(
                ticker=ticker,
                strategy_name=strategy_name,
                date=date,
                data_path=data_path,
                template_variant=template_variant,
                output_path=output_path,
                validate_content=validate_content,
                performance_threshold=performance_threshold,
            )

            # Load strategy data
            strategy_data = self._load_strategy_data(ticker, strategy_name, date, data_path)

            # Apply performance filtering if threshold is set
            if performance_threshold > 0:
                self._validate_performance_threshold(strategy_data, performance_threshold)

            # Select template
            if template_variant:
                selected_template = template_variant
                template_metadata = {"manual_selection": True}
            else:
                (
                    selected_template,
                    template_metadata,
                ) = self.template_selector.select_optimal_template("strategy", strategy_data)

            # Generate content
            content = self._generate_content(strategy_data, selected_template)

            # Validate content if requested
            validation_result = None
            if validate_content:
                validation_result = self.validation_framework.validate_content(content, "strategy", strategy_data)

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
            output_file = self._save_content(content, ticker, strategy_name, date, output_path)

            # Create processing result
            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                success=True,
                operation="strategy_analysis_generation",
                content=content,
                output_path=output_file,
                processing_time=processing_time,
            )

            # Add metadata
            result.add_metadata("ticker", ticker)
            result.add_metadata("strategy_name", strategy_name)
            result.add_metadata("date", date)
            result.add_metadata("selected_template", selected_template)
            result.add_metadata("template_metadata", template_metadata)

            if validation_result:
                result.validation_score = float(
                    validation_result["overall_assessment"]["overall_reliability_score"].split("/")[0]
                )
                result.add_metadata("validation_result", validation_result)

            self.logger.log_operation(
                f"Strategy analysis generated for {ticker} ({strategy_name})",
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
                operation="strategy_analysis_generation",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("ticker", ticker)
            error_result.add_error_context("strategy_name", strategy_name)
            error_result.add_error_context("date", date)

            self.logger.log_error(
                e,
                {
                    "ticker": ticker,
                    "strategy_name": strategy_name,
                    "date": date,
                    "processing_time": processing_time,
                },
            )

            return error_result

    def validate_inputs(self, **kwargs) -> None:
        """Validate inputs before execution"""

        # Validate required parameters
        self.validate_required_parameters(**kwargs)

        # Validate parameter types
        self.validate_parameter_types(**kwargs)

        # Custom validation
        ticker = kwargs.get("ticker", "")
        strategy_name = kwargs.get("strategy_name", "")
        date = kwargs.get("date", "")
        performance_threshold = kwargs.get("performance_threshold", 0.0)

        # Validate ticker format
        if not ticker or not ticker.isalnum() or len(ticker) > 10:
            raise ValidationError(
                f"Invalid ticker format: {ticker}",
                context={"valid_format": "Alphanumeric, 1-10 characters"},
            )

        # Validate strategy name
        if not strategy_name or len(strategy_name) > 50:
            raise ValidationError(
                f"Invalid strategy name: {strategy_name}",
                context={"valid_format": "Non-empty string, max 50 characters"},
            )

        # Validate date format
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValidationError(f"Invalid date format: {date}", context={"valid_format": "YYYYMMDD"})

        # Validate performance threshold
        if not isinstance(performance_threshold, (int, float)) or performance_threshold < 0:
            raise ValidationError(
                f"Invalid performance threshold: {performance_threshold}",
                context={"valid_range": "Non-negative number"},
            )

        # Validate data path if provided
        data_path = kwargs.get("data_path")
        if data_path and not Path(data_path).exists():
            raise DataError(
                f"Data file not found: {data_path}",
                source_path=Path(data_path),
                operation="input_validation",
            )

    def _load_strategy_data(
        self,
        ticker: str,
        strategy_name: str,
        date: str,
        data_path: str | None = None,
    ) -> dict[str, Any]:
        """Load strategy analysis data"""

        if data_path:
            # Load from custom path
            data_file = Path(data_path)
        else:
            # Load from default path
            data_file = self.data_outputs_path / f"{ticker}_{strategy_name}_{date}.json"

        if not data_file.exists():
            raise DataError(
                f"Strategy data not found: {data_file}",
                source_path=data_file,
                operation="data_loading",
            )

        try:
            with open(data_file, encoding="utf-8") as f:
                data = json.load(f)

            # Ensure required fields
            data.setdefault("ticker", ticker)
            data.setdefault("strategy_name", strategy_name)
            data.setdefault("strategy_type", strategy_name)
            data.setdefault("date", date)

            return data

        except json.JSONDecodeError as e:
            raise DataError(
                f"Invalid JSON in data file: {data_file}",
                source_path=data_file,
                operation="data_loading",
                context={"json_error": str(e)},
            )

    def _validate_performance_threshold(self, strategy_data: dict[str, Any], threshold: float) -> None:
        """Validate strategy performance against threshold"""

        # Check various performance metrics
        performance_metrics = [
            "net_performance",
            "win_rate",
            "total_return",
            "annualized_return",
            "sharpe_ratio",
        ]

        performance_found = False
        for metric in performance_metrics:
            if metric in strategy_data:
                value = strategy_data[metric]
                if isinstance(value, (int, float)):
                    if metric == "win_rate" and value < threshold:
                        raise ValidationError(
                            f"Strategy win rate {value:.2%} below threshold {threshold:.2%}",
                            context={
                                "metric": metric,
                                "value": value,
                                "threshold": threshold,
                            },
                        )
                    if metric != "win_rate" and value < threshold:
                        raise ValidationError(
                            f"Strategy {metric} {value:.2f} below threshold {threshold:.2f}",
                            context={
                                "metric": metric,
                                "value": value,
                                "threshold": threshold,
                            },
                        )
                    performance_found = True
                    break

        if not performance_found:
            raise ValidationError(
                "No performance metrics found in strategy data",
                context={
                    "available_fields": list(strategy_data.keys()),
                    "required_metrics": performance_metrics,
                },
            )

    def _generate_content(self, strategy_data: dict[str, Any], template_variant: str) -> str:
        """Generate Twitter content using template"""

        try:
            # Render template
            content = self.template_renderer.render_template(
                template_type="strategy",
                template_variant=template_variant,
                data=strategy_data,
            )

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
                    "data_keys": list(strategy_data.keys()),
                },
            )

    def _save_content(
        self,
        content: str,
        ticker: str,
        strategy_name: str,
        date: str,
        output_path: str | None = None,
    ) -> Path:
        """Save generated content to file"""

        if output_path:
            output_file = Path(output_path)
        else:
            # Create output directory if it doesn't exist
            self.template_outputs_path.mkdir(parents=True, exist_ok=True)
            output_file = self.template_outputs_path / f"{ticker}_{strategy_name}_{date}.md"

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
                "description": "Generate strategy analysis for AAPL SMA strategy",
                "parameters": {
                    "ticker": "AAPL",
                    "strategy_name": "SMA_50_200",
                    "date": "20240118",
                },
            },
            {
                "description": "Generate with performance threshold",
                "parameters": {
                    "ticker": "TSLA",
                    "strategy_name": "RSI_MACD",
                    "date": "20240118",
                    "performance_threshold": 0.6,
                },
            },
            {
                "description": "Generate with custom data file",
                "parameters": {
                    "ticker": "MSFT",
                    "strategy_name": "BOLLINGER_BANDS",
                    "date": "20240118",
                    "data_path": "/path/to/strategy/data.json",
                },
            },
            {
                "description": "Generate with specific template",
                "parameters": {
                    "ticker": "GOOGL",
                    "strategy_name": "MOMENTUM",
                    "date": "20240118",
                    "template_variant": "default",
                },
            },
        ]

    def get_strategy_performance_summary(
        self,
        ticker: str,
        strategy_name: str,
        date: str,
        data_path: str | None = None,
    ) -> dict[str, Any]:
        """Get strategy performance summary"""

        try:
            strategy_data = self._load_strategy_data(ticker, strategy_name, date, data_path)

            # Extract performance metrics
            performance_metrics = {}
            for metric in [
                "win_rate",
                "net_performance",
                "total_trades",
                "reward_risk",
                "sharpe_ratio",
                "max_drawdown",
            ]:
                if metric in strategy_data:
                    performance_metrics[metric] = strategy_data[metric]

            return {
                "ticker": ticker,
                "strategy_name": strategy_name,
                "date": date,
                "performance_metrics": performance_metrics,
                "data_quality": {
                    "total_fields": len(strategy_data),
                    "has_performance_data": bool(performance_metrics),
                    "performance_field_count": len(performance_metrics),
                },
            }

        except Exception as e:
            return {
                "ticker": ticker,
                "strategy_name": strategy_name,
                "date": date,
                "error": str(e),
                "performance_metrics": {},
            }

    def validate_strategy_data_quality(
        self,
        ticker: str,
        strategy_name: str,
        date: str,
        data_path: str | None = None,
    ) -> dict[str, Any]:
        """Validate strategy data quality"""

        try:
            strategy_data = self._load_strategy_data(ticker, strategy_name, date, data_path)

            # Check required fields
            required_fields = ["ticker", "strategy_type", "date"]
            missing_fields = [field for field in required_fields if field not in strategy_data]

            # Check performance fields
            performance_fields = [
                "win_rate",
                "net_performance",
                "total_trades",
                "reward_risk",
            ]
            available_performance = [field for field in performance_fields if field in strategy_data]

            # Check data types
            type_issues = []
            for field, value in strategy_data.items():
                if field in [
                    "win_rate",
                    "net_performance",
                    "reward_risk",
                    "sharpe_ratio",
                ] and not isinstance(value, (int, float)):
                    type_issues.append(f"{field}: expected number, got {type(value).__name__}")
                elif field == "total_trades" and not isinstance(value, int):
                    type_issues.append(f"{field}: expected integer, got {type(value).__name__}")

            quality_score = 1.0
            if missing_fields:
                quality_score -= 0.3
            if len(available_performance) < 2:
                quality_score -= 0.4
            if type_issues:
                quality_score -= 0.2 * len(type_issues)

            quality_score = max(0.0, quality_score)

            return {
                "ticker": ticker,
                "strategy_name": strategy_name,
                "date": date,
                "quality_score": quality_score,
                "missing_fields": missing_fields,
                "available_performance": available_performance,
                "type_issues": type_issues,
                "recommendations": self._generate_data_quality_recommendations(
                    missing_fields, available_performance, type_issues
                ),
            }

        except Exception as e:
            return {
                "ticker": ticker,
                "strategy_name": strategy_name,
                "date": date,
                "error": str(e),
                "quality_score": 0.0,
            }

    def _generate_data_quality_recommendations(
        self,
        missing_fields: list[str],
        available_performance: list[str],
        type_issues: list[str],
    ) -> list[str]:
        """Generate data quality improvement recommendations"""

        recommendations = []

        if missing_fields:
            recommendations.append(f"Add missing required fields: {', '.join(missing_fields)}")

        if len(available_performance) < 2:
            recommendations.append(
                "Include more performance metrics (win_rate, net_performance, reward_risk, total_trades)"
            )

        if type_issues:
            recommendations.append("Fix data type issues: " + ", ".join(type_issues))

        if not recommendations:
            recommendations.append("Data quality is good - no major issues found")

        return recommendations
