# dYdX Python Trading Interface

A higher-level asynchronous Python interface for interacting with the **dYdX decentralized perpetual futures exchange**.

This project was built to simplify programmatic interaction with dYdX by wrapping the lower-level dYdX Python SDK and API functionality behind a cleaner trading interface.

Instead of requiring trading applications to repeatedly interact with separate indexer, node, wallet, market, account, and order APIs, `DydxInterface` provides a centralized abstraction for common trading operations.

The repository contains implementations for both **dYdX v3** and **dYdX v4**, with the v4 interface representing the current implementation.

> **Note:** This is an independent project and is not affiliated with or maintained by dYdX.

---

## Features

### dYdX v4 Interface

The v4 interface provides asynchronous methods for:

* Connecting to dYdX testnet or mainnet
* Initializing a wallet from a mnemonic
* Connecting to the dYdX Indexer
* Connecting directly to a dYdX Chain node
* Fetching account information
* Fetching account equity
* Fetching free collateral
* Fetching open orders
* Fetching historical/current orders
* Fetching open perpetual positions
* Fetching trade fills
* Fetching ETH oracle pricing
* Determining current position size
* Placing limit orders
* Cancelling open orders
* Cancelling multiple orders
* Closing existing positions
* Clearing existing orders and positions
* Managing dYdX wallet sequence numbers
* Retrying transient gRPC failures with exponential backoff
* Logging API and trading activity to both console and file

---

## Why I Built This

The official dYdX SDK exposes the functionality required to interact with the protocol, but using it directly in a larger automated trading system requires coordinating several separate components.

This project creates an application-level abstraction around those components.

For example, application code can initialize one interface:

```python
dydx = await DydxInterface.create(environment="test")
```

and then perform operations such as:

```python
account = await dydx.fetch_account()
positions = await dydx.fetch_open_positions()
orders = await dydx.fetch_open_orders()
price = await dydx.fetch_eth_price()
```

or submit an order through:

```python
await dydx.place_limit_order(
    side_input="buy",
    size=0.01,
    price=2500
)
```

This allows trading strategies, machine-learning systems, bots, and other applications to operate against a simpler interface without duplicating dYdX-specific API logic throughout the rest of the application.

---

## Architecture

The v4 interface combines several components of the dYdX SDK:

```text
Trading Strategy / Application
            │
            ▼
     DydxInterface
            │
    ┌───────┼─────────┐
    │       │         │
    ▼       ▼         ▼
 Indexer   Node      Wallet
    │       │         │
    │       │         └── Transaction signing
    │       │
    │       └──────────── Order submission / cancellation
    │
    └──────────────────── Markets / accounts / positions / fills
```

### Indexer

The dYdX Indexer is used for read-oriented operations including:

* Account information
* Orders
* Positions
* Fills
* Market data
* Oracle pricing

### Node

The dYdX Chain node is used for blockchain operations including:

* Order placement
* Order cancellation
* Current block-height retrieval

### Wallet

The wallet is constructed from the configured dYdX mnemonic and address and is used to sign transactions submitted to the chain.

---

## Repository Structure

```text
DYDXInterface/
│
├── dydx_v4_interface.py
│   └── Current asynchronous dYdX Chain interface
│
├── dydx_v3_interface.py
│   └── Legacy interface built for the dYdX v3 API
│
├── v4-clients/
│   └── dYdX v4 client SDK source/dependencies
│
├── Not For Production/
│   └── Experimental/development code
│
├── Install.txt
│   └── Local SDK installation notes
│
└── interface.log
    └── Runtime logging output
```

---

# Getting Started

## Requirements

* Python 3
* pip
* A dYdX-compatible wallet
* dYdX account/address
* dYdX wallet mnemonic
* Network access to the dYdX Indexer and Chain node

---

## Clone the Repository

```bash
git clone https://github.com/RyanYarbery/DYDXInterface.git
cd DYDXInterface
```

---

## Install the dYdX v4 Python Client

The repository includes the dYdX v4 client source under:

```text
v4-clients/v4-client-py-v2
```

Install it locally with:

```bash
cd v4-clients/v4-client-py-v2
python -m pip install .
cd ../..
```

Using:

```bash
python -m pip
```

instead of invoking `pip` directly can help ensure the package is installed into the Python environment being used to run the application.

---

# Configuration

Credentials are loaded from environment variables instead of being hard-coded into the source.

## Testnet

Configure:

```bash
export dydx_test_address="YOUR_DYDX_TESTNET_ADDRESS"
export dydx_test_mnemonic="YOUR_TESTNET_WALLET_MNEMONIC"
```

Then initialize with:

```python
dydx = await DydxInterface.create(environment="test")
```

---

## Mainnet

Configure:

```bash
export dydx_address="YOUR_DYDX_ADDRESS"
export dydx_mnemonic="YOUR_WALLET_MNEMONIC"
```

Then initialize with:

```python
dydx = await DydxInterface.create(environment="main")
```

> **Security:** Never commit wallet mnemonics, private keys, API credentials, or `.env` files containing secrets to source control.

---

# Usage

Because the v4 SDK relies heavily on asynchronous network operations, the interface uses Python's `asyncio`.

## Basic Example

```python
import asyncio

from dydx_v4_interface import DydxInterface


async def main():
    dydx = await DydxInterface.create(environment="test")

    account = await dydx.fetch_account()
    print("Account:", account)

    equity = await dydx.fetch_equity()
    print("Equity:", equity)

    collateral = await dydx.fetch_free_collateral()
    print("Free collateral:", collateral)

    price = await dydx.fetch_eth_price()
    print("ETH oracle price:", price)


if __name__ == "__main__":
    asyncio.run(main())
```

---

# Account Information

## Fetch Account

```python
account = await dydx.fetch_account()
```

Returns account information including:

```python
{
    "equity": ...,
    "freeCollateral": ...
}
```

---

## Fetch Equity

```python
equity = await dydx.fetch_equity()
```

---

## Fetch Free Collateral

```python
free_collateral = await dydx.fetch_free_collateral()
```

---

# Orders

## Fetch All Orders

```python
orders = await dydx.fetch_orders()
```

---

## Fetch Open Orders

```python
orders = await dydx.fetch_open_orders()
```

---

## Place a Limit Order

```python
transaction = await dydx.place_limit_order(
    side_input="buy",
    size=0.01,
    price=2500
)
```

Sell orders use:

```python
transaction = await dydx.place_limit_order(
    side_input="sell",
    size=0.01,
    price=2600
)
```

The interface constructs the required dYdX order object and submits the transaction through the connected node.

---

## Cancel Open Orders

```python
await dydx.cancel_all_orders()
```

The implementation reconstructs the dYdX `OrderId` objects required for cancellation and submits cancellation transactions to the network.

Wallet sequence numbers are managed as transactions are submitted.

---

# Positions

## Fetch Open Positions

```python
positions = await dydx.fetch_open_positions()
```

---

## Fetch Current Position Size

```python
size = await dydx.fetch_position_size()
```

The current implementation assumes the trading application is operating with a single open position.

---

## Close Positions

```python
await dydx.close_positions()
```

The interface determines whether each position is long or short and generates an opposing limit order intended to close the position.

---

## Clear Existing Trading State

```python
await dydx.clear_existing_orders_and_positions()
```

This performs:

```text
Cancel Open Orders
        │
        ▼
Wait for propagation
        │
        ▼
Close Open Positions
```

This method was designed for automated trading systems that need to normalize account state before initiating a new trading cycle.

---

# Market Data

## Fetch ETH Oracle Price

```python
price = await dydx.fetch_eth_price()
```

The current implementation targets:

```text
ETH-USD
```

The market is currently configured inside `DydxInterface` as:

```python
MARKET_ID = "ETH-USD"
```

---

# Price Adjustment

The interface includes a helper for adjusting and rounding prices:

```python
new_price = dydx.calculate_new_price(
    oraclePrice=2500,
    operation="subtract",
    buffer_value=5,
    tickSize_value=0.1
)
```

This is used when generating closing orders near the current oracle price.

---

# Reliability

Interacting directly with blockchain infrastructure introduces network and RPC failure modes that ordinary REST applications do not always encounter.

The interface therefore includes retry logic for retrieving the current block height.

Transient gRPC errors such as:

```text
UNAVAILABLE
UNKNOWN
```

are retried using exponential backoff.

The retry delay follows approximately:

```text
2s → 4s → 8s → 16s → 30s
```

before ultimately raising an error if the node remains unavailable.

---

# Logging

Runtime activity is logged using Python's `logging` module.

Output is written to:

```text
interface.log
```

and simultaneously printed to the console.

Example events include:

```text
Setting up the client
Fetching account info
Fetching open orders
Placing limit order
Cancelling order
Closing positions
gRPC retry attempts
```

This makes the interface easier to debug when incorporated into long-running trading applications.

---

# dYdX v3

The repository also contains:

```text
dydx_v3_interface.py
```

This was the original version of the interface and was developed against the dYdX v3 Python API.

It includes functionality for:

* API credential initialization
* Stark key initialization
* Limit-order placement
* Order retrieval
* Position retrieval
* Account balance retrieval
* Equity retrieval
* Leverage calculations
* Position management

The v3 implementation remains in the repository as a historical example of the project's evolution as dYdX transitioned from the v3 API architecture to the dYdX v4 Chain.

For new development, use:

```text
dydx_v4_interface.py
```

---

# Current Scope

This project was developed as infrastructure for algorithmic and automated trading applications.

The current implementation makes several application-specific assumptions:

* Primary market is `ETH-USD`
* Subaccount `0` is used
* Position-size utilities assume one active position
* Some order parameters are currently configured specifically for the original trading system
* Development and experimental functions remain in the source

These are intentional limitations of the current project rather than a complete general-purpose dYdX SDK replacement.

---

# Potential Applications

The interface can serve as the exchange integration layer for systems such as:

```text
Algorithmic Trading Systems
          │
Machine Learning Models
          │
Reinforcement Learning Agents
          │
Portfolio Management Software
          │
Trading Bots
          │
Market Monitoring Systems
          │
Automated Risk Management
          ▼
     DydxInterface
          ▼
       dYdX Chain
```

Separating exchange-specific functionality from trading logic makes it easier to replace or extend strategies without duplicating protocol integration code.

---

# Technologies Demonstrated

This project demonstrates practical experience with:

* Python
* Asynchronous programming (`asyncio`)
* Object-oriented application design
* API abstraction
* REST APIs
* gRPC
* Blockchain infrastructure
* Decentralized exchanges
* Cosmos-based blockchain clients
* Transaction signing
* Programmatic order management
* Environment-based configuration
* Decimal-safe financial calculations
* Logging
* Error handling
* Retry and exponential-backoff strategies
* External SDK integration
* Automated trading infrastructure

---

# Project Evolution

This repository also documents the migration of the interface between two substantially different generations of dYdX infrastructure:

```text
dYdX v3 API
     │
     ▼
dydx_v3_interface.py
     │
 Protocol Migration
     ▼
dYdX Chain / v4
     │
     ▼
dydx_v4_interface.py
```

Maintaining the interface across the protocol transition required adapting the trading abstraction from the older API/client architecture to the v4 Indexer, blockchain node, wallet, protobuf, and asynchronous transaction model.

---

# Disclaimer

This project is provided for software-development and educational purposes.

Cryptocurrency and derivatives trading involve substantial financial risk. This software has not been independently audited and should not be considered production-ready financial infrastructure.

Use testnet and thoroughly validate all transaction behavior before considering interaction with real assets.

Nothing in this repository constitutes financial or investment advice.

---

## Author

**Ryan Yarbery**

Software developer focused on Python, AI/ML, automation, API integration, blockchain systems, and backend development.

GitHub: [RyanYarbery](https://github.com/RyanYarbery)
