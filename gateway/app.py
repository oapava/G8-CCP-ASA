from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

SERVICE1_URL = 'http://localhost:5001'
SERVICE2_URL = 'http://localhost:5002'

@app.route('/api/route')
def proxy_service1():
    response = requests.get(f'{SERVICE1_URL}/route')
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
