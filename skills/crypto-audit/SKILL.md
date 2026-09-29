---
name: crypto-audit
description: Performs smart contract security audits. Use when reviewing Solidity, Rust (Solana), Move, or Vyper code for vulnerabilities. Covers static analysis, dynamic analysis, fuzzing, and formal verification.
---

# Crypto Audit

Smart contract security auditing skill. Reviews Solidity, Rust (Solana), Move, Vyper, and Cairo code for vulnerabilities using static analysis, dynamic analysis, fuzzing, and formal verification.

## Constitutional Rules

1. **Never skip manual review.** Static analysis tools catch ~30% of vulnerabilities. Manual line-by-line review is mandatory for every audit.
2. **Always verify exploitability.** A finding is only valid if you can demonstrate a concrete exploit path. Theoretical vulnerabilities are marked as informational.
3. **Trust boundaries define scope.** Every external call, oracle, and user input is a trust boundary. Map them before analyzing.
4. **Severity follows impact × likelihood.** Use Immunefi severity scale (Critical/High/Medium/Low/Informational). Never inflate severity.
5. **Report every finding.** Even if a vulnerability is mitigated, document it. Silence is worse than a false positive.
6. **Reproduce before reporting.** Every finding must include a proof-of-concept or test case that triggers the vulnerability.
7. **Stay within declared scope.** Do not audit contracts outside the agreed scope without explicit approval.

## Audit Process

### Phase 1: Understand

- Read all in-scope contracts and their dependencies
- Map architecture: contracts, actors, trust boundaries, asset flows
- Identify external integrations (oracles, bridges, DEXs)
- Document invariants: what must always be true
- Review documentation and specs for intended behavior

### Phase 2: Static Analysis

Run automated tools to identify known vulnerability patterns.

```bash
# Slither — comprehensive static analysis
slither . --json results.json

# Aderyn — Rust-based analyzer for Solidity
aderyn . --json output.json

# Mythril — symbolic execution
myth analyze contract.sol

# Solhint — linting and style
solhint "contracts/**/*.sol"
```

See `scripts/static-analysis-runner.sh` for automated execution.

### Phase 3: Dynamic Analysis

Execute tests and fuzzing to validate behavior under adversarial conditions.

```bash
# Foundry fuzzing
forge test --fuzz-runs 10000

# Echidna — property-based fuzzing
echidna contract.sol --contract TestContract

# Medusa — fuzzing with coverage guidance
medusa fuzz --contract TestContract
```

See `scripts/fuzz-test-generator.py` for test generation.

### Phase 4: Formal Verification

Prove critical invariants hold for all possible inputs.

```bash
# Certora — formal verification
certoraRun contracts/MyContract.sol:MyContract --verify MyContract:specs/MySpec.spec

# Halmos — symbolic testing
halmos --contract MyContract
```

### Phase 5: Manual Review

Line-by-line review focusing on:
- Access control and authorization logic
- Reentrancy and external call safety
- Integer arithmetic and precision
- Oracle manipulation vectors
- Front-running and MEV exposure
- Upgradeability and proxy patterns
- Gas-related denial of service
- Business logic errors

### Phase 6: Report Writing

Produce structured audit report (see Output Format below).

## Tool Selection Defaults

| Task | Tool | Command |
|------|------|---------|
| Static analysis (Solidity) | Slither | `slither . --json results.json` |
| Static analysis (Rust-based) | Aderyn | `aderyn . --json output.json` |
| Symbolic execution | Mythril | `myth analyze contract.sol` |
| Linting | Solhint | `solhint "contracts/**/*.sol"` |
| Unit/fuzz testing | Foundry | `forge test --fuzz-runs 10000` |
| Property fuzzing | Echidna | `echidna contract.sol --contract TestContract` |
| Coverage-guided fuzzing | Medusa | `medusa fuzz --contract TestContract` |
| Formal verification | Certora | `certoraRun contracts/MyContract.sol:MyContract --verify MyContract:specs/MySpec.spec` |
| Symbolic testing | Halmos | `halmos --contract MyContract` |

## Vulnerability Categories

Map all findings to the Smart Contract Weakness Classification (SWC) registry.

| Category | SWC IDs | Description |
|----------|---------|-------------|
| Reentrancy | SWC-107 | External call before state update enables recursive exploitation |
| Integer overflow/underflow | SWC-101 | Arithmetic operations exceed type bounds |
| Access control | SWC-105, SWC-106, SWC-115 | Missing or flawed authorization checks |
| Oracle manipulation | SWC-116, SWC-120 | Price feed manipulation, stale data |
| Front-running/MEV | SWC-114 | Transaction ordering exploitation |
| Logic errors | SWC-110, SWC-136 | Flawed business logic, incorrect assumptions |
| Gas-related DoS | SWC-128, SWC-133 | Unbounded loops, gas griefing |
| Delegatecall injection | SWC-112 | Unsafe delegatecall to untrusted contracts |
| Storage collision | SWC-134 | Proxy storage layout mismatches |
| Signature replay | SWC-121 | Reuse of signed messages across contexts |

Full catalog with CWE mappings, attack vectors, and prevention patterns: `references/vulnerability-catalog.md`

## Cross-References

| Skill | When to Use |
|-------|-------------|
| **cyber-verify** | Verification discipline and proof techniques |
| **cyber-report** | Report generation and formatting standards |
| **cyber-wiki** | Knowledge management and finding documentation |
| **cyber-coach** | Course correction and audit quality review |
| **crypto-recon** | Blockchain reconnaissance for target identification |
| **crypto-defi** | DeFi protocol analysis for protocol-specific risks |
| **crypto-exploit** | Exploit development for confirmed vulnerabilities |
| **crypto-forensics** | Post-incident investigation and evidence handling |

**Workflow:** `crypto-recon` → `crypto-audit` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

- **SWC registry is incomplete and not actively maintained since 2020.** Use SCSVS (Smart Contract Security Verification Standard) for current guidance, but SWC IDs remain useful for classification.
- **Solidity 0.8+ auto-checks overflow** but `unchecked` blocks are still vulnerable. Always audit `unchecked` blocks explicitly.
- **Transient storage (EIP-1153) is often overlooked.** `tload`/`tstore` bypass normal storage analysis. Check for transient storage misuse.
- **Proxy storage collisions are subtle.** Storage layout mismatches between implementation and proxy corrupt state. Verify layout compatibility.
- **Signature replay spans contracts and chains.** A signature valid on one contract or chain may be replayed on another. Always include domain separators.
- **Business logic vulnerabilities are the most common finding.** Tools miss these. Manual review of economic incentives and edge cases is essential.
- **Static analysis misses economic attacks.** Flash loan attacks, sandwich attacks, and governance manipulation require manual economic analysis.
- **Compiler bugs are real.** Pin compiler versions. Verify bytecode matches source.
- **Test coverage ≠ security.** High coverage can coexist with critical vulnerabilities. Focus on invariant testing.

## Output Format

Every audit produces a structured report:

```markdown
# Smart Contract Security Audit Report

## Executive Summary
- Scope: [contracts audited]
- Duration: [time period]
- Findings: [Critical: N, High: N, Medium: N, Low: N, Informational: N]
- Overall Risk: [Low/Medium/High/Critical]

## Methodology
- Tools used
- Manual review approach
- Fuzzing parameters

## Findings

### [SEVERITY] Finding Title
- **SWC:** [SWC-XXX]
- **CWE:** [CWE-XXX]
- **Location:** [file:line]
- **Description:** [what is wrong]
- **Impact:** [what an attacker can achieve]
- **Proof of Concept:** [code or test demonstrating the issue]
- **Recommendation:** [how to fix]
- **Status:** [Open/Fixed/Acknowledged/Won't Fix]

## Appendix
- Tool outputs
- Test results
- Formal verification reports
```

## Quick Start

1. Run static analysis: `bash scripts/static-analysis-runner.sh /path/to/project`
2. Generate fuzz tests: `python3 scripts/fuzz-test-generator.py --contract MyContract --output tests/`
3. Review `references/vulnerability-catalog.md` for known patterns
4. Follow `references/audit-methodology.md` for detailed process
5. Write report using Output Format above
