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
            """
            Register data on the smart contract.
            
            Args:
                data_hash (str): Hash of the data.
                filename (str): Name of the file.
                file_cid (str): Content ID of the file on IPFS.
                size (int): Size of the file.
                account (str): Ethereum address of the account registering the data.
            
            Returns:
                dict: Transaction receipt if successful, None otherwise.
            """
            try:
                # Validate input data types
                if not isinstance(data_hash, str) or not data_hash.startswith('0x'):
                    raise ValueError("Invalid data hash.")
                if not isinstance(filename, str) or len(filename) > 32:
                    raise ValueError("Invalid filename.")
                if not isinstance(file_cid, str) or len(file_cid) > 32:
                    raise ValueError("Invalid file CID.")
                if not isinstance(size, int) or size <= 0:
                    raise ValueError("Invalid size.")
                if not self.web3.isAddress(account):
                    raise ValueError("Invalid Ethereum address.")

                # Convert data types
                data_hash_bytes = Web3.toBytes(hexstr=data_hash)
                filename_bytes32 = Web3.toBytes(text=filename.ljust(32, '\x00'))
                file_cid_bytes32 = Web3.toBytes(text=file_cid.ljust(32, '\x00'))
                size_uint256 = self.web3.toWei(size, 'ether')  # Convert to wei (uint256)

                # Call the register function with the correct types
                tx_hash = self.contract.functions.register(
                    data_hash_bytes, filename_bytes32, file_cid_bytes32, size_uint256
                ).transact({'from': account})

                # Wait for transaction receipt
                receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
                return receipt
            except Exception as e:
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
