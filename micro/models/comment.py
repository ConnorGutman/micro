# Necessary imports
from google.appengine.ext import db


# Comment class
class Comment(db.Model):
    author = db.StringProperty()
    post = db.StringProperty()
    text = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
