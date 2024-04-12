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

        self.contract = self.web3.eth.contract(
            address=self.contract_address, 
            abi=self.contract_abi
        )
        
    def register_data(self, data_hash, filename, file_cid, size, account):
        try:
            # Convert data_hash to bytes32
            data_hash_bytes = bytes.fromhex(data_hash[2:])  # Remove '0x' prefix and convert to bytes

            # Convert filename and file_cid to bytes32
            filename_bytes32 = filename.encode('utf-8')
            if len(filename_bytes32) > 32:
                raise ValueError("Filename exceeds 32 bytes.")
            filename_bytes32 += b'\x00' * (32 - len(filename_bytes32))  # Pad with null bytes

            file_cid_bytes32 = file_cid.encode('utf-8')
            if len(file_cid_bytes32) > 32:
                raise ValueError("File CID exceeds 32 bytes.")
            file_cid_bytes32 += b'\x00' * (32 - len(file_cid_bytes32))  # Pad with null bytes

            # Convert size to uint256
            size_uint256 = int(size)

            # Call the register function with the correct types
            tx_hash = self.contract.functions.register(
                data_hash_bytes, filename_bytes32, file_cid_bytes32, size_uint256
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
