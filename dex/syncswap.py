from decimal import Decimal
from eth_abi import encode
from dex.dex import DEX
import time
from cfg import token_abi
from utils import execute_tx, get_token_info


class SyncSwap(DEX):
    def __init__(self, network='testnet', name='syncswap'):
        DEX.__init__(self, name=name, network=network)
        if network == 'testnet':
            self.token_list['eth'] = '0x20b28b1e4665fff290650586ad76e977eab90c5d'

    def get_pool_address(self, token_1, token_2):
        pool_address = self.factory_contract.functions.getPool(
            self.rpc.to_checksum_address(self.token_list[token_1]),
            self.rpc.to_checksum_address(self.token_list[token_2])).call()
        pool_address = self.rpc.to_checksum_address(pool_address)
        return pool_address

    def query_swap(self, token_from, token_to, amount, slippage=0.015):
        pool_address = self.get_pool_address(token_from, token_to)
        pool_address = self.rpc.to_checksum_address(pool_address)
        pool_contract = self.rpc.eth.contract(address=pool_address, abi=self.pool_abi)
        if token_from == 'eth':
            value = self.rpc.to_wei(amount, 'ether')
        else:
            token_info = get_token_info(self.token_list[token_from], self.rpc)
            value = int(Decimal(amount * 10 ** token_info['decimal']))
        amount_out = pool_contract.functions.getAmountOut(self.rpc.to_checksum_address(self.token_list[token_from]),
                                                          value, self.rpc.to_checksum_address(self.router_address)).call()

        amount_out_min = int(Decimal(amount_out * (1-slippage)))
        token_info_to = get_token_info(self.token_list[token_to], self.rpc)
        amount_out_min = amount_out_min / 10 ** token_info_to['decimal']
        return amount_out_min

    def swap_token(self, account, token_from, token_to, amount, slippage):
        pool_address = self.get_pool_address(token_from, token_to)
        pool_address = self.rpc.to_checksum_address(pool_address)
        if token_from == 'eth':
            value = self.rpc.to_wei(amount, 'ether')
        else:
            token_info = get_token_info(self.token_list[token_from], self.rpc)
            value = int(Decimal(amount * 10 ** token_info['decimal']))

        withdraw_mode = 1
        swap_data = encode(
            ["address", "address", "uint8"],
            [self.rpc.to_checksum_address(self.token_list[token_from]),
             self.rpc.to_checksum_address(account.address), withdraw_mode])

        steps = [(
            pool_address, swap_data,
            self.rpc.to_checksum_address("0x0000000000000000000000000000000000000000"), b'0x',
        )]

        if token_from == 'eth':
            paths = [(steps, self.rpc.to_checksum_address("0x0000000000000000000000000000000000000000"),
                      value)]
        else:
            paths = [(steps, self.rpc.to_checksum_address(self.token_list[token_from]), value)]

        current_time = int(time.time())
        big_number = current_time + 1800

        pool_contract = self.rpc.eth.contract(address=pool_address, abi=self.pool_abi)
        amount_out = pool_contract.functions.getAmountOut(self.rpc.to_checksum_address(self.token_list[token_from]),
                                                          value, self.rpc.to_checksum_address(self.router_address)).call()

        amount_out_min = int(Decimal(amount_out * (1-slippage)))
        func = self.router_contract.functions.swap(paths, amount_out_min, big_number)
        try:
            gas_estimate = func.estimate_gas({'from': account.address})
        except:
            gas_estimate = 1200000

        if token_from == 'eth':
            tx = func.build_transaction(
                {'chainId': self.chain_id,
                    'gas': gas_estimate,
                    'gasPrice': self.rpc.eth.gas_price,
                    'from': account.address,
                    'value': value,
                    'nonce': self.rpc.eth.get_transaction_count(
                      account.address)})
        else:
            tx = func.build_transaction(
                {'chainId': self.chain_id,
                    'gas': gas_estimate,
                    'gasPrice': self.rpc.eth.gas_price,
                    'from': account.address,
                    # 'value': value,
                    'nonce': self.rpc.eth.get_transaction_count(
                      account.address)})

        tx['data'] = tx['data'][:-64]
        p1 = tx['data'][:-128]
        if token_from == 'eth':
            p2 = '00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'
        else:
            p2 = '00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000'
        tx['data'] = p1 + p2
        print(tx['data'])
        success = execute_tx(tx, account, self.rpc)
        return success

    def construct_liquidity_tx_data(self, acc, token_1, token_2, amount_1, amount_2):
        function_signature = '0x94ec6d78'
        pool_address = self.get_pool_address(token_1, token_2)
        param_1 = '000000000000000000000000' + pool_address[2:]
        param_2 = '00000000000000000000000000000000000000000000000000000000000000c0'
        param_3 = '0000000000000000000000000000000000000000000000000000000000000160'
        if token_1 == 'eth':
            lp = self.calculate_receive_lp(pool_address, amount_1, amount_2)
        else:
            lp = self.calculate_receive_lp(pool_address, amount_2, amount_1)
        lp = hex(int(lp * 10 ** 18))[2:]
        # param_4 = '000000000000000000000000000000000000000000000000000001103a4545b9'
        # param_4 = '0' * (64 - len(lp)) + lp
        param_4 = '0000000000000000000000000000000000000000000000000000000000000000'
        param_4_2 = '0000000000000000000000000000000000000000000000000000000000000000'
        param_5 = '00000000000000000000000000000000000000000000000000000000000001a0'
        param_6 = '0000000000000000000000000000000000000000000000000000000000000002'

        if token_1 == 'eth':
            param_7 = '0000000000000000000000000000000000000000000000000000000000000000'
            param_8 = self.rpc.to_wei(amount_1, 'ether')
        else:
            param_7 = '0' * (64-len(self.token_list[token_1])+2) + self.rpc.to_checksum_address(self.token_list[token_1])[2:]
            param_8 = int(Decimal(amount_1 * 10 ** 6))

        param_8 = str(hex(param_8))[2:]
        param_8 = '0' * (64-len(param_8)) + param_8

        if token_2 == 'eth':
            param_9 = '0000000000000000000000000000000000000000000000000000000000000000'
            param_10 = self.rpc.to_wei(amount_1, 'ether')
        else:
            param_9 = '0' * (64-len(self.token_list[token_1])+2) + self.rpc.to_checksum_address(self.token_list[token_2])[2:]
            param_10 = int(Decimal(amount_2 * 10 ** 6))

        param_10 = str(hex(param_10))[2:]
        param_10 = '0' * (64-len(param_10)) + param_10
        param_12 = '0000000000000000000000000000000000000000000000000000000000000020'
        param_13 = '0' * (64-len(acc.address)+2) + self.rpc.to_checksum_address(acc.address)[2:]
        param_14 = '0000000000000000000000000000000000000000000000000000000000000000'
        tx_data = function_signature + param_1 + param_2 + param_3 + param_4 + param_4_2 + param_5 + param_6 + \
                  param_7 + param_8 + param_9 + param_10 + param_12 + param_13 + param_14

        return tx_data

    def construct_burn_lp_data(self, acc, token_1, token_2, slippage):
        function_signature = '0x53c43f15'
        pool_address = self.get_pool_address(token_1, token_2)
        param_1 = '000000000000000000000000' + pool_address[2:]
        lp_balance = acc.get_lp_balance(pool_address, 'zks_era_' + self.network)
        hex_lp = hex(lp_balance)[2:]
        param_2 = '0' * (64-len(hex_lp)) + hex_lp
        param_3 = '00000000000000000000000000000000000000000000000000000000000000c0'
        # param_4 = '0000000000000000000000000000000000000000000000000000000000000000'
        receive_eth = self.calculate_receive_eth(pool_address, lp_balance, slippage)
        receive_eth = self.rpc.to_wei(receive_eth, 'ether')
        receive_eth = hex(receive_eth)[2:]
        print(lp_balance, receive_eth)
        param_4 = '0' * (64-len(receive_eth)) + receive_eth
        param_5 = '0000000000000000000000000000000000000000000000000000000000000000'
        param_6 = '0000000000000000000000000000000000000000000000000000000000000140'
        param_7 = '0000000000000000000000000000000000000000000000000000000000000060'
        param_8 = '0' * (64-len(self.token_list['eth'])+2) + self.rpc.to_checksum_address(self.token_list['eth'])[2:]
        param_9 = '0' * (64-len(acc.address)+2) + self.rpc.to_checksum_address(acc.address)[2:]
        param_10 = '0000000000000000000000000000000000000000000000000000000000000001'
        param_11 = '0000000000000000000000000000000000000000000000000000000000000000'

        tx_data = function_signature + param_1 + param_2 + param_3 + param_4 + \
            param_5 + param_6 + param_7 + param_8 + param_9 + param_10 + param_11

        return tx_data


    def add_liquidity(self, account, token_1, token_2, amount_1, amount_2):
        tx_data = self.construct_liquidity_tx_data(account, token_1, token_2, amount_1, amount_2)
        if token_1 == 'eth':
            value = self.rpc.to_wei(amount_1, 'ether')
            approved_amount = self.check_approval(account, token_2, self.router_address)
            if approved_amount < amount_2 * 10 ** 6:
                self.approve_token(account, token_2, amount_2)
        elif token_2 == 'eth':
            value = self.rpc.to_wei(amount_2, 'ether')
            approved_amount = self.check_approval(account, token_1, self.router_address)
            if approved_amount < amount_1 * 10 ** 6:
                self.approve_token(account, token_2, amount_1)



        tx = {'chainId': self.chain_id,
                    'gas': 4000000,
                    'gasPrice': self.rpc.eth.gas_price,
                    'from': account.address,
                    'value': value,
                    'nonce': self.rpc.eth.get_transaction_count(
                      account.address),
              'data': tx_data,
              'to': self.rpc.to_checksum_address(self.router_address)}
        print(tx)
        success = execute_tx(tx, account, self.rpc)

    def remove_liquidity(self, account, token_1, token_2, slippage=0.005):
        # approve LP token
        pool_address = self.get_pool_address(token_1, token_2)
        lp_balance = account.get_lp_balance(pool_address, 'zks_era_' + self.network)
        approved_amount = self.check_approval(account, self.rpc.to_checksum_address(pool_address),
                                              self.router_address)
        print(approved_amount)
        if approved_amount < lp_balance:
            self.approve_token(account, pool_address, lp_balance)

        tx_data = self.construct_burn_lp_data(account, token_1, token_2, slippage)
        tx = {'chainId': self.chain_id,
                    'gas': 800000,
                    'gasPrice': self.rpc.eth.gas_price,
                    'from': account.address,
                    # 'value': value,
                    'nonce': self.rpc.eth.get_transaction_count(
                      account.address),
              'data': tx_data,
              'to': self.rpc.to_checksum_address(self.router_address)}
        print(tx['data'])
        success = execute_tx(tx, account, self.rpc)

    def calculate_receive_lp(self, pool_address, amount_eth, amount_token, slippage=0.05):
        pool_contract = self.rpc.eth.contract(address=pool_address, abi=self.pool_abi)
        token_0_address = pool_contract.functions.token0().call()
        reserve_0 = pool_contract.functions.reserve0().call()
        reserve_1 = pool_contract.functions.reserve1().call()

        if token_0_address == self.rpc.to_checksum_address(self.token_list['eth']):
            reserve_eth = Decimal(reserve_0) / Decimal(10 ** 18)
            reserve_token = Decimal(reserve_1) / Decimal(10 ** 6)
        else:
            reserve_eth = Decimal(reserve_1) / Decimal(10 ** 18)
            reserve_token = Decimal(reserve_0) / Decimal(10 ** 6)

        token_price = reserve_token / reserve_eth
        token_eq_eth = amount_token / token_price
        total_add_eth = Decimal(amount_eth) + token_eq_eth
        total_pool = reserve_eth * 2
        receive_lp = total_add_eth * Decimal(1 - slippage) / total_pool

        return receive_lp

    def calculate_receive_eth(self, pool_address, lp_balance, slippage=0.005):
        pool_contract = self.rpc.eth.contract(address=pool_address, abi=self.pool_abi)
        # lp_balance = Decimal(lp_balance) / Decimal(10 ** 18)
        total_lp = pool_contract.functions.totalSupply().call()
        pool_share = lp_balance / Decimal(total_lp)
        token_0_address = pool_contract.functions.token0().call()
        # token_1_address = pool_contract.functions.token1().call()
        reserve_0 = pool_contract.functions.reserve0().call()
        reserve_1 = pool_contract.functions.reserve1().call()

        if token_0_address == self.rpc.to_checksum_address(self.token_list['eth']):
            reserve_eth = Decimal(reserve_0) / Decimal(10 ** 18)
        else:
            reserve_eth = Decimal(reserve_1) / Decimal(10 ** 18)
        #
        total_pool = reserve_eth * 2
        receive_eth = total_pool * pool_share * Decimal((1 - slippage))
        # receive_eth = self.rpc.to_wei(receive_eth, 'ether')
        return receive_eth

