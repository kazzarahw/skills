# Verification Checklist

Detailed verification criteria by finding type.

## Vulnerability Reproduction Checklist

### Pre-Conditions

- [ ] Target is reachable and in expected state
- [ ] Prerequisites are met (auth, configuration, data)
- [ ] Environment matches the reported conditions

### Execution

- [ ] Exact command or action is recorded
- [ ] Command is run against the correct target
- [ ] No unintended side effects on non-target systems
- [ ] Exit code is captured
- [ ] Full stdout and stderr are captured

### Result Validation

- [ ] Output matches the vulnerability description
- [ ] Side-effect assertions confirm the claimed state change
- [ ] Result is consistent across N runs (minimum 3)
- [ ] No environmental factors explain the result

### Post-Conditions

- [ ] Target state is as expected after the action
- [ ] No collateral damage to non-target systems
- [ ] Evidence is preserved (logs, files, screenshots)

## Exploit Verification Checklist

### Pre-Conditions

- [ ] Exploit is tested in a controlled environment
- [ ] Target version matches the vulnerable version
- [ ] Exploit does not depend on undefined behavior

### Execution

- [ ] Exploit command is recorded exactly
- [ ] Exploit is run against the correct target
- [ ] Network callbacks (if any) are captured
- [ ] File system changes are captured
- [ ] Process behavior is captured

### Result Validation

- [ ] Exploit achieves the claimed effect (RCE, data exfil, auth bypass)
- [ ] Effect is observable and measurable
- [ ] Effect is consistent across N runs
- [ ] Effect does not occur on the patched version (if available)

### Post-Conditions

- [ ] Exploit artifacts are preserved
- [ ] Target state is documented
- [ ] Cleanup is performed (if applicable)

## Report Verification Checklist

### Content

- [ ] Vulnerability description is accurate and specific
- [ ] Affected versions are correctly identified
- [ ] Impact is correctly assessed
- [ ] Remediation is technically sound

### Evidence

- [ ] All claims are backed by evidence
- [ ] Evidence is raw output, not summaries
- [ ] Commands are reproducible
- [ ] Timestamps are included
- [ ] Side-effect assertions are included

### Reproducibility

- [ ] Steps are clear and complete
- [ ] Steps produce the same result when followed
- [ ] No hidden assumptions or prerequisites
- [ ] Environment is described accurately

### Adversarial Review

- [ ] Specificity question answered with evidence
- [ ] Targeting question answered with evidence
- [ ] Patch resistance question answered with evidence
- [ ] Description match question answered with evidence
- [ ] Disagreements are documented with evidence

## Finding-Type Specific Criteria

### Remote Code Execution (RCE)

- [ ] Command execution is proven (not just connection)
- [ ] Command output is captured
- [ ] Execution is not dependent on a specific tool or shell
- [ ] Privilege level of execution is documented

### SQL Injection

- [ ] Injection point is identified
- [ ] Data extraction is proven (not just error)
- [ ] Injection works without authentication (if claimed)
- [ ] Database type and version are confirmed

### Cross-Site Scripting (XSS)

- [ ] Script execution is proven in a browser context
- [ ] Execution is not dependent on a specific browser
- [ ] Cookie access or action execution is demonstrated
- [ ] Context (reflected, stored, DOM) is correctly identified

### Authentication Bypass

- [ ] Bypass is proven (access granted without valid credentials)
- [ ] Bypass is not dependent on session state
- [ ] Bypass works consistently
- [ ] Bypass does not require physical access (unless claimed)

### Denial of Service (DoS)

- [ ] Service degradation is measurable
- [ ] Attack is not dependent on bandwidth alone
- [ ] Recovery behavior is documented
- [ ] Scope of impact is correctly assessed

### Information Disclosure

- [ ] Sensitive data is actually exposed
- [ ] Data exposure is not dependent on error messages alone
- [ ] Data is not already publicly available
- [ ] Exposure is consistent across runs
