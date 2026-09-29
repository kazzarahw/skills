# Common Port/Service Reference

> **Priority**: High | **Skill**: cyber-recon | **Last Updated**: 2026-09-28

A comprehensive mapping of ports to services, default credentials, and common vulnerabilities for reconnaissance operations.

---

## Quick Reference Table

| Port | Service | Protocol | Default Credentials | Common Vulns | Scan Priority |
|------|---------|----------|---------------------|--------------|---------------|
| 21 | FTP | TCP | anonymous:anonymous, admin:admin | CVE-2011-2523 (VSFTPd), CVE-2015-3300 (ProFTPD) | High |
| 22 | SSH | TCP | root: (none default) | CVE-2018-15473 (OpenSSH enum), CVE-2020-15778 (scp RCE) | High |
| 23 | Telnet | TCP | admin:admin, root:root | Cleartext auth, CVE-2020-10188 (Telnetd) | High |
| 25 | SMTP | TCP | (none) | CVE-2014-3566 (POODLE), Open relay abuse | Medium |
| 53 | DNS | TCP/UDP | (none) | CVE-2015-7547 (Ghost), Zone transfer (AXFR) | High |
| 67/68 | DHCP | UDP | (none) | CVE-2011-0997 (DHCP starvation) | Low |
| 80 | HTTP | TCP | admin:admin (various) | CVE-2017-5638 (Struts2), CVE-2021-41773 (Path traversal) | High |
| 110 | POP3 | TCP | (user accounts) | Cleartext auth, CVE-2014-3566 (POODLE) | Medium |
| 111 | RPCbind | TCP | (none) | CVE-2017-8779 (RPC DDoS) | Medium |
| 135 | MSRPC | TCP | (none) | CVE-2003-0352 (Blaster), CVE-2019-0708 (BlueKeep) | High |
| 139 | NetBIOS | TCP | (none) | CVE-2017-0144 (EternalBlue), CVE-2003-0352 | High |
| 143 | IMAP | TCP | (user accounts) | Cleartext auth, CVE-2014-3566 (POODLE) | Medium |
| 161 | SNMP | UDP | public, private | CVE-2016-3411 (SNMP RCE), Community string brute | High |
| 389 | LDAP | TCP | (none) | CVE-2017-9287 (LDAP injection), Anonymous bind | Medium |
| 443 | HTTPS | TCP | admin:admin (various) | CVE-2014-0160 (Heartbleed), CVE-2021-44228 (Log4Shell) | High |
| 445 | SMB | TCP | (none) | CVE-2017-0144 (EternalBlue), CVE-2020-0796 (SMBGhost) | High |
| 465 | SMTPS | TCP | (user accounts) | CVE-2014-3566 (POODLE) | Medium |
| 514 | Syslog | UDP | (none) | CVE-2015-0235 (Syslog injection) | Low |
| 587 | SMTP Submission | TCP | (user accounts) | CVE-2014-3566 (POODLE) | Medium |
| 636 | LDAPS | TCP | (none) | CVE-2017-9287 (LDAP injection) | Medium |
| 993 | IMAPS | TCP | (user accounts) | CVE-2014-3566 (POODLE) | Medium |
| 995 | POP3S | TCP | (user accounts) | CVE-2014-3566 (POODLE) | Medium |
| 1080 | SOCKS Proxy | TCP | (none) | Open proxy abuse, CVE-2019-0808 | Medium |
| 1433 | MSSQL | TCP | sa:sa, sa:(empty) | CVE-2002-0649 (Slammer), xp_cmdshell abuse | High |
| 1521 | Oracle DB | TCP | system:manager, scott:tiger | CVE-2012-1675 (TNS Poison), CVE-2021-35587 | High |
| 2049 | NFS | TCP | (none) | CVE-2019-16884 (NFS root squash bypass) | Medium |
| 2181 | ZooKeeper | TCP | (none) | CVE-2019-0107 (ZooKeeper unauth) | Medium |
| 2375 | Docker API | TCP | (none) | CVE-2019-5736 (runc escape), Unauth API access | High |
| 2376 | Docker TLS | TCP | (none) | CVE-2019-5736 (runc escape) | High |
| 3000 | Dev Server | TCP | (none) | Debug mode exposure, CVE-2021-41267 | Medium |
| 3306 | MySQL | TCP | root:(empty), root:root | CVE-2012-2122 (auth bypass), CVE-2016-6662 | High |
| 3389 | RDP | TCP | (domain users) | CVE-2019-0708 (BlueKeep), CVE-2019-1181/1182 | High |
| 5000 | UPnP/Flask | TCP | (none) | CVE-2020-12695 (CallStranger), Debug mode | Medium |
| 5001 | Dev Server | TCP | (none) | Debug mode exposure | Medium |
| 5432 | PostgreSQL | TCP | postgres:postgres, postgres:(empty) | CVE-2019-10164 (RCE), CVE-2021-3677 | High |
| 5601 | Kibana | TCP | (none) | CVE-2019-7609 (Kibana RCE), Unauth access | High |
| 5900 | VNC | TCP | (none default) | CVE-2019-15681 (VNC auth bypass), Cleartext | High |
| 5984 | CouchDB | TCP | admin:admin | CVE-2017-12635/12636 (Erlang RCE) | High |
| 5985 | WinRM HTTP | TCP | (domain users) | CVE-2019-0708 (BlueKeep), Pass-the-hash | High |
| 5986 | WinRM HTTPS | TCP | (domain users) | CVE-2019-0708 (BlueKeep) | High |
| 6379 | Redis | TCP | (none default) | CVE-2022-0543 (Redis Lua RCE), Unauth access | High |
| 7001 | WebLogic | TCP | weblogic:weblogic, weblogic:Oracle@123 | CVE-2017-10271 (WLS RCE), CVE-2020-14882 | High |
| 8000 | HTTP Alt | TCP | (varies) | CVE-2021-41773 (Path traversal) | Medium |
| 8008 | HTTP Alt | TCP | (varies) | CVE-2021-41773 (Path traversal) | Medium |
| 8080 | HTTP Proxy | TCP | admin:admin, admin:password | CVE-2017-5638 (Struts2), CVE-2021-44228 (Log4Shell) | High |
| 8081 | HTTP Alt | TCP | admin:admin | CVE-2021-44228 (Log4Shell) | Medium |
| 8088 | HTTP Alt | TCP | (varies) | CVE-2021-44228 (Log4Shell) | Medium |
| 8161 | ActiveMQ | TCP | admin:admin | CVE-2015-5254 (Java deserialization), CVE-2023-46604 | High |
| 8443 | HTTPS Alt | TCP | admin:admin | CVE-2014-0160 (Heartbleed), CVE-2021-44228 | High |
| 8888 | HTTP Alt | TCP | (varies) | CVE-2021-41773 (Path traversal) | Medium |
| 9000 | PHP-FPM | TCP | (none) | CVE-2019-11043 (PHP-FPM RCE) | High |
| 9001 | Tor ORPort | TCP | (none) | CVE-2020-10188 (Telnetd) | Low |
| 9042 | Cassandra | TCP | cassandra:cassandra | CVE-2020-13946 (Cassandra RCE) | High |
| 9090 | Prometheus | TCP | (none) | CVE-2021-27482 (Prometheus RCE), Unauth access | High |
| 9092 | Kafka | TCP | (none) | CVE-2023-25152 (Kafka RCE) | Medium |
| 9200 | Elasticsearch | TCP | (none) | CVE-2015-1427 (RCE), CVE-2014-3120 (RCE) | High |
| 9300 | Elasticsearch Node | TCP | (none) | CVE-2015-1427 (RCE) | Medium |
| 11211 | Memcached | TCP | (none) | CVE-2020-10188 (Telentd), Amplification DDoS | Medium |
| 15672 | RabbitMQ Mgmt | TCP | guest:guest | CVE-2023-34095 (RabbitMQ RCE), Unauth access | High |
| 27017 | MongoDB | TCP | (none default) | CVE-2019-2386 (MongoDB RCE), Unauth access | High |
| 27018 | MongoDB Shard | TCP | (none) | CVE-2019-2386 (MongoDB RCE) | Medium |
| 50000 | SAP Management | TCP | (varies) | CVE-2020-6287 (SAP RECON), CVE-2020-6207 | High |
| 50070 | Hadoop NameNode | TCP | (none) | CVE-2018-3279 (Hadoop RCE), Unauth access | High |
| 50075 | Hadoop DataNode | TCP | (none) | CVE-2018-3279 (Hadoop RCE) | Medium |
| 50090 | Hadoop JobTracker | TCP | (none) | CVE-2018-3279 (Hadoop RCE) | Medium |
| 61616 | ActiveMQ OpenWire | TCP | admin:admin | CVE-2015-5254 (Java deserialization) | High |

---

## Detailed Service Profiles

### FTP (Port 21)

**Protocol**: TCP
**Common Versions**: vsftpd 2.3.4, ProFTPD 1.3.5, FileZilla Server, Pure-FTPd
**Default Credentials**:
- `anonymous:anonymous` (read-only)
- `ftp:ftp`
- `admin:admin` (some embedded systems)

**Common Vulnerabilities**:
- CVE-2011-2523: vsftpd 2.3.4 backdoor command execution
- CVE-2015-3300: ProFTPD mod_copy RCE
- CVE-2020-9273: ProFTPD SQL injection
- Anonymous write access leading to webshell upload
- Cleartext credential transmission

**Recon Commands**:
```bash
# Banner grabbing
nc -vn <target> 21

# Anonymous login test
ftp <target>
# Login: anonymous / anonymous

# Nmap scripts
nmap -p 21 --script ftp-anon,ftp-bounce,ftp-libopie,ftp-proftpd-backdoor,ftp-vsftpd-backdoor <target>
```

---

### SSH (Port 22)

**Protocol**: TCP
**Common Versions**: OpenSSH 7.x-9.x, Dropbear, libssh
**Default Credentials**: None (key-based or password auth)

**Common Vulnerabilities**:
- CVE-2018-15473: OpenSSH user enumeration
- CVE-2020-15778: OpenSSH scp RCE
- CVE-2023-38408: OpenSSH agent forwarding RCE
- CVE-2024-6387: OpenSSH regreSSHion RCE
- Weak ciphers (CBC mode, RC4)
- Password authentication with weak credentials

**Recon Commands**:
```bash
# Version detection
nc -vn <target> 22

# Algorithm enumeration
nmap -p 22 --script ssh2-enum-algos <target>

# User enumeration
nmap -p 22 --script ssh-user-enum <target>

# Weak algorithms
nmap -p 22 --script ssh-audit <target>
```

---

### SMB (Port 445)

**Protocol**: TCP
**Common Versions**: SMBv1, SMBv2, SMBv3
**Default Credentials**: None (domain/NTLM auth)

**Common Vulnerabilities**:
- CVE-2017-0144: EternalBlue (WannaCry)
- CVE-2020-0796: SMBGhost
- CVE-2019-0708: BlueKeep (RDP but related)
- CVE-2003-0352: Blaster
- Null session enumeration
- SMB signing disabled

**Recon Commands**:
```bash
# SMB version detection
nmap -p 445 --script smb-protocols <target>

# SMB security mode
nmap -p 445 --script smb-security-mode <target>

# SMB shares enumeration
nmap -p 445 --script smb-enum-shares <target>

# SMB OS discovery
nmap -p 445 --script smb-os-discovery <target>

# EternalBlue check
nmap -p 445 --script smb-vuln-ms17-010 <target>
```

---

### HTTP/HTTPS (Ports 80, 443, 8080, 8443)

**Protocol**: TCP
**Common Versions**: Apache 2.4.x, Nginx 1.x, IIS 10.x, Node.js, Tomcat
**Default Credentials**:
- `admin:admin` (Tomcat manager)
- `admin:password` (various web apps)
- `tomcat:s3cret` (Tomcat)

**Common Vulnerabilities**:
- CVE-2021-44228: Log4Shell
- CVE-2017-5638: Apache Struts2 RCE
- CVE-2021-41773: Path traversal
- CVE-2014-0160: Heartbleed
- CVE-2019-0107: Kibana RCE
- Directory listing enabled
- Debug mode enabled
- Default credentials on admin panels

**Recon Commands**:
```bash
# HTTP enumeration
nmap -p 80,443 --script http-enum <target>

# HTTP methods
nmap -p 80,443 --script http-methods <target>

# SSL/TLS enumeration
nmap -p 443 --script ssl-enum-ciphers <target>

# Heartbleed check
nmap -p 443 --script ssl-heartbleed <target>

# Web tech detection
whatweb http://<target>
```

---

### RDP (Port 3389)

**Protocol**: TCP
**Common Versions**: RDP 8.0, 8.1, 10.0
**Default Credentials**: None (domain/NTLM auth)

**Common Vulnerabilities**:
- CVE-2019-0708: BlueKeep
- CVE-2019-1181/1182: DejaBlue
- CVE-2022-22013: Windows RDP RCE
- NLA disabled (allows pre-auth attacks)
- Weak TLS ciphers

**Recon Commands**:
```bash
# RDP security layer
nmap -p 3389 --script rdp-enum-encryption <target>

# BlueKeep check
nmap -p 3389 --script rdp-vuln-ms12-020 <target>

# NLA check
nmap -p 3389 --script rdp-ntlm-info <target>
```

---

### Database Services

#### MySQL (Port 3306)
**Default Credentials**: `root:(empty)`, `root:root`, `root:password`
**Common Vulns**: CVE-2012-2122 (auth bypass), CVE-2016-6662 (RCE), UDF exploitation

#### PostgreSQL (Port 5432)
**Default Credentials**: `postgres:postgres`, `postgres:(empty)`
**Common Vulns**: CVE-2019-10164 (RCE), CVE-2021-3677 (RCE), COPY TO/FROM PROGRAM

#### MSSQL (Port 1433)
**Default Credentials**: `sa:sa`, `sa:(empty)`
**Common Vulns**: CVE-2002-0649 (Slammer), xp_cmdshell, CVE-2019-1068 (RCE)

#### MongoDB (Port 27017)
**Default Credentials**: None (no auth by default)
**Common Vulns**: CVE-2019-2386 (RCE), Unauth access, CVE-2021-20333 (RCE)

#### Redis (Port 6379)
**Default Credentials**: None (no auth by default)
**Common Vulns**: CVE-2022-0543 (Lua RCE), Unauth access, Master-slave RCE

---

### Container/Orchestration

#### Docker API (Port 2375)
**Default Credentials**: None
**Common Vulns**: CVE-2019-5736 (runc escape), Unauth API access, Container escape

#### Kubernetes API (Port 6443/8443)
**Default Credentials**: None (cert-based)
**Common Vulns**: CVE-2018-1002105 (API server proxy), Unauth dashboard, etcd unauth

---

## Scan Priority Methodology

### High Priority (Scan First)
- Ports with known critical RCE vulnerabilities
- Ports with default credentials
- Ports with unauthenticated access
- Internet-facing management interfaces

**Ports**: 21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 443, 445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 7001, 8080, 8161, 8443, 9000, 9042, 9090, 9200, 15672, 27017, 50000, 50070

### Medium Priority (Scan Second)
- Ports with information disclosure
- Ports with authentication bypass potential
- Internal service ports

**Ports**: 67/68, 111, 389, 465, 514, 587, 636, 1080, 2049, 2181, 2375, 2376, 3000, 5000, 5001, 5601, 5984, 5985, 5986, 8000, 8008, 8081, 8088, 8888, 9001, 9092, 9300, 11211, 27018, 50075, 50090, 61616

### Low Priority (Scan Last)
- Ports with limited attack surface
- UDP-only services
- Legacy/rarely used services

**Ports**: 514, 9001, 61616

---

## Default Credentials Reference

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| FTP | anonymous | anonymous | Read-only access |
| FTP | ftp | ftp | Common default |
| Telnet | admin | admin | Common default |
| Telnet | root | root | Common default |
| SSH | root | (none) | Key-based auth |
| MySQL | root | (empty) | Common default |
| MySQL | root | root | Common default |
| PostgreSQL | postgres | postgres | Common default |
| MSSQL | sa | sa | Common default |
| MSSQL | sa | (empty) | Common default |
| Oracle | system | manager | Common default |
| Oracle | scott | tiger | Common default |
| Redis | (none) | (none) | No auth by default |
| MongoDB | (none) | (none) | No auth by default |
| Docker | (none) | (none) | No auth by default |
| RabbitMQ | guest | guest | Default guest |
| ActiveMQ | admin | admin | Default admin |
| Tomcat | admin | admin | Manager app |
| Tomcat | tomcat | s3cret | Manager app |
| Kibana | (none) | (none) | No auth by default |
| Elasticsearch | (none) | (none) | No auth by default |
| Jenkins | admin | admin | Default admin |
| GitLab | root | 5iveL!fe | Default root |
| WordPress | admin | admin | Default admin |
| Joomla | admin | admin | Default admin |
| Drupal | admin | admin | Default admin |
| phpMyAdmin | root | (empty) | MySQL root |
| VNC | (none) | (none) | No auth by default |
| SNMP | public | private | Community strings |
| SNMP | public | public | Community strings |
| SNMP | private | private | Community strings |

---

## Vulnerability Severity Classification

### Critical (CVSS 9.0-10.0)
- Remote code execution without authentication
- Wormable vulnerabilities
- Default credential access to sensitive services

**Examples**: EternalBlue, Log4Shell, Heartbleed, BlueKeep

### High (CVSS 7.0-8.9)
- Remote code execution with authentication
- SQL injection
- Authentication bypass
- Privilege escalation

**Examples**: Struts2 RCE, PHP-FPM RCE, SMBGhost

### Medium (CVSS 4.0-6.9)
- Information disclosure
- Cross-site scripting
- CSRF
- Directory traversal

**Examples**: Directory listing, HTTP methods, SSL/TLS issues

### Low (CVSS 0.1-3.9)
- Information disclosure (minor)
- Configuration issues
- Missing security headers

**Examples**: Server banner disclosure, missing CSP

---

## Usage in Reconnaissance Workflow

1. **Port Scan**: Use nmap/masscan to identify open ports
2. **Service Detection**: Use nmap `-sV` to identify service versions
3. **Reference Lookup**: Cross-reference open ports with this document
4. **Vulnerability Mapping**: Identify potential CVEs based on service/version
5. **Credential Testing**: Test default credentials where applicable
6. **Exploitation Planning**: Prioritize based on scan priority and vulnerability severity

---

## References

- [NIST National Vulnerability Database](https://nvd.nist.gov/)
- [CVE Details](https://www.cvedetails.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SANS Top 25](https://www.sans.org/top25-software-errors/)
- [Common Weakness Enumeration](https://cwe.mitre.org/)
