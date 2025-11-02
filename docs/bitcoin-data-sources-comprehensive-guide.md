# Bitcoin Data Sources: Comprehensive API Guide

**Version**: 2.1 | **Last Updated**: 2024-08-29 | **Status**: Active
**Authority**: Research Team | **Audience**: Data Analysts & Developers

*A complete reference for Bitcoin data infrastructure across all aspects of the ecosystem*

## Executive Summary

This comprehensive guide catalogs over 80 Bitcoin data sources across 12 critical categories, from on-chain analytics to institutional flows. Whether you're building trading algorithms, conducting research, or developing applications, this document provides the definitive map of Bitcoin's data infrastructure.

**Key Categories Covered:**
- On-Chain & Blockchain Data
- Market Data & Trading APIs
- Derivatives & Options Data
- Order Books & Market Depth
- ETF & Institutional Flows
- Mining & Network Metrics
- Social Sentiment & Fear/Greed Indices
- Compliance & AML Screening
- Whale Tracking & Large Transactions
- Lightning Network Data
- DeFi & Wrapped Bitcoin
- Technical Indicators & Trading Signals

---

## 🔗 On-Chain Analytics & Blockchain Data

### Enterprise Solutions

**Chainalysis**
- **Purpose**: Professional-grade blockchain analytics with court-admissible data
- **Key Features**: Advanced ML clustering, government-grade compliance, real-time monitoring
- **Pricing**: Enterprise only
- **Best For**: Compliance, investigations, institutional analysis
- **API Access**: REST API with comprehensive documentation

**Glassnode**
- **Purpose**: Leading on-chain metrics and institutional-grade analytics
- **Key Features**: 200+ on-chain metrics, market intelligence, professional reports
- **Pricing**: Free tier + paid plans starting $29/month
- **Best For**: Trading strategies, market analysis, institutional research
- **API Access**: REST API with Python/R libraries

**Bitquery**
- **Purpose**: Multi-blockchain data platform with real-time capabilities
- **Key Features**: GraphQL APIs, WebSocket streams, SQL access, 40+ chains
- **Pricing**: Free tier + usage-based pricing
- **Best For**: Cross-chain analysis, real-time applications
- **API Access**: GraphQL, WebSocket, SQL, Cloud providers (AWS, Snowflake)

### Developer-Friendly Options

**Blockchain.com API**
- **Purpose**: Bitcoin blockchain explorer with comprehensive data
- **Key Features**: Real-time stats, wallet info, transaction data, network metrics
- **Pricing**: **FREE**
- **Best For**: Basic blockchain data, educational projects
- **API Access**: REST API, no authentication required

**Blockstream Explorer API**
- **Purpose**: Bitcoin and Liquid network data with high reliability
- **Key Features**: 99.9% SLA, mempool monitoring, fee estimation
- **Pricing**: Free tier (30 days) + paid plans
- **Best For**: Production applications, Lightning integration
- **API Access**: REST API with comprehensive endpoints

**Mempool.space API**
- **Purpose**: Open-source Bitcoin explorer with full API access
- **Key Features**: Mempool analysis, fee estimation, transaction broadcasting
- **Pricing**: **FREE**
- **Best For**: Real-time mempool data, fee optimization
- **API Access**: REST API, fully documented

### Infrastructure Providers

**CoinMetrics**
- **Purpose**: Institutional-grade crypto data with academic rigor
- **Key Features**: Network data, market data, comprehensive coverage
- **Pricing**: Free tier + enterprise plans
- **Best For**: Research, backtesting, institutional analysis
- **API Access**: REST API with extensive historical data

**QuickNode**
- **Purpose**: Web3 infrastructure with multi-chain support
- **Key Features**: Low latency, global endpoints, 16+ chains
- **Pricing**: Free tier + usage-based
- **Best For**: Application development, high-frequency access
- **API Access**: RPC methods in multiple languages

---

## 📈 Market Data & Trading APIs

### Primary Market Data

**CoinGecko API**
- **Purpose**: Comprehensive cryptocurrency market data
- **Key Features**: 13,000+ coins, historical data, DeFi metrics
- **Pricing**: **FREE** (50 calls/month) + paid tiers
- **Best For**: General market data, portfolio tracking
- **API Access**: REST API with extensive documentation

**CoinMarketCap API**
- **Purpose**: Leading crypto market data provider
- **Key Features**: Real-time prices, market cap data, global metrics
- **Pricing**: **FREE** basic tier + professional plans
- **Best For**: Market overviews, comparative analysis
- **API Access**: REST API with WebSocket for real-time data

**CryptoCompare**
- **Purpose**: High-reliability market data with institutional focus
- **Key Features**: 180M requests/hour capacity, 800+ trades/second
- **Pricing**: Free tier + enterprise solutions
- **Best For**: High-frequency trading, enterprise applications
- **API Access**: REST + WebSocket APIs

### Exchange APIs (Free)

**Binance Public API**
- **Purpose**: World's largest crypto exchange data
- **Key Features**: Real-time market data, order books, klines
- **Pricing**: **FREE** (no authentication required)
- **Best For**: Real-time trading data, arbitrage
- **API Access**: REST + WebSocket with comprehensive endpoints

**Kraken Public API**
- **Purpose**: Established exchange with robust API
- **Key Features**: Market data, order books, recent trades
- **Pricing**: **FREE** public endpoints
- **Best For**: Reliable market data, European markets
- **API Access**: REST API with clear documentation

**Coinbase Pro API**
- **Purpose**: Major US exchange public data
- **Key Features**: Real-time market data, historical candles
- **Pricing**: **FREE** public endpoints
- **Best For**: US market focus, institutional data
- **API Access**: REST + WebSocket APIs

---

## 🎯 Derivatives Data (Futures/Options/Perpetuals)

### Premium Solutions

**Tardis.dev**
- **Purpose**: Most granular derivatives data available
- **Key Features**: Tick-level data, L2/L3 order books, historical depth
- **Pricing**: Paid service with various tiers
- **Best For**: Quantitative trading, academic research
- **API Access**: REST API + downloadable datasets

**CoinDesk Data**
- **Purpose**: Institutional-grade derivatives analytics
- **Key Features**: 98% market coverage, tick-level granularity
- **Pricing**: Enterprise pricing
- **Best For**: Professional trading, market making
- **API Access**: REST API with extensive derivative instruments

**Amberdata AD Derivatives**
- **Purpose**: Comprehensive derivatives analytics platform
- **Key Features**: Futures, perpetuals, options across venues
- **Pricing**: Professional service
- **Best For**: Institutional derivatives trading
- **API Access**: REST API + AWS S3 delivery

### Community & Free Options

**CoinGlass**
- **Purpose**: Derivatives market overview and analytics
- **Key Features**: Open interest, liquidations, funding rates
- **Pricing**: **FREE** with premium features
- **Best For**: Market sentiment, liquidation tracking
- **API Access**: Web-based with some API endpoints

**CoinAPI**
- **Purpose**: Unified access to derivative markets
- **Key Features**: Multi-exchange coverage, normalized data
- **Pricing**: Free tier + paid plans
- **Best For**: Multi-exchange derivatives data
- **API Access**: REST API with unified format

---

## 📊 Order Book & Market Depth

### Unified Access

**CoinAPI**
- **Purpose**: Single API for multiple exchange order books
- **Key Features**: L1/L2/L3 data, unified format across exchanges
- **Pricing**: **FREE** tier + paid plans
- **Best For**: Cross-exchange arbitrage, market analysis
- **API Access**: REST + WebSocket APIs

**Shrimpy API**
- **Purpose**: Universal order book access
- **Key Features**: Major exchanges, completely free access
- **Pricing**: **FREE** (no sign-up required)
- **Best For**: Educational projects, basic market depth
- **API Access**: Single API endpoint for multiple exchanges

### Granular Data

**Tardis.dev**
- **Purpose**: Tick-level order book updates
- **Key Features**: L2/L3 data, historical tick updates
- **Pricing**: Paid service
- **Best For**: HFT strategies, detailed market microstructure
- **API Access**: REST API + real-time streaming

**CoinDesk Data**
- **Purpose**: Institutional order book analytics
- **Key Features**: 99.8% market coverage, maximum depth
- **Pricing**: Enterprise pricing
- **Best For**: Professional market making
- **API Access**: REST API + WebSocket streams

### Direct Exchange Access

**Exchange WebSocket APIs**
- **Purpose**: Direct real-time order book feeds
- **Key Features**: Lowest latency, exchange-specific optimizations
- **Pricing**: **FREE** (Binance, Kraken, Coinbase)
- **Best For**: Real-time trading applications
- **API Access**: WebSocket with exchange-specific protocols

---

## 🏦 ETF Flows & Institutional Tracking

### API Solutions

**Amberdata**
- **Purpose**: Comprehensive institutional data platform
- **Key Features**: ETF holdings/flows, real-time institutional tracking
- **Pricing**: Enterprise pricing
- **Best For**: Institutional analysis, compliance monitoring
- **API Access**: REST API + cloud integrations (BigQuery, Snowflake)

### Real-Time Tracking Platforms

**SoSoValue ETF Dashboard**
- **Purpose**: Comprehensive Bitcoin ETF tracking
- **Key Features**: Real-time flows, historical data, major ETF coverage
- **Pricing**: **FREE** web access
- **Best For**: ETF flow monitoring, institutional sentiment
- **API Access**: Web-based platform

**Farside Investors**
- **Purpose**: Automated Bitcoin ETF flow tracking
- **Key Features**: Daily flow data, London-based analysis
- **Pricing**: **FREE** data tables
- **Best For**: Daily ETF flow analysis
- **API Access**: Web-based with automated updates

**CoinGlass ETF Tracker**
- **Purpose**: Bitcoin ETF comprehensive tracking
- **Key Features**: Flows, trading volume, market cap analysis
- **Pricing**: **FREE** basic access
- **Best For**: ETF market overview
- **API Access**: Web-based platform

**Apollo Bitcoin Tracker**
- **Purpose**: Institutional and corporate treasury tracking
- **Key Features**: ETF data + corporate treasury holdings
- **Pricing**: **FREE** access
- **Best For**: Comprehensive institutional analysis
- **API Access**: Web-based tracker

---

## ⛏️ Mining & Network Metrics

### API Providers

**CoinMetrics API**
- **Purpose**: Institutional-grade mining analytics
- **Key Features**: Hash rate, difficulty, mining economics
- **Pricing**: Free tier + paid plans
- **Best For**: Research, network analysis
- **API Access**: REST API with comprehensive mining metrics

**minerstat API**
- **Purpose**: Mining-focused data platform
- **Key Features**: ASIC/GPU data, profitability calculations
- **Pricing**: **FREE** tier + paid features
- **Best For**: Mining operations, hardware analysis
- **API Access**: REST API for mining-specific data

**Blockchain.com Charts**
- **Purpose**: Basic network statistics
- **Key Features**: Hash rate estimation, network difficulty
- **Pricing**: **FREE**
- **Best For**: Basic network monitoring
- **API Access**: Web-based charts with some API endpoints

### Specialized Platforms

**Hashrate Index**
- **Purpose**: Bitcoin mining industry analytics
- **Key Features**: ASIC pricing, pool tracking, profitability
- **Pricing**: Mixed (free data + paid analysis)
- **Best For**: Mining industry analysis
- **API Access**: Web-based with some API endpoints

**Bitcoin Visuals**
- **Purpose**: Network capacity and statistics
- **Key Features**: Historical network data, visualization tools
- **Pricing**: **FREE**
- **Best For**: Network analysis, educational content
- **API Access**: Web-based platform

---

## 😨 Social Sentiment & Fear/Greed Indices

### Comprehensive Sentiment APIs

**BittsAnalytics**
- **Purpose**: Machine learning-based sentiment analysis
- **Key Features**: 1M+ tweets daily, news sentiment, investor index
- **Pricing**: Subscription required for API
- **Best For**: Sophisticated sentiment analysis
- **API Access**: REST API with ML-powered insights

### Popular Indices (Free)

**Alternative.me Crypto Fear & Greed Index**
- **Purpose**: Most popular crypto sentiment indicator
- **Key Features**: Daily updates, multiple data sources, 0-100 scale
- **Pricing**: **FREE**
- **Best For**: General market sentiment tracking
- **API Access**: Simple API endpoints

**CoinMarketCap Fear & Greed Index**
- **Purpose**: CMC's proprietary sentiment index
- **Key Features**: Top 10 crypto analysis, social metrics
- **Pricing**: **FREE** API access
- **Best For**: Mainstream sentiment analysis
- **API Access**: REST API integration

**CoinStats Fear & Greed**
- **Purpose**: 12-hour updated sentiment index
- **Key Features**: Regular updates, simple integration
- **Pricing**: **FREE**
- **Best For**: Automated sentiment tracking
- **API Access**: REST API endpoints

---

## 🔒 Compliance & AML/Sanctions Screening

### Enterprise Solutions

**Chainalysis**
- **Purpose**: Industry-leading compliance platform
- **Key Features**: AML screening, sanctions compliance, risk scoring
- **Pricing**: Enterprise + **FREE** basic sanctions screening
- **Best For**: Financial institutions, compliance programs
- **API Access**: REST API + smart contract oracles

**Scorechain**
- **Purpose**: Real-time AML compliance API
- **Key Features**: Risk scoring, global sanctions coverage, behavioral analysis
- **Pricing**: Paid service with API access
- **Best For**: Crypto businesses, automated compliance
- **API Access**: REST API for real-time screening

**Elliptic**
- **Purpose**: Wallet and transaction screening platform
- **Key Features**: 70+ risk categories, broad network coverage
- **Pricing**: Enterprise pricing
- **Best For**: Streamlined compliance workflows
- **API Access**: Comprehensive screening APIs

### Accessible Options

**AMLBot**
- **Purpose**: AML compliance tools with API integration
- **Key Features**: ISO 27001 certified, 24/7 support, automated verification
- **Pricing**: Various tiers available
- **Best For**: Mid-sized crypto businesses
- **API Access**: API integration for existing systems

**Sanction Scanner**
- **Purpose**: Automated AML compliance for crypto exchanges
- **Key Features**: Reduces false positives, flexible APIs
- **Pricing**: Various pricing tiers
- **Best For**: Crypto exchanges, automated screening
- **API Access**: Powerful API support

---

## 🐋 Whale Tracking & Large Transactions

### Premium Services

**Whale Alert**
- **Purpose**: Industry leader in whale transaction monitoring
- **Key Features**: Multi-blockchain coverage, 2.4M Twitter followers
- **Pricing**: **FREE** Twitter alerts + paid API ($49/month+)
- **Best For**: Real-time whale tracking, market alerts
- **API Access**: Enterprise Priority Alerts API + WebSocket

**Nansen**
- **Purpose**: Advanced on-chain analytics platform
- **Key Features**: Smart alerts, wallet labeling, token insights
- **Pricing**: Paid subscription service
- **Best For**: Professional on-chain analysis
- **API Access**: Advanced analytics platform with API

### Community Options

**Cryptocurrency Alerting**
- **Purpose**: Automated whale transaction discovery
- **Key Features**: ETH/BSC coverage, multiple notification methods
- **Pricing**: $3.99/month basic, $19.99/month pro
- **Best For**: Affordable whale tracking
- **API Access**: Alert system with API integration

**Whalemap**
- **Purpose**: Bitcoin-focused whale analysis
- **Key Features**: Support/resistance levels, Telegram integration
- **Pricing**: **FREE** basic access
- **Best For**: Bitcoin trading strategies
- **API Access**: Telegram Mini App

**Arkham Intelligence**
- **Purpose**: Comprehensive wallet tracking
- **Key Features**: **FREE** alerts, customizable tracking
- **Pricing**: **FREE** with paid premium features
- **Best For**: Custom whale monitoring
- **API Access**: Web-based with alert system

---

## ⚡ Lightning Network Data

### Direct APIs

**LND REST/gRPC API**
- **Purpose**: Lightning Network Daemon direct access
- **Key Features**: Complete Lightning functionality, channel management
- **Pricing**: **FREE** (self-hosted)
- **Best For**: Lightning application development
- **API Access**: REST + gRPC with comprehensive documentation

**BTCPay Server Lightning API**
- **Purpose**: Lightning integration for payments
- **Key Features**: Payment processing, invoice management
- **Pricing**: **FREE** (self-hosted)
- **Best For**: Lightning payment applications
- **API Access**: REST API for payment processing

### Explorer & Analytics

**Mempool.space Lightning**
- **Purpose**: Lightning Network explorer
- **Key Features**: Node explorer, channel tracking
- **Pricing**: **FREE**
- **Best For**: Lightning network analysis
- **API Access**: REST API for Lightning data

**Amboss Space**
- **Purpose**: Lightning explorer and analytics
- **Key Features**: Node search, channel analytics, notifications
- **Pricing**: **FREE** explorer + premium features
- **Best For**: Lightning network intelligence
- **API Access**: Web-based platform

**1ML (1 Million Lightning)**
- **Purpose**: Lightning Network search and analysis
- **Key Features**: Network-wide statistics, node/channel search
- **Pricing**: **FREE**
- **Best For**: Lightning network research
- **API Access**: Web-based with search capabilities

**Bitcoin Visuals Lightning**
- **Purpose**: Lightning capacity and statistics
- **Key Features**: Historical capacity data, network metrics
- **Pricing**: **FREE**
- **Best For**: Lightning network analysis
- **API Access**: Web-based charts and statistics

---

## 🔄 DeFi & Wrapped Bitcoin

### TVL Aggregators

**DefiLlama**
- **Purpose**: Comprehensive DeFi data aggregation
- **Key Features**: $93B+ TVL tracked, completely free, open-source
- **Pricing**: **FREE**
- **Best For**: DeFi analytics, TVL tracking
- **API Access**: REST API with comprehensive DeFi data

**DeFi Pulse**
- **Purpose**: DeFi protocol tracking
- **Key Features**: Basic TVL and protocol data
- **Pricing**: **FREE** basic access
- **Best For**: DeFi protocol overview
- **API Access**: Web-based platform

### Protocol APIs

**Aave API**
- **Purpose**: Leading DeFi lending protocol
- **Key Features**: Lending rates, reserve data, governance
- **Pricing**: **FREE** public data
- **Best For**: DeFi lending analysis
- **API Access**: GraphQL API

**Compound API**
- **Purpose**: Autonomous interest rate protocol
- **Key Features**: Interest rates, market data, governance
- **Pricing**: **FREE** public data
- **Best For**: DeFi interest rate tracking
- **API Access**: REST API with market data

**Uniswap API**
- **Purpose**: Leading DEX protocol data
- **Key Features**: Trading data, liquidity pools, token metrics
- **Pricing**: **FREE** public data
- **Best For**: DEX analytics, token trading
- **API Access**: GraphQL API (The Graph)

---

## 📊 Technical Indicators & Trading Signals

### Comprehensive Solutions

**TAAPI.IO**
- **Purpose**: 200+ technical analysis indicators API
- **Key Features**: Real-time calculations, multiple assets, backtesting
- **Pricing**: **FREE** tier + paid plans
- **Best For**: Automated trading, technical analysis
- **API Access**: REST API with 200+ indicators

**Quantify Crypto**
- **Purpose**: Specialized crypto technical analysis
- **Key Features**: ML-enhanced indicators, trend algorithms
- **Pricing**: Paid service
- **Best For**: Advanced technical analysis
- **API Access**: Research-grade API access

### Free Options

**TradingView**
- **Purpose**: Popular charting platform
- **Key Features**: **FREE** basic indicators, community scripts
- **Pricing**: **FREE** with premium features
- **Best For**: Chart analysis, community indicators
- **API Access**: Limited API access

**Investing.com Technical Analysis**
- **Purpose**: Real-time technical analysis data
- **Key Features**: Multiple timeframes, various indicators
- **Pricing**: **FREE** basic access
- **Best For**: Quick technical overview
- **API Access**: Web-based with some API endpoints

**Barchart Technical Analysis**
- **Purpose**: Technical analysis summary for Bitcoin
- **Key Features**: Moving averages, oscillators, summary scores
- **Pricing**: **FREE** basic data
- **Best For**: Technical analysis overview
- **API Access**: Web-based platform

---

## 💰 Free Tier Summary

### Best Free Starting Points

| **Service** | **Category** | **Free Limits** | **Best For** |
|-------------|--------------|-----------------|--------------|
| **Mempool.space** | On-chain | Unlimited | Bitcoin blockchain data |
| **CoinGecko** | Market Data | 50 calls/month | General market data |
| **DefiLlama** | DeFi | Unlimited | DeFi/wrapped Bitcoin |
| **Alternative.me** | Sentiment | Unlimited | Fear & Greed tracking |
| **Blockchain.com** | On-chain | Unlimited | Basic Bitcoin metrics |
| **Binance API** | Market Data | Rate limited | Real-time trading data |
| **Shrimpy** | Order Books | Unlimited | Cross-exchange order books |
| **Whale Alert** | Whale Tracking | Twitter alerts | Large transaction alerts |
| **Bitcoin Visuals** | Mining/Lightning | Unlimited | Network statistics |
| **TAAPI.IO** | Technical | Limited calls | Technical indicators |

### Free Tier Limitations

**Common Restrictions:**
- Rate limiting (100-1000 requests/month typical)
- Historical data limitations (30-90 days)
- No commercial use restrictions
- Basic features only
- No guaranteed uptime/SLA
- Limited support

---

## 🔧 Integration Guidelines

### API Selection Criteria

**For Trading Applications:**
1. **Real-time Requirements**: WebSocket APIs (Binance, Kraken)
2. **Historical Analysis**: CoinMetrics, Glassnode
3. **Cross-exchange**: CoinAPI, Shrimpy
4. **Order Books**: Tardis.dev (premium), exchange APIs (free)

**For Research Projects:**
1. **On-chain Analysis**: Mempool.space, Blockchain.com
2. **Market Data**: CoinGecko, CoinMarketCap
3. **Sentiment**: Alternative.me, BittsAnalytics
4. **Network Stats**: Bitcoin Visuals, CoinMetrics

**For Compliance Applications:**
1. **AML Screening**: Chainalysis (enterprise), basic free tools
2. **Transaction Monitoring**: Scorechain, Elliptic
3. **Risk Assessment**: Multiple providers for redundancy

### Technical Implementation Notes

**Authentication Patterns:**
- **API Keys**: Most services require registration
- **Rate Limiting**: Implement exponential backoff
- **Error Handling**: Plan for service outages
- **Data Caching**: Reduce API calls with local caching

**Data Quality Considerations:**
- **Multiple Sources**: Cross-validate critical data
- **Real-time vs Batch**: Choose appropriate update frequency
- **Historical Availability**: Verify data retention periods
- **Format Standardization**: Normalize data across sources

---

## 🧮 Advanced On-Chain Metrics: DIY Calculation Guide

*Calculate professional-grade Bitcoin indicators using only free APIs and open-source data*

### Overview

While premium services like Glassnode charge $29-799/month for advanced on-chain metrics, you can calculate these same indicators yourself using free APIs. This section provides formulas, data sources, and implementation guidance for the most important Bitcoin on-chain metrics.

### 1. **MVRV Z-Score**

**What it measures**: Market overvaluation/undervaluation by comparing market value to realized value in standard deviations

**Formula**:
```
MVRV Z-Score = (Market Value - Realized Value) / Standard Deviation of Market Value
```

**Free Data Sources**:
- **Market Cap**: CoinGecko API (`/coins/bitcoin`), CoinMarketCap API
- **Realized Cap**: Calculate from UTXO data + historical prices
  - UTXO data: Mempool.space API (`/api/address/{address}/utxo`)
  - Historical prices: CoinGecko (`/coins/bitcoin/market_chart/range`)
- **Alternative**: Blockchain.com Charts API (limited MVRV data)

**Implementation Steps**:
1. Fetch current market cap from CoinGecko
2. Calculate realized cap by summing (UTXO value × price when UTXO created)
3. Calculate rolling standard deviation of market cap (typically 30-day window)
4. Apply formula

**Interpretation**:
- Above 7: Market likely in bubble territory
- Below 0: Market undervalued, potential accumulation zone

### 2. **SOPR (Spent Output Profit Ratio)**

**What it measures**: Whether Bitcoin holders are selling at profit or loss on average

**Formula**:
```
SOPR = (Value × Price_spent) / (Value × Price_created)
```

**Free APIs**:
- **UTXO Data**: Mempool.space
  - `/api/address/{address}/utxo` - Current UTXOs
  - `/api/address/{address}/txs` - Transaction history
- **Price History**: CoinGecko, Yahoo Finance API

**Variants to Calculate**:
- **aSOPR (Adjusted)**: Filter out UTXOs held < 1 hour
- **STH-SOPR**: Only UTXOs held < 155 days
- **LTH-SOPR**: Only UTXOs held > 155 days

**Implementation**:
```python
# Pseudo-code structure
for each spent_output:
    price_created = get_historical_price(output.created_time)
    price_spent = get_historical_price(output.spent_time)
    sopr = (output.value * price_spent) / (output.value * price_created)
```

**Interpretation**:
- SOPR > 1: Coins sold at profit on average
- SOPR < 1: Coins sold at loss on average

### 3. **Realized Price**

**What it measures**: The average price at which all bitcoins last moved on-chain

**Formula**:
```
Realized Price = Realized Cap / Total Bitcoin Supply
```

**Free Data Sources**:
- **CoinMetrics Community API**: `https://community-api.coinmetrics.io/v4`
  - Endpoint: `/timeseries/asset-metrics`
  - Metrics: `CapRealUSD`, `SplyCur`
- **Alternative Calculation**:
  - Parse blockchain for all UTXOs
  - Sum (UTXO amount × price when created)
  - Divide by total supply

**Quick Access**: Some realized price data available on Blockchain.com Charts

### 4. **NUPL (Net Unrealized Profit/Loss)**

**What it measures**: Overall profit/loss state of Bitcoin holders

**Formula**:
```
NUPL = (Market Cap - Realized Cap) / Market Cap
```

**Components**: Same data sources as MVRV
- Market Cap: Any price API × circulating supply
- Realized Cap: Calculate as in MVRV section

**LTH/STH Variants**:
- **LTH-NUPL**: Filter for coins held > 155 days
- **STH-NUPL**: Filter for coins held < 155 days

**Interpretation**:
- > 0.75: Euphoria/Greed
- 0.5-0.75: Belief
- 0-0.5: Optimism
- < 0: Capitulation

### 5. **Long-Term Holder (LTH) / Short-Term Holder (STH) Metrics**

**Definition**: 155-day threshold separates long-term from short-term holders

**Free Calculation Method**:
1. Parse transaction history from Mempool.space
2. Calculate coin age for each UTXO
3. Classify as LTH (>155 days) or STH (<155 days)
4. Calculate supply, realized price for each cohort

**Key Metrics**:
- **LTH Supply**: Total BTC held > 155 days
- **STH Supply**: Total BTC held < 155 days
- **LTH/STH Realized Price**: Average cost basis for each group

### 6. **Bitcoin Hash Ribbons**

**What it measures**: Miner capitulation and recovery signals

**Components**:
- 30-day Simple Moving Average of Hash Rate
- 60-day Simple Moving Average of Hash Rate

**Free Data Source**:
- Blockchain.com API: `/charts/hash-rate`
- Alternative: CoinMetrics Community API

**Signal Generation**:
- **Capitulation**: 30-day MA crosses below 60-day MA
- **Recovery**: 30-day MA crosses back above 60-day MA
- **Buy Signal**: Recovery + price momentum confirmation

### 7. **Puell Multiple**

**What it measures**: Mining profitability relative to historical average

**Formula**:
```
Puell Multiple = Daily Mining Revenue (USD) / 365-day MA of Mining Revenue
```

**Calculation**:
```
Daily Mining Revenue = Daily Blocks × Block Reward × BTC Price
Daily Blocks ≈ 144
Current Block Reward = 6.25 BTC (halves every 4 years)
```

**Free Data**:
- Block data: Blockchain.com API
- Price data: Any market data API

**Interpretation**:
- > 4: Mining highly profitable, potential market top
- < 0.5: Miners under stress, potential market bottom

### 8. **PI Cycle Top Indicator**

**What it measures**: Bitcoin market cycle tops using moving averages

**Formula**:
- **Upper Band**: 111-day Moving Average × 2
- **Lower Band**: 350-day Moving Average × 2
- **Signal**: Upper band crossing above lower band

**Free Data**: Any price API (CoinGecko, Yahoo Finance)

**Implementation**: Simple moving average calculation on daily close prices

### 9. **Additional Metrics (Complex Calculations)**

**CVDD (Cumulative Value Days Destroyed)**
- Requires parsing entire blockchain history
- Complex calculation: Sum of (coin_days_destroyed × price)
- Alternative: Use simplified proxies or pre-calculated when available

**Reserve Risk**
- Formula: `Price / HODL Bank`
- Requires coin age distribution data
- Can approximate using UTXO age analysis

### Implementation Framework

**Recommended Tech Stack**:
```python
# Core Libraries
import requests  # API calls
import pandas as pd  # Data manipulation
import numpy as np  # Calculations
from datetime import datetime, timedelta

# Caching
import sqlite3  # Local price history cache

# Example structure
class OnChainMetrics:
    def __init__(self):
        self.price_cache = PriceCache()
        self.utxo_analyzer = UTXOAnalyzer()

    def calculate_mvrv_z_score(self):
        market_cap = self.get_market_cap()
        realized_cap = self.calculate_realized_cap()
        std_dev = self.calculate_market_cap_std()
        return (market_cap - realized_cap) / std_dev
```

**Optimization Tips**:
1. **Cache Historical Prices**: Store in local database to minimize API calls
2. **Batch API Requests**: Group multiple data requests when possible
3. **Incremental Updates**: Only fetch new data since last calculation
4. **Parallel Processing**: Calculate independent metrics simultaneously

### Data Quality Considerations

**Challenges**:
- UTXO data completeness varies by provider
- Historical price data may have gaps
- Large blockchain parsing can be resource-intensive

**Solutions**:
- Cross-reference multiple data sources
- Implement data validation checks
- Use sampling techniques for large datasets
- Consider cloud computing for intensive calculations

### Example: Complete SOPR Implementation

```python
def calculate_sopr(date_range):
    """Calculate SOPR for a given date range using free APIs"""

    # 1. Get spent transactions for the period
    spent_outputs = get_spent_outputs(date_range)  # From blockchain API

    # 2. Calculate SOPR for each output
    total_realized_value = 0
    total_cost_basis = 0

    for output in spent_outputs:
        # Get prices
        price_created = get_historical_price(output.created_date)
        price_spent = get_historical_price(output.spent_date)

        # Calculate values
        realized_value = output.amount * price_spent
        cost_basis = output.amount * price_created

        total_realized_value += realized_value
        total_cost_basis += cost_basis

    # 3. Return SOPR
    return total_realized_value / total_cost_basis if total_cost_basis > 0 else 1
```

### Resources & Tools

**Open Source Libraries**:
- `python-bitcoinlib`: Bitcoin protocol library
- `blockchain-parser`: Parse blockchain data
- `pandas-ta`: Technical analysis indicators

**Free Data Endpoints Summary**:
- **Mempool.space**: Best for UTXO and transaction data
- **CoinGecko**: Best for price history (10,000+ days)
- **CoinMetrics Community**: Best for calculated on-chain metrics
- **Blockchain.com**: Best for network statistics

**Community Resources**:
- GitHub repositories with indicator implementations
- TradingView Pine Script versions of indicators
- Academic papers with detailed formulas

---

## 🎯 Use Case Matrix

### Trading & Investment

| **Use Case** | **Primary APIs** | **Free Options** |
|--------------|------------------|------------------|
| **Algorithmic Trading** | Binance API, Kraken API, TAAPI.IO | ✅ Binance, Kraken public |
| **Portfolio Tracking** | CoinGecko, CoinMarketCap | ✅ CoinGecko, CMC free tiers |
| **Arbitrage Detection** | CoinAPI, Shrimpy, Exchange APIs | ✅ Shrimpy, exchange APIs |
| **Market Making** | Tardis.dev, CoinDesk Data | ❌ Premium required |
| **Risk Management** | Glassnode, Chainalysis | ⚠️ Limited free options |

### Research & Analysis

| **Use Case** | **Primary APIs** | **Free Options** |
|--------------|------------------|------------------|
| **Academic Research** | CoinMetrics, Glassnode | ⚠️ Limited free access |
| **Market Analysis** | CoinGecko, Alternative.me | ✅ Multiple free sources |
| **On-chain Analysis** | Mempool.space, Blockchain.com | ✅ Comprehensive free data |
| **Network Health** | Bitcoin Visuals, CoinMetrics | ✅ Basic metrics free |
| **Sentiment Analysis** | Alternative.me, social APIs | ✅ Basic sentiment free |

### Compliance & Security

| **Use Case** | **Primary APIs** | **Free Options** |
|--------------|------------------|------------------|
| **AML Screening** | Chainalysis, Scorechain | ⚠️ Basic screening only |
| **Transaction Monitoring** | Elliptic, AMLBot | ❌ Enterprise required |
| **Risk Scoring** | Multiple compliance APIs | ❌ Premium features |
| **Regulatory Reporting** | Enterprise solutions | ❌ Not available free |

### Application Development

| **Use Case** | **Primary APIs** | **Free Options** |
|--------------|------------------|------------------|
| **Wallet Applications** | Blockchain.com, Mempool.space | ✅ Full functionality |
| **Payment Processing** | BTCPay Server, Lightning APIs | ✅ Self-hosted solutions |
| **Block Explorers** | Blockstream, Mempool.space | ✅ Complete API access |
| **DeFi Integration** | DefiLlama, protocol APIs | ✅ Most data free |
| **Mobile Apps** | Lightweight APIs (CoinGecko) | ✅ Mobile-friendly tiers |

---

## 📋 Quick Reference

### Emergency/Essential APIs
For mission-critical applications, maintain access to multiple providers:

**Blockchain Data**: Mempool.space + Blockchain.com + Blockstream
**Market Data**: CoinGecko + Binance API + CoinMarketCap
**Order Books**: Exchange APIs + CoinAPI backup
**Network Status**: Bitcoin Visuals + CoinMetrics
**Sentiment**: Alternative.me + social media APIs

### API Status Monitoring
Monitor these key indicators:
- **Response Times**: <200ms for real-time apps
- **Error Rates**: <1% for production systems
- **Rate Limits**: Track usage across all endpoints
- **Data Freshness**: Verify timestamps on critical data

### Cost Optimization
- **Start Free**: Begin with free tiers, upgrade as needed
- **Batch Requests**: Combine multiple data points per call
- **Cache Strategically**: Store frequently accessed data locally
- **Monitor Usage**: Track API consumption to optimize costs

---

## 🚀 Getting Started Recommendations

### For Beginners
1. **Start with**: Mempool.space + CoinGecko + Alternative.me
2. **Learn**: Basic API concepts, rate limiting, error handling
3. **Build**: Simple portfolio tracker or price monitor
4. **Expand**: Add more data sources as needs grow

### For Developers
1. **Infrastructure**: Set up proper caching and monitoring
2. **Authentication**: Secure API key management
3. **Error Handling**: Implement robust retry logic
4. **Testing**: Use sandbox/testnet environments
5. **Documentation**: Maintain API integration docs

### For Enterprises
1. **Compliance**: Start with Chainalysis for AML requirements
2. **Redundancy**: Multiple providers for critical data
3. **SLAs**: Negotiate service level agreements
4. **Custom Solutions**: Consider dedicated infrastructure
5. **Risk Management**: Implement comprehensive monitoring

---

*This guide represents the current state of Bitcoin data infrastructure as of 2024. The ecosystem evolves rapidly - verify current pricing, features, and availability before implementation.*

**Last Updated**: August 2024
**Sources**: Direct API documentation, provider websites, community feedback
**Maintenance**: This guide should be updated quarterly to reflect ecosystem changes
