#!/usr/bin/env python3
"""
Trade History Script

Generalized, parameter-driven script for trade history content generation:
- Dynamic analysis name and date parameters
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


@twitter_script(name="trade_history", content_types=["trade_history"], requires_validation=True)
class TradeHistoryScript(BaseScript):
    """
    Generalized trade history script

    Parameters:
        analysis_name (str): Name/identifier for the trade analysis
        date (str): Analysis date in YYYYMMDD format
        data_path (Optional[str]): Path to trade history data file
        template_variant (Optional[str]): Specific template to use
        output_path (Optional[str]): Custom output path
        validate_content (bool): Whether to validate generated content
        min_win_rate (float): Minimum win rate threshold
        min_trades (int): Minimum number of trades required
        transparency_level (str): Level of transparency ("high", "medium", "low")
    """

    SUPPORTED_CONTENT_TYPES = ["trade_history"]
    REQUIRES_VALIDATION = True

    VALID_TRANSPARENCY_LEVELS = ["high", "medium", "low"]

    def __init__(self, config: ScriptConfig):
        super().__init__(config)

        # Initialize components
        self.template_selector = TwitterTemplateSelector()
        self.validation_framework = UnifiedValidationFramework()
        self.template_renderer = TwitterTemplateRenderer()

        # Default paths
        self.data_outputs_path = config.data_outputs_path / "trade_history"
        self.template_outputs_path = config.data_outputs_path / "twitter_trade_history"

    def execute(
        self,
        analysis_name: str,
        date: str,
        data_path: str | None = None,
        template_variant: str | None = None,
        output_path: str | None = None,
        validate_content: bool = True,
        min_win_rate: float = 0.0,
        min_trades: int = 0,
        transparency_level: str = "high",
        **kwargs,
    ) -> ProcessingResult:
        """Execute trade history script"""

        start_time = datetime.now()

        try:
            # Validate inputs
            self.validate_inputs(
                analysis_name=analysis_name,
                date=date,
                data_path=data_path,
                template_variant=template_variant,
                output_path=output_path,
                validate_content=validate_content,
                min_win_rate=min_win_rate,
                min_trades=min_trades,
                transparency_level=transparency_level,
            )

            # Load trade history data
            trade_data = self._load_trade_data(analysis_name, date, data_path)

            # Apply performance filtering
            self._validate_performance_requirements(trade_data, min_win_rate, min_trades)

            # Add transparency and analysis information
            trade_data["transparency_level"] = transparency_level
            trade_data["performance_metrics"] = self._has_performance_metrics(trade_data)

            # Select template
            if template_variant:
                selected_template = template_variant
                template_metadata = {"manual_selection": True}
            else:
                (
                    selected_template,
                    template_metadata,
                ) = self.template_selector.select_optimal_template("trade_history", trade_data)

            # Generate content
            content = self._generate_content(trade_data, selected_template)

            # Validate content if requested
            validation_result = None
            if validate_content:
                validation_result = self.validation_framework.validate_content(content, "trade_history", trade_data)

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
            output_file = self._save_content(content, analysis_name, date, output_path)

            # Create processing result
            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                success=True,
                operation="trade_history_generation",
                content=content,
                output_path=output_file,
                processing_time=processing_time,
            )

            # Add metadata
            result.add_metadata("analysis_name", analysis_name)
            result.add_metadata("date", date)
            result.add_metadata("selected_template", selected_template)
            result.add_metadata("template_metadata", template_metadata)
            result.add_metadata("transparency_level", transparency_level)

            if validation_result:
                result.validation_score = float(
                    validation_result["overall_assessment"]["overall_reliability_score"].split("/")[0]
                )
                result.add_metadata("validation_result", validation_result)

            self.logger.log_operation(
                f"Trade history analysis generated for {analysis_name}",
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
                operation="trade_history_generation",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("analysis_name", analysis_name)
            error_result.add_error_context("date", date)

            self.logger.log_error(
                e,
                {
                    "analysis_name": analysis_name,
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
        analysis_name = kwargs.get("analysis_name", "")
        date = kwargs.get("date", "")
        min_win_rate = kwargs.get("min_win_rate", 0.0)
        min_trades = kwargs.get("min_trades", 0)
        transparency_level = kwargs.get("transparency_level", "high")

        # Validate analysis name
        if not analysis_name or len(analysis_name) > 100:
            raise ValidationError(
                f"Invalid analysis name: {analysis_name}",
                context={"valid_format": "Non-empty string, max 100 characters"},
            )

        # Validate date format
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValidationError(f"Invalid date format: {date}", context={"valid_format": "YYYYMMDD"})

        # Validate win rate threshold
        if not isinstance(min_win_rate, (int, float)) or not 0.0 <= min_win_rate <= 1.0:
            raise ValidationError(
                f"Invalid win rate threshold: {min_win_rate}",
                context={"valid_range": "0.0 to 1.0"},
            )

        # Validate minimum trades
        if not isinstance(min_trades, int) or min_trades < 0:
            raise ValidationError(
                f"Invalid minimum trades: {min_trades}",
                context={"valid_range": "Non-negative integer"},
            )

        # Validate transparency level
        if transparency_level not in self.VALID_TRANSPARENCY_LEVELS:
            raise ValidationError(
                f"Invalid transparency level: {transparency_level}",
                context={"valid_levels": self.VALID_TRANSPARENCY_LEVELS},
            )

        # Validate data path if provided
        data_path = kwargs.get("data_path")
        if data_path and not Path(data_path).exists():
            raise DataError(
                f"Data file not found: {data_path}",
                source_path=Path(data_path),
                operation="input_validation",
            )

    def _load_trade_data(self, analysis_name: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Load trade history data"""

        if data_path:
            # Load from custom path
            data_file = Path(data_path)
        else:
            # Load from default path
            data_file = self.data_outputs_path / f"{analysis_name}_{date}.json"

        if not data_file.exists():
            raise DataError(
                f"Trade history data not found: {data_file}",
                source_path=data_file,
                operation="data_loading",
            )

        try:
            with open(data_file, encoding="utf-8") as f:
                data = json.load(f)

            # Ensure required fields
            data.setdefault("analysis_name", analysis_name)
            data.setdefault("date", date)

            return data

        except json.JSONDecodeError as e:
            raise DataError(
                f"Invalid JSON in data file: {data_file}",
                source_path=data_file,
                operation="data_loading",
                context={"json_error": str(e)},
            )

    def _validate_performance_requirements(
        self, trade_data: dict[str, Any], min_win_rate: float, min_trades: int
    ) -> None:
        """Validate trade performance against requirements"""

        # Check minimum trades
        if min_trades > 0:
            total_trades = trade_data.get("total_trades", 0)
            if not isinstance(total_trades, int) or total_trades < min_trades:
                raise ValidationError(
                    f"Insufficient trades: {total_trades} < {min_trades}",
                    context={"total_trades": total_trades, "min_trades": min_trades},
                )

        # Check minimum win rate
        if min_win_rate > 0.0:
            win_rate = trade_data.get("win_rate", 0.0)
            if not isinstance(win_rate, (int, float)) or win_rate < min_win_rate:
                raise ValidationError(
                    f"Win rate {win_rate:.2%} below minimum {min_win_rate:.2%}",
                    context={"win_rate": win_rate, "min_win_rate": min_win_rate},
                )

    def _has_performance_metrics(self, trade_data: dict[str, Any]) -> bool:
        """Check if trade data has performance metrics"""

        performance_fields = [
            "win_rate",
            "total_trades",
            "period_return",
            "sharpe_ratio",
            "max_drawdown",
            "profit_factor",
            "average_win",
            "average_loss",
        ]

        return any(field in trade_data for field in performance_fields)

    def _generate_content(self, trade_data: dict[str, Any], template_variant: str) -> str:
        """Generate Twitter content using template"""

        try:
            # Render template
            content = self.template_renderer.render_template(
                template_type="trade_history",
                template_variant=template_variant,
                data=trade_data,
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
                    "data_keys": list(trade_data.keys()),
                },
            )

    def _save_content(
        self,
        content: str,
        analysis_name: str,
        date: str,
        output_path: str | None = None,
    ) -> Path:
        """Save generated content to file"""

        if output_path:
            output_file = Path(output_path)
        else:
            # Create output directory if it doesn't exist
            self.template_outputs_path.mkdir(parents=True, exist_ok=True)
            output_file = self.template_outputs_path / f"{analysis_name}_{date}.md"

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
                "description": "Generate Q1 performance report",
                "parameters": {"analysis_name": "Q1_PERFORMANCE", "date": "20240331"},
            },
            {
                "description": "Generate with performance requirements",
                "parameters": {
                    "analysis_name": "HIGH_PERFORMANCE_STRATEGIES",
                    "date": "20240118",
                    "min_win_rate": 0.65,
                    "min_trades": 20,
                },
            },
            {
                "description": "Generate with custom transparency level",
                "parameters": {
                    "analysis_name": "MONTHLY_SUMMARY",
                    "date": "20240131",
                    "transparency_level": "medium",
                },
            },
            {
                "description": "Generate with custom data file",
                "parameters": {
                    "analysis_name": "CUSTOM_ANALYSIS",
                    "date": "20240118",
                    "data_path": "/path/to/custom/trade_data.json",
                },
            },
        ]

    def get_performance_summary(self, analysis_name: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Get performance summary for trade history"""

        try:
            trade_data = self._load_trade_data(analysis_name, date, data_path)

            # Extract performance metrics
            performance_metrics = {}
            for metric in [
                "win_rate",
                "total_trades",
                "period_return",
                "sharpe_ratio",
                "max_drawdown",
                "profit_factor",
            ]:
                if metric in trade_data:
                    performance_metrics[metric] = trade_data[metric]

            # Calculate summary statistics
            has_performance = self._has_performance_metrics(trade_data)

            return {
                "analysis_name": analysis_name,
                "date": date,
                "has_performance_metrics": has_performance,
                "performance_metrics": performance_metrics,
                "data_quality": {
                    "total_fields": len(trade_data),
                    "performance_field_count": len(performance_metrics),
                    "completeness_score": len(performance_metrics) / 6.0,  # 6 key metrics
                },
            }

        except Exception as e:
            return {
                "analysis_name": analysis_name,
                "date": date,
                "error": str(e),
                "has_performance_metrics": False,
                "performance_metrics": {},
            }

    def validate_trade_data_quality(
        self, analysis_name: str, date: str, data_path: str | None = None
    ) -> dict[str, Any]:
        """Validate trade data quality"""

        try:
            trade_data = self._load_trade_data(analysis_name, date, data_path)

            # Check required fields
            required_fields = ["analysis_name", "date"]
            missing_fields = [field for field in required_fields if field not in trade_data]

            # Check performance fields
            performance_fields = [
                "win_rate",
                "total_trades",
                "period_return",
                "sharpe_ratio",
                "max_drawdown",
            ]
            available_performance = [field for field in performance_fields if field in trade_data]

            # Check data types
            type_issues = []
            for field, value in trade_data.items():
                if field in [
                    "win_rate",
                    "period_return",
                    "sharpe_ratio",
                    "max_drawdown",
                    "profit_factor",
                ] and not isinstance(value, (int, float)):
                    type_issues.append(f"{field}: expected number, got {type(value).__name__}")
                elif field == "total_trades" and not isinstance(value, int):
                    type_issues.append(f"{field}: expected integer, got {type(value).__name__}")

            # Check logical consistency
            logical_issues = []
            if "win_rate" in trade_data:
                win_rate = trade_data["win_rate"]
                if isinstance(win_rate, (int, float)) and not 0.0 <= win_rate <= 1.0:
                    logical_issues.append(f"win_rate {win_rate} outside valid range [0.0, 1.0]")

            if "total_trades" in trade_data:
                total_trades = trade_data["total_trades"]
                if isinstance(total_trades, int) and total_trades < 0:
                    logical_issues.append(f"total_trades {total_trades} cannot be negative")

            # Calculate quality score
            quality_score = 1.0
            if missing_fields:
                quality_score -= 0.2
            if len(available_performance) < 3:
                quality_score -= 0.3
            if type_issues:
                quality_score -= 0.1 * len(type_issues)
            if logical_issues:
                quality_score -= 0.2 * len(logical_issues)

            quality_score = max(0.0, quality_score)

            return {
                "analysis_name": analysis_name,
                "date": date,
                "quality_score": quality_score,
                "missing_fields": missing_fields,
                "available_performance": available_performance,
                "type_issues": type_issues,
                "logical_issues": logical_issues,
                "recommendations": self._generate_quality_recommendations(
                    missing_fields, available_performance, type_issues, logical_issues
                ),
            }

        except Exception as e:
            return {
                "analysis_name": analysis_name,
                "date": date,
                "error": str(e),
                "quality_score": 0.0,
            }

    def _generate_quality_recommendations(
        self,
        missing_fields: list[str],
        available_performance: list[str],
        type_issues: list[str],
        logical_issues: list[str],
    ) -> list[str]:
        """Generate data quality improvement recommendations"""

        recommendations = []

        if missing_fields:
            recommendations.append(f"Add missing required fields: {', '.join(missing_fields)}")

        if len(available_performance) < 3:
            recommendations.append(
                "Include more performance metrics (win_rate, total_trades, period_return, sharpe_ratio, max_drawdown)"
            )

        if type_issues:
            recommendations.append("Fix data type issues: " + ", ".join(type_issues))

        if logical_issues:
            recommendations.append("Fix logical inconsistencies: " + ", ".join(logical_issues))

        if not recommendations:
            recommendations.append("Data quality is good - no major issues found")

        return recommendations

    def get_valid_transparency_levels(self) -> list[str]:
        """Get list of valid transparency levels"""
        return self.VALID_TRANSPARENCY_LEVELS.copy()
