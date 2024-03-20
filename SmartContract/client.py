import requests
import random
import time
from web3 import Web3

# Configuration
GATEWAY_URL = "http://127.0.0.1:8080/api"
GANACHE_URL = "http://127.0.0.1:8545"

# Connect to Ganache and get accounts
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
accounts = web3.eth.accounts

# Randomly select an account
test_account_id = random.choice(accounts)
print(f"Using random account from Ganache: {test_account_id}")

def handle_response(response):
    if response.ok:
        try:
            response_json = response.json()
            print(f"Response: {response_json}")
        except requests.exceptions.JSONDecodeError:
            print(f"Failed to decode JSON. Status Code: {response.status_code}, Response Text: {response.text}")
    else:
        print(f"Request failed. Status Code: {response.status_code}, Response Text: {response.text}")

def deposit(token_value):
    print("Testing deposit...")
    print("Deposit function called.")
    data = {"account_id": test_account_id, "token_value": token_value}
    print(f"Sending request to {GATEWAY_URL}/deposit with data: {data}")
    response = requests.post(f"{GATEWAY_URL}/deposit", json=data)
    print("Response received:")
    handle_response(response)

def withdraw(token_value):
    print("\nTesting withdraw...")
    print("Withdraw function called.")
    data = {"account_id": test_account_id, "token_value": token_value}
    print(f"Sending request to {GATEWAY_URL}/withdraw with data: {data}")
    response = requests.post(f"{GATEWAY_URL}/withdraw", json=data)
    print("Response received:")
    handle_response(response)

def query():
    print("\nTesting query...")
    print("Query function called.")
    data = {"account_id": test_account_id}
    print(f"Sending request to {GATEWAY_URL}/query with data: {data}")
    response = requests.post(f"{GATEWAY_URL}/query", json=data)
    print("Response received:")
    handle_response(response)

def set_policy(str_policy):
    print("\nTesting set policy...")
    print("Set policy function called.")
    data = {"account_id": test_account_id, "str_policy": str_policy}
    print(f"Sending request to {GATEWAY_URL}/set_policy with data: {data}")
    response = requests.post(f"{GATEWAY_URL}/set_policy", json=data)
    print("Response received:")
    handle_response(response)

def get_policy():
    print("\nTesting get policy...")
    print("Get policy function called.")
    data = {"account_id": test_account_id}
    print(f"Sending request to {GATEWAY_URL}/get_policy with data: {data}")
    response = requests.post(f"{GATEWAY_URL}/get_policy", json=data)
    print("Response received:")
    handle_response(response)

if __name__ == "__main__":
    deposit(100)
    withdraw(50)
    query()
    set_policy("active")
    get_policy()
