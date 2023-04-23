import json
import time
from decimal import Decimal

from web3 import Web3, HTTPProvider
from utils import get_accounts
from cfg import providers

network = 'testnet'
provider_url = providers['zks_era_{}'.format(network)]
w3_zks = Web3(HTTPProvider(provider_url))

accounts = get_accounts()
acc = accounts[-1]

if network == 'testnet':
    chain_id = 280
else:
    chain_id = 324

if network == 'testnet':
    ETH_ADDRESS = w3_zks.to_checksum_address(
        "0x0000000000000000000000000000000000000000")
    WETH_ADDRESS = w3_zks.to_checksum_address(
        "0x294cB514815CAEd9557e6bAA2947d6Cf0733f014")
    USDC_ADDRESS = w3_zks.to_checksum_address(
        "0x0faF6df7054946141266420b43783387A78d82A9")
else:
    ETH_ADDRESS = w3_zks.to_checksum_address(
        "0x0000000000000000000000000000000000000000")
    WETH_ADDRESS = w3_zks.to_checksum_address(
        "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91")
    USDC_ADDRESS = w3_zks.to_checksum_address(
        "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4")

ADDRESS = {'eth': WETH_ADDRESS, 'usdc': USDC_ADDRESS}

# ABIs
with open("config/muteswap_pair_abi.json", encoding='utf-8', errors='ignore') as json_data:
    pair_abi = json.load(json_data, strict=False)

with open("config/muteswap_factory_abi.json", encoding='utf-8', errors='ignore') as json_data:
    factory_abi = json.load(json_data, strict=False)

with open("config/muteswap_router_abi.json", encoding='utf-8', errors='ignore') as json_data:
    router_abi = json.load(json_data, strict=False)

# contract addresses
if network == 'testnet':
    ROUTER_ADDRESS = w3_zks.to_checksum_address(
        "0x96c2Cf9edbEA24ce659EfBC9a6e3942b7895b5e8")
    FACTORY_ADDRESS = w3_zks.to_checksum_address(
        "0xCc05E242b4A82f813a895111bCa072c8BBbA4a0e")
    PAIR_ADDRESS = w3_zks.to_checksum_address(
        "0x0f6d5b6c5c6b5f0e5c7f8b0d0c7e9e6f5d7c0a6f")
else:
    ROUTER_ADDRESS = w3_zks.to_checksum_address(
        "0x8B791913eB07C32779a16750e3868aA8495F5964")
    FACTORY_ADDRESS = w3_zks.to_checksum_address(
        "0x40be1cBa6C5B47cDF9da7f963B6F761F4C60627D")
    PAIR_ADDRESS = w3_zks.to_checksum_address(
        "0x0f6d5b6c5c6b5f0e5c7f8b0d0c7e9e6f5d7c0a6f")

# contract instances
router_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)
factory_contract = w3_zks.eth.contract(
    address=FACTORY_ADDRESS, abi=factory_abi)
# pair_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=pair_abi)


def get_pair_address(token1=WETH_ADDRESS, token2=USDC_ADDRESS):
    pool_address = factory_contract.functions.getPair(token1, token2, False).call()
    pool_address = w3_zks.to_checksum_address(pool_address)
    return pool_address

def get_amount_out(pair_address, token, amount_in):
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)
    if token == 'eth':
        amount_in = w3_zks.to_wei(amount_in, 'ether')
    else:
        amount_in = int(Decimal(amount_in * 10 ** 6))
    amount_out = pair_contract.functions.current(ADDRESS[token], amount_in).call()
    return amount_out


def swap_tokens(token_from='eth', token_to='usdc', amount=0.001, slippage=0.05):
    if token_from == 'eth':
        value = w3_zks.to_wei(amount, 'ether')
    else:
        # todo: swap other tokens to eth
        value = amount * 10 ** 6

    swap_pair_address = get_pair_address(ADDRESS[token_from], ADDRESS[token_to])
    amount_out = get_amount_out(swap_pair_address, token_from, amount)
    amount_out_min = int(Decimal(amount_out * (1-slippage)))

    path = [w3_zks.to_checksum_address(ADDRESS[token_from]),
            w3_zks.to_checksum_address(ADDRESS[token_to])]

    to = w3_zks.to_checksum_address(acc['address'])
    deadline = int(time.time()) + 60 * 60

    swap_function = router_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        amount_out_min, path, to, deadline, [False, False])
    tx = swap_function.build_transaction({
        'from': acc['address'],
        # 'to': ROUTER_ADDRESS,
        'gas': 15000000,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
        'value': value,
        'chainId': chain_id,
    })

    print(tx)

    # Sign the transaction
    signed_tx = w3_zks.eth.account.sign_transaction(tx, acc['private_key'])

    # Send the signed transaction
    tx_hash = w3_zks.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3_zks.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Transaction hash: {tx_hash.hex()}")
    print(f"Transaction receipt: {tx_receipt}")


if __name__ == "__main__":
    swap_tokens(amount=0.001)

