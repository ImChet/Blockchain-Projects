from flask import Flask, request, jsonify, abort, send_file
from werkzeug.utils import secure_filename
from ipfs_middleware import IPFSMiddleware
import os
import hashlib
import json

app = Flask(__name__)
middleware = IPFSMiddleware('http://localhost:5001')  # Initialize middleware with IPFS API URL

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
    download_path = f'/tmp/{file_hash}'
    # Assume filename is stored or can be retrieved; here just appending 'dl_' prefix
    # filename = f'dl_{file_hash}'
    if middleware.download_file(file_hash, download_path):
        return send_file(download_path, as_attachment=True, download_name=filename)
    else:
        abort(404, 'File not found')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
