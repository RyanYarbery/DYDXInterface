import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import ORDER_STATUS_OPEN

def place_limit_order(side_input, size, price, expiration_minutes=5):
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

    stark_key_data = client.onboarding.derive_stark_key()
    client.stark_private_key = stark_key_data['private_key']

    account_response = client.private.get_account().data
    position_id = account_response['account']['positionId']

    market = MARKET_ETH_USD

    if side_input.lower() == 'buy':
        side = ORDER_SIDE_BUY
    elif side_input.lower() == 'sell':
        side = ORDER_SIDE_SELL
    else:
        raise ValueError("Invalid order side. Must be 'buy' or 'sell'.")

    order_type = ORDER_TYPE_LIMIT

    expiration_time = int(time.time()) + expiration_minutes * 60

    order_params = {
        'position_id': position_id,
        'market': market,
        'side': side,
        'order_type': order_type,
        'size': size,
        'post_only': False,
        'price': price,
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': expiration_time,
    }

    order_response = client.private.create_order(**order_params)

    return order_response.data

# Example usage:
if __name__ == "__main__":
    side = 'buy'  # or 'sell'
    size = '0.5'  # Amount of ETH
    price = '3348'  # Price in USD
    result = place_limit_order(side, size, price)
    print("Order response:", result)
