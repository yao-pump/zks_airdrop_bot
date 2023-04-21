import json
import time
from decimal import Decimal

from web3 import Web3, HTTPProvider
from utils import get_accounts, get_providers
import asyncio
from eth_abi import encode

providers = get_providers()
provider_url = providers['zks_era']
# provider_url = providers['zks_testnet']
w3_zks = Web3(HTTPProvider(provider_url))

accounts = get_accounts()
acc = accounts[0]

ETH_ADDRESS = w3_zks.to_checksum_address(
    "0x0000000000000000000000000000000000000000")
WETH_ADDERSS = w3_zks.to_checksum_address(
    "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91")
UDSC_ADDRESS = w3_zks.to_checksum_address(
    "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4")

# ABIs
with open("config/muteswap_pair_abi.json", encoding='utf-8', errors='ignore') as json_data:
    pair_abi = json.load(json_data, strict=False)

with open("config/muteswap_factory_abi.json", encoding='utf-8', errors='ignore') as json_data:
    factory_abi = json.load(json_data, strict=False)

with open("config/muteswap_router_abi.json", encoding='utf-8', errors='ignore') as json_data:
    router_abi = json.load(json_data, strict=False)

# contract addresses
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
pair_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=pair_abi)


# swap tokens using router contract
def swap_tokens(amount_out_min, path, to, deadline):

    swap_function = router_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        amount_out_min, path, to, deadline, [False, False])
    tx = swap_function.build_transaction({
        'from': acc['address'],
        # 'to': ROUTER_ADDRESS,
        'gas': 15000000,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
        # 'value': 0,
        # testnet chainId
        # 'chainId': 280,
        # mainnet chainId
        'chainId': 324,
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

    # amount_out_min = w3_zks.to_wei(Decimal('1.9'), 'usdc')
    amount_out_min = 1900616
    path = [w3_zks.to_checksum_address(
        WETH_ADDERSS), w3_zks.to_checksum_address(UDSC_ADDRESS)]
    to = w3_zks.to_checksum_address(acc['address'])
    deadline = int(time.time()) + 60*60
    swap_tokens(amount_out_min, path, to, deadline)

    # balance = w3_zks.eth.get_balance(acc['address'])
    # print(f"Balance: {w3_zks.from_wei(balance, 'ether')} ETH")
