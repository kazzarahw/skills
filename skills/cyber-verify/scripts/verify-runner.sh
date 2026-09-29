#!/usr/bin/env bash
#
# verify-runner.sh - Automated Verification Runner
#
# Automates the deterministic reproduction stage of vulnerability verification.
# Runs a command N times with timeout, captures output and exit codes,
# compares results across runs, and generates a verdict.
#
# Usage:
#   ./verify-runner.sh --command "curl -s http://target" --target 192.168.1.1 [OPTIONS]
#
# Options:
#   --command <cmd>       Command to execute (required)
#   --target <host>       Target host/IP for reference
#   --runs <int>          Number of runs (default: 3)
#   --timeout <int>       Timeout per run in seconds (default: 30)
#   --output <dir>        Output directory (default: ./verify-results)
#   --compare <mode>      Comparison mode: hash|output|exitcode (default: hash)
#   --tolerance <float>   Tolerance for output comparison 0.0-1.0 (default: 0.0)
#   --help                Show this help message
#
# Exit Codes:
#   0   REPRODUCIBLE - All runs produced identical results
#   1   NOT_REPRODUCIBLE - Results varied across runs
#   2   Error during execution
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly VERSION="1.0.0"

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Global variables
COMMAND=""
TARGET=""
RUNS=3
TIMEOUT=30
OUTPUT_DIR="./verify-results"
COMPARE_MODE="hash"
TOLERANCE=0.0
RESULTS=()
EXIT_CODES=()
HASHES=()
START_TIME=""

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    
    case "$level" in
        INFO)    echo -e "${GREEN}[${ts}] [INFO]${NC} $message" ;;
        WARN)    echo -e "${YELLOW}[${ts}] [WARN]${NC} $message" ;;
        ERROR)   echo -e "${RED}[${ts}] [ERROR]${NC} $message" ;;
        DEBUG)   echo -e "${CYAN}[${ts}] [DEBUG]${NC} $message" ;;
        SECTION) echo -e "\n${BLUE}━━━ $message ━━━${NC}" ;;
        SUCCESS) echo -e "${GREEN}  ✓ $message${NC}" ;;
        FAILURE) echo -e "${RED}  ✗ $message${NC}" ;;
    esac
}

die() {
    log ERROR "$*"
    exit 2
}

usage() {
    cat <<EOF
${SCRIPT_NAME} v${VERSION} - Automated Verification Runner

Usage:
    ${SCRIPT_NAME} --command <cmd> [OPTIONS]

Required Arguments:
    --command <cmd>       Command to execute for verification

Optional Arguments:
    --target <host>       Target host/IP for reference
    --runs <int>          Number of runs (default: 3)
    --timeout <int>       Timeout per run in seconds (default: 30)
    --output <dir>        Output directory (default: ./verify-results)
    --compare <mode>      Comparison mode: hash|output|exitcode (default: hash)
    --tolerance <float>   Tolerance for output comparison 0.0-1.0 (default: 0.0)
    --help                Show this help message

Comparison Modes:
    hash        Compare SHA256 hashes of output (strictest)
    output      Compare raw output text
    exitcode    Compare only exit codes

Examples:
    # Basic verification (3 runs)
    ${SCRIPT_NAME} --command "curl -s http://target/login" --target 192.168.1.1

    # 5 runs with 60s timeout
    ${SCRIPT_NAME} --command "nmap -sV target" --runs 5 --timeout 60

    # Compare exit codes only
    ${SCRIPT_NAME} --command "ssh user@target" --compare exitcode

    # Output comparison with 10% tolerance
    ${SCRIPT_NAME} --command "curl -s http://target" --compare output --tolerance 0.1

EOF
    exit 0
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --command)
                COMMAND="${2:?--command requires a value}"
                shift 2
                ;;
            --target)
                TARGET="${2:?--target requires a value}"
                shift 2
                ;;
            --runs)
                RUNS="${2:?--runs requires a value}"
                if ! [[ "$RUNS" =~ ^[0-9]+$ ]] || [[ "$RUNS" -lt 1 ]]; then
                    die "Runs must be a positive integer"
                fi
                shift 2
                ;;
            --timeout)
                TIMEOUT="${2:?--timeout requires a value}"
                if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]] || [[ "$TIMEOUT" -lt 1 ]]; then
                    die "Timeout must be a positive integer"
                fi
                shift 2
                ;;
            --output)
                OUTPUT_DIR="${2:?--output requires a value}"
                shift 2
                ;;
            --compare)
                COMPARE_MODE="${2:?--compare requires a value}"
                if [[ ! "$COMPARE_MODE" =~ ^(hash|output|exitcode)$ ]]; then
                    die "Compare mode must be: hash, output, or exitcode"
                fi
                shift 2
                ;;
            --tolerance)
                TOLERANCE="${2:?--tolerance requires a value}"
                if ! [[ "$TOLERANCE" =~ ^[0-9]*\.?[0-9]+$ ]]; then
                    die "Tolerance must be a number between 0.0 and 1.0"
                fi
                shift 2
                ;;
            --help|-h)
                usage
                ;;
            *)
                die "Unknown option: $1"
                ;;
        esac
    done
    
    if [[ -z "$COMMAND" ]]; then
        die "Missing required argument: --command"
    fi
}

# ============================================================================
# OUTPUT SETUP
# ============================================================================

setup_output() {
    mkdir -p "$OUTPUT_DIR"
    START_TIME="$(date +%s)"
    
    log INFO "Command: $COMMAND"
    log INFO "Target: ${TARGET:-N/A}"
    log INFO "Runs: $RUNS"
    log INFO "Timeout: ${TIMEOUT}s"
    log INFO "Compare mode: $COMPARE_MODE"
    log INFO "Tolerance: $TOLERANCE"
    log INFO "Output directory: $OUTPUT_DIR"
}

# ============================================================================
# RUN COMMAND
# ============================================================================

run_command() {
    local run_id="$1"
    local output_file="$OUTPUT_DIR/run-${run_id}.txt"
    local exit_code=0
    
    log INFO "Run $run_id/$RUNS: Executing command..."
    
    # Execute command with timeout
    set +e
    timeout "$TIMEOUT" bash -c "$COMMAND" > "$output_file" 2>&1
    exit_code=$?
    set -e
    
    # Handle timeout
    if [[ $exit_code -eq 124 ]]; then
        log WARN "Run $run_id: Command timed out after ${TIMEOUT}s"
        echo "TIMEOUT" >> "$output_file"
    fi
    
    # Calculate hash
    local hash
    hash=$(sha256sum "$output_file" | cut -d' ' -f1)
    
    # Store results
    RESULTS+=("$output_file")
    EXIT_CODES+=("$exit_code")
    HASHES+=("$hash")
    
    log DEBUG "Run $run_id: Exit code=$exit_code, Hash=${hash:0:16}..."
    
    return $exit_code
}

# ============================================================================
# COMPARISON LOGIC
# ============================================================================

compare_hash() {
    log SECTION "COMPARING RESULTS (HASH MODE)"
    
    local unique_hashes
    unique_hashes=$(printf '%s\n' "${HASHES[@]}" | sort -u | wc -l)
    
    if [[ "$unique_hashes" -eq 1 ]]; then
        log SUCCESS "All runs produced identical output (hash match)"
        return 0
    else
        log FAILURE "Output varies across runs ($unique_hashes unique hashes)"
        
        # Show differences
        for i in "${!HASHES[@]}"; do
            local run_num=$((i + 1))
            log INFO "  Run $run_num: ${HASHES[$i]:0:16}..."
        done
        
        return 1
    fi
}

compare_output() {
    log SECTION "COMPARING RESULTS (OUTPUT MODE)"
    
    local reference_file="${RESULTS[0]}"
    local all_match=true
    local differences=0
    
    for i in "${!RESULTS[@]}"; do
        local run_num=$((i + 1))
        
        if [[ $i -eq 0 ]]; then
            continue
        fi
        
        local current_file="${RESULTS[$i]}"
        
        # Compare with tolerance
        if [[ "$TOLERANCE" == "0.0" ]]; then
            # Exact match
            if ! diff -q "$reference_file" "$current_file" > /dev/null 2>&1; then
                all_match=false
                differences=$((differences + 1))
                log WARN "  Run $run_num differs from reference"
            fi
        else
            # Fuzzy match with tolerance
            local similarity
            similarity=$(python3 -c "
import difflib
with open('$reference_file') as f1, open('$current_file') as f2:
    text1 = f1.read()
    text2 = f2.read()
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    print(f'{similarity:.4f}')
" 2>/dev/null || echo "0.0")
            
            local threshold
            threshold=$(python3 -c "print(1.0 - $TOLERANCE)")
            
            if (( $(echo "$similarity < $threshold" | bc -l) )); then
                all_match=false
                differences=$((differences + 1))
                log WARN "  Run $run_num differs (similarity: $similarity)"
            fi
        fi
    done
    
    if [[ "$all_match" == true ]]; then
        log SUCCESS "All runs produced matching output"
        return 0
    else
        log FAILURE "$differences run(s) differ from reference"
        return 1
    fi
}

compare_exitcode() {
    log SECTION "COMPARING RESULTS (EXIT CODE MODE)"
    
    local unique_codes
    unique_codes=$(printf '%s\n' "${EXIT_CODES[@]}" | sort -u | wc -l)
    
    if [[ "$unique_codes" -eq 1 ]]; then
        log SUCCESS "All runs produced identical exit codes (${EXIT_CODES[0]})"
        return 0
    else
        log FAILURE "Exit codes vary across runs ($unique_codes unique codes)"
        
        for i in "${!EXIT_CODES[@]}"; do
            local run_num=$((i + 1))
            log INFO "  Run $run_num: Exit code ${EXIT_CODES[$i]}"
        done
        
        return 1
    fi
}

# ============================================================================
# VERDICT GENERATION
# ============================================================================

generate_verdict() {
    local comparison_result="$1"
    local end_time
    end_time="$(date +%s)"
    local duration=$((end_time - START_TIME))
    
    local verdict="REPRODUCIBLE"
    local confidence="HIGH"
    local exit_code=0
    
    if [[ "$comparison_result" -ne 0 ]]; then
        verdict="NOT_REPRODUCIBLE"
        confidence="HIGH"
        exit_code=1
    fi
    
    # Adjust confidence based on number of runs
    if [[ "$RUNS" -lt 3 ]]; then
        confidence="LOW"
    elif [[ "$RUNS" -lt 5 ]]; then
        confidence="MEDIUM"
    fi
    
    # Generate structured results
    local results_file="$OUTPUT_DIR/verification-results.json"
    
    cat > "$results_file" <<EOF
{
  "verification": {
    "verdict": "${verdict}",
    "confidence": "${confidence}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "duration_seconds": ${duration}
  },
  "parameters": {
    "command": "${COMMAND}",
    "target": "${TARGET:-null}",
    "runs": ${RUNS},
    "timeout_seconds": ${TIMEOUT},
    "compare_mode": "${COMPARE_MODE}",
  "tolerance": ${TOLERANCE}
  },
  "results": [
EOF
    
    for i in "${!RESULTS[@]}"; do
        local run_num=$((i + 1))
        local comma=","
        [[ $i -eq $((${#RESULTS[@]} - 1)) ]] && comma=""
        
        cat >> "$results_file" <<EOF
    {
      "run": ${run_num},
      "exit_code": ${EXIT_CODES[$i]},
      "output_file": "${RESULTS[$i]}",
      "output_hash": "${HASHES[$i]}"
    }${comma}
EOF
    done
    
    cat >> "$results_file" <<EOF
  ],
  "analysis": {
    "unique_hashes": $(printf '%s\n' "${HASHES[@]}" | sort -u | wc -l),
    "unique_exit_codes": $(printf '%s\n' "${EXIT_CODES[@]}" | sort -u | wc -l),
    "all_exit_codes": [$(printf '%s, ' "${EXIT_CODES[@]}" | sed 's/, $//')],
    "all_hashes": [$(printf '"%s", ' "${HASHES[@]}" | sed 's/, $//')]
  }
}
EOF
    
    # Print summary
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  VERIFICATION RESULTS${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Verdict:     $verdict"
    echo "  Confidence:  $confidence"
    echo "  Duration:    ${duration}s"
    echo "  Runs:        $RUNS"
    echo ""
    echo "  Results: $results_file"
    echo ""
    
    if [[ "$verdict" == "REPRODUCIBLE" ]]; then
        echo -e "${GREEN}  ✓ Command is REPRODUCIBLE${NC}"
        echo -e "${GREEN}    All $RUNS runs produced identical results${NC}"
    else
        echo -e "${RED}  ✗ Command is NOT REPRODUCIBLE${NC}"
        echo -e "${RED}    Results varied across runs${NC}"
    fi
    echo ""
    
    return $exit_code
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     VERIFICATION RUNNER v${VERSION}                            ║"
    echo "║     Automated Deterministic Reproduction                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    parse_args "$@"
    setup_output
    
    log SECTION "EXECUTING RUNS"
    
    for i in $(seq 1 "$RUNS"); do
        run_command "$i"
    done
    
    # Compare results
    local comparison_result=0
    case "$COMPARE_MODE" in
        hash)     compare_hash || comparison_result=$? ;;
        output)   compare_output || comparison_result=$? ;;
        exitcode) compare_exitcode || comparison_result=$? ;;
    esac
    
    # Generate verdict
    generate_verdict "$comparison_result"
}

main "$@"
