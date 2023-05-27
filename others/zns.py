import json
import time
import random

from base.zks_app_base import BaseAPP
from utils import execute_tx


class ZNS(BaseAPP):
    def __init__(self):
        BaseAPP.__init__(self, name='ZNS', network='mainnet')
        self.register_address = "0xCBE2093030F485adAaf5b61deb4D9cA8ADEAE509"
        self.domain_address = "0xCc788c0495894C01F01cD328CF637c7C441Ee69E"

        with open("config/zns_register_abi.json", encoding='utf-8', errors='ignore') as json_data:
            register_abi = json.load(json_data, strict=False)
        with open("config/zns_domain_abi.json", encoding='utf-8', errors='ignore') as json_data:
            domain_abi = json.load(json_data, strict=False)

        self.register_contract = self.rpc.eth.contract(
                address=self.register_address, abi=register_abi)

        self.domain_contract = self.rpc.eth.contract(
                address=self.domain_address, abi=domain_abi)

        words = open("config/words_alpha.txt", "r").readlines()
        self.word_list = [word[:-1] for word in words if 5 <= len(word) <= 8]


    def check_available(self, domain):
        result = self.register_contract.functions.available(domain).call()
        return result

    def can_register(self, account, domain):
        result = self.register_contract.functions.canRegister(domain, account.address).call()
        if False in result:
            return False
        else:
            return True

    def get_rent_price(self, domain, rent_year=1):
        result = self.register_contract.functions.rentPrice(domain, rent_year).call()
        return result


    def get_owned_domains(self, account):
        result = self.domain_contract.functions.getOwnedDomains(account.address).call()
        domains = []
        for i in range(len(result[0])):
            domains.append({'domain_name': result[1][i], 'domain_id': result[0][i]})
        return domains

    def get_primary_domain(self, account):
        result = self.domain_contract.functions.getPrimaryDomainName(account.address).call()
        if result == '':
            result = None
        return result

    def set_primary_domain(self, account, domain):
        domain_id = domain['domain_id']
        func = self.domain_contract.functions.setPrimaryDomain(domain_id)
        gas_estimate = func.estimate_gas({'from': account.address})

        tx = func.build_transaction(
            {'chainId': self.chain_id,
             'gas': gas_estimate,
             'gasPrice': self.rpc.eth.gas_price,
             'from': account.address,
             'nonce': self.rpc.eth.get_transaction_count(
                 account.address)})

        success = execute_tx(tx, account, self.rpc)
        return success

    def register_domain(self, account):
        try_time = 0
        while True:
            domain = random.choice(self.word_list)
            rent_price = self.get_rent_price(domain)
            if self.can_register(account, domain) and rent_price == 0:
                break
            else:
                if try_time == 10:
                    print("Cannot register a free domain")
                    return [False, '0x']
                else:
                    try_time += 1
                    time.sleep(random.uniform(0.5, 2))
        print("Register domain: ", domain)
        func = self.register_contract.functions.register(domain, account.address, 1)

        gas_estimate = func.estimate_gas({'from': account.address})

        tx = func.build_transaction(
            {'chainId': self.chain_id,
                'gas': gas_estimate,
                'gasPrice': self.rpc.eth.gas_price,
                'from': account.address,
                'nonce': self.rpc.eth.get_transaction_count(
                    account.address)})

        success = execute_tx(tx, account, self.rpc)
        return success
