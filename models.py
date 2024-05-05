class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    reviewee = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(default=datetime)