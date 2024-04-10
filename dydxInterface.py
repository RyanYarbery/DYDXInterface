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

def fetch_eth_market_data():
    """
    Fetches market data for Ethereum from the dYdX exchange.

    :return: A dictionary with specific market details for Ethereum.
    """
    client = initialize_client()

    # Fetch all market data
    market_data_response = client.public.get_markets()
    market_data = market_data_response.data.get('markets', {})

    # Extract ETH-USD market data
    eth_data = market_data.get('ETH-USD', {})

    # Extract specific details
    eth_details = {
        'indexPrice': eth_data.get('indexPrice'),
        'oraclePrice': eth_data.get('oraclePrice'),
        'priceChange24H': eth_data.get('priceChange24H'),
        'openInterest': eth_data.get('openInterest'),
        'volume24H': eth_data.get('volume24H'),
        'trades24H': eth_data.get('trades24H'),
        'nextFundingRate': eth_data.get('nextFundingRate'),
        'nextFundingAt': eth_data.get('nextFundingAt')
    }

    return eth_details

# Need to rename to order_id
def cancel_order(position_id):
    """
    Cancels an order on the dYdX exchange given a position_id.

    :param position_id: The ID of the position associated with the order to cancel.
    :return: The response from the cancel order request.
    """
    client = initialize_client()

    # Cancel the order
    cancel_response = client.private.cancel_order(order_id=position_id)
    
    return cancel_response.data

def cancel_all_orders():
    """
    Cancels all open orders on the dYdX exchange.

    :return: The response from the cancel all orders request.
    """
    client = initialize_client()

    # Cancel all orders
    cancel_response = client.private.cancel_all_orders()
    
    return cancel_response.data

# if __name__ == "__main__":
#     # Test place_limit_order function
#     print("Placing a limit order...")
#     try:
#         order_result = place_limit_order(
#             side_input='buy',  # or 'sell'
#             size='0.5',  # Specify the size
#             price='3407.1',  # Specify the price
#             post_only=False,
#             limit_fee='0.0015',
#             expiration_seconds=300  # 5 minutes
#         )
#         print("Limit Order Result:")
#         print(order_result)
#     except Exception as e:
#         print(f"Error placing limit order: {e}")

#     # Test fetch_current_orders_and_positions function
#     print("\nFetching current orders and positions...")
#     try:
#         orders, positions = fetch_current_orders_and_positions()
#         print("Current Orders:")
#         print(orders)
#         print("Current Positions:")
#         print(positions)
#     except Exception as e:
#         print(f"Error fetching orders and positions: {e}")

#     # Test fetch_account_balance function
#     print("\nFetching account balance...")
#     try:
#         balance_info = fetch_account_balance()
#         print("Account Balance:")
#         print(balance_info)
#     except Exception as e:
#         print(f"Error fetching account balance: {e}")

#     print("\nFetching Ethereum market data...")
#     try:
#         eth_market_data = fetch_eth_market_data()
#         print("Ethereum Market Data:")
#         print(eth_market_data)
#     except Exception as e:
#         print(f"Error fetching Ethereum market data: {e}")

# if __name__ == "__main__":
#     # Other test functions...

#     # Test cancel_order function
#     print("\nCancelling an order...")
#     try:
#         position_id_to_cancel = '26f8721eb69f7f885dd6f3a7e80a395ffbb8dc0d6ce801376a7d7deb71401f5'  # Replace with the actual position ID you want to cancel
#         cancel_result = cancel_order(position_id_to_cancel)
#         print("Cancel Order Result:")
#         print(cancel_result)
#     except Exception as e:
#         print(f"Error cancelling order: {e}")

# if __name__ == "__main__":
#     # Test cancel_all_orders function
#     print("\nCancelling all orders...")
#     try:
#         cancel_all_result = cancel_all_orders()
#         print("Cancel All Orders Result:")
#         print(cancel_all_result)
#     except Exception as e:
#         print(f"Error cancelling all orders: {e}")

