# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler


class DeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        postID = int(post_id)
        if not BlogHandler.user_logged_in(self):
            self.redirect('/login')
        else:
            if not BlogHandler.user_owns_post(self, post):
                self.redirect('/%s' % postID)
            else:
                db.delete(key)
                contentType = "Your post has been deleted!"
                self.render("deleted.html", contentType=contentType,
                            postID="")
                # self.redirect("/deleted/%s" % postID)
