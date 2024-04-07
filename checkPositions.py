
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import NETWORK_ID_SEPOLIA

def fetch_current_orders_and_positions():
    """
    Fetches the current open orders and positions on the dYdX exchange.

    :return: A tuple containing a list of open orders and a list of positions.
    """
    # Initialize the dYdX client with the environment's API credentials
    api_key = os.getenv('dydxKey')
    api_secret = os.getenv('dydxSecret')
    passphrase = os.getenv('dydxPassphrase')
    ethereum_private_key = os.getenv('maskKey')

    client = Client(
        network_id=NETWORK_ID_SEPOLIA,
        host=API_HOST_SEPOLIA,
        eth_private_key=ethereum_private_key,
        api_key_credentials={
            'key': api_key,
            'secret': api_secret,
            'passphrase': passphrase,
        },
    )

    # Fetch open orders
    open_orders_response = client.private.get_orders()
    open_orders = open_orders_response.data.get('orders', [])

    # Fetch positions
    positions_response = client.private.get_positions()
    positions = positions_response.data.get('positions', [])

    return open_orders, positions

def main():
    orders, positions = fetch_current_orders_and_positions()

    print("Open Orders:")
    for order in orders:
        print(order)

    print("\nPositions:")
    for position in positions:
        print(position)

if __name__ == "__main__":
    main()