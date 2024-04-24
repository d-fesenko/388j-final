from flask import Flask, url_for, session, request, redirect, jsonify, render_template
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_login import UserMixin
from flask_mongoengine import MongoEngine
import requests
import re
from urllib.parse import urlencode
from config import STEAM_API_KEY

db = MongoEngine()
login_manager = LoginManager()


app = Flask(__name__)

app.config['SECRET_KEY'] = b'\x9dGP\x1dq\xec=\x05_\xfd=(\xd3q"a'
app.config['MONGODB_HOST'] = 'mongodb+srv://dfesenko:daniel2004@cluster0.ac3iyvb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

    
db.init_app(app)
login_manager.init_app(app)




@app.route('/')
def index():
    if current_user.is_authenticated:
        print("authenticated")
    else:
        print("not authenticated")
    return render_template('index.html', userdata = {})

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) #this should probably redirect to the account page, once we make one 
    
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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

    response = requests.post('https://steamcommunity.com/openid/login', params=openid_params)
    if response:
        match = re.search(r'https://steamcommunity.com/openid/id/(\d+)', request.args.get('openid.claimed_id', ''))
        if match:
            steamID64 = match.group(1)
            # Fetch user details from Steam API
            steam_api_key = STEAM_API_KEY
            api_url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steamID64}'
            api_response = requests.get(api_url).json()
            if api_response.get('response') and api_response['response'].get('players'):
                userData = api_response['response']['players'][0]

                

                existing_user = User.objects(steamid=userData['steamid']).first()
                if existing_user:
                    #If user alr exists we don't need to keep adding duplicates, so just login
                    login_user(existing_user)
                else:
                    # No user exists, create new user
                    new_user = User(steamid=userData['steamid'], name=userData['personaname'], avatar=userData['avatarmedium'])
                    new_user.save() 
                    login_user(new_user)
                return redirect(url_for('index'))
            
    return "Error: Unable to validate your request" #This should prolly never happen

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

class User(db.Document, UserMixin):
    steamid = db.StringField(required = True)
    name = db.StringField(required = True)
    avatar = db.StringField(required = True) #The URL for the avatar image, not the image itself

    # Implement the get_id method required by Flask-Login
    def get_id(self):
        return str(self.id)
