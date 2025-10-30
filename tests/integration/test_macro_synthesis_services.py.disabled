#!/usr/bin/env python3
"""
Macro Synthesis Service Integration Tests

Test-driven development for macro synthesis service integration including:
- Service collection with all services healthy
- Service collection with service failures
- Null safety checks preventing None assignment errors
- Graceful degradation on service unavailability
- Service health aggregation
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from macro_synthesis import MacroEconomicSynthesis


class TestMacroSynthesisServiceCollection:
    """Test macro synthesis service collection functionality"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    @patch('services.sector_economic_correlations.create_sector_economic_correlations')
    def test_service_collection_with_all_services_healthy(
        self,
        mock_sector_factory,
        mock_liquidity_factory,
        mock_calendar_factory,
        sample_economic_calendar_response,
        sample_service_health_response
    ):
        """Test service collection when all services are healthy"""
        # Arrange
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = {
            "status": "healthy",
            "service_name": "economic_calendar"
        }
        mock_calendar_service.get_upcoming_economic_events.return_value = sample_economic_calendar_response["upcoming_events"]
        mock_calendar_service.get_fomc_decision_probabilities.return_value = sample_economic_calendar_response["fomc_probabilities"]
        mock_calendar_service.get_economic_surprise_index.return_value = sample_economic_calendar_response["economic_surprises"]

        mock_liquidity_service = Mock()
        mock_liquidity_service.health_check.return_value = {
            "status": "healthy",
            "service_name": "global_liquidity_monitor"
        }
        mock_liquidity_service.get_comprehensive_liquidity_analysis.return_value = {
            "global_m2_analysis": {"growth_rate": 5.2},
            "central_bank_analysis": {"fed_policy": "neutral"},
            "global_liquidity_conditions": {"status": "adequate"},
            "cross_border_capital_flows": [],
            "trading_implications": {"recommendation": "balanced"}
        }

        mock_sector_service = Mock()
        mock_sector_service.health_check.return_value = {
            "status": "healthy",
            "service_name": "sector_correlations"
        }
        mock_sector_service.get_comprehensive_sector_analysis.return_value = {
            "sector_sensitivities": {"technology": 0.85},
            "economic_regime_analysis": {"current_regime": "expansion"},
            "sector_rotation_signals": [],
            "factor_attribution_summary": {},
            "investment_recommendations": {}
        }

        mock_calendar_factory.return_value = mock_calendar_service
        mock_liquidity_factory.return_value = mock_liquidity_service
        mock_sector_factory.return_value = mock_sector_service

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.service_health["economic_calendar"]["status"] == "healthy"
        assert synthesis.service_health["global_liquidity"]["status"] == "healthy"
        assert synthesis.service_health["sector_correlations"]["status"] == "healthy"

        assert len(synthesis.economic_calendar_data) > 0
        assert len(synthesis.global_liquidity_data) > 0
        assert len(synthesis.sector_correlation_data) > 0

        assert "upcoming_events" in synthesis.economic_calendar_data
        assert "m2_analysis" in synthesis.global_liquidity_data
        assert "sector_sensitivities" in synthesis.sector_correlation_data

    @patch('services.economic_calendar.create_economic_calendar_service')
    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    @patch('services.sector_economic_correlations.create_sector_economic_correlations')
    def test_service_collection_with_service_failures(
        self,
        mock_sector_factory,
        mock_liquidity_factory,
        mock_calendar_factory
    ):
        """Test service collection handles service failures gracefully"""
        # Arrange - Services return None (factory failure)
        mock_calendar_factory.return_value = None
        mock_liquidity_factory.return_value = None
        mock_sector_factory.return_value = None

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.service_health["economic_calendar"]["status"] == "failed"
        assert synthesis.service_health["global_liquidity"]["status"] == "failed"
        assert synthesis.service_health["sector_correlations"]["status"] == "failed"

        assert synthesis.economic_calendar_data == {}
        assert synthesis.global_liquidity_data == {}
        assert synthesis.sector_correlation_data == {}

        # Ensure error messages are captured
        assert "Service factory returned None" in synthesis.service_health["economic_calendar"]["error"]
        assert "Service factory returned None" in synthesis.service_health["global_liquidity"]["error"]
        assert "Service factory returned None" in synthesis.service_health["sector_correlations"]["error"]


class TestMacroSynthesisNullSafetyChecks:
    """Test null safety checks in macro synthesis service integration"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    def test_null_safety_checks_prevent_none_assignment(self, mock_calendar_factory):
        """Test null safety checks prevent NoneType assignment errors"""
        # Arrange
        mock_calendar_factory.return_value = None  # Service creation fails

        synthesis = MacroEconomicSynthesis(region="US")

        # Act - This should not raise NoneType assignment errors
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.economic_calendar_data == {}
        assert synthesis.service_health["economic_calendar"]["status"] == "failed"
        assert "Service factory returned None" in synthesis.service_health["economic_calendar"]["error"]

    @patch('services.economic_calendar.create_economic_calendar_service')
    def test_health_check_none_response_handled(self, mock_calendar_factory):
        """Test graceful handling when health check returns None"""
        # Arrange
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = None  # Health check returns None
        mock_calendar_factory.return_value = mock_calendar_service

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.service_health["economic_calendar"]["status"] == "failed"
        assert "Health check returned None" in synthesis.service_health["economic_calendar"]["error"]
        assert synthesis.economic_calendar_data == {}

    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    def test_service_method_call_on_none_prevented(self, mock_liquidity_factory):
        """Test prevention of method calls on None service objects"""
        # Arrange
        mock_liquidity_factory.return_value = None

        synthesis = MacroEconomicSynthesis(region="US")

        # Act - Should not attempt to call methods on None object
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.global_liquidity_data == {}
        assert synthesis.service_health["global_liquidity"]["status"] == "failed"


class TestMacroSynthesisGracefulDegradation:
    """Test graceful degradation when services are unavailable"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    @patch('services.sector_economic_correlations.create_sector_economic_correlations')
    def test_graceful_degradation_on_service_unavailability(
        self,
        mock_sector_factory,
        mock_liquidity_factory,
        mock_calendar_factory
    ):
        """Test system continues to function when services are unavailable"""
        # Arrange - Mix of working and failing services
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = {"status": "healthy"}
        mock_calendar_service.get_upcoming_economic_events.return_value = []
        mock_calendar_service.get_fomc_decision_probabilities.return_value = {}
        mock_calendar_service.get_economic_surprise_index.return_value = {}

        mock_calendar_factory.return_value = mock_calendar_service
        mock_liquidity_factory.return_value = None  # Liquidity service fails
        mock_sector_factory.return_value = None     # Sector service fails

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert - System should continue with partial functionality
        assert synthesis.service_health["economic_calendar"]["status"] == "healthy"
        assert synthesis.service_health["global_liquidity"]["status"] == "failed"
        assert synthesis.service_health["sector_correlations"]["status"] == "failed"

        # Economic calendar data should be collected
        assert len(synthesis.economic_calendar_data) > 0

        # Failed services should have empty data
        assert synthesis.global_liquidity_data == {}
        assert synthesis.sector_correlation_data == {}

    @patch('services.economic_calendar.create_economic_calendar_service')
    def test_import_errors_handled_gracefully(self, mock_calendar_factory):
        """Test graceful handling of service import errors"""
        # Arrange
        mock_calendar_factory.side_effect = ImportError("Module not found")

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.service_health["economic_calendar"]["status"] == "import_failed"
        assert "Import failed" in synthesis.service_health["economic_calendar"]["error"]
        assert synthesis.economic_calendar_data == {}


class TestMacroSynthesisServiceHealthAggregation:
    """Test service health aggregation functionality"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    @patch('services.sector_economic_correlations.create_sector_economic_correlations')
    def test_service_health_aggregation(
        self,
        mock_sector_factory,
        mock_liquidity_factory,
        mock_calendar_factory
    ):
        """Test service health aggregation provides accurate status summary"""
        # Arrange - Mixed health statuses
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = {"status": "healthy"}
        mock_calendar_service.get_upcoming_economic_events.return_value = []
        mock_calendar_service.get_fomc_decision_probabilities.return_value = {}
        mock_calendar_service.get_economic_surprise_index.return_value = {}

        mock_liquidity_service = Mock()
        mock_liquidity_service.health_check.return_value = {"status": "configuration_error"}

        mock_calendar_factory.return_value = mock_calendar_service
        mock_liquidity_factory.return_value = mock_liquidity_service
        mock_sector_factory.return_value = None  # Complete failure

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        healthy_count = sum(
            1 for service in synthesis.service_health.values()
            if service["status"] == "healthy"
        )
        total_count = len(synthesis.service_health)

        assert healthy_count == 1  # Only calendar service is healthy
        assert total_count == 3   # All three services tracked

        assert synthesis.service_health["economic_calendar"]["status"] == "healthy"
        assert synthesis.service_health["global_liquidity"]["status"] == "failed"
        assert synthesis.service_health["sector_correlations"]["status"] == "failed"

    def test_service_health_initialization(self):
        """Test service health is properly initialized"""
        # Arrange & Act
        synthesis = MacroEconomicSynthesis(region="US")

        # Assert - All services should be initialized with pending status
        expected_services = ["economic_calendar", "global_liquidity", "sector_correlations"]

        for service_name in expected_services:
            assert service_name in synthesis.service_health
            assert synthesis.service_health[service_name]["status"] == "pending"
            assert synthesis.service_health[service_name]["error"] is None


class TestMacroSynthesisErrorRecovery:
    """Test error recovery and resilience in macro synthesis"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    def test_service_exception_during_data_collection_handled(self, mock_calendar_factory):
        """Test graceful handling of exceptions during service data collection"""
        # Arrange
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = {"status": "healthy"}
        mock_calendar_service.get_upcoming_economic_events.side_effect = Exception("API timeout")

        mock_calendar_factory.return_value = mock_calendar_service

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert - Should handle exception and mark service as failed
        assert synthesis.service_health["economic_calendar"]["status"] == "failed"
        assert "API timeout" in synthesis.service_health["economic_calendar"]["error"]
        assert synthesis.economic_calendar_data == {}

    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    def test_unhealthy_service_status_prevents_data_collection(self, mock_liquidity_factory):
        """Test that unhealthy service status prevents data collection"""
        # Arrange
        mock_liquidity_service = Mock()
        mock_liquidity_service.health_check.return_value = {
            "status": "configuration_error",
            "error": "Missing API key"
        }

        mock_liquidity_factory.return_value = mock_liquidity_service

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert
        assert synthesis.service_health["global_liquidity"]["status"] == "failed"
        assert "Missing API key" in synthesis.service_health["global_liquidity"]["error"]
        assert synthesis.global_liquidity_data == {}

        # Verify data collection methods were not called
        mock_liquidity_service.get_comprehensive_liquidity_analysis.assert_not_called()


@pytest.mark.integration
class TestMacroSynthesisEndToEndServiceIntegration:
    """Test end-to-end service integration scenarios"""

    @patch('services.economic_calendar.create_economic_calendar_service')
    @patch('services.global_liquidity_monitor.create_global_liquidity_monitor')
    @patch('services.sector_economic_correlations.create_sector_economic_correlations')
    def test_end_to_end_service_integration_success_scenario(
        self,
        mock_sector_factory,
        mock_liquidity_factory,
        mock_calendar_factory,
        sample_economic_calendar_response
    ):
        """Test complete end-to-end service integration success scenario"""
        # Arrange - All services healthy and returning data
        mock_calendar_service = Mock()
        mock_calendar_service.health_check.return_value = {"status": "healthy"}
        mock_calendar_service.get_upcoming_economic_events.return_value = sample_economic_calendar_response["upcoming_events"]
        mock_calendar_service.get_fomc_decision_probabilities.return_value = sample_economic_calendar_response["fomc_probabilities"]
        mock_calendar_service.get_economic_surprise_index.return_value = sample_economic_calendar_response["economic_surprises"]

        mock_liquidity_service = Mock()
        mock_liquidity_service.health_check.return_value = {"status": "healthy"}
        mock_liquidity_service.get_comprehensive_liquidity_analysis.return_value = {
            "global_m2_analysis": {"growth_rate": 5.2, "trend": "moderate"},
            "central_bank_analysis": {"fed_policy": "neutral", "ecb_policy": "accommodative"},
            "global_liquidity_conditions": {"status": "adequate", "risk_level": "low"},
            "cross_border_capital_flows": [{"region": "US", "flow": "inbound", "amount": 1.2}],
            "trading_implications": {"recommendation": "balanced", "risk_appetite": "moderate"}
        }

        mock_sector_service = Mock()
        mock_sector_service.health_check.return_value = {"status": "healthy"}
        mock_sector_service.get_comprehensive_sector_analysis.return_value = {
            "sector_sensitivities": {"technology": 0.85, "healthcare": 0.65, "financials": 0.78},
            "economic_regime_analysis": {"current_regime": "expansion", "confidence": 0.82},
            "sector_rotation_signals": [{"from": "growth", "to": "value", "strength": 0.6}],
            "factor_attribution_summary": {"momentum": 0.3, "quality": 0.4, "value": 0.3},
            "investment_recommendations": {"overweight": ["technology"], "underweight": ["utilities"]}
        }

        mock_calendar_factory.return_value = mock_calendar_service
        mock_liquidity_factory.return_value = mock_liquidity_service
        mock_sector_factory.return_value = mock_sector_service

        synthesis = MacroEconomicSynthesis(region="US")

        # Act
        synthesis._collect_enhanced_service_data()

        # Assert - All services should be operational and data collected
        assert all(
            service["status"] == "healthy"
            for service in synthesis.service_health.values()
        )

        # Verify rich data collection
        assert len(synthesis.economic_calendar_data["upcoming_events"]) == 2
        assert synthesis.economic_calendar_data["fomc_probabilities"]["rate_cut_probability"] == 0.65
        assert synthesis.economic_calendar_data["economic_surprises"]["trend"] == "improving"

        assert synthesis.global_liquidity_data["m2_analysis"]["growth_rate"] == 5.2
        assert synthesis.global_liquidity_data["central_bank_analysis"]["fed_policy"] == "neutral"
        assert len(synthesis.global_liquidity_data["cross_border_capital_flows"]) == 1

        assert synthesis.sector_correlation_data["sector_sensitivities"]["technology"] == 0.85
        assert synthesis.sector_correlation_data["economic_regime_analysis"]["current_regime"] == "expansion"
        assert len(synthesis.sector_correlation_data["sector_rotation_signals"]) == 1
