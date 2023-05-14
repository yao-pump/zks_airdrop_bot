from nft.utils import upload_image_to_url, send_url_request
from urllib.request import urlopen
from nft.NFTMarketplace import NFTMarketplace
import json

from utils import execute_tx


class MintSquare(NFTMarketplace):
    def __init__(self, network='testnet'):
        NFTMarketplace.__init__(self, name='mint_square', network=network)
        self.abi_path = 'mint_square_abi.json'
        with open("config/{}".format(self.abi_path), encoding='utf-8', errors='ignore') as json_data:
            abi = json.load(json_data, strict=False)

        if network == 'testnet':
            contract_address = self.rpc.to_checksum_address('0x74E6d686F70fD5829f00dB0F95EC0f153970baD3')
        else:
            contract_address = self.rpc.to_checksum_address('0x53eC17BD635F7A54B3551E76Fd53Db8881028fC3')

        self.contract = self.rpc.eth.contract(address=contract_address, abi=abi)

    def upload_image(self, image_web_link):
        url = 'https://api.mintsquare.io/files/upload/'
        # download image as a binary file
        image = urlopen(image_web_link).read()
        response = upload_image_to_url(image, url)
        if response:
            return str(response.text)
        else:
            return None

    def get_nft_hash(self, image_info):
        url = 'https://api.mintsquare.io/metadata/upload/'
        # metadata = {"name": image_info["name"], "attributes": image_info["attributes"],
        #             "image": image_info["link"]}
        # metadata = '{"name":"pepe","attributes":[],"image":"https://mintsquare.sfo3.cdn.digitaloceanspaces.com/mintsquare/mintsquare/DVs4it1BqbXamu5P1LzVdJ_1683930338725226565.webp"}'
        # metadata = json.dumps(metadata)
        # metadata = metadata.replace('"', '\"')
        metadata = "{\"name\":\"pepe\",\"attributes\":[],\"image\":\"http\"}"
        metadata = metadata.replace("pepe", image_info["name"])
        metadata = metadata.replace("http", image_info["link"])

        payload = {"metadata": metadata}

        # payload = {"metadata":"{\"name\":\"{image_info['name']}\",\"attributes\":[],\"image\":\"{image_info['link']}\"}"}
        response = send_url_request(url, method='POST', data=json.dumps(payload))
        # print(response.text)
        return response

    def mint_nft(self, nft_info, account):
        uri = "ipfs://{}".format(nft_info["Hash"])
        func = self.contract.functions.mint(uri)
        gas_estimate = func.estimate_gas({'from': account.address})

        # print(gas_estimate)

        tx = func.build_transaction(
            {'chainId': self.chain_id,
             'gas': gas_estimate,
             'gasPrice': self.rpc.eth.gas_price,
             'from': account.address,
             'value': 0,
             'nonce': self.rpc.eth.get_transaction_count(
                 account.address)})

        success = execute_tx(tx, account, self.rpc)




