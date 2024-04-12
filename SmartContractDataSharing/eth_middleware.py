from web3 import Web3
import os
import json
import base58
import binascii

class EthereumMiddleware:
    def __init__(self, rpc_url, contract_address):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError("Unable to connect to the Ethereum node.")

        # Load contract details
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address:
            raise EnvironmentError('CONTRACT_ADDRESS environment variable not set.')
        self.contract_address = Web3.to_checksum_address(contract_address)
        
        # Load the ABI from the contract JSON file
        with open('build/contracts/DataToken.json', 'r') as abi_file:
            self.contract_abi = json.load(abi_file)['abi']  # Make sure this variable is assigned

        self.contract = self.web3.eth.contract(
            address=self.contract_address, 
            abi=self.contract_abi  # Use the instance variable here
        )

    # Use this to handle sending transactions
    def send_transaction(self, function, account):
        tx_hash = function.transact({'from': account})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def register_data(self, data_hash, filename, file_cid, size, account):
        # Decode Base58 string to bytes
        try:
            data_hash_bytes = base58.b58decode(data_hash)
        except ValueError as e:
            raise ValueError(f"Invalid Base58 value: {data_hash}") from e

        # Ensure the decoded bytes are 32 bytes in length
        print(f'data_hash_bytes: {data_hash_bytes}')
        print(f'len(data_hash_bytes): {len(data_hash_bytes)}')
        if len(data_hash_bytes) != 32:
            # You may need to adjust this depending on your exact requirements
            raise ValueError("The decoded data hash must be exactly 32 bytes in length.")

        # Continue with the smart contract interaction using the bytes
        function = self.contract.functions.register(data_hash_bytes, filename, file_cid, size)
        tx_hash = function.transact({'from': account})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def query_data(self, data_hash):
        # Call the query function from the smart contract
        return self.contract.functions.query(Web3.to_bytes(hexstr=data_hash)).call()

    def transfer_data(self, data_hash, from_address, to_address):
        # Call the transferData function from the smart contract
        function = self.contract.functions.transferData(Web3.to_bytes(hexstr=data_hash), to_address)
        return self.send_transaction(function, from_address)

    def burn_data(self, data_hash, from_address):
        # Call the burn function from the smart contract
        function = self.contract.functions.burn(Web3.to_bytes(hexstr=data_hash))
        return self.send_transaction(function, from_address)

    def query_tracker(self, data_hash):
        # Call the queryTracker function from the smart contract
        return self.contract.functions.queryTracker(Web3.to_bytes(hexstr=data_hash)).call()
