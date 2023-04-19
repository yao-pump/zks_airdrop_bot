import json

from web3 import Web3, HTTPProvider

from utils import get_accounts, get_providers

CHAIN_IDS = {
    'mainnet': 1,
    'testnet': 5,
}
network = 'mainnet'
acc = get_accounts()[1]
# account = Account.from_key(acc["private_key"])
provider_url = get_providers()['eth_{}'.format(network)]
web3 = Web3(HTTPProvider(endpoint_uri=provider_url))

def get_bridge_abi(network='testnet'):
    with open('config/contracts.json', 'r') as f:
        contract_file = json.load(f)
    contract_address = contract_file['zks_bridge_{}'.format(network)]
    with open("config/zks_abi.json", encoding='utf-8', errors='ignore') as json_data:
        bridge_abi = json.load(json_data, strict=False)
    return {"contract_address": contract_address, "abi": bridge_abi}


def bridge_eth(web3, abi_info, account, amount=0.005):
    contract = web3.eth.contract(address=web3.to_checksum_address(abi_info['contract_address']), abi=abi_info['abi'])
    l2_address = web3.to_checksum_address(account['address'])
    transaction_fee = 0.00036675
    transfer_value = web3.to_wei(amount+transaction_fee, 'ether')
    amount_value = web3.to_wei(amount, 'ether')
    # print(eth_value)
    call_data = b''
    gas_limit = 720000
    gas_byte_limit = 800
    factory_deps = [b'']
    tx = contract.functions.requestL2Transaction(l2_address, amount_value, call_data,
                                                 gas_limit, gas_byte_limit,
                                                 factory_deps, l2_address).build_transaction({'chainId': CHAIN_IDS[network],
                   'gas': 125080, 'maxFeePerGas': web3.to_wei('20', 'gwei'),
	    'maxPriorityFeePerGas': web3.to_wei('1.5', 'gwei'), 'value': transfer_value,
                   'nonce': web3.eth.get_transaction_count(account['address'])})
    tx['data'] = tx['data'][:64*9+10-1] + '0'
    print(tx)
    signed_txn = web3.eth.account.sign_transaction(tx, account['private_key'])
    transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction hash: {transaction_hash.hex()}")


abi_info = get_bridge_abi(network)
bridge_eth(web3, abi_info, account=acc, amount=0.69)

# account = get