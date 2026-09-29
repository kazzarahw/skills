# Web2 Log Analysis

Comprehensive guide to analyzing system, application, security, network, and authentication logs during incident response.

## Table of Contents

- [Log Sources](#log-sources)
- [Log Formats](#log-formats)
- [Analysis Techniques](#analysis-techniques)
- [Common Attack Patterns in Logs](#common-attack-patterns-in-logs)
- [Tools](#tools)
- [Log Retention and Preservation](#log-retention-and-preservation)
- [Chain of Custody for Log Evidence](#chain-of-custody-for-log-evidence)
- [Timeline Reconstruction from Logs](#timeline-reconstruction-from-logs)

## Log Sources

### System Logs

| Source | Location | Content |
|--------|----------|---------|
| Linux syslog | `/var/log/syslog`, `/var/log/messages` | Kernel events, service starts/stops, hardware errors |
| Linux auth log | `/var/log/auth.log`, `/var/log/secure` | Authentication attempts, sudo usage, SSH logins |
| Linux auditd | `/var/log/audit/audit.log` | System calls, file access, policy violations |
| Windows Event Log | `C:\Windows\System32\winevt\Logs\` | System, application, security events |
| macOS Unified Log | `log show` (command-line) | System-wide logging with structured data |
| systemd journal | `journalctl` | Service logs, boot messages, kernel messages |

### Application Logs

| Source | Location | Content |
|--------|----------|---------|
| Web server (nginx) | `/var/log/nginx/access.log`, `error.log` | HTTP requests, response codes, errors |
| Web server (Apache) | `/var/log/apache2/access.log`, `error.log` | HTTP requests, response codes, errors |
| Database (PostgreSQL) | `/var/log/postgresql/` | Queries, connections, errors, slow queries |
| Database (MySQL) | `/var/log/mysql/` | Queries, connections, errors, slow queries |
| Application logs | Varies by framework | Business logic events, errors, stack traces |
| Container logs | `docker logs`, `kubectl logs` | Container stdout/stderr, orchestration events |

### Security Logs

| Source | Location | Content |
|--------|----------|---------|
| Firewall | Vendor-specific | Allowed/denied connections, rule matches |
| IDS/IPS | Snort, Suricata, Zeek | Alerts, signatures matched, packet captures |
| EDR/XDR | CrowdStrike, SentinelOne, Carbon Black | Process creation, file modifications, network connections |
| WAF | ModSecurity, Cloudflare, AWS WAF | Blocked requests, rule violations, attack signatures |
| DLP | Vendor-specific | Data exfiltration attempts, policy violations |
| Antivirus | Windows Defender, ClamAV, etc. | Detections, quarantines, scan results |

### Network Logs

| Source | Location | Content |
|--------|----------|---------|
| NetFlow/sFlow | Collector | Flow records (src/dst IP, ports, bytes, duration) |
| DNS logs | BIND, dnsmasq, Windows DNS | Queries, responses, zone transfers |
| DHCP logs | ISC DHCP, Windows DHCP | Lease assignments, renewals |
| Proxy logs | Squid, HAProxy | URLs accessed, response codes, bytes transferred |
| VPN logs | OpenVPN, WireGuard, IPsec | Connections, authentication, traffic |
| PCAP | `tcpdump`, Wireshark | Full packet capture for deep analysis |

### Authentication Logs

| Source | Location | Content |
|--------|----------|---------|
| SSH | `/var/log/auth.log` | Login attempts, key usage, failures |
| Active Directory | Windows Security Event Log | Logon events (4624, 4625), privilege use |
| LDAP | OpenLDAP, AD | Bind requests, searches, modifications |
| OAuth/SAML | Identity provider logs | Token issuance, authentication flows |
| Application auth | Application-specific | Login attempts, session management, MFA events |

## Log Formats

### Syslog (RFC 5424)

```
<134>1 2024-01-15T10:30:00.000Z webserver01 nginx 1234 - - 
  client=192.168.1.100 method=GET uri=/api/users status=200 
  bytes=1234 referer=https://example.com ua="Mozilla/5.0"
```

**Fields:** Priority, Version, Timestamp, Hostname, App-name, ProcID, Structured Data, Message

### JSON

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "host": "webserver01",
  "service": "nginx",
  "level": "info",
  "client_ip": "192.168.1.100",
  "method": "GET",
  "uri": "/api/users",
  "status": 200,
  "bytes": 1234,
  "user_agent": "Mozilla/5.0"
}
```

### CEF (Common Event Format)

```
CEF:0|Company|Product|1.0|100|Successful login|5|
  src=192.168.1.100 dst=10.0.0.5 spt=51234 dpt=22 
  proto=TCP act=allow outcome=success
```

**Fields:** CEF Version, Device Vendor, Device Product, Device Version, Signature ID, Name, Severity, Extensions

### LEEF (Log Event Extended Format)

```
LEEF:2.0|Company|Product|1.0|100|
  src=192.168.1.100 dst=10.0.0.5 spt=51234 dpt=22 
  proto=TCP act=allow outcome=success
```

**Fields:** LEEF Version, Vendor, Product, Version, Event ID, Delimiter, Key-Value Pairs

### Windows Event Log

```
Event ID: 4624
Type: An account was successfully logged on
Logon Type: 3 (Network)
Account: administrator
Source IP: 192.168.1.100
Authentication Package: NTLM
```

**Key Event IDs:**
- 4624: Successful logon
- 4625: Failed logon
- 4672: Special privileges assigned
- 4720: User account created
- 4726: User account deleted
- 4732: Member added to security-enabled group
- 1102: Audit log cleared

## Analysis Techniques

### Pattern Matching

```bash
# Find failed SSH login attempts
grep "Failed password" /var/log/auth.log

# Find sudo usage
grep "sudo:" /var/log/auth.log

# Find 4xx/5xx responses in web logs
awk '$9 ~ /^[45]/' /var/log/nginx/access.log

# Find specific IP across all logs
grep -r "192.168.1.100" /var/log/

# Find SQL injection patterns
grep -iE "(union.*select|insert.*into|delete.*from|drop.*table)" /var/log/nginx/access.log

# Find path traversal attempts
grep -E "(\.\./|\.\.\\|%2e%2e)" /var/log/nginx/access.log
```

### Anomaly Detection

```bash
# Find top 10 source IPs by request count
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Find requests with unusually large response sizes
awk '$10 > 1000000 {print $0}' /var/log/nginx/access.log

# Find requests outside business hours (before 6am or after 10pm)
awk -F'[: ]' '$2 < 6 || $2 > 22 {print $0}' /var/log/nginx/access.log

# Find user agents with high request counts (potential bots)
awk -F'"' '{print $6}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Find failed login attempts by source IP
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -10
```

### Timeline Correlation

```bash
# Extract timestamps and events from multiple logs
grep "2024-01-15" /var/log/auth.log /var/log/syslog /var/log/nginx/access.log | \
  awk '{print $1, $2, $3, $0}' | sort -k1,1M -k2,2n -k3,3

# Correlate events by time window (events within 5 minutes)
# Use log2timeline/plaso for automated timeline generation
log2timeline.py --storage_file timeline.plaso /var/log/
psort.py timeline.plaso -o l2tcsv -w timeline.csv
```

## Common Attack Patterns in Logs

### Brute Force Attacks

**Indicators:**
- High volume of failed login attempts from single IP
- Sequential username attempts (admin, administrator, root, etc.)
- Short time between attempts
- Multiple protocols targeted (SSH, RDP, FTP, web login)

**Detection:**
```bash
# Count failed SSH attempts per IP in last hour
grep "Failed password" /var/log/auth.log | \
  awk '{print $11}' | sort | uniq -c | sort -rn | head -20

# Find IPs with >50 failed attempts
grep "Failed password" /var/log/auth.log | \
  awk '{print $11}' | sort | uniq -c | awk '$1 > 50 {print $2}'
```

### Privilege Escalation

**Indicators:**
- Sudo usage by non-admin users
- SUID binary execution
- Kernel exploit attempts
- Service account misuse

**Detection:**
```bash
# Find sudo commands by non-standard users
grep "sudo:" /var/log/auth.log | grep -v "root" | grep -v "admin"

# Find SUID binary execution
grep -E "setuid|setgid" /var/log/audit/audit.log

# Find kernel errors (possible exploit attempts)
grep -i "segfault\|kernel BUG\|general protection fault" /var/log/syslog
```

### Lateral Movement

**Indicators:**
- Internal IP scanning (multiple ports, multiple hosts)
- SMB/RDP/WinRM connections between internal hosts
- Pass-the-hash indicators (NTLM authentication without Kerberos)
- Unusual service creation

**Detection:**
```bash
# Find internal port scans (many connections to different ports from one IP)
awk '{print $1, $4}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Find SMB connections between internal hosts
grep -E "smbd|samba" /var/log/syslog | grep -v "localhost"

# Find RDP connections
grep -E "rdp|remote desktop|xrdp" /var/log/auth.log
```

### Data Exfiltration

**Indicators:**
- Large outbound data transfers
- Unusual DNS queries (DNS tunneling)
- Compressed archive creation followed by outbound transfer
- Connections to known C2 domains/IPs

**Detection:**
```bash
# Find large outbound transfers
awk '$10 > 10000000 {print $0}' /var/log/nginx/access.log

# Find DNS queries to suspicious domains
grep -E "dns|named" /var/log/syslog | grep -v "localhost"

# Find archive creation
grep -E "tar|zip|7z|rar" /var/log/auth.log
```

## Tools

### Splunk

```bash
# Search for failed logons
index=windows EventCode=4625 | stats count by src_ip, user

# Find privilege escalation
index=linux "sudo:" | stats count by user, command

# Detect brute force
index=linux "Failed password" | bin _time span=5m | 
  stats count by src_ip, _time | where count > 20

# Timeline of events
index=* | timechart span=1h count by sourcetype
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Logstash configuration for nginx logs
input {
  file {
    path => "/var/log/nginx/access.log"
    start_position => "beginning"
  }
}
filter {
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  }
}
output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "nginx-%{+YYYY.MM.dd}"
  }
}
```

### Graylog

```bash
# Search for failed SSH attempts
message:"Failed password" AND _exists_:source_ip

# Extract fields from syslog
# Use extractors to parse key-value pairs

# Create streams for different log types
# Stream: "Authentication Logs" — condition: facility: auth
# Stream: "Web Server Logs" — condition: source: webserver*
```

### grep/awk/sed

```bash
# Extract specific time range
sed -n '/2024-01-15 10:00/,/2024-01-15 11:00/p' /var/log/auth.log

# Count events per hour
awk -F'[: ]' '{print $1, $2}' /var/log/auth.log | sort | uniq -c

# Extract unique IPs
awk '{print $1}' /var/log/nginx/access.log | sort -u

# Find events matching multiple patterns
grep -E "(error|fail|critical|alert)" /var/log/syslog

# Remove sensitive data (PII redaction)
sed -E 's/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}/XXXX-XXXX-XXXX-XXXX/g' /var/log/application.log
```

## Log Retention and Preservation

### Retention Policy

| Log Type | Minimum Retention | Recommended Retention |
|----------|-------------------|----------------------|
| Authentication logs | 90 days | 1 year |
| Web server logs | 30 days | 90 days |
| System logs | 30 days | 1 year |
| Security logs | 1 year | 3 years |
| Network logs | 30 days | 90 days |
| Application logs | 90 days | 1 year |

### Preservation Procedures

```bash
# Create read-only archive of logs
tar -czf /evidence/logs-2024-01-15.tar.gz /var/log/
chmod 444 /evidence/logs-2024-01-15.tar.gz

# Generate hash for integrity verification
sha256sum /evidence/logs-2024-01-15.tar.gz > /evidence/logs-2024-01-15.tar.gz.sha256

# Copy to write-once media
cp /evidence/logs-2024-01-15.tar.gz /mnt/worm-media/

# Verify integrity
sha256sum -c /evidence/logs-2024-01-15.tar.gz.sha256
```

## Chain of Custody for Log Evidence

### Documentation Requirements

For each log file collected, document:

1. **Evidence ID** — Unique identifier (e.g., LOG-2024-0115-001)
2. **Source system** — Hostname, IP, OS version
3. **Log type** — syslog, auth.log, nginx access.log, etc.
4. **Time range** — First and last timestamp in the log
5. **Collection method** — How the log was collected (scp, rsync, disk image)
6. **Collection timestamp** — When the log was collected
7. **Collector identity** — Who collected the log
8. **Hash value** — SHA-256 hash of the collected file
9. **Storage location** — Where the evidence is stored
10. **Access log** — Who accessed the evidence, when, why

### Chain of Custody Form

```
Evidence ID: LOG-2024-0115-001
Description: Authentication logs from webserver01
Source: webserver01 (10.0.0.5) — Ubuntu 22.04
File: /var/log/auth.log
Time Range: 2024-01-01 00:00:00 to 2024-01-15 23:59:59
Collected: 2024-01-16 09:30:00 UTC
Collector: J. Smith
Method: SCP from live system
SHA-256: a1b2c3d4e5f6...
Storage: /evidence/case-2024-0115/

Access Log:
| Timestamp | Person | Action | Reason |
|-----------|--------|--------|--------|
| 2024-01-16 09:30 | J. Smith | Collection | Initial evidence collection |
| 2024-01-16 10:15 | A. Jones | Analysis | Brute force investigation |
| 2024-01-16 14:00 | A. Jones | Copy | Working copy for analysis |
```

## Timeline Reconstruction from Logs

### Step-by-Step Process

1. **Collect all relevant logs** — Gather logs from all systems in scope
2. **Normalize timestamps** — Convert all timestamps to UTC
3. **Sort chronologically** — Merge all logs into a single timeline
4. **Identify key events** — Mark significant events (logins, file access, errors)
5. **Correlate across sources** — Link related events across different log types
6. **Identify gaps** — Look for periods with no logging (possible log tampering)
7. **Document findings** — Create timeline with evidence references

### Example Timeline

```
2024-01-15 02:13:45 UTC — SSH login failed for user "admin" from 203.0.113.50
  Source: /var/log/auth.log on webserver01
  Event: Failed password for admin from 203.0.113.50

2024-01-15 02:13:47 UTC — SSH login failed for user "root" from 203.0.113.50
  Source: /var/log/auth.log on webserver01
  Event: Failed password for root from 203.0.113.50

2024-01-15 02:14:02 UTC — SSH login successful for user "deploy" from 203.0.113.50
  Source: /var/log/auth.log on webserver01
  Event: Accepted publickey for deploy from 203.0.113.50

2024-01-15 02:14:15 UTC — Sudo command executed by deploy
  Source: /var/log/auth.log on webserver01
  Event: deploy : TTY=pts/0 ; PWD=/home/deploy ; COMMAND=/bin/bash

2024-01-15 02:15:00 UTC — Web request to /admin from 203.0.113.50
  Source: /var/log/nginx/access.log on webserver01
  Event: GET /admin 200

2024-01-15 02:15:30 UTC — Database query executed
  Source: /var/log/postgresql/postgresql.log on dbserver01
  Event: SELECT * FROM users WHERE id=1

2024-01-15 02:16:00 UTC — Large file download
  Source: /var/log/nginx/access.log on webserver01
  Event: GET /export/users.csv 200 (size: 50MB)
```

### Automated Timeline Generation

```bash
# Using log2timeline/plaso
log2timeline.py --storage_file /evidence/timeline.plaso /evidence/logs/
psort.py /evidence/timeline.plaso -o l2tcsv -w /evidence/timeline.csv

# Using Timesketch (for collaborative analysis)
timesketch_importer.py /evidence/timeline.csv

# Using ELK for timeline visualization
# In Kibana: Discover → Select index → Time range → Visualize
```
