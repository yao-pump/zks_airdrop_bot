import json
import time
from decimal import Decimal

from web3 import Web3, HTTPProvider
from utils import get_accounts, get_providers
import asyncio
from eth_abi import encode

providers = get_providers()
provider_url = providers['zks_era']
w3_zks = Web3(HTTPProvider(provider_url))

accounts = get_accounts()
acc = accounts[1]

with open("config/syncswap_pool_abi.json", encoding='utf-8', errors='ignore') as json_data:
    pool_abi = json.load(json_data, strict=False)

with open("config/syncswap_pool_factory_abi.json", encoding='utf-8', errors='ignore') as json_data:
    pool_factory_abi = json.load(json_data, strict=False)

with open("config/syncswap_router_abi.json", encoding='utf-8', errors='ignore') as json_data:
    router_abi = json.load(json_data, strict=False)

ADDRESS = {
    'eth': w3_zks.to_checksum_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'),
    'usdc': w3_zks.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
    'ot': w3_zks.to_checksum_address('0xD0eA21ba66B67bE636De1EC4bd9696EB8C61e9AA')
}

ETH_ADDRESS = w3_zks.to_checksum_address("0x0000000000000000000000000000000000000000")
WETH_ADDERSS = w3_zks.to_checksum_address("0x5aea5775959fbc2557cc8789bc1bf90a239d9a91")
UDSC_ADDRESS = w3_zks.to_checksum_address("0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4")

POOL_FACTORY_ADDRESS = w3_zks.to_checksum_address("0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb")
ROUTER_ADDRESS = w3_zks.to_checksum_address("0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295")

pool_factory_contract = w3_zks.eth.contract(address=POOL_FACTORY_ADDRESS, abi=pool_factory_abi)
router_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)


def get_balance(token, pool_address):
    pool_contract = w3_zks.eth.contract(address=pool_address, abi=pool_abi)
    balance = pool_contract.functions.balanceOf(w3_zks.to_checksum_address(token)).call()
    print(balance)

def get_pool_address(token1, token2):
    pool_address = pool_factory_contract.functions.getPool(ADDRESS[token1], ADDRESS[token2]).call()
    pool_address = w3_zks.to_checksum_address(pool_address)
    return pool_address

def swap(token1, token2, amount):
    pool_address = pool_factory_contract.functions.getPool(ADDRESS[token1], ADDRESS[token2]).call()
    pool_address = w3_zks.to_checksum_address(pool_address)
    print(pool_address)
    if token1 == 'eth':
        value = w3_zks.to_wei(amount, 'ether')
    else:
        value = int(Decimal(amount * 10 ** 6))
    print(value)

    withdraw_mode = 1
    swap_data = encode(
        ["address", "address", "uint8"],
        [w3_zks.to_checksum_address(ADDRESS[token1]), w3_zks.to_checksum_address(acc['address']), withdraw_mode])


    steps = [(
        pool_address, swap_data, ETH_ADDRESS, b'0x',
    )]

    if token1 == 'eth':
        paths = [(steps, ETH_ADDRESS, value)]
    else:
        paths = [(steps, ADDRESS[token1], value)]


    current_time = int(time.time())
    big_number = current_time + 1800
    # tx = router_contract.functions.swap(paths, 0, big_number).call()
    tx = router_contract.functions.swap(paths, 0, big_number).build_transaction({'chainId': 324,
                   'gas': 4000000, 'gasPrice': w3_zks.eth.gas_price, 'from': acc['address'], 'value': value,
                   'nonce': w3_zks.eth.get_transaction_count(acc['address'])})
    print(tx['data'])
    tx['data'] = tx['data'][:-64]
    p1 = tx['data'][:-128]
    # if token1 == 'eth':
    #     p2 = '00000000000000000000000000000000000000000000000000000000010f4605'
    # else:
    #     p2 = '0000000000000000000000000000000000000000000000000000000000000000'
    # p3 = tx['data'][128+10:-128]
    if token1 == 'eth':
        p2 = '00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'
    else:
        p2 = '00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000'
    tx['data'] = p1 + p2
    print(tx)

    signed_txn = w3_zks.eth.account.sign_transaction(tx, acc['private_key'])
    print(signed_txn.rawTransaction)
    transaction_hash = w3_zks.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction hash: {transaction_hash.hex()}")

async def main():
    # pool = 
    pool_address = get_pool_address('eth', 'usdc')
    print(pool_address)


if __name__ == '__main__':
    asyncio.run(main())
