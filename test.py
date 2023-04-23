from database import connect_mongodb, get_random_account, get_account
from account import Account
from dex.syncswap import SyncSwap
from decimal import Decimal

neworks = ['eth_mainnet', 'eth_testnet', 'zks_era_mainnet', 'zks_era_testnet']
def test_account():
    db = connect_mongodb()
    acc_info = get_account(db, 2)
    acc = Account(acc_info)
    print(acc.address)


    # acc.transfer_eth(acc, amount=0, network='zks_era_testnet')

def test_pool():
    db = connect_mongodb()
    acc_info = get_account(db, 2)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
    pool_address = syncswap.get_pool_address('usdt', 'eth')
    print(pool_address)
    pool_contract = syncswap.rpc.eth.contract(address=pool_address, abi=syncswap.pool_abi)
    lp_balance = acc.get_lp_balance(pool_address, 'zks_era_' + syncswap.network)
    print(lp_balance)
    print(syncswap.calculate_receive_eth(pool_contract, lp_balance))

def test_swap():
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
    syncswap.swap(acc, 'eth', 'usdt', 0.001, slippage=0.05)


def test_add_liquidity():
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
    usdt_amount = (acc.get_balance('usdc', 'zks_era', 'testnet'))
    syncswap.add_liquidity(acc, 'eth', 'usdc', 0.001, usdt_amount)

def test_remove_liquidity():
    db = connect_mongodb()
    acc_info = get_account(db, 3)
    acc = Account(acc_info)
    syncswap = SyncSwap(network='testnet')
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

if __name__ == '__main__':
    # test_account()
    # test_approve()
    # test_swap()
    # test_add_liquidity()
    test_remove_liquidity()
    # test_pool()