__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler
from tornado.web import authenticated


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.render(self.application.settings['template_path'] + '/index.template')
        self.redirect(self.application.reverse_url('Servers_Index'))


class LoginHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.render(self.application.settings['template_path'] + '/login.template',
                    current_user="Not Logged In")


class LogoutHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.clear_all_cookies()
        self.application.authentication.make_session(self.current_user)
        self.redirect(self.application.settings['login_url'])