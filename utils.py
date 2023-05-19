import json
import web3
import time

from cfg import rpcs, token_abi


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

    print(get_gas_price())

    # data3 = '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000012475ceafe6000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000003040ee148d09e5b92956a64cdc78b49f48c0cddc00000000000000000000000000000000000000000000083054643f6502e4df8000000000000000000000000000000000000000000000000000466aa184debbdf000000000000000000000000000000000000000000000000000000006460dce9000000000000000000000000000000000000000000000000000000000000002ba5900cce51c45ab9730039943b3863c8223420340007d08c3e3f2983db650727f3e05b7a7773e4d641537b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000cea3fd38d59ea7c736737848e40555b13a70512500000000000000000000000000000000000000000000000000000000'
    # analyze_tx_data(data3)
    #
    # data4 = '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001e00000000000000000000000000000000000000000000000000000000000000164375d2b18000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000cea3fd38d59ea7c736737848e40555b13a7051250000000000000000000000000000000000077299d4e4a0c7927ae2a9671410000000000000000000000000000000000000000000000000000f3561caef6932800000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000002ba5900cce51c45ab9730039943b3863c8223420340007d08c3e3f2983db650727f3e05b7a7773e4d641537b000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a307866666666666666660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000cea3fd38d59ea7c736737848e40555b13a70512500000000000000000000000000000000000000000000000000000000'
    # analyze_tx_data(data4)

    # get_ABI_functions('config/syncswap_pool_abi.json')