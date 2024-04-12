import requests

class IPFSMiddleware:
    def __init__(self, ipfs_api_url):
        # Initialize IPFSMiddleware with the URL of the IPFS API.
        self.ipfs_api_url = ipfs_api_url

    def upload_file(self, file_storage):
        # Prepare the file payload for the POST request, including the filename and content type.
        files = {'file': (file_storage.filename, file_storage, file_storage.content_type)}
        
        # Send a POST request to the IPFS API to upload the file. The 'add' endpoint is used for uploading.
        response = requests.post(f'{self.ipfs_api_url}/api/v0/add', files=files)
        
        # Return the JSON response which contains the file hash among other details.
        return response.json()

    def download_file(self, file_hash, destination):
        # Send a POST request to the IPFS API to fetch the file content using its hash.
        # The 'cat' endpoint outputs the content of a file identified by the file hash.
        response = requests.post(f'{self.ipfs_api_url}/api/v0/cat?arg={file_hash}', stream=True)
        
        if response.status_code == 200:
            # If the file is found, write the content to the destination file in chunks.
            # This is efficient for handling large files.
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return True  # Return True to indicate successful download.
        
        # Return False if the file is not found or if there's an error in downloading.
        return False