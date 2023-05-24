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
    print(f"Transaction hash: {transaction_hash.hex()}")

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

    data3 = '0xe3b462680000000000000000000000000000000000000000000000000000000000000100000000000000000000000000e74e124f6bfed634ebbd421010ea9e8527abcab300000000000000000000000000000000000000000000065a4da25d3016c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000b84c429ffcb9b9d6eaa000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000005a2428f1e26ffeabffb956000000000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000020000000000000000000000007455eb101303877511d73c5841fbb088801f9b12000000000000000000000000e74e124f6bfed634ebbd421010ea9e8527abcab30000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000006b301000000030d003f1b062f51bae15196be5b4ed3010b6b592994fc8476733313eba9994d04609d30ce39d65d53d0517a5dfffc6e78da7cf9418fb92288e5b2939ee140540c90d4010363e31bb1724964a9640394d4edf55b255451e92b50620f850db60d55d900cec82c2efea26fc9d58e23e34cbf4a3d414dcdf2a796d8ece87d4645a8bcaaa128920004d9b0f7df57f66155e47a7880e4aa7bb5f52fd8425dbfe7316a9438df2ee8c2735e197d1afd9a91b2409bd33fe3a9ad6bec9d40613830165c891454494091dc970006fe51041c48374dd62a3389296a020738a8cb267125a2bb27b0425846a7f7c15f18bc494f1057cc307f15f8ef2220d41accb7fc94f578110e135b74002519b32b00089b6efb432ad2939c763939fdc1ba551f5f102f4e9641acbac7947f7a04edc7830e7114a6c8f339ec652f8b71f41bb71783417c181871cabda13b7427e470bca9000a8411599cd1f661d4d33bd6790622686985145ac422cbe5c46d1b15e6b83e60bd7c5d93d50242aa346c94b4af9307fd39414f5503216c32f02626d9c137e4ccb8000bfa94c1d1371d4760ce37a0f0439eca2ef57981eb6d65d27b4479a440c57b09fb335b13361d7cde1b15228bdfb7d9eea332a4d264adb1e88de1f33eab0003930e010cff3d60b20e7c504b9c7e6f5172372f707930a5f5fb45ee1cce9713f80b0505f84692cbaa6bf03d22cd8c2068756d757e55c1c0c417f83c333fdb2ae4b589a299010d4bf0de7f964169f3232fb05d99373df9216cd8e8f9bc83a1787692ba1921f3dd70284d287b5948a46f2d810abfae37328b4d0e1ffb89aefca44e25764b7bb31b010eb8c9efb70902824485fca99508c33cf66a98de8c00ec98dade416e0feb59965e711cfc9ed5e93113463aad72210247e6adee8ec9c30d7cef617d338acfc10e19010fd91f083d03a52aea4319f70974d54251a7dba89037c332926f40c782831f7cf21a1fdfd339cde00aa7abdc3d8b969ac5e548ab85719c9d06589d852ab4d32b2c01114dc2a998f6026fd1ae1116892b28cb023eb6e1399c6c82869f7830843f01816403e294a2dc3a87d1b2d271b757b60cd39709dc42d3b8df67978d9852c8d4dd720012db3fd5a746c807d695fc7119c1407153428258c18aaeb7089b8d14c83e5d95de2c2842f050fb28fddb6d1638a72e2c285024ba0d4ecd9f485f105cbcbb3dd49601646be3d300000000001af8cd23c2ab91237730770bbea08d61005cdda0984348f3f6eecb559638c0bba00000000019befd570150325748000300010001020005009d04028fba493a357ecde648d51375a445ce1cb9681da1ea11e562b53522a5d3877f981f906d7cfe93f618804f1de89e0199ead306edc022d3230b3e8305f391b00000002a6831b05a000000000abdd63afffffff80000002a5c2df47000000000087a61ec01000000060000000900000000646be3d300000000646be3d300000000646be3d20000002a6831b05a000000000abdd63a00000000646be3d2e6c020c1a15366b779a8c870e065023657c88c82b82d58a9fe856896a4034b0415ecddd26d49e1a8f1de9376ebebc03916ede873447c1255d2d5891b92ce57170000002bdc259fd80000000009079fc7fffffff80000002bcfee13800000000008e35e0a01000000050000000700000000646be3d300000000646be3d300000000646be3d20000002bdc259fd8000000000916e33300000000646be3d2c67940be40e0cc7ffaa1acb08ee3fab30955a197da1ec297ab133d4d43d86ee6ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace0000002a6dc1218000000000030f3f8dfffffff80000002a601b86380000000003beeaea01000000150000001e00000000646be3d300000000646be3d300000000646be3d20000002a6d935ac000000000033d064d00000000646be3d28d7c0971128e8a4764e757dedb32243ed799571706af3a68ab6a75479ea524ff846ae1bdb6300b817cee5fdee2a6da192775030db5615b94a465f53bd40850b50000002a66a507b7000000001493b200fffffff80000002a4dc30d580000000012fdbab201000000080000000900000000646be3d300000000646be3d300000000646be3d20000002a66a507b7000000001493b20000000000646be3d2543b71a4c292744d3fcf814a2ccda6f7c00f283d457f83aa73c41e9defae034ba0255134973f4fdf2f8f7808354274a3b1ebc6ee438be898d045e8b56ba1fe1300000000000000000000000000000000fffffff80000000000000000000000000000000000000000000000000600000000646be3d300000000646be3d2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    success = analyze_tx_data(data3)
    #
    data4 = '0x2cc4081e000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000010557cc00000000000000000000000000000000000000000000000000000000646b68b30000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000080115c708e12edd42e504c1cd52aea96c547c05c00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000600000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000dc8d45d062e2fa5cd76b17d24f8691c950d0de5800000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'
    fail = analyze_tx_data(data4)


    # print(get_update_data('eth'))
    # get_ABI_functions('config/syncswap_pool_abi.json')