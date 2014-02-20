__author__ = 'brayden'

from tornado.web import asynchronous
from Handlers.Base import BaseHandler


class LoginHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.render(self.application.settings['template_path'] + '/login.template',
                    current_user="Not Logged In")