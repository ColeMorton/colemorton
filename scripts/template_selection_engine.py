#!/usr/bin/env python3
"""
Template Selection Engine

Core template selection algorithms:
- Multi-criteria decision making
- Context-aware selection
- Performance-based optimization
- A/B testing support
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from error_handler import ErrorHandler
from errors import ValidationError
from logging_config import TwitterSystemLogger
from result_types import TemplateSelectionResult
from template_scoring import TemplateScoringEngine


@dataclass
class SelectionContext:
    """Context for template selection"""

    market_conditions: str | None = None
    user_preferences: dict[str, Any] = field(default_factory=dict)
    historical_performance: dict[str, float] = field(default_factory=dict)
    a_b_test_group: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "market_conditions": self.market_conditions,
            "user_preferences": self.user_preferences,
            "historical_performance": self.historical_performance,
            "a_b_test_group": self.a_b_test_group,
        }


class BaseSelectionStrategy(ABC):
    """Base class for template selection strategies"""

    def __init__(self, scoring_engine: TemplateScoringEngine):
        self.scoring_engine = scoring_engine
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger(self.__class__.__name__)

    @abstractmethod
    def select_template(
        self, content_type: str, data: dict[str, Any], context: SelectionContext
    ) -> TemplateSelectionResult:
        """Select optimal template based on strategy"""

    def validate_selection_input(self, content_type: str, data: dict[str, Any]) -> None:
        """Validate input for template selection"""

        if not content_type:
            raise ValidationError("Content type cannot be empty")

        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        if not data:
            raise ValidationError("Data cannot be empty")


class HighestScoreStrategy(BaseSelectionStrategy):
    """Select template with highest score"""

    def select_template(
        self, content_type: str, data: dict[str, Any], context: SelectionContext
    ) -> TemplateSelectionResult:
        """Select template with highest score"""

        self.validate_selection_input(content_type, data)

        # Score all templates
        try:
            scoring_results = self.scoring_engine.score_all_templates(content_type, data, context.to_dict())
        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_scoring",
                {"content_type": content_type, "data_keys": list(data.keys())},
                e,
            )
            raise

        if not scoring_results:
            raise ValidationError(f"No templates available for content type: {content_type}")

        # Find highest scoring template
        best_template = max(scoring_results.keys(), key=lambda k: scoring_results[k].score)
        best_result = scoring_results[best_template]

        # Create selection result
        all_scores = {k: v.score for k, v in scoring_results.items()}

        return TemplateSelectionResult(
            content_type=content_type,
            identifier=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            selected_template=best_template,
            selection_score=best_result.score,
            all_scores=all_scores,
            selection_reason=best_result.explanation,
            selection_confidence=best_result.confidence,
        )


class ContextAwareStrategy(BaseSelectionStrategy):
    """Select template based on context and performance history"""

    def __init__(
        self,
        scoring_engine: TemplateScoringEngine,
        context_weights: dict[str, float] | None = None,
    ):
        super().__init__(scoring_engine)
        self.context_weights = context_weights or {
            "market_conditions": 0.2,
            "historical_performance": 0.3,
            "user_preferences": 0.2,
            "data_quality": 0.3,
        }

    def select_template(
        self, content_type: str, data: dict[str, Any], context: SelectionContext
    ) -> TemplateSelectionResult:
        """Select template with context-aware scoring"""

        self.validate_selection_input(content_type, data)

        # Score all templates
        scoring_results = self.scoring_engine.score_all_templates(content_type, data, context.to_dict())

        if not scoring_results:
            raise ValidationError(f"No templates available for content type: {content_type}")

        # Apply context-based adjustments
        adjusted_scores = {}
        for template_name, result in scoring_results.items():
            base_score = result.score

            # Apply context adjustments
            context_bonus = self._calculate_context_bonus(template_name, context)
            performance_bonus = self._calculate_performance_bonus(template_name, context)

            adjusted_score = base_score + context_bonus + performance_bonus
            adjusted_scores[template_name] = min(1.0, max(0.0, adjusted_score))

        # Select best template
        best_template = max(adjusted_scores.keys(), key=lambda k: adjusted_scores[k])

        return TemplateSelectionResult(
            content_type=content_type,
            identifier=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            selected_template=best_template,
            selection_score=adjusted_scores[best_template],
            all_scores=adjusted_scores,
            selection_reason=f"Context-aware selection based on {', '.join(context.to_dict().keys())}",
            selection_confidence=scoring_results[best_template].confidence,
        )

    def _calculate_context_bonus(self, template_name: str, context: SelectionContext) -> float:
        """Calculate context-based bonus for template"""

        bonus = 0.0

        # Market conditions bonus
        if context.market_conditions:
            market_bonus = self._get_market_conditions_bonus(template_name, context.market_conditions)
            bonus += market_bonus * self.context_weights.get("market_conditions", 0.0)

        # User preferences bonus
        if context.user_preferences:
            preference_bonus = self._get_user_preferences_bonus(template_name, context.user_preferences)
            bonus += preference_bonus * self.context_weights.get("user_preferences", 0.0)

        return bonus

    def _calculate_performance_bonus(self, template_name: str, context: SelectionContext) -> float:
        """Calculate performance-based bonus for template"""

        if not context.historical_performance:
            return 0.0

        template_performance = context.historical_performance.get(template_name, 0.0)
        max_performance = max(context.historical_performance.values()) if context.historical_performance else 1.0

        if max_performance > 0:
            normalized_performance = template_performance / max_performance
            return normalized_performance * self.context_weights.get("historical_performance", 0.0)

        return 0.0

    def _get_market_conditions_bonus(self, template_name: str, market_conditions: str) -> float:
        """Get market conditions bonus for template"""

        # Simple market condition matching
        condition_bonuses = {
            "bullish": {"A_valuation": 0.1, "B_catalyst": 0.15},
            "bearish": {"C_moat": 0.1, "risk_analysis": 0.15},
            "volatile": {"strategy": 0.1, "technical": 0.15},
        }

        return condition_bonuses.get(market_conditions, {}).get(template_name, 0.0)

    def _get_user_preferences_bonus(self, template_name: str, user_preferences: dict[str, Any]) -> float:
        """Get user preferences bonus for template"""

        # Simple preference matching
        preference_style = user_preferences.get("style", "balanced")

        style_bonuses = {
            "detailed": {"A_valuation": 0.1, "fundamental": 0.15},
            "concise": {"B_catalyst": 0.1, "summary": 0.15},
            "visual": {"charts": 0.1, "technical": 0.15},
        }

        return style_bonuses.get(preference_style, {}).get(template_name, 0.0)


class ABTestStrategy(BaseSelectionStrategy):
    """A/B testing strategy for template selection"""

    def __init__(self, scoring_engine: TemplateScoringEngine, test_allocation: float = 0.5):
        super().__init__(scoring_engine)
        self.test_allocation = test_allocation

    def select_template(
        self, content_type: str, data: dict[str, Any], context: SelectionContext
    ) -> TemplateSelectionResult:
        """Select template with A/B testing logic"""

        self.validate_selection_input(content_type, data)

        scoring_results = self.scoring_engine.score_all_templates(content_type, data, context.to_dict())

        if not scoring_results:
            raise ValidationError(f"No templates available for content type: {content_type}")

        # Sort templates by score
        sorted_templates = sorted(scoring_results.keys(), key=lambda k: scoring_results[k].score, reverse=True)

        # A/B test logic
        if context.a_b_test_group == "control" or not context.a_b_test_group:
            # Use highest scoring template
            selected_template = sorted_templates[0]
        else:
            # Use second highest scoring template for test group
            selected_template = sorted_templates[1] if len(sorted_templates) > 1 else sorted_templates[0]

        all_scores = {k: v.score for k, v in scoring_results.items()}

        return TemplateSelectionResult(
            content_type=content_type,
            identifier=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            selected_template=selected_template,
            selection_score=scoring_results[selected_template].score,
            all_scores=all_scores,
            selection_reason=f"A/B test selection (group: {context.a_b_test_group or 'control'})",
            selection_confidence=scoring_results[selected_template].confidence,
        )


class TemplateSelectionEngine:
    """Main template selection engine"""

    def __init__(self, scoring_engine: TemplateScoringEngine | None = None):
        self.scoring_engine = scoring_engine or TemplateScoringEngine()
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger("TemplateSelectionEngine")

        # Initialize selection strategies
        self.strategies = {
            "highest_score": HighestScoreStrategy(self.scoring_engine),
            "context_aware": ContextAwareStrategy(self.scoring_engine),
            "ab_test": ABTestStrategy(self.scoring_engine),
        }

        # Default strategy
        self.default_strategy = "highest_score"

    def select_template(
        self,
        content_type: str,
        data: dict[str, Any],
        context: SelectionContext | None = None,
        strategy: str | None = None,
    ) -> TemplateSelectionResult:
        """Select optimal template using specified strategy"""

        # Use default context if none provided
        if context is None:
            context = SelectionContext()

        # Use default strategy if none specified
        strategy_name = strategy or self.default_strategy

        if strategy_name not in self.strategies:
            raise ValidationError(
                f"Unknown selection strategy: {strategy_name}",
                context={"available_strategies": list(self.strategies.keys())},
            )

        strategy_instance = self.strategies[strategy_name]

        try:
            result = strategy_instance.select_template(content_type, data, context)

            self.logger.log_operation(
                f"Template selected: {result.selected_template}",
                {
                    "content_type": content_type,
                    "strategy": strategy_name,
                    "score": result.selection_score,
                },
            )

            return result

        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_selection",
                {
                    "content_type": content_type,
                    "strategy": strategy_name,
                    "data_keys": list(data.keys()),
                },
                e,
            )
            raise

    def get_template_recommendations(
        self,
        content_type: str,
        data: dict[str, Any],
        context: SelectionContext | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Get ranked template recommendations"""

        if context is None:
            context = SelectionContext()

        try:
            # Score all templates
            scoring_results = self.scoring_engine.score_all_templates(content_type, data, context.to_dict())

            if not scoring_results:
                return []

            # Sort by score
            sorted_results = sorted(scoring_results.items(), key=lambda x: x[1].score, reverse=True)

            # Create recommendations
            recommendations = []
            for template_name, result in sorted_results[:limit]:
                recommendations.append(
                    {
                        "template_variant": template_name,
                        "score": result.score,
                        "confidence": result.confidence,
                        "explanation": result.explanation,
                        "recommended": result.score >= 0.6,
                    }
                )

            return recommendations

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
        selected_template: str,
        data: dict[str, Any],
        context: SelectionContext | None = None,
    ) -> dict[str, Any]:
        """Validate a template selection"""

        if context is None:
            context = SelectionContext()

        try:
            # Score the selected template
            result = self.scoring_engine.score_template(content_type, selected_template, data, context.to_dict())

            # Validate selection
            is_valid = result.score >= 0.5 and result.confidence >= 0.4

            return {
                "valid": is_valid,
                "score": result.score,
                "confidence": result.confidence,
                "explanation": result.explanation,
                "validation_threshold": 0.5,
                "confidence_threshold": 0.4,
            }

        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_validation",
                {
                    "content_type": content_type,
                    "selected_template": selected_template,
                    "data_keys": list(data.keys()),
                },
                e,
            )
            raise

    def add_selection_strategy(self, name: str, strategy: BaseSelectionStrategy) -> None:
        """Add custom selection strategy"""

        if not isinstance(strategy, BaseSelectionStrategy):
            raise ValidationError(
                "Strategy must inherit from BaseSelectionStrategy",
                context={"strategy_type": type(strategy).__name__},
            )

        self.strategies[name] = strategy

        self.logger.log_operation(
            f"Added selection strategy: {name}",
            {"strategy_type": type(strategy).__name__},
        )

    def get_strategy_performance(self) -> dict[str, dict[str, float]]:
        """Get performance metrics for each strategy"""

        # This would be implemented with actual performance tracking
        # For now, return placeholder data
        return {
            strategy_name: {
                "selection_count": 0,
                "average_score": 0.0,
                "success_rate": 0.0,
            }
            for strategy_name in self.strategies.keys()
        }
