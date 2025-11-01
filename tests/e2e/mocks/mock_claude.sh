#!/usr/bin/env bash
# Mock Claude CLI for E2E Testing
# Simulates Claude command behavior based on test scenarios
# Usage: mock_claude.sh -p [command_file]

# Strict error handling
set -euo pipefail

# Mock configuration from environment
readonly TEST_SCENARIO="${TEST_SCENARIO:-success}"
readonly TEST_PHASE_OVERRIDE="${TEST_PHASE_OVERRIDE:-}"
readonly TEST_ATTEMPT_COUNT="${TEST_ATTEMPT_COUNT:-0}"
readonly TEST_OUTPUT_DIR="${TEST_OUTPUT_DIR:-/tmp/test_output}"
readonly TEST_FIXTURES_DIR="${TEST_FIXTURES_DIR:-$(dirname "$0")/../fixtures}"
readonly TEST_TICKER="${TEST_TICKER:-AAPL}"
readonly TEST_DATE="${TEST_DATE:-$(date '+%Y%m%d')}"

# Enhanced scenario control variables
readonly TEST_VALIDATION_FAIL_FIRST="${TEST_VALIDATION_FAIL_FIRST:-false}"
readonly TEST_CONFIDENCE_FAIL_PHASE="${TEST_CONFIDENCE_FAIL_PHASE:-}"
readonly TEST_CONFIDENCE_FAIL_FIRST="${TEST_CONFIDENCE_FAIL_FIRST:-false}"
readonly TEST_PARSE_FAIL_PHASE="${TEST_PARSE_FAIL_PHASE:-}"
readonly TEST_PARSE_FAIL_FIRST="${TEST_PARSE_FAIL_FIRST:-false}"

# Debugging
readonly DEBUG_MOCK="${DEBUG_MOCK:-false}"

debug_log() {
    if [[ "${DEBUG_MOCK}" == "true" ]]; then
        echo "[MOCK DEBUG] $1" >&2
    fi
}

# Parse command line arguments
COMMAND_FILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -p)
            COMMAND_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Mock Claude CLI for testing"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Read ticker from stdin (simulating echo TICKER | claude -p command)
TICKER_INPUT=""
if [[ -t 0 ]]; then
    # stdin is a terminal, use default
    TICKER_INPUT="${TEST_TICKER}"
else
    # Read from stdin
    read -r TICKER_INPUT || TICKER_INPUT="${TEST_TICKER}"
fi

debug_log "Mock Claude called with command: ${COMMAND_FILE}"
debug_log "Ticker input: ${TICKER_INPUT}"
debug_log "Test scenario: ${TEST_SCENARIO}"
debug_log "Attempt count: ${TEST_ATTEMPT_COUNT}"

# Determine which phase is being executed
determine_phase() {
    local cmd_file="$1"
    case "${cmd_file}" in
        *discover.md*) echo "discovery" ;;
        *analyze.md*) echo "analysis" ;;
        *synthesize.md*) echo "synthesis" ;;
        *validate.md*) echo "validation" ;;
        *) echo "unknown" ;;
    esac
}

# Generate output file path based on phase (match shell script's actual output structure)
generate_output_path() {
    local phase="$1"
    local ticker="$2"
    local date="$3"

    # Use the actual project data outputs directory structure
    local project_root="/Users/colemorton/Projects/colemorton-command-system-enhancements"
    local data_outputs="${project_root}/data/outputs"

    case "${phase}" in
        "discovery")
            echo "${data_outputs}/fundamental_analysis/discovery/${ticker}_${date}_discovery.json"
            ;;
        "analysis")
            echo "${data_outputs}/fundamental_analysis/analysis/${ticker}_${date}_analysis.json"
            ;;
        "synthesis")
            echo "${data_outputs}/fundamental_analysis/${ticker}_${date}.md"
            ;;
        "validation")
            echo "${data_outputs}/fundamental_analysis/validation/${ticker}_${date}_validation.json"
            ;;
        *)
            echo "${data_outputs}/unknown_output.txt"
            ;;
    esac
}

# Load fixture content based on scenario and phase
load_fixture() {
    local phase="$1"
    local scenario="$2"
    local attempt="$3"

    local fixture_file=""

    debug_log "load_fixture: phase=$phase, scenario=$scenario, attempt=$attempt"
    debug_log "Enhanced controls: VALIDATION_FAIL_FIRST=$TEST_VALIDATION_FAIL_FIRST, CONFIDENCE_FAIL_PHASE=$TEST_CONFIDENCE_FAIL_PHASE, PARSE_FAIL_PHASE=$TEST_PARSE_FAIL_PHASE"

    # Check for validation fail first scenario
    if [[ "$TEST_VALIDATION_FAIL_FIRST" == "true" && "$phase" == "validation" && "$attempt" == "0" ]]; then
        fixture_file="validation_fail.json"
        debug_log "Using validation_fail fixture for first attempt"
    # Check for confidence fail scenario
    elif [[ -n "$TEST_CONFIDENCE_FAIL_PHASE" && "$phase" == "$TEST_CONFIDENCE_FAIL_PHASE" && "$TEST_CONFIDENCE_FAIL_FIRST" == "true" && "$attempt" == "0" ]]; then
        fixture_file="${phase}_low_confidence.json"
        if [[ "${phase}" == "synthesis" ]]; then
            fixture_file="${phase}_low_confidence.md"
        fi
        debug_log "Using low confidence fixture for phase $phase on first attempt"
    # Check for parse fail scenario
    elif [[ -n "$TEST_PARSE_FAIL_PHASE" && "$phase" == "$TEST_PARSE_FAIL_PHASE" && "$TEST_PARSE_FAIL_FIRST" == "true" && "$attempt" == "0" ]]; then
        fixture_file="${phase}_malformed.json"
        if [[ "${phase}" == "synthesis" ]]; then
            fixture_file="${phase}_low_confidence.md"  # Use low confidence for synthesis parse fail
        fi
        debug_log "Using malformed fixture for phase $phase on first attempt"
    else
        # Default to success scenarios or determine based on legacy scenario format
        case "${scenario}" in
            "success"|"validation_fail_then_success"|"confidence_fail_retry"|"parse_fail_retry")
                fixture_file="${phase}_success.json"
                if [[ "${phase}" == "synthesis" ]]; then
                    fixture_file="${phase}_success.md"
                fi
                ;;
            "validation_fail_retry_success")
                if [[ "${phase}" == "validation" ]]; then
                    if [[ "${attempt}" == "0" ]]; then
                        fixture_file="${phase}_fail.json"
                    else
                        fixture_file="${phase}_success.json"
                    fi
                else
                    fixture_file="${phase}_success.json"
                    if [[ "${phase}" == "synthesis" ]]; then
                        fixture_file="${phase}_success.md"
                    fi
                fi
                ;;
            "confidence_fail_discovery"|"confidence_fail_analysis"|"confidence_fail_synthesis"|"confidence_fail_validation")
                local failing_phase="${scenario#confidence_fail_}"
                if [[ "${phase}" == "${failing_phase}" ]]; then
                    if [[ "${attempt}" == "0" ]]; then
                        fixture_file="${phase}_low_confidence.json"
                        if [[ "${phase}" == "synthesis" ]]; then
                            fixture_file="${phase}_low_confidence.md"
                        fi
                    else
                        fixture_file="${phase}_success.json"
                        if [[ "${phase}" == "synthesis" ]]; then
                            fixture_file="${phase}_success.md"
                        fi
                    fi
                else
                    fixture_file="${phase}_success.json"
                    if [[ "${phase}" == "synthesis" ]]; then
                        fixture_file="${phase}_success.md"
                    fi
                fi
                ;;
            "parse_fail")
                if [[ "${phase}" == "validation" ]]; then
                    if [[ "${attempt}" == "0" ]]; then
                        fixture_file="${phase}_malformed.json"
                    else
                        fixture_file="${phase}_success.json"
                    fi
                else
                    fixture_file="${phase}_success.json"
                    if [[ "${phase}" == "synthesis" ]]; then
                        fixture_file="${phase}_success.md"
                    fi
                fi
                ;;
            *)
                fixture_file="${phase}_success.json"
                if [[ "${phase}" == "synthesis" ]]; then
                    fixture_file="${phase}_success.md"
                fi
                ;;
        esac
    fi

    local fixture_path="${TEST_FIXTURES_DIR}/${fixture_file}"
    debug_log "Loading fixture: ${fixture_path}"

    if [[ -f "${fixture_path}" ]]; then
        cat "${fixture_path}"
    else
        debug_log "Fixture not found: ${fixture_path}, generating default"
        generate_default_output "${phase}" "${TICKER_INPUT}"
    fi
}

# Generate default output if fixture not found
generate_default_output() {
    local phase="$1"
    local ticker="$2"

    case "${phase}" in
        "discovery")
            cat << EOF
{
  "metadata": {
    "ticker": "${ticker}",
    "analysis_date": "${TEST_DATE}",
    "phase": "discovery",
    "confidence": 9.2
  },
  "market_data": {
    "current_price": 150.50,
    "market_cap": 2400000000000
  },
  "financial_metrics": {
    "revenue_ttm": 365000000000,
    "eps": 6.15,
    "roe": 0.245
  }
}
EOF
            ;;
        "analysis")
            cat << EOF
{
  "metadata": {
    "ticker": "${ticker}",
    "analysis_date": "${TEST_DATE}",
    "phase": "analysis",
    "confidence": 9.1
  },
  "financial_health": {
    "profitability_score": "A",
    "balance_sheet_score": "A-",
    "overall_grade": "A"
  },
  "competitive_analysis": {
    "market_position": "strong",
    "moat_strength": "wide"
  }
}
EOF
            ;;
        "synthesis")
            cat << EOF
# Fundamental Analysis: ${ticker}

## 🎯 Investment Thesis
Strong technology company with excellent fundamentals and competitive positioning.

## 📊 Business Intelligence
Revenue: \$365B (TTM)
EPS: \$6.15
Market Cap: \$2.4T

## 🏆 Competitive Position
Market leader with strong competitive moats.

## 📈 Valuation
Fair value estimate: \$155-165 per share

## ⚠️ Risk Matrix
| Risk | Probability | Impact |
|------|-------------|---------|
| Market volatility | 0.3 | 3 |
| Regulatory changes | 0.2 | 4 |

## 📋 Analysis Metadata
- Analysis Date: ${TEST_DATE}
- Confidence: 9.1/10.0
- Analyst: Mock System

## 🏁 Investment Recommendation Summary
${ticker} represents a strong investment opportunity with excellent fundamentals, market leadership, and sustainable competitive advantages. The company's strong financial position and growth prospects support the current valuation.
EOF
            ;;
        "validation")
            cat << EOF
{
  "metadata": {
    "ticker": "${ticker}",
    "validation_date": "${TEST_DATE}",
    "phase": "validation"
  },
  "overall_assessment": {
    "overall_reliability_score": "9.2/10.0",
    "decision_confidence": "High",
    "minimum_threshold_met": "true",
    "institutional_quality_certified": "true"
  },
  "dasv_validation_breakdown": {
    "discovery_validation": {
      "overall_discovery_score": "9.2/10.0"
    },
    "analysis_validation": {
      "overall_analysis_score": "9.1/10.0"
    },
    "synthesis_validation": {
      "overall_synthesis_score": "9.1/10.0"
    }
  }
}
EOF
            ;;
    esac
}

# Main execution
main() {
    if [[ -z "${COMMAND_FILE}" ]]; then
        echo "Error: No command file specified" >&2
        exit 1
    fi

    # Determine phase from command file
    local phase
    phase=$(determine_phase "${COMMAND_FILE}")

    debug_log "Determined phase: ${phase}"

    # Apply phase override if specified
    if [[ -n "${TEST_PHASE_OVERRIDE}" ]]; then
        phase="${TEST_PHASE_OVERRIDE}"
        debug_log "Phase override applied: ${phase}"
    fi

    # Generate output path
    local output_path
    output_path=$(generate_output_path "${phase}" "${TICKER_INPUT}" "${TEST_DATE}")

    debug_log "Output path: ${output_path}"

    # Create output directory
    mkdir -p "$(dirname "${output_path}")"

    # Load fixture content and write to output file
    local content
    content=$(load_fixture "${phase}" "${TEST_SCENARIO}" "${TEST_ATTEMPT_COUNT}")

    # Replace placeholders in content
    content="${content//TICKER_PLACEHOLDER/${TICKER_INPUT}}"
    content="${content//DATE_PLACEHOLDER/${TEST_DATE}}"

    # Write to output file
    echo "${content}" > "${output_path}"

    debug_log "Written output to: ${output_path}"

    # Simulate Claude command output (what would appear in logs)
    echo "Mock Claude executed successfully for ${phase} phase"
    echo "Generated output: ${output_path}"

    # Small delay to simulate processing time
    sleep 0.1

    exit 0
}

# Execute main function
main "$@"
