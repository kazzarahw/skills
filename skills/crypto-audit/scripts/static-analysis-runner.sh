#!/usr/bin/env bash
# static-analysis-runner.sh
# Runs all static analysis tools and aggregates results
# Usage: bash static-analysis-runner.sh /path/to/project

set -euo pipefail

PROJECT_DIR="${1:-.}"
OUTPUT_DIR="${PROJECT_DIR}/audit-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="${OUTPUT_DIR}/summary_${TIMESTAMP}.md"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Initialize counters
SLITHER_COUNT=0
ADERYN_COUNT=0
MYTHRIL_COUNT=0
SOLHINT_COUNT=0
TOTAL_COUNT=0

# Initialize summary
cat > "${RESULTS_FILE}" << EOF
# Static Analysis Summary

**Project:** ${PROJECT_DIR}
**Date:** $(date)
**Tools:** Slither, Aderyn, Mythril, Solhint

---

EOF

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to count JSON findings
count_json_findings() {
    local file="$1"
    if [ -f "$file" ]; then
        # Try to count results array length
        python3 -c "
import json
import sys
try:
    with open('$file') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'results' in data:
        print(len(data['results']))
    elif isinstance(data, list):
        print(len(data))
    else:
        print(0)
except:
    print(0)
" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Run Slither
run_slither() {
    log_info "Running Slither..."
    local output="${OUTPUT_DIR}/slither_${TIMESTAMP}.json"
    
    if command_exists slither; then
        if slither "${PROJECT_DIR}" --json "${output}" >/dev/null 2>&1; then
            SLITHER_COUNT=$(count_json_findings "${output}")
            log_success "Slither completed: ${SLITHER_COUNT} findings"
            echo "## Slither Results" >> "${RESULTS_FILE}"
            echo "- **Findings:** ${SLITHER_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        else
            log_warn "Slither found issues or encountered errors"
            SLITHER_COUNT=$(count_json_findings "${output}")
            echo "## Slither Results" >> "${RESULTS_FILE}"
            echo "- **Findings:** ${SLITHER_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        fi
    else
        log_error "Slither not installed. Install with: pip install slither-analyzer"
        echo "## Slither Results" >> "${RESULTS_FILE}"
        echo "- **Status:** Not installed" >> "${RESULTS_FILE}"
        echo "" >> "${RESULTS_FILE}"
    fi
}

# Run Aderyn
run_aderyn() {
    log_info "Running Aderyn..."
    local output="${OUTPUT_DIR}/aderyn_${TIMESTAMP}.json"
    
    if command_exists aderyn; then
        if aderyn "${PROJECT_DIR}" --json "${output}" >/dev/null 2>&1; then
            ADERYN_COUNT=$(count_json_findings "${output}")
            log_success "Aderyn completed: ${ADERYN_COUNT} findings"
            echo "## Aderyn Results" >> "${RESULTS_FILE}"
            echo "- **Findings:** ${ADERYN_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        else
            log_warn "Aderyn found issues or encountered errors"
            ADERYN_COUNT=$(count_json_findings "${output}")
            echo "## Aderyn Results" >> "${RESULTS_FILE}"
            echo "- **Findings:** ${ADERYN_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        fi
    else
        log_error "Aderyn not installed. Install with: cargo install aderyn"
        echo "## Aderyn Results" >> "${RESULTS_FILE}"
        echo "- **Status:** Not installed" >> "${RESULTS_FILE}"
        echo "" >> "${RESULTS_FILE}"
    fi
}

# Run Mythril
run_mythril() {
    log_info "Running Mythril..."
    local output="${OUTPUT_DIR}/mythril_${TIMESTAMP}.json"
    
    if command_exists myth; then
        # Find Solidity files
        local sol_files
        sol_files=$(find "${PROJECT_DIR}" -name "*.sol" -type f 2>/dev/null | head -5)
        
        if [ -n "$sol_files" ]; then
            # Run mythril on first contract file
            local first_file
            first_file=$(echo "$sol_files" | head -1)
            if myth analyze "${first_file}" --json "${output}" >/dev/null 2>&1; then
                MYTHRIL_COUNT=$(count_json_findings "${output}")
                log_success "Mythril completed: ${MYTHRIL_COUNT} findings"
                echo "## Mythril Results" >> "${RESULTS_FILE}"
                echo "- **Findings:** ${MYTHRIL_COUNT}" >> "${RESULTS_FILE}"
                echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
                echo "" >> "${RESULTS_FILE}"
            else
                log_warn "Mythril found issues or encountered errors"
                MYTHRIL_COUNT=$(count_json_findings "${output}")
                echo "## Mythril Results" >> "${RESULTS_FILE}"
                echo "- **Findings:** ${MYTHRIL_COUNT}" >> "${RESULTS_FILE}"
                echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
                echo "" >> "${RESULTS_FILE}"
            fi
        else
            log_warn "No Solidity files found for Mythril"
            echo "## Mythril Results" >> "${RESULTS_FILE}"
            echo "- **Status:** No Solidity files found" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        fi
    else
        log_error "Mythril not installed. Install with: pip install mythril"
        echo "## Mythril Results" >> "${RESULTS_FILE}"
        echo "- **Status:** Not installed" >> "${RESULTS_FILE}"
        echo "" >> "${RESULTS_FILE}"
    fi
}

# Run Solhint
run_solhint() {
    log_info "Running Solhint..."
    local output="${OUTPUT_DIR}/solhint_${TIMESTAMP}.txt"
    
    if command_exists solhint; then
        if solhint "${PROJECT_DIR}/**/*.sol" > "${output}" 2>&1; then
            SOLHINT_COUNT=$(grep -c "error\|warning" "${output}" 2>/dev/null || echo "0")
            log_success "Solhint completed: ${SOLHINT_COUNT} issues"
            echo "## Solhint Results" >> "${RESULTS_FILE}"
            echo "- **Issues:** ${SOLHINT_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        else
            SOLHINT_COUNT=$(grep -c "error\|warning" "${output}" 2>/dev/null || echo "0")
            log_warn "Solhint found issues"
            echo "## Solhint Results" >> "${RESULTS_FILE}"
            echo "- **Issues:** ${SOLHINT_COUNT}" >> "${RESULTS_FILE}"
            echo "- **Output:** ${output}" >> "${RESULTS_FILE}"
            echo "" >> "${RESULTS_FILE}"
        fi
    else
        log_error "Solhint not installed. Install with: npm install -g solhint"
        echo "## Solhint Results" >> "${RESULTS_FILE}"
        echo "- **Status:** Not installed" >> "${RESULTS_FILE}"
        echo "" >> "${RESULTS_FILE}"
    fi
}

# Generate summary
generate_summary() {
    TOTAL_COUNT=$((SLITHER_COUNT + ADERYN_COUNT + MYTHRIL_COUNT + SOLHINT_COUNT))
    
    cat >> "${RESULTS_FILE}" << EOF
## Summary

| Tool | Findings |
|------|----------|
| Slither | ${SLITHER_COUNT} |
| Aderyn | ${ADERYN_COUNT} |
| Mythril | ${MYTHRIL_COUNT} |
| Solhint | ${SOLHINT_COUNT} |
| **Total** | **${TOTAL_COUNT}** |

## Next Steps

1. Review all tool outputs for confirmed findings
2. Deduplicate findings across tools
3. Classify findings by severity
4. Perform manual review for missed vulnerabilities
5. Generate final audit report

---

*Generated by static-analysis-runner.sh*
EOF

    log_info "Summary written to: ${RESULTS_FILE}"
}

# Main execution
main() {
    log_info "Starting static analysis for: ${PROJECT_DIR}"
    log_info "Output directory: ${OUTPUT_DIR}"
    echo ""
    
    run_slither
    run_aderyn
    run_mythril
    run_solhint
    
    generate_summary
    
    echo ""
    log_success "Static analysis complete!"
    log_info "Total findings: ${TOTAL_COUNT}"
    log_info "Results: ${RESULTS_FILE}"
}

main "$@"
