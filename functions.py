import time
from random import random
from cfg import create_wallet
from database import connect_mongodb, insert_new_account
from bridge.zks_era import bridge as official_bridge
from bridge.orbiter import bridge as orbiter_bridge
from bridge.layerswap import bridge as layerswap_bridge
from bridge.bungee import bridge as bungee_bridge
from dex.syncswap import SyncSwap
from dex.muteswap import MuteSwap
from dex.izumiswap import IzumiSwap
from nft.mint_square import MintSquare
from nft.utils import get_random_image
from others.zkdx import ZkDX

def create_new_account():
    db = connect_mongodb()
    wallet = create_wallet()
    print('New account created: ', wallet['address'])
    insert_new_account(db, wallet)


def bridge(account, network_type='mainnet'):
    balance_main = account.get_eth_balance('eth_{}'.format(network_type))
    if balance_main > 0.11:
        success = official_bridge(account, balance_main, network_type=network_type)
        return success

    balance_arb = account.get_eth_balance('arb_{}'.format(network_type))
    if balance_arb > 0:
        use_bridge = random.choice(['orbiter', 'layerswap', 'bungee'])
        if use_bridge == 'orbiter':
            success = orbiter_bridge(account, balance_arb, network_type=network_type)
        elif use_bridge == 'layerswap':
            success = layerswap_bridge(account, balance_arb, network_type=network_type)
        elif use_bridge == 'bungee':
            success = bungee_bridge(account, balance_arb, network_type=network_type)
        return success
    else:
        return False

def swap(use_swap, account, token_from, token_to, amount, network_type='mainnet'):
    if use_swap == 'syncswap':
        current_swap = SyncSwap(network=network_type)
    elif use_swap == 'muteswap':
        current_swap = MuteSwap(network=network_type)
    elif use_swap == 'izumiswap':
        current_swap = IzumiSwap(network=network_type)

    success = current_swap.swap(account, token_from, token_to, amount)
    return success

def mint_nft(account, network_type='mainnet'):
    market = MintSquare(network=network_type)
    image_url, image_name = get_random_image()
    print('Mint NFT for image: ', image_name)
    upload_info = market.upload_image(image_url)

    if upload_info:
        time.sleep(1)
        image_info = {"name": image_name, "attributes": [],
                      "link": upload_info}
        nft_info = market.get_nft_hash(image_info)
        if nft_info:
            market.mint_nft(nft_info, account)


def open_position_zkdx(account, symbol='eth', amount=10000, leverage=2, is_long=True):
    zkdx = ZkDX()
    success = zkdx.increase_position(account, amount, symbol, leverage, is_long)
    return success

def claim_zkdx_usdc(account):
    zkdx = ZkDX()
    success = zkdx.claim_tudsc(account)
    return success


def close_position_zkdx(account, symbol, size_delta, is_long):
    zkdx = ZkDX()
    success = zkdx.decrease_position(account, size_delta, symbol, is_long)
    return success


def add_liquidity(account, token_1, token_2, amount_1, amount_2):
    pass


def remove_liquidity(account, token_1, token_2):
    pass

if __name__ == '__main__':
    create_new_account()