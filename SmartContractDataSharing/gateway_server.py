from flask import Flask, request, jsonify, abort, send_file
from werkzeug.utils import secure_filename
from ipfs_middleware import IPFSMiddleware
import os
import hashlib
import json

app = Flask(__name__)
middleware = IPFSMiddleware('http://localhost:5001')  # Initialize middleware with IPFS API URL

# In-memory mapping of file hashes to original filenames
file_mapping = {}

# Helper function to generate hash of file metadata
def generate_metadata_hash(metadata):
    # Prepare the data for hashing
    data_string = f"{metadata['Size']}{metadata['Name']}{metadata['Hash']}"
    return hashlib.sha256(data_string.encode()).hexdigest()

# Endpoint to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file_to_ipfs():
    if 'file' not in request.files:
        abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '':
        abort(400, 'No selected file')
    filename = secure_filename(file.filename)
    response = middleware.upload_file(file)  # Upload the file via middleware

    # Store the mapping of the file hash to the original filename
    file_mapping[response['Hash']] = filename

    # Create a receipt with the required information
    receipt = {
        'size': response['Size'],
        'filename': filename,
        'public': response['Hash'],
        'hash': generate_metadata_hash(response)
    }
    return jsonify(receipt), 200  # Return the receipt as JSON

# Endpoint to handle file downloads
@app.route('/download/<string:file_hash>', methods=['GET'])
def download_file_from_ipfs(file_hash):
    # Retrieve the original filename from the in-memory mapping
    original_filename = file_mapping.get(file_hash)
    if not original_filename:
        abort(404, 'Original filename not found')

    download_path = f'/tmp/{file_hash}'
    if middleware.download_file(file_hash, download_path):
        # Use the original filename in the content disposition
        return send_file(download_path, as_attachment=True, download_name=f'dl_{original_filename}')
    else:
        abort(404, 'File not found')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
