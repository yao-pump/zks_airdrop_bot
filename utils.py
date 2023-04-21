import json
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


if __name__ == '__main__':

    data3 = ''
    # data3 = '0x2cc4081e000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000010f016400000000000000000000000000000000000000000000000000000000642af5f50000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000080115c708e12edd42e504c1cd52aea96c547c05c00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000600000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000dc8d45d062e2fa5cd76b17d24f8691c950d0de5800000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'
    a = analyze_tx_data(data3)
    print()
    data = '0x2cc4081e0000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000642b65600000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000080115c708e12edd42e504c1cd52aea96c547c05c00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000600000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000dc8d45d062e2fa5cd76b17d24f8691c950d0de58000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000023078000000000000000000000000000000000000000000000000000000000000'
    # data = '0x2cc4081e000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000010f691e00000000000000000000000000000000000000000000000000000000642aff410000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000080115c708e12edd42e504c1cd52aea96c547c05c00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000600000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000dc8d45d062e2fa5cd76b17d24f8691c950d0de5800000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'
    b = analyze_tx_data(data)

    # for i in range(len(a)):
    #     if a[i] != b[i]:
    #         print(i, a[i], b[i])
    # print(get_accounts())
    get_ABI_functions("config/syncswap_pool_factory_abi.json")
    # get_ABI_functions("config/zks_abi.json")
