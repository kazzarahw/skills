#!/usr/bin/env bash
# =============================================================================
# static-analysis-runner.sh
#
# Comprehensive static analysis runner for web2 and web3 security audits.
# Executes multiple tools, aggregates results, deduplicates findings, and
# generates structured output.
#
# Usage:
#   ./static-analysis-runner.sh [OPTIONS] <target_path>
#
# Options:
#   -t, --type <web2|web3|auto>     Target type (default: auto-detect)
#   -o, --output <directory>        Output directory (default: ./audit-results)
#   -f, --format <json|text|sarif>  Output format (default: json)
#   --severity <level>              Minimum severity (low|medium|high|critical)
#   --skip <tool1,tool2>            Comma-separated list of tools to skip
#   --include <tool1,tool2>         Comma-separated list of tools to include
#   -v, --verbose                   Verbose output
#   -h, --help                      Show this help message
#
# Examples:
#   ./static-analysis-runner.sh ./contracts
#   ./static-analysis-runner.sh -t web3 -o ./results ./src
#   ./static-analysis-runner.sh -t web2 --severity high ./app
# =============================================================================

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"
OUTPUT_DIR="./audit-results"
OUTPUT_FORMAT="json"
TARGET_TYPE="auto"
MIN_SEVERITY="low"
VERBOSE=false
SKIP_TOOLS=""
INCLUDE_TOOLS=""

# Tool availability flags
HAS_SLITHER=false
HAS_ADERYN=false
HAS_MYTHRIL=false
HAS_SOLHINT=false
HAS_SEMGREP=false
HAS_BANDIT=false
HAS_SAFETY=false
HAS_NPMAUDIT=false
HAS_GOVULNCHECK=false
HAS_CARGOAUDIT=false
HAS_GOSEC=false

# Result files
SLITHER_RESULTS=""
ADERYN_RESULTS=""
MYTHRIL_RESULTS=""
SOLHINT_RESULTS=""
SEMGREP_RESULTS=""
BANDIT_RESULTS=""
SAFETY_RESULTS=""
NPMAUDIT_RESULTS=""
GOVULNCHECK_RESULTS=""
CARGOAUDIT_RESULTS=""
GOSEC_RESULTS=""

# ─── Color Codes ─────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ─── Helper Functions ────────────────────────────────────────────────────────

log_info() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_section() {
    echo -e "\n${BOLD}${CYAN}═══ $1 ═══${NC}\n"
}

show_help() {
    sed -n '2,30p' "$0" | sed 's/^# \?//'
    exit 0
}

check_tool() {
    local tool="$1"
    if command -v "$tool" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

detect_target_type() {
    local target="$1"
    
    log_info "Auto-detecting target type..."
    
    # Check for Solidity files
    if find "$target" -name "*.sol" -type f 2>/dev/null | head -1 | grep -q .; then
        log_info "Detected Solidity files — target type: web3"
        echo "web3"
        return
    fi
    
    # Check for Rust files (Solana/Near)
    if find "$target" -name "*.rs" -type f 2>/dev/null | head -1 | grep -q .; then
        log_info "Detected Rust files — target type: web3"
        echo "web3"
        return
    fi
    
    # Check for Move files (Aptos/Sui)
    if find "$target" -name "*.move" -type f 2>/dev/null | head -1 | grep -q .; then
        log_info "Detected Move files — target type: web3"
        echo "web3"
        return
    fi
    
    # Check for package.json (Node.js)
    if [[ -f "$target/package.json" ]]; then
        log_info "Detected package.json — target type: web2"
        echo "web2"
        return
    fi
    
    # Check for requirements.txt or pyproject.toml (Python)
    if [[ -f "$target/requirements.txt" ]] || [[ -f "$target/pyproject.toml" ]]; then
        log_info "Detected Python project — target type: web2"
        echo "web2"
        return
    fi
    
    # Check for go.mod (Go)
    if [[ -f "$target/go.mod" ]]; then
        log_info "Detected Go project — target type: web2"
        echo "web2"
        return
    fi
    
    # Check for Cargo.toml (Rust)
    if [[ -f "$target/Cargo.toml" ]]; then
        log_info "Detected Rust project — target type: web2"
        echo "web2"
        return
    fi
    
    # Default to web2
    log_warning "Could not auto-detect target type — defaulting to web2"
    echo "web2"
}

should_run_tool() {
    local tool="$1"
    
    # Check if tool is in skip list
    if [[ -n "$SKIP_TOOLS" ]]; then
        if echo ",$SKIP_TOOLS," | grep -q ",$tool,"; then
            return 1
        fi
    fi
    
    # Check if include list is specified and tool is not in it
    if [[ -n "$INCLUDE_TOOLS" ]]; then
        if ! echo ",$INCLUDE_TOOLS," | grep -q ",$tool,"; then
            return 1
        fi
    fi
    
    return 0
}

# ─── Tool Detection ──────────────────────────────────────────────────────────

detect_tools() {
    log_section "Detecting Available Tools"
    
    # Web3 tools
    if check_tool slither; then
        HAS_SLITHER=true
        log_info "Slither: $(slither --version 2>/dev/null || echo 'installed')"
    else
        log_warning "Slither not found — install with: pip install slither-analyzer"
    fi
    
    if check_tool aderyn; then
        HAS_ADERYN=true
        log_info "Aderyn: installed"
    else
        log_warning "Aderyn not found — install with: cargo install aderyn"
    fi
    
    if check_tool myth; then
        HAS_MYTHRIL=true
        log_info "Mythril: installed"
    else
        log_warning "Mythril not found — install with: pip install mythril"
    fi
    
    if check_tool solhint; then
        HAS_SOLHINT=true
        log_info "Solhint: installed"
    else
        log_warning "Solhint not found — install with: npm install -g solhint"
    fi
    
    # Web2 tools
    if check_tool bandit; then
        HAS_BANDIT=true
        log_info "Bandit: installed"
    else
        log_warning "Bandit not found — install with: pip install bandit"
    fi
    
    if check_tool safety; then
        HAS_SAFETY=true
        log_info "Safety: installed"
    else
        log_warning "Safety not found — install with: pip install safety"
    fi
    
    if check_tool npm; then
        HAS_NPMAUDIT=true
        log_info "npm audit: available"
    else
        log_warning "npm not found"
    fi
    
    if check_tool gosec; then
        HAS_GOSEC=true
        log_info "gosec: installed"
    else
        log_warning "gosec not found — install with: go install github.com/securego/gosec/v2/cmd/gosec@latest"
    fi
    
    if check_tool govulncheck; then
        HAS_GOVULNCHECK=true
        log_info "govulncheck: installed"
    else
        log_warning "govulncheck not found — install with: go install golang.org/x/vuln/cmd/govulncheck@latest"
    fi
    
    if check_tool cargo; then
        HAS_CARGOAUDIT=true
        log_info "cargo audit: available"
    else
        log_warning "cargo not found"
    fi
    
    # Common tools
    if check_tool semgrep; then
        HAS_SEMGREP=true
        log_info "Semgrep: installed"
    else
        log_warning "Semgrep not found — install with: pip install semgrep"
    fi
    
    echo ""
}

# ─── Web3 Analysis Functions ─────────────────────────────────────────────────

run_slither() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_SLITHER" != true ]] || ! should_run_tool "slither"; then
        return
    fi
    
    log_section "Running Slither"
    
    local result_file="$output_dir/slither-results.json"
    SLITHER_RESULTS="$result_file"
    
    slither "$target" \
        --json "$result_file" \
        --exclude-optimization \
        --exclude-informational \
        2>&1 | tee "$output_dir/slither-output.log"
    
    if [[ -f "$result_file" ]]; then
        local count=$(jq '.results | length' "$result_file" 2>/dev/null || echo "0")
        log_success "Slither completed — $count findings"
    else
        log_warning "Slither produced no results"
    fi
}

run_aderyn() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_ADERYN" != true ]] || ! should_run_tool "aderyn"; then
        return
    fi
    
    log_section "Running Aderyn"
    
    local result_file="$output_dir/aderyn-results.json"
    ADERYN_RESULTS="$result_file"
    
    aderyn "$target" \
        --json "$result_file" \
        2>&1 | tee "$output_dir/aderyn-output.log"
    
    if [[ -f "$result_file" ]]; then
        log_success "Aderyn completed"
    else
        log_warning "Aderyn produced no results"
    fi
}

run_mythril() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_MYTHRIL" != true ]] || ! should_run_tool "mythril"; then
        return
    fi
    
    log_section "Running Mythril"
    
    local result_file="$output_dir/mythril-results.json"
    MYTHRIL_RESULTS="$result_file"
    
    # Find Solidity files
    local sol_files
    sol_files=$(find "$target" -name "*.sol" -type f 2>/dev/null | head -5)
    
    if [[ -z "$sol_files" ]]; then
        log_warning "No Solidity files found for Mythril"
        return
    fi
    
    myth analyze "$target" \
        --execution-timeout 300 \
        --json "$result_file" \
        2>&1 | tee "$output_dir/mythril-output.log" || true
    
    if [[ -f "$result_file" ]]; then
        log_success "Mythril completed"
    else
        log_warning "Mythril produced no results"
    fi
}

run_solhint() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_SOLHINT" != true ]] || ! should_run_tool "solhint"; then
        return
    fi
    
    log_section "Running Solhint"
    
    local result_file="$output_dir/solhint-results.json"
    SOLHINT_RESULTS="$result_file"
    
    solhint "$target/**/*.sol" \
        --formatter json \
        > "$result_file" 2>&1 || true
    
    if [[ -f "$result_file" ]]; then
        local count=$(jq 'length' "$result_file" 2>/dev/null || echo "0")
        log_success "Solhint completed — $count findings"
    else
        log_warning "Solhint produced no results"
    fi
}

# ─── Web2 Analysis Functions ─────────────────────────────────────────────────

run_bandit() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_BANDIT" != true ]] || ! should_run_tool "bandit"; then
        return
    fi
    
    log_section "Running Bandit"
    
    local result_file="$output_dir/bandit-results.json"
    BANDIT_RESULTS="$result_file"
    
    bandit -r "$target" \
        -f json \
        -o "$result_file" \
        -ll \
        2>&1 | tee "$output_dir/bandit-output.log" || true
    
    if [[ -f "$result_file" ]]; then
        local count=$(jq '.results | length' "$result_file" 2>/dev/null || echo "0")
        log_success "Bandit completed — $count findings"
    else
        log_warning "Bandit produced no results"
    fi
}

run_safety() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_SAFETY" != true ]] || ! should_run_tool "safety"; then
        return
    fi
    
    log_section "Running Safety"
    
    local result_file="$output_dir/safety-results.json"
    SAFETY_RESULTS="$result_file"
    
    safety check \
        --json \
        --output "$result_file" \
        2>&1 | tee "$output_dir/safety-output.log" || true
    
    if [[ -f "$result_file" ]]; then
        log_success "Safety completed"
    else
        log_warning "Safety produced no results"
    fi
}

run_npm_audit() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_NPMAUDIT" != true ]] || ! should_run_tool "npm-audit"; then
        return
    fi
    
    if [[ ! -f "$target/package.json" ]]; then
        log_warning "No package.json found — skipping npm audit"
        return
    fi
    
    log_section "Running npm audit"
    
    local result_file="$output_dir/npm-audit-results.json"
    NPMAUDIT_RESULTS="$result_file"
    
    cd "$target"
    npm audit --json > "$result_file" 2>&1 || true
    cd - > /dev/null
    
    if [[ -f "$result_file" ]]; then
        local count=$(jq '.metadata.vulnerabilities.total // 0' "$result_file" 2>/dev/null || echo "0")
        log_success "npm audit completed — $count vulnerabilities"
    else
        log_warning "npm audit produced no results"
    fi
}

run_gosec() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_GOSEC" != true ]] || ! should_run_tool "gosec"; then
        return
    fi
    
    if [[ ! -f "$target/go.mod" ]]; then
        log_warning "No go.mod found — skipping gosec"
        return
    fi
    
    log_section "Running gosec"
    
    local result_file="$output_dir/gosec-results.json"
    GOSEC_RESULTS="$result_file"
    
    gosec -fmt json -out "$result_file" "$target/..." 2>&1 | tee "$output_dir/gosec-output.log" || true
    
    if [[ -f "$result_file" ]]; then
        log_success "gosec completed"
    else
        log_warning "gosec produced no results"
    fi
}

run_govulncheck() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_GOVULNCHECK" != true ]] || ! should_run_tool "govulncheck"; then
        return
    fi
    
    if [[ ! -f "$target/go.mod" ]]; then
        log_warning "No go.mod found — skipping govulncheck"
        return
    fi
    
    log_section "Running govulncheck"
    
    local result_file="$output_dir/govulncheck-results.json"
    GOVULNCHECK_RESULTS="$result_file"
    
    cd "$target"
    govulncheck -json ./... > "$result_file" 2>&1 || true
    cd - > /dev/null
    
    if [[ -f "$result_file" ]]; then
        log_success "govulncheck completed"
    else
        log_warning "govulncheck produced no results"
    fi
}

run_cargo_audit() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_CARGOAUDIT" != true ]] || ! should_run_tool "cargo-audit"; then
        return
    fi
    
    if [[ ! -f "$target/Cargo.toml" ]]; then
        log_warning "No Cargo.toml found — skipping cargo audit"
        return
    fi
    
    log_section "Running cargo audit"
    
    local result_file="$output_dir/cargo-audit-results.json"
    CARGOAUDIT_RESULTS="$result_file"
    
    cd "$target"
    cargo audit --json > "$result_file" 2>&1 || true
    cd - > /dev/null
    
    if [[ -f "$result_file" ]]; then
        log_success "cargo audit completed"
    else
        log_warning "cargo audit produced no results"
    fi
}

# ─── Common Analysis Functions ───────────────────────────────────────────────

run_semgrep() {
    local target="$1"
    local output_dir="$2"
    
    if [[ "$HAS_SEMGREP" != true ]] || ! should_run_tool "semgrep"; then
        return
    fi
    
    log_section "Running Semgrep"
    
    local result_file="$output_dir/semgrep-results.json"
    SEMGREP_RESULTS="$result_file"
    
    # Use appropriate config based on target type
    local config="p/owasp-top-ten"
    if [[ "$TARGET_TYPE" == "web3" ]]; then
        config="p/smart-contracts"
    fi
    
    semgrep --config="$config" \
        "$target" \
        --json \
        --output "$result_file" \
        --quiet \
        2>&1 | tee "$output_dir/semgrep-output.log" || true
    
    if [[ -f "$result_file" ]]; then
        local count=$(jq '.results | length' "$result_file" 2>/dev/null || echo "0")
        log_success "Semgrep completed — $count findings"
    else
        log_warning "Semgrep produced no results"
    fi
}

# ─── Result Aggregation ───────────────────────────────────────────────────────

aggregate_results() {
    local output_dir="$1"
    
    log_section "Aggregating Results"
    
    local aggregated_file="$output_dir/aggregated-results.json"
    
    # Create aggregated JSON structure
    cat > "$aggregated_file" << 'EOF'
{
    "metadata": {
        "timestamp": "TIMESTAMP",
        "target_type": "TARGET_TYPE",
        "tools_run": [],
        "total_findings": 0,
        "findings_by_severity": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0
        }
    },
    "findings": []
}
EOF
    
    # Replace placeholders
    sed -i "s/TIMESTAMP/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" "$aggregated_file"
    sed -i "s/TARGET_TYPE/$TARGET_TYPE/g" "$aggregated_file"
    
    # Collect findings from each tool
    local all_findings="[]"
    
    # Slither findings
    if [[ -n "$SLITHER_RESULTS" ]] && [[ -f "$SLITHER_RESULTS" ]]; then
        log_info "Processing Slither results..."
        local slither_findings
        slither_findings=$(jq -c '[.results[]? | {
            tool: "slither",
            title: .check,
            description: .description,
            severity: (.impact | ascii_downcase),
            confidence: (.confidence | ascii_downcase),
            swc: (.id // "N/A"),
            file: (.filename // "N/A"),
            line: (.line // 0)
        }]' "$SLITHER_RESULTS" 2>/dev/null || echo "[]")
        all_findings=$(jq -c --argjson new "$slither_findings" '. + $new' <<< "$all_findings")
    fi
    
    # Semgrep findings
    if [[ -n "$SEMGREP_RESULTS" ]] && [[ -f "$SEMGREP_RESULTS" ]]; then
        log_info "Processing Semgrep results..."
        local semgrep_findings
        semgrep_findings=$(jq -c '[.results[]? | {
            tool: "semgrep",
            title: .check_id,
            description: .extra.message,
            severity: (.extra.severity | ascii_downcase),
            confidence: "medium",
            swc: "N/A",
            file: .path,
            line: .start.line
        }]' "$SEMGREP_RESULTS" 2>/dev/null || echo "[]")
        all_findings=$(jq -c --argjson new "$semgrep_findings" '. + $new' <<< "$all_findings")
    fi
    
    # Bandit findings
    if [[ -n "$BANDIT_RESULTS" ]] && [[ -f "$BANDIT_RESULTS" ]]; then
        log_info "Processing Bandit results..."
        local bandit_findings
        bandit_findings=$(jq -c '[.results[]? | {
            tool: "bandit",
            title: .test_id,
            description: .issue_text,
            severity: (.issue_severity | ascii_downcase),
            confidence: "high",
            swc: "N/A",
            file: .filename,
            line: .line_number
        }]' "$BANDIT_RESULTS" 2>/dev/null || echo "[]")
        all_findings=$(jq -c --argjson new "$bandit_findings" '. + $new' <<< "$all_findings")
    fi
    
    # Deduplicate findings (same file + line + similar title)
    log_info "Deduplicating findings..."
    local deduplicated
    deduplicated=$(jq -c 'unique_by(.file + ":" + (.line | tostring) + ":" + .title)' <<< "$all_findings")
    
    # Count by severity
    local critical_count high_count medium_count low_count info_count
    critical_count=$(jq '[.[] | select(.severity == "critical")] | length' <<< "$deduplicated")
    high_count=$(jq '[.[] | select(.severity == "high")] | length' <<< "$deduplicated")
    medium_count=$(jq '[.[] | select(.severity == "medium")] | length' <<< "$deduplicated")
    low_count=$(jq '[.[] | select(.severity == "low")] | length' <<< "$deduplicated")
    info_count=$(jq '[.[] | select(.severity == "informational" or .severity == "info")] | length' <<< "$deduplicated")
    
    local total=$((critical_count + high_count + medium_count + low_count + info_count))
    
    # Update aggregated file
    jq --argjson findings "$deduplicated" \
       --argjson total "$total" \
       --argjson critical "$critical_count" \
       --argjson high "$high_count" \
       --argjson medium "$medium_count" \
       --argjson low "$low_count" \
       --argjson info "$info_count" \
       '.findings = $findings |
        .metadata.total_findings = $total |
        .metadata.findings_by_severity.critical = $critical |
        .metadata.findings_by_severity.high = $high |
        .metadata.findings_by_severity.medium = $medium |
        .metadata.findings_by_severity.low = $low |
        .metadata.findings_by_severity.informational = $info' \
       "$aggregated_file" > "${aggregated_file}.tmp" && mv "${aggregated_file}.tmp" "$aggregated_file"
    
    log_success "Aggregation complete — $total unique findings"
    echo ""
    echo -e "  ${RED}Critical:${NC} $critical_count"
    echo -e "  ${RED}High:${NC}     $high_count"
    echo -e "  ${YELLOW}Medium:${NC}   $medium_count"
    echo -e "  ${BLUE}Low:${NC}      $low_count"
    echo -e "  ${GREEN}Info:${NC}      $info_count"
    echo ""
}

generate_report() {
    local output_dir="$1"
    
    log_section "Generating Report"
    
    local report_file="$output_dir/audit-report.md"
    
    cat > "$report_file" << EOF
# Static Analysis Report

**Date:** $(date -u +%Y-%m-%d)
**Target Type:** $TARGET_TYPE
**Output Format:** $OUTPUT_FORMAT

## Summary

| Severity | Count |
|----------|-------|
| Critical | $(jq '.metadata.findings_by_severity.critical' "$output_dir/aggregated-results.json") |
| High | $(jq '.metadata.findings_by_severity.high' "$output_dir/aggregated-results.json") |
| Medium | $(jq '.metadata.findings_by_severity.medium' "$output_dir/aggregated-results.json") |
| Low | $(jq '.metadata.findings_by_severity.low' "$output_dir/aggregated-results.json") |
| Informational | $(jq '.metadata.findings_by_severity.informational' "$output_dir/aggregated-results.json") |
| **Total** | **$(jq '.metadata.total_findings' "$output_dir/aggregated-results.json")** |

## Tools Executed

EOF
    
    # Add tools that were run
    for tool in slither aderyn mythril solhint semgrep bandit safety npm-audit gosec govulncheck cargo-audit; do
        local result_var="${tool//-/_}_RESULTS"
        result_var=$(echo "$result_var" | tr '[:lower:]' '[:upper:]')
        if [[ -n "${!result_var:-}" ]] && [[ -f "${!result_var}" ]]; then
            echo "- $tool" >> "$report_file"
        fi
    done
    
    echo "" >> "$report_file"
    echo "## Findings" >> "$report_file"
    echo "" >> "$report_file"
    
    # Add findings table
    echo "| Tool | Severity | Title | File | Line |" >> "$report_file"
    echo "|------|----------|-------|------|------|" >> "$report_file"
    
    jq -r '.findings[] | "| \(.tool) | \(.severity) | \(.title) | \(.file) | \(.line) |"' \
        "$output_dir/aggregated-results.json" >> "$report_file" 2>/dev/null || true
    
    log_success "Report generated: $report_file"
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
    local target=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--type)
                TARGET_TYPE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --severity)
                MIN_SEVERITY="$2"
                shift 2
                ;;
            --skip)
                SKIP_TOOLS="$2"
                shift 2
                ;;
            --include)
                INCLUDE_TOOLS="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                ;;
            *)
                target="$1"
                shift
                ;;
        esac
    done
    
    # Validate target
    if [[ -z "$target" ]]; then
        log_error "No target specified"
        show_help
    fi
    
    if [[ ! -d "$target" ]]; then
        log_error "Target directory does not exist: $target"
        exit 1
    fi
    
    # Auto-detect target type if needed
    if [[ "$TARGET_TYPE" == "auto" ]]; then
        TARGET_TYPE=$(detect_target_type "$target")
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    echo -e "${BOLD}${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Static Analysis Runner v${VERSION}                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Target: $target"
    echo "Type: $TARGET_TYPE"
    echo "Output: $OUTPUT_DIR"
    echo "Format: $OUTPUT_FORMAT"
    echo ""
    
    # Detect available tools
    detect_tools
    
    # Run analysis based on target type
    if [[ "$TARGET_TYPE" == "web3" ]]; then
        run_slither "$target" "$OUTPUT_DIR"
        run_aderyn "$target" "$OUTPUT_DIR"
        run_mythril "$target" "$OUTPUT_DIR"
        run_solhint "$target" "$OUTPUT_DIR"
        run_semgrep "$target" "$OUTPUT_DIR"
    else
        run_bandit "$target" "$OUTPUT_DIR"
        run_safety "$target" "$OUTPUT_DIR"
        run_npm_audit "$target" "$OUTPUT_DIR"
        run_gosec "$target" "$OUTPUT_DIR"
        run_govulncheck "$target" "$OUTPUT_DIR"
        run_cargo_audit "$target" "$OUTPUT_DIR"
        run_semgrep "$target" "$OUTPUT_DIR"
    fi
    
    # Aggregate and report
    aggregate_results "$OUTPUT_DIR"
    generate_report "$OUTPUT_DIR"
    
    log_section "Analysis Complete"
    log_success "Results saved to: $OUTPUT_DIR"
    echo ""
    echo "Files generated:"
    echo "  - $OUTPUT_DIR/aggregated-results.json"
    echo "  - $OUTPUT_DIR/audit-report.md"
    echo ""
}

main "$@"
