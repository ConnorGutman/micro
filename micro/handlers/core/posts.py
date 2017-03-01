# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler
from micro.models import Comment


class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.error(404)
            return
        else:
            comments = Comment.all().filter("post =", post_id).order('created')
            self.render("permalink.html", post=post, comments=comments)
