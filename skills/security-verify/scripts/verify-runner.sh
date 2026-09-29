#!/usr/bin/env bash
# verify-runner.sh — Automated deterministic reproduction runner
# Part of the security-verify skill
#
# Usage:
#   ./verify-runner.sh --target <target> --runs <N> --command <command> [options]
#
# Options:
#   --target <target>        Target identifier (host, URL, contract address)
#   --runs <N>               Number of runs (minimum 3, default: 3)
#   --command <command>      Command to execute (use {target} placeholder)
#   --type <web2|web3>       Target type (default: web2)
#   --assertion <type>       Side-effect assertion type:
#                            file, output, callback, process, port, http, onchain
#   --assertion-cmd <cmd>    Assertion command to run after each execution
#   --output <dir>           Output directory for evidence (default: ./evidence)
#   --rpc-url <url>          RPC URL for web3 targets
#   --private-key <key>      Private key for web3 transactions
#   --wait <seconds>         Wait time between runs (default: 5)
#   --finality <blocks>      Blocks to wait for finality (web3 only, default: 12)
#   --timeout <seconds>      Command timeout (default: 60)
#   --help                   Show this help message
#
# Examples:
#   # Web2: Verify XSS with 5 runs
#   ./verify-runner.sh --target "http://example.com/search?q=" --runs 5 \
#     --command "curl -s '{target}<script>alert(1)</script>' | grep -F 'alert(1)'" \
#     --type web2 --assertion output --assertion-cmd "grep -q 'alert(1)'"
#
#   # Web3: Verify state change with 3 runs
#   ./verify-runner.sh --target "0xContractAddress" --runs 3 \
#     --command "cast send {target} 'exploit()' --private-key \$PK --rpc-url \$RPC_URL" \
#     --type web3 --assertion onchain \
#     --assertion-cmd "cast storage {target} 0 --rpc-url \$RPC_URL" \
#     --rpc-url "https://mainnet.infura.io/v3/YOUR_KEY"
#
# Exit codes:
#   0 = All runs passed (VERIFIED)
#   1 = One or more runs failed (UNVERIFIABLE)
#   2 = Usage error
#   3 = Configuration error

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE_DIR="./evidence"
RUNS=3
TARGET=""
COMMAND=""
TARGET_TYPE="web2"
ASSERTION_TYPE=""
ASSERTION_CMD=""
RPC_URL=""
PRIVATE_KEY=""
WAIT_BETWEEN=5
FINALITY_BLOCKS=12
TIMEOUT=60
TIMESTAMP_FORMAT="%Y-%m-%dT%H:%M:%SZ"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date +"${TIMESTAMP_FORMAT}") - $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $(date +"${TIMESTAMP_FORMAT}") - $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $(date +"${TIMESTAMP_FORMAT}") - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date +"${TIMESTAMP_FORMAT}") - $1"
}

usage() {
    sed -n '2,40p' "${BASH_SOURCE[0]}" | sed 's/^# //'
    exit 2
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 3
}

# ============================================================================
# Argument Parsing
# ============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --target)
                TARGET="$2"
                shift 2
                ;;
            --runs)
                RUNS="$2"
                shift 2
                ;;
            --command)
                COMMAND="$2"
                shift 2
                ;;
            --type)
                TARGET_TYPE="$2"
                shift 2
                ;;
            --assertion)
                ASSERTION_TYPE="$2"
                shift 2
                ;;
            --assertion-cmd)
                ASSERTION_CMD="$2"
                shift 2
                ;;
            --output)
                EVIDENCE_DIR="$2"
                shift 2
                ;;
            --rpc-url)
                RPC_URL="$2"
                shift 2
                ;;
            --private-key)
                PRIVATE_KEY="$2"
                shift 2
                ;;
            --wait)
                WAIT_BETWEEN="$2"
                shift 2
                ;;
            --finality)
                FINALITY_BLOCKS="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --help|-h)
                usage
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# ============================================================================
# Validation
# ============================================================================

validate_args() {
    if [[ -z "$TARGET" ]]; then
        error "--target is required"
    fi

    if [[ -z "$COMMAND" ]]; then
        error "--command is required"
    fi

    if [[ "$RUNS" -lt 3 ]]; then
        error "--runs must be at least 3 (got $RUNS)"
    fi

    if [[ "$TARGET_TYPE" != "web2" && "$TARGET_TYPE" != "web3" ]]; then
        error "--type must be 'web2' or 'web3' (got $TARGET_TYPE)"
    fi

    if [[ "$TARGET_TYPE" == "web3" && -z "$RPC_URL" ]]; then
        error "--rpc-url is required for web3 targets"
    fi

    if [[ "$TARGET_TYPE" == "web3" && -z "$PRIVATE_KEY" ]]; then
        error "--private-key is required for web3 targets"
    fi

    if [[ -n "$ASSERTION_TYPE" && -z "$ASSERTION_CMD" ]]; then
        error "--assertion-cmd is required when --assertion is specified"
    fi

    # Reject dangerous characters in command to prevent eval injection
    if [[ "$COMMAND" =~ [\;\|\&] ]] || [[ "$COMMAND" == *'$('* ]] || [[ "$COMMAND" == *'`'* ]]; then
        error "Command contains dangerous characters (; | & \$() backticks) — rejected for security"
    fi
}

# ============================================================================
# Evidence Capture
# ============================================================================

init_evidence_dir() {
    mkdir -p "$EVIDENCE_DIR"
    log_info "Evidence directory: $EVIDENCE_DIR"
}

capture_run() {
    local run_num="$1"
    local run_dir="${EVIDENCE_DIR}/run-${run_num}"
    mkdir -p "$run_dir"

    local timestamp
    timestamp=$(date +"${TIMESTAMP_FORMAT}")

    # Record run metadata
    cat > "${run_dir}/metadata.txt" <<EOF
Run: ${run_num}
Timestamp: ${timestamp}
Target: ${TARGET}
Type: ${TARGET_TYPE}
Command: ${COMMAND}
EOF

    log_info "Run ${run_num}/${RUNS} — ${timestamp}"

    # Execute the command
    local exit_code=0
    local output_file="${run_dir}/output.txt"
    local stderr_file="${run_dir}/stderr.txt"

    # Replace {target} placeholder
    local resolved_command="${COMMAND//\{target\}/$TARGET}"

    # Execute and capture output with timeout
    if ! timeout "$TIMEOUT" bash -c "$resolved_command" > "$output_file" 2> "$stderr_file"; then
        exit_code=$?
    fi

    # Record exit code
    echo "Exit code: ${exit_code}" >> "${run_dir}/metadata.txt"

    # Run assertion if specified
    local assertion_result="SKIPPED"
    local assertion_output=""

    if [[ -n "$ASSERTION_TYPE" && -n "$ASSERTION_CMD" ]]; then
        local assertion_exit=0
        assertion_output=$(eval "${ASSERTION_CMD//\{target\}/$TARGET}" 2>&1) || assertion_exit=$?

        if [[ $assertion_exit -eq 0 ]]; then
            assertion_result="PASS"
            log_success "Assertion passed (run ${run_num})"
        else
            assertion_result="FAIL"
            log_fail "Assertion failed (run ${run_num})"
        fi

        echo "$assertion_output" > "${run_dir}/assertion-output.txt"
    fi

    # Record assertion result
    echo "Assertion: ${assertion_result}" >> "${run_dir}/metadata.txt"

    # Return exit code and assertion result
    if [[ $exit_code -ne 0 ]]; then
        return 1
    fi

    if [[ "$assertion_result" == "FAIL" ]]; then
        return 1
    fi

    return 0
}

# ============================================================================
# Result Comparison
# ============================================================================

compare_results() {
    log_info "Comparing results across ${RUNS} runs..."

    local all_match=true
    local reference_output="${EVIDENCE_DIR}/run-1/output.txt"
    local reference_stderr="${EVIDENCE_DIR}/run-1/stderr.txt"
    local reference_metadata="${EVIDENCE_DIR}/run-1/metadata.txt"

    for ((i=2; i<=RUNS; i++)); do
        local current_output="${EVIDENCE_DIR}/run-${i}/output.txt"
        local current_stderr="${EVIDENCE_DIR}/run-${i}/stderr.txt"
        local current_metadata="${EVIDENCE_DIR}/run-${i}/metadata.txt"

        if [[ ! -f "$current_output" ]]; then
            log_fail "Run ${i} output file missing"
            all_match=false
            continue
        fi

        # Compare stdout
        if diff -q "$reference_output" "$current_output" > /dev/null 2>&1; then
            log_success "Run ${i} stdout matches run 1"
        else
            log_fail "Run ${i} stdout differs from run 1"
            diff "$reference_output" "$current_output" > "${EVIDENCE_DIR}/diff-run-1-vs-${i}.txt" 2>&1 || true
            all_match=false
        fi

        # Compare stderr
        if diff -q "$reference_stderr" "$current_stderr" > /dev/null 2>&1; then
            log_success "Run ${i} stderr matches run 1"
        else
            log_fail "Run ${i} stderr differs from run 1"
            diff "$reference_stderr" "$current_stderr" > "${EVIDENCE_DIR}/diff-stderr-run-1-vs-${i}.txt" 2>&1 || true
            all_match=false
        fi

        # Compare exit codes
        local ref_exit_code
        local cur_exit_code
        ref_exit_code=$(grep "Exit code:" "$reference_metadata" | awk '{print $3}')
        cur_exit_code=$(grep "Exit code:" "$current_metadata" | awk '{print $3}')

        if [[ "$ref_exit_code" == "$cur_exit_code" ]]; then
            log_success "Run ${i} exit code matches run 1 (${cur_exit_code})"
        else
            log_fail "Run ${i} exit code differs from run 1 (expected ${ref_exit_code}, got ${cur_exit_code})"
            all_match=false
        fi
    done

    if $all_match; then
        log_success "All runs produced identical output, stderr, and exit codes"
        return 0
    else
        log_fail "Runs produced different output, stderr, or exit codes"
        return 1
    fi
}

# ============================================================================
# Report Generation
# ============================================================================

generate_report() {
    local verdict="$1"
    local report_file="${EVIDENCE_DIR}/verification-report.md"

    log_info "Generating verification report: ${report_file}"

    cat > "$report_file" <<EOF
# Verification Report

## Summary

| Field | Value |
|-------|-------|
| **Verdict** | ${verdict} |
| **Target** | ${TARGET} |
| **Type** | ${TARGET_TYPE} |
| **Runs** | ${RUNS} |
| **Timestamp** | $(date +"${TIMESTAMP_FORMAT}") |
| **Command** | ${COMMAND} |

## Run Details

EOF

    for ((i=1; i<=RUNS; i++)); do
        local run_dir="${EVIDENCE_DIR}/run-${i}"
        local metadata_file="${run_dir}/metadata.txt"

        if [[ -f "$metadata_file" ]]; then
            cat >> "$report_file" <<EOF
### Run ${i}

\`\`\`
$(cat "$metadata_file")
\`\`\`

EOF
        fi
    done

    cat >> "$report_file" <<EOF
## Result Comparison

EOF

    if [[ -f "${EVIDENCE_DIR}/diff-run-1-vs-2.txt" ]]; then
        cat >> "$report_file" <<EOF
\`\`\`
$(cat "${EVIDENCE_DIR}/diff-run-1-vs-2.txt")
\`\`\`

EOF
    else
        echo "All runs produced identical output." >> "$report_file"
    fi

    cat >> "$report_file" <<EOF
## Verdict

**${verdict}**

EOF

    if [[ "$verdict" == "VERIFIED" ]]; then
        cat >> "$report_file" <<EOF
- All ${RUNS} runs produced identical output
- All side-effect assertions passed
- Results are reproducible

EOF
    else
        cat >> "$report_file" <<EOF
- One or more runs failed
- One or more side-effect assertions failed
- Results are not reproducible

EOF
    fi

    log_info "Report saved to: ${report_file}"
}

# ============================================================================
# Main
# ============================================================================

main() {
    parse_args "$@"
    validate_args
    init_evidence_dir

    log_info "Starting verification runner"
    log_info "Target: ${TARGET}"
    log_info "Type: ${TARGET_TYPE}"
    log_info "Runs: ${RUNS}"
    log_info "Command: ${COMMAND}"

    local all_passed=true

    for ((i=1; i<=RUNS; i++)); do
        if ! capture_run "$i"; then
            all_passed=false
        fi

        # Wait between runs (except after the last run)
        if [[ $i -lt $RUNS ]]; then
            log_info "Waiting ${WAIT_BETWEEN}s before next run..."
            sleep "$WAIT_BETWEEN"
        fi
    done

    # Wait for finality on web3 targets before comparing results
    if [[ "$TARGET_TYPE" == "web3" ]]; then
        log_info "Waiting for finality (${FINALITY_BLOCKS} blocks)..."
        local wait_seconds=$((FINALITY_BLOCKS * 12))
        log_info "Sleeping ${wait_seconds}s for finality..."
        sleep "$wait_seconds"
        log_info "Finality wait complete"
    fi

    # Compare results
    local comparison_passed=true
    if ! compare_results; then
        comparison_passed=false
    fi

    # Determine verdict
    local verdict="UNVERIFIABLE"
    if $all_passed && $comparison_passed; then
        verdict="VERIFIED"
    fi

    # Generate report
    generate_report "$verdict"

    # Final output
    echo ""
    if [[ "$verdict" == "VERIFIED" ]]; then
        log_success "VERIFICATION COMPLETE: ${verdict}"
        log_info "Evidence saved to: ${EVIDENCE_DIR}"
        exit 0
    else
        log_fail "VERIFICATION COMPLETE: ${verdict}"
        log_info "Evidence saved to: ${EVIDENCE_DIR}"
        exit 1
    fi
}

main "$@"
