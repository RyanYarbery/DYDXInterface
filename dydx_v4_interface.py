
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
            print('Network:')
            # #  Could just use TESTNET instead of all of this. Need to see if that can be applied here
            # self.dydx_subaccount = 0
            # self.net_node = 'testnet_node'
            # self.rest_indexer="dydx-testnet.imperator.co"
            # self.websocket_indexer="wss://indexer.v4testnet.dydx.exchange/v4/ws"
            # self.node_url="test-dydx-grpc.kingnodes.com"

        # self.NETWORK = partial(
        #                 make_secure,
        #                 self.net_node,
        #                 self.rest_indexer,
        #                 self.websocket_indexer,
        #                 self.node_url,
        #         )
        self.client = None
        self._client_task = asyncio.create_task(self._setup_client())  # Start async setup task
        
        

    async def _setup_client(self):
        """Asynchronous internal client setup method."""
        try:
            print('Trying to setup client')
            self.client = IndexerClient(self.NETWORK.rest_indexer)
            logging.info("Client successfully initialized.")
        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            self.client = None


    async def get_open_orders(self):
        """Fetch open orders asynchronously."""
        if not self.client:
            await self._client_task  # Ensure the client setup task is complete

        orders = await self.client.account.get_subaccount_orders(
            address=self.dydx_address,
            subaccount_id=self.dydx_subaccount,
            status="OPEN"
        )
        if not orders:
            # print("No orders to fetch.")
            logging.info("No orders to fetch")
        return orders
    
# Ridiculous error that I don't understand
# Node URL should not contain http(s)://. Stripping the prefix. In the future, consider providing the URL without the http(s) prefix.

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