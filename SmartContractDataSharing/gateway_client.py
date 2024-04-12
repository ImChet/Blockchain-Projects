import requests
from web3 import Web3

# Configuration
GATEWAY_URL = "http://127.0.0.1:8080"

# Connect to Ganache and get accounts
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
accounts = web3.eth.accounts

# Use the first account as the default account for this example
default_account = accounts[0]
print(f"Using the first account from Ganache: {default_account}")

def handle_response(response):
    if response.ok:
        try:
            response_json = response.json()
            print(f"Response: {response_json}")
        except ValueError:
            print(f"Failed to decode JSON. Status Code: {response.status_code}, Response Text: {response.text}")
    else:
        print(f"Request failed. Status Code: {response.status_code}, Response Text: {response.text}")

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


def register_data_on_gateway(data_hash, filename, file_cid, size):
    data = {
        'data_hash': data_hash,
        'filename': filename,
        'file_cid': file_cid,
        'size': size,
        'account': default_account
    }
    response = requests.post(f"{GATEWAY_URL}/register_data", json=data)
    handle_response(response)

def transfer_data_on_gateway(data_hash, to_address):
    data = {
        'data_hash': data_hash,
        'from_address': default_account,
        'to_address': to_address
    }
    response = requests.post(f"{GATEWAY_URL}/transfer_data", json=data)
    handle_response(response)

def burn_data_on_gateway(data_hash):
    data = {
        'data_hash': data_hash,
        'from_address': default_account
    }
    response = requests.post(f"{GATEWAY_URL}/burn_data", json=data)
    handle_response(response)

def query_tracker_on_gateway(data_hash):
    response = requests.get(f"{GATEWAY_URL}/query_tracker", params={'data_hash': data_hash})
    handle_response(response)

# Example usage
if __name__ == "__main__":
    upload_response = upload_to_gateway('/practical/file.txt')
    if upload_response:
        file_hash = upload_response['public']
        register_data_on_gateway(file_hash, upload_response['filename'], file_hash, upload_response['size'])
        transfer_data_on_gateway(file_hash, '0xRecipientAddress')
        burn_data_on_gateway(file_hash)
        query_tracker_on_gateway(file_hash)
        download_from_gateway(file_hash)