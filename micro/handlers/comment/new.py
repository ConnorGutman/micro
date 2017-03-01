# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler
from micro.models import Comment


# Create a new comment at /newcomment
class NewComment(BlogHandler):
    def get(self, post_id):
        self.redirect("/")

    def post(self, post_id):
                key = db.Key.from_path('Post', int(post_id),
                                       parent=blog_key())
                post = db.get(key)
                if not BlogHandler.post_exists(self, post):
                    self.redirect('/')
                else:
                    if not BlogHandler.user_logged_in(self):
                        self.redirect('/login')
                    else:
                        author = self.user.name
                        text = self.request.get('commentText')
                        c = Comment(parent=blog_key(), author=author,
                                    post=post_id, text=text)
                        c.put()
                        self.redirect('/%s' % post_id)
