import requests
import json
from web3 import Web3

API_KEY = '645b2c8c-5825-4930-baf3-d9b997fcd88c'  # SOCKET PUBLIC API KEY
headers = {'API-KEY': API_KEY, 'Accept': 'application/json', 'Content-Type': 'application/json',
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}

# Web3 provider
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))  # Replace with your provider

# Main function
def main():

    # Wallet details
    private_key = "YOUR_PRIVATE_KEY"
    account = w3.eth.account.privateKeyToAccount(private_key)
    user_address = account.address

    # Bridging Params fetched from users
    from_chain_id = 137
    to_chain_id = 56
    from_asset_address = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
    to_asset_address = "0x55d398326f99059fF775485246999027B3197955"
    amount = 100000000  # 100 USDC, USDC is 6 decimals
    unique_routes_per_bridge = True  # Returns the best route for a given DEX / bridge combination
    sort = "output"  # "output" | "gas" | "time"
    single_tx_only = True

    # Quote for bridging 100 USDC on Polygon to USDT on BSC
    # For single transaction bridging, mark singleTxOnly flag as true in query params
    quote = get_quote(from_chain_id, from_asset_address, to_chain_id, to_asset_address, amount, user_address, unique_routes_per_bridge, sort, single_tx_only)

    # Choosing first route from the returned route results
    route = quote['result']['routes'][0]

    # Fetching transaction data for swap/bridge tx
    api_return_data = get_route_transaction_data(route)

    # Used to check for ERC-20 approvals
    approval_data = api_return_data['result']['approvalData']
    allowance_target = approval_data['allowanceTarget']
    minimum_approval_amount = approval_data['minimumApprovalAmount']

    # approvalData from apiReturnData is null for native tokens
    # Values are returned for ERC20 tokens but token allowance needs to be checked
    if approval_data is not None:
        # Fetches token allowance given to Socket contracts
        allowance_check_status = check_allowance(from_chain_id, user_address, allowance_target, from_asset_address)
        allowance_value = allowance_check_status['result']['value']

        # If Socket contracts don't have sufficient allowance
        if minimum_approval_amount > allowance_value:
            # Approval tx data fetched
            approval_transaction_data = get_approval_transaction_data(from_chain_id, user_address, allowance_target, from_asset_address, amount)

            # Initiates approval transaction on user's frontend which user has to sign
            receipt = w3.eth.sendRawTransaction(approval_transaction_data)
            print('Approval Transaction Hash :', receipt.hex())

    # Initiates swap/bridge transaction on user's frontend which user has to sign
    receipt = w3.eth.sendRawTransaction(api_return_data)
    tx_hash = receipt.hex()
    print('Bridging Transaction : ', receipt.hex())

    # Checks status of transaction every 20 secs
    while True:
        status = get_bridge_status(tx_hash, from_chain_id, to_chain_id)
        print('SOURCE TX : {}\nDEST TX : {}'.format(status['result']['sourceTxStatus'], status
        ['result']['destinationTxStatus']))

        if status['result']['destinationTxStatus'] == "COMPLETED":
            print('DEST TX HASH :', status['result']['destinationTransactionHash'])
            break

        time.sleep(20)


# Helper Functions

def get_quote(from_chain_id, from_token_address, to_chain_id, to_token_address, from_amount, user_address, unique_routes_per_bridge, sort, single_tx_only):
    url = f"https://api.socket.tech/v2/quote?fromChainId={from_chain_id}&fromTokenAddress={from_token_address}&toChainId={to_chain_id}&toTokenAddress={to_token_address}&fromAmount={from_amount}&userAddress={user_address}&uniqueRoutesPerBridge={unique_routes_per_bridge}&sort={sort}&singleTxOnly={single_tx_only}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_route_transaction_data(route):
    url = "https://api.socket.tech/v2/build-tx"
    data = json.dumps({"route": route})
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def check_allowance(chain_id, owner, allowance_target, token_address):
    url = f"https://api.socket.tech/v2/approval/check-allowance?chainID={chain_id}&owner={owner}&allowanceTarget={allowance_target}&tokenAddress={token_address}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_approval_transaction_data(chain_id, owner, allowance_target, token_address, amount):
    url = f"https://api.socket.tech/v2/approval/build-tx?chainID={chain_id}&owner={owner}&allowanceTarget={allowance_target}&tokenAddress={token_address}&amount={amount}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_bridge_status(transaction_hash, from_chain_id, to_chain_id):
    url = f"https://api.socket.tech/v2/bridge-status?transactionHash={transaction_hash}&fromChainId={from_chain_id}&toChainId={to_chain_id}"
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    main()
