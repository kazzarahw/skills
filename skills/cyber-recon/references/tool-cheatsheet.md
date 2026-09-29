# Tool Cheatsheet

Quick-reference commands for reconnaissance and vulnerability scanning.

## nmap

### Service Version Detection
```bash
nmap -sV -sC -p<ports> <target>
```
- `-sV`: Version detection
- `-sC`: Default scripts
- `-p`: Target specific ports

### Full Port Scan (Authorized Only)
```bash
nmap -sV -sC -p- --min-rate=1000 <target>
```
- `-p-`: All 65535 ports
- `--min-rate`: Speed control

### Stealth SYN Scan
```bash
nmap -sS -sV -p<ports> <target>
```
- `-sS`: SYN scan (requires root)

### UDP Scan
```bash
nmap -sU --top-ports 100 <target>
```
- `-sU`: UDP scan
- `--top-ports`: Most common ports

### Output Formats
```bash
nmap -sV -sC -p<ports> -oA <basename> <target>
```
- `-oA`: Output all formats (normal, XML, grepable)

### Version Intensity
```bash
nmap -sV --intensity 7 -p<ports> <target>
```
- `--intensity 0-9`: Higher = more probes, slower

## masscan

### Fast Discovery
```bash
masscan -p1-65535 --rate=1000 <target>
```
- `--rate`: Packets per second (adjust for network)

### Specific Ports
```bash
masscan -p80,443,8080,8443 --rate=1000 <target>
```

### Exclude Targets
```bash
masscan -p1-65535 --rate=1000 --exclude <ip> <target>
```

### Output
```bash
masscan -p1-65535 --rate=1000 -oJ <output.json> <target>
```
- `-oJ`: JSON output
- `-oL`: List output

## nuclei

### CVE Templates
```bash
nuclei -t cves/ -u <target>
```

### Exposure Templates
```bash
nuclei -t exposure/ -u <target>
```

### Multiple Template Directories
```bash
nuclei -t cves/ -t exposure/ -t misconfiguration/ -u <target>
```

### Severity Filter
```bash
nuclei -t cves/ -u <target> -severity high,critical
```

### Rate Limiting
```bash
nuclei -t cves/ -u <target> -rl 100
```
- `-rl`: Requests per second

### Output
```bash
nuclei -t cves/ -u <target> -o <output.json> -json
```

## gobuster

### Directory Enumeration
```bash
gobuster dir -u <url> -w /usr/share/wordlists/dirb/common.txt
```

### Medium Wordlist (Default)
```bash
gobuster dir -u <url> -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
```

### Extensions
```bash
gobuster dir -u <url> -w <wordlist> -x php,html,txt
```

### Threads
```bash
gobuster dir -u <url> -w <wordlist> -t 50
```
- `-t`: Concurrent threads (default 10)

### Status Codes
```bash
gobuster dir -u <url> -w <wordlist> -s 200,204,301,302,307,401,403
```

## ffuf

### Directory Fuzzing
```bash
ffuf -u <url>/FUZZ -w <wordlist>
```

### Recursive
```bash
ffuf -u <url>/FUZZ -w <wordlist> -recursion -recursion-depth 2
```

### Extensions
```bash
ffuf -u <url>/FUZZ -w <wordlist> -e .php,.html,.txt
```

### Threads
```bash
ffuf -u <url>/FUZZ -w <wordlist> -t 50
```

## whatweb

### Level 1 (Stealth - Default)
```bash
whatweb -a 1 <url>
```

### Level 3 (Aggressive)
```bash
whatweb -a 3 <url>
```

### Level 4 (Heavy)
```bash
whatweb -a 4 <url>
```

### Batch Mode
```bash
whatweb -a 1 -i <target_list.txt>
```

### Output
```bash
whatweb -a 1 <url> --log-json=<output.json>
```

## nikto

### Basic Scan
```bash
nikto -h <url>
```

### Specific Port
```bash
nikto -h <ip> -p 8080
```

### SSL
```bash
nikto -h <url> -ssl
```

### Output
```bash
nikto -h <url> -o <output.html> -Format html
```

### Tuning
```bash
nikto -h <url> -Tuning 123456789
```
- `1`: Interesting file
- `2`: Misconfiguration
- `3`: Information disclosure
- `4`: Injection
- `5`: Remote file retrieval
- `6`: Denial of service
- `7`: Remote shell
- `8`: Software identification
- `9`: Remote file inclusion

## OSINT Pipeline

### Subfinder (Subdomain Discovery)
```bash
subfinder -d <domain> -silent
```

### Amass (Deep OSINT)
```bash
amass enum -d <domain> -passive
```

### theHarvester (Emails, Subdomains)
```bash
theHarvester -d <domain> -b google,bing,linkedin
```

### httpx (HTTP Probing)
```bash
cat subdomains.txt | httpx -silent -status-code -title -tech-detect
```

### crt.sh (Certificate Transparency)
```bash
curl -s "https://crt.sh/?q=%25.<domain>&output=json" | jq -r '.[].name_value' | sort -u
```

### recon-ng (Framework)
```bash
recon-ng
# Inside recon-ng:
# use recon/domains-hosts/bing_domain_web
# set SOURCE <domain>
# run
```

## Wordlists

| Wordlist | Path | Use Case |
|----------|------|----------|
| dirb common | `/usr/share/wordlists/dirb/common.txt` | Quick scan |
| directory-list-2.3-medium | `/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt` | Balanced (default) |
| directory-list-2.3-big | `/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-big.txt` | Thorough |
| raft-large | `/usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt` | Large targets |
| subdomains-top1m | `/usr/share/seclists/Discovery/DNS/subdomains-top1m.txt` | Subdomain brute |

## Common Ports Reference

| Port | Service | Scan Priority |
|------|---------|---------------|
| 21 | ftp | Medium |
| 22 | ssh | High |
| 23 | telnet | Medium |
| 25 | smtp | Low |
| 53 | dns | Medium |
| 80 | http | High |
| 110 | pop3 | Low |
| 143 | imap | Low |
| 443 | https | High |
| 445 | smb | High |
| 3306 | mysql | Medium |
| 3389 | rdp | High |
| 5432 | postgresql | Medium |
| 8080 | http-proxy | High |
| 8443 | https-alt | High |
