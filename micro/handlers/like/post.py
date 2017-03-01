# Necessary imports
from google.appengine.ext import db
from micro.handlers import blog_key
from micro.handlers import BlogHandler
from micro.models import Like


class likePost(BlogHandler):
    def get(self):
        self.redirect('/')

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            postID = str(post.key().id())
            if BlogHandler.user_logged_in(self):
                if not BlogHandler.user_owns_post(self, post):
                    username = self.user.name
                    likeCount = Like.all().filter('post =',
                                                  postID).filter('user =',
                                                                 username
                                                                 ).count()
                    if likeCount is 0:
                        l = Like(post=postID, user=username, liked=True)
                        l.put()
                        self.redirect('/liked/%s' % postID)
                    else:
                        self.redirect('/%s' % postID)
                else:
                    postID = str(post.key().id())
                    contentType = "Sorry, you cannot like your own post."
                    self.render("deleted.html", contentType=contentType,
                                postID=postID)
            else:
                self.redirect('/login')


class liked(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
                               parent=blog_key())
        post = db.get(key)
        if not BlogHandler.post_exists(self, post):
            self.redirect('/')
        else:
            postID = str(post.key().id())
            contentType = "You have successfully liked this post!"
            self.render("deleted.html", contentType=contentType, postID=postID)
