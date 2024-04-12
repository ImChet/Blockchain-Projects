import requests
from requests.utils import requote_uri

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
    print(f'Response from download_from_gateway(): {response}')
    
    if response.status_code == 200:
        # Extract the filename from the Content-Disposition header
        content_disposition = response.headers.get('content-disposition')
        filename = content_disposition.split("filename=")[-1].strip("\"'")
        
        # If no filename is found in the Content-Disposition header, use a default one
        if not filename:
            filename = f'downloaded_{file_hash}'
        
        # Save the downloaded content to a file with the extracted filename
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        print(f'Download successful, saved as {filename}')
    else:
        # Handle download errors
        print('Download failed')

# Example usage of the client functions
upload_response = upload_to_gateway('/practical/file.txt')  # Replace '/practical/file.txt' with your file path
if upload_response:
    file_hash = upload_response['public']
    print(f'public: {file_hash}')
    download_from_gateway(file_hash)