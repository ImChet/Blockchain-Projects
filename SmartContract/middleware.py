import os
import time
import logging
from flask import Flask, request, jsonify
from web3 import Web3, HTTPProvider
import json
import subprocess
import shlex
import pexpect
import re

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Use Web3 to connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Set the default transaction sender to the first account provided by Ganache
default_sender = web3.eth.accounts[0]

# Read contract address from environment variable and convert it to checksum address
contract_address_env = os.environ.get("CONTRACT_ADDRESS")
logging.debug(f"contract_address_env variable set to: {contract_address_env}")
if not contract_address_env:
    raise ValueError("CONTRACT_ADDRESS environment variable not set")

contract_address = Web3.to_checksum_address(contract_address_env)

# Load the contract ABI
with open(
    "./build/contracts/TokenManager.json", "r"
) as file:
    contract_json = json.load(file)
    contract_abi = contract_json["abi"]

logging.debug(f"contract_abi set to: {contract_abi}")
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


@app.route("/deposit", methods=["POST"])
def deposit():
    logging.debug("Received deposit request.")
    account_id = request.json["account_id"]
    logging.debug(f"Account ID: {account_id}")
    token_value = int(request.json["token_value"])
    logging.debug(f"Token Value: {token_value}")
    try:
        tx_hash = contract.functions.deposit(account_id, token_value).transact(
            {"from": account_id}
        )
        logging.debug(f"Transaction Hash: {tx_hash}")
        web3.eth.wait_for_transaction_receipt(tx_hash)
        logging.debug("Transaction completed.")
        return jsonify({"status": "Transaction completed"})
    except Exception as e:
        logging.error(f"Error during deposit: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/withdraw", methods=["POST"])
def withdraw():
    logging.debug("Received withdraw request.")
    account_id = request.json["account_id"]
    logging.debug(f"Account ID: {account_id}")
    token_value = int(request.json["token_value"])
    logging.debug(f"Token Value: {token_value}")
    try:
        tx_hash = contract.functions.withdraw(account_id, token_value).transact(
            {"from": account_id}
        )
        logging.debug(f"Transaction Hash: {tx_hash}")
        web3.eth.wait_for_transaction_receipt(tx_hash)
        logging.debug("Transaction completed.")
        return jsonify({"status": "Transaction completed"})
    except Exception as e:
        logging.error(f"Error during withdraw: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def query():
    logging.debug("Received query request.")
    account_id = request.json["account_id"]
    logging.debug(f"Account ID: {account_id}")
    try:
        # Log details to help with debugging
        logging.info(f"Querying balance for account ID: {account_id}")
        logging.info(f"Using contract address: {contract_address}")

        # Get the balance of the specified account using web3.py's get_balance function
        # balance = web3.eth.get_balance(account_id)
        balance = contract.functions.query(account_id).call(
            {"from": account_id}
        )
        logging.debug(f"Balance for account ID {account_id}: {balance}")
        return jsonify({"balance": balance})
    except Exception as e:
        logging.error(f"Error during query: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/set_policy', methods=['POST'])
def set_policy():
    logging.debug("Received set policy request.")
    account_id = request.json['account_id']
    str_policy = request.json['str_policy']
    logging.debug(f"Account ID: {account_id}")
    logging.debug(f"Policy: {str_policy}")
    try:
        # Send the transaction and get the transaction hash
        tx_hash = contract.functions.setPolicy(account_id, str_policy).transact({'from': account_id})
        logging.debug(f"Transaction Hash: {tx_hash.hex()}")  # Convert to string
        
        # Wait for the transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # Set timeout to 120 seconds
        logging.debug("Transaction completed.")
        
        # Check if the transaction was successful
        if receipt.status == 1:
            return jsonify({'status': 'Transaction completed', 'tx_hash': tx_hash.hex()})  # Convert to string
        else:
            return jsonify({'error': 'Transaction failed', 'tx_hash': tx_hash.hex()}), 500  # Convert to string
    except Exception as e:
        logging.error(f"Error setting policy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_policy', methods=['POST'])
def get_policy():
    logging.debug("Received get policy request.")
    account_id = request.json['account_id']
    logging.debug(f"Account ID: {account_id}")
    try:
        # Call the getPolicy function of the smart contract
        policy = contract.functions.getPolicy(account_id).call(
             {"from": account_id}
        )

        return jsonify({'policy': policy})

    except Exception as e:
        logging.error(f"Error getting policy: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

