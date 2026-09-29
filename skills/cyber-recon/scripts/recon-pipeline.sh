#!/usr/bin/env bash
#
# recon-pipeline.sh - Automated Reconnaissance Pipeline
#
# Executes the full recon pipeline (passive → active → vuln scan) in one invocation.
# Designed for authorized penetration testing engagements only.
#
# Usage:
#   ./recon-pipeline.sh --target example.com --scope scope.txt --output results/ [OPTIONS]
#
# Options:
#   --target <domain>       Target domain or IP range (required)
#   --scope <file>          File containing in-scope targets (one per line)
#   --output <dir>          Output directory for results (default: ./recon-results)
#   --rate <int>            Rate limit for active scans in pps (default: 1000)
#   --wordlist <file>       Wordlist for subdomain brute forcing
#   --phases <list>         Comma-separated phases to run (default: all)
#   --timeout <int>         Global timeout in seconds (default: 3600)
#   --verbose               Enable verbose output
#   --dry-run               Show commands without executing
#   --help                  Show this help message
#
# Phases:
#   passive     Passive reconnaissance (subfinder, crt.sh)
#   active      Active reconnaissance (masscan → nmap)
#   vuln        Vulnerability scanning (nuclei, nikto)
#   compile     Compile and structure results
#
# Exit Codes:
#   0   Success
#   1   General error
#   2   Invalid arguments
#   3   Out-of-scope target detected
#   4   Required tool not found
#   5   Timeout exceeded
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly VERSION="1.0.0"
readonly DEFAULT_RATE=1000
readonly DEFAULT_TIMEOUT=3600
readonly DEFAULT_WORDLIST="/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Global variables
TARGET=""
SCOPE_FILE=""
OUTPUT_DIR="./recon-results"
RATE="$DEFAULT_RATE"
WORDLIST="$DEFAULT_WORDLIST"
PHASES="passive,active,vuln,compile"
TIMEOUT="$DEFAULT_TIMEOUT"
VERBOSE=false
DRY_RUN=false
START_TIME=""
LOG_FILE=""
RESULTS_JSON=""

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    case "$level" in
        INFO)    echo -e "${GREEN}[${timestamp}] [INFO]${NC} $message" ;;
        WARN)    echo -e "${YELLOW}[${timestamp}] [WARN]${NC} $message" ;;
        ERROR)   echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" ;;
        DEBUG)   [[ "$VERBOSE" == true ]] && echo -e "${CYAN}[${timestamp}] [DEBUG]${NC} $message" ;;
        PHASE)   echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
                 echo -e "${BLUE}  PHASE: $message${NC}"
                 echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}" ;;
    esac
    
    if [[ -n "$LOG_FILE" ]]; then
        echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE"
    fi
}

die() {
    local exit_code="$1"
    shift
    log ERROR "$*"
    exit "$exit_code"
}

cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log WARN "Pipeline terminated with exit code $exit_code"
        log WARN "Partial results may be available in: $OUTPUT_DIR"
    fi
    # Kill any background jobs
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT INT TERM

usage() {
    cat <<EOF
${SCRIPT_NAME} v${VERSION} - Automated Reconnaissance Pipeline

Usage:
    ${SCRIPT_NAME} --target <domain> --scope <file> [OPTIONS]

Required Arguments:
    --target <domain>       Target domain or IP range
    --scope <file>          File containing in-scope targets (one per line)

Optional Arguments:
    --output <dir>          Output directory (default: ./recon-results)
    --rate <int>            Rate limit in packets/sec (default: ${DEFAULT_RATE})
    --wordlist <file>       Wordlist for subdomain enumeration
    --phases <list>         Comma-separated phases: passive,active,vuln,compile
    --timeout <int>         Global timeout in seconds (default: ${DEFAULT_TIMEOUT})
    --verbose               Enable verbose output
    --dry-run               Show commands without executing
    --help                  Show this help message

Examples:
    # Full pipeline
    ${SCRIPT_NAME} --target example.com --scope scope.txt --output results/

    # Passive only
    ${SCRIPT_NAME} --target example.com --scope scope.txt --phases passive

    # Active scan with custom rate
    ${SCRIPT_NAME} --target 192.168.1.0/24 --scope scope.txt --rate 500 --phases active

    # Dry run to preview commands
    ${SCRIPT_NAME} --target example.com --scope scope.txt --dry-run --verbose

EOF
    exit 0
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --target)
                TARGET="${2:?--target requires a value}"
                shift 2
                ;;
            --scope)
                SCOPE_FILE="${2:?--scope requires a value}"
                shift 2
                ;;
            --output)
                OUTPUT_DIR="${2:?--output requires a value}"
                shift 2
                ;;
            --rate)
                RATE="${2:?--rate requires a value}"
                if ! [[ "$RATE" =~ ^[0-9]+$ ]]; then
                    die 2 "Rate must be a positive integer"
                fi
                shift 2
                ;;
            --wordlist)
                WORDLIST="${2:?--wordlist requires a value}"
                shift 2
                ;;
            --phases)
                PHASES="${2:?--phases requires a value}"
                shift 2
                ;;
            --timeout)
                TIMEOUT="${2:?--timeout requires a value}"
                if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
                    die 2 "Timeout must be a positive integer"
                fi
                shift 2
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --dry-run|-n)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                usage
                ;;
            *)
                die 2 "Unknown option: $1"
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$TARGET" ]]; then
        die 2 "Missing required argument: --target"
    fi

    if [[ -z "$SCOPE_FILE" ]]; then
        die 2 "Missing required argument: --scope"
    fi

    if [[ ! -f "$SCOPE_FILE" ]]; then
        die 2 "Scope file not found: $SCOPE_FILE"
    fi

    # Validate phases
    local valid_phases="passive active vuln compile"
    IFS=',' read -ra phase_array <<< "$PHASES"
    for phase in "${phase_array[@]}"; do
        phase="$(echo "$phase" | tr -d '[:space:]')"
        if [[ ! " $valid_phases " =~ " $phase " ]]; then
            die 2 "Invalid phase: $phase. Valid phases: $valid_phases"
        fi
    done
}

# ============================================================================
# SCOPE VALIDATION
# ============================================================================

validate_scope() {
    log INFO "Validating target against scope..."
    
    local in_scope=false
    local target_normalized
    target_normalized="$(echo "$TARGET" | tr '[:upper:]' '[:lower:]')"
    
    while IFS= read -r scope_line || [[ -n "$scope_line" ]]; do
        # Skip comments and empty lines
        [[ "$scope_line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${scope_line// }" ]] && continue
        
        local scope_normalized
        scope_normalized="$(echo "$scope_line" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
        
        # Exact match
        if [[ "$target_normalized" == "$scope_normalized" ]]; then
            in_scope=true
            break
        fi
        
        # Subdomain match (target ends with .scope)
        if [[ "$target_normalized" == *."$scope_normalized" ]]; then
            in_scope=true
            break
        fi
        
        # CIDR match for IP targets
        if [[ "$scope_normalized" == */* ]] && [[ "$target_normalized" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            if ip_in_cidr "$target_normalized" "$scope_normalized"; then
                in_scope=true
                break
            fi
        fi
    done < "$SCOPE_FILE"
    
    if [[ "$in_scope" != true ]]; then
        die 3 "Target '$TARGET' is NOT in scope. Refusing to proceed."
    fi
    
    log INFO "Target '$TARGET' verified as in-scope"
}

ip_in_cidr() {
    local ip="$1"
    local cidr="$2"
    
    # Use python3 for CIDR matching (more reliable than pure bash)
    python3 -c "
import ipaddress
import sys
try:
    net = ipaddress.ip_network('$cidr', strict=False)
    addr = ipaddress.ip_address('$ip')
    sys.exit(0 if addr in net else 1)
except ValueError:
    sys.exit(1)
" 2>/dev/null
}

# ============================================================================
# TOOL CHECKS
# ============================================================================

check_tools() {
    local missing=()
    
    # Phase-specific tool requirements
    IFS=',' read -ra phase_array <<< "$PHASES"
    for phase in "${phase_array[@]}"; do
        phase="$(echo "$phase" | tr -d '[:space:]')"
        case "$phase" in
            passive)
                command -v subfinder &>/dev/null || missing+=("subfinder")
                command -v curl &>/dev/null || missing+=("curl")
                ;;
            active)
                command -v masscan &>/dev/null || missing+=("masscan")
                command -v nmap &>/dev/null || missing+=("nmap")
                ;;
            vuln)
                command -v nuclei &>/dev/null || missing+=("nuclei")
                command -v nikto &>/dev/null || missing+=("nikto")
                ;;
        esac
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        die 4 "Required tools not found: ${missing[*]}"
    fi
    
    log INFO "All required tools are available"
}

# ============================================================================
# OUTPUT SETUP
# ============================================================================

setup_output() {
    mkdir -p "$OUTPUT_DIR"/{passive,active,vuln,compiled,logs}
    LOG_FILE="$OUTPUT_DIR/logs/pipeline.log"
    RESULTS_JSON="$OUTPUT_DIR/compiled/recon-results.json"
    START_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    log INFO "Output directory: $OUTPUT_DIR"
    log INFO "Log file: $LOG_FILE"
    log INFO "Rate limit: ${RATE} pps"
    log INFO "Timeout: ${TIMEOUT}s"
    log INFO "Phases: $PHASES"
}

# ============================================================================
# COMMAND EXECUTION
# ============================================================================

run_cmd() {
    local description="$1"
    shift
    local cmd="$*"
    
    log DEBUG "Executing: $cmd"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $cmd"
        return 0
    fi
    
    # Execute with timeout
    local exit_code=0
    timeout "$TIMEOUT" bash -c "$cmd" || exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        die 5 "Command timed out after ${TIMEOUT}s: $description"
    elif [[ $exit_code -ne 0 ]]; then
        log WARN "Command exited with code $exit_code: $description"
    fi
    
    return $exit_code
}

# ============================================================================
# PHASE 1: PASSIVE RECONNAISSANCE
# ============================================================================

phase_passive() {
    log PHASE "PASSIVE RECONNAISSANCE"
    
    local passive_dir="$OUTPUT_DIR/passive"
    local subdomain_file="$passive_dir/subdomains.txt"
    
    # Subfinder - subdomain enumeration
    log INFO "Running subfinder for subdomain enumeration..."
    run_cmd "subfinder" \
        "subfinder -d '$TARGET' -silent -all -o '$subdomain_file' 2>>'$LOG_FILE'"
    
    # crt.sh - certificate transparency
    log INFO "Querying crt.sh for certificate transparency data..."
    local crtsh_file="$passive_dir/crtsh-raw.json"
    run_cmd "crt.sh query" \
        "curl -s --max-time 30 'https://crt.sh/?q=${TARGET}&output=json' -o '$crtsh_file' 2>>'$LOG_FILE'"
    
    # Parse crt.sh results
    if [[ -f "$crtsh_file" ]] && [[ "$DRY_RUN" != true ]]; then
        log INFO "Parsing crt.sh results..."
        python3 -c "
import json
import sys

try:
    with open('$crtsh_file') as f:
        data = json.load(f)
    
    domains = set()
    for entry in data:
        name = entry.get('name_value', '')
        for part in name.split('\n'):
            part = part.strip().lstrip('*.')
            if part and '$TARGET' in part:
                domains.add(part)
    
    with open('$passive_dir/crtsh-domains.txt', 'w') as f:
        for d in sorted(domains):
            f.write(d + '\n')
    
    print(f'Found {len(domains)} unique domains from crt.sh')
except Exception as e:
    print(f'Error parsing crt.sh: {e}', file=sys.stderr)
" 2>>"$LOG_FILE"
    fi
    
    # Combine all discovered subdomains
    if [[ "$DRY_RUN" != true ]]; then
        cat "$subdomain_file" "$passive_dir/crtsh-domains.txt" 2>/dev/null | \
            sort -u > "$passive_dir/all-subdomains.txt" || true
        
        local count
        count=$(wc -l < "$passive_dir/all-subdomains.txt" 2>/dev/null || echo "0")
        log INFO "Total unique subdomains discovered: $count"
    fi
}

# ============================================================================
# PHASE 2: ACTIVE RECONNAISSANCE
# ============================================================================

phase_active() {
    log PHASE "ACTIVE RECONNAISSANCE"
    
    local active_dir="$OUTPUT_DIR/active"
    local masscan_output="$active_dir/masscan-results.xml"
    local nmap_output="$active_dir/nmap-results"
    local targets_file="$active_dir/targets.txt"
    
    # Build target list from passive results
    if [[ -f "$OUTPUT_DIR/passive/all-subdomains.txt" ]]; then
        cp "$OUTPUT_DIR/passive/all-subdomains.txt" "$targets_file"
    else
        echo "$TARGET" > "$targets_file"
    fi
    
    # Resolve subdomains to IPs
    log INFO "Resolving targets to IP addresses..."
    local resolved_file="$active_dir/resolved-targets.txt"
    if [[ "$DRY_RUN" != true ]]; then
        while IFS= read -r host; do
            local ip
            ip=$(dig +short "$host" 2>/dev/null | grep -E '^[0-9]+\.' | head -1)
            if [[ -n "$ip" ]]; then
                echo "$ip" >> "$resolved_file"
            fi
        done < "$targets_file"
        sort -u "$resolved_file" -o "$resolved_file" 2>/dev/null || true
    fi
    
    # Masscan - fast port scanning
    log INFO "Running masscan (rate: ${RATE} pps)..."
    run_cmd "masscan" \
        "masscan -iL '$resolved_file' --rate '$RATE' -p 0-65535 \
         --open-only -oJ '$active_dir/masscan-results.json' 2>>'$LOG_FILE'"
    
    # Parse masscan results for nmap targets
    local open_ports_file="$active_dir/open-ports.txt"
    if [[ -f "$active_dir/masscan-results.json" ]] && [[ "$DRY_RUN" != true ]]; then
        log INFO "Parsing masscan results..."
        python3 -c "
import json

ports = set()
try:
    with open('$active_dir/masscan-results.json') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                for p in entry.get('ports', []):
                    ports.add(p['port'])
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    pass

with open('$open_ports_file', 'w') as f:
    f.write(','.join(str(p) for p in sorted(ports)))
print(f'Found {len(ports)} unique open ports')
" 2>>"$LOG_FILE"
    fi
    
    # Nmap - service version detection and OS fingerprinting
    local port_list
    port_list=$(cat "$open_ports_file" 2>/dev/null || echo "80,443,8080,8443")
    
    log INFO "Running nmap service detection on ports: $port_list"
    run_cmd "nmap service scan" \
        "nmap -sV -sC -O --open -p '$port_list' \
         -iL '$resolved_file' \
         -oA '$nmap_output' 2>>'$LOG_FILE'"
    
    log INFO "Active reconnaissance complete"
}

# ============================================================================
# PHASE 3: VULNERABILITY SCANNING
# ============================================================================

phase_vuln() {
    log PHASE "VULNERABILITY SCANNING"
    
    local vuln_dir="$OUTPUT_DIR/vuln"
    local nuclei_output="$vuln_dir/nuclei-results.json"
    local nikto_output="$vuln_dir/nikto-results.txt"
    
    # Build URL list for scanning
    local url_list="$vuln_dir/target-urls.txt"
    if [[ -f "$OUTPUT_DIR/passive/all-subdomains.txt" ]]; then
        if [[ "$DRY_RUN" != true ]]; then
            while IFS= read -r host; do
                echo "https://$host" >> "$url_list"
                echo "http://$host" >> "$url_list"
            done < "$OUTPUT_DIR/passive/all-subdomains.txt"
        fi
    else
        echo "https://$TARGET" > "$url_list"
    fi
    
    # Nuclei - template-based vulnerability scanning
    log INFO "Running nuclei vulnerability scanner..."
    run_cmd "nuclei scan" \
        "nuclei -l '$url_list' \
         -t '\$(nuclei -templates 2>/dev/null || echo /root/nuclei-templates)' \
         -severity low,medium,high,critical \
         -json -o '$nuclei_output' \
         -rate-limit '$RATE' \
         -timeout 10 \
         -retries 2 2>>'$LOG_FILE'"
    
    # Nikto - web server scanning
    log INFO "Running nikto web server scanner..."
    run_cmd "nikto scan" \
        "nikh -h '$url_list' -Format txt -o '$nikto_output' \
         -timeout 10 -maxtime 300 2>>'$LOG_FILE'"
    
    log INFO "Vulnerability scanning complete"
}

# ============================================================================
# PHASE 4: COMPILE RESULTS
# ============================================================================

phase_compile() {
    log PHASE "COMPILING RESULTS"
    
    log INFO "Aggregating results into structured output..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would compile results into: $RESULTS_JSON"
        return 0
    fi
    
    python3 << 'PYTHON_SCRIPT'
import json
import os
import glob
from datetime import datetime, timezone

output_dir = os.environ.get('OUTPUT_DIR', './recon-results')
results_json = os.environ.get('RESULTS_JSON', '')
target = os.environ.get('TARGET', '')
start_time = os.environ.get('START_TIME', '')

if not results_json:
    print("ERROR: RESULTS_JSON not set", file=os.stderr)
    exit(1)

# Initialize results structure
results = {
    "engagement_id": f"RECON-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{hash(target) & 0xFFFFFF:06X}",
    "target": target,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "scope_verified": True,
    "hosts": [],
    "findings": [],
    "methodology": {
        "tools_used": [],
        "commands_executed": [],
        "time_window": {
            "start": start_time,
            "end": datetime.now(timezone.utc).isoformat()
        }
    }
}

# Parse nmap results
nmap_files = glob.glob(os.path.join(output_dir, "active", "nmap-results.*"))
hosts = {}
for nmap_file in nmap_files:
    if nmap_file.endswith('.xml'):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(nmap_file)
            root = tree.getroot()
            for host in root.findall('.//host'):
                addr_elem = host.find('.//address[@addrtype="ipv4"]')
                if addr_elem is None:
                    continue
                ip = addr_elem.get('addr')
                if ip not in hosts:
                    hosts[ip] = {
                        "ip": ip,
                        "hostnames": [],
                        "ports": [],
                        "services": [],
                        "tech_stack": []
                    }
                # Hostnames
                for hostname in host.findall('.//hostname'):
                    hosts[ip]["hostnames"].append(hostname.get('name', ''))
                # Ports and services
                for port in host.findall('.//port'):
                    port_id = port.get('portid')
                    state = port.find('.//state')
                    if state is not None and state.get('state') == 'open':
                        service_elem = port.find('.//service')
                        service_name = service_elem.get('name', 'unknown') if service_elem is not None else 'unknown'
                        service_version = service_elem.get('version', '') if service_elem is not None else ''
                        service_product = service_elem.get('product', '') if service_elem is not None else ''
                        
                        port_info = {
                            "port": int(port_id),
                            "protocol": port.get('protocol', 'tcp'),
                            "service": service_name,
                            "version": service_version,
                            "product": service_product
                        }
                        hosts[ip]["ports"].append(port_info)
                        hosts[ip]["services"].append(service_name)
                        
                        # Tech stack detection
                        if service_product:
                            hosts[ip]["tech_stack"].append(service_product)
        except Exception as e:
            print(f"Warning: Error parsing nmap XML: {e}", file=os.stderr)

results["hosts"] = list(hosts.values())

# Parse nuclei results
nuclei_file = os.path.join(output_dir, "vuln", "nuclei-results.json")
finding_id = 0
if os.path.exists(nuclei_file):
    try:
        with open(nuclei_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    finding_id += 1
                    finding = {
                        "id": f"VULN-{finding_id:04d}",
                        "title": entry.get('info', {}).get('name', 'Unknown'),
                        "severity": entry.get('info', {}).get('severity', 'unknown').lower(),
                        "host": entry.get('host', ''),
                        "port": entry.get('port', ''),
                        "service": entry.get('matched-at', ''),
                        "cve": entry.get('info', {}).get('classification', {}).get('cve-id', ''),
                        "cvss": entry.get('info', {}).get('classification', {}).get('cvss-score', ''),
                        "evidence": entry.get('matched-at', ''),
                        "verification": "pending"
                    }
                    results["findings"].append(finding)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Warning: Error parsing nuclei results: {e}", file=os.stderr)

# Parse nikto results
nikto_file = os.path.join(output_dir, "vuln", "nikto-results.txt")
if os.path.exists(nikto_file):
    try:
        with open(nikto_file) as f:
            content = f.read()
            # Simple parsing - look for vulnerability lines
            for line in content.split('\n'):
                if '+ ' in line and 'OSVDB' in line:
                    finding_id += 1
                    finding = {
                        "id": f"VULN-{finding_id:04d}",
                        "title": line.strip('+ ').strip(),
                        "severity": "low",
                        "host": target,
                        "port": "",
                        "service": "http",
                        "cve": "",
                        "cvss": "",
                        "evidence": line.strip(),
                        "verification": "pending"
                    }
                    results["findings"].append(finding)
    except Exception as e:
        print(f"Warning: Error parsing nikto results: {e}", file=os.stderr)

# Populate methodology
results["methodology"]["tools_used"] = ["subfinder", "crt.sh", "masscan", "nmap", "nuclei", "nikto"]

# Write results
os.makedirs(os.path.dirname(results_json), exist_ok=True)
with open(results_json, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results compiled: {len(results['hosts'])} hosts, {len(results['findings'])} findings")
print(f"Output: {results_json}")
PYTHON_SCRIPT

    log INFO "Results compiled to: $RESULTS_JSON"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           RECON PIPELINE v${VERSION}                          ║"
    echo "║     Automated Reconnaissance Framework                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    parse_args "$@"
    validate_scope
    check_tools
    setup_output
    
    log INFO "Starting recon pipeline for target: $TARGET"
    log INFO "Engagement ID: RECON-$(date +%Y%m%d)-$(echo "$TARGET" | md5sum | head -c 6 | tr '[:lower:]' '[:upper:]')"
    
    # Execute phases
    IFS=',' read -ra phase_array <<< "$PHASES"
    for phase in "${phase_array[@]}"; do
        phase="$(echo "$phase" | tr -d '[:space:]')"
        case "$phase" in
            passive) phase_passive ;;
            active)  phase_active ;;
            vuln)    phase_vuln ;;
            compile) phase_compile ;;
        esac
    done
    
    local end_time
    end_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local duration
    duration=$(($(date +%s) - $(date -d "$START_TIME" +%s 2>/dev/null || echo $(date +%s))))
    
    log PHASE "PIPELINE COMPLETE"
    log INFO "Duration: ${duration}s"
    log INFO "Results: $OUTPUT_DIR"
    log INFO "Structured output: $RESULTS_JSON"
    
    echo -e "\n${GREEN}✓ Reconnaissance pipeline completed successfully${NC}"
    echo -e "${GREEN}  Output directory: $OUTPUT_DIR${NC}"
    echo -e "${GREEN}  Results file: $RESULTS_JSON${NC}"
}

main "$@"
