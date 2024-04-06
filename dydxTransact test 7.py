import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT

def place_limit_order(side_input, size, price, post_only=True, limit_fee='0.0015', expiration_seconds=300, position_id=None):
    """
    Place a limit order on the dYdX exchange.

    :param side_input: 'BUY' or 'SELL' indicating the order side.
    :param size: The amount of the asset to trade, e.g., 0.5 for 0.5 ETH.
    :param price: The limit price at which to execute the order, e.g., 3348 for $3348.
    :param post_only: Whether the order should be post only, default is True.
    :param limit_fee: The fee rate for the order, default is '0.0015'.
    :param expiration_seconds: The time in seconds until the order expires, default is 5 minutes.
    :param position_id: Optional custom position ID. If not provided, it's fetched from the account info.

    :return: The response from the order request as a dictionary.
    """
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

    # Derive and set the STARK private key
    stark_key_data = client.onboarding.derive_stark_key()
    client.stark_private_key = stark_key_data['private_key']

    # Fetch the position ID if not provided
    if not position_id:
        account_response = client.private.get_account().data
        position_id = account_response['account']['positionId']

# Convert side input to the appropriate constant
    if side_input.lower() == 'buy':
        side = ORDER_SIDE_BUY
    elif side_input.lower() == 'sell':
        side = ORDER_SIDE_SELL
    else:
        raise ValueError("Invalid order side. Must be 'buy' or 'sell'.")
    
    # Set the expiration time
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

    order_response = client.private.create_order(**order_params)

    return order_response.data

# Example usage
if __name__ == "__main__":
    side = ORDER_SIDE_BUY  # or ORDER_SIDE_SELL
    size = 0.5  # Amount of ETH
    price = 3348  # Price in USD
    result = place_limit_order(side, size, price)
    print("Order response:", result)
