#!/usr/bin/env python3
"""
Twitter Template Renderer

Unified template rendering system for all Twitter content types:
- Standardized Jinja2 environment setup
- Template selection algorithms
- Data validation and mapping
- Content quality assurance
- Output formatting and export
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.cli_base import ServiceError, ValidationError


class TwitterTemplateRenderer:
    """Unified Twitter template rendering system"""

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the template renderer"""
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.twitter_templates_dir = self.templates_dir / "twitter"

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Template mappings
        self.template_mappings = {
            "fundamental": {
                "A_valuation": "twitter/fundamental/twitter_fundamental_A_valuation.j2",
                "B_catalyst": "twitter/fundamental/twitter_fundamental_B_catalyst.j2",
                "C_moat": "twitter/fundamental/twitter_fundamental_C_moat.j2",
                "D_contrarian": "twitter/fundamental/twitter_fundamental_D_contrarian.j2",
                "E_financial": "twitter/fundamental/twitter_fundamental_E_financial.j2",
            },
            "strategy": {
                "default": "twitter/strategy/twitter_post_strategy.j2",
                "strategy": "twitter/strategy/twitter_strategy_default.j2",
            },
            "sector": {
                "comparison": "twitter/sector/cross_sector_comparison.j2",
                "rotation": "twitter/sector/rotation_analysis.j2",
            },
            "trade_history": {"performance": "twitter/trade_history/performance_update.j2"},
        }

    def render_content(
        self,
        content_type: str,
        ticker: str,
        data: dict[str, Any],
        template_variant: str | None = None,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        """
        Render Twitter content using the unified template system

        Args:
            content_type: Type of content (fundamental, strategy, sector, trade_history)
            ticker: Stock ticker symbol
            data: Data context for template rendering
            template_variant: Specific template variant to use
            timestamp: ISO timestamp for the content

        Returns:
            Dict containing rendered content and metadata
        """
        try:
            # Generate timestamp if not provided
            if not timestamp:
                timestamp = datetime.now().isoformat()

            # Select optimal template
            template_path = self._select_template(content_type, data, template_variant)
            template = self._get_template(template_path)

            # Prepare rendering context
            context = self._prepare_context(content_type, ticker, data, timestamp)

            # Validate data completeness
            validation_result = self._validate_data_completeness(content_type, data)

            # Render content
            rendered_content = template.render(**context)

            # Post-render validation
            content_validation = self._validate_rendered_content(rendered_content, content_type, template_variant)

            return {
                "content": rendered_content.strip(),
                "metadata": {
                    "content_type": content_type,
                    "ticker": ticker,
                    "template_path": template_path,
                    "template_variant": template_variant,
                    "character_count": len(rendered_content),
                    "timestamp": timestamp,
                    "data_validation": validation_result,
                    "content_validation": content_validation,
                    "institutional_compliant": content_validation.get("compliant", False),
                },
            }

        except Exception as e:
            raise ServiceError(f"Failed to render Twitter content: {e}")

    def _select_template(
        self,
        content_type: str,
        data: dict[str, Any],
        template_variant: str | None = None,
    ) -> str:
        """Select optimal template based on content type and data characteristics"""

        if template_variant:
            # Use explicit template variant if provided
            if content_type in self.template_mappings:
                if template_variant in self.template_mappings[content_type]:
                    return self.template_mappings[content_type][template_variant]
            raise ValidationError(f"Template variant '{template_variant}' not found for content type '{content_type}'")

        # Intelligent template selection based on data content
        if content_type == "fundamental":
            return self._select_fundamental_template(data)
        if content_type == "strategy":
            return self.template_mappings["strategy"]["default"]
        if content_type == "sector":
            return self._select_sector_template(data)
        if content_type == "trade_history":
            return self.template_mappings["trade_history"]["performance"]
        raise ValidationError(f"Unknown content type: {content_type}")

    def _select_fundamental_template(self, data: dict[str, Any]) -> str:
        """Select fundamental analysis template based on data characteristics"""

        # Template A: Valuation Disconnect
        if self._has_valuation_data(data):
            return self.template_mappings["fundamental"]["A_valuation"]

        # Template B: Catalyst Focus
        if self._has_catalyst_data(data):
            return self.template_mappings["fundamental"]["B_catalyst"]

        # Template C: Moat Analysis
        if self._has_moat_data(data):
            return self.template_mappings["fundamental"]["C_moat"]

        # Template D: Contrarian Take
        if self._has_contrarian_data(data):
            return self.template_mappings["fundamental"]["D_contrarian"]

        # Template E: Financial Health (default)
        return self.template_mappings["fundamental"]["E_financial"]

    def _select_sector_template(self, data: dict[str, Any]) -> str:
        """Select sector analysis template based on data characteristics"""

        # Check for rotation signals
        if data.get("rotation_signal") or data.get("sector_rotation"):
            return self.template_mappings["sector"]["rotation"]

        # Default to comparison template
        return self.template_mappings["sector"]["comparison"]

    def _has_valuation_data(self, data: dict[str, Any]) -> bool:
        """Check if data contains valuation-focused content"""
        valuation_indicators = [
            "fair_value",
            "fair_value_low",
            "fair_value_high",
            "dcf_value",
            "valuation_methods",
            "current_price",
            "weighted_fair_value",
        ]
        return any(data.get(indicator) for indicator in valuation_indicators)

    def _has_catalyst_data(self, data: dict[str, Any]) -> bool:
        """Check if data contains catalyst-focused content"""
        catalyst_indicators = [
            "catalysts",
            "catalyst_1",
            "upcoming_events",
            "timeline_detail",
            "catalyst_count",
            "total_catalyst_impact",
        ]
        return any(data.get(indicator) for indicator in catalyst_indicators)

    def _has_moat_data(self, data: dict[str, Any]) -> bool:
        """Check if data contains moat/competitive advantage content"""
        moat_indicators = [
            "moat_advantages",
            "competitive_advantages",
            "moat_strength",
            "market_share",
            "pricing_power",
            "competitive_position",
        ]
        return any(data.get(indicator) for indicator in moat_indicators)

    def _has_contrarian_data(self, data: dict[str, Any]) -> bool:
        """Check if data contains contrarian analysis content"""
        contrarian_indicators = [
            "contrarian_insight",
            "common_perception",
            "market_misconception",
            "mispricing",
            "contrarian_evidence",
        ]
        return any(data.get(indicator) for indicator in contrarian_indicators)

    def _prepare_context(self, content_type: str, ticker: str, data: dict[str, Any], timestamp: str) -> dict[str, Any]:
        """Prepare the rendering context for templates"""

        context = {
            "ticker": ticker,
            "timestamp": timestamp,
            "data": data,
            "content_type": content_type,
            # Add template-specific context variables
            "blog_content_type": self._get_blog_content_type(content_type),
            "disclaimer_type": self._get_disclaimer_type(content_type),
            "additional_hashtags": self._get_additional_hashtags(content_type, data),
        }

        return context

    def _get_blog_content_type(self, content_type: str) -> str:
        """Get blog content type for URL generation"""
        mapping = {
            "fundamental": "fundamental-analysis",
            "strategy": "trading-strategy",
            "sector": "sector-analysis",
            "trade_history": "trading-performance",
        }
        return mapping.get(content_type, "analysis")

    def _get_disclaimer_type(self, content_type: str) -> str:
        """Get disclaimer type for content"""
        mapping = {
            "fundamental": "fundamental",
            "strategy": "strategy",
            "sector": "sector",
            "trade_history": "trade_history",
        }
        return mapping.get(content_type, "default")

    def _get_additional_hashtags(self, content_type: str, data: dict[str, Any]) -> list[str]:
        """Get additional hashtags based on content type and data"""
        hashtags = []

        if content_type == "fundamental":
            if data.get("value_opportunity"):
                hashtags.append("#ValueInvesting")
            if data.get("growth_potential"):
                hashtags.append("#GrowthStocks")
        elif content_type == "strategy":
            if data.get("live_signal"):
                hashtags.append("#LiveSignal")
            if data.get("high_probability"):
                hashtags.append("#HighProbability")
        elif content_type == "sector":
            if data.get("rotation_signal"):
                hashtags.append("#MarketRotation")
        elif content_type == "trade_history":
            if data.get("transparency"):
                hashtags.append("#TradingTransparency")

        return hashtags

    def _validate_data_completeness(self, content_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Validate data completeness for content type"""

        required_fields = {
            "fundamental": ["ticker", "current_price"],
            "strategy": ["ticker", "strategy_type", "win_rate", "net_performance"],
            "sector": ["sector_name", "allocation_recommendation"],
            "trade_history": ["period_return", "win_rate", "total_trades"],
        }

        missing_fields = []
        content_required = required_fields.get(content_type, [])

        for field in content_required:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        completeness_score = 1.0 - (len(missing_fields) / max(len(content_required), 1))

        return {
            "completeness_score": completeness_score,
            "missing_fields": missing_fields,
            "required_fields": content_required,
            "data_quality": (
                "excellent"
                if completeness_score >= 0.9
                else ("good" if completeness_score >= 0.7 else "fair" if completeness_score >= 0.5 else "poor")
            ),
        }

    def _validate_rendered_content(
        self, content: str, content_type: str, template_variant: str | None
    ) -> dict[str, Any]:
        """Validate rendered content meets quality standards"""

        issues = []
        compliant = True

        # Character count validation
        char_count = len(content)
        if char_count > 4000:  # Maximum for threaded content
            issues.append(f"Content too long: {char_count} characters")
            compliant = False

        # Hook validation (first 280 characters)
        lines = content.split("\n")
        if lines:
            hook_length = len(lines[0])
            if hook_length > 280:
                issues.append(f"Hook exceeds Twitter limit: {hook_length} characters")
                compliant = False

        # Required elements validation
        required_elements = {
            "ticker": r"\$[A-Z]{1,5}",
            "disclaimer": r"Not financial advice",
            "blog_link": r"https://www\.colemorton\.com/blog/",
            "hashtags": r"#[A-Za-z]+",
        }

        for element, pattern in required_elements.items():
            if not re.search(pattern, content):
                issues.append(f"Missing required element: {element}")
                compliant = False

        # NO BOLD FORMATTING validation
        if "**" in content:
            issues.append("Content contains bold formatting (violates institutional standards)")
            compliant = False

        # Template-specific validation
        if content_type == "fundamental":
            if template_variant == "A_valuation":
                if not re.search(r"fair value", content, re.IGNORECASE):
                    issues.append("Valuation template should include fair value")
                    compliant = False

        return {
            "compliant": compliant,
            "issues": issues,
            "character_count": char_count,
            "hook_length": len(lines[0]) if lines else 0,
            "validation_timestamp": datetime.now().isoformat(),
        }

    def _get_template(self, template_path: str) -> Template:
        """Get Jinja2 template with error handling"""
        try:
            return self.jinja_env.get_template(template_path)
        except TemplateNotFound:
            raise ServiceError(f"Template not found: {template_path}")
        except Exception as e:
            raise ServiceError(f"Failed to load template {template_path}: {e}")

    def render_fundamental_analysis(
        self, ticker: str, data: dict[str, Any], template_variant: str | None = None
    ) -> dict[str, Any]:
        """Render fundamental analysis Twitter content"""
        return self.render_content("fundamental", ticker, data, template_variant)

    def render_strategy_post(
        self, ticker: str, data: dict[str, Any], template_variant: str | None = None
    ) -> dict[str, Any]:
        """Render strategy Twitter content"""
        return self.render_content("strategy", ticker, data, template_variant)

    def render_sector_analysis(
        self, sector: str, data: dict[str, Any], template_variant: str | None = None
    ) -> dict[str, Any]:
        """Render sector analysis Twitter content"""
        return self.render_content("sector", sector, data, template_variant)

    def render_trade_history(
        self,
        identifier: str,
        data: dict[str, Any],
        template_variant: str | None = None,
    ) -> dict[str, Any]:
        """Render trade history Twitter content"""
        return self.render_content("trade_history", identifier, data, template_variant)

    def get_available_templates(self) -> dict[str, list[str]]:
        """Get list of available templates by content type"""
        return {content_type: list(templates.keys()) for content_type, templates in self.template_mappings.items()}

    def validate_template_exists(self, content_type: str, template_variant: str) -> bool:
        """Validate that a template exists"""
        if content_type not in self.template_mappings:
            return False
        if template_variant not in self.template_mappings[content_type]:
            return False

        template_path = self.template_mappings[content_type][template_variant]
        template_file = self.templates_dir / template_path
        return template_file.exists()
