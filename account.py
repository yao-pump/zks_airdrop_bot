from cfg import rpcs, chains, zks_token_addresses, token_abi
from utils import get_gas_price, execute_tx, get_token_info
from decimal import Decimal


class Account:
    def __init__(self, account_info) -> None:
        self.address = account_info['address']
        self.private_key = account_info['private_key']
        # self.transactions = account_info['transactions']
        try:
            self.zkdx_info = account_info['zkdx']
        except:
            self.zkdx_info = None
        try:
            self.coin_balance = account_info['other_balance']
        except:
            self.coin_balance = {}

    def get_eth_balance(self, network='eth_mainnet'):
        balance = rpcs[network].eth.get_balance(self.address)
        eth_balance = rpcs[network].from_wei(balance, "ether")
        print('Balance for {} on {}: {} ETH'.format(self.address, network, eth_balance))
        return eth_balance


    def get_lp_balance(self, pool_address, network):
        contract = rpcs[network].eth.contract(address=pool_address, abi=token_abi)
        balance = contract.functions.balanceOf(self.address).call()
        # balance = Decimal(balance) / Decimal(10 ** 6)
        return balance

    def get_balance(self, token, network_symbol='eth', network_type='testnet'):
        # Connect to the Ethereum provider
        if network_type != '':
            network = network_symbol + '_' + network_type
        else:
            network = network_symbol
        if network_symbol == 'zks_era':
            contract_address = zks_token_addresses[network_type][token]
        else:
            contract_address = token

        contract_address = rpcs[network].to_checksum_address(contract_address)

        # Create a contract object
        contract = rpcs[network].eth.contract(address=contract_address, abi=token_abi)

        # Get the token balance
        balance = contract.functions.balanceOf(self.address).call()

        token_info = get_token_info(contract_address, rpcs[network])
        balance = Decimal(balance) / Decimal(10 ** token_info['decimal'])
        return balance



    def transfer_eth(self, to, amount, network='eth_mainnet', nonce=None):
        if type(to) == str:
            to_address = to
        else:
            to_address = to.address
        if self.get_eth_balance(network) <= amount:
            print('insufficient balance')
            return
        if nonce is None:
            nonce = rpcs[network].eth.get_transaction_count(self.address)

        gas_price = get_gas_price(network)

        if 'eth' in network:
            gas = 21000
        else:
            gas = 800000

        transaction = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas,
            'to': rpcs[network].to_checksum_address(to_address),
            'value': rpcs[network].to_wei(amount, 'ether'),
            'chainId': chains[network],
        }
        # signed_txn = rpcs[network].eth.account.sign_transaction(transaction, self.private_key)
        # transaction_hash = rpcs[network].eth.send_raw_transaction(signed_txn.rawTransaction)
        # print(f'Transaction sent! TX hash: {transaction_hash.hex()}')
        success = execute_tx(transaction, self, rpcs[network])
        return success
