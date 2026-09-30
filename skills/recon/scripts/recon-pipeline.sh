#!/usr/bin/env bash
#
# recon-pipeline.sh - Automated web2/web3 reconnaissance pipeline
#
# Usage: ./recon-pipeline.sh -t <target> -s <scope-file> -o <output-dir> [-m web2|web3|mixed]
#
# This script performs comprehensive reconnaissance:
#   - Passive recon (subfinder, theHarvester)
#   - Active recon (masscan, nmap)
#   - Web fingerprinting (whatweb)
#   - Vulnerability scanning (nuclei)
#   - Structured output generation
#
# Constitutional rules enforced:
#   - Scope validation before any active scanning
#   - Rate limiting on all active scans
#   - Evidence capture for all findings
#   - Structured output format
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
readonly TIMESTAMP=$(date +%Y%m%d-%H%M%S)
readonly VERSION="1.0.0"

# Default values
TARGET=""
SCOPE_FILE=""
OUTPUT_DIR="./recon-output"
MODE="web2"
RATE_LIMIT=1000
TIMING="T3"
VERBOSE=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

usage() {
    cat << EOF
Usage: $SCRIPT_NAME -t <target> -s <scope-file> -o <output-dir> [options]

Required:
    -t, --target       Target (domain, IP, or blockchain address)
    -s, --scope        Scope file (one target per line)
    -o, --output       Output directory

Optional:
    -m, --mode         Scan mode: web2, web3, mixed (default: web2)
    -r, --rate         Rate limit for masscan (default: 1000 pps)
    -T, --timing       nmap timing template: T0-T5 (default: T3)
    -v, --verbose      Verbose output
    -d, --dry-run      Show commands without executing
    -h, --help         Show this help message

Examples:
    $SCRIPT_NAME -t example.com -s scope.txt -o ./output
    $SCRIPT_NAME -t 10.0.0.0/24 -s scope.txt -o ./output -m web2 -r 5000
    $SCRIPT_NAME -t 0x1234... -s scope.txt -o ./output -m web3

EOF
    exit 0
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_debug() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Validate scope - ensure target is in scope
validate_scope() {
    local target="$1"
    local scope_file="$2"

    if [[ ! -f "$scope_file" ]]; then
        log_error "Scope file not found: $scope_file"
        exit 1
    fi

    # Check if target is in scope
    if grep -qF "$target" "$scope_file"; then
        log_info "Target $target is IN SCOPE"
        return 0
    fi

    # Check for CIDR ranges
    if [[ "$target" == */* ]]; then
        local network=$(echo "$target" | cut -d'/' -f1)
        if grep -qF "$network" "$scope_file"; then
            log_info "Target $target is IN SCOPE (CIDR match)"
            return 0
        fi
    fi

    # Check for domain subdomains
    if [[ "$target" == *.* ]]; then
        # Extract base domain handling multi-level TLDs (e.g., example.co.uk)
        local domain
        # Try two-part TLD first (co.uk, com.au, etc.)
        domain=$(echo "$target" | awk -F. '{
            if (NF >= 3) {
                # Check if last two parts look like a TLD (2-3 chars each)
                last = $NF
                second = $(NF-1)
                if (length(last) <= 3 && length(second) <= 3) {
                    print $(NF-2)"."$(NF-1)"."$NF
                } else {
                    print $(NF-1)"."$NF
                }
            } else {
                print $(NF-1)"."$NF
            }
        }')
        if grep -qF "$domain" "$scope_file"; then
            log_info "Target $target is IN SCOPE (domain match: $domain)"
            return 0
        fi
    fi

    log_error "Target $target is OUT OF SCOPE - ABORTING"
    exit 1
}

# Validate dependencies
check_dependencies() {
    local missing=()

    # Core dependencies
    for cmd in nmap masscan subfinder theHarvester whatweb nuclei jq curl; do
        if ! command_exists "$cmd"; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_warn "Missing tools: ${missing[*]}"
        log_warn "Some pipeline stages will be skipped"
    fi
}

# Create output directory structure
setup_output() {
    local output_dir="$1"

    mkdir -p "$output_dir"/{passive,active,web,vuln,evidence,reports}

    log_info "Output directory: $output_dir"
}

# ============================================================================
# Passive Reconnaissance
# ============================================================================

run_passive_recon() {
    local target="$1"
    local output_dir="$2"

    log_info "=== Phase 1: Passive Reconnaissance ==="

    # Subdomain enumeration
    if command_exists subfinder; then
        log_info "Running subfinder for subdomain enumeration..."
        if [[ "$DRY_RUN" == false ]]; then
            subfinder -d "$target" -o "$output_dir/passive/subdomains.txt" 2>&1 | tee "$output_dir/evidence/subfinder.log"
            log_info "Subdomains found: $(wc -l < "$output_dir/passive/subdomains.txt" 2>/dev/null || echo 0)"
        else
            log_debug "subfinder -d $target -o $output_dir/passive/subdomains.txt"
        fi
    else
        log_warn "subfinder not found, skipping subdomain enumeration"
    fi

    # OSINT collection
    if command_exists theHarvester; then
        log_info "Running theHarvester for OSINT collection..."
        if [[ "$DRY_RUN" == false ]]; then
            theHarvester -d "$target" -b all -f "$output_dir/passive/osint.html" 2>&1 | tee "$output_dir/evidence/theharvester.log"
            log_info "OSINT results saved to $output_dir/passive/osint.html"
        else
            log_debug "theHarvester -d $target -b all -f $output_dir/passive/osint.html"
        fi
    else
        log_warn "theHarvester not found, skipping OSINT collection"
    fi

    # Certificate transparency
    log_info "Querying certificate transparency logs..."
    if [[ "$DRY_RUN" == false ]]; then
        curl -s --connect-timeout 10 --max-time 30 "https://crt.sh/?q=%25.$target&output=json" 2>/dev/null | jq -r '.[].name_value' 2>/dev/null | sort -u > "$output_dir/passive/crtsh-subdomains.txt" || true
        log_info "crt.sh subdomains found: $(wc -l < "$output_dir/passive/crtsh-subdomains.txt" 2>/dev/null || echo 0)"
    else
        log_debug "curl -s https://crt.sh/?q=%25.$target ..."
    fi

    # DNS enumeration
    if command_exists dig; then
        log_info "Running DNS enumeration..."
        if [[ "$DRY_RUN" == false ]]; then
            {
                echo "=== A Records ==="
                dig "$target" A +noall +answer 2>/dev/null || true
                echo ""
                echo "=== AAAA Records ==="
                dig "$target" AAAA +noall +answer 2>/dev/null || true
                echo ""
                echo "=== MX Records ==="
                dig "$target" MX +noall +answer 2>/dev/null || true
                echo ""
                echo "=== NS Records ==="
                dig "$target" NS +noall +answer 2>/dev/null || true
                echo ""
                echo "=== TXT Records ==="
                dig "$target" TXT +noall +answer 2>/dev/null || true
                echo ""
                echo "=== SOA Records ==="
                dig "$target" SOA +noall +answer 2>/dev/null || true
                echo ""
                echo "=== CNAME Records ==="
                dig "$target" CNAME +noall +answer 2>/dev/null || true
            } > "$output_dir/passive/dns-records.txt" 2>&1 || true
            log_info "DNS records saved to $output_dir/passive/dns-records.txt"
        else
            log_debug "dig $target A +noall +answer"
        fi
    else
        log_warn "dig not found, skipping DNS enumeration"
    fi

    # Combine subdomain lists
    if [[ "$DRY_RUN" == false ]]; then
        cat "$output_dir/passive/subdomains.txt" "$output_dir/passive/crtsh-subdomains.txt" 2>/dev/null | sort -u > "$output_dir/passive/all-subdomains.txt"
        log_info "Total unique subdomains: $(wc -l < "$output_dir/passive/all-subdomains.txt" 2>/dev/null || echo 0)"
    fi

    log_info "Passive recon complete"
}

# ============================================================================
# Active Reconnaissance
# ============================================================================

run_active_recon() {
    local target="$1"
    local output_dir="$2"
    local rate="$3"
    local timing="$4"

    log_info "=== Phase 2: Active Reconnaissance ==="

    # Fast port scan with masscan
    if command_exists masscan; then
        log_info "Running masscan for fast port scan (rate: $rate pps)..."
        if [[ "$DRY_RUN" == false ]]; then
            timeout 300 masscan -p1-65535 "$target" --rate="$rate" -oJ "$output_dir/active/masscan-results.json" 2>&1 | tee "$output_dir/evidence/masscan.log" || true
            log_info "Masscan results saved to $output_dir/active/masscan-results.json"
        else
            log_debug "masscan -p1-65535 $target --rate=$rate -oJ $output_dir/active/masscan-results.json"
        fi
    else
        log_warn "masscan not found, skipping fast port scan"
    fi

    # Detailed port scan with nmap
    if command_exists nmap; then
        log_info "Running nmap for detailed port scan (timing: $timing)..."
        if [[ "$DRY_RUN" == false ]]; then
            timeout 600 nmap -sS -sV -sC -O -"$timing" -p- "$target" -oA "$output_dir/active/nmap-results" 2>&1 | tee "$output_dir/evidence/nmap.log" || true
            log_info "Nmap results saved to $output_dir/active/nmap-results.*"
        else
            log_debug "nmap -sS -sV -sC -O -$timing -p- $target -oA $output_dir/active/nmap-results"
        fi
    else
        log_warn "nmap not found, skipping detailed port scan"
    fi

    # Extract open ports from nmap
    if [[ "$DRY_RUN" == false ]] && [[ -f "$output_dir/active/nmap-results.gnmap" ]]; then
        grep "open" "$output_dir/active/nmap-results.gnmap" | awk '{print $2}' > "$output_dir/active/open-ports.txt"
        log_info "Open ports: $(wc -l < "$output_dir/active/open-ports.txt" 2>/dev/null || echo 0)"
    fi

    log_info "Active recon complete"
}

# ============================================================================
# Web Fingerprinting
# ============================================================================

run_web_fingerprinting() {
    local target="$1"
    local output_dir="$2"

    log_info "=== Phase 3: Web Fingerprinting ==="

    if command_exists whatweb; then
        log_info "Running whatweb for web fingerprinting..."
        if [[ "$DRY_RUN" == false ]]; then
            whatweb -a 1 "$target" --log-verbose="$output_dir/web/whatweb-results.txt" 2>&1 | tee "$output_dir/evidence/whatweb.log"
            log_info "WhatWeb results saved to $output_dir/web/whatweb-results.txt"
        else
            log_debug "whatweb -a 1 $target --log-verbose=$output_dir/web/whatweb-results.txt"
        fi
    else
        log_warn "whatweb not found, skipping web fingerprinting"
    fi

    # HTTP headers
    log_info "Capturing HTTP headers..."
    if [[ "$DRY_RUN" == false ]]; then
        curl -sI --connect-timeout 10 --max-time 30 "$target" > "$output_dir/web/http-headers.txt" 2>&1 || true
        log_info "HTTP headers saved to $output_dir/web/http-headers.txt"
    else
        log_debug "curl -sI $target > $output_dir/web/http-headers.txt"
    fi

    log_info "Web fingerprinting complete"
}

# ============================================================================
# Vulnerability Scanning
# ============================================================================

run_vuln_scanning() {
    local target="$1"
    local output_dir="$2"

    log_info "=== Phase 4: Vulnerability Scanning ==="

    if command_exists nuclei; then
        log_info "Running nuclei for vulnerability scanning..."
        if [[ "$DRY_RUN" == false ]]; then
            timeout 600 nuclei -u "$target" -t cves/ -severity critical,high,medium -o "$output_dir/vuln/nuclei-results.json" -json 2>&1 | tee "$output_dir/evidence/nuclei.log" || true
            log_info "Nuclei results saved to $output_dir/vuln/nuclei-results.json"
        else
            log_debug "nuclei -u $target -t cves/ -severity critical,high,medium -o $output_dir/vuln/nuclei-results.json -json"
        fi
    else
        log_warn "nuclei not found, skipping vulnerability scanning"
    fi

    log_info "Vulnerability scanning complete"
}

# ============================================================================
# Web3 Reconnaissance
# ============================================================================

run_web3_recon() {
    local target="$1"
    local output_dir="$2"

    log_info "=== Web3 Reconnaissance ==="

    # Determine chain
    local chain="ethereum"
    if [[ "$target" == 0x* ]]; then
        log_info "EVM address detected, using Ethereum"
    elif [[ "$target" =~ ^[1-9A-HJ-NP-Za-km-z]{32,44}$ ]]; then
        chain="solana"
        log_info "Solana address detected"
    fi

    # Query Etherscan API
    if [[ "$chain" == "ethereum" ]]; then
        log_info "Querying Etherscan API..."
        if [[ "$DRY_RUN" == false ]]; then
            # Get contract info
            curl -s --connect-timeout 10 --max-time 30 "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$target" 2>/dev/null | jq . > "$output_dir/active/etherscan-contract.json" 2>&1 || true

            # Get transactions
            curl -s --connect-timeout 10 --max-time 30 "https://api.etherscan.io/api?module=account&action=txlist&address=$target&startblock=0&endblock=99999999&page=1&offset=100&sort=asc" 2>/dev/null | jq . > "$output_dir/active/etherscan-transactions.json" 2>&1 || true

            # Get balance
            curl -s --connect-timeout 10 --max-time 30 "https://api.etherscan.io/api?module=account&action=balance&address=$target&tag=latest" 2>/dev/null | jq . > "$output_dir/active/etherscan-balance.json" 2>&1 || true

            log_info "Etherscan results saved"
        else
            log_debug "curl -s https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$target"
        fi
    fi

    # Query Solscan API
    if [[ "$chain" == "solana" ]]; then
        log_info "Querying Solscan API..."
        if [[ "$DRY_RUN" == false ]]; then
            curl -s --connect-timeout 10 --max-time 30 "https://api.solscan.io/v2/account/detail?address=$target" 2>/dev/null | jq . > "$output_dir/active/solscan-account.json" 2>&1 || true
            curl -s --connect-timeout 10 --max-time 30 "https://api.solscan.io/v2/account/txs?address=$target&limit=100" 2>/dev/null | jq . > "$output_dir/active/solscan-transactions.json" 2>&1 || true
            log_info "Solscan results saved"
        else
            log_debug "curl -s https://api.solscan.io/v2/account/detail?address=$target"
        fi
    fi

    log_info "Web3 recon complete"
}

# ============================================================================
# False Positive Filtering
# ============================================================================

filter_false_positives() {
    local output_dir="$1"

    log_info "=== Filtering False Positives ==="

    if [[ "$DRY_RUN" == true ]]; then
        log_debug "Filtering false positives..."
        return
    fi

    # Filter nuclei results
    if [[ -f "$output_dir/vuln/nuclei-results.json" ]]; then
        # Remove informational findings
        jq '[.[] | select(.info.severity != "info")]' "$output_dir/vuln/nuclei-results.json" > "$output_dir/vuln/nuclei-filtered.json" 2>/dev/null || true
        log_info "Filtered nuclei results saved to $output_dir/vuln/nuclei-filtered.json"
    fi

    # Filter nmap results
    if [[ -f "$output_dir/active/nmap-results.gnmap" ]]; then
        # Remove closed ports
        grep "open" "$output_dir/active/nmap-results.gnmap" > "$output_dir/active/nmap-open-only.gnmap" 2>/dev/null || true
        log_info "Filtered nmap results saved to $output_dir/active/nmap-open-only.gnmap"
    fi

    log_info "False positive filtering complete"
}

# ============================================================================
# Report Generation
# ============================================================================

generate_report() {
    local target="$1"
    local output_dir="$2"
    local mode="$3"

    log_info "=== Generating Report ==="

    if [[ "$DRY_RUN" == true ]]; then
        log_debug "Generating report..."
        return
    fi

    local report_file="$output_dir/reports/recon-report.md"

    cat > "$report_file" << EOF
# Reconnaissance Report: $target

**Date:** $(date +%Y-%m-%d)
**Time:** $(date +%H:%M:%S)
**Mode:** $mode
**Target:** $target
**Pipeline Version:** $VERSION

## Executive Summary

- **Passive recon:** $([[ -f "$output_dir/passive/all-subdomains.txt" ]] && wc -l < "$output_dir/passive/all-subdomains.txt" || echo 0) subdomains found
- **Active recon:** $([[ -f "$output_dir/active/open-ports.txt" ]] && wc -l < "$output_dir/active/open-ports.txt" || echo 0) open ports found
- **Vulnerabilities:** $([[ -f "$output_dir/vuln/nuclei-results.json" ]] && jq length < "$output_dir/vuln/nuclei-results.json" 2>/dev/null || echo 0) findings

## Findings

### Subdomains
EOF

    if [[ -f "$output_dir/passive/all-subdomains.txt" ]]; then
        echo "" >> "$report_file"
        while IFS= read -r subdomain; do
            echo "- $subdomain" >> "$report_file"
        done < "$output_dir/passive/all-subdomains.txt"
    fi

    cat >> "$report_file" << EOF

### Open Ports
EOF

    if [[ -f "$output_dir/active/open-ports.txt" ]]; then
        echo "" >> "$report_file"
        while IFS= read -r port; do
            echo "- $port" >> "$report_file"
        done < "$output_dir/active/open-ports.txt"
    fi

    cat >> "$report_file" << EOF

### Vulnerabilities
EOF

    if [[ -f "$output_dir/vuln/nuclei-results.json" ]]; then
        echo "" >> "$report_file"
        jq -r '.[] | "- [\(.info.severity)] \(info.name): \(.matched-at)"' "$output_dir/vuln/nuclei-results.json" 2>/dev/null >> "$report_file" || true
    fi

    cat >> "$report_file" << EOF

## Methodology

### Tools Used
- subfinder (passive subdomain enumeration)
- theHarvester (OSINT collection)
- masscan (fast port scanning)
- nmap (detailed port scanning)
- whatweb (web fingerprinting)
- nuclei (vulnerability scanning)

### Commands Executed
See evidence/ directory for full command logs.

### Output Structure
- \`passive/\` - Passive recon results
- \`active/\` - Active recon results
- \`web/\` - Web fingerprinting results
- \`vuln/\` - Vulnerability scanning results
- \`evidence/\` - Command logs and raw output
- \`reports/\` - Generated reports

## Evidence

All findings are backed by captured tool output in the \`evidence/\` directory.

EOF

    log_info "Report generated: $report_file"
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--target)
                TARGET="$2"
                shift 2
                ;;
            -s|--scope)
                SCOPE_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -m|--mode)
                MODE="$2"
                shift 2
                ;;
            -r|--rate)
                RATE_LIMIT="$2"
                shift 2
                ;;
            -T|--timing)
                TIMING="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$TARGET" ]] || [[ -z "$SCOPE_FILE" ]]; then
        log_error "Target and scope file are required"
        usage
    fi

    # Print banner
    echo "========================================"
    echo "  Recon Pipeline v$VERSION"
    echo "  Target: $TARGET"
    echo "  Mode: $MODE"
    echo "  Rate: $RATE_LIMIT pps"
    echo "  Timing: $TIMING"
    echo "========================================"
    echo ""

    # Validate scope
    validate_scope "$TARGET" "$SCOPE_FILE"

    # Check dependencies
    check_dependencies

    # Setup output directory
    setup_output "$OUTPUT_DIR"

    # Run pipeline based on mode
    case "$MODE" in
        web2)
            run_passive_recon "$TARGET" "$OUTPUT_DIR"
            run_active_recon "$TARGET" "$OUTPUT_DIR" "$RATE_LIMIT" "$TIMING"
            run_web_fingerprinting "$TARGET" "$OUTPUT_DIR"
            run_vuln_scanning "$TARGET" "$OUTPUT_DIR"
            ;;
        web3)
            run_web3_recon "$TARGET" "$OUTPUT_DIR"
            ;;
        mixed)
            run_passive_recon "$TARGET" "$OUTPUT_DIR"
            run_active_recon "$TARGET" "$OUTPUT_DIR" "$RATE_LIMIT" "$TIMING"
            run_web_fingerprinting "$TARGET" "$OUTPUT_DIR"
            run_vuln_scanning "$TARGET" "$OUTPUT_DIR"
            run_web3_recon "$TARGET" "$OUTPUT_DIR"
            ;;
        *)
            log_error "Invalid mode: $MODE"
            exit 1
            ;;
    esac

    # Filter false positives
    filter_false_positives "$OUTPUT_DIR"

    # Generate report
    generate_report "$TARGET" "$OUTPUT_DIR" "$MODE"

    echo ""
    log_info "=== Reconnaissance Complete ==="
    log_info "Results: $OUTPUT_DIR"
    log_info "Report: $OUTPUT_DIR/reports/recon-report.md"
}

main "$@"
