# Audit Methodology

Complete methodology for conducting smart contract security audits.

## 10-Phase Audit Process

### Phase 1: Scoping and Planning

**Objective:** Define audit boundaries, deliverables, and timeline.

**Activities:**
- Identify in-scope contracts and dependencies
- Determine audit type (full, focused, follow-up)
- Establish communication channels and escalation paths
- Define severity classification framework
- Set deliverable format and timeline

**Deliverables:**
- Audit scope document
- Timeline with milestones
- Communication plan

### Phase 2: Architecture Review

**Objective:** Understand system design, trust boundaries, and asset flows.

**Activities:**
- Map contract interactions and dependencies
- Identify all external calls and oracles
- Document actor roles and permissions
- Trace asset flows (ETH, ERC-20, ERC-721, etc.)
- Identify upgradeability mechanisms
- Document invariants and expected behaviors

**Key Questions:**
- Who can call each function?
- What are the trust assumptions?
- Where does value enter and exit the system?
- What must always be true (invariants)?

**Deliverables:**
- Architecture diagram
- Trust boundary map
- Asset flow documentation
- Invariant list

### Phase 3: Configuration Review

**Objective:** Identify misconfigurations and deployment issues.

**Activities:**
- Verify compiler version and optimization settings
- Check for floating pragmas
- Review access control initialization
- Verify oracle configurations
- Check for hardcoded addresses
- Review gas limit configurations

**Common Issues:**
- Floating pragma (`pragma solidity ^0.8.0`) — pin to exact version
- Missing access control on initialization functions
- Hardcoded oracle addresses without fallback
- Incorrect inheritance order

### Phase 4: Static Analysis

**Objective:** Automated detection of known vulnerability patterns.

**Tools:**
- Slither: `slither . --json results.json`
- Aderyn: `aderyn . --json output.json`
- Mythril: `myth analyze contract.sol`
- Solhint: `solhint "contracts/**/*.sol"`

**Process:**
1. Run all applicable static analysis tools
2. Deduplicate findings across tools
3. Classify findings by severity
4. Filter false positives through manual review
5. Document all confirmed findings

**Output:** Deduplicated findings list with severity classification

### Phase 5: Dynamic Analysis

**Objective:** Validate behavior under adversarial conditions.

**Activities:**
- Review existing test coverage
- Execute test suite
- Run fuzzing campaigns
- Perform invariant testing
- Test edge cases and boundary conditions

**Tools:**
- Foundry: `forge test --fuzz-runs 10000`
- Echidna: `echidna-test contract.sol --contract TestContract`
- Medusa: `medusa fuzz --contract TestContract`

**Process:**
1. Establish baseline test coverage
2. Generate additional fuzz tests
3. Run fuzzing campaigns (minimum 10,000 runs)
4. Analyze coverage gaps
5. Test identified edge cases

### Phase 6: Manual Code Review

**Objective:** Identify vulnerabilities that automated tools miss.

**Review Areas:**

#### Access Control
- [ ] All external functions have access control
- [ ] Admin functions are properly restricted
- [ ] Role-based access is correctly implemented
- [ ] No tx.origin usage for authorization
- [ ] Multi-sig requirements for critical operations

#### Reentrancy
- [ ] State updates before external calls (CEI pattern)
- [ ] Reentrancy guards on all external-calling functions
- [ ] No cross-function reentrancy vectors
- [ ] Read-only reentrancy considered

#### Arithmetic
- [ ] Solidity 0.8+ or SafeMath for older versions
- [ ] No unchecked blocks without justification
- [ ] Division precision handled correctly
- [ ] Rounding direction favors protocol

#### Oracle Security
- [ ] Price feeds have staleness checks
- [ ] TWAP or other manipulation-resistant oracles
- [ ] Fallback mechanisms for oracle failures
- [ ] No single-block oracle manipulation

#### Upgradeability
- [ ] Storage layout compatibility verified
- [ ] Initialization functions protected
- [ ] Upgrade timelocks implemented
- [ ] No storage collisions

#### Logic Errors
- [ ] Business logic matches specification
- [ ] Edge cases handled (zero, max, overflow)
- [ ] State machine transitions are valid
- [ ] No off-by-one errors

### Phase 7: Economic Analysis

**Objective:** Identify economic attack vectors.

**Activities:**
- Analyze flash loan attack surfaces
- Evaluate sandwich/front-running exposure
- Assess governance attack vectors
- Review incentive mechanisms for manipulation
- Analyze liquidation mechanisms

**Common Economic Attacks:**
- Flash loan price manipulation
- Sandwich attacks on DEX integrations
- Governance token accumulation attacks
- Liquidation front-running
- Incentive gaming

### Phase 8: Formal Verification

**Objective:** Prove critical invariants hold for all inputs.

**Activities:**
- Identify critical invariants to prove
- Write formal verification specifications
- Run Certora or Halmos
- Analyze counterexamples
- Document proof results

**Tools:**
- Certora: `certoraRun contracts/MyContract.sol --verify MyContract:specs/MySpec.spec`
- Halmos: `halmos --contract MyContract`

### Phase 9: Reporting

**Objective:** Document findings clearly and actionably.

**Report Structure:**
1. Executive Summary
2. Scope and Methodology
3. Findings (by severity)
4. Detailed Analysis
5. Recommendations
6. Appendix (tool outputs, test results)

**Finding Format:**
- Title and severity
- SWC/CWE classification
- Location (file:line)
- Description
- Impact
- Proof of Concept
- Recommendation
- Status

### Phase 10: Remediation Verification

**Objective:** Verify all findings are properly addressed.

**Activities:**
- Review all code changes
- Re-run static analysis on fixed code
- Execute regression tests
- Verify fixes don't introduce new issues
- Update report with remediation status

## Threat Modeling: STRIDE for Smart Contracts

| Threat Category | Smart Contract Manifestation |
|-----------------|------------------------------|
| **Spoofing** | Fake tokens, signature replay, tx.origin auth |
| **Tampering** | Storage corruption, delegatecall injection, storage collisions |
| **Repudiation** | Missing events, incomplete logging |
| **Information Disclosure** | Unencrypted on-chain data, front-running visibility |
| **Denial of Service** | Gas griefing, unbounded loops, block gas limit |
| **Elevation of Privilege** | Access control flaws, initialization flaws, proxy issues |

## Risk Assessment Frameworks

### SCSVS (Smart Contract Security Verification Standard)

| Level | Description | Requirements |
|-------|-------------|--------------|
| Level 0 | No security | No security measures |
| Level 1 | Basic security | Static analysis, basic tests |
| Level 2 | Standard security | + Manual review, fuzzing |
| Level 3 | Enhanced security | + Formal verification, economic analysis |
| Level 4 | Maximum security | + Multiple audits, bug bounty |

### Immunefi Severity Scale

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Direct loss of funds, permanent corruption | Reentrancy draining all funds |
| High | Loss of funds with conditions, temporary corruption | Oracle manipulation for profit |
| Medium | State corruption without direct fund loss | Access control bypass |
| Low | Minor issues, best practice violations | Missing events |
| Informational | Code quality, optimization suggestions | Gas optimization |

## Review Checklists

### Access Control Checklist
- [ ] All external functions have access control modifiers
- [ ] Admin functions use onlyOwner or role-based access
- [ ] No tx.origin for authorization
- [ ] Critical operations require multi-sig
- [ ] Access control is not bypassable through delegatecall
- [ ] Initialization functions are protected
- [ ] No default admin privileges

### Reentrancy Checklist
- [ ] CEI pattern followed (Checks-Effects-Interactions)
- [ ] Reentrancy guards on all functions making external calls
- [ ] No cross-function reentrancy vectors
- [ ] Read-only reentrancy considered (view functions)
- [ ] No reentrancy through callbacks (ERC-777, ERC-1155)
- [ ] State changes before token transfers

### Oracle Checklist
- [ ] Price feeds have staleness checks (heartbeat)
- [ ] TWAP or manipulation-resistant oracle used
- [ ] Fallback oracle or circuit breaker
- [ ] No single-block price manipulation possible
- [ ] Oracle addresses are configurable
- [ ] Oracle deviation checks implemented

### Upgradeability Checklist
- [ ] Storage layout verified between versions
- [ ] Initialization functions protected (initializer modifier)
- [ ] Upgrade timelock implemented
- [ ] No storage collisions between proxy and implementation
- [ ] Upgrade events emitted
- [ ] Emergency pause mechanism exists

## Report Standards

### Finding Severity Classification

**Critical:**
- Direct loss of funds without conditions
- Permanent state corruption
- Complete system compromise

**High:**
- Loss of funds with specific conditions
- Temporary state corruption
- Significant privilege escalation

**Medium:**
- State corruption without direct fund loss
- Access control bypass with limited impact
- Oracle manipulation with limited profit

**Low:**
- Minor issues with minimal impact
- Best practice violations
- Code quality issues

**Informational:**
- Optimization suggestions
- Style improvements
- Documentation gaps

### Finding Status

- **Open:** Finding not yet addressed
- **Fixed:** Finding has been resolved
- **Acknowledged:** Finding accepted but not fixed (risk accepted)
- **Won't Fix:** Finding dismissed with justification

## Bug Bounty Platform Comparison

| Platform | Focus | Payout Range | Competition | Best For |
|----------|-------|--------------|-------------|----------|
| **Immunefi** | Web3 native | $10K - $10M+ | Medium | Large protocols, serious bugs |
| **Code4rena** | Competitive | $10K - $500K | High | Community audits, learning |
| **Sherlock** | Underwriting | $5K - $250K | Medium | DeFi protocols, insurance-backed |
| **Hats Finance** | Flexible | $1K - $500K | Low-Medium | Smaller projects, continuous bounties |

### Platform Selection Guide

- **Immunefi:** Best for established protocols with significant TVL
- **Code4rena:** Best for competitive audits and learning
- **Sherlock:** Best for DeFi protocols wanting insurance-backed audits
- **Hats Finance:** Best for continuous bug bounty programs
