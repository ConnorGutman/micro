# Necessary imports
from google.appengine.ext import db


# Like class
class Like(db.Model):
    post = db.StringProperty()
    user = db.StringProperty()
    liked = db.BooleanProperty()
