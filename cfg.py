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
    addresses = {}
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
        addresses['router'] = router_address
        addresses['factory'] = factory_address

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
        addresses['router'] = router_address
        addresses['factory'] = factory_address

    elif dex_name == 'izumiswap':
        abi_paths['factory'] = 'izumiswap_factory_abi.json'
        abi_paths['pool'] = 'izumiswap_pool_abi.json'
        abi_paths['liquid'] = 'izumiswap_liquid_abi.json'
        abi_paths['quoter'] = 'izumiswap_quoter_abi.json'
        abi_paths['router'] = 'izumiswap_swap_abi.json'

        if network == 'testnet':
            router_address = '0x3040EE148D09e5B92956a64CDC78b49f48C0cDdc'
            factory_address = '0x7FD55801c066AeB0bD848c2BA8AEc821AF700A41'
            quoter_address = '0xE93D1d35a63f7C6b51ef46a27434375761a7Db28'
            liquid_address = '0x38D526f278189Cb6983Cf8bc58BBFAea7D2c3B22'
            liquid_manager_address = '0x25727b360604E1e6B440c3B25aF368F54fc580B6'
            swapX2Y_address = '0x19ed8bB72F93B87A0605fAcc116019039757e95A'
        else:
            router_address = '0x9606eC131EeC0F84c95D82c9a63959F2331cF2aC'
            factory_address = '0x33D9936b7B7BC155493446B5E6dDC0350EB83AEC'
            quoter_address = '0x377EC7c9ae5a0787F384668788a1654249059dD6'
            liquid_address = '0xC319755Dff1601b3D0520B421A281B11bF22E80F'
            liquid_manager_address = '0x25727b360604E1e6B440c3B25aF368F54fc580B6'
            swapX2Y_address = '0x7499ce9c8F4FF47Be5dd5308Ab54cC710DE751E1'


        addresses['factory'] = factory_address
        addresses['quoter'] = quoter_address
        addresses['liquid'] = liquid_address
        addresses['liquid_manager'] = liquid_manager_address
        addresses['swapX2Y'] = swapX2Y_address
        addresses['router'] = router_address



    return addresses, abi_paths

providers = get_providers()
eth_main_rpc = Web3(HTTPProvider(endpoint_uri=providers['eth_mainnet']))
eth_test_rpc = Web3(HTTPProvider(endpoint_uri=providers['eth_testnet']))
zks_era_main_rpc = Web3(HTTPProvider(endpoint_uri=providers['zks_era_mainnet']))
zks_era_test_rpc = Web3(HTTPProvider(endpoint_uri=providers['zks_era_testnet']))
arb_rpc = Web3(HTTPProvider(endpoint_uri='https://arb1.arbitrum.io/rpc'))
rpcs = {'eth_mainnet': eth_main_rpc, 'eth_testnet': eth_test_rpc,
        'zks_era_mainnet': zks_era_main_rpc, 'zks_era_testnet': zks_era_test_rpc,
        'arb_mainnet': arb_rpc}

chains = {
    'eth_mainnet': 1,
    'eth_testnet': 5,
    'zks_era_mainnet': 324,
    'zks_era_testnet': 280,
    'arb_mainnet': 42161,
}

zks_token_addresses = {
    'mainnet': {'eth': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
                'usdc': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'},
    'testnet': {'eth': '0x294cB514815CAEd9557e6bAA2947d6Cf0733f014',
                'usdc': '0x0faF6df7054946141266420b43783387A78d82A9',
                'link': '0x40609141Db628BeEE3BfAB8034Fc2D8278D0Cc78',
                'usdt': '0xfcEd12dEbc831D3a84931c63687C395837D42c2B',
                'izi': '0xA5900cce51c45Ab9730039943B3863C822342034',
                },

}
with open("config/token_abi.json", encoding='utf-8', errors='ignore') as json_data:
    token_abi = json.load(json_data, strict=False)
