from decimal import Decimal
from eth_abi import encode
from dex.dex import DEX
import json
import time

from utils import append_hex, fee2Hex, get_token_info, execute_tx, num2Hex


class IzumiSwap(DEX):
    def __init__(self, network='testnet', name='izumiswap'):
        DEX.__init__(self, name=name, network=network)
        if network == 'testnet':
            self.token_list['eth'] = '0x8C3e3f2983DB650727F3e05B7a7773e4D641537B'

        with open("config/{}".format(self.abi_paths['quoter']), encoding='utf-8', errors='ignore') as json_data:
            self.quoter_abi = json.load(json_data, strict=False)
            self.quoter_contract = self.rpc.eth.contract(
                address=self.addresses['quoter'], abi=self.quoter_abi)

    def query_swap(self, path, token_from, token_info_from, amount, fee=2000):
        # token_info_from = get_token_info(self.token_list[token_from], self.rpc)
        # # token_info_to = get_token_info(self.token_list[token_to], self.rpc)
        # path = self.get_token_chain_path(token_from, token_to, fee)
        if token_from != 'eth':
            swap_amount = int(Decimal(amount * 10 ** token_info_from['decimal']))
        else:
            swap_amount = self.rpc.to_wei(amount, 'ether')
        output_amount, final_points = self.quoter_contract.functions.swapAmount(swap_amount, path).call()

        return output_amount, final_points

    def swap_token(self, account, token_from, token_to, amount, slippage=0.015):
        # try:
        multicall = []

        deadline = int('0xffffffff', 16)
        # current_time = int(time.time())
        # deadline = current_time + 1800
        path = self.get_token_chain_path(token_from, token_to)
        token_info_from = get_token_info(self.token_list[token_from], self.rpc)
        amount_out, _ = self.query_swap(path, token_from, token_info_from, amount)
        amount_out_min = int(Decimal(amount_out * (1-slippage)))
        final_recipient_address = account.address
        if token_to == 'eth':
            inner_recipient_address = '0x0000000000000000000000000000000000000000'
        else:
            inner_recipient_address = final_recipient_address

        if token_from != 'eth':
            swap_amount = int(Decimal(amount * 10 ** token_info_from['decimal']))
            value = 0
        else:
            swap_amount = self.rpc.to_wei(amount, 'ether')
            value = swap_amount

        func = self.router_contract.functions.swapAmount([path, inner_recipient_address, swap_amount,
                                                         amount_out_min, deadline])
        # gas_estimate = func.estimate_gas({'from': account.address})

        multicall.append(self.router_contract.encodeABI(fn_name='swapAmount', args=[[path, inner_recipient_address, swap_amount, amount_out_min, deadline]]))
        if token_from == 'eth':
            multicall.append(self.router_contract.encodeABI(fn_name='refundETH'))

        if token_to == 'eth':
            multicall.append(self.router_contract.encodeABI(fn_name='unwrapWETH9', args=[0, account.address]))
        # multicall = [1]
        if len(multicall) == 1:
            tx = func.build_transaction(
            {'chainId': self.chain_id,
                'gas': 5000000,
                'gasPrice': self.rpc.eth.gas_price,
                'from': account.address,
                'value': value,
                'nonce': self.rpc.eth.get_transaction_count(
                  account.address)})
        else:
            func = self.router_contract.functions.multicall(multicall)
            try:
                gas_estimate = func.estimate_gas({'from': account.address})
            except:
                gas_estimate = 5000000
            tx = func.build_transaction(
            {'chainId': self.chain_id,
                'gas': gas_estimate,
                'gasPrice': self.rpc.eth.gas_price,
                'from': account.address,
                'value': value,
                'nonce': self.rpc.eth.get_transaction_count(
                  account.address)})

        success = execute_tx(tx, account, self.rpc)
        return success
        # except:
        #     return False


    def get_token_chain_path(self, token_from, token_to, fee=2000):
        token_info_from = get_token_info(self.token_list[token_from], self.rpc)
        token_info_to = get_token_info(self.token_list[token_to], self.rpc)
        token_chain = [token_info_from['address'], token_info_to['address']]
        fee_chain = [fee]

        path = token_chain[0]
        for i in range(len(fee_chain)):
            path = append_hex(path, fee2Hex(fee_chain[i]))
            path = append_hex(path, token_chain[i+1])


        return path

