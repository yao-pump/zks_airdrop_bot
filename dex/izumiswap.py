from dex.dex import DEX

class SyncSwap(DEX):
    def __init__(self, network='testnet', name='izumiswap'):
        DEX.__init__(self, name=name, network=network)
        # if network == 'testnet':
        #     self.token_list['eth'] = '0x20b28b1e4665fff290650586ad76e977eab90c5d'