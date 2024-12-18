
#  The answer to all of my weird package issues is python -m pip install
#  Conda install may still be lame

import asyncio
import random
import os
import time
import logging
from decimal import Decimal
from decimal import ROUND_DOWN
from functools import partial

from v4_proto.dydxprotocol.clob.order_pb2 import Order

from dydx_v4_client import MAX_CLIENT_ID, OrderFlags
from dydx_v4_client.indexer.rest.constants import OrderType, OrderExecution
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import make_mainnet, make_testnet, make_secure, make_insecure, mainnet_node, testnet_node
from dydx_v4_client.network import TESTNET
from dydx_v4_client.node.client import NodeClient
from dydx_v4_client.node.market import Market, since_now
from dydx_v4_client.wallet import Wallet

MARKET_ID = "ETH-USD"


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers= [
                        logging.FileHandler('interface.log'),
                        logging.StreamHandler()
                    ])

class DydxInterface:

    def __init__(self, environment='test'):
        """
        Initializes the dYdX v4 client with the environment's API credentials.
        
        :param environment: Set to 'main' for mainnet, otherwise defaults to testnet.
        """
        self.environment = environment.lower()
        self.client = None
        self.MARKET_ID = "ETH-USD"


        
        if self.environment == 'main':
            self.dydx_address = os.getenv('dydx_address') # Potential for there to be a different address and mnemonic for main than test
            self.dydx_mnemonic = os.getenv('dydx_mnemonic')
            self.dydx_subaccount = 0
            self.net_node = 'mainnet_node'
            self.rest_indexer="https://indexer.dydx.trade"
            self.websocket_indexer="wss://indexer.dydx.trade/v4/ws"
            self.node_url="dydx-grpc.publicnode.com"
            self.NETWORK = make_mainnet(
                node_url=self.node_url,  # No 'https://' prefix
                rest_indexer=self.rest_indexer,
                websocket_indexer=self.websocket_indexer
            )
        else:
            self.dydx_address = os.getenv('dydx_address')
            self.dydx_mnemonic = os.getenv('dydx_mnemonic')
            self.NETWORK = TESTNET
            self.dydx_subaccount = 0
        
        self._client_task = asyncio.create_task(self._setup_client())
        
        
    async def _setup_client(self):
        """Asynchronous internal client setup method."""
        try:
            logging.info("Setting up the client...")
            self.client = IndexerClient(self.NETWORK.rest_indexer)
            self.node = await NodeClient.connect(self.NETWORK.node)
            logging.info("Client successfully initialized.")
        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            self.client = None
            self.node = None


    async def fetch_open_orders(self):
        """Fetch open orders asynchronously."""
        logging.info("Fetching open orders")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch open orders.")
            return []

        orders = await self.client.account.get_subaccount_orders(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
            status="OPEN"
        )
        if not orders:
            logging.info("No orders to fetch.")
        return orders
    
    async def fetch_orders(self):
        """Fetch orders asynchronously."""
        logging.info("Fetching orders")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch orders.")
            return []

        orders = await self.client.account.get_subaccount_orders(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
        )
        if not orders:
            logging.info("No orders to fetch.")
        return orders
    
    async def fetch_open_positions(self):
        """Fetch orders asynchronously."""
        logging.info("Fetching open positions")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch positions.")
            return []

        positions = await self.client.account.get_subaccount_perpetual_positions(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
            status="OPEN"
        )
        positions = positions.get('positions', [])
        if not positions:
            logging.info("No open positions to fetch.")
        return positions[0]
    
    async def fetch_fills(self):
        """Fetch orders asynchronously."""
        logging.info("Fetching fills")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch fills.")
            return []

        positions = await self.client.account.get_subaccount_fills(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
        )
        if not positions:
            logging.info("No positions to fetch.")
        return positions
    
    async def fetch_account(self):
        """Fetch account asynchronously."""
        logging.info("Fetching account info")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch account.")
            return []

        account_info = await self.client.account.get_subaccount(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
        )
        if not account_info:
            logging.info("No account info to fetch.")
        subaccount = account_info.get('subaccount', {})
        return {
            'equity': subaccount.get('equity'),
            'freeCollateral': subaccount.get('freeCollateral'),
            'pendingDeposits': subaccount.get('pendingDeposits'),
            'pendingWithdrawals': subaccount.get('pendingWithdrawals'),
            'quoteBalance': subaccount.get('quoteBalance')
        }
    
    async def fetch_equity(self):
        """Fetch equity asynchronously."""
        logging.info("Fetching equity")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch equity.")
            return []

        equity = await self.client.account.get_subaccount(
            address=self.dydx_address,
            subaccount_number=self.dydx_subaccount,
        )
        if not equity:
            logging.info("No equity to fetch.")
        subaccount = equity.get('subaccount', {})
        return subaccount.get('equity')

    async def fetch_position_size(self):
        # Assuming that we are operating with one open position at all times
        open_positions = await self.fetch_open_positions()
        print('Open Positions: ', open_positions)
        size = open_positions['size'] if open_positions else None
        size = abs(Decimal(size))
        if not size:
            # print("No open positions found to fetch size.")
            logging.info("No positions found to fetch size")
        return size
    
    async def fetch_eth_price(self):
        # This only has the oracle price available. Will have to determine whether this is our only option for pulling price.
        """Fetch ethereum price asynchronously."""
        logging.info("Fetching eth price")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot fetch eth price.")
            return []

        market = await self.client.markets.get_perpetual_markets(
            market=self.MARKET_ID,
        )
        if not market:
            logging.info("No market to fetch.")
        return market
    
# Usage Example
async def main():
    dydx_interface = DydxInterface(environment='test')
    await asyncio.sleep(1)  # Allow time for async setup
    # position = await dydx_interface.fetch_open_positions()
    # print('Position: ', position)
    # size = await dydx_interface.fetch_position_size()
    # print("Position Size:", size)
    price = await dydx_interface.fetch_eth_price()
    print("ETH Price: ", price)

if __name__ == "__main__":
    asyncio.run(main())
    

# Place Limit Order
# fetch_order_by_id
# fetch_positions
# fetch_open_positions
# fetch_account_balance
# fetch_equity
# fetch_position_size
# fetch_leverage
# fetch_eth_market_data
# fetch_eth_price
# cancel_order
# cancel_all_orders
# place_trailing_stop_order
# calculate_new_price
# clear_existing_orders_and_positions
# 