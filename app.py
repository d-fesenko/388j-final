from flask import Flask, url_for, session, request, redirect, jsonify, render_template, flash
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_login import UserMixin
from flask_mongoengine import MongoEngine
import requests
import re
from urllib.parse import urlencode
from config import STEAM_API_KEY, SECRET_KEY, MONGODB_HOST
from forms import SearchForm, FavoritesForm, create_favorites_form
from client import SteamProfileClient

from utils import get_steam_games, get_items_equipped, get_steam_level


db = MongoEngine()
login_manager = LoginManager()


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGODB_HOST'] = MONGODB_HOST

    
db.init_app(app)
login_manager.init_app(app)

class User(db.Document, UserMixin):
    steamid = db.StringField(required = True)
    name = db.StringField(required = True)
    avatar = db.StringField(required = True)
    avatar_frame = db.StringField()
    profile_background = db.StringField()
    is_background_animated = db.BooleanField()
    level = db.StringField()
    games = db.ListField()
    preferences = db.ListField()

    # Implement the get_id method required by Flask-Login
    def get_id(self):
        return str(self.id)

client = SteamProfileClient(db, User.objects())


@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()
    user = current_user
    if form.validate_on_submit():
        return redirect(url_for("query_results", query=form.search_query.data))

    return render_template("index.html", form=form, user=user)


@app.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    results = client.search(query)
    return render_template("query.html", results=results)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) #this should probably redirect to the account page, once we make one 
    
    login_url_params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': url_for('process_openid', _external=True),
        'openid.realm': request.url_root,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    steam_login_url = 'https://steamcommunity.com/openid/login?' + urlencode(login_url_params)
    return redirect(steam_login_url)

@app.route('/logout')
def logout():
    session.clear()
    resp = redirect(url_for('index'))
    resp.set_cookie('session', "", expires=0)
    return resp

@app.route('/account', methods=['GET', 'POST'])
def account():
    if current_user.is_authenticated:

        user = current_user
        sorted_games = sorted(user.games, key=lambda game: int(game['playtime_hours']), reverse=True)

        form = create_favorites_form(sorted_games)


        if form.validate_on_submit():
            for game in user.games:
                field_name = str(game['appid'])
                favorite_field = getattr(form, field_name)
                if favorite_field.data:
                    game['is_favorite'] = True
                else:
                    game['is_favorite'] = False
            
            current_user.save()

            flash('Favorites updated!')

        return render_template('account.html', user=user, sorted_games=sorted_games, form=form)
    else:
        return redirect(url_for('login'))


@app.route("/user/<steamid>")
def userprofile(steamid):
    if current_user.is_authenticated and steamid == current_user['steamid']:
        return redirect(url_for('account'))
    user = User.objects(steamid=steamid).first() 
    sorted_games = sorted(user.games, key=lambda game: int(game['playtime_hours']), reverse=True)
    has_favorites = False
    for game in sorted_games:
        if game['is_favorite']:
            has_favorites = True
            break
    return render_template('user_profile.html', user=user, sorted_games=sorted_games, has_favorites = has_favorites)

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

                games = get_steam_games(STEAM_API_KEY, userData['steamid'])
                items = get_items_equipped(STEAM_API_KEY, userData['steamid'])
                profile_background = items['profilebackground']
                is_background_animated = items['isbackgroundanimated']
                avatar_frame = items['avatarframe']
                level = get_steam_level(STEAM_API_KEY, userData['steamid'])

                existing_user = User.objects(steamid=userData['steamid']).first()
                if existing_user:
                    existing_user.name = userData['personaname']
                    existing_user.avatar = userData['avatarfull']
                    existing_user.games = games
                    existing_user.profile_background = profile_background
                    existing_user.is_background_animated = is_background_animated
                    existing_user.avatar_frame = avatar_frame
                    existing_user.level = level
                    existing_user.save()
                    login_user(existing_user)
                else:
                    # No user exists, create new user
                    
                    new_user = User(
                        steamid=userData['steamid'], 
                        name=userData['personaname'], 
                        avatar=userData['avatarmedium'], 
                        games=games, 
                        profile_background = profile_background, 
                        is_background_animated = is_background_animated, 
                        level=level, 
                        avatar_frame=avatar_frame)
                    
                    new_user.save() 
                    login_user(new_user)
                return redirect(url_for('index'))
            
    return "Error: Unable to validate your request" #This should prolly never happen

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()