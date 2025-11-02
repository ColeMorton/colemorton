#!/usr/bin/env python3
"""
Template Criteria Manager

Configurable validation criteria management:
- Dynamic criteria configuration
- Validation rule management
- Performance-based criteria optimization
- Template requirement enforcement
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from error_handler import ErrorHandler
from errors import ValidationError
from logging_config import TwitterSystemLogger
from template_scoring import ScoringCriteria


@dataclass
class TemplateRequirement:
    """Template requirement specification"""

    name: str
    description: str
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    validation_rules: dict[str, Any] = field(default_factory=dict)

    def validate_data(self, data: dict[str, Any]) -> list[str]:
        """Validate data against template requirements"""

        issues = []

        # Check required fields
        for field in self.required_fields:
            if field not in data or data[field] is None:
                issues.append(f"Missing required field: {field}")

        # Check validation rules
        for field, rule in self.validation_rules.items():
            if field in data:
                value = data[field]
                if not self._validate_field(value, rule):
                    issues.append(f"Field '{field}' failed validation: {rule}")

        return issues

    def _validate_field(self, value: Any, rule: dict[str, Any]) -> bool:
        """Validate a single field against a rule"""

        rule_type = rule.get("type", "any")

        if rule_type == "numeric":
            if not isinstance(value, (int, float)):
                return False
            min_val = rule.get("min")
            max_val = rule.get("max")
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False

        elif rule_type == "string":
            if not isinstance(value, str):
                return False
            min_len = rule.get("min_length")
            max_len = rule.get("max_length")
            if min_len is not None and len(value) < min_len:
                return False
            if max_len is not None and len(value) > max_len:
                return False

        elif rule_type == "list":
            if not isinstance(value, list):
                return False
            min_len = rule.get("min_items")
            max_len = rule.get("max_items")
            if min_len is not None and len(value) < min_len:
                return False
            if max_len is not None and len(value) > max_len:
                return False

        elif rule_type == "enum":
            allowed_values = rule.get("values", [])
            if value not in allowed_values:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "required_fields": self.required_fields,
            "optional_fields": self.optional_fields,
            "validation_rules": self.validation_rules,
        }


@dataclass
class CriteriaProfile:
    """Profile containing criteria configuration for a content type"""

    name: str
    content_type: str
    scoring_criteria: dict[str, list[ScoringCriteria]] = field(default_factory=dict)
    template_requirements: dict[str, TemplateRequirement] = field(default_factory=dict)
    performance_thresholds: dict[str, float] = field(default_factory=dict)

    def get_criteria_for_template(self, template_name: str) -> list[ScoringCriteria]:
        """Get scoring criteria for a specific template"""
        return self.scoring_criteria.get(template_name, [])

    def get_requirements_for_template(self, template_name: str) -> TemplateRequirement | None:
        """Get requirements for a specific template"""
        return self.template_requirements.get(template_name)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "content_type": self.content_type,
            "scoring_criteria": {k: [c.__dict__ for c in v] for k, v in self.scoring_criteria.items()},
            "template_requirements": {k: v.to_dict() for k, v in self.template_requirements.items()},
            "performance_thresholds": self.performance_thresholds,
        }


class TemplateCriteriaManager:
    """Manager for template criteria and requirements"""

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.error_handler = ErrorHandler()
        self.logger = TwitterSystemLogger("TemplateCriteriaManager")

        # Criteria profiles
        self.criteria_profiles: dict[str, CriteriaProfile] = {}

        # Load default criteria
        self._load_default_criteria()

    def _load_default_criteria(self) -> None:
        """Load default criteria configurations"""

        # Fundamental analysis criteria
        fundamental_profile = CriteriaProfile(name="fundamental_default", content_type="fundamental")

        # A_valuation template criteria
        fundamental_profile.scoring_criteria["A_valuation"] = [
            ScoringCriteria("valuation_gap", 0.3, 10.0, True),
            ScoringCriteria("valuation_methods", 0.2, 2.0),
            ScoringCriteria("dcf_value", 0.2, 1.0),
            ScoringCriteria("fair_value", 0.3, 1.0, True),
        ]

        fundamental_profile.template_requirements["A_valuation"] = TemplateRequirement(
            name="valuation_template",
            description="Valuation-focused fundamental analysis",
            required_fields=["ticker", "fair_value", "current_price"],
            optional_fields=["dcf_value", "valuation_methods", "moat_strength"],
            validation_rules={
                "fair_value": {"type": "numeric", "min": 0.01},
                "current_price": {"type": "numeric", "min": 0.01},
                "valuation_methods": {"type": "list", "min_items": 1},
            },
        )

        # B_catalyst template criteria
        fundamental_profile.scoring_criteria["B_catalyst"] = [
            ScoringCriteria("catalyst_count", 0.4, 2.0, True),
            ScoringCriteria("catalyst_probability", 0.3, 0.7),
            ScoringCriteria("upcoming_events", 0.3, 1.0),
        ]

        fundamental_profile.template_requirements["B_catalyst"] = TemplateRequirement(
            name="catalyst_template",
            description="Catalyst-focused fundamental analysis",
            required_fields=["ticker", "catalysts"],
            optional_fields=["catalyst_count", "upcoming_events"],
            validation_rules={
                "catalysts": {"type": "list", "min_items": 1},
                "catalyst_count": {"type": "numeric", "min": 1},
            },
        )

        # C_moat template criteria
        fundamental_profile.scoring_criteria["C_moat"] = [
            ScoringCriteria("moat_strength", 0.4, 7.0, True),
            ScoringCriteria("competitive_advantages", 0.3, 2.0),
            ScoringCriteria("market_position", 0.3, 1.0),
        ]

        fundamental_profile.template_requirements["C_moat"] = TemplateRequirement(
            name="moat_template",
            description="Competitive moat analysis",
            required_fields=["ticker", "moat_strength"],
            optional_fields=["competitive_advantages", "market_position"],
            validation_rules={
                "moat_strength": {"type": "numeric", "min": 0, "max": 10},
                "competitive_advantages": {"type": "list", "min_items": 1},
            },
        )

        self.criteria_profiles["fundamental"] = fundamental_profile

        # Strategy analysis criteria
        strategy_profile = CriteriaProfile(name="strategy_default", content_type="strategy")

        strategy_profile.scoring_criteria["default"] = [
            ScoringCriteria("win_rate", 0.3, 0.6),
            ScoringCriteria("net_performance", 0.3, 10.0),
            ScoringCriteria("reward_risk", 0.2, 1.5),
            ScoringCriteria("total_trades", 0.2, 10.0),
        ]

        strategy_profile.template_requirements["default"] = TemplateRequirement(
            name="strategy_template",
            description="Strategy analysis template",
            required_fields=["ticker", "strategy_type"],
            optional_fields=[
                "win_rate",
                "net_performance",
                "reward_risk",
                "total_trades",
            ],
            validation_rules={
                "win_rate": {"type": "numeric", "min": 0.0, "max": 1.0},
                "net_performance": {"type": "numeric"},
                "reward_risk": {"type": "numeric", "min": 0.0},
            },
        )

        self.criteria_profiles["strategy"] = strategy_profile

        # Sector analysis criteria
        sector_profile = CriteriaProfile(name="sector_default", content_type="sector")

        sector_profile.scoring_criteria["rotation"] = [
            ScoringCriteria("rotation_signal", 0.4, 0.5, True),
            ScoringCriteria("rotation_score", 0.3, 0.7),
            ScoringCriteria("relative_performance", 0.3, 5.0),
        ]

        sector_profile.template_requirements["rotation"] = TemplateRequirement(
            name="rotation_template",
            description="Sector rotation analysis",
            required_fields=["sector_name", "rotation_signal"],
            optional_fields=["rotation_score", "relative_performance", "flow_data"],
            validation_rules={
                "rotation_signal": {"type": "enum", "values": [True, False]},
                "rotation_score": {"type": "numeric", "min": 0.0, "max": 1.0},
            },
        )

        sector_profile.scoring_criteria["comparison"] = [
            ScoringCriteria("sector_comparison", 0.3, 0.5, True),
            ScoringCriteria("relative_valuation", 0.3, 0.5),
            ScoringCriteria("performance_ranking", 0.4, 1.0),
        ]

        sector_profile.template_requirements["comparison"] = TemplateRequirement(
            name="comparison_template",
            description="Sector comparison analysis",
            required_fields=["sector_name", "sector_comparison"],
            optional_fields=["relative_valuation", "performance_ranking"],
            validation_rules={
                "sector_comparison": {"type": "enum", "values": [True, False]},
                "relative_valuation": {"type": "numeric", "min": 0.0, "max": 1.0},
            },
        )

        self.criteria_profiles["sector"] = sector_profile

        # Trade history criteria
        trade_history_profile = CriteriaProfile(name="trade_history_default", content_type="trade_history")

        trade_history_profile.scoring_criteria["performance"] = [
            ScoringCriteria("performance_metrics", 0.4, 0.5, True),
            ScoringCriteria("win_rate", 0.3, 0.6),
            ScoringCriteria("transparency_level", 0.3, 0.5),
        ]

        trade_history_profile.template_requirements["performance"] = TemplateRequirement(
            name="performance_template",
            description="Trade performance analysis",
            required_fields=["analysis_name", "performance_metrics"],
            optional_fields=["win_rate", "total_trades", "period_return"],
            validation_rules={
                "performance_metrics": {"type": "enum", "values": [True, False]},
                "win_rate": {"type": "numeric", "min": 0.0, "max": 1.0},
            },
        )

        self.criteria_profiles["trade_history"] = trade_history_profile

    def get_criteria_profile(self, content_type: str) -> CriteriaProfile | None:
        """Get criteria profile for content type"""
        return self.criteria_profiles.get(content_type)

    def get_scoring_criteria(self, content_type: str, template_name: str) -> list[ScoringCriteria]:
        """Get scoring criteria for specific template"""

        profile = self.get_criteria_profile(content_type)
        if not profile:
            return []

        return profile.get_criteria_for_template(template_name)

    def get_template_requirements(self, content_type: str, template_name: str) -> TemplateRequirement | None:
        """Get template requirements"""

        profile = self.get_criteria_profile(content_type)
        if not profile:
            return None

        return profile.get_requirements_for_template(template_name)

    def validate_template_data(self, content_type: str, template_name: str, data: dict[str, Any]) -> list[str]:
        """Validate data against template requirements"""

        requirements = self.get_template_requirements(content_type, template_name)
        if not requirements:
            return []

        try:
            return requirements.validate_data(data)
        except Exception as e:
            self.error_handler.handle_processing_error(
                "template_validation",
                {"content_type": content_type, "template_name": template_name},
                e,
            )
            return [f"Validation error: {str(e)}"]

    def update_scoring_criteria(self, content_type: str, template_name: str, criteria: list[ScoringCriteria]) -> None:
        """Update scoring criteria for template"""

        profile = self.get_criteria_profile(content_type)
        if not profile:
            raise ValidationError(f"No criteria profile found for content type: {content_type}")

        profile.scoring_criteria[template_name] = criteria

        self.logger.log_operation(
            f"Updated scoring criteria for {content_type}/{template_name}",
            {"criteria_count": len(criteria)},
        )

    def update_template_requirements(
        self, content_type: str, template_name: str, requirements: TemplateRequirement
    ) -> None:
        """Update template requirements"""

        profile = self.get_criteria_profile(content_type)
        if not profile:
            raise ValidationError(f"No criteria profile found for content type: {content_type}")

        profile.template_requirements[template_name] = requirements

        self.logger.log_operation(
            f"Updated template requirements for {content_type}/{template_name}",
            {"required_fields": len(requirements.required_fields)},
        )

    def add_criteria_profile(self, profile: CriteriaProfile) -> None:
        """Add new criteria profile"""

        if profile.content_type in self.criteria_profiles:
            self.logger.log_operation(
                f"Replacing existing criteria profile for {profile.content_type}",
                {"old_profile": self.criteria_profiles[profile.content_type].name},
            )

        self.criteria_profiles[profile.content_type] = profile

        self.logger.log_operation(
            f"Added criteria profile: {profile.name}",
            {"content_type": profile.content_type},
        )

    def export_criteria_configuration(self, output_path: Path) -> None:
        """Export criteria configuration to file"""

        config_data = {
            "profiles": {content_type: profile.to_dict() for content_type, profile in self.criteria_profiles.items()},
            "export_timestamp": (
                self.logger.logger.handlers[0].formatter.formatTime(None, None)
                if self.logger.logger.handlers
                else "unknown"
            ),
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            self.logger.log_operation(
                f"Exported criteria configuration to {output_path}",
                {"profile_count": len(self.criteria_profiles)},
            )

        except Exception as e:
            self.error_handler.handle_processing_error("criteria_export", {"output_path": str(output_path)}, e)

    def import_criteria_configuration(self, config_path: Path) -> None:
        """Import criteria configuration from file"""

        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            profiles_data = config_data.get("profiles", {})

            for content_type, profile_data in profiles_data.items():
                # Reconstruct criteria profile
                profile = CriteriaProfile(name=profile_data["name"], content_type=profile_data["content_type"])

                # Reconstruct scoring criteria
                for template_name, criteria_data in profile_data.get("scoring_criteria", {}).items():
                    criteria = [
                        ScoringCriteria(
                            name=c["name"],
                            weight=c["weight"],
                            threshold=c.get("threshold", 0.0),
                            required=c.get("required", False),
                        )
                        for c in criteria_data
                    ]
                    profile.scoring_criteria[template_name] = criteria

                # Reconstruct template requirements
                for template_name, req_data in profile_data.get("template_requirements", {}).items():
                    requirement = TemplateRequirement(
                        name=req_data["name"],
                        description=req_data["description"],
                        required_fields=req_data.get("required_fields", []),
                        optional_fields=req_data.get("optional_fields", []),
                        validation_rules=req_data.get("validation_rules", {}),
                    )
                    profile.template_requirements[template_name] = requirement

                profile.performance_thresholds = profile_data.get("performance_thresholds", {})

                self.criteria_profiles[content_type] = profile

            self.logger.log_operation(
                f"Imported criteria configuration from {config_path}",
                {"profile_count": len(profiles_data)},
            )

        except Exception as e:
            self.error_handler.handle_processing_error("criteria_import", {"config_path": str(config_path)}, e)

    def get_available_templates(self, content_type: str) -> list[str]:
        """Get list of available templates for content type"""

        profile = self.get_criteria_profile(content_type)
        if not profile:
            return []

        # Get templates from both criteria and requirements
        templates = set()
        templates.update(profile.scoring_criteria.keys())
        templates.update(profile.template_requirements.keys())

        return sorted(list(templates))

    def get_criteria_statistics(self) -> dict[str, Any]:
        """Get statistics about criteria configuration"""

        stats = {
            "total_profiles": len(self.criteria_profiles),
            "content_types": list(self.criteria_profiles.keys()),
            "total_templates": 0,
            "templates_by_type": {},
        }

        for content_type, profile in self.criteria_profiles.items():
            templates = self.get_available_templates(content_type)
            stats["templates_by_type"][content_type] = len(templates)
            stats["total_templates"] += len(templates)

        return stats
