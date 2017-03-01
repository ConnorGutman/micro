# Necessary imports
from google.appengine.ext import db


# General blog key
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)
