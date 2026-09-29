---
name: cyber-recon
description: Performs reconnaissance and vulnerability scanning on targets. Use when starting engagements, discovering attack surface, or identifying vulnerabilities. Covers network scanning, service enumeration, OSINT, and web fingerprinting.
---

# Cyber Recon

Reconnaissance and vulnerability scanning skill for authorized security testing.

## Constitutional Rules

1. **Authorization required** — Verify written scope before any active scanning. Refuse out-of-scope targets immediately.
2. **Evidence over assertion** — Every finding traces to captured tool output. No finding without a command log.
3. **Minimal blast radius** — Use rate limiting by default. Aggressive modes require explicit authorization.
4. **Structured output** — All results use the report template. No prose-only findings.
5. **Deterministic defaults** — Use the specified tool and parameters unless scope constraints require deviation. Log all deviations.

## Process

### Phase 1: Passive Reconnaissance

Gather intelligence without touching the target.

```
1.1  OSINT collection        → subdomains, emails, tech stack
1.2  DNS enumeration         → records, zone transfer attempts
1.3  Certificate transparency → crt.sh, certspotter
1.4  Search engine recon      → dorks, exposed documents
```

**Exit criteria:** Subdomain list compiled, tech stack identified, attack surface mapped.

### Phase 2: Active Reconnaissance

Direct interaction with in-scope targets.

```
2.1  Host discovery          → masscan (fast sweep)
2.2  Port scanning           → nmap (detailed enumeration)
2.3  Service enumeration      → nmap -sV -sC on open ports
2.4  Web fingerprinting       → whatweb (level 1 default)
```

**Exit criteria:** All open ports identified, services versioned, web tech fingerprinted.

### Phase 3: Vulnerability Scanning

Automated vulnerability detection.

```
3.1  Template scanning       → nuclei (cves/ + exposure/)
3.2  Web server scanning     → nikto (baseline check)
3.3  Directory enumeration    → gobuster (medium wordlist)
```

**Exit criteria:** All templates executed, results triaged, false positives filtered.

### Phase 4: Reporting

Compile structured findings with evidence.

```
4.1  Aggregate results        → deduplicate, severity-rank
4.2  Evidence attachment     → command + output per finding
4.3  Report generation        → structured markdown output
```

## Tool Selection Defaults

| Task | Default Tool | Command Pattern | Why |
|------|-------------|-----------------|-----|
| Fast port discovery | masscan | `masscan -p1-65535 --rate=1000` | 100x faster than nmap for discovery |
| Detailed enumeration | nmap | `nmap -sV -sC -p<ports>` | Accurate service/version detection |
| Web fingerprinting | whatweb | `whatweb -a 1 <url>` | Level 1 avoids WAF triggers |
| Vulnerability scanning | nuclei | `nuclei -t cves/ -t exposure/` | Community-maintained templates |
| Directory enumeration | gobuster | `gobuster dir -w directory-list-2.3-medium.txt` | Balanced coverage vs. noise |
| Subdomain discovery | subfinder | `subfinder -d <domain>` | Passive sources, no direct contact |
| HTTP probing | httpx | `httpx -silent -status-code -title` | Fast validation of live hosts |

**Deviation rule:** If a default tool is unavailable or blocked, substitute the next tool in the chain and log the substitution.

## Budget Caps

Prevent runaway resource consumption.

| Phase | Max Iterations | Max Commands/Target | Time Limit |
|-------|---------------|---------------------|------------|
| Passive recon | 3 | 15 | 30 min |
| Active recon | 2 | 10 | 45 min |
| Vuln scanning | 2 | 8 | 60 min |
| Reporting | 1 | 5 | 15 min |

**Token budget awareness:** If approaching context limits, prioritize:
1. High-severity findings with evidence
2. Attack surface summary
3. Remaining findings as file references

## Scope Containment

### Pre-Scan Checklist

```
[ ] Target list explicitly defined (IPs, domains, ranges)
[ ] Excluded targets documented
[ ] Authorization verified (written scope document)
[ ] Rate limits confirmed with target owner
[ ] Emergency contact identified
```

### Scope Decision Log

Every scan decision records:
- Target identifier
- In-scope / out-of-scope determination
- Rationale
- Timestamp

### Refusal Triggers

Refuse immediately if:
- Target not in written scope
- Target belongs to third party (cloud provider, CDN)
- Rate limit would be exceeded
- Target is critical infrastructure without explicit approval

## Evidence Capture

Every finding requires:

```yaml
finding:
  id: RECON-001
  title: "Apache 2.4.49 Path Traversal"
  severity: high
  host: target.example.com
  port: 443/tcp
  service: http
  evidence:
    tool: nmap
    command: "nmap -sV -p443 target.example.com"
    output: "443/tcp open  http Apache httpd 2.4.49"
    timestamp: "2026-01-15T14:32:00Z"
  verification:
    method: "nuclei -t cves/2021/CVE-2021-41773.yaml"
    confirmed: true
```

**No finding without complete evidence block.**

## Gotchas

### Hallucinated Vulnerabilities
LLM-generated vuln reports have ~30% false positive rate. Every finding MUST be verified by a second tool or manual confirmation before reporting.

### Scope Creep
53% of organizations report agents exceeding authorized permissions. Stick to the defined target list. If new targets are discovered, pause and request authorization.

### Tool Version Sensitivity
Results vary significantly between versions. Record tool versions in every scan:
```bash
nmap --version | head -1
nuclei -version
whatweb --version
```

### WAF/Bot Detection
Aggressive scanning triggers WAF blocks. If fingerprinting returns empty or generic results:
1. Reduce aggression level
2. Add delays between requests
3. Rotate user agents
4. Document the block as a finding

### masscan False Positives
masscan can report false open ports. Always verify masscan results with nmap before reporting.

### Nikto Noise
Nikto produces many informational findings. Treat as a starting point, not definitive. Filter to medium+ severity for reporting.

## Output Format

```markdown
# Reconnaissance Report: [Target]

**Date:** YYYY-MM-DD
**Scope:** [target list]
**Tools:** [tool + versions]

## Executive Summary
- Hosts discovered: N
- Open ports: N
- Services identified: N
- High findings: N
- Medium findings: N
- Low findings: N

## Attack Surface
| Host | Open Ports | Services | Tech Stack |
|------|-----------|----------|------------|
| ... | ... | ... | ... |

## Findings

### [SEVERITY] Finding Title
- **Host:** target:port
- **Evidence:** `command` → output snippet
- **Verification:** secondary confirmation
- **Recommendation:** remediation step

## Methodology
- Commands executed (full list)
- Tools and versions
- Time window

## Appendix
- Raw tool outputs
- Scope decision log
```

## Scripts

- `scripts/recon-pipeline.sh` — Automated recon pipeline (passive → active → vuln → compile)
- `scripts/false-positive-filter.py` — Filter common false positives from scan results

## Reference Files

- **Tool commands:** `references/tool-cheatsheet.md`
- **WSTG test catalog:** `references/wstg-checklist.md`
- **Output schema:** `references/output-schema.json`
- **Port/service reference:** `references/ports-services.md`
- **Rate limiting:** `references/rate-limits.md`
