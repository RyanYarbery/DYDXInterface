# Questions I need to answer = 
# dydx3 library installation -- Megagay
# Dydx account -- Done
# DYDX api key and stark api key -- Done


from dydx3 import Client
from dydx3.constants import *
from decimal import Decimal
import json

# Function to execute a buy or sell order on dYdX
def execute_order(api_url, api_key, stark_private_key, ethereum_address, order_side, amount, price):
    """
    Executes a buy or sell order on dYdX.

    :param api_url: URL of the dYdX API.
    :param api_key: Your dYdX API key.
    :param stark_private_key: Your dYdX STARK private key.
    :param ethereum_address: Your Ethereum address associated with your dYdX account.
    :param order_side: 'buy' for buy order, 'sell' for sell order.
    :param amount: Amount of ETH to buy or sell.
    :param price: Price at which to buy or sell ETH.
    """
    client = dydx3.Client(
        host=api_url,
        api_key_credentials={
            'key': api_key['key'],
            'secret': api_key['secret'],
            'passphrase': api_key['passphrase'],
        },
        stark_private_key=stark_private_key,
        eth_private_key=ethereum_address,
    )

    # Set order parameters
    side = ORDER_SIDE_BUY if order_side == 'buy' else ORDER_SIDE_SELL
    order = {
        'market': MARKET_ETH_USD,
        'side': side,
        'orderType': 'LIMIT',
        'postOnly': False,
        'size': str(amount),
        'price': str(price),
        'timeInForce': TIME_IN_FORCE_GTT,
        'cancelAfter': '2021-03-20T12:30:00Z',
    }

    # Place the order
    response = client.private.create_order(**order)
    return response.data

# Main function for executing the script
def main():
    # Your dYdX API credentials and account information
    api_url = 'https://api.dydx.exchange'
    api_key = {
        'key': '320c771e-0989-a099-67a3-fae38c18bcfb',
        'secret': 'k_xw0YJ0BJOikGpez6jWkwrx0JDKt6aZKjjWwfKC',
        'passphrase': 'EKgG_M9yZkqzGwmR1T9r',
    }
    stark_private_key = '07b0a4450932d36a7cc89af0dfe68d49e9fde00be2a9d233c5cd3dda0f3b0d24'
    ethereum_address = '0xE3Cb26ad8999575d39db889666dD1cFcdFC92f72'

    # Parameters for the order
    order_side = 'buy'  # or 'sell'
    amount = 1.0  # Amount of ETH to buy or sell
    price = 2000.0  # Price at which to buy or sell ETH

    # Execute the order
    result = execute_order(api_url, api_key, stark_private_key, ethereum_address, order_side, amount, price)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
