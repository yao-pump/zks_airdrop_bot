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
acc = accounts[0]

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
else:
    ROUTER_ADDRESS = w3_zks.to_checksum_address(
        "0x8B791913eB07C32779a16750e3868aA8495F5964")
    FACTORY_ADDRESS = w3_zks.to_checksum_address(
        "0x40be1cBa6C5B47cDF9da7f963B6F761F4C60627D")

# contract instances
router_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)
factory_contract = w3_zks.eth.contract(
    address=FACTORY_ADDRESS, abi=factory_abi)
# pair_contract = w3_zks.eth.contract(address=ROUTER_ADDRESS, abi=pair_abi)


def get_pair_address(token1=WETH_ADDRESS, token2=USDC_ADDRESS):
    pool_address = factory_contract.functions.getPair(
        token1, token2, False).call()
    pool_address = w3_zks.to_checksum_address(pool_address)
    return pool_address


def get_amount_out(pair_address, token, amount_in):
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)
    if token == 'eth':
        amount_in = w3_zks.to_wei(amount_in, 'ether')
    else:
        amount_in = int(Decimal(amount_in * 10 ** 6))
    amount_out = pair_contract.functions.current(
        ADDRESS[token], amount_in).call()
    return amount_out

# approve_token(pair_address, ROUTER_ADDRESS, amount_token_min, acc)


def approve_token(token_address, spender, amount, account):
    token_contract = w3_zks.eth.contract(address=token_address, abi=pair_abi)
    approve_function = token_contract.functions.approve(spender, amount)

    transaction_object = {
        'from': account['address'],
        'gas': 15000000,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(account['address']),
        'chainId': chain_id,
    }
    estimated_gas = approve_function.estimate_gas(transaction_object)
    transaction_object['gas'] = estimated_gas

    approve_tx = approve_function.build_transaction(transaction_object)
    signed_approve_tx = w3_zks.eth.account.sign_transaction(
        approve_tx, account['private_key'])
    tx_hash = w3_zks.eth.send_raw_transaction(signed_approve_tx.rawTransaction)

    tx_receipt = w3_zks.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def swap_tokens(token_from='eth', token_to='usdc', amount=0.001, slippage=0.05):
    token_from_address = ADDRESS[token_from]
    token_to_address = ADDRESS[token_to]

    if token_from == 'eth':
        value = w3_zks.to_wei(amount, 'ether')
    else:
        value = int(Decimal(amount * 10 ** 6))

    swap_pair_address = get_pair_address(token_from_address, token_to_address)
    amount_out = get_amount_out(swap_pair_address, token_from, amount)
    amount_out_min = int(Decimal(amount_out * (1 - slippage)))

    path = [w3_zks.to_checksum_address(token_from_address),
            w3_zks.to_checksum_address(token_to_address)]

    to = w3_zks.to_checksum_address(acc['address'])
    deadline = int(time.time()) + 60 * 60

    if token_from == 'eth':
        swap_function = router_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            amount_out_min, path, to, deadline, [False, False])
    else:
        approve_token(token_from_address, ROUTER_ADDRESS, value, acc)
        swap_function = router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            value, amount_out_min, path, to, deadline, [False, False])

    # Build the transaction object without the gas and gasPrice
    transaction_object = {
        'from': acc['address'],
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
        'value': 0 if token_from != 'eth' else value,
        'chainId': chain_id,
    }

    # Estimate gas for the transaction
    estimated_gas = swap_function.estimate_gas(transaction_object)

    # Add a buffer to the estimated gas (e.g., 10%)
    gas_limit = int(estimated_gas * 1.2)

    # Update the transaction object with the gas limit and gas price
    transaction_object.update({
        'gas': gas_limit,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
    })

    # Build the transaction
    tx = swap_function.build_transaction(transaction_object)

    # Sign the transaction
    signed_tx = w3_zks.eth.account.sign_transaction(tx, acc['private_key'])

    # Send the signed transaction
    tx_hash = w3_zks.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3_zks.eth.wait_for_transaction_receipt(tx_hash)


def get_token_rate(pair_address):
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    reserve_eth = Web3.from_wei(reserves[0], 'ether')
    reserve_usdc = reserves[1] / (10 ** 6)

    rate = reserve_usdc / float(reserve_eth)
    return rate


def add_liquidity(token='usdc', amount=2):
    token_address = ADDRESS[token]

    if token == 'eth':
        amount = w3_zks.to_wei(amount, 'ether')
    else:
        amount = int(Decimal(amount * 10**6))

    slippage = 0.001
    amountTokenMin = int(amount*(1-slippage))
    token_rate = get_token_rate(get_pair_address())
    amountETHMin = int((token_rate*amountTokenMin)/10**12)
    feeType = int(50)
    to = w3_zks.to_checksum_address(acc['address'])
    deadline = int(time.time()) + 60 * 60  # Deadline: 1 hour from now

    # Approve router contract to spend the tokens on behalf of the user
    approve_token(token_address, ROUTER_ADDRESS, amount, acc)

    add_liquidity_function = router_contract.functions.addLiquidityETH(
        # token to pair with eth
        token_address,
        # amount of token to add
        amount,
        # amount token min
        amountTokenMin,
        # amount eth min
        amountETHMin,
        # address where the liquidity tokens will be sent
        to,
        # timestamp represent the latest time the transaction is valid
        deadline,
        # An integer value representing the type of fee for the liquidity provider.
        feeType,
        # stable
        False
    )

    transcation_object = {
        'from': acc['address'],
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
        'chainId': chain_id,
        'value': amountETHMin,
    }
    try:
        estimated_gas = add_liquidity_function.estimate_gas(transcation_object)
        print("estimated gas: ", estimated_gas)
    except BaseException as e:
        estimated_gas = 2000000
        print('estimate gas error: ', e)
    gas_limit = int(estimated_gas * 1.2)

    # Update the transaction object with the gas limit and gas price
    transcation_object.update({
        'gas': gas_limit,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
    })

    # Build the transaction
    tx = add_liquidity_function.build_transaction(transcation_object)

    # Sign the transaction
    signed_tx = w3_zks.eth.account.sign_transaction(tx, acc['private_key'])

    # Send the signed transaction
    tx_hash = w3_zks.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3_zks.eth.wait_for_transaction_receipt(tx_hash)


def get_liquidity_balance(account, pair_address):
    # Create a contract instance for the pair using the pair's ABI
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)

    # Get the user's liquidity balance in the pool
    liquidity_balance = pair_contract.functions.balanceOf(
        account['address']).call()

    return liquidity_balance


def remove_liquidity(token='usdc', liquidity_rate=1.0):
    token_address = ADDRESS[token]

    # Get the user's liquidity balance in the pool
    liquidity_balance = get_liquidity_balance(acc, get_pair_address())
    liquidity = int(liquidity_balance * liquidity_rate)

    # Get reserves
    reserve_usdc, reserve_eth = get_reserves(get_pair_address())
    # get total lp supply
    total_lp_supply = get_total_lp(get_pair_address(), pair_abi)

    Slippage = 0.001
    amount_token_min = int(
        ((reserve_usdc/total_lp_supply) * liquidity_balance)*(1-Slippage))
    amount_eth_min = int(
        ((reserve_eth/total_lp_supply) * liquidity_balance)*(1-Slippage))
    to = w3_zks.to_checksum_address(acc['address'])
    deadline = int(time.time()) + 60 * 60  # Deadline: 1 hour from now
    stable = False

    # Approve router contract to spend the liquidity tokens on behalf of the user
    pair_address = get_pair_address()
    approve_token(pair_address, ROUTER_ADDRESS, amount_token_min, acc)

    remove_liquidity_function = router_contract.functions.removeLiquidityETHSupportingFeeOnTransferTokens(
        token_address,
        liquidity,
        amount_token_min,
        amount_eth_min,
        to,
        deadline,
        stable
    )

    transaction_object = {
        'from': acc['address'],
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
        'chainId': chain_id,
    }
    try:
        estimated_gas = remove_liquidity_function.estimate_gas(
            transaction_object)
        print("estimated gas: ", estimated_gas)
    except BaseException as e:
        estimated_gas = 3300000
        print("Unable to estimate_gas, error message: ", e)
        print("Using gas limit of ", estimated_gas)

    gas_limit = int(estimated_gas * 1.2)

    # Update the transaction object with the gas limit and gas price
    transaction_object.update({
        'gas': gas_limit,
        'gasPrice': w3_zks.eth.gas_price,
        'nonce': w3_zks.eth.get_transaction_count(acc['address']),
    })

    remove_tx = remove_liquidity_function.build_transaction(transaction_object)
    signed_remove_tx = w3_zks.eth.account.sign_transaction(
        remove_tx, acc['private_key'])
    tx_hash = w3_zks.eth.send_raw_transaction(signed_remove_tx.rawTransaction)

    tx_receipt = w3_zks.eth.wait_for_transaction_receipt(tx_hash)
    # print('transaction_hash: ', tx_hash)
    # print('Transaction receipt: ', tx_receipt)
    return tx_receipt


def get_reserves(pair_address):
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    token0_address = pair_contract.functions.token0().call()

    if token0_address.lower() == ADDRESS['eth'].lower():
        reserve_eth = reserves[0]
        reserve_usdc = reserves[1]
    else:
        reserve_eth = reserves[1]
        reserve_usdc = reserves[0]

    return reserve_usdc, reserve_eth


def get_total_lp(pair_address, pair_abi):
    pair_contract = w3_zks.eth.contract(address=pair_address, abi=pair_abi)
    total_supply = pair_contract.functions.totalSupply().call()
    return total_supply


if __name__ == "__main__":
    # swap_tokens(amount=0.1)
    # swap_tokens(token_from='usdc', token_to='eth', amount=500, slippage=0.1)

    # add_liquidity(token='usdc', amount=500)

    remove_liquidity(token='usdc', liquidity_rate=1.0)
