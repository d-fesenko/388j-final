from flask import Flask, url_for, session, request, redirect, jsonify
import requests
import re
from openid.consumer.consumer import Consumer
from openid.store.filestore import FileOpenIDStore
from openid.extensions import ax
from urllib.parse import urlencode
from config import STEAM_API_KEY

app = Flask(__name__)
app.secret_key = b'\x9dGP\x1dq\xec=\x05_\xfd=(\xd3q"a'

@app.route('/')
def index():
    return "Welcome to the app!"

@app.route('/login')
def login():
    login_url_params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://localhost:5000/process-openid',
        'openid.realm': request.url_root,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    steam_login_url = 'https://steamcommunity.com/openid/login?' + urlencode(login_url_params)
    return redirect(steam_login_url)

@app.route('/process-openid')
def process_openid():
    # Extract the necessary parameters from query string
    openid_params = {
        'openid.assoc_handle': request.args.get('openid_assoc_handle'),
        'openid.signed': request.args.get('openid_signed'),
        'openid.sig': request.args.get('openid_sig'),
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'check_authentication',
    }
    
    # Prepare the data to verify
    signed_params = request.args.get('openid_signed', '').split(',')
    for item in signed_params:
        value = request.args.get(f'openid_{item.replace(".", "_")}')
        if value:
            openid_params[f'openid.{item}'] = value

    data = urlencode(openid_params)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(data))
    }

    response = requests.post('https://steamcommunity.com/openid/login', headers=headers, data=data)
    if response:
        match = re.search(r'https://steamcommunity.com/openid/id/(\d+)', request.args.get('openid_claimed_id', ''))
        if match:
            steamID64 = match.group(1)
            # Fetch user details from Steam API
            steam_api_key = STEAM_API_KEY
            api_url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steamID64}'
            api_response = requests.get(api_url).json()
            if api_response.get('response') and api_response['response'].get('players'):
                userData = api_response['response']['players'][0]

                # Set user data in session
                session['logged_in'] = True
                session['userData'] = {
                    'steam_id': userData['steamid'],
                    'name': userData['personaname'],
                    'avatar': userData['avatarmedium'],
                }
                return redirect(url_for('dashboard'))
    return "Error: Unable to validate your request"

@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        return jsonify(session['userData'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)