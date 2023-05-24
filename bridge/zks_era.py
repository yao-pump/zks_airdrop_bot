import json

from web3 import Web3, HTTPProvider

from utils import execute_tx
from cfg import  providers

CHAIN_IDS = {
    'mainnet': 1,
    'testnet': 5,
}


def get_bridge_abi(network='testnet'):
    with open('../config/contracts.json', 'r') as f:
        contract_file = json.load(f)
    contract_address = contract_file['zks_bridge_{}'.format(network)]
    with open("../config/zks_abi.json", encoding='utf-8', errors='ignore') as json_data:
        bridge_abi = json.load(json_data, strict=False)
    return {"contract_address": contract_address, "abi": bridge_abi}


def bridge(account, amount, network_type="test"):
    provider_url = providers['eth_{}'.format(network_type)]
    web3 = Web3(HTTPProvider(endpoint_uri=provider_url))
    abi_info = get_bridge_abi(network_type)
    contract = web3.eth.contract(address=web3.to_checksum_address(abi_info['contract_address']), abi=abi_info['abi'])
    l2_address = web3.to_checksum_address(account.address)
    transaction_fee = 0.00036675
    transfer_value = web3.to_wei(amount+transaction_fee, 'ether')
    amount_value = web3.to_wei(amount, 'ether')
    call_data = b''
    gas_limit = 720000
    gas_byte_limit = 800
    factory_deps = [b'']
    tx = contract.functions.requestL2Transaction(l2_address, amount_value, call_data,
                                                 gas_limit, gas_byte_limit,
                                                 factory_deps, l2_address).build_transaction({'chainId': CHAIN_IDS[network_type],
                   'gas': web3.eth.gas_price, 'maxFeePerGas': web3.to_wei('20', 'gwei'),
	    'maxPriorityFeePerGas': web3.to_wei('1.5', 'gwei'), 'value': transfer_value,
                   'nonce': web3.eth.get_transaction_count(account.address)})
    tx['data'] = tx['data'][:64*9+10-1] + '0'
    success = execute_tx(tx, account, web3)
    return success