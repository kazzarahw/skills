# DeFi Protocol-Specific Audit Guidance

Comprehensive audit guidance for different DeFi protocol types, covering unique attack vectors and security considerations.

---

## Table of Contents

- [AMMs (Automated Market Makers)](#ams)
  - [Protocols: Uniswap, Curve, Balancer](#protocols-uniswap-curve-balancer)
  - [Unique Attack Vectors](#unique-attack-vectors)
  - [Audit Checklist](#audit-checklist)
- [Lending Protocols](#lending-protocols)
  - [Protocols: Aave, Compound, MakerDAO](#protocols-aave-compound-makerdao)
  - [Unique Attack Vectors](#unique-attack-vectors-1)
  - [Audit Checklist](#audit-checklist-1)
- [Yield Aggregators](#yield-aggregators)
  - [Protocols: Yearn, Harvest](#protocols-yearn-harvest)
  - [Unique Attack Vectors](#unique-attack-vectors-2)
  - [Audit Checklist](#audit-checklist-2)
- [Stablecoins](#stablecoins)
  - [Protocols: DAI, FRAX, USDC](#protocols-dai-frax-usdc)
  - [Unique Attack Vectors](#unique-attack-vectors-3)
  - [Audit Checklist](#audit-checklist-3)
- [Bridges](#bridges)
  - [Protocols: Wormhole, Ronin, Nomad](#protocols-wormhole-ronin-nomad)
  - [Unique Attack Vectors](#unique-attack-vectors-4)
  - [Audit Checklist](#audit-checklist-4)
- [Perpetuals](#perpetuals)
  - [Protocols: dYdX, GMX, GNS](#protocols-dydx-gmx-gns)
  - [Unique Attack Vectors](#unique-attack-vectors-5)
  - [Audit Checklist](#audit-checklist-5)
- [Liquid Staking](#liquid-staking)
  - [Protocols: Lido, Rocket Pool](#protocols-lido-rocket-pool)
  - [Unique Attack Vectors](#unique-attack-vectors-6)
  - [Audit Checklist](#audit-checklist-6)
- [Restaking](#restaking)
  - [Protocols: EigenLayer](#protocols-eigenlayer)
  - [Unique Attack Vectors](#unique-attack-vectors-7)
  - [Audit Checklist](#audit-checklist-7)
- [Options](#options)
  - [Protocols: Lyra, Premia](#protocols-lyra-premia)
  - [Unique Attack Vectors](#unique-attack-vectors-8)
  - [Audit Checklist](#audit-checklist-8)
- [RWA (Real World Assets)](#rwa)
  - [Protocols: Centrifuge, Maple](#protocols-centrifuge-maple)
  - [Unique Attack Vectors](#unique-attack-vectors-9)
  - [Audit Checklist](#audit-checklist-9)
- [General Audit Checklist (All Protocols)](#general-audit-checklist-all-protocols)
  - [Access Control](#access-control)
  - [Oracle Security](#oracle-security)
  - [Economic Security](#economic-security)
  - [Operational Security](#operational-security)
  - [Code Quality](#code-quality)

---

## AMMs (Automated Market Makers)

### Protocols: Uniswap, Curve, Balancer

### Unique Attack Vectors

#### Price Manipulation
```solidity
// VULNERABLE: Spot price dependency
function getAmountOut(uint256 amountIn, uint256 reserveIn, uint256 reserveOut) 
    public pure returns (uint256) {
    return (amountIn * reserveOut) / (reserveIn + amountIn);
    // Can be manipulated with flash loans
}

// SECURE: Use TWAP or oracle
function getAmountOut(uint256 amountIn) public view returns (uint256) {
    uint256 twapPrice = getTWAP(1 hours);
    return amountIn * twapPrice / 1e18;
}
```

#### Slippage Protection
```solidity
// VULNERABLE: No slippage protection
function swap(uint256 amountIn) external {
    uint256 amountOut = getAmountOut(amountIn);
    // No minimum output check!
    tokenOut.transfer(msg.sender, amountOut);
}

// SECURE: Slippage protection
function swap(uint256 amountIn, uint256 minAmountOut) external {
    uint256 amountOut = getAmountOut(amountIn);
    require(amountOut >= minAmountOut, "Slippage too high");
    tokenOut.transfer(msg.sender, amountOut);
}
```

#### LP Accounting
```solidity
// VULNERABLE: Incorrect LP token minting
function addLiquidity(uint256 amountA, uint256 amountB) external {
    uint256 lpTokens = sqrt(amountA * amountB);
    _mint(msg.sender, lpTokens);
    // Can be manipulated with donation attacks
}

// SECURE: Proportional minting
function addLiquidity(uint256 amountA, uint256 amountB) external {
    uint256 lpSupply = totalSupply();
    uint256 lpTokens;
    if (lpSupply == 0) {
        lpTokens = sqrt(amountA * amountB);
    } else {
        lpTokens = min(amountA * lpSupply / reserveA, amountB * lpSupply / reserveB);
    }
    _mint(msg.sender, lpTokens);
}
```

### Audit Checklist

- [ ] Price oracle manipulation resistance
- [ ] Slippage protection on all swaps
- [ ] LP token accounting correctness
- [ ] Flash loan attack resistance
- [ ] Fee calculation accuracy
- [ ] Emergency pause functionality
- [ ] Admin key security

---

## Lending Protocols

### Protocols: Aave, Compound, MakerDAO

### Unique Attack Vectors

#### Oracle Manipulation
```solidity
// VULNERABLE: Spot price for collateral
function borrow(uint256 amount) external {
    uint256 collateralValue = collateralAmount * getSpotPrice();
    require(collateralValue >= amount * 1.5e18);
    // Can be manipulated with flash loans
}

// SECURE: TWAP for collateral valuation
function borrow(uint256 amount) external {
    uint256 collateralValue = collateralAmount * getTWAP(1 hours);
    require(collateralValue >= amount * 1.5e18);
}
```

#### Liquidation Manipulation
```solidity
// VULNERABLE: No liquidation incentive
function liquidate(address user) external {
    uint256 debt = getDebt(user);
    uint256 collateral = getCollateral(user);
    transferCollateral(msg.sender, collateral);
    repayDebt(debt);
    // No incentive for liquidator
}

// SECURE: Liquidation incentive
function liquidate(address user) external {
    uint256 debt = getDebt(user);
    uint256 collateral = getCollateral(user);
    uint256 bonus = collateral * 5 / 100; // 5% bonus
    transferCollateral(msg.sender, collateral + bonus);
    repayDebt(debt);
}
```

#### Interest Rate Model
```solidity
// VULNERABLE: Incorrect interest rate calculation
function calculateInterest(uint256 utilization) public pure returns (uint256) {
    return utilization * 10 / 100; // Linear, can be gamed
}

// SECURE: Kinked interest rate model
function calculateInterest(uint256 utilization) public pure returns (uint256) {
    uint256 kink = 80e16; // 80%
    if (utilization <= kink) {
        return utilization * 5 / 100; // 5% base rate
    } else {
        uint256 excess = utilization - kink;
        return kink * 5 / 100 + excess * 50 / 100; // 50% above kink
    }
}
```

### Audit Checklist

- [ ] Oracle manipulation resistance
- [ ] Liquidation mechanism correctness
- [ ] Interest rate model accuracy
- [ ] Collateral factor appropriateness
- [ ] Liquidation incentive adequacy
- [ ] Bad debt handling
- [ ] Flash loan resistance
- [ ] Governance attack resistance

---

## Yield Aggregators

### Protocols: Yearn, Harvest

### Unique Attack Vectors

#### Inflation Attack
```solidity
// VULNERABLE: First depositor can inflate share price
function deposit(uint256 amount) external {
    uint256 shares = totalSupply == 0 ? amount : amount * totalSupply / balance;
    _mint(msg.sender, shares);
    // First depositor can donate tokens to inflate share price
}

// SECURE: Virtual offset
function deposit(uint256 amount) external {
    uint256 shares = (amount * (totalSupply + VIRTUAL_OFFSET)) / (balance + VIRTUAL_OFFSET);
    _mint(msg.sender, shares);
}
```

#### Donation Attack
```solidity
// VULNERABLE: Donation can manipulate share price
function deposit(uint256 amount) external {
    uint256 shares = amount * totalSupply / balance;
    _mint(msg.sender, shares);
    // Attacker donates tokens to manipulate share price
}

// SECURE: Use oracle for share price
function deposit(uint256 amount) external {
    uint256 sharePrice = getOracleSharePrice();
    uint256 shares = amount / sharePrice;
    _mint(msg.sender, shares);
}
```

### Audit Checklist

- [ ] Inflation attack resistance
- [ ] Donation attack resistance
- [ ] Share price calculation accuracy
- [ ] Withdrawal fee fairness
- [ ] Strategy risk assessment
- [ ] Emergency withdrawal mechanism
- [ ] Admin key security

---

## Stablecoins

### Protocols: DAI, FRAX, USDC

### Unique Attack Vectors

#### Oracle Failure
```solidity
// VULNERABLE: Single oracle dependency
function mint(uint256 amount) external {
    uint256 price = getOraclePrice();
    require(price >= 1e18, "Peg broken");
    // Single oracle can fail
}

// SECURE: Multiple oracles
function mint(uint256 amount) external {
    uint256 price1 = getOracle1Price();
    uint256 price2 = getOracle2Price();
    uint256 price = (price1 + price2) / 2;
    require(price >= 1e18, "Peg broken");
}
```

#### Peg Manipulation
```solidity
// VULNERABLE: No circuit breaker
function redeem(uint256 amount) external {
    uint256 price = getOraclePrice();
    uint256 collateral = amount * price / 1e18;
    transferCollateral(msg.sender, collateral);
    // No circuit breaker for large deviations
}

// SECURE: Circuit breaker
function redeem(uint256 amount) external {
    uint256 price = getOraclePrice();
    require(price >= 0.98e18 && price <= 1.02e18, "Circuit breaker");
    uint256 collateral = amount * price / 1e18;
    transferCollateral(msg.sender, collateral);
}
```

#### Collateral Insolvency
```solidity
// VULNERABLE: No collateral ratio check
function mint(uint256 amount) external {
    uint256 collateralValue = getCollateralValue();
    require(collateralValue >= amount);
    // No buffer for collateral volatility
}

// SECURE: Overcollateralization
function mint(uint256 amount) external {
    uint256 collateralValue = getCollateralValue();
    require(collateralValue >= amount * 1.5e18 / 1e18, "Insufficient collateral");
    // 150% collateralization ratio
}
```

### Audit Checklist

- [ ] Oracle failure handling
- [ ] Peg manipulation resistance
- [ ] Collateral ratio adequacy
- [ ] Circuit breaker implementation
- [ ] Blacklist functionality
- [ ] Upgrade mechanism security
- [ ] Governance attack resistance

---

## Bridges

### Protocols: Wormhole, Ronin, Nomad

### Unique Attack Vectors

#### Validator Set Compromise
```solidity
// VULNERABLE: Low threshold
uint256 public constant REQUIRED_SIGNATURES = 5;
uint256 public constant TOTAL_VALIDATORS = 9;

// SECURE: Higher threshold
uint256 public constant REQUIRED_SIGNATURES = 8;
uint256 public constant TOTAL_VALIDATORS = 15;
```

#### Message Replay
```solidity
// VULNERABLE: No replay protection
function executeMessage(bytes memory message) external {
    // Can replay same message multiple times
}

// SECURE: Replay protection
mapping(bytes32 => bool) public executedMessages;

function executeMessage(bytes memory message) external {
    bytes32 messageHash = keccak256(message);
    require(!executedMessages[messageHash], "Already executed");
    executedMessages[messageHash] = true;
    // Execute message
}
```

### Audit Checklist

- [ ] Validator set security
- [ ] Signature threshold adequacy
- [ ] Message replay protection
- [ ] Liquidity adequacy
- [ ] Upgrade mechanism security
- [ ] Emergency pause functionality
- [ ] Admin key security

---

## Perpetuals

### Protocols: dYdX, GMX, GNS

### Unique Attack Vectors

#### Oracle Latency
```solidity
// VULNERABLE: Instant oracle updates
function updatePrice(uint256 newPrice) external onlyOracle {
    price = newPrice;
    // Can be front-run
}

// SECURE: Delayed oracle updates
function updatePrice(uint256 newPrice) external onlyOracle {
    pendingPrice = newPrice;
    priceUpdateTime = block.timestamp;
}

function executeTrade() external {
    require(block.timestamp >= priceUpdateTime + 1 hours, "Oracle delay");
    // Use pendingPrice
}
```

#### Funding Rate Manipulation
```solidity
// VULNERABLE: No funding rate limits
function updateFundingRate(int256 rate) external onlyOracle {
    fundingRate = rate;
    // Can be manipulated to liquidate positions
}

// SECURE: Funding rate limits
int256 public constant MAX_FUNDING_RATE = 1e16; // 1%

function updateFundingRate(int256 rate) external onlyOracle {
    require(rate <= MAX_FUNDING_RATE && rate >= -MAX_FUNDING_RATE, "Rate too high");
    fundingRate = rate;
}
```

#### Liquidation Cascades
```solidity
// VULNERABLE: No liquidation batching
function liquidate(address user) external {
    // Can cause cascading liquidations
}

// SECURE: Liquidation batching
function liquidateBatch(address[] memory users) external {
    // Process liquidations in batches to prevent cascades
}
```

### Audit Checklist

- [ ] Oracle latency handling
- [ ] Funding rate limits
- [ ] Liquidation cascade prevention
- [ ] Position size limits
- [ ] Insurance fund adequacy
- [ ] Emergency pause functionality
- [ ] Admin key security

---

## Liquid Staking

### Protocols: Lido, Rocket Pool

### Unique Attack Vectors

#### Oracle Manipulation
```solidity
// VULNERABLE: Spot price for staking rewards
function claimRewards() external {
    uint256 rewards = getSpotRewards();
    // Can be manipulated
}

// SECURE: TWAP for rewards
function claimRewards() external {
    uint256 rewards = getTWARewards(1 days);
}
```

#### Validator Slashing
```solidity
// VULNERABLE: No slashing protection
function stake() external payable {
    // No protection against validator slashing
}

// SECURE: Slashing insurance
function stake() external payable {
    uint256 insurance = msg.value * 5 / 100; // 5% insurance
    insuranceFund += insurance;
    // Use remaining for staking
}
```

#### Depeg Risk
```solidity
// VULNERABLE: No depeg protection
function unstake() external {
    uint256 ethAmount = stakedAmount * exchangeRate / 1e18;
    // No protection against depeg
}

// SECURE: Depeg protection
function unstake() external {
    uint256 ethAmount = stakedAmount * exchangeRate / 1e18;
    require(exchangeRate >= 0.95e18, "Depeg protection");
}
```

### Audit Checklist

- [ ] Oracle manipulation resistance
- [ ] Validator slashing protection
- [ ] Depeg risk mitigation
- [ ] Withdrawal queue fairness
- [ ] Admin key security
- [ ] Emergency pause functionality
- [ ] Reward distribution accuracy

---

## Restaking

### Protocols: EigenLayer

### Unique Attack Vectors

#### Slashing Cascade
```solidity
// VULNERABLE: No slashing limits
function slash(address operator, uint256 amount) external {
    // Can cascade across multiple AVS
}

// SECURE: Slashing limits
mapping(address => uint256) public slashedAmount;
uint256 public constant MAX_SLASHING = 30e16; // 30%

function slash(address operator, uint256 amount) external {
    require(slashedAmount[operator] + amount <= MAX_SLASHING * stake, "Slashing limit");
    slashedAmount[operator] += amount;
}
```

#### Operator Collusion
```solidity
// VULNERABLE: No operator diversity check
function registerOperator(address operator) external {
    // No check for operator collusion
}

// SECURE: Operator diversity
mapping(address => bool) public registeredOperators;

function registerOperator(address operator) external {
    require(!registeredOperators[operator], "Already registered");
    require(getOperatorDiversity() >= MIN_DIVERSITY, "Insufficient diversity");
    registeredOperators[operator] = true;
}
```

#### AVS Security
```solidity
// VULNERABLE: No AVS validation
function registerAVS(address avs) external {
    // No validation of AVS security
}

// SECURE: AVS validation
function registerAVS(address avs) external {
    require(getAVSSecurityScore(avs) >= MIN_SECURITY_SCORE, "Insufficient security");
    registeredAVS[avs] = true;
}
```

### Audit Checklist

- [ ] Slashing cascade prevention
- [ ] Operator collusion resistance
- [ ] AVS security validation
- [ ] Withdrawal queue fairness
- [ ] Admin key security
- [ ] Emergency pause functionality
- [ ] Reward distribution accuracy

---

## Options

### Protocols: Lyra, Premia

### Unique Attack Vectors

#### Oracle Manipulation
```solidity
// VULNERABLE: Spot price for option pricing
function getOptionPrice() public view returns (uint256) {
    return getSpotPrice() * volatility;
    // Can be manipulated
}

// SECURE: TWAP for option pricing
function getOptionPrice() public view returns (uint256) {
    return getTWAP(1 hours) * volatility;
}
```

#### Liquidation Manipulation
```solidity
// VULNERABLE: No liquidation batching
function liquidate(address user) external {
    // Can be front-run
}

// SECURE: Liquidation batching
function liquidateBatch(address[] memory users) external {
    // Process in batches
}
```

#### Premium Calculation
```solidity
// VULNERABLE: Incorrect premium calculation
function calculatePremium(uint256 strike, uint256 expiry) public view returns (uint256) {
    return strike * volatility * timeToExpiry;
    // Can be manipulated
}

// SECURE: Use Black-Scholes
function calculatePremium(uint256 strike, uint256 expiry) public view returns (uint256) {
    return blackScholes(currentPrice, strike, volatility, timeToExpiry);
}
```

### Audit Checklist

- [ ] Oracle manipulation resistance
- [ ] Liquidation manipulation prevention
- [ ] Premium calculation accuracy
- [ ] Collateral ratio adequacy
- [ ] Exercise mechanism correctness
- [ ] Admin key security
- [ ] Emergency pause functionality

---

## RWA (Real World Assets)

### Protocols: Centrifuge, Maple

### Unique Attack Vectors

#### Oracle Failure
```solidity
// VULNERABLE: Single oracle for asset valuation
function getValue() public view returns (uint256) {
    return getOracleValue();
    // Single oracle can fail
}

// SECURE: Multiple oracles
function getValue() public view returns (uint256) {
    uint256 value1 = getOracle1Value();
    uint256 value2 = getOracle2Value();
    return (value1 + value2) / 2;
}
```

#### Collateral Default
```solidity
// VULNERABLE: No default protection
function borrow(uint256 amount) external {
    uint256 collateralValue = getCollateralValue();
    require(collateralValue >= amount);
    // No protection against default
}

// SECURE: Overcollateralization
function borrow(uint256 amount) external {
    uint256 collateralValue = getCollateralValue();
    require(collateralValue >= amount * 1.5e18 / 1e18, "Insufficient collateral");
}
```

#### Legal Compliance
```solidity
// VULNERABLE: No compliance checks
function transfer(address to, uint256 amount) external {
    // No compliance checks
}

// SECURE: Compliance checks
function transfer(address to, uint256 amount) external {
    require(isWhitelisted(to), "Not whitelisted");
    require(isCompliant(to), "Not compliant");
}
```

### Audit Checklist

- [ ] Oracle failure handling
- [ ] Collateral default protection
- [ ] Legal compliance
- [ ] Asset valuation accuracy
- [ ] Admin key security
- [ ] Emergency pause functionality
- [ ] Governance attack resistance

---

## General Audit Checklist (All Protocols)

### Access Control
- [ ] Admin key security
- [ ] Multi-sig implementation
- [ ] Timelock for sensitive operations
- [ ] Role-based access control

### Oracle Security
- [ ] Oracle manipulation resistance
- [ ] Multiple oracle sources
- [ ] Circuit breakers
- [ ] TWAP implementation

### Economic Security
- [ ] Flash loan resistance
- [ ] Governance attack resistance
- [ ] Inflation attack resistance
- [ ] Donation attack resistance

### Operational Security
- [ ] Emergency pause functionality
- [ ] Upgrade mechanism security
- [ ] Monitoring and alerting
- [ ] Incident response plan

### Code Quality
- [ ] Test coverage > 80%
- [ ] Fuzzing executed
- [ ] Formal verification (if applicable)
- [ ] Documentation complete
