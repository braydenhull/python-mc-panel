__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler


class LogoutHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.clear_all_cookies()
        self.redirect(self.application.settings['login_url'])