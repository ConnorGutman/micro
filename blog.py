# Necessary imports
import webapp2
# Core
from micro.handlers.core import BlogFront
from micro.handlers.core import PostPage
# User
from micro.handlers.user import Register
from micro.handlers.user import Login
from micro.handlers.user import Logout
# Post
from micro.handlers.post import NewPost
from micro.handlers.post import EditPost
from micro.handlers.post import Edited
from micro.handlers.post import DeletePost
# Comment
from micro.handlers.comment import NewComment
from micro.handlers.comment import EditComment
from micro.handlers.comment import UpdateComment
from micro.handlers.comment import DeleteComment
from micro.handlers.comment import DeletedComment
# Like
from micro.handlers.like import likePost
from micro.handlers.like import liked


# Assign functions to respective URLs
app = webapp2.WSGIApplication([('/?', BlogFront),
                               ('/([0-9]+)', PostPage),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/newpost', NewPost),
                               ('/newcomment/([0-9]+)', NewComment),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/deletecomment/([0-9]+)', DeleteComment),
                               ('/deletedcomment/([0-9]+)', DeletedComment),
                               ('/edit/([0-9]+)', EditPost),
                               ('/edited/([0-9]+)', Edited),
                               ('/editcomment/([0-9]+)', EditComment),
                               ('/updatecomment/([0-9]+)', UpdateComment),
                               ('/likepost/([0-9]+)', likePost),
                               ('/liked/([0-9]+)', liked)
                               ],
                              debug=True)
