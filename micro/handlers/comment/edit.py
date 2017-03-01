# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler


class EditComment(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
        comment = db.get(key)
        if not BlogHandler.comment_exists(self, comment):
            self.redirect('/')
        else:
            if not BlogHandler.user_logged_in(self):
                self.redirect('/login')
            else:
                if BlogHandler.user_owns_comment(self, comment):
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
        if not BlogHandler.comment_exists(self, comment):
            self.redirect('/')
        else:
            returnPost = comment.post
            if not BlogHandler.user_logged_in(self):
                self.redirect('/login')
            else:
                if BlogHandler.user_owns_comment(self, comment):
                    comment.text = self.request.get('commentText')
                    comment.put()
                    self.redirect('/%s' % returnPost)
                else:
                    self.redirect('/%s' % returnPost)
