import requests
from requests.utils import requote_uri
from web3 import Web3
import os

# Connect to Ganache and get accounts
web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
accounts = web3.eth.accounts
default_account = accounts[0]
transfer_account = accounts[1]

def handle_response(response):
    if response.status_code == 200:
        return response.json()  # Assuming response is in JSON format
    else:
        print("Error:", response.text)
        return None

# Uploads a file to the Flask server via HTTP POST
def upload_to_gateway(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        # Send the file to the server's upload endpoint
        response = requests.post('http://localhost:8080/upload', files=files)
        print("Raw response content:", response.text)

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                print('The response is not valid JSON:', e)
        else:
            print(f'Error {response.status_code}:')
            print(response.text)
        return None

def download_from_gateway(file_hash):
    # Make a GET request to download the file by its hash
    response = requests.get(requote_uri(f'http://localhost:8080/download/{file_hash}'), stream=True)
    
    if response.status_code == 200:
        # Extract the filename from the Content-Disposition header
        content_disposition = response.headers.get('content-disposition')
        filename = content_disposition.split("filename=")[-1].strip("\"'")
        
        # If no filename is found in the Content-Disposition header, use a default one
        if not filename:
            filename = f'dl_{file_hash}'
        
        # Define the path where the file will be saved
        download_path = os.path.join(os.getcwd(), filename)
        
        # Save the downloaded content to a file with the extracted filename
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # Get the absolute path of the downloaded file
        absolute_path = os.path.abspath(download_path)
        print(f'Download successful, saved as {absolute_path}')
    else:
        print('Download failed')

def register_data(data_hash, filename, file_cid, size, account):
    print("Registering data on the blockchain...")
    print(f"Data hash: {data_hash}")
    print(f"Filename: {filename}")
    print(f"File CID: {file_cid}")
    print(f"Size: {size}")
    print(f"Account: {account}")
    data = {
        'data_hash': data_hash,
        'filename': filename,
        'file_cid': file_cid,
        'size': size,
        'account': account
    }
    response = requests.post('http://localhost:8080/register', json=data)
    return handle_response(response)

def transfer_data(data_hash, to_address):
    print(f"Transferring data token with hash {data_hash} to the account specified at transfer_account: {transfer_account}...")
    data = {
        'data_hash': data_hash,
        'from_address': default_account,
        'to_address': to_address
    }
    response = requests.post('http://localhost:8080/transfer', json=data)
    print("Transfer response:", response.text)
    return response.json() if response.ok else None

def burn_data(data_hash, from_account):
    print(f"For testing, assume the account at \"{transfer_account}\" initiated a burning of data token with hash {data_hash}...")
    data = {
        'data_hash': data_hash,
        'from_address': from_account
    }
    response = requests.post('http://localhost:8080/burn', json=data)
    print("Burn response:", response.text)
    return response.json() if response.ok else None

def query_tracker(data_hash):
    print(f"Querying tracker for data token with hash {data_hash}...")
    response = requests.get(f'http://localhost:8080/tracker?data_hash={data_hash}')
    print("Tracker response:", response.text)
    return response.json() if response.ok else None

def query_token(data_hash):
    print(f"Querying token info for data token with hash {data_hash}...")
    response = requests.get(f'http://localhost:8080/query?data_hash={data_hash}')
    print("Query token response:", response.text)
    return response.json() if response.ok else None

# Example usage
if __name__ == "__main__":
    print("Client script started.")
    print(f'For testing purposes:\nYour address is: {default_account}\nThe account you will transfer to is: {transfer_account}')
    # Prompt the user for an absolute file path
    file_path = input("Please enter the absolute path of the file you want to upload: ")
    uploaded_file = upload_to_gateway(file_path)
    if uploaded_file:
        file_cid = uploaded_file['public']
        file_hex_hash_str = '0x' + uploaded_file['hash']
        register_response = register_data(file_hex_hash_str, uploaded_file['filename'], uploaded_file['public'], int(uploaded_file.get('size', 0)), default_account)
        if register_response:
            transfer_response = transfer_data(file_hex_hash_str, transfer_account)
            if transfer_response:
                burn_response = burn_data(file_hex_hash_str, transfer_account)
                if burn_response:
                    tracker_response = query_tracker(file_hex_hash_str)
                    if tracker_response:
                        download_from_gateway(file_cid)
    print("Client script finished.")
