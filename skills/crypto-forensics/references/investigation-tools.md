# Investigation Tools Reference

## Block Explorers

### Etherscan (Ethereum)

**URL:** https://etherscan.io

**Key Features:**
- Transaction decoding and internal transaction viewing
- Contract verification and source code access
- Token transfer tracking (ERC-20, ERC-721, ERC-1155)
- Address labeling and tags
- Gas tracking and analytics
- API access for programmatic queries

**Investigation Workflow:**
1. Search for exploit transaction hash
2. Analyze transaction calldata (decode input parameters)
3. Trace internal transactions (token transfers, contract calls)
4. Identify attacker address from transaction origin
5. Check address labels and tags
6. Export transaction data for evidence

**API Endpoints:**
```
GET /api?module=account&action=txlist&address={address}
GET /api?module=account&action=tokentx&address={address}
GET /api?module=transaction&action=gettxinfo&txhash={hash}
```

**Tips:**
- Use "Internal Txns" tab to trace token movements
- Check "State Diff" for storage changes
- Use "Debug Trace" for detailed execution analysis
- Export CSV for large transaction sets

### Solscan (Solana)

**URL:** https://solscan.io

**Key Features:**
- Solana program and instruction analysis
- Token account tracking
- Program verification
- Real-time transaction monitoring
- API access

**Investigation Workflow:**
1. Search for transaction signature
2. Analyze instruction data and program calls
3. Trace token account changes
4. Identify attacker address (wallet)
5. Check program verification status
6. Export transaction data

**Tips:**
- Use "Inner Instructions" for detailed call analysis
- Check "Token Balances" for before/after comparison
- Use "Program Logs" for debugging information

### Blockscout (Multi-chain)

**URL:** https://blockscout.com (self-hosted instances vary)

**Key Features:**
- Multi-chain support (Ethereum, Polygon, Arbitrum, Optimism, etc.)
- Open-source and self-hostable
- Privacy-focused (no tracking)
- Comprehensive API
- Contract verification

**Investigation Workflow:**
1. Select appropriate chain instance
2. Search for transaction or address
3. Analyze transaction details and internal calls
4. Trace token transfers
5. Export data via API

**Tips:**
- Use self-hosted instances for sensitive investigations
- API supports bulk queries for large datasets
- Check "Raw Traces" for detailed execution data

---

## Fund Tracking Tools

### Chainalysis Reactor

**Access:** Enterprise (law enforcement, exchanges, institutions)

**Key Features:**
- Exchange attribution and clustering
- Risk scoring and attribution
- Interactive fund flow visualization
- Cross-chain tracing
- Integration with law enforcement databases

**Investigation Workflow:**
1. Input attacker address or transaction hash
2. Generate fund flow graph
3. Identify exchange deposits
4. Generate attribution report
5. Export evidence package

**Tips:**
- Use "Cluster" feature to group related addresses
- Check "Exchange" tags for CEX deposits
- Use "Risk Score" to prioritize investigation targets

### TRM Labs

**Access:** Enterprise (financial institutions, crypto exchanges, law enforcement)

**Key Features:**
- Risk screening and monitoring
- Attribution and clustering
- Cross-chain analytics
- Sanctions screening
- Investigation tools

**Investigation Workflow:**
1. Screen address for risk indicators
2. Generate risk report
3. Trace fund flows
4. Identify counterparties
5. Export compliance report

**Tips:**
- Use "Risk Indicators" to identify mixer usage
- Check "Sanctions" for OFAC-listed addresses
- Use "Entity" tags for known attacker groups

### Elliptic

**Access:** Enterprise (exchanges, financial institutions, law enforcement)

**Key Features:**
- Wallet screening and monitoring
- Transaction risk scoring
- Attribution and clustering
- Cross-chain analytics
- Regulatory compliance tools

**Investigation Workflow:**
1. Screen wallet address
2. Generate risk score
3. Trace transaction history
4. Identify exposure to illicit services
5. Export compliance report

**Tips:**
- Use "Wallet Screening" for real-time risk assessment
- Check "Transaction Monitoring" for suspicious patterns
- Use "Investigation" tools for deep analysis

---

## Transaction Analysis

### Tenderly

**Access:** Public (limited) / Private (full features)

**Key Features:**
- Transaction simulation and debugging
- Gas analysis and optimization
- State change visualization
- Alert and monitoring
- API access

**Investigation Workflow:**
1. Import transaction hash
2. Analyze execution trace
3. Identify state changes
4. Debug failed transactions
5. Simulate attack scenarios

**Tips:**
- Use "Debug" tab for step-by-step execution
- Check "State Diff" for storage changes
- Use "Simulate" to test attack scenarios
- Export trace data for evidence

### Phalcon

**Access:** Enterprise (security teams, investigators)

**Key Features:**
- Transaction visualization and tracing
- Attack detection and analysis
- Fund flow tracking
- Cross-chain analysis
- Real-time monitoring

**Investigation Workflow:**
1. Input transaction hash
2. Generate visual trace
3. Identify attack patterns
4. Trace fund flows
5. Export analysis report

**Tips:**
- Use "Trace" view for fund flow visualization
- Check "Attack" detection for known patterns
- Use "Cross-chain" for bridge tracing

### BlockSec

**Access:** Enterprise (protocols, exchanges, institutions)

**Key Features:**
- Real-time attack detection
- Transaction monitoring
- Incident response
- Forensic analysis
- Cross-chain monitoring

**Investigation Workflow:**
1. Configure monitoring rules
2. Receive attack alerts
3. Analyze attack transaction
4. Trace fund flows
5. Generate incident report

**Tips:**
- Use "Phalcon Explorer" for transaction analysis
- Check "Attack Detection" for real-time alerts
- Use "Incident Response" for coordinated response

---

## Visualization

### Dune Analytics

**Access:** Public (free) / Premium (paid)

**Key Features:**
- Custom SQL queries on blockchain data
- Dashboard creation and sharing
- Real-time data updates
- Cross-chain support
- Community dashboards

**Investigation Workflow:**
1. Write SQL query for fund flow analysis
2. Create visualization dashboard
3. Share with investigation team
4. Monitor in real-time
5. Export data

**Tips:**
- Use community dashboards as templates
- Create custom queries for specific incidents
- Use "Spellbook" for pre-built queries
- Share dashboards with law enforcement

### Nansen

**Access:** Subscription (paid)

**Key Features:**
- Wallet labeling and profiling
- Money flow visualization
- Token analytics
- Smart money tracking
- Real-time alerts

**Investigation Workflow:**
1. Search for attacker address
2. Check wallet label and profile
3. Analyze money flow
4. Identify smart money connections
5. Export data

**Tips:**
- Use "Wallet Profiler" for address analysis
- Check "Money Flow" for fund tracking
- Use "Alerts" for real-time monitoring

---

## On-Chain Messaging and Negotiation

### On-Chain Messaging

Some attackers communicate on-chain to negotiate fund return or claim bounties.

**Common Methods:**
- Ethereum transactions with input data messages
- ENS domain registration with message
- Contract deployment with message in constructor
- Event log messages

**Investigation Workflow:**
1. Check transaction input data for messages
2. Monitor ENS registrations
3. Check contract deployment calldata
4. Monitor event logs for messages

### Negotiation

After an exploit, attackers may negotiate fund return in exchange for immunity or bug bounty.

**Common Patterns:**
- Attacker sends message on-chain offering to return funds
- Protocol team responds via governance proposal
- Funds returned through specific contract
- Attacker receives bug bounty (if applicable)

**Investigation Workflow:**
1. Monitor attacker address for messages
2. Track governance proposals for negotiation
3. Document all communications
4. Coordinate with legal team

---

## Exchange Cooperation Procedures

### Identifying Exchange Deposits

When funds reach a centralized exchange, cooperation is needed to freeze and recover.

**Investigation Workflow:**
1. Trace funds to exchange deposit address
2. Identify exchange (using clustering and labeling)
3. Contact exchange compliance team
4. Provide evidence package
5. Request fund freeze

### Exchange Contact Information

| Exchange | Compliance Contact | Response Time |
|----------|-------------------|---------------|
| Binance | compliance@binance.com | 24-48 hours |
| Coinbase | compliance@coinbase.com | 24-48 hours |
| Kraken | compliance@kraken.com | 24-48 hours |
| OKX | compliance@okx.com | 24-48 hours |
| Huobi | compliance@huobi.com | 24-48 hours |
| KuCoin | compliance@kucoin.com | 24-48 hours |

### Evidence Package for Exchanges

When contacting exchanges, provide:
1. Incident report with timeline
2. Attacker address list
3. Transaction hashes
4. Fund flow analysis
5. Proof of ownership (for affected protocol)
6. Legal documentation (if applicable)

### Legal Considerations

- **Subpoenas:** Law enforcement can subpoena exchange records
- **MLAT:** Mutual Legal Assistance Treaties for international cooperation
- **OFAC:** Sanctions screening for OFAC-listed addresses
- **FinCEN:** US financial crimes enforcement network
- **FATF:** Financial Action Task Force recommendations

### Fund Recovery Process

1. **Identification:** Trace funds to exchange
2. **Contact:** Reach out to exchange compliance team
3. **Evidence:** Provide complete evidence package
4. **Freeze:** Exchange freezes funds
5. **Legal:** Law enforcement initiates legal process
6. **Recovery:** Funds returned to protocol or users
7. **Timeline:** Weeks to months (depending on jurisdiction)
