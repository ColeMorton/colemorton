#!/usr/bin/env python3
"""
Test Suite for Template Selection

Integration tests for template selection algorithms:
- Template selection determinism
- Template scoring validation
- Template recommendation accuracy
- Performance testing
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from result_types import TemplateSelectionResult
from twitter_template_selector import TwitterTemplateSelector


class TestTemplateSelection:
    """Integration tests for template selection algorithms"""

    def setup_method(self):
        """Setup template selector for testing"""
        self.template_selector = TwitterTemplateSelector()

    def test_template_selection_deterministic(self):
        """Test that template selection is deterministic for same inputs"""

        # Test data for fundamental analysis
        test_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "fair_value_low": 175,
            "fair_value_high": 195,
            "valuation_methods": [
                {"method": "DCF", "confidence": 0.8},
                {"method": "P/E", "confidence": 0.7},
            ],
            "catalysts": [{"name": "iPhone cycle", "probability": 0.8}],
            "moat_strength": 8.5,
        }

        # Run selection multiple times
        results = []
        for _ in range(5):
            template, metadata = self.template_selector.select_optimal_template("fundamental", test_data)
            results.append((template, metadata["selection_score"]))

        # All results should be identical
        templates = [r[0] for r in results]
        scores = [r[1] for r in results]

        assert len(set(templates)) == 1, "Template selection should be deterministic"
        assert len(set(scores)) == 1, "Selection scores should be deterministic"

    def test_template_scoring_ranges(self):
        """Test that template scores are within expected ranges"""

        # Test with complete data (should score high)
        complete_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "fair_value_low": 175,
            "fair_value_high": 195,
            "valuation_methods": [
                {"method": "DCF", "confidence": 0.9},
                {"method": "P/E", "confidence": 0.8},
            ],
            "catalysts": [
                {"name": "iPhone cycle", "probability": 0.8},
                {"name": "AI integration", "probability": 0.7},
            ],
            "moat_strength": 9.0,
            "competitive_advantages": ["ecosystem", "brand", "patents"],
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", complete_data)

        # Score should be high for complete data
        assert metadata["selection_score"] >= 0.7

        # All scores should be between 0 and 1
        for score in metadata["all_scores"].values():
            assert 0.0 <= score <= 1.0

    def test_template_scoring_empty_data(self):
        """Test template scoring with minimal data"""

        # Test with minimal data
        minimal_data = {"ticker": "AAPL"}

        template, metadata = self.template_selector.select_optimal_template("fundamental", minimal_data)

        # Should still select a template
        assert template is not None
        assert template in metadata["all_scores"]

        # Score should be low for minimal data
        assert metadata["selection_score"] < 0.5

    def test_fundamental_template_selection(self):
        """Test fundamental analysis template selection logic"""

        # Test data optimized for valuation template
        valuation_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "fair_value_low": 175,
            "fair_value_high": 195,
            "valuation_methods": [
                {"method": "DCF", "confidence": 0.9},
                {"method": "P/E", "confidence": 0.8},
            ],
            "dcf_value": 180,
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", valuation_data)

        # Should select valuation template
        assert template == "A_valuation"

        # Test data optimized for catalyst template
        catalyst_data = {
            "ticker": "AAPL",
            "catalysts": [
                {"name": "iPhone cycle", "probability": 0.8},
                {"name": "AI integration", "probability": 0.7},
                {"name": "Services growth", "probability": 0.9},
            ],
            "catalyst_count": 3,
            "upcoming_events": ["WWDC", "iPhone launch"],
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", catalyst_data)

        # Should select catalyst template
        assert template == "B_catalyst"

    def test_template_validation(self):
        """Test template selection validation"""

        # Test valid template selection
        valid_data = {
            "ticker": "AAPL",
            "fair_value": 185,
            "current_price": 150,
            "valuation_methods": [{"method": "DCF", "confidence": 0.8}],
        }

        validation_result = self.template_selector.validate_template_selection("fundamental", "A_valuation", valid_data)

        assert validation_result["valid"] is True
        assert validation_result["confidence"] > 0.5

        # Test invalid template selection
        invalid_data = {"ticker": "AAPL"}

        validation_result = self.template_selector.validate_template_selection(
            "fundamental", "A_valuation", invalid_data
        )

        assert validation_result["valid"] is False
        assert validation_result["confidence"] < 0.6

    def test_template_recommendations(self):
        """Test template recommendation system"""

        test_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "catalysts": [{"name": "iPhone cycle", "probability": 0.8}],
            "moat_strength": 8.5,
        }

        recommendations = self.template_selector.get_template_recommendations("fundamental", test_data)

        # Should return recommendations
        assert len(recommendations) > 0

        # Recommendations should be sorted by score
        scores = [r["score"] for r in recommendations]
        assert scores == sorted(scores, reverse=True)

        # Each recommendation should have required fields
        for rec in recommendations:
            assert "template_variant" in rec
            assert "score" in rec
            assert "confidence" in rec
            assert "explanation" in rec
            assert "recommended" in rec

    def test_strategy_template_selection(self):
        """Test strategy template selection"""

        strategy_data = {
            "ticker": "AAPL",
            "strategy_type": "SMA",
            "win_rate": 0.65,
            "net_performance": 15.5,
            "reward_risk": 2.1,
            "total_trades": 25,
        }

        template, metadata = self.template_selector.select_optimal_template("strategy", strategy_data)

        assert template == "default"
        assert metadata["selection_score"] > 0.5

    def test_sector_template_selection(self):
        """Test sector template selection"""

        # Test rotation template selection
        rotation_data = {
            "sector_name": "technology",
            "rotation_signal": True,
            "rotation_score": 0.8,
            "economic_cycle": "expansion",
            "relative_performance": 12.5,
            "flow_data": "positive",
        }

        template, metadata = self.template_selector.select_optimal_template("sector", rotation_data)

        assert template == "rotation"

        # Test comparison template selection
        comparison_data = {
            "sector_name": "technology",
            "sector_comparison": True,
            "relative_valuation": 0.85,
            "cross_sector": True,
            "performance_ranking": 3,
            "allocation_recommendation": "overweight",
        }

        template, metadata = self.template_selector.select_optimal_template("sector", comparison_data)

        assert template == "comparison"

    def test_trade_history_template_selection(self):
        """Test trade history template selection"""

        trade_data = {
            "analysis_name": "Q1_PERFORMANCE",
            "performance_metrics": True,
            "win_rate": 0.72,
            "total_trades": 15,
            "period_return": 18.5,
            "transparency_level": "high",
        }

        template, metadata = self.template_selector.select_optimal_template("trade_history", trade_data)

        assert template == "performance"
        assert metadata["selection_score"] > 0.5

    def test_template_scoring_edge_cases(self):
        """Test template scoring with edge cases"""

        # Test with zero values
        zero_data = {
            "ticker": "AAPL",
            "current_price": 0,
            "fair_value": 0,
            "moat_strength": 0,
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", zero_data)

        # Should handle zero values gracefully
        assert template is not None
        assert all(0.0 <= score <= 1.0 for score in metadata["all_scores"].values())

        # Test with negative values
        negative_data = {"ticker": "AAPL", "net_performance": -5.2, "reward_risk": -0.5}

        template, metadata = self.template_selector.select_optimal_template("strategy", negative_data)

        # Should handle negative values gracefully
        assert template is not None
        assert all(0.0 <= score <= 1.0 for score in metadata["all_scores"].values())

    def test_template_explanation_generation(self):
        """Test template explanation generation"""

        test_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "catalysts": [
                {"name": "iPhone cycle", "probability": 0.8},
                {"name": "AI integration", "probability": 0.7},
            ],
            "moat_strength": 8.5,
        }

        recommendations = self.template_selector.get_template_recommendations("fundamental", test_data)

        # Each recommendation should have meaningful explanation
        for rec in recommendations:
            assert len(rec["explanation"]) > 0
            assert rec["explanation"] != "General template match"

    def test_template_performance_tracking(self):
        """Test template performance tracking"""

        # Add performance metrics
        self.template_selector.update_template_performance(
            "A_valuation",
            {
                "engagement_score": 8.5,
                "click_through_rate": 0.15,
                "conversion_rate": 0.08,
            },
        )

        # Get analytics
        analytics = self.template_selector.get_template_performance_analytics()

        assert "A_valuation" in analytics
        assert analytics["A_valuation"]["usage_count"] == 1
        assert "average_metrics" in analytics["A_valuation"]

    def test_selection_confidence_metrics(self):
        """Test selection confidence metrics"""

        # Test with high confidence data
        high_confidence_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 200,  # Large gap
            "valuation_methods": [
                {"method": "DCF", "confidence": 0.9},
                {"method": "P/E", "confidence": 0.85},
            ],
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", high_confidence_data)

        # Should have high confidence
        assert metadata["selection_score"] > 0.8

        # Test with low confidence data
        low_confidence_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 152,  # Small gap
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", low_confidence_data)

        # Should have lower confidence
        assert metadata["selection_score"] < 0.6

    def test_template_selection_with_context(self):
        """Test template selection with additional context"""

        test_data = {"ticker": "AAPL", "fair_value": 185, "current_price": 150}

        context = {
            "market_conditions": "bullish",
            "sector_rotation": "into_tech",
            "user_preference": "detailed_analysis",
        }

        template, metadata = self.template_selector.select_optimal_template("fundamental", test_data, context)

        # Should select template and include context in metadata
        assert template is not None
        assert "selection_timestamp" in metadata

    def test_invalid_content_type_handling(self):
        """Test handling of invalid content types"""

        with pytest.raises(ValueError, match="Unknown content type"):
            self.template_selector.select_optimal_template("invalid_type", {"ticker": "AAPL"})

    def test_template_selection_performance(self):
        """Test template selection performance"""

        test_data = {
            "ticker": "AAPL",
            "current_price": 150,
            "fair_value": 185,
            "valuation_methods": [
                {"method": "DCF", "confidence": 0.8},
                {"method": "P/E", "confidence": 0.7},
            ],
            "catalysts": [{"name": "iPhone cycle", "probability": 0.8}],
            "moat_strength": 8.5,
        }

        import time

        start_time = time.time()

        for _ in range(10):
            template, metadata = self.template_selector.select_optimal_template("fundamental", test_data)

        end_time = time.time()
        avg_time = (end_time - start_time) / 10

        # Should be fast (less than 10ms per selection)
        assert avg_time < 0.01

    def test_template_selection_result_type(self):
        """Test template selection result type safety"""

        test_data = {"ticker": "AAPL", "fair_value": 185, "current_price": 150}

        template, metadata = self.template_selector.select_optimal_template("fundamental", test_data)

        # Test that we can create a structured result
        result = TemplateSelectionResult(
            content_type="fundamental",
            identifier="AAPL_20240101",
            selected_template=template,
            selection_score=metadata["selection_score"],
            all_scores=metadata["all_scores"],
            selection_reason=metadata["selection_reason"],
        )

        # Test result methods
        assert result.get_second_best() is not None
        assert result.get_selection_margin() >= 0
        assert isinstance(result.is_confident_selection(), bool)

        # Test serialization
        result_dict = result.to_dict()
        assert "content_type" in result_dict
        assert "selected_template" in result_dict


class TestTemplateSelectionCriteria:
    """Test template selection criteria evaluation"""

    def setup_method(self):
        """Setup template selector for testing"""
        self.template_selector = TwitterTemplateSelector()

    def test_valuation_gap_criterion(self):
        """Test valuation gap criterion evaluation"""

        # Test large gap
        large_gap_data = {"current_price": 100, "fair_value": 150}
        score = self.template_selector._evaluate_criterion(large_gap_data, "valuation_gap", 10)
        assert score == 1.0  # Should get full score

        # Test small gap
        small_gap_data = {"current_price": 100, "fair_value": 105}
        score = self.template_selector._evaluate_criterion(small_gap_data, "valuation_gap", 10)
        assert score < 1.0  # Should get partial score

    def test_catalyst_count_criterion(self):
        """Test catalyst count criterion evaluation"""

        # Test with catalyst list
        catalyst_data = {
            "catalysts": [
                {"name": "iPhone cycle", "probability": 0.8},
                {"name": "AI integration", "probability": 0.7},
            ]
        }
        score = self.template_selector._evaluate_criterion(catalyst_data, "catalyst_count", 2)
        assert score == 1.0

        # Test with catalyst count field
        count_data = {"catalyst_count": 3}
        score = self.template_selector._evaluate_criterion(count_data, "catalyst_count", 2)
        assert score == 1.0

    def test_moat_strength_criterion(self):
        """Test moat strength criterion evaluation"""

        # Test high moat strength
        high_moat_data = {"moat_strength": 9.0}
        score = self.template_selector._evaluate_criterion(high_moat_data, "moat_strength", 7)
        assert score == 1.0

        # Test low moat strength
        low_moat_data = {"moat_strength": 5.0}
        score = self.template_selector._evaluate_criterion(low_moat_data, "moat_strength", 7)
        assert score < 1.0

    def test_default_criterion_evaluation(self):
        """Test default criterion evaluation"""

        # Test numeric value
        numeric_data = {"test_metric": 8.5}
        score = self.template_selector._evaluate_criterion(numeric_data, "test_metric", 7.0)
        assert score == 1.0

        # Test list value
        list_data = {"test_list": [1, 2, 3, 4]}
        score = self.template_selector._evaluate_criterion(list_data, "test_list", 3)
        assert score == 1.0

        # Test boolean value
        bool_data = {"test_bool": True}
        score = self.template_selector._evaluate_criterion(bool_data, "test_bool", 0.5)
        assert score == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
