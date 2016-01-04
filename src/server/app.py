from datetime import datetime, timedelta
import os
import jwt
import json
import requests
from flask import Flask, send_file
from jwt import DecodeError, ExpiredSignature


# Configuration

current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, '..', 'client'))

app = Flask(__name__, static_url_path='', static_folder=client_path)
app.config.from_object('config')


# Helper functions

def create_tokens(user):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    return token.decode('unicode_escape')

def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['TOKEN_SECRET'])


# Routes

@app.route('/')
def index():
    return send_file(os.path.join(client_path, 'index.html'))

@app.route('/callback', methods=['POST'])
# we will rename this at some point
def callback():
    # Step 1. Exchange authorization code for access token.
    # Step 2. Retrieve information about the current user.
    # Step 3. (optional) Link accounts.
    # Step 4. Create a new account or return an existing one.
    token = {'hello': 'world'}
    return jsonify(token=token)


if __name__ == '__main__':
    app.run(port=5000)
