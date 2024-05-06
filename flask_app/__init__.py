from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager
)

from .config import SECRET_KEY, MONGODB_HOST
from .client import SteamProfileClient


db = MongoEngine()
login_manager = LoginManager()

client = SteamProfileClient(db)


from .users.routes import users
from .logins.routes import logins


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['MONGODB_HOST'] = MONGODB_HOST

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(logins)

    login_manager.login_view = "users.login"

    return app
