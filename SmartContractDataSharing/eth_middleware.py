from web3 import Web3

class EthereumMiddleware:
    def __init__(self, rpc_url, contract_address, contract_abi):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = Web3.toChecksumAddress(contract_address)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=contract_abi)

    def register_data(self, data_hash, filename, file_cid, size, account):
        function = self.contract.functions.register(data_hash, filename, file_cid, size)
        tx_hash = function.transact({'from': account})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def query_data(self, data_hash):
        return self.contract.functions.query(data_hash).call()

    def transfer_data(self, data_hash, from_address, to_address):
        tx_hash = self.contract.functions.transferData(Web3.toBytes(hexstr=data_hash), to_address).transact({'from': from_address})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def burn_data(self, data_hash, from_address):
        tx_hash = self.contract.functions.burn(Web3.toBytes(hexstr=data_hash)).transact({'from': from_address})
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

    def query_tracker(self, data_hash):
        transfer_log = self.contract.functions.query_tracker(Web3.toBytes(hexstr=data_hash)).call()
        return transfer_log