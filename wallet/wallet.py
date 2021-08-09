# Import dependencies
import os
from dotenv import load_dotenv
import subprocess
import json
from pprint import pprint

# Import constants.py and necessary functions from bit and web3
from constants import BTC, BTCTEST, ETH
from web3 import Web3, middleware, Account
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy # new
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI


load_dotenv('../blockchain_hw19.env')
mnemonic=os.getenv("mnemonic")


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

 
# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic, depth):
    wallet_fpath = '/Users/rhnil/Desktop/Columbia_Bootcamp/Blockchain_Python_homework19/wallet/hd-wallet-derive/hd-wallet-derive.php'
    command = f'php {wallet_fpath} -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_txn(coin, account, recipient, amount):
    if coin == ETH:
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
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_txn(coin, account, recipient, amount):
    if coin == ETH:
        raw_txn = create_txn(coin, account.address, recipient, amount)
        signed_txn = account.signTransaction(raw_txn)
        return w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    if coin == BTCTEST:
        raw_txn = create_txn(coin, account, recipient, amount)
        signed_txn = account.sign_transaction(raw_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)
    
# Create a dictionary object called coins to store the output from `derive_wallets`.
no_of_accounts = 3
coins = {BTC: derive_wallets(BTC, mnemonic, no_of_accounts),
         ETH: derive_wallets(ETH, mnemonic, no_of_accounts),
         BTCTEST: derive_wallets(BTCTEST, mnemonic, no_of_accounts),
    
}

pprint(coins)