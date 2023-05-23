from cfg import zks_token_addresses, chains, rpcs


class BaseAPP:
    def __init__(self, name, chain="zks_era", network='testnet'):
        self.name = name
        self.chain = chain
        self.chain_id = chains['zks_era_{}'.format(network)]
        self.network = network
        self.token_list = zks_token_addresses[network]
        # self.rpc = Web3(HTTPProvider(providers['zks_era_{}'.format(network)]))
        self.rpc = rpcs[chain + '_' + network]
