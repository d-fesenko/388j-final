from ast import Pass
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
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
