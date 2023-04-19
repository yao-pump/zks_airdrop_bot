import os
import json
from getpass import getpass
from web3 import Web3, HTTPProvider
from utils import get_providers, get_accounts
from eth_account import Account
import secrets


def create_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    print("SAVE BUT DO NOT SHARE THIS:", private_key)
    acct = Account.from_key(private_key)
    print("Address:", acct.address)
    account = {acct.address: private_key}
    # password = getpass('Enter a password to protect your wallet: ')
    # encrypted_key = w3.eth.account.encrypt(private_key, password)
    with open('config/wallet.json', 'r+') as f:
        accounts_json = json.load(f)
        # with open('config/wallet.json', 'w') as f:
        accounts_json[acct.address] = private_key
        f.seek(0)
        json.dump(accounts_json, f)
    print('Wallet created and saved to wallet.json')


def load_wallet(w3):
    password = getpass('Enter your wallet password: ')
    with open('config/wallet.json', 'r') as f:
        encrypted_key = json.load(f)
    private_key = w3.eth.account.decrypt(encrypted_key, password)
    return w3.eth.account.privateKeyToAccount(private_key)


def check_balance(w3, address):
    if not w3.isChecksumAddress(address):
        print("Invalid Ethereum address")
        return

    balance = w3.eth.get_balance(address)
    eth_balance = w3.fromWei(balance, "ether")
    print(f'Balance for {address}: {eth_balance} ETH')


def transfer_eth(w3, account, to, amount, nonce=None):
    if nonce is None:
        nonce = w3.eth.get_transaction_count(w3.to_checksum_address(account['address']))
    gas_price = w3.eth.gas_price
    transaction = {
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': 21000,
        'to': w3.to_checksum_address(to['address']),
        'value': w3.to_wei(amount, 'ether'),
        'chainId': 1,
    }
    signed_txn = w3.eth.account.sign_transaction(transaction, account['private_key'])
    transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f'Transaction sent! TX hash: {transaction_hash.hex()}')


if __name__ == "__main__":
    # Connect to a local Ethereum node or an external provider like Infura
    providers = get_providers()
    # provider_url = providers['eth_goerli']
    provider_url = providers['zks_era']
    w3 = Web3(HTTPProvider(provider_url))

    accounts = get_accounts()
    acc = accounts[0]
    # transfer_eth(w3, acc, acc, 0, nonce=0)
    check_balance(w3, acc['address'])
    # create_wallet()
    # for address in accounts.keys():
    #     print(check_balance(address))
