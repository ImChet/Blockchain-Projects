from flask import Flask, request, jsonify, abort, send_file
from werkzeug.utils import secure_filename
from ipfs_middleware import IPFSMiddleware
import os
import hashlib
import json

app = Flask(__name__)
middleware = IPFSMiddleware('http://localhost:5001')

# Helper function to generate hash of file metadata
def generate_metadata_hash(metadata):
    metadata_string = json.dumps(metadata, sort_keys=True)
    return hashlib.sha256(metadata_string.encode()).hexdigest()

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
    response['filename'] = filename  # Include sanitized filename in response
    response['hash'] = generate_metadata_hash(response)  # Add hash of metadata to response
    return jsonify(response), 200  # Return the JSON response from IPFS

# Endpoint to handle file downloads
@app.route('/download/<string:file_hash>', methods=['GET'])
def download_file_from_ipfs(file_hash):
    download_path = f'/tmp/dl_{file_hash}'
    if middleware.download_file(file_hash, download_path):
        return send_file(download_path, as_attachment=True, attachment_filename=f'dl_{file_hash}')
    else:
        abort(404, 'File not found')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
