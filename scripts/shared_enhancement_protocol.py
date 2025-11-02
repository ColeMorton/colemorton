#!/usr/bin/env python3
"""
Shared Enhancement Protocol

Unified enhancement system for all Twitter commands:
- Standardized validation-driven enhancement
- Common enhancement patterns and workflows
- Consistent quality improvement methodologies
- Shared enhancement templates and logic
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from twitter_template_renderer import TwitterTemplateRenderer
from twitter_template_selector import TwitterTemplateSelector


class SharedEnhancementProtocol:
    """Unified enhancement protocol for all Twitter content types"""

    def __init__(self, base_path: Path | None = None):
        """Initialize the enhancement protocol"""
        self.base_path = base_path or Path(__file__).parent.parent
        self.data_outputs_path = self.base_path / "data" / "outputs"

        # Initialize components
        self.template_renderer = TwitterTemplateRenderer()
        self.template_selector = TwitterTemplateSelector()

        # Enhancement patterns
        self.enhancement_patterns = {
            "data_authority_resolution": {
                "fundamental": self._resolve_fundamental_authority,
                "strategy": self._resolve_strategy_authority,
                "sector": self._resolve_sector_authority,
                "trade_history": self._resolve_trade_history_authority,
            },
            "validation_issue_fixing": {
                "accuracy": self._fix_accuracy_issues,
                "compliance": self._fix_compliance_issues,
                "engagement": self._fix_engagement_issues,
                "formatting": self._fix_formatting_issues,
            },
            "quality_improvements": {
                "disclaimer_enhancement": self._enhance_disclaimers,
                "data_attribution": self._enhance_data_attribution,
                "confidence_scoring": self._enhance_confidence_scoring,
                "professional_standards": self._enhance_professional_standards,
            },
        }

    def detect_enhancement_request(self, input_param: str) -> tuple[bool, dict[str, Any]]:
        """
        Detect if input is a validation file path for enhancement

        Args:
            input_param: Input parameter from command

        Returns:
            Tuple of (is_enhancement_request, enhancement_context)
        """

        # Check if input looks like a validation file path
        validation_patterns = [
            r".*validation.*\.json$",
            r".*outputs.*validation.*",
            r".*twitter.*validation.*",
        ]

        is_validation_path = any(re.match(pattern, input_param) for pattern in validation_patterns)

        if is_validation_path:
            try:
                # Parse validation file path
                content_type, identifier, date = self._parse_validation_path(input_param)

                return True, {
                    "validation_file_path": input_param,
                    "content_type": content_type,
                    "identifier": identifier,
                    "date": date,
                    "enhancement_type": "validation_driven",
                }
            except Exception as e:
                return False, {"error": f"Failed to parse validation path: {e}"}

        return False, {}

    def execute_enhancement(self, enhancement_context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute validation-driven enhancement

        Args:
            enhancement_context: Enhancement context from detection

        Returns:
            Enhancement result
        """

        try:
            # Load validation data
            validation_data = self._load_validation_data(enhancement_context["validation_file_path"])

            # Load original content
            original_content = self._load_original_content(
                enhancement_context["content_type"],
                enhancement_context["identifier"],
                enhancement_context["date"],
            )

            # Load original source data
            original_source_data = self._load_original_source_data(
                enhancement_context["content_type"],
                enhancement_context["identifier"],
                enhancement_context["date"],
            )

            # Apply data authority resolution
            enhanced_source_data = self._apply_data_authority_resolution(
                original_source_data,
                validation_data,
                enhancement_context["content_type"],
            )

            # Apply validation-driven fixes
            enhancement_plan = self._create_enhancement_plan(validation_data, enhancement_context["content_type"])

            # Re-render content with enhanced data
            enhanced_result = self._re_render_with_enhancements(
                enhancement_context["content_type"],
                enhancement_context["identifier"],
                enhanced_source_data,
                enhancement_plan,
            )

            # Apply post-render improvements
            final_result = self._apply_post_render_improvements(enhanced_result, enhancement_plan, validation_data)

            return {
                "success": True,
                "enhanced_content": final_result["content"],
                "enhancement_metadata": {
                    "original_issues": len(
                        validation_data.get("critical_findings_matrix", {}).get("inaccurate_statements", [])
                    ),
                    "enhancements_applied": len(enhancement_plan.get("improvements", [])),
                    "data_authority_resolved": enhancement_plan.get("data_authority_applied", False),
                    "validation_issues_fixed": enhancement_plan.get("validation_fixes_applied", 0),
                    "enhancement_timestamp": datetime.now().isoformat(),
                },
                "validation_data": validation_data,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enhancement_context": enhancement_context,
            }

    def _parse_validation_path(self, validation_file_path: str) -> tuple[str, str, str]:
        """Parse validation file path to extract content type, identifier, and date"""

        path = Path(validation_file_path)

        # Determine content type from path
        content_type_mapping = {
            "fundamental_analysis": "fundamental",
            "post_strategy": "strategy",
            "sector_analysis": "sector",
            "trade_history": "trade_history",
        }

        content_type = None
        for path_key, type_key in content_type_mapping.items():
            if path_key in str(path):
                content_type = type_key
                break

        if not content_type:
            raise ValueError(f"Cannot determine content type from path: {validation_file_path}")

        # Extract identifier and date from filename
        filename = path.stem
        if filename.endswith("_validation"):
            filename = filename[:-11]  # Remove "_validation" suffix

        # Parse based on content type
        if content_type in ["fundamental", "strategy"]:
            # Format: TICKER_YYYYMMDD
            if "_" not in filename:
                raise ValueError(f"Invalid filename format: {filename}")
            parts = filename.split("_")
            if len(parts) != 2:
                raise ValueError(f"Invalid filename format: {filename}")
            identifier, date = parts
        elif content_type == "sector":
            # Format: SECTOR_YYYYMMDD
            if "_" not in filename:
                raise ValueError(f"Invalid filename format: {filename}")
            parts = filename.split("_")
            if len(parts) != 2:
                raise ValueError(f"Invalid filename format: {filename}")
            identifier, date = parts
        else:  # trade_history
            # Format: ANALYSIS_NAME_YYYYMMDD
            if "_" not in filename:
                raise ValueError(f"Invalid filename format: {filename}")
            parts = filename.split("_")
            if len(parts) < 2:
                raise ValueError(f"Invalid filename format: {filename}")
            date = parts[-1]
            identifier = "_".join(parts[:-1])

        return content_type, identifier, date

    def _load_validation_data(self, validation_file_path: str) -> dict[str, Any]:
        """Load validation data from JSON file"""

        path = Path(validation_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Validation file not found: {validation_file_path}")

        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _load_original_content(self, content_type: str, identifier: str, date: str) -> dict[str, Any]:
        """Load original Twitter content"""

        # Map content type to directory
        dir_mapping = {
            "fundamental": "fundamental_analysis",
            "strategy": "post_strategy",
            "sector": "sector_analysis",
            "trade_history": "trade_history",
        }

        content_dir = dir_mapping.get(content_type, content_type)
        content_path = self.data_outputs_path / "twitter" / content_dir / f"{identifier}_{date}.md"

        if not content_path.exists():
            raise FileNotFoundError(f"Original content not found: {content_path}")

        content = content_path.read_text(encoding="utf-8")

        # Load metadata if available
        metadata_path = content_path.with_suffix("").with_suffix("_metadata.json")
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)

        return {
            "content": content,
            "metadata": metadata,
            "file_path": str(content_path),
        }

    def _load_original_source_data(self, content_type: str, identifier: str, date: str) -> dict[str, Any]:
        """Load original source data that was used to generate the content"""

        # Map content type to source directory
        source_mapping = {
            "fundamental": "fundamental_analysis",
            "strategy": "analysis_strategy",  # CSV files
            "sector": "sector_analysis",
            "trade_history": "trade_history",
        }

        source_dir = source_mapping.get(content_type, content_type)

        if content_type == "strategy":
            # Strategy uses CSV files
            source_path = self.base_path / "data" / "raw" / source_dir / f"{identifier}_{date}.csv"
        else:
            # Others use markdown files
            source_path = self.data_outputs_path / source_dir / f"{identifier}_{date}.md"

        if not source_path.exists():
            # Return minimal data structure
            return {
                "identifier": identifier,
                "date": date,
                "content_type": content_type,
                "source_available": False,
            }

        if content_type == "strategy":
            # Parse CSV data (simplified)
            return {
                "identifier": identifier,
                "date": date,
                "content_type": content_type,
                "source_available": True,
                "csv_path": str(source_path),
            }
        # Parse markdown with frontmatter
        content = source_path.read_text(encoding="utf-8")
        data = self._parse_markdown_with_frontmatter(content)
        data.update(
            {
                "identifier": identifier,
                "date": date,
                "content_type": content_type,
                "source_available": True,
            }
        )
        return data

    def _parse_markdown_with_frontmatter(self, content: str) -> dict[str, Any]:
        """Parse markdown content with YAML frontmatter"""

        data = {}

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml

                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        data.update(frontmatter)
                    data["markdown_content"] = parts[2].strip()
                except Exception:
                    data["markdown_content"] = content
            else:
                data["markdown_content"] = content
        else:
            data["markdown_content"] = content

        return data

    def _apply_data_authority_resolution(
        self,
        source_data: dict[str, Any],
        validation_data: dict[str, Any],
        content_type: str,
    ) -> dict[str, Any]:
        """Apply data authority resolution based on content type"""

        if content_type in self.enhancement_patterns["data_authority_resolution"]:
            resolver = self.enhancement_patterns["data_authority_resolution"][content_type]
            return resolver(source_data, validation_data)

        return source_data

    def _resolve_fundamental_authority(
        self, source_data: dict[str, Any], validation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve fundamental analysis data authority conflicts"""

        # Apply fundamental analysis authority protocol
        enhanced_data = source_data.copy()

        # Check for data conflicts in validation
        data_conflicts = validation_data.get("critical_findings_matrix", {}).get("questionable_assertions", [])

        for conflict in data_conflicts:
            if "price" in conflict.lower() or "valuation" in conflict.lower():
                # Use real-time price data authority
                enhanced_data["price_authority_applied"] = True

            if "confidence" in conflict.lower():
                # Enhance confidence scoring
                enhanced_data["confidence_enhanced"] = True

        return enhanced_data

    def _resolve_strategy_authority(
        self, source_data: dict[str, Any], validation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve strategy data authority conflicts"""

        enhanced_data = source_data.copy()

        # Apply TrendSpider authority protocol
        data_conflicts = validation_data.get("critical_findings_matrix", {}).get("questionable_assertions", [])

        for conflict in data_conflicts:
            if "performance" in conflict.lower() or "metrics" in conflict.lower():
                # Use TrendSpider as authoritative source
                enhanced_data["trendspider_authority_applied"] = True

        return enhanced_data

    def _resolve_sector_authority(self, source_data: dict[str, Any], validation_data: dict[str, Any]) -> dict[str, Any]:
        """Resolve sector analysis data authority conflicts"""

        enhanced_data = source_data.copy()

        # Apply sector analysis authority protocol
        data_conflicts = validation_data.get("critical_findings_matrix", {}).get("questionable_assertions", [])

        for conflict in data_conflicts:
            if "etf" in conflict.lower() or "pricing" in conflict.lower():
                # Use sector ETF data as authoritative
                enhanced_data["sector_etf_authority_applied"] = True

        return enhanced_data

    def _resolve_trade_history_authority(
        self, source_data: dict[str, Any], validation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve trade history data authority conflicts"""

        enhanced_data = source_data.copy()

        # Apply trade history authority protocol
        data_conflicts = validation_data.get("critical_findings_matrix", {}).get("questionable_assertions", [])

        for conflict in data_conflicts:
            if "performance" in conflict.lower() or "return" in conflict.lower():
                # Use trade history analysis as authoritative
                enhanced_data["trade_history_authority_applied"] = True

        return enhanced_data

    def _create_enhancement_plan(self, validation_data: dict[str, Any], content_type: str) -> dict[str, Any]:
        """Create enhancement plan based on validation data"""

        plan = {
            "improvements": [],
            "data_authority_applied": False,
            "validation_fixes_applied": 0,
        }

        # Extract issues from validation data
        overall_assessment = validation_data.get("overall_assessment", {})
        validation_breakdown = validation_data.get("validation_breakdown", {})
        recommendations = validation_data.get("actionable_recommendations", {})

        # Add improvements based on validation issues
        if overall_assessment.get("compliance_status") != "COMPLIANT":
            plan["improvements"].append("compliance_enhancement")

        if overall_assessment.get("engagement_potential_score", 0) < 9.0:
            plan["improvements"].append("engagement_optimization")

        # Add specific improvements from recommendations
        required_corrections = recommendations.get("required_corrections", {})

        for priority, corrections in required_corrections.items():
            for correction in corrections:
                plan["improvements"].append(f"{priority}_{correction}")
                plan["validation_fixes_applied"] += 1

        # Check for data authority requirements
        critical_findings = validation_data.get("critical_findings_matrix", {})
        if critical_findings.get("questionable_assertions") or critical_findings.get("inaccurate_statements"):
            plan["data_authority_applied"] = True

        return plan

    def _re_render_with_enhancements(
        self,
        content_type: str,
        identifier: str,
        enhanced_source_data: dict[str, Any],
        enhancement_plan: dict[str, Any],
    ) -> dict[str, Any]:
        """Re-render content with enhanced data"""

        # Use template renderer to regenerate content
        if content_type == "fundamental":
            result = self.template_renderer.render_fundamental_analysis(identifier, enhanced_source_data)
        elif content_type == "strategy":
            result = self.template_renderer.render_strategy_post(identifier, enhanced_source_data)
        elif content_type == "sector":
            result = self.template_renderer.render_sector_analysis(identifier, enhanced_source_data)
        elif content_type == "trade_history":
            result = self.template_renderer.render_trade_history(identifier, enhanced_source_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")

        # Add enhancement metadata
        result["metadata"]["enhancement_applied"] = True
        result["metadata"]["enhancement_plan"] = enhancement_plan

        return result

    def _apply_post_render_improvements(
        self,
        rendered_result: dict[str, Any],
        enhancement_plan: dict[str, Any],
        validation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply post-render improvements"""

        content = rendered_result["content"]

        # Apply improvements based on plan
        for improvement in enhancement_plan.get("improvements", []):
            if improvement == "compliance_enhancement":
                content = self._enhance_compliance(content)
            elif improvement == "engagement_optimization":
                content = self._enhance_engagement(content)
            elif improvement.startswith("high_"):
                content = self._apply_high_priority_fix(content, improvement)

        return {"content": content, "metadata": rendered_result["metadata"]}

    def _enhance_compliance(self, content: str) -> str:
        """Enhance compliance aspects of content"""

        # Ensure disclaimer is present and prominent
        if "Not financial advice" not in content:
            content += "\n\n⚠️ Not financial advice. Do your own research."

        # Enhance risk warnings
        if "risk" not in content.lower():
            content = content.replace(
                "⚠️ Not financial advice",
                "⚠️ Not financial advice. Investments carry risk of loss",
            )

        return content

    def _enhance_engagement(self, content: str) -> str:
        """Enhance engagement aspects of content"""

        # Ensure emoji presence
        if not re.search(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            content,
        ):
            # Add relevant emoji to first line
            lines = content.split("\n")
            if lines:
                lines[0] = "🚨 " + lines[0]
                content = "\n".join(lines)

        return content

    def _apply_high_priority_fix(self, content: str, improvement: str) -> str:
        """Apply high priority fixes"""

        # Remove bold formatting if present
        if "**" in content:
            content = content.replace("**", "")

        # Ensure character limits
        lines = content.split("\n")
        if lines and len(lines[0]) > 280:
            lines[0] = lines[0][:277] + "..."
            content = "\n".join(lines)

        return content

    def get_enhancement_statistics(self) -> dict[str, Any]:
        """Get enhancement system statistics"""

        return {
            "available_patterns": list(self.enhancement_patterns.keys()),
            "content_types_supported": [
                "fundamental",
                "strategy",
                "sector",
                "trade_history",
            ],
            "enhancement_capabilities": [
                "data_authority_resolution",
                "validation_issue_fixing",
                "compliance_enhancement",
                "engagement_optimization",
                "quality_improvements",
            ],
        }
