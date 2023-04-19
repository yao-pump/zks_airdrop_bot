from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.core.types import Token
from zksync2.provider.eth_provider import EthereumProvider

from utils import get_accounts, get_providers

sdk = ZkSyncBuilder.build("https://zksync2-testnet.zksync.dev")
CHAIN_IDS = {
    'mainnet': 1,
    'testnet': 5,
}
network = 'testnet'
acc = get_accounts()[-1]
# account = Account.from_key(acc["private_key"])
provider_url = get_providers()['eth_{}'.format(network)]
web3 = Web3(HTTPProvider(endpoint_uri=provider_url))
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)
account = Account.from_key(bytes.fromhex(acc['private_key'][2:]))
# gas_provider = StaticGasProvider(Web3.toWei(1, "gwei"), 555000)
eth_provider = EthereumProvider(sdk, web3, account)


def get_balance():

def deposit(amount=0.01):
    gas_price = web3.eth.gas_price
    tx_receipt = eth_provider.deposit(Token.create_eth(),
                                      web3.to_wei(str(amount), "ether"),
                                      gas_price=gas_price)
    print(f"tx status: {tx_receipt['status']}")


if __name__ == "__main__":
    deposit()

