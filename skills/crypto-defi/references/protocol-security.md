# Protocol Security Reference

## AMM Security

### Price Manipulation

AMMs determine prices based on reserve ratios. An attacker with sufficient capital (or flash loans) can skew reserves to manipulate prices.

**Attack vector:**
1. Flash loan large amount of Token A
2. Swap Token A for Token B on target AMM, depleting Token B reserves
3. Oracle now reports inflated Token A price
4. Protocol using oracle price for lending/liquidation is now vulnerable
5. Repay flash loan, keep profit

**Mitigation:**
- Use TWAP (Time-Weighted Average Price) instead of spot price
- Use Chainlink decentralized oracle feeds
- Implement circuit breakers for large price deviations
- Use quantity limits on single-transaction swaps

### Slippage Exploitation

Slippage tolerance allows trades to execute within a price range. Attackers can exploit high slippage settings.

**Attack vector:**
1. User sets high slippage (e.g., 20%)
2. Attacker front-runs with large swap, moving price
3. User's trade executes at manipulated price
4. Attacker back-runs, capturing difference

**Mitigation:**
- Enforce maximum slippage limits
- Use private transaction pools (Flashbots)
- Implement MEV protection

### LP Token Accounting

LP tokens represent share of pool reserves. Accounting errors can allow minting excess LP tokens or burning others' liquidity.

**Attack vector:**
1. Donate tokens directly to pool (not via deposit)
2. Share/asset ratio becomes skewed
3. Attacker mints LP tokens at favorable ratio
4. Attacker redeems LP tokens for disproportionate share of reserves

**Mitigation:**
- Use robust share calculation (e.g., Curve's invariant)
- Implement donation attack prevention (minimum deposit amounts, ratio checks)
- Use OpenZeppelin's ERC-20 with proper decimal handling

---

## Lending Security

### Oracle Manipulation

Lending protocols use oracles to determine collateral value. Manipulated oracles enable under-borrowing against inflated collateral.

**Attack vector:**
1. Manipulate oracle price (via AMM spot price or low-liquidity pair)
2. Borrow against inflated collateral
3. Oracle price returns to normal
4. Position is underwater but attacker keeps borrowed funds

**Mitigation:**
- Use TWAP or Chainlink oracles
- Implement price deviation circuit breakers
- Use multiple oracle sources with medianization
- Implement borrow caps on low-liquidity collateral

### Liquidation

Liquidations maintain protocol solvency. Broken liquidation mechanisms can leave bad debt.

**Attack vector:**
1. Manipulate oracle to make healthy positions appear underwater
2. Liquidate positions at bonus rate
3. Profit from liquidation bonus
4. Protocol left with bad debt

**Mitigation:**
- Ensure liquidation bonus covers gas costs
- Implement liquidation thresholds with buffer
- Use fair liquidation mechanisms (e.g., Dutch auction)
- Monitor liquidation health factor

### Interest Rate Model

Interest rate models balance supply and demand. Manipulated rates can cause insolvency.

**Attack vector:**
1. Flash loan large deposit to spike utilization
2. Interest rates spike dramatically
3. Borrowers cannot repay, positions go underwater
4. Attacker profits from liquidation or rate arbitrage

**Mitigation:**
- Use rate models with smoothing (e.g., Aave's rate strategy)
- Implement rate change limits (max change per block)
- Use flash loan-resistant rate calculations (TWAP-based utilization)

---

## Yield Security

### Inflation Attack

Inflation attacks corrupt share/asset ratios by donating assets directly to a vault.

**Attack vector:**
1. Attacker deposits small amount, receives shares
2. Attacker donates large amount directly to vault (not via deposit)
3. Share/asset ratio is corrupted
4. Other depositors' shares are now worth less
5. Attacker withdraws, capturing value from other depositors

**Mitigation:**
- Use virtual shares or offset (e.g., ERC-4626 with virtual shares)
- Implement minimum deposit amounts
- Use OpenZeppelin's ERC-4626 with inflation attack protection
- Track deposits separately from total balance

### Donation Attack

Donation attacks are a subset of inflation attacks where direct token transfers corrupt accounting.

**Attack vector:**
1. Attacker sends tokens directly to vault contract (not via deposit function)
2. Vault's internal accounting doesn't recognize the donation
3. Share price is artificially inflated or deflated
4. Attacker exploits the accounting discrepancy

**Mitigation:**
- Use `balanceOf` for share calculations, not internal accounting
- Implement deposit/withdrawal functions that track shares properly
- Use ERC-4626 standard with virtual offset

---

## Stablecoin Security

### Oracle Failure

Stablecoins rely on oracles to maintain peg. Oracle failure can cause de-peg or insolvency.

**Attack vector:**
1. Oracle reports incorrect price (manipulation or failure)
2. Protocol mints/redeems stablecoins at wrong rate
3. Attacker profits from price discrepancy
4. Stablecoin de-pegs

**Mitigation:**
- Use decentralized oracle networks (Chainlink, Band)
- Implement oracle heartbeat and deviation thresholds
- Use multiple oracle sources with medianization
- Implement emergency shutdown (circuit breaker)

### Peg Manipulation

Peg mechanisms (Peg Stability Modules, arbitrage incentives) can be manipulated.

**Attack vector:**
1. Manipulate secondary market price of stablecoin
2. Exploit PSM (Peg Stability Module) for arbitrage
3. Drain protocol reserves
4. Stablecoin de-pegs

**Mitigation:**
- Implement PSM limits (max mint/redeem per transaction)
- Use dynamic fees based on market conditions
- Implement PSM cooldown periods

### Flash Mint

Some stablecoins allow flash minting (minting without collateral, repaying in same transaction).

**Attack vector:**
1. Flash mint large amount of stablecoin
2. Use stablecoin in DeFi protocol (e.g., as collateral)
3. Exploit protocol using stablecoin
4. Repay flash mint, keep profit

**Mitigation:**
- Disable flash minting for collateral
- Implement flash mint fees
- Use reentrancy guards
- Implement quantity limits

---

## Bridge Security

### Signature Verification

Bridges verify messages from source chain using validator signatures. Signature verification failures are catastrophic.

**Attack vector:**
1. Compromise or collude with validator threshold
2. Forge message authorizing token mint
3. Mint tokens on destination chain without corresponding lock on source chain
4. Drain bridge liquidity

**Mitigation:**
- Use decentralized validator sets (high threshold)
- Use light client verification (e.g., IBC, Nomad)
- Implement optimistic verification with challenge period
- Use multi-sig with diverse key holders

### Message Replay

Bridge messages can be replayed if not properly tracked.

**Attack vector:**
1. Observe valid bridge message
2. Replay same message on destination chain
3. Mint tokens multiple times
4. Drain bridge liquidity

**Mitigation:**
- Implement nonce tracking for all messages
- Use message ID deduplication
- Implement replay protection at contract level

### Validator Compromise

Bridge validator sets can be compromised through social engineering, key theft, or collusion.

**Attack vector:**
1. Compromise validator keys (phishing, insider, malware)
2. Forge validator signatures
3. Authorize fraudulent token mints
4. Drain bridge funds

**Mitigation:**
- Use hardware security modules (HSMs)
- Implement validator diversity (different geographic, organizational)
- Use multi-party computation (MPC) for signature generation
- Implement validator rotation and monitoring

---

## Perpetual Security

### Oracle Latency

Perpetual protocols use oracles for mark price. Latency between oracle updates can be exploited.

**Attack vector:**
1. Oracle updates price with delay
2. Attacker trades at stale price
3. Oracle catches up
4. Attacker profits from price discrepancy

**Mitigation:**
- Use low-latency oracle updates
- Implement oracle heartbeat monitoring
- Use multiple oracle sources
- Implement maximum staleness threshold

### Funding Rate Manipulation

Funding rates balance long/short positions. Manipulated funding rates can cause cascading liquidations.

**Attack vector:**
1. Open large position to skew funding rate
2. Other traders pay inflated funding
3. Attacker profits from funding rate
4. Cascading liquidations amplify profit

**Mitigation:**
- Implement funding rate limits (max change per epoch)
- Use TWAP for funding rate calculations
- Implement funding rate smoothing

### Liquidation Cascades

Large liquidations can cascade, causing market instability.

**Attack vector:**
1. Accumulate large position
2. Manipulate oracle to trigger own liquidation
3. Liquidation cascade causes market crash
4. Attacker profits from short positions or liquidation bonus

**Mitigation:**
- Implement position size limits
- Use ADL (Auto-Deleveraging) to prevent cascading
- Implement liquidation queue with rate limiting
- Use insurance fund to absorb bad debt

---

## Governance Security

### Flash Loan Voting

Governance tokens can be flash loaned to acquire voting power within a single transaction.

**Attack vector:**
1. Flash loan governance tokens
2. Submit malicious proposal
3. Vote with borrowed tokens
4. Execute proposal before loan repayment
5. Repay flash loan, keep profit from malicious proposal

**Mitigation:**
- Implement voting power snapshot (historical balance, not current)
- Use quadratic voting to reduce flash loan impact
- Implement proposal timelock (delay between approval and execution)
- Use governance token lock-up periods

### Proposal Manipulation

Governance proposals can be manipulated through vote buying or bribery.

**Attack vector:**
1. Attacker accumulates or borrows voting power
2. Proposes malicious change (e.g., upgrade to malicious contract)
3. Votes in favor with majority
4. Executes malicious proposal

**Mitigation:**
- Implement proposal threshold (minimum tokens to propose)
- Use timelock for all governance actions
- Implement veto mechanism for critical changes
- Use decentralized governance (not single-team controlled)

### Quorum Manipulation

Low voter participation can allow governance capture by small groups.

**Attack vector:**
1. Attacker accumulates tokens during low-participation period
2. Proposes and passes malicious proposal
3. Other token holders don't participate
4. Attacker controls protocol

**Mitigation:**
- Implement minimum quorum requirements
- Use delegation to increase participation
- Implement governance mining to incentivize participation
- Use optimistic governance (pass unless vetoed)

---

## Composability Risks

### Integration Risk

Protocols integrate with other protocols, creating dependency risks.

**Attack vector:**
1. Protocol A depends on Protocol B
2. Protocol B is exploited
3. Protocol A's funds are now at risk
4. Cascade failure across DeFi

**Mitigation:**
- Diversify dependencies across multiple protocols
- Implement dependency health monitoring
- Use circuit breakers for critical dependencies
- Implement maximum exposure limits per dependency

### Dependency Risk

External contract dependencies can be upgraded or exploited.

**Attack vector:**
1. Protocol uses external contract (e.g., oracle, token)
2. External contract is upgraded with malicious code
3. Protocol now interacts with malicious contract
4. Funds are drained

**Mitigation:**
- Use immutable dependencies where possible
- Implement upgrade monitoring for dependencies
- Use proxy patterns with timelocks
- Implement emergency shutdown for compromised dependencies

### Cascade Risk

Failure in one protocol can cascade to others through shared dependencies.

**Attack vector:**
1. Protocol A holds tokens from Protocol B
2. Protocol B is exploited, token value drops to zero
3. Protocol A is now insolvent
4. Protocol A's users cannot withdraw
5. Cascade continues to Protocol C, D, etc.

**Mitigation:**
- Implement exposure limits per protocol
- Use diversified collateral
- Implement emergency shutdown mechanisms
- Use insurance funds to absorb cascade losses
- Implement real-time risk monitoring across protocols
