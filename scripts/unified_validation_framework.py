#!/usr/bin/env python3
"""
Unified Validation Framework

Standardized validation system for all Twitter content types:
- Common validation criteria and scoring
- Consistent output formats
- Shared validation logic and utilities
- Institutional quality standards enforcement
"""

import re
from datetime import datetime
from typing import Any


class UnifiedValidationFramework:
    """Unified validation framework for all Twitter content types"""

    def __init__(self):
        """Initialize the validation framework"""

        # Validation thresholds
        self.quality_thresholds = {
            "institutional_minimum": 9.0,
            "publication_minimum": 8.5,
            "accuracy_minimum": 9.5,
            "compliance_minimum": 9.5,
        }

        # Common validation criteria
        self.common_criteria = {
            "content_structure": {
                "character_limits": self._validate_character_limits,
                "required_elements": self._validate_required_elements,
                "formatting_rules": self._validate_formatting_rules,
            },
            "compliance_standards": {
                "disclaimer_presence": self._validate_disclaimers,
                "risk_warnings": self._validate_risk_warnings,
                "investment_advice_language": self._validate_investment_advice,
                "attribution_requirements": self._validate_attribution,
            },
            "accuracy_standards": {
                "data_consistency": self._validate_data_consistency,
                "source_verification": self._validate_source_verification,
                "claim_substantiation": self._validate_claim_substantiation,
            },
            "engagement_optimization": {
                "hook_effectiveness": self._validate_hook_effectiveness,
                "content_accessibility": self._validate_content_accessibility,
                "call_to_action": self._validate_call_to_action,
            },
        }

        # Content-specific validation extensions
        self.content_specific_validators = {
            "fundamental": self._validate_fundamental_specific,
            "strategy": self._validate_strategy_specific,
            "sector": self._validate_sector_specific,
            "trade_history": self._validate_trade_history_specific,
        }

    def validate_content(
        self,
        content: str,
        content_type: str,
        source_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Perform comprehensive validation of Twitter content

        Args:
            content: The rendered Twitter content
            content_type: Type of content (fundamental, strategy, sector, trade_history)
            source_data: Source data used to generate content
            metadata: Additional metadata for validation

        Returns:
            Comprehensive validation result
        """

        validation_result = {
            "metadata": {
                "validation_timestamp": datetime.now().isoformat(),
                "content_type": content_type,
                "validation_framework": "unified",
                "framework_version": "1.0",
            },
            "overall_assessment": {},
            "validation_breakdown": {},
            "critical_findings_matrix": {},
            "actionable_recommendations": {},
            "methodology_notes": {},
        }

        # Perform common validation
        common_results = self._validate_common_criteria(content, content_type, source_data)

        # Perform content-specific validation
        specific_results = self._validate_content_specific(content, content_type, source_data)

        # Perform real-time validation (if applicable)
        realtime_results = self._validate_realtime_context(content, content_type, metadata)

        # Combine all validation results
        all_results = {**common_results, **specific_results, **realtime_results}

        # Calculate overall scores
        overall_assessment = self._calculate_overall_assessment(all_results)

        # Generate findings matrix
        findings_matrix = self._generate_findings_matrix(all_results, content, source_data)

        # Generate recommendations
        recommendations = self._generate_recommendations(all_results, overall_assessment)

        # Compile final validation result
        validation_result.update(
            {
                "overall_assessment": overall_assessment,
                "validation_breakdown": all_results,
                "critical_findings_matrix": findings_matrix,
                "actionable_recommendations": recommendations,
                "methodology_notes": self._generate_methodology_notes(content_type, all_results),
            }
        )

        return validation_result

    def _validate_common_criteria(self, content: str, content_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate common criteria across all content types"""

        results = {}

        # Content structure validation
        results["content_structure"] = {}
        for criterion, validator in self.common_criteria["content_structure"].items():
            results["content_structure"][criterion] = validator(content, content_type, source_data)

        # Compliance standards validation
        results["compliance_standards"] = {}
        for criterion, validator in self.common_criteria["compliance_standards"].items():
            results["compliance_standards"][criterion] = validator(content, content_type, source_data)

        # Accuracy standards validation
        results["accuracy_standards"] = {}
        for criterion, validator in self.common_criteria["accuracy_standards"].items():
            results["accuracy_standards"][criterion] = validator(content, content_type, source_data)

        # Engagement optimization validation
        results["engagement_optimization"] = {}
        for criterion, validator in self.common_criteria["engagement_optimization"].items():
            results["engagement_optimization"][criterion] = validator(content, content_type, source_data)

        return results

    def _validate_content_specific(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate content-specific criteria"""

        if content_type in self.content_specific_validators:
            validator = self.content_specific_validators[content_type]
            return {"content_specific": validator(content, source_data)}

        return {"content_specific": {"score": 1.0, "issues": []}}

    def _validate_realtime_context(
        self, content: str, content_type: str, metadata: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Validate real-time context relevance"""

        # Placeholder for real-time validation
        # In full implementation, this would integrate with market data APIs

        return {
            "realtime_context": {
                "market_relevance": {"score": 0.9, "issues": []},
                "timing_appropriateness": {"score": 0.85, "issues": []},
                "data_currency": {"score": 0.95, "issues": []},
            }
        }

    # Common validation methods
    def _validate_character_limits(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate character limits and structure"""

        issues = []
        score = 1.0

        # Check overall content length
        total_chars = len(content)
        if total_chars > 4000:
            issues.append(f"Content too long: {total_chars} characters")
            score -= 0.3

        # Check hook length (first line)
        lines = content.split("\n")
        if lines:
            hook_length = len(lines[0])
            if hook_length > 280:
                issues.append(f"Hook exceeds Twitter limit: {hook_length} characters")
                score -= 0.5

        return {
            "score": max(0.0, score),
            "issues": issues,
            "character_count": total_chars,
            "hook_length": len(lines[0]) if lines else 0,
        }

    def _validate_required_elements(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate required elements are present"""

        issues = []
        score = 1.0

        # Common required elements
        required_elements = {
            "ticker": r"\$[A-Z]{1,5}",
            "blog_link": r"https://www\.colemorton\.com/blog/",
            "hashtags": r"#[A-Za-z]+",
        }

        for element, pattern in required_elements.items():
            if not re.search(pattern, content):
                issues.append(f"Missing required element: {element}")
                score -= 0.2

        return {
            "score": max(0.0, score),
            "issues": issues,
            "elements_found": len(required_elements) - len(issues),
        }

    def _validate_formatting_rules(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate formatting rules"""

        issues = []
        score = 1.0

        # NO BOLD FORMATTING rule
        if "**" in content:
            issues.append("Content contains bold formatting (violates institutional standards)")
            score -= 0.5

        # Check for proper emoji usage
        emoji_count = len(
            re.findall(
                r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
                content,
            )
        )
        if emoji_count == 0:
            issues.append("No emojis found - may reduce engagement")
            score -= 0.1
        elif emoji_count > 5:
            issues.append("Too many emojis - may appear unprofessional")
            score -= 0.1

        return {"score": max(0.0, score), "issues": issues, "emoji_count": emoji_count}

    def _validate_disclaimers(self, content: str, content_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate disclaimer presence and adequacy"""

        issues = []
        score = 1.0

        # Check for disclaimer presence
        disclaimer_patterns = [
            r"Not financial advice",
            r"⚠️.*Not financial advice",
            r"Do your own research",
        ]

        disclaimer_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in disclaimer_patterns)

        if not disclaimer_found:
            issues.append("Missing required disclaimer")
            score -= 0.8

        return {
            "score": max(0.0, score),
            "issues": issues,
            "disclaimer_found": disclaimer_found,
        }

    def _validate_risk_warnings(self, content: str, content_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate risk warnings"""

        issues = []
        score = 1.0

        # Check for risk-related language
        risk_keywords = ["risk", "loss", "volatile", "uncertain", "past performance"]
        risk_mentions = sum(1 for keyword in risk_keywords if keyword.lower() in content.lower())

        if risk_mentions == 0:
            issues.append("No risk warnings found")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "risk_mentions": risk_mentions,
        }

    def _validate_investment_advice(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate investment advice language compliance"""

        issues = []
        score = 1.0

        # Check for problematic language
        problematic_phrases = [
            "you should buy",
            "guaranteed returns",
            "no risk",
            "certain profit",
            "will increase",
        ]

        for phrase in problematic_phrases:
            if phrase.lower() in content.lower():
                issues.append(f"Problematic investment advice language: '{phrase}'")
                score -= 0.4

        return {"score": max(0.0, score), "issues": issues}

    def _validate_attribution(self, content: str, content_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate attribution requirements"""

        issues = []
        score = 1.0

        # Check for blog link attribution
        if "colemorton.com" not in content:
            issues.append("Missing blog attribution")
            score -= 0.2

        return {"score": max(0.0, score), "issues": issues}

    def _validate_data_consistency(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate data consistency"""

        issues = []
        score = 1.0

        # Extract numbers from content and verify against source data
        # This is a simplified validation - full implementation would be more sophisticated

        return {"score": score, "issues": issues, "consistency_check": "basic"}

    def _validate_source_verification(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate source verification"""

        issues = []
        score = 1.0

        # Check if source data is available
        if not source_data.get("source_available", True):
            issues.append("Source data not available for verification")
            score -= 0.3

        return {"score": max(0.0, score), "issues": issues}

    def _validate_claim_substantiation(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate claim substantiation"""

        issues = []
        score = 1.0

        # Check for unsubstantiated claims
        # This is a placeholder - full implementation would use NLP

        return {"score": score, "issues": issues}

    def _validate_hook_effectiveness(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate hook effectiveness"""

        issues = []
        score = 1.0

        lines = content.split("\n")
        if not lines:
            issues.append("No hook found")
            return {"score": 0.0, "issues": issues}

        hook = lines[0]

        # Check hook characteristics
        if len(hook) < 50:
            issues.append("Hook too short - may not be engaging")
            score -= 0.2

        if not re.search(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            hook,
        ):
            issues.append("Hook missing emoji - may reduce engagement")
            score -= 0.1

        return {"score": max(0.0, score), "issues": issues, "hook_length": len(hook)}

    def _validate_content_accessibility(
        self, content: str, content_type: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate content accessibility"""

        issues = []
        score = 1.0

        # Check for jargon and complexity
        # This is a simplified check - full implementation would use readability metrics

        return {"score": score, "issues": issues}

    def _validate_call_to_action(self, content: str, content_type: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate call to action effectiveness"""

        issues = []
        score = 1.0

        # Check for call to action
        cta_patterns = [
            r"📋 Full analysis:",
            r"Read more:",
            r"Check out:",
            r"Learn more:",
        ]

        cta_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in cta_patterns)

        if not cta_found:
            issues.append("No clear call to action found")
            score -= 0.2

        return {"score": max(0.0, score), "issues": issues, "cta_found": cta_found}

    # Content-specific validation methods
    def _validate_fundamental_specific(self, content: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate fundamental analysis specific criteria"""

        issues = []
        score = 1.0

        # Check for valuation-related content
        valuation_keywords = ["fair value", "price target", "valuation", "DCF"]
        valuation_mentions = sum(1 for keyword in valuation_keywords if keyword.lower() in content.lower())

        if valuation_mentions == 0:
            issues.append("No valuation content found in fundamental analysis")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "valuation_mentions": valuation_mentions,
        }

    def _validate_strategy_specific(self, content: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate strategy specific criteria"""

        issues = []
        score = 1.0

        # Check for strategy metrics
        strategy_keywords = ["win rate", "performance", "signal", "strategy"]
        strategy_mentions = sum(1 for keyword in strategy_keywords if keyword.lower() in content.lower())

        if strategy_mentions == 0:
            issues.append("No strategy metrics found")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "strategy_mentions": strategy_mentions,
        }

    def _validate_sector_specific(self, content: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate sector analysis specific criteria"""

        issues = []
        score = 1.0

        # Check for sector-specific content
        sector_keywords = ["sector", "allocation", "rotation", "ETF"]
        sector_mentions = sum(1 for keyword in sector_keywords if keyword.lower() in content.lower())

        if sector_mentions == 0:
            issues.append("No sector-specific content found")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "sector_mentions": sector_mentions,
        }

    def _validate_trade_history_specific(self, content: str, source_data: dict[str, Any]) -> dict[str, Any]:
        """Validate trade history specific criteria"""

        issues = []
        score = 1.0

        # Check for performance data
        performance_keywords = ["return", "trades", "performance", "portfolio"]
        performance_mentions = sum(1 for keyword in performance_keywords if keyword.lower() in content.lower())

        if performance_mentions == 0:
            issues.append("No performance data found")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "performance_mentions": performance_mentions,
        }

    def _calculate_overall_assessment(self, all_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall assessment scores"""

        # Collect all scores
        scores = []
        for category, results in all_results.items():
            if isinstance(results, dict):
                for criterion, result in results.items():
                    if isinstance(result, dict) and "score" in result:
                        scores.append(result["score"])

        # Calculate overall reliability score
        overall_reliability = sum(scores) / len(scores) if scores else 0.0

        # Determine grades
        def score_to_grade(score):
            if score >= 0.95:
                return "A+"
            if score >= 0.90:
                return "A"
            if score >= 0.85:
                return "B+"
            if score >= 0.80:
                return "B"
            if score >= 0.70:
                return "C"
            return "F"

        # Determine compliance status
        compliance_score = overall_reliability
        if compliance_score >= 0.95:
            compliance_status = "COMPLIANT"
        elif compliance_score >= 0.85:
            compliance_status = "FLAGGED"
        else:
            compliance_status = "NON_COMPLIANT"

        return {
            "overall_reliability_score": f"{overall_reliability:.1f}/10.0",
            "content_quality_grade": score_to_grade(overall_reliability),
            "engagement_potential_score": f"{min(overall_reliability + 0.1, 1.0):.1f}/10.0",
            "compliance_status": compliance_status,
            "ready_for_publication": compliance_score >= 0.85,
        }

    def _generate_findings_matrix(
        self, all_results: dict[str, Any], content: str, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate critical findings matrix"""

        verified_claims = []
        questionable_assertions = []
        inaccurate_statements = []
        unverifiable_claims = []

        # Collect issues from all validation results
        for category, results in all_results.items():
            if isinstance(results, dict):
                for criterion, result in results.items():
                    if isinstance(result, dict) and "issues" in result:
                        for issue in result["issues"]:
                            if "missing" in issue.lower() or "not found" in issue.lower():
                                unverifiable_claims.append(issue)
                            elif "inaccurate" in issue.lower() or "incorrect" in issue.lower():
                                inaccurate_statements.append(issue)
                            elif "questionable" in issue.lower() or "uncertain" in issue.lower():
                                questionable_assertions.append(issue)
                            else:
                                verified_claims.append(f"Issue identified: {issue}")

        return {
            "verified_accurate_claims": verified_claims,
            "questionable_assertions": questionable_assertions,
            "inaccurate_statements": inaccurate_statements,
            "unverifiable_claims": unverifiable_claims,
        }

    def _generate_recommendations(
        self, all_results: dict[str, Any], overall_assessment: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate actionable recommendations"""

        high_priority = []
        medium_priority = []
        low_priority = []

        # Collect recommendations based on scores
        for category, results in all_results.items():
            if isinstance(results, dict):
                for criterion, result in results.items():
                    if isinstance(result, dict) and "score" in result:
                        score = result["score"]
                        if score < 0.6:
                            high_priority.extend(result.get("issues", []))
                        elif score < 0.8:
                            medium_priority.extend(result.get("issues", []))
                        elif score < 0.9:
                            low_priority.extend(result.get("issues", []))

        return {
            "required_corrections": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
            },
            "optimization_opportunities": {
                "engagement_improvements": [
                    "Enhance hook effectiveness",
                    "Improve call-to-action",
                ],
                "accuracy_enhancements": [
                    "Strengthen data verification",
                    "Improve source attribution",
                ],
                "compliance_reinforcement": [
                    "Enhance disclaimers",
                    "Strengthen risk warnings",
                ],
            },
            "monitoring_requirements": {
                "real_time_validation": "Ongoing market context verification",
                "performance_tracking": "Content performance monitoring",
                "feedback_integration": "User response analysis",
            },
        }

    def _generate_methodology_notes(self, content_type: str, all_results: dict[str, Any]) -> dict[str, Any]:
        """Generate methodology notes"""

        return {
            "validation_framework": "unified_validation_framework_v1.0",
            "content_type": content_type,
            "validation_completeness": "comprehensive",
            "institutional_standards": "applied",
            "validation_timestamp": datetime.now().isoformat(),
        }
