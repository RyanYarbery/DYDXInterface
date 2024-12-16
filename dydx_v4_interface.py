

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
            self.dydx_address = os.getenv('dydx_address')
            self.dydx_mnemonic = os.getenv('dydx_mnemonic')
            self.dydx_subaccount = 0
            self.net_node = 'mainnet'
        else:
            self.dydx_address = os.getenv('dydx_address')
            self.dydx_mnemonic = os.getenv('dydx_mnemonic')
            self.dydx_subaccount = 0
            self.net_node = 'testnet'


        self.client = Client(
            network_id=self.network_id,
            host=self.host,
            eth_private_key=self.ethereum_private_key,
            api_key_credentials={
                'key': self.api_key,
                'secret': self.api_secret,
                'passphrase': self.passphrase,
            },
        )
