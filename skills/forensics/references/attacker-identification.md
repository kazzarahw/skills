# Attacker Identification

Techniques for identifying and clustering attackers across web2 and web3 environments.

## Table of Contents

- [Web2 Attacker Identification](#web2-attacker-identification)
- [Web3 Attacker Identification](#web3-attacker-identification)
- [Known Threat Actors](#known-threat-actors)
- [Attribution Confidence Scoring](#attribution-confidence-scoring)
- [Tools](#tools)
- [Legal Considerations](#legal-considerations)
- [Best Practices](#best-practices)

## Web2 Attacker Identification

### IP Analysis

```bash
# Extract source IPs from logs
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Check IP reputation
# Use AbuseIPDB, VirusTotal, or ThreatCrowd
curl "https://api.abuseipdb.com/api/v2/check?ipAddress=<ip>" \
  -H "Key: <api_key>" \
  -H "Accept: application/json"

# Check for VPN/Tor usage
# Tor exit nodes
curl "https://check.torproject.org/torbulkexitlist" | grep "<ip>"

# Known VPN exit nodes
# Use IP2Location or similar service

# Geolocation
curl "http://ip-api.com/json/<ip>"
```

### TTP Mapping (MITRE ATT&CK)

| Tactic | Technique | Log Indicators |
|--------|-----------|----------------|
| Initial Access | Phishing | Email logs, web proxy logs |
| Initial Access | Exploit Public-Facing Application | WAF logs, application logs |
| Execution | Command and Scripting Interpreter | Process logs, PowerShell logs |
| Persistence | Registry Run Keys | Registry logs, EDR logs |
| Privilege Escalation | Exploitation for Privilege Escalation | System logs, audit logs |
| Defense Evasion | Indicator Removal | Log gaps, cleared logs |
| Credential Access | Credential Dumping | LSASS access, Mimikatz indicators |
| Discovery | Network Service Scanning | Port scan logs, firewall logs |
| Lateral Movement | Remote Services | RDP, SSH, SMB logs |
| Collection | Data from Local System | File access logs, EDR logs |
| Exfiltration | Exfiltration Over C2 Channel | Network logs, DLA logs |
| Impact | Data Encrypted for Impact | File system logs, ransom notes |

### Malware Analysis

```bash
# Identify malware family
# Use VirusTotal, Joe Sandbox, or Cuckoo

# Extract IOCs from malware
strings malware.exe | grep -iE "(http|https|ftp|\.exe|\.dll|mutex|registry)"

# Map to MITRE ATT&CK
# - Process creation → Execution
# - Registry modification → Persistence
# - Network connections → Command and Control
# - File encryption → Impact
```

### Credential Analysis

```bash
# Analyze stolen credentials
# Check for password patterns
# Check for reused credentials
# Check for default credentials

# Analyze authentication logs
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn

# Check for password spraying
# Many usernames, same password, short time window
```

## Web3 Attacker Identification

### Address Clustering

**Common Funding Source:**
```bash
# If multiple addresses receive funds from same source, likely same attacker
# Example: Multiple addresses funded by same CEX withdrawal

# Get funding sources for each address
cast logs --from-block <start_block> --to-block <end_block> \
  --rpc-url <rpc_url> \
  "Transfer(address,address,uint256)" \
  --address <token_contract>

# Cluster by common funding source
# If address A and address B both funded by address C, cluster A and B
```

**Timing Patterns:**
```python
# Pseudo-code for timing-based clustering
def cluster_by_timing(addresses, rpc_url):
    clusters = []
    
    for address in addresses:
        txs = get_all_transactions(address, rpc_url)
        first_tx = min(txs, key=lambda tx: tx['timestamp'])
        last_tx = max(txs, key=lambda tx: tx['timestamp'])
        
        # Check if timing overlaps with existing clusters
        for cluster in clusters:
            if timing_overlaps(first_tx, last_tx, cluster):
                cluster.append(address)
                break
        else:
            clusters.append([address])
    
    return clusters
```

**Behavioral Fingerprinting:**
```python
# Pseudo-code for behavioral fingerprinting
def behavioral_fingerprint(address, rpc_url):
    txs = get_all_transactions(address, rpc_url)
    
    fingerprint = {
        'gas_price_pattern': analyze_gas_prices(txs),
        'transaction_timing': analyze_timing(txs),
        'contract_preferences': analyze_contracts(txs),
        'token_preferences': analyze_tokens(txs),
        'value_patterns': analyze_values(txs),
        'nonce_patterns': analyze_nonces(txs)
    }
    
    return fingerprint
```

### Funding Source Analysis

```bash
# 1. Identify how attacker address was funded
# Check first incoming transaction to attacker address

# 2. Classify funding source
# - CEX (Binance, Coinbase, Kraken, etc.)
# - DEX (Uniswap, SushiSwap, etc.)
# - Bridge (Multichain, Wormhole, etc.)
# - Mixer (Tornado Cash, Samourai, etc.)
# - Other (Unknown)

# 3. Trace funding source
# If CEX: Document exchange, may be able to identify account
# If DEX: Continue tracing
# If Bridge: Trace to source chain
# If Mixer: Note that source is now opaque
```

### Behavioral Fingerprinting

**Gas Preferences:**
- High gas price = urgency, front-running
- Low gas price = non-urgent, regular transfer
- Consistent gas price = automated bot

**Transaction Timing:**
- Regular intervals = automated bot
- Irregular timing = manual operation
- Time zone patterns = geographic indicator

**Contract Interactions:**
- Repeated interactions with same contracts = specific target
- Diverse contract interactions = experienced attacker
- New contract interactions = custom attack tools

**Value Patterns:**
- Round numbers = manual operation
- Precise amounts = automated bot
- Dust amounts = testing or obfuscation

## Known Threat Actors

### APT Groups

| Group | Targets | TTPs | Attribution |
|-------|---------|------|-------------|
| Lazarus Group | Crypto exchanges, DeFi | Spear phishing, malware, social engineering | North Korea |
| APT28 | Government, military | Zero-day exploits, spear phishing | Russia |
| APT29 | Government, think tanks | Supply chain, cloud compromise | Russia |
| Carbanak | Financial institutions | ATM malware, ransomware | Russia |
| FIN7 | Retail, hospitality | POS malware, phishing | Russia |

### Cybercriminal Organizations

| Group | Specialty | Notable Incidents |
|-------|-----------|-------------------|
| REvil | Ransomware | Kaseya, JBA |
| Conti | Ransomware | Costa Rica, healthcare |
| LockBit | Ransomware | Multiple targets |
| BlackCat/ALPHV | Ransomware | Change Healthcare |
| Scattered Spider | Social engineering | MGM, Caesars |

### Crypto-Specific Threat Actors

| Group | Specialty | Notable Incidents |
|-------|-----------|-------------------|
| Lazarus Group | Bridge exploits, DEX hacks | Ronin Bridge, Harmony Bridge |
| North Korea | DeFi exploits, mixing | Multiple DeFi exploits |
| Ransomware groups | Crypto extortion | Multiple incidents |

## Attribution Confidence Scoring

### Confidence Levels

| Level | Description | Evidence Required |
|-------|-------------|-------------------|
| Speculative | Weak indicator, possible false positive | Single indicator, no corroboration |
| Moderate | Some indicators, but not conclusive | Multiple indicators, some corroboration |
| High | Strong indicators, likely correct | Multiple indicators, strong corroboration |
| Confirmed | Definitive proof of attribution | Direct evidence, multiple sources |

### Scoring Methodology

```python
# Pseudo-code for attribution confidence scoring
def calculate_confidence(indicators):
    score = 0
    
    # Technical indicators
    if indicators['malware_family']:
        score += 20
    if indicators['infrastructure']:
        score += 15
    if indicators['ttp_match']:
        score += 15
    
    # Behavioral indicators
    if indicators['timing_match']:
        score += 10
    if indicators['targeting_match']:
        score += 10
    
    # Intelligence indicators
    if indicators['threat_intel_match']:
        score += 20
    if indicators['historical_match']:
        score += 10
    
    # Determine confidence level
    if score >= 80:
        return "Confirmed"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Moderate"
    else:
        return "Speculative"
```

## Tools

### Chainalysis

```bash
# Chainalysis Reactor
# 1. Enter transaction hash or address
# 2. Reactor automatically traces fund flow
# 3. Identifies exchanges and services
# 4. Generates visual graph
# 5. Exports evidence package

# Chainalysis KYT (Know Your Transaction)
# API for real-time risk scoring
curl "https://api.chainalysis.com/api/kyt/v1/users/<user_id>/txs" \
  -H "Authorization: Token <api_key>" \
  -H "Content-Type: application/json"
```

### TRM Labs

```bash
# TRM Labs API
curl "https://api.trmlabs.com/v1/entities/<address>" \
  -H "Authorization: Bearer <api_key>"

# TRM provides:
# - Risk scoring
# - Entity identification
# - Transaction monitoring
# - Investigation tools
```

### Elliptic

```bash
# Elliptic API
curl "https://api.elliptic.co/v2/wallet/synchronous" \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"subject": {"asset": "ETH", "type": "address", "hash": "<address>"}}'

# Elliptic provides:
# - Wallet screening
# - Transaction screening
# - Risk scoring
# - Investigation tools
```

### Arkham

```bash
# Arkham API
curl "https://api.arkhamintelligence.com/api/v1/address/<address>" \
  -H "Authorization: Bearer <api_key>"

# Arkham provides:
# - Entity labeling
# - Fund flow visualization
# - Exchange identification
# - Attacker tracking
```

### Nansen

```bash
# Nansen API
curl "https://api.nansen.ai/v1/address/<address>/transactions" \
  -H "Authorization: Bearer <api_key>"

# Nansen provides:
# - Wallet labeling
# - Smart money tracking
# - Fund flow analysis
# - Exchange identification
```

## Legal Considerations

### Attribution is Not Accusation

**Key Principles:**
- Attribution is based on technical indicators, not proof
- False positives are possible
- Attribution should be presented with confidence levels
- Legal action requires additional evidence
- Defamation risks exist with public attribution

### Responsible Disclosure

**Best Practices:**
- Share findings with affected parties first
- Coordinate with law enforcement
- Consider public disclosure carefully
- Provide evidence to support claims
- Allow time for remediation

### Privacy Considerations

**Key Principles:**
- Respect privacy of individuals
- Only collect necessary data
- Comply with data protection laws
- Secure all collected data
- Limit access to authorized personnel

## Best Practices

1. **Use multiple indicators** — Never rely on single indicator
2. **Corroborate findings** — Cross-validate with multiple tools
3. **Document confidence levels** — Always state confidence level
4. **Consider false positives** — Clustering can produce false positives
5. **Respect privacy** — Only collect necessary data
6. **Consult legal** — Involve legal counsel for public attribution
7. **Share responsibly** — Consider impact of public attribution
8. **Stay objective** — Follow the evidence, avoid bias
9. **Keep learning** — Threat actors evolve, stay current
10. **Collaborate** — Share information with trusted partners
