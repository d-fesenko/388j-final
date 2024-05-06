from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask import Flask, url_for, session, request, redirect, jsonify, render_template, flash
from urllib.parse import urlencode
from werkzeug.utils import secure_filename
from ..forms import SearchForm, create_favorites_form, PreferencesForm
from ..utils import get_steam_games, get_items_equipped, get_steam_level
from ..config import STEAM_API_KEY
import requests
import re
from ..models import User


logins = Blueprint("logins", __name__)

@logins.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()
    user = current_user
    if form.validate_on_submit():
        return redirect(url_for('users.query_results', query=form.search_query.data)) #this line causes error

    return render_template("index.html", form=form, user=user)

@logins.route('/login')
def log_in():
    if current_user.is_authenticated:
        return redirect(url_for('logins.index'))
    
    login_url_params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': url_for('logins.process_openid', _external=True),
        'openid.realm': request.url_root,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    steam_login_url = 'https://steamcommunity.com/openid/login?' + urlencode(login_url_params)
    return redirect(steam_login_url)

@logins.route('/logout')
def logout():
    session.clear()
    resp = redirect(url_for('logins.index'))
    resp.set_cookie('session', "", expires=0)
    return resp

@logins.route('/account', methods=['GET', 'POST'])
def account():
    if current_user.is_authenticated:

        user = current_user
        sorted_games = sorted(user.games, key=lambda game: int(game['playtime_hours']), reverse=True)

        form = create_favorites_form(sorted_games)
        preferencesform = PreferencesForm(
        game_library_privacy=current_user.preferences.get('game_library_privacy', 'private'),
        playtime_privacy=current_user.preferences.get('playtime_privacy', 'public'),
        display_profile_background=current_user.preferences.get('display_profile_background', 'yes')
    )


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
        
        if preferencesform.validate_on_submit():
            user.preferences = {
                "game_library_privacy": preferencesform.game_library_privacy.data,
                "playtime_privacy": preferencesform.playtime_privacy.data,
                "display_profile_background": preferencesform.display_profile_background.data
            }

            
            current_user.save()

        return render_template('account.html', user=user, sorted_games=sorted_games, form=form, preferencesform=preferencesform)
    else:
        return redirect(url_for('logins.log_in'))
    
@logins.route('/process-openid')
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
                    existing_games = [game['appid'] for game in existing_user.games]
                    for game in games:
                        if game['appid'] not in existing_games:
                            existing_user.games.append(game)
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
                        avatar_frame=avatar_frame,
                        preferences = { #default preferences
                            "game_library_privacy": "public",
                            "playtime_privacy": "public",
                            "display_profile_background": "yes"
                        }
                        )
                    
                    new_user.save() 
                    login_user(new_user)
                return redirect(url_for('logins.index'))
            
    return "Error: Unable to validate your request" #This should prolly never happen
