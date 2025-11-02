#!/usr/bin/env python3
"""
Test Suite for Validation Framework

Property-based testing for validation logic:
- Consistency testing for scoring algorithms
- Validation criteria coverage testing
- Edge case testing for validation rules
- Performance testing for validation processing
"""

import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st


# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from result_types import validation_failure, validation_success
from unified_validation_framework import UnifiedValidationFramework


class TestValidationFramework:
    """Property-based testing for validation logic"""

    def setup_method(self):
        """Setup validation framework for testing"""
        self.validation_framework = UnifiedValidationFramework()

    def test_scoring_algorithms_consistency(self):
        """Test that scoring algorithms produce consistent results"""

        # Test data that should consistently pass
        high_quality_content = """
        🚨 $AAPL Analysis: Strong fundamental outlook with 85% upside potential

        • Fair value: $185 vs current $100
        • Strong moat with pricing power
        • Catalyst: New iPhone cycle Q2 2024

        Risk: Market volatility may affect timeline

        📋 Full analysis: https://www.colemorton.com/blog/aapl-analysis-20240101/

        #AAPL #StockAnalysis #TechInvesting

        ⚠️ Not financial advice. Past performance doesn't guarantee future results.
        """

        source_data = {
            "ticker": "AAPL",
            "current_price": 100,
            "fair_value": 185,
            "moat_strength": 8.5,
            "catalysts": [{"name": "iPhone cycle", "probability": 0.8}],
        }

        # Run validation multiple times
        results = []
        for _ in range(5):
            result = self.validation_framework.validate_content(high_quality_content, "fundamental", source_data)
            results.append(result["overall_assessment"]["overall_reliability_score"])

        # All results should be identical
        assert len(set(results)) == 1, "Scoring should be deterministic"

    def test_validation_criteria_coverage(self):
        """Test that all validation criteria are properly covered"""

        # Test each validation category
        content_structure_tests = [
            ("character_limits", "Short content"),
            ("required_elements", "Content without ticker"),
            ("formatting_rules", "Content with **bold** formatting"),
        ]

        for criterion, test_content in content_structure_tests:
            result = self.validation_framework._validate_character_limits(test_content, "fundamental", {})
            assert "score" in result
            assert "issues" in result
            assert isinstance(result["score"], float)
            assert isinstance(result["issues"], list)

    def test_validation_threshold_enforcement(self):
        """Test that validation thresholds are properly enforced"""

        # Test institutional minimum threshold
        assert self.validation_framework.quality_thresholds["institutional_minimum"] == 9.0
        assert self.validation_framework.quality_thresholds["publication_minimum"] == 8.5

        # Test threshold enforcement in scoring
        low_score_content = "Bad content"
        result = self.validation_framework.validate_content(low_score_content, "fundamental", {"ticker": "TEST"})

        score = float(result["overall_assessment"]["overall_reliability_score"].split("/")[0])
        assert score < 9.0  # Should be below institutional threshold

    def test_content_type_specific_validation(self):
        """Test content-type specific validation rules"""

        # Test fundamental-specific validation
        fundamental_content = "Analysis without valuation keywords"
        result = self.validation_framework._validate_fundamental_specific(fundamental_content, {})

        assert result["score"] < 1.0  # Should be penalized for missing valuation content
        assert "valuation" in str(result["issues"]).lower()

        # Test strategy-specific validation
        strategy_content = "Post without strategy metrics"
        result = self.validation_framework._validate_strategy_specific(strategy_content, {})

        assert result["score"] < 1.0  # Should be penalized for missing strategy content

    def test_disclaimer_validation(self):
        """Test disclaimer validation rules"""

        # Content without disclaimer
        content_without_disclaimer = "Investment advice without proper warnings"
        result = self.validation_framework._validate_disclaimers(content_without_disclaimer, "fundamental", {})

        assert result["score"] < 1.0
        assert not result["disclaimer_found"]

        # Content with disclaimer
        content_with_disclaimer = "Investment advice. ⚠️ Not financial advice."
        result = self.validation_framework._validate_disclaimers(content_with_disclaimer, "fundamental", {})

        assert result["score"] == 1.0
        assert result["disclaimer_found"]

    def test_formatting_rules_validation(self):
        """Test formatting rules validation"""

        # Test bold formatting detection
        content_with_bold = "Content with **bold** formatting"
        result = self.validation_framework._validate_formatting_rules(content_with_bold, "fundamental", {})

        assert result["score"] < 1.0
        assert "bold formatting" in str(result["issues"]).lower()

        # Test emoji counting
        content_with_emojis = "Content with 🚨 multiple 📊 emojis 🎯"
        result = self.validation_framework._validate_formatting_rules(content_with_emojis, "fundamental", {})

        assert result["emoji_count"] == 3

    def test_character_limits_validation(self):
        """Test character limits validation"""

        # Test very long content
        very_long_content = "A" * 5000
        result = self.validation_framework._validate_character_limits(very_long_content, "fundamental", {})

        assert result["score"] < 1.0
        assert "too long" in str(result["issues"]).lower()

        # Test very long hook
        long_hook_content = "A" * 300 + "\nRest of content"
        result = self.validation_framework._validate_character_limits(long_hook_content, "fundamental", {})

        assert result["score"] < 1.0
        assert "exceeds Twitter limit" in str(result["issues"]).lower()

    def test_required_elements_validation(self):
        """Test required elements validation"""

        # Content missing ticker
        content_without_ticker = "Analysis without ticker symbol"
        result = self.validation_framework._validate_required_elements(content_without_ticker, "fundamental", {})

        assert result["score"] < 1.0
        assert "ticker" in str(result["issues"]).lower()

        # Content with all required elements
        complete_content = "$AAPL analysis with https://www.colemorton.com/blog/ and #StockAnalysis"
        result = self.validation_framework._validate_required_elements(complete_content, "fundamental", {})

        assert result["score"] == 1.0
        assert len(result["issues"]) == 0

    def test_overall_assessment_calculation(self):
        """Test overall assessment calculation"""

        # Mock validation results
        mock_results = {
            "category1": {"criterion1": {"score": 0.9}, "criterion2": {"score": 0.8}},
            "category2": {"criterion3": {"score": 0.95}},
        }

        assessment = self.validation_framework._calculate_overall_assessment(mock_results)

        assert "overall_reliability_score" in assessment
        assert "content_quality_grade" in assessment
        assert "compliance_status" in assessment

        # Test score calculation
        expected_score = (0.9 + 0.8 + 0.95) / 3
        actual_score = float(assessment["overall_reliability_score"].split("/")[0])
        assert abs(actual_score - expected_score) < 0.1

    def test_validation_error_handling(self):
        """Test validation error handling"""

        # Test with invalid content type
        with pytest.raises(Exception):
            self.validation_framework.validate_content("test content", "invalid_type", {})

        # Test with missing source data
        result = self.validation_framework.validate_content("test content", "fundamental", {})

        # Should complete without crashing
        assert "overall_assessment" in result

    @given(st.text(min_size=1, max_size=1000))
    def test_content_validation_robustness(self, content):
        """Property-based test for content validation robustness"""

        # Validation should never crash regardless of input
        try:
            result = self.validation_framework.validate_content(content, "fundamental", {"ticker": "TEST"})

            # Result should always have required structure
            assert "overall_assessment" in result
            assert "validation_breakdown" in result
            assert "metadata" in result

        except Exception as e:
            pytest.fail(f"Validation should not crash with input: {content[:100]}... Error: {e}")

    def test_validation_performance(self):
        """Test validation performance with realistic content"""

        realistic_content = """
        🚨 $AAPL Technical Analysis: Bullish momentum building

        • Strong support at $150
        • RSI showing oversold conditions
        • Volume increasing on breakout

        Target: $175 (+16.7%)
        Stop: $145 (-3.3%)

        Risk/Reward: 1:5 ratio

        📋 Full analysis: https://www.colemorton.com/blog/aapl-technical-20240101/

        #AAPL #TechnicalAnalysis #StockTrading

        ⚠️ Not financial advice. Past performance doesn't guarantee future results.
        """

        source_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "target_price": 175,
            "stop_price": 145,
            "source_available": True,
        }

        import time

        start_time = time.time()

        result = self.validation_framework.validate_content(realistic_content, "fundamental", source_data)

        end_time = time.time()
        processing_time = end_time - start_time

        # Validation should complete quickly
        assert processing_time < 1.0  # Should take less than 1 second

        # Result should be high quality
        score = float(result["overall_assessment"]["overall_reliability_score"].split("/")[0])
        assert score > 7.0  # Should be reasonably high quality


class TestValidationResultTypes:
    """Test validation result type safety"""

    def test_validation_result_creation(self):
        """Test ValidationResult creation and methods"""

        # Test successful validation result
        success_result = validation_success("fundamental", "AAPL_20240101", 9.2, "A")

        assert success_result.is_compliant()
        assert not success_result.has_critical_issues()
        assert success_result.get_score_summary()["overall_score"] == 9.2

        # Test failed validation result
        failure_result = validation_failure(
            "fundamental",
            "AAPL_20240101",
            6.5,
            ["Missing disclaimer", "No valuation data"],
            ["Add disclaimer", "Include fair value"],
        )

        assert not failure_result.is_compliant()
        assert failure_result.has_critical_issues()
        assert len(failure_result.required_corrections) == 2

    def test_validation_result_serialization(self):
        """Test ValidationResult serialization"""

        result = validation_success("fundamental", "AAPL_20240101", 9.2, "A")
        result_dict = result.to_dict()

        # Test required fields
        required_fields = [
            "content_type",
            "identifier",
            "overall_score",
            "timestamp",
            "quality_grade",
            "compliance_status",
            "ready_for_publication",
        ]

        for field in required_fields:
            assert field in result_dict


# Integration tests
class TestValidationIntegration:
    """Integration tests for validation framework"""

    def test_end_to_end_validation(self):
        """Test complete validation workflow"""

        framework = UnifiedValidationFramework()

        # Complete content example
        content = """
        🚨 $AAPL Fundamental Analysis: Strong Buy Signal

        • Fair Value: $185 vs Current $150 (23% upside)
        • Strong competitive moat in ecosystem
        • Catalyst: AI integration in iPhone 16

        Valuation Methods:
        - DCF: $180
        - P/E Multiple: $175
        - Sum-of-Parts: $190

        Risk: Supply chain disruption, regulatory pressure

        📋 Full analysis: https://www.colemorton.com/blog/aapl-fundamental-20240101/

        #AAPL #FundamentalAnalysis #TechStocks

        ⚠️ Not financial advice. Past performance doesn't guarantee future results.
        """

        source_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "dcf_value": 180,
            "valuation_methods": [
                {"method": "DCF", "value": 180, "confidence": 0.8},
                {"method": "P/E", "value": 175, "confidence": 0.7},
            ],
            "catalysts": [{"name": "AI integration", "probability": 0.75}],
            "moat_strength": 8.5,
            "source_available": True,
        }

        result = framework.validate_content(content, "fundamental", source_data)

        # Should be high quality
        score = float(result["overall_assessment"]["overall_reliability_score"].split("/")[0])
        assert score >= 8.0

        # Should be compliant
        assert result["overall_assessment"]["compliance_status"] in [
            "COMPLIANT",
            "FLAGGED",
        ]

        # Should be ready for publication
        assert result["overall_assessment"]["ready_for_publication"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
