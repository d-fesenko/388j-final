from datetime import datetime
from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask import Flask, url_for, session, request, redirect, jsonify, render_template, flash
import base64
import io
from io import BytesIO
from urllib.parse import urlencode
from werkzeug.utils import secure_filename
from ..forms import SearchForm, create_favorites_form, PreferencesForm, UserReviewForm
from ..utils import get_steam_games, get_items_equipped, get_steam_level
from ..config import STEAM_API_KEY, SECRET_KEY, MONGODB_HOST
import requests
import re
from ..models import User, Review
from ..client import SteamProfileClient
from .. import db, client

users = Blueprint("users", __name__)

def current_time() -> str:
    return datetime.now().strftime("%B %d, %Y at %H:%M:%S")


@users.route("/search-results/<query>", methods=["GET", "POST"])
def query_results(query):
    results = client.search(User, query)

    return render_template("query.html", results=results)


@users.route("/user/<steamid>",  methods=["GET", "POST"])
def userprofile(steamid):
    if current_user.is_authenticated and steamid == current_user['steamid']:
        return redirect(url_for('logins.account'))
    user = User.objects(steamid=steamid).first() 
    
    sorted_games = sorted(user.games, key=lambda game: int(game['playtime_hours']), reverse=True)
    has_favorites = False
    for game in sorted_games:
        if game['is_favorite']:
            has_favorites = True
            break
    form = UserReviewForm()
    steamid = request.form.get('steamid')
    if request.method == 'POST' and form.validate_on_submit() and current_user.is_authenticated:
        if user:
            review = Review(
                commenter=current_user._get_current_object(),
                reviewee=user.name,
                content=form.text.data,
                date=current_time()
            )
            review.save()
            flash('Your review has been posted.')

    reviews = Review.objects(reviewee=str(user.name))
    return render_template('user_profile.html', form=form, reviews=list(reviews), user=user, sorted_games=sorted_games, has_favorites = has_favorites)