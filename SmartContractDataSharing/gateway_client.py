import requests

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

# Downloads a file from the Flask server using the file hash
def download_from_gateway(file_hash):
    # Make a GET request to download the file by its hash
    response = requests.get(f'http://localhost:8080/download/{file_hash}', stream=True)
    print(f'Response from download_from_gateway(): {response}')
    if response.status_code == 200:
        # Save the downloaded content to a file
        with open(f'downloaded_{file_hash}', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)  # Write in chunks to avoid loading the whole file into memory
        print('Download successful')
    else:
        # Handle download errors
        print('Download failed')

# Example usage of the client functions
upload_response = upload_to_gateway('/practical/file.txt')  # Replace '/practical/file.txt' with your file path
if upload_response:
    file_hash = upload_response['public']
    print(f'public: {file_hash}')
    download_from_gateway(file_hash)