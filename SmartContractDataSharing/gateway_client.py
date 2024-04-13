import requests
from requests.utils import requote_uri
from web3 import Web3

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
        
        # Save the downloaded content to a file with the extracted filename
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f'Download successful, saved as {filename}')
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

# # Example usage
# if __name__ == "__main__":
#     print("Client script started.")
#     # Prompt the user for an absolute file path
#     file_path = input("Please enter the absolute path of the file you want to upload: ")
#     uploaded_file = upload_to_gateway(file_path)
#     if uploaded_file:
#         file_cid = uploaded_file['public']
#         file_hex_hash_str = '0x' + uploaded_file['hash']
#         register_response = register_data(file_hex_hash_str, uploaded_file['filename'], uploaded_file['public'], int(uploaded_file.get('size', 0)), default_account)
#         if register_response:
#             transfer_response = transfer_data(file_hex_hash_str, transfer_account)
#             if transfer_response:
#                 burn_response = burn_data(file_hex_hash_str, transfer_account)
#                 if burn_response:
#                     tracker_response = query_tracker(file_hex_hash_str)
#                     if tracker_response:
#                         download_from_gateway(file_cid)
#     print("Client script finished.")

def main_menu():
    print("\nChoose an action:")
    print("1: Register File")
    print("2: Transfer Data Token")
    print("3: Burn Data Token")
    print("4: Query Data Transfer Tracker")
    print("5: Download File")
    print("0: Exit")
    return input("Enter the number of the action you want to perform: ")

# Define a function to execute each action
def get_account_selection(accounts):
    print("\nAvailable accounts:")
    for index, account in enumerate(accounts):
        print(f"{index}: {account}")
    selected_index = int(input("Select an account by entering the number next to it: "))
    if 0 <= selected_index < len(accounts):
        return accounts[selected_index]
    else:
        print("Invalid selection. Please try again.")
        return get_account_selection(accounts)

def transfer_data_token(file_hex_hash_str, current_owner):
    to_account = get_account_selection(accounts)  # Let the user pick an account
    # Query the current owner of the token from the smart contract
    token_info = query_token(file_hex_hash_str)
    if token_info and token_info['owner'] == current_owner:
        print(f"Transferring data token with hash {file_hex_hash_str} from {current_owner} to {to_account}...")
        data = {
            'data_hash': file_hex_hash_str,
            'from_address': current_owner,
            'to_address': to_account
        }
        response = requests.post('http://localhost:8080/transfer', json=data)
        print("Transfer response:", response.text)
        if response.ok:
            # If transfer is successful, update the current owner
            return response.json(), to_account
        else:
            return None, current_owner
    else:
        print("Transfer failed: You are not the owner of this token.")
        return None, current_owner

def burn_data_token(file_hex_hash_str, current_owner):
    # Query the current owner of the token from the smart contract
    token_info = query_token(file_hex_hash_str)
    if token_info and token_info['owner'] == current_owner:
        print(f"Burning data token with hash {file_hex_hash_str}...")
        data = {
            'data_hash': file_hex_hash_str,
            'from_address': current_owner
        }
        response = requests.post('http://localhost:8080/burn', json=data)
        print("Burn response:", response.text)
        return response.json() if response.ok else None
    else:
        print("Burn failed: You are not the owner of this token.")
        return None


def query_data_tracker(file_hex_hash_str):
    return query_tracker(file_hex_hash_str)

def download_data(file_cid):
    download_from_gateway(file_cid)

# Example usage
if __name__ == "__main__":
    print("Client script started.")
    
    # Prompt the user for an absolute file path
    file_path = input("Please enter the absolute path of the file you want to upload: ")
    uploaded_file = upload_to_gateway(file_path)
    file_hex_hash_str = None
    file_cid = None

    if uploaded_file:
        file_cid = uploaded_file['public']
        file_hex_hash_str = '0x' + uploaded_file['hash']
        print("File uploaded successfully. You may now choose further actions for this file.")
    else:
        print("File upload failed. Please check the file path and try again.")
        exit(0)

    while True:
        user_choice = main_menu()
        
        if user_choice == '1' and file_hex_hash_str:
            register_response = register_data(file_hex_hash_str, uploaded_file['filename'], uploaded_file['public'], int(uploaded_file.get('size', 0)), default_account)
            if register_response:
                print("Data registered on the blockchain.")
            else:
                print("Failed to register data.")
        
        elif user_choice == '2' and file_hex_hash_str:
            transfer_response, new_owner = transfer_data_token(file_hex_hash_str, default_account)
            if transfer_response:
                # Update the default account to the new owner after a successful transfer
                default_account = new_owner
                print("Transfer successful.")
            else:
                print("Transfer failed.")
        
        elif user_choice == '3' and file_hex_hash_str:
            burn_response = burn_data_token(file_hex_hash_str, default_account)
            if burn_response:
                print("Burn response:", burn_response)
        
        elif user_choice == '4' and file_hex_hash_str:
            tracker_response = query_data_tracker(file_hex_hash_str)
            if tracker_response:
                print("Tracker response:", tracker_response)
        
        elif user_choice == '5' and file_cid:
            download_data(file_cid)
            print("Download complete.")
        
        elif user_choice == '0':
            print("Exiting the script.")
            break
        
        else:
            print("Invalid choice or action not available. Please try again.")

    print("Client script finished.")
