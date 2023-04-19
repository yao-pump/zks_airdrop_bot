from decimal import Decimal

from zksync_sdk import HttpJsonRPCTransport, ZkSyncProviderV01, network, ZkSyncLibrary, EthereumSignerWeb3, ZkSync, \
    EthereumProvider, ZkSyncSigner, Wallet
import asyncio
from web3 import Account, Web3, HTTPProvider
from zksync_sdk.types import ChangePubKeyEcdsa

from utils import get_accounts, get_providers
import os

os.environ['ZK_SYNC_LIBRARY_PATH'] = '/Users/yao/Downloads/zks-crypto-aarch64-apple-darwin.dylib'

library = ZkSyncLibrary()
provider = ZkSyncProviderV01(provider=HttpJsonRPCTransport(network=network.goerli))
# Setup web3 account
acc = get_accounts()[-1]
account = Account.from_key(acc["private_key"])
provider_url = get_providers()['eth_testnet']
w3 = Web3(HTTPProvider(endpoint_uri=provider_url))
# Create EthereumSigner
ethereum_signer = EthereumSignerWeb3(account=account)
# Load contract addresses from server


async def check_balance(wallet):
    committedETHBalance = await wallet.get_balance("ETH", "committed")
    print(committedETHBalance)

    # Verified state is final
    verifiedETHBalance = await wallet.get_balance("ETH", "verified")
    print(verifiedETHBalance)


async def unlock_account(wallet):
    if not await wallet.is_signing_key_set():
        tx = await wallet.set_signing_key("ETH", eth_auth_data=ChangePubKeyEcdsa())
        status = await tx.await_committed()
        print(status)
        # Committed state is not final yet


async def transfer(wallet, token, amount):
    tx = await wallet.transfer("0x21dDF51966f2A66D03998B0956fe59da1b3a179F",
                               amount=Decimal(str(amount)), token=token)
    status = await tx.await_committed()
    print(status)


async def withdraw(wallet, address, token, amount):
    tx = await wallet.withdraw(address,
                               Decimal(amount), token)
    status = await tx.await_committed()
    print(status)


async def mintNFT(wallet, recipient_address, token):
    tx = await wallet.mint_nft("0x0000000000000000000000000000000000000000000000000000000000000123",
                               recipient_address, token)
    status = await tx.await_committed()
    print(status)

async def deposit(wallet, symbol='ETH', amount=0.01):
    # Find token for depositing
    token = await wallet.resolve_token(symbol)
    # Approve Enough deposit using token contract
    if symbol != 'ETH':
        await wallet.ethereum_provider.approve_deposit(token, Decimal(amount))

    # Deposit money from contract to our address
    deposit = await wallet.ethereum_provider.deposit(token, Decimal(amount),
                                                     account.address)
    print(deposit)

async def get_wallet():
    contracts = await provider.get_contract_address()
    # Setup web3
    # NOTE: Please ensure that the web3 provider and zksync provider match.
    # A mainnet web3 provider paired with a testnet zksync provider will transact on mainnet!!
    # Setup zksync contract interactor
    zksync = ZkSync(account=account, web3=w3,
                    zksync_contract_address=contracts.main_contract)
    # Create ethereum provider for interacting with ethereum node
    ethereum_provider = EthereumProvider(w3, zksync)

    # Initialize zksync signer, all creating options were described earlier
    signer = ZkSyncSigner.from_account(account, library, network.goerli.chain_id)
    # Initialize Wallet
    wallet = Wallet(ethereum_provider=ethereum_provider, zk_signer=signer,
                    eth_signer=ethereum_signer, provider=provider)
    return wallet


async def main():
    wallet = await get_wallet()
    # await deposit(wallet)
    await check_balance(wallet)

    await mintNFT(wallet, account.address, 'ETH')


if __name__ == '__main__':
    asyncio.run(main())
