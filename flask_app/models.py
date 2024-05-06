from flask_login import UserMixin
from . import db, login_manager


class User(db.Document, UserMixin):
    steamid = db.StringField(required = True)
    name = db.StringField(required = True)
    avatar = db.StringField(required = True)
    avatar_frame = db.StringField()
    profile_background = db.StringField()
    is_background_animated = db.BooleanField()
    level = db.StringField()
    games = db.ListField()
    preferences = db.DictField()

    # Implement the get_id method required by Flask-Login
    def get_id(self):
        return str(self.id)
    
@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()
    
class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    reviewee = db.StringField(required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)

