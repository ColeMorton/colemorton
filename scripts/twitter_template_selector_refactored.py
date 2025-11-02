#!/usr/bin/env python3
"""
Twitter Template Selector (Refactored)

Modular template selection system using:
- TemplateScoringEngine for scoring logic
- TemplateSelectionEngine for selection algorithms
- TemplateCriteriaManager for criteria management
"""

from pathlib import Path
from typing import Any

from error_handler import ErrorHandler
from logging_config import TwitterSystemLogger
from result_types import TemplateSelectionResult
from template_criteria_manager import TemplateCriteriaManager
from template_scoring import TemplateScoringEngine
from template_selection_engine import SelectionContext, TemplateSelectionEngine


class TwitterTemplateSelector:
    """
    Refactored Twitter template selector using modular architecture

    This class provides a high-level interface to the modular template selection system
    while maintaining backward compatibility with the existing API.
    """

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the modular template selector"""

        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger("TwitterTemplateSelector")

        # Initialize modular components
        self.criteria_manager = TemplateCriteriaManager()
        self.scoring_engine = TemplateScoringEngine()
        self.selection_engine = TemplateSelectionEngine(self.scoring_engine)

        # Template performance tracking
        self.template_performance = {}

        # Selection history for analytics
        self.selection_history = []

    def select_optimal_template(
        self,
        content_type: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Select the optimal template based on data characteristics and context

        Args:
            content_type: Type of content (fundamental, strategy, sector, trade_history)
            data: Data context for analysis
            context: Additional context information

        Returns:
            Tuple of (template_variant, selection_metadata)
        """

        try:
            # Convert context to SelectionContext
            selection_context = self._convert_context(context)

            # Use selection engine to select template
            result = self.selection_engine.select_template(content_type, data, selection_context)

            # Track selection
            self._track_selection(result)

            # Convert result to legacy format
            metadata = {
                "selected_template": result.selected_template,
                "selection_score": result.selection_score,
                "all_scores": result.all_scores,
                "selection_timestamp": result.timestamp,
                "content_type": content_type,
                "selection_reason": result.selection_reason,
            }

            return result.selected_template, metadata

        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_selection",
                {"content_type": content_type, "data_keys": list(data.keys())},
                e,
            )
            raise

    def get_template_recommendations(
        self,
        content_type: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get ranked template recommendations"""

        try:
            selection_context = self._convert_context(context)

            return self.selection_engine.get_template_recommendations(content_type, data, selection_context)

        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_recommendations",
                {"content_type": content_type, "data_keys": list(data.keys())},
                e,
            )
            raise

    def validate_template_selection(
        self,
        content_type: str,
        template_variant: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate a template selection"""

        try:
            selection_context = self._convert_context(context)

            return self.selection_engine.validate_template_selection(
                content_type, template_variant, data, selection_context
            )

        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_validation",
                {"content_type": content_type, "template_variant": template_variant},
                e,
            )
            raise

    def update_template_performance(self, template_variant: str, metrics: dict[str, float]) -> None:
        """Update template performance metrics"""

        if template_variant not in self.template_performance:
            self.template_performance[template_variant] = {
                "usage_count": 0,
                "metrics_history": [],
                "average_metrics": {},
            }

        self.template_performance[template_variant]["usage_count"] += 1
        self.template_performance[template_variant]["metrics_history"].append(metrics)

        # Update average metrics
        history = self.template_performance[template_variant]["metrics_history"]
        averages = {}
        for metric_name in metrics:
            values = [m.get(metric_name, 0) for m in history if metric_name in m]
            if values:
                averages[metric_name] = sum(values) / len(values)

        self.template_performance[template_variant]["average_metrics"] = averages

        self.logger.log_operation(
            f"Updated performance metrics for {template_variant}",
            {
                "metrics": list(metrics.keys()),
                "usage_count": self.template_performance[template_variant]["usage_count"],
            },
        )

    def get_template_performance_analytics(self) -> dict[str, Any]:
        """Get template performance analytics"""

        return self.template_performance.copy()

    def _convert_context(self, context: dict[str, Any] | None) -> SelectionContext:
        """Convert legacy context to SelectionContext"""

        if not context:
            return SelectionContext()

        return SelectionContext(
            market_conditions=context.get("market_conditions"),
            user_preferences=context.get("user_preferences", {}),
            historical_performance=context.get("historical_performance", {}),
            a_b_test_group=context.get("a_b_test_group"),
        )

    def _track_selection(self, result: TemplateSelectionResult) -> None:
        """Track selection for analytics"""

        self.selection_history.append(
            {
                "timestamp": result.timestamp,
                "content_type": result.content_type,
                "selected_template": result.selected_template,
                "selection_score": result.selection_score,
                "confidence": result.get_confidence_score(),
            }
        )

        # Keep only last 1000 selections
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]

    def _evaluate_criterion(self, data: dict[str, Any], criterion_name: str, threshold: float) -> float:
        """
        Evaluate a criterion (backward compatibility method)

        This method provides backward compatibility with the old template selection system
        by delegating to the scoring engine.
        """

        try:
            # Get the value from data
            value = data.get(criterion_name)

            if value is None:
                return 0.0

            # Handle specific criterion types
            if criterion_name == "valuation_gap":
                current_price = data.get("current_price", 0)
                fair_value = data.get("fair_value", 0)
                if current_price > 0 and fair_value > 0:
                    gap = abs(fair_value - current_price) / current_price * 100
                    return min(1.0, gap / threshold)
                return 0.0

            if criterion_name == "catalyst_count":
                if isinstance(value, list):
                    return min(1.0, len(value) / threshold)
                if isinstance(value, int):
                    return min(1.0, value / threshold)
                return 0.0

            if criterion_name == "moat_strength":
                if isinstance(value, (int, float)):
                    return min(1.0, value / threshold)
                return 0.0

            # Default evaluation
            if isinstance(value, (int, float)):
                return min(1.0, value / threshold) if threshold > 0 else 1.0
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if isinstance(value, list):
                return min(1.0, len(value) / threshold) if threshold > 0 else 1.0
            if isinstance(value, str):
                return 1.0 if value.strip() else 0.0
            return 0.5

        except Exception as e:
            self.logger.log_error(e, {"criterion_name": criterion_name, "threshold": threshold})
            return 0.0

    def get_selection_analytics(self) -> dict[str, Any]:
        """Get selection analytics"""

        if not self.selection_history:
            return {"total_selections": 0}

        # Calculate statistics
        total_selections = len(self.selection_history)

        # Template usage counts
        template_usage = {}
        for selection in self.selection_history:
            template = selection["selected_template"]
            template_usage[template] = template_usage.get(template, 0) + 1

        # Average scores by template
        template_scores = {}
        for selection in self.selection_history:
            template = selection["selected_template"]
            score = selection["selection_score"]
            if template not in template_scores:
                template_scores[template] = []
            template_scores[template].append(score)

        average_scores = {template: sum(scores) / len(scores) for template, scores in template_scores.items()}

        return {
            "total_selections": total_selections,
            "template_usage": template_usage,
            "average_scores": average_scores,
            "most_used_template": (max(template_usage.items(), key=lambda x: x[1])[0] if template_usage else None),
            "highest_scoring_template": (
                max(average_scores.items(), key=lambda x: x[1])[0] if average_scores else None
            ),
        }

    def export_configuration(self, output_path: Path) -> None:
        """Export template selector configuration"""

        try:
            self.criteria_manager.export_criteria_configuration(output_path)
            self.logger.log_operation(
                f"Exported template selector configuration to {output_path}",
                {"criteria_profiles": len(self.criteria_manager.criteria_profiles)},
            )

        except Exception as e:
            self.error_handler.handle_processing_error("configuration_export", {"output_path": str(output_path)}, e)

    def import_configuration(self, config_path: Path) -> None:
        """Import template selector configuration"""

        try:
            self.criteria_manager.import_criteria_configuration(config_path)
            # Re-initialize scoring engine with new criteria
            self.scoring_engine = TemplateScoringEngine()
            self.selection_engine = TemplateSelectionEngine(self.scoring_engine)

            self.logger.log_operation(
                f"Imported template selector configuration from {config_path}",
                {"criteria_profiles": len(self.criteria_manager.criteria_profiles)},
            )

        except Exception as e:
            self.error_handler.handle_processing_error("configuration_import", {"config_path": str(config_path)}, e)

    def get_available_templates(self, content_type: str) -> list[str]:
        """Get available templates for content type"""

        return self.criteria_manager.get_available_templates(content_type)

    def get_system_status(self) -> dict[str, Any]:
        """Get system status and health metrics"""

        return {
            "scoring_engine_status": "active",
            "selection_engine_status": "active",
            "criteria_manager_status": "active",
            "template_performance_tracking": len(self.template_performance),
            "selection_history_size": len(self.selection_history),
            "criteria_statistics": self.criteria_manager.get_criteria_statistics(),
        }
