import json
import web3
import time

from cfg import rpcs


def get_contract_address(token, network):
    pass


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



    data3 = '0x0000000008021f9a432199be41105aea5775959fbc2557cc8789bc1bf90a239d9a9180115c708e12edd42e504c1cd52aea96c547c05c21651f0e067f06ec247679efb0bdd77605019c7c1e040204'
    analyze_tx_data(data3)

    data4 = '0x00000000080205631ac9f9df52d05aea5775959fbc2557cc8789bc1bf90a239d9a9108f328c72a9b420b7568415ed331a1c236e6f6207aa33c576954e86460a94a2fa1ff7f7d3403e7e314140204'
    analyze_tx_data(data4)

    data5 = '0x000000000702430232db3fc3575aea5775959fbc2557cc8789bc1bf90a239d9a91952d4039615f85d1abd85b244eb7840deb9cf9239532cd4e84c7b5c57923ebd95ee7f97b10f0208f141e0200'
    analyze_tx_data(data5)

    data6 = '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000012475ceafe6000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000cea3fd38d59ea7c736737848e40555b13a705125000000000000000000000000000000000000000000000000002386f26fc1000000000000000000000000000000000000000000000000041317469d38e2cee7fa00000000000000000000000000000000000000000000000000000000645c1cda000000000000000000000000000000000000000000000000000000000000002b8c3e3f2983db650727f3e05b7a7773e4d641537b0007d0a5900cce51c45ab9730039943b3863c82234203400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000412210e8a00000000000000000000000000000000000000000000000000000000'

    # get_ABI_functions('config/syncswap_pool_abi.json')