from web3 import Web3
import os
import json

class EthereumMiddleware:
    def __init__(self):
        rpc_url = "http://127.0.0.1:8545"  # Ganache RPC URL
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Load contract details
        contract_address = os.getenv('CONTRACT_ADDRESS', 'default_contract_address')
        self.contract_address = Web3.toChecksumAddress(contract_address)
        
        # Load ABI
        with open('build/contracts/DataToken.json', 'r') as abi_file:
            contract_abi = json.load(abi_file)['abi']

        self.contract = self.web3.eth.contract(address=self.contract_address, abi=contract_abi)

    def register_data(self, data_hash, filename, file_cid, size, account):
        function = self.contract.functions.register(data_hash, filename, file_cid, size)
        tx_hash = function.transact({'from': account})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def query_data(self, data_hash):
        return self.contract.functions.query(data_hash).call()

    def transfer_data(self, data_hash, from_address, to_address):
        function = self.contract.functions.transferData(data_hash, to_address)
        tx_hash = function.transact({'from': from_address})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def burn_data(self, data_hash, from_address):
        function = self.contract.functions.burn(data_hash)
        tx_hash = function.transact({'from': from_address})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def query_tracker(self, data_hash):
        return self.contract.functions.queryTracker(data_hash).call()
