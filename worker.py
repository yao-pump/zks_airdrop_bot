import random
import time
from datetime import datetime

from cfg import rpcs
from database import update_account
from dex.izumiswap import IzumiSwap
from dex.syncswap import SyncSwap
from functions import bridge, mint_nft, open_position_zkdx, close_position_zkdx, claim_zkdx_usdc, swap
from others.eraland import EraLand
from others.zns import ZNS
from utils import get_coin_price


def create_tx_info(tx_data, activity):
    tx_info = {'status': tx_data[0], 'hash': tx_data[1],
               'activity': activity, 'time': datetime.fromtimestamp(time.time())}
    return tx_info


class Worker:
    def __init__(self, account, network_type='mainnet'):
        self.work_account = account
        self.network_type = network_type
        print('Worker start running on {} for account {}'.format(self.network_type, self.work_account.address))

    '''
    Interaction logic:
    0. check eth balance of the account in zks era network
        0.1 if eth balance < 0.003, either bridge eth or quit
        
    1. randomly choose one task: swap, mint nft, or zkdx future
    2. if the task is mint nft, directly call mint_square function
    3. if the task is swap
        3.1 check current account positions of all support coins (usdc, cheems, zat, izi)
        3.2 if the number of one of the above coin is not zero, check the buy price of that coin
            3.2.1 if the current price is higher than the buy price, sell the coin
            3.2.2 if not, either add liquidity of the coin or select another coin to buy
        3.3 if no above coins in the wallet, check whether liquidity of these coins are added
            3.3.1 if liquidity exists, remove liquidity
        3.4 if no coins and no liquidity, randomly select one coin to buy on a random swap app
    4. if the task is zkdx future, check whether current position exists
        4.1 if current position exists, check the profit
            4.1 if profit > 0, close the position
            4.2 if profit < 0, either close the position or add the position
        4.2 if no current position, open position
        
    weights of tasks: swap 6, mint nft 2, zkdx 2
    weights of swap coins: usdc 7, cheems 1, zat 1, izi 1
    '''

    def run_mint(self):
        tx_info = []
        print('Mint a NFT on mint square.')
        success = mint_nft(self.work_account, self.network_type)
        tx_info.append(create_tx_info(success, 'mint nft'))
        return tx_info

    def run_zkdx(self):
        tx_info = []
        zkdx_udsc_amount = self.work_account.get_balance('tudsc', 'zks_era', 'mainnet')
        if zkdx_udsc_amount < 20000:
            print('Claim ZkDX usdc')
            success = claim_zkdx_usdc(self.work_account)
            tx_info.append(create_tx_info(success, 'claim zkDX usdc'))
            if success[0]:
                time.sleep(random.uniform(2, 5))
            else:
                print('Claim zkdx usdc failed.')
                return tx_info

        print('Check existing positions on ZkDX.')
        if not self.work_account.zkdx_info:
            zkdx_udsc_amount = self.work_account.get_balance('tudsc', 'zks_era', 'mainnet')
            print('No existing positions. Open a new position. Available USDC amount: ', zkdx_udsc_amount)
            while True:
                try:
                    symbol = random.choice(['eth', 'btc', 'ltc'])
                    amount = random.choice([i * 1000 for i in range(10, int(zkdx_udsc_amount / 3000))])
                    leverage = random.choice([2, 3, 5, 8, 10])
                    is_long = random.choice([True, False])
                    print('Open a new position: ', symbol, amount, leverage, is_long)
                    success, size_delta, open_price = open_position_zkdx(self.work_account, symbol, amount, leverage,
                                                                         is_long)
                    break
                except:
                    time.sleep(random.uniform(3, 10))
            tx_info.append(create_tx_info(success,
                                          'Open a new position: symbol {}, amount {},'
                                          ' leverage {}, is_long {}, open_price {}'.format(symbol, amount,
                                                                                           leverage, is_long,
                                                                                           open_price)))
            if success[0]:
                update_account(client=None, account_address=self.work_account.address, field_name='zkdx',
                               field_value={'size_delta': str(size_delta), 'is_long': is_long,
                                            'open_price': open_price, 'symbol': symbol})
        else:
            print('Existing position: ', self.work_account.zkdx_info)
            symbol = self.work_account.zkdx_info['symbol']
            open_price = self.work_account.zkdx_info['open_price']
            is_long = self.work_account.zkdx_info['is_long']
            size_delta = int(self.work_account.zkdx_info['size_delta'])
            symbol_current_price, _, expo = get_coin_price(symbol)
            symbol_current_price = symbol_current_price * 10 ** expo
            if (symbol_current_price > open_price and is_long) or (
                    symbol_current_price < open_price and is_long is False):
                print('Close current position to take profit.')
                success = close_position_zkdx(self.work_account, symbol, size_delta, is_long)
                tx_info.append(create_tx_info(success, 'close position'))
                if success[0]:
                    update_account(client=None, account_address=self.work_account.address,
                                   field_name='zkdx', field_value=None)
                    return tx_info

            # choice = "close position"
            choice = random.choice(['add position', 'close position'])
            print('Current choice: %s' % choice)
            if choice == 'close position':
                success = close_position_zkdx(self.work_account, symbol, size_delta, is_long)
                tx_info.append(create_tx_info(success, 'close position'))
                if success[0]:
                    update_account(client=None, account_address=self.work_account.address,
                                   field_name='zkdx', field_value=None)
            else:
                zkdx_udsc_amount = self.work_account.get_balance('tudsc', 'zks_era', 'mainnet')
                amount = random.choice([i * 1000 for i in range(10, zkdx_udsc_amount // 3000)])
                leverage = random.choice([2, 5, 10, 20])
                print('Open a new position: ', symbol, amount, leverage, is_long)
                success, size_delta_add, open_price = open_position_zkdx(self.work_account, symbol, amount,
                                                                         leverage,
                                                                         is_long)
                tx_info.append(create_tx_info(success,
                                              'Open a new position: symbol {}, amount {},'
                                              ' leverage {}, is_long {}, open_price {}'.format(symbol, amount,
                                                                                               leverage, is_long,
                                                                                               open_price)))
                if success[0]:
                    update_account(client=None, account_address=self.work_account.address, field_name='zkdx',
                                   field_value={'size_delta': size_delta + size_delta_add, 'is_long': is_long,
                                                'open_price': open_price, 'symbol': symbol})
        return tx_info

    def run_swap(self):
        tx_info = []
        # check coin balance
        syncswap = SyncSwap(network=self.network_type)
        coin_balance = self.work_account.coin_balance.items()
        if len(coin_balance) > 0:
            for symbol, buy_amount in coin_balance:
                amount = self.work_account.get_balance(symbol, 'zks_era', self.network_type)
                amount_out = syncswap.query_swap(symbol, 'eth', amount)
                if amount_out > buy_amount:
                    print('Sell {} to take profit'.format(symbol))
                    # success = syncswap.swap(self.work_account, symbol, 'eth', amount)
                    # success = izumiswap.swap(self.work_account, symbol, 'eth', amount)
                    swap_choice = random.choice(['syncswap', 'izumiswap'])
                    success = swap(swap_choice, self.work_account, symbol, 'eth', amount)
                    tx_info.append(create_tx_info(success, 'Sell {}, amount: {}'.format(symbol, amount)))
                    if success[0]:
                        print('{} sold'.format(symbol))
                        other_balance = self.work_account.coin_balance.copy()
                        del (other_balance[symbol])
                        update_account(client=None, account_address=self.work_account.address,
                                       field_name='other_balance', field_value=other_balance)

                    return tx_info
        # coin_choice = 'usdc'
        coin_choice = random.choices(['usdc', 'cheems', 'izi', 'zat'], [0.4, 0.2, 0.2, 0.2])[0]
        if coin_choice == 'usdc':
            swap_choice = random.choice(['syncswap', 'izumiswap', 'muteswap'])
            # swap_choice = 'muteswap'
        elif coin_choice == 'izi':
            swap_choice = 'izumiswap'
        else:
            swap_choice = random.choice(['syncswap', 'izumiswap'])

        eth_balance = self.work_account.get_eth_balance('zks_era_{}'.format(self.network_type))
        swap_amount = random.uniform(eth_balance * 0.2, eth_balance * 0.4)
        print('Swap {}, amount: {} eth'.format(swap_choice, swap_amount))
        success = swap(swap_choice, self.work_account, 'eth', coin_choice, swap_amount, self.network_type)
        tx_info.append(create_tx_info(success, 'Swap {}, amount: {} eth'.format(swap_choice, swap_amount)))
        if success[0]:
            other_balance = self.work_account.coin_balance.copy()
            if coin_choice not in other_balance:
                other_balance[coin_choice] = swap_amount
            else:
                other_balance[coin_choice] += swap_amount

            update_account(client=None, account_address=self.work_account.address,
                           field_name='other_balance', field_value=other_balance)

        return tx_info

    def run_eraland_supply(self, symbol, amount):
        eraland = EraLand()
        success = eraland.supply(self.work_account, symbol, amount)
        return success

    def run_eraland_redeem(self, symbol, amount):
        eraland = EraLand()
        success = eraland.redeem(self.work_account, symbol, amount)
        return success

    def run_eraland(self):
        tx_info = []
        # check current supply in eraland, if exists, redeem it
        supply_eth = self.work_account.eraland_info['eth']
        supply_usdc = self.work_account.eraland_info['usdc']

        if supply_eth > 0:
            success = self.run_eraland_redeem('eth', supply_eth)
            tx_info.append('Redeem eth. Amount: {}'.format(supply_eth))
            if success[0]:
                self.work_account.eraland_info['eth'] = 0
            else:
                print('failed to redeem eth')
        elif supply_usdc > 0:
            success = self.run_eraland_redeem('usdc', supply_usdc)
            tx_info.append('Redeem usdc. Amount: {}'.format(supply_usdc))
            self.work_account.other_balance['usdc'] = supply_usdc
            update_account(None, self.work_account.address, 'other_balance',
                           self.work_account.other_balance)

            if success[0]:
                self.work_account.eraland_info['usdc'] = 0
            else:
                print('failed to redeem usdc')
        else:
            # check usdc balance in the account
            usdc_balance = self.work_account.get_balance('usdc', 'zks_era', self.network_type)
            if usdc_balance > 0:
                success = self.run_eraland_supply('usdc', usdc_balance)
                tx_info.append('Supply usdc. Amount: {}'.format(usdc_balance))
                del(self.work_account.other_balance['usdc'])
                update_account(None, self.work_account.address, 'other_balance',
                               self.work_account.other_balance)

                if success[0]:
                    self.work_account.eraland_info['usdc'] = usdc_balance
                else:
                    print('failed to supply usdc')
            else:
                eth_balance = self.work_account.get_eth_balance()
                supply_eth = round(eth_balance * random.uniform(0.2, 0.4), random.uniform(2, 5))
                success = self.run_eraland_supply('eth', supply_eth)
                tx_info.append('Supply eth. Amount: {}'.format(supply_eth))
                if success[0]:
                    self.work_account.eraland_info['eth'] = supply_eth
                else:
                    print('failed to supply eth')

        update_account(None, self.work_account.address, 'eraland', self.work_account.eraland_info)
        return tx_info

    def run_zns(self):
        tx_info = []
        zns = ZNS()
        success = zns.register_domain(self.work_account)
        tx_info.append(create_tx_info(success, 'Register domain.'))
        if success[0]:
            primary_domain = zns.get_primary_domain(self.work_account)
            if not primary_domain:
                domains = zns.get_owned_domains(self.work_account)
                success = zns.set_primary_domain(self.work_account, domains[0])
                tx_info.append(create_tx_info(success, 'Set primary domain.'))

        return tx_info

    def update_account_status(self):
        eth_balance_main = self.work_account.get_eth_balance("eth_mainnet")
        eth_balance_zks = self.work_account.get_eth_balance('zks_era_{}'.format(self.network_type))
        eth_balance = {"eth": eth_balance_main, "zks": eth_balance_zks}

        num_txs = rpcs['zks_era_mainnet'].eth.get_transaction_count(self.work_account.address)

        timestamp = time.time()
        last_tx_time = datetime.fromtimestamp(timestamp)
        # last_tx_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        update_account(None, self.work_account.address, 'eth_balance', eth_balance)
        update_account(None, self.work_account.address, 'num_txs', num_txs)
        update_account(None, self.work_account.address, 'last_tx_time', last_tx_time)
        print("Account status updated.")

    def run(self):
        eth_balance_zks = self.work_account.get_eth_balance('zks_era_{}'.format(self.network_type))
        print('ETH balance on zks_era_{}: {}'.format(self.network_type, eth_balance_zks))
        if eth_balance_zks < 0.003:
            # check eth in eraland
            if self.work_account.eraland_info['eth'] > 0:
                print('Reddem eth from eraland.')
                self.run_eraland_redeem('eth', self.work_account.eraland_info['eth'])
            else:
                print('Balance is too low. Try to bridge eth from other network.')
                success = bridge(self.work_account, self.network_type)
                if not success:
                    print('Bridge eth failed. Check your eth balance in your account.')
                    return
                else:
                    while True:
                        eth_balance = self.work_account.get_eth_balance('zks_era_{}'.format(self.network_type))
                        if eth_balance > 0.003:
                            break
                        else:
                            time.sleep(random.uniform(60, 120))

        # todo: add liquidity or remove liquidity
        # task = 'zns'
        task = random.choices(['swap', 'eraland', 'zkdx', 'zns'], weights=[0.5, 0.15, 0.2, 0.15], k=1)[0]
        print('Current task is: ', task)

        if task == 'mint nft':
            tx_info = self.run_mint()

        elif task == 'zkdx':
            tx_info = self.run_zkdx()

        elif task == 'swap':
            tx_info = self.run_swap()

        elif task == 'eraland':
            tx_info = self.run_eraland()

        elif task == 'zns':
            tx_info = self.run_zns()

        for tx in tx_info:
            self.work_account.transactions.append(tx)

        update_account(None, self.work_account.address, 'transactions', self.work_account.transactions)
        self.update_account_status()
        print('Account {} Done.'.format(self.work_account.address))
