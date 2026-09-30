# Web2 OSINT Techniques

Comprehensive Open Source Intelligence collection guide. Covers domain enumeration, email harvesting, social media recon, search engine dorks, document metadata, historical data, cloud asset discovery, code repository analysis, and breach data.

**Scope:** this file covers target-exposure execution (what is exposed, where). Identity and attribution procedure (who owns what, verification standards, OPSEC) is canonical in `osint/references/` — defer to it, don't duplicate it.

## Table of Contents

- [Domain Enumeration](#domain-enumeration)
- [Email Harvesting](#email-harvesting)
- [Social Media Recon](#social-media-recon)
- [Search Engine Dorks](#search-engine-dorks)
- [Document Metadata Extraction](#document-metadata-extraction)
- [Historical Data](#historical-data)
- [Cloud Asset Discovery](#cloud-asset-discovery)
- [Code Repository Analysis](#code-repository-analysis)
- [Breach Data](#breach-data)
- [Reporting & Attribution](#reporting--attribution)

---

## Domain Enumeration

### WHOIS

```bash
# WHOIS lookup
whois example.com

# WHOIS with specific server
whois -h whois.verisign-grs.com example.com

# WHOIS for IP
whois 10.0.0.1

# WHOIS JSON output
whois -h whois.verisign-grs.com example.com --json
```

**Information gathered:** Registrar, creation date, expiration date, name servers, registrant contact (often redacted), status codes.

### DNS Records

```bash
# All records
dig example.com ANY +noall +answer

# Specific records
dig example.com A +noall +answer
dig example.com AAAA +noall +answer
dig example.com MX +noall +answer
dig example.com TXT +noall +answer
dig example.com NS +noall +answer
dig example.com SOA +noall +answer
dig example.com CNAME +noall +answer
dig example.com SRV +noall +answer
dig example.com CAA +noall +answer

# Reverse DNS
dig -x 10.0.0.1 +noall +answer

# DNSSEC
dig example.com DNSKEY +noall +answer
dig example.com DS +noall +answer
dig example.com RRSIG +noall +answer
```

### Subdomain Enumeration

```bash
# subfinder (passive)
subfinder -d example.com -o subdomains.txt
subfinder -d example.com -all -o subdomains-all.txt

# amass (comprehensive)
amass enum -d example.com -o amass-subdomains.txt
amass enum -passive -d example.com -o amass-passive.txt
amass enum -active -d example.com -o amass-active.txt

# crt.sh (certificate transparency)
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u > crtsh-subdomains.txt

# dnsrecon
dnsrecon -d example.com -t std,brt -j dnsrecon-results.json

# subbrute
subbrute example.com -o subbrute-results.txt

# Combine all sources
cat subdomains.txt amass-subdomains.txt crtsh-subdomains.txt | sort -u > all-subdomains.txt
```

### Reverse DNS Lookup

```bash
# Reverse DNS for IP range
for ip in $(seq 1 254); do dig -x 10.0.0.$ip +short; done

# Using dnsrecon
dnsrecon -r 10.0.0.0/24 -n 10.0.0.1

# Using nmap
nmap -sL 10.0.0.0/24
```

---

## Email Harvesting

### theHarvester

```bash
# All sources
theHarvester -d example.com -b all -f results.html

# Specific sources
theHarvester -d example.com -b google,linkedin,bing,hunter

# Limit results
theHarvester -d example.com -b all -l 500

# With Shodan
theHarvester -d example.com -b shodan
```

### Hunter.io

```bash
# Web interface
https://hunter.io/search/example.com

# API
curl -s "https://api.hunter.io/v2/domain-search?domain=example.com&api_key=$HUNTER_API_KEY" | jq .
```

**Information gathered:** Email addresses, patterns, sources, department filters.

### Email Pattern Identification

```bash
# Common patterns
first.last@example.com
firstinitiallastname@example.com
firstname@example.com
lastname@example.com

# Verify with Hunter.io
curl -s "https://api.hunter.io/v2/email-finder?domain=example.com&first_name=John&last_name=Doe&api_key=$HUNTER_API_KEY" | jq .
```

### Email Verification

```bash
# Verify email exists
curl -s "https://api.hunter.io/v2/email-verifier?email=john@example.com&api_key=$HUNTER_API_KEY" | jq .

# Check MX records
dig example.com MX +noall +answer

# SMTP verification (manual)
nc -nv mail.example.com 25
VRFY john@example.com
```

---

## Social Media Recon

### LinkedIn

```bash
# Search for employees
https://www.linkedin.com/search/results/people/?keywords=example.com

# Company page
https://www.linkedin.com/company/example

# Employee profiles (manual)
# Look for: name, title, email pattern, skills, connections
```

**Information gathered:** Employee names, titles, email patterns, tech stack, connections, company size.

### GitHub

```bash
# Search for organization
https://github.com/example

# Search for code
https://github.com/search?q=example.com&type=code

# Search for repositories
https://github.com/search?q=example.com&type=repositories

# Search for issues
https://github.com/search?q=example.com&type=issues

# Search for users
https://github.com/search?q=example.com&type=users

# GitHub API
curl -s "https://api.github.com/orgs/example" | jq .
curl -s "https://api.github.com/orgs/example/repos" | jq .
curl -s "https://api.github.com/search/code?q=example.com" | jq .
```

**Information gathered:** Source code, employee names, email addresses, tech stack, API keys, internal hostnames.

### Twitter/X

```bash
# Search for mentions
https://twitter.com/search?q=example.com

# Search for employees
https://twitter.com/search?q=example.com%20developer

# Advanced search
https://twitter.com/search-advanced
```

**Information gathered:** Employee handles, tech stack mentions, breach disclosures, internal discussions.

### Additional Sources

```bash
# Reddit
https://www.reddit.com/search/?q=example.com

# Stack Overflow
https://stackoverflow.com/search?q=example.com

# Pastebin
https://pastebin.com/search?q=example.com

# GitHub Gist
https://gist.github.com/search?q=example.com
```

---

## Search Engine Dorks

### Google Dorks

```
# File types
site:example.com filetype:pdf
site:example.com filetype:doc
site:example.com filetype:docx
site:example.com filetype:xls
site:example.com filetype:xlsx
site:example.com filetype:ppt
site:example.com filetype:pptx
site:example.com filetype:sql
site:example.com filetype:log
site:example.com filetype:env
site:example.com filetype:config
site:example.com filetype:xml
site:example.com filetype:json
site:example.com filetype:txt
site:example.com filetype:csv
site:example.com filetype:backup
site:example.com filetype:bak
site:example.com filetype:old
site:example.com filetype:tmp

# Directory listing
site:example.com intitle:"index of"
site:example.com intitle:"index of /admin"
site:example.com intitle:"index of /backup"

# Sensitive paths
site:example.com inurl:admin
site:example.com inurl:backup
site:example.com inurl:api
site:example.com inurl:swagger
site:example.com inurl:.git
site:example.com inurl:.env
site:example.com inurl:config
site:example.com inurl:backup
site:example.com inurl:db
site:example.com inurl:sql
site:example.com inurl:log
site:example.com inurl:debug
site:example.com inurl:test
site:example.com inurl:dev
site:example.com inurl:staging

# Credentials
site:example.com "password" filetype:txt
site:example.com "api_key" filetype:env
site:example.com "secret" filetype:env
site:example.com "token" filetype:env

# Error messages
site:example.com "sql syntax"
site:example.com "stack trace"
site:example.com "fatal error"
site:example.com "warning:"
site:exception"

# Vulnerabilities
site:example.com "you have an error in your sql syntax"
site:example.com "unclosed quotation mark"
site:example.com "odbc drivers error"
site:example.com "ora-01756"
site:example.com "microsoft ole db provider for sql server error"

# Login pages
site:example.com inurl:login
site:example.com inurl:signin
site:example.com intitle:"login"
site:example.com intitle:"sign in"

# PDF documents
site:example.com filetype:pdf "confidential"
site:example.com filetype:pdf "internal"
site:example.com filetype:pdf "restricted"

# Database dumps
site:example.com filetype:sql "insert into"
site:example.com filetype:sql "create table"

# Configuration files
site:example.com filetype:env "DB_PASSWORD"
site:example.com filetype:env "API_KEY"
site:example.com filetype:env "SECRET_KEY"

# Backup files
site:example.com filetype:bak
site:example.com filetype:old
site:example.com filetype:backup
site:example.com inurl:backup
```

### Bing Dorks

```
# Similar to Google but different indexing
site:example.com filetype:pdf
site:example.com inurl:admin
site:example.com intitle:"index of"

# Bing-specific
site:example.com "password" filetype:txt
site:example.com "api_key" filetype:env
```

### Shodan Dorks

```
# Domain search
hostname:example.com

# IP search
net:10.0.0.0/24

# Port search
port:22,80,443,8080

# Product search
product:"Apache httpd"

# Version search
product:"Apache httpd" version:"2.4.49"

# Vulnerability search
vuln:CVE-2021-44228

# SSL search
ssl:"example.com"

# Combined
hostname:example.com port:8080
hostname:example.com product:"nginx"
```

### Censys Dorks

```
# Domain search
services.tls.certificates.leaf_data.names: example.com

# IP search
ip: 10.0.0.0/24

# Port search
services.port: 8080

# Product search
services.software.product: "Apache httpd"

# Combined
services.tls.certificates.leaf_data.names: example.com and services.port: 443
```

---

## Document Metadata Extraction

### exiftool

```bash
# Extract metadata from document
exiftool document.pdf

# Extract all metadata
exiftool -a -u document.pdf

# Extract specific fields
exiftool -Author -Creator -Producer document.pdf

# Batch extraction
exiftool -r -csv documents/ > metadata.csv

# Extract from URL
curl -s https://example.com/document.pdf | exiftool -
```

**Information gathered:** Author, creator, producer, creation date, modification date, software used, email addresses, internal paths.

### FOCA (Fingerprinting Organizations with Collected Archives)

```bash
# FOCA is a Windows tool for metadata extraction
# Download from: https://github.com/ElevenPaths/FOCA

# Extract metadata from documents
foca.exe -d example.com -s all
```

### Metagoofil

```bash
# Extract metadata from public documents
metagoofil -d example.com -t doc,pdf,xls,ppt,docx,xlsx,pptx -l 200 -n 50 -o files/ -f results.html
```

---

## Historical Data

### Wayback Machine

```bash
# Web interface
https://web.archive.org/web/*/example.com

# API
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com&output=json&limit=100" | jq .

# Get all snapshots
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com&output=json&limit=10000" | jq -r '.[].timestamp' | sort -u

# Get specific snapshot
curl -s "https://web.archive.org/web/20200101000000*/example.com"

# Download snapshot
curl -s "https://web.archive.org/web/20200101000000/https://example.com" > snapshot.html

# Search for specific paths
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com*&output=json&limit=1000" | jq .
```

**Information gathered:** Historical endpoints, deleted pages, old versions, exposed files, technology changes.

### Archive.today

```bash
# Web interface
https://archive.ph/newest/https://example.com

# Search
https://archive.ph/https://example.com
```

### Common Crawl

```bash
# Search index
https://index.commoncrawl.org/CC-MAIN-2024-10-index?url=example.com&output=json

# API
curl -s "https://index.commoncrawl.org/CC-MAIN-2024-10-index?url=example.com&output=json" | jq .
```

---

## Cloud Asset Discovery

### AWS S3 Buckets

```bash
# Search for S3 buckets
s3scanner example.com

# Check bucket permissions
aws s3 ls s3://example.com --no-sign-request

# List objects
aws s3 ls s3://example.com --recursive --no-sign-request

# Check bucket policy
aws s3api get-bucket-policy --bucket example.com --no-sign-request

# Check bucket ACL
aws s3api get-bucket-acl --bucket example.com --no-sign-request

# Search for exposed buckets
s3-buckets-finder example.com
```

### Azure Blob Storage

```bash
# Check blob storage
curl -s "https://example.blob.core.windows.net/?comp=list"

# Check container ACL
curl -s "https://example.blob.core.windows.net/container?restype=container&comp=acl"

# Azure Storage Explorer
# Download from: https://azure.microsoft.com/en-us/products/storage/storage-explorer/
```

### GCP Storage

```bash
# Check bucket
curl -s "https://storage.googleapis.com/example"

# List objects
curl -s "https://storage.googleapis.com/storage/v1/b/example/o"

# Check bucket ACL
curl -s "https://storage.googleapis.com/storage/v1/b/example/iam"

# Search for exposed buckets
gsutil ls gs://example
```

### Cloud Asset Enumeration

```bash
# Cloudenum
cloudenum -k example.com

# S3 bucket finder
s3-buckets-finder example.com

# Azure storage finder
azure-storage-explorer example.com

# GCP bucket finder
gcp-bucket-finder example.com

# Combined cloud enum
cloud-enum example.com
```

---

## Code Repository Analysis

### GitHub

```bash
# Search for organization
curl -s "https://api.github.com/orgs/example" | jq .

# List repositories
curl -s "https://api.github.com/orgs/example/repos?per_page=100" | jq .

# Search code
curl -s "https://api.github.com/search/code?q=example.com" | jq .

# Search commits
curl -s "https://api.github.com/search/commits?q=example.com" | jq .

# Search issues
curl -s "https://api.github.com/search/issues?q=example.com" | jq .

# Search users
curl -s "https://api.github.com/search/users?q=example.com" | jq .

# Get repository contents
curl -s "https://api.github.com/repos/example/repo/contents/" | jq .

# Get commit history
curl -s "https://api.github.com/repos/example/repo/commits" | jq .

# Get branches
curl -s "https://api.github.com/repos/example/repo/branches" | jq .

# Get tags
curl -s "https://api.github.com/repos/example/repo/tags" | jq .
```

### GitLab

```bash
# Search for projects
curl -s "https://gitlab.com/api/v4/projects?search=example" | jq .

# Get project details
curl -s "https://gitlab.com/api/v4/projects/example%2Frepo" | jq .

# Get repository tree
curl -s "https://gitlab.com/api/v4/projects/example%2Frepo/repository/tree" | jq .

# Get commits
curl -s "https://gitlab.com/api/v4/projects/example%2Frepo/repository/commits" | jq .

# Get issues
curl -s "https://gitlab.com/api/v4/projects/example%2Frepo/issues" | jq .

# Get merge requests
curl -s "https://gitlab.com/api/v4/projects/example%2Frepo/merge_requests" | jq .
```

### Code Search Tools

```bash
# GitHub code search
https://github.com/search?q=example.com&type=code

# GitLab code search
https://gitlab.com/search?search=example.com

# Sourcegraph
https://sourcegraph.com/search?q=example.com

# Searchcode
https://searchcode.com/?q=example.com

# PublicWWW
https://publicwww.com/websites/example.com/
```

### Secrets in Code

```bash
# truffleHog
trufflehog git https://github.com/example/repo

# gitleaks
gitleaks detect --source https://github.com/example/repo

# detect-secrets
detect-secrets scan --all-files

# shhgit
shhgit https://github.com/example/repo

# Yelp/detect-secrets
detect-secrets scan --all-files --force-all-plugins
```

---

## Breach Data

### HaveIBeenPwned

```bash
# Check if email is in breach
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/john@example.com" -H "hibp-api-key: $HIBP_API_KEY" | jq .

# Check pastes
curl -s "https://haveibeenpwned.com/api/v3/pasteaccount/john@example.com" -H "hibp-api-key: $HIBP_API_KEY" | jq .

# List all breaches
curl -s "https://haveibeenpwned.com/api/v3/breaches" -H "hibp-api-key: $HIBP_API_KEY" | jq .
```

### DeHashed

```bash
# Search for email
curl -s "https://api.dehashed.com/v2/search?query=john@example.com" -H "Authorization: Bearer $DEHASHED_API_KEY" | jq .

# Search for domain
curl -s "https://api.dehashed.com/v2/search?query=domain:example.com" -H "Authorization: Bearer $DEHASHED_API_KEY" | jq .

# Search for username
curl -s "https://api.dehashed.com/v2/search?query=username:john" -H "Authorization: Bearer $DEHASHED_API_KEY" | jq .
```

### LeakCheck

```bash
# Search for email
curl -s "https://leakcheck.io/api/v2/query/john@example.com" -H "X-API-Key: $LEAKCHECK_API_KEY" | jq .

# Search for domain
curl -s "https://leakcheck.io/api/v2/query/example.com" -H "X-API-Key: $LEAKCHECK_API_KEY" | jq .
```

### Intelligence X

```bash
# Search for email
curl -s "https://intelx.io/search?term=john@example.com" | jq .

# Search for domain
curl -s "https://intelx.io/search?term=example.com" | jq .
```

---

## Reporting & Attribution

### OSINT Report Template

```markdown
# OSINT Report: example.com

**Date:** YYYY-MM-DD
**Analyst:** [Name]
**Scope:** example.com and subdomains

## Executive Summary
- Total subdomains: 50
- Total emails: 25
- Employees identified: 10
- Exposed documents: 5
- Breach exposure: 3 emails found in breaches

## Domain Information
- Registrar: [Registrar]
- Creation date: [Date]
- Expiration date: [Date]
- Name servers: [NS1, NS2]

## Subdomains
| Subdomain | IP | Service | Technology |
|-----------|----|---------|------------|
| www.example.com | 10.0.0.1 | HTTP | nginx |
| api.example.com | 10.0.0.2 | HTTP | Apache |

## Email Addresses
| Email | Source | Breach Exposure |
|-------|--------|-----------------|
| john@example.com | LinkedIn | Found in [Breach] |
| jane@example.com | GitHub | Not found |

## Employees
| Name | Title | LinkedIn | Email |
|------|-------|----------|-------|
| John Doe | Developer | [Link] | john@example.com |

## Exposed Documents
| Document | Type | Metadata | URL |
|----------|------|----------|-----|
| report.pdf | PDF | Author: John Doe | [URL] |

## Cloud Assets
| Asset | Type | Exposure | URL |
|-------|------|----------|-----|
| example.s3.amazonaws.com | S3 Bucket | Public | [URL] |

## Historical Data
| URL | Snapshot Date | Notes |
|-----|---------------|-------|
| /admin | 2020-01-01 | Admin panel exposed |

## Breach Data
| Email | Breach | Date | Compromised Data |
|-------|--------|------|------------------|
| john@example.com | [Breach] | 2021-01-01 | Email, Password |

## Risk Indicators
| Indicator | Severity | Evidence |
|-----------|----------|----------|
| Exposed admin panel | High | /admin accessible without auth |
| Public S3 bucket | Medium | Bucket listing enabled |
| Breached credentials | High | 3 emails found in breaches |
```

### Attribution

```bash
# Domain attribution
whois example.com | grep -i "registrant\|admin\|tech"

# IP attribution
whois 10.0.0.1 | grep -i "orgname\|netname\|descr"

# Email attribution
theHarvester -d example.com -b all | grep "@example.com"

# Social media attribution
# LinkedIn: Search for company page
# Twitter: Search for company handle
# GitHub: Search for organization

# Code repository attribution
curl -s "https://api.github.com/orgs/example" | jq '.name, .blog, .location, .email'
```
