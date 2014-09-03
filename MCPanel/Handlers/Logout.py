__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseHandler


class LogoutHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.clear_all_cookies()
        self.application.authentication.make_session(self.current_user)
        self.redirect(self.application.settings['login_url'])