from decimal import Decimal
from eth_abi import encode
from dex.dex import DEX
import time
from cfg import token_abi
from utils import execute_tx
from web3 import Web3


class MuteSwap(DEX):
    def __init__(self, name='muteswap', network='testnet'):
        super().__init__(name, network)
        if network == 'testnet':
            self.token_list['eth'] = '0x20b28b1e4665fff290650586ad76e977eab90c5d'

    def get_pair_address(self, token_1, token_2):
        pool_address = self.factory_contract.functions.getPair(
            self.rpc.to_checksum_address(self.token_list[token_1]),
            self.rpc.to_checksum_address(self.token_list[token_2]), False).call()
        pool_address = self.rpc.to_checksum_address(pool_address)
        return pool_address

    def get_liquidity_balance(self, account, pair_address):
        # Create a contract instance for the pair using the pair's ABI
        pair_contract = self.rpc.eth.contract(
            address=pair_address, abi=self.pool_abi)

        # Get the user's liquidity balance in the pool
        liquidity_balance = pair_contract.functions.balanceOf(
            account['address']).call()

        return liquidity_balance

    def get_amount_out(self, pair_address, token, amount_in):
        pair_contract = self.rpc.eth.contract(
            address=pair_address, abi=self.pool_abi)
        if token == 'eth':
            amount_in = self.rpc.to_wei(amount_in, 'ether')
        else:
            amount_in = int(Decimal(amount_in * 10 ** 6))
        amount_out = pair_contract.functions.current(
            self.rpc.to_checksum_address(self.token_list[token]), amount_in).call()
        return amount_out

    def get_token_rate(self, pair_address):
        pair_contract = self.rpc.eth.contract(
            address=pair_address, abi=self.pool_abi)
        reserves = pair_contract.functions.getReserves().call()
        reserve_eth = Web3.from_wei(reserves[0], 'ether')
        reserve_usdc = reserves[1] / (10 ** 6)

        rate = reserve_usdc / float(reserve_eth)
        return rate

    def swap_token(self, account, token_from, token_to, amount, slippage):
        token_from_address = self.token_list[token_from]
        token_to_address = self.token_list[token_to]

        if token_from == 'eth':
            value = self.rpc.to_wei(amount, 'ether')
        else:
            value = int(Decimal(amount * 10 ** 6))

        swap_pair_address = self.get_pair_address(
            token_from, token_to)
        amount_out = self.get_amount_out(swap_pair_address, token_from, amount)
        amount_out_min = int(Decimal(amount_out * (1 - slippage)))

        path = [self.rpc.to_checksum_address(token_from_address),
                self.rpc.to_checksum_address(token_to_address)]

        to = self.rpc.to_checksum_address(account.address)
        deadline = int(time.time()) + 60 * 60

        if token_from == 'eth':
            swap_function = self.router_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min, path, to, deadline, [False, False])
        else:
            self.approve_token(account, token_to, amount)
            swap_function = self.router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                value, amount_out_min, path, to, deadline, [False, False])

        # Build the transaction object without the gas and gasPrice
        transaction_object = {
            'from': account.address,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
            'value': 0 if token_from != 'eth' else value,
            'chainId': self.chain_id,
        }

        balance = self.rpc.eth.get_balance(account.address)
        print("ETH balance: ", balance)
        # Estimate gas for the transaction
        estimated_gas = swap_function.estimate_gas(transaction_object)

        # Add a buffer to the estimated gas (e.g., 10%)
        gas_limit = int(estimated_gas * 1.2)

        # Update the transaction object with the gas limit and gas price
        transaction_object.update({
            'gas': gas_limit,
            'gasPrice': self.rpc.eth.gas_price,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
        })

        # Build the transaction
        tx = swap_function.build_transaction(transaction_object)

        success = execute_tx(tx, account, self.rpc)

    def add_liquidity(self, account, token_1, token_2, amount_1, amount_2):

        if token_1 == 'usdc':
            token_address = self.token_list[token_1]
            amount = int(Decimal(amount_1 * 10**6))
            value = amount_1
            token_to = token_1
        elif token_2 == 'usdc':
            token_address = self.token_list[token_2]
            amount = int(Decimal(amount_2 * 10**6))
            value = amount_2
            token_to = token_2

        slippage = 0.001
        amountTokenMin = int(amount*(1-slippage))
        token_rate = self.get_token_rate(
            self.get_pair_address(token_1, token_2))
        amountETHMin = int((token_rate*amountTokenMin)/10**12)
        feeType = int(50)
        to = self.rpc.to_checksum_address(account.address)
        deadline = int(time.time()) + 60 * 60  # Deadline: 1 hour from now

        # Approve router contract to spend the tokens on behalf of the user
        self.approve_token(account, token_to, value)

        add_liquidity_function = self.router_contract.functions.addLiquidityETH(
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
            'from': account.address,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
            'chainId': self.chain_id,
            'value': amountETHMin,
        }

        estimated_gas = add_liquidity_function.estimate_gas(transcation_object)
        gas_limit = int(estimated_gas * 1.2)

        # Update the transaction object with the gas limit and gas price
        transcation_object.update({
            'gas': gas_limit,
            'gasPrice': self.rpc.eth.gas_price,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
        })

        # Build the transaction
        tx = add_liquidity_function.build_transaction(transcation_object)
        success = execute_tx(tx, account, self.rpc)

    def remove_liquidity(self, account, token_1, token_2, liquidity_rate):

        if token_1 == 'usdc':
            token_address = self.token_list[token_1]
            token_to = token_1
        elif token_2 == 'usdc':
            token_address = self.token_list[token_2]
            token_to = token_2

        # Get the user's liquidity balance in the pool
        liquidity_balance = self.get_liquidity_balance(
            account, self.get_pair_address(token_1, token_2))
        liquidity = int(liquidity_balance * liquidity_rate)

        # Get reserves
        reserve_usdc, reserve_eth = self.get_reserves(
            self.get_pair_address(token_1, token_2))
        # get total lp supply
        total_lp_supply = self.get_total_lp(
            self.get_pair_address(token_1, token_2), self.pool_abi)

        Slippage = 0.001
        amount_token_min = int(
            ((reserve_usdc/total_lp_supply) * liquidity_balance)*(1-Slippage))
        amount_eth_min = int(
            ((reserve_eth/total_lp_supply) * liquidity_balance)*(1-Slippage))
        to = self.rpc.to_checksum_address(account.address)
        deadline = int(time.time()) + 60 * 60  # Deadline: 1 hour from now
        stable = False

        # Approve router contract to spend the liquidity tokens on behalf of the user
        self.approve_token(account, token_to, amount_token_min)

        remove_liquidity_function = self.router_contract.functions.removeLiquidityETHSupportingFeeOnTransferTokens(
            token_address,
            liquidity,
            amount_token_min,
            amount_eth_min,
            to,
            deadline,
            stable
        )

        transaction_object = {
            'from': account.address,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
            'chainId': self.chain_id,
        }
        estimated_gas = remove_liquidity_function.estimate_gas(
            transaction_object)
        gas_limit = int(estimated_gas * 1.2)

        # Update the transaction object with the gas limit and gas price
        transaction_object.update({
            'gas': gas_limit,
            'gasPrice': self.rpc.eth.gas_price,
            'nonce': self.rpc.eth.get_transaction_count(account.address),
        })

        remove_tx = remove_liquidity_function.build_transaction(
            transaction_object)
        success = execute_tx(remove_tx, account, self.rpc)

    def get_reserves(self, pair_address):
        pair_contract = self.rpc.eth.contract(
            address=pair_address, abi=self.pool_abi)
        reserves = pair_contract.functions.getReserves().call()
        token0_address = pair_contract.functions.token0().call()

        if token0_address.lower() == self.token_list['eth'].lower():
            reserve_eth = reserves[0]
            reserve_usdc = reserves[1]
        else:
            reserve_eth = reserves[1]
            reserve_usdc = reserves[0]

        return reserve_usdc, reserve_eth

    def get_total_lp(self, pair_address, pair_abi):
        pair_contract = self.rpc.eth.contract(
            address=pair_address, abi=pair_abi)
        total_supply = pair_contract.functions.totalSupply().call()
        return total_supply
