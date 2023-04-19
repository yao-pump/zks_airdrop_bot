# zks_airdrop_bot
 
ZKSync interaction bot to earn airdrops 

## Functions
+ Wallet management
    - Create new wallets
    - Deposit and withdraw eth from/to CEX
    - Manage wallets using Mongodb
    - Monitor wallet interaction records

+ ZkSync v1 (lite) interaction
    - Official bridge
    - NFT mint

+ ZKSync v2 (era) interaction
    - Official bridge
    - NFT mint
    - SyncSwap
        + Swap
        + Add liquidity
    - MuteSwap
        + Swap
        + Add liquidity
    - Onchain Trade
        + Swap
        + Add liquidity

+ Automated workflow
    1. Optional: Create a new wallet, deposit random amount of eth from CEX
    2. Randomly select a wallet from database
    3. Randomly select an unfinished task from above interactions to do
    4. Update intersection records into database