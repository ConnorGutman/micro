# Necessary imports
from micro.handlers import BlogHandler
from micro.handlers.validate import valid_username
from micro.handlers.validate import valid_password
from micro.handlers.validate import valid_email
from micro.models import User


class Signup(BlogHandler):
    def get(self):
        if not BlogHandler.user_logged_in(self):
            self.render("signup-form.html")
        else:
            self.redirect("/")

    def post(self):
        if not BlogHandler.user_logged_in(self):
            # Grab user input
            have_error = False
            self.username = self.request.get('username')
            self.password = self.request.get('password')
            self.verify = self.request.get('verify')
            self.email = self.request.get('email')

            # Assign username and email to variables
            params = dict(username=self.username,
                          email=self.email)

            # Validate user input
            if not valid_username(self.username):
                params['error_username'] = "That's not a valid username."
                have_error = True

            if not valid_password(self.password):
                params['error_password'] = "That wasn't a valid password."
                have_error = True
            elif self.password != self.verify:
                params['error_verify'] = "Your passwords didn't match."
                have_error = True

            if not valid_email(self.email):
                params['error_email'] = "That's not a valid email."
                have_error = True

            if have_error:
                self.render('signup-form.html', **params)
            else:
                self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


# Class for registering a user that has been validated
class Register(Signup):
    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')
