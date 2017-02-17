# Necessary imports
import os
import re
import random
import hashlib
import hmac
from string import letters
import webapp2
import jinja2
from google.appengine.ext import db

# Set jinja2 template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# function for rendering templates
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# Secret key for encryption
secret = 'bees'


# Function for encrypting things!
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


# Function for checking if value is encrypted
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# BlogHandler class code ------------------------------------------------------
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def render_post(response, post):
        response.out.write('<b>' + post.subject + '</b><br>')
        response.out.write(post.content)


# User Account code -----------------------------------------------------------
# validate user input
# Check that username contains only valid characters
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


# Function to check username validity
def valid_username(username):
    return username and USER_RE.match(username)


# Check that password contains only valid characters
PASS_RE = re.compile(r"^.{3,20}$")


# Function to check password validity
def valid_password(password):
    return password and PASS_RE.match(password)


# Check that email contains only valid characters
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


# Function to check email validity
def valid_email(email):
    return not email or EMAIL_RE.match(email)


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


# Blog code -------------------------------------------------------------------
# General blog key
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


# Post class
class Post(db.Model):
    subject = db.StringProperty(required=True)
    author = db.StringProperty()
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        postID = self.key().id()
        liked = Like.all().filter('post =', str(postID)).count()
        return render_str("post.html", p=self, id=postID, l=liked)


# Comment class
class Comment(db.Model):
    author = db.StringProperty()
    post = db.StringProperty()
    text = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)


# Like class
class Like(db.Model):
    post = db.StringProperty()
    user = db.StringProperty()
    liked = db.BooleanProperty()


class likePost(BlogHandler):
    def get(self):
        self.redirect('/')

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        postID = str(post.key().id())
        if self.user and self.user.name != post.author:
            username = self.user.name
            likeCount = Like.all().filter('post =',
                                          postID).filter('user =',
                                                         username).count()
            if likeCount is 0:
                l = Like(post=postID, user=username, liked=True)
                l.put()
                self.redirect('/liked/%s' % postID)
            else:
                self.redirect('/%s' % postID)
        else:
            self.redirect('/login')


class liked(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        postID = str(post.key().id())
        contentType = "You have successfully liked this post!"
        self.render("deleted.html", contentType=contentType, postID=postID)


# Get all comments at /allcomments
class allComments(BlogHandler):
    def get(self):
        comments = Comment.all()
        self.render('comment.html', comments=comments)


# Create a new comment at /newcomment
class NewComment(BlogHandler):
    def get(self, post_id):
        self.redirect("/")

    def post(self, post_id):
                key = db.Key.from_path('Post', int(post_id),
                                       parent=blog_key())
                post = db.get(key)
                postID = str(post.key().id())
                if self.user:
                    author = self.user.name
                    text = self.request.get('commentText')
                    c = Comment(parent=blog_key(), author=author, post=postID,
                                text=text)
                    c.put()
                    self.redirect('/%s' % postID)
                else:
                    self.redirect('/%s' % postID)


# Delete a comment at /deletecomment
class DeleteComment(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
        comment = db.get(key)
        postID = comment.post
        if self.user and self.user.name == comment.author:
            db.delete(key)
            self.redirect("/deletedcomment/%s" % postID)
        else:
            self.redirect('/')


# Edit a comment at /editcomment
class EditComment(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
        comment = db.get(key)
        if self.user and self.user.name == comment.author:
            commentID = comment.key().id()
            commentText = comment.text
            postID = comment.post
            self.render('editcomment.html', commentText=commentText,
                        commentID=commentID, postID=postID)
        else:
            self.redirect('/')


# Submit updated comment at /updatecomment
class UpdateComment(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
        comment = db.get(key)
        returnPost = comment.post
        if self.user and self.user.name == comment.author:
            comment.text = self.request.get('commentText')
            comment.put()
            self.redirect('/%s' % returnPost)
        else:
            self.redirect('/%s' % returnPost)


# Redirect user to success page for deletion at /deletedcomment
class DeletedComment(BlogHandler):
    def get(self, post_id):
        postID = int(post_id)
        self.redirect('/%s' % postID)


# Generate blog homepage
class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts=posts)


# Individual post pages accessible by postID
class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = Comment.all().filter("post =", post_id).order('created')

        if not post:
            self.error(404)
            return
        self.render("permalink.html", post=post, comments=comments)


# Create a new post at /newpost
class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/')
        author = self.user.name
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content and author:
            p = Post(parent=blog_key(), subject=subject, content=content,
                     author=author)
            p.put()
            self.redirect('/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content,
                        error=error, author=author)


# Edit a post at /edit/postID
class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if self.user and self.user.name == post.author:
            subject = post.subject
            content = post.content
            author = post.author
            error = ""
            postID = post.key().id()
            self.render("editpost.html", subject=subject, content=content,
                        error=error, author=author, postID=postID)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if not self.user:
            self.redirect('/')
        author = self.user.name
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content and author:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.subject = subject
            post.content = content
            postID = int(post_id)
            post.put()
            self.redirect('/edited/%s' % postID)
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject, content=content,
                        error=error, author=author)


# Redirect user to success page for edited post
class Edited(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        postID = str(post.key().id())
        self.redirect('/%s' % postID)


# Delete a post at /delete/postID
class DeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        postID = int(post_id)
        if self.user and self.user.name == post.author:
            db.delete(key)
            self.redirect("/deleted/%s" % postID)
        else:
            if self.user:
                self.redirect('/')
            else:
                self.redirect('/login')

# Redirect user to success page for deleted post


class Deleted(BlogHandler):
    def get(self, post_id):
        postID = ""
        contentType = "Your post has been deleted!"
        self.render("deleted.html", contentType=contentType, postID=postID)


# Signup page for Micro at /signup
class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        # Grab user input
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        # Assign username and email to variables
        params = dict(username=self.username,
                      email=self.email)

        # Validate user input
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


# Class for registering a user that has been validated
class Register(Signup):
    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


# Log into Micro at /login
class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


# Log out of Micro at /logout
class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


# Assign functions to respective URLs
app = webapp2.WSGIApplication([('/?', BlogFront),
                               ('/([0-9]+)', PostPage),
                               ('/newpost', NewPost),
                               ('/newcomment/([0-9]+)', NewComment),
                               ('/deletecomment/([0-9]+)', DeleteComment),
                               ('/editcomment/([0-9]+)', EditComment),
                               ('/updatecomment/([0-9]+)', UpdateComment),
                               ('/deletedcomment/([0-9]+)', DeletedComment),
                               ('/allcomments', allComments),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/edit/([0-9]+)', EditPost),
                               ('/likepost/([0-9]+)', likePost),
                               ('/edited/([0-9]+)', Edited),
                               ('/deleted/([0-9]+)', Deleted),
                               ('/liked/([0-9]+)', liked),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)
                               ],
                              debug=True)
