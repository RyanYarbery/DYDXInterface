import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_STATUS_OPEN
from dydx3.constants import ORDER_TYPE_MARKET

# Assuming you have the API credentials and the Ethereum private key
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

# Ensure the private key is a hexadecimal string
stark_private_key = str(client.onboarding.derive_stark_key())

# Set STARK key.
# stark_private_key = client.onboarding.derive_stark_key()
client.stark_private_key = stark_private_key

# Get account information (to retrieve the unique position ID)
account_response = client.private.get_account().data
position_id = account_response['account']['positionId']  # Unique identifier for the trading position

# User input for transaction parameters
market = MARKET_ETH_USD  # Trading pair, here it is Ethereum to US Dollar

# Capture and validate user input for the order side
side_input = input("Enter order side (buy/sell): ").strip().lower()
if side_input not in [ORDER_SIDE_BUY.lower(), ORDER_SIDE_SELL.lower()]:
    print("Invalid order side. Must be 'buy' or 'sell'.")
    exit()
else:
    side = side_input  # Set the side to the validated input

order_type = ORDER_TYPE_MARKET  # Using market order type for this example
size = input("Enter order size (amount of ETH): ").strip()  # Amount of ETH to buy or sell

order_params = {
    'position_id': position_id,
    'market': market,
    'side': side,
    'order_type': order_type,
    'size': size,
    'post_only': False,  # For market orders, typically set to False
    'expiration_epoch_seconds': int(time.time()) + 10,  # Expires 10 seconds from now
    'price': '0',  # Not required for market orders, comment out or remove
    'limit_fee': '0',  # Not required for market orders, comment out or remove
}


# Create the market order on dYdX
order_response = client.private.create_order(**order_params)
print("Order response:", order_response.data)

# Fetch and display open orders to confirm the order was placed
orders_response = client.private.get_orders(
    market=market,
    status=ORDER_STATUS_OPEN,
).data
print("Open orders:", orders_response['orders'])
