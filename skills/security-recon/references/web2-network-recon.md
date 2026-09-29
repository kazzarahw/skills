# Web2 Network Reconnaissance

Comprehensive guide for web2 network reconnaissance. Covers passive and active techniques, tool selection, rate limiting, and evidence capture.

## Table of Contents

- [Passive Reconnaissance](#passive-reconnaissance)
- [Active Reconnaissance](#active-reconnaissance)
- [Web Fingerprinting](#web-fingerprinting)
- [Directory Enumeration](#directory-enumeration)
- [Vulnerability Scanning](#vulnerability-scanning)
- [Rate Limiting & Evasion](#rate-limiting--evasion)
- [Budget Caps & Scope Containment](#budget-caps--scope-containment)
- [Evidence Capture Format](#evidence-capture-format)
- [Common Ports & Services](#common-ports--services)
- [WSTG Mapping](#wstg-mapping)

---

## Passive Reconnaissance

Passive recon does not directly touch the target infrastructure. Use these techniques first to build a picture of the attack surface.

### OSINT Collection

#### theHarvester

Multi-source OSINT tool that aggregates emails, subdomains, IPs, and URLs from public sources.

```bash
# Full OSINT sweep across all sources
theHarvester -d example.com -b all -f results.html

# Specific sources (faster, less noise)
theHarvester -d example.com -b google,linkedin,bing

# Limit results per source
theHarvester -d example.com -b all -l 500
```

**Sources:** Google, Bing, LinkedIn, Twitter, GitHub, Shodan, Censys, Hunter.io, VirusTotal, and more.

#### Shodan

Internet-wide scanner database. Search for exposed services, banners, and vulnerabilities.

```bash
# Search for domain
shodan search hostname:example.com

# Search for exposed services
shodan search "hostname:example.com" --fields ip_str,port,product,version

# Search for specific vulnerabilities
shodan search "hostname:example.com vuln:CVE-2021-44228"
```

**Web interface:** `https://www.shodan.io/search?query=hostname:example.com`

#### Censys

Similar to Shodan with different coverage. Useful for certificate and service enumeration.

```bash
# Search via API
curl -s "https://search.censys.io/api/v2/hosts/search?q=example.com&per_page=100" \
  -u "$CENSYS_API_ID:$CENSYS_API_SECRET" | jq .
```

#### Google Dorks

Search engine queries that expose sensitive information.

```
# Exposed files
site:example.com filetype:pdf
site:example.com filetype:sql
site:example.com filetype:log
site:example.com filetype:env
site:example.com filetype:config

# Directory listing
site:example.com intitle:"index of"

# Sensitive paths
site:example.com inurl:admin
site:example.com inurl:backup
site:example.com inurl:api
site:example.com inurl:swagger
site:example.com inurl:.git

# Credentials
site:example.com "password" filetype:txt
site:example.com "api_key" filetype:env

# Error messages
site:example.com "sql syntax"
site:example.com "stack trace"
```

### DNS Enumeration

#### Basic DNS Records

```bash
# All DNS records
dig example.com ANY +noall +answer

# Specific record types
dig example.com A +noall +answer
dig example.com AAAA +noall +answer
dig example.com MX +noall +answer
dig example.com TXT +noall +answer
dig example.com NS +noall +answer
dig example.com SOA +noall +answer
dig example.com CNAME +noall +answer

# DNSSEC
dig example.com DNSKEY +noall +answer
dig example.com DS +noall +answer
```

#### Zone Transfer Attempt

```bash
# Attempt zone transfer (rarely works on modern servers)
dig @ns1.example.com example.com AXFR

# Using dnsrecon
dnsrecon -d example.com -t axfr
```

#### Subdomain Discovery

```bash
# subfinder - passive subdomain enumeration
subfinder -d example.com -o subdomains.txt
subfinder -d example.com -all -o subdomains-all.txt

# amass - comprehensive subdomain enumeration
amass enum -d example.com -o amass-subdomains.txt
amass enum -passive -d example.com -o amass-passive.txt

# crt.sh - certificate transparency
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u > crtsh-subdomains.txt

# dnsrecon - multiple techniques
dnsrecon -d example.com -t std,brt -j dnsrecon-results.json
```

### Certificate Transparency

Certificate transparency logs reveal subdomains that may not appear in DNS.

```bash
# crt.sh
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u

# certspotter
curl -s "https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true&expand=dns_names" | jq -r '.[].dns_names[]' | sort -u

# Cross-check with DNS
comm -12 <(sort subdomains.txt) <(sort crtsh-subdomains.txt)
```

---

## Active Reconnaissance

Active recon directly interacts with the target. **Verify scope authorization before proceeding.**

### Host Discovery

#### masscan

Fast port scanner. Scans the entire internet in ~6 minutes. Use for large ranges.

```bash
# Fast scan of common ports
masscan -p1-65535 10.0.0.0/24 --rate=10000 -oJ masscan-results.json

# Scan specific ports
masscan -p80,443,8080,8443 10.0.0.0/24 --rate=5000

# Scan with banners
masscan -p80,443 10.0.0.0/24 --rate=10000 --banners

# Exclude specific IPs
masscan -p1-65535 10.0.0.0/24 --rate=10000 --exclude 10.0.0.1
```

**Rate limiting:** Default 10,000 pps. Reduce to 1,000 pps for production targets. Aggressive rates require explicit authorization.

#### nmap Host Discovery

```bash
# Ping sweep (no port scan)
nmap -sn 10.0.0.0/24

# ARP discovery (local network)
nmap -PR -sn 10.0.0.0/24

# TCP SYN discovery
nmap -PS22,80,443 -sn 10.0.0.0/24

# UDP discovery
nmap -PU53,161 -sn 10.0.0.0/24
```

### Port Scanning

#### nmap Scan Types

```bash
# TCP SYN scan (stealthy, default for root)
nmap -sS 10.0.0.1

# TCP Connect scan (no root required)
nmap -sT 10.0.0.1

# UDP scan (slow)
nmap -sU --top-ports 100 10.0.0.1

# FIN scan (stealthy, may bypass firewalls)
nmap -sF 10.0.0.1

# NULL scan (stealthy)
nmap -sN 10.0.0.1

# Xmas scan (stealthy)
nmap -sX 10.0.0.1

# ACK scan (firewall mapping)
nmap -sA 10.0.0.1

# Window scan
nmap -sW 10.0.0.1

# Maimon scan
nmap -sM 10.0.0.1
```

#### nmap Timing Templates

```bash
# T0 - Paranoid (IDS evasion, very slow)
nmap -sS -T0 10.0.0.1

# T1 - Sneaky (slow)
nmap -sS -T1 10.0.0.1

# T2 - Polite (slow, less bandwidth)
nmap -sS -T2 10.0.0.1

# T3 - Normal (default)
nmap -sS -T3 10.0.0.1

# T4 - Aggressive (fast, may trigger IDS)
nmap -sS -T4 10.0.0.1

# T5 - Insane (very fast, unreliable)
nmap -sS -T5 10.0.0.1
```

#### nmap Service & Version Detection

```bash
# Service version detection
nmap -sV 10.0.0.1

# Version detection with intensity
nmap -sV --version-intensity 9 10.0.0.1

# Version detection (all ports)
nmap -sV -p- 10.0.0.1

# OS detection
nmap -O 10.0.0.1

# OS detection with aggressive timing
nmap -O -T4 10.0.0.1

# Combined service + OS + scripts + traceroute
nmap -A 10.0.0.1
```

#### nmap NSE Scripts

```bash
# Default scripts
nmap -sC 10.0.0.1

# Specific script categories
nmap --script=default 10.0.0.1
nmap --script=vuln 10.0.0.1
nmap --script=exploit 10.0.0.1
nmap --script=auth 10.0.0.1
nmap --script=brute 10.0.0.1
nmap --script=discovery 10.0.0.1

# Specific scripts
nmap --script=http-title,http-headers 10.0.0.1
nmap --script=ssl-cert,ssl-enum-ciphers 10.0.0.1
nmap --script=smb-os-discovery,smb-enum-shares 10.0.0.1

# Script with arguments
nmap --script=http-enum --script-args http-enum.basepath=/api 10.0.0.1

# All scripts (slow, comprehensive)
nmap --script=all 10.0.0.1
```

### Service Enumeration

#### HTTP/HTTPS

```bash
# HTTP headers
curl -sI https://example.com

# HTTP methods
curl -sI -X OPTIONS https://example.com

# SSL/TLS certificate
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -text

# SSL/TLS cipher enumeration
nmap --script=ssl-enum-ciphers -p 443 example.com

# HTTP enumeration
nmap --script=http-enum -p 80,443 example.com

# HTTP title
nmap --script=http-title -p 80,443 example.com

# HTTP headers
nmap --script=http-headers -p 80,443 example.com
```

#### SMB

```bash
# SMB enumeration
nmap --script=smb-os-discovery,smb-enum-shares,smb-enum-users -p 445 10.0.0.1

# SMB vulnerability scan
nmap --script=smb-vuln-* -p 445 10.0.0.1

# smbclient
smbclient -L //10.0.0.1 -N

# enum4linux
enum4linux -a 10.0.0.1
```

#### SMTP

```bash
# SMTP enumeration
nmap --script=smtp-commands,smtp-enum-users -p 25 10.0.0.1

# Manual SMTP
nc -nv 10.0.0.1 25
VRFY root
EXPN root
```

#### SNMP

```bash
# SNMP enumeration
nmap --script=snmp-info,snmp-interfaces -p 161 10.0.0.1

# snmpwalk
snmpwalk -v2c -c public 10.0.0.1

# SNMP brute force
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 10.0.0.1
```

#### Database

```bash
# MySQL
nmap --script=mysql-info,mysql-databases,mysql-users -p 3306 10.0.0.1

# PostgreSQL
nmap --script=pgsql-brute -p 5432 10.0.0.1

# MongoDB
nmap --script=mongodb-info,mongodb-databases -p 27017 10.0.0.1

# Redis
nmap --script=redis-info -p 6379 10.0.0.1
redis-cli -h 10.0.0.1 INFO
```

---

## Web Fingerprinting

### whatweb

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
```

### Wappalyzer

```bash
# CLI
wappalyzer https://example.com

# Node.js
npx wappalyzer https://example.com
```

### BuiltWith

```bash
# Web interface
https://builtwith.com/example.com

# API
curl -s "https://api.builtwith.com/v20/api.json?KEY=$BUILTWITH_KEY&LOOKUP=example.com" | jq .
```

### Additional Fingerprinting

```bash
# HTTP headers analysis
curl -sI https://example.com | grep -iE 'server|x-powered-by|x-aspnet-version'

# Favicon hash (Shodan)
curl -s https://example.com/favicon.ico | md5sum

# WAF detection
wafw00f https://example.com

# Technology detection
whatweb -a 3 https://example.com
```

---

## Directory Enumeration

### gobuster

```bash
# Directory brute force
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt

# With extensions
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

# With threads and timeout
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/big.txt -t 50 --timeout 10s

# With status codes
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -s 200,204,301,302,307,401,403

# Exclude status codes
gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt -b 404

# Fuzzing
gobuster fuzz -u https://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

### ffuf

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
```

### dirb

```bash
# Basic scan
dirb https://example.com

# With wordlist
dirb https://example.com /usr/share/wordlists/dirb/common.txt

# With extensions
dirb https://example.com -X .php,.html,.txt

# With cookies
dirb https://example.com -c "session=abc123"

# With authentication
dirb https://example.com -u admin:password
```

---

## Vulnerability Scanning

### nuclei

Template-based vulnerability scanner. Fast and comprehensive.

```bash
# Scan with CVE templates
nuclei -u https://example.com -t cves/

# Scan with exposure templates
nuclei -u https://example.com -t exposure/

# Scan with all templates
nuclei -u https://example.com -t nuclei-templates/

# Scan with specific templates
nuclei -u https://example.com -t cves/2021/CVE-2021-44228.yaml

# Scan with severity filter
nuclei -u https://example.com -t cves/ -severity critical,high

# Scan with rate limiting
nuclei -u https://example.com -t cves/ -rate-limit 100

# Scan with concurrency
nuclei -u https://example.com -t cves/ -c 25

# Scan with output
nuclei -u https://example.com -t cves/ -o nuclei-results.json -json

# Scan with tags
nuclei -u https://example.com -t cves/ -tags cve,rce,sqli

# Scan multiple targets
nuclei -l targets.txt -t cves/ -o nuclei-results.json

# Scan with headless (for XSS)
nuclei -u https://example.com -t cves/ -headless

# Scan with passive HTTP traffic
nuclei -passive -u https://example.com
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
nikto -h https://example.com -o nikto-results.html -Format html

# With tuning
nikto -h https://example.com -Tuning 123456789

# With evasion
nikto -h https://example.com -evasion 1

# With all options
nikto -h https://example.com -o nikto-results.txt -Format txt -Tuning x 123456789 -evasion 1
```

---

## Rate Limiting & Evasion

### Rate Limiting Defaults

| Tool | Default Rate | Recommended Rate | Aggressive Rate |
|------|-------------|------------------|-----------------|
| masscan | 10,000 pps | 1,000 pps | 10,000 pps |
| nmap | N/A (timing) | -T3 | -T5 |
| gobuster | 10 threads | 10 threads | 50 threads |
| ffuf | N/A | 100 req/s | 500 req/s |
| nuclei | N/A | 100 req/s | 500 req/s |
| nikto | N/A | Default | -Tuning x |

### Evasion Techniques

#### nmap Evasion

```bash
# Fragment packets
nmap -f 10.0.0.1

# Decoy scan
nmap -D RND:10 10.0.0.1

# Spoof source IP
nmap -S 10.0.0.2 10.0.0.1

# Idle scan (zombie)
nmap -sI zombie_host 10.0.0.1

# Randomize target order
nmap --randomize-hosts 10.0.0.0/24

# Slow scan
nmap -T0 10.0.0.1

# Source port manipulation
nmap --source-port 53 10.0.0.1
```

#### HTTP Evasion

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
```

---

## Budget Caps & Scope Containment

### Budget Caps

| Phase | Time Budget | Request Budget | Notes |
|-------|------------|----------------|-------|
| Passive recon | 2 hours | Unlimited | No rate limits |
| Active recon | 4 hours | 10,000 requests | Rate limited |
| Vuln scanning | 2 hours | 5,000 requests | Rate limited |
| Directory enum | 2 hours | 50,000 requests | Rate limited |

### Scope Containment

```bash
# Validate target is in scope
echo "10.0.0.1" | grep -f scope.txt || echo "OUT OF SCOPE"

# Exclude out-of-scope IPs
nmap -sS --exclude-file out-of-scope.txt 10.0.0.0/24

# Validate domain
echo "sub.example.com" | grep -E "^[a-z0-9.-]+\.example\.com$" || echo "OUT OF SCOPE"

# Check against scope file
if grep -q "example.com" scope.txt; then
    echo "IN SCOPE"
else
    echo "OUT OF SCOPE - ABORT"
    exit 1
fi
```

---

## Evidence Capture Format

Every finding must include evidence. Use the following format:

```markdown
### [SEVERITY] Finding Title

- **Category:** Web2
- **Target:** 10.0.0.1:8080
- **Description:** Apache Tomcat 9.0.30 detected with default credentials
- **Evidence:**
  ```
  $ nmap -sV -p 8080 10.0.0.1
  PORT     STATE SERVICE VERSION
  8080/tcp open  http    Apache Tomcat 9.0.30
  ```
- **Risk:** Default credentials may allow remote code execution
- **WSTG:** WSTG-ATHN-04
```

### Evidence Capture Commands

```bash
# Save all output
nmap -sV -sC -p- 10.0.0.1 | tee nmap-results.txt

# Save with timestamp
nmap -sV -sC -p- 10.0.0.1 | tee "nmap-$(date +%Y%m%d-%H%M%S).txt"

# Save JSON output
nmap -sV -sC -p- -oX nmap-results.xml 10.0.0.1

# Save nuclei output
nuclei -u https://example.com -t cves/ -o nuclei-results.json -json

# Save masscan output
masscan -p1-65535 10.0.0.0/24 --rate=10000 -oJ masscan-results.json
```

---

## Common Ports & Services

### Well-Known Ports

| Port | Service | Protocol | Description |
|------|---------|----------|-------------|
| 21 | FTP | TCP | File Transfer Protocol |
| 22 | SSH | TCP | Secure Shell |
| 23 | Telnet | TCP | Telnet (insecure) |
| 25 | SMTP | TCP | Simple Mail Transfer Protocol |
| 53 | DNS | TCP/UDP | Domain Name System |
| 67/68 | DHCP | UDP | Dynamic Host Configuration Protocol |
| 69 | TFTP | UDP | Trivial File Transfer Protocol |
| 80 | HTTP | TCP | Hypertext Transfer Protocol |
| 110 | POP3 | TCP | Post Office Protocol v3 |
| 123 | NTP | UDP | Network Time Protocol |
| 135 | MSRPC | TCP | Microsoft RPC |
| 137-139 | NetBIOS | TCP/UDP | NetBIOS Name/Datagram/Session |
| 143 | IMAP | TCP | Internet Message Access Protocol |
| 161/162 | SNMP | UDP | Simple Network Management Protocol |
| 389 | LDAP | TCP | Lightweight Directory Access Protocol |
| 443 | HTTPS | TCP | HTTP over TLS/SSL |
| 445 | SMB | TCP | Server Message Block |
| 465 | SMTPS | TCP | SMTP over SSL |
| 514 | Syslog | UDP | System Logging |
| 587 | SMTP | TCP | SMTP Submission |
| 636 | LDAPS | TCP | LDAP over SSL |
| 993 | IMAPS | TCP | IMAP over SSL |
| 995 | POP3S | TCP | POP3 over SSL |
| 1433 | MSSQL | TCP | Microsoft SQL Server |
| 1521 | Oracle | TCP | Oracle Database |
| 2049 | NFS | TCP | Network File System |
| 2375 | Docker | TCP | Docker API (insecure) |
| 2376 | Docker | TCP | Docker API (TLS) |
| 3306 | MySQL | TCP | MySQL Database |
| 3389 | RDP | TCP | Remote Desktop Protocol |
| 5432 | PostgreSQL | TCP | PostgreSQL Database |
| 5900 | VNC | TCP | Virtual Network Computing |
| 5985 | WinRM | TCP | Windows Remote Management (HTTP) |
| 5986 | WinRM | TCP | Windows Remote Management (HTTPS) |
| 6379 | Redis | TCP | Redis Key-Value Store |
| 8080 | HTTP-Alt | TCP | HTTP Alternate (proxy) |
| 8443 | HTTPS-Alt | TCP | HTTPS Alternate |
| 9200 | Elasticsearch | TCP | Elasticsearch |
| 11211 | Memcached | UDP | Memcached |
| 27017 | MongoDB | TCP | MongoDB Database |

### Quick Port Reference

```bash
# Top 100 ports
nmap --top-ports 100 10.0.0.1

# Top 1000 ports
nmap --top-ports 1000 10.0.0.1

# All ports
nmap -p- 10.0.0.1

# Common web ports
nmap -p 80,443,8080,8443,8000,8888 10.0.0.1

# Common database ports
nmap -p 3306,5432,1433,27017,6379,9200 10.0.0.1
```

---

## WSTG Mapping

Map recon findings to the OWASP Web Security Testing Guide (WSTG). Reconnaissance activities map to information gathering (WSTG-INFO-*) and configuration testing (WSTG-CONF-*) entries. Vulnerability scanning results map to specific WSTG-VULN-* entries based on the type of finding.

### Reconnaissance Activities → Information Gathering

| Activity | WSTG ID | Description |
|----------|---------|-------------|
| Subdomain enumeration | WSTG-INFO-01 | Search engine discovery and reconnaissance |
| Subdomain enumeration | WSTG-INFO-02 | Fingerprint web server |
| Subdomain enumeration | WSTG-INFO-04 | Enumerate applications on webserver |
| Subdomain enumeration | WSTG-INFO-06 | Identify application entry points |
| Subdomain enumeration | WSTG-INFO-09 | Map application architecture |
| Directory enumeration | WSTG-INFO-04 | Enumerate applications on webserver |
| Directory enumeration | WSTG-INFO-05 | Review comments and metadata |
| Directory enumeration | WSTG-INFO-06 | Identify application entry points |
| Directory enumeration | WSTG-INFO-07 | Map execution paths and application flows |
| Web fingerprinting | WSTG-INFO-02 | Fingerprint web server |
| Web fingerprinting | WSTG-INFO-03 | Review webserver meta files |
| Web fingerprinting | WSTG-INFO-08 | Fingerprint web application framework |
| Web fingerprinting | WSTG-INFO-09 | Map application architecture |
| Web fingerprinting | WSTG-INFO-10 | Map application dependencies |
| Port scanning | WSTG-CONF-01 | Test network infrastructure configuration |
| Port scanning | WSTG-CONF-02 | Test application platform configuration |
| Port scanning | WSTG-CONF-05 | Test for file extensions handling |
| Service enumeration | WSTG-CONF-01 | Test network infrastructure configuration |
| Service enumeration | WSTG-CONF-02 | Test application platform configuration |
| Service enumeration | WSTG-CONF-03 | Test for file upload and handling |
| DNS enumeration | WSTG-INFO-01 | Search engine discovery and reconnaissance |
| DNS enumeration | WSTG-CONF-01 | Test network infrastructure configuration |
| Certificate transparency | WSTG-INFO-01 | Search engine discovery and reconnaissance |
| Certificate transparency | WSTG-CONF-06 | Test HTTP methods and headers |
| OSINT collection | WSTG-INFO-01 | Search engine discovery and reconnaissance |
| OSINT collection | WSTG-INFO-05 | Review comments and metadata |

### Vulnerability Scanning Results → Specific WSTG Entries

Map vulnerability scanning findings to WSTG-VULN-* entries based on the type of vulnerability discovered.

| Vulnerability Type | WSTG ID | Description |
|-------------------|---------|-------------|
| Reflected XSS | WSTG-VULN-01 | Test for reflected cross-site scripting |
| Stored XSS | WSTG-VULN-02 | Test for stored cross-site scripting |
| HTTP verb tampering | WSTG-VULN-03 | Test for HTTP verb tampering |
| HTTP parameter pollution | WSTG-VULN-04 | Test for HTTP parameter pollution |
| SQL injection | WSTG-VULN-05 | Test for SQL injection |
| LDAP injection | WSTG-VULN-06 | Test for LDAP injection |
| XML injection | WSTG-VULN-07 | Test for XML injection |
| SSI injection | WSTG-VULN-08 | Test for SSI injection |
| XPath injection | WSTG-VULN-09 | Test for XPath injection |
| IMAP/SMTP injection | WSTG-VULN-10 | Test for IMAP/SMTP injection |
| Code injection | WSTG-VULN-11 | Test for code injection |
| Command injection | WSTG-VULN-12 | Test for command injection |
| Buffer overflow | WSTG-VULN-13 | Test for buffer overflow |
| Incubated vulnerabilities | WSTG-VULN-14 | Test for incubated vulnerabilities |
| HTTP splitting/smuggling | WSTG-VULN-15 | Test for HTTP splitting/smuggling |
| Host header injection | WSTG-VULN-17 | Test for host header injection |
| SSRF | WSTG-VULN-18 | Test for server-side request forgery |
| Insecure cryptographic storage | WSTG-VULN-20 | Test for insecure cryptographic storage |
| Insecure cryptographic transport | WSTG-VULN-21 | Test for insecure cryptographic transport |
| Insecure cryptographic algorithms | WSTG-VULN-22 | Test for insecure cryptographic algorithms |
| Insecure cryptographic modes | WSTG-VULN-23 | Test for insecure cryptographic modes |
| Insecure cryptographic padding | WSTG-VULN-24 | Test for insecure cryptographic padding |
| Insecure cryptographic salts | WSTG-VULN-25 | Test for insecure cryptographic salts |
| Insecure cryptographic iterations | WSTG-VULN-26 | Test for insecure cryptographic iterations |
| Insecure cryptographic key generation | WSTG-VULN-27 | Test for insecure cryptographic key generation |
| Insecure cryptographic key storage | WSTG-VULN-28 | Test for insecure cryptographic key storage |
| Insecure cryptographic key rotation | WSTG-VULN-29 | Test for insecure cryptographic key rotation |
| Insecure cryptographic key destruction | WSTG-VULN-30 | Test for insecure cryptographic key destruction |
| Insecure cryptographic key recovery | WSTG-VULN-31 | Test for insecure cryptographic key recovery |
| Insecure cryptographic key escrow | WSTG-VULN-32 | Test for insecure cryptographic key escrow |
| Insecure cryptographic key backup | WSTG-VULN-33 | Test for insecure cryptographic key backup |
| Insecure cryptographic key archival | WSTG-VULN-34 | Test for insecure cryptographic key archival |
| Insecure cryptographic key compromise | WSTG-VULN-35 | Test for insecure cryptographic key compromise |
| Insecure cryptographic key revocation | WSTG-VULN-36 | Test for insecure cryptographic key revocation |
| Insecure cryptographic key expiration | WSTG-VULN-37 | Test for insecure cryptographic key expiration |
| Insecure cryptographic key renewal | WSTG-VULN-38 | Test for insecure cryptographic key renewal |
| Insecure cryptographic key update | WSTG-VULN-39 | Test for insecure cryptographic key update |
| Insecure cryptographic key migration | WSTG-VULN-40 | Test for insecure cryptographic key migration |
| Insecure cryptographic key synchronization | WSTG-VULN-41 | Test for insecure cryptographic key synchronization |
| Insecure cryptographic key distribution | WSTG-VULN-42 | Test for insecure cryptographic key distribution |
| Insecure cryptographic key agreement | WSTG-VULN-43 | Test for insecure cryptographic key agreement |
| Insecure cryptographic key exchange | WSTG-VULN-44 | Test for insecure cryptographic key exchange |
| Insecure cryptographic key establishment | WSTG-VULN-45 | Test for insecure cryptographic key establishment |
| Insecure cryptographic key derivation | WSTG-VULN-46 | Test for insecure cryptographic key derivation |
| Insecure cryptographic key wrapping | WSTG-VULN-47 | Test for insecure cryptographic key wrapping |
| Insecure cryptographic key unwrapping | WSTG-VULN-48 | Test for insecure cryptographic key unwrapping |
| Insecure cryptographic key encapsulation | WSTG-VULN-49 | Test for insecure cryptographic key encapsulation |
| Insecure cryptographic key decapsulation | WSTG-VULN-50 | Test for insecure cryptographic key decapsulation |
