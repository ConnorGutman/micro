# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler


class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            if not BlogHandler.user_logged_in(self):
                self.redirect('/login')
            else:
                if not BlogHandler.user_owns_post(self, post):
                    self.redirect('/%s' % post_id)
                else:
                    subject = post.subject
                    content = post.content
                    author = post.author
                    error = ""
                    postID = post.key().id()
                    self.render("editpost.html", subject=subject,
                                content=content, error=error, author=author,
                                postID=postID)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            if not BlogHandler.user_logged_in(self):
                self.redirect('/login')
            else:
                if not BlogHandler.user_owns_post(self, post):
                    self.redirect('/%s' % post_id)
                else:
                    author = self.user.name
                    subject = self.request.get('subject')
                    content = self.request.get('content')

                    if subject and content and author:
                        key = db.Key.from_path('Post', int(post_id),
                                               parent=blog_key())
                        post = db.get(key)
                        post.subject = subject
                        post.content = content
                        postID = int(post_id)
                        post.put()
                        self.redirect('/edited/%s' % postID)
                    else:
                        error = "subject and content, please!"
                        self.render("editpost.html", subject=subject,
                                    content=content, error=error,
                                    author=author)


# Redirect user to success page for edited post
class Edited(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            self.redirect('/%s' % post_id)
