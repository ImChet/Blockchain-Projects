from flask import Flask, request, jsonify, abort, send_file
from werkzeug.utils import secure_filename
from ipfs_middleware import IPFSMiddleware
from eth_middleware import EthereumMiddleware
import os
import hashlib
from web3.exceptions import ContractLogicError

app = Flask(__name__)
ipfs_middleware = IPFSMiddleware('http://localhost:5001')
app = Flask(__name__)
eth_middleware = EthereumMiddleware('http://localhost:8545', os.getenv('CONTRACT_ADDRESS'))

# In-memory mapping of file hashes to original filenames
file_mapping = {}

# Helper function to generate hash of file metadata
def generate_metadata_hash(metadata):
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
    response = ipfs_middleware.upload_file(file)

    file_mapping[response['Hash']] = filename

    receipt = {
        'size': response['Size'],
        'filename': filename,
        'public': response['Hash'],
        'hash': generate_metadata_hash(response)
    }
    return jsonify(receipt), 200

# Endpoint to handle file downloads
@app.route('/download/<string:file_hash>', methods=['GET'])
def download_file_from_ipfs(file_hash):
    # Retrieve the original filename from the in-memory mapping
    original_filename = file_mapping.get(file_hash)
    if not original_filename:
        abort(404, 'Original filename not found')

    download_path = f'/tmp/{file_hash}'
    if ipfs_middleware.download_file(file_hash, download_path):
        # Use the original filename in the content disposition
        return send_file(download_path, as_attachment=True, download_name=f'dl_{original_filename}')
    else:
        abort(404, 'File not found')

def to_dict(dictToParse):
    # convert any 'AttributeDict' type found to 'dict'
    parsedDict = dict(dictToParse)
    for key, val in parsedDict.items():
        if isinstance(val, list):
            parsedDict[key] = [parseValue(x) for x in val]
        else:
            parsedDict[key] = parseValue(val)
    return parsedDict

def parseValue(val):
    # check for nested dict structures to iterate through
    if 'dict' in str(type(val)).lower():
        return to_dict(val)
    # convert 'bytes' type to 'str'
    elif 'bytes' in str(type(val)):
        return val.hex()
    else:
        return val

@app.route('/register', methods=['POST'])
def register_data():
    data_hash = request.json.get('data_hash')
    filename = request.json.get('filename')
    file_cid = request.json.get('file_cid')
    size = request.json.get('size')
    account = request.json.get('account')

    receipt = eth_middleware.register_data(data_hash, filename, file_cid, size, account)
    if receipt:
        receipt_dict = to_dict(receipt)
        return jsonify({'status': 'success', 'receipt': receipt_dict}), 200
    else:
        print("Failed to register data.")
        return jsonify({'status': 'error', 'message': 'Failed to register data.'}), 400

@app.route('/query', methods=['GET'])
def query_data():
    data_hash = request.args.get('data_hash')
    data_info = eth_middleware.query_data(data_hash)
    return jsonify(to_dict(data_info)), 200

@app.route('/transfer', methods=['POST'])
def transfer_data():
    data_hash = request.json.get('data_hash')
    from_address = request.json.get('from_address')
    to_address = request.json.get('to_address')
    receipt = eth_middleware.transfer_data(data_hash, from_address, to_address)
    
    return jsonify(to_dict(receipt)), 200

@app.route('/burn', methods=['POST'])
def burn_data():
    try:
        data_hash = request.json.get('data_hash')
        from_address = request.json.get('from_address')
        receipt = eth_middleware.burn_data(data_hash, from_address)
        return jsonify(to_dict(receipt)), 200
    except ContractLogicError as e:
        error_message = str(e)
        print(f"Contract logic error: {error_message}")
        return jsonify({'status': 'error', 'message': error_message}), 500

@app.route('/tracker', methods=['GET'])
def query_tracker():
    data_hash = request.args.get('data_hash')
    transfer_log = eth_middleware.query_tracker(data_hash)
    return jsonify(transfer_log), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)