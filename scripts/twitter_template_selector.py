#!/usr/bin/env python3
"""
Twitter Template Selector

Advanced template selection system with:
- Data-driven template selection algorithms
- Template performance analytics
- A/B testing framework
- Selection validation and optimization
"""

from datetime import datetime
from pathlib import Path
from typing import Any


class TwitterTemplateSelector:
    """Advanced template selection and optimization system"""

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the template selector"""
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"

        # Template selection criteria weights
        self.selection_weights = {
            "fundamental": {
                "data_completeness": 0.3,
                "insight_strength": 0.4,
                "template_match": 0.3,
            },
            "strategy": {
                "signal_strength": 0.4,
                "performance_metrics": 0.3,
                "market_context": 0.3,
            },
            "sector": {
                "rotation_indicators": 0.4,
                "relative_performance": 0.3,
                "economic_context": 0.3,
            },
            "trade_history": {
                "performance_data": 0.4,
                "transparency_level": 0.3,
                "narrative_focus": 0.3,
            },
        }

        # Template performance tracking
        self.template_performance = {}

        # Initialize selection rules
        self.selection_rules = self._initialize_selection_rules()

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

        if content_type not in self.selection_rules:
            raise ValueError(f"Unknown content type: {content_type}")

        # Get selection rules for content type
        rules = self.selection_rules[content_type]

        # Score each template variant
        template_scores = {}
        for template_variant, rule in rules.items():
            score = self._calculate_template_score(data, rule, context)
            template_scores[template_variant] = score

        # Select highest scoring template
        selected_template = max(template_scores, key=template_scores.get)

        # Generate selection metadata
        selection_metadata = {
            "selected_template": selected_template,
            "selection_score": template_scores[selected_template],
            "all_scores": template_scores,
            "selection_timestamp": datetime.now().isoformat(),
            "content_type": content_type,
            "selection_reason": self._generate_selection_reason(
                selected_template, template_scores, rules[selected_template]
            ),
        }

        return selected_template, selection_metadata

    def _initialize_selection_rules(self) -> dict[str, dict[str, dict[str, Any]]]:
        """Initialize template selection rules"""

        return {
            "fundamental": {
                "A_valuation": {
                    "required_indicators": [
                        "fair_value",
                        "fair_value_low",
                        "fair_value_high",
                        "current_price",
                        "valuation_methods",
                        "dcf_value",
                    ],
                    "scoring_criteria": {
                        "valuation_gap": {"weight": 0.4, "min_threshold": 10},
                        "method_confidence": {"weight": 0.3, "min_threshold": 0.7},
                        "price_target_clarity": {"weight": 0.3, "min_threshold": 0.8},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 1.0,
                },
                "B_catalyst": {
                    "required_indicators": [
                        "catalysts",
                        "catalyst_1",
                        "upcoming_events",
                        "timeline_detail",
                        "catalyst_count",
                    ],
                    "scoring_criteria": {
                        "catalyst_count": {"weight": 0.4, "min_threshold": 2},
                        "catalyst_probability": {"weight": 0.3, "min_threshold": 0.6},
                        "catalyst_timeline": {"weight": 0.3, "min_threshold": 0.7},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 0.9,
                },
                "C_moat": {
                    "required_indicators": [
                        "moat_advantages",
                        "competitive_advantages",
                        "moat_strength",
                        "market_share",
                        "pricing_power",
                        "competitive_position",
                    ],
                    "scoring_criteria": {
                        "moat_strength": {"weight": 0.4, "min_threshold": 7},
                        "advantage_count": {"weight": 0.3, "min_threshold": 3},
                        "competitive_sustainability": {
                            "weight": 0.3,
                            "min_threshold": 0.7,
                        },
                    },
                    "exclusion_criteria": [],
                    "priority_score": 0.8,
                },
                "D_contrarian": {
                    "required_indicators": [
                        "contrarian_insight",
                        "common_perception",
                        "market_misconception",
                        "mispricing",
                        "contrarian_evidence",
                    ],
                    "scoring_criteria": {
                        "contrarian_strength": {"weight": 0.4, "min_threshold": 0.8},
                        "evidence_quality": {"weight": 0.3, "min_threshold": 0.7},
                        "mispricing_magnitude": {"weight": 0.3, "min_threshold": 15},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 0.7,
                },
                "E_financial": {
                    "required_indicators": [
                        "financial_health",
                        "profitability_grade",
                        "balance_sheet_grade",
                        "cash_flow_grade",
                        "financial_grades",
                    ],
                    "scoring_criteria": {
                        "financial_health_score": {"weight": 0.4, "min_threshold": 0.7},
                        "grade_consistency": {"weight": 0.3, "min_threshold": 0.6},
                        "financial_trend": {"weight": 0.3, "min_threshold": 0.7},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 0.6,  # Default fallback
                },
            },
            "strategy": {
                "default": {
                    "required_indicators": [
                        "strategy_type",
                        "win_rate",
                        "net_performance",
                        "reward_risk",
                        "total_trades",
                    ],
                    "scoring_criteria": {
                        "performance_strength": {"weight": 0.4, "min_threshold": 10},
                        "consistency_metrics": {"weight": 0.3, "min_threshold": 0.6},
                        "signal_quality": {"weight": 0.3, "min_threshold": 0.7},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 1.0,
                }
            },
            "sector": {
                "rotation": {
                    "required_indicators": [
                        "rotation_signal",
                        "sector_rotation",
                        "economic_cycle",
                        "relative_performance",
                        "flow_data",
                    ],
                    "scoring_criteria": {
                        "rotation_strength": {"weight": 0.4, "min_threshold": 0.7},
                        "economic_alignment": {"weight": 0.3, "min_threshold": 0.6},
                        "flow_confirmation": {"weight": 0.3, "min_threshold": 0.7},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 1.0,
                },
                "comparison": {
                    "required_indicators": [
                        "sector_comparison",
                        "relative_valuation",
                        "cross_sector",
                        "performance_ranking",
                        "allocation_recommendation",
                    ],
                    "scoring_criteria": {
                        "comparison_depth": {"weight": 0.4, "min_threshold": 0.7},
                        "valuation_clarity": {"weight": 0.3, "min_threshold": 0.6},
                        "allocation_conviction": {"weight": 0.3, "min_threshold": 0.7},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 0.8,
                },
            },
            "trade_history": {
                "performance": {
                    "required_indicators": [
                        "performance_metrics",
                        "win_rate",
                        "total_trades",
                        "period_return",
                        "transparency_level",
                    ],
                    "scoring_criteria": {
                        "performance_data_quality": {
                            "weight": 0.4,
                            "min_threshold": 0.8,
                        },
                        "transparency_level": {"weight": 0.3, "min_threshold": 0.7},
                        "narrative_strength": {"weight": 0.3, "min_threshold": 0.6},
                    },
                    "exclusion_criteria": [],
                    "priority_score": 1.0,
                }
            },
        }

    def _calculate_template_score(
        self,
        data: dict[str, Any],
        rule: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate template selection score based on data and rules"""

        total_score = 0.0
        max_possible_score = 0.0

        # Check required indicators
        required_indicators = rule.get("required_indicators", [])
        indicators_found = sum(1 for indicator in required_indicators if data.get(indicator))

        if required_indicators:
            indicator_score = indicators_found / len(required_indicators)
            total_score += indicator_score * 0.3  # 30% weight for required indicators
            max_possible_score += 0.3

        # Check scoring criteria
        scoring_criteria = rule.get("scoring_criteria", {})
        for criterion, params in scoring_criteria.items():
            weight = params.get("weight", 0.1)
            min_threshold = params.get("min_threshold", 0.0)

            criterion_score = self._evaluate_criterion(data, criterion, min_threshold)
            total_score += criterion_score * weight
            max_possible_score += weight

        # Apply priority score
        priority_score = rule.get("priority_score", 1.0)
        total_score *= priority_score
        max_possible_score *= priority_score

        # Check exclusion criteria
        exclusion_criteria = rule.get("exclusion_criteria", [])
        for exclusion in exclusion_criteria:
            if data.get(exclusion):
                total_score *= 0.5  # Penalty for exclusion criteria

        # Normalize score
        if max_possible_score > 0:
            normalized_score = total_score / max_possible_score
        else:
            normalized_score = 0.0

        return min(1.0, max(0.0, normalized_score))

    def _evaluate_criterion(self, data: dict[str, Any], criterion: str, min_threshold: float) -> float:
        """Evaluate a specific scoring criterion"""

        if criterion == "valuation_gap":
            current_price = data.get("current_price", 0)
            fair_value = data.get("fair_value") or data.get("weighted_fair_value", 0)
            if current_price > 0 and fair_value > 0:
                gap = abs(fair_value - current_price) / current_price * 100
                return 1.0 if gap >= min_threshold else gap / min_threshold

        elif criterion == "method_confidence":
            methods = data.get("valuation_methods", [])
            if methods:
                avg_confidence = sum(m.get("confidence", 0) for m in methods) / len(methods)
                return 1.0 if avg_confidence >= min_threshold else avg_confidence / min_threshold

        elif criterion == "catalyst_count":
            catalysts = data.get("catalysts", [])
            catalyst_count = len(catalysts) if catalysts else data.get("catalyst_count", 0)
            return 1.0 if catalyst_count >= min_threshold else catalyst_count / min_threshold

        elif criterion == "catalyst_probability":
            catalysts = data.get("catalysts", [])
            if catalysts:
                avg_prob = sum(c.get("probability", 0) for c in catalysts) / len(catalysts)
                return 1.0 if avg_prob >= min_threshold else avg_prob / min_threshold

        elif criterion == "moat_strength":
            moat_strength = data.get("moat_strength", 0)
            return 1.0 if moat_strength >= min_threshold else moat_strength / min_threshold

        elif criterion == "advantage_count":
            advantages = data.get("competitive_advantages", [])
            advantage_count = len(advantages) if advantages else 0
            return 1.0 if advantage_count >= min_threshold else advantage_count / min_threshold

        elif criterion == "contrarian_strength":
            contrarian_score = data.get("contrarian_score", 0)
            return 1.0 if contrarian_score >= min_threshold else contrarian_score / min_threshold

        elif criterion == "mispricing_magnitude":
            mispricing = data.get("mispricing_percentage", 0)
            return 1.0 if mispricing >= min_threshold else mispricing / min_threshold

        elif criterion == "financial_health_score":
            financial_score = data.get("financial_health_score", 0)
            return 1.0 if financial_score >= min_threshold else financial_score / min_threshold

        elif criterion == "performance_strength":
            net_performance = data.get("net_performance", 0)
            return 1.0 if net_performance >= min_threshold else max(0, net_performance / min_threshold)

        elif criterion == "rotation_strength":
            rotation_score = data.get("rotation_score", 0)
            return 1.0 if rotation_score >= min_threshold else rotation_score / min_threshold

        elif criterion == "performance_data_quality":
            quality_score = data.get("data_quality_score", 0)
            return 1.0 if quality_score >= min_threshold else quality_score / min_threshold

        # Default evaluation for other criteria
        criterion_value = data.get(criterion, 0)
        if isinstance(criterion_value, (int, float)):
            return 1.0 if criterion_value >= min_threshold else criterion_value / min_threshold
        if isinstance(criterion_value, (list, dict)):
            return 1.0 if len(criterion_value) >= min_threshold else len(criterion_value) / min_threshold
        return 1.0 if criterion_value else 0.0

    def _generate_selection_reason(
        self,
        selected_template: str,
        template_scores: dict[str, float],
        rule: dict[str, Any],
    ) -> str:
        """Generate human-readable selection reason"""

        score = template_scores[selected_template]

        # Find the top scoring criteria
        top_criteria = []
        scoring_criteria = rule.get("scoring_criteria", {})
        for criterion, params in scoring_criteria.items():
            weight = params.get("weight", 0.1)
            if weight >= 0.3:  # High weight criteria
                top_criteria.append(criterion)

        reason_parts = [
            f"Selected template '{selected_template}' with score {score:.2f}",
            f"Primary factors: {', '.join(top_criteria) if top_criteria else 'general fit'}",
        ]

        # Add comparison context
        other_scores = [f"{k}: {v:.2f}" for k, v in template_scores.items() if k != selected_template]
        if other_scores:
            reason_parts.append(f"Alternatives: {', '.join(other_scores)}")

        return ". ".join(reason_parts)

    def validate_template_selection(
        self, content_type: str, template_variant: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate that a template selection is appropriate"""

        if content_type not in self.selection_rules:
            return {
                "valid": False,
                "reason": f"Unknown content type: {content_type}",
                "confidence": 0.0,
            }

        if template_variant not in self.selection_rules[content_type]:
            return {
                "valid": False,
                "reason": f"Unknown template variant: {template_variant}",
                "confidence": 0.0,
            }

        rule = self.selection_rules[content_type][template_variant]
        score = self._calculate_template_score(data, rule)

        # Calculate validation confidence
        confidence = min(1.0, max(0.0, score))

        # Determine validation result
        valid = confidence >= 0.6  # 60% threshold for validation

        return {
            "valid": valid,
            "confidence": confidence,
            "score": score,
            "reason": f"Template score {score:.2f} {'meets' if valid else 'below'} validation threshold",
            "validation_timestamp": datetime.now().isoformat(),
        }

    def get_template_recommendations(self, content_type: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Get ranked template recommendations with explanations"""

        if content_type not in self.selection_rules:
            return []

        recommendations = []
        rules = self.selection_rules[content_type]

        for template_variant, rule in rules.items():
            score = self._calculate_template_score(data, rule)

            # Generate recommendation explanation
            explanation = self._generate_template_explanation(template_variant, rule, data)

            recommendations.append(
                {
                    "template_variant": template_variant,
                    "score": score,
                    "confidence": min(1.0, max(0.0, score)),
                    "explanation": explanation,
                    "recommended": score >= 0.6,
                }
            )

        # Sort by score (descending)
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return recommendations

    def _generate_template_explanation(self, template_variant: str, rule: dict[str, Any], data: dict[str, Any]) -> str:
        """Generate explanation for why a template is recommended"""

        required_indicators = rule.get("required_indicators", [])
        found_indicators = [ind for ind in required_indicators if data.get(ind)]

        explanation_parts = []

        if found_indicators:
            explanation_parts.append(f"Has {len(found_indicators)}/{len(required_indicators)} required indicators")

        # Add specific explanations based on template type
        if template_variant == "A_valuation":
            if data.get("current_price") and data.get("fair_value"):
                explanation_parts.append("Contains price vs fair value analysis")
        elif template_variant == "B_catalyst":
            catalyst_count = len(data.get("catalysts", []))
            if catalyst_count > 0:
                explanation_parts.append(f"Has {catalyst_count} identified catalysts")
        elif template_variant == "C_moat":
            moat_strength = data.get("moat_strength", 0)
            if moat_strength > 0:
                explanation_parts.append(f"Moat strength score: {moat_strength}")
        elif template_variant == "D_contrarian":
            if data.get("contrarian_insight"):
                explanation_parts.append("Contains contrarian analysis")
        elif template_variant == "E_financial":
            if data.get("financial_health"):
                explanation_parts.append("Contains financial health analysis")

        return ". ".join(explanation_parts) if explanation_parts else "General template match"

    def update_template_performance(self, template_variant: str, performance_metrics: dict[str, Any]) -> None:
        """Update template performance tracking"""

        if template_variant not in self.template_performance:
            self.template_performance[template_variant] = []

        self.template_performance[template_variant].append(
            {"timestamp": datetime.now().isoformat(), "metrics": performance_metrics}
        )

    def get_template_performance_analytics(self) -> dict[str, Any]:
        """Get template performance analytics"""

        analytics = {}

        for template_variant, performance_data in self.template_performance.items():
            if not performance_data:
                continue

            # Calculate average metrics
            avg_metrics = {}
            for metric in ["engagement_score", "click_through_rate", "conversion_rate"]:
                values = [p["metrics"].get(metric, 0) for p in performance_data]
                avg_metrics[metric] = sum(values) / len(values) if values else 0

            analytics[template_variant] = {
                "usage_count": len(performance_data),
                "average_metrics": avg_metrics,
                "latest_performance": (performance_data[-1] if performance_data else None),
            }

        return analytics
