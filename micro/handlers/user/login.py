# Necessary imports
from micro.handlers import BlogHandler
from micro.models import User


class Login(BlogHandler):
    def get(self):
        if not BlogHandler.user_logged_in(self):
            self.render('login-form.html')
        else:
            self.redirect('/')

    def post(self):
        if BlogHandler.user_logged_in(self):
            self.redirect('/')
        else:
            username = self.request.get('username')
            password = self.request.get('password')

            u = User.login(username, password)
            if u:
                self.login(u)
                self.redirect('/')
            else:
                msg = 'Invalid login'
                self.render('login-form.html', error=msg)
