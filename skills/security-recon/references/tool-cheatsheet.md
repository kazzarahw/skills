# Tool Cheatsheet

Quick reference for all reconnaissance tools. Covers web2 tools, web3 tools, common commands and flags, output parsing tips, and rate limiting defaults.

## Table of Contents

- [Web2 Tools](#web2-tools)
- [Web3 Tools](#web3-tools)
- [Output Parsing Tips](#output-parsing-tips)
- [Rate Limiting Defaults](#rate-limiting-defaults)

---

## Web2 Tools

### nmap

Network scanner for port scanning, service detection, and vulnerability scanning.

```bash
# Basic scans
nmap 10.0.0.1                          # Default scan (top 1000 ports)
nmap -sS 10.0.0.1                       # TCP SYN scan (stealthy)
nmap -sT 10.0.0.1                       # TCP Connect scan (no root)
nmap -sU 10.0.0.1                       # UDP scan (slow)
nmap -sA 10.0.0.1                       # ACK scan (firewall mapping)
nmap -sF 10.0.0.1                       # FIN scan (stealthy)
nmap -sN 10.0.0.1                       # NULL scan (stealthy)
nmap -sX 10.0.0.1                       # Xmas scan (stealthy)

# Port specification
nmap -p 80 10.0.0.1                     # Single port
nmap -p 80,443 10.0.0.1                 # Multiple ports
nmap -p 1-1000 10.0.0.1                 # Port range
nmap -p- 10.0.0.1                       # All ports (65535)
nmap --top-ports 100 10.0.0.1           # Top 100 ports
nmap --top-ports 1000 10.0.0.1          # Top 1000 ports

# Service and version detection
nmap -sV 10.0.0.1                       # Service version detection
nmap -sV --version-intensity 9 10.0.0.1 # Aggressive version detection
nmap -sV --version-light 10.0.0.1       # Light version detection

# OS detection
nmap -O 10.0.0.1                        # OS detection
nmap -O --osscan-guess 10.0.0.1         # Aggressive OS detection

# Timing templates
nmap -T0 10.0.0.1                       # Paranoid (IDS evasion)
nmap -T1 10.0.0.1                       # Sneaky
nmap -T2 10.0.0.1                       # Polite
nmap -T3 10.0.0.1                       # Normal (default)
nmap -T4 10.0.0.1                       # Aggressive
nmap -T5 10.0.0.1                       # Insane

# NSE scripts
nmap -sC 10.0.0.1                       # Default scripts
nmap --script=default 10.0.0.1          # Default scripts
nmap --script=vuln 10.0.0.1             # Vulnerability scripts
nmap --script=exploit 10.0.0.1          # Exploit scripts
nmap --script=auth 10.0.0.1             # Authentication scripts
nmap --script=brute 10.0.0.1            # Brute force scripts
nmap --script=discovery 10.0.0.1        # Discovery scripts
nmap --script=http-* 10.0.0.1           # All HTTP scripts
nmap --script=smb-* 10.0.0.1            # All SMB scripts
nmap --script=ssl-* 10.0.0.1            # All SSL scripts
nmap --script=all 10.0.0.1              # All scripts (slow)

# Script arguments
nmap --script=http-enum --script-args http-enum.basepath=/api 10.0.0.1
nmap --script=http-headers --script-args http-headers.use-get 10.0.0.1

# Output formats
nmap -oN output.txt 10.0.0.1            # Normal output
nmap -oX output.xml 10.0.0.1            # XML output
nmap -oG output.gnmap 10.0.0.1          # Grepable output
nmap -oA output 10.0.0.1                # All formats

# Evasion
nmap -f 10.0.0.1                        # Fragment packets
nmap -D RND:10 10.0.0.1                 # Decoy scan
nmap -S 10.0.0.2 10.0.0.1               # Spoof source IP
nmap -sI zombie 10.0.0.1                # Idle scan
nmap --source-port 53 10.0.0.1          # Source port manipulation
nmap --randomize-hosts 10.0.0.0/24      # Randomize target order
nmap --spoof-mac 0 10.0.0.1             # Spoof MAC address

# Combined
nmap -A 10.0.0.1                        # Aggressive scan (OS + version + scripts + traceroute)
nmap -sS -sV -sC -O -T4 10.0.0.1        # Comprehensive scan
nmap -sS -sV -sC -O -T4 -oA output 10.0.0.1  # Comprehensive scan with all output
```

### masscan

Fast port scanner for large networks.

```bash
# Basic scans
masscan 10.0.0.0/24                     # Scan all ports (default rate: 100 pps)
masscan -p80,443 10.0.0.0/24            # Scan specific ports
masscan -p1-65535 10.0.0.0/24           # Scan all ports

# Rate limiting
masscan --rate=1000 10.0.0.0/24         # 1000 packets per second
masscan --rate=10000 10.0.0.0/24        # 10000 packets per second
masscan --rate=100000 10.0.0.0/24       # 100000 packets per second

# Output formats
masscan -oJ output.json 10.0.0.0/24     # JSON output
masscan -oX output.xml 10.0.0.0/24      # XML output
masscan -oG output.grep 10.0.0.0/24     # Grepable output
masscan -oL output.list 10.0.0.0/24     # List output

# Banners
masscan --banners 10.0.0.0/24           # Grab banners

# Exclusions
masscan --exclude 10.0.0.1 10.0.0.0/24  # Exclude IP
masscan --exclude-file exclude.txt 10.0.0.0/24  # Exclude from file

# Combined
masscan -p1-65535 10.0.0.0/24 --rate=10000 -oJ output.json
```

### gobuster

Directory and file brute forcer.

```bash
# Directory brute force
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt

# With extensions
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

# With threads
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -t 50

# With status codes
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -s 200,204,301,302,307,401,403

# Exclude status codes
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -b 404

# With cookies
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -c "session=abc123"

# With authentication
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -u admin:password

# Fuzzing
gobuster fuzz -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Virtual host discovery
gobuster vhost -u https://example.com -w /usr/share/wordlists/subdomains-top1million-5000.txt

# DNS enumeration
gobuster dns -d example.com -w /usr/share/wordlists/subdomains-top1million-5000.txt

# Output
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -o output.txt
```

### ffuf

Fast web fuzzer.

```bash
# Directory brute force
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# With recursion
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -recursion -recursion-depth 2

# With extensions
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .php,.html,.txt

# With rate limiting
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -rate 100

# With filtering
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -fs 404,403

# With matching
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302

# Virtual host discovery
ffuf -u https://example.com -H "Host: FUZZ.example.com" -w /usr/share/wordlists/subdomains-top1million-5000.txt

# Parameter fuzzing
ffuf -u https://example.com/?FUZZ=value -w /usr/share/wordlists/dirb/common.txt

# POST data fuzzing
ffuf -u https://example.com/ -X POST -d "FUZZ=value" -w /usr/share/wordlists/dirb/common.txt

# Output
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -o output.json -json
```

### nikto

Web server vulnerability scanner.

```bash
# Basic scan
nikto -h https://example.com

# With port
nikto -h 10.0.0.1 -p 8080

# With SSL
nikto -h https://example.com -ssl

# With output
nikto -h https://example.com -o output.html -Format html

# With tuning
nikto -h https://example.com -Tuning 123456789

# With evasion
nikto -h https://example.com -evasion 1

# With all options
nikto -h https://example.com -o output.txt -Format txt -Tuning x 123456789 -evasion 1

# Tuning options
# 1: Interesting file
# 2: Misconfiguration
# 3: Information disclosure
# 4: Injection
# 5: Remote file retrieval
# 6: Denial of service
# 7: Remote server
# 8: Command execution
# 9: SQL injection
# 0: File upload
# x: Reverse tuning
```

### nuclei

Template-based vulnerability scanner.

```bash
# Basic scan
nuclei -u https://example.com

# With CVE templates
nuclei -u https://example.com -t cves/

# With exposure templates
nuclei -u https://example.com -t exposure/

# With all templates
nuclei -u https://example.com -t nuclei-templates/

# With specific templates
nuclei -u https://example.com -t cves/2021/CVE-2021-44228.yaml

# With severity filter
nuclei -u https://example.com -t cves/ -severity critical,high

# With rate limiting
nuclei -u https://example.com -t cves/ -rate-limit 100

# With concurrency
nuclei -u https://example.com -t cves/ -c 25

# With output
nuclei -u https://example.com -t cves/ -o output.json -json

# With tags
nuclei -u https://example.com -t cves/ -tags cve,rce,sqli

# Multiple targets
nuclei -l targets.txt -t cves/ -o output.json -json

# Headless (for XSS)
nuclei -u https://example.com -t cves/ -headless

# Passive HTTP traffic
nuclei -passive -u https://example.com

# With interactsh
nuclei -u https://example.com -t cves/ -interactsh-url https://interactsh.com

# With templates list
nuclei -tl

# Update templates
nuclei -ut
```

### whatweb

Web technology fingerprinting tool.

```bash
# Level 1 (quick)
whatweb -a 1 https://example.com

# Level 3 (aggressive)
whatweb -a 3 https://example.com

# Level 4 (very aggressive, may trigger WAF)
whatweb -a 4 https://example.com

# Batch scan
whatweb -a 1 -i targets.txt

# Output to file
whatweb -a 1 https://example.com --log-verbose=whatweb-results.txt

# Output formats
whatweb -a 1 https://example.com --log-json=whatweb-results.json
whatweb -a 1 https://example.com --log-xml=whatweb-results.xml
```

### subfinder

Passive subdomain enumeration tool.

```bash
# Basic enumeration
subfinder -d example.com

# With all sources
subfinder -d example.com -all

# Output to file
subfinder -d example.com -o subdomains.txt

# With recursive
subfinder -d example.com -recursive

# With silent output
subfinder -d example.com -silent

# With sources
subfinder -d example.com -sources crtsh,virustotal,alienvault

# Exclude sources
subfinder -d example.com -exclude-sources shodan,censys

# With config
subfinder -d example.com -config config.yaml
```

### theHarvester

OSINT collection tool.

```bash
# All sources
theHarvester -d example.com -b all

# Specific sources
theHarvester -d example.com -b google,linkedin,bing

# Limit results
theHarvester -d example.com -b all -l 500

# Output to file
theHarvester -d example.com -b all -f results.html

# With Shodan
theHarvester -d example.com -b shodan

# With GitHub
theHarvester -d example.com -b github-code

# With config
theHarvester -d example.com -b all -c config.yaml
```

---

## Web3 Tools

### Etherscan

Ethereum block explorer and analytics platform.

```bash
# Web interface
https://etherscan.io/address/0xAddress
https://etherscan.io/tx/0xTxHash
https://etherscan.io/token/0xTokenAddress

# API - Get balance
curl -s "https://api.etherscan.io/api?module=account&action=balance&address=0xAddress&tag=latest" | jq .

# API - Get transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=100&sort=asc" | jq .

# API - Get token transfers
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=100&sort=asc" | jq .

# API - Get contract source code
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq .

# API - Get contract ABI
curl -s "https://api.etherscan.io/api?module=contract&action=getabi&address=0xAddress" | jq .

# API - Get internal transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlistinternal&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=100&sort=asc" | jq .

# API - Get logs
curl -s "https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=0&toBlock=latest&address=0xAddress&topic0=0xTopicHash" | jq .
```

### Solscan

Solana block explorer and analytics platform.

```bash
# Web interface
https://solscan.io/account/0xAddress
https://solscan.io/tx/0xSignature
https://solscan.io/token/0xTokenAddress

# API - Get account info
curl -s "https://api.solscan.io/v2/account/detail?address=0xAddress" | jq .

# API - Get transactions
curl -s "https://api.solscan.io/v2/account/txs?address=0xAddress&limit=100" | jq .

# API - Get token accounts
curl -s "https://api.solscan.io/v2/account/tokens?address=0xAddress" | jq .

# API - Get transaction details
curl -s "https://api.solscan.io/v2/transaction/detail?tx=0xSignature" | jq .
```

### Blockscout

Open-source block explorer for EVM chains.

```bash
# Web interface
https://blockscout.com/eth/mainnet/address/0xAddress
https://blockscout.com/eth/mainnet/tx/0xTxHash

# API - Get address info
curl -s "https://blockscout.com/eth/mainnet/api?module=account&action=balance&address=0xAddress" | jq .

# API - Get transactions
curl -s "https://blockscout.com/eth/mainnet/api?module=account&action=txlist&address=0xAddress" | jq .

# API - Get token transfers
curl -s "https://blockscout.com/eth/mainnet/api?module=account&action=tokentx&address=0xAddress" | jq .
```

### Heimdall

Fast EVM bytecode decompilation tool.

```bash
# Decompile bytecode
heimdall decompile 0xAddress --rpc-url https://eth.llamarpc.com

# Decompile with output
heimdall decompile 0xAddress -o decompiled/ --rpc-url https://eth.llamarpc.com

# Decompile with resolver
heimdall decompile 0xAddress --resolver https://api.etherscan.io/api --etherscan-api-key $ETHERSCAN_API_KEY

# Decompile with all options
heimdall decompile 0xAddress --rpc-url https://eth.llamarpc.com --output decompiled/ --verbose
```

### Nansen

Blockchain analytics platform with wallet labeling.

```bash
# Web interface
https://nansen.ai

# API - Get address info
curl -s "https://api.nansen.ai/v1/address/0xAddress" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .

# API - Get address labels
curl -s "https://api.nansen.ai/v1/address/0xAddress/labels" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .

# API - Get address transactions
curl -s "https://api.nansen.ai/v1/address/0xAddress/transactions" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .

# API - Get smart money
curl -s "https://api.nansen.ai/v1/smart-money" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .
```

### TRM Labs

Blockchain intelligence and risk management platform.

```bash
# Web interface
https://trmlabs.com

# API - Get address risk
curl -s "https://api.trmlabs.com/v1/address/0xAddress/risk" -H "Authorization: Bearer $TRM_API_KEY" | jq .

# API - Get address sanctions
curl -s "https://api.trmlabs.com/v1/address/0xAddress/sanctions" -H "Authorization: Bearer $TRM_API_KEY" | jq .

# API - Get address labels
curl -s "https://api.trmlabs.com/v1/address/0xAddress/labels" -H "Authorization: Bearer $TRM_API_KEY" | jq .

# API - Get transaction risk
curl -s "https://api.trmlabs.com/v1/transaction/0xTxHash/risk" -H "Authorization: Bearer $TRM_API_KEY" | jq .
```

### Tenderly

Transaction simulation and debugging platform.

```bash
# Web interface
https://tenderly.co

# API - Simulate transaction
curl -s "https://api.tenderly.co/api/v1/public/simulate" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: $TENDERLY_API_KEY" \
  -d '{"network_id":"1","from":"0xAddress","to":"0xContractAddress","input":"0xCalldata","value":"0"}' | jq .

# API - Get transaction trace
curl -s "https://api.tenderly.co/api/v1/public/tx/0xTxHash/trace" \
  -H "X-Access-Key: $TENDERLY_API_KEY" | jq .

# API - Get contract
curl -s "https://api.tenderly.co/api/v1/public/contract/0xContractAddress" \
  -H "X-Access-Key: $TENDERLY_API_KEY" | jq .
```

### Foundry (cast)

EVM development framework with cast for RPC interaction.

```bash
# Get balance
cast balance 0xAddress --rpc-url https://eth.llamarpc.com

# Get nonce
cast nonce 0xAddress --rpc-url https://eth.llamarpc.com

# Get code
cast code 0xAddress --rpc-url https://eth.llamarpc.com

# Get storage
cast storage 0xAddress 0xSlot --rpc-url https://eth.llamarpc.com

# Call contract
cast call 0xAddress "functionName(types)(returnType)" --rpc-url https://eth.llamarpc.com

# Send transaction
cast send 0xAddress "functionName(types)" --private-key $PRIVATE_KEY --rpc-url https://eth.llamarpc.com

# Get transaction receipt
cast receipt 0xTxHash --rpc-url https://eth.llamarpc.com

# Get transaction details
cast tx 0xTxHash --rpc-url https://eth.llamarpc.com

# Get block details
cast block latest --rpc-url https://eth.llamarpc.com

# Decode calldata
cast calldata "functionName(types)" args...

# Get function signature
cast sig "functionName(types)"

# Get event signature
cast sig-event "EventName(types)"

# Get chain ID
cast chain-id --rpc-url https://eth.llamarpc.com

# Get gas price
cast gas-price --rpc-url https://eth.llamarpc.com
```

---

## Output Parsing Tips

### JSON Parsing with jq

```bash
# Extract specific fields
jq '.result[0].SourceCode' response.json

# Filter by condition
jq '.result[] | select(.to == "0xAddress")' response.json

# Count results
jq '.result | length' response.json

# Extract unique values
jq '[.result[].from] | unique' response.json

# Sort by value
jq '.result | sort_by(.value) | reverse' response.json

# Group by key
jq '.result | group_by(.from)' response.json

# Extract and format
jq -r '.result[] | "\(.from) -> \(.to): \(.value)"' response.json

# Calculate sum
jq '[.result[].value | tonumber] | add' response.json

# Extract timestamps
jq '.result[] | .timeStamp | tonumber | strftime("%Y-%m-%d %H:%M:%S")' response.json
```

### XML Parsing with xmllint

```bash
# Extract elements
xmllint --xpath "//port[@portid='80']/state/@state" nmap-results.xml

# Extract all ports
xmllint --xpath "//port" nmap-results.xml

# Format output
xmllint --format nmap-results.xml

# Count elements
xmllint --xpath "count(//port)" nmap-results.xml
```

### Grepable Output Parsing

```bash
# Extract open ports
grep "open" output.gnmap | awk '{print $2, $3}'

# Extract hosts with open ports
grep "Status: Up" output.gnmap

# Extract services
grep "open" output.gnmap | awk '{print $4}'

# Count open ports
grep -c "open" output.gnmap
```

### Text Output Parsing

```bash
# Extract open ports
grep "open" output.txt | awk '{print $1, $3}'

# Extract host IP
grep "Nmap scan report" output.txt | awk '{print $NF}'

# Extract service versions
grep "open" output.txt | awk '{print $1, $3, $4, $5}'

# Count open ports
grep -c "open" output.txt
```

---

## Rate Limiting Defaults

### Tool Rate Limits

| Tool | Default Rate | Recommended Rate | Aggressive Rate | Notes |
|------|-------------|------------------|-----------------|-------|
| masscan | 100 pps | 1,000 pps | 10,000 pps | Packets per second |
| nmap | N/A (timing) | -T3 | -T5 | Timing template |
| gobuster | 10 threads | 10 threads | 50 threads | Concurrent threads |
| ffuf | N/A | 100 req/s | 500 req/s | Requests per second |
| nuclei | N/A | 100 req/s | 500 req/s | Requests per second |
| nikto | N/A | Default | -Tuning x | No rate limit |
| whatweb | N/A | -a 1 | -a 4 | Aggression level |
| subfinder | N/A | Default | -all | Passive only |
| theHarvester | N/A | Default | -b all | Passive only |

### API Rate Limits

| API | Free Tier | Paid Tier | Notes |
|-----|-----------|-----------|-------|
| Etherscan | 5 req/s | 10 req/s | API key required |
| Solscan | 10 req/s | 100 req/s | API key required |
| Nansen | 10 req/s | 100 req/s | API key required |
| TRM Labs | 10 req/s | 100 req/s | API key required |
| Tenderly | 10 req/s | 100 req/s | API key required |
| Shodan | 1 req/s | 10 req/s | API key required |
| Censys | 1 req/s | 10 req/s | API key required |
| HaveIBeenPwned | 1 req/1.5s | N/A | API key required |
| Hunter.io | 10 req/s | 100 req/s | API key required |

### Rate Limiting Best Practices

```bash
# Add delay between requests
sleep 1 && curl https://api.example.com/endpoint

# Random delay
sleep $((RANDOM % 5)) && curl https://api.example.com/endpoint

# Rate limit with curl
curl --limit-rate 100K https://api.example.com/endpoint

# Rate limit with wget
wget --limit-rate=100k https://api.example.com/endpoint

# Parallel requests with rate limit
cat urls.txt | xargs -P 10 -I {} sh -c 'sleep 1 && curl {}'

# Using GNU parallel
parallel -j 10 --delay 1 curl {} ::: urls.txt
```

### Evasion Techniques

```bash
# Random User-Agent
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" https://example.com

# Rotate User-Agents
for ua in $(cat user-agents.txt); do curl -A "$ua" https://example.com; done

# Use proxy
curl -x http://proxy:8080 https://example.com

# Add delays
sleep 1 && curl https://example.com

# Random delays
sleep $((RANDOM % 5)) && curl https://example.com

# nmap evasion
nmap -f 10.0.0.1                    # Fragment packets
nmap -D RND:10 10.0.0.1             # Decoy scan
nmap -T0 10.0.0.1                   # Paranoid timing
nmap --source-port 53 10.0.0.1      # Source port manipulation
```
