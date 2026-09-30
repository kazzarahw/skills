---
title: "TargetCorp Attack Surface"
type: overview
tags: [web2, attack-surface, overview, eng-2026-001, client-targetcorp]
sources: ["raw/2026-09-15-nmap.md", "raw/2026-09-16-nuclei.md"]
created: 2026-09-16
updated: 2026-09-29
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# TargetCorp Attack Surface

## External Attack Surface
| Host | Port | Service | Risk |
|------|------|---------|------|
| targetcorp.com | 443 | HTTPS | Medium |
| admin.targetcorp.com | 443 | HTTPS | High |
| api.targetcorp.com | 443 | HTTPS | Medium |
| mail.targetcorp.com | 993 | IMAPS | Low |

## Internal Attack Surface
| Segment | Host Count | Key Services | Risk |
|---------|-----------|--------------|------|
| DMZ | 8 | Web, Mail | High |
| App Tier | 12 | App servers | Medium |
| Data Tier | 4 | Databases | Critical |
| Management | 6 | AD, Jump hosts | Critical |

## Critical Findings
- [[SQL Injection in Login]] — Internet-facing
- [[Exposed Admin Panel]] — Internet-facing
- Unpatched Apache — CVE-2024-38475

## Attack Paths
- [[Web App Attack Path to DB Compromise]]

## Related Pages
- [[TargetCorp]]
- [[ENG-2026-001 Timeline]]
