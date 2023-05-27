import base64
import json

import requests
import web3
import time

from cfg import rpcs, token_abi


def estimate_gas(data, rpc, contract_address, self_address):

    # transaction parameters
    transaction = {
        'from': self_address,
        'to': contract_address,
        'data': data,
    }
    gas_estimate = rpc.eth.estimate_gas(transaction, block_identifier=None)
    print("Gas estimate: ", gas_estimate)
    return gas_estimate
def append_hex(hex_string, new_hex_string):
    return hex_string + new_hex_string[2:]

def num2Hex(n):
    if n < 10:
        return str(n)
    str_hex = 'ABCDEF'
    return str_hex[n - 10]

def fee2Hex(fee):
    n0 = fee % 16
    n1 = (fee // 16) % 16
    n2 = (fee // 256) % 16
    n3 = (fee // 4096) % 16
    n4 = 0
    n5 = 0
    return '0x' + num2Hex(n5) + num2Hex(n4) + num2Hex(n3) + num2Hex(n2) + num2Hex(n1) + num2Hex(n0)

def get_token_info(token_address, rpc):
    if token_address != '0x0000000000000000000000000000000000000000':
        contract = rpc.eth.contract(address=rpc.to_checksum_address(token_address),
                                    abi=token_abi)
        decimal = contract.functions.decimals().call()
        symbol = contract.functions.symbol().call()
        name = contract.functions.name().call()
        token_info = {'name': name, 'symbol': symbol, 'decimal': decimal,
                      'address': rpc.to_checksum_address(token_address)}
    else:
        token_info ={'name': 'eth', 'symbol': 'eth', 'decimal': 18,
                     'address': rpc.to_checksum_address('0x0000000000000000000000000000000000000000')}
    return token_info


def get_gas_price(network='eth_mainnet'):
    gas_price = rpcs[network].eth.gas_price
    return gas_price


def analyze_tx_data(tx_data):
    function = tx_data[:10]
    parameters = tx_data[10:]
    print(function)
    print(len(parameters))
    data = []
    num_params = len(parameters) // 64
    for i in range(num_params):
        print(parameters[i*64:(i+1)*64])
        data.append(parameters[i*64:(i+1)*64])
    return data


def load_json(filename):
    with open(filename, 'r') as f:
        json_file = json.load(f)
    return json_file


def get_accounts():
    accounts_dict = load_json('config/wallet.json')
    accounts = []
    for key, value in accounts_dict.items():
        accounts.append({"address": key, "private_key": value})
    return accounts


def get_ABI_functions(path):
    with open(path, encoding='utf-8', errors='ignore') as json_data:
        contract_abi = json.load(json_data, strict=False)

    function_parameters = {}

    for item in contract_abi:
        if item['type'] == 'function':
            function_name = item['name']
            parameters = []

            for param in item['inputs']:
                param_info = {
                    'name': param['name'],
                    'type': param['type']
                }
                parameters.append(param_info)

            function_parameters[function_name] = parameters

    print("Functions:")
    for function_name, parameters in function_parameters.items():
        print(f"{function_name}:")
        for param in parameters:
            print(f"  {param['name']} ({param['type']})")
def execute_tx(tx, account, rpc):
    signed_txn = rpc.eth.account.sign_transaction(tx, account.private_key)
    # print(signed_txn.rawTransaction)
    transaction_hash = rpc.eth.send_raw_transaction(signed_txn.rawTransaction)
    # print(f"Transaction hash: {transaction_hash.hex()}")

    while True:
        transaction_receipt = rpc.eth.wait_for_transaction_receipt(transaction_hash)
        if transaction_receipt['status'] == 1:
            success = True
            break
        elif transaction_receipt['status'] == 0:
            success = False
            break
        time.sleep(2)

    # Check if the transaction was successful
    if not success:
        print('Transaction failed.')
    else:
        print('Transaction succeeded.')

    return [success, transaction_hash.hex()]



def get_function_by_data(input_data, abi_path):

    with open(abi_path, encoding='utf-8', errors='ignore') as json_data:
        contract_abi = json.load(json_data, strict=False)

    for function in contract_abi:
        if function['type'] == 'function':
            # Get the function signature
            function_signature = f"{function['name']}({','.join([input['type'] for input in function['inputs']])})"

            # Calculate the Keccak-256 hash of the function signature
            function_hash = web3.Web3.keccak(text=function_signature).hex()

            # Compare the first 4 bytes of the function hash with the input data
            if function_hash[:10] == input_data:
                print(f"Function found: {function_signature}")
                break


price_feed_ids = {
    'eth': '0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace',
    'btc': '0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43',
    'ltc': '0x6e3f3fa8253588df9326580180233eb791e03b443a3ba7a1d892e73874e19a54',
    'doge': '0xdcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c',
    'tusdc': '0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a'

}

def get_coin_price(symbol):
    url = "https://xc-mainnet.pyth.network/api/latest_price_feeds?ids[]={}".format(price_feed_ids[symbol])
    response = requests.get(url).json()[0]

    # print(response.json()['price'])
    # return int(response['price']['price']) * 10 ** response['price']['expo']
    return int(response['price']['price']), int(response['price']['conf']), response['price']['expo']


def get_update_data(symbol):
    url = 'https://xc-mainnet.pyth.network/api/latest_vaas?&ids[]=0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a&ids[]=0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace'
    # url = "https://xc-mainnet.pyth.network/api/latest_vaas?ids[]={}".format(price_feed_ids[symbol])
    data = requests.get(url).json()

    update_data = ["0x" + base64.b64decode(item).hex() for item in data]
    # print(response.json()['price'])
    # return int(response['price']['price']) * 10 ** response['price']['expo']
    return update_data


if __name__ == '__main__':

    # print(get_gas_price())

    data3 = '0x0d537e8d5905d1ad2714cd1be40275a36b411888fca46c5cbaa10fb30cec48572d84bf74'
    success = analyze_tx_data(data3)
    #
    data4 = '0x0d537e8d5905d1ad2714cd1be40275a36b411888fca46c5cbaa10fb30cec48572d84bf74'
    fail = analyze_tx_data(data4)


    # print(get_update_data('eth'))
    # get_ABI_functions('config/syncswap_pool_abi.json')