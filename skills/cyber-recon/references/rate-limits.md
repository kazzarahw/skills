# Rate Limiting Guidelines

> **Priority**: High | **Skill**: cyber-recon | **Last Updated**: 2026-09-28

A reference table of safe rate limits per tool and target type for reconnaissance operations.

---

## Quick Reference

| Tool | Default | Cautious | Aggressive | Notes |
|------|---------|----------|------------|-------|
| masscan | 100,000 pps | 10,000 pps | 1,000,000 pps | Use --rate to set pps |
| nmap | 1,500 pps | 100 pps | 10,000 pps | Use --min-rate/--max-rate |
| nuclei | 15 req/s | 5 req/s | 50 req/s | Use -rate-limit |
| gobuster | 50 req/s | 10 req/s | 100 req/s | Use -t for threads |
| ffuf | 50 req/s | 10 req/s | 100 req/s | Use -rate for rate |
| nikto | 10 req/s | 2 req/s | 30 req/s | Use -delay for delay |

---

## Tool-Specific Rate Limits

### masscan

**Description**: Asynchronous port scanner, extremely fast

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 100,000 pps | Internal networks, lab environments |
| Cautious | 10,000 pps | Production networks, sensitive targets |
| Aggressive | 1,000,000 pps | Lab environments only, may cause network issues |

**Command Examples**:
```bash
# Default (100k pps)
masscan -p1-65535 <target> --rate=100000

# Cautious (10k pps)
masscan -p1-65535 <target> --rate=10000

# Aggressive (1M pps) - LAB ONLY
masscan -p1-65535 <target> --rate=1000000

# With exclusions
masscan -p1-65535 <target> --rate=10000 --exclude 10.0.0.0/8
```

**Notes**:
- masscan can overwhelm networks and cause denial of service
- Always get written permission before aggressive scanning
- Use `--wait` to control SYN cache behavior
- Consider `--retries` for unreliable networks

---

### nmap

**Description**: Synchronous port scanner with service detection

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 1,500 pps | General purpose scanning |
| Cautious | 100 pps | Production networks, WAF-protected targets |
| Aggressive | 10,000 pps | Internal networks, lab environments |

**Command Examples**:
```bash
# Default timing (-T4)
nmap -sV -sC <target>

# Cautious timing (-T2)
nmap -sV -sC -T2 <target>

# Aggressive timing (-T5)
nmap -sV -sC -T5 <target>

# Custom rate
nmap -sV -sC --min-rate 100 --max-rate 1000 <target>

# With scan delay
nmap -sV -sC --scan-delay 1s <target>
```

**Notes**:
- nmap's `-T` flag controls timing (0-5)
- `-T0` (Paranoid): 5 minutes between probes
- `-T1` (Sneaky): 15 seconds between probes
- `-T2` (Polite): 400ms between probes
- `-T3` (Normal): default timing
- `-T4` (Aggressive): fast scan
- `-T5` (Insane): very fast, may miss ports

---

### nuclei

**Description**: Template-based vulnerability scanner

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 15 req/s | General purpose scanning |
| Cautious | 5 req/s | Production networks, rate-limited targets |
| Aggressive | 50 req/s | Internal networks, lab environments |

**Command Examples**:
```bash
# Default rate
nuclei -u <target> -rate-limit 15

# Cautious rate
nuclei -u <target> -rate-limit 5

# Aggressive rate
nuclei -u <target> -rate-limit 50

# With concurrency control
nuclei -u <target> -rate-limit 15 -c 10

# With timeout
nuclei -u <target> -rate-limit 15 -timeout 5
```

**Notes**:
- nuclei can generate significant traffic
- Use `-rate-limit` to control requests per second
- Use `-c` to control concurrent requests
- Use `-timeout` to control request timeout
- Consider `-retries` for unreliable networks

---

### gobuster

**Description**: Directory/file brute forcer

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 50 req/s | General purpose brute forcing |
| Cautious | 10 req/s | Production networks, WAF-protected targets |
| Aggressive | 100 req/s | Internal networks, lab environments |

**Command Examples**:
```bash
# Default threads (10)
gobuster dir -u <target> -w wordlist.txt

# Cautious threads (5)
gobuster dir -u <target> -w wordlist.txt -t 5

# Aggressive threads (50)
gobuster dir -u <target> -w wordlist.txt -t 50

# With delay
gobuster dir -u <target> -w wordlist.txt -t 10 -d 100ms

# With timeout
gobuster dir -u <target> -w wordlist.txt -t 10 --timeout 10s
```

**Notes**:
- gobuster uses threads, not rate limiting
- Lower thread count = slower but safer
- Use `-d` to add delay between requests
- Use `--timeout` to control request timeout
- Consider `-r` to follow redirects

---

### ffuf

**Description**: Fast web fuzzer

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 50 req/s | General purpose fuzzing |
| Cautious | 10 req/s | Production networks, rate-limited targets |
| Aggressive | 100 req/s | Internal networks, lab environments |

**Command Examples**:
```bash
# Default rate
ffuf -u <target>/FUZZ -w wordlist.txt

# Cautious rate
ffuf -u <target>/FUZZ -w wordlist.txt -rate 10

# Aggressive rate
ffuf -u <target>/FUZZ -w wordlist.txt -rate 100

# With delay
ffuf -u <target>/FUZZ -w wordlist.txt -rate 10 -p 0.1

# With timeout
ffuf -u <target>/FUZZ -w wordlist.txt -rate 10 -timeout 10
```

**Notes**:
- ffuf uses `-rate` for requests per second
- Use `-p` to add delay between requests
- Use `-timeout` to control request timeout
- Consider `-maxtime` to limit total scan time
- Use `-maxtime-job` to limit per-job time

---

### nikto

**Description**: Web server scanner

| Setting | Rate | Use Case |
|---------|------|----------|
| Default | 10 req/s | General purpose scanning |
| Cautious | 2 req/s | Production networks, WAF-protected targets |
| Aggressive | 30 req/s | Internal networks, lab environments |

**Command Examples**:
```bash
# Default delay (0s)
nikto -h <target>

# Cautious delay (5s)
nikto -h <target> -delay 5

# Aggressive delay (0s, max threads)
nikto -h <target> -maxtime 30m

# With tuning
nikto -h <target> -Tuning x 6

# With evasion
nikto -h <target> -evasion 1
```

**Notes**:
- nikto uses `-delay` to control delay between requests
- Use `-maxtime` to limit total scan time
- Use `-Tuning` to control scan depth
- Use `-evasion` to control evasion techniques
- Consider `-Format` for output format

---

## Target Type Modifiers

### WAF-Protected Targets

**Characteristics**:
- Web Application Firewall (Cloudflare, AWS WAF, Akamai, etc.)
- Rate limiting at edge
- Bot detection
- CAPTCHA challenges

**Recommended Adjustments**:
- Reduce rate by 50-80%
- Use cautious or lower settings
- Add random delays between requests
- Rotate User-Agent strings
- Use residential proxies if necessary

**Example**:
```bash
# WAF-protected target
nuclei -u <target> -rate-limit 3 -c 5
gobuster dir -u <target> -w wordlist.txt -t 3 -d 500ms
```

---

### CDN-Protected Targets

**Characteristics**:
- Content Delivery Network (Cloudflare, Fastly, Akamai, etc.)
- Distributed edge nodes
- Rate limiting per IP
- Geographic restrictions

**Recommended Adjustments**:
- Reduce rate by 30-50%
- Use cautious settings
- Consider origin IP discovery
- Use multiple source IPs if available

**Example**:
```bash
# CDN-protected target
nmap -sV -sC -T2 <target>
nuclei -u <target> -rate-limit 8 -c 10
```

---

### Rate-Limited Targets

**Characteristics**:
- Explicit rate limiting (429 responses)
- Throttling after threshold
- Account lockout potential
- API rate limits

**Recommended Adjustments**:
- Reduce rate by 70-90%
- Use cautious or lower settings
- Implement exponential backoff
- Monitor for 429 responses
- Use session persistence

**Example**:
```bash
# Rate-limited target
nuclei -u <target> -rate-limit 2 -c 3
ffuf -u <target>/FUZZ -w wordlist.txt -rate 5 -p 0.5
```

---

### Idle/Low-Traffic Targets

**Characteristics**:
- Low traffic volume
- Minimal monitoring
- Legacy systems
- Development/staging environments

**Recommended Adjustments**:
- Can use aggressive settings
- Monitor for unexpected behavior
- Still maintain reasonable limits
- Document all scanning activity

**Example**:
```bash
# Idle target
nmap -sV -sC -T4 <target>
nuclei -u <target> -rate-limit 30 -c 20
```

---

## Rate Limit Decision Matrix

| Target Type | masscan | nmap | nuclei | gobuster | ffuf | nikto |
|-------------|---------|------|--------|----------|------|-------|
| Internal/Lab | Aggressive | Aggressive | Aggressive | Aggressive | Aggressive | Aggressive |
| Production | Cautious | Cautious | Cautious | Cautious | Cautious | Cautious |
| WAF-Protected | N/A | Cautious | Cautious | Cautious | Cautious | Cautious |
| CDN-Protected | N/A | Cautious | Cautious | Cautious | Cautious | Cautious |
| Rate-Limited | N/A | Cautious | Cautious | Cautious | Cautious | Cautious |
| Idle | Aggressive | Aggressive | Aggressive | Aggressive | Aggressive | Aggressive |

---

## When to Adjust Rate Limits

### Increase Rate When:
- Scanning internal/lab networks
- Target is idle with low traffic
- Time constraints require faster scanning
- Target has no rate limiting
- Scanning during maintenance windows

### Decrease Rate When:
- Target is production-critical
- WAF/CDN protection is detected
- Rate limiting responses (429) are received
- Network congestion is observed
- Target is sensitive (healthcare, financial)
- Scanning during business hours

### Emergency Stop Conditions:
- Target becomes unresponsive
- Network performance degrades
- Security team contacts you
- Unexpected alerts are triggered
- Legal/compliance concerns arise

---

## Rate Limit Best Practices

1. **Always start cautious**: Begin with lower rates and increase if safe
2. **Monitor responses**: Watch for 429, 503, and other rate limit indicators
3. **Use exponential backoff**: Increase delay when rate limited
4. **Respect robots.txt**: Check and follow robots.txt directives
5. **Document settings**: Record all rate limit configurations
6. **Get authorization**: Ensure written permission for all scanning
7. **Time scanning appropriately**: Avoid business hours for production
8. **Use scan windows**: Coordinate with target organization
9. **Implement circuit breakers**: Stop scanning if issues detected
10. **Log all activity**: Maintain detailed scan logs

---

## References

- [Nmap Timing Templates](https://nmap.org/book/man-performance.html)
- [masscan Documentation](https://github.com/robertdavidgraham/masscan)
- [nuclei Documentation](https://docs.projectdiscovery.io/tools/nuclei)
- [ffuf Documentation](https://github.com/ffuf/ffuf)
- [gobuster Documentation](https://github.com/OJ/gobuster)
- [nikto Documentation](https://github.com/sullo/nikto)
