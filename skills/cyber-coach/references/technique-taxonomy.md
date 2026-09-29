# Technique Taxonomy

This file defines the technique categories the coach uses to classify agent behavior and suggest alternatives.

---

## Category Definitions

### 1. Static Analysis

**Definition:** Examining code, binaries, or configurations without executing them.

**Techniques:**
- Source code review
- Pattern matching (grep, regex)
- Decompilation / disassembly
- Configuration review
- Dependency analysis
- Data flow analysis (manual)

**When appropriate:**
- Source code is available
- Target is a compiled binary
- Looking for logic flaws, backdoors, or insecure patterns
- Initial reconnaissance phase

**Common pitfalls:**
- Reading too much code without forming hypotheses
- Missing the attack surface by auditing irrelevant modules
- Analyzing library code instead of application logic
- Not tracing data flow from input to sink

**Coach suggestions when stuck:**
- "Form a hypothesis about the vulnerability class, then search for it specifically."
- "Trace data flow from the input source to the sensitive sink."
- "Focus on the code paths reachable from the attack surface."

---

### 2. Dynamic Analysis

**Definition:** Observing the target's behavior during execution.

**Techniques:**
- Debugging (gdb, lldb, WinDbg)
- Fuzzing (coverage-guided, grammar-based)
- Runtime instrumentation (frida, strace, ltrace)
- Sandbox execution
- Input mutation and observation

**When appropriate:**
- Target can be executed locally
- Vulnerability is timing-dependent or state-dependent
- Static analysis has identified a suspicious code path
- Need to understand runtime behavior

**Common pitfalls:**
- Fuzzing without coverage feedback
- Testing with inputs that don't reach the target code
- Not isolating the crashing input
- Debugging without breakpoints at key locations

**Coach suggestions when stuck:**
- "Build the target and run it under a debugger with a crafted input."
- "Use coverage-guided fuzzing to reach deeper code paths."
- "Set a breakpoint at the input parser and trace execution."

---

### 3. Network Analysis

**Definition:** Capturing and analyzing network traffic to understand protocols and find weaknesses.

**Techniques:**
- Packet capture (tcpdump, Wireshark)
- Protocol analysis
- Traffic replay
- Man-in-the-middle testing
- Service enumeration

**When appropriate:**
- Target exposes network services
- Protocol implementation may be flawed
- Encryption or authentication is implemented custom
- Need to understand client-server interaction

**Common pitfalls:**
- Capturing traffic without understanding the protocol
- Missing encrypted or binary protocols
- Not replaying modified traffic
- Focusing on well-known protocols instead of custom ones

**Coach suggestions when stuck:**
- "Capture traffic between the client and server, then replay with modifications."
- "Analyze the custom protocol implementation for logic flaws."
- "Test the authentication handshake with edge-case inputs."

---

### 4. Web Analysis

**Definition:** Testing web applications for input validation, authentication, and authorization flaws.

**Techniques:**
- Parameter testing (injection, XSS, SSRF)
- Authentication bypass testing
- Session management testing
- Business logic testing
- API endpoint analysis

**When appropriate:**
- Target is a web application or API
- Input validation is the primary attack surface
- Authentication/authorization logic is custom
- Business logic flaws are suspected

**Common pitfalls:**
- Testing the same parameter with the same payload repeatedly
- Not varying attack vectors (trying only one injection type)
- Missing IDOR by not testing object references
- Overlooking client-side validation bypass

**Coach suggestions when stuck:**
- "Vary your attack vector — if SQLi failed, try command injection or template injection."
- "Test for IDOR by modifying object references in requests."
- "Bypass client-side validation by sending requests directly to the API."

---

### 5. Cryptanalysis

**Definition:** Analyzing cryptographic implementations for weaknesses.

**Techniques:**
- Protocol analysis
- Implementation review (side channels, padding oracles)
- Key management analysis
- Randomness testing
- Algorithm misuse detection

**When appropriate:**
- Target uses custom cryptography
- Standard algorithms may be misused
- Key management is suspect
- Protocol has known cryptographic patterns

**Common pitfalls:**
- Assuming the algorithm is broken when the implementation is the issue
- Not checking for algorithm misuse (ECB mode, IV reuse)
- Missing side-channel leaks in error messages
- Overlooking key derivation weaknesses

**Coach suggestions when stuck:**
- "Check for algorithm misuse — ECB mode, static IVs, or missing authentication."
- "Analyze error messages for padding oracle or timing side channels."
- "Review the key derivation and storage implementation."

---

### 6. Social Engineering

**Definition:** Manipulating people to gain access or information.

**Techniques:**
- Phishing simulation
- Pretexting
- Baiting
- Tailgating (physical)
- Vishing (voice phishing)

**When appropriate:**
- Engagement explicitly includes social engineering
- Technical attack surface is hardened
- Human element is the weakest link
- Physical access is in scope

**Common pitfalls:**
- Not following the engagement rules of engagement
- Targeting individuals not in scope
- Missing the objective (gathering info vs. gaining access)
- Not documenting the social engineering attack path

**Coach suggestions when stuck:**
- "Refine your pretext to match the target's role and context."
- "Use information gathered from OSINT to make your approach more credible."
- "If phishing failed, try a different vector — phone or in-person."

---

## Technique Classification Table

Use this table to classify tool calls into technique categories.

| Tool / Action | Category |
|---------------|----------|
| `read`, `grep`, `glob` on source files | Static analysis |
| `shell` with `objdump`, `nm`, `strings` | Static analysis |
| `shell` with `gdb`, `lldb`, `frida` | Dynamic analysis |
| `shell` with `afl`, `honggfuzz`, `libfuzzer` | Dynamic analysis |
| `shell` with `tcpdump`, `wireshark`, `tshark` | Network analysis |
| `shell` with `curl`, `wget`, custom HTTP | Web analysis |
| `shell` with `nmap`, `masscan` | Network analysis |
| `shell` with `openssl`, `hashcat` | Cryptanalysis |
| Writing phishing emails / scripts | Social engineering |
| `shell` with `strace`, `ltrace` | Dynamic analysis |

---

## Suggestion Matrix

When the agent is stuck in one category, suggest an alternative:

| Current Category | Suggest |
|------------------|---------|
| Static analysis | Dynamic analysis, Network analysis |
| Dynamic analysis | Static analysis, Network analysis |
| Network analysis | Dynamic analysis, Web analysis |
| Web analysis | Network analysis, Cryptanalysis |
| Cryptanalysis | Static analysis, Dynamic analysis |
| Social engineering | Web analysis, Network analysis |

**Rule:** Never suggest the same category the agent is already using. Always suggest a fundamentally different approach.
