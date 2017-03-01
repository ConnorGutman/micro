# Necessary imports
import random
import hashlib
from string import letters
from google.appengine.ext import db


# User Account code -----------------------------------------------------------
# Encrypt user info
# Define salt for encryption functions
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


# Generate salt for password
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


# Generate password hash
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


# Get User key
def users_key(group='default'):
    return db.Key.from_path('users', group)


# Declare user class
class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    # Get user by ID
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    # Get user by name
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    # Create new user
    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    # Log into user
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
