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
        print(f'\n---\ncontract_address for eth_middleware.py: {contract_address}\n---\n')

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

# wait_for_transaction_receipt
# to_bytes

    def register_data(self, data_hash, filename, file_cid, size, account):
        try:
            # Convert the data hash to bytes32
            data_hash_bytes = Web3.to_bytes(hexstr=(data_hash.encode()).hex())

            # Invoke the register function on the contract
            tx_hash = self.contract.functions.register(
                data_hash_bytes, filename, file_cid, size
            ).transact({'from': account})

            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt
        except ValueError as e:
            print(f"Error registering data: {str(e)}")
            return None

    def query_data(self, data_hash):
        # Call the query function from the smart contract
        return self.contract.functions.query(data_hash).call()

    def transfer_data(self, data_hash, from_address, to_address):
        # Call the transferData function from the smart contract
        tx_hash = self.contract.functions.transferData(data_hash, to_address).transact({'from': from_address})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def burn_data(self, data_hash, from_address):
        # Call the burn function from the smart contract
        tx_hash = self.contract.functions.burn(data_hash).transact({'from': from_address})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def query_tracker(self, data_hash):
        # Call the queryTracker function from the smart contract
        return self.contract.functions.queryTracker(data_hash).call()