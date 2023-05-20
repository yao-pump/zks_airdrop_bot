import json
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
    print(f"Transaction hash: {transaction_hash.hex()}")

    success = None
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

    return success



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


if __name__ == '__main__':

    # print(get_gas_price())

    data3 = '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000012475ceafe6000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000470de4df82000000000000000000000000000000000000000000000000000000000000021fb9ba00000000000000000000000000000000000000000000000000000000ffffffff000000000000000000000000000000000000000000000000000000000000002b5aea5775959fbc2557cc8789bc1bf90a239d9a910007d03355df6d4c9c3035724fd0e3914de96a5a83aaf400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000412210e8a00000000000000000000000000000000000000000000000000000000'
    analyze_tx_data(data3)

    data4 = '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000012475ceafe6000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f06288b3da8b0e55ed0fdc398fcd3929f5a8577b00000000000000000000000000000000000000000000000000470de4df82000000000000000000000000000000000000000000000000000000000000022522bf000000000000000000000000000000000000000000000000000000006468a155000000000000000000000000000000000000000000000000000000000000002b5aea5775959fbc2557cc8789bc1bf90a239d9a910007d03355df6d4c9c3035724fd0e3914de96a5a83aaf400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000412210e8a00000000000000000000000000000000000000000000000000000000'
    analyze_tx_data(data4)

    # get_ABI_functions('config/syncswap_pool_abi.json')