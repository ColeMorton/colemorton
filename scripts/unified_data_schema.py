#!/usr/bin/env python3
"""
Unified Data Schema

Standardized data structures for all Twitter content types:
- Common data schema definitions
- Data validation and normalization
- Cross-content type compatibility
- Template-ready data formatting
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContentType(Enum):
    """Content type enumeration"""

    FUNDAMENTAL = "fundamental"
    STRATEGY = "strategy"
    SECTOR = "sector"
    TRADE_HISTORY = "trade_history"


class ValidationStatus(Enum):
    """Validation status enumeration"""

    COMPLIANT = "COMPLIANT"
    FLAGGED = "FLAGGED"
    NON_COMPLIANT = "NON_COMPLIANT"


class QualityGrade(Enum):
    """Quality grade enumeration"""

    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    F = "F"


@dataclass
class BaseMetadata:
    """Base metadata for all content types"""

    content_type: ContentType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    framework_version: str = "1.0"
    generated_by: str = "unified_twitter_system"
    institutional_compliant: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content_type": self.content_type.value,
            "timestamp": self.timestamp,
            "framework_version": self.framework_version,
            "generated_by": self.generated_by,
            "institutional_compliant": self.institutional_compliant,
        }


@dataclass
class ValidationResult:
    """Standard validation result structure"""

    score: float
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "score": self.score,
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


@dataclass
class OverallAssessment:
    """Overall assessment structure"""

    overall_reliability_score: float
    content_quality_grade: QualityGrade
    engagement_potential_score: float
    compliance_status: ValidationStatus
    ready_for_publication: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "overall_reliability_score": f"{self.overall_reliability_score:.1f}/10.0",
            "content_quality_grade": self.content_quality_grade.value,
            "engagement_potential_score": f"{self.engagement_potential_score:.1f}/10.0",
            "compliance_status": self.compliance_status.value,
            "ready_for_publication": self.ready_for_publication,
        }


@dataclass
class CriticalFindingsMatrix:
    """Critical findings matrix structure"""

    verified_accurate_claims: list[str] = field(default_factory=list)
    questionable_assertions: list[str] = field(default_factory=list)
    inaccurate_statements: list[str] = field(default_factory=list)
    unverifiable_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "verified_accurate_claims": self.verified_accurate_claims,
            "questionable_assertions": self.questionable_assertions,
            "inaccurate_statements": self.inaccurate_statements,
            "unverifiable_claims": self.unverifiable_claims,
        }


@dataclass
class ActionableRecommendations:
    """Actionable recommendations structure"""

    required_corrections: dict[str, list[str]] = field(
        default_factory=lambda: {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
        }
    )
    optimization_opportunities: dict[str, list[str]] = field(
        default_factory=lambda: {
            "engagement_improvements": [],
            "accuracy_enhancements": [],
            "compliance_reinforcement": [],
        }
    )
    monitoring_requirements: dict[str, str] = field(
        default_factory=lambda: {
            "real_time_validation": "",
            "performance_tracking": "",
            "feedback_integration": "",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "required_corrections": self.required_corrections,
            "optimization_opportunities": self.optimization_opportunities,
            "monitoring_requirements": self.monitoring_requirements,
        }


@dataclass
class FundamentalDataSchema:
    """Fundamental analysis data schema"""

    # Core identification
    ticker: str
    date: str
    company_name: str | None = None
    sector: str | None = None
    industry: str | None = None

    # Market data
    current_price: float | None = None
    market_cap: float | None = None
    beta: float | None = None

    # Valuation data
    fair_value: float | None = None
    fair_value_low: float | None = None
    fair_value_high: float | None = None
    weighted_fair_value: float | None = None
    dcf_value: float | None = None
    valuation_methods: list[dict[str, Any]] = field(default_factory=list)
    valuation_confidence: float | None = None

    # Investment thesis
    investment_thesis: str | None = None
    recommendation: str | None = None
    conviction: float | None = None

    # Catalysts
    catalysts: list[dict[str, Any]] = field(default_factory=list)
    catalyst_count: int | None = None
    total_catalyst_impact: float | None = None

    # Moat analysis
    moat_strength: float | None = None
    competitive_advantages: list[dict[str, Any]] = field(default_factory=list)
    pricing_power: str | None = None

    # Contrarian analysis
    contrarian_insight: str | None = None
    common_perception: str | None = None
    mispricing_percentage: float | None = None

    # Financial health
    financial_health_score: float | None = None
    profitability_grade: str | None = None
    balance_sheet_grade: str | None = None
    cash_flow_grade: str | None = None
    financial_grades: dict[str, Any] | None = None

    # Quality metrics
    overall_confidence: float | None = None
    data_quality: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ticker": self.ticker,
            "date": self.date,
            "company_name": self.company_name,
            "sector": self.sector,
            "industry": self.industry,
            "current_price": self.current_price,
            "market_cap": self.market_cap,
            "beta": self.beta,
            "fair_value": self.fair_value,
            "fair_value_low": self.fair_value_low,
            "fair_value_high": self.fair_value_high,
            "weighted_fair_value": self.weighted_fair_value,
            "dcf_value": self.dcf_value,
            "valuation_methods": self.valuation_methods,
            "valuation_confidence": self.valuation_confidence,
            "investment_thesis": self.investment_thesis,
            "recommendation": self.recommendation,
            "conviction": self.conviction,
            "catalysts": self.catalysts,
            "catalyst_count": self.catalyst_count,
            "total_catalyst_impact": self.total_catalyst_impact,
            "moat_strength": self.moat_strength,
            "competitive_advantages": self.competitive_advantages,
            "pricing_power": self.pricing_power,
            "contrarian_insight": self.contrarian_insight,
            "common_perception": self.common_perception,
            "mispricing_percentage": self.mispricing_percentage,
            "financial_health_score": self.financial_health_score,
            "profitability_grade": self.profitability_grade,
            "balance_sheet_grade": self.balance_sheet_grade,
            "cash_flow_grade": self.cash_flow_grade,
            "financial_grades": self.financial_grades,
            "overall_confidence": self.overall_confidence,
            "data_quality": self.data_quality,
        }


@dataclass
class StrategyDataSchema:
    """Strategy data schema"""

    # Core identification
    ticker: str
    date: str

    # Strategy parameters
    strategy_type: str | None = None
    short_window: int | None = None
    long_window: int | None = None
    period: str | None = None

    # Performance metrics
    net_performance: float | None = None
    win_rate: float | None = None
    total_trades: int | None = None
    avg_win: float | None = None
    avg_loss: float | None = None
    reward_risk_ratio: float | None = None
    max_drawdown: float | None = None
    buy_hold_drawdown: float | None = None
    sharpe: float | None = None
    sortino: float | None = None
    exposure: float | None = None
    avg_trade_length: float | None = None
    expectancy: float | None = None

    # Seasonality data
    current_month: str | None = None
    current_month_performance: float | None = None
    current_month_avg: float | None = None
    best_months: str | None = None
    best_months_performance: float | None = None
    worst_months: str | None = None
    worst_months_performance: float | None = None
    seasonality_strength: str | None = None

    # Live signal context
    signal_triggered: bool | None = None
    current_price: float | None = None
    technical_setup: str | None = None
    fundamental_catalyst: str | None = None
    market_context: str | None = None
    risk_management: str | None = None

    # Additional context
    hook: str | None = None
    key_insight: str | None = None
    conviction_level: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ticker": self.ticker,
            "date": self.date,
            "strategy_type": self.strategy_type,
            "short_window": self.short_window,
            "long_window": self.long_window,
            "period": self.period,
            "net_performance": self.net_performance,
            "win_rate": self.win_rate,
            "total_trades": self.total_trades,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "reward_risk_ratio": self.reward_risk_ratio,
            "max_drawdown": self.max_drawdown,
            "buy_hold_drawdown": self.buy_hold_drawdown,
            "sharpe": self.sharpe,
            "sortino": self.sortino,
            "exposure": self.exposure,
            "avg_trade_length": self.avg_trade_length,
            "expectancy": self.expectancy,
            "current_month": self.current_month,
            "current_month_performance": self.current_month_performance,
            "current_month_avg": self.current_month_avg,
            "best_months": self.best_months,
            "best_months_performance": self.best_months_performance,
            "worst_months": self.worst_months,
            "worst_months_performance": self.worst_months_performance,
            "seasonality_strength": self.seasonality_strength,
            "signal_triggered": self.signal_triggered,
            "current_price": self.current_price,
            "technical_setup": self.technical_setup,
            "fundamental_catalyst": self.fundamental_catalyst,
            "market_context": self.market_context,
            "risk_management": self.risk_management,
            "hook": self.hook,
            "key_insight": self.key_insight,
            "conviction_level": self.conviction_level,
        }


@dataclass
class SectorDataSchema:
    """Sector analysis data schema"""

    # Core identification
    sector_name: str
    date: str

    # Sector positioning
    allocation_recommendation: str | None = None
    overweight_underweight: str | None = None
    conviction_level: float | None = None

    # Performance metrics
    relative_performance: float | None = None
    outperformance: float | None = None
    ytd_return: float | None = None
    performance_ranking: int | None = None

    # Rotation analysis
    rotation_signal: bool | None = None
    rotation_score: float | None = None
    economic_cycle_position: str | None = None

    # Valuation metrics
    relative_valuation: float | None = None
    pe_vs_spy: float | None = None
    pb_vs_tech: float | None = None
    sector_rank: int | None = None

    # Economic sensitivity
    gdp_correlation: float | None = None
    employment_beta: float | None = None
    interest_rate_sensitivity: float | None = None

    # ETF data
    etf_symbol: str | None = None
    etf_price: float | None = None
    etf_flows: str | None = None

    # Quality metrics
    overall_confidence: float | None = None
    data_quality: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "sector_name": self.sector_name,
            "date": self.date,
            "allocation_recommendation": self.allocation_recommendation,
            "overweight_underweight": self.overweight_underweight,
            "conviction_level": self.conviction_level,
            "relative_performance": self.relative_performance,
            "outperformance": self.outperformance,
            "ytd_return": self.ytd_return,
            "performance_ranking": self.performance_ranking,
            "rotation_signal": self.rotation_signal,
            "rotation_score": self.rotation_score,
            "economic_cycle_position": self.economic_cycle_position,
            "relative_valuation": self.relative_valuation,
            "pe_vs_spy": self.pe_vs_spy,
            "pb_vs_tech": self.pb_vs_tech,
            "sector_rank": self.sector_rank,
            "gdp_correlation": self.gdp_correlation,
            "employment_beta": self.employment_beta,
            "interest_rate_sensitivity": self.interest_rate_sensitivity,
            "etf_symbol": self.etf_symbol,
            "etf_price": self.etf_price,
            "etf_flows": self.etf_flows,
            "overall_confidence": self.overall_confidence,
            "data_quality": self.data_quality,
        }


@dataclass
class TradeHistoryDataSchema:
    """Trade history data schema"""

    # Core identification
    analysis_name: str
    date: str

    # Performance metrics
    period_return: float | None = None
    ytd_return: float | None = None
    win_rate: float | None = None
    total_trades: int | None = None
    avg_win: float | None = None
    avg_loss: float | None = None
    profit_factor: float | None = None

    # Portfolio context
    current_holdings: list[dict[str, Any]] | None = None
    portfolio_value: float | None = None
    cash_position: float | None = None

    # Top performers
    best_trades: list[dict[str, Any]] | None = None
    worst_trades: list[dict[str, Any]] | None = None

    # Transparency level
    transparency_level: str | None = None
    full_disclosure: bool | None = None

    # Narrative focus
    narrative_focus: str | None = None
    key_insights: list[str] | None = None

    # Quality metrics
    data_quality_score: float | None = None
    performance_data_quality: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_name": self.analysis_name,
            "date": self.date,
            "period_return": self.period_return,
            "ytd_return": self.ytd_return,
            "win_rate": self.win_rate,
            "total_trades": self.total_trades,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "current_holdings": self.current_holdings,
            "portfolio_value": self.portfolio_value,
            "cash_position": self.cash_position,
            "best_trades": self.best_trades,
            "worst_trades": self.worst_trades,
            "transparency_level": self.transparency_level,
            "full_disclosure": self.full_disclosure,
            "narrative_focus": self.narrative_focus,
            "key_insights": self.key_insights,
            "data_quality_score": self.data_quality_score,
            "performance_data_quality": self.performance_data_quality,
        }


@dataclass
class UnifiedValidationOutput:
    """Unified validation output schema"""

    metadata: BaseMetadata
    overall_assessment: OverallAssessment
    validation_breakdown: dict[str, dict[str, ValidationResult]]
    critical_findings_matrix: CriticalFindingsMatrix
    actionable_recommendations: ActionableRecommendations
    methodology_notes: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        # Convert validation breakdown
        validation_breakdown_dict = {}
        for category, results in self.validation_breakdown.items():
            validation_breakdown_dict[category] = {}
            for criterion, result in results.items():
                validation_breakdown_dict[category][criterion] = result.to_dict()

        return {
            "metadata": self.metadata.to_dict(),
            "overall_assessment": self.overall_assessment.to_dict(),
            "validation_breakdown": validation_breakdown_dict,
            "critical_findings_matrix": self.critical_findings_matrix.to_dict(),
            "actionable_recommendations": self.actionable_recommendations.to_dict(),
            "methodology_notes": self.methodology_notes,
        }


class UnifiedDataSchema:
    """Unified data schema manager"""

    def __init__(self):
        """Initialize the schema manager"""
        self.schema_registry = {
            ContentType.FUNDAMENTAL: FundamentalDataSchema,
            ContentType.STRATEGY: StrategyDataSchema,
            ContentType.SECTOR: SectorDataSchema,
            ContentType.TRADE_HISTORY: TradeHistoryDataSchema,
        }

    def create_data_schema(
        self, content_type: ContentType, **kwargs
    ) -> FundamentalDataSchema | StrategyDataSchema | SectorDataSchema | TradeHistoryDataSchema:
        """Create a data schema instance"""
        schema_class = self.schema_registry.get(content_type)
        if not schema_class:
            raise ValueError(f"Unknown content type: {content_type}")

        return schema_class(**kwargs)

    def validate_data_schema(self, data: dict[str, Any], content_type: ContentType) -> dict[str, Any]:
        """Validate data against schema"""
        schema_class = self.schema_registry.get(content_type)
        if not schema_class:
            raise ValueError(f"Unknown content type: {content_type}")

        validation_result = {
            "valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
        }

        # Check required fields (simplified validation)
        if content_type == ContentType.FUNDAMENTAL:
            required_fields = ["ticker", "date"]
        elif content_type == ContentType.STRATEGY:
            required_fields = ["ticker", "date", "strategy_type"]
        elif content_type == ContentType.SECTOR:
            required_fields = ["sector_name", "date"]
        elif content_type == ContentType.TRADE_HISTORY:
            required_fields = ["analysis_name", "date"]
        else:
            required_fields = []

        for required_field in required_fields:
            if required_field not in data or data[required_field] is None:
                validation_result["missing_fields"].append(required_field)
                validation_result["valid"] = False

        return validation_result

    def normalize_data(self, data: dict[str, Any], content_type: ContentType) -> dict[str, Any]:
        """Normalize data to schema format"""
        schema_class = self.schema_registry.get(content_type)
        if not schema_class:
            raise ValueError(f"Unknown content type: {content_type}")

        # Create schema instance with available data
        try:
            schema_instance = schema_class(**{k: v for k, v in data.items() if k in schema_class.__annotations__})
            return schema_instance.to_dict()
        except Exception:
            # Return original data if normalization fails
            return data

    def create_validation_output(
        self,
        content_type: ContentType,
        overall_score: float,
        validation_results: dict[str, Any],
        findings: dict[str, Any] | None = None,
        recommendations: dict[str, Any] | None = None,
    ) -> UnifiedValidationOutput:
        """Create unified validation output"""

        # Create metadata
        metadata = BaseMetadata(content_type=content_type, institutional_compliant=overall_score >= 9.0)

        # Create overall assessment
        def score_to_grade(score: float) -> QualityGrade:
            if score >= 9.5:
                return QualityGrade.A_PLUS
            if score >= 9.0:
                return QualityGrade.A
            if score >= 8.5:
                return QualityGrade.B_PLUS
            if score >= 8.0:
                return QualityGrade.B
            if score >= 7.0:
                return QualityGrade.C
            return QualityGrade.F

        def score_to_status(score: float) -> ValidationStatus:
            if score >= 9.5:
                return ValidationStatus.COMPLIANT
            if score >= 8.5:
                return ValidationStatus.FLAGGED
            return ValidationStatus.NON_COMPLIANT

        overall_assessment = OverallAssessment(
            overall_reliability_score=overall_score,
            content_quality_grade=score_to_grade(overall_score),
            engagement_potential_score=min(overall_score + 0.5, 10.0),
            compliance_status=score_to_status(overall_score),
            ready_for_publication=overall_score >= 8.5,
        )

        # Create validation breakdown
        validation_breakdown = {}
        for category, results in validation_results.items():
            validation_breakdown[category] = {}
            for criterion, result in results.items():
                if isinstance(result, dict):
                    validation_breakdown[category][criterion] = ValidationResult(
                        score=result.get("score", 0.0),
                        issues=result.get("issues", []),
                        warnings=result.get("warnings", []),
                        recommendations=result.get("recommendations", []),
                    )

        # Create findings matrix
        critical_findings = CriticalFindingsMatrix()
        if findings:
            critical_findings = CriticalFindingsMatrix(
                verified_accurate_claims=findings.get("verified_accurate_claims", []),
                questionable_assertions=findings.get("questionable_assertions", []),
                inaccurate_statements=findings.get("inaccurate_statements", []),
                unverifiable_claims=findings.get("unverifiable_claims", []),
            )

        # Create recommendations
        actionable_recommendations = ActionableRecommendations()
        if recommendations:
            actionable_recommendations = ActionableRecommendations(
                required_corrections=recommendations.get("required_corrections", {}),
                optimization_opportunities=recommendations.get("optimization_opportunities", {}),
                monitoring_requirements=recommendations.get("monitoring_requirements", {}),
            )

        # Create methodology notes
        methodology_notes = {
            "validation_framework": "unified_schema_v1.0",
            "schema_compliance": "enforced",
            "data_normalization": "applied",
            "validation_timestamp": datetime.now().isoformat(),
        }

        return UnifiedValidationOutput(
            metadata=metadata,
            overall_assessment=overall_assessment,
            validation_breakdown=validation_breakdown,
            critical_findings_matrix=critical_findings,
            actionable_recommendations=actionable_recommendations,
            methodology_notes=methodology_notes,
        )

    def get_schema_definition(self, content_type: ContentType) -> dict[str, Any]:
        """Get schema definition for content type"""
        schema_class = self.schema_registry.get(content_type)
        if not schema_class:
            raise ValueError(f"Unknown content type: {content_type}")

        return {
            "content_type": content_type.value,
            "schema_class": schema_class.__name__,
            "fields": list(schema_class.__annotations__.keys()),
            "required_fields": self._get_required_fields(content_type),
        }

    def _get_required_fields(self, content_type: ContentType) -> list[str]:
        """Get required fields for content type"""
        if content_type == ContentType.FUNDAMENTAL:
            return ["ticker", "date"]
        if content_type == ContentType.STRATEGY:
            return ["ticker", "date", "strategy_type"]
        if content_type == ContentType.SECTOR:
            return ["sector_name", "date"]
        if content_type == ContentType.TRADE_HISTORY:
            return ["analysis_name", "date"]
        return []

    def get_available_schemas(self) -> list[dict[str, Any]]:
        """Get list of available schemas"""
        return [self.get_schema_definition(content_type) for content_type in self.schema_registry.keys()]
