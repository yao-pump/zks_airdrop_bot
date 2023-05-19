from cfg import rpcs, chains
from utils import get_gas_price
import random



marker_address_main = [
    "0x80C67432656d59144cEFf962E8fAF8926599bCF8",
    "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
    "0xee73323912a4e3772B74eD0ca1595a152b0ef282",
    "0x0a88BC5c32b684D467b43C06D9e0899EfEAF59Df",
]

marker_address_test = [
    "0x0043d60e87c5dd08C86C3123340705a1556C4719",
    "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
    "0x3Fbd1E8CFc71b5B8814525E7129a3f41870A238B",
]

marker_address = {
    'main': marker_address_main,
    'test': marker_address_test
}

identify_code_main = {
    "zks_era": 9014,
    "arb": 9002
}

identify_code_test = {
    "zks_era": 9514,
    "arb": 9022
}

identify_code = {
    'main': identify_code_main,
    'test': identify_code_test
}

def bridge(account, amount, source_network="arb", destination_network="zks_era", network_type='test'):
    source_network = source_network+'_'+network_type
    bridge_address = random.choice(marker_address[network_type])
    if account.get_eth_balance(source_network) <= amount:
        print('insufficient balance')
        return

    nonce = rpcs[source_network].eth.get_transaction_count(account.address)

    gas_price = get_gas_price(source_network)

    amount = rpcs[source_network].to_wei(amount, 'ether')
    amount += identify_code[network_type][destination_network]

    transaction = {
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': 21000,
        'to': rpcs[source_network].to_checksum_address(bridge_address),
        'value': amount,
        'chainId': chains[source_network],
    }
    signed_txn = rpcs[source_network].eth.account.sign_transaction(transaction, account.private_key)
    transaction_hash = rpcs[source_network].eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f'Transaction sent! TX hash: {transaction_hash.hex()}')


