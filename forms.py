from ast import Pass
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    ValidationError,
)

class UserReviewForm(FlaskForm):
    text = TextAreaField(
        "Review", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")

class PreferencesForm(FlaskForm):
    game_library_privacy = SelectField(
        'Game Library Privacy  ',
        choices=[('public', 'Public'), ('private', 'Private')],
        validators=[DataRequired()]
    )
    playtime_privacy = SelectField(
        'Playtime Privacy  ',
        choices=[('public', 'Public'), ('private', 'Private')],
        validators=[DataRequired()]
    )
    display_profile_background = SelectField(
        'Display Profile Background?  ',
        choices=[('yes', 'Yes'), ('no', 'No')],
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Changes")

class FavoritesForm(FlaskForm):
    submit = SubmitField('Update Favorites')

def create_favorites_form(games_list):
    for game in games_list:
        setattr(FavoritesForm, str(game['appid']), BooleanField(default=game['is_favorite']))
    return FavoritesForm()

