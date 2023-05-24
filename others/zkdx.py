import json
from decimal import Decimal

from cfg import rpcs, chains, token_abi
from base.zks_app_base import BaseAPP
from utils import execute_tx, get_token_info, get_coin_price, price_feed_ids, get_update_data
import requests



class ZkDX(BaseAPP):
    def __init__(self):
        BaseAPP.__init__(self, name='zkdx', network='mainnet')
        self.faucet_address = "0x7455eb101303877511d73c5841Fbb088801f9b12"
        self.approve_address = "a6dbd1bdb1dc4339df51d90ce306cce6edfbbbb1"
        self.trade_address = "0xBe8f858A61E740F40871306ee154E460A4B7c771"
        self.dx_coins = {
            'btc': '0xd2Ff1D57C6b098f02c067FC294542D33EB7c2fA6',
            'eth': '0xe74E124f6BFED634EbbD421010ea9e8527aBCab3',
            'doge': '0xB613a4445cdcD8F98d156C47434673e3fd21FcD0',
            'ltc': '0xcCb504941ED744F472079447AdaE9A04EaF48CF8',
        }
        with open("config/{}".format('zkdx.json'), encoding='utf-8', errors='ignore') as json_data:
            abi = json.load(json_data, strict=False)
        self.trade_contract = self.rpc.eth.contract(
                address=self.trade_address, abi=abi)

    def claim_tudsc(self, account):
        tx_data = "0xde5f72fd"
        tx = {'chainId': self.chain_id,
              'gas': 1200000,
              'gasPrice': self.rpc.eth.gas_price,
              'from': account.address,
              'value': 0,
              'nonce': self.rpc.eth.get_transaction_count(
                  account.address),
              'data': tx_data,
              'to': self.rpc.to_checksum_address(self.faucet_address)}

        success = execute_tx(tx, account, self.rpc)
        return success

    def approve_tudsc(self, account):
        token_contract = self.rpc.eth.contract(address=self.rpc.to_checksum_address(self.faucet_address),
                                                   abi=token_abi)

        token_info = get_token_info(self.faucet_address, self.rpc)

        amount = account.get_balance('tudsc', 'zks_era', 'mainnet')
        amount_approve = amount * 10 ** token_info['decimal']
        func = token_contract.functions.approve(
            self.rpc.to_checksum_address(self.approve_address), int(Decimal(amount_approve)))

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


    def increase_position(self, account, amount_tusdc, symbol='eth', leverage=2, is_long=True, slippage=0.003):
        if is_long:
            path = [self.faucet_address, self.dx_coins[symbol]]
        else:
            path = [self.faucet_address]
        index_token = self.dx_coins[symbol]
        token_info = get_token_info(self.faucet_address, self.rpc)
        amount_in = int(amount_tusdc * 10 ** token_info['decimal'])
        min_out = 0
        usdc_price, conf, expo = get_coin_price('tusdc')
        usdc_price = (usdc_price - conf) * 10 ** expo
        amount_position = usdc_price * amount_tusdc
        # size_delta = (amount_position - fee) * leverage
        # position_size = amount_position * leverage * (1 - slippage)
        swap_fee = 29.999
        size_delta = (amount_position - swap_fee) * leverage / (1 + 0.001 * leverage)
        # size_delta = int(Decimal(size_delta) * 10 ** 30)
        size_delta = int(Decimal(size_delta * 10 ** 20) * 10 ** 10)
        # fee = swap_fee + 0.001 * size_delta
        # position_fee = amount_position * 0.001
        # fee = swap_fee + position_fee
        # size_delta = int((position_size - fee) * 10 ** token_info['decimal']) * 10 ** 12
        price, conf, expo = get_coin_price(symbol)
        # price = int(price * (1 + 0.003))
        if is_long:
            price = int(round((price+conf) * 10 ** expo * 1.003, 5) * 10 ** 5) * 10 ** 25
        else:
            price = int(round((price-conf) * 10 ** expo * 0.997, 5) * 10 ** 5) * 10 ** 25

        update_data = get_update_data(symbol)
        # update_data = update_data[-1::]
        func = self.trade_contract.functions.increasePosition(path, index_token, amount_in, min_out,
                                                              size_delta, is_long, price, [])
        # gas_estimate = func.estimate_gas({'from': account.address})
        # print(gas_estimate)
        tx = func.build_transaction(
            {'chainId': self.chain_id,
             'gas': 8000000,
             'gasPrice': self.rpc.eth.gas_price,
             'from': account.address,
             # 'value': value,
             'nonce': self.rpc.eth.get_transaction_count(
                 account.address)})

        print(path, index_token, amount_in, min_out, size_delta, is_long, price)
        print(tx['data'])
        execute_tx(tx, account, self.rpc)


    def decrease_position(self, account, size_delta, symbol='eth', is_long=True):
        if is_long:
            path = [self.dx_coins[symbol], self.faucet_address]
        else:
            path = [self.dx_coins[symbol]]

        index_token = self.dx_coins[symbol]
        collateral_delta = 0
        receiver = account.address
        price, conf, expo = get_coin_price(symbol)
        if is_long:
            price = int(round((price-conf) * 10 ** expo * 0.997, 5) * 10 ** 5) * 10 ** 25
        else:
            price = int(round((price+conf) * 10 ** expo * 1.003, 5) * 10 ** 5) * 10 ** 25

        min_out = 0
        withdraw_eth = False
        update_data = []
        func = self.trade_contract.functions.decreasePosition(path, index_token, collateral_delta,
                                                              size_delta, is_long, receiver,
                                                              price, min_out, withdraw_eth, update_data)
        gas_estimate = func.estimate_gas({'from': account.address})
        # print(gas_estimate)
        tx = func.build_transaction(
            {'chainId': self.chain_id,
             'gas': gas_estimate,
             'gasPrice': self.rpc.eth.gas_price,
             'from': account.address,
             # 'value': value,
             'nonce': self.rpc.eth.get_transaction_count(
                 account.address)})

        # print(path, index_token, amount_in, min_out, size_delta, is_long, price)
        print(tx['data'])
        execute_tx(tx, account, self.rpc)