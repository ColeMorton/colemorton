#!/usr/bin/env python3
"""
DASV Workflow Orchestrator

High-level orchestrator for managing complete DASV workflows across all domains.
Provides workflow templates, dependency management, quality gates, and orchestration
patterns for institutional-grade analysis execution.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from command_execution_service import (
    CommandExecutionService,
    ExecutionMode,
    ExecutionResult,
    ExecutionStatus,
)


class WorkflowStatus(Enum):
    """Overall workflow status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"
    QUALITY_GATE_FAILED = "quality_gate_failed"


class QualityGateResult(Enum):
    """Quality gate evaluation results"""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class WorkflowPhaseResult:
    """Result of a single workflow phase"""

    phase: str
    execution_result: ExecutionResult
    quality_gate_result: QualityGateResult
    confidence_score: float | None = None
    quality_issues: list[str] = field(default_factory=list)
    passed_to_next_phase: bool = False


@dataclass
class WorkflowResult:
    """Complete workflow execution result"""

    workflow_id: str
    domain: str
    status: WorkflowStatus
    start_time: datetime
    end_time: datetime | None = None
    phase_results: dict[str, WorkflowPhaseResult] = field(default_factory=dict)
    final_outputs: list[str] = field(default_factory=list)
    overall_confidence: float | None = None
    quality_summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class DASVWorkflowOrchestrator:
    """
    High-level orchestrator for DASV workflows across all domains.

    Provides:
    - Workflow templates and patterns
    - Quality gate enforcement
    - Dependency management
    - Error handling and recovery
    - Performance monitoring
    - Institutional quality standards
    """

    def __init__(self):
        """Initialize the workflow orchestrator"""
        self.execution_service = CommandExecutionService()
        self.active_workflows = {}

        # Quality gate thresholds
        self.quality_thresholds = {
            "minimum_confidence": 0.9,
            "institutional_confidence": 0.95,
            "data_freshness_hours": 48,
            "validation_score_minimum": 0.9,
        }

        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()

    def _load_workflow_templates(self) -> dict[str, dict[str, Any]]:
        """Load workflow templates for different domains"""
        return {
            "fundamental_analysis": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["data_completeness", "price_accuracy"],
                    "analyze": ["confidence_threshold", "calculation_accuracy"],
                    "synthesize": ["template_compliance", "confidence_threshold"],
                    "validate": ["institutional_quality", "validation_score"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 10,
                    "analyze": 15,
                    "synthesize": 10,
                    "validate": 5,
                },
            },
            "sector_analysis": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["multi_company_coverage", "etf_data_quality"],
                    "analyze": ["sector_consistency", "confidence_threshold"],
                    "synthesize": ["template_compliance", "investment_recommendation"],
                    "validate": ["institutional_quality", "cross_sector_validation"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 15,
                    "analyze": 20,
                    "synthesize": 15,
                    "validate": 10,
                },
            },
            "industry_analysis": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["industry_scope_accuracy", "representative_companies"],
                    "analyze": [
                        "competitive_moat_assessment",
                        "growth_catalyst_validation",
                    ],
                    "synthesize": ["template_compliance", "industry_investment_thesis"],
                    "validate": ["institutional_quality", "industry_validation_score"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 12,
                    "analyze": 18,
                    "synthesize": 12,
                    "validate": 8,
                },
            },
            "comparative_analysis": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["dual_company_data", "data_consistency"],
                    "analyze": ["comparative_methodology", "cross_stock_validation"],
                    "synthesize": ["winner_determination", "portfolio_allocation"],
                    "validate": ["comparative_validation", "cross_stock_accuracy"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 20,
                    "analyze": 25,
                    "synthesize": 15,
                    "validate": 12,
                },
            },
            "macro_analysis": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["economic_data_coverage", "regional_specificity"],
                    "analyze": ["business_cycle_positioning", "policy_assessment"],
                    "synthesize": ["economic_investment_thesis", "policy_implications"],
                    "validate": ["macro_validation_score", "economic_consistency"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 8,
                    "analyze": 12,
                    "synthesize": 10,
                    "validate": 6,
                },
            },
            "trade_history": {
                "phases": ["discover", "analyze", "synthesize", "validate"],
                "quality_gates": {
                    "discover": ["trade_data_completeness", "performance_calculation"],
                    "analyze": ["statistical_significance", "benchmark_comparison"],
                    "synthesize": ["performance_summary", "lessons_learned"],
                    "validate": ["calculation_verification", "report_accuracy"],
                },
                "dependencies": {
                    "analyze": ["discover"],
                    "synthesize": ["discover", "analyze"],
                    "validate": ["discover", "analyze", "synthesize"],
                },
                "timeout_minutes": {
                    "discover": 5,
                    "analyze": 8,
                    "synthesize": 6,
                    "validate": 4,
                },
            },
        }

    def _evaluate_quality_gate(
        self, phase: str, execution_result: ExecutionResult, domain: str
    ) -> tuple[QualityGateResult, list[str]]:
        """Evaluate quality gates for a specific phase"""
        issues = []

        # Basic execution success check
        if execution_result.status == ExecutionStatus.FAILED:
            return QualityGateResult.FAIL, ["Execution failed"]

        # Confidence score check
        if execution_result.confidence_score is not None:
            if execution_result.confidence_score < self.quality_thresholds["minimum_confidence"]:
                issues.append(
                    f"Confidence score {execution_result.confidence_score:.2f} below minimum {self.quality_thresholds['minimum_confidence']}"
                )

        # Output file generation check
        if not execution_result.output_files:
            issues.append("No output files generated")

        # Domain and phase specific checks
        template = self.workflow_templates.get(domain, {})
        phase_gates = template.get("quality_gates", {}).get(phase, [])

        for gate in phase_gates:
            # Placeholder for specific gate implementations
            # In a full implementation, these would be specific validation functions
            if gate == "template_compliance":
                # Check if output follows template structure
                pass
            elif gate == "confidence_threshold":
                # Already checked above
                pass
            elif gate == "data_completeness":
                # Check data completeness in metadata
                pass

        # Determine overall result
        if issues:
            if any("fail" in issue.lower() for issue in issues):
                return QualityGateResult.FAIL, issues
            return QualityGateResult.WARNING, issues

        return QualityGateResult.PASS, []

    def _should_continue_workflow(self, quality_result: QualityGateResult, phase: str) -> bool:
        """Determine if workflow should continue based on quality gate result"""
        if quality_result == QualityGateResult.PASS:
            return True
        if quality_result == QualityGateResult.WARNING:
            # Continue with warnings, but flag for review
            return True
        if quality_result == QualityGateResult.FAIL:
            # Stop workflow on critical failures
            if phase in ["discover", "analyze"]:
                return False  # Critical phases
            return True  # Allow synthesis/validation to proceed with warnings
        return True

    def execute_workflow(
        self,
        domain: str,
        parameters: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.DIRECT,
        workflow_id: str | None = None,
    ) -> WorkflowResult:
        """
        Execute a complete DASV workflow with quality gates and orchestration

        Args:
            domain: Analysis domain (e.g., 'fundamental_analysis')
            parameters: Workflow parameters
            mode: Execution mode
            workflow_id: Optional workflow identifier

        Returns:
            WorkflowResult with complete execution details
        """
        if workflow_id is None:
            workflow_id = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            domain=domain,
            status=WorkflowStatus.IN_PROGRESS,
            start_time=datetime.now(),
            metadata=parameters.copy(),
        )

        try:
            # Get workflow template
            template = self.workflow_templates.get(domain)
            if not template:
                workflow_result.status = WorkflowStatus.FAILED
                workflow_result.metadata["error"] = f"No workflow template for domain: {domain}"
                return workflow_result

            phases = template["phases"]
            current_params = parameters.copy()

            print("🚀 Starting workflow {workflow_id} for {domain}")

            # Execute each phase
            for i, phase in enumerate(phases):
                print("📋 Phase {i+1}/{len(phases)}: {phase}")

                # Execute phase
                start_time = time.time()
                execution_result = self.execution_service.execute_command(domain, phase, current_params, mode)
                execution_time = time.time() - start_time

                # Evaluate quality gates
                quality_result, quality_issues = self._evaluate_quality_gate(phase, execution_result, domain)

                # Create phase result
                phase_result = WorkflowPhaseResult(
                    phase=phase,
                    execution_result=execution_result,
                    quality_gate_result=quality_result,
                    confidence_score=execution_result.confidence_score,
                    quality_issues=quality_issues,
                )

                workflow_result.phase_results[phase] = phase_result

                # Log phase completion
                status_emoji = (
                    "✅"
                    if quality_result == QualityGateResult.PASS
                    else "⚠️"
                    if quality_result == QualityGateResult.WARNING
                    else "❌"
                )
                print(f"   {status_emoji} {phase}: {execution_result.status.value} (Quality: {quality_result.value})")

                if quality_issues:
                    for issue in quality_issues[:3]:  # Show first 3 issues
                        print("      ⚠️  {issue}")

                if execution_result.output_files:
                    print("      📄 Output: {execution_result.output_files[0]}")

                # Check if should continue
                if not self._should_continue_workflow(quality_result, phase):
                    print(f"   🛑 Workflow stopped at {phase} due to quality gate failure")
                    workflow_result.status = WorkflowStatus.QUALITY_GATE_FAILED
                    break

                # Prepare parameters for next phase
                if execution_result.output_files:
                    phase_result.passed_to_next_phase = True
                    if phase == "discover":
                        current_params["discovery_file"] = execution_result.output_files[0]
                    elif phase == "analyze":
                        current_params["analysis_file"] = execution_result.output_files[0]
                    elif phase == "synthesize":
                        current_params["synthesis_file"] = execution_result.output_files[0]

                # Add to final outputs
                if execution_result.output_files:
                    workflow_result.final_outputs.extend(execution_result.output_files)

            # Determine overall status
            if workflow_result.status == WorkflowStatus.IN_PROGRESS:
                failed_phases = [
                    p
                    for p, r in workflow_result.phase_results.items()
                    if r.execution_result.status == ExecutionStatus.FAILED
                ]
                warning_phases = [
                    p
                    for p, r in workflow_result.phase_results.items()
                    if r.quality_gate_result == QualityGateResult.WARNING
                ]

                if failed_phases or warning_phases:
                    workflow_result.status = WorkflowStatus.PARTIAL_SUCCESS
                else:
                    workflow_result.status = WorkflowStatus.SUCCESS

            # Calculate overall confidence
            confidences = [
                r.confidence_score for r in workflow_result.phase_results.values() if r.confidence_score is not None
            ]
            if confidences:
                workflow_result.overall_confidence = sum(confidences) / len(confidences)

            # Generate quality summary
            workflow_result.quality_summary = self._generate_quality_summary(workflow_result)

        except Exception as e:
            workflow_result.status = WorkflowStatus.FAILED
            workflow_result.metadata["exception"] = str(e)
            print("💥 Workflow failed with exception: {e}")

        finally:
            workflow_result.end_time = datetime.now()
            duration = workflow_result.end_time - workflow_result.start_time

            # Final summary
            status_emoji = (
                "🎉"
                if workflow_result.status == WorkflowStatus.SUCCESS
                else ("⚠️" if workflow_result.status == WorkflowStatus.PARTIAL_SUCCESS else "💥")
            )
            print(f"\n{status_emoji} Workflow {workflow_id} completed: {workflow_result.status.value}")
            print("   ⏱️  Duration: {duration}")
            print("   📊 Phases completed: {len(workflow_result.phase_results)}")
            print("   📁 Output files: {len(workflow_result.final_outputs)}")

            if workflow_result.overall_confidence:
                print(f"   🎯 Overall confidence: {workflow_result.overall_confidence:.2f}")

        return workflow_result

    def _generate_quality_summary(self, workflow_result: WorkflowResult) -> dict[str, Any]:
        """Generate comprehensive quality summary for workflow"""
        summary = {
            "total_phases": len(workflow_result.phase_results),
            "successful_phases": 0,
            "warning_phases": 0,
            "failed_phases": 0,
            "quality_issues": [],
            "confidence_scores": {},
            "output_files_generated": len(workflow_result.final_outputs),
        }

        for phase, result in workflow_result.phase_results.items():
            # Count phase outcomes
            if result.execution_result.status == ExecutionStatus.SUCCESS:
                summary["successful_phases"] += 1
            elif result.execution_result.status == ExecutionStatus.FAILED:
                summary["failed_phases"] += 1

            if result.quality_gate_result == QualityGateResult.WARNING:
                summary["warning_phases"] += 1

            # Collect quality issues
            summary["quality_issues"].extend([f"{phase}: {issue}" for issue in result.quality_issues])

            # Record confidence scores
            if result.confidence_score:
                summary["confidence_scores"][phase] = result.confidence_score

        return summary

    def get_workflow_status(self, workflow_id: str) -> WorkflowResult | None:
        """Get status of an active or completed workflow"""
        return self.active_workflows.get(workflow_id)

    def list_available_workflows(self) -> list[str]:
        """List all available workflow domains"""
        return list(self.workflow_templates.keys())

    def get_workflow_template_info(self, domain: str) -> dict[str, Any] | None:
        """Get information about a workflow template"""
        return self.workflow_templates.get(domain)


def main():
    """CLI interface for the DASV workflow orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="DASV Workflow Orchestrator")
    parser.add_argument("domain", help="Workflow domain (e.g., fundamental_analysis)")
    parser.add_argument(
        "--mode",
        choices=["direct", "sub_agent"],
        default="direct",
        help="Execution mode",
    )
    parser.add_argument("--ticker", help="Ticker symbol")
    parser.add_argument("--sector", help="Sector symbol")
    parser.add_argument("--industry", help="Industry identifier")
    parser.add_argument("--region", help="Region identifier")
    parser.add_argument("--ticker-1", help="First ticker (for comparative analysis)")
    parser.add_argument("--ticker-2", help="Second ticker (for comparative analysis)")
    parser.add_argument("--date", help="Analysis date (YYYYMMDD format)")
    parser.add_argument("--workflow-id", help="Custom workflow identifier")
    parser.add_argument("--list-workflows", action="store_true", help="List available workflows")
    parser.add_argument(
        "--template-info",
        action="store_true",
        help="Show template information for domain",
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = DASVWorkflowOrchestrator()

    # Handle special commands
    if args.list_workflows:
        workflows = orchestrator.list_available_workflows()
        print("Available workflows:")
        for workflow in workflows:
            print("  {workflow}")
        return

    if args.template_info:
        info = orchestrator.get_workflow_template_info(args.domain)
        if info:
            print("Workflow Template: {args.domain}")
            print("  Phases: {info['phases']}")
            print("  Quality Gates: {info['quality_gates']}")
            print("  Dependencies: {info['dependencies']}")
            print("  Timeouts: {info['timeout_minutes']}")
        else:
            print("No template found for domain: {args.domain}")
        return

    # Build parameters
    parameters = {}
    if args.ticker:
        parameters["ticker"] = args.ticker
    if args.sector:
        parameters["sector"] = args.sector
    if args.industry:
        parameters["industry"] = args.industry
    if args.region:
        parameters["region"] = args.region
    if args.ticker_1:
        parameters["ticker_1"] = args.ticker_1
    if args.ticker_2:
        parameters["ticker_2"] = args.ticker_2
    if args.date:
        parameters["date"] = args.date

    # Execute workflow
    mode = ExecutionMode.DIRECT if args.mode == "direct" else ExecutionMode.SUB_AGENT

    result = orchestrator.execute_workflow(args.domain, parameters, mode, args.workflow_id)

    # Print detailed results
    print("\n" + "=" * 60)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 60)
    print("Workflow ID: {result.workflow_id}")
    print("Domain: {result.domain}")
    print("Status: {result.status.value}")
    print("Duration: {result.end_time - result.start_time}")
    print("Overall Confidence: {result.overall_confidence or 'N/A'}")

    print("\nPhase Results:")
    for phase, phase_result in result.phase_results.items():
        status_emoji = "✅" if phase_result.execution_result.status == ExecutionStatus.SUCCESS else "❌"
        quality_emoji = (
            "✅"
            if phase_result.quality_gate_result == QualityGateResult.PASS
            else ("⚠️" if phase_result.quality_gate_result == QualityGateResult.WARNING else "❌")
        )

        print(
            f"  {status_emoji} {phase}: {phase_result.execution_result.status.value} (Quality: {quality_emoji} {phase_result.quality_gate_result.value})"
        )

        if phase_result.quality_issues:
            for issue in phase_result.quality_issues:
                print("     ⚠️  {issue}")

        if phase_result.execution_result.output_files:
            for output_file in phase_result.execution_result.output_files:
                print("     📄 {output_file}")

    print("\nFinal Output Files ({len(result.final_outputs)}):")
    for output_file in result.final_outputs:
        print("  📄 {output_file}")

    print("\nQuality Summary:")
    for key, value in result.quality_summary.items():
        print("  {key}: {value}")


if __name__ == "__main__":
    main()
