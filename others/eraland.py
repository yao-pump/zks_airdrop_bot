import json
from decimal import Decimal

from base.zks_app_base import BaseAPP
from cfg import token_abi
from utils import execute_tx, get_token_info


class EraLand(BaseAPP):
    def __init__(self):
        BaseAPP.__init__(self, name='eraland', network='mainnet')
        with open("config/eraland_eth_abi.json", encoding='utf-8', errors='ignore') as json_data:
            eth_abi = json.load(json_data, strict=False)
        with open("config/eraland_usdc_abi.json", encoding='utf-8', errors='ignore') as json_data:
            usdc_abi = json.load(json_data, strict=False)
        self.usdc_address = '0x1181D7BE04D80A8aE096641Ee1A87f7D557c6aeb'
        self.eth_contract = self.rpc.eth.contract(
                address='0x1BbD33384869b30A323e15868Ce46013C82B86FB', abi=eth_abi)
        self.usdc_contract = self.rpc.eth.contract(
                address='0x1181D7BE04D80A8aE096641Ee1A87f7D557c6aeb', abi=usdc_abi)

    def approve_udsc(self, account):
        token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(self.token_list['usdc']),
                                                   abi=token_abi)

        token_info = get_token_info(self.token_list['usdc'], self.rpc)

        amount = account.get_balance('tudsc', 'zks_era', 'mainnet')
        amount_approve = amount * 10 ** token_info['decimal']
        func = token_contract.functions.approve(
            self.rpc.to_checksum_address(self.usdc_address), int(Decimal(amount_approve)))

        gas_estimate = func.estimate_gas({'from': account.address})

        tx = func.build_transaction(
            {'chainId': self.chain_id,
                'gas': gas_estimate,
                'gasPrice': self.rpc.eth.gas_price,
                'from': account.address,
                'nonce': self.rpc.eth.get_transaction_count(
                    account.address)})
        print("Transaction: approve token")
        success = execute_tx(tx, account, self.rpc)
        return success

    def supply(self, account, symbol, amount):
        if symbol == 'eth':
            amount = self.rpc.to_wei(amount, 'ether')
            func = self.eth_contract.functions.mint()
            gas_estimate = func.estimate_gas({'from': account.address})
            tx = func.build_transaction(
                {'chainId': self.chain_id,
                 'gas': gas_estimate,
                 'gasPrice': self.rpc.eth.gas_price,
                 'from': account.address,
                 'value': amount,
                 'nonce': self.rpc.eth.get_transaction_count(
                     account.address)})
        elif symbol == 'usdc':
            # approve first
            success_approve = self.approve_udsc(account)
            if success_approve:
                amount = int(amount * 10 ** 6)
                func = self.usdc_contract.functions.mint(amount)
                gas_estimate = func.estimate_gas({'from': account.address})
                tx = func.build_transaction(
                    {'chainId': self.chain_id,
                     'gas': gas_estimate,
                     'gasPrice': self.rpc.eth.gas_price,
                     'from': account.address,
                     'nonce': self.rpc.eth.get_transaction_count(
                         account.address)})

                success = execute_tx(tx, account, self.rpc)
                return success
            else:
                return success_approve

    def redeem(self, account, symbol, amount):
        if symbol == 'eth':
            amount = self.rpc.to_wei(amount, 'ether')
            func = self.eth_contract.functions.redeemUnderlying(amount)
        elif symbol == 'usdc':
            amount = int(amount * 10 ** 6)
            func = self.usdc_contract.functions.redeemUnderlying(amount)

        gas_estimate = func.estimate_gas({'from': account.address})
        tx = func.build_transaction(
            {'chainId': self.chain_id,
             'gas': gas_estimate,
             'gasPrice': self.rpc.eth.gas_price,
             'from': account.address,
             'nonce': self.rpc.eth.get_transaction_count(
                 account.address)})

        success = execute_tx(tx, account, self.rpc)
        return success

    def check_supply(self, account, symbol):
        if symbol == 'eth':
            supply_amount = self.eth_contract.functions.balanceOfUnderlying(account.address).call()
            supply_amount = supply_amount * 10 ** (-18)
        elif symbol == 'usdc':
            supply_amount = self.usdc_contract.functions.balanceOfUnderlying(account.address).call()
            supply_amount = supply_amount * 10 ** (-6)

        return supply_amount
