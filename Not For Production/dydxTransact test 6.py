import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import ORDER_STATUS_OPEN

# Presuming you have the API credentials and the Ethereum private key
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

# Derive STARK key (used for cryptographic operations on dYdX)
stark_key_data = client.onboarding.derive_stark_key()

# Extract the private key from the STARK key data
stark_private_key = stark_key_data['private_key']

# Set the STARK private key in the client for further operations
client.stark_private_key = stark_private_key

# Get account information (to retrieve the unique position ID)
account_response = client.private.get_account().data
position_id = account_response['account']['positionId']

# User input for transaction parameters
market = MARKET_ETH_USD  # Trading pair, here it is Ethereum to US Dollar
side_input = input("Enter order side (buy/sell): ").strip().lower()  # 'buy' for buying, 'sell' for selling

# Map user input to the corresponding constant
if side_input == 'buy':
    side = ORDER_SIDE_BUY
elif side_input == 'sell':
    side = ORDER_SIDE_SELL
else:
    print("Invalid order side. Must be 'buy' or 'sell'.")
    exit()

order_type = ORDER_TYPE_LIMIT  # Using market order type
size = input("Enter order size (amount of ETH): ").strip()  # Amount of ETH to buy or sell
price = input("Enter order price (in USD): ").strip()

# Set the expiration time to at least 1 minute in the future
expiration_time = int(time.time()) + 300  # 60 seconds added to the current time


order_params = {
    'position_id': position_id,
    'market': market,
    'side': side,
    'order_type': order_type,
    'size': size,
    'post_only': False,  # Can be set to false if we want the order to fill immediately when conditions are met
    'price': price,
    'limit_fee': '0.0015', 
    'expiration_epoch_seconds': expiration_time,  # Placeholder expiration time
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
