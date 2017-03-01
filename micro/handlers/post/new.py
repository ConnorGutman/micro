# Necessary imports
from micro.handlers import blog_key
from micro.handlers import BlogHandler
from micro.models import Post


class NewPost(BlogHandler):
    def get(self):
        if BlogHandler.user_logged_in(self):
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not BlogHandler.user_logged_in(self):
            self.redirect('/')
        else:
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
