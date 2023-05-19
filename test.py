import time

from web3 import Web3, HTTPProvider

from cfg import providers
from database import connect_mongodb, get_random_account, get_account
from account import Account
from dex.izumiswap import IzumiSwap
from dex.syncswap import SyncSwap
from decimal import Decimal

from nft.mint_square import MintSquare
from nft.utils import get_random_image
from bridge.orbiter import bridge as orbiter_bridge

neworks = ['eth_mainnet', 'eth_testnet', 'zks_era_mainnet', 'zks_era_testnet']
def test_account():
    db = connect_mongodb()
    acc_info = get_account(db, 2)
    acc = Account(acc_info)
    print(acc.address)


    # acc.transfer_eth(acc, amount=0, network='zks_era_testnet')

def test_pool():
    db = connect_mongodb()
    acc_info = get_account(db, 4)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='mainnet')
    pool_address = syncswap.get_pool_address('usdc', 'eth')
    print(pool_address)
    pool_contract = syncswap.rpc.eth.contract(address=pool_address, abi=syncswap.pool_abi)
    print(pool_contract.functions.balanceOf(acc.address).call())
    print(pool_contract.functions.totalSupply().call())
    # lp_balance = acc.get_lp_balance(pool_address, 'zks_era_' + syncswap.network)
    # print(lp_balance)
    # print(syncswap.calculate_receive_eth(pool_contract, lp_balance))

def test_swap():
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
    syncswap.swap(acc, 'usdc', 'eth', 665763371979268731311347415, slippage=0.05)


def test_add_liquidity():
    db = connect_mongodb()
    acc_info = get_account(db, 4)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='mainnet')
    usdt_amount = (acc.get_balance('usdc', 'zks_era', 'mainnet'))
    syncswap.add_liquidity(acc, 'eth', 'usdc', 0.1, usdt_amount)

def test_remove_liquidity():
    db = connect_mongodb()
    acc_info = get_account(db, 4)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='mainnet')
    syncswap.remove_liquidity(acc, 'eth', 'usdc')

def test_approve():
    db = connect_mongodb()
    acc_info = get_account(db, 2)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
    usdt_amount = (acc.get_balance('usdt', 'zks_era', 'testnet'))
    print(usdt_amount)
    # pool_address = syncswap.get_pool_address('usdt', 'eth')
    syncswap.approve_token(acc, 'usdt', usdt_amount)


def test_mint_square():
    db = connect_mongodb()
    acc_info = get_account(db, 0)
    acc = Account(acc_info)
    print(acc.address)

    market = MintSquare(network='mainnet')

    image_url, image_name = get_random_image()
    print('Mint NFT for image: ', image_name)
    upload_info = market.upload_image(image_url)

    if upload_info:
        time.sleep(1)
        image_info = {"name": image_name, "attributes": [],
                      "link": upload_info}
        nft_info = market.get_nft_hash(image_info)
        if nft_info:
            market.mint_nft(nft_info, acc)


def test_izumi():
    izumi_swap = IzumiSwap(network='testnet')
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    izi_amount = (acc.get_balance('izi', 'zks_era', 'testnet'))
    print(izi_amount)
    izumi_swap.swap_token(acc, 'eth', 'izi', 0.01)


def test_orbiter():
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    orbiter_bridge(acc, 0.005)

if __name__ == '__main__':
    # test_account()
    # test_approve()
    test_swap()
    # test_add_liquidity()
    # test_remove_liquidity()
    # test_pool()
    # db = connect_mongodb()
    # acc_info = get_account(db, 4)
    # acc = Account(acc_info)
    # test_mint_square()
    # test_izumi()
    # test_orbiter()

