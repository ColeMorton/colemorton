#!/usr/bin/env python3
"""
Sector Analysis Script

Generalized, parameter-driven script for sector analysis content generation:
- Dynamic sector and analysis type parameters
- Rotation and comparison analysis support
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


@twitter_script(name="sector_analysis", content_types=["sector"], requires_validation=True)
class SectorAnalysisScript(BaseScript):
    """
    Generalized sector analysis script

    Parameters:
        sector_name (str): Sector name (e.g., "technology", "healthcare")
        analysis_type (str): Type of analysis ("rotation", "comparison", "auto")
        date (str): Analysis date in YYYYMMDD format
        data_path (Optional[str]): Path to sector data file
        template_variant (Optional[str]): Specific template to use
        output_path (Optional[str]): Custom output path
        validate_content (bool): Whether to validate generated content
        min_rotation_signal (float): Minimum rotation signal threshold
        benchmark_sectors (List[str]): Sectors to compare against
    """

    SUPPORTED_CONTENT_TYPES = ["sector"]
    REQUIRES_VALIDATION = True

    VALID_SECTORS = [
        "technology",
        "healthcare",
        "financials",
        "consumer_discretionary",
        "consumer_staples",
        "energy",
        "industrials",
        "materials",
        "utilities",
        "real_estate",
        "communication_services",
    ]

    VALID_ANALYSIS_TYPES = ["rotation", "comparison", "auto"]

    def __init__(self, config: ScriptConfig):
        super().__init__(config)

        # Initialize components
        self.template_selector = TwitterTemplateSelector()
        self.validation_framework = UnifiedValidationFramework()
        self.template_renderer = TwitterTemplateRenderer()

        # Default paths
        self.data_outputs_path = config.data_outputs_path / "sector_analysis"
        self.template_outputs_path = config.data_outputs_path / "twitter_sector_analysis"

    def execute(
        self,
        sector_name: str,
        analysis_type: str,
        date: str,
        data_path: str | None = None,
        template_variant: str | None = None,
        output_path: str | None = None,
        validate_content: bool = True,
        min_rotation_signal: float = 0.5,
        benchmark_sectors: list[str] | None = None,
        **kwargs,
    ) -> ProcessingResult:
        """Execute sector analysis script"""

        start_time = datetime.now()

        try:
            # Validate inputs
            self.validate_inputs(
                sector_name=sector_name,
                analysis_type=analysis_type,
                date=date,
                data_path=data_path,
                template_variant=template_variant,
                output_path=output_path,
                validate_content=validate_content,
                min_rotation_signal=min_rotation_signal,
                benchmark_sectors=benchmark_sectors,
            )

            # Load sector data
            sector_data = self._load_sector_data(sector_name, date, data_path)

            # Determine analysis type if auto
            if analysis_type == "auto":
                analysis_type = self._determine_analysis_type(sector_data)

            # Apply analysis-specific validation
            if analysis_type == "rotation":
                self._validate_rotation_analysis(sector_data, min_rotation_signal)
            elif analysis_type == "comparison":
                self._validate_comparison_analysis(sector_data, benchmark_sectors)

            # Enhance data with analysis type information
            sector_data["analysis_type"] = analysis_type
            if analysis_type == "rotation":
                sector_data["rotation_signal"] = sector_data.get("rotation_signal", False)
            elif analysis_type == "comparison":
                sector_data["sector_comparison"] = sector_data.get("sector_comparison", True)

            # Select template
            if template_variant:
                selected_template = template_variant
                template_metadata = {"manual_selection": True}
            else:
                (
                    selected_template,
                    template_metadata,
                ) = self.template_selector.select_optimal_template("sector", sector_data)

            # Generate content
            content = self._generate_content(sector_data, selected_template)

            # Validate content if requested
            validation_result = None
            if validate_content:
                validation_result = self.validation_framework.validate_content(content, "sector", sector_data)

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
            output_file = self._save_content(content, sector_name, analysis_type, date, output_path)

            # Create processing result
            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                success=True,
                operation="sector_analysis_generation",
                content=content,
                output_path=output_file,
                processing_time=processing_time,
            )

            # Add metadata
            result.add_metadata("sector_name", sector_name)
            result.add_metadata("analysis_type", analysis_type)
            result.add_metadata("date", date)
            result.add_metadata("selected_template", selected_template)
            result.add_metadata("template_metadata", template_metadata)

            if validation_result:
                result.validation_score = float(
                    validation_result["overall_assessment"]["overall_reliability_score"].split("/")[0]
                )
                result.add_metadata("validation_result", validation_result)

            self.logger.log_operation(
                f"Sector analysis generated for {sector_name} ({analysis_type})",
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
                operation="sector_analysis_generation",
                error=str(e),
                processing_time=processing_time,
            )

            error_result.add_error_context("sector_name", sector_name)
            error_result.add_error_context("analysis_type", analysis_type)
            error_result.add_error_context("date", date)

            self.logger.log_error(
                e,
                {
                    "sector_name": sector_name,
                    "analysis_type": analysis_type,
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
        sector_name = kwargs.get("sector_name", "")
        analysis_type = kwargs.get("analysis_type", "")
        date = kwargs.get("date", "")
        min_rotation_signal = kwargs.get("min_rotation_signal", 0.5)
        benchmark_sectors = kwargs.get("benchmark_sectors", [])

        # Validate sector name
        if sector_name.lower() not in self.VALID_SECTORS:
            raise ValidationError(
                f"Invalid sector name: {sector_name}",
                context={"valid_sectors": self.VALID_SECTORS},
            )

        # Validate analysis type
        if analysis_type not in self.VALID_ANALYSIS_TYPES:
            raise ValidationError(
                f"Invalid analysis type: {analysis_type}",
                context={"valid_types": self.VALID_ANALYSIS_TYPES},
            )

        # Validate date format
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValidationError(f"Invalid date format: {date}", context={"valid_format": "YYYYMMDD"})

        # Validate rotation signal threshold
        if not isinstance(min_rotation_signal, (int, float)) or not 0.0 <= min_rotation_signal <= 1.0:
            raise ValidationError(
                f"Invalid rotation signal threshold: {min_rotation_signal}",
                context={"valid_range": "0.0 to 1.0"},
            )

        # Validate benchmark sectors
        if benchmark_sectors:
            if not isinstance(benchmark_sectors, list):
                raise ValidationError(
                    f"Benchmark sectors must be a list, got {type(benchmark_sectors).__name__}",
                    context={"valid_type": "list"},
                )

            invalid_sectors = [s for s in benchmark_sectors if s.lower() not in self.VALID_SECTORS]
            if invalid_sectors:
                raise ValidationError(
                    f"Invalid benchmark sectors: {invalid_sectors}",
                    context={"valid_sectors": self.VALID_SECTORS},
                )

        # Validate data path if provided
        data_path = kwargs.get("data_path")
        if data_path and not Path(data_path).exists():
            raise DataError(
                f"Data file not found: {data_path}",
                source_path=Path(data_path),
                operation="input_validation",
            )

    def _load_sector_data(self, sector_name: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Load sector analysis data"""

        if data_path:
            # Load from custom path
            data_file = Path(data_path)
        else:
            # Load from default path
            data_file = self.data_outputs_path / f"{sector_name.lower()}_{date}.json"

        if not data_file.exists():
            raise DataError(
                f"Sector data not found: {data_file}",
                source_path=data_file,
                operation="data_loading",
            )

        try:
            with open(data_file, encoding="utf-8") as f:
                data = json.load(f)

            # Ensure required fields
            data.setdefault("sector_name", sector_name)
            data.setdefault("date", date)

            return data

        except json.JSONDecodeError as e:
            raise DataError(
                f"Invalid JSON in data file: {data_file}",
                source_path=data_file,
                operation="data_loading",
                context={"json_error": str(e)},
            )

    def _determine_analysis_type(self, sector_data: dict[str, Any]) -> str:
        """Automatically determine analysis type based on data"""

        # Check for rotation indicators
        rotation_indicators = [
            "rotation_signal",
            "rotation_score",
            "flow_data",
            "economic_cycle",
            "relative_momentum",
            "sector_rotation",
        ]

        rotation_score = sum(1 for indicator in rotation_indicators if indicator in sector_data)

        # Check for comparison indicators
        comparison_indicators = [
            "sector_comparison",
            "relative_valuation",
            "performance_ranking",
            "cross_sector",
            "benchmark_comparison",
            "peer_sectors",
        ]

        comparison_score = sum(1 for indicator in comparison_indicators if indicator in sector_data)

        # Determine analysis type
        if rotation_score >= comparison_score:
            return "rotation"
        return "comparison"

    def _validate_rotation_analysis(self, sector_data: dict[str, Any], min_rotation_signal: float) -> None:
        """Validate rotation analysis requirements"""

        # Check for rotation signal
        rotation_signal = sector_data.get("rotation_signal")
        if rotation_signal is None:
            raise ValidationError(
                "Rotation signal not found in sector data",
                context={"required_field": "rotation_signal"},
            )

        # Check rotation score if available
        rotation_score = sector_data.get("rotation_score")
        if rotation_score is not None and isinstance(rotation_score, (int, float)):
            if rotation_score < min_rotation_signal:
                raise ValidationError(
                    f"Rotation score {rotation_score:.2f} below minimum threshold {min_rotation_signal:.2f}",
                    context={
                        "rotation_score": rotation_score,
                        "threshold": min_rotation_signal,
                    },
                )

    def _validate_comparison_analysis(self, sector_data: dict[str, Any], benchmark_sectors: list[str] | None) -> None:
        """Validate comparison analysis requirements"""

        # Check for comparison indicators
        comparison_fields = [
            "sector_comparison",
            "relative_valuation",
            "performance_ranking",
        ]
        available_fields = [field for field in comparison_fields if field in sector_data]

        if not available_fields:
            raise ValidationError(
                "No comparison indicators found in sector data",
                context={
                    "required_fields": comparison_fields,
                    "available_fields": list(sector_data.keys()),
                },
            )

        # If benchmark sectors are provided, validate they're different from target sector
        if benchmark_sectors:
            sector_name = sector_data.get("sector_name", "").lower()
            if sector_name in [s.lower() for s in benchmark_sectors]:
                raise ValidationError(
                    f"Sector {sector_name} cannot be compared to itself",
                    context={
                        "sector_name": sector_name,
                        "benchmark_sectors": benchmark_sectors,
                    },
                )

    def _generate_content(self, sector_data: dict[str, Any], template_variant: str) -> str:
        """Generate Twitter content using template"""

        try:
            # Render template
            content = self.template_renderer.render_template(
                template_type="sector",
                template_variant=template_variant,
                data=sector_data,
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
                    "data_keys": list(sector_data.keys()),
                },
            )

    def _save_content(
        self,
        content: str,
        sector_name: str,
        analysis_type: str,
        date: str,
        output_path: str | None = None,
    ) -> Path:
        """Save generated content to file"""

        if output_path:
            output_file = Path(output_path)
        else:
            # Create output directory if it doesn't exist
            self.template_outputs_path.mkdir(parents=True, exist_ok=True)
            output_file = self.template_outputs_path / f"{sector_name.lower()}_{analysis_type}_{date}.md"

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
                "description": "Generate technology sector rotation analysis",
                "parameters": {
                    "sector_name": "technology",
                    "analysis_type": "rotation",
                    "date": "20240118",
                },
            },
            {
                "description": "Generate healthcare sector comparison analysis",
                "parameters": {
                    "sector_name": "healthcare",
                    "analysis_type": "comparison",
                    "date": "20240118",
                    "benchmark_sectors": ["technology", "financials"],
                },
            },
            {
                "description": "Auto-determine analysis type",
                "parameters": {
                    "sector_name": "energy",
                    "analysis_type": "auto",
                    "date": "20240118",
                },
            },
            {
                "description": "Generate with custom rotation threshold",
                "parameters": {
                    "sector_name": "financials",
                    "analysis_type": "rotation",
                    "date": "20240118",
                    "min_rotation_signal": 0.7,
                },
            },
        ]

    def get_sector_analysis_preview(self, sector_name: str, date: str, data_path: str | None = None) -> dict[str, Any]:
        """Preview sector analysis without generating content"""

        try:
            sector_data = self._load_sector_data(sector_name, date, data_path)

            # Determine best analysis type
            auto_analysis_type = self._determine_analysis_type(sector_data)

            # Get template recommendations
            sector_data_copy = sector_data.copy()
            sector_data_copy["analysis_type"] = auto_analysis_type

            if auto_analysis_type == "rotation":
                sector_data_copy["rotation_signal"] = sector_data_copy.get("rotation_signal", False)
            elif auto_analysis_type == "comparison":
                sector_data_copy["sector_comparison"] = sector_data_copy.get("sector_comparison", True)

            recommendations = self.template_selector.get_template_recommendations("sector", sector_data_copy)

            return {
                "sector_name": sector_name,
                "date": date,
                "recommended_analysis_type": auto_analysis_type,
                "data_summary": {
                    "fields": list(sector_data.keys()),
                    "has_rotation_indicators": any(
                        field in sector_data for field in ["rotation_signal", "rotation_score", "flow_data"]
                    ),
                    "has_comparison_indicators": any(
                        field in sector_data
                        for field in [
                            "sector_comparison",
                            "relative_valuation",
                            "performance_ranking",
                        ]
                    ),
                },
                "recommendations": recommendations,
            }

        except Exception as e:
            return {
                "sector_name": sector_name,
                "date": date,
                "error": str(e),
                "recommendations": [],
            }

    def get_valid_sectors(self) -> list[str]:
        """Get list of valid sector names"""
        return self.VALID_SECTORS.copy()

    def get_valid_analysis_types(self) -> list[str]:
        """Get list of valid analysis types"""
        return self.VALID_ANALYSIS_TYPES.copy()
