# Evidence Preservation

Evidence preservation and chain of custody procedures for digital forensics.

## Table of Contents

- [Evidence Types](#evidence-types)
- [Chain of Custody](#chain-of-custody)
- [Evidence Handling](#evidence-handling)
- [Hash Verification](#hash-verification)
- [Legal Admissibility](#legal-admissibility)
- [Evidence Storage](#evidence-storage)
- [Documentation](#documentation)
- [Best Practices](#best-practices)

## Evidence Types

### Digital Evidence

| Type | Description | Examples |
|------|-------------|----------|
| Volatile data | Data lost on power-off | RAM contents, network connections, running processes |
| Persistent data | Data stored on media | Hard drives, SSDs, USB drives, mobile devices |
| Network data | Data in transit | PCAP files, flow data, firewall logs |
| Cloud data | Data in cloud services | SaaS logs, cloud storage, serverless functions |
| Blockchain data | On-chain data | Transactions, smart contracts, event logs |
| Log data | System and application logs | Syslog, auth logs, application logs, security logs |

### Physical Evidence

| Type | Description | Examples |
|------|-------------|----------|
| Storage media | Physical storage devices | Hard drives, SSDs, USB drives, memory cards |
| Computing devices | Devices that process data | Servers, workstations, laptops, mobile devices |
| Network equipment | Network infrastructure | Routers, switches, firewalls, access points |
| Documentation | Physical documents | Printed logs, handwritten notes, photographs |

### Testimonial Evidence

| Type | Description | Examples |
|------|-------------|----------|
| Witness statements | Accounts from individuals | Employee interviews, expert opinions |
| Expert analysis | Professional analysis | Forensic reports, technical analysis |
| Business records | Organizational records | Policies, procedures, audit logs |

## Chain of Custody

### Definition

Chain of custody is the chronological documentation of the seizure, custody, control, transfer, analysis, and disposition of evidence.

### Requirements

1. **Unique identification** — Each piece of evidence has a unique ID
2. **Complete documentation** — Every transfer is documented
3. **Integrity verification** — Hash verification at each transfer
4. **Access control** — Only authorized personnel handle evidence
5. **Secure storage** — Evidence stored in access-controlled location
6. **Audit trail** — Complete history of all access and transfers

### Chain of Custody Form

```
EVIDENCE CUSTODY FORM
=====================

Evidence ID: EVD-2024-0115-001
Case Number: CASE-2024-0115
Description: [Detailed description of evidence]
Source: [System/Address/Account/Location]
Type: [Digital/Physical/Testimonial]
Collected: [Date and time]
Collector: [Name and title]
Collection Method: [How evidence was collected]
SHA-256 Hash: [Hash value]
Storage Location: [Where evidence is stored]

CUSTODY LOG:
| # | Date/Time | From | To | Action | Reason | Hash Verified |
|---|-----------|------|----|--------|--------|---------------|
| 1 | 2024-01-15 09:00 | J. Smith | Evidence Locker | Collection | Initial collection | Yes |
| 2 | 2024-01-15 10:00 | Evidence Locker | A. Jones | Analysis | Forensic analysis | Yes |
| 3 | 2024-01-15 14:00 | A. Jones | Evidence Locker | Return | Analysis complete | Yes |

ACCESS LOG:
| # | Date/Time | Person | Access Type | Purpose | Duration |
|---|-----------|--------|-------------|---------|----------|
| 1 | 2024-01-15 10:15 | A. Jones | Read | Analysis | 2 hours |
| 2 | 2024-01-15 14:30 | J. Smith | Read | Review | 30 minutes |
```

## Evidence Handling

### Collection

**Principles:**
- Minimize alteration of original evidence
- Document the collection process
- Use write blockers for storage media
- Collect volatile data first
- Hash evidence immediately after collection
- Work on copies, never originals

**Procedures:**

```bash
# 1. Document the scene
# Photograph the system, note the time, record system state

# 2. Collect volatile data (if applicable)
# Memory capture, network connections, running processes

# 3. Create bit-for-bit copy of storage media
dd if=/dev/sda of=/evidence/disk-sda.img bs=4M conv=noerror,sync status=progress

# 4. Hash the original and copy
sha256sum /dev/sda > /evidence/original-hash.txt
sha256sum /evidence/disk-sda.img > /evidence/copy-hash.txt

# 5. Verify hashes match
diff /evidence/original-hash.txt /evidence/copy-hash.txt

# 6. Document everything
# Record all commands, timestamps, and observations
```

### Storage

**Requirements:**
- Encrypted storage (AES-256)
- Access-controlled location
- Redundant backup
- Environmental controls (temperature, humidity)
- Fire suppression
- Physical security

**Storage Procedures:**

```bash
# 1. Encrypt evidence
gpg --symmetric --cipher-algo AES256 /evidence/disk-sda.img

# 2. Store in access-controlled location
# - Evidence locker with limited access
# - Secure server room with access logging

# 3. Create redundant backup
cp /evidence/disk-sda.img.gpg /backup/evidence/disk-sda.img.gpg

# 4. Verify backup integrity
sha256sum /evidence/disk-sda.img.gpg > /evidence/primary-hash.txt
sha256sum /backup/evidence/disk-sda.img.gpg > /backup/backup-hash.txt
diff /evidence/primary-hash.txt /backup/backup-hash.txt
```

### Transmission

**Requirements:**
- Encrypted transmission (TLS 1.3, SFTP, or encrypted media)
- Hash verification after transmission
- Documented chain of custody
- Secure courier for physical media

**Transmission Procedures:**

```bash
# 1. Encrypt evidence for transmission
gpg --recipient investigator@example.com --encrypt /evidence/disk-sda.img

# 2. Transmit securely
scp /evidence/disk-sda.img.gpg investigator@secure-server:/evidence/

# 3. Verify after transmission
sha256sum /evidence/disk-sda.img.gpg > /evidence/sent-hash.txt
# On receiving end:
sha256sum /evidence/disk-sda.img.gpg > /evidence/received-hash.txt
diff /evidence/sent-hash.txt /evidence/received-hash.txt

# 4. Document transmission
# Record sender, recipient, method, timestamp, hash verification
```

### Destruction

**Requirements:**
- Documented authorization
- Secure destruction method
- Verification of destruction
- Certificate of destruction

**Destruction Procedures:**

```bash
# 1. Obtain authorization
# Written authorization from case supervisor or legal counsel

# 2. Secure destruction
# For digital media:
shred -vfz -n 3 /evidence/disk-sda.img
# For physical media:
# Use certified destruction service

# 3. Verify destruction
# Confirm data is unrecoverable

# 4. Document destruction
# Record what was destroyed, when, how, by whom
# Obtain certificate of destruction
```

## Hash Verification

### SHA-256

```bash
# Generate SHA-256 hash
sha256sum /evidence/file > /evidence/file.sha256

# Verify hash
sha256sum -c /evidence/file.sha256

# Generate hash for multiple files
find /evidence -type f -exec sha256sum {} \; > /evidence/MANIFEST.sha256

# Verify all hashes
cd /evidence && sha256sum -c MANIFEST.sha256
```

### MD5

```bash
# Generate MD5 hash (legacy, not recommended for security)
md5sum /evidence/file > /evidence/file.md5

# Verify MD5 hash
md5sum -c /evidence/file.md5
```

### Hash Verification Best Practices

1. **Hash immediately** — Generate hash as soon as evidence is collected
2. **Hash at every transfer** — Verify hash at each chain of custody transfer
3. **Use SHA-256** — MD5 is deprecated for security purposes
4. **Store hashes separately** — Keep hash files separate from evidence
5. **Document all hashes** — Record all hash values in evidence log
6. **Verify before analysis** — Always verify hash before analyzing evidence
7. **Verify after analysis** — Verify hash after analysis to confirm no modification

## Legal Admissibility

### Standards

**United States:**
- Federal Rules of Evidence (FRE)
- Daubert standard (expert testimony)
- Frye standard (scientific evidence)

**Key Requirements:**
- Relevance — Evidence must be relevant to the case
- Authenticity — Evidence must be authentic and unaltered
- Reliability — Collection and analysis must be reliable
- Chain of custody — Complete documentation of handling

### Best Practices for Admissibility

1. **Follow established procedures** — Use documented, tested procedures
2. **Use validated tools** — Use tools that are accepted in the field
3. **Document everything** — Complete documentation of all actions
4. **Maintain chain of custody** — Unbroken chain of custody
5. **Be reproducible** — Another expert should reach same conclusions
6. **Be objective** — Avoid bias, follow the evidence
7. **Stay within expertise** — Only testify within area of expertise

### Common Challenges

| Challenge | Response |
|-----------|----------|
| Evidence was altered | Hash verification proves integrity |
| Chain of custody broken | Document all transfers, explain gaps |
| Tool is not validated | Provide validation studies, peer review |
| Procedure is not standard | Explain rationale, provide documentation |
| Expert is not qualified | Provide credentials, experience, training |

## Evidence Storage

### Encrypted Storage

```bash
# Encrypt evidence directory
gpg --symmetric --cipher-algo AES256 /evidence/case-2024-0115/

# Or use encrypted container
cryptsetup luksFormat /dev/sdb1
cryptsetup luksOpen /dev/sdb1 evidence-vault
mkfs.ext4 /dev/mapper/evidence-vault
mount /dev/mapper/evidence-vault /evidence/
```

### Access Control

```bash
# Set permissions
chmod 700 /evidence/case-2024-0115/
chown root:forensics /evidence/case-2024-0115/

# Use ACLs for granular access
setfacl -m u:investigator:r-x /evidence/case-2024-0115/
setfacl -m u:analyst:r /evidence/case-2024-0115/

# Audit access
auditctl -w /evidence/case-2024-0115/ -p rwxa -k evidence-access
```

### Redundant Storage

```bash
# Primary storage
cp /evidence/case-2024-0115/ /storage/primary/

# Backup storage
cp /evidence/case-2024-0115/ /storage/backup/

# Offsite storage
rsync -avz /evidence/case-2024-0115/ offsite-server:/evidence/

# Verify all copies
find /evidence/case-2024-0115/ -type f -exec sha256sum {} \; > /evidence/MANIFEST.sha256
find /storage/primary/case-2024-0115/ -type f -exec sha256sum {} \; > /storage/primary/MANIFEST.sha256
find /storage/backup/case-2024-0115/ -type f -exec sha256sum {} \; > /storage/backup/MANIFEST.sha256
diff /evidence/MANIFEST.sha256 /storage/primary/MANIFEST.sha256
diff /evidence/MANIFEST.sha256 /storage/backup/MANIFEST.sha256
```

## Documentation

### Evidence Log

```
EVIDENCE LOG
============

Case Number: CASE-2024-0115
Incident: [Description]
Date Opened: 2024-01-15
Lead Investigator: [Name]

EVIDENCE ITEMS:
| ID | Description | Type | Collected | Collector | Hash | Location |
|----|-------------|------|-----------|-----------|------|----------|
| EVD-001 | [Description] | [Type] | [Date] | [Name] | [Hash] | [Location] |
| EVD-002 | [Description] | [Type] | [Date] | [Name] | [Hash] | [Location] |

HANDLING LOG:
| Date | Evidence ID | From | To | Action | Reason | Hash Verified |
|------|-------------|------|----|--------|--------|---------------|
| ... | ... | ... | ... | ... | ... | ... |

ACCESS LOG:
| Date | Evidence ID | Person | Access Type | Purpose | Duration |
|------|-------------|--------|-------------|---------|----------|
| ... | ... | ... | ... | ... | ... |
```

### Handling Procedures

```
EVIDENCE HANDLING PROCEDURES
============================

1. COLLECTION
   - Use write blockers for storage media
   - Collect volatile data first
   - Hash evidence immediately
   - Document collection process

2. STORAGE
   - Store in encrypted, access-controlled location
   - Maintain redundant backup
   - Verify integrity regularly
   - Limit access to authorized personnel

3. TRANSMISSION
   - Encrypt before transmission
   - Use secure transmission methods
   - Verify hash after transmission
   - Document all transfers

4. ANALYSIS
   - Work on copies, never originals
   - Document all analysis steps
   - Verify hash before and after analysis
   - Use validated tools and procedures

5. DESTRUCTION
   - Obtain written authorization
   - Use secure destruction methods
   - Verify destruction
   - Document destruction
```

## Best Practices

1. **Preserve before analysis** — Always preserve evidence before any analysis
2. **Hash everything** — Generate hashes for all evidence immediately
3. **Document everything** — Complete documentation of all actions
4. **Work on copies** — Never analyze original evidence
5. **Maintain chain of custody** — Unbroken chain of custody
6. **Use validated tools** — Use tools accepted in the field
7. **Be reproducible** — Another investigator should reach same conclusions
8. **Stay current** — Keep up with evolving standards and procedures
9. **Consult legal** — Involve legal counsel early
10. **Train regularly** — Regular training on evidence handling procedures
