# Blockchain_Python_homework19

## Onjective

Create a "universal" wallet that uses a secret 12 word mnemonic to access a set of addresses and keys related to the coin the user would like to transact in. Based on the coin the user chooses to trasact in -- send and receive transactions.  

### Solution
I utilzed hd-wallet-derive, a command-line tool that derives bip32 addresses and private keys for Bitcoin and many altcoins. Once I had a set of addresses and keys for each coin, I was able to create and send signed transactions in BTC-TEST coin or ETH.


### Test Transactions

#### ETH: Test Transactions
![ETH TEST](Images/eth_txn2.png)
![ETH TEST](Images/eth_txn.png)


#### BTC: Test Transations
![BTC TEST](Images/btc_test_txn4.png)
![BTC TEST](Images/btc_test_txn2.png)

