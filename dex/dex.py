from decimal import Decimal

from cfg import get_dex_info, zks_token_addresses, providers, chains, token_abi
import json
from web3 import Web3, HTTPProvider

from utils import execute_tx
import random


class DEX:
    def __init__(self, name, network='testnet'):
        self.name = name
        self.network = network
        self.token_list = zks_token_addresses[network]
        self.rpc = Web3(HTTPProvider(providers['zks_era_{}'.format(network)]))
        self.chain_id = chains['zks_era_{}'.format(network)]
        # self.router_address, self.factory_address, self.abi_paths = get_dex_info(
        #     self.name, self.network)
        self.addresses, self.abi_paths = get_dex_info(
            self.name, self.network)

        self.factory_address = self.addresses['factory']
        self.router_address = self.addresses['router']

        with open("config/{}".format(self.abi_paths['pool']), encoding='utf-8', errors='ignore') as json_data:
            self.pool_abi = json.load(json_data, strict=False)

        with open("config/{}".format(self.abi_paths['factory']), encoding='utf-8', errors='ignore') as json_data:
            self.factory_abi = json.load(json_data, strict=False)
            self.factory_contract = self.rpc.eth.contract(
                address=self.factory_address, abi=self.factory_abi)

        with open("config/{}".format(self.abi_paths['router']), encoding='utf-8', errors='ignore') as json_data:
            self.router_abi = json.load(json_data, strict=False)
            self.router_contract = self.rpc.eth.contract(
                address=self.router_address, abi=self.router_abi)

    def swap(self, account, token_from, token_to, amount, slippage):
        # approve token
        if token_from != 'eth':
            value = int(Decimal(amount * 10 ** 6))
            approved_amount = self.check_approval(
                account, token_from, self.router_address)
            if approved_amount < value:
                tx_status = self.approve_token(account, token_from, amount)
                if tx_status != 1:
                    print('Approve token failed. Stop swap.')
                    return

        self.swap_token(account, token_from, token_to, amount, slippage)

    def swap_token(self, account, token_from, token_to, amount, slippage):
        pass

    def get_liquidity_info(self, account, token_1, token_2):
        pass

    def add_liquidity(self, account, token_1, token_2, amount_1, amount_2):
        pass

    def remove_liquidity(self, account, token_1, token_2, amount_1, amount_2):
        pass

    def remove_liquidity(self, account, token_1, token_2, liquidity_rate):
        pass

    def approve_token(self, account, token, amount):
        if len(token) < 10:
            token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(self.token_list[token]),
                                                   abi=token_abi)
        else:
            token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(token),
                                                   abi=token_abi)
        func = token_contract.functions.approve(
            self.router_address, int(Decimal(amount * 10 ** 6)))
        gas_estimate = func.estimate_gas({'from': account.address})
        # get random gas
        gas_estimate = int(gas_estimate*random.uniform(1, 1.2))

        tx = func.build_transaction(
            {'chainId': self.chain_id,
                'gas': gas_estimate,  # TODO: random gas
                'gasPrice': self.rpc.eth.gas_price,
                'from': account.address,
                'nonce': self.rpc.eth.get_transaction_count(
                    account.address)})
        print("Transaction: approve token")
        success = execute_tx(tx, account, self.rpc)

    def approve_token_mute(self, account, token, amount):
        token_contract = self.rpc.eth.contract(
            address=token, abi=self.pool_abi)
        approve_function = token_contract.functions.approve(
            self.router_address, amount)

        transaction_object = {
            'from': account.address,
            'gas': 15000000,
            'gasPrice': self.rpc.eth.gas_price,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
            'chainId': self.chain_id,
        }
        estimated_gas = approve_function.estimate_gas(transaction_object)
        transaction_object['gas'] = estimated_gas

        approve_tx = approve_function.build_transaction(transaction_object)
        success = execute_tx(approve_tx, account, self.rpc)

    def check_approval(self, account, token, spender_address):
        if len(token) < 10:
            token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(self.token_list[token]),
                                                   abi=token_abi)
        else:
            token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(token),
                                                   abi=token_abi)
        approved_amount = token_contract.functions.allowance(
            account.address, spender_address).call()
        return approved_amount
