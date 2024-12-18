
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
from dydx_v4_client.indexer.rest.constants import OrderType, OrderExecution, OrderSide
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import make_mainnet, make_testnet, make_secure, make_insecure, mainnet_node, testnet_node
from dydx_v4_client.network import TESTNET
from dydx_v4_client.node.client import NodeClient
from dydx_v4_client.node.market import Market, since_now
from dydx_v4_client.node.message import cancel_order, batch_cancel, OrderBatch
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
        self.clobPairId = 1


        
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
            
            # Initialize the IndexerClient
            self.client = IndexerClient(self.NETWORK.rest_indexer)
            if not self.client:
                raise ConnectionError("Failed setting up indexer.")

            # Connect to the node
            self.node = await NodeClient.connect(self.NETWORK.node)
            if not self.node:
                raise ConnectionError("Failed to connect to the node.")

            # Initialize the wallet
            if not self.dydx_mnemonic or not self.dydx_address:
                raise ValueError("Mnemonic or address is not provided.")
            
            self.wallet = await Wallet.from_mnemonic(self.node, self.dydx_mnemonic, self.dydx_address)

            
            # Get market info
            self.market = Market(
                (await self.client.markets.get_perpetual_markets(self.MARKET_ID))["markets"][self.MARKET_ID]
            )

            logging.info("Client successfully initialized.")

        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            self.client = None
            self.node = None
            self.wallet = None

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
            'quoteBalance': subaccount.get('quoteBalance') # Doesn't exist
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
        # Fetches oracle price
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
        markets = market['markets']
        eth = markets['ETH-USD']
        price = float(eth['oraclePrice']) 

        return price # Returns Oracle price Cast to a float
    
    async def place_limit_order(self, side_input: str, size: float, price: float):
        """Placing Limit Order asynchronously."""
        logging.info(f"Placing limit order: side={side_input}, size={size}, price={price}")

        order_id = self.market.order_id(
            self.dydx_address, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM # Other options are LONG_TERM or CONDITIONAL
        )
        # NOTE: Other functions are affected by what we put in the OrderFlags parameter here such as cancelling orders.

        if side_input.lower() == 'buy':
            side = Order.Side.SIDE_BUY
        elif side_input.lower() == 'sell':
            side = Order.Side.SIDE_SELL

        current_block = await self.node.latest_block_height()

        new_order = self.market.order(
            order_id=order_id,
            order_type=OrderType.LIMIT,
            side=side,
            size=size,
            price=price,
            time_in_force=Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED,
            reduce_only=False,
            good_til_block=current_block + 60,
            )
        
        transaction = await self.node.place_order(
            wallet=self.wallet,
            order=new_order,
        )

        self.wallet.sequence += 1
            
        return transaction

    # Close Position
    # Cancel ORder
    # Close all positions and cancel all orders
    


    async def cancel_order(self, order_id):
        """Cancel order asynchronously."""
        logging.info(f"Cancelling order with id:{order_id}")
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Node client is not initialized. Cannot cancel order.")
            return []
        
        current_block = await self.node.latest_block_height()
        if not current_block:
            logging.error("Could not get current block. Cannot cancel order.")
            return[]
        
        good_til_block = current_block + 60

        response = await self.node.cancel_order(
            self.wallet,
            order_id,
            good_til_block,
            good_til_block_time=good_til_block_time
        )
        if not response:
            logging.info("Could not cancel order.")
        return response
    
    async def cancell_all_orders(self):
        """ Cancel ALl Orders asynchronously."""
        
        if not self.client:
            await self._client_task  # Ensure the client setup task completes

        if not self.client:
            logging.error("Client is not initialized. Cannot cancel orders.")
            return []
        
        logging.info("Getting order ids")
        orders = await self.fetch_open_orders()
        if not orders:
            logging.error("Could't Pull orders")

        client_ids = [order['clientId'] for order in orders]

        short_term_cancels = [OrderBatch(clob_pair_id=self.clobPairId, client_ids=client_ids)]

        current_block = await self.node.latest_block_height()
        if not current_block:
            logging.error("Could not get current block. Cannot cancel orders.")
            return[]
        
        good_til_block = current_block + 60
        
        logging.info("Cancelling orders")

        response = await self.node.batch_cancel_orders(
            self.wallet,
            self.subaccount_id,
            short_term_cancels,
            good_til_block
        )
        if not response:
            logging.info(".")
        return response

# Usage Example
async def main():
    dydx_interface = DydxInterface(environment='test')
    await asyncio.sleep(1)  # Allow time for async setup
    # position = await dydx_interface.fetch_open_positions()
    # print('Position: ', position)
    # size = await dydx_interface.fetch_position_size()
    # print("Position Size:", size)
    # price = await dydx_interface.fetch_eth_price()
    # print("ETH Price: ", price)
    ## account_info = await dydx_interface.fetch_account()
    # print("Account Info: ", account_info)
    # price = await dydx_interface.fetch_eth_price()
    # price = (price + (price * 0.01))
    # order = await dydx_interface.place_limit_order('Sell', .01, price)
    # print('Order: ', order)
    # orders = await dydx_interface.fetch_open_orders()
    # print('Orders: ', orders)
    # client_ids = [order['clientId'] for order in orders]
    # print('Client IDs: ', client_ids)
    # market_info = await dydx_interface.client.markets.get_perpetual_markets(dydx_interface.MARKET_ID)
    # print('Market info: ', market_info)

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

