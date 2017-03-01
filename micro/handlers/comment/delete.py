# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler


class DeleteComment(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
        comment = db.get(key)
        if not BlogHandler.comment_exists(self, comment):
            self.redirect('/')
        else:
            postID = comment.post
            if BlogHandler.user_logged_in(self):
                if BlogHandler.user_owns_comment(self, comment):
                    db.delete(key)
                    self.redirect("/deletedcomment/%s" % postID)
                else:
                    self.redirect('/')
            else:
                self.redirect('/')


# Redirect user to success page for deletion at /deletedcomment
class DeletedComment(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            self.redirect('/%s' % post_id)
