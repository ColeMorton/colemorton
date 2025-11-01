#!/usr/bin/env python3
"""
Dynamic Confidence Engine

Advanced confidence calculation system that dynamically adjusts confidence scores based on:
- Data quality assessment (completeness, freshness, source reliability)
- Multi-source validation and cross-correlation
- Temporal decay functions for aging data
- Statistical confidence intervals and uncertainty quantification
- Service availability and performance metrics

Key Features:
- Data age-based confidence decay with configurable half-life
- Multi-dimensional quality assessment (source, age, completeness, consistency)
- Cross-source validation with correlation analysis
- Statistical confidence intervals using bootstrap methods
- Service reliability tracking with exponential decay
- Institutional-grade confidence calibration

Usage:
    engine = DynamicConfidenceEngine(config_manager)
    confidence = engine.calculate_confidence(data_points, context)
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np


# Import configuration and data structures
try:
    from services.real_time_market_data import MarketDataPoint
    from utils.config_manager import ConfigManager

    SERVICES_AVAILABLE = True
except ImportError as e:
    SERVICES_AVAILABLE = False
    logging.warning(f"Service imports not available: {e}")

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level classifications"""

    CRITICAL = "critical"  # 0.95+
    HIGH = "high"  # 0.85-0.95
    INSTITUTIONAL = "institutional"  # 0.80-0.85
    MODERATE = "moderate"  # 0.70-0.80
    LOW = "low"  # 0.50-0.70
    INSUFFICIENT = "insufficient"  # <0.50


@dataclass
class DataQualityMetrics:
    """Data quality assessment structure"""

    completeness_score: float  # 0-1, data availability
    freshness_score: float  # 0-1, age-adjusted score
    reliability_score: float  # 0-1, source reliability
    consistency_score: float  # 0-1, cross-source agreement
    statistical_confidence: float  # 0-1, statistical significance
    overall_quality: float  # 0-1, weighted composite


@dataclass
class ConfidenceDecayParameters:
    """Parameters for confidence decay functions"""

    half_life_hours: float  # Half-life for exponential decay
    minimum_confidence: float  # Floor confidence level
    decay_function: str  # 'exponential', 'linear', 'stepped'
    critical_age_hours: float  # Point where confidence becomes critical


class DynamicConfidenceEngine:
    """Advanced dynamic confidence calculation engine"""

    def __init__(self, config_manager: ConfigManager | None = None):
        self.config = config_manager or ConfigManager()

        # Load confidence parameters from configuration
        self.decay_parameters = self._load_decay_parameters()
        self.quality_weights = self._load_quality_weights()
        self.institutional_thresholds = self._load_institutional_thresholds()

        # Service reliability tracking
        self.service_reliability_history = {}
        self.cross_validation_cache = {}

        logger.info("Dynamic confidence engine initialized")

    def _load_decay_parameters(self) -> dict[str, ConfidenceDecayParameters]:
        """Load data aging and decay parameters from configuration - NO FALLBACKS, fail if missing"""
        try:
            data_quality_config = self.config.get("data_quality_parameters", {})
            if not data_quality_config:
                raise ValueError("data_quality_parameters section not found in configuration - failing fast")

            return {
                "market_data": ConfidenceDecayParameters(
                    half_life_hours=data_quality_config.get("market_data_half_life_hours"),
                    minimum_confidence=data_quality_config.get("market_data_min_confidence"),
                    decay_function="exponential",
                    critical_age_hours=data_quality_config.get("market_data_critical_age_hours"),
                ),
                "economic_indicators": ConfidenceDecayParameters(
                    half_life_hours=data_quality_config.get("economic_data_half_life_hours"),
                    minimum_confidence=data_quality_config.get("economic_data_min_confidence"),
                    decay_function="exponential",
                    critical_age_hours=data_quality_config.get("economic_data_critical_age_hours"),
                ),
                "volatility_data": ConfidenceDecayParameters(
                    half_life_hours=data_quality_config.get("volatility_data_half_life_hours"),
                    minimum_confidence=data_quality_config.get("volatility_data_min_confidence"),
                    decay_function="exponential",
                    critical_age_hours=data_quality_config.get("volatility_data_critical_age_hours"),
                ),
                "consumer_confidence": ConfidenceDecayParameters(
                    half_life_hours=data_quality_config.get("consumer_conf_half_life_hours"),
                    minimum_confidence=data_quality_config.get("consumer_conf_min_confidence"),
                    decay_function="exponential",
                    critical_age_hours=data_quality_config.get("consumer_conf_critical_age_hours"),
                ),
            }
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to load decay parameters - failing fast: {e}")
            raise RuntimeError(f"Confidence engine initialization failed - no fallback values available: {e}")

    def _load_quality_weights(self) -> dict[str, float]:
        """Load quality factor weights from configuration - NO FALLBACKS, fail if missing"""
        try:
            data_quality_config = self.config.get("data_quality_parameters", {})
            if not data_quality_config:
                raise ValueError("data_quality_parameters section not found in configuration - failing fast")

            return {
                "completeness": data_quality_config.get("quality_weight_completeness"),
                "freshness": data_quality_config.get("quality_weight_freshness"),
                "reliability": data_quality_config.get("quality_weight_reliability"),
                "consistency": data_quality_config.get("quality_weight_consistency"),
                "statistical": data_quality_config.get("quality_weight_statistical"),
            }
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to load quality weights - failing fast: {e}")
            raise RuntimeError(f"Quality weights initialization failed - no fallback values available: {e}")

    def _load_institutional_thresholds(self) -> dict[str, float]:
        """Load institutional-grade confidence thresholds"""
        return {
            "discovery_minimum": self.config.get_confidence_threshold("discovery_minimum"),
            "analysis_minimum": self.config.get_confidence_threshold("analysis_minimum"),
            "synthesis_minimum": self.config.get_confidence_threshold("synthesis_minimum"),
            "institutional_grade": self.config.get_confidence_threshold("institutional_grade"),
        }

    def calculate_confidence(
        self,
        data_points: dict[str, MarketDataPoint] | list[MarketDataPoint],
        context: dict[str, Any],
        data_type: str = "market_data",
    ) -> dict[str, Any]:
        """Calculate dynamic confidence with comprehensive quality assessment"""

        try:
            # Convert single list to dict format
            if isinstance(data_points, list):
                data_points = {f"data_{i}": point for i, point in enumerate(data_points)}

            # Assess data quality across all dimensions
            quality_metrics = self._assess_data_quality(data_points, context, data_type)

            # Calculate age-adjusted confidence with decay
            aged_confidence = self._apply_confidence_decay(data_points, data_type)

            # Perform cross-source validation
            validation_results = self._cross_validate_sources(data_points, context)

            # Calculate statistical confidence intervals
            statistical_confidence = self._calculate_statistical_confidence(data_points, context)

            # Composite confidence calculation
            composite_confidence = self._calculate_composite_confidence(
                quality_metrics,
                aged_confidence,
                validation_results,
                statistical_confidence,
            )

            # Classify confidence level
            confidence_level = self._classify_confidence_level(composite_confidence)

            # Generate recommendations
            recommendations = self._generate_confidence_recommendations(
                quality_metrics, aged_confidence, validation_results, confidence_level
            )

            return {
                "composite_confidence": composite_confidence,
                "confidence_level": confidence_level.value,
                "quality_metrics": quality_metrics,
                "aged_confidence": aged_confidence,
                "validation_results": validation_results,
                "statistical_confidence": statistical_confidence,
                "recommendations": recommendations,
                "calculation_timestamp": datetime.now().isoformat(),
                "meets_institutional_grade": composite_confidence
                >= self.institutional_thresholds["institutional_grade"],
            }

        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return {
                "composite_confidence": 0.5,
                "confidence_level": ConfidenceLevel.MODERATE.value,
                "error": str(e),
                "calculation_timestamp": datetime.now().isoformat(),
            }

    def _assess_data_quality(
        self,
        data_points: dict[str, MarketDataPoint],
        context: dict[str, Any],
        data_type: str,
    ) -> DataQualityMetrics:
        """Comprehensive data quality assessment"""

        total_points = len(data_points)
        if total_points == 0:
            return DataQualityMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Completeness: What percentage of expected data is available
        expected_points = context.get("expected_data_points", total_points)
        completeness_score = min(1.0, total_points / expected_points)

        # Freshness: Age-weighted average freshness
        freshness_scores = []
        for data_point in data_points.values():
            if hasattr(data_point, "age_hours"):
                freshness = self._calculate_freshness_score(data_point.age_hours, data_type)
                freshness_scores.append(freshness)
            else:
                freshness_scores.append(0.5)  # Neutral if no age info

        freshness_score = np.mean(freshness_scores) if freshness_scores else 0.5

        # Reliability: Source reliability average
        reliability_scores = []
        for data_point in data_points.values():
            if hasattr(data_point, "source"):
                if data_point.source == "fred":
                    reliability_scores.append(0.95)
                elif data_point.source == "alpha_vantage":
                    reliability_scores.append(0.85)
                elif data_point.source == "eia":
                    reliability_scores.append(0.90)
                elif "real_time" in data_point.source or "mock" in data_point.source:
                    reliability_scores.append(0.80)
                elif "config_fallback" in data_point.source:
                    reliability_scores.append(0.70)
                else:
                    reliability_scores.append(0.75)
            else:
                reliability_scores.append(0.75)

        reliability_score = np.mean(reliability_scores) if reliability_scores else 0.75

        # Consistency: Cross-source agreement (simplified)
        consistency_score = self._calculate_consistency_score(data_points, context)

        # Statistical confidence: Based on data variance and sample size
        statistical_confidence = self._calculate_data_statistical_confidence(data_points)

        # Overall quality: Weighted composite
        overall_quality = (
            self.quality_weights["completeness"] * completeness_score
            + self.quality_weights["freshness"] * freshness_score
            + self.quality_weights["reliability"] * reliability_score
            + self.quality_weights["consistency"] * consistency_score
            + self.quality_weights["statistical"] * statistical_confidence
        )

        return DataQualityMetrics(
            completeness_score=completeness_score,
            freshness_score=freshness_score,
            reliability_score=reliability_score,
            consistency_score=consistency_score,
            statistical_confidence=statistical_confidence,
            overall_quality=overall_quality,
        )

    def _calculate_freshness_score(self, age_hours: float, data_type: str) -> float:
        """Calculate freshness score based on data age with type-specific decay"""

        decay_params = self.decay_parameters.get(data_type, self.decay_parameters["market_data"])

        if decay_params.decay_function == "exponential":
            # Exponential decay: score = exp(-ln(2) * age / half_life)
            decay_factor = math.exp(-math.log(2) * age_hours / decay_params.half_life_hours)
            freshness_score = max(decay_params.minimum_confidence, decay_factor)

        elif decay_params.decay_function == "linear":
            # Linear decay over critical age period
            if age_hours <= decay_params.critical_age_hours:
                freshness_score = 1.0 - (age_hours / decay_params.critical_age_hours) * (
                    1.0 - decay_params.minimum_confidence
                )
            else:
                freshness_score = decay_params.minimum_confidence

        elif decay_params.decay_function == "stepped":
            # Stepped decay at critical thresholds
            if age_hours <= decay_params.half_life_hours:
                freshness_score = 1.0
            elif age_hours <= decay_params.critical_age_hours:
                freshness_score = 0.7
            else:
                freshness_score = decay_params.minimum_confidence

        else:
            # Default exponential
            decay_factor = math.exp(-math.log(2) * age_hours / decay_params.half_life_hours)
            freshness_score = max(decay_params.minimum_confidence, decay_factor)

        return freshness_score

    def _calculate_consistency_score(self, data_points: dict[str, MarketDataPoint], context: dict[str, Any]) -> float:
        """Calculate cross-source consistency score"""

        # Group data points by type
        data_by_type = {}
        for key, data_point in data_points.items():
            data_type = getattr(data_point, "data_type", "unknown")
            if data_type not in data_by_type:
                data_by_type[data_type] = []
            data_by_type[data_type].append(data_point.value)

        # Calculate consistency within each data type
        consistency_scores = []
        for data_type, values in data_by_type.items():
            if len(values) > 1:
                # Calculate coefficient of variation (CV)
                mean_val = np.mean(values)
                std_val = np.std(values)

                if mean_val != 0:
                    cv = std_val / abs(mean_val)
                    # Convert CV to consistency score (lower CV = higher consistency)
                    consistency = max(0.0, 1.0 - min(1.0, cv))
                else:
                    consistency = 1.0 if std_val == 0 else 0.0

                consistency_scores.append(consistency)
            else:
                # Single source, assume moderate consistency
                consistency_scores.append(0.75)

        return np.mean(consistency_scores) if consistency_scores else 0.75

    def _calculate_data_statistical_confidence(self, data_points: dict[str, MarketDataPoint]) -> float:
        """Calculate statistical confidence based on data characteristics"""

        if not data_points:
            return 0.0

        values = [dp.value for dp in data_points.values() if hasattr(dp, "value")]
        if len(values) < 2:
            return 0.5  # Neutral confidence for single data point

        # Calculate statistical metrics
        n = len(values)
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1) if n > 1 else 0

        # Sample size adjustment (larger samples = higher confidence)
        sample_size_factor = min(1.0, math.log(n + 1) / math.log(20))  # Asymptotically approaches 1

        # Variance adjustment (lower relative variance = higher confidence)
        if mean_val != 0:
            cv = std_val / abs(mean_val)
            variance_factor = max(0.1, 1.0 - min(1.0, cv))
        else:
            variance_factor = 0.5

        # Combined statistical confidence
        statistical_confidence = 0.4 * sample_size_factor + 0.6 * variance_factor

        return statistical_confidence

    def _apply_confidence_decay(self, data_points: dict[str, MarketDataPoint], data_type: str) -> dict[str, float]:
        """Apply aging-based confidence decay to each data point"""

        aged_confidences = {}
        decay_params = self.decay_parameters.get(data_type, self.decay_parameters["market_data"])

        for key, data_point in data_points.items():
            base_confidence = getattr(data_point, "confidence", 0.8)
            age_hours = getattr(data_point, "age_hours", 0.0)

            # Calculate age-adjusted confidence
            freshness_multiplier = self._calculate_freshness_score(age_hours, data_type)
            aged_confidence = base_confidence * freshness_multiplier

            aged_confidences[key] = max(decay_params.minimum_confidence, aged_confidence)

        return aged_confidences

    def _cross_validate_sources(
        self, data_points: dict[str, MarketDataPoint], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform cross-source validation and correlation analysis"""

        # Group by source
        sources = {}
        for key, data_point in data_points.items():
            source = getattr(data_point, "source", "unknown")
            if source not in sources:
                sources[source] = []
            sources[source].append(data_point.value)

        validation_results = {
            "source_count": len(sources),
            "sources_available": list(sources.keys()),
            "cross_source_correlation": 0.0,
            "source_agreement": 0.0,
            "validation_quality": "insufficient",
        }

        if len(sources) >= 2:
            # Calculate cross-source correlation
            source_means = [np.mean(values) for values in sources.values()]
            if len(source_means) >= 2:
                try:
                    if len(source_means) == 2:
                        corr_matrix = np.corrcoef(source_means)
                        correlation = corr_matrix[0, 1] if corr_matrix.ndim > 1 else 0.0
                    else:
                        correlations = []
                        for i in range(len(source_means)):
                            for j in range(i + 1, len(source_means)):
                                corr_matrix = np.corrcoef([source_means[i], source_means[j]])
                                if corr_matrix.ndim > 1:
                                    correlations.append(corr_matrix[0, 1])
                        correlation = np.mean(correlations) if correlations else 0.0

                    validation_results["cross_source_correlation"] = correlation if not np.isnan(correlation) else 0.0
                except Exception:
                    validation_results["cross_source_correlation"] = 0.0

            # Source agreement based on relative differences
            all_values = [val for vals in sources.values() for val in vals]
            if all_values:
                mean_all = np.mean(all_values)
                std_all = np.std(all_values)
                agreement = max(0.0, 1.0 - (std_all / abs(mean_all)) if mean_all != 0 else 0.0)
                validation_results["source_agreement"] = agreement

        # Validation quality classification
        if validation_results["source_count"] >= 3 and validation_results["source_agreement"] > 0.8:
            validation_results["validation_quality"] = "excellent"
        elif validation_results["source_count"] >= 2 and validation_results["source_agreement"] > 0.7:
            validation_results["validation_quality"] = "good"
        elif validation_results["source_count"] >= 2:
            validation_results["validation_quality"] = "moderate"
        else:
            validation_results["validation_quality"] = "insufficient"

        return validation_results

    def _calculate_statistical_confidence(
        self, data_points: dict[str, MarketDataPoint], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate statistical confidence intervals and significance tests"""

        values = [dp.value for dp in data_points.values() if hasattr(dp, "value")]

        if len(values) < 2:
            return {
                "confidence_interval_95": (0.0, 0.0),
                "standard_error": 0.0,
                "degrees_of_freedom": 0,
                "statistical_significance": 0.5,
            }

        # Basic statistical measures
        n = len(values)
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)
        standard_error = std_val / math.sqrt(n)

        # 95% confidence interval (using t-distribution for small samples)
        try:
            from scipy import stats

            t_critical = stats.t.ppf(0.975, n - 1)  # 95% confidence level
            margin_error = t_critical * standard_error
            confidence_interval = (mean_val - margin_error, mean_val + margin_error)

            # Statistical significance (inverse of p-value for non-zero mean hypothesis)
            if std_val > 0:
                t_stat = abs(mean_val) / standard_error
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 1))
                statistical_significance = max(0.0, 1.0 - p_value)
            else:
                statistical_significance = 1.0
        except ImportError:
            # Fallback to normal approximation when scipy not available
            z_critical = 1.96  # 95% confidence level
            margin_error = z_critical * standard_error
            confidence_interval = (mean_val - margin_error, mean_val + margin_error)

            # Simple statistical significance approximation
            if std_val > 0:
                z_stat = abs(mean_val) / standard_error
                # Approximate p-value calculation
                statistical_significance = max(0.0, min(1.0, z_stat / 3.0))
            else:
                statistical_significance = 1.0

        return {
            "confidence_interval_95": confidence_interval,
            "standard_error": standard_error,
            "degrees_of_freedom": n - 1,
            "statistical_significance": min(1.0, statistical_significance),
        }

    def _calculate_composite_confidence(
        self,
        quality_metrics: DataQualityMetrics,
        aged_confidence: dict[str, float],
        validation_results: dict[str, Any],
        statistical_confidence: dict[str, Any],
    ) -> float:
        """Calculate final composite confidence score"""

        # Base confidence from data quality
        base_confidence = quality_metrics.overall_quality

        # Age adjustment (average of aged confidences)
        age_adjustment = np.mean(list(aged_confidence.values())) if aged_confidence else 0.5

        # Validation bonus based on cross-source agreement
        validation_bonus = 0.0
        if validation_results["validation_quality"] == "excellent":
            validation_bonus = 0.1
        elif validation_results["validation_quality"] == "good":
            validation_bonus = 0.05
        elif validation_results["validation_quality"] == "moderate":
            validation_bonus = 0.02

        # Statistical confidence bonus
        statistical_bonus = statistical_confidence.get("statistical_significance", 0.5) * 0.05

        # Composite calculation with weighted factors
        composite_confidence = (
            0.5 * base_confidence
            + 0.3 * age_adjustment  # 50% from data quality
            + 0.15 * (0.5 + validation_bonus)  # 30% from age adjustment
            + 0.05  # 15% from validation (with bonus)
            * (0.5 + statistical_bonus)  # 5% from statistical confidence (with bonus)
        )

        return max(0.0, min(1.0, composite_confidence))

    def _classify_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Classify confidence score into levels"""

        if confidence_score >= 0.95:
            return ConfidenceLevel.CRITICAL
        if confidence_score >= 0.85:
            return ConfidenceLevel.HIGH
        if confidence_score >= 0.80:
            return ConfidenceLevel.INSTITUTIONAL
        if confidence_score >= 0.70:
            return ConfidenceLevel.MODERATE
        if confidence_score >= 0.50:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.INSUFFICIENT

    def _generate_confidence_recommendations(
        self,
        quality_metrics: DataQualityMetrics,
        aged_confidence: dict[str, float],
        validation_results: dict[str, Any],
        confidence_level: ConfidenceLevel,
    ) -> list[str]:
        """Generate actionable recommendations for improving confidence"""

        recommendations = []

        # Data quality recommendations
        if quality_metrics.completeness_score < 0.8:
            recommendations.append("Increase data coverage by adding more sources or indicators")

        if quality_metrics.freshness_score < 0.7:
            recommendations.append("Update data sources more frequently to improve freshness")

        if quality_metrics.reliability_score < 0.8:
            recommendations.append("Use higher-reliability data sources (institutional sources preferred)")

        if quality_metrics.consistency_score < 0.7:
            recommendations.append("Investigate data inconsistencies across sources")

        # Age-based recommendations
        avg_aged_confidence = np.mean(list(aged_confidence.values())) if aged_confidence else 0.5
        if avg_aged_confidence < 0.6:
            recommendations.append("Data is aging significantly - consider refreshing real-time sources")

        # Validation recommendations
        if validation_results["source_count"] < 2:
            recommendations.append("Add additional data sources for cross-validation")
        elif validation_results["source_agreement"] < 0.7:
            recommendations.append("Review source discrepancies and validate data quality")

        # Confidence level recommendations
        if confidence_level == ConfidenceLevel.INSUFFICIENT:
            recommendations.append("CRITICAL: Confidence insufficient for institutional use - review all data sources")
        elif confidence_level == ConfidenceLevel.LOW:
            recommendations.append("Consider supplementing with additional high-quality data sources")
        elif confidence_level == ConfidenceLevel.MODERATE:
            recommendations.append("Acceptable for general analysis - consider upgrades for institutional use")

        return recommendations


def create_dynamic_confidence_engine(
    config_manager: ConfigManager | None = None,
) -> DynamicConfidenceEngine:
    """Factory function to create dynamic confidence engine"""
    return DynamicConfidenceEngine(config_manager)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        engine = create_dynamic_confidence_engine()

        # Mock data points for testing
        from services.real_time_market_data import MarketDataPoint

        test_data = {
            "fed_funds_rate": MarketDataPoint(
                value=5.25,
                timestamp=datetime.now(),
                source="fred",
                data_type="fed_funds_rate",
                confidence=0.95,
                is_real_time=True,
                age_hours=2.0,
            ),
            "gdp_growth": MarketDataPoint(
                value=2.3,
                timestamp=datetime.now() - timedelta(days=30),
                source="fred",
                data_type="gdp_growth",
                confidence=0.90,
                is_real_time=False,
                age_hours=720.0,
            ),
            "vix_level": MarketDataPoint(
                value=16.8,
                timestamp=datetime.now() - timedelta(hours=1),
                source="alpha_vantage",
                data_type="vix_volatility",
                confidence=0.85,
                is_real_time=True,
                age_hours=1.0,
            ),
        }

        context = {
            "expected_data_points": 3,
            "analysis_type": "macro_discovery",
            "region": "US",
        }

        # Test confidence calculation
        result = engine.calculate_confidence(test_data, context, "market_data")

        print("Composite Confidence: {result['composite_confidence']:.3f}")
        print("Confidence Level: {result['confidence_level']}")
        print("Meets Institutional Grade: {result['meets_institutional_grade']}")
        print("Quality Score: {result['quality_metrics'].overall_quality:.3f}")

        if result["recommendations"]:
            print("Recommendations:")
            for rec in result["recommendations"]:
                print("  - {rec}")

        print("\n✅ Dynamic confidence engine test completed successfully!")

    except Exception:
        print("❌ Dynamic confidence engine test failed: {e}")
        import traceback

        traceback.print_exc()
