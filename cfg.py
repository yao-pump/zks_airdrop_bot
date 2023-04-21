import json

from web3 import Web3, HTTPProvider


def load_json(filename):
    with open(filename, 'r') as f:
        json_file = json.load(f)
    return json_file
def get_providers():
    providers = load_json('config/providers.json')
    return providers

providers = get_providers()
eth_main_rpc = Web3(HTTPProvider(endpoint_uri=providers['eth_mainnet']))
eth_test_rpc = Web3(HTTPProvider(endpoint_uri=providers['eth_testnet']))
zks_era_main_rpc = Web3(HTTPProvider(endpoint_uri=providers['zks_era_mainnet']))
zks_era_test_rpc = Web3(HTTPProvider(endpoint_uri=providers['zks_era_testnet']))

rpcs = {'eth_mainnet': eth_main_rpc, 'eth_testnet': eth_test_rpc,
        'zks_era_mainnet': zks_era_main_rpc, 'zks_era_testnet': zks_era_test_rpc}

chains = {
    'eth_mainnet': 1,
    'eth_testnet': 5,
    'zks_era_mainnet': 324,
    'zks_era_testnet': 280,
}

# token_abi = json.loads('config/token_abi.json')
