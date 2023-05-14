from web3 import Web3, HTTPProvider
from cfg import providers, chains


class NFTMarketplace:
    def __init__(self, name, network='testnet'):
        self.name = name
        self.rpc = Web3(HTTPProvider(providers['zks_era_{}'.format(network)]))
        self.chain_id = chains['zks_era_{}'.format(network)]

    def mint_nft(self, nft_info, account):
        pass

    def buy_nft(self, image_link, account):
        pass