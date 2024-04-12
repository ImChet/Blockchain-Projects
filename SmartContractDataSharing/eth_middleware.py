from web3 import Web3
import os
import json

class EthereumMiddleware:
    def __init__(self, rpc_url, contract_address):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError("Unable to connect to the Ethereum node.")

        self.contract_address = Web3.to_checksum_address(contract_address)
        
        # Load the ABI from the contract JSON file
        with open('build/contracts/DataToken.json', 'r') as abi_file:
            self.contract_abi = json.load(abi_file)['abi']
            print("Contract ABI:", self.contract_abi)  # Add this line to print the contract ABI
        
        self.contract = self.web3.eth.contract(
            address=self.contract_address, 
            abi=self.contract_abi
        )

    def register_data(self, data_hash, filename, file_cid, size, account):
        try:
            print(f"Registering data - data_hash: {data_hash}, filename: {filename}, file_cid: {file_cid}, size: {size}, account: {account}")

            # Convert data_hash to bytes32
            data_hash_bytes = self.web3.to_bytes(hexstr=data_hash)

            # Convert filename and file_cid to string
            filename_str = str(filename)
            file_cid_str = str(file_cid)

            # Ensure size is an integer
            size_int = int(size)

            print(f"data_hash_bytes type: {type(data_hash_bytes)}")
            print(f"filename_str type: {type(filename_str)}")
            print(f"file_cid_str type: {type(file_cid_str)}")
            print(f"size_int type: {type(size_int)}")


            print("Calling register function on the contract.")
            # Call the register function with the correct types
            tx_hash = self.contract.functions.register(
                data_hash_bytes, filename_str, file_cid_str, size_int
            ).transact({'from': account})

            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print("Registration transaction receipt:", receipt)
            return receipt
        except ValueError as e:
            print(f"Error registering data: {str(e)}")
            return None

    def query_data(self, data_hash):
        # Call the query function from the smart contract
        return self.contract.functions.query(data_hash).call()

    def transfer_data(self, data_hash, from_address, to_address):
        # Send transaction to transfer data
        tx_hash = self.contract.functions.transferData(data_hash, to_address).transact({'from': from_address})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def burn_data(self, data_hash, from_address):
        # Send transaction to burn data
        tx_hash = self.contract.functions.burn(data_hash).transact({'from': from_address})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def query_tracker(self, data_hash):
        # Call the queryTracker function from the smart contract
        return self.contract.functions.queryTracker(data_hash).call()