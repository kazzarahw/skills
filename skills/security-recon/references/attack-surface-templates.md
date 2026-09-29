# Attack Surface Map Templates

Templates for mapping attack surfaces across web2, web3, and mixed environments. Includes entry point catalogs, trust boundary mapping, dependency mapping, and risk indicator templates.

## Table of Contents

- [Web2 Attack Surface Template](#web2-attack-surface-template)
- [Web3 Attack Surface Template](#web3-attack-surface-template)
- [Mixed Attack Surface Template](#mixed-attack-surface-template)
- [Risk Indicator Templates](#risk-indicator-templates)
- [Entry Point Catalog](#entry-point-catalog)
- [Trust Boundary Mapping](#trust-boundary-mapping)
- [Dependency Mapping](#dependency-mapping)

---

## Web2 Attack Surface Template

```markdown
# Web2 Attack Surface Map: [Target]

**Date:** YYYY-MM-DD
**Scope:** [In-scope targets]
**Analyst:** [Name]

## Executive Summary
- Total entry points: [N]
- Total trust boundaries: [N]
- Total dependencies: [N]
- Risk indicators: [N] critical, [N] high, [N] medium, [N] low

## Entry Points

### Network Services
| Host | Port | Service | Version | Exposure | Notes |
|------|------|---------|---------|----------|-------|
| 10.0.0.1 | 80 | HTTP | nginx 1.18.0 | Public | Main website |
| 10.0.0.1 | 443 | HTTPS | nginx 1.18.0 | Public | Main website (SSL) |
| 10.0.0.2 | 22 | SSH | OpenSSH 8.2 | Internal | Admin access |
| 10.0.0.3 | 3306 | MySQL | MySQL 8.0 | Internal | Database |

### Web Applications
| URL | Technology | Authentication | Authorization | Notes |
|-----|-----------|----------------|---------------|-------|
| https://example.com | React, nginx | Session-based | Role-based | Main application |
| https://api.example.com | Node.js, Express | JWT | Scope-based | REST API |
| https://admin.example.com | PHP, Apache | Session-based | Admin only | Admin panel |

### APIs
| Endpoint | Method | Authentication | Rate Limit | Notes |
|----------|--------|----------------|------------|-------|
| /api/v1/users | GET | JWT | 100/min | User list |
| /api/v1/users | POST | JWT | 10/min | Create user |
| /api/v1/auth/login | POST | None | 5/min | Login |

### Cloud Assets
| Asset | Type | Exposure | Notes |
|-------|------|----------|-------|
| example.s3.amazonaws.com | S3 Bucket | Public | Static assets |
| example.blob.core.windows.net | Azure Blob | Private | Backups |

## Trust Boundaries

### Authentication Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| User → Web App | Session cookie | Medium | HttpOnly, Secure flags |
| Web App → API | JWT | Medium | 1h expiry |
| API → Database | Service account | Strong | Least privilege |

### Authorization Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| User → Admin | Role-based | Medium | Admin role required |
| API → Internal | Network-based | Strong | Internal only |

### Network Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| Internet → DMZ | Firewall | Strong | Port-based rules |
| DMZ → Internal | Firewall | Strong | IP-based rules |

## Data Flows

### User Authentication Flow
```
User → Web App (login) → Database (verify) → Web App (session) → User
```

### API Request Flow
```
Client → API (auth) → Database (query) → API (response) → Client
```

### File Upload Flow
```
User → Web App (upload) → S3 (store) → Web App (confirm) → User
```

## Dependencies

### External Dependencies
| Dependency | Type | Version | Risk | Notes |
|------------|------|---------|------|-------|
| jQuery | Library | 3.6.0 | Low | CDN |
| Stripe | Payment | N/A | Low | PCI compliant |
| Google Analytics | Tracking | N/A | Medium | Data collection |

### Internal Dependencies
| Dependency | Type | Risk | Notes |
|------------|------|------|-------|
| Auth Service | Service | High | Single point of failure |
| Database | Storage | High | Contains PII |

## Risk Indicators

| Indicator | Severity | Evidence | WSTG |
|-----------|----------|----------|------|
| Default credentials | Critical | nmap -sV shows default creds | WSTG-ATHN-04 |
| Outdated software | High | nginx 1.18.0 (EOL) | WSTG-INFO-08 |
| Verbose errors | Medium | Stack traces in responses | WSTG-ERRH-01 |
| Missing security headers | Medium | No CSP, HSTS | WSTG-CONF-05 |
```

---

## Web3 Attack Surface Template

```markdown
# Web3 Attack Surface Map: [Target]

**Date:** YYYY-MM-DD
**Scope:** [In-scope addresses/contracts]
**Chain:** [Ethereum/BSC/Polygon/etc.]
**Analyst:** [Name]

## Executive Summary
- Total contracts: [N]
- Total entry points: [N]
- Total trust boundaries: [N]
- Total dependencies: [N]
- Risk indicators: [N] critical, [N] high, [N] medium, [N] low

## Contract Inventory

### Core Contracts
| Address | Name | Type | Verified | Proxy | TVL | Notes |
|---------|------|------|----------|-------|-----|-------|
| 0x... | Protocol Token | ERC-20 | Yes | No | $10M | Main token |
| 0x... | Protocol Vault | Custom | Yes | Yes (UUPS) | $50M | Core vault |
| 0x... | Protocol Governor | Governor | Yes | No | N/A | Governance |

### Supporting Contracts
| Address | Name | Type | Verified | Proxy | TVL | Notes |
|---------|------|------|----------|-------|-----|-------|
| 0x... | Oracle | Chainlink | Yes | No | N/A | Price feed |
| 0x... | Timelock | Timelock | Yes | No | N/A | Governance delay |

## Entry Points

### External Functions
| Contract | Function | Access | Value Limit | Notes |
|----------|----------|--------|-------------|-------|
| Vault | deposit() | Public | None | Deposit tokens |
| Vault | withdraw() | Public | None | Withdraw tokens |
| Governor | propose() | Public | None | Create proposal |
| Governor | execute() | Public | None | Execute proposal |

### Oracles
| Oracle | Update Frequency | Deviation Threshold | Notes |
|--------|------------------|---------------------|-------|
| ETH/USD | 1 hour | 0.5% | Chainlink |
| BTC/USD | 1 hour | 0.5% | Chainlink |

### Admin Functions
| Contract | Function | Role | Timelock | Notes |
|----------|----------|------|----------|-------|
| Vault | pause() | Pauser | No | Emergency pause |
| Vault | upgradeTo() | Owner | Yes (48h) | Upgrade implementation |
| Governor | setTimelock() | Owner | Yes (48h) | Change timelock |

## Trust Boundaries

### Access Control Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| User → Contract | Token approval | Medium | ERC-20 approve |
| Contract → Oracle | Price feed | Strong | Chainlink |
| Owner → Contract | Ownable | Medium | Single EOA |
| Timelock → Contract | Timelock | Strong | 48h delay |

### Upgrade Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| Proxy → Implementation | EIP-1967 | Medium | UUPS pattern |
| Owner → Proxy | upgradeTo() | Medium | Timelock protected |

## Data Flows

### Deposit Flow
```
User → Vault.deposit() → Token.transferFrom() → Vault.mintShares() → User
```

### Withdrawal Flow
```
User → Vault.withdraw() → Vault.burnShares() → Token.transfer() → User
```

### Governance Flow
```
User → Governor.propose() → Timelock.queue() → Timelock.execute() → Contract
```

## Dependencies

### Token Dependencies
| Token | Type | Address | Risk | Notes |
|-------|------|---------|------|-------|
| ETH | Native | 0x0 | Low | Native token |
| USDC | ERC-20 | 0x... | Low | Stablecoin |
| WBTC | ERC-20 | 0x... | Medium | Wrapped Bitcoin |

### Oracle Dependencies
| Oracle | Provider | Address | Risk | Notes |
|--------|----------|---------|------|-------|
| ETH/USD | Chainlink | 0x... | Low | Decentralized |
| BTC/USD | Chainlink | 0x... | Low | Decentralized |

### Protocol Dependencies
| Protocol | Type | Address | Risk | Notes |
|----------|------|---------|------|-------|
| Uniswap | DEX | 0x... | Low | Liquidity |
| Aave | Lending | 0x... | Low | Flash loans |

## Risk Indicators

| Indicator | Severity | Evidence | SWC |
|-----------|----------|----------|-----|
| Unverified contract | Critical | No source code | SWC-101 |
| Public mint function | Critical | mint() is public | SWC-105 |
| Reentrancy vulnerability | High | No reentrancy guard | SWC-107 |
| Oracle manipulation | High | Single oracle | SWC-120 |
| Centralization risk | Medium | Owner is EOA | SWC-102 |
| No timelock on pause | Medium | pause() has no delay | SWC-106 |
```

---

## Mixed Attack Surface Template

```markdown
# Mixed Attack Surface Map: [Target]

**Date:** YYYY-MM-DD
**Scope:** [In-scope targets]
**Type:** Web2 + Web3
**Analyst:** [Name]

## Executive Summary
- Web2 entry points: [N]
- Web3 entry points: [N]
- Cross-chain entry points: [N]
- Risk indicators: [N] critical, [N] high, [N] medium, [N] low

## Web2 Attack Surface

### Network Services
| Host | Port | Service | Version | Exposure | Notes |
|------|------|---------|---------|----------|-------|
| 10.0.0.1 | 443 | HTTPS | nginx 1.18.0 | Public | Web app |

### Web Applications
| URL | Technology | Authentication | Notes |
|-----|-----------|----------------|-------|
| https://example.com | React, nginx | Session-based | Main app |
| https://app.example.com | React, nginx | Wallet connect | Web3 app |

## Web3 Attack Surface

### Contracts
| Address | Name | Type | Verified | TVL | Notes |
|---------|------|------|----------|-----|-------|
| 0x... | Protocol Token | ERC-20 | Yes | $10M | Main token |
| 0x... | Protocol Vault | Custom | Yes | $50M | Core vault |

### Entry Points
| Contract | Function | Access | Notes |
|----------|----------|--------|-------|
| Vault | deposit() | Public | Deposit tokens |
| Vault | withdraw() | Public | Withdraw tokens |

## Cross-Chain Attack Surface

### Bridge Interactions
| Bridge | Source Chain | Destination Chain | Risk | Notes |
|--------|--------------|-------------------||-------|
| Multichain | Ethereum | BSC | High | Bridge contract |
| Wormhole | Ethereum | Solana | High | Bridge contract |

### Multi-Chain Contracts
| Contract | Ethereum | BSC | Polygon | Notes |
|----------|----------|-----|---------|-------|
| Protocol Token | 0x... | 0x... | 0x... | Same address |
| Protocol Vault | 0x... | 0x... | 0x... | Same address |

## Trust Boundaries

### Web2 Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| User → Web App | Session cookie | Medium | HttpOnly, Secure |
| Web App → API | JWT | Medium | 1h expiry |

### Web3 Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| User → Contract | Wallet signature | Strong | ECDSA |
| Contract → Oracle | Price feed | Strong | Chainlink |

### Cross-Chain Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| Ethereum → BSC | Bridge | High | Multichain |
| Ethereum → Solana | Bridge | High | Wormhole |

## Data Flows

### Web2 → Web3 Flow
```
User → Web App (connect wallet) → Web3 Contract (deposit) → Web App (confirm) → User
```

### Web3 → Web2 Flow
```
User → Web3 Contract (withdraw) → Web App (update balance) → User
```

### Cross-Chain Flow
```
User → Ethereum Contract (lock) → Bridge (relay) → BSC Contract (mint) → User
```

## Dependencies

### Web2 Dependencies
| Dependency | Type | Risk | Notes |
|------------|------|------|-------|
| Web3.js | Library | Low | Ethereum interaction |
| WalletConnect | Protocol | Medium | Wallet connection |

### Web3 Dependencies
| Dependency | Type | Risk | Notes |
|------------|------|------|-------|
| Chainlink | Oracle | Low | Price feeds |
| Uniswap | DEX | Low | Liquidity |

### Cross-Chain Dependencies
| Dependency | Type | Risk | Notes |
|------------|------|------|-------|
| Multichain | Bridge | High | Cross-chain transfers |
| Wormhole | Bridge | High | Cross-chain transfers |

## Risk Indicators

| Indicator | Severity | Evidence | Category |
|-----------|----------|----------|----------|
| Bridge vulnerability | Critical | Unverified bridge contract | Cross-chain |
| Reentrancy in vault | High | No reentrancy guard | Web3 |
| XSS in web app | High | No CSP header | Web2 |
| Oracle manipulation | High | Single oracle | Web3 |
| Centralization risk | Medium | Owner is EOA | Web3 |
| Missing rate limiting | Medium | No rate limit on API | Web2 |
```

---

## Risk Indicator Templates

### Critical Risk Indicators

| Indicator | Web2 Evidence | Web3 Evidence | Impact |
|-----------|---------------|---------------|--------|
| Default credentials | nmap shows default creds | N/A | Full compromise |
| Unverified contract | N/A | No source code | Unknown behavior |
| Public mint function | N/A | mint() is public | Infinite tokens |
| SQL injection | nuclei finds SQLi | N/A | Data breach |
| RCE vulnerability | nuclei finds RCE | N/A | Full compromise |
| Bridge vulnerability | N/A | Unverified bridge | Fund loss |

### High Risk Indicators

| Indicator | Web2 Evidence | Web3 Evidence | Impact |
|-----------|---------------|---------------|--------|
| Outdated software | Version banner shows EOL | Old compiler version | Known CVEs |
| Reentrancy vulnerability | N/A | No reentrancy guard | Fund drain |
| Oracle manipulation | N/A | Single oracle | Price manipulation |
| XSS vulnerability | nuclei finds XSS | N/A | Session hijacking |
| CSRF vulnerability | nuclei finds CSRF | N/A | Unauthorized actions |
| Missing authentication | No auth on endpoint | Public sensitive function | Unauthorized access |

### Medium Risk Indicators

| Indicator | Web2 Evidence | Web3 Evidence | Impact |
|-----------|---------------|---------------|--------|
| Verbose errors | Stack traces in responses | Verbose revert reasons | Information disclosure |
| Missing security headers | No CSP, HSTS | N/A | Various attacks |
| Centralization risk | N/A | Owner is EOA | Single point of failure |
| No timelock | N/A | Admin functions have no delay | Instant changes |
| Missing rate limiting | No rate limit on API | No rate limit on functions | DoS |
| Information disclosure | Directory listing enabled | Exposed storage | Data leakage |

### Low Risk Indicators

| Indicator | Web2 Evidence | Web3 Evidence | Impact |
|-----------|---------------|---------------|--------|
| Missing security headers | No X-Frame-Options | N/A | Clickjacking |
| Cookie flags missing | No HttpOnly, Secure | N/A | Session theft |
| Information disclosure | Server header exposed | Compiler version exposed | Reconnaissance |
| Missing CSP | No Content-Security-Policy | N/A | XSS |
| Missing HSTS | No Strict-Transport-Security | N/A | MITM |

---

## Entry Point Catalog

### Web2 Entry Points

| Category | Entry Point | Detection Method | Risk |
|----------|-------------|-----------------|------|
| Web | HTTP/HTTPS | nmap, whatweb | High |
| API | REST/GraphQL | gobuster, ffuf | High |
| Admin | Admin panels | gobuster, dorks | Critical |
| Database | MySQL, PostgreSQL, MongoDB | nmap | Critical |
| File | FTP, SFTP, SMB | nmap | High |
| Mail | SMTP, IMAP, POP3 | nmap | Medium |
| Remote | SSH, RDP, Telnet | nmap | High |
| Cloud | S3, Azure Blob, GCP Storage | cloud enum | High |
| DNS | DNS servers | dnsrecon | Medium |
| VPN | OpenVPN, WireGuard | nmap | High |

### Web3 Entry Points

| Category | Entry Point | Detection Method | Risk |
|----------|-------------|-----------------|------|
| Contract | External functions | Etherscan, Heimdall | High |
| Oracle | Price feeds | Contract analysis | High |
| Admin | Owner functions | Contract analysis | Critical |
| Upgrade | Proxy functions | EIP-1967 slots | High |
| Bridge | Bridge contracts | Cross-chain analysis | Critical |
| Token | ERC-20/721/1155 | Etherscan | High |
| Governance | Governor contracts | Etherscan | Medium |
| Timelock | Timelock contracts | Etherscan | Low |

### Cross-Chain Entry Points

| Category | Entry Point | Detection Method | Risk |
|----------|-------------|-----------------|------|
| Bridge | Bridge contracts | Cross-chain analysis | Critical |
| Multi-chain | Same address on multiple chains | Address matching | High |
| Wrapped | Wrapped tokens | Token analysis | High |
| Oracle | Cross-chain oracles | Oracle analysis | High |

---

## Trust Boundary Mapping

### Web2 Trust Boundaries

| Boundary | Mechanism | Strength | Bypass Risk |
|----------|-----------|----------|-------------|
| User → Web App | Session cookie | Medium | XSS, CSRF |
| Web App → API | JWT | Medium | Token theft |
| API → Database | Service account | Strong | SQL injection |
| Internet → DMZ | Firewall | Strong | Firewall bypass |
| DMZ → Internal | Firewall | Strong | Firewall bypass |
| User → Admin | Role-based | Medium | Privilege escalation |
| API → Internal | Network-based | Strong | Network bypass |

### Web3 Trust Boundaries

| Boundary | Mechanism | Strength | Bypass Risk |
|----------|-----------|----------|-------------|
| User → Contract | Wallet signature | Strong | Key compromise |
| Contract → Oracle | Price feed | Strong | Oracle manipulation |
| Owner → Contract | Ownable | Medium | Key compromise |
| Timelock → Contract | Timelock | Strong | Governance attack |
| Proxy → Implementation | EIP-1967 | Medium | Upgrade exploit |
| Bridge → Bridge | Cross-chain | High | Bridge exploit |
| User → Bridge | Wallet signature | Strong | Key compromise |

### Cross-Chain Trust Boundaries

| Boundary | Mechanism | Strength | Bypass Risk |
|----------|-----------|----------|-------------|
| Ethereum → BSC | Bridge | High | Bridge exploit |
| Ethereum → Solana | Bridge | High | Bridge exploit |
| Ethereum → Polygon | Bridge | High | Bridge exploit |
| L1 → L2 | Rollup | Medium | Rollup exploit |

---

## Dependency Mapping

### Web2 Dependencies

| Dependency | Type | Version | Risk | Mitigation |
|------------|------|---------|------|------------|
| jQuery | Library | 3.6.0 | Low | Update to latest |
| React | Library | 18.0.0 | Low | Update to latest |
| nginx | Web server | 1.18.0 | Medium | Update to latest |
| MySQL | Database | 8.0 | Medium | Update to latest |
| Redis | Cache | 6.0 | Medium | Update to latest |
| Stripe | Payment | N/A | Low | PCI compliant |
| Google Analytics | Tracking | N/A | Medium | Data collection |

### Web3 Dependencies

| Dependency | Type | Address | Risk | Mitigation |
|------------|------|---------|------|------------|
| Chainlink | Oracle | 0x... | Low | Decentralized |
| Uniswap | DEX | 0x... | Low | Audited |
| Aave | Lending | 0x... | Low | Audited |
| OpenZeppelin | Library | N/A | Low | Audited |
| USDC | Stablecoin | 0x... | Low | Regulated |
| WBTC | Wrapped BTC | 0x... | Medium | Custodial |

### Cross-Chain Dependencies

| Dependency | Type | Chains | Risk | Mitigation |
|------------|------|--------|------|------------|
| Multichain | Bridge | Multi | High | Audit status |
| Wormhole | Bridge | Multi | High | Audit status |
| LayerZero | Bridge | Multi | Medium | Audit status |
| Axelar | Bridge | Multi | Medium | Audit status |
