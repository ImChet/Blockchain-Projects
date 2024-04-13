import requests
from requests.utils import requote_uri
from web3 import Web3
import hashlib

# Connect to Ganache and get accounts
web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
accounts = web3.eth.accounts
default_account = accounts[0]
transfer_account = accounts[1]
print(f"Using the first account from Ganache: {default_account}")

def handle_response(response):
    if response.status_code == 200:
        return response.json()  # Assuming response is in JSON format
    else:
        print("Error:", response.text)
        return None

# Uploads a file to the Flask server via HTTP POST
def upload_to_gateway(file_path):
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        files = {'file': f}  # Prepare the file for the request
        # Send the file to the server's upload endpoint
        response = requests.post('http://localhost:8080/upload', files=files)
        print("Raw response content:", response.text)  # Debugging: print raw response content

        # Check if the request was successful
        if response.status_code == 200:
            try:
                return response.json()  # Return the JSON response if available
            except ValueError as e:
                # Handle cases where the response is not valid JSON
                print('The response is not valid JSON:', e)
        else:
            # Handle error responses
            print(f'Error {response.status_code}:')
            print(response.text)
        return None  # Return None in case of errors

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
        
        # Save the downloaded content to a file with the extracted filename
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        print(f'Download successful, saved as {filename}')
    else:
        # Handle download errors
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
    print(f"Transferring data token with hash {data_hash}...")
    data = {
        'data_hash': data_hash,
        'from_address': default_account,
        'to_address': to_address
    }
    response = requests.post('http://localhost:8080/transfer', json=data)
    print("Transfer response:", response.text)
    return response.json() if response.ok else None

def burn_data(data_hash, from_account):
    print(f"Burning data token with hash {data_hash}...")
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
    print(f"Querying token for data token with hash {data_hash}...")
    response = requests.get(f'http://localhost:8080/query?data_hash={data_hash}')
    print("Token response:", response.text)
    return response.json() if response.ok else None

# Example usage
if __name__ == "__main__":
    print("Client script started.")
    print("Using account:", default_account)
    
    uploaded_file = upload_to_gateway('/practical/file.txt')
    if uploaded_file:
        file_hash = '0x' + uploaded_file['hash']
        # Convert the file_hash string to bytes using UTF-8 encoding
        print(f"File hash: {file_hash}")
        # query_token(file_hash)
        register_response = register_data(file_hash, uploaded_file['filename'], uploaded_file['public'], int(uploaded_file.get('size', 0)), default_account)
        if register_response:
            transfer_response = transfer_data(file_hash, transfer_account)
            if transfer_response:
                burn_response = burn_data(file_hash, transfer_account)
                if burn_response:
                    tracker_response = query_tracker(file_hash)
                    if tracker_response:
                        download_from_gateway(file_hash)
    print("Client script finished.")