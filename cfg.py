import json

from web3 import Web3, HTTPProvider


def load_json(filename):
    with open(filename, 'r') as f:
        json_file = json.load(f)
    return json_file


def get_providers():
    with open('config/providers.json', 'r') as f:
        providers = json.load(f)
    return providers


def get_dex_info(dex_name, network='testnet'):
    router_address = None
    factory_address = None
    abi_paths = {}
    if dex_name == 'syncswap':
        abi_paths['factory'] = 'syncswap_pool_factory_abi.json'
        abi_paths['pool'] = 'syncswap_pool_abi.json'
        abi_paths['router'] = 'syncswap_router_abi.json'

        if network == 'testnet':
            router_address = '0xB3b7fCbb8Db37bC6f572634299A58f51622A847e'
            factory_address = '0xf2FD2bc2fBC12842aAb6FbB8b1159a6a83E72006'
        else:
            router_address = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'
            factory_address = '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb'

    elif dex_name == 'muteswap':
        abi_paths['factory'] = 'muteswap_factory_abi.json'
        abi_paths['pool'] = 'muteswap_pair_abi.json'
        abi_paths['router'] = 'muteswap_router_abi.json'

        if network == 'testnet':
            router_address = '0x96c2Cf9edbEA24ce659EfBC9a6e3942b7895b5e8'
            factory_address = '0xCc05E242b4A82f813a895111bCa072c8BBbA4a0e'
        else:
            router_address = '0x8B791913eB07C32779a16750e3868aA8495F5964'
            factory_address = '0x40be1cBa6C5B47cDF9da7f963B6F761F4C60627D'

    return router_address, factory_address, abi_paths

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

zks_token_addresses = {
    'mainnet': {'eth': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
                'usdc': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'},
    'testnet': {'eth': '0x294cB514815CAEd9557e6bAA2947d6Cf0733f014',
                'usdc': '0x0faF6df7054946141266420b43783387A78d82A9',
                'link': '0x40609141Db628BeEE3BfAB8034Fc2D8278D0Cc78',
                'usdt': '0xfcEd12dEbc831D3a84931c63687C395837D42c2B'},

}
with open("config/token_abi.json", encoding='utf-8', errors='ignore') as json_data:
    token_abi = json.load(json_data, strict=False)
