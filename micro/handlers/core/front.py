# Necessary imports
from micro.handlers import BlogHandler
from micro.models import Post


# Generate blog homepage
class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts=posts)
