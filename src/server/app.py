import os, sys, optparse
import jwt, json, requests, hashlib
from datetime import datetime, timedelta
from urllib.parse import parse_qsl
from flask import Flask, send_file, jsonify, request
from jwt import DecodeError, ExpiredSignature

# Configure

current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, '..', 'client'))

app = Flask(__name__, static_url_path='', static_folder=client_path)
app.config.from_object('config')

# Run with CL option

def run_app(app, default_host="localhost",
            default_port="5000"):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """# http://flask.pocoo.org/snippets/133/

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help="Hostname of the Flask app " + \
                           "[default %s]" % default_host,
                      default=default_host)
    parser.add_option("-P", "--port",
                      help="Port for the Flask app " + \
                           "[default %s]" % default_port,
                      default=default_port)

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)
    parser.add_option("-p", "--profile",
                      action="store_true", dest="profile",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                       restrictions=[30])
        options.debug = True

    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )

# Helper functions

def create_token(user):
    profile = user['result']
    payload = {
        'sub': profile['uuid'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14),
        'firstname': profile['firstName'],
        'lastname': profile['lastName'],
        'username': profile['username'],
        'email': profile['email'],
        'gravatar_hash': hashlib.md5(profile['email'].lower().encode('utf-8')).hexdigest()
    }
    token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    return token.decode('unicode_escape')

def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['TOKEN_SECRET'])

# Decorators

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.user_id = payload['sub']

        return f(*args, **kwargs)

    return decorated_function

# Routes

@app.route('/')
def index():
    return send_file(os.path.join(client_path, 'index.html'))

@app.route('/auth/iplant/config')
def iplant_config():
    # no secrets
    conf = {
        'url': '/auth/iplant',
        'clientId': app.config['CONSUMER_KEY'],
        'redirectUri': app.config['CALLBACK_URL'],
    }
    return json.dumps(conf)

@app.route('/auth/iplant', methods=['POST'])
# we will rename this at some point
def iplant():
    access_token_url = app.config['ACCESS_TOKEN_URL']
    profile_api_url = app.config['PROFILE_API_URL']

    payload = dict(
        client_id=request.json['clientId'],
        redirect_uri=request.json['redirectUri'],
        client_secret=app.config['CONSUMER_SECRET'],
        code=request.json['code'],
        grant_type='authorization_code'
    )

    # Step 1. Exchange authorization code for access token.
    r = requests.post(access_token_url, data=payload)
    token = json.loads(r.text)

    # Step 2. Retrieve information about the current user.
    headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}
    r = requests.get(profile_api_url, headers=headers)
    profile = json.loads(r.text)

    # Step 3. (optional) Link accounts.
    #

    # Step 4. Create a new account or return an existing one.
    token = create_token(profile)

    return jsonify(token=token)

if __name__=="__main__":
    run_app(app)
