#!/usr/bin/env python3
"""
Template Scoring System

Modular template scoring algorithms:
- Data-driven scoring with contextual weighting
- Configurable scoring criteria
- Performance-based scoring adjustments
- Fail-fast validation for scoring inputs
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from error_handler import ErrorHandler
from errors import TypeValidationError, ValidationError
from logging_config import TwitterSystemLogger


@dataclass
class ScoringCriteria:
    """Configuration for template scoring criteria"""

    name: str
    weight: float
    threshold: float = 0.0
    required: bool = False

    def validate(self) -> None:
        """Validate scoring criteria configuration"""
        if not 0.0 <= self.weight <= 1.0:
            raise ValidationError(
                f"Invalid weight for criterion '{self.name}': {self.weight}",
                context={"valid_range": "0.0 to 1.0"},
            )
        if self.threshold < 0.0:
            raise ValidationError(
                f"Invalid threshold for criterion '{self.name}': {self.threshold}",
                context={"minimum_threshold": 0.0},
            )


@dataclass
class ScoringResult:
    """Result of template scoring operation"""

    template_variant: str
    score: float
    criteria_scores: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "template_variant": self.template_variant,
            "score": self.score,
            "criteria_scores": self.criteria_scores,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


class BaseScoringAlgorithm(ABC):
    """Base class for scoring algorithms"""

    def __init__(self, criteria: list[ScoringCriteria]):
        self.criteria = criteria
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger(self.__class__.__name__)

        # Validate criteria
        self._validate_criteria()

    def _validate_criteria(self) -> None:
        """Validate scoring criteria configuration"""
        for criterion in self.criteria:
            criterion.validate()

        # Check that weights sum to reasonable value
        total_weight = sum(c.weight for c in self.criteria)
        if not 0.8 <= total_weight <= 1.2:
            raise ValidationError(
                f"Criteria weights sum to {total_weight}, should be close to 1.0",
                context={
                    "total_weight": total_weight,
                    "criteria_count": len(self.criteria),
                },
            )

    @abstractmethod
    def calculate_score(self, data: dict[str, Any], context: dict[str, Any] | None = None) -> ScoringResult:
        """Calculate template score based on data"""

    def validate_input_data(self, data: dict[str, Any]) -> None:
        """Validate input data for scoring"""
        if not isinstance(data, dict):
            raise TypeValidationError(
                "Input data must be a dictionary",
                expected_type="dict",
                actual_type=type(data).__name__,
                field_name="data",
            )

        # Check for required fields based on criteria (fail-fast approach)
        for criterion in self.criteria:
            if criterion.required and criterion.name not in data:
                # For backward compatibility, we'll warn but not fail
                self.logger.logger.warning(
                    f"Missing required field for scoring: {criterion.name}",
                    extra={"available_fields": list(data.keys())},
                )
                # Continue with scoring using default values


class WeightedScoringAlgorithm(BaseScoringAlgorithm):
    """Weighted scoring algorithm with configurable criteria"""

    def calculate_score(self, data: dict[str, Any], context: dict[str, Any] | None = None) -> ScoringResult:
        """Calculate weighted score based on criteria"""

        self.validate_input_data(data)

        criteria_scores = {}
        total_score = 0.0
        total_weight = 0.0

        for criterion in self.criteria:
            try:
                score = self._evaluate_criterion(data, criterion, context)
                criteria_scores[criterion.name] = score
                total_score += score * criterion.weight
                total_weight += criterion.weight

            except Exception as e:
                self.logger.log_error(e, {"criterion": criterion.name, "data_keys": list(data.keys())})
                # Continue with other criteria
                criteria_scores[criterion.name] = 0.0

        # Normalize score
        final_score = total_score / total_weight if total_weight > 0 else 0.0

        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(data, criteria_scores)

        return ScoringResult(
            template_variant="",  # Will be set by caller
            score=final_score,
            criteria_scores=criteria_scores,
            confidence=confidence,
            explanation=self._generate_explanation(criteria_scores, final_score),
        )

    def _evaluate_criterion(
        self,
        data: dict[str, Any],
        criterion: ScoringCriteria,
        context: dict[str, Any] | None,
    ) -> float:
        """Evaluate a single scoring criterion"""

        # Handle special criterion types
        if criterion.name == "valuation_gap":
            current_price = data.get("current_price", 0)
            fair_value = data.get("fair_value", 0)
            if current_price > 0 and fair_value > 0:
                gap = abs(fair_value - current_price) / current_price * 100
                return min(1.0, gap / criterion.threshold)
            return 0.0

        if criterion.name == "catalyst_count":
            # Check for catalyst list or catalyst_count field
            catalysts = data.get("catalysts", [])
            catalyst_count = data.get("catalyst_count", len(catalysts) if catalysts else 0)
            return min(1.0, catalyst_count / criterion.threshold) if criterion.threshold > 0 else 1.0

        # Get criterion value from data
        value = data.get(criterion.name)

        if value is None:
            return 0.0 if not criterion.required else 0.0

        # Handle different value types
        if isinstance(value, (int, float)):
            return min(1.0, max(0.0, value / criterion.threshold)) if criterion.threshold > 0 else 1.0
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, list):
            return min(1.0, len(value) / criterion.threshold) if criterion.threshold > 0 else 1.0
        if isinstance(value, str):
            return 1.0 if value.strip() else 0.0
        return 0.5  # Default score for unknown types

    def _calculate_confidence(self, data: dict[str, Any], scores: dict[str, float]) -> float:
        """Calculate confidence in scoring result"""

        # Base confidence on data completeness
        available_fields = len([k for k in data if data[k] is not None])
        total_fields = len(self.criteria)

        data_completeness = available_fields / total_fields if total_fields > 0 else 0.0

        # Adjust for score variance
        score_values = list(scores.values())
        if score_values:
            score_variance = sum((s - sum(score_values) / len(score_values)) ** 2 for s in score_values) / len(
                score_values
            )
            variance_penalty = min(0.3, score_variance)
        else:
            variance_penalty = 0.3

        confidence = data_completeness - variance_penalty
        return max(0.0, min(1.0, confidence))

    def _generate_explanation(self, scores: dict[str, float], final_score: float) -> str:
        """Generate explanation for scoring result"""

        if final_score >= 0.8:
            return "Strong match across multiple criteria"
        if final_score >= 0.6:
            return "Good match with some missing elements"
        if final_score >= 0.4:
            return "Moderate match with significant gaps"
        return "Poor match with minimal criteria satisfied"


class TemplateScoringEngine:
    """Main scoring engine for template selection"""

    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger("TemplateScoringEngine")

        # Initialize scoring algorithms for different content types
        self.scoring_algorithms = self._initialize_scoring_algorithms()

    def _initialize_scoring_algorithms(
        self,
    ) -> dict[str, dict[str, BaseScoringAlgorithm]]:
        """Initialize scoring algorithms for each content type and template"""

        algorithms = {}

        # Fundamental analysis scoring
        algorithms["fundamental"] = {
            "A_valuation": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("valuation_gap", 0.3, 10.0, True),
                    ScoringCriteria("valuation_methods", 0.2, 2.0),
                    ScoringCriteria("dcf_value", 0.2, 1.0),
                    ScoringCriteria("fair_value", 0.3, 1.0, True),
                ]
            ),
            "B_catalyst": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("catalyst_count", 0.4, 2.0, True),
                    ScoringCriteria("catalyst_probability", 0.3, 0.7),
                    ScoringCriteria("upcoming_events", 0.3, 1.0),
                ]
            ),
            "C_moat": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("moat_strength", 0.4, 7.0, True),
                    ScoringCriteria("competitive_advantages", 0.3, 2.0),
                    ScoringCriteria("market_position", 0.3, 1.0),
                ]
            ),
        }

        # Strategy analysis scoring
        algorithms["strategy"] = {
            "default": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("win_rate", 0.3, 0.6),
                    ScoringCriteria("net_performance", 0.3, 10.0),
                    ScoringCriteria("reward_risk", 0.2, 1.5),
                    ScoringCriteria("total_trades", 0.2, 10.0),
                ]
            )
        }

        # Sector analysis scoring
        algorithms["sector"] = {
            "rotation": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("rotation_signal", 0.4, 0.5, True),
                    ScoringCriteria("rotation_score", 0.3, 0.7),
                    ScoringCriteria("relative_performance", 0.3, 5.0),
                ]
            ),
            "comparison": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("sector_comparison", 0.3, 0.5, True),
                    ScoringCriteria("relative_valuation", 0.3, 0.5),
                    ScoringCriteria("performance_ranking", 0.4, 1.0),
                ]
            ),
        }

        # Trade history scoring
        algorithms["trade_history"] = {
            "performance": WeightedScoringAlgorithm(
                [
                    ScoringCriteria("performance_metrics", 0.4, 0.5, True),
                    ScoringCriteria("win_rate", 0.3, 0.6),
                    ScoringCriteria("transparency_level", 0.3, 0.5),
                ]
            )
        }

        return algorithms

    def score_template(
        self,
        content_type: str,
        template_variant: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> ScoringResult:
        """Score a specific template variant"""

        if content_type not in self.scoring_algorithms:
            raise ValidationError(
                f"Unknown content type: {content_type}",
                context={"available_types": list(self.scoring_algorithms.keys())},
            )

        if template_variant not in self.scoring_algorithms[content_type]:
            raise ValidationError(
                f"Unknown template variant '{template_variant}' for content type '{content_type}'",
                context={"available_variants": list(self.scoring_algorithms[content_type].keys())},
            )

        algorithm = self.scoring_algorithms[content_type][template_variant]

        try:
            result = algorithm.calculate_score(data, context)
            result.template_variant = template_variant

            self.logger.log_operation(
                f"Template scored: {template_variant}",
                {"score": result.score, "confidence": result.confidence},
            )

            return result

        except Exception as e:
            self.error_handler.handle_processing_error(
                f"template_scoring_{template_variant}",
                {"content_type": content_type, "data_keys": list(data.keys())},
                e,
            )
            raise

    def score_all_templates(
        self,
        content_type: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, ScoringResult]:
        """Score all templates for a content type"""

        if content_type not in self.scoring_algorithms:
            raise ValidationError(
                f"Unknown content type: {content_type}",
                context={"available_types": list(self.scoring_algorithms.keys())},
            )

        results = {}

        for template_variant in self.scoring_algorithms[content_type]:
            try:
                result = self.score_template(content_type, template_variant, data, context)
                results[template_variant] = result
            except Exception as e:
                self.logger.log_error(
                    e,
                    {
                        "content_type": content_type,
                        "template_variant": template_variant,
                    },
                )
                # Continue with other templates

        return results

    def get_scoring_criteria(self, content_type: str, template_variant: str) -> list[ScoringCriteria]:
        """Get scoring criteria for a specific template"""

        if content_type not in self.scoring_algorithms:
            return []

        if template_variant not in self.scoring_algorithms[content_type]:
            return []

        return self.scoring_algorithms[content_type][template_variant].criteria

    def update_scoring_criteria(
        self, content_type: str, template_variant: str, criteria: list[ScoringCriteria]
    ) -> None:
        """Update scoring criteria for a template"""

        if content_type not in self.scoring_algorithms:
            raise ValidationError(f"Unknown content type: {content_type}")

        if template_variant not in self.scoring_algorithms[content_type]:
            raise ValidationError(f"Unknown template variant: {template_variant}")

        # Create new algorithm with updated criteria
        self.scoring_algorithms[content_type][template_variant] = WeightedScoringAlgorithm(criteria)

        self.logger.log_operation(
            f"Updated scoring criteria for {content_type}/{template_variant}",
            {"criteria_count": len(criteria)},
        )
