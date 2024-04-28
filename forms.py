from ast import Pass
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    ValidationError,
)



class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")

class PreferencesForm(FlaskForm):
    make_game_library_private = BooleanField("Make game library private")

    make_playtime_private = BooleanField("Make playtime private")

    display_profile_background = BooleanField("Display custom profile background")

    submit = SubmitField("Save Changes")

class FavoritesForm(FlaskForm):
    submit = SubmitField('Update Favorites')

def create_favorites_form(games_list):
    for game in games_list:
        setattr(FavoritesForm, str(game['appid']), BooleanField(default=game['is_favorite']))
    return FavoritesForm()

