#!/usr/bin/env python3
"""
Twitter Validation Orchestrator

Enhanced validation system that integrates real-time data validation,
fail-fast logic, and automated content correction for Twitter posts.

Key Features:
- Pre-generation validation gates
- Real-time financial data validation
- Fail-fast publication blocking
- Automated content correction workflows
- Data freshness SLA monitoring
- Multi-source validation hierarchy

Usage:
    orchestrator = TwitterValidationOrchestrator()
    result = orchestrator.validate_twitter_post(post_path)
    if not result.ready_for_publication:
        # Handle validation failure
        corrections = orchestrator.generate_corrections(result)
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add services directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services"))

from real_time_validation_service import (
    RealTimeValidationService,
    SeverityLevel,
    ValidationResult,
)


logger = logging.getLogger(__name__)


class ValidationOrchestrationResult:
    """Comprehensive validation orchestration result"""

    def __init__(
        self,
        post_path: str,
        real_time_validation: ValidationResult,
        content_analysis: dict[str, Any],
        compliance_check: dict[str, Any],
        overall_assessment: dict[str, Any],
    ):
        self.post_path = post_path
        self.real_time_validation = real_time_validation
        self.content_analysis = content_analysis
        self.compliance_check = compliance_check
        self.overall_assessment = overall_assessment

        # Calculate final decision
        self.is_blocking = real_time_validation.is_blocking
        self.ready_for_publication = (
            real_time_validation.ready_for_publication
            and compliance_check.get("compliant", False)
            and not self.is_blocking
        )

        # Overall reliability score (weighted combination)
        weights = {
            "real_time_validation": 0.4,
            "content_quality": 0.3,
            "compliance": 0.3,
        }

        self.overall_reliability_score = (
            (real_time_validation.overall_score * weights["real_time_validation"])
            + (content_analysis.get("quality_score", 8.0) * weights["content_quality"])
            + (compliance_check.get("compliance_score", 9.0) * weights["compliance"])
        )


class ContentCorrectionEngine:
    """Generates automated corrections for validation issues"""

    def __init__(self):
        self.correction_patterns = {
            "stock_price_variance": self._correct_price_variance,
            "return_calculation_variance": self._correct_return_calculation,
            "market_cap_variance": self._correct_market_cap,
        }

    def generate_corrections(self, validation_result: ValidationResult, original_content: str) -> dict[str, Any]:
        """Generate automated corrections for validation issues"""
        corrections = {
            "automated_corrections": [],
            "manual_review_required": [],
            "corrected_content": original_content,
            "correction_confidence": 0.0,
        }

        high_confidence_corrections = 0
        total_corrections = 0

        for issue in validation_result.issues:
            if issue.metric in self.correction_patterns:
                correction = self.correction_patterns[issue.metric](issue, original_content)
                if correction:
                    if correction["confidence"] >= 0.9:
                        corrections["automated_corrections"].append(correction)
                        corrections["corrected_content"] = correction["corrected_content"]
                        high_confidence_corrections += 1
                    else:
                        corrections["manual_review_required"].append(correction)
                    total_corrections += 1

        corrections["correction_confidence"] = (
            high_confidence_corrections / total_corrections if total_corrections > 0 else 0.0
        )

        return corrections

    def _correct_price_variance(self, issue, content: str) -> dict[str, Any] | None:
        """Correct stock price variance issues"""
        import re

        if isinstance(issue.actual_value, (int, float)):
            actual_price = float(issue.actual_value)
            claimed_price = float(issue.claimed_value)

            # Find and replace price in content
            price_pattern = rf"\${claimed_price:,.2f}"
            corrected_price = f"${actual_price:.2f}"

            corrected_content = re.sub(price_pattern, corrected_price, content)

            return {
                "type": "price_correction",
                "issue_metric": issue.metric,
                "original_value": claimed_price,
                "corrected_value": actual_price,
                "corrected_content": corrected_content,
                "confidence": 0.95,
                "description": f"Updated price from ${claimed_price:.2f} to ${actual_price:.2f}",
            }

        return None

    def _correct_return_calculation(self, issue, content: str) -> dict[str, Any] | None:
        """Correct return calculation variance issues"""
        import re

        if isinstance(issue.actual_value, (int, float)):
            actual_return = float(issue.actual_value)
            claimed_return = float(issue.claimed_value)

            # Find and replace return percentage in content
            return_pattern = rf"\({claimed_return:.1f}%\)"
            corrected_return = f"({actual_return:.1f}%)"

            corrected_content = re.sub(return_pattern, corrected_return, content)

            return {
                "type": "return_calculation_correction",
                "issue_metric": issue.metric,
                "original_value": claimed_return,
                "corrected_value": actual_return,
                "corrected_content": corrected_content,
                "confidence": 0.92,
                "description": f"Updated expected return from {claimed_return:.1f}% to {actual_return:.1f}%",
            }

        return None

    def _correct_market_cap(self, issue, content: str) -> dict[str, Any] | None:
        """Correct market cap variance issues"""
        # Market cap corrections typically require manual review
        return {
            "type": "market_cap_correction",
            "issue_metric": issue.metric,
            "original_value": issue.claimed_value,
            "corrected_value": issue.actual_value,
            "corrected_content": content,
            "confidence": 0.7,  # Lower confidence for market cap corrections
            "description": f"Market cap correction required: {issue.description}",
            "manual_review_reason": "Market cap formatting varies significantly",
        }


class TwitterValidationOrchestrator:
    """
    Main orchestrator for Twitter post validation workflow

    Coordinates real-time validation, content analysis, compliance checks,
    and automated correction generation.
    """

    def __init__(self, config_path: str | None = None):
        self.real_time_validator = RealTimeValidationService(config_path)
        self.correction_engine = ContentCorrectionEngine()

        # SLA configuration
        self.sla_config = {
            "max_validation_time_seconds": 30,
            "max_data_age_hours": 8,
            "min_reliability_score": 9.0,
            "critical_issue_threshold": 0,  # No critical issues allowed
        }

        # Validation statistics
        self.orchestration_stats = {
            "total_validations": 0,
            "auto_corrected": 0,
            "manual_review_required": 0,
            "blocked_publications": 0,
            "average_validation_time_seconds": 0.0,
        }

        logger.info("Twitter validation orchestrator initialized")

    def validate_twitter_post(
        self,
        post_path: str,
        source_analysis_path: str | None = None,
        metadata: dict[str, Any] = None,
    ) -> ValidationOrchestrationResult:
        """
        Complete validation workflow for Twitter post

        Args:
            post_path: Path to Twitter post file
            source_analysis_path: Path to source analysis file for cross-validation
            metadata: Additional metadata for validation

        Returns:
            ValidationOrchestrationResult with comprehensive validation outcomes
        """
        start_time = datetime.now()
        self.orchestration_stats["total_validations"] += 1

        # Read post content
        try:
            with open(post_path) as f:
                post_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read post file {post_path}: {e}")
            raise

        # Phase 1: Real-time financial data validation (CRITICAL)
        logger.info(f"Phase 1: Real-time validation for {post_path}")
        real_time_result = self.real_time_validator.validate_twitter_post_claims(post_content, metadata)

        # FAIL-FAST: Block if critical real-time validation issues
        if real_time_result.is_blocking:
            logger.warning(f"BLOCKED: Critical validation issues in {post_path}")
            self.orchestration_stats["blocked_publications"] += 1

            return ValidationOrchestrationResult(
                post_path=post_path,
                real_time_validation=real_time_result,
                content_analysis={"quality_score": 0.0, "skipped": True},
                compliance_check={
                    "compliant": False,
                    "compliance_score": 0.0,
                    "skipped": True,
                },
                overall_assessment={
                    "validation_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "blocked_reason": "Critical real-time validation failures",
                    "sla_compliance": False,
                },
            )

        # Phase 2: Content quality analysis
        logger.info(f"Phase 2: Content analysis for {post_path}")
        content_analysis = self._analyze_content_quality(post_content, source_analysis_path)

        # Phase 3: Compliance and regulatory check
        logger.info(f"Phase 3: Compliance check for {post_path}")
        compliance_check = self._check_compliance(post_content)

        # Phase 4: Overall assessment
        validation_time = (datetime.now() - start_time).total_seconds()
        overall_assessment = self._generate_overall_assessment(
            real_time_result, content_analysis, compliance_check, validation_time
        )

        # Update statistics
        self._update_orchestration_stats(validation_time)

        result = ValidationOrchestrationResult(
            post_path=post_path,
            real_time_validation=real_time_result,
            content_analysis=content_analysis,
            compliance_check=compliance_check,
            overall_assessment=overall_assessment,
        )

        logger.info(
            f"Validation complete for {post_path}: Score {result.overall_reliability_score:.1f}/10, Ready: {result.ready_for_publication}"
        )

        return result

    def _analyze_content_quality(self, content: str, source_path: str | None = None) -> dict[str, Any]:
        """Analyze content quality and template effectiveness"""
        quality_metrics = {
            "character_count": len(content),
            "has_disclaimer": "not investment advice" in content.lower() or "dyoer" in content.lower(),
            "has_ticker_mention": "$" in content and any(c.isupper() for c in content),
            "has_specific_metrics": any(char in content for char in ["%", "$"]),
            "readability_score": self._calculate_readability_score(content),
            "engagement_potential": self._estimate_engagement_potential(content),
        }

        # Calculate overall quality score
        quality_score = 0.0

        # Character count check (Twitter optimized)
        if 50 <= quality_metrics["character_count"] <= 280:
            quality_score += 2.0
        elif quality_metrics["character_count"] <= 280:
            quality_score += 1.5

        # Content requirements
        if quality_metrics["has_disclaimer"]:
            quality_score += 2.0
        if quality_metrics["has_ticker_mention"]:
            quality_score += 1.5
        if quality_metrics["has_specific_metrics"]:
            quality_score += 1.5

        # Readability and engagement
        quality_score += quality_metrics["readability_score"] * 1.0
        quality_score += quality_metrics["engagement_potential"] * 1.0

        return {
            "quality_score": min(10.0, quality_score),
            "metrics": quality_metrics,
            "recommendations": self._generate_content_recommendations(quality_metrics),
        }

    def _check_compliance(self, content: str) -> dict[str, Any]:
        """Check regulatory compliance and investment disclaimer requirements"""
        compliance_checks = {
            "has_investment_disclaimer": any(
                phrase in content.lower()
                for phrase in [
                    "not investment advice",
                    "not financial advice",
                    "dyoer",
                    "do your own research",
                ]
            ),
            "no_guaranteed_returns": not any(
                phrase in content.lower() for phrase in ["guaranteed", "promise", "will return", "certain profit"]
            ),
            "balanced_risk_presentation": any(
                phrase in content.lower()
                for phrase in [
                    "risk",
                    "volatile",
                    "uncertainty",
                    "may",
                    "could",
                    "potential",
                ]
            ),
            "source_attribution": "analysis" in content.lower() or "research" in content.lower(),
        }

        # Calculate compliance score
        compliance_score = sum(compliance_checks.values()) / len(compliance_checks) * 10

        return {
            "compliant": compliance_score >= 7.0,  # 70% compliance threshold
            "compliance_score": compliance_score,
            "checks": compliance_checks,
            "violations": [key for key, passed in compliance_checks.items() if not passed],
        }

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score (0-1 scale)"""
        # Simple readability metrics
        sentences = content.count(".") + content.count("!") + content.count("?") + 1
        words = len(content.split())
        avg_word_length = sum(len(word) for word in content.split()) / words if words > 0 else 0

        # Optimal ranges for Twitter content
        readability = 1.0

        # Penalize very long or very short average word length
        if avg_word_length > 7 or avg_word_length < 3:
            readability -= 0.2

        # Penalize very long sentences
        avg_sentence_length = words / sentences if sentences > 0 else 0
        if avg_sentence_length > 15:
            readability -= 0.3

        # Reward use of numbers and specific metrics
        if any(char.isdigit() for char in content):
            readability += 0.1

        return max(0.0, min(1.0, readability))

    def _estimate_engagement_potential(self, content: str) -> float:
        """Estimate social media engagement potential (0-1 scale)"""
        engagement_signals = {
            "has_numbers": any(char.isdigit() for char in content),
            "has_controversy": any(word in content.lower() for word in ["vs", "versus", "contrarian", "paradox"]),
            "has_question": "?" in content,
            "has_call_to_action": any(phrase in content.lower() for phrase in ["choose", "decide", "consider"]),
            "has_emojis": any(ord(char) > 127 for char in content),  # Simple emoji detection
            "specific_metrics": content.count("%") + content.count("$"),
        }

        base_score = 0.5

        # Add points for engagement signals
        if engagement_signals["has_numbers"]:
            base_score += 0.1
        if engagement_signals["has_controversy"]:
            base_score += 0.2
        if engagement_signals["has_question"]:
            base_score += 0.1
        if engagement_signals["has_call_to_action"]:
            base_score += 0.1
        if engagement_signals["has_emojis"]:
            base_score += 0.05

        # Bonus for specific metrics
        base_score += min(0.1, engagement_signals["specific_metrics"] * 0.02)

        return min(1.0, base_score)

    def _generate_content_recommendations(self, quality_metrics: dict[str, Any]) -> list[str]:
        """Generate content improvement recommendations"""
        recommendations = []

        if not quality_metrics["has_disclaimer"]:
            recommendations.append("Add investment disclaimer ('Not investment advice. DYOER.')")

        if not quality_metrics["has_ticker_mention"]:
            recommendations.append("Include ticker symbol with $ prefix (e.g., $TSLA)")

        if not quality_metrics["has_specific_metrics"]:
            recommendations.append("Add specific financial metrics (percentages, dollar amounts)")

        if quality_metrics["character_count"] > 280:
            recommendations.append("Reduce content length for Twitter compatibility")

        if quality_metrics["readability_score"] < 0.7:
            recommendations.append("Improve readability - shorter sentences, simpler words")

        if quality_metrics["engagement_potential"] < 0.6:
            recommendations.append("Enhance engagement - add contrarian angle or specific question")

        return recommendations

    def _generate_overall_assessment(
        self,
        real_time_result: ValidationResult,
        content_analysis: dict[str, Any],
        compliance_check: dict[str, Any],
        validation_time: float,
    ) -> dict[str, Any]:
        """Generate overall validation assessment"""

        # SLA compliance check
        sla_compliant = (
            validation_time <= self.sla_config["max_validation_time_seconds"]
            and real_time_result.data_freshness_hours <= self.sla_config["max_data_age_hours"]
            and not real_time_result.is_blocking
        )

        return {
            "validation_time_seconds": validation_time,
            "sla_compliance": sla_compliant,
            "data_freshness_compliant": real_time_result.data_freshness_hours <= self.sla_config["max_data_age_hours"],
            "critical_issues_count": len([i for i in real_time_result.issues if i.severity == SeverityLevel.CRITICAL]),
            "blocking_reason": ("Critical validation failures" if real_time_result.is_blocking else None),
            "recommendations_count": len(content_analysis.get("recommendations", [])),
            "automated_corrections_available": len(
                [i for i in real_time_result.issues if i.metric in self.correction_engine.correction_patterns]
            ),
        }

    def _update_orchestration_stats(self, validation_time: float) -> None:
        """Update orchestration statistics"""
        current_avg = self.orchestration_stats["average_validation_time_seconds"]
        total = self.orchestration_stats["total_validations"]

        self.orchestration_stats["average_validation_time_seconds"] = (
            current_avg * (total - 1) + validation_time
        ) / total

    def generate_corrections(self, validation_result: ValidationOrchestrationResult) -> dict[str, Any]:
        """Generate automated corrections for validation issues"""
        # Read original content
        with open(validation_result.post_path) as f:
            original_content = f.read()

        corrections = self.correction_engine.generate_corrections(
            validation_result.real_time_validation, original_content
        )

        # Update statistics
        if corrections["automated_corrections"]:
            self.orchestration_stats["auto_corrected"] += 1
        if corrections["manual_review_required"]:
            self.orchestration_stats["manual_review_required"] += 1

        return corrections

    def save_corrected_content(self, corrections: dict[str, Any], output_path: str) -> bool:
        """Save corrected content to file"""
        try:
            with open(output_path, "w") as f:
                f.write(corrections["corrected_content"])

            # Save correction metadata
            metadata_path = output_path.replace(".md", "_corrections.json")
            with open(metadata_path, "w") as f:
                json.dump(
                    {
                        "corrections_applied": corrections["automated_corrections"],
                        "manual_review_required": corrections["manual_review_required"],
                        "correction_confidence": corrections["correction_confidence"],
                        "correction_timestamp": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Corrected content saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save corrected content: {e}")
            return False

    def get_orchestration_stats(self) -> dict[str, Any]:
        """Get comprehensive orchestration statistics"""
        return {
            "orchestration_statistics": self.orchestration_stats.copy(),
            "real_time_validator_stats": self.real_time_validator.get_validation_stats(),
            "sla_configuration": self.sla_config.copy(),
            "service_status": {
                "validator_available": self.real_time_validator is not None,
                "correction_engine_available": self.correction_engine is not None,
                "uptime": "active",
            },
        }


def create_twitter_validation_orchestrator() -> TwitterValidationOrchestrator:
    """Factory function to create validation orchestrator"""
    return TwitterValidationOrchestrator()


if __name__ == "__main__":
    # Test the orchestrator
    logging.basicConfig(level=logging.INFO)

    orchestrator = create_twitter_validation_orchestrator()

    # Test with the problematic TSLA_vs_NIO post
    test_post_path = (
        "/Users/colemorton/Projects/colemorton/data/outputs/twitter/fundamental_analysis/TSLA_vs_NIO_20250819.md"
    )

    try:
        result = orchestrator.validate_twitter_post(test_post_path)

        print("\nOrchestration Result:")
        print("Overall Reliability Score: {result.overall_reliability_score:.1f}/10.0")
        print("Ready for Publication: {result.ready_for_publication}")
        print("Blocking Issues: {result.is_blocking}")

        if result.real_time_validation.issues:
            print("\nReal-time Validation Issues:")
            for issue in result.real_time_validation.issues:
                print("  {issue.severity.value.upper()}: {issue.description}")

        if not result.ready_for_publication:
            print("\nGenerating corrections...")
            corrections = orchestrator.generate_corrections(result)
            print("Automated corrections: {len(corrections['automated_corrections'])}")
            print(f"Manual review required: {len(corrections['manual_review_required'])}")

    except FileNotFoundError:
        print("Test file not found - creating mock validation test")
        # Could add mock test here
