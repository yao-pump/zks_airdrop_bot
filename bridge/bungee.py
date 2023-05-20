import requests
import json
from web3 import Web3

from cfg import chains, rpcs
from utils import estimate_gas, execute_tx

API_KEY = '1b2fd225-062f-41aa-8c63-d1fef19945e7'  # SOCKET PUBLIC API KEY
headers = {'API-KEY': API_KEY, 'Accept': 'application/json', 'Content-Type': 'application/json',
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def bridge(account, amount, source_network="arb", destination_network="zks_era", network_type="test"):
    unique_routes_per_bridge = "true"  # Returns the best route for a given DEX / bridge combination
    sort = "output"  # "output" | "gas" | "time"
    single_tx_only = "true"
    rpc = rpcs[source_network+'_'+network_type]
    amount = rpc.to_wei(amount, 'ether')
    # amount = int(amount * 10**18)
    # For single transaction bridging, mark singleTxOnly flag as true in query params
    quote = get_quote(chains[source_network+'_'+network_type],
                      '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', chains[destination_network+'_'+network_type],
                      '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', amount, account.address,
                      unique_routes_per_bridge, sort, single_tx_only)

    # Choosing first route from the returned route results
    route = quote['result']['routes'][0]

    # Fetching transaction data for swap/bridge tx
    api_return_data = get_route_transaction_data(route)

    # Used to check for ERC-20 approvals
    # approval_data = api_return_data['result']['approvalData']

    # Values are returned for ERC20 tokens but token allowance needs to be checked
    if route is not None:

        approval_transaction_data = get_approval_transaction_data(route)
        tx_data = approval_transaction_data['result']['txData']
        tx_target = approval_transaction_data['result']['txTarget']
        value = int(approval_transaction_data['result']['value'], 16)
        chain_id = approval_transaction_data['result']['chainId']
        # gas = estimate_gas(tx_data, rpc, rpc.to_checksum_address(tx_target), account.address)
        gas = int(route['userTxs'][0]['gasFees']['gasAmount'])

        tx = {'chainId': chain_id,
                'gas': gas,
                'gasPrice': rpc.eth.gas_price,
                'from': account.address,
                'value': value,
                'nonce': rpc.eth.get_transaction_count(
                      account.address),
                'data': tx_data,
                'to': rpc.to_checksum_address(tx_target)}

        success = execute_tx(tx, account, rpc)
            # Initiates approval transaction on user's frontend which user has to sign
            # receipt = w3.eth.sendRawTransaction(approval_transaction_data)
            # print('Approval Transaction Hash :', receipt.hex())

    # Initiates swap/bridge transaction on user's frontend which user has to sign
    # receipt = w3.eth.sendRawTransaction(api_return_data)
    # tx_hash = receipt.hex()
    # print('Bridging Transaction : ', receipt.hex())

    # Checks status of transaction every 20 secs
    while True:
        status = get_bridge_status(tx_hash, chains[source_network+'_'+network_type],
                                   chains[destination_network+'_'+network_type])
        print('SOURCE TX : {}\nDEST TX : {}'.format(status['result']['sourceTxStatus'], status
        ['result']['destinationTxStatus']))

        if status['result']['destinationTxStatus'] == "COMPLETED":
            print('DEST TX HASH :', status['result']['destinationTransactionHash'])
            break
# Helper Functions

def get_quote(from_chain_id, from_token_address, to_chain_id, to_token_address, from_amount, user_address, unique_routes_per_bridge, sort, single_tx_only):
    # https: // api.socket.tech / v2 / quote?fromChainId = 42161 & toChainId = 324 & fromTokenAddress = 0xff970a61a04b1ca14834a43f5de4533ebddb5cc8 & toTokenAddress = 0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4 & fromAmount = 33005935 & userAddress = 0xdc8D45d062E2FA5cD76b17d24f8691c950d0DE58 & singleTxOnly = true & bridgeWithGas = false & sort = output & defaultSwapSlippage = 1 & isContractCall = false
    url = f"https://api.socket.tech/v2/quote?fromChainId={from_chain_id}&toChainId={to_chain_id}&fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&fromAmount={from_amount}&userAddress={user_address}&singleTxOnly={single_tx_only}&bridgeWithGas=false&sort=output&defaultSwapSlippage=1&isContractCall=false"
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

def get_approval_transaction_data(route):
    url = f"https://api.socket.tech/v2/build-tx"
    data = {
        "route": route,

    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()

def get_bridge_status(transaction_hash, from_chain_id, to_chain_id):
    url = f"https://api.socket.tech/v2/bridge-status?transactionHash={transaction_hash}&fromChainId={from_chain_id}&toChainId={to_chain_id}"
    response = requests.get(url, headers=headers)
    return response.json()

