# Necessary imports
from google.appengine.ext import db
from micro.handlers import render_str
from like import Like


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
