# dydx_helpers.py

import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT

def initialize_client():
    """
    Initializes and returns a dYdX client with the environment's API credentials.

    :return: Initialized dYdX Client object.
    """
    api_key = os.getenv('dydxKey')
    api_secret = os.getenv('dydxSecret')
    passphrase = os.getenv('dydxPassphrase')
    ethereum_private_key = os.getenv('maskKey')

    return Client(
        network_id=NETWORK_ID_SEPOLIA,
        host=API_HOST_SEPOLIA,
        eth_private_key=ethereum_private_key,
        api_key_credentials={
            'key': api_key,
            'secret': api_secret,
            'passphrase': passphrase,
        },
    )

def place_limit_order(side_input, size, price, post_only=True, limit_fee='0.0015', expiration_seconds=300, position_id=None):
    client = initialize_client()
    stark_key_data = client.onboarding.derive_stark_key()
    client.stark_private_key = stark_key_data['private_key']

    if not position_id:
        account_response = client.private.get_account().data
        position_id = account_response['account']['positionId']

    if side_input.lower() == 'buy':
        side = ORDER_SIDE_BUY
    elif side_input.lower() == 'sell':
        side = ORDER_SIDE_SELL
    else:
        raise ValueError("Invalid order side. Must be 'buy' or 'sell'.")

    expiration_time = int(time.time()) + expiration_seconds

    order_params = {
        'position_id': position_id,
        'market': MARKET_ETH_USD,
        'side': side,
        'order_type': ORDER_TYPE_LIMIT,
        'size': str(size),
        'post_only': post_only,
        'price': str(price),
        'limit_fee': limit_fee,
        'expiration_epoch_seconds': expiration_time,
    }

    return client.private.create_order(**order_params).data

def fetch_current_orders_and_positions():
    client = initialize_client()
    open_orders_response = client.private.get_orders()
    open_orders = open_orders_response.data.get('orders', [])

    positions_response = client.private.get_positions()
    positions = positions_response.data.get('positions', [])

    return open_orders, positions

def fetch_account_balance():
    client = initialize_client()
    account_response = client.private.get_account()
    balance_info = account_response.data.get('account', {})

    return {
        'equity': balance_info.get('equity'),
        'freeCollateral': balance_info.get('freeCollateral'),
        'pendingDeposits': balance_info.get('pendingDeposits'),
        'pendingWithdrawals': balance_info.get('pendingWithdrawals'),
        'quoteBalance': balance_info.get('quoteBalance')
    }
