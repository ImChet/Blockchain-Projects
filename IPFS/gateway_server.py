from flask import Flask, request, jsonify, abort, send_file
from werkzeug.utils import secure_filename
from ipfs_middleware import IPFSMiddleware
import os

app = Flask(__name__)
middleware = IPFSMiddleware('http://localhost:5001')  # Initialize middleware with IPFS API URL

# Endpoint to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file_to_ipfs():
    if 'file' not in request.files:
        abort(400, 'No file part')  # Abort if no file is part of the request
    file = request.files['file']
    if file.filename == '':
        abort(400, 'No selected file')  # Abort if no file is selected
    filename = secure_filename(file.filename)  # Secure the filename to avoid directory traversal attacks
    response = middleware.upload_file(file)  # Upload the file via middleware
    return jsonify(response), 200  # Return the JSON response from IPFS

# Endpoint to handle file downloads
@app.route('/download/<string:file_hash>', methods=['GET'])
def download_file_from_ipfs(file_hash):
    download_path = f'/tmp/{file_hash}'  # Define a path for the downloaded file
    if middleware.download_file(file_hash, download_path):
        return send_file(download_path, as_attachment=True)  # Send the file to the client
    else:
        abort(404, 'File not found')  # Abort if the file is not found

if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Run the Flask server in debug mode on port 8080