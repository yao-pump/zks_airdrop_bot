import json

from web3 import Web3, HTTPProvider
from utils import get_providers

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
}

token_abi = json.loads('config/token_abi.json')
