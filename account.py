from cfg import rpcs, chains
from utils import get_gas_price, get_contract_address

class Account:
    def __init__(self, account_info) -> None:
        self.address = account_info['address']
        self.private_key = account_info['private_key']
        self.transactions = account_info['transactions']

    def get_eth_balance(self, network='eth_mainnet'):
        balance = rpcs[network].eth.get_balance(self.address)
        eth_balance = rpcs[network].fromWei(balance, "ether")
        print('Balance for {} on {}: {} ETH'.format(self.address, network, eth_balance))
        return eth_balance

    def get_balance(self, token, network):
        # Connect to the Ethereum provider

        contract_address = get_contract_address(token, network)
        contract_address = rpcs[network].toChecksumAddress(contract_address)

        # Create a contract object
        contract = rpcs[network].eth.contract(address=contract_address, abi=abi)

        # Get the token balance
        balance = contract.functions.balanceOf(self.address).call()

        return balance



    def transfer_eth(self, to, amount, network='eth_mainnet', nonce=None):
        if self.get_eth_balance(network) <= amount:
            print('insufficient balance')
            return
        if nonce is None:
            nonce = rpcs[network].eth.get_transaction_count(self.address)

        gas_price = get_gas_price(network)

        transaction = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 21000,
            'to': rpcs[network].to_checksum_address(to['address']),
            'value': rpcs[network].to_wei(amount, 'ether'),
            'chainId': chains[network],
        }
        signed_txn = rpcs[network].eth.account.sign_transaction(transaction, self.private_key)
        transaction_hash = rpcs[network].eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f'Transaction sent! TX hash: {transaction_hash.hex()}')