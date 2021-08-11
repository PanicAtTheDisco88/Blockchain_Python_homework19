# Step 1: Program requirements
### Import dependencies, load and set environment variables

# Import dependencies
import subprocess
import json
import os

from dotenv import load_dotenv
import import_ipynb
import constants

from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import wif_to_key

from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

from pprint import pprint

# Load and set environment variables

# Import necessary functions from bit and web3
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

load_dotenv('../blockchain_hw19.env')
mnemonic=os.getenv("mnemonic")

# set gas price strategy to built-in "medium" algorithm (est ~5min per tx)
# see https://web3py.readthedocs.io/en/stable/gas_price.html?highlight=gas
# see https://ethgasstation.info/ API for a more accurate strategy
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# Step 2: Key functions
### 1) derive_wallets: Lookup and return account keys based on 12 word mnemonic
### 2) priv_key_to_account: Based on the coin passed to the function, looks up the coin's address and private key stored in the coin dictionary.
### 3) create_txn: Creates an unsigned transaction appropriate metadata.
### 4) send_txn: Calls create_txn, signs and sends the transaction.

# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic=mnemonic, depth=3):
    wallet_fpath = '/Users/rhnil/Desktop/Columbia_Bootcamp/Blockchain_Python_homework19/wallet/hd-wallet-derive/hd-wallet-derive.php'
    command = f'php {wallet_fpath} -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {'btc': derive_wallets(constants.BTC),
         'eth': derive_wallets(constants.ETH),
         'btc-test': derive_wallets(constants.BTCTEST), 
}

pprint(coins)

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin):
    if coin == 'eth':
        list_of_accounts = coins.get('eth')
        account_info =[]
        for coin in list_of_accounts:
            account_info.append(tuple((coin['address'],coin['privkey'])))
        return account_info
            
    if coin == 'btc-test':
        list_of_accounts = coins.get('btc-test')
        account_info =[]
        for coin in list_of_accounts:
            account_info.append(tuple((coin['address'], coin['privkey'])))
        return account_info
       


# Create a function called `create_txn` that creates an unsigned transaction appropriate metadata.
def create_txn(coin, account, recipient, amount):
    if coin == 'eth':
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas({"to":recipient, "from":account, "amount":amount})
        return {
            "to":recipient,
            "from":account,
            "value":value,
            "gas":gasEstimate,
            "gasPrice":w3.eth.generateGasPrice(),
            "nonce":w3.eth.getTransactionCount(account),
            "chainId":w3.eth.chain_id
        }
    if coin == 'btc-test':
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, constants.BTC)])

# Create a function called `send_txn` that calls `create_txn`, signs and sends the transaction.
def send_txn(coin, account, recipient, amount):
    if coin == 'eth':
        raw_txn = create_txn(coin, account.address, recipient, amount)
        signed_txn = account.signTransaction(raw_txn)
        return w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    if coin == 'btc-test':
        raw_txn = create_txn(coin, account, recipient, amount)
        print(raw_txn)
        signed_txn = account.sign_transaction(raw_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)

# Step 3: Test functions
### 1) Send ETH transaction and confirm via updated ETH balance
### 2) Send BTC-TEST transaction and confirm via updated BTC-TEST balance

# ETH: Get current eth account address and eth balance
sender_account_address = priv_key_to_account('eth')[0][0]
sender_eth_balance = w3.fromWei(w3.eth.getBalance(sender_account_address), "ether")
sender_key = Account.privateKeyToAccount(priv_key_to_account('eth')[0][1])

receiver_account_address = priv_key_to_account('eth')[1][0]
receiver_eth_balance = w3.fromWei(w3.eth.getBalance(receiver_account_address), "ether")

print(f"Sender account address: {sender_account_address}")
print(f"Sender ETH balance: {sender_eth_balance}")

print(f"Receiver account address: {receiver_account_address}")
print(f"Receiver ETH balance: {receiver_eth_balance}")

# ETH: Send eth 
send_txn('eth', sender_key, receiver_account_address, 1)

# ETH: Get updated eth account address and eth balance
sender_account_address = priv_key_to_account('eth')[0][0]
sender_eth_balance = w3.fromWei(w3.eth.getBalance(sender_account_address), "ether")

receiver_account_address = priv_key_to_account('eth')[1][0]
receiver_eth_balance = w3.fromWei(w3.eth.getBalance(receiver_account_address), "ether")


print(f"Sender account address: {sender_account_address}")
print(f"Sender ETH balance: {sender_eth_balance}")

print(f"Receiver account address: {receiver_account_address}")
print(f"Receiver ETH balance: {receiver_eth_balance}")


# BTC-TEST: Get account address and current btc-test balance
account_address = priv_key_to_account('btc-test')[0][0]
key = wif_to_key(priv_key_to_account('btc-test')[0][1])
print(f"Account address: {account_address}")
print(f"BTC-TEST balance: {key.get_balance('btc')}")

# BTC-TEST: Send btc-test and get new account balance
send_txn('btc-test', key, account_address, 0.000001)
print(f"Account address: {account_address}")
print(f"BTC-TEST balance: {key.get_balance('btc')}")