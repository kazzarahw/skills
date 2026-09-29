# OWASP WSTG v4.2 — Information Gathering Test Catalog

Stable IDs for consistent reporting. Maps WSTG tests to tool commands.

## WSTG-INFO-01: Conduct Search Engine Discovery

**Objective:** Identify sensitive information exposed via search engines.

**Tools:** theHarvester, Google dorks

**Commands:**
```bash
theHarvester -d <domain> -b google,bing
```

**Test Cases:**
- `site:<domain> filetype:pdf`
- `site:<domain> filetype:doc,xls,ppt`
- `site:<domain> inurl:admin`
- `site:<domain> intitle:index.of`

**Evidence:** Screenshots of search results, downloaded documents.

---

## WSTG-INFO-02: Fingerprint Web Server

**Objective:** Identify web server software and version.

**Tools:** whatweb, nmap, httpx

**Commands:**
```bash
whatweb -a 1 <url>
nmap -sV -p80,443 <target>
httpx -silent -tech-detect -status-code
```

**Evidence:** HTTP response headers, whatweb output, nmap version detection.

---

## WSTG-INFO-03: Review Webserver Metafiles

**Objective:** Find robots.txt, sitemap.xml, .git/, .svn/, .DS_Store.

**Tools:** gobuster, ffuf, curl

**Commands:**
```bash
curl -s <url>/robots.txt
curl -s <url>/.git/HEAD
curl -s <url>/.svn/entries
gobuster dir -u <url> -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
```

**Evidence:** File contents, HTTP status codes.

---

## WSTG-INFO-04: Enumerate Webserver Applications

**Objective:** Identify applications, platforms, and frameworks.

**Tools:** whatweb, nuclei, wappalyzer

**Commands:**
```bash
whatweb -a 3 <url>
nuclei -t exposure/ -u <url>
```

**Evidence:** whatweb output, nuclei template matches.

---

## WSTG-INFO-05: Review Webpage Content

**Objective:** Find comments, hidden fields, credentials, and sensitive data.

**Tools:** Manual review, grep

**Commands:**
```bash
curl -s <url> | grep -iE "(password|passwd|pwd|secret|token|api[_-]?key)"
curl -s <url> | grep -iE "<!--.*-->"  # HTML comments
```

**Evidence:** Source code snippets, comment blocks.

---

## WSTG-INFO-06: Identify Application Entry Points

**Objective:** Map all application entry points (URLs, parameters, APIs).

**Tools:** gobuster, ffuf, nuclei

**Commands:**
```bash
gobuster dir -u <url> -w <wordlist> -x php,html,js,json
ffuf -u <url>/FUZZ -w <wordlist>
nuclei -t exposure/ -u <url>
```

**Evidence:** Discovered endpoints, parameter lists, API documentation.

---

## WSTG-INFO-07: Map Execution Paths

**Objective:** Trace application workflows and execution paths.

**Tools:** Manual testing, burp suite

**Test Cases:**
- Identify all user-accessible functions
- Map authentication flows
- Document session management
- Trace data flow

**Evidence:** Flow diagrams, request/response pairs.

---

## WSTG-INFO-08: Fingerprint Web Application Framework

**Objective:** Identify underlying frameworks (Rails, Django, Laravel, etc.).

**Tools:** whatweb, nuclei, wappalyzer

**Commands:**
```bash
whatweb -a 3 <url>
nuclei -t exposure/ -u <url>
```

**Evidence:** Framework-specific headers, cookies, error pages.

---

## WSTG-INFO-09: Fingerprint Web Application

**Objective:** Identify specific application and version.

**Tools:** nuclei, nmap, manual review

**Commands:**
```bash
nuclei -t cves/ -u <url>
nmap -sV -sC -p80,443 <target>
```

**Evidence:** Version strings, changelog references, CVE matches.

---

## WSTG-INFO-10: Map Application Architecture

**Objective:** Understand application architecture and infrastructure.

**Tools:** nmap, masscan, subfinder, amass

**Commands:**
```bash
masscan -p1-65535 --rate=1000 <target>
nmap -sV -sC -p<ports> <target>
subfinder -d <domain> -silent
amass enum -d <domain> -passive
```

**Evidence:** Network topology, service inventory, subdomain map.

---

## Severity Mapping

| WSTG ID | Typical Severity | Finding Category |
|---------|-----------------|------------------|
| INFO-01 | Low | Information disclosure |
| INFO-02 | Info | Fingerprinting |
| INFO-03 | Medium | Sensitive file exposure |
| INFO-04 | Info | Technology disclosure |
| INFO-05 | Medium | Content exposure |
| INFO-06 | Info | Attack surface |
| INFO-07 | Info | Architecture mapping |
| INFO-08 | Info | Framework disclosure |
| INFO-09 | Info | Version disclosure |
| INFO-10 | Info | Infrastructure mapping |

## Reporting Template

```markdown
### [WSTG-ID] [Test Name]

**Status:** [Complete / Partial / N/A]
**Tool:** [tool name + version]
**Command:** `[exact command]`
**Finding:** [description]
**Severity:** [critical/high/medium/low/info]
**Evidence:**
\```
[tool output]
\```
**Recommendation:** [remediation]
```
