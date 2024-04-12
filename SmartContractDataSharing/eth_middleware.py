from web3 import Web3
import os
import json

class EthereumMiddleware:
    def __init__(self):
        # Use the Ganache RPC URL
        rpc_url = "http://127.0.0.1:8545"
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.isConnected():
            raise ConnectionError("Unable to connect to the Ethereum node at " + rpc_url)

        # Load contract details
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address:
            raise EnvironmentError('CONTRACT_ADDRESS environment variable not set.')
        self.contract_address = Web3.toChecksumAddress(contract_address)
        
        # Load the ABI from the contract JSON file
        with open('build/contracts/DataToken.json', 'r') as abi_file:
            contract_abi = json.load(abi_file)['abi']

        self.contract = self.web3.eth.contract(address=self.contract_address, abi=contract_abi)

    # Use this to handle sending transactions
    def send_transaction(self, function, account):
        tx_hash = function.transact({'from': account})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def register_data(self, data_hash, filename, file_cid, size, account):
        # Call the register function from the smart contract
        function = self.contract.functions.register(Web3.toBytes(hexstr=data_hash), filename, file_cid, size)
        return self.send_transaction(function, account)

    def query_data(self, data_hash):
        # Call the query function from the smart contract
        return self.contract.functions.query(Web3.toBytes(hexstr=data_hash)).call()

    def transfer_data(self, data_hash, from_address, to_address):
        # Call the transferData function from the smart contract
        function = self.contract.functions.transferData(Web3.toBytes(hexstr=data_hash), to_address)
        return self.send_transaction(function, from_address)

    def burn_data(self, data_hash, from_address):
        # Call the burn function from the smart contract
        function = self.contract.functions.burn(Web3.toBytes(hexstr=data_hash))
        return self.send_transaction(function, from_address)

    def query_tracker(self, data_hash):
        # Call the queryTracker function from the smart contract
        return self.contract.functions.queryTracker(Web3.toBytes(hexstr=data_hash)).call()
