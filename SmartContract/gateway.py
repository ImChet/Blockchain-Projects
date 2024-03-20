from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
middleware_url = 'http://localhost:5000'  # URL where your middleware is running

@app.route('/api/deposit', methods=['POST'])
def deposit():
    response = requests.post(f'{middleware_url}/deposit', json=request.json)
    return jsonify(response.json())

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    response = requests.post(f'{middleware_url}/withdraw', json=request.json)
    return jsonify(response.json())

@app.route('/api/query', methods=['POST'])
def query():
    response = requests.post(f'{middleware_url}/query', json=request.json)
    return jsonify(response.json())

@app.route('/api/set_policy', methods=['POST'])
def set_policy():
    response = requests.post(f'{middleware_url}/set_policy', json=request.json)
    return jsonify(response.json())

@app.route('/api/get_policy', methods=['POST']) 
def get_policy():
    response = requests.post(f'{middleware_url}/get_policy', json=request.json)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=8080)

