# dydx_helpers.py

import os
from dydx3 import Client
from dydx3.constants import API_HOST_SEPOLIA
from dydx3.constants import NETWORK_ID_SEPOLIA

def fetch_account_balance():
    """
    Fetches balance-related details from the dYdX exchange account.

    :return: A dictionary containing equity, freeCollateral, pendingDeposits, pendingWithdrawals, and quoteBalance.
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

    # Fetch the account details
    account_response = client.private.get_account()
    account_data = account_response.data.get('account', {})

    # Extract the balance-related details
    balance_details = {
        'equity': account_data.get('equity'),
        'freeCollateral': account_data.get('freeCollateral'),
        'pendingDeposits': account_data.get('pendingDeposits'),
        'pendingWithdrawals': account_data.get('pendingWithdrawals'),
        'quoteBalance': account_data.get('quoteBalance')
    }

    return balance_details


def main():
    balance_info = fetch_account_balance()
    print("Account Balance:")
    print(balance_info)

if __name__ == "__main__":
    main()