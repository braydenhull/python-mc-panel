__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler


class LoginHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.render(self.application.settings['template_path'] + '/login.template', pageName="Login",
                    current_user="Not Logged In")