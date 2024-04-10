import time
import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import NETWORK_ID_SEPOLIA
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL
from dydx3.constants import ORDER_STATUS_OPEN
from dydx3.constants import ORDER_TYPE_LIMIT

# from web3.auto import w3  # Automatically detects and uses local Ethereum node

# Presuming you have the API credentials and the Ethereum private key
api_key = os.getenv('dydxKey')
api_secret = os.getenv('dydxSecret')
passphrase = os.getenv('dydxPassphrase')
ethereum_private_key = os.getenv('maskKey')
ethereum_address = os.getenv('maskWallet')  # This should match the address derived from the private key

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
stark_private_key = client.onboarding.derive_stark_key()
client.stark_private_key = stark_private_key

# # Get account information (to retrieve the unique position ID)
# account_response = client.private.get_account()
# position_id = account_response['account']['position_id']  # Unique identifier for the trading position

# Get account information and extract the data from the response
account_response = client.private.get_account().data

# Assuming the response data is a dictionary, access the position ID
position_id = account_response['account']['positionId']


# User input for transaction parameters
market = MARKET_ETH_USD  # Trading pair, here it is Ethereum to US Dollar
side = input("Enter order side (buy/sell): ").strip().lower()  # 'buy' for buying, 'sell' for selling
order_type = 'MARKET' #ORDER_TYPE_LIMIT  # Type of order, 'limit' for executing at a specific price
size = input("Enter order size (amount of ETH): ").strip()  # Amount of ETH to buy or sell
# price = input("Enter order price (in USD): ").strip()  # Price to buy/sell ETH in USD
# limit_fee = '0.0015'  # Fee for placing the order
# expiration_epoch_seconds = time.time() + 60  # Order expiration time (60 seconds from now)

# Validate order side input
if side not in [ORDER_SIDE_BUY, ORDER_SIDE_SELL]:
    print("Invalid order side. Must be 'buy' or 'sell'.")
    exit()

order_params = {
    'position_id': position_id,  # Identifies the trading position for this order
    'market': market,  # Specifies the market (trading pair) for the order
    'side': side,  # Determines if this is a buy or sell order
    'order_type': order_type,  # Defines the type of order (limit, market, etc.)
    'post_only': True,  # Ensures the order is added to the order book and not immediately matched
    'size': size,  # Specifies the amount of the asset to trade
    # 'price': price,  # Defines the price at which to execute the trade
    # 'limit_fee': limit_fee,  # The fee to be paid for executing the order
    # 'expiration_epoch_seconds': expiration_epoch_seconds,  # When the order will expire and be removed if not filled
}

# Create the order on dYdX
order_response = client.private.create_order(**order_params)
print("Order response:", order_response)

# Fetch and display open orders to confirm the order was placed
orders_response = client.private.get_orders(
    market=market,  # Filters the orders to the specified market
    status=ORDER_STATUS_OPEN,  # Filters the orders to those that are still open
)
print("Open orders:", orders_response['orders'])

# Uncomment the lines below to cancel all orders as part of the script's cleanup
# client.private.cancel_all_orders()
# print("All orders cancelled.")
